#!/usr/bin/env python3
"""写入Sony完整的brand.json"""
import json
from pathlib import Path
ROOT = Path("/workspace/pinpai-ai-in")

data = {
    "slug": "sony",
    "names": {"zh-CN":"索尼","en":"Sony","fr":"Sony","es":"Sony","de":"Sony","ja":"ソニー","ko":"소니","pt":"Sony","ru":"Sony","ar":"سوني"},
    "category":"tech",
    "founding_year":1946,
    "founding_location":"东京",
    "founding_location_en":"Tokyo",
    "founder":"井深大、盛田昭夫",
    "official_website":"https://www.sony.com/en/",
    "main_business":["消费电子","游戏","影视娱乐","金融服务"],
    "current_slogan":"Be Moved",
    "description_zh":"索尼（Sony）是1946年在东京创立的日本跨国企业集团，由井深大和盛田昭夫共同创立。前身为东京通信工业株式会社。索尼是全球最大的消费电子与娱乐公司之一，业务涵盖电子、游戏（PlayStation）、影视（索尼影业）、音乐（索尼音乐娱乐）和金融服务。索尼以创新精神著称，曾发明了Walkman随身听、PlayStation游戏机、Bravia电视等革命性产品。",
    "languages": {}
}
(ROOT / "sony" / "brand.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ Sony template ready")
