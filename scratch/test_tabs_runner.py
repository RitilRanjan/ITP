from playwright.sync_api import sync_playwright
import time
import subprocess
import os

# Start streamlit
process = subprocess.Popen(["streamlit", "run", "scratch/test_tabs.py", "--server.port", "8502"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
time.sleep(3)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8502")
        page.wait_for_selector("text=Tab 1")
        
        # Click Tab 2
        page.click("button[id^='tabs-bui'][id$='-tab-1']")
        time.sleep(1)
        
        # Click button without callback
        page.click("text=Go without callback")
        time.sleep(1)
        
        # Check if Tab 2 is still active
        is_tab2_active = page.evaluate("document.querySelector('button[id^=\"tabs-bui\"][id$=\"-tab-1\"]').getAttribute('aria-selected')")
        print(f"Without callback: Tab 2 active = {is_tab2_active}")
        
        # Go back
        page.click("button[id^='tabs-bui'][id$='-tab-1']") # click tab 2 again if it reset
        time.sleep(1)
        if page.query_selector("text=Back without callback"):
            page.click("text=Back without callback")
        time.sleep(1)
        
        # Click tab 2
        page.click("button[id^='tabs-bui'][id$='-tab-1']")
        time.sleep(1)
        
        # Click button WITH callback
        page.click("text=Go with callback")
        time.sleep(1)
        
        is_tab2_active = page.evaluate("document.querySelector('button[id^=\"tabs-bui\"][id$=\"-tab-1\"]').getAttribute('aria-selected')")
        print(f"WITH callback: Tab 2 active = {is_tab2_active}")
        
        browser.close()
finally:
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
