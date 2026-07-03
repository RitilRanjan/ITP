import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            print("Navigating to http://localhost:8501...")
            await page.goto('http://localhost:8501', wait_until="networkidle")
            
            # Wait a few seconds for Streamlit to render WebSockets content
            await page.wait_for_timeout(5000)
            
            # Check for generic exception tracebacks (Streamlit error modal)
            print("Checking for errors...")
            error_element = await page.query_selector('.stException')
            if error_element:
                text = await error_element.inner_text()
                print(f"APP ERROR FOUND:\n{text}")
                exit(1)
                
            content = await page.content()
            if "Interactive Theorem Prover" in content or "ITP" in content:
                print("App loaded successfully without errors!")
            else:
                print("App loaded but couldn't find expected content.")
                print(f"Content dump length: {len(content)}")
                # save screenshot just to see what's wrong
                await page.screenshot(path="scratch/app_screenshot.png")
                
        except Exception as e:
            print(f"Playwright error: {e}")
            exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
