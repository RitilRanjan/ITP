from playwright.sync_api import sync_playwright
import time
import subprocess

def test_app():
    proc = subprocess.Popen([".venv/bin/python", "-m", "streamlit", "run", "scratch/test_st_input.py", "--server.port", "8503"])
    time.sleep(3)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8503')
        time.sleep(5) # Wait for 2s timeout and Streamlit to rerun
        
        texts = page.locator('.stMarkdown').all_inner_texts()
        print("MARKDOWNS:", texts)
        browser.close()
    proc.kill()

if __name__ == '__main__':
    test_app()
