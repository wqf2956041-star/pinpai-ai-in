#!/usr/bin/env python3
"""
brand_cycle.py — Self-sustaining brand encyclopedia cycle.
1. Source new brands from Wikipedia if pool runs low
2. Run heartbeat to deploy next batch
3. Git push

No user interaction needed. Runs autonomously forever.
"""
import sys, os, subprocess, json

BASE = "/workspace/pinpai-ai-in"
LOCK_FILE = os.path.join(BASE, ".brand_cycle.lock")

# Lock check
if os.path.exists(LOCK_FILE):
    import time as t
    if t.time() - os.path.getmtime(LOCK_FILE) < 1200:  # 20 min lock
        print("LOCKED")
        sys.exit(0)
    os.remove(LOCK_FILE)
open(LOCK_FILE, "w").close()

os.chdir(BASE)

try:
    # Step 1: Check current pool and brand count
    total_before = 0
    with open("brands_index.json") as f:
        total_before = len(json.load(f))

    pool_exists = os.path.exists(".next_batch.json")
    pool_remaining = 0
    if pool_exists:
        with open(".next_batch.json") as f:
            pool_remaining = len(json.load(f))

    print(f"📊 Current: {total_before} brands | Pool: {pool_remaining}")

    # Step 2: Source more brands if pool < 5
    if pool_remaining < 5:
        print("🔍 Sourcing more brands from Wikipedia...")
        result = subprocess.run(
            [sys.executable, "auto_source_brands.py"],
            capture_output=True, text=True, timeout=60
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr[:500])

    # Step 3: Run heartbeat
    print("🚀 Running heartbeat...")
    result = subprocess.run(
        [sys.executable, "brand_heartbeat.py"],
        capture_output=True, text=True, timeout=120
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[:500])

    # Step 4: Final count
    total_after = 0
    with open("brands_index.json") as f:
        total_after = len(json.load(f))

    added = total_after - total_before
    if added > 0:
        print(f"\n✅ Cycle complete: +{added} brands (total: {total_after})")
    else:
        print(f"\n⏸️ No new brands this cycle (total: {total_after})")

    # Step 5: Sync gh-pages branch
    print("🔄 Syncing gh-pages branch...")
    subprocess.run(["git", "config", "user.email", "robot@pinpai.ai.in"],
                   capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Brand Bot"],
                   capture_output=True, text=True)

    # Commit and push main first
    subprocess.run(["git", "add", "-A", "."], capture_output=True, text=True)
    result_commit = subprocess.run(["git", "commit", "-m", f"auto: cycle +{added} brands"],
                                   capture_output=True, text=True)
    if result_commit.returncode == 0 or "nothing to commit" in result_commit.stdout:
        subprocess.run(["git", "push", "origin", "main"],
                       capture_output=True, text=True, timeout=30)
        print("✅ main pushed")

    # Sync gh-pages: checkout, merge main, push
    result = subprocess.run(
        ["git", "push", "origin", "main:gh-pages"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        print("✅ gh-pages synced (fast-forward)")
    else:
        # If fast-forward fails, do proper merge
        subprocess.run(["git", "fetch", "origin", "gh-pages"],
                       capture_output=True, text=True)
        subprocess.run(["git", "checkout", "gh-pages"],
                       capture_output=True, text=True)
        merge = subprocess.run(["git", "merge", "main"],
                               capture_output=True, text=True)
        print(merge.stdout.strip() if merge.stdout else "merge done")
        subprocess.run(["git", "push", "origin", "gh-pages"],
                       capture_output=True, text=True, timeout=30)
        subprocess.run(["git", "checkout", "main"],
                       capture_output=True, text=True)
        print("✅ gh-pages synced (merge)")

finally:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
