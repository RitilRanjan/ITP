import re

with open('scratch/found_swap.txt', 'r') as f:
    text = f.read()

# find where "741: " starts
lines = text.split('\n')
clean_lines = []
for line in lines:
    match = re.match(r'^\d+:\s?(.*)$', line)
    if match:
        clean_lines.append(match.group(1))

with open('scratch/clean_swap.py_out', 'w') as f:
    f.write('\n'.join(clean_lines))
