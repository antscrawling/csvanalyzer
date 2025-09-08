import json

def manipulate_json():
    mydict = {}
    with open('chatgpt_results.json', 'r') as f:
        mydict = json.load(f)
        
        
    for key, value in mydict.items():
        print(f"{key}: {value}")

if __name__ == "__main__":      
    manipulate_json()