import pexpect
import sys

child = pexpect.spawn("python main.py", encoding="utf-8")
child.logfile = sys.stdout

child.expect("Choose theory.*:")
child.sendline("NT")
child.expect("Enable foundational proof logging.*:")
child.sendline("N")
child.expect("ITP.*> ")
child.sendline("cv u w z")
child.expect("ITP.*> ")
child.sendline("cf goal ∀w ( S(w) = S(u) ⇔ u = w ) ∧ u = u")
child.expect("ITP.*> ")
child.sendline("mission goal")
child.expect("ITP.*> ")
child.sendline("and f1 f2")
child.expect("ITP.*> ")
child.sendline("apply E1")
child.expect("ITP.*> ")
child.sendline("intro z f3")
child.expect("ITP.*> ")
child.sendline("exit")
child.close()
