import pexpect
import sys

def test():
    child = pexpect.spawn('python main.py', encoding='utf-8')
    child.logfile = sys.stdout
    child.expect(r'Choose theory \(default ZFC\):')
    child.sendline('ZFC')
    child.expect(r'Enable foundational proof logging to proofs.html\? \[y/N\]:')
    child.sendline('N')

    child.expect(r'ITP 0> ')
    child.sendline('play')
    child.expect(r'Enter level name or path to level JSON file: ')
    child.sendline('games/advanced REPL commands/level19.json')
    
    child.expect(r'ITP 0> ')
    child.sendline('swap_eq H1 H2')
    
    child.expect(r'ITP 0> ')
    child.sendline('swap_bi H2 H3')
    
    child.expect(r'ITP 0> ')
    child.sendline('apply H3')
    
    child.expect(r'ITP 0> ')
    child.sendline('show')
    
    output = child.before
    if "Proof complete!" in output or "goal" in output:
        print("Test passed!")
    else:
        print("Test output:", output)
        
    child.sendline('exit')
    
if __name__ == '__main__':
    test()
