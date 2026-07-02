from playwright.sync_api import sync_playwright
import time
import uuid

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        alerts = []
        page.on("dialog", lambda dialog: (alerts.append(dialog.message), dialog.accept()))
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        
        page.goto('http://localhost:8501', timeout=60000)
        
        page.wait_for_selector('button:has-text("Programs")', state="attached", timeout=30000)
        page.locator('button', has_text="Programs").first.click(force=True)
        
        page.wait_for_selector('input[aria-label="Program Name"]', timeout=30000)
        prog_name = f"test_{uuid.uuid4().hex[:6]}"
        page.locator('input[aria-label="Program Name"]').fill(prog_name)
        page.locator('button', has_text="Create").first.click(force=True)
        
        page.wait_for_selector('h3:has-text("Command Input")', timeout=30000)
        time.sleep(2)
        
        keyup = page.frame_locator('iframe[title="st_keyup.st_keyup"]').first
        if keyup:
            input_elem = keyup.locator('input').first
            input_elem.focus()
            input_elem.press_sequentially('cf f1 x = y', delay=100)
            time.sleep(2)
            page.locator('button', has_text="Run Command").first.click(force=True)
        
        time.sleep(4)
        
        symbols = page.locator('.interactive-symbol')
        if symbols.count() == 0:
            print("Symbol not found!")
            browser.close()
            return
            
        print(f"Found {symbols.count()} symbols. Clicking the first one...")
        
        symbol = page.locator('.interactive-symbol').first
        symbol.scroll_into_view_if_needed()
        symbol.click()
        
        time.sleep(2)
        
        props = page.evaluate('''() => {
            let popover = document.querySelector('.itp-popover');
            if (!popover) return "Not found";
            let rect = popover.getBoundingClientRect();
            let styles = window.getComputedStyle(popover);
            return {
                rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
                display: styles.display,
                visibility: styles.visibility,
                opacity: styles.opacity,
                position: styles.position,
                zIndex: styles.zIndex,
                top: styles.top,
                left: styles.left,
                innerHTML: popover.innerHTML
            };
        }''')
        print(f"Popover props: {props}")
        
        browser.close()

if __name__ == '__main__':
    test_app()
