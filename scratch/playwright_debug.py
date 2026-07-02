import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:8501")
        await page.wait_for_timeout(2000)
        
        # Click the Games tab
        await page.locator('button[data-baseweb="tab"]:has-text("🎮 Games")').click()
        await page.wait_for_timeout(1000)
        
        try:
            await page.locator('button:has-text("Play")').nth(0).click()
            await page.wait_for_timeout(2000)
            
            # Print all iframes
            frames = page.frames
            print("Frames:")
            for f in frames:
                print(f.name, f.url)
            
            # Print iframe titles
            iframe_titles = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('iframe')).map(i => i.title);
            }''')
            print("Iframe Titles:", iframe_titles)
            
        except Exception as e:
            print("Error:", e)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
