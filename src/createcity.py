import json

def main():
    with open('cities.json', 'r') as f:
        cities = json.load(f)
    
    for city in cities:
        print(city['name'], city['country'])
        
if __name__ == "__main__":
    main()
    