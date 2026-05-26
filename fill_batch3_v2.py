#!/usr/bin/env python3
"""补写第3批品牌（Adidas/Lego/Coca-Cola/Ferrari/L'Oreal）10语言完整内容"""
import json
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

def write_full(slug, langs):
    path = ROOT / slug / "brand.json"
    data = json.loads(path.read_text())
    data["languages"] = langs
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    ok = True
    for lang, text in langs.items():
        n = len(text)
        req = 800 if lang in ("zh-CN","ja","ko") else 1500
        flag = "" if n >= req else f" ✗({n}<{req})"
        if flag:
            ok = False
        print(f"  {lang}: {n}{flag}")
    print(f"  {'✅' if ok else '❌'} {slug}")
    return ok

all_ok = True

# ============ Adidas ============
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
print("=== Adidas ===")
