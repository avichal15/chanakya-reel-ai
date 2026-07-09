import sys
import os

# Add backend/services to sys.path slightly hacky
sys.path.append(os.path.join(os.getcwd(), 'backend', 'services'))
from thumbnail_engine import create_rage_thumbnail

output_path = "backend/output/test_rage_thumbnail.jpg"
os.makedirs("backend/output", exist_ok=True)
create_rage_thumbnail("STOP SCROLLING NOW", output_path)

if os.path.exists(output_path):
    print("SUCCESS: Thumbnail created at", output_path)
else:
    print("FAILED: Thumbnail not created.")
