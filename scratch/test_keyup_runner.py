from playwright.sync_api import sync_playwright
import time
import subprocess
import os

process = subprocess.Popen(["streamlit", "run", "scratch/test_keyup.py", "--server.port", "8503"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
time.sleep(3)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8503")
        page.wait_for_selector("text=Type something:")
        
        # Type into the input
        page.type('input[type="text"]', "hello", delay=100)
        time.sleep(1)
        
        val = page.evaluate("document.querySelector('input[type=\"text\"]').value")
        print(f"After typing, value is: '{val}'")
        
        browser.close()
finally:
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
