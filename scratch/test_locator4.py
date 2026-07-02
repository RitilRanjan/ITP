import asyncio
from playwright.async_api import async_playwright
import time

async def click_and_run(page, target_sel, cmd_text, input_vals=None, wait_time=2000):
    clicked = False
    for attempt in range(10):  # Retry up to 10 times (10 seconds)
        # Try main page first
        try:
            el = page.locator(target_sel).first
            if await el.count() > 0:
                await el.click(force=True, timeout=1000)
                clicked = True
        except Exception as e:
            pass
            
        if clicked:
            break
            
        # Try iframes
        for i in range(5):
            try:
                iframe = page.frame_locator('iframe[title="st.iframe"]').nth(i)
                el = iframe.locator(target_sel).first
                if await el.count() > 0:
                    await el.click(force=True, timeout=1000)
                    clicked = True
                    break
            except Exception as e:
                pass
        if clicked:
            break
        await page.wait_for_timeout(1000)
    
    if not clicked:
        raise Exception(f"Could not find {target_sel} in any iframe")
        
    await page.wait_for_timeout(200)
    await page.locator(f'.itp-popover button:has-text("{cmd_text}")').click(force=True)
    await page.wait_for_timeout(200)
    if input_vals:
        if isinstance(input_vals, str): input_vals = [input_vals]
        for attempt in range(5):
            try:
                for idx, val in enumerate(input_vals):
                    input_box = page.locator('.itp-popover input').nth(idx)
                    await input_box.click(force=True)
                    await input_box.press('End')
                    await input_box.press_sequentially(val, delay=10)
                await page.wait_for_timeout(200)
                await page.locator('.itp-popover button:has-text("Run")').click(force=True)
                break
            except Exception as e:
                if attempt == 4: raise e
                await page.wait_for_timeout(500)
    await page.wait_for_timeout(wait_time)

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
        
        print("Clicking russel...")
        await click_and_run(page, '.interactive-name[data-target="russel"]', "contra", ["f2", "f3"])
        
        print("Checking locator...")
        count1 = await page.locator('span[data-target="f2"]').count()
        print(f"Main page span[data-target='f2'] count: {count1}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
