import sys
import os
from pathlib import Path
import time

sys.path.append(str(Path(__file__).resolve().parent))
from backend.scheduler import run_automation_pipeline, wait_for_backend

def test():
    print("Waiting for backend...")
    if not wait_for_backend():
        print("Backend not available!")
        return
        
    print("\nTriggering automation pipeline test...")
    start = time.time()
    try:
        run_automation_pipeline()
        print(f"\nPipeline finished successfully in {time.time()-start:.1f}s!")
    except Exception as e:
        print(f"\nPipeline failed: {e}")

if __name__ == "__main__":
    test()
