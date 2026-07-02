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
        await input_box.press_sequentially('cv a b c z A B C x y', delay=10)
        await page.wait_for_timeout(200)
        await input_box.press('Enter')
        await page.wait_for_timeout(2000)
        
        await input_box.fill('')
        await input_box.press_sequentially('def_r 2 x∉y ¬x∈y', delay=10)
        await page.wait_for_timeout(200)
        await input_box.press('Enter')
        await page.wait_for_timeout(2000)
        
        await input_box.fill('')
        await input_box.press_sequentially('cf russel ¬∃A ∀B B∈A', delay=10)
        await page.wait_for_timeout(200)
        await input_box.press('Enter')
        await page.wait_for_timeout(2000)
        
        content = await page.content()
        with open('scratch/dom2.html', 'w') as f:
            f.write(content)
            
        print("DOM saved to dom2.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
