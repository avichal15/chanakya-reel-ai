import os
import time
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("InstaAuth")

def authenticate(username, password):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_dir = os.path.join(base_dir, "playwright_instagram_profile")
    
    logger.info("Launching Playwright to authenticate Instagram...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False, # Must be headful to bypass anti-bot blocks
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = browser.new_page()
        logger.info("Navigating to Instagram login page...")
        page.goto("https://www.instagram.com/accounts/login/")
        
        try:
            # Wait for the login button to be visible, which implies the form is loaded
            page.wait_for_selector("button[type='submit']", timeout=15000)
            
            logger.info("Form loaded. Filling credentials...")
            
            # Instagram obfuscates input names to block bots. We will grab the first two inputs.
            # 1st input is username, 2nd is password
            inputs = page.locator("input")
            
            # Type username
            inputs.nth(0).click(force=True)
            time.sleep(1)
            inputs.nth(0).press_sequentially(username, delay=100)
            time.sleep(1)
            
            # Type password
            inputs.nth(1).click(force=True)
            time.sleep(1)
            inputs.nth(1).press_sequentially(password, delay=100)
            time.sleep(2)
            
            logger.info("Clicking Log In...")
            page.locator("button[type='submit']").click()
            
            logger.info("Waiting for successful login...")
            
            # Wait for successful login (Feed or Save Info prompt)
            page.wait_for_selector("svg[aria-label='Home'], svg[aria-label='Messages'], button:has-text('Save info'), button:has-text('Not now')", timeout=30000)
            
            # Handle "Save Your Login Info?" if it appears
            try:
                if page.locator("button:has-text('Save info')").is_visible():
                    logger.info("Clicking 'Save info'...")
                    page.locator("button:has-text('Save info')").click()
                    time.sleep(3)
            except Exception:
                pass
                
            logger.info("✅ Instagram Authentication Successful! Profile saved.")
        except Exception as e:
            logger.error(f"❌ Instagram Authentication Failed: {e}")
            page.screenshot(path="insta_auth_error.png")
            logger.info("Saved error screenshot to insta_auth_error.png")
        finally:
            time.sleep(2)
            browser.close()

if __name__ == "__main__":
    authenticate("philosphyforge", "Avichal#1504")
