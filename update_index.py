#!/usr/bin/env python3
"""
首页更新脚本 — 每次生成品牌后，自动更新 index.html 的品牌列表

用法：
  python3 update_index.py
  
说明：
  读取 brands_done.json，生成 index.html 中的品牌目录列表
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
INDEX_FILE = REPO_ROOT / "index.html"
BRANDS_FILE = REPO_ROOT / "brands_done.json"


def update_index():
    try:
        with open(BRANDS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("⚠️  brands_done.json 不存在或无效，跳过首页更新")
        return
    
    brand_entries = []
    for slug, info in data.get("brands", {}).items():
        name_cn = info.get("name_cn", info.get("name", slug))
        name_en = info.get("name", "")
        brand_entries.append((slug, name_cn, name_en))
    
    # 按时间倒序（最新做的排最前）
    sorted_entries = sorted(
        brand_entries,
        key=lambda x: data["brands"].get(x[0], {}).get("done_at", ""),
        reverse=True
    )
    
    # 生成品牌列表HTML
    list_html = ""
    for slug, name_cn, name_en in sorted_entries:
        display = f"{name_cn} ({name_en})" if name_en else name_cn
        list_html += f'            <li><a href="/{slug}/">{display}</a></li>\n'
    
    # 读取index.html
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 替换品牌列表部分
    start_marker = '<!-- 由品牌生成器自动填充 -->'
    end_marker = '        </ul>'
    
    new_content = content.replace(
        f'{start_marker}\n{end_marker}',
        f'{start_marker}\n{list_html}        </ul>'
    )
    
    if content == new_content:
        print("ℹ️  品牌列表无变化，首页未更新")
    else:
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ 首页已更新: {len(sorted_entries)} 个品牌")


if __name__ == "__main__":
    update_index()
