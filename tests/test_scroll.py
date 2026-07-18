import re
import time
from playwright.sync_api import sync_playwright, expect

def test_scroll_position():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to Streamlit app
        page.goto("http://localhost:8504")
        
        # Wait for the app to load
        page.wait_for_selector(".stApp")
        time.sleep(2)
        
        # Go to Games page
        page.locator("text=🎮 Games").first.click()
        time.sleep(1)
        
        # Click natural number game view levels
        page.locator("button:has-text('View Levels')").first.click()
        time.sleep(1)
        
        # Click level 4
        page.locator("button", has_text=re.compile(r"Level 4", re.IGNORECASE)).first.click()
        time.sleep(2)
        
        # Find iframe for input
        chat_input = page.frame_locator('iframe[title="st_keyup.st_keyup"]').locator('input')
        
        # Send a few commands to populate the chat history and make it scrollable
        for cmd in ["help", "help", "help", "help", "help", "help", "help", "help"]:
            chat_input.fill(cmd)
            chat_input.press("Enter")
            time.sleep(1.5)
            
        # Scroll down to the bottom
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for the user to be at the bottom
        time.sleep(1)
        
        # The scroll container in Streamlit's new architecture might be `.stMainBlockContainer` or `[data-testid='stMain']`
        get_scroll_pos = "document.querySelector('section[data-testid=\"stMain\"]').scrollTop"
        
        initial_scroll = page.evaluate(get_scroll_pos)
        print(f"Initial scroll position: {initial_scroll}")
        
        # Type another command and press Enter
        chat_input.fill("rb_stat")
        chat_input.press("Enter")
        
        # Immediately check scroll position a few times to catch any jump
        jump_detected = False
        for _ in range(10):
            time.sleep(0.1)
            current_scroll = page.evaluate(get_scroll_pos)
            if current_scroll < initial_scroll - 50: # Tolerance of 50px
                jump_detected = True
                print(f"Jump detected! Scroll went from {initial_scroll} to {current_scroll}")
                break
                
        assert not jump_detected, f"Page jumped to top! Scroll went from {initial_scroll} to {current_scroll}"
        print("Test passed: Scroll position was maintained after pressing Enter.")
        
        browser.close()

if __name__ == "__main__":
    test_scroll_position()
