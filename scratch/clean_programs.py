import json
import os

if os.path.exists('user_programs.json'):
    with open('user_programs.json', 'r') as f:
        data = json.load(f)
    
    new_data = {k: v for k, v in data.items() if not k.startswith('test_')}
    
    with open('user_programs.json', 'w') as f:
        json.dump(new_data, f, indent=4)
    print(f"Removed {len(data) - len(new_data)} test programs.")
