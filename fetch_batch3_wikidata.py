#!/usr/bin/env python3
"""
Batch 3 Wikidata info fetcher
Completes Wikidata fields (founding_year, founder, etc.) for 17 brands
"""
import json, urllib.request, urllib.parse, time, re
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

def wikidata_query(qid):
    params = {
        'action': 'wbgetentities',
        'ids': qid,
        'props': 'labels|descriptions|claims|sitelinks',
        'languages': 'zh,en',
        'format': 'json',
        'origin': '*',
    }
    url = f'https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url, headers={'User-Agent': 'GlobalBrandIndex/1.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        entity = data.get('entities', {}).get(qid, {})
        result = {}
        
        labels = entity.get('labels', {})
        result['zh_label'] = labels.get('zh', {}).get('value', '')
        result['en_label'] = labels.get('en', {}).get('value', '')
        
        descs = entity.get('descriptions', {})
        result['zh_desc'] = descs.get('zh', {}).get('value', '')
        result['en_desc'] = descs.get('en', {}).get('value', '')
        
        claims = entity.get('claims', {})
        inception = claims.get('P571', [])
        if inception:
            result['founding_year'] = inception[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('time', '')
        
        profit = claims.get('P2139', [])
        if profit:
            result['revenue'] = profit[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('amount', '')
        
        employees = claims.get('P1128', [])
        if employees:
            result['employees'] = employees[0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
        
        website = claims.get('P856', [])
        if website:
            result['website'] = website[0].get('mainsnak', {}).get('datavalue', {}).get('value', '')
        
        sitelinks = entity.get('sitelinks', {})
        result['wiki_zh'] = sitelinks.get('zhwiki', {}).get('title', '')
        result['wiki_en'] = sitelinks.get('enwiki', {}).get('title', '')
        
        # founder
        founder = claims.get('P112', [])
        if not founder:
            founder = claims.get('P57', [])
        if founder:
            fid = founder[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')
            if fid:
                p2 = {
                    'action': 'wbgetentities',
                    'ids': fid,
                    'props': 'labels',
                    'languages': 'zh,en',
                    'format': 'json',
                    'origin': '*',
                }
                u2 = f'https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(p2)}'
                r2 = urllib.request.Request(u2, headers={'User-Agent': 'GlobalBrandIndex/1.0'})
                with urllib.request.urlopen(r2, timeout=10) as resp2:
                    d2 = json.loads(resp2.read())
                    e2 = d2.get('entities', {}).get(fid, {})
                    l2 = e2.get('labels', {})
                    result['founder'] = l2.get('zh', {}).get('value', '') or l2.get('en', {}).get('value', '')
        
        # country
        country = claims.get('P17', [])
        if country:
            cid = country[0].get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id', '')
            if cid:
                p3 = {
                    'action': 'wbgetentities',
                    'ids': cid,
                    'props': 'labels',
                    'languages': 'zh,en',
                    'format': 'json',
                    'origin': '*',
                }
                u3 = f'https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(p3)}'
                r3 = urllib.request.Request(u3, headers={'User-Agent': 'GlobalBrandIndex/1.0'})
                with urllib.request.urlopen(r3, timeout=10) as resp3:
                    d3 = json.loads(resp3.read())
                    e3 = d3.get('entities', {}).get(cid, {})
                    l3 = e3.get('labels', {})
                    result['country_zh'] = l3.get('zh', {}).get('value', '')
        
        return result

def resolve_label(qid):
    p = {
        'action': 'wbgetentities',
        'ids': qid,
        'props': 'labels',
        'languages': 'zh,en',
        'format': 'json',
        'origin': '*',
    }
    u = f'https://www.wikidata.org/w/api.php?{urllib.parse.urlencode(p)}'
    r = urllib.request.Request(u, headers={'User-Agent': 'GlobalBrandIndex/1.0'})
    with urllib.request.urlopen(r, timeout=10) as resp:
        d = json.loads(resp.read())
        e = d.get('entities', {}).get(qid, {})
        l = e.get('labels', {})
        return l.get('zh', {}).get('value', '') or l.get('en', {}).get('value', '') or qid

qids_to_query = {
    'apple': 'Q89',
    'google': 'Q95',
    'amazon': 'Q456120',
    'samsung': 'Q20716',
    'huawei': 'Q160120',
    'sony': 'Q41187',
    'nvidia': 'Q182477',
    'nike': 'Q218202',
    'adidas': 'Q3895',
    'puma': 'Q1572564',
    'coca-cola': 'Q2813',
    'mcdonald-s': 'Q38076',
    'starbucks': 'Q37158',
    'mattel': 'Q596139',
    'coach': 'Q404866',
}

for slug, qid in qids_to_query.items():
    print(f'\n=== {slug} (Q{qid}) ===')
    info = wikidata_query(qid)
    print(f'  中文名: {info.get("zh_label", "")}')
    print(f'  英文名: {info.get("en_label", "")}')
    
    # Write to brand.json
    bj = ROOT / slug / 'brand.json'
    if bj.exists():
        data = json.loads(bj.read_text(encoding='utf-8'))
        
        if info.get('zh_label'):
            data['names']['zh-CN'] = info['zh_label']
        if info.get('en_label'):
            data['names']['en'] = info['en_label']
        
        fy = info.get('founding_year', '')
        if fy:
            m = re.search(r'(\d{4})', fy)
            if m:
                data['founding_year'] = m.group(1)
                print(f'  成立年份: {m.group(1)}')
        
        if info.get('founder'):
            data['founder'] = info['founder']
            print(f'  创始人: {info["founder"]}')
        
        if info.get('website'):
            data['official_website'] = info['website']
            print(f'  官网: {info["website"]}')
        
        if info.get('country_zh'):
            data['founding_location'] = info['country_zh']
            print(f'  国家: {info["country_zh"]}')
        
        if info.get('revenue'):
            print(f'  收入: {info["revenue"]}')
        if info.get('employees'):
            print(f'  员工数: {info["employees"]}')
        if info.get('zh_desc'):
            print(f'  描述: {info["zh_desc"]}')
        if info.get('wiki_zh'):
            print(f'  维基: {info["wiki_zh"]}')
        
        bj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    time.sleep(0.5)

print('\n✅ Batch 3 Wikidata info complete')
