import os
import time
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("YouTubeAuth")

def authenticate(email, password):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_dir = os.path.join(base_dir, "playwright_youtube_profile")
    
    logger.info("Launching Playwright to authenticate Google/YouTube...")
    with sync_playwright() as p:
        # We must use a normal browser profile to bypass Google's automation detection
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.new_page()
        logger.info("Navigating to StackOverflow Google Login (easier bypass)...")
        # Going directly to Google login often fails automation checks. 
        # Going to a third-party that uses Google Login is sometimes easier, but let's try direct first.
        page.goto("https://accounts.google.com/signin/v2/identifier?service=youtube&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle%3Dsignin%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en")
        
        try:
            # 1. Email input
            page.wait_for_selector("input[type='email']", timeout=15000)
            logger.info("Filling email...")
            page.fill("input[type='email']", email)
            page.keyboard.press("Enter")
            
            # 2. Wait for password input
            time.sleep(3)
            page.wait_for_selector("input[type='password']", timeout=15000)
            logger.info("Filling password...")
            page.fill("input[type='password']", password)
            page.keyboard.press("Enter")
            
            # Check for passkey or "Sign in faster" prompt
            time.sleep(5)
            try:
                if page.locator("button:has-text('Not now'), span:has-text('Not now'), a:has-text('Not now')").is_visible():
                    logger.info("Handling 'Sign in faster' prompt...")
                    page.locator("button:has-text('Not now'), span:has-text('Not now'), a:has-text('Not now')").click()
            except Exception:
                pass
            
            # 3. Wait for YouTube to load (Login success)
            page.wait_for_selector("ytd-masthead", timeout=30000)
            logger.info("✅ YouTube Authentication Successful! Profile saved.")
            
        except Exception as e:
            logger.error(f"❌ YouTube Authentication Failed: {e}")
            page.screenshot(path="yt_auth_error.png")
            logger.info("Saved error screenshot to yt_auth_error.png")
        finally:
            time.sleep(5)
            # Make sure we visit studio once
            try:
                page.goto("https://studio.youtube.com")
                page.wait_for_selector("#create-icon", timeout=10000)
                logger.info("✅ YouTube Studio accessed successfully.")
            except:
                pass
            browser.close()

if __name__ == "__main__":
    authenticate("deadman150469@gmail.com", "Avichal#1")
