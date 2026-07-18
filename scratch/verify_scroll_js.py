from playwright.sync_api import sync_playwright
import time

def test_scroll():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")
        time.sleep(3)
        
        # Test if our JS is present in the DOM
        try:
            scroll_script = page.evaluate("window.document.getElementById('itp-enter-script') !== null")
            print("Is scroll enforcer script present?", scroll_script)
            
            # Click Exit Game
            try:
                page.locator("text=Exit Game").click(timeout=1000)
                time.sleep(1)
            except:
                pass
            
            # Check if input is present in any frame
            frames = page.frames
            input_found = False
            for frame in frames:
                if frame.locator('input').count() > 0:
                    print("Found input field in frame!")
                    input_found = True
                    break
            
            if not input_found:
                if page.locator('input').count() > 0:
                    print("Found input field in main page!")
                    
        except Exception as e:
            print("Error checking DOM:", e)
        
        browser.close()

if __name__ == "__main__":
    test_scroll()
