#!/usr/bin/env python3
"""Translate all 5 brands' Chinese desc into 9 languages and update JSON."""
import json
import time
from deep_translator import GoogleTranslator

LANGUAGES = ['en', 'fr', 'de', 'es', 'ja', 'ko', 'ru', 'pt', 'ar']

with open('brands_today.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

brands = data['brands']

for idx, brand in enumerate(brands):
    # Skip if translations already exist
    if 'translations' in brand and brand['translations']:
        print(f"[SKIP] Brand {idx}: {brand['name_en']} already has {len(brand['translations'])} translations")
        continue

    chinese_desc = brand['desc']
    translations = {}

    for lang in LANGUAGES:
        try:
            result = GoogleTranslator(source='zh-CN', target=lang).translate(chinese_desc)
            translations[lang] = result
            print(f"[OK] {brand['name_en']} -> {lang}: {result[:60]}...")
        except Exception as e:
            print(f"[ERROR] {brand['name_en']} -> {lang}: {e}")
            translations[lang] = f"[Translation error: {e}]"
        time.sleep(0.3)  # Rate limiting

    brand['translations'] = translations
    print(f"[DONE] Brand {idx}: {brand['name_en']} - translated into {len(translations)} languages")

# Save updated JSON
with open('brands_today.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nAll done! Saved to brands_today.json")
