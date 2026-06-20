import subprocess

script = """
def_r 2 R x=y
mission ∃x R(x,y)
fold R 1 OUT1
fold ∃ 1 OUT2
show
exit
"""

with open("test_fold_omission.py", "w") as f:
    f.write(script)
