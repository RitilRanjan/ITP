import pexpect
import sys

child = pexpect.spawn("python main.py", encoding="utf-8")
child.logfile = sys.stdout

child.expect("Choose theory.*:")
child.sendline("NT")
child.expect("Enable foundational proof logging.*:")
child.sendline("N")
child.expect("ITP.*> ")
child.sendline("cv x y")
child.expect("ITP.*> ")
child.sendline("def_f 1 P x S x")
child.expect("ITP.*> ")
child.sendline("cf goal ∀x P x = x")
child.expect("ITP.*> ")
child.sendline("fold P goal")
child.expect("ITP.*> ")
child.sendline("undo")
child.expect("ITP.*> ")
child.sendline("show")
child.expect("ITP.*> ")
child.sendline("exit")
child.close()
