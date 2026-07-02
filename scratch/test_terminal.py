import pexpect
import sys

child = pexpect.spawn('python main.py', encoding='utf-8')
child.expect('ITP>')
child.sendline('guide')
child.expect('ITP>')
output = child.before
if 'intro2' in output:
    print("intro2 is in guide")
else:
    print("intro2 missing")
child.sendline('exit')
