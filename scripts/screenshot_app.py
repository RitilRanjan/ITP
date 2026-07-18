from playwright.sync_api import sync_playwright
import time
import os

def take_screenshot():
    # Print the current working directory to confirm
    print(f"Running screenshot app in {os.getcwd()}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501")
        
        print("Waiting for 3 seconds for the app to load...")
        time.sleep(3) 
        
        screenshot_path = os.path.abspath("artifacts/streamlit_screenshot.png")
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        
        print(f"Saving screenshot to {screenshot_path}...")
        page.screenshot(path=screenshot_path, full_page=True)
        
        browser.close()
        print("Done!")

if __name__ == "__main__":
    take_screenshot()
