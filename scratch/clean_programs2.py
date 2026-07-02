import json
import os
import shutil

PROGRAMS_DIR = "saved_programs"

# Clean user_programs.json
if os.path.exists('user_programs.json'):
    with open('user_programs.json', 'r') as f:
        data = json.load(f)
    
    new_data = {k: v for k, v in data.items() if k == 'ritil1'}
    
    with open('user_programs.json', 'w') as f:
        json.dump(new_data, f, indent=4)
        
# Clean saved_programs directory
if os.path.exists(PROGRAMS_DIR):
    for d in os.listdir(PROGRAMS_DIR):
        if d != 'ritil1' and os.path.isdir(os.path.join(PROGRAMS_DIR, d)):
            shutil.rmtree(os.path.join(PROGRAMS_DIR, d))
            
print("Cleaned up programs.")
