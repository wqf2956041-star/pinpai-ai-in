#!/usr/bin/env python3
"""重新渲染所有品牌"""
import json, sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# 用 importlib 加载 brand_factory 模块
spec = importlib.util.spec_from_file_location("bf", ROOT / "brand_factory.py")
bf = importlib.util.module_from_spec(spec)
# 抑制 docstring 打印
sys.modules["bf"] = bf
spec.loader.exec_module(bf)

render_brand = bf.render_brand

# 扫描所有有brand.json的目录
rendered = []
failed = []
for d in sorted(ROOT.iterdir()):
    if not d.is_dir() or d.name == 'logs':
        continue
    bj_path = d / 'brand.json'
    if not bj_path.exists():
        continue
    slug = d.name
    try:
        data = json.loads(bj_path.read_text(encoding='utf-8'))
        html = render_brand(data)
        (d / 'index.html').write_text(html, encoding='utf-8')
        rendered.append(slug)
        print(f'OK: {slug}')
    except Exception as e:
        failed.append(slug)
        print(f'FAIL: {slug} - {e}')

print(f'\nDone. Rendered: {len(rendered)}, Failed: {len(failed)}')
if failed:
    print(f'Failed: {", ".join(failed)}')
