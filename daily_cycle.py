#!/usr/bin/env python3
"""
daily_cycle.py — Complete brand cycle script for cron.
每15分钟运行一次。
1. 检查池子，如果 < 5 个则调用自动源补充
2. 运行心跳（取5个品牌 → Wikipedia内容 → 生成页面 → 更新索引 → 刷新首页）
"""
import sys, os, subprocess, json, time

BASE = "/workspace/pinpai-ai-in"
POOL_FILE = os.path.join(BASE, ".next_batch.json")
CYCLE_LOCK = os.path.join(BASE, ".cycle.lock")

# Lock check: 10 min expiry
if os.path.exists(CYCLE_LOCK):
    mtime = os.path.getmtime(CYCLE_LOCK)
    if time.time() - mtime < 600:
        sys.exit(0)
    os.remove(CYCLE_LOCK)
open(CYCLE_LOCK, "w").close()

os.chdir(BASE)

try:
    # 1. Check pool
    pool_size = 0
    if os.path.exists(POOL_FILE):
        with open(POOL_FILE) as f:
            pool_size = len(json.load(f))
    
    print(f"[{time.strftime('%H:%M')}] Pool: {pool_size} | Index: ", end="")
    try:
        idx = json.load(open("/var/www/pinpai/brands_index.json"))
        print(len(idx))
    except:
        print("?")
    
    # 2. Source more if pool low
    if pool_size < 3:
        print("Pool low! Sourcing...")
        result = subprocess.run(
            [sys.executable, "auto_source_brands.py"],
            capture_output=True, text=True, timeout=60
        )
        for line in result.stdout.split("\n"):
            if line.strip():
                print(f"  {line.strip()}")
    
    # 3. Run heartbeat
    result = subprocess.run(
        [sys.executable, "simple_heartbeat.py"],
        capture_output=True, text=True, timeout=120
    )
    for line in result.stdout.split("\n"):
        if line.strip():
            print(f"  {line.strip()}")

finally:
    if os.path.exists(CYCLE_LOCK):
        os.remove(CYCLE_LOCK)
