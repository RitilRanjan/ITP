import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8501")
        await page.wait_for_timeout(2000)
        
        print("Clicking 'Programs' tab...")
        await page.locator('button[role="tab"]:has-text("Programs")').click()
        await page.wait_for_timeout(5000)
        
        await page.screenshot(path="scratch/streamlit_screen2.png")
        print("Screenshot taken.")
        
        frames = page.frames
        print(f"Number of frames: {len(frames)}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
