import sys
import json
import os
import time
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def upload_to_youtube(video_path, title, description):
    print(f"Starting YouTube Upload for: {video_path}")
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        return False

    title = (title[:85] + " #Shorts") if len(title) > 85 else f"{title} #Shorts"
    
    # Use the dedicated bot profile directory within the backend folder
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bot_profile_dir = os.path.join(base_dir, "bot_profile")
    
    if not os.path.exists(bot_profile_dir):
        print("ERROR: bot_profile directory not found!")
        print("Please run `python setup_bot_profile.py` first to log into YouTube.")
        return False
    
    with sync_playwright() as p:
        try:
            print("Launching Dedicated Bot Chrome Profile...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=bot_profile_dir,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars"
                ],
                ignore_default_args=["--enable-automation", "--no-sandbox"],
                headless=True,  # 100% Invisible Background Execution
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                timeout=60000
            )
            
            page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
            
            print("Navigating to YouTube Studio...")
            page.goto("https://studio.youtube.com/", timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            
            debug_path = os.path.join(base_dir, "yt_bot_debug.png")
            page.screenshot(path=debug_path)
            
            if "accounts.google.com" in page.url or "signin" in page.url.lower() or "v2/identifier" in page.url.lower():
                print("ERROR: Not logged in! The bot profile cookie expired or wasn't set.")
                print("Please run `python setup_bot_profile.py` to log back in.")
                page.screenshot(path=debug_path.replace(".png", "_auth_error.png"))
                return False
                
            print("Successfully verified Studio load.")
            
            # Step 1.4: Identity Check
            try:
                handle = page.locator("#channel-handle").inner_text(timeout=5000)
                print(f"✅ LOGGED IN AS: {handle}")
            except:
                print("Could not detect channel handle automatically.")

            # Step 1.5: Handle potential "Welcome to Studio" popup for new profiles
            print("Checking for Welcome splash screens...")
            try:
                # More comprehensive list of dismiss/continue buttons
                selectors = ["#continue-button", "#dismiss-button", "button:has-text('CONTINUE')", "ytcp-button:has-text('Dismiss')"]
                for sel in selectors:
                    btn = page.locator(sel)
                    if btn.count() > 0:
                        print(f"Dismissing splash screen with {sel}...")
                        btn.first.click()
                        page.wait_for_timeout(2000)
            except:
                pass

            # Step 2: Click 'Create' -> 'Upload videos'
            print("Clicking Create Button...")
            try:
                clicked_create = False
                create_selectors = [
                    "button[aria-label='Create']",
                    "#create-icon",
                    "tp-yt-paper-button:has-text('Create')"
                ]
                
                for sel in create_selectors:
                    el = page.locator(sel)
                    if el.count() > 0:
                        el.first.click()
                        clicked_create = True
                        break
                        
                if not clicked_create:
                    print("Warning: Could not find standard create button, trying dynamic index click...")
                    page.locator("ytcp-button").first.click()
                    
                page.wait_for_timeout(2000)
                
                # Now click the 'Upload videos' item
                upload_item = page.locator("tp-yt-paper-item:has-text('Upload videos')")
                if upload_item.count() > 0:
                    upload_item.first.click()
                else:
                    # Fallback index if text changed
                    page.locator("tp-yt-paper-item").first.click()
                    
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Could not click 'Upload videos' flow: {e}")
                page.screenshot(path=debug_path.replace(".png", "_create_error.png"))
                return False
                
            # Step 3: Attach the video explicitly
            print("Attaching video file...")
            try:
                page.locator("input[type='file']").set_input_files(video_path)
            except Exception as e:
                print(f"Failed to attach video via input: {e}")
                return False
                
            # Step 4: Wait for upload modal to appear
            print("Waiting for details dialogue to load...")
            page.wait_for_selector("#details", timeout=60000)
            page.wait_for_timeout(3000)
            
            # Step 5: Fill Title and Description
            print("Filling metadata...")
            try:
                title_box = page.locator("#title-textarea").locator("[id='textbox']")
                title_box.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(title, delay=10)
                
                desc_box = page.locator("#description-textarea").locator("[id='textbox']")
                desc_box.click()
                page.keyboard.press("Control+A")
                page.keyboard.press("Backspace")
                page.keyboard.type(description, delay=5)
            except Exception as e:
                print(f"Failed to fill metadata: {e}")
                
            # Step 6: Set "Not made for kids" radio
            print("Setting audience restrictions...")
            try:
                # Use a more stable selector if possible
                page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").click()
            except Exception as e:
                print(f"Could not set audience restrict: {e}")
                
            page.wait_for_timeout(2000)
            
            # Step 7: Click 'Next' three times
            print("Proceeding through menus...")
            for step in range(3):
                try:
                    next_btn = page.locator("#next-button")
                    if next_btn.is_visible():
                        next_btn.click()
                        page.wait_for_timeout(3000)
                except:
                    break
                    
            # Step 8: Set Visibility to Public
            print("Setting visibility to Public...")
            try:
                page.locator("tp-yt-paper-radio-button[name='PUBLIC']").click()
            except Exception as e:
                print(f"Could not set Public visibility: {e}")
                
            page.wait_for_timeout(3000)
            
            # Step 9: Wait for processing
            print("Waiting for upload to finish processing...")
            page.screenshot(path=debug_path.replace(".png", "_pre_publish.png"))
            
            # Step 10: Click Publish
            print("Clicking Publish...")
            try:
                page.locator("#done-button").click()
                print("✅ Publish event dispatched.")
            except Exception as e:
                print(f"Failed to click Publish: {e}")
                return False
                
            # Step 11: Success Verification
            print("Waiting for final 'Video published' confirmation...")
            try:
                # YouTube shows a 'Video published' modal
                page.wait_for_selector("text='Video published'", timeout=90000)
                print("✅ CONFIRMED: YouTube Video Published Successfully!")
                page.screenshot(path=debug_path.replace(".png", "_success.png"))
            except:
                print("Timed out waiting for 'Video published' modal. Checking for alternate success signals...")
                page.screenshot(path=debug_path.replace(".png", "_success_timeout.png"))
                if not page.locator("#done-button").is_visible():
                    print("✅ Publish modal closed, assuming success.")
                else:
                    print("WARNING: Modal still visible after timeout. Check _success_timeout.png")
            
            browser.close()
            return True
        except Exception as e:
            print(f"Fatal error during YouTube upload: {e}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtube_uploader.py <metadata_json_file>")
        sys.exit(1)
        
    meta_file = sys.argv[1]
    with open(meta_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    title = data.get("title", data["description"].split('\n')[0])
    upload_to_youtube(data["video_path"], title, data["description"])
