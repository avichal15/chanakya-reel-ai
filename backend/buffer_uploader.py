"""
Buffer Uploader — Chrome Profile Hijacker
Uses a COPY of Chrome Profile 12 (deadman150469@gmail.com) so that
the original Chrome can stay open while this script runs.
"""
import sys
import json
import os
import time
import shutil
import tempfile
from playwright.sync_api import sync_playwright

# Source Chrome profile
CHROME_USER_DATA = r"C:\Users\avich\AppData\Local\Google\Chrome\User Data"
PROFILE_NAME = "Profile 12"
BUFFER_URL = "https://publish.buffer.com/channels/69aa6d8c3f3b94a1211f27cc"

def copy_profile_to_temp():
    """Copy essential Chrome profile data to a temp dir to avoid lock conflicts."""
    temp_base = os.path.join(tempfile.gettempdir(), "chanakya_buffer_profile")
    
    # Clean previous temp copy if it exists
    if os.path.exists(temp_base):
        try:
            shutil.rmtree(temp_base, ignore_errors=True)
        except:
            pass
    
    os.makedirs(temp_base, exist_ok=True)
    
    src_profile = os.path.join(CHROME_USER_DATA, PROFILE_NAME)
    dst_profile = os.path.join(temp_base, PROFILE_NAME)
    
    print(f"Copying profile from {src_profile} to {dst_profile}...")
    
    # Copy the profile directory (skip lock files and heavy cache)
    skip_dirs = {"Cache", "Code Cache", "Service Worker", "GPUCache", "blob_storage",
                 "File System", "IndexedDB", "Session Storage", "ShaderCache"}
    skip_files = {"lockfile", "SingletonLock", "SingletonSocket", "SingletonCookie"}
    
    def copy_filtered(src, dst):
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if item in skip_files:
                continue
            if os.path.isdir(s):
                if item in skip_dirs:
                    continue
                try:
                    copy_filtered(s, d)
                except Exception as e:
                    print(f"  Skipping dir {item}: {e}")
            else:
                try:
                    shutil.copy2(s, d)
                except Exception as e:
                    print(f"  Skipping file {item}: {e}")
    
    copy_filtered(src_profile, dst_profile)
    
    # Also copy the root-level files needed by Chrome (Local State, etc.)
    for root_file in ["Local State"]:
        src_f = os.path.join(CHROME_USER_DATA, root_file)
        dst_f = os.path.join(temp_base, root_file)
        if os.path.exists(src_f):
            try:
                shutil.copy2(src_f, dst_f)
            except Exception as e:
                print(f"  Skipping root file {root_file}: {e}")
    
    print("Profile copy complete.")
    return temp_base


def upload_to_buffer(video_path, description_text):
    print(f"Upload starting for video: {video_path}")
    
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        return
    
    # Copy the profile to bypass Chrome's lock
    temp_user_data = copy_profile_to_temp()
    
    with sync_playwright() as p:
        try:
            print(f"Launching Chrome with copied {PROFILE_NAME}...")
            browser = p.chromium.launch_persistent_context(
                user_data_dir=temp_user_data,
                channel="chrome",
                args=[f"--profile-directory={PROFILE_NAME}"],
                headless=False,
                viewport={"width": 1280, "height": 720},
                timeout=60000
            )
            print("Chrome launched successfully!")
            
            page = browser.new_page()
            print(f"Navigating to Buffer: {BUFFER_URL}")
            page.goto(BUFFER_URL, timeout=60000, wait_until="domcontentloaded")
            
            # Wait for page to settle
            page.wait_for_timeout(5000)
            
            # Check if login was needed
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            if "login" in current_url.lower():
                print("Login page detected. Attempting Google login...")
                try:
                    google_btn = page.locator("text='Continue with Google'").or_(
                        page.locator("text='Log in with Google'")
                    ).or_(page.locator("text='Sign in with Google'"))
                    if google_btn.count() > 0:
                        google_btn.first.click()
                        page.wait_for_timeout(10000)
                except Exception as e:
                    print(f"Google login attempt: {e}")
                    print("Waiting 15s for manual fallback...")
                    page.wait_for_timeout(15000)
            
            # Ensure we're on the right page
            if "publish.buffer.com" not in page.url:
                print("Navigating to Buffer again...")
                page.goto(BUFFER_URL, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(5000)
            
            print("Looking for composer...")
            
            # Take a screenshot for debugging
            debug_ss = os.path.join(os.path.dirname(__file__), "buffer_debug_screenshot.png")
            page.screenshot(path=debug_ss)
            print(f"Debug screenshot saved: {debug_ss}")
            
            # Try multiple ways to open the composer
            composer_opened = False
            selectors = [
                "text='What would you like to share?'",
                "[data-testid='composer-placeholder']",
                "text='Create Post'",
                "button:has-text('New Post')",
                "button:has-text('Create')",
                "[role='textbox']",
                "div[contenteditable='true']",
            ]
            
            for sel in selectors:
                try:
                    el = page.locator(sel)
                    if el.count() > 0:
                        el.first.click()
                        composer_opened = True
                        print(f"Opened composer using: {sel}")
                        break
                except:
                    continue
            
            if not composer_opened:
                print("WARNING: Could not find composer element. Proceeding anyway...")
            
            page.wait_for_timeout(3000)
            
            # Attach the video file
            print("Attaching video file...")
            try:
                file_input = page.locator("input[type='file']")
                if file_input.count() > 0:
                    file_input.first.set_input_files(video_path)
                    print("Video file attached successfully!")
                    # Wait for upload processing
                    print("Waiting for video to process...")
                    page.wait_for_timeout(15000)
                else:
                    print("No file input found. Looking for drag-drop area...")
            except Exception as e:
                print(f"File attachment failed: {e}")
            
            # Type the description
            print("Typing caption/description...")
            try:
                textbox = page.locator("[role='textbox']").or_(
                    page.locator("div[contenteditable='true']")
                ).or_(page.locator("textarea"))
                
                if textbox.count() > 0:
                    textbox.first.click()
                    textbox.first.fill("")
                    page.keyboard.type(description_text, delay=5)
                    print("Caption typed successfully!")
                else:
                    print("No text input found.")
            except Exception as e:
                print(f"Caption typing failed: {e}")
            
            page.wait_for_timeout(2000)

            # Take another screenshot before submitting
            page.screenshot(path=debug_ss.replace(".png", "_pre_submit.png"))
            
            # Click Add to Queue
            print("Clicking submit button...")
            submit_selectors = [
                "button:has-text('Add to Queue')",
                "button:has-text('Share Now')",
                "button:has-text('Schedule Post')",
                "button:has-text('Save')",
            ]
            
            submitted = False
            for sel in submit_selectors:
                try:
                    btn = page.locator(sel)
                    if btn.count() > 0:
                        btn.first.click()
                        submitted = True
                        print(f"Clicked: {sel}")
                        break
                except:
                    continue
            
            if not submitted:
                print("WARNING: Could not find submit button.")
            
            page.wait_for_timeout(5000)
            
            # Final screenshot
            page.screenshot(path=debug_ss.replace(".png", "_result.png"))
            print("Upload process completed!")
            
            browser.close()
            
        except Exception as e:
            print(f"Error during upload: {e}")
            raise e
        finally:
            # Clean up temp profile
            try:
                shutil.rmtree(temp_user_data, ignore_errors=True)
            except:
                pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python buffer_uploader.py <metadata_json_file>")
        sys.exit(1)
        
    meta_file = sys.argv[1]
    with open(meta_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    upload_to_buffer(data["video_path"], data["description"])
