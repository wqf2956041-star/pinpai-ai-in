#!/usr/bin/env python3
"""翻译工具：读取brands_today.json，生成翻译占位文件用于分步翻译"""
import json

LANG_MAP = {
    "en": "English",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "pt": "Portuguese",
    "ar": "Arabic"
}

with open("brands_today.json", "r") as f:
    data = json.load(f)

print("=== 品牌翻译任务清单 ===")
for brand in data["brands"]:
    name = brand["name"]
    name_en = brand["name_en"]
    desc = brand["desc"]
    print(f"\n{'='*60}")
    print(f"品牌: {name} ({name_en})")
    print(f"需要翻译: 9种语言 × {len(desc)} 字")
    print(f"{'='*60}")
    print(f"【原始中文】")
    print(desc)
    print(f"\n--- 翻译指令 ---")
    print(f"请将以上中文翻译成以下9种语言（保持专业品牌百科风格，约{len(desc)}字为宜）：")
    for code, lang_name in LANG_MAP.items():
        print(f"  {code}: {lang_name}")
    print(f"\n输出格式（JSON）：")
    print(f'{{"{name_en}": {{"en": "...", "fr": "...", ...}}}}')
