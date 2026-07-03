import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to local Streamlit app...")
        try:
            await page.goto("http://localhost:8501", timeout=10000)
            print("Successfully connected. Waiting for load...")
            await page.wait_for_selector("text=Games", timeout=10000)
            print("Page loaded successfully! The app is running.")
            await browser.close()
            return 0
        except Exception as e:
            print(f"Error connecting or waiting for load: {e}")
            await browser.close()
            return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
