
from playwright.sync_api import sync_playwright
import os
import time

def check_identity():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bot_profile_dir = os.path.join(base_dir, "bot_profile")
    
    print(f"Using profile: {bot_profile_dir}")
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=bot_profile_dir,
                channel="chrome",
                headless=True,
                viewport={"width": 1280, "height": 900}
            )
            page = browser.new_page()
            
            # YouTube Identity
            print("Checking YouTube Identity...")
            page.goto("https://www.youtube.com/", wait_until="domcontentloaded")
            time.sleep(5)
            # Click profile icon to show handle
            try:
                page.locator("button#avatar-btn").click(timeout=5000)
                time.sleep(2)
            except:
                pass
            page.screenshot(path=os.path.join(base_dir, "yt_identity_check.png"))
            
            # Instagram Identity
            print("Checking Instagram Identity...")
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
            time.sleep(5)
            # Go to profile page
            try:
                page.locator("svg[aria-label='Profile']").locator("xpath=..").click(timeout=5000)
                time.sleep(3)
            except:
                pass
            page.screenshot(path=os.path.join(base_dir, "ig_identity_check.png"))
            
            browser.close()
            print("Diagnostic screenshots saved to backend/")
        except Exception as e:
            print(f"Diagnostic failed: {e}")

if __name__ == "__main__":
    check_identity()
