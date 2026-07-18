import time
import os
import subprocess
import shutil
from playwright.sync_api import sync_playwright

def test_game_creator_ui():
    print("Starting Streamlit server...")
    # Start streamlit
    server = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port", "8502", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(5) # Wait for server to boot
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("Navigating to app...")
            page.goto("http://localhost:8502")
            page.wait_for_load_state("networkidle")
            
            print("Selecting Game Creator tab...")
            # Click the radio button for Game Creator using javascript to bypass visibility
            try:
                page.evaluate("document.evaluate(\"//p[contains(text(), '🛠️ Game Creator')]\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()")
            except Exception:
                page.get_by_text("🛠️ Game Creator").first.click(force=True)
            time.sleep(2)
            
            # Ensure "Game Creator" header is visible
            assert page.locator("text='Create New Game'").first.is_visible()
            print("Game Creator tab verified.")
            
            print("Creating dummy game...")
            # Click Create New Game expander if not expanded
            create_btn = page.get_by_text("Create New Game")
            if create_btn.is_visible():
                create_btn.click()
                time.sleep(1)
            
            page.get_by_label("New Game Name").fill("TestDummyGame")
            # Streamlit buttons are tricky, sometimes we need to hit Enter or find the button specifically
            page.get_by_role("button", name="Create").click()
            time.sleep(2)
            
            # Check if directory was created
            assert os.path.exists("games/TestDummyGame"), "Directory games/TestDummyGame was not created"
            print("Dummy game directory created.")
            
            # Now click on "Edit Levels" for TestDummyGame
            page.get_by_text("TestDummyGame").is_visible()
            # The button has key edit_TestDummyGame, but visible text is "Edit Levels"
            # It's next to the game. We can just click the first "Edit Levels" if it's the only one, or find it by parent.
            # There might be multiple games, let's just use page.locator
            # Since TestDummyGame was just created, it has an Edit Levels button
            edit_levels_btns = page.locator("button:has-text('Edit Levels')").all()
            # We'll just click the last one assuming it's the newest
            edit_levels_btns[-1].click()
            time.sleep(2)
            
            print("Creating dummy level...")
            page.get_by_text("➕ Create New Level").click()
            time.sleep(2)
            
            # Now we are in level editor
            page.get_by_label("Level Name").fill("Dummy Level 1")
            # Just verify the form is rendered
            assert page.get_by_label("Level Name").is_visible()
            assert page.get_by_label("Goal Statement").is_visible()
            
            print("All UI tests passed successfully!")
            browser.close()
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        # Terminate early so we can see error
        server.terminate()
        server.wait()
        if os.path.exists("games/TestDummyGame"):
            shutil.rmtree("games/TestDummyGame")
        raise e
        
    finally:
        print("Cleaning up...")
        server.terminate()
        server.wait()
        # Remove dummy game
        if os.path.exists("games/TestDummyGame"):
            shutil.rmtree("games/TestDummyGame")

if __name__ == "__main__":
    test_game_creator_ui()
