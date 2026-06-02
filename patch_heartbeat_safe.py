"""Patch simple_heartbeat.py to safely regenerate homepage without breaking JS"""
import re

path = "/workspace/pinpai-ai-in/simple_heartbeat.py"
code = open(path).read()

# Find the homepage regeneration section and make it safe
# Current code uses regex which can corrupt the page
# Replace with safe JSON array replacement using exact string matching

old_regen = """    log("Regenerating homepage (%d brands)..." % len(index))
    hp_path = os.path.join(WWW, "index.html")
    with open(hp_path, encoding="utf-8") as f:
        homepage = f.read()
    
    new_data = json.dumps(index, ensure_ascii=False)
    homepage = re.sub(r'var brandsData = \\[.*?\\];', 'var brandsData = %s;' % new_data, homepage, count=1, flags=re.DOTALL)
    
    cards = ""
    for b in index[-20:]:
        cards += '\\n        <a class="brand-card" href="/%s/"><h2>%s</h2><div class="en">%s</div><span class="cat-tag">%s</span></a>' % (b["slug"], b["name"], b.get("name_en", b["name"]), b.get("category",""))
    
    brand_list_pattern = r'<div class="brand-grid" id="brand-list">.*?</div>'
    homepage = re.sub(brand_list_pattern, '<div class="brand-grid" id="brand-list">%s\\n    </div>' % cards, homepage, count=1, flags=re.DOTALL)
    
    homepage = re.sub(r'\\u5171 \\\\d+ \\\\u4e2a\\\\u54c1\\\\u724c', '\\u5171 %d \\u4e2a\\u54c1\\u724c' % len(index), homepage)
    
    with open(hp_path, "w", encoding="utf-8") as f:
        f.write(homepage)"""

new_regen = """    # SAFE homepage regeneration - preserve all JS functions
    log("Regenerating homepage (%d brands)..." % len(index))
    hp_path = os.path.join(WWW, "index.html")
    with open(hp_path, encoding="utf-8") as f:
        homepage = f.read()
    
    new_data = json.dumps(index, ensure_ascii=False)
    
    # Find the exact position of var brandsData and replace just the data
    start_marker = 'var brandsData = ['
    start = homepage.find(start_marker)
    if start < 0:
        log("ERROR: Cannot find brandsData in homepage! Skipping regen.")
    else:
        # Find the closing ]; by bracket matching
        depth = 0
        end = start + len(start_marker)
        while end < len(homepage):
            c = homepage[end]
            if c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end += 1  # include ]
                    break
            end += 1
        
        if homepage[end:end+1] == ';':
            end += 1  # include ;
        
        # Replace the data
        homepage = homepage[:start] + 'var brandsData = ' + new_data + ';' + homepage[end:]
        log("  brandsData replaced: %d entries" % len(index))
    
    # Update brand cards (server-side rendered)
    cards = ""
    for b in index[-20:]:
        cards += '\\n        <a class="brand-card" href="/%s/"><h2>%s</h2><div class="en">%s</div></a>' % (b["slug"], b["name"], b.get("name_en", b["name"]))
    
    brand_list_start = '<div class="brand-grid" id="brand-list">'
    bls = homepage.find(brand_list_start)
    ble = homepage.find('</div>', bls + len(brand_list_start))
    if bls >= 0 and ble >= 0:
        before = homepage[:bls + len(brand_list_start)]
        after = homepage[ble:]
        homepage = before + cards + '\\n    ' + after
    
    # Update count
    count_marker = '\\u5171 \\u4e2a\\u54c1\\u724c'
    if '\\u5171' in homepage:
        homepage = re.sub(r'\\u5171 \\d+ \\u4e2a\\u54c1\\u724c', '\\u5171 %d \\u4e2a\\u54c1\\u724c' % len(index), homepage)
    
    # Verify JS integrity before saving
    if 'function renderBrands' not in homepage or 'function buildShuffledList' not in homepage:
        log("ERROR: Homepage JS functions missing! Will NOT save broken homepage.")
        log("  renderBrands: %s" % ('function renderBrands' in homepage))
        log("  buildShuffledList: %s" % ('function buildShuffledList' in homepage))
    else:
        with open(hp_path, "w", encoding="utf-8") as f:
            f.write(homepage)
        log("  Homepage saved OK")"""

if old_regen in code:
    code = code.replace(old_regen, new_regen)
    with open(path, "w") as f:
        f.write(code)
    print("Patched heartbeat with SAFE homepage regeneration!")
else:
    print("Old pattern not found - checking code...")
    # Try to find the actual code
    if "Regenerating homepage" in code:
        print("Found 'Regenerating homepage' but pattern differs")
        # Show the actual code around it
        idx = code.find("Regenerating homepage")
        print(code[idx:idx+500])
    else:
        print("No homepage regeneration found in heartbeat!")
