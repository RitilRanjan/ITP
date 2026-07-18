import pexpect

def test():
    child = pexpect.spawn('python main.py', encoding='utf-8')
    child.expect(r'Choose theory \(default ZFC\):')
    child.sendline('NT')
    child.expect(r'Enable foundational proof logging to proofs.html\? \[y/N\]:')
    child.sendline('N')

    child.expect(r'ITP 0> ')
    child.sendline('cf g 0=0')
    child.expect(r'ITP 0> ')
    child.sendline('mission g')
    
    child.expect(r'ITP 1> ')
    child.sendline('apply E1')
    
    child.expect(r'ITP 0> ')
    child.sendline('mission g')
    # Oh wait, we just proved it so it's closed and we are back to 0>
    child.expect(r'ITP 0> ')
    child.sendline('exit')
    
    print("Test passed!")

if __name__ == '__main__':
    test()
