from playwright.sync_api import sync_playwright
import time
import subprocess
import os

process = subprocess.Popen(["streamlit", "run", "app.py", "--server.port", "8505"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
time.sleep(3)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("http://localhost:8505")
        page.wait_for_selector("text=Interactive Theorem Prover", timeout=10000)
        
        # Navigate to Games
        page.locator("label:has-text('🎮 Games')").click()
        time.sleep(1)
        
        page.locator("button:has-text('View Levels')").first.click()
        time.sleep(1)
        
        play_btns = page.locator("button:has-text('Play')")
        if play_btns.count() > 1:
            play_btns.nth(1).click()
        else:
            play_btns.first.click()
        
        time.sleep(2)
        
        # Print all iframes
        iframes = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('iframe')).map(i => i.title);
        }''')
        print(f"IFRAME TITLES: {iframes}")
        
        # Dump inputs in the first st_keyup iframe if any
        inputs = page.evaluate('''() => {
            const iframe = document.querySelector('iframe[title="streamlit_keyup.st_keyup"]');
            if (iframe && iframe.contentDocument) {
                return Array.from(iframe.contentDocument.querySelectorAll('input')).map(i => i.outerHTML);
            }
            return [];
        }''')
        print(f"INPUTS IN KEYUP IFRAME: {inputs}")
        
        browser.close()
finally:
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
