import sys
import pexpect

def test():
    child = pexpect.spawn('python main.py', encoding='utf-8')
    child.expect(r'Choose theory \(default ZFC\):')
    child.sendline('NT')
    child.expect(r'Enable foundational proof logging to proofs.html\? \[y/N\]:')
    child.sendline('N')

    child.expect(r'ITP 0> ')
    child.sendline('def_r 2 ≠ x y ¬ x = y')
    
    child.expect(r'ITP 0> ')
    child.sendline('cf goal ≠(0, 1)')
    
    child.expect(r'ITP 0> ')
    child.sendline('show')
    
    output = child.before
    print(output)
    child.sendline('exit')
    
if __name__ == '__main__':
    test()
