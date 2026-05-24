#!/usr/bin/env python3
"""
Translate Chinese 'desc' fields in brands_today.json for brands lacking translations.
Translates into 9 languages: en, fr, de, es, ja, ko, ru, pt, ar.
"""
import json
import sys
from deep_translator import GoogleTranslator

FILE = "/workspace/pinpai-ai-in/brands_today.json"

# Target languages (excluding zh-CN which is the source)
LANGUAGES = {
    "en": "english",
    "fr": "french",
    "de": "german",
    "es": "spanish",
    "ja": "japanese",
    "ko": "korean",
    "ru": "russian",
    "pt": "portuguese",
    "ar": "arabic",
}

def detect_lang(text):
    """Detect if text is mostly Chinese characters"""
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return chinese_chars > len(text) * 0.3

def translate_text(text, target_lang, source_lang="auto"):
    """Translate text using Google Translate via deep-translator"""
    try:
        result = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return result
    except Exception as e:
        print(f"    ❌ Translation to {target_lang} failed: {e}")
        return None

def main():
    with open(FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    brands = data.get("brands", [])
    print(f"📋 Loaded {len(brands)} brands from brands_today.json")
    
    translated_count = 0
    skip_count = 0
    
    for i, brand in enumerate(brands):
        name = brand.get("name", "?")
        name_en = brand.get("name_en", "")
        
        # Check if translations already exist
        if "translations" in brand and brand["translations"]:
            print(f"⏭️  [{i+1}/{len(brands)}] {name} ({name_en}) — already has translations, skipping")
            skip_count += 1
            continue
        
        desc = brand.get("desc", "")
        if not desc:
            print(f"⚠️  [{i+1}/{len(brands)}] {name} — empty desc, skipping")
            skip_count += 1
            continue
        
        # Detect source language
        is_chinese = detect_lang(desc)
        source_lang = "zh-CN" if is_chinese else "en"
        source_label = "Chinese" if is_chinese else "English"
        
        print(f"🌐 [{i+1}/{len(brands)}] {name} ({name_en}) — translating from {source_label}...")
        print(f"   Source text ({len(desc)} chars): {desc[:80]}...")
        
        translations = {}
        lang_list = list(LANGUAGES.items())
        
        for idx, (code, lang_name) in enumerate(lang_list):
            # For English source, skip english target (use original)
            if source_lang == "en" and code == "en":
                translations["en"] = desc
                print(f"   ✅ [{idx+1}/{len(lang_list)}] en — using original (already English)")
                continue
            
            result = translate_text(desc, code, source_lang)
            if result:
                translations[code] = result
                preview = result[:60].replace('\n', ' ')
                print(f"   ✅ [{idx+1}/{len(lang_list)}] {code} ({lang_name}): {preview}...")
            else:
                print(f"   ⚠️  [{idx+1}/{len(lang_list)}] {code} — failed, keeping placeholder")
                translations[code] = f"[{lang_name} translation pending]"
        
        brand["translations"] = translations
        translated_count += 1
        print(f"   ✅ {name}: {len(translations)} translations added\n")
    
    # Save updated JSON
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"📊 Summary: {translated_count} brands translated, {skip_count} skipped")
    print(f"💾 Saved to {FILE}")
    
    return translated_count

if __name__ == "__main__":
    main()
