from playwright.sync_api import sync_playwright
import time
import subprocess
import os

process = subprocess.Popen(["streamlit", "run", "app.py", "--server.port", "8504"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
time.sleep(3)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("http://localhost:8504")
        page.wait_for_selector("text=Interactive Theorem Prover", timeout=10000)
        
        # Navigate to Games
        page.click("text=🎮 Games")
        time.sleep(1)
        
        page.click("button:has-text('View Levels') >> nth=0")
        time.sleep(1)
        
        page.click("button:has-text('Play') >> nth=0")
        time.sleep(2)
        
        # Print all inputs
        inputs = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('input')).map(i => i.outerHTML);
        }''')
        print("INPUTS FOUND:")
        for i in inputs:
            print(i)
            
        browser.close()
finally:
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
