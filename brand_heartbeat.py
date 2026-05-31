#!/usr/bin/env python3
"""
brand_heartbeat.py — Autonomous brand encyclopedia heartbeat.
Flow: generate page -> copy to /var/www/pinpai/ -> git push -> write index (only if page succeeds).
Uses pre-defined brand list from .next_batch.json.
If pool empty, calls auto_source_brands.py to refill.
"""
import json, os, csv, re, sys, shutil, subprocess

BASE = "/workspace/pinpai-ai-in"
WWW = "/var/www/pinpai"
LOCK_FILE = os.path.join(BASE, ".heartbeat.lock")

RENDER_JS = """
// ===== 品牌渲染（仅前20个 + 加载更多） =====
var currentLang = 'zh-CN';
var DISPLAY_COUNT = 20;
var currentCount = DISPLAY_COUNT;

function renderBrands(lang) {
    var list = document.getElementById('brand-list');
    if (!list) return;
    var html = '';
    var count = Math.min(currentCount, brandsData.length);
    for (var i = 0; i < count; i++) {
        var b = brandsData[i];
        var name = b.name;
        var nameEn = b.name_en || b.name;
        html += '<a class="brand-card" href="/' + b.slug + '/">';
        html += '<h2>' + name + '</h2>';
        html += '<div class="en">' + nameEn + '</div>';
        if (b.category) html += '<span class="cat-tag">' + b.category + '</span>';
        html += '</a>';
    }
    if (count < brandsData.length) {
        html += '<div style="text-align:center;padding:20px">';
        html += '<button onclick="loadMore()" style="padding:12px 36px;background:#222;color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer">加载更多品牌 ↓</button>';
        html += '</div>';
    }
    list.innerHTML = html;
    var el = document.querySelector('.brand-count');
    if (el) el.textContent = '共 ' + brandsData.length + ' 个品牌 · 显示前 ' + count + ' 个';
}

function loadMore() {
    currentCount += DISPLAY_COUNT;
    if (currentCount > brandsData.length) currentCount = brandsData.length;
    renderBrands(currentLang);
}

function switchLang(lang) {
    currentLang = lang;
    var tabs = document.querySelectorAll('.lang-tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove('active');
        if (tabs[i].getAttribute('onclick').indexOf(lang) >= 0) {
            tabs[i].classList.add('active');
        }
    }
    renderBrands(lang);
}

function searchBrand() {
    var input = document.getElementById('search-input');
    var query = input.value.toLowerCase().trim();
    var list = document.getElementById('brand-list');
    if (!list) return;
    if (!query) { currentCount = DISPLAY_COUNT; renderBrands(currentLang); return; }
    var html = '';
    for (var i = 0; i < brandsData.length; i++) {
        var b = brandsData[i];
        var name = (b.name || '').toLowerCase();
        var nameEn = (b.name_en || '').toLowerCase();
        if (name.indexOf(query) >= 0 || nameEn.indexOf(query) >= 0) {
            html += '<a class="brand-card" href="/' + b.slug + '/">';
            html += '<h2>' + b.name + '</h2>';
            html += '<div class="en">' + (b.name_en || b.name) + '</div>';
            if (b.category) html += '<span class="cat-tag">' + b.category + '</span>';
            html += '</a>';
        }
    }
    if (!html) html = '<div style="padding:30px;text-align:center;color:#999">未找到匹配的品牌</div>';
    list.innerHTML = html;
    var el = document.querySelector('.brand-count');
    if (el) el.textContent = '搜索结果';
}

document.addEventListener('DOMContentLoaded', function() {
    renderBrands('zh-CN');
});
"""

def _update_index_html():
    """Regenerate brandsData — remove ALL old var brandsData blocks, then append one at end of </script>."""
    with open(os.path.join(BASE, "brands_index.json")) as f:
        idx = json.load(f)
    with open(os.path.join(BASE, "index.html")) as f:
        html = f.read()

    # Remove ALL existing var brandsData = [...]; blocks (there may be duplicates from old bugs)
    html = re.sub(r'// ===== 品牌数据 =====\s*\nvar brandsData = \[[\s\S]*?\];\s*', '', html)

    # Build new brandsData from JSON index
    lines = []
    for b in reversed(idx):
        t = b.get('t', 1)
        def esc(s):
            return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
        line = ('{name:"' + esc(b['name']) +
                '",name_en:"' + esc(b.get('name_en', '')) +
                '",slug:"' + esc(b['slug']) +
                '",category:"' + esc(b.get('category', '')) +
                '",t:' + str(t) + '}')
        lines.append(line)
    new_data = ",\n".join(lines)
    new_block = ("\n// ===== 品牌数据 =====\nvar brandsData = [\n" + new_data + "\n];\n" + RENDER_JS)

    # Insert before last </script> tag or append before </html>
    insert_pos = html.rfind('</script>')
    if insert_pos < 0:
        insert_pos = html.rfind('</html>')
    html = html[:insert_pos] + new_block + html[insert_pos:]

    with open(os.path.join(BASE, "index.html"), "w") as f:
        f.write(html)
    # CRITICAL: Sync to www directory
    import shutil, subprocess
    shutil.copy2(os.path.join(BASE, "index.html"), "/tmp/pinpai_index.html")
    subprocess.run(["sudo", "cp", "/tmp/pinpai_index.html", os.path.join(WWW, "index.html")], capture_output=True)
    subprocess.run(["sudo", "chown", "caddy:caddy", os.path.join(WWW, "index.html")], capture_output=True)
    print("   index.html updated (" + str(len(idx)) + " brands)")

# Lock to prevent concurrent runs
if os.path.exists(LOCK_FILE):
    import time
    mtime = os.path.getmtime(LOCK_FILE)
    if time.time() - mtime < 1800:  # 30 min lock expiry
        print("LOCKED - another heartbeat may be running")
        sys.exit(0)
    else:
        os.remove(LOCK_FILE)

open(LOCK_FILE, "w").close()

try:
    # --- Read current state ---
    with open(os.path.join(BASE, "brands_index.json")) as f:
        index = json.load(f)
    existing_slugs = set(b['slug'] for b in index)

    # Read master.csv to find brands already in csv
    csv_slugs = set()
    with open(os.path.join(BASE, "master.csv"), newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        try:
            header = next(reader)
        except StopIteration:
            header = ["slug","name","name_en","category","founding_location","founding_year","deployed"]
        for row in reader:
            if row and len(row) >= 1:
                csv_slugs.add(row[0].strip())

    # --- Load next batch from pre-defined brand list ---
    batch_file = os.path.join(BASE, ".next_batch.json")
    if os.path.exists(batch_file):
        with open(batch_file) as f:
            remaining = json.load(f)
    else:
        # If pool is gone, try to refill from auto_source_brands
        print("Pool empty, sourcing more brands from Wikipedia...")
        result = subprocess.run(
            [sys.executable, os.path.join(BASE, "auto_source_brands.py")],
            capture_output=True, text=True, timeout=60
        )
        print(result.stdout[:500])
        if os.path.exists(batch_file):
            with open(batch_file) as f:
                remaining = json.load(f)
        else:
            print("No brands sourced. Nothing to do.")
            sys.exit(0)

    # Filter out already existing brands in workspace dir (we check /var/www for deployment)
    # For safety, filter out brands already in the index
    to_add = [b for b in remaining if b['slug'] not in existing_slugs]

    if not to_add:
        print("All brands completed! No more to add.")
        if os.path.exists(batch_file):
            os.remove(batch_file)
        os.remove(LOCK_FILE)
        sys.exit(0)

    # Take next batch (10 per run)
    BATCH_SIZE = 10
    batch = to_add[:BATCH_SIZE]
    new_remaining = to_add[BATCH_SIZE:]

    # Save remaining for next run
    json.dump(new_remaining, open(batch_file, "w"))

    # --- Generate brand pages ---
    added_count = 0
    successfully_deployed = []  # track brands that fully succeeded

    for b in batch:
        slug = b["slug"]
        name_zh = b["name"]
        name_en = b.get("name_en", name_zh)
        category = b.get("category", "")

        brand_dir = os.path.join(BASE, slug)
        www_dir = os.path.join(WWW, slug)

        # --- STEP 1: Create brand.json ---
        founding_year_str = ""
        if b.get("founding_year"):
            founding_year_str = "，创立于" + str(b["founding_year"]) + "年。"
        description_slogan = b.get("slogan") or b.get("description", "")
        description_en = name_en + " is a global brand"
        if b.get("founding_year"):
            description_en += " founded in " + str(b["founding_year"])

        brand_json = {
            "slug": slug, "name_en": name_en, "name_zh": name_zh,
            "category": category, "country": b.get("country", ""),
            "founder": b.get("founder", ""), "year": b.get("founding_year", 0),
            "website": b.get("website", ""),
            "wikidata_id": "",
            "description_en": description_en + ".",
            "description_zh": name_zh + "（" + name_en + "）是全球知名品牌" + founding_year_str + description_slogan,
            "languages": {}
        }
        os.makedirs(brand_dir, exist_ok=True)
        with open(os.path.join(brand_dir, "brand.json"), "w") as f:
            json.dump(brand_json, f, ensure_ascii=False, indent=2)

        # --- STEP 2: Create index.html from adidas template ---
        template_dir = os.path.join(BASE, "adidas")
        template_path = os.path.join(template_dir, "index.html")
        if not os.path.exists(template_path):
            print("No template for " + slug + " -- skipping")
            continue

        with open(template_path) as f:
            template_html = f.read()

        html = template_html.replace("adidas", slug)
        html = html.replace("阿迪达斯", name_zh)
        html = html.replace("Adidas", name_en)
        html = html.replace('category: "sport"', 'category: "' + category + '"')

        brand_html_path = os.path.join(brand_dir, "index.html")
        with open(brand_html_path, "w") as f:
            f.write(html)

        # --- STEP 3: Copy to /var/www/pinpai/ ---
        os.makedirs(www_dir, exist_ok=True)
        shutil.copy2(brand_html_path, os.path.join(www_dir, "index.html"))
        shutil.copy2(os.path.join(brand_dir, "brand.json"), os.path.join(www_dir, "brand.json"))

        # --- STEP 4: Verify copy succeeded ---
        if not os.path.exists(os.path.join(www_dir, "index.html")):
            print("FAILED to copy " + slug + " to www -- rolling back index write")
            continue

        # Mark as successfully deployed
        successfully_deployed.append(b)
        added_count += 1
        print("  OK " + slug + " (" + name_zh + ") -> generated + deployed to www")

    if added_count == 0:
        print("No brands were generated this cycle")
        os.remove(LOCK_FILE)
        # Still update index.html (ensure esc() applied to all brands)
        _update_index_html()
        sys.exit(0)

    # --- STEP 5: Write to brands_index.json (ONLY for successfully deployed brands) ---
    for b in successfully_deployed:
        index.append({
            "slug": b["slug"],
            "name": b["name"],
            "name_en": b.get("name_en", b["name"]),
            "category": b.get("category", ""),
        })

    json.dump(index, open(os.path.join(BASE, "brands_index.json"), "w"), ensure_ascii=False, indent=2)

    # --- STEP 6: Add to master.csv ---
    for b in successfully_deployed:
        with open(os.path.join(BASE, "master.csv"), 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow([
                b["slug"], b["name"], b.get("name_en", b["name"]),
                b.get("category", ""), b.get("founding_location", ""),
                str(b.get("founding_year", "")), "TRUE"
            ])

    # --- STEP 7: Update index.html brandsData ---
    _update_index_html()

    # --- STEP 8: Git add, commit, push ---
    os.chdir(BASE)
    os.system("git add -A")
    names = ", ".join(b.get("name_en", b["name"]) for b in successfully_deployed)
    os.system('git commit -m "batch add ' + str(added_count) + ' brands: ' + names + '"')
    result = os.system("git push")
    if result == 0:
        print("   Git push successful")
    else:
        print("   Git push returned " + str(result))

    print("")
    print("Heartbeat complete: +" + str(added_count) + " brands deployed (total: " + str(len(index)) + ")")
    print("   Remaining in pool: " + str(len(new_remaining)))

finally:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
