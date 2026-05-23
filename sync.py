#!/usr/bin/env python3
"""
自动同步脚本 — 凌晨5点执行
用途：
  1. 生成任务包备份（TASK_PACKAGE.md）
  2. 更新brands_done.json + 首页
  3. Git push到GitHub私有仓库
  4. 用cron触发：0 5 * * *
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


def bj_now():
    """获取北京时间"""
    try:
        result = subprocess.run(
            ["TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M'"],
            shell=True, capture_output=True, text=True
        )
        return result.stdout.strip()
    except:
        return datetime.now().strftime("%Y-%m-%d %H:%M")


def git_sync():
    """同步到GitHub"""
    try:
        # 检查是否有变化
        result = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT,
                               capture_output=True, text=True)
        if not result.stdout.strip():
            print("ℹ️  无变化，跳过同步")
            return
        
        subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-m", f"🔄 自动同步 {bj_now()} 北京时间"],
                       cwd=REPO_ROOT, check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT, check=True,
                       capture_output=True)
        print(f"✅ 自动同步完成: {bj_now()}")
        
        # 更新记忆记录
        last_sync = {"last_sync": bj_now(), "next_sync": "14天后"}
        (REPO_ROOT / ".last_sync.json").write_text(
            json.dumps(last_sync, ensure_ascii=False, indent=2)
        )
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 同步失败: {e}")


def sync_stats():
    """输出统计"""
    brands_file = REPO_ROOT / "brands_done.json"
    if brands_file.exists():
        with open(brands_file) as f:
            data = json.load(f)
        total = data["stats"]["total_brands"]
        pages = data["stats"]["total_pages"]
        print(f"📊 品牌数: {total} | 页面数: {pages}")
    else:
        print("📊 暂无品牌")


if __name__ == "__main__":
    print(f"🔄 开始自动同步: {bj_now()}")
    git_sync()
    sync_stats()
