#!/usr/bin/env python3
"""
pinpai_enricher.py — 品牌百科内容填充器
从 Wikipedia API 拉取品牌描述，填充到空品牌页面中
每次运行处理 50 个品牌（Wikipedia API 支持批量查询）
"""
import json, os, urllib.request, urllib.parse, urllib.error, time, re
from datetime import datetime

BASE = "/workspace/pinpai-ai-in"
WWW = "/var/www/pinpai"
STATE_FILE = os.path.join(BASE, ".enricher_state.json")
LOG = "/var/log/pinpai_enricher.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def wikipedia_query(titles_batch):
    """Query Wikipedia API for page extracts"""
    titles = "|".join(titles_batch)
    url = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&exchars=1000&titles=" + urllib.parse.quote(titles) + "&format=json&redirects=1"
    
    req = urllib.request.Request(url, headers={"User-Agent": "PinpaiEnricher/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            pages = data.get("query", {}).get("pages", {})
            results = {}
            for page_id, page_data in pages.items():
                if page_id == "-1":
                    continue
                title = page_data.get("title", "")
                extract = page_data.get("extract", "")
                if extract and len(extract) > 100:
                    results[title] = extract
            return results
    except Exception as e:
        log(f"  API error: {e}")
        return {}

def name_to_wikipedia_title(slug, name_en):
    """Convert brand info to Wikipedia page title"""
    # Try the slug first (it often matches Wikipedia URL format)
    title = slug.replace("-", " ")
    # Capitalize properly
    title = " ".join(w.capitalize() if w.islower() else w for w in title.split())
    # Try the English name
    if name_en and name_en != slug:
        return name_en
    return slug

def update_brand_page(slug, extract):
    """Update the brand HTML page with Wikipedia content"""
    path = os.path.join(WWW, slug, "index.html")
    if not os.path.exists(path):
        return False
    
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        html = f.read()
    
    # Find the content div
    start_tag = 'id="brand-content">'
    start = html.find(start_tag)
    if start < 0:
        return False
    
    start += len(start_tag)
    end = html.find("</div>", start)
    if end < 0:
        return False
    
    # Format the extract as paragraph
    paragraphs = extract.strip().split("\n")
    content_html = ""
    for p in paragraphs:
        p = p.strip()
        if p:
            content_html += f"<p>{p}</p>\n"
    
    # Update the content
    new_html = html[:start] + "\n" + content_html + "\n" + html[end:]
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    
    return True

def main():
    # Load current state or start fresh
    processed = set()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        processed = set(state.get("processed", []))
    
    # Load brand index
    with open(os.path.join(WWW, "brands_index.json"), "r") as f:
        index = json.load(f)
    
    # Find brands that need content (content div is empty)
    to_process = []
    checked = 0
    for b in index:
        slug = b["slug"]
        path = os.path.join(WWW, slug, "index.html")
        if not os.path.exists(path):
            continue
        if slug in processed:
            continue
        
        # Check if content is empty
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        
        start_tag = 'id="brand-content">'
        start = html.find(start_tag)
        if start < 0:
            processed.add(slug)
            continue
        
        start += len(start_tag)
        end = html.find("</div>", start)
        if end < 0:
            processed.add(slug)
            continue
        
        content = html[start:end].replace("\n", "").replace(" ", "").replace("<p>", "").replace("</p>", "")
        if len(content) < 50:
            name_en = b.get("name_en", b.get("name", slug))
            to_process.append((slug, name_en))
            checked += 1
            if len(to_process) >= 50:
                break
    
    if not to_process:
        log(f"All brands have content! Total checked: {len(processed)}")
        return
    
    log(f"Found {len(to_process)} brands to enrich (total checked: {checked})")
    
    # Batch query Wikipedia
    titles = [t[1] for t in to_process]
    log(f"Querying Wikipedia for {len(titles)} titles...")
    results = wikipedia_query(titles)
    log(f"Got {len(results)} results from Wikipedia")
    
    # Update pages
    enriched = 0
    for slug, name_en in to_process:
        # Try exact title match first, then partial
        matched_title = None
        for wiki_title in results:
            if wiki_title.lower() == name_en.lower():
                matched_title = wiki_title
                break
        if not matched_title:
            for wiki_title in results:
                if wiki_title.lower() in name_en.lower() or name_en.lower() in wiki_title.lower():
                    matched_title = wiki_title
                    break
        
        if matched_title:
            extract = results[matched_title]
            if update_brand_page(slug, extract):
                log(f"  OK {slug}: +{len(extract)} chars")
                enriched += 1
            else:
                log(f"  FAIL {slug}: could not update page")
        else:
            log(f"  SKIP {slug}: no Wikipedia match")
        
        processed.add(slug)
    
    # Save state
    with open(STATE_FILE, "w") as f:
        json.dump({"processed": list(processed), "last_run": datetime.now().isoformat()}, f)
    
    log(f"Done: {enriched} brands enriched this cycle")

if __name__ == "__main__":
    main()
