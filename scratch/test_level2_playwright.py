import time
from playwright.sync_api import sync_playwright

def test_level2():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Connecting to localhost:8501")
        page.goto("http://localhost:8501")
        
        print("Clicking Games Tab...")
        try:
            page.wait_for_selector("text=🎮 Games", timeout=5000)
            page.locator("text=🎮 Games").click()
        except:
            print("Could not find games tab")
        print("Clicking View Levels for Natural Number Game...")
        try:
            # natural number game is the 3rd game in alphabetical order
            page.wait_for_selector("button:has-text('View Levels')", timeout=5000)
            page.locator("button", has_text="View Levels").nth(2).click()
        except:
            print("Could not find View Levels button")
            
        # Click on Level 2: Predecessor using Iota
        print("Clicking Play for Level 2...")
        try:
            page.wait_for_selector("button:has-text('Play')", timeout=5000)
            page.locator("button", has_text="Play").nth(1).click()
        except:
            print("Could not find Play button")
            
        page.wait_for_selector('input[aria-label="Type your command:"]', timeout=10000)
        
        def run_command(cmd, wait_time=1000):
            print(f"Running command: {cmd}")
            input_box = page.locator('input[aria-label="Type your command:"]')
            input_box.fill(cmd)
            page.locator("button", has_text="Run Command").click()
            page.wait_for_timeout(wait_time)
            
        run_command("cv x y")
        run_command("def_f 1 P x ι y S y = x")
        run_command("cf goal ∀x P S x = x")
        run_command("mission goal")
        run_command("intro u g1")
        run_command("fold all g1 g2")
        
        # Now wait for the popup asking for variable 'v'
        try:
            page.wait_for_selector('input[aria-label="Expansion of \'iota (first variable)\' requires a new variable."]', timeout=5000)
            print("Popup for first variable appeared!")
            input_box = page.locator('input[aria-label="Expansion of \'iota (first variable)\' requires a new variable."]')
            input_box.fill("v")
            input_box.press("Enter")
            
            page.wait_for_selector('input[aria-label="Expansion of \'iota (second variable)\' requires a new variable."]', timeout=5000)
            print("Popup for second variable appeared!")
            input_box2 = page.locator('input[aria-label="Expansion of \'iota (second variable)\' requires a new variable."]')
            input_box2.fill("w")
            input_box2.press("Enter")
        except Exception as e:
            print(f"Popup logic failed: {e}")
        
        page.wait_for_timeout(2000)
        content = page.content()
        if "¬∀v ¬(" in content:
            print("Successfully expanded completely on the web!")
        else:
            print("Failed to expand completely on the web.")
            
        browser.close()

if __name__ == "__main__":
    test_level2()
