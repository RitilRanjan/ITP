import pexpect

def test_iff():
    child = pexpect.spawn('python main.py', encoding='utf-8')
    child.expect(r'Choose theory \(default ZFC\):')
    child.sendline('ZFC')
    child.expect(r'Enable foundational proof logging to proofs.html\? \[y/N\]:')
    child.sendline('N')

    child.expect(r'ITP 0> ')
    child.sendline('cV p q')
    child.expect(r'ITP 0> ')
    child.sendline('cf g p ⇔ q')
    child.expect(r'ITP 0> ')
    child.sendline('mission g')
    
    child.expect(r'ITP 1> ')
    child.sendline('iff')
    
    child.expect(r'Now working on Φ⇒Ψ \(')
    child.expect(r'ITP 2> ')
    child.sendline('show')
    child.expect(r'ITP 2> ')
    child.sendline('exit')
    
    print("Test passed!")

if __name__ == '__main__':
    test_iff()
