"""Patch heartbeat: NEVER touch homepage HTML. Only update brands_index.json."""
code = open("/workspace/pinpai-ai-in/simple_heartbeat.py").read()

# Find and remove the homepage regeneration section entirely
old = """    # SAFE homepage regeneration - preserve all JS functions
    log("Regenerating homepage (%d brands)..." % len(index))
    hp_path = os.path.join(WWW, "index.html")
    with open(hp_path, encoding="utf-8") as f:
        homepage = f.read()
    
    new_data = json.dumps(index, ensure_ascii=False)
    
    # Find the exact position of var brandsData and replace just the data
    start_marker = 'var brandsData = ['
    start_idx = homepage.find(start_marker)
    if start_idx < 0:
        log("ERROR: Cannot find brandsData in homepage! Skipping regen.")
    else:
        # Find the closing ]; by bracket matching
        depth = 0
        end_idx = start_idx + len(start_marker)
        while end_idx < len(homepage):
            c = homepage[end_idx]
            if c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end_idx += 1  # include ]
                    break
            end_idx += 1
        
        if end_idx < len(homepage) and homepage[end_idx:end_idx+1] == ';':
            end_idx += 1  # include ;
        
        homepage = homepage[:start_idx] + 'var brandsData = ' + new_data + ';' + homepage[end_idx:]
        log("  brandsData replaced: %d entries" % len(index))
    
    # Update server-side brand cards
    cards = ""
    for b in index[-20:]:
        cards += '\\n        <a class="brand-card" href="/%s/"><h2>%s</h2><div class="en">%s</div></a>' % (b["slug"], b["name"], b.get("name_en", ""))
    
    bl_marker = '<div class="brand-grid" id="brand-list">'
    bls = homepage.find(bl_marker)
    if bls >= 0:
        ble = homepage.find('</div>', bls + len(bl_marker))
        if ble >= 0:
            homepage = homepage[:bls + len(bl_marker)] + cards + '\\n    ' + homepage[ble:]
    
    # Update count
    import re as re2
    count_pattern = r'共 \\d+ 个品牌'
    if re2.search(count_pattern, homepage):
        homepage = re2.sub(count_pattern, '共 %d 个品牌' % len(index), homepage)
    
    # CRITICAL: Verify JS integrity before saving
    if 'function renderBrands' not in homepage:
        log("ERROR: Homepage JS missing renderBrands! NOT saving broken page.")
    elif 'function buildShuffledList' not in homepage:
        log("ERROR: Homepage JS missing buildShuffledList! NOT saving broken page.")
    elif 'function fetchBrands' not in homepage:
        log("ERROR: Homepage JS missing fetchBrands! NOT saving broken page.")
    elif 'DOMContentLoaded' not in homepage:
        log("ERROR: Homepage JS missing DOMContentLoaded! NOT saving broken page.")
    else:
        with open(hp_path, "w", encoding="utf-8") as f:
            f.write(homepage)
        log("  Homepage saved OK (verified all JS functions intact)")"""

new = """    # Homepage is NEVER modified by heartbeat.
    # JS loads brands dynamically from brands_index.json via fetchBrands()
    log("Homepage not modified (JS renders dynamically from JSON)")"""

if old in code:
    code = code.replace(old, new)
    with open("/workspace/pinpai-ai-in/simple_heartbeat.py", "w") as f:
        f.write(code)
    print("Patched: heartbeat no longer touches homepage")
else:
    print("Old pattern not found - checking what's there...")
    idx = code.find("SAFE homepage regeneration")
    if idx >= 0:
        print("Found 'SAFE homepage regeneration' at %d" % idx)
        # Find the end - look for "Complete:" or "finally:"
        end_idx = code.find('log("Complete:', idx)
        if end_idx < 0:
            end_idx = code.find('finally:', idx)
        if end_idx < 0:
            end_idx = idx + 3000
        print("Replacing from %d to %d" % (idx, end_idx))
        new_section = '    log("Homepage not modified (JS renders from JSON)")'
        code = code[:idx] + new_section + code[end_idx:]
        with open("/workspace/pinpai-ai-in/simple_heartbeat.py", "w") as f:
            f.write(code)
        print("Patched!")
    else:
        print("Cannot find the section. Current code around 'Regenerating homepage':")
        ridx = code.find("Regenerating homepage")
        if ridx >= 0:
            print(code[ridx:ridx+500])

# Verify compile
import py_compile
py_compile.compile("/workspace/pinpai-ai-in/simple_heartbeat.py", doraise=True)
print("Compile OK!")
