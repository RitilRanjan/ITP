import re
import time
from playwright.sync_api import sync_playwright, expect

def test_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to Streamlit app
        page.goto("http://localhost:8504")
        
        # Wait for the app to load
        page.wait_for_selector(".stApp")
        time.sleep(3)
        
        # Go to Games mode
        page.get_by_role("tab", name="Games").click()
        time.sleep(2)
        
        # Click on Natural Number Game Level 4
        page.get_by_role("button", name="Level 4").click()
        time.sleep(2)
        
        # Send a command
        chat_input = page.locator("[data-testid='stChatInput'] textarea")
        chat_input.fill("hello")
        chat_input.press("Enter")
        time.sleep(2)
        
        # Send another command
        chat_input.fill("world")
        chat_input.press("Enter")
        time.sleep(2)
        
        # Capture screenshot to see the state
        page.screenshot(path="artifacts/ui_test.png")
        print("UI test complete")
        browser.close()

if __name__ == "__main__":
    test_ui()
