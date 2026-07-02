from playwright.sync_api import sync_playwright
import time

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto('http://localhost:8501', timeout=60000)
        
        # Inject a massive fixed div into body
        page.evaluate('''() => {
            let div = document.createElement('div');
            div.id = "test-fixed-div";
            div.style.position = 'fixed';
            div.style.top = '10px';
            div.style.left = '10px';
            div.style.width = '200px';
            div.style.height = '200px';
            div.style.background = 'red';
            div.style.zIndex = '999999';
            document.body.appendChild(div);
        }''')
        time.sleep(1)
        
        div = page.locator('#test-fixed-div')
        print(f"Bounding box: {div.bounding_box()}")
        print(f"Is visible: {div.is_visible()}")
        
        browser.close()

if __name__ == '__main__':
    test_app()
