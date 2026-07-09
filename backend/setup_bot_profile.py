"""
Dedicated Bot Profile Setup

Run this script ONCE manually to log into YouTube and Instagram.
The session cookies will be saved to the 'bot_profile' directory.
The automated scheduled scripts will then use this profile invisibly
in the background to upload videos without any interruptions!
"""
import os
from playwright.sync_api import sync_playwright

def run_setup():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_dir = os.path.join(base_dir, "bot_profile")
    
    print("\n" + "="*50)
    print("Welcome to the Bot Profile Setup!")
    print("This will open a dedicated Chrome window.")
    print("1. Log into your YouTube account.")
    print("2. Log into your Instagram account.")
    print("3. Check the 'Remember Me' box on both.")
    print("4. Close the browser window when you are completely done.")
    print("="*50 + "\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            channel="chrome",
            headless=False,  # You need to see it to log in!
            viewport={"width": 1280, "height": 720},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ],
            ignore_default_args=["--enable-automation", "--no-sandbox"]
        )
        page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        
        # Open both tabs
        page.goto("https://studio.youtube.com/")
        ig_page = browser.new_page()
        ig_page.goto("https://www.instagram.com/")
        
        print("Waiting for you to log in. Close the entire browser window to finish setup!")
        
        # Wait until all pages are closed by the user
        try:
            page.wait_for_event("close", timeout=0)
        except:
            pass
            
        print("\nSetup complete! The bot_profile is now authenticated and ready for background scheduling.")

if __name__ == "__main__":
    run_setup()
