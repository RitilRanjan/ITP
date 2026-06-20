import subprocess
import time
import os

def read_until(proc, target_string, timeout=2.0):
    start = time.time()
    out = ""
    while time.time() - start < timeout:
        char = proc.stdout.read(1)
        if not char:
            time.sleep(0.01)
            continue
        out += char
        if out.endswith(target_string):
            return out
    return out

def run_test():
    proc = subprocess.Popen(
        [".venv/bin/python", "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    print("Waiting for prompt...")
    out = read_until(proc, "ITP> ")
    print(out)
    
    commands = [
        "cv x",
        "cv y",
        "cv z",
        "cf d1 ∀y(x=y)",
        "def_f 1 f d1"
    ]
    for cmd in commands:
        print(f"Sending: {cmd}")
        proc.stdin.write(cmd + "\n")
        out = read_until(proc, "ITP> ")
        print(out)
        
    print("Testing fold with capture (Internal Capture)...")
    proc.stdin.write("cf form f(y)\n")
    out = read_until(proc, "ITP> ")
    print(out)
    
    proc.stdin.write("fold f 1 form f_output\n")
    # This should trigger capture and ask for replacement variable for 'y'
    out = read_until(proc, "capturing variable 'y': ")
    print("Output after fold:", out)
    assert "Variable capture detected!" in out
    
    # Provide the replacement 'z'
    proc.stdin.write("z\n")
    out = read_until(proc, "ITP> ")
    print("Output after replacement:", out)
    
    assert "Expanded function 'f'" in out
    
    proc.stdin.write("show\n")
    out = read_until(proc, "ITP> ")
    print(out)
    
    proc.stdin.write("exit\n")
    proc.wait()
    print("Test passed!")

if __name__ == "__main__":
    run_test()
