import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            print("Navigating to http://localhost:8515...")
            await page.goto('http://localhost:8515', wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # Find the iframe and read its content
            frame = page.frames[1] # 0 is main page, 1 is the component
            text = await frame.locator("body").inner_text()
            print("Iframe Text content:", text)
        except Exception as e:
            print(f"Playwright error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
