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
        
        # Select game "basics of ITP" - Streamlit selectbox might be tricky to interact with
        # Since it's the only game, maybe it's selected by default? Let's check if the Play button is there.
        try:
            await page.locator('button:has-text("Play")').nth(0).click()
            await page.wait_for_timeout(2000)
            print("Successfully entered game mode!")
            await page.screenshot(path="scratch/game_mode.png")
            
            # Now let's try to prove x = x!
            input_el = page.locator('input[placeholder="Enter command here (install streamlit-keyup for autocomplete)"]')
            await input_el.fill("cv x")
            await input_el.press("Enter")
            await page.wait_for_timeout(500)
            
            await input_el.fill("cf goal x=x")
            await input_el.press("Enter")
            await page.wait_for_timeout(500)
            
            # Wait for goal to appear
            await page.wait_for_timeout(500)
            
            # Click goal
            await page.locator('.interactive-name[data-target="goal"]').click()
            await page.wait_for_timeout(500)
            
            # Click apply
            await page.locator('.itp-popover button:has-text("apply")').click(force=True)
            await page.wait_for_timeout(500)
            
            # Enter E1
            await page.locator('.itp-popover-input').fill("E1")
            await page.locator('.itp-popover button:has-text("Run")').click(force=True)
            await page.wait_for_timeout(1000)
            
            # Screenshot of completion
            await page.screenshot(path="scratch/game_complete.png")
            print("Finished successfully!")
        except Exception as e:
            print("Error:", e)
            await page.screenshot(path="scratch/game_error.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
