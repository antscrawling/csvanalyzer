import json
import pandas as pd
import numpy as np
import duckdb
from datetime import datetime, timedelta
from tqdm import tqdm

def main():
    generate_initial_data()

def generate_initial_data(chunks=10):
    print("🏪 Retail Sales Database Generator")
    print("=" * 40)

    # Set a random seed for reproducibility
    np.random.seed(142)

    # Create a date range with daily frequency (split into chunks)
    start_date = '1900-01-01'
    end_date = '2025-09-02'
    
    # Calculate full date range first to get total days
    full_range = pd.date_range(start=start_date, end=end_date, freq='D')
    total_days = len(full_range)
    chunk_size = total_days // chunks
    
    print(f"📅 Date range: {total_days} days (processing in {chunks} chunks)")

    # Load dependencies
    with open('src/cities.json') as f:
        cities = json.load(f)
    
    # Product catalog and other static data definitions remain the same
    genders = [{"F":0},{"M": 1}]
    products = [
        {'product_id': 100, 'product_name': 'iPhone 13', 'unit_price': 999.00},
        {'product_id': 200, 'product_name': 'Samsung Galaxy S21', 'unit_price': 899.00},
        {'product_id': 300, 'product_name': 'Google Pixel 6', 'unit_price': 599.00},
        {'product_id': 400, 'product_name': 'OnePlus 9', 'unit_price': 729.00},
        {'product_id': 500, 'product_name': 'Xiaomi Mi 11', 'unit_price': 749.00},
        {'product_id': 600, 'product_name': 'Sony Xperia 5', 'unit_price': 899.00},
        {'product_id': 700, 'product_name': 'Oppo Find X3', 'unit_price': 1149.00},
        {'product_id': 800, 'product_name': 'Nokia 8.3', 'unit_price': 699.00},
        {'product_id': 900, 'product_name': 'Realme GT', 'unit_price': 599.00},
        {'product_id': 1000, 'product_name': 'Water', 'unit_price': 2.00},
        {'product_id': 1100, 'product_name': 'Sparkling Water', 'unit_price': 2.50},
        {'product_id': 1200, 'product_name': 'Iced Tea', 'unit_price': 3.00},
        {'product_id': 1300, 'product_name': 'MacBook Pro', 'unit_price': 2399.00},
        {'product_id': 1400, 'product_name': 'Dell XPS 13', 'unit_price': 1499.00},
        {'product_id': 1500, 'product_name': 'HP Spectre x360', 'unit_price': 1699.00},
        {'product_id': 1600, 'product_name': 'Lenovo ThinkPad X1', 'unit_price': 1899.00},
        {'product_id': 1700, 'product_name': 'iPad Pro', 'unit_price': 1099.00},
        {'product_id': 1800, 'product_name': 'Samsung Galaxy Tab S7', 'unit_price': 849.00},
        {'product_id': 1900, 'product_name': 'Microsoft Surface Pro 7', 'unit_price': 999.00},
        {'product_id': 2000, 'product_name': 'Amazon Kindle', 'unit_price': 89.00}
    ]
    transaction_types = [{'transaction_type_id':100,'transaction_type':'Sales','transaction_desc':'Product Sale'},
                         {'transaction_type_id':200,'transaction_type':'Refund','transaction_desc':'Product Refund'},
                         {'transaction_type_id':300,'transaction_type':'Exchange','transaction_desc':'Product Exchange'}
                        ]
    
    # Initialize database
    con = duckdb.connect(database='sales_timeseries.db', read_only=False)
    con.execute("DROP TABLE IF EXISTS sales_data")
    print("💾 Database initialized")
    
    # Create table schema first
    schema_sql = """
    CREATE TABLE sales_data (
        date INTEGER,
        transaction_id INTEGER,
        transaction_desc INTEGER,
        customer_number INTEGER,
        age INTEGER,
        gender INTEGER,
        receipt_number INTEGER,
        product_id INTEGER,
        product_name INTEGER,
        units_sold INTEGER,
        unit_price_sgd DECIMAL(10,2),
        total_amount_per_product_sgd DECIMAL(10,2),
        receipt_total_sgd DECIMAL(10,2),
        country_id INTEGER,
        country INTEGER,
        city INTEGER,
        discount_period INTEGER,
        discount_percentage INTEGER,
        discount_applied INTEGER
    )
    """
    con.execute(schema_sql)
    
    # Process in chunks
    customer_id = 100001
    receipt_id = 200001
    customer_ages = {}
    
    # Process data in chunks
    for chunk_idx in range(chunks):
        chunk_start = chunk_idx * chunk_size
        chunk_end = (chunk_idx + 1) * chunk_size if chunk_idx < chunks - 1 else total_days
        
        # Get date range for this chunk
        date_chunk = full_range[chunk_start:chunk_end]
        
        print(f"\n🔄 Processing chunk {chunk_idx+1}/{chunks} ({len(date_chunk)} days)")
        
        # Generate transactions for this chunk
        transactions = []
        
        for date in tqdm(date_chunk, desc=f"Chunk {chunk_idx+1}/{chunks}"):
            year = date.year * 1000
            month = date.month * 100
            day = date.day * 10
            
            # Number of receipts per day
            day_of_week = date.weekday()
            if day_of_week >= 5:  # Weekend
                num_receipts = np.random.randint(20, 40)
            else:  # Weekday
                num_receipts = np.random.randint(30, 60)
            
            # Generate receipts logic (same as before)
            for receipt in range(num_receipts):
                # Assign age to customer if not already assigned
                if customer_id not in customer_ages:
                    # Realistic age distribution: more customers in 25-45 range
                    age_ranges = [18, 25, 35, 45, 55, 65, 75]
                    age_weights = [0.05, 0.20, 0.25, 0.25, 0.15, 0.08, 0.02]
                    age_range_start = np.random.choice(age_ranges, p=age_weights)
                    customer_ages[customer_id] = np.random.randint(age_range_start, min(age_range_start + 10, 80))
                    city = np.random.choice([city['name'] for city in cities])
                    selected_city = next(item for item in cities if item['name'] == city)
                    country_id = selected_city['country_id']
                    country = selected_city['country']
                    transaction_type = transaction_types[np.random.choice([0,1,2], p=[0.95,0.025,0.025])]
                
                # Number of items per receipt
                items_per_receipt = np.random.choice([1, 2, 3, 4], p=[0.4, 0.3, 0.2, 0.1])
                selected_products = np.random.choice(len(products), size=items_per_receipt, replace=False)
                
                receipt_total = 0
                
                for product_idx in selected_products:
                    product = products[product_idx]
                    units_sold = np.random.randint(1, 4)  # 1-3 units per item
                    
                    # Add some price variation (±10%)
                    unit_price = product['unit_price'] * np.random.uniform(0.9, 1.1)
                    
                    total_amount_per_product = units_sold * unit_price
                    receipt_total += total_amount_per_product
                    
                    # Add hour variation throughout the day
                    hour = np.random.randint(6, 22)  # Store hours 6 AM to 10 PM
                    transaction_datetime = date + timedelta(hours=hour, minutes=np.random.randint(0, 60))
                    
                    transactions.append({
                        'date': int(f'{transaction_datetime.year}{transaction_datetime.month:02d}{transaction_datetime.day:02d}{transaction_datetime.hour:02d}{transaction_datetime.minute:02d}'),
                        'transaction_id': transaction_type['transaction_type_id'],
                        'transaction_desc': transaction_type['transaction_type_id'],
                        'customer_number': customer_id,
                        'age': customer_ages[customer_id],
                        'gender': np.random.choice(genders),
                        'receipt_number': receipt_id,
                        'product_id': product['product_id'],
                        'product_name': product['product_id'],
                        'units_sold': units_sold,
                        'unit_price_sgd': round(unit_price, 2),
                        'total_amount_per_product_sgd': round(total_amount_per_product, 2),
                        'receipt_total_sgd': 0,  # Will be filled later
                        'country_id': country_id,
                        'country': country,
                        'city': city,
                        'discount_period': None,
                        'discount_percentage': None,
                        'discount_applied': None
                    })
                
                # Update receipt total for all items in this receipt
                receipt_start_idx = len(transactions) - items_per_receipt
                for i in range(receipt_start_idx, len(transactions)):
                    transactions[i]['receipt_total_sgd'] = round(receipt_total, 2)
                
                customer_id += 1
                receipt_id += 1
            
            # After every 10 days, save to database to avoid memory issues
            if len(transactions) > 50000 or date == date_chunk[-1]:
                print(f"Saving {len(transactions)}, records to database...")
                df_chunk = pd.DataFrame(transactions)
                con.register('df_view', df_chunk)
                con.execute("INSERT INTO sales_data SELECT * FROM df_view")
                transactions = []  # Clear for next batch
        
        print(f"✅ Chunk {chunk_idx+1}/{chunks} completed")
    
    # Create indexes after all data is inserted
    print("\n📊 Creating indexes...")
    con.execute("CREATE INDEX idx_date ON sales_data (date)")
    con.execute("CREATE INDEX idx_customer ON sales_data (customer_number)")
    con.execute("CREATE INDEX idx_receipt ON sales_data (receipt_number)")
    con.execute("CREATE INDEX idx_product ON sales_data (product_id)")
    
    # Get statistics about the table
    print("\n📈 Database statistics:")
    record_count = con.execute("SELECT COUNT(*) FROM sales_data").fetchone()[0]
    revenue = con.execute("SELECT SUM(total_amount_per_product_sgd) FROM sales_data").fetchone()[0]
    unique_customers = con.execute("SELECT COUNT(DISTINCT customer_number) FROM sales_data").fetchone()[0]
    unique_receipts = con.execute("SELECT COUNT(DISTINCT receipt_number) FROM sales_data").fetchone()[0]
    
    con.close()
    
    print("\n✅ Data saved to sales_timeseries.db database file")
    print(f"📊 Total records: {record_count:,}")
    print(f"💰 Total revenue: SGD ${revenue:,.2f}")
    print(f"👥 Unique customers: {unique_customers:,}")
    print(f"🧾 Unique receipts: {unique_receipts:,}")
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
