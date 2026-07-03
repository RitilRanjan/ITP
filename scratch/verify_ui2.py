import asyncio
from playwright.async_api import async_playwright
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Connecting to Streamlit...")
            await page.goto("http://localhost:8501", timeout=10000)
            
            print("Waiting for page load...")
            await page.wait_for_selector("text=Games", timeout=10000)
            
            print("Clicking Games tab...")
            # Streamlit tabs are buttons, click the Games tab
            await page.click("button[id*='tab-'][id$='-2']")
            
            print("Waiting for games to load...")
            await page.wait_for_selector("text=natural number game", timeout=10000)
            
            print("Clicking 'natural number game'...")
            # Click the button for natural number game
            await page.click("button:has-text('🎮 natural number game')")
            
            print("Waiting for levels to load...")
            await page.wait_for_selector("text=Level 2: Predecessor using Iota", timeout=10000)
            
            print("Clicking 'Play Level' for level 2...")
            play_buttons = await page.query_selector_all("button:has-text('Play Level')")
            if len(play_buttons) >= 2:
                await play_buttons[1].click()
            else:
                print("Could not find Level 2 Play Level button")
                return 1
                
            print("Waiting for level 2 environment to load...")
            # We wait up to 5 seconds to let the backend crash if it will
            try:
                await page.wait_for_selector("text=Active Environments Chain", timeout=5000)
                print("Level 2 loaded.")
            except Exception:
                print("Level 2 failed to load 'Active Environments Chain'!")
            
            await browser.close()
            return 0
            
        except Exception as e:
            print(f"Error: {e}")
            await browser.close()
            return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
