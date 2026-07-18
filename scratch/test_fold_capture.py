import re
with open("app.py", "r") as f:
    app = f.read()

print("scrollEnforcerStarted" in app)
print("itp-enter-script" in app)
