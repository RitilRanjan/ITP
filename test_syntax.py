import sys
import re

with open('/Users/ritilranjan/ITP/app.py', 'r') as f:
    content = f.read()

match = re.search(r'st\.components\.v1\.html\("""(.*?)"""', content, re.DOTALL)
if match:
    html = match.group(1)
    with open('/Users/ritilranjan/ITP/test_js.html', 'w') as f:
        f.write(html)
    print("Extracted HTML script")
else:
    print("Not found")
