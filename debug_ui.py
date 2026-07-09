"""
Comprehensive UI debugger.
Fetches the page, checks for errors, and tests all API endpoints.
"""
import requests
import time

BASE = "http://localhost:5173"
API = "http://127.0.0.1:8000"

def check(label, url, method="GET", json_data=None, timeout=15):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    try:
        if method == "GET":
            r = requests.get(url, timeout=timeout)
        else:
            r = requests.post(url, json=json_data, timeout=timeout)
        
        print(f"  Status: {r.status_code}")
        ct = r.headers.get("content-type", "")
        print(f"  Content-Type: {ct}")
        
        if r.status_code != 200:
            print(f"  ERROR Body: {r.text[:500]}")
            return None
        
        if "html" in ct:
            body = r.text
            # Check for script tags
            import re
            scripts = re.findall(r'<script[^>]*src="([^"]*)"', body)
            print(f"  Scripts found: {scripts}")
            
            # Check for error indicators
            if "error" in body.lower():
                print("  WARNING: 'error' found in HTML")
            
            # Check for the root div
            if 'id="root"' in body:
                print("  OK: #root div found")
            else:
                print("  ERROR: #root div NOT found!")
                
            # Check for import map (should be removed)
            if "importmap" in body:
                print("  ERROR: importmap STILL in HTML!")
            else:
                print("  OK: No importmap found")
            
            # Check for tailwind CDN (should be removed)
            if "cdn.tailwindcss" in body:
                print("  ERROR: Tailwind CDN STILL in HTML!")
            else:
                print("  OK: No Tailwind CDN")
                
            # Print the full HTML for review
            print(f"\n  --- Full HTML ({len(body)} bytes) ---")
            print(body)
            print("  --- End HTML ---")
            
        elif "javascript" in ct or "module" in ct:
            body = r.text
            print(f"  JS Size: {len(body)} bytes")
            # Check first 500 chars
            print(f"  JS Preview: {body[:300]}...")
            
        elif "json" in ct:
            data = r.json()
            print(f"  JSON: {str(data)[:500]}")
            return data
        elif "css" in ct:
            body = r.text
            print(f"  CSS Size: {len(body)} bytes")
            if len(body) < 100:
                print(f"  WARNING: CSS seems very small!")
                print(f"  CSS Content: {body}")
            else:
                print(f"  OK: CSS loaded ({len(body)} bytes)")
        else:
            print(f"  Body preview: {r.text[:300]}")
            
        return r
    except Exception as e:
        print(f"  FAILED: {e}")
        return None

print("=" * 60)
print("  CHANAKYA REEL AI - COMPREHENSIVE UI DEBUG")
print("=" * 60)

# 1. Check if frontend serves HTML
check("1. Frontend HTML (Vite)", BASE)

# 2. Check if CSS loads
check("2. CSS File", f"{BASE}/index.css")

# 3. Check if main JS bundle loads
check("3. Main JS (index.tsx)", f"{BASE}/index.tsx")

# 4. Check backend health
check("4. Backend Health", f"{API}/api/health")

# 5. Test generate-script endpoint directly
print("\n" + "=" * 60)
print("  5. Testing /api/generate-script (via proxy)")
print("=" * 60)
result = check("5a. Via Proxy", f"{BASE}/api/generate-script", "POST", {
    "quote": "Truth is bitter",
    "philosopher": "Chanakya",
    "rage_level": 5
})

result2 = check("5b. Direct Backend", f"{API}/api/generate-script", "POST", {
    "quote": "Truth is bitter",
    "philosopher": "Chanakya",
    "rage_level": 5
})

if result2:
    print("\n  Script generation works! Checking response structure...")
    data = result2.json() if hasattr(result2, 'json') else result2
    if isinstance(data, dict):
        print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        if 'sections' in data:
            print(f"  Sections count: {len(data['sections'])}")
            for i, s in enumerate(data['sections']):
                print(f"    [{i}] type={s.get('type','?')}, content={s.get('content','?')[:50]}...")
        if 'fullText' in data:
            print(f"  fullText length: {len(data['fullText'])}")
        if 'id' in data:
            print(f"  id: {data['id']}")

print("\n\nDEBUG COMPLETE.")
