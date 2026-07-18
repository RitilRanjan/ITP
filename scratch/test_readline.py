import pexpect

def test():
    child = pexpect.spawn('python main.py', encoding='utf-8')
    child.expect(r'Choose theory \(default ZFC\):')
    child.sendline('ZFC')
    child.expect(r'Enable foundational proof logging to proofs.html\? \[y/N\]:')
    child.sendline('N')

    child.expect(r'ITP 0> ')
    child.sendline('invalidcmd')
    child.expect(r'ITP 0> ')
    child.sendline('cv a')
    child.expect(r'ITP 0> ')
    child.sendline('undo')
    child.expect(r'ITP 0> ')
    child.sendline('show')
    child.expect(r'ITP 0> ')
    child.sendline('exit')
    print("Test passed!")

if __name__ == '__main__':
    test()
