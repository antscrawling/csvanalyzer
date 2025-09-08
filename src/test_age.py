import pandas as pd
import numpy as np
from datetime import timedelta
from tqdm import tqdm

def test_age_field():
    print("🧪 Testing Age Field Addition")
    print("=" * 40)

    # Set a random seed for reproducibility
    np.random.seed(142)

    # Create a small date range for testing
    date_range = pd.date_range(start='2024-01-01', end='2024-01-03', freq='D')
    print(f"📅 Date range: {len(date_range)} days")

    # Product catalog (simplified)
    products = [
        {'product_id': 'P001', 'product_name': 'Coffee', 'unit_price': 4.50},
        {'product_id': 'P002', 'product_name': 'Sandwich', 'unit_price': 8.90}
    ]

    # Generate transaction data
    transactions = []
    customer_id = 100001
    receipt_id = 200001
    
    # Create a dictionary to store customer ages (consistent per customer)
    customer_ages = {}

    print("📅 Generating transaction data...")
    for date in tqdm(date_range, desc="Processing dates"):
        # Small number of receipts for testing
        num_receipts = 5
        
        for receipt in range(num_receipts):
            # Assign age to customer if not already assigned
            if customer_id not in customer_ages:
                # Realistic age distribution
                age_ranges = [18, 25, 35, 45, 55, 65, 75]
                age_weights = [0.05, 0.20, 0.25, 0.25, 0.15, 0.08, 0.02]
                age_range_start = np.random.choice(age_ranges, p=age_weights)
                customer_ages[customer_id] = np.random.randint(age_range_start, min(age_range_start + 10, 80))
            
            # Select a random product
            product = np.random.choice(products)
            units_sold = np.random.randint(1, 3)
            
            # Add hour variation
            hour = np.random.randint(6, 22)
            transaction_datetime = date + timedelta(hours=hour)
            
            transactions.append({
                'date': transaction_datetime,
                'customer_number': customer_id,
                'age': customer_ages[customer_id],
                'receipt_number': receipt_id,
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'units_sold': units_sold,
                'unit_price_sgd': product['unit_price'],
                'total_amount_sgd': units_sold * product['unit_price']
            })
            
            customer_id += 1
            receipt_id += 1

    print("📊 Creating DataFrame...")
    df = pd.DataFrame(transactions)
    
    print(f"Dataset size: {df.shape}")
    print("Age statistics:")
    print(f"  Min age: {df['age'].min()}")
    print(f"  Max age: {df['age'].max()}")
    print(f"  Mean age: {df['age'].mean():.1f}")
    print(f"  Unique ages: {df['age'].nunique()}")
    
    print("\n📋 Sample data with age:")
    print(df[['customer_number', 'age', 'product_name', 'units_sold', 'total_amount_sgd']].head(10))
    
    print("\n👥 Customer age distribution:")
    age_dist = df.groupby('customer_number')['age'].first().value_counts().sort_index()
    print(age_dist.head(10))
    
    print("\n✅ Age field test completed!")

if __name__ == "__main__":
    test_age_field()
