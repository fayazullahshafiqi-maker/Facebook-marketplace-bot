from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()
    page.goto("https://www.facebook.com/login")

    print("👉 Login to Facebook in the browser window")
    print("👉 After login is fully done, come back here and press ENTER")

    input()

    context.storage_state(path="state.json")

    print("✅ Session saved to state.json")
    browser.close()
