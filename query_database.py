import duckdb

# Connect to the database file

with duckdb.connect('sales_timeseries.db',read_only=True) as con:
    # Query the data
    print("=== Database Schema === ")
    print("DB = sales_timeseries.db")
    print("TABLE = sales_data")
    result = con.execute("DESCRIBE sales_data").fetchall()
    for row in result:
        print(f"{row[0]}: {row[1]}")

    print("\n=== Sample Data ===")
    df = con.execute("SELECT * FROM sales_data").df()
    #print(df)
    #print customer id , age, and sales for each age group
    
    #print(df['customer_number'][(df['age'] > 25) & (df['age'] <= 50)])
    print(df['age'][(df['age'] > 25) & (df['age'] <= 50)])
    print(df['total_amount_per_product_sgd'][(df['age'] > 25) & (df['age'] <= 50)])
