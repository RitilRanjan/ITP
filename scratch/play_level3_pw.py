from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        print("Navigating to local Streamlit app...")
        page.goto("http://localhost:8503")
        time.sleep(2)

        # Click the "Games" tab
        print("Looking for Games tab...")
        try:
            games_tab = page.locator("button:has-text('Games')")
            games_tab.click()
            time.sleep(1)
        except Exception as e:
            print(f"Error clicking Games tab: {e}")
            page.screenshot(path="scratch/pw_error_games.png")
            return

        # Start Level 3
        print("Looking for Level 3...")
        try:
            level_btn = page.locator("button:has-text('Level 3 - Zero is Not One')")
            level_btn.click()
            time.sleep(1)
            play_btn = page.locator("button:has-text('Play')")
            play_btn.click()
            time.sleep(1)
        except Exception as e:
            print(f"Error starting Level 3: {e}")
            page.screenshot(path="scratch/pw_error_level3.png")
            return
            
        print("Starting proof sequence...")
        
        commands = [
            "cv u v",
            "def_r 2 u ≠ v ¬ u = v",
            "ct 1 S 0",
            "cf goal 0 ≠ 1",
            "mission goal",
            "fold ≠ (1)",
            "rw 1 (1)",
            "cv x",
            "cf f1 ¬∃x S x = 0",
            "apply f1 0_pred",
            "fold ∃ (1) f1 f1_unfolded",
            "neg- f1_unfolded f2",
            "intro f2 0",
            "swap_eq (1) f2"
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            # Use javascript to set value and dispatch Enter event since iframe logic is tricky
            # Wait, the input is in an iframe for st_keyup!
            try:
                frame_element = page.locator("iframe[title='st_keyup.st_keyup']").first
                frame = frame_element.content_frame
                input_locator = frame.locator("input[type='text']")
                input_locator.fill(cmd)
                input_locator.press("Enter")
                time.sleep(0.5)
            except Exception as e:
                print(f"Failed to enter command '{cmd}': {e}")
                page.screenshot(path="scratch/pw_error_cmd.png")
                return

        time.sleep(1)
        page.screenshot(path="artifacts/pw_level3_success.png")
        print("Done! Screenshot saved to pw_level3_success.png")
        
        browser.close()

if __name__ == "__main__":
    run()
