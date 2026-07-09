import sys
import json
import os
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

def upload_to_instagram(video_path, caption):
    print(f"Starting Instagram Upload for: {video_path}")
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        return False
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    bot_profile_dir = os.path.join(base_dir, "bot_profile")
    
    if not os.path.exists(bot_profile_dir):
        print("ERROR: bot_profile directory not found!")
        print("Please run `python setup_bot_profile.py` first to log into Instagram.")
        return False

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=bot_profile_dir,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars"
                ],
                ignore_default_args=["--enable-automation", "--no-sandbox"],
                headless=False,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 900},
                timeout=60000
            )
            page = browser.pages[0] if len(browser.pages) > 0 else browser.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
            
            # Add console logging for debugging JS injections
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            
            debug_ss = os.path.join(base_dir, "ig_bot_debug.png")
            
            # Step 1: Nav to Instagram
            print("Navigating to Instagram...")
            page.goto("https://www.instagram.com/", timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(5000)
            
            page.screenshot(path=debug_ss)
            
            if "login" in page.url or "accounts/login" in page.url:
                print("ERROR: Not logged into Instagram. The bot profile cookie expired.")
                print("Please run `python setup_bot_profile.py` to log back in.")
                page.screenshot(path=debug_ss.replace(".png", "_auth_error.png"))
                return False
                
            # Step 2: Trigger Create Modal via JS to bypass responsive CSS blocking
            # Step 2: Native SVG Create Trigger with Forced Bypasses
            print("Forcing Instagram Create State via SVG Click...")
            
            # Navigate to base URL to clear any weird routing states
            page.goto("https://www.instagram.com/", timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            try:
                # Force=True tells Playwright to ignore CSS overlapping/visibility checks and fire the raw event
                page.locator("svg[aria-label='New post']").locator("xpath=..").click(force=True, timeout=5000)
                print("Clicked Create SVG (Forced)")
            except:
                print("Failed to click SVG Create, trying exact text...")
                try:
                    page.locator("text='Create'").first.click(force=True, timeout=5000)
                except:
                    pass
            
            page.wait_for_timeout(2000)
            page.screenshot(path=debug_ss.replace(".png", "_step1_after_create.png"))
            
            print("Checking for Post/Live slideout menus...")
            try:
                post_btn = page.locator("text='Post'").first
                if post_btn.is_visible():
                    post_btn.click(force=True, timeout=5000)
                    print("Clicked Post Submenu (Forced)")
                    page.wait_for_timeout(2000)
                    page.screenshot(path=debug_ss.replace(".png", "_step2_after_post.png"))
            except:
                print("No slideout menu detected, proceeding to modal wait...")
            
            # Wait for the upload modal to actually pop up
            page.wait_for_selector("text='Drag photos and videos here'", timeout=15000)
            print("Modal is visible, proceeding...")
            page.screenshot(path=debug_ss.replace(".png", "_step3_modal_open.png"))
            
            # Step 3: Attach Video via Native File Chooser
            print("Attaching Video via File Chooser...")
            try:
                # Use Playwright's native file chooser which is more reliable than synthetic drag/drop
                with page.expect_file_chooser() as fc_info:
                    # Click "Select from computer" button
                    page.get_by_role("button", name="Select from computer").click()
                
                file_chooser = fc_info.value
                file_chooser.set_files(video_path)
                print("Video attached successfully via File Chooser.")
                
            except Exception as e:
                print(f"Fatal error attaching video: {e}")
                page.screenshot(path=debug_ss.replace(".png", "_attach_error.png"))
                return False
                
            page.wait_for_timeout(7000)
            
            # Close any informational popups (e.g., "Video posts are now shared as reels")
            print("Checking for informational popups...")
            try:
                ok_btn = page.get_by_role("button", name="OK").first
                if ok_btn.count() > 0:
                    print("Dispatching click on 'OK' modal...")
                    ok_btn.dispatch_event("click")
                    page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Error clearing OK modal: {e}")
            
            # Step 4: Click Next through cropping and filters
            print("Bypassing crop/filter stages...")
            for stage in ["Crop", "Filter"]:
                print(f"Attempting to advance from {stage} stage...")
                try:
                    # Wait for the preview stage to actually load (look for Next button or Crop toggle)
                    print(f"Waiting for {stage} interface to stabilize...")
                    page.wait_for_selector("button:has-text('Next'), [aria-label='Select crop']", timeout=30000)
                    
                    # Capture state after stabilization
                    page.screenshot(path=debug_ss.replace(".png", f"_{stage}_loaded.png"))
                    
                    if stage == "Crop":
                        print("Force-selecting 9:16 aspect ratio...")
                        ar_success = False
                        for ar_attempt in range(3):
                            try:
                                # 1. Click the aspect ratio toggle button
                                crop_toggle = page.locator("svg[aria-label='Select crop'], button:has(svg[aria-label='Select crop'])").first
                                if crop_toggle.is_visible(timeout=5000):
                                    print(f"Attempt {ar_attempt+1}: Found crop toggle, clicking...")
                                    crop_toggle.click()
                                    page.wait_for_timeout(1000)
                                    
                                    # 2. Select the 9:16 option
                                    ratio_9_16 = page.get_by_text("9:16", exact=True).first
                                    if ratio_9_16.is_visible(timeout=3000):
                                        print("Selecting 9:16 vertical format...")
                                        ratio_9_16.click()
                                        page.wait_for_timeout(1000)
                                        page.screenshot(path=debug_ss.replace(".png", "_9_16_applied.png"))
                                        ar_success = True
                                        break
                                    else:
                                        print("9:16 option button not visible yet.")
                                else:
                                    print("Crop toggle button not visible yet.")
                            except Exception as ar_e:
                                print(f"Aspect ratio attempt {ar_attempt+1} failed: {ar_e}")
                            page.wait_for_timeout(2000)
                        
                        if not ar_success:
                             print("Warning: Could not force 9:16 ratio after 3 attempts. Proceeding with default.")

                    # Try multiple selectors for the "Next" button in order of reliability
                    selectors = [
                        "button:has-text('Next')",
                        "div[role='button']:has-text('Next')",
                        "div[role='dialog'] [role='button']:has-text('Next')",
                        "text='Next'"
                    ]
                    
                    success_move = False
                    for selector in selectors:
                        try:
                            btn = page.locator(selector).first
                            if btn.is_visible(timeout=5000):
                                print(f"Found Next button with: {selector}. Clicking...")
                                btn.click(force=True)
                                page.wait_for_timeout(3000)
                                
                                # Verify if stage changed
                                next_text = "Filter" if stage == "Crop" else "Write a caption"
                                if page.get_by_text(next_text).count() > 0 or page.locator("div[aria-label='Write a caption...']").is_visible():
                                    print(f"Successfully moved past {stage} stage.")
                                    success_move = True
                                    break
                        except:
                            continue
                    
                    if not success_move:
                         print(f"Warning: Could not verify transition from {stage}. Trying dispatch fallback...")
                         page.get_by_role("button", name="Next").first.dispatch_event("click")
                         page.wait_for_timeout(3000)

                    # If we already see the caption box, we can stop clicking Next
                    if page.locator("div[aria-label='Write a caption...']").is_visible():
                        print("Reached caption stage successfully.")
                        break
                except Exception as e:
                    print(f"Failed to move from {stage}: {e}")
                    page.screenshot(path=debug_ss.replace(".png", f"_{stage}_error.png"))
                    if page.locator("div[aria-label='Write a caption...']").is_visible():
                        print("Caption box already visible, proceeding.")
                        break
                    
            # Step 5: Fill Caption
            print("Writing Caption...")
            try:
                caption_selector = "div[aria-label='Write a caption...']"
                page.wait_for_selector(caption_selector, timeout=20000)
                caption_box = page.locator(caption_selector).first
                caption_box.click(force=True)
                page.wait_for_timeout(1000)
                
                # Clear existing text if any and type
                for _ in range(20): page.keyboard.press("Backspace")
                page.keyboard.type(caption, delay=20)
                print(f"Caption typed ({len(caption)} chars)")
            except Exception as e:
                print(f"Could not write caption: {e}")
                page.screenshot(path=debug_ss.replace(".png", "_caption_error.png"))
                
            page.wait_for_timeout(2000)
            page.screenshot(path=debug_ss.replace(".png", "_pre_share.png"))
            
            # Step 6: Click Share
            print("Sharing Reel...")
            try:
                # Use robust multiple selectors same as Next buttons
                share_selectors = [
                    "button:has-text('Share')",
                    "div[role='button']:has-text('Share')",
                    "div[role='dialog'] [role='button']:has-text('Share')",
                    "text='Share'"
                ]
                
                # Pre-click capture
                page.screenshot(path=debug_ss.replace(".png", "_pre_share.png"))
                
                success_share = False
                for selector in share_selectors:
                    try:
                        btn = page.locator(selector).first
                        if btn.is_visible(timeout=5000):
                            print(f"Found Share button with: {selector}. Clicking...")
                            # Scroll into view just in case
                            btn.scroll_into_view_if_needed()
                            # Use physical click if possible
                            btn.click()
                            success_share = True
                            break
                    except:
                        continue
                
                if not success_share:
                    print("Warning: Standard Share click failed, trying Coordinate-based click...")
                    # Fallback: Find the 'Share' text and click its center
                    try:
                        share_text = page.get_by_text("Share", exact=True).first
                        box = share_text.bounding_box()
                        if box:
                            page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                            success_share = True
                            print("Coordinate click performed on 'Share' text.")
                    except:
                        pass
                
                if not success_share:
                    print("Last resort: Dispatching click event...")
                    page.get_by_role("button", name="Share").first.dispatch_event("click")
                
                print("✅ Share action performed.")
            except Exception as e:
                print(f"Critial failure at Share stage: {e}")
                page.screenshot(path=debug_ss.replace(".png", "_share_stage_error.png"))
                return False
                
            # Wait for upload completion confirmation
            print("Waiting for upload persistence (up to 120s)...")
            success_selector = "text='Your reel has been shared'"
            try:
                # Wait for either the success message OR the creation modal to disappear
                page.wait_for_selector(success_selector, timeout=120000)
                print("✅ CONFIRMED: Your reel has been shared.")
                page.screenshot(path=debug_ss.replace(".png", "_success.png"))
            except:
                print("Success message not found, checking if modal closed...")
                page.screenshot(path=debug_ss.replace(".png", "_final_check.png"))
                if not page.locator("div[role='dialog']").is_visible():
                    print("✅ Modal closed, assuming upload persistence complete.")
                else:
                    print("WARNING: Modal still visible. Upload may have stalled or failed.")
                    # Take one more shot of the full screen for debugging
                    page.screenshot(path=debug_ss.replace(".png", "_final_stalled.png"))
            
            # Absolute final wait to ensure network requests finish
            page.wait_for_timeout(5000)
            print("✅ Instagram Flow Complete.")
            
            browser.close()
            return True
            
        except Exception as e:
            print(f"Fatal error during Instagram upload: {e}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python instagram_uploader.py <metadata_json_file>")
        sys.exit(1)
        
    meta_file = sys.argv[1]
    with open(meta_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    try:
        desc = data["description"]
    except KeyError:
        desc = data.get("caption", "Chanakya Wisdom")
        
    upload_to_instagram(data["video_path"], desc)
