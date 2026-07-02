import asyncio
from playwright.async_api import async_playwright
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('http://localhost:8501')
        await page.wait_for_timeout(3000)
        
        await page.locator('button[role="tab"]:has-text("Programs")').click()
        await page.wait_for_timeout(2000)
        
        prog_name = f"test_russell_{int(time.time())}"
        await page.get_by_label("Program Name").fill(prog_name)
        await page.locator('button:has-text("Create")').click()
        await page.wait_for_timeout(3000)
        
        input_box = page.frame_locator('iframe[title="st_keyup.st_keyup"]').locator('input').first
        
        await input_box.fill('')
        await input_box.press_sequentially('cf russel ¬∃A ∀B B∈A', delay=10)
        await page.wait_for_timeout(200)
        await input_box.press('Enter')
        await page.wait_for_timeout(2000)
        
        print("Checking locator...")
        count = await page.locator('.interactive-name[data-target="russel"]').count()
        print(f"Main page count: {count}")
        
        for i in range(5):
            try:
                iframe = page.frame_locator('iframe[title="st.iframe"]').nth(i)
                iframe_count = await iframe.locator('.interactive-name[data-target="russel"]').count()
                print(f"Iframe {i} count: {iframe_count}")
            except Exception as e:
                print(f"Iframe {i} error: {e}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
