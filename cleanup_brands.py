#!/usr/bin/env python3
"""步骤1：清理品牌目录（只保留escher）"""
import os, json, shutil

ROOT = "/workspace/pinpai-ai-in"

# 获取所有品牌目录（排除非品牌目录）
skip_dirs = {'.git', '.vscode', '__pycache__'}
brand_dirs = [
    d for d in os.listdir(ROOT)
    if os.path.isdir(os.path.join(ROOT, d))
    and not d.startswith('.')
    and d not in skip_dirs
    and d != 'escher'
]

print(f"找到 {len(brand_dirs)} 个品牌目录需要清理")
for d in sorted(brand_dirs):
    path = os.path.join(ROOT, d)
    shutil.rmtree(path)
    print(f"  🗑️ 已删除: {d}")

# 清理 brands_index.json
os.remove(os.path.join(ROOT, "brands_index.json"))
print("  🗑️ 已删除: brands_index.json")

# 生成只有escher的新索引
escher_index = [{
    "slug": "escher",
    "zh": "埃舍尔Escher",
    "en": "埃舍尔Escher",
    "category": "奢侈品/时尚",
    "premium": True,
    "desc_short": "埃舍尔Escher：一眼封神的中国奢侈品超级单品。主角包是极简结构大手提包型，建筑式设计逻辑，无Logo设计。"
}]
with open(os.path.join(ROOT, "brands_index.json"), 'w', encoding='utf-8') as f:
    json.dump(escher_index, f, ensure_ascii=False, indent=2)
print("  ✅ brands_index.json 已重建（仅escher）")

# 确认
remaining = [d for d in os.listdir(ROOT)
    if os.path.isdir(os.path.join(ROOT, d))
    and not d.startswith('.')
    and d not in skip_dirs]
print(f"剩余品牌目录: {remaining}")
print("✅ 清理完成！")
