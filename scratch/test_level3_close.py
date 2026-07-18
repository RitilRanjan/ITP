import pexpect
import sys

def test():
    child = pexpect.spawn('python main.py', encoding='utf-8')
    child.logfile = sys.stdout
    child.expect(r'Choose theory \(default ZFC\):')
    child.sendline('NT')
    child.expect(r'Enable foundational proof logging to proofs.html\? \[y/N\]:')
    child.sendline('N')

    commands = [
        "cv x u v",
        "def_r 2 u ≠ v ¬ u = v",
        "def_f 0 1 S 0",
        "cf goal 0 ≠ 1",
        "mission goal",
        "fold ≠ (1)",
        "fold 1 (1)",
        "cf f1 ¬∃x S x = 0",
        "apply f1 0_pred",
        "fold ∃ (1) f1 f1_unfolded",  
        "neg- f1_unfolded f2",        
        "intro f2 0",
        "swap_eq (1) f2 goal", # Wait! swap_eq (1) f2 goal
        "show"
    ]
    
    for cmd in commands:
        child.expect(r'ITP \d+> ')
        child.sendline(cmd)
        
    child.expect(r'ITP \d+> ')
    output = child.before
    if "Proof complete!" in output or "goal" not in output:
        print("\n\n=== Test passed! ===")
    else:
        print("\n\n=== Test output: ===\n", output)
        
    child.sendline('exit')
    
if __name__ == '__main__':
    test()
