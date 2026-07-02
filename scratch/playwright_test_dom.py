from playwright.sync_api import sync_playwright
import time

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://localhost:8501', timeout=60000)
        time.sleep(2)
        
        inputs = page.evaluate('''() => {
            let res = [];
            document.querySelectorAll('input').forEach(i => res.push(i.getAttribute('aria-label') || 'NO-LABEL'));
            return res;
        }''')
        
        print("INPUT ARIA LABELS:")
        print(inputs)
        
        browser.close()

if __name__ == '__main__':
    test_app()
