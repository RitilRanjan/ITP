import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            print("Navigating to http://localhost:8511...")
            await page.goto('http://localhost:8511', wait_until="networkidle")
            await page.wait_for_timeout(3000)
            text = await page.locator("body").inner_text()
            print("Text content:", text)
        except Exception as e:
            print(f"Playwright error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
