
import sys
import os

# Add backend to path
backend_dir = os.path.join(os.getcwd(), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from scheduler import run_automation_pipeline

if __name__ == "__main__":
    print("🚀 Starting End-to-End Automation Test...")
    run_automation_pipeline()
    print("🏁 Test run completed.")
