"""Direct patch: Replace the homepage regen code in simple_heartbeat.py"""
import re

path = "/workspace/pinpai-ai-in/simple_heartbeat.py"
with open(path) as f:
    code = f.read()

# Find the complete homepage regen section
start = code.find('log("Regenerating homepage')
if start < 0:
    print("ERROR: Cannot find regen section")
    exit(1)

# Find the end - search for the next log() call or the finally block
end = code.find('\nfinally:', start)
if end < 0:
    # Maybe it ends at '    log(' after the write
    end = code.find('    log("Complete:', start)
    if end < 0:
        end = start + 1000

print("Regen section: bytes %d to %d" % (start, end))
print("Current code:")
print(code[start:end])
print("---")

new_code = """    # SAFE homepage regeneration - preserve all JS functions
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

code = code[:start] + new_code + code[end:]
with open(path, "w") as f:
    f.write(code)

print("Patched! Verifying compile...")
import py_compile
py_compile.compile(path, doraise=True)
print("Compile OK!")
