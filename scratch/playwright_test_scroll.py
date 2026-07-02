from playwright.sync_api import sync_playwright
import time

def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto('http://localhost:8501', timeout=60000)
        
        # Inject our scroll listener test
        page.evaluate('''() => {
            let div = document.createElement('div');
            div.id = "target-div";
            div.style.marginTop = '1500px';
            div.style.marginBottom = '1500px';
            div.innerText = 'TARGET';
            let app = document.querySelector('.stApp');
            app.appendChild(div);
            
            let popover = document.createElement('div');
            popover.id = "test-fixed-div";
            popover.style.position = 'fixed';
            popover.style.width = '100px';
            popover.style.height = '50px';
            popover.style.background = 'blue';
            popover.style.zIndex = '999999';
            document.body.appendChild(popover);
            
            let updatePosition = function() {
                let rect = div.getBoundingClientRect();
                popover.style.top = (rect.top - 60) + 'px';
                popover.style.left = rect.left + 'px';
            };
            updatePosition();
            
            let scrollListener = function() {
                updatePosition();
            };
            window.addEventListener('scroll', scrollListener, true);
        }''')
        time.sleep(1)
        
        # Now scroll the page
        page.evaluate("document.querySelector('.stApp').scrollTop = 500")
        time.sleep(1)
        
        props = page.evaluate('''() => {
            let popover = document.querySelector('#test-fixed-div');
            let target = document.querySelector('#target-div');
            let prect = popover.getBoundingClientRect();
            let trect = target.getBoundingClientRect();
            return {
                popover_top: prect.top,
                target_top: trect.top,
                diff: trect.top - prect.top
            };
        }''')
        print(f"Scroll test props: {props}")
        
        browser.close()

if __name__ == '__main__':
    test_app()
