"""Find which test file hangs during import."""
import subprocess
import sys
import os
import time

test_dir = os.path.join(os.path.dirname(__file__), "tests")
test_files = sorted(f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py"))

passed = []
failed = []
hung = []

for tf in test_files:
    path = os.path.join("tests", tf)
    print(f"  Collecting {tf}...", end=" ", flush=True)
    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", path, "--collect-only", "-q"],
            capture_output=True, text=True, timeout=15, cwd=os.path.dirname(__file__)
        )
        elapsed = time.time() - start
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            count = lines[-1] if lines else "?"
            print(f"OK ({elapsed:.1f}s) — {count}")
            passed.append(tf)
        else:
            print(f"ERROR ({elapsed:.1f}s)")
            # Print first 3 lines of stderr
            for line in (result.stderr or "").strip().split("\n")[:3]:
                print(f"    {line}")
            failed.append(tf)
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        print(f"HUNG! ({elapsed:.1f}s)")
        hung.append(tf)

print(f"\n{'='*60}")
print(f"PASSED: {len(passed)}  FAILED: {len(failed)}  HUNG: {len(hung)}")
if failed:
    print("\nFailed files:")
    for f in failed:
        print(f"  - {f}")
if hung:
    print("\nHung files (these block the full suite):")
    for f in hung:
        print(f"  - {f}")
