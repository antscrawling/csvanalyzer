import duckdb
import pandas as pd
import numpy as np
import os
import sys
import json
#from openai import OpenAI  # Ensure you have the OpenAI Python library installed
import requests  # Ensure you have the Claude Python library installed
from pprint import pprint

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def add_static_parameters()->dict:
    """Add static parameters to database"""
    # Create DataFrame for day of week
    params = load_parameters('parameter.db')
    day_numbers = [1, 2, 3, 4, 5, 6, 7]  # Monday=1, Sunday=7
    day_names = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    df_days = pd.DataFrame({
        'day_of_week': day_numbers,
        'day_of_week_text': [day_names[x - 1] for x in day_numbers],
        'day_of_week_sin': np.sin(2 * np.pi * pd.Series(day_numbers) / 7),
        'day_of_week_cos': np.cos(2 * np.pi * pd.Series(day_numbers) / 7)
    })

    # Create DataFrame for months
    month_numbers = list(range(1, 13))
    month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                   'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    df_months = pd.DataFrame({
        'month': month_numbers,
        'month_text': [month_names[x - 1] for x in month_numbers],
        'month_sin': np.sin(2 * np.pi * pd.Series(month_numbers) / 12),
        'month_cos': np.cos(2 * np.pi * pd.Series(month_numbers) / 12)
    })

    # Create DataFrame for time of day
    time_of_day = np.arange(0, 24)
    df_time = pd.DataFrame({
        'time_of_day': time_of_day,
        'time_of_day_sin': np.sin(2 * np.pi * pd.Series(time_of_day) / 24),
        'time_of_day_cos': np.cos(2 * np.pi * pd.Series(time_of_day) / 24)
    })

    # Combine both DataFrames
    df = pd.concat([df_days, df_months], axis=1)

    # Save DataFrame to dictionary
  
    for column in df.columns:
        params[column] = {
            "key": column,
            "value": df[column].dropna().tolist(),
            "alternative_key": "",
            "alternative_value": ""
        }
        # Add time of day parameters
    for column in df_time.columns:
        params[f"time_of_day_{column}"] = {
            "key": f"time_of_day_{column}",
            "value": df_time[column].dropna().tolist(),
            "alternative_key": "",
            "alternative_value": ""
        }
    
    
    data_elements = {
    "person_id": "integer (max 9,223,372,036,854,775,807)",  # 64-bit int
    "first_name": "character (50)",
    "last_name": "character (50)",
    "sex": "character (1)",                 # M/F
    "gender": "character (20)",             # Male/Female/Other
    "age": "integer (0-120)",
    "date_of_birth": "date (YYYY-MM-DD)",
    "marital_status": "character (20)",
    "nationality": "character (50)",
    "education_level": "character (50)",

    "city": "character (100)",
    "state": "character (100)",
    "country": "character (2)",             
    "zip_code": "character (15)",

    "email": "character (100)",
    "phone_number": "character (20)",

    "income": "float (up to 1e9.99)",      
    "expense": "float (up to 1e9.99)",
    "savings": "float (up to 1e12.99)",
    "debt": "float (up to 1e12.99)",
    "employment_status": "character (30)",
    "job_title": "character (100)",
    "industry": "character (100)",

    "household_size": "integer (0-20)",
    "vehicle_owned": "character (3)",      
    "home_ownership_status": "character (10)", 
    "internet_usage_hours": "float (0-24)",

    "hobbies": "character (255)",

    "height_cm": "float (0-300.0)",
    "weight_kg": "float (0-500.0)",
    "blood_type": "character (3)",          
    "smoker_status": "character (3)",       
    "alcohol_consumption_frequency": "character (20)",

    "account_created_date": "date (YYYY-MM-DD)",
    "last_login_date": "date (YYYY-MM-DD)",
    "transaction_count": "integer (0-1e9)",
    "average_transaction_value": "float (up to 1e9.99)",
    "loyalty_points": "integer (0-1e9)"
    }

    for key, value in data_elements.items():
        # Split the value string into parts
        value_parts = value.split(" ", 1)
        params[key] = {
            "key": key,
            "value": value_parts[0],  # Map the first word to 'value'
            "alternative_key": value_parts[1] if len(value_parts) > 1 else "",  # Map the rest to 'alternative_key'
            "alternative_value": ""
        }    
    save_parameters('parameter.db', params)
    return params
    
def add_country_codes(cc: dict[str,str])->None:
    """Add country codes to parameters"""
    params = load_parameters('parameter.db')
    for code, country in cc.items():
        # Add each country code as a unique entry
        
        params[code] = {
            "key": f"countries_{code}",
            "value": "character 2",
            "alternative_key": code,
            "alternative_value": country
        }
    save_parameters('parameter.db', params)

def load_parameters(param_file):
    """Load parameters from database"""
    params = {}
    try:
        # Check if database exists first
        if not os.path.exists(param_file):
            print(f"Parameter file {param_file} not found. Creating new database...")
            create_parameter_db(param_file)
            return params
            
        with duckdb.connect(param_file, read_only=True) as con:
            cur = con.cursor()
            cur.execute("SELECT key, value, alternative_key, alternative_value FROM parameters")
            rows = cur.fetchall()
            for row in rows:
                params[row[0]] = {
                    "key": row[0],
                    'value': row[1],
                    'alternative_key': row[2],
                    'alternative_value': row[3]
                }
    except Exception as e:
        print(f"Error loading parameters: {e}")
        print("Creating new parameter database...")
        # Remove corrupted file if it exists
        if os.path.exists(param_file):
            os.remove(param_file)
        create_parameter_db(param_file)
    return params

def save_df_tofile(dataframe: pd.DataFrame, parameters: dict):
    """Save DataFrame to DuckDB database with all columns"""
    try:
        with duckdb.connect('analyzed_database.db') as con:
            # Create table with all DataFrame columns
            columns = dataframe.columns.tolist()
            
            # Generate CREATE TABLE statement dynamically based on DataFrame columns
            column_definitions = []
            for col in columns:
                if dataframe[col].dtype in ['int64', 'int32']:
                    column_definitions.append(f"{col} INTEGER")
                elif dataframe[col].dtype in ['float64', 'float32']:
                    column_definitions.append(f"{col} FLOAT")
                elif dataframe[col].dtype == 'datetime64[ns]':
                    column_definitions.append(f"{col} TIMESTAMP")
                elif dataframe[col].dtype == 'bool':
                    column_definitions.append(f"{col} BOOLEAN")
                else:
                    column_definitions.append(f"{col} VARCHAR")
            
            create_table_sql = f"""
                CREATE OR REPLACE TABLE analyzed_data (
                    {', '.join(column_definitions)}
                )
            """
            
            con.execute(create_table_sql)
            print("Table 'analyzed_data' created successfully.")
            
            # Insert DataFrame data into the table
            placeholders = ', '.join(['?' for _ in columns])
            insert_sql = f"INSERT INTO analyzed_data ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Convert DataFrame to list of tuples for insertion
            data_tuples = []
            for _, row in dataframe.iterrows():
                data_tuples.append(tuple(row.tolist()))
            
            con.executemany(insert_sql, data_tuples)
            print(f"Inserted {len(data_tuples)} rows into 'analyzed_data' table.")
            
            # Also save parameters to a separate table
            con.execute("""
                CREATE OR REPLACE TABLE analysis_parameters (
                    key VARCHAR,
                    value VARCHAR,
                    alternative_key VARCHAR,
                    alternative_value VARCHAR
                )
            """)
            
            for key, value in parameters.items():
                if isinstance(value, dict):
                    con.execute(
                        "INSERT INTO analysis_parameters (key, value, alternative_key, alternative_value) VALUES (?, ?, ?, ?)",
                        [
                            value.get('key', key),
                            str(value.get('value', '')),
                            value.get('alternative_key', ''),
                            value.get('alternative_value', '')
                        ]
                    )
                else:
                    con.execute(
                        "INSERT INTO analysis_parameters (key, value, alternative_key, alternative_value) VALUES (?, ?, ?, ?)",
                        [key, str(value), '', '']
                    )
            
            print("Parameters saved to 'analysis_parameters' table.")
            
    except Exception as e:
        print(f"Error saving DataFrame to database: {e}")


def create_parameter_db(param_file):
    """Create a parameter database if it doesn't exist"""
    if not os.path.exists(param_file):
        with duckdb.connect(param_file) as con:
            con.execute("""
                CREATE TABLE parameters (
                    key VARCHAR,
                    value VARCHAR,
                    alternative_key VARCHAR,
                    alternative_value VARCHAR
                )
            """)
            print("Parameter database created.")
    else:
        print("Parameter database already exists.")


def save_parameters(param_file, params):
    """Save parameters to DuckDB database"""
    # Remove old table if exists to avoid duplicates
    with duckdb.connect(param_file) as con: 
        con.execute("CREATE TABLE IF NOT EXISTS parameters (key VARCHAR, value VARCHAR, alternative_key VARCHAR, alternative_value VARCHAR)")
        con.execute("DELETE FROM parameters")

        if isinstance(params, dict):
            # Handle dictionary input
            for key, value in params.items():
                if isinstance(value, str):
                    value = {
                        'key': key,
                        'value': value,
                        'alternative_key': '',
                        'alternative_value': ''
                    }
                con.execute(
                    "INSERT INTO parameters (key, value, alternative_key, alternative_value) VALUES (?, ?, ?, ?)",
                    [value.get('key', key), value.get('value', ''), value.get('alternative_key', ''), value.get('alternative_value', '')]
                )
        elif isinstance(params, list):
            # Handle list input
            for item in params:
                if isinstance(item, dict):
                    con.execute(
                        "INSERT INTO parameters (key, value, alternative_key, alternative_value) VALUES (?, ?, ?, ?)",
                        [
                            item.get('key', ''),
                            item.get('value', ''),
                            item.get('alternative_key', ''),
                            item.get('alternative_value', '')
                        ]
                    )
                else:
                    raise ValueError("List items must be dictionaries.")
        else:
            raise TypeError("params must be a dictionary or a list of dictionaries.")
            

def main(country_codes  : dict):
    params = add_static_parameters()
    df = None  # Initialize df variable
    while True: 
        print("""=== CSV Data Analyzer ===
            1. Create Parameter 
            2. Add a Parameter
            3. Edit a Parameter
            40. Delete a Parameter
            42. Add Country Codes
            43. Add Static Parameters
            5. Display Parameters
            6. Load a CSV File from Directory
            7. Analyze data with ChatGPT
            8. Display Proposed Analysis on data elements
            9. Manual Analysis 
            0. Exit
          """)
        choice = input("Select an option (1-9): ").strip()
        if choice == '1':
            create_parameter_db('parameter.db')
        elif choice == '8':
            display_proposed_analysis(dataframe=df,json_file='chatgpt_results.json')   
        elif choice == '9':
            manual_analysis(dataframe=df, parameters=params)
            save_df_tofile(dataframe=df,parameters=params)
        elif choice == '2':
            key = input("Enter parameter key: ").strip()
            value = input("Enter parameter value: ").strip()
            alt_key = input("Enter alternative key (optional): ").strip()
            alt_value = input("Enter alternative value (optional): ").strip()
            params = load_parameters('parameter.db')
            params[key] = {
                'key': key,
                'value': value,
                'alternative_key': alt_key,
                'alternative_value': alt_value
            }
            save_parameters('parameter.db', params)
            print("Parameter added.")
        elif choice == '42':
            add_country_codes(country_codes)
        elif choice == '43':
            add_static_parameters()
        elif choice == '5':
            params = load_parameters('parameter.db')
            print("Loaded Parameters:")
            for key, value in params.items():
                print(f"{key}: {value}")
        elif choice == '3':
            params = {
                'example_key': 'example_value',
                'another_key': 'another_value'
            }
            save_parameters('parameter.db', params)
            print("Parameters saved.")
        elif choice == '40':
            #...analyze_csv()
            #delete a parameter
            key_to_delete = input("Enter the parameter key to delete: ").strip()
            params = load_parameters('parameter.db')
            if key_to_delete in params:
                del params[key_to_delete]
                save_parameters('parameter.db', params)
                print("Parameter deleted.")
            else:
                print("Parameter not found.")
        elif choice == '6':
            # Load a CSV file
            #csv_file = input("Enter the CSV file name (with .csv extension): ").strip()
            #open a os dialog to choose a file
            print("Available CSV files in current directory:")
            csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
            for i, file in enumerate(csv_files):
                print(f"{i+1}. {file}")
            if not csv_files:
                print("No CSV files found in current directory.")
                continue
            choice = input(f"Select a file (1-{len(csv_files)}) or enter filename: ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(csv_files):
                    csv_file = csv_files[index]
                else:
                    print("Invalid choice.")
                    continue
            else:
                csv_file = choice
            if not os.path.isfile(csv_file):
                print("File not found.")
                continue
            df = pd.read_csv(csv_file)
            print("CSV Data Loaded:")
            print(df.head())
            print(f"DataFrame shape: {df.shape}")
            print("CSV file loaded successfully. You can now use option 7 to analyze the data.")
        elif choice == '7':
            if df is None:
                print("Please load a CSV file first using option 6.")
                continue
            analyze_csv(dataframe=df, params=params)
        elif choice == '0':
            print("Exiting...")
            break
            sys.exit(0)

def manual_analysis(dataframe: pd.DateOffset, parameters:dict):
    for column, dtype in parameters.items():
        if column in dataframe.columns:
            try:
                if ['date','hour','datetijme'] in column.lower() :
                    dataframe[column] = pd.to_datetime(dataframe[column], errors='coerce', format='%Y-%m-%d %H:%M:%S')
                
                elif 'integer' in dtype.lower():
                    dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce', downcast='integer')
                elif 'float' in dtype.lower():
                    dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce', downcast='float')
                elif 'character' in dtype.lower() or 'string' in dtype.lower():
                    dataframe[column] = dataframe[column].astype(str)
                else:
                    print(f"Unknown data type for column {column}: {dtype}")
            except Exception as e:
                print(f"Error converting column {column} to {dtype}: {e}")
    pprint(dataframe)
def analyze_csv(dataframe: pd.DataFrame, params: dict):
    """Analyze CSV data for sales trends""" 
   
    # Load CSV data
    df = dataframe
    params = params
    myparams = []
    mycolumns = []
    print("Parameter File:")
    
    if df is None or df.empty:
        print("No data to analyze.")
        return
    print("CSV Data Loaded:")
    for key, value  in params.items():
        myparams.append(f"{key}: {value}")
    #pprint(df.head())
    #analyze the header of the csv file
    print("\nCSV Header:")
    mycolumns = df.columns.tolist()
    for column in mycolumns:
        print(f" - {column}")
    myresults = {}
    try:
        json_response = get_similar_columns_chatgpt(paramlist=myparams, columnlist=mycolumns)
        myresults = json.loads(json_response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {json_response}")
        myresults = {"error": "Failed to parse JSON response"}
    
    with open('chatgpt_results.json', 'w') as f:
        json.dump(myresults, f, indent=4)
        
    #read the json file, amend the dataframe according to the header row in this list that matched.
    with open('chatgpt_results.json', 'r') as f:
        json_data = json.load(f)
        for column in df.columns:
            if column in json_data:
                
                #include hours, minutes, seconds if present
                if 'date' in column.lower() or 'time' in column.lower():
                    df[column] = pd.to_datetime(df[column], errors='coerce', format='%Y-%m-%d %H:%M:%S')
                df[column] = df[column].astype(json_data[column])
    # print the dataframe info
    print("\nAnalyzed DataFrame Info:")
    print(df.info())
    
    
def get_similar_columns_chatgpt(paramlist : list, columnlist : list)->list:
    """Analyze CSV data and compare with saved parameters using ChatGPT API."""
    # Load CSV data    
    #client = OpenAI() 

    url = "https://models.github.ai/inference/chat/completions"
    # Prepare data for ChatGPT API
    prompt = f"""Generate a JSON object that maps Column headers: {columnlist} with similar descriptions from the parameters: {paramlist}. 
    
    Return only a valid JSON object in this format:
    {{
        "column_name_1": "matching_parameter_description",
        "column_name_2": "matching_parameter_description",
        ...
    }}
    
    Do not include any other text or explanation, just the JSON object."""
      
    # Call ChatGPT API
    try:
        headers = {
         "Authorization": f"Bearer {GITHUB_TOKEN}",
         "Content-Type": "application/json",
         "Accept": "application/vnd.github+json",
         "X-GitHub-Api-Version": "2022-11-28"
            }
        data = {
            "model": "DeepSeek-V3-0324",
            "messages": [{"role": "user", "content": f"{prompt}"}]
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print(result)
            # Extract the content from the response
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                # Clean up the content by removing markdown code blocks
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                return content
            else:
                return "No response content found"
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return "API request failed"
      
                                        
    except Exception as e:
        print(f"Error calling ChatGPT API: {e}")

def display_proposed_analysis(dataframe, json_file: str):
    """Display proposed analysis from JSON file"""
    if not os.path.exists(json_file):
        print(f"File {json_file} not found.")
        return
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
            print("\nProposed Analysis:")
            for column, dtype in data.items():
                if column in dataframe.columns:
                    print(f" - {column}: {dtype}")
                    if 'date' in column.lower() or 'time' in column.lower():
                        print(f"   (This column appears to be a date/time field.)")
                        dataframe[column] = pd.to_datetime(dataframe[column], errors='coerce', format='%Y-%m-%d %H:%M:%S')
        print("\nDataFrame after applying proposed analysis:")
        print(dataframe.info())
        #print all the columns and first 5 rows
        print(dataframe.head())
        
        
        return dataframe
    except Exception as     e:
        print(f"Error reading {json_file}: {e}")
        
if __name__ == "__main__":
    countries =  {
    "AF": "Afghanistan",
    "AX": "Åland Islands",
    "AL": "Albania",
    "DZ": "Algeria",
    "AS": "American Samoa",
    "AD": "Andorra",
    "AO": "Angola",
    "AI": "Anguilla",
    "AQ": "Antarctica",
    "AG": "Antigua and Barbuda",
    "AR": "Argentina",
    "AM": "Armenia",
    "AW": "Aruba",
    "AU": "Australia",
    "AT": "Austria",
    "AZ": "Azerbaijan",
    "BS": "Bahamas",
    "BH": "Bahrain",
    "BD": "Bangladesh",
    "BB": "Barbados",
    "BY": "Belarus",
    "BE": "Belgium",
    "BZ": "Belize",
    "BJ": "Benin",
    "BM": "Bermuda",
    "BT": "Bhutan",
    "BO": "Bolivia (Plurinational State of)",
    "BQ": "Bonaire, Sint Eustatius and Saba",
    "BA": "Bosnia and Herzegovina",
    "BW": "Botswana",
    "BV": "Bouvet Island",
    "BR": "Brazil",
    "IO": "British Indian Ocean Territory",
    "BN": "Brunei Darussalam",
    "BG": "Bulgaria",
    "BF": "Burkina Faso",
    "BI": "Burundi",
    "CV": "Cabo Verde",
    "KH": "Cambodia",
    "CM": "Cameroon",
    "CA": "Canada",
    "KY": "Cayman Islands",
    "CF": "Central African Republic",
    "TD": "Chad",
    "CL": "Chile",
    "CN": "China",
    "CX": "Christmas Island",
    "CC": "Cocos (Keeling) Islands",
    "CO": "Colombia",
    "KM": "Comoros",
    "CG": "Congo",
    "CD": "Congo (Democratic Republic of the)",
    "CK": "Cook Islands",
    "CR": "Costa Rica",
    "CI": "Côte d’Ivoire",
    "HR": "Croatia",
    "CU": "Cuba",
    "CW": "Curaçao",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DK": "Denmark",
    "DJ": "Djibouti",
    "DM": "Dominica",
    "DO": "Dominican Republic",
    "EC": "Ecuador",
    "EG": "Egypt",
    "SV": "El Salvador",
    "GQ": "Equatorial Guinea",
    "ER": "Eritrea",
    "EE": "Estonia",
    "SZ": "Eswatini",
    "ET": "Ethiopia",
    "FK": "Falkland Islands (Malvinas)",
    "FO": "Faroe Islands",
    "FJ": "Fiji",
    "FI": "Finland",
    "FR": "France",
    "GF": "French Guiana",
    "PF": "French Polynesia",
    "TF": "French Southern Territories",
    "GA": "Gabon",
    "GM": "Gambia",
    "GE": "Georgia",
    "DE": "Germany",
    "GH": "Ghana",
    "GI": "Gibraltar",
    "GR": "Greece",
    "GL": "Greenland",
    "GD": "Grenada",
    "GP": "Guadeloupe",
    "GU": "Guam",
    "GT": "Guatemala",
    "GG": "Guernsey",
    "GN": "Guinea",
    "GW": "Guinea-Bissau",
    "GY": "Guyana",
    "HT": "Haiti",
    "HM": "Heard Island and McDonald Islands",
    "VA": "Holy See",
    "HN": "Honduras",
    "HK": "Hong Kong",
    "HU": "Hungary",
    "IS": "Iceland",
    "IN": "India",
    "ID": "Indonesia",
    "IR": "Iran (Islamic Republic of)",
    "IQ": "Iraq",
    "IE": "Ireland",
    "IM": "Isle of Man",
    "IL": "Israel",
    "IT": "Italy",
    "JM": "Jamaica",
    "JP": "Japan",
    "JE": "Jersey",
    "JO": "Jordan",
    "KZ": "Kazakhstan",
    "KE": "Kenya",
    "KI": "Kiribati",
    "KP": "Korea (Democratic People’s Republic of)",
    "KR": "Korea (Republic of)",
    "KW": "Kuwait",
    "KG": "Kyrgyzstan",
    "LA": "Lao People’s Democratic Republic",
    "LV": "Latvia",
    "LB": "Lebanon",
    "LS": "Lesotho",
    "LR": "Liberia",
    "LY": "Libya",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "MO": "Macao",
    "MG": "Madagascar",
    "MW": "Malawi",
    "MY": "Malaysia",
    "MV": "Maldives",
    "ML": "Mali",
    "MT": "Malta",
    "MH": "Marshall Islands",
    "MQ": "Martinique",
    "MR": "Mauritania",
    "MU": "Mauritius",
    "YT": "Mayotte",
    "MX": "Mexico",
    "FM": "Micronesia (Federated States of)",
    "MD": "Moldova (Republic of)",
    "MC": "Monaco",
    "MN": "Mongolia",
    "ME": "Montenegro",
    "MS": "Montserrat",
    "MA": "Morocco",
    "MZ": "Mozambique",
    "MM": "Myanmar",
    "NA": "Namibia",
    "NR": "Nauru",
    "NP": "Nepal",
    "NL": "Netherlands",
    "NC": "New Caledonia",
    "NZ": "New Zealand",
    "NI": "Nicaragua",
    "NE": "Niger",
    "NG": "Nigeria",
    "NU": "Niue",
    "NF": "Norfolk Island",
    "MK": "North Macedonia",
    "MP": "Northern Mariana Islands",
    "NO": "Norway",
    "OM": "Oman",
    "PK": "Pakistan",
    "PW": "Palau",
    "PS": "Palestine, State of",
    "PA": "Panama",
    "PG": "Papua New Guinea",
    "PY": "Paraguay",
    "PE": "Peru",
    "PH": "Philippines",
    "PN": "Pitcairn",
    "PL": "Poland",
    "PT": "Portugal",
    "PR": "Puerto Rico",
    "QA": "Qatar",
    "RE": "Réunion",
    "RO": "Romania",
    "RU": "Russian Federation",
    "RW": "Rwanda",
    "BL": "Saint Barthélemy",
    "SH": "Saint Helena, Ascension and Tristan da Cunha",
    "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia",
    "MF": "Saint Martin (French part)",
    "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines",
    "WS": "Samoa",
    "SM": "San Marino",
    "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia",
    "SN": "Senegal",
    "RS": "Serbia",
    "SC": "Seychelles",
    "SL": "Sierra Leone",
    "SG": "Singapore",
    "SX": "Sint Maarten (Dutch part)",
    "SK": "Slovakia",
    "SI": "Slovenia",
    "SB": "Solomon Islands",
    "SO": "Somalia",
    "ZA": "South Africa",
    "GS": "South Georgia and the South Sandwich Islands",
    "SS": "South Sudan",
    "ES": "Spain",
    "LK": "Sri Lanka",
    "SD": "Sudan",
    "SR": "Suriname",
    "SJ": "Svalbard and Jan Mayen",
    "SE": "Sweden",
    "CH": "Switzerland",
    "SY": "Syrian Arab Republic",
    "TW": "Taiwan (Province of China)",
    "TJ": "Tajikistan",
    "TZ": "Tanzania, United Republic of",
    "TH": "Thailand",
    "TL": "Timor-Leste",
    "TG": "Togo",
    "TK": "Tokelau",
    "TO": "Tonga",
    "TT": "Trinidad and Tobago",
    "TN": "Tunisia",
    "TR": "Türkiye",
    "TM": "Turkmenistan",
    "TC": "Turks and Caicos Islands",
    "TV": "Tuvalu",
    "UG": "Uganda",
    "UA": "Ukraine",
    "AE": "United Arab Emirates",
    "GB": "United Kingdom of Great Britain and Northern Ireland",
    "US": "United States of America",
    "UM": "United States Minor Outlying Islands",
    "UY": "Uruguay",
    "UZ": "Uzbekistan",
    "VU": "Vanuatu",
    "VE": "Venezuela (Bolivarian Republic of)",
    "VN": "Viet Nam",
    "VG": "Virgin Islands (British)",
    "VI": "Virgin Islands (U.S.)",
    "WF": "Wallis and Futuna",
    "EH": "Western Sahara",
    "YE": "Yemen",
    "ZM": "Zambia",
    "ZW": "Zimbabwe"
}
    
    main(country_codes=countries)