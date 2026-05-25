#!/usr/bin/env python3
"""
为批次3（科技/运动/食品/潮玩）17个品牌生成品牌描述内容
使用预定义高质量内容，直接写入 brand.json
"""
import json
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

# 品牌内容数据
brand_content = {
    "apple": {
        "names": {"zh-CN": "苹果", "en": "Apple"},
        "founding_year": "1976",
        "founder": "史蒂夫·乔布斯",
        "official_website": "https://www.apple.com/",
        "founding_location": "美国",
        "wikidata_id": "Q312",
        "description_zh": "苹果（Apple Inc.）是全球最具价值的科技公司之一，由史蒂夫·乔布斯、史蒂夫·沃兹尼亚克和罗纳德·韦恩于1976年4月1日在美国加利福尼亚州库比蒂诺创立。苹果以其创新的消费电子产品闻名于世，包括Mac电脑、iPhone智能手机、iPad平板电脑、Apple Watch智能手表和AirPods无线耳机等。苹果的iOS操作系统和macOS系统构建了强大的生态系统，App Store拥有数百万应用。苹果以极简设计、高端定位和卓越用户体验著称，是全球第一家市值突破3万亿美元的公司。",
        "languages": {"en": "Apple Inc. is an American multinational technology company headquartered in Cupertino, California. Founded by Steve Jobs, Steve Wozniak, and Ronald Wayne on April 1, 1976, Apple designs, develops, and sells consumer electronics, computer software, and online services. Known for iconic products like the iPhone, Mac, iPad, and Apple Watch, the company is celebrated for its minimalist design philosophy and seamless ecosystem integration. Apple became the world's first publicly traded company to reach a $3 trillion market capitalization."},
        "similar_brands": [{"zh":"谷歌","en":"Google","slug":"google"},{"zh":"微软","en":"Microsoft","slug":"microsoft"},{"zh":"三星","en":"Samsung","slug":"samsung"},{"zh":"索尼","en":"Sony","slug":"sony"},{"zh":"英伟达","en":"NVIDIA","slug":"nvidia"}]
    },
    "google": {
        "names": {"zh-CN": "谷歌", "en": "Google"},
        "founding_year": "1998",
        "founder": "谢尔盖·布林",
        "official_website": "https://about.google/",
        "founding_location": "美国",
        "wikidata_id": "Q95",
        "description_zh": "Google（谷歌）是全球最大的搜索引擎公司，由拉里·佩奇和谢尔盖·布林于1998年9月4日在美国加利福尼亚州创立。Google的核心产品是搜索引擎，占据全球搜索市场90%以上的份额。此外，Google还拥有YouTube视频平台、Android移动操作系统、Google Maps地图服务、Google Cloud云计算平台等众多产品。Google以「整合全球信息，使人人皆可访问并从中受益」为使命，是Alphabet Inc.的全资子公司，2023年营业收入超过3000亿美元。",
        "languages": {"en": "Google LLC is an American multinational technology company specializing in Internet-related services and products. Founded by Larry Page and Sergey Brin in 1998, Google's search engine is the world's most popular, handling over 90% of global search queries. The company also develops Android, YouTube, Google Maps, Gmail, and Google Cloud. Restructured under Alphabet Inc. in 2015, Google generates over $300 billion in annual revenue primarily through online advertising."},
        "similar_brands": [{"zh":"苹果","en":"Apple","slug":"apple"},{"zh":"微软","en":"Microsoft","slug":"microsoft"},{"zh":"亚马逊","en":"Amazon","slug":"amazon"},{"zh":"三星","en":"Samsung","slug":"samsung"},{"zh":"英伟达","en":"NVIDIA","slug":"nvidia"}]
    },
    "amazon": {
        "names": {"zh-CN": "亚马逊", "en":"Amazon"},
        "founding_year": "1994",
        "founder": "杰夫·贝佐斯",
        "official_website": "https://www.amazon.com/",
        "founding_location": "美国",
        "wikidata_id": "Q3884",
        "description_zh": "Amazon（亚马逊）是全球最大的电子商务和云计算公司，由杰夫·贝佐斯于1994年7月5日在美国华盛顿州西雅图创立。亚马逊最初是一家在线书店，随后迅速扩展成为「万物商店」，涵盖几乎所有品类的商品零售。亚马逊还通过Amazon Web Services（AWS）占据了全球云计算市场近三分之一的份额。此外，亚马逊拥有Kindle电子阅读器、Alexa智能语音助手、Prime Video流媒体等产品线。亚马逊是全球市值最高的公司之一，2023年营收超过5000亿美元。",
        "languages": {"en": "Amazon.com, Inc. is an American multinational technology company focused on e-commerce, cloud computing, digital streaming, and artificial intelligence. Founded by Jeff Bezos in 1994, Amazon started as an online bookstore and rapidly expanded into the world's largest online retailer. Its cloud computing division, Amazon Web Services (AWS), is a leading provider of cloud infrastructure. Amazon also produces Kindle e-readers, Echo smart speakers with Alexa, and Prime Video streaming service."},
        "similar_brands": [{"zh":"苹果","en":"Apple","slug":"apple"},{"zh":"谷歌","en":"Google","slug":"google"},{"zh":"微软","en":"Microsoft","slug":"microsoft"},{"zh":"三星","en":"Samsung","slug":"samsung"}]
    },
    "samsung": {
        "names": {"zh-CN":"三星","en":"Samsung"},
        "founding_year": "1938",
        "founder": "李秉喆",
        "official_website": "https://www.samsung.com/",
        "founding_location": "韩国",
        "wikidata_id": "Q20716",
        "description_zh": "三星集团（Samsung Group）是韩国最大的跨国企业集团，由李秉喆于1938年创立于韩国大邱。三星最初是一家贸易公司，历经八十余年发展，已成为涵盖电子、金融、重工业、建筑、生物制药等领域的庞大商业帝国。三星电子是其核心子公司，是全球最大的智能手机制造商、半导体制造商和电视机制造商。三星在存储芯片、OLED显示屏等领域占据全球领先地位，2023年集团营收超过2000亿美元。",
        "languages": {"en": "Samsung Group is a South Korean multinational conglomerate headquartered in Samsung Town, Seoul. Founded by Lee Byung-chul in 1938 as a trading company, Samsung has grown into one of the world's largest companies. Samsung Electronics, the flagship division, is the world's largest manufacturer of smartphones, memory chips, and TVs. The group also encompasses shipbuilding, construction, insurance, and biotechnology sectors."},
        "similar_brands": [{"zh":"苹果","en":"Apple","slug":"apple"},{"zh":"谷歌","en":"Google","slug":"google"},{"zh":"索尼","en":"Sony","slug":"sony"},{"zh":"华为","en":"Huawei","slug":"huawei"}]
    },
    "huawei": {
        "names": {"zh-CN":"华为","en":"Huawei"},
        "founding_year": "1987",
        "founder": "任正非",
        "official_website": "https://www.huawei.com/",
        "founding_location": "中国",
        "wikidata_id": "Q160120",
        "description_zh": "华为（Huawei Technologies Co., Ltd.）是全球领先的信息与通信技术（ICT）基础设施和智能终端提供商，由任正非于1987年创立于中国深圳。华为是全球最大的电信设备制造商，在5G技术领域拥有最多的核心专利。华为的消费者业务包括华为手机、平板、PC和可穿戴设备，曾经是全球第二大智能手机制造商。华为还提供云计算、人工智能、智能汽车解决方案等业务，2023年营收超过7000亿元人民币。",
        "languages": {"en": "Huawei Technologies Co., Ltd. is a Chinese multinational technology corporation headquartered in Shenzhen. Founded by Ren Zhengfei in 1987, Huawei is the world's largest telecommunications equipment manufacturer and a leading provider of ICT infrastructure and smart devices. The company holds the largest number of 5G essential patents globally. Despite facing international trade restrictions, Huawei continues to innovate in smartphones, cloud computing, AI, and automotive solutions."},
        "similar_brands": [{"zh":"三星","en":"Samsung","slug":"samsung"},{"zh":"小米","en":"Xiaomi"},{"zh":"苹果","en":"Apple","slug":"apple"},{"zh":"索尼","en":"Sony","slug":"sony"}]
    },
    "sony": {
        "names": {"zh-CN":"索尼","en":"Sony"},
        "founding_year": "1946",
        "founder": "井深大",
        "official_website": "https://www.sony.com/",
        "founding_location": "日本",
        "wikidata_id": "Q41187",
        "description_zh": "索尼集团（Sony Group Corporation）是日本最具代表性的跨国综合电子娱乐企业，由井深大和盛田昭夫于1946年5月7日在东京创立，最初名为东京通信工业株式会社。索尼以随身听Walkman、PlayStation游戏机、Bravia电视、Alpha微单相机等标志性产品闻名世界。索尼是全球最大的游戏和音乐娱乐公司之一，旗下PlayStation是全球最畅销的游戏主机之一。此外，索尼在影视制作、半导体图像传感器等领域也占据领先地位。",
        "languages": {"en": "Sony Group Corporation is a Japanese multinational conglomerate headquartered in Tokyo. Founded by Masaru Ibuka and Akio Morita in 1946 as Tokyo Tsushin Kogyo, Sony became a global electronics icon with products like the Walkman, PlayStation, Bravia TV, and Alpha cameras. Today, Sony is one of the world's largest entertainment companies, encompassing gaming (PlayStation), music (Sony Music), film (Sony Pictures), and imaging sensors for smartphones."},
        "similar_brands": [{"zh":"三星","en":"Samsung","slug":"samsung"},{"zh":"苹果","en":"Apple","slug":"apple"},{"zh":"华为","en":"Huawei","slug":"huawei"},{"zh":"英伟达","en":"NVIDIA","slug":"nvidia"}]
    },
    "nvidia": {
        "names": {"zh-CN":"英伟达","en":"NVIDIA"},
        "founding_year": "1993",
        "founder": "黄仁勋",
        "official_website": "https://www.nvidia.com/",
        "founding_location": "美国",
        "wikidata_id": "Q182477",
        "description_zh": "NVIDIA（英伟达）是全球领先的图形处理器（GPU）和人工智能计算公司，由黄仁勋、克里斯·马拉科夫斯基和柯蒂斯·普里姆于1993年4月在美国加利福尼亚州圣克拉拉创立。NVIDIA的GeForce系列显卡是全球游戏玩家的首选，而其Tesla/Ampere/Hopper系列的AI加速芯片则在数据中心和人工智能领域占据绝对主导地位。NVIDIA的CUDA并行计算平台已成为AI训练和推理的事实标准。2024年，NVIDIA成为全球市值最高的半导体公司。",
        "languages": {"en": "NVIDIA Corporation is an American multinational technology company headquartered in Santa Clara, California. Founded by Jensen Huang, Chris Malachowsky, and Curtis Priem in 1993, NVIDIA is the world's leading designer of graphics processing units (GPUs) for gaming, professional visualization, and artificial intelligence. Its CUDA platform has become the industry standard for GPU-accelerated computing, powering most AI training workloads. NVIDIA's data center GPU business has grown explosively with the AI boom."},
        "similar_brands": [{"zh":"苹果","en":"Apple","slug":"apple"},{"zh":"微软","en":"Microsoft","slug":"microsoft"},{"zh":"谷歌","en":"Google","slug":"google"},{"zh":"亚马逊","en":"Amazon","slug":"amazon"},{"zh":"索尼","en":"Sony","slug":"sony"}]
    },
    "nike": {
        "names": {"zh-CN":"耐克","en":"Nike"},
        "founding_year": "1964",
        "founder": "菲尔·奈特",
        "official_website": "https://www.nike.com/",
        "founding_location": "美国",
        "wikidata_id": "Q218202",
        "description_zh": "耐克（Nike, Inc.）是全球最大的运动服饰和鞋类制造商，由菲尔·奈特和比尔·鲍尔曼于1964年创立，最初名为Blue Ribbon Sports，1971年更名为Nike。耐克以其标志性的Swoosh勾形标志和「Just Do It」口号闻名于世。耐克签约了包括迈克尔·乔丹、勒布朗·詹姆斯、克里斯蒂亚诺·罗纳尔多在内的众多顶级运动员，Air Jordan系列是全球最畅销的运动鞋品牌之一。耐克2023财年营收超过510亿美元，在全球拥有超过7万名员工。",
        "languages": {"en": "Nike, Inc. is an American multinational corporation that designs, develops, and sells athletic footwear, apparel, equipment, accessories, and services. Founded by Bill Bowerman and Phil Knight in 1964 as Blue Ribbon Sports, the company was renamed Nike in 1971 after the Greek goddess of victory. Famous for its Swoosh logo and 'Just Do It' slogan, Nike is the world's largest supplier of athletic shoes and apparel. The Air Jordan brand, born from Michael Jordan's signature line, remains an iconic cultural phenomenon."},
        "similar_brands": [{"zh":"阿迪达斯","en":"Adidas","slug":"adidas"},{"zh":"彪马","en":"Puma","slug":"puma"},{"zh":"安德玛"},{"zh":"新百伦"}]
    },
    "adidas": {
        "names": {"zh-CN":"阿迪达斯","en":"Adidas"},
        "founding_year": "1949",
        "founder": "阿道夫·达斯勒",
        "official_website": "https://www.adidas.com/",
        "founding_location": "德国",
        "wikidata_id": "Q3895",
        "description_zh": "阿迪达斯（Adidas AG）是德国著名的运动用品制造商，由阿道夫·「阿迪」·达斯勒于1949年在德国黑措根奥拉赫创立。阿迪达斯以其三条纹标志闻名全球，是全球第二大运动品牌。阿迪达斯的产品线覆盖足球、篮球、跑步、训练、时尚生活等多个领域。品牌历史上最著名的产品包括Stan Smith网球鞋、Superstar贝壳头鞋、Ultraboost跑鞋等。阿迪达斯通过与Kanye West合作的Yeezy系列和与众多设计师的联名，成功打入高端时尚市场。",
        "languages": {"en": "Adidas AG is a German multinational corporation that designs and manufactures athletic and casual footwear, apparel, and accessories. Founded by Adolf 'Adi' Dassler in 1949 in Herzogenaurach, Germany, Adidas is the largest sportswear manufacturer in Europe and the second-largest globally. Known for its three-stripe logo, Adidas produces iconic products like the Stan Smith, Superstar, and Ultraboost. The company has successfully bridged sportswear and high fashion through collaborations with designers like Yohji Yamamoto and Kanye West."},
        "similar_brands": [{"zh":"耐克","en":"Nike","slug":"nike"},{"zh":"彪马","en":"Puma","slug":"puma"},{"zh":"汤米·希尔费格","en":"Tommy Hilfiger","slug":"tommy-hilfiger"},{"zh":"卡尔文·克莱因","en":"Calvin Klein","slug":"calvin-klein"}]
    },
    "puma": {
        "names": {"zh-CN":"彪马","en":"Puma"},
        "founding_year": "1948",
        "founder": "鲁道夫·达斯勒",
        "official_website": "https://www.puma.com/",
        "founding_location": "德国",
        "wikidata_id": "Q1572564",
        "description_zh": "彪马（Puma SE）是德国知名的运动用品品牌，由鲁道夫·达斯勒于1948年在德国黑措根奥拉赫创立。彪马与阿迪达斯同源于达斯勒家族，鲁道夫与弟弟阿道夫分家后创立了彪马。彪马以其标志性的美洲狮跳跃标志和Formstrip条纹设计著称。彪马在足球、跑步、赛车运动领域拥有深厚传统，签约了包括内马尔、刘易斯·汉密尔顿、尤塞恩·博尔特在内的众多顶级运动员。彪马近年来通过与Rihanna、Selena Gomez等明星合作，成功提升了时尚影响力。",
        "languages": {"en": "Puma SE is a German multinational corporation that designs and manufactures athletic and casual footwear, apparel, and accessories. Founded by Rudolf Dassler in 1948, Puma originated from the same family business that also spawned Adidas. Known for its leaping cat logo and Formstrip design, Puma has strong roots in football, running, and motorsports. The brand has signed legendary athletes including Pelé, Usain Bolt, Lewis Hamilton, and Neymar. In recent years, Puma has strengthened its fashion credentials through partnerships with Rihanna and Selena Gomez."},
        "similar_brands": [{"zh":"阿迪达斯","en":"Adidas","slug":"adidas"},{"zh":"耐克","en":"Nike","slug":"nike"},{"zh":"锐步"}]
    },
    "coca-cola": {
        "names": {"zh-CN":"可口可乐","en":"Coca-Cola"},
        "founding_year": "1886",
        "founder": "约翰·彭伯顿",
        "official_website": "https://www.coca-cola.com/",
        "founding_location": "美国",
        "wikidata_id": "Q2813",
        "description_zh": "可口可乐（The Coca-Cola Company）是全球最大的饮料公司，由药剂师约翰·斯蒂斯·彭伯顿于1886年在佐治亚州亚特兰大创立。可口可乐的配方由彭伯顿发明，最初作为一种药用饮品在雅各布斯药房出售。可口可乐的标志性弧形瓶身设计于1915年推出，成为全球最知名的包装设计之一。可口可乐公司旗下拥有超过500个品牌，包括雪碧、芬达、健怡可乐、零度可乐等。可口可乐产品在200多个国家和地区销售，日均消费量超过19亿杯。",
        "languages": {"en": "The Coca-Cola Company is an American multinational beverage corporation headquartered in Atlanta, Georgia. Invented by pharmacist John Stith Pemberton in 1886, Coca-Cola is the world's most recognized soft drink brand. The company's iconic contour bottle was introduced in 1915. Coca-Cola owns over 500 brands including Sprite, Fanta, Diet Coke, and Coke Zero. The company operates in more than 200 countries and serves over 1.9 billion servings daily. Coca-Cola's marketing campaigns, including the iconic Santa Claus imagery, have shaped modern advertising."},
        "similar_brands": [{"zh":"百事可乐"},{"zh":"星巴克","en":"Starbucks","slug":"starbucks"},{"zh":"麦当劳","en":"McDonald's","slug":"mcdonald-s"}]
    },
    "mcdonald-s": {
        "names": {"zh-CN":"麦当劳","en":"McDonald's"},
        "founding_year": "1955",
        "founder": "雷·克洛克",
        "official_website": "https://www.mcdonalds.com/",
        "founding_location": "美国",
        "wikidata_id": "Q38076",
        "description_zh": "麦当劳（McDonald's Corporation）是全球最大的快餐连锁企业，由雷·克洛克于1955年在美国伊利诺伊州创立。麦当劳最初由理查德和莫里斯·麦克唐纳兄弟于1940年创立，雷·克洛克将之发展为全球连锁帝国。麦当劳以其「金拱门」标志闻名于世，是全球最具辨识度的品牌之一。核心产品包括巨无霸汉堡、薯条、麦乐鸡、开心乐园餐等。麦当劳在全球100多个国家和地区拥有超过3.8万家餐厅，日均服务约6900万名顾客。",
        "languages": {"en": "McDonald's Corporation is an American multinational fast food chain, the world's largest by revenue. Founded by Ray Kroc in 1955 after acquiring the original McDonald's brothers' restaurant in San Bernardino, California. Golden Arches is one of the most recognized symbols globally. McDonald's serves iconic items including the Big Mac, Chicken McNuggets, French Fries, and Happy Meals. With over 38,000 locations in more than 100 countries, McDonald's serves approximately 69 million customers daily."},
        "similar_brands": [{"zh":"星巴克","en":"Starbucks","slug":"starbucks"},{"zh":"可口可乐","en":"Coca-Cola","slug":"coca-cola"},{"zh":"汉堡王"},{"zh":"肯德基"}]
    },
    "starbucks": {
        "names": {"zh-CN":"星巴克","en":"Starbucks"},
        "founding_year": "1971",
        "founder": "霍华德·舒尔茨",
        "official_website": "https://www.starbucks.com/",
        "founding_location": "美国",
        "wikidata_id": "Q37158",
        "description_zh": "星巴克（Starbucks Corporation）是全球最大的咖啡连锁品牌，由杰瑞·鲍德温、泽夫·西格尔和戈登·鲍克于1971年在美国华盛顿州西雅图创立。星巴克最初是一家高档咖啡豆零售商，1987年在霍华德·舒尔茨的领导下转型为意式咖啡连锁店。星巴克以其绿色美人鱼标志闻名，在全球80多个市场拥有超过3.5万家门店。星巴克不仅是咖啡店，更创造了「第三空间」概念——除了家和工作场所之外的生活空间。星巴克的南瓜拿铁、星冰乐等季节限定产品深受消费者喜爱。",
        "languages": {"en": "Starbucks Corporation is an American multinational chain of coffeehouses and roastery reserves headquartered in Seattle, Washington. Founded in 1971 by Jerry Baldwin, Zev Siegl, and Gordon Bowker, Starbucks was transformed into a global coffeehouse phenomenon by Howard Schultz. The Siren logo is recognized worldwide across over 35,000 locations in 80+ markets. Starbucks pioneered the 'third place' concept — a comfortable space between home and work. Seasonal offerings like the Pumpkin Spice Latte have achieved cult status."},
        "similar_brands": [{"zh":"麦当劳","en":"McDonald's","slug":"mcdonald-s"},{"zh":"可口可乐","en":"Coca-Cola","slug":"coca-cola"},{"zh":"瑞幸咖啡"}]
    },
    "lego": {
        "names": {"zh-CN":"乐高","en":"LEGO"},
        "founding_year": "1932",
        "founder": "奥勒·基尔克·克里斯蒂安森",
        "official_website": "https://www.lego.com/",
        "founding_location": "丹麦",
        "wikidata_id": "Q8957",
        "description_zh": "乐高（LEGO）是全球最大的玩具制造商之一，由奥勒·基尔克·克里斯蒂安森于1932年在丹麦比隆创立。公司名LEGO源自丹麦语「leg godt」，意为「玩得好」。乐高最著名的产品是带有凸起圆点的塑料积木系统，1949年首次推出，1958年获得专利。乐高积木的独特之处在于任意两块积木都可以完美拼接，创造了无限可能的建筑世界。乐高业务涵盖玩具制造、主题公园（乐高乐园）、电影制作（《乐高大电影》系列）、电子游戏等多个领域。",
        "languages": {"en": "LEGO Group is a Danish family-owned toy company founded by Ole Kirk Christiansen in 1932 in Billund, Denmark. The name LEGO is a contraction of the Danish phrase 'leg godt' meaning 'play well'. The iconic interlocking plastic brick system was introduced in 1949 and patented in 1958. The unique clutch power system makes each brick compatible with every other brick ever produced. LEGO has expanded into themed sets, video games, movies (The LEGO Movie franchise), and amusement parks (LEGOLAND)."},
        "similar_brands": [{"zh":"美泰","en":"Mattel","slug":"mattel"},{"zh":"万代南梦宫"},{"zh":"孩之宝"}]
    },
    "mattel": {
        "names": {"zh-CN":"美泰","en":"Mattel"},
        "founding_year": "1945",
        "founder": "哈罗德·马特森",
        "official_website": "https://www.mattel.com/",
        "founding_location": "美国",
        "wikidata_id": "Q596139",
        "description_zh": "美泰（Mattel, Inc.）是全球最大的玩具公司之一，由哈罗德·「马特」·马特森和艾略特·汉德勒于1945年在美国加利福尼亚州创立。美泰最著名的产品是芭比娃娃（Barbie），由露丝·汉德勒于1959年创造，至今仍是全球最畅销的时尚玩偶品牌。美泰还拥有风火轮（Hot Wheels）小汽车、费雪（Fisher-Price）婴幼儿玩具、美国女孩（American Girl）玩偶、UNO纸牌等众多知名品牌。2023年，随着《芭比》真人电影全球票房突破14亿美元，美泰品牌影响力达到新高峰。",
        "languages": {"en": "Mattel, Inc. is an American multinational toy manufacturing company founded in 1945 by Harold 'Matt' Matson and Elliot Handler in El Segundo, California. Mattel is best known as the creator of Barbie (1959), the world's most famous fashion doll, and Hot Wheels die-cast cars (1968). The company also owns Fisher-Price, American Girl, UNO, and MEGA Brands. The 2023 'Barbie' feature film, which grossed over $1.4 billion globally, dramatically boosted Mattel's brand visibility and cultural relevance."},
        "similar_brands": [{"zh":"乐高","en":"LEGO","slug":"lego"},{"zh":"孩之宝"},{"zh":"万代南梦宫"}]
    },
    "coach": {
        "names": {"zh-CN":"蔻驰","en":"Coach"},
        "founding_year": "1941",
        "founder": "Lillian 和 Miles Cahn",
        "official_website": "https://www.coach.com/",
        "founding_location": "美国",
        "wikidata_id": "Q514378",
        "description_zh": "蔻驰（Coach, Inc.）是源自美国纽约的全球知名奢华时尚品牌，由Lillian和Miles Cahn于1941年在曼哈顿创立，最初是一家小型皮具作坊。Coach以优质皮革手袋闻名，其设计融合了美式实用主义与高端时尚感。品牌经典产品包括Willow手袋、Tabby肩包、Rogue系列等。Coach以其标志性的C字印花和马车标志著称，定位于「触手可及的奢华」——比顶级奢侈品牌价格更亲民，但品质毫不妥协。Coach母公司Tapestry, Inc.也是Kate Spade和Stuart Weitzman的母公司。",
        "languages": {"en": "Coach, Inc. is an American luxury fashion house founded in 1941 in New York City. Known for its quality leather goods, Coach occupies the 'accessible luxury' segment — offering premium handbags, wallets, and accessories at more approachable price points than top-tier European luxury houses. Signature products include the Willow bag, Tabby shoulder bag, and Rogue collection. Coach is recognizable by its 'C' monogram print and horse-and-carriage logo. The brand is owned by Tapestry, Inc., which also owns Kate Spade and Stuart Weitzman."},
        "similar_brands": [{"zh":"汤米·希尔费格","en":"Tommy Hilfiger","slug":"tommy-hilfiger"},{"zh":"拉尔夫·劳伦","en":"Ralph Lauren","slug":"ralph-lauren"},{"zh":"卡尔文·克莱因","en":"Calvin Klein","slug":"calvin-klein"},{"zh":"迈克·科尔斯"}]
    },
    "microsoft": {
        "names": {"zh-CN":"微软","en":"Microsoft"},
        "founding_year": "1975",
        "founder": "比尔·盖茨",
        "official_website": "https://www.microsoft.com/",
        "founding_location": "美国",
        "wikidata_id": "Q2283",
        "description_zh": "微软（Microsoft Corporation）是全球最大的软件公司之一，由比尔·盖茨和保罗·艾伦于1975年4月4日在美国新墨西哥州阿尔伯克基创立。微软的Windows操作系统是全球使用最广泛的电脑操作系统，Office办公套件是全球企业和个人办公的标准工具。微软还通过Xbox品牌在游戏领域占据重要地位，通过Azure云计算平台成为全球第二大云服务提供商。2023年，微软对OpenAI的投资使其在人工智能革命中占据了领先地位。",
        "languages": {"en": "Microsoft Corporation is an American multinational technology corporation founded by Bill Gates and Paul Allen on April 4, 1975 in Albuquerque, New Mexico. Microsoft's Windows operating system dominates the PC market, and its Office productivity suite is the global standard for business software. The company also leads in gaming with Xbox, cloud computing with Azure (the world's second-largest cloud platform), and professional networking through LinkedIn. In 2023, Microsoft's strategic investment in OpenAI positioned it at the forefront of the AI revolution."},
        "similar_brands": [{"zh":"苹果","en":"Apple","slug":"apple"},{"zh":"谷歌","en":"Google","slug":"google"},{"zh":"亚马逊","en":"Amazon","slug":"amazon"},{"zh":"英伟达","en":"NVIDIA","slug":"nvidia"}]
    }
}

# Apply to brand.json files
for slug, content in brand_content.items():
    bj = ROOT / slug / 'brand.json'
    if not bj.exists():
        print(f"❌ {slug}: brand.json not found")
        continue
    
    data = json.loads(bj.read_text(encoding='utf-8'))
    
    # Update all fields
    for key, value in content.items():
        if key in ('names', 'languages', 'similar_brands'):
            data[key] = value
        elif key == 'description_zh':
            data['description_zh'] = value
        elif value:  # only overwrite if we have a value
            data[key] = value
    
    # Write back
    bj.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ {slug}: content written")

    # Validate
    try:
        json.loads(bj.read_text(encoding='utf-8'))
        print(f"   ✓ valid JSON")
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON error: {e}")

print("\n✅ Batch 3 complete! 17 brands written.")
