import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8504")
        page.wait_for_selector(".stApp")
        time.sleep(5)
        
        frames = page.frames
        for frame in frames:
            print(f"Frame URL: {frame.url}, Name: {frame.name}")
        
        print("\nIFRAMES in page:")
        iframes = page.locator("iframe").all()
        for i, iframe in enumerate(iframes):
            title = iframe.get_attribute("title")
            print(f"Iframe {i} title: {title}")
            
        page.screenshot(path="screenshot.png")
        browser.close()

if __name__ == "__main__":
    run()
