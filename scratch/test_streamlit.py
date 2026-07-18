from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("http://localhost:8501")
    page.wait_for_selector(".stApp")
    
    # Check if there are any error texts
    error_elements = page.query_selector_all(".stException")
    if error_elements:
        print("FOUND STREAMLIT ERRORS!")
        for el in error_elements:
            print(el.inner_text())
    else:
        print("NO ERRORS FOUND.")
        
    browser.close()
