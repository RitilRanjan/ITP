with open('scratch/found_rw.py', 'r') as f:
    text = f.read()
import re
match = re.search(r'new_rw = """(.*?)"""\n\ncontent = content.replace', text, flags=re.DOTALL)
if match:
    with open('scratch/handle_rw_clean.py', 'w') as f:
        f.write(match.group(1))
    print("Extracted handle_rw")
else:
    print("Could not extract handle_rw")
