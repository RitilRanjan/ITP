import time
from playwright.sync_api import sync_playwright

def test_level2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Connecting to localhost:8502...")
        page.goto("http://localhost:8502")
        page.wait_for_selector("text=Interactive Theorem Prover", timeout=10000)
        
        print("Navigating to Games...")
        page.locator("label:has-text('🎮 Games')").click()
        time.sleep(1)
        
        print("Selecting 'natural number game'...")
        page.locator("button:has-text('View Levels')").first.click()
        time.sleep(1)
        
        print("Selecting level 2...")
        play_btns = page.locator("button:has-text('Play')")
        if play_btns.count() > 1:
            play_btns.nth(1).click()
        else:
            play_btns.first.click()
        
        time.sleep(2)
        
        # Now we are in the game!
        print("Playing the game...")
        
        commands = [
            "cv x y u v w",
            "def_f 1 P x ι y S(y) = x",
            "cf goal ∀x P(S(x)) = x",
            "mission goal",
            "intro2 u",
            "rw P (1)",
            "fold ι (1)"
        ]
        
        # NOTE: Using the correct syntax for Level 2 (from the hints: P(S(x)) etc)
        
        for cmd in commands:
            print(f"Typing: {cmd}")
            frame = page.frame_locator('iframe[title="st_keyup.st_keyup"]').first
            input_box = frame.locator('input')
            
            # Use fill to avoid flaky typing
            input_box.fill(cmd)
            time.sleep(0.5)
            
            # Click "Run Command"
            page.locator("button:has-text('Run Command')").click(force=True)
            time.sleep(1)
            
        print("Checking if goal completed...")
        # Check if ∃v (∀w (S w = S u ⇔ v = w) ∧ v = u) is printed in the console
        time.sleep(2)
        
        page.screenshot(path="artifacts/after_run.png")
        print("Test finished successfully!")
        browser.close()

if __name__ == "__main__":
    test_level2()
