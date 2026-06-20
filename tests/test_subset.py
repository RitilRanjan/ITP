import subprocess

def run_itp(commands):
    process = subprocess.Popen(
        ['/usr/bin/python3', 'main.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = process.communicate(commands)
    return out

commands = """y
cv x
cv y
cv z
cv A
cv B
cv C
cf z_in_x z ∈ x
cf z_in_y z ∈ y
cf imp_z z ∈ x ⇒ z ∈ y
cf sub_def ∀ z ( z ∈ x ⇒ z ∈ y )
def_r 2 x sub y sub_def
cf ref A sub A
fold sub 1 ref f1
backward_search f1 +proof
simp_l_bi f1 f1 ref
show
exit
"""
print(run_itp(commands))
