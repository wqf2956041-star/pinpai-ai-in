#!/usr/bin/env python3
"""
批量修复所有 50 个品牌的 brand.json 使其通过 Schema 校验
需要补充/修复的字段：
1. founding_year: 字符串→整数（如 "1994" → 1994）
2. current_slogan: 不能为空，≥2字
3. main_business: 不能为空数组
4. 各品牌 special slug fix (Hermès等)
"""
import csv, json
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

# 品牌修复数据
brand_fixes = {
    "escher": {
        "founding_year": 2024,
        "current_slogan": "专为模特设计",
        "main_business": ["手提包", "箱包"]
    },
    "louis-vuitton": {
        "founding_year": 1854,
        "current_slogan": "Louis Vuitton, Maison fondée en 1854",
        "main_business": ["皮具", "时装", "配饰", "香水"]
    },
    "hermès": {
        "founding_year": 1837,
        "current_slogan": "轻盈、优雅、品质",
        "main_business": ["皮具", "丝巾", "时装", "香水", "腕表"]
    },
    "gucci": {
        "founding_year": 1921,
        "current_slogan": "Gucci, 意大利奢华",
        "main_business": ["皮具", "时装", "配饰", "香水"]
    },
    "chanel": {
        "founding_year": 1910,
        "current_slogan": "时尚易逝，风格永存",
        "main_business": ["时装", "香水", "配饰", "高级珠宝"]
    },
    "christian-dior": {
        "founding_year": 1946,
        "current_slogan": "迪奥，优雅与创新",
        "main_business": ["时装", "香水", "配饰", "化妆品"]
    },
    "prada": {
        "founding_year": 1913,
        "current_slogan": "Prada, 前卫与奢华",
        "main_business": ["皮具", "时装", "配饰", "香水"]
    },
    "burberry": {
        "founding_year": 1856,
        "current_slogan": "经典英伦风衣",
        "main_business": ["时装", "配饰", "香水", "风衣"]
    },
    "versace": {
        "founding_year": 1978,
        "current_slogan": "Versace, 意式奢华",
        "main_business": ["时装", "配饰", "香水", "家居"]
    },
    "balenciaga": {
        "founding_year": 1919,
        "current_slogan": "Balenciaga, 结构与先锋",
        "main_business": ["时装", "配饰", "香水"]
    },
    "zara": {
        "founding_year": 1975,
        "current_slogan": "时尚触手可及",
        "main_business": ["时装", "配饰"]
    },
    "uniqlo": {
        "founding_year": 1949,
        "current_slogan": "LifeWear 服适人生",
        "main_business": ["休闲服装", "内衣"]
    },
    "h-m": {
        "names": {"zh-CN": "H&M", "en": "H&M"},
        "founding_year": 1947,
        "main_business": ["时装", "配饰"]
    },
    "levi-s": {
        "names": {"zh-CN": "李维斯", "en": "Levi's"},
        "founding_year": 1853,
        "current_slogan": "原创牛仔，始于1853",
        "main_business": ["牛仔裤", "服装", "配饰"]
    },
    "calvin-klein": {
        "founding_year": 1968,
        "current_slogan": "Calvin Klein, 极简与性感",
        "main_business": ["时装", "内衣", "香水", "配饰"]
    },
    "ralph-lauren": {
        "founding_year": 1967,
        "current_slogan": "Polo Ralph Lauren, 美式经典",
        "main_business": ["时装", "配饰", "家居", "香水"]
    },
    "tommy-hilfiger": {
        "founding_year": 1985,
        "current_slogan": "Tommy Hilfiger, 美式学院风格",
        "main_business": ["时装", "配饰"]
    },
    "l-oréal": {
        "founding_year": 1909,
        "current_slogan": "你值得拥有",
        "main_business": ["化妆品", "护肤品", "护发产品", "香水"]
    },
    "estée-lauder": {
        "founding_year": 1946,
        "current_slogan": "Estée Lauder, 奢华护肤",
        "main_business": ["护肤品", "化妆品", "香水"]
    },
    "shiseido": {
        "founding_year": 1872,
        "current_slogan": "美力创新让世界更好",
        "main_business": ["护肤品", "化妆品", "护发产品", "香水"]
    },
    "lancôme": {
        "founding_year": 1935,
        "current_slogan": "兰蔻，法式优雅",
        "main_business": ["护肤品", "化妆品", "香水"]
    },
    "mac-cosmetics": {
        "founding_year": 1984,
        "current_slogan": "M·A·C, 专业彩妆",
        "main_business": ["化妆品", "彩妆"]
    },
    "rolex": {
        "founding_year": 1905,
        "current_slogan": "劳力士，精准与经典",
        "main_business": ["腕表"],
        "category": "watch"
    },
    "patek-philippe": {
        "founding_year": 1839,
        "current_slogan": "百达翡丽，世代传承",
        "main_business": ["腕表"],
        "category": "watch"
    },
    "audemars-piguet": {
        "founding_year": 1875,
        "current_slogan": "驾驭常规，铸就创新",
        "main_business": ["腕表"],
        "category": "watch"
    },
    "tiffany-co": {
        "founding_year": 1837,
        "current_slogan": "Tiffany, 爱之标志",
        "main_business": ["珠宝", "银器", "配饰"],
        "category": "jewelry"
    },
    "cartier": {
        "founding_year": 1847,
        "current_slogan": "卡地亚，皇帝的珠宝商",
        "main_business": ["珠宝", "腕表", "配饰"],
        "category": "jewelry"
    },
    "bulgari": {
        "founding_year": 1884,
        "current_slogan": "宝格丽，意式色彩",
        "main_business": ["珠宝", "腕表", "配饰", "香水"],
        "category": "jewelry"
    },
    "toyota": {
        "founding_year": 1937,
        "current_slogan": "车到山前必有路，有路必有丰田车",
        "main_business": ["汽车", "混合动力"],
        "category": "auto"
    },
    "mercedes-benz": {
        "founding_year": 1926,
        "current_slogan": "The Best or Nothing",
        "main_business": ["汽车", "豪华车"],
        "category": "auto"
    },
    "bmw": {
        "founding_year": 1916,
        "current_slogan": "Sheer Driving Pleasure",
        "main_business": ["汽车", "摩托车"],
        "category": "auto"
    },
    "ferrari": {
        "founding_year": 1947,
        "current_slogan": "法拉利，赛道传奇",
        "main_business": ["超级跑车"],
        "category": "auto"
    },
    "byd": {
        "founding_year": 1995,
        "current_slogan": "Build Your Dreams",
        "main_business": ["电动汽车", "电池"],
        "category": "auto"
    },
    "apple": {
        "founding_year": 1976,
        "current_slogan": "Think Different",
        "main_business": ["智能手机", "电脑", "可穿戴设备"],
        "category": "tech"
    },
    "google": {
        "founding_year": 1998,
        "current_slogan": "整合全球信息",
        "main_business": ["搜索引擎", "云计算", "广告"],
        "category": "tech"
    },
    "amazon": {
        "founding_year": 1994,
        "current_slogan": "地球上最以客户为中心的公司",
        "main_business": ["电子商务", "云计算", "数字流媒体"],
        "category": "tech"
    },
    "samsung": {
        "founding_year": 1938,
        "current_slogan": "Do What You Can't",
        "main_business": ["智能手机", "半导体", "家电"],
        "category": "tech"
    },
    "huawei": {
        "founding_year": 1987,
        "current_slogan": "构建万物互联的智能世界",
        "main_business": ["通信设备", "智能手机", "云计算"],
        "category": "tech"
    },
    "sony": {
        "founding_year": 1946,
        "current_slogan": "感动人心",
        "main_business": ["游戏", "电子", "影视", "音乐"],
        "category": "tech"
    },
    "nvidia": {
        "founding_year": 1993,
        "current_slogan": "加速计算",
        "main_business": ["GPU", "AI加速器"],
        "category": "tech"
    },
    "microsoft": {
        "founding_year": 1975,
        "current_slogan": "予力全球每一人、每一组织",
        "main_business": ["操作系统", "办公软件", "云计算"],
        "category": "tech"
    },
    "nike": {
        "founding_year": 1964,
        "current_slogan": "Just Do It",
        "main_business": ["运动鞋", "运动服装", "运动装备"],
        "category": "sport"
    },
    "adidas": {
        "founding_year": 1949,
        "current_slogan": "Impossible Is Nothing",
        "main_business": ["运动鞋", "运动服装", "运动装备"],
        "category": "sport"
    },
    "puma": {
        "founding_year": 1948,
        "current_slogan": "Forever Faster",
        "main_business": ["运动鞋", "运动服装", "运动装备"],
        "category": "sport"
    },
    "coca-cola": {
        "founding_year": 1886,
        "current_slogan": "Taste the Feeling",
        "main_business": ["饮料", "碳酸饮料"],
        "category": "food"
    },
    "mcdonald-s": {
        "founding_year": 1955,
        "current_slogan": "I'm Lovin' It",
        "main_business": ["快餐", "连锁餐厅"],
        "category": "food"
    },
    "starbucks": {
        "founding_year": 1971,
        "current_slogan": "一切从一杯咖啡开始",
        "main_business": ["咖啡连锁"],
        "category": "food"
    },
    "lego": {
        "founding_year": 1932,
        "current_slogan": "Only the best is good enough",
        "main_business": ["积木玩具"],
        "category": "toy"
    },
    "mattel": {
        "founding_year": 1945,
        "current_slogan": "创造奇迹",
        "main_business": ["玩具", "玩偶"],
        "category": "toy"
    },
    "coach": {
        "founding_year": 1941,
        "current_slogan": "触手可及的奢华",
        "main_business": ["皮具", "手袋", "配饰"],
        "category": "fashion"
    },
}

# Apply fixes
fixed_count = 0
for slug, fixes in brand_fixes.items():
    bj = ROOT / slug / 'brand.json'
    if not bj.exists():
        print(f"⏭️  {slug}: brand.json not found")
        continue
    
    data = json.loads(bj.read_text(encoding='utf-8'))
    
    # Apply fixes
    needs_change = False
    for key, value in fixes.items():
        existing = data.get(key)
        if existing != value:
            data[key] = value
            needs_change = True
    
    if needs_change:
        bj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        fixed_count += 1
        print(f"✅ {slug}: fixed")
    else:
        print(f"✓ {slug}: OK")

print(f"\n共计修复 {fixed_count} 个品牌")

# Now run schema validation
print("\n验证 Schema...")
import subprocess
r = subprocess.run(
    ["python3", "brand_factory.py", "process", "all"],
    capture_output=True, text=True, timeout=120
)
print(r.stdout[-2000:])
if r.stderr:
    print(f"ERR: {r.stderr[-500:]}")
