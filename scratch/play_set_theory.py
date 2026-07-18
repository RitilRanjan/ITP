from playwright.sync_api import sync_playwright
import time
import sys

def test_level(page, level_name, commands):
    print(f"Testing {level_name}...")
    page.locator('label').filter(has_text="🎮 Games").click()
    time.sleep(1)
    
    # Click Set Theory
    page.locator("text=Set Theory").first.click()
    time.sleep(1)
    
    # Click Level
    page.locator(f"text={level_name}").first.click()
    time.sleep(2)
    
    # Try the commands
    for cmd in commands:
        print(f"Executing: {cmd}")
        page.fill("input[type='text']", cmd)
        page.press("input[type='text']", "Enter")
        time.sleep(1)
    
    # Wait to see if it says "Mission Accomplished!"
    time.sleep(2)
    success = page.locator("text=Mission Accomplished!").is_visible()
    if success:
        print(f"Success: {level_name} proved!")
    else:
        print(f"Failed: {level_name}")
    
    # Go back home
    page.locator('label').filter(has_text="🏠 Home").click()
    time.sleep(1)
    return success

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")
        time.sleep(3)
        
        try:
            test_level(page, "Axiom of Extension", [
                "cv x A B",
                "cf goal ∀x(x∈A ⇔ x∈B) ⇒ A=B",
                "apply goal extension"
            ])
            
            test_level(page, "Subset Relation is Reflexive", [
                "cv A",
                'cf subset "?t1 ⊆ ?t2" ∀?v3 (?v3 ∈ ?t1 ⇒ ?v3 ∈ ?t2)',
                "cf goal A⊆A",
                "mission goal",
                "rw subset x",
                "intro y",
                "apply PC1"
            ])
            
        except Exception as e:
            print(f"Error: {e}")
        
        browser.close()

if __name__ == "__main__":
    run_tests()
