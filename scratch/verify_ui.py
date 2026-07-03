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
            
            # Wait a moment for rendering
            await page.wait_for_timeout(2000)
            
            print("Taking screenshot...")
            await page.screenshot(path="/Users/ritilranjan/ITP/scratch/verify_games_tab.png", full_page=True)
            print("Screenshot saved to /Users/ritilranjan/ITP/scratch/verify_games_tab.png")
            
            await browser.close()
            return 0
            
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="/Users/ritilranjan/ITP/scratch/verify_ui_exception.png", full_page=True)
            await browser.close()
            return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
