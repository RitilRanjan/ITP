import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8501")
        
        await page.wait_for_selector('iframe', timeout=10000)
        frames = page.frames
        for i, frame in enumerate(frames):
            try:
                inputs = await frame.locator('input').all()
                for inp in inputs:
                    ph = await inp.get_attribute('placeholder')
                    print(f"Frame {i}: input with placeholder '{ph}'")
            except Exception as e:
                pass
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
