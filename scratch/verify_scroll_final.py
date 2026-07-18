from playwright.sync_api import sync_playwright
import time

def test_scroll():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8501")
        time.sleep(3)
        
        # Click Exit Game if available
        try:
            btn = page.locator("text=Exit Game").first
            if btn.is_visible(timeout=2000):
                btn.click()
                time.sleep(2)
        except Exception as e:
            pass
            
        commands = [
            "cv u v",
            "def_r 2 u ≠ v ¬ u = v",
            "def_f 0 1 S 0",
            "cf goal 0 ≠ 1",
            "mission goal",
            "fold ≠ (1)",
            "fold 1 (1)",
            "cf f1 ¬∃x S x = 0",
            "apply f1 0_pred",
            "fold ∃ (1) f1 f1_unfolded",
            "neg- f1_unfolded f2"
        ]
        
        for cmd in commands:
            success = False
            try:
                # First try the keyup input
                iframe = page.frame_locator('iframe[title="streamlit_keyup.st_keyup"]')
                input_el = iframe.locator('input')
                if input_el.count() > 0:
                    input_el.fill(cmd, timeout=1000)
                    input_el.press("Enter", timeout=1000)
                    success = True
            except:
                pass
                
            if not success:
                try:
                    # Fallback for st.chat_input which is a textarea
                    input_el = page.get_by_placeholder("Enter command here").first
                    input_el.fill(cmd, timeout=1000)
                    input_el.press("Enter", timeout=1000)
                except Exception as e:
                    print("Failed to type command:", cmd, e)
            
            time.sleep(0.8) # Wait for execution and scroll
            
        time.sleep(2)
        
        # Evaluate scroll position
        scroll_y = page.evaluate("window.scrollY || document.documentElement.scrollTop || (document.querySelector('.main') ? document.querySelector('.main').scrollTop : 0)")
        body_h = page.evaluate("document.body.scrollHeight || (document.querySelector('.main') ? document.querySelector('.main').scrollHeight : 0)")
        viewport_h = page.evaluate("window.innerHeight || (document.querySelector('.main') ? document.querySelector('.main').clientHeight : 0)")
        
        print(f"ScrollY: {scroll_y}, Body Height: {body_h}, Viewport Height: {viewport_h}")
        
        if scroll_y + viewport_h < body_h - 100:
            print("FAILED: Page is not scrolled to the bottom!")
        else:
            print("SUCCESS: Page is scrolled to the bottom.")
            
        browser.close()

if __name__ == "__main__":
    test_scroll()
