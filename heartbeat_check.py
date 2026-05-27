#!/usr/bin/env python3
"""品牌百科锁检查 + 心跳报告
cron的no_agent脚本：每10分钟检查一次锁状态
- 有锁且<60分钟 → 静默退出（不输出，不打扰）
- 有锁且>60分钟 → 清理死锁，输出提醒
- 无锁 → 输出心跳信号（触发agent开始工作）

配合cron的script模式 + no_agent=true使用。
输出非空 = 通知用户；输出空 = 静默跳过
"""
import os, time

LOCKFILE = "/workspace/pinpai-ai-in/.brand_worker.lock"
PIDFILE = "/workspace/pinpai-ai-in/.brand_worker.pid"

now = time.time()

if os.path.exists(LOCKFILE):
    try:
        lock_time = int(open(LOCKFILE).read().strip())
        age = now - lock_time
        if age > 3600:
            # 死锁，清理
            os.remove(LOCKFILE)
            if os.path.exists(PIDFILE):
                os.remove(PIDFILE)
            print(f"[HEARTBEAT] 死锁清理 (age={age:.0f}s)，请agent开始下一个品牌")
        else:
            # 正常工作中，静默跳过
            pass
    except (ValueError, OSError):
        # 锁文件损坏，清理
        os.remove(LOCKFILE)
        print("[HEARTBEAT] 锁文件损坏已清理")
else:
    # 空闲中，通知agent开始工作
    print("[HEARTBEAT] 空闲中，请处理下一个品牌")
