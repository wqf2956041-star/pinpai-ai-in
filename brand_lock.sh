#!/bin/bash
# 品牌百科锁脚本
# 用途：防止多个cron同时处理品牌导致冲突丢包
# 每次cron启动时先检查锁，有锁则跳过，无锁则创建锁并继续

LOCKFILE="/workspace/pinpai-ai-in/.brand_worker.lock"
PIDFILE="/workspace/pinpai-ai-in/.brand_worker.pid"

# 检查锁文件和进程是否真实存活
if [ -f "$LOCKFILE" ]; then
    LOCK_TIME=$(cat "$LOCKFILE")
    NOW=$(date +%s)
    AGE=$((NOW - LOCK_TIME))
    
    # 如果锁存在但超过60分钟，视为死锁，可以清理
    if [ "$AGE" -gt 3600 ]; then
        echo "[LOCK] 锁已存在${AGE}秒（超过60分钟），视为死锁，清理后继续..."
        rm -f "$LOCKFILE" "$PIDFILE"
    else
        echo "[LOCK] 锁存在（${AGE}秒前创建），本轮跳过"
        exit 0
    fi
fi

# 创建锁（写入当前时间戳）
echo $(date +%s) > "$LOCKFILE"
echo $$ > "$PIDFILE"
echo "[LOCK] 锁已创建 (PID $$)"

# 设置退出时清理锁
cleanup() {
    rm -f "$LOCKFILE" "$PIDFILE"
    echo "[LOCK] 锁已清理"
}
trap cleanup EXIT

# 执行品牌处理任务
echo "[WORK] 开始处理品牌..."
