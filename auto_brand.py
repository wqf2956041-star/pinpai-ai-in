#!/usr/bin/env python3
"""
Auto Brand Pipeline — 自动化品牌生成部署流水线
每批处理5个品牌（从品牌池取），完整包含：
  1. 从 brand_pool.json 取待处理品牌（先查 master.csv 去重）
  2. 生成10语言内容（AI独立重写，非翻译）
  3. init + fill brand.json
  4. render index.html
  5. 验证（字数、语言独立性、功能完整）
  6. 更新 brands_index.json + sitemap.xml
  7. git add + commit + push
"""
import csv, json, os, re, sys
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")
CSV_PATH = ROOT / "master.csv"
POOL_PATH = ROOT / "brand_pool.json"
INDEX_PATH = ROOT / "brands_index.json"
SITEMAP_PATH = ROOT / "sitemap.xml"

BATCH_SIZE = 5

CJK_LANGS = {"zh-CN", "ja", "ko"}
CJK_THRESH = 800
NON_CJK_THRESH = 1500

LANG_ORDER = [
    ("zh-CN","中文"),("en","English"),("fr","Français"),("es","Español"),
    ("de","Deutsch"),("ja","日本語"),("ko","한국어"),("pt","Português"),
    ("ru","Русский"),("ar","العربية")
]

def slugify(name):
    """品牌名转slug"""
    s = name.lower().replace("&","and").replace(".","-").replace("'","").replace(" ","-").replace("--","-").strip("-")
    replacements = {'é':'e','è':'e','ê':'e','ë':'e','à':'a','â':'a','ô':'o','ö':'o','û':'u','ü':'u','ù':'u','ç':'c','ì':'i','î':'i','œ':'oe','ÿ':'y'}
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s

def load_pool():
    return json.loads(POOL_PATH.read_text(encoding="utf-8"))

def load_master():
    existing = set()
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing.add(row['slug'])
    return existing

def add_to_master(entries):
    """添加品牌到master.csv"""
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        header = reader.fieldnames or ['slug','name_en','name_zh','category','country','deployed']
    
    for entry in entries:
        rows.append({
            'slug': entry['slug'],
            'name_en': entry['name_en'],
            'name_zh': entry['name_zh'],
            'category': entry['category'],
            'country': entry.get('country',''),
            'deployed': 'false'
        })
    
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ master.csv: 新增 {len(entries)} 个品牌")

def init_brand(slug):
    """初始化brand.json模板"""
    brand_dir = ROOT / slug
    brand_dir.mkdir(parents=True, exist_ok=True)
    json_path = brand_dir / "brand.json"
    
    if json_path.exists():
        return True  # 已存在
    
    template = {
        "slug": slug,
        "names": {"zh-CN": "", "en": slug},
        "category": "",
        "founding_year": "",
        "founding_location": "",
        "founder": "",
        "official_website": "",
        "main_business": [],
        "current_slogan": "",
        "description_zh": "",
        "languages": {},
        "is_premium": False,
        "image_url": "",
        "similar_brands": []
    }
    json_path.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"  ✅ {slug}: brand.json 模板已初始化")
    return True

def get_pending_brands():
    """从pool取待处理品牌"""
    pool = load_pool()
    existing = load_master()
    
    pending = []
    for b in pool:
        s = slugify(b['name_en'])
        if s not in existing:
            b['slug'] = s
            pending.append(b)
            if len(pending) >= BATCH_SIZE:
                break
    
    return pending

def generate_content(brand):
    """生成品牌内容 — 返回填充内容"""
    slug = brand['slug']
    name_en = brand['name_en']
    name_zh = brand['name_zh']
    category = brand.get('category', 'general')
    country = brand.get('country', '')
    founder = brand.get('founder', '')
    year = brand.get('year', '')
    website = brand.get('website', '')
    desc_en = brand.get('description_en', f'{name_en} is a {category} brand from {country}.')
    desc_zh = brand.get('description_zh', f'{name_zh}是来自{country}的{category}品牌。')
    
    return {
        'slug': slug,
        'names': {'zh-CN': name_zh, 'en': name_en},
        'category': category,
        'country': country,
        'founder': founder,
        'founding_year': str(year) if year else '',
        'founding_location': country,
        'official_website': website,
        'main_business': [category],
        'current_slogan': '',
        'description_zh': desc_zh,
        'description_en': desc_en,
        'is_premium': False,
        'image_url': '',
        'similar_brands': []
    }

def fill_brand_json(slug, data, languages):
    """填充brand.json的完整内容"""
    path = ROOT / slug / "brand.json"
    bj = json.loads(path.read_text(encoding="utf-8"))
    
    bj['names'] = data['names']
    bj['category'] = data['category']
    bj['founding_year'] = data['founding_year']
    bj['founding_location'] = data['founding_location']
    bj['founder'] = data['founder']
    bj['official_website'] = data['official_website']
    bj['main_business'] = data['main_business']
    bj['current_slogan'] = data['current_slogan']
    bj['description_zh'] = data['description_zh']
    bj['languages'] = languages
    bj['is_premium'] = data['is_premium']
    bj['similar_brands'] = data.get('similar_brands', [])
    
    path.write_text(json.dumps(bj, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 验证
    en = languages.get("en", "")
    for lang, content in languages.items():
        thresh = CJK_THRESH if lang in CJK_LANGS else NON_CJK_THRESH
        n = len(content)
        eq = content == en
        flag = "✅" if n >= thresh and not eq else "❌"
        print(f"    {flag} {lang}: {n} chars{' (=EN!)' if eq else ''}")

def render_brand(slug):
    """调用 brand_factory.py 渲染"""
    result = os.system(f'cd {ROOT} && python3 brand_factory.py process {slug}')
    return result == 0

def update_index_and_sitemap(new_slugs):
    """更新 brands_index.json 和 sitemap.xml"""
    # 读取现有index
    if INDEX_PATH.exists():
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    else:
        index = []
    
    existing_slugs = {e['slug'] for e in index}
    
    for slug in new_slugs:
        json_path = ROOT / slug / "brand.json"
        if not json_path.exists():
            continue
        bj = json.loads(json_path.read_text(encoding="utf-8"))
        entry = {
            "name": bj.get("names", {}).get("zh-CN", slug),
            "en": bj.get("names", {}).get("en", slug),
            "slug": slug,
            "category": bj.get("category", ""),
            "description": bj.get("description_zh", "")[:200]
        }
        if slug not in existing_slugs:
            index.append(entry)
            existing_slugs.add(slug)
    
    json.dump(index, open(INDEX_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ brands_index.json: {len(index)} 个品牌")
    
    # 更新sitemap
    def gen_sitemap(brands):
        urls = ""
        for b in brands:
            urls += f"""  <url>
    <loc>https://pinpai.ai.in/{b}/</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
"""
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>"""
    
    all_slugs = [e['slug'] for e in index]
    SITEMAP_PATH.write_text(gen_sitemap(all_slugs), encoding="utf-8")
    print(f"✅ sitemap.xml: {len(all_slugs)} 个URL")

def verify_deployed(slugs):
    """在线验证已部署的品牌"""
    print("\n🔍 在线验证...")
    for slug in slugs:
        # 跳过local验证（因为还没git push）
        json_path = ROOT / slug / "brand.json"
        bj = json.loads(json_path.read_text(encoding="utf-8"))
        langs = bj.get("languages", {})
        en = langs.get("en", "")
        
        ok = True
        issues = []
        for lang in ["zh-CN", "en", "fr", "es", "de", "ja", "ko", "pt", "ru", "ar"]:
            content = langs.get(lang, "")
            n = len(content)
            thresh = CJK_THRESH if lang in CJK_LANGS else NON_CJK_THRESH
            eq = content == en
            if n < thresh:
                ok = False
                issues.append(f"{lang}: {n}chars < {thresh}")
            if eq and lang != "en":
                ok = False
                issues.append(f"{lang}: =EN")
        
        print(f"  {'✅' if ok else '❌'} {slug}: {'; '.join(issues) if issues else 'ALL PASS'}")

def git_push(batch_name):
    """git提交并推送"""
    os.chdir(str(ROOT))
    os.system("git add -A")
    msg = f"feat: add batch — {batch_name}"
    ret = os.system(f'git commit -m "{msg}" --allow-empty')
    result = os.system("git push")
    if result == 0:
        print(f"✅ git push 成功")
    else:
        print(f"❌ git push 失败（可能是网络问题）")
    return result == 0

def run_batch():
    """运行一批处理"""
    print(f"{'='*60}")
    print(f"📦 品牌百科自动化 — 新一批处理")
    print(f"{'='*60}")
    
    pending = get_pending_brands()
    if not pending:
        print("✅ 品牌池已空！所有品牌已完成处理。")
        return False
    
    print(f"\n本次待处理 {len(pending)} 个品牌:")
    for b in pending:
        print(f"  📌 {b['name_en']} ({b['name_zh']}) — {b.get('category','')}")
    
    # Step 1: 添加master.csv + init
    print("\n📋 Step 1: 注册品牌...")
    add_to_master([{
        'slug': b['slug'],
        'name_en': b['name_en'],
        'name_zh': b['name_zh'],
        'category': b.get('category', ''),
        'country': b.get('country', '')
    } for b in pending])
    
    for b in pending:
        init_brand(b['slug'])
    
    # Step 2: 生成内容 — 各个品牌独立处理
    print("\n📝 Step 2: 生成10语言内容（需要在AI中执行）")
    print(f"   请在下一个execute_code调用中填充 {len(pending)} 个品牌的内容")
    
    batch_names = ", ".join([b['name_en'] for b in pending])
    print(f"\n✅ 品牌已注册，批次: {batch_names}")
    print(f"   total masters.csv pending: {len(pending)}")
    
    return True, pending, batch_names

def check_and_save_state(pending):
    """保存批次状态到文件，供后续步骤使用"""
    state = {
        'batch_slugs': [b['slug'] for b in pending],
        'batch_names': {b['slug']: {'en': b['name_en'], 'zh': b['name_zh'], 'category': b.get('category','')} for b in pending}
    }
    (ROOT / '.batch_state.json').write_text(json.dumps(state, ensure_ascii=False), encoding='utf-8')
    print(f"✅ 批次状态已保存到 .batch_state.json")

if __name__ == "__main__":
    result = run_batch()
    if isinstance(result, tuple):
        _, pending, batch_names = result
        check_and_save_state(pending)
        print(f"\n🚀 批次: {batch_names}")
        print(f"   准备就绪，请调用 fill_batch_content 来填充10语言内容")
