import asyncio
from playwright.async_api import async_playwright

async def run_command(page, cmd: str):
    print(f"Running command: {cmd}")
    # The input might be st_keyup or st.chat_input
    # st_keyup creates an input field.
    input_selector = "input[aria-label='Type your command:']"
    if await page.query_selector(input_selector):
        await page.fill(input_selector, cmd)
        await page.click("button:has-text('Run Command')")
    else:
        # Fallback to chat_input
        chat_input = await page.wait_for_selector("input[data-testid='stChatInput']", timeout=5000)
        await chat_input.fill(cmd)
        await chat_input.press("Enter")
    await page.wait_for_timeout(2000)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Connecting to Streamlit...")
            await page.goto("http://localhost:8501", timeout=10000)
            
            await page.wait_for_selector("text=Games", timeout=10000)
            await page.click("button[id*='tab-'][id$='-2']")
            
            await page.wait_for_selector("text=natural number game", timeout=10000)
            await page.click("button:has-text('🎮 natural number game')")
            
            await page.wait_for_selector("text=Level 2: Predecessor using Iota", timeout=10000)
            play_buttons = await page.query_selector_all("button:has-text('Play Level')")
            await play_buttons[1].click()
            
            await page.wait_for_selector("text=Active Environments Chain", timeout=10000)
            
            # Check if Constants and suggestions work
            await run_command(page, "cv x y u v w")
            await run_command(page, "def_f 1 P x ι y S y = x")
            
            await page.screenshot(path="/Users/ritilranjan/ITP/scratch/verify_level2_progress.png", full_page=True)
            print("Success! UI elements are functioning and commands can be entered.")
            
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="/Users/ritilranjan/ITP/scratch/verify_level2_error.png", full_page=True)
        finally:
            await browser.close()

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
