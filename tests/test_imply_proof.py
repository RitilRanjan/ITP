import subprocess

process = subprocess.Popen(
    ['/usr/bin/python3', 'main.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

commands = """y
cp imp p ⇒ p
backward_search imp +proof
show
exit
"""
out, err = process.communicate(commands)
print("STDOUT:")
print(out)
print("STDERR:")
print(err)

print("\n--- proofs.html content ---")
try:
    with open('proofs.html', 'r') as f:
        lines = f.readlines()
        for line in lines:
            print(line, end="")
except Exception as e:
    print("Could not read proofs.html:", e)
