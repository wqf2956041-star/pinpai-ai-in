#!/usr/bin/env python3
"""
simple_heartbeat.py -- Clean brand pipeline for pinpai.cc.cd
Runs every 15 min, processes 5 brands per cycle.
Flow: brand -> Wikipedia(500+ chars) -> multilingual page -> index -> homepage
"""
import json, os, sys, re, time, urllib.request, urllib.parse

BASE = "/workspace/pinpai-ai-in"
WWW = "/var/www/pinpai"
POOL_FILE = os.path.join(BASE, ".next_batch.json")
LOCK_FILE = os.path.join(BASE, ".heartbeat.lock")
LOG_FILE = os.path.join(BASE, "heartbeat.log")

LANG_MAP = {
    "zh-CN": "zh", "en": "en", "fr": "fr", "es": "es", "de": "de",
    "ja": "ja", "ko": "ko", "pt": "pt", "ru": "ru", "ar": "ar"
}
LANG_NAMES = {
    "zh-CN": "Chinese", "en": "English", "fr": "Francais",
    "es": "Espanol", "de": "Deutsch", "ja": "Japanese",
    "ko": "Korean", "pt": "Portugues", "ru": "Russian", "ar": "Arabic"
}

def log(msg):
    t = time.strftime("%H:%M:%S")
    line = "[%s] %s" % (t, msg)
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write("[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), msg))

def get_langlinks(title):
    url = ("https://en.wikipedia.org/w/api.php"
           "?action=query&prop=langlinks&titles=%s"
           "&lllimit=500&format=json") % urllib.parse.quote(title)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PinpaiBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        for pid, pdata in data.get("query",{}).get("pages",{}).items():
            if pid == "-1":
                return {}
            return {l["lang"]: l["*"] for l in pdata.get("langlinks", [])}
    except:
        return {}

def get_local_extract(lang_code, title):
    url = ("https://%s.wikipedia.org/w/api.php"
           "?action=query&prop=extracts&exintro&explaintext&exchars=500"
           "&titles=%s&format=json&redirects=1") % (lang_code, urllib.parse.quote(title))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PinpaiBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        for pid, pdata in data.get("query",{}).get("pages",{}).items():
            if pid == "-1":
                continue
            ext = pdata.get("extract", "")
            if ext and len(ext) > 50:
                return ext
    except:
        pass
    return ""

if os.path.exists(LOCK_FILE):
    mtime = os.path.getmtime(LOCK_FILE)
    if time.time() - mtime < 1800:
        log("LOCKED")
        sys.exit(0)
    os.remove(LOCK_FILE)
open(LOCK_FILE, "w").close()

try:
    with open(os.path.join(WWW, "brands_index.json")) as f:
        index = json.load(f)
    existing = set(b["slug"] for b in index)
    log("Current: %d brands" % len(index))

    if not os.path.exists(POOL_FILE):
        log("Pool empty, sourcing...")
        os.system("cd %s && python3 auto_source_brands.py 2>&1" % BASE)
        if not os.path.exists(POOL_FILE):
            log("No pool after sourcing")
            sys.exit(0)

    with open(POOL_FILE) as f:
        pool = json.load(f)
    log("Pool: %d brands" % len(pool))

    todo = [b for b in pool if b["slug"] not in existing]
    if not todo:
        log("All done, clearing pool")
        os.remove(POOL_FILE)
        sys.exit(0)

    BATCH = 5
    batch = todo[:BATCH]
    rem = todo[BATCH:]
    kept = [b for b in pool if b["slug"] in existing] if len(pool) > len(todo) else []
    json.dump(rem + kept, open(POOL_FILE, "w"), ensure_ascii=False, indent=2)

    added = 0
    for b in batch:
        slug = b["slug"]
        name = b["name"]
        name_en = b.get("name_en", name)
        cat = b.get("category", "general")

        url = ("https://en.wikipedia.org/w/api.php"
               "?action=query&prop=extracts&exintro&explaintext&exchars=500"
               "&titles=%s&format=json&redirects=1") % urllib.parse.quote(name)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PinpaiBot/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            log("  SKIP %s: %s" % (slug, str(e)))
            time.sleep(1)
            continue

        en_ext = ""
        for pid, pdata in data.get("query",{}).get("pages",{}).items():
            if pid == "-1":
                continue
            ext = pdata.get("extract", "")
            if ext and len(ext) >= 500:
                en_ext = ext
                break

        if not en_ext:
            log("  SKIP %s: content too short" % slug)
            time.sleep(0.5)
            continue

        langlinks = get_langlinks(name_en)
        lang_cont = {"en": en_ext}
        for lc, wc in LANG_MAP.items():
            if lc == "en":
                continue
            if wc in langlinks:
                ext = get_local_extract(wc, langlinks[wc])
                lang_cont[lc] = ext if ext and len(ext) > 50 else en_ext
            else:
                lang_cont[lc] = en_ext

        real_tr = sum(1 for lc in lang_cont if lc not in ("en") and lang_cont[lc] != en_ext)

        # Build HTML with string concat (no f-strings, em-dashes, or special unicode)
        html = "<!DOCTYPE html>\n<html lang=\"en\" data-lang=\"en\">\n<head>\n"
        html += "<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        safe_name = name_en.replace("&","&amp;").replace("<","&lt;").replace("\"","&quot;")
        html += "<title>%s | Global Brand Index</title>\n" % safe_name
        first_s = en_ext.split(".")[0].replace("\"","'").replace("\n"," ")
        html += "<meta name=\"description\" content=\"%s\">\n" % first_s[:200]
        html += ("<style>*{margin:0;padding:0;box-sizing:border-box}"
                 "body{font-family:sans-serif;background:#f8f9fa;color:#222;line-height:1.7}"
                 ".container{max-width:960px;margin:0 auto;padding:20px}"
                 ".lang-nav{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:20px}"
                 ".lang-nav .lang-tab{display:inline-block;padding:4px 10px;border-radius:4px;font-size:12px;text-decoration:none;color:#555;border:1px solid #ddd;cursor:pointer}"
                 ".lang-nav .lang-tab:hover{background:#eee}"
                 ".lang-nav .lang-tab.active{background:#222;color:#fff;border-color:#222}"
                 ".brand-header{margin-bottom:20px;padding-bottom:15px;border-bottom:2px solid #222}"
                 ".brand-header h1{font-size:26px;margin-bottom:2px}"
                 ".brand-header .brand-sub{font-size:13px;color:#777}"
                 ".brand-content{background:#fff;border:1px solid #eee;border-radius:8px;padding:24px;margin-bottom:30px;font-size:15px;line-height:1.8;overflow:auto}"
                 ".brand-content p{margin-bottom:12px}"
                 ".similar-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin-bottom:30px}"
                 ".similar-card{display:block;background:#fff;border:1px solid #eee;border-radius:6px;padding:10px 14px;text-decoration:none;font-size:13px}"
                 ".similar-card.premium{background:#222;color:#fff}"
                 ".badge-premium{background:#e53935;color:#fff;font-size:10px;padding:1px 5px;border-radius:3px}"
                 ".footer{margin-top:40px;padding-top:15px;border-top:1px solid #eee;font-size:12px;color:#999;text-align:center}"
                 ".footer a{color:#666}</style>\n</head>\n<body>\n<div class=\"container\">\n")

        html += "<div class=\"lang-nav\">\n"
        for lc in LANG_MAP:
            act = " active" if lc == "en" else ""
            html += "    <a href=\"#\" lang=\"%s\" class=\"lang-tab%s\">%s</a>\n" % (lc, act, LANG_NAMES[lc])
        html += "</div>\n"

        html += "<div class=\"brand-header\">\n<h1>%s</h1>\n<div class=\"brand-sub\">%s</div>\n</div>\n" % (safe_name, cat)

        for lc in LANG_MAP:
            cont = lang_cont.get(lc, en_ext)
            pars = "".join("<p>%s</p>\n" % p.strip() for p in cont.strip().split("\n") if p.strip())
            disp = "block" if lc == "en" else "none"
            html += "<div class=\"brand-content\" lang=\"%s\" id=\"content-%s\" style=\"display:%s\">\n%s</div>\n" % (lc, lc, disp, pars)

        html += "<div class=\"similar-grid\">\n<a href=\"/escher/\" class=\"similar-card premium\">* Escher <span class=\"badge-premium\">推广</span></a>\n</div>\n"
        html += "<div class=\"footer\">\n<p><a href=\"https://pinpai.cc.cd\">Global Brand Index</a> | <a href=\"/\">Home</a></p>\n</div>\n</div>\n"
        html += "<script>\n"
        html += "document.querySelectorAll('.lang-nav .lang-tab').forEach(function(l){l.addEventListener('click',function(e){e.preventDefault();var lang=this.getAttribute('lang');document.querySelectorAll('.lang-nav .lang-tab').forEach(function(x){x.classList.remove('active')});this.classList.add('active');document.querySelectorAll('[id^=\"content-\"]').forEach(function(d){d.style.display='none'});var el=document.getElementById('content-'+lang);if(el)el.style.display='block'})});\n"
        html += "</script>\n</body>\n</html>"

        www_dir = os.path.join(WWW, slug)
        os.makedirs(www_dir, exist_ok=True)
        with open(os.path.join(www_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)

        index.append({"slug": slug, "name": name, "name_en": name_en, "category": cat, "updated_at": int(time.time())})
        added += 1
        if real_tr > 0:
            log("  ADDED %s: %s (+%d langs)" % (slug, name_en, real_tr))
        else:
            log("  ADDED %s: %s (en only)" % (slug, name_en))
        time.sleep(1)

    json.dump(index, open(os.path.join(WWW, "brands_index.json"), "w"), ensure_ascii=False, indent=2)

        # SAFE homepage regeneration - preserve all JS functions
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
        cards += '\n        <a class="brand-card" href="/%s/"><h2>%s</h2><div class="en">%s</div></a>' % (b["slug"], b["name"], b.get("name_en", ""))
    
    bl_marker = '<div class="brand-grid" id="brand-list">'
    bls = homepage.find(bl_marker)
    if bls >= 0:
        ble = homepage.find('</div>', bls + len(bl_marker))
        if ble >= 0:
            homepage = homepage[:bls + len(bl_marker)] + cards + '\n    ' + homepage[ble:]
    
    # Update count
    import re as re2
    count_pattern = r'共 \d+ 个品牌'
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
        log("  Homepage saved OK (verified all JS functions intact)")
finally:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
