#!/usr/bin/env python3
"""
Regenerate ALL brand pages with proper multi-language structure.
For each brand:
1. Get English Wikipedia content (already have from heartbeat)
2. Get Wikipedia langlinks
3. Fetch real translations for available languages
4. Generate page with language switcher
Process in batches to avoid rate limiting.
"""
import json, os, re, time, urllib.request, urllib.parse, sys

WWW = "/var/www/pinpai"

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
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg))

def get_langlinks(title):
    url = ("https://en.wikipedia.org/w/api.php"
           "?action=query&prop=langlinks&titles=%s"
           "&lllimit=500&format=json") % urllib.parse.quote(title)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PinpaiRegen/1.0"})
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
        req = urllib.request.Request(url, headers={"User-Agent": "PinpaiRegen/1.0"})
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

def make_page(name_en, cat, en_ext, lang_cont):
    safe_name = name_en.replace("&","&amp;").replace("<","&lt;").replace("\"","&quot;")
    first_s = en_ext.split(".")[0].replace("\"","'").replace("\n"," ")[:200]
    
    html = "<!DOCTYPE html>\n<html lang=\"en\" data-lang=\"en\">\n<head>\n"
    html += "<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
    html += "<title>%s | Global Brand Index</title>\n" % safe_name
    html += "<meta name=\"description\" content=\"%s\">\n" % first_s
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
             ".brand-content{background:#fff;border:1px solid #eee;border-radius:8px;padding:24px;margin-bottom:30px;font-size:15px;line-height:1.8}"
             ".brand-content p{margin-bottom:12px}"
             ".similar-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin-bottom:30px}"
             ".similar-card{display:block;background:#fff;border:1px solid #eee;border-radius:6px;padding:10px 14px;text-decoration:none;font-size:13px}"
             ".similar-card.premium{background:#222;color:#fff}"
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
    html += "<script>"
    html += "document.querySelectorAll('.lang-nav .lang-tab').forEach(function(l){l.addEventListener('click',function(e){e.preventDefault();var lang=this.getAttribute('lang');document.querySelectorAll('.lang-nav .lang-tab').forEach(function(x){x.classList.remove('active')});this.classList.add('active');document.querySelectorAll('[id^=\"content-\"]').forEach(function(d){d.style.display='none'});var el=document.getElementById('content-'+lang);if(el)el.style.display='block'})})"
    html += "</script>\n</body>\n</html>"
    return html

# Load index
with open(os.path.join(WWW, "brands_index.json")) as f:
    idx = json.load(f)

# Find brands that DON'T have multi-lang structure yet
BATCH = int(sys.argv[1]) if len(sys.argv) > 1 else 50
log("Scanning %d brands, processing %d..." % (len(idx), BATCH))

processed = 0
start = time.time()
for i, b in enumerate(idx):
    if processed >= BATCH:
        break
    if time.time() - start > 240:  # 4 min max
        log("Time limit reached")
        break
    
    slug = b["slug"]
    name_en = b.get("name_en", b.get("name", slug))
    cat = b.get("category", "general")
    path = os.path.join(WWW, slug, "index.html")
    
    if not os.path.exists(path):
        continue
    
    html = open(path, encoding="utf-8", errors="replace").read()
    
    # Check if already has multi-lang structure with lang attributes
    if 'id="content-ja"' in html and 'id="content-ko"' in html:
        continue  # Already multi-lang
    
    # Extract English content
    en_m = re.search(r'id="content-en"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not en_m:
        en_m = re.search(r'id="brand-content"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not en_m:
        continue
    
    en_ext = re.sub(r'<[^>]+>', '', en_m.group(1)).strip()
    if len(en_ext) < 200:
        continue
    
    # Get Wikipedia translations (only for major brands - skip if langlinks API fails)
    langlinks = get_langlinks(name_en)
    time.sleep(0.3)
    
    lang_cont = {"en": en_ext}
    for lc, wc in LANG_MAP.items():
        if lc == "en":
            continue
        if wc in langlinks:
            ext = get_local_extract(wc, langlinks[wc])
            lang_cont[lc] = ext if ext and len(ext) > 50 else en_ext
            time.sleep(0.2)
        else:
            lang_cont[lc] = en_ext
    
    real_tr = [lc for lc in lang_cont if lc not in ("en") and lang_cont[lc] != en_ext]
    
    new_html = make_page(name_en, cat, en_ext, lang_cont)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    
    processed += 1
    if real_tr:
        log("  [%d/%d] %s: +%d langs" % (processed, BATCH, slug, len(real_tr)))
    else:
        log("  [%d/%d] %s: en only" % (processed, BATCH, slug))

log("Done: %d pages regenerated" % processed)

# Quick verification: check Yahoo
log("\n=== VERIFY ===")
for check in ["yahoo", "walmart", "visa-inc", "xerox", "caproni"]:
    p = os.path.join(WWW, check, "index.html")
    if os.path.exists(p):
        h = open(p).read()
        langs = re.findall(r'id="content-([^"]+)"', h)
        has_real = sum(1 for l in langs if l not in ["en"])
        log("  %s: %d languages" % (check, len(langs)))
