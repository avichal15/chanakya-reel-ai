"""Test runner for buffer_uploader.py that captures full output."""
import subprocess
import sys
import os

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
script = os.path.join(BACKEND_DIR, "buffer_uploader.py")
meta = os.path.join(BACKEND_DIR, "test_buffer_meta.json")
log = os.path.join(BACKEND_DIR, "buffer_full_log.txt")

result = subprocess.run(
    [sys.executable, script, meta],
    capture_output=True,
    text=True,
    timeout=120
)

with open(log, "w", encoding="utf-8") as f:
    f.write("=== STDOUT ===\n")
    f.write(result.stdout or "(empty)\n")
    f.write("\n=== STDERR ===\n")
    f.write(result.stderr or "(empty)\n")
    f.write(f"\n=== EXIT CODE: {result.returncode} ===\n")

print(f"Log written to {log}")
print(f"Exit code: {result.returncode}")
