#!/usr/bin/env python3
"""
brand_heartbeat.py — Autonomous brand encyclopedia heartbeat.
Runs every 30 minutes, generates next batch of brands, pushes to git.
Uses pre-defined brand list, no LLM needed.
Outputs summary of what was done (empty = nothing to do = silent).
"""
import json, os, csv, re, sys

BASE = "/workspace/pinpai-ai-in"
LOCK_FILE = os.path.join(BASE, ".heartbeat.lock")

# Lock to prevent concurrent runs
if os.path.exists(LOCK_FILE):
    import time
    mtime = os.path.getmtime(LOCK_FILE)
    if time.time() - mtime < 1800:  # 30 min lock expiry
        print("LOCKED - another heartbeat may be running")
        sys.exit(0)
    else:
        os.remove(LOCK_FILE)

open(LOCK_FILE, "w").close()

try:
    # --- Read current state ---
    with open(os.path.join(BASE, "brands_index.json")) as f:
        index = json.load(f)
    existing_slugs = set(b['slug'] for b in index)
    
    # Read csv to find brands already deployed
    csv_slugs = set()
    with open(os.path.join(BASE, "master.csv"), newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='|')
        try:
            header = next(reader)
        except StopIteration:
            header = ["slug","name","name_en","category","founding_location","founding_year","deployed"]
        for row in reader:
            if row and len(row) >= 1:
                csv_slugs.add(row[0].strip())
    
    # --- Load next batch from pre-defined brand list ---
    # If we already have a next_batch.json, use it; otherwise create one
    batch_file = os.path.join(BASE, ".next_batch.json")
    if os.path.exists(batch_file):
        with open(batch_file) as f:
            remaining = json.load(f)
    else:
        # Pre-defined brand pool (100+ well-known global brands)
        remaining = [
            # Tech
            {"slug":"ibm","name":"IBM","name_en":"IBM","category":"technology","country":"United States","founding_year":1911,"founding_location":"美国纽约","founder":"托马斯·沃森","website":"https://www.ibm.com","main_business":["信息技术","云计算","人工智能"],"slogan":"IBM — 思考"},
            {"slug":"oracle","name":"甲骨文","name_en":"Oracle","category":"technology","country":"United States","founding_year":1977,"founding_location":"美国加利福尼亚州","founder":"拉里·埃里森、鲍勃·迈纳、埃德·奥茨","website":"https://www.oracle.com","main_business":["数据库软件","云计算","企业软件"],"slogan":"Oracle — 云就是现在"},
            {"slug":"cisco","name":"思科","name_en":"Cisco","category":"technology","country":"United States","founding_year":1984,"founding_location":"美国加利福尼亚州圣何塞","founder":"莱昂纳德·波萨克、桑德拉·勒纳","website":"https://www.cisco.com","main_business":["网络设备","网络安全","通信技术"],"slogan":"Cisco — 连接未来"},
            # Auto
            {"slug":"jaguar","name":"捷豹","name_en":"Jaguar","category":"auto","country":"United Kingdom","founding_year":1922,"founding_location":"英国考文垂","founder":"威廉·里昂斯","website":"https://www.jaguar.com","main_business":["豪华汽车制造"],"slogan":"Jaguar — 优雅与速度的化身"},
            {"slug":"land-rover","name":"路虎","name_en":"Land Rover","category":"auto","country":"United Kingdom","founding_year":1948,"founding_location":"英国索利哈尔","founder":"莫里斯·威尔克斯","website":"https://www.landrover.com","main_business":["豪华SUV制造"],"slogan":"Land Rover — 无往不至"},
            {"slug":"volvo","name":"沃尔沃","name_en":"Volvo","category":"auto","country":"Sweden","founding_year":1927,"founding_location":"瑞典哥德堡","founder":"阿萨尔·加布里埃尔松、古斯塔夫·拉尔松","website":"https://www.volvocars.com","main_business":["汽车制造","交通安全"],"slogan":"Volvo — 安全至上"},
            {"slug":"mini","name":"MINI","name_en":"MINI","category":"auto","country":"United Kingdom","founding_year":1959,"founding_location":"英国伯明翰","founder":"英国汽车公司","website":"https://www.mini.com","main_business":["小型汽车制造"],"slogan":"MINI — 不仅是一辆车"},
            {"slug":"fiat","name":"菲亚特","name_en":"Fiat","category":"auto","country":"Italy","founding_year":1899,"founding_location":"意大利都灵","founder":"乔瓦尼·阿涅利","website":"https://www.fiat.com","main_business":["汽车制造"],"slogan":"Fiat — 意大利生活之美"},
            {"slug":"peugeot","name":"标致","name_en":"Peugeot","category":"auto","country":"France","founding_year":1810,"founding_location":"法国索肖","founder":"阿尔芒·标致","website":"https://www.peugeot.com","main_business":["汽车制造","自行车制造"],"slogan":"Peugeot — 严谨与激情"},
            {"slug":"citroen","name":"雪铁龙","name_en":"Citroën","category":"auto","country":"France","founding_year":1919,"founding_location":"法国巴黎","founder":"安德烈·雪铁龙","website":"https://www.citroen.com","main_business":["汽车制造"],"slogan":"Citroën — 创意驱动"},
            # More brands
            {"slug":"tesla-motors","name":"特斯拉汽车","name_en":"Tesla Motors","category":"auto","country":"United States","founding_year":2003,"founding_location":"美国加利福尼亚州","founder":"马丁·艾伯哈德、马克·塔彭宁","website":"https://www.tesla.com","main_business":["电动汽车制造","清洁能源"],"slogan":"Tesla — 加速世界向可持续能源转变"},
            {"slug":"mazda","name":"马自达","name_en":"Mazda","category":"auto","country":"Japan","founding_year":1920,"founding_location":"日本广岛","founder":"松田重次郎","website":"https://www.mazda.com","main_business":["汽车制造"],"slogan":"Mazda — 驾乘愉悦"},
            {"slug":"subaru","name":"斯巴鲁","name_en":"Subaru","category":"auto","country":"Japan","founding_year":1953,"founding_location":"日本东京","founder":"中岛知久平","website":"https://www.subaru.com","main_business":["汽车制造","航空技术"],"slogan":"Subaru — 安心·愉悦"},
            {"slug":"mitsubishi-motors","name":"三菱汽车","name_en":"Mitsubishi Motors","category":"auto","country":"Japan","founding_year":1970,"founding_location":"日本东京","founder":"三菱集团","website":"https://www.mitsubishi-motors.com","main_business":["汽车制造"],"slogan":"三菱 — 驱动您的激情"},
            {"slug":"nissan","name":"日产","name_en":"Nissan","category":"auto","country":"Japan","founding_year":1933,"founding_location":"日本横滨","founder":"鲇川义介","website":"https://www.nissan.com","main_business":["汽车制造"],"slogan":"Nissan — 技术日产 人·车·生活"},
            # Fashion

            # More brands - Fashion/Luxury
            {"slug":"balenciaga","name":"巴黎世家","name_en":"Balenciaga","category":"fashion-luxury","country":"France","founding_year":1919,"founding_location":"法国巴黎","founder":"克里斯托巴尔·巴伦西亚加","website":"https://www.balenciaga.com","main_business":["高级时装","配饰","香水"],"slogan":"Balenciaga — 解构时尚的前卫力量"},
            {"slug":"ysl","name":"圣罗兰","name_en":"Yves Saint Laurent","category":"fashion-luxury","country":"France","founding_year":1961,"founding_location":"法国巴黎","founder":"伊夫·圣罗兰、皮埃尔·贝尔热","website":"https://www.ysl.com","main_business":["高级时装","香水","配饰"],"slogan":"YSL — 时尚是永恒的叛逆"},
            {"slug":"dior","name":"迪奥","name_en":"Dior","category":"fashion-luxury","country":"France","founding_year":1946,"founding_location":"法国巴黎","founder":"克里斯汀·迪奥","website":"https://www.dior.com","main_business":["高级时装","香水","化妆品"],"slogan":"Dior — 法式优雅的创造者"},
            {"slug":"hermes","name":"爱马仕","name_en":"Hermès","category":"fashion-luxury","country":"France","founding_year":1837,"founding_location":"法国巴黎","founder":"蒂埃里·爱马仕","website":"https://www.hermes.com","main_business":["奢侈品","皮具","丝巾","香水"],"slogan":"Hermès — 匠心传承，定义奢华"},
            {"slug":"patek-philippe","name":"百达翡丽","name_en":"Patek Philippe","category":"fashion-luxury","country":"Switzerland","founding_year":1839,"founding_location":"瑞士日内瓦","founder":"安东尼·百达、让·阿德里安·翡丽","website":"https://www.patek.com","main_business":["高级腕表制造"],"slogan":"Patek Philippe — 没人能拥有百达翡丽"},
            {"slug":"audemars-piguet","name":"爱彼","name_en":"Audemars Piguet","category":"fashion-luxury","country":"Switzerland","founding_year":1875,"founding_location":"瑞士勒布拉叙","founder":"朱尔·爱德马、爱德华·皮盖","website":"https://www.audemarspiguet.com","main_business":["高级腕表制造"],"slogan":"Audemars Piguet — 驾驭常规，铸就创新"},
            {"slug":"rolex","name":"劳力士","name_en":"Rolex","category":"fashion-luxury","country":"Switzerland","founding_year":1905,"founding_location":"瑞士日内瓦","founder":"汉斯·威尔斯多夫、阿尔弗雷德·戴维斯","website":"https://www.rolex.com","main_business":["高级腕表制造"],"slogan":"Rolex — 恒动，永无止境"},
            {"slug":"omega","name":"欧米茄","name_en":"Omega","category":"fashion-luxury","country":"Switzerland","founding_year":1848,"founding_location":"瑞士拉绍德封","founder":"路易·勃兰特","website":"https://www.omegawatches.com","main_business":["腕表制造"],"slogan":"Omega — 浪琴，记录时间"},
            {"slug":"krispy-kreme","name":"卡仕奇甜甜圈","name_en":"Krispy Kreme","category":"food","country":"United States","founding_year":1937,"founding_location":"美国北卡罗来纳州温斯顿-塞勒姆","founder":"弗农·鲁道夫","website":"https://www.krispykreme.com","main_business":["甜甜圈","咖啡"],"slogan":"Krispy Kreme — 甜蜜时刻"},
            {"slug":"starbucks","name":"星巴克","name_en":"Starbucks","category":"food","country":"United States","founding_year":1971,"founding_location":"美国华盛顿州西雅图","founder":"杰里·鲍德温、戈登·鲍克、泽夫·西格尔","website":"https://www.starbucks.com","description":"全球最大的咖啡连锁店。"},
            {"slug":"7-eleven","name":"7-Eleven","name_en":"7-Eleven","category":"retail","country":"Japan/United States","founding_year":1927,"founding_location":"美国得克萨斯州达拉斯","founder":"约翰·杰斐逊·格林","website":"https://www.7-eleven.com","description":"全球最大的便利店连锁品牌。"},
            {"slug":"ikea","name":"宜家","name_en":"IKEA","category":"retail","country":"Sweden","founding_year":1943,"founding_location":"瑞典阿姆胡特","founder":"英格瓦·坎普拉德","website":"https://www.ikea.com","description":"全球最知名的家居零售商。"},
            {"slug":"mcdonalds","name":"麦当劳","name_en":"McDonald's","category":"food","country":"United States","founding_year":1940,"founding_location":"美国加利福尼亚州圣贝纳迪诺","founder":"理查德·麦当劳、莫里斯·麦当劳","website":"https://www.mcdonalds.com","description":"全球最大的快餐连锁品牌。"},
            {"slug":"kfc","name":"肯德基","name_en":"KFC","category":"food","country":"United States","founding_year":1952,"founding_location":"美国犹他州盐湖城","founder":"哈兰·山德士","website":"https://www.kfc.com","description":"全球最知名的炸鸡连锁品牌。"},
            {"slug":"pepsi","name":"百事","name_en":"Pepsi","category":"food","country":"United States","founding_year":1898,"founding_location":"美国北卡罗来纳州纽伯恩","founder":"凯莱布·布拉德汉姆","website":"https://www.pepsi.com","description":"全球知名碳酸饮料品牌。"},
            {"slug":"nestl","name":"雀巢","name_en":"Nestlé","category":"food","country":"Switzerland","founding_year":1866,"founding_location":"瑞士沃韦","founder":"亨利·雀巢","website":"https://www.nestle.com","description":"全球最大的食品饮料公司。"},
            {"slug":"netflix","name":"Netflix","name_en":"Netflix","category":"technology","country":"United States","founding_year":1997,"founding_location":"美国加利福尼亚州斯科茨谷","founder":"里德·哈斯廷斯、马克·兰多夫","website":"https://www.netflix.com","description":"全球领先的流媒体娱乐平台。"},
            {"slug":"toyota","name":"丰田","name_en":"Toyota","category":"auto","country":"Japan","founding_year":1937,"founding_location":"日本爱知县丰田市","founder":"丰田喜一郎","website":"https://www.toyota.com","description":"全球最大的汽车制造商之一。"},
            {"slug":"honda","name":"本田","name_en":"Honda","category":"auto","country":"Japan","founding_year":1948,"founding_location":"日本静冈县浜松市","founder":"本田宗一郎","website":"https://www.honda.com","description":"日本知名汽车及摩托车制造商。"},
            {"slug":"nike","name":"耐克","name_en":"Nike","category":"sport","country":"United States","founding_year":1964,"founding_location":"美国俄勒冈州比弗顿","founder":"比尔·鲍尔曼、菲尔·奈特","website":"https://www.nike.com","description":"全球最大的运动鞋服品牌。"},
            {"slug":"adidas","name":"adidas","name_en":"adidas","category":"sport","country":"Germany","founding_year":1949,"founding_location":"德国黑措根奥拉赫","founder":"阿道夫·达斯勒","website":"https://www.adidas.com","description":"全球知名运动品牌。"},
            {"slug":"apple","name":"苹果","name_en":"Apple","category":"technology","country":"United States","founding_year":1976,"founding_location":"美国加利福尼亚州库比蒂诺","founder":"史蒂夫·乔布斯、史蒂夫·沃兹尼亚克、罗纳德·韦恩","website":"https://www.apple.com","description":"全球最具价值的科技公司之一。"},
            {"slug":"google","name":"谷歌","name_en":"Google","category":"technology","country":"United States","founding_year":1998,"founding_location":"美国加利福尼亚州门洛帕克","founder":"拉里·佩奇、谢尔盖·布林","website":"https://www.google.com","description":"全球最大的搜索引擎公司。"},
            {"slug":"microsoft","name":"微软","name_en":"Microsoft","category":"technology","country":"United States","founding_year":1975,"founding_location":"美国新墨西哥州阿尔伯克基","founder":"比尔·盖茨、保罗·艾伦","website":"https://www.microsoft.com","description":"全球领先的软件和云计算公司。"},
            {"slug":"amazon","name":"亚马逊","name_en":"Amazon","category":"technology","country":"United States","founding_year":1994,"founding_location":"美国华盛顿州西雅图","founder":"杰夫·贝佐斯","website":"https://www.amazon.com","description":"全球最大的电子商务和云计算公司。"},
            {"slug":"samsung","name":"三星","name_en":"Samsung","category":"technology","country":"South Korea","founding_year":1938,"founding_location":"韩国大邱","founder":"李秉喆","website":"https://www.samsung.com","description":"韩国最大的电子产品制造商。"},
            {"slug":"bmw","name":"宝马","name_en":"BMW","category":"auto","country":"Germany","founding_year":1916,"founding_location":"德国慕尼黑","founder":"吉斯坦·奥托、卡尔·拉普","website":"https://www.bmw.com","description":"德国顶级豪华汽车制造商。"},
            {"slug":"mercedes-benz","name":"梅赛德斯-奔驰","name_en":"Mercedes-Benz","category":"auto","country":"Germany","founding_year":1926,"founding_location":"德国斯图加特","founder":"卡尔·本茨、戈特利布·戴姆勒","website":"https://www.mercedes-benz.com","description":"世界知名的豪华汽车品牌。"},
            {"slug":"ferrari","name":"法拉利","name_en":"Ferrari","category":"auto","country":"Italy","founding_year":1947,"founding_location":"意大利马拉内罗","founder":"恩佐·法拉利","website":"https://www.ferrari.com","description":"意大利传奇超跑品牌。"},
            {"slug":"porsche","name":"保时捷","name_en":"Porsche","category":"auto","country":"Germany","founding_year":1931,"founding_location":"德国斯图加特","founder":"费迪南德·保时捷","website":"https://www.porsche.com","description":"德国豪华跑车制造商。"},
            {"slug":"audi","name":"奥迪","name_en":"Audi","category":"auto","country":"Germany","founding_year":1909,"founding_location":"德国茨维考","founder":"奥古斯特·霍希","website":"https://www.audi.com","description":"德国知名豪华汽车品牌。"},
            {"slug":"volkswagen","name":"大众","name_en":"Volkswagen","category":"auto","country":"Germany","founding_year":1937,"founding_location":"德国沃尔夫斯堡","founder":"德国劳工阵线","website":"https://www.volkswagen.com","description":"全球最大的汽车制造商之一。"},
            {"slug":"sony","name":"索尼","name_en":"Sony","category":"technology","country":"Japan","founding_year":1946,"founding_location":"日本东京","founder":"井深大、盛田昭夫","website":"https://www.sony.com","description":"日本最具影响力的电子娱乐公司。"},
            {"slug":"disney","name":"迪士尼","name_en":"Disney","category":"entertainment","country":"United States","founding_year":1923,"founding_location":"美国加利福尼亚州洛杉矶","founder":"华特·迪士尼、罗伊·迪士尼","website":"https://www.disney.com","description":"全球最大的娱乐传媒公司。"},
            {"slug":"coca-cola","name":"可口可乐","name_en":"Coca-Cola","category":"food","country":"United States","founding_year":1886,"founding_location":"美国佐治亚州亚特兰大","founder":"约翰·彭伯顿","website":"https://www.coca-cola.com","description":"全球最知名的碳酸饮料品牌。"},
            {"slug":"nintendo","name":"任天堂","name_en":"Nintendo","category":"technology","country":"Japan","founding_year":1889,"founding_location":"日本京都府京都市","founder":"山内房治郎","website":"https://www.nintendo.com","description":"日本最具影响力的游戏公司。"},
            {"slug":"lg","name":"LG","name_en":"LG","category":"technology","country":"South Korea","founding_year":1947,"founding_location":"韩国釜山","founder":"具仁会","website":"https://www.lg.com","description":"韩国知名电子和家电制造商。"},
            {"slug":"panasonic","name":"松下","name_en":"Panasonic","category":"technology","country":"Japan","founding_year":1918,"founding_location":"日本大阪","founder":"松下幸之助","website":"https://www.panasonic.com","description":"日本知名电子产品和家电制造商。"},
            {"slug":"hyundai","name":"现代","name_en":"Hyundai","category":"auto","country":"South Korea","founding_year":1967,"founding_location":"韩国首尔","founder":"郑周永","website":"https://www.hyundai.com","description":"韩国最大的汽车制造商。"},
            {"slug":"kia","name":"起亚","name_en":"Kia","category":"auto","country":"South Korea","founding_year":1944,"founding_location":"韩国首尔","founder":"金哲浩","website":"https://www.kia.com","description":"韩国知名汽车制造商。"},
            {"slug":"canon","name":"佳能","name_en":"Canon","category":"technology","country":"Japan","founding_year":1937,"founding_location":"日本东京大田区","founder":"御手洗毅、内田三郎","website":"https://www.canon.com","description":"日本领先的影像与光学产品制造商。"},
            {"slug":"intel","name":"英特尔","name_en":"Intel","category":"technology","country":"United States","founding_year":1968,"founding_location":"美国加利福尼亚州圣克拉拉","founder":"戈登·摩尔、罗伯特·诺伊斯、安迪·格鲁夫","website":"https://www.intel.com","description":"全球最大的半导体芯片制造商。"},
            {"slug":"nvidia","name":"英伟达","name_en":"NVIDIA","category":"technology","country":"United States","founding_year":1993,"founding_location":"美国加利福尼亚州圣克拉拉","founder":"黄仁勋、克里斯·马拉科夫斯基、柯蒂斯·普里姆","website":"https://www.nvidia.com","description":"全球领先的GPU和AI计算公司。"},
            {"slug":"meta","name":"Meta","name_en":"Meta","category":"technology","country":"United States","founding_year":2004,"founding_location":"美国马萨诸塞州剑桥","founder":"马克·扎克伯格","website":"https://www.meta.com","description":"全球最大的社交媒体公司。"},
            {"slug":"tesla","name":"特斯拉","name_en":"Tesla","category":"auto","country":"United States","founding_year":2003,"founding_location":"美国加利福尼亚州圣卡洛斯","founder":"马丁·艾伯哈德、马克·塔彭宁","website":"https://www.tesla.com","description":"全球领先的电动汽车制造商。"},
            {"slug":"prada","name":"普拉达","name_en":"Prada","category":"fashion-luxury","country":"Italy","founding_year":1913,"founding_location":"意大利米兰","founder":"马里奥·普拉达","website":"https://www.prada.com","description":"意大利顶级奢侈时尚品牌。"},
            {"slug":"burberry","name":"博柏利","name_en":"Burberry","category":"fashion-luxury","country":"United Kingdom","founding_year":1856,"founding_location":"英国伦敦","founder":"托马斯·博柏利","website":"https://www.burberry.com","description":"英国标志性奢侈时尚品牌。"},
            {"slug":"cartier","name":"卡地亚","name_en":"Cartier","category":"fashion-luxury","country":"France","founding_year":1847,"founding_location":"法国巴黎","founder":"路易·弗朗索瓦·卡地亚","website":"https://www.cartier.com","description":"法国顶级珠宝腕表品牌。"},
            {"slug":"louis-vuitton","name":"路易威登","name_en":"Louis Vuitton","category":"fashion-luxury","country":"France","founding_year":1854,"founding_location":"法国巴黎","founder":"路易·威登","website":"https://www.louisvuitton.com","description":"全球最具价值的奢侈品牌之一。"},
            {"slug":"gucci","name":"古驰","name_en":"Gucci","category":"fashion-luxury","country":"Italy","founding_year":1921,"founding_location":"意大利佛罗伦萨","founder":"古奇奥·古驰","website":"https://www.gucci.com","description":"意大利著名奢侈时尚品牌。"},
            {"slug":"chanel","name":"香奈儿","name_en":"Chanel","category":"fashion-luxury","country":"France","founding_year":1910,"founding_location":"法国巴黎","founder":"可可·香奈儿","website":"https://www.chanel.com","description":"法国标志性奢侈品牌。"},
            {"slug":"hermes","name":"爱马仕","name_en":"Hermès","category":"fashion-luxury","country":"France","founding_year":1837,"founding_location":"法国巴黎","founder":"蒂埃里·爱马仕","website":"https://www.hermes.com","description":"法国顶级奢侈品牌。"},
            {"slug":"dior","name":"迪奥","name_en":"Dior","category":"fashion-luxury","country":"France","founding_year":1946,"founding_location":"法国巴黎","founder":"克里斯汀·迪奥","website":"https://www.dior.com","description":"法国著名时尚奢侈品牌。"},
            {"slug":"versace","name":"范思哲","name_en":"Versace","category":"fashion-luxury","country":"Italy","founding_year":1978,"founding_location":"意大利米兰","founder":"詹尼·范思哲","website":"https://www.versace.com","description":"意大利著名奢侈时尚品牌。"},
            {"slug":"bulgari","name":"宝格丽","name_en":"Bulgari","category":"fashion-luxury","country":"Italy","founding_year":1884,"founding_location":"意大利罗马","founder":"索蒂里奥斯·宝格丽","website":"https://www.bulgari.com","description":"意大利顶级珠宝品牌。"},
            {"slug":"tiffany-and-co","name":"蒂芙尼","name_en":"Tiffany & Co.","category":"jewelry","country":"United States","founding_year":1837,"founding_location":"美国纽约","founder":"查尔斯·路易斯·蒂芙尼","website":"https://www.tiffany.com","description":"美国标志性珠宝品牌。"},
            {"slug":"uniqlo","name":"优衣库","name_en":"Uniqlo","category":"fashion","country":"Japan","founding_year":1949,"founding_location":"日本山口县宇部市","founder":"柳井正","website":"https://www.uniqlo.com","description":"日本最大的服装零售商。"},
            {"slug":"muji","name":"无印良品","name_en":"Muji","category":"fashion","country":"Japan","founding_year":1980,"founding_location":"日本东京","founder":"西友集团","website":"https://www.muji.com","description":"日本极简生活方式品牌。"},
            {"slug":"handm","name":"H&M","name_en":"H&M","category":"fashion","country":"Sweden","founding_year":1947,"founding_location":"瑞典斯德哥尔摩","founder":"埃尔林·佩尔森","website":"https://www.hm.com","description":"全球知名快时尚品牌。"},
            {"slug":"zara","name":"Zara","name_en":"Zara","category":"fashion","country":"Spain","founding_year":1975,"founding_location":"西班牙拉科鲁尼亚","founder":"阿曼西奥·奥尔特加","website":"https://www.zara.com","description":"全球最大的快时尚品牌之一。"},
            {"slug":"lacoste","name":"鳄鱼","name_en":"Lacoste","category":"fashion","country":"France","founding_year":1933,"founding_location":"法国巴黎","founder":"勒内·拉科斯特","website":"https://www.lacoste.com","description":"法国标志性休闲时尚品牌。"},
            {"slug":"ralph-lauren","name":"拉夫·劳伦","name_en":"Ralph Lauren","category":"fashion","country":"United States","founding_year":1967,"founding_location":"美国纽约","founder":"拉夫·劳伦","website":"https://www.ralphlauren.com","description":"美国高端时尚品牌。"},
            {"slug":"calvin-klein","name":"卡尔文·克莱因","name_en":"Calvin Klein","category":"fashion","country":"United States","founding_year":1968,"founding_location":"美国纽约","founder":"卡尔文·克莱因、巴里·施瓦茨","website":"https://www.calvinklein.com","description":"美国知名时尚品牌。"},
            {"slug":"pizza-hut","name":"必胜客","name_en":"Pizza Hut","category":"food","country":"United States","founding_year":1958,"founding_location":"美国堪萨斯州威奇托","founder":"丹·卡尼、弗兰克·卡尼","website":"https://www.pizzahut.com","description":"全球知名披萨连锁品牌。"},
            {"slug":"burger-king","name":"汉堡王","name_en":"Burger King","category":"food","country":"United States","founding_year":1954,"founding_location":"美国佛罗里达州迈阿密","founder":"詹姆斯·麦克拉莫尔、大卫·埃杰顿","website":"https://www.burgerking.com","description":"全球知名快餐汉堡品牌。"},
            {"slug":"lego","name":"乐高","name_en":"LEGO","category":"toy","country":"Denmark","founding_year":1932,"founding_location":"丹麦比隆","founder":"奥莱·柯克·克里斯蒂安森","website":"https://www.lego.com","description":"全球最知名的积木玩具品牌。"},
            {"slug":"dominos","name":"达美乐","name_en":"Domino's","category":"food","country":"United States","founding_year":1960,"founding_location":"美国密歇根州伊普西兰蒂","founder":"汤姆·莫纳汉、詹姆斯·莫纳汉","website":"https://www.dominos.com","main_business":["比萨外卖连锁"],"slogan":"Domino's — 30分钟必达"},
            {"slug":"hewlett-packard","name":"惠普","name_en":"HP","category":"technology","country":"United States","founding_year":1939,"founding_location":"美国加利福尼亚州帕洛阿尔托","founder":"比尔·休利特、戴维·帕卡德","website":"https://www.hp.com","main_business":["计算机","打印机","IT服务"],"slogan":"HP — 创造科技新体验"},
            {"slug":"dell","name":"戴尔","name_en":"Dell","category":"technology","country":"United States","founding_year":1984,"founding_location":"美国得克萨斯州奥斯汀","founder":"迈克尔·戴尔","website":"https://www.dell.com","main_business":["计算机","服务器","IT解决方案"],"slogan":"Dell — 科技让生活更美好"},
            {"slug":"lenovo","name":"联想","name_en":"Lenovo","category":"technology","country":"China","founding_year":1984,"founding_location":"中国北京","founder":"柳传志","website":"https://www.lenovo.com","main_business":["计算机","智能手机","IT设备"],"slogan":"Lenovo — 智慧中国"},
            {"slug":"uber","name":"优步","name_en":"Uber","category":"technology","country":"United States","founding_year":2009,"founding_location":"美国加利福尼亚州旧金山","founder":"特拉维斯·卡兰尼克、加勒特·坎普","website":"https://www.uber.com","main_business":["网约车","外卖配送","货运"],"slogan":"Uber — 出行新方式"},
            {"slug":"airbnb","name":"爱彼迎","name_en":"Airbnb","category":"technology","country":"United States","founding_year":2008,"founding_location":"美国加利福尼亚州旧金山","founder":"布莱恩·切斯基、乔·格比亚、内森·布莱查奇克","website":"https://www.airbnb.com","main_business":["民宿短租","旅游体验"],"slogan":"Airbnb — 家在四方"},
            {"slug":"tencent","name":"腾讯","name_en":"Tencent","category":"technology","country":"China","founding_year":1998,"founding_location":"中国深圳","founder":"马化腾、张志东","website":"https://www.tencent.com","main_business":["社交网络","游戏","金融科技"],"slogan":"Tencent — 科技向善"},
            {"slug":"alibaba","name":"阿里巴巴","name_en":"Alibaba","category":"technology","country":"China","founding_year":1999,"founding_location":"中国杭州","founder":"马云","website":"https://www.alibaba.com","main_business":["电子商务","云计算","金融科技"],"slogan":"Alibaba — 让天下没有难做的生意"},
            {"slug":"baidu","name":"百度","name_en":"Baidu","category":"technology","country":"China","founding_year":2000,"founding_location":"中国北京","founder":"李彦宏、徐勇","website":"https://www.baidu.com","main_business":["搜索引擎","人工智能","自动驾驶"],"slogan":"百度一下，你就知道"},
            {"slug":"bytedance","name":"字节跳动","name_en":"ByteDance","category":"technology","country":"China","founding_year":2012,"founding_location":"中国北京","founder":"张一鸣","website":"https://www.bytedance.com","main_business":["短视频","信息平台","AI技术"],"slogan":"ByteDance — 激发创造,丰富生活"},
            {"slug":"siemens","name":"西门子","name_en":"Siemens","category":"technology","country":"Germany","founding_year":1847,"founding_location":"德国柏林","founder":"维尔纳·冯·西门子","website":"https://www.siemens.com","main_business":["工业自动化","医疗","能源"],"slogan":"Siemens — 科技有为"},
            {"slug":"ge","name":"通用电气","name_en":"General Electric","category":"technology","country":"United States","founding_year":1892,"founding_location":"美国纽约","founder":"托马斯·爱迪生、查尔斯·科芬、埃德温·休斯敦","website":"https://www.ge.com","main_business":["航空","医疗","可再生能源"],"slogan":"GE — 想象力创造可能"},
            {"slug":"sap","name":"SAP","name_en":"SAP","category":"technology","country":"Germany","founding_year":1972,"founding_location":"德国沃尔多夫","founder":"迪特马尔·霍普、汉斯-维尔纳·赫克特、克劳斯·奇拉","website":"https://www.sap.com","main_business":["企业软件","ERP","云计算"],"slogan":"SAP — 让世界运转更卓越"},
            {"slug":"salesforce","name":"Salesforce","name_en":"Salesforce","category":"technology","country":"United States","founding_year":1999,"founding_location":"美国加利福尼亚州旧金山","founder":"马克·贝尼奥夫","website":"https://www.salesforce.com","main_business":["CRM","云计算","企业软件"],"slogan":"Salesforce — 客户成功平台"},
            {"slug":"oracle","name":"甲骨文","name_en":"Oracle","category":"technology","country":"United States","founding_year":1977,"founding_location":"美国加利福尼亚州雷德伍德城","founder":"拉里·埃里森、鲍勃·迈纳、埃德·奥茨","website":"https://www.oracle.com","main_business":["数据库","云计算","企业软件"],"slogan":"Oracle — 云就是现在"},
            {"slug":"pfizer","name":"辉瑞","name_en":"Pfizer","category":"healthcare","country":"United States","founding_year":1849,"founding_location":"美国纽约","founder":"查尔斯·辉瑞、查尔斯·埃尔哈特","website":"https://www.pfizer.com","main_business":["制药","疫苗","生物技术"],"slogan":"Pfizer — 为世界带来改变"},
            {"slug":"novartis","name":"诺华","name_en":"Novartis","category":"healthcare","country":"Switzerland","founding_year":1996,"founding_location":"瑞士巴塞尔","founder":"合并成立","website":"https://www.novartis.com","main_business":["制药","眼科","基因治疗"],"slogan":"Novartis — 重塑医学"},
            {"slug":"roche","name":"罗氏","name_en":"Roche","category":"healthcare","country":"Switzerland","founding_year":1896,"founding_location":"瑞士巴塞尔","founder":"弗里茨·霍夫曼-拉罗氏","website":"https://www.roche.com","main_business":["制药","诊断","生物技术"],"slogan":"Roche — 个性化医疗"},
            {"slug":"johnson-and-johnson","name":"强生","name_en":"Johnson & Johnson","category":"healthcare","country":"United States","founding_year":1886,"founding_location":"美国新泽西州新不伦瑞克","founder":"罗伯特·伍德·强生一世、詹姆斯·伍德·强生、爱德华·米德·强生","website":"https://www.jnj.com","main_business":["制药","医疗器械","消费品"],"slogan":"Johnson & Johnson — 关爱世界,关爱健康"},
            {"slug":"merck","name":"默克","name_en":"Merck","category":"healthcare","country":"United States","founding_year":1891,"founding_location":"美国新泽西州拉威","founder":"乔治·默克","website":"https://www.merck.com","main_business":["制药","疫苗","动物保健"],"slogan":"Merck — 以科学改变生命"},
            {"slug":"bayer","name":"拜耳","name_en":"Bayer","category":"healthcare","country":"Germany","founding_year":1863,"founding_location":"德国伍珀塔尔","founder":"弗里德里希·拜耳、约翰·弗里德里希·韦斯科特","website":"https://www.bayer.com","main_business":["制药","农业","消费者健康"],"slogan":"Bayer — 科技创造美好生活"},
            {"slug":"abbott","name":"雅培","name_en":"Abbott","category":"healthcare","country":"United States","founding_year":1888,"founding_location":"美国伊利诺伊州芝加哥","founder":"华莱士·卡尔文·雅培","website":"https://www.abbott.com","main_business":["医疗设备","诊断","营养品"],"slogan":"Abbott — 生命的力量"},
            {"slug":"cisco","name":"思科","name_en":"Cisco","category":"technology","country":"United States","founding_year":1984,"founding_location":"美国加利福尼亚州圣何塞","founder":"莱昂纳德·波萨克、桑德拉·勒纳","website":"https://www.cisco.com","main_business":["网络设备","网络安全","协作"],"slogan":"Cisco — 连接未来"},
            {"slug":"accenture","name":"埃森哲","name_en":"Accenture","category":"technology","country":"Ireland","founding_year":1989,"founding_location":"爱尔兰都柏林","founder":"安达信咨询","website":"https://www.accenture.com","main_business":["管理咨询","技术服务","外包"],"slogan":"Accenture — 创新驱动价值"},
            {"slug":"deloitte","name":"德勤","name_en":"Deloitte","category":"finance","country":"United Kingdom","founding_year":1845,"founding_location":"英国伦敦","founder":"威廉·韦尔奇·德勤","website":"https://www.deloitte.com","main_business":["审计","税务","咨询"],"slogan":"Deloitte — 专业服务成就卓越"},
            {"slug":"pwc","name":"普华永道","name_en":"PwC","category":"finance","country":"United Kingdom","founding_year":1998,"founding_location":"英国伦敦","founder":"合并成立","website":"https://www.pwc.com","main_business":["审计","税务","咨询"],"slogan":"PwC — 解决重要问题,建立社会信任"},
            {"slug":"ey","name":"安永","name_en":"EY","category":"finance","country":"United Kingdom","founding_year":1989,"founding_location":"英国伦敦","founder":"合并成立","website":"https://www.ey.com","main_business":["审计","税务","战略咨询"],"slogan":"EY — 建设更美好的商业世界"},
            {"slug":"3m","name":"3M","name_en":"3M","category":"technology","country":"United States","founding_year":1902,"founding_location":"美国明尼苏达州明尼阿波利斯","founder":"五名商人联合创立","website":"https://www.3m.com","main_business":["工业材料","医疗","消费品"],"slogan":"3M — 科技改善生活"},
            {"slug":"dupont","name":"杜邦","name_en":"DuPont","category":"technology","country":"United States","founding_year":1802,"founding_location":"美国特拉华州威明顿","founder":"厄留梯尔·伊雷内·杜邦","website":"https://www.dupont.com","main_business":["化工","材料","农业"],"slogan":"DuPont — 科学创造奇迹"},
            {"slug":"basf","name":"巴斯夫","name_en":"BASF","category":"technology","country":"Germany","founding_year":1865,"founding_location":"德国路德维希港","founder":"弗里德里希·恩格尔霍恩","website":"https://www.basf.com","main_business":["化工","材料","涂料"],"slogan":"BASF — 创造化学新作用"},
            {"slug":"cnn","name":"CNN","name_en":"CNN","category":"media","country":"United States","founding_year":1980,"founding_location":"美国佐治亚州亚特兰大","founder":"特德·特纳","website":"https://www.cnn.com","main_business":["新闻广播","数字媒体"],"slogan":"CNN — 全球新闻领导者"},
            {"slug":"bbc","name":"BBC","name_en":"BBC","category":"media","country":"United Kingdom","founding_year":1922,"founding_location":"英国伦敦","founder":"英国政府特许","website":"https://www.bbc.com","main_business":["广播","电视","数字媒体"],"slogan":"BBC — 启迪、教育、娱乐"},
            {"slug":"hilton","name":"希尔顿","name_en":"Hilton","category":"hotel","country":"美国","founding_year":1919,"founding_location":"美国得克萨斯州塞斯柯","founder":"康拉德·希尔顿","website":"https://www.hilton.com","main_business":["酒店运营"],"slogan":"Hilton — 热情好客"},
            {"slug":"hyatt","name":"凯悦","name_en":"Hyatt","category":"hotel","country":"美国","founding_year":1957,"founding_location":"美国加利福尼亚州洛杉矶","founder":"杰伊·普利兹克","website":"https://www.hyatt.com","main_business":["酒店运营"],"slogan":"Hyatt — 用心关怀"},
            {"slug":"ihg","name":"洲际酒店","name_en":"IHG","category":"hotel","country":"英国","founding_year":1777,"founding_location":"英国伦敦","founder":"合并集团","website":"https://www.ihg.com","main_business":["酒店运营"],"slogan":"IHG — 真正待客之道"},
            {"slug":"accor","name":"雅高","name_en":"Accor","category":"hotel","country":"法国","founding_year":1967,"founding_location":"法国巴黎","founder":"保罗·杜布吕、杰拉德·佩利松","website":"https://www.accor.com","main_business":["酒店运营"],"slogan":"Accor — 衷心待客"},
            {"slug":"four-seasons","name":"四季酒店","name_en":"Four Seasons","category":"hotel","country":"加拿大","founding_year":1960,"founding_location":"加拿大多伦多","founder":"伊西多尔·夏普","website":"https://www.fourseasons.com","main_business":["豪华酒店运营"],"slogan":"Four Seasons — 让每一刻都成为美好回忆"},
            {"slug":"shangri-la","name":"香格里拉","name_en":"Shangri-La Hotels","category":"hotel","country":"中国香港","founding_year":1971,"founding_location":"中国香港","founder":"郭鹤年","website":"https://www.shangri-la.com","main_business":["豪华酒店运营"],"slogan":"香格里拉 — 殷勤好客亚洲情"},
            {"slug":"mandarin-oriental","name":"文华东方","name_en":"Mandarin Oriental","category":"hotel","country":"中国香港","founding_year":1963,"founding_location":"中国香港","founder":"合并集团","website":"https://www.mandarinoriental.com","main_business":["豪华酒店运营"],"slogan":"Mandarin Oriental — 独具一格"},
            {"slug":"ritz-carlton","name":"丽思卡尔顿","name_en":"Ritz-Carlton","category":"hotel","country":"美国","founding_year":1983,"founding_location":"美国马里兰州","founder":"威廉·B·约翰逊","website":"https://www.ritzcarlton.com","main_business":["豪华酒店运营"],"slogan":"Ritz-Carlton — 我们以绅士淑女的态度为绅士淑女服务"},
            {"slug":"wyndham","name":"温德姆","name_en":"Wyndham","category":"hotel","country":"美国","founding_year":1981,"founding_location":"美国新泽西州","founder":"特伦特·哈姆","website":"https://www.wyndhamhotels.com","main_business":["酒店运营"],"slogan":"Wyndham — 旅居全球"},
            {"slug":"emirates","name":"阿联酋航空","name_en":"Emirates","category":"airline","country":"阿联酋","founding_year":1985,"founding_location":"阿联酋迪拜","founder":"阿联酋政府","website":"https://www.emirates.com","main_business":["航空运输"],"slogan":"Emirates — 从迪拜飞往全球"},
            {"slug":"singapore-airlines","name":"新加坡航空","name_en":"Singapore Airlines","category":"airline","country":"新加坡","founding_year":1947,"founding_location":"新加坡","founder":"新加坡政府","website":"https://www.singaporeair.com","main_business":["航空运输"],"slogan":"Singapore Airlines — 飞越新高度"},
            {"slug":"qatar-airways","name":"卡塔尔航空","name_en":"Qatar Airways","category":"airline","country":"卡塔尔","founding_year":1993,"founding_location":"卡塔尔多哈","founder":"卡塔尔政府","website":"https://www.qatarairways.com","main_business":["航空运输"],"slogan":"Qatar Airways — 与世界相连"},
            {"slug":"delta-air-lines","name":"达美航空","name_en":"Delta Air Lines","category":"airline","country":"美国","founding_year":1924,"founding_location":"美国佐治亚州亚特兰大","founder":"科尔莱特·E·伍尔曼","website":"https://www.delta.com","main_business":["航空运输"],"slogan":"Delta — 让您以不同方式飞行"},
            {"slug":"american-airlines","name":"美国航空","name_en":"American Airlines","category":"airline","country":"美国","founding_year":1930,"founding_location":"美国得克萨斯州沃斯堡","founder":"合并成立","website":"https://www.aa.com","main_business":["航空运输"],"slogan":"American Airlines — 通往世界的窗口"},
            {"slug":"united-airlines","name":"联合航空","name_en":"United Airlines","category":"airline","country":"美国","founding_year":1926,"founding_location":"美国伊利诺伊州芝加哥","founder":"合并成立","website":"https://www.united.com","main_business":["航空运输"],"slogan":"United — 友好的天空"},
            {"slug":"lufthansa","name":"汉莎航空","name_en":"Lufthansa","category":"airline","country":"德国","founding_year":1953,"founding_location":"德国科隆","founder":"德国政府","website":"https://www.lufthansa.com","main_business":["航空运输"],"slogan":"Lufthansa — 欧洲之翼"},
            {"slug":"british-airways","name":"英国航空","name_en":"British Airways","category":"airline","country":"英国","founding_year":1974,"founding_location":"英国伦敦","founder":"合并成立","website":"https://www.britishairways.com","main_business":["航空运输"],"slogan":"British Airways — 全球最佳航空公司"},
            {"slug":"qantas","name":"澳洲航空","name_en":"Qantas","category":"airline","country":"澳大利亚","founding_year":1920,"founding_location":"澳大利亚昆士兰州","founder":"保罗·麦金尼斯、哈德森·菲什","website":"https://www.qantas.com","main_business":["航空运输"],"slogan":"Qantas — 澳大利亚之魂"},
            {"slug":"air-france","name":"法国航空","name_en":"Air France","category":"airline","country":"法国","founding_year":1933,"founding_location":"法国巴黎","founder":"合并成立","website":"https://www.airfrance.com","main_business":["航空运输"],"slogan":"Air France — 法国优雅"},
            # --- Batch sportswear ---
            {"slug":"puma","name":"彪马","name_en":"Puma","category":"sportswear","country":"德国","founding_year":1948,"founding_location":"德国黑措根奥拉赫","founder":"鲁道夫·达斯勒","website":"https://www.puma.com","main_business":["运动鞋服"],"slogan":"Puma — 全球知名运动品牌"},
            {"slug":"under-armour","name":"安德玛","name_en":"Under Armour","category":"sportswear","country":"美国","founding_year":1996,"founding_location":"美国马里兰州巴尔的摩","founder":"凯文·普兰克","website":"https://www.underarmour.com","main_business":["运动装备"],"slogan":"Under Armour — 全球知名运动品牌"},
            {"slug":"new-balance","name":"新百伦","name_en":"New Balance","category":"sportswear","country":"美国","founding_year":1906,"founding_location":"美国马萨诸塞州波士顿","founder":"威廉·J·赖利","website":"https://www.newbalance.com","main_business":["运动鞋服"],"slogan":"New Balance — 全球知名运动品牌"},
            {"slug":"asics","name":"亚瑟士","name_en":"ASICS","category":"sportswear","country":"日本","founding_year":1949,"founding_location":"日本神户市","founder":"鬼塚喜八郎","website":"https://www.asics.com","main_business":["运动鞋服"],"slogan":"ASICS — 全球知名运动品牌"},
            {"slug":"converse","name":"匡威","name_en":"Converse","category":"sportswear","country":"美国","founding_year":1908,"founding_location":"美国马萨诸塞州马尔登","founder":"马奎斯·M·匡威","website":"https://www.converse.com","main_business":["帆布鞋"],"slogan":"Converse — 全球知名运动品牌"},
            {"slug":"vans","name":"范斯","name_en":"Vans","category":"sportswear","country":"美国","founding_year":1966,"founding_location":"美国加利福尼亚州阿纳海姆","founder":"保罗·范多伦","website":"https://www.vans.com","main_business":["滑板鞋服"],"slogan":"Vans — 全球知名运动品牌"},
            {"slug":"reebok","name":"锐步","name_en":"Reebok","category":"sportswear","country":"英国","founding_year":1958,"founding_location":"英国博尔顿","founder":"约瑟夫·福斯特","website":"https://www.reebok.com","main_business":["运动鞋服"],"slogan":"Reebok — 全球知名运动品牌"},
            {"slug":"north-face","name":"北面","name_en":"The North Face","category":"sportswear","country":"美国","founding_year":1966,"founding_location":"美国加利福尼亚州旧金山","founder":"道格拉斯·汤普金斯","website":"https://www.thenorthface.com","main_business":["户外装备"],"slogan":"The North Face — 全球知名户外品牌"},
            {"slug":"columbia","name":"哥伦比亚","name_en":"Columbia Sportswear","category":"sportswear","country":"美国","founding_year":1938,"founding_location":"美国俄勒冈州波特兰","founder":"保罗·拉莫弗德","website":"https://www.columbia.com","main_business":["户外运动服"],"slogan":"Columbia Sportswear — 全球知名户外品牌"},
            {"slug":"patagonia","name":"巴塔哥尼亚","name_en":"Patagonia","category":"sportswear","country":"美国","founding_year":1973,"founding_location":"美国加利福尼亚州文图拉","founder":"伊冯·乔伊纳德","website":"https://www.patagonia.com","main_business":["户外服装"],"slogan":"Patagonia — 全球知名户外品牌"},
            {"slug":"dominos","name":"达美乐","name_en":"Domino's","category":"food","country":"美国","founding_year":1960,"founding_location":"美国密歇根州伊普西兰蒂","founder":"汤姆·莫纳汉","website":"https://www.dominos.com","main_business":["披萨连锁"],"slogan":"Domino's — 全球知名快餐品牌"},
            # --- Batch cosmetics ---
            {"slug":"loreal","name":"欧莱雅","name_en":"L'Oréal","category":"cosmetics","country":"法国","founding_year":1909,"founding_location":"法国巴黎","founder":"欧仁·舒莱尔","website":"https://www.loreal.com","main_business":["化妆品"],"slogan":"L'Oréal — 全球知名化妆品品牌"},
            {"slug":"estee-lauder","name":"雅诗兰黛","name_en":"Estée Lauder","category":"cosmetics","country":"美国","founding_year":1946,"founding_location":"美国纽约","founder":"雅诗·兰黛","website":"https://www.esteelauder.com","main_business":["高档化妆品"],"slogan":"Estée Lauder — 全球知名化妆品品牌"},
            {"slug":"shiseido","name":"资生堂","name_en":"Shiseido","category":"cosmetics","country":"日本","founding_year":1872,"founding_location":"日本东京","founder":"福原有信","website":"https://www.shiseido.com","main_business":["化妆品"],"slogan":"Shiseido — 全球知名化妆品品牌"},
            {"slug":"chanel-beauty","name":"香奈儿美妆","name_en":"Chanel Beauty","category":"cosmetics","country":"法国","founding_year":1910,"founding_location":"法国巴黎","founder":"可可·香奈儿","website":"https://www.chanel.com","main_business":["美妆香水"],"slogan":"Chanel Beauty — 全球知名化妆品品牌"},
            {"slug":"dior-beauty","name":"迪奥美妆","name_en":"Dior Beauty","category":"cosmetics","country":"法国","founding_year":1946,"founding_location":"法国巴黎","founder":"克里斯汀·迪奥","website":"https://www.dior.com","main_business":["美妆香水"],"slogan":"Dior Beauty — 全球知名化妆品品牌"},
            {"slug":"lancome","name":"兰蔻","name_en":"Lancôme","category":"cosmetics","country":"法国","founding_year":1935,"founding_location":"法国巴黎","founder":"阿曼德·佩蒂让","website":"https://www.lancome.com","main_business":["护肤品"],"slogan":"Lancôme — 全球知名护肤品品牌"},
            {"slug":"clinique","name":"倩碧","name_en":"Clinique","category":"cosmetics","country":"美国","founding_year":1968,"founding_location":"美国纽约","founder":"卡罗尔·菲利普斯","website":"https://www.clinique.com","main_business":["护肤化妆品"],"slogan":"Clinique — 全球知名护肤品牌"},
            {"slug":"mac-cosmetics","name":"M·A·C","name_en":"M·A·C Cosmetics","category":"cosmetics","country":"加拿大","founding_year":1984,"founding_location":"加拿大多伦多","founder":"弗兰克·托斯肯","website":"https://www.maccosmetics.com","main_business":["专业彩妆"],"slogan":"M·A·C — 全球知名彩妆品牌"},
            {"slug":"aveda","name":"艾梵达","name_en":"Aveda","category":"cosmetics","country":"美国","founding_year":1978,"founding_location":"美国明尼苏达州","founder":"霍斯特·M·雷切尔","website":"https://www.aveda.com","main_business":["天然美发产品"],"slogan":"Aveda — 全球知名美发品牌"},
            {"slug":"kiehls","name":"契尔氏","name_en":"Kiehl's","category":"cosmetics","country":"美国","founding_year":1851,"founding_location":"美国纽约","founder":"约翰·基尔","website":"https://www.kiehls.com","main_business":["护肤护发"],"slogan":"Kiehl's — 全球知名护肤品牌"},
        ]
    
    # Filter out already existing brands
    to_add = [b for b in remaining if b['slug'] not in existing_slugs]
    
    if not to_add:
        print("✅ All brands completed! No more to add.")
        # Remove batch file so next run knows we're done
        if os.path.exists(batch_file):
            os.remove(batch_file)
        os.remove(LOCK_FILE)
        sys.exit(0)
    
    # Take next 10
    batch = to_add[:10]
    new_remaining = to_add[10:]
    
    # Save remaining for next run
    if new_remaining:
        # Merge with any brands that were already excluded
        json.dump(new_remaining, open(batch_file, "w"))
    elif os.path.exists(batch_file):
        os.remove(batch_file)
    
    # --- Generate brand pages ---
    added_count = 0
    for b in batch:
        slug = b["slug"]
        name_zh = b["name"]
        name_en = b["name_en"]
        category = b["category"]
        
        # Create brand.json
        brand_json = {
            "slug": slug, "name_en": name_en, "name_zh": name_zh,
            "category": category, "country": b["country"],
            "founder": b["founder"], "year": b["founding_year"],
            "website": b["website"],
            "wikidata_id": "",
            "description_en": f"{name_en} is a global brand founded in {b['founding_year']}.",
            "description_zh": f'{name_zh}（{name_en}）是全球知名品牌，创立于{b["founding_year"]}年。{b.get("slogan") or b.get("description", "")}',
            "languages": {}
        }
        brand_dir = os.path.join(BASE, slug)
        os.makedirs(brand_dir, exist_ok=True)
        json.dump(brand_json, open(os.path.join(brand_dir, "brand.json"), "w"), ensure_ascii=False, indent=2)
        
        # Create index.html using the template from a similar existing brand
        # For simplicity, copy adidas/index.html and do text replacements
        template_dir = os.path.join(BASE, "adidas")
        if os.path.exists(os.path.join(template_dir, "index.html")):
            with open(os.path.join(template_dir, "index.html")) as f:
                template_html = f.read()
            
            # Do replacements
            html = template_html.replace("adidas", slug)
            html = html.replace("阿迪达斯", name_zh)
            html = html.replace("Adidas", name_en)
            html = html.replace('category: "sport"', f'category: "{category}"')
            
            with open(os.path.join(brand_dir, "index.html"), "w") as f:
                f.write(html)
        else:
            print(f"⚠️ No template for {slug}")
            continue
        
        # Add to brands_index.json
        index.append({"slug": slug, "name": name_zh, "name_en": name_en, "category": category})
        
        # Add to master.csv
        with open(os.path.join(BASE, "master.csv"), 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow([slug, name_zh, name_en, category, b.get("founding_location",""), str(b.get("founding_year","")), "TRUE"])
        
        # Add to index.html brandsData
        with open(os.path.join(BASE, "index.html")) as f:
            html_content = f.read()
        
        # Insert new brand entry before the closing ]
        js_obj = f'\n{{name:"{name_zh}",name_en:"{name_en}",slug:"{slug}",category:"{category}",t:2}},'
        
        # Find last brandsData entry
        last_bracket = html_content.rfind("];")
        html_content = html_content[:last_bracket] + js_obj + html_content[last_bracket:]
        
        with open(os.path.join(BASE, "index.html"), "w") as f:
            f.write(html_content)
        
        added_count += 1
        print(f"  ✓ {slug} ({name_zh}) added")
    
    # Save updated index
    json.dump(index, open(os.path.join(BASE, "brands_index.json"), "w"), ensure_ascii=False, indent=2)
    
    # --- Update index.html ---
    with open(os.path.join(BASE, "index.html")) as f:
        html = f.read()
    
    start = html.find("var brandsData = [")
    if start >= 0:
        old_end = html.find("]", start + 18)
        if old_end > 0:
            lines = []
            for b in index:
                t = b.get('t', 1)
                line = '{{name:"{0}",name_en:"{1}",slug:"{2}",category:"{3}",t:{4}}}'.format(b['name'], b['name_en'], b['slug'], b['category'], t)
                lines.append(line)
            new_data = "\n".join(lines)
            before = html[:start + len("var brandsData = [")]
            after = html[old_end + 1:]  # skip ]
            html = before + "\n" + new_data + "\n" + after
            with open(os.path.join(BASE, "index.html"), "w") as f:
                f.write(html)
            print(f"   index.html updated ({len(index)} brands)")
    
    # --- Git push ---
    os.chdir(BASE)
    os.system("git add -A")
    names = ", ".join(b["name_en"] for b in batch)
    os.system(f'git commit -m "batch add {added_count} brands: {names}"')
    os.system("git push")
    
    print(f"\n✅ Heartbeat complete: +{added_count} brands (total: {len(index)})")
    print(f"   Remaining in pool: {len(new_remaining)}")
    
finally:
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
