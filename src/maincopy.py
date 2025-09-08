import pandas as pd
import numpy as np
import duckdb
from datetime import datetime, timedelta
from tqdm import tqdm

def main():
    generate_initial_data()

def generate_initial_data():
    print("🏪 Retail Sales Database Generator")
    print("=" * 40)

    # Set a random seed for reproducibility
    np.random.seed(142)

    # Create a date range with daily frequency (6 months for reasonable performance)
    date_range = pd.date_range(start='1900-01-01', end='2025-09-02', freq='D')
    print(f"📅 Date range: {len(date_range)} days")

    # Product catalog
    #change to phone models
    # add computers, devices, gadgets
    
    
    products = [
        {'product_id': 'P001', 'product_name': 'iPhone 13', 'unit_price': 999.00},
        {'product_id': 'P002', 'product_name': 'Samsung Galaxy S21', 'unit_price': 899.00},
        {'product_id': 'P003', 'product_name': 'Google Pixel 6', 'unit_price': 599.00},
        {'product_id': 'P004', 'product_name': 'OnePlus 9', 'unit_price': 729.00},
        {'product_id': 'P005', 'product_name': 'Xiaomi Mi 11', 'unit_price': 749.00},
        {'product_id': 'P006', 'product_name': 'Sony Xperia 5', 'unit_price': 899.00},
        {'product_id': 'P007', 'product_name': 'Oppo Find X3', 'unit_price': 1149.00},
        {'product_id': 'P008', 'product_name': 'Nokia 8.3', 'unit_price': 699.00},
        {'product_id': 'P009', 'product_name': 'Realme GT', 'unit_price': 599.00},
        {'product_id': 'P010', 'product_name': 'Water', 'unit_price': 2.00},
        {'product_id': 'P011', 'product_name': 'Sparkling Water', 'unit_price': 2.50},
        {'product_id': 'P012', 'product_name': 'Iced Tea', 'unit_price': 3.00},
        {'product_id': 'P013', 'product_name': 'MacBook Pro', 'unit_price': 2399.00},
        {'product_id': 'P014', 'product_name': 'Dell XPS 13', 'unit_price': 1499.00},
        {'product_id': 'P015', 'product_name': 'HP Spectre x360', 'unit_price': 1699.00},
        {'product_id': 'P016', 'product_name': 'Lenovo ThinkPad X1', 'unit_price': 1899.00},
        {'product_id': 'P017', 'product_name': 'iPad Pro', 'unit_price': 1099.00},
        {'product_id': 'P018', 'product_name': 'Samsung Galaxy Tab S7', 'unit_price': 849.00},
        {'product_id': 'P019', 'product_name': 'Microsoft Surface Pro 7', 'unit_price': 999.00},
        {'product_id': 'P020', 'product_name': 'Amazon Kindle', 'unit_price': 89.00}
    ]
    countries = [
        {'country_id': 'C001', 'country_name': 'Singapore'},
        {'country_id': 'C002', 'country_name': 'Malaysia'},
        {'country_id': 'C003', 'country_name': 'Indonesia'},
        {'country_id': 'C004', 'country_name': 'Thailand'},
        {'country_id': 'C005', 'country_name': 'Vietnam'},
        {'country_id': 'C006', 'country_name': 'Philippines'},
        {'country_id': 'C007', 'country_name': 'Brunei'},
        {'country_id': 'C008', 'country_name': 'Myanmar'},
        {'country_id': 'C009', 'country_name': 'Cambodia'},
        {'country_id': 'C010', 'country_name': 'Laos'},
        {'country_id': 'C011', 'country_name': 'Brunei'},
        {'country_id': 'C012', 'country_name': 'Myanmar'},
        {'country_id': 'C013', 'country_name': 'Thailand'}
    ]
    transaction_types = [{'transaction_id':'Sales','transaction_desc':'Product Sale'},
                         {'transaction_id':'Refund','transaction_desc':'Product Refund'},
                         {'transaction_id':'Exchange','transaction_desc':'Product Exchange'}
                        ]
    
    discount_codes = ['BLACKFRIDAY', 'CYBERMONDAY', 'NEWYEAR','CHRISTMAS']
    
    def get_black_friday(year):
        """Get Black Friday date (4th Friday in November)"""
        # First day of November
        nov_1 = datetime(year, 11, 1)
        # Find first Friday in November
        days_until_friday = (4 - nov_1.weekday()) % 7
        first_friday = nov_1 + timedelta(days=days_until_friday)
        # Fourth Friday is 3 weeks later
        black_friday = first_friday + timedelta(weeks=3)
        return black_friday
    
    def get_cyber_monday(year):
        """Get Cyber Monday (Monday after Black Friday)"""
        black_friday = get_black_friday(year)
        cyber_monday = black_friday + timedelta(days=3)  # 3 days after Friday
        return cyber_monday
    
    def get_discount_periods(year):
        """Get all discount periods for a given year"""
        black_friday = get_black_friday(year)
        cyber_monday = get_cyber_monday(year)
        
        return {
            'BLACKFRIDAY': (black_friday, black_friday),  # Just Black Friday
            'CYBERMONDAY': (cyber_monday, cyber_monday),  # Just Cyber Monday
            'NEWYEAR': (datetime(year-1, 12, 26), datetime(year, 1, 2)),  # Dec 26 to Jan 2
            'CHRISTMAS': (datetime(year, 12, 1), datetime(year, 12, 26))  # Dec 1 to Dec 26
        }
    
    def is_discount_period(date, discount_periods):
        """Check if a date falls within any discount period"""
        for period_name, (start_date, end_date) in discount_periods.items():
            if start_date <= date <= end_date:
                return period_name
        return None
     

    # Generate transaction data
    transactions = []
    customer_id = 100001
    receipt_id = 200001
    
    # Create a dictionary to store customer ages (consistent per customer)
    customer_ages = {}

    print("📅 Generating transaction data...")
    for date in tqdm(date_range, desc="Processing dates"):
        # Get discount periods for current year
        year = date.year
        current_discount_periods = get_discount_periods(year)
        discount_period_name = is_discount_period(date, current_discount_periods)
        
        # Number of receipts per day (reduced for better performance)
        day_of_week = date.weekday()
        if day_of_week >= 5:  # Weekend
            num_receipts = np.random.randint(20, 40)  # Reduced from 80-150
        else:  # Weekday
            num_receipts = np.random.randint(30, 60)  # Reduced from 100-200
        
        # Increase activity during discount periods
        if discount_period_name:
            num_receipts = int(num_receipts * 1.5)  # 50% more activity during sales
        
        for receipt in range(num_receipts):
            # Assign age to customer if not already assigned
            if customer_id not in customer_ages:
                # Realistic age distribution: more customers in 25-45 range
                age_ranges = [18, 25, 35, 45, 55, 65, 75]
                age_weights = [0.05, 0.20, 0.25, 0.25, 0.15, 0.08, 0.02]
                age_range_start = np.random.choice(age_ranges, p=age_weights)
                customer_ages[customer_id] = np.random.randint(age_range_start, min(age_range_start + 10, 80))
                country = np.random.choice(countries)
                #every 6 months 1 or 2 return or exchange
                #based on random but 95% weight on Sales
                transaction_type = transaction_types[np.random.choice([0,1,2], p=[0.95,0.025,0.025])] 
                
            # Number of items per receipt
            items_per_receipt = np.random.choice([1, 2, 3, 4], p=[0.4, 0.3, 0.2, 0.1])
            
            # Select random products for this receipt
            selected_products = np.random.choice(len(products), size=items_per_receipt, replace=False)
            
            receipt_total = 0
            
            for product_idx in selected_products:
                product = products[product_idx]
                units_sold = np.random.randint(1, 4)  # 1-3 units per item
                
                # Add some price variation (±10%)
                unit_price = product['unit_price'] * np.random.uniform(0.9, 1.1)
                
                # Apply discount if in discount period
                discount_applied = False
                discount_percentage = 0
                if discount_period_name and transaction_type['transaction_desc'] == 'Product Sale':
                    # Apply 50% discount during discount periods
                    discount_percentage = 50
                    unit_price = unit_price * 0.5
                    discount_applied = True
                
                total_amount_per_product = units_sold * unit_price
                receipt_total += total_amount_per_product
                
                # Add hour variation throughout the day
                hour = np.random.randint(6, 22)  # Store hours 6 AM to 10 PM
                transaction_datetime = date + timedelta(hours=hour, minutes=np.random.randint(0, 60))
                
                transactions.append({
                    'date': transaction_datetime,
                    'transaction_id': transaction_type['transaction_id'],
                    'transaction_desc': transaction_type['transaction_desc'],
                    'customer_number': customer_id,
                    'age': customer_ages[customer_id],
                    'receipt_number': receipt_id,
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'units_sold': units_sold,
                    'unit_price_sgd': round(unit_price, 2),
                    'total_amount_per_product_sgd': round(total_amount_per_product, 2),
                    'receipt_total_sgd': 0,  # Will be filled later
                    'country_id': country['country_id'],
                    'country': country['country_name'],
                    'discount_period': discount_period_name if discount_applied else None,
                    'discount_percentage': discount_percentage,
                    'discount_applied': discount_applied
                })
            
            # Update receipt total for all items in this receipt
            receipt_start_idx = len(transactions) - items_per_receipt
            for i in range(receipt_start_idx, len(transactions)):
                transactions[i]['receipt_total_sgd'] = round(receipt_total, 2)
            
            customer_id += 1
            receipt_id += 1

    print("📊 Creating DataFrame...")
    # Create DataFrame
    df = pd.DataFrame(transactions)
    df = df.set_index('date')

    print(f"Dataset size: {df.shape}")
    print(f"Total transactions: {len(df):,}")
    print(f"Date range: {df.index.min()} to {df.index.max()}")

    # Add datetime components
    print("⏰ Adding temporal features...")
    df['day_of_week'] = df.index.dayofweek
    df['month'] = df.index.month
    df['hour'] = df.index.hour
    df['year'] = df.index.year

    # Add day of week as text
    day_names = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    df['day_of_week_text'] = df['day_of_week'].map(lambda x: day_names[x])

    # Add month as text
    month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                   'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    df['month_text'] = df['month'].map(lambda x: month_names[x-1])

    # Cyclic encoding for temporal features
    df['day_of_week_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_of_week_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

    print("\n📋 Sample data preview:")
    print(df[['customer_number', 'age', 'product_name', 'units_sold', 'unit_price_sgd', 
              'total_amount_per_product_sgd', 'receipt_total_sgd', 'day_of_week_text', 'month_text','country_id','country','transaction_id','transaction_desc', 'discount_period', 'discount_applied']].head())

    print("\n💾 Saving to database...")
    # Store the results into a file database
    # Reset index to make 'date' a regular column for DuckDB
    df_for_db = df.reset_index()

    with tqdm(total=4, desc="Database operations") as pbar:
        con = duckdb.connect(database='sales_timeseries.db', read_only=False)
        pbar.set_description("Connected to database")
        pbar.update(1)
        
        con.execute("DROP TABLE IF EXISTS sales_data")
        pbar.set_description("Dropped existing table")
        pbar.update(1)
        
        con.execute("CREATE TABLE sales_data AS SELECT * FROM df_for_db")
        pbar.set_description("Created table with data")
        pbar.update(1)
        
        con.execute("CREATE INDEX idx_date ON sales_data (date)")
        con.execute("CREATE INDEX idx_customer ON sales_data (customer_number)")
        con.execute("CREATE INDEX idx_receipt ON sales_data (receipt_number)")
        con.execute("CREATE INDEX idx_product ON sales_data (product_id)")
        pbar.set_description("Created indexes")
        pbar.update(1)
        
        con.close()

    print("\n✅ Data saved to sales_timeseries.db database file")
    print(f"📊 Total records: {len(df_for_db):,}")
    print(f"💰 Total revenue: SGD ${df['total_amount_per_product_sgd'].sum():,.2f}")
    print(f"👥 Unique customers: {df['customer_number'].nunique():,}")
    print(f"🧾 Unique receipts: {df['receipt_number'].nunique():,}")
    print("🎉 Database creation complete!")


if __name__ == "__main__":
    import sys
    import os
    
    print("🏪 Retail TimeSeries Database Generator")
    print("=" * 40)
    
    # Check if we should launch the menu directly
    if len(sys.argv) > 1 and sys.argv[1] == "--menu":
        try:
            from retail_menu import RetailMenu
            menu = RetailMenu()
            menu.main_menu()
        except ImportError:
            print("❌ retail_menu.py not found. Creating database only...")
            if not os.path.exists("sales_timeseries.db"):
                generate_initial_data()
        sys.exit(0)
    
    if os.path.exists("sales_timeseries.db"):
        print("📊 Database already exists!")
        print("🔄 Options:")
        print("   1. Delete and recreate database")
        print("   2. Launch retail menu")
        print("   3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            os.remove("sales_timeseries.db")
            print("🗑️  Deleted existing database")
            print("⚡ Generating new database...")
            generate_initial_data()
            print("✅ Database recreation complete!")
        elif choice == '2':
            try:
                from retail_menu import RetailMenu
                menu = RetailMenu()
                menu.main_menu()
            except ImportError:
                print("❌ retail_menu.py not found!")
        else:
            print("👋 Goodbye!")
            sys.exit(0)
    else:
        print("⚡ Generating comprehensive retail database...")
        generate_initial_data()
        print("✅ Database generation complete!")
        print("📁 Check 'sales_timeseries.db' for your data")
        
        # Ask if user wants to launch menu
        launch_menu = input("\n🚀 Launch retail menu? (y/n): ").strip().lower()
        if launch_menu in ['y', 'yes']:
            try:
                from retail_menu import RetailMenu
                menu = RetailMenu()
                menu.main_menu()
            except ImportError:
                print("❌ retail_menu.py not found!")
