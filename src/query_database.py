import duckdb

# Connect to the database file

with duckdb.connect("transformed_data.db",read_only=True) as con:
    # Query the data
    
    
    print("TABLE = all_data")
    result = con.execute("SELECT * FROM  all_data").fetchall()
    for row in result:
        print(row)

   # print("\n=== Sample Data ===")
   # df = con.execute("SELECT age,customer_id,gender  FROM sales_data").df()
   # #print(df)
   # #print customer id , age, and sales for each age group
   # 
   # #print(df['customer_number'][(df['age'] > 25) & (df['age'] <= 50)])
   # print(df['age'][(df['age'] > 25) & (df['age'] <= 50)])
   # print(df['total_amount_per_product_sgd'][(df['age'] > 25) & (df['age'] <= 50)])
