# Nike brand.json 写入
import json
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

# 读模板
tpl = json.loads((ROOT / "nike" / "brand.json").read_text())
tpl["names"] = {"zh-CN":"耐克","en":"Nike","fr":"Nike","es":"Nike","de":"Nike","ja":"ナイキ","ko":"나이키","pt":"Nike","ru":"Nike","ar":"نايك"}
tpl["founding_year"] = 1964
tpl["founding_location"] = "俄勒冈州比弗顿"
tpl["founding_location_en"] = "Beaverton, Oregon"
tpl["founder"] = "比尔·鲍尔曼（Bill Bowerman）、菲尔·奈特（Phil Knight）"
tpl["official_website"] = "https://www.nike.com/"
tpl["main_business"] = ["运动鞋","服装","装备","数字健身"]
tpl["current_slogan"] = "Just Do It"
tpl["description_zh"] = "耐克（Nike）是全球最大的运动鞋和服装制造商，1964年由比尔·鲍尔曼和菲尔·奈特创立。最初名为蓝带体育（Blue Ribbon Sports），1971年更名为Nike，以希腊胜利女神命名。标志性的Swoosh勾勾由波特兰州立大学学生Carolyn Davidson设计。品牌以「Just Do It」口号闻名全球，签约众多顶级运动员。"
tpl["languages"] = {}

# 写英文
tpl["languages"]["en"] = (
    "Nike, Inc. is an American multinational corporation that is the world's largest supplier of athletic shoes and apparel "
    "and a major manufacturer of sports equipment. Founded on January 25, 1964 by Bill Bowerman and Phil Knight as Blue "
    "Ribbon Sports, the company was officially renamed Nike, Inc. on May 30, 1971. The name Nike is taken from the Greek "
    "goddess of victory. The iconic Swoosh logo was designed by Carolyn Davidson, a graphic design student at Portland "
    "State University, for just $35. Nike's signature 'Just Do It' slogan was coined in 1988 and became one of the most "
    "recognizable advertising taglines in history. The Air Max cushioning system, introduced in 1987, revolutionized "
    "athletic footwear with visible air technology. Nike acquired Converse in 2003 and owns the Jordan Brand which "
    "generates over $5 billion annually through the Michael Jordan legacy line. The company sponsors numerous prominent "
    "athletes across sports including basketball legend LeBron James, soccer star Cristiano Ronaldo, tennis champion "
    "Serena Williams, and golfer Tiger Woods. Nike's Innovation Kitchen in Beaverton, Oregon develops cutting-edge "
    "technologies like Flyknit, which creates lightweight, seamless uppers, and Nike Air cushioning systems. "
    "The company's direct-to-consumer business through Nike.com and its app ecosystem has grown significantly. "
    "Nike has faced criticism over labor practices in overseas factories and has implemented sustainability initiatives "
    "including Move to Zero, aiming for zero carbon and zero waste. The company operates approximately 1,000 retail "
    "stores worldwide and employs over 73,000 people. In fiscal year 2023, Nike generated over $51 billion in revenue. "
    "The brand collaborates with high-fashion designers including Virgil Abloh's Off-White and Travis Scott. "
    "Nike's digital transformation through the Nike Training Club and Nike Run Club apps has created a fitness ecosystem. "
    "The company's headquarters, the Nike World Headquarters in Beaverton, spans 400 acres with multiple buildings "
    "named after famous athletes. Nike has been the official uniform provider for the NFL since 2012. "
    "The company's commitment to innovation, athlete endorsement strategy, and powerful marketing have made it "
    "one of the most valuable brands in the world, consistently ranking in the top 20 of Interbrand's Best Global Brands."
)

tpl["languages"]["zh-CN"] = (
    "耐克公司是全球最大的运动鞋和服装供应商，也是重要的运动装备制造商。"
    "1964年1月25日由比尔·鲍尔曼和菲尔·奈特以「蓝带体育」之名创立，"
    "1971年5月30日正式更名为耐克，名字取自希腊胜利女神尼刻。"
    "标志性的Swoosh勾勾标志由波特兰州立大学学生卡罗琳·戴维森设计，报酬仅35美元。"
    "1988年推出的「Just Do It」口号成为历史上最著名的广告语之一。"
    "1987年推出的Air Max气垫系统以可视化气垫技术彻底改变了运动鞋行业。"
    "耐克于2003年收购匡威，并拥有飞人乔丹品牌，该品牌凭借迈克尔·乔丹的传奇产品线年收入超50亿美元。"
    "公司签约众多顶级运动员，包括篮球传奇勒布朗·詹姆斯、足球巨星克里斯蒂亚诺·罗纳尔多、"
    "网球冠军塞雷娜·威廉姆斯和高尔夫球手泰格·伍兹。"
    "耐克位于比弗顿的创新厨房（Innovation Kitchen）开发了Flyknit飞织技术等尖端科技。"
    "公司通过Nike.com和应用生态系统的直接面向消费者的业务大幅增长。"
    "耐克在全球运营约1000家零售店，员工超过7.3万人。2023财年营收超过510亿美元。"
    "耐克与Virgil Abloh的Off-White、Travis Scott等高端设计师合作推出联名系列。"
    "通过Nike Training Club和Nike Run Club等数字应用构建了健身生态系统。"
    "公司总部位于俄勒冈州比弗顿，占地400英亩，多栋建筑以著名运动员命名。"
    "自2012年起，耐克一直是NFL的官方球衣供应商。"
    "耐克对创新的承诺、运动员代言策略和强大的营销使其成为全球最有价值的品牌之一。"
)

tpl["languages"]["fr"] = (
    "Nike, Inc. est une société multinationale américaine, le plus grand fournisseur mondial de chaussures et "
    "vêtements de sport. Fondée le 25 janvier 1964 par Bill Bowerman et Phil Knight sous le nom de Blue Ribbon Sports, "
    "l'entreprise a été renommée Nike, Inc. le 30 mai 1971. Le nom Nike vient de la déesse grecque de la victoire. "
    "Le logo Swoosh a été créé par Carolyn Davidson pour 35 dollars. Le slogan 'Just Do It' est devenu un des plus "
    "célèbres de l'histoire de la publicité. Nike a acquis Converse en 2003 et possède la marque Air Jordan. "
    "L'entreprise sponsorise de nombreux athlètes comme LeBron James, Cristiano Ronaldo et Serena Williams. "
    "Nike emploie plus de 73 000 personnes et a généré plus de 51 milliards de dollars de revenus en 2023. "
    "Le Nike World Headquarters à Beaverton s'étend sur 160 hectares. "
    "Nike est le fournisseur officiel des uniformes de la NFL depuis 2012. "
    "L'engagement envers l'innovation et le marketing puissant font de Nike l'une des marques les plus valorisées."
)

tpl["languages"]["es"] = (
    "Nike, Inc. es una corporación multinacional estadounidense, el mayor proveedor mundial de calzado y "
    "ropa deportiva. Fundada el 25 de enero de 1964 por Bill Bowerman y Phil Knight como Blue Ribbon Sports, "
    "la empresa pasó a llamarse Nike, Inc. el 30 de mayo de 1971. El nombre Nike proviene de la diosa griega "
    "de la victoria. El logo Swoosh fue diseñado por Carolyn Davidson por 35 dólares. El lema 'Just Do It' se "
    "convirtió en uno de los más famosos de la historia publicitaria. Nike adquirió Converse en 2003 y posee "
    "la marca Jordan. La empresa patrocina numerosos atletas como LeBron James y Serena Williams. "
    "Nike emplea a más de 73.000 personas y generó más de 51 mil millones de dólares en ingresos en 2023. "
    "La sede mundial de Nike en Beaverton abarca 160 hectáreas. "
    "Nike es el proveedor oficial de uniformes de la NFL desde 2012."
)

tpl["languages"]["de"] = (
    "Nike, Inc. ist ein amerikanischer multinationaler Konzern, der weltweit größte Anbieter von Sportschuhen "
    "und Sportbekleidung. Gegründet am 25. Januar 1964 von Bill Bowerman und Phil Knight als Blue Ribbon Sports, "
    "wurde das Unternehmen am 30. Mai 1971 in Nike, Inc. umbenannt. Der Name Nike stammt von der griechischen "
    "Siegesgöttin. Das Swoosh-Logo wurde von Carolyn Davidson für 35 Dollar entworfen. Der Slogan 'Just Do It' "
    "wurde zu einem der berühmtesten Werbesprüche. Nike übernahm Converse 2003 und besitzt die Marke Air Jordan. "
    "Das Unternehmen sponsert zahlreiche Athleten wie LeBron James und Serena Williams. "
    "Nike beschäftigt über 73.000 Mitarbeiter und erzielte 2023 Einnahmen von über 51 Milliarden Dollar. "
    "Der Nike-Hauptsitz in Beaverton erstreckt sich über 160 Hektar. "
    "Nike ist seit 2012 offizieller Trikotausrüster der NFL."
)

tpl["languages"]["ja"] = (
    "ナイキ（Nike, Inc.）はアメリカの多国籍企業で、世界最大のスポーツシューズおよびアパレルサプライヤーである。"
    "1964年1月25日にビル・バウワーマンとフィル・ナイトによってブルーリボンスポーツとして設立され、"
    "1971年5月30日に正式にナイキに改名された。社名はギリシャ神話の勝利の女神ニーケーに由来する。"
    "象徴的なスウッシュロゴは、ポートランド州立大学の学生キャロリン・デイビッドソンが35ドルでデザインした。"
    "「Just Do It」スローガンは1988年に生まれ、広告史上最も有名なキャッチフレーズの一つとなった。"
    "2003年にコンバースを買収し、マイケル・ジョーダンのエアジョーダンブランドを所有している。"
    "レブロン・ジェームズやセリーナ・ウィリアムズなど多くのトップアスリートをスポンサーしている。"
    "ナイキは73,000人以上の従業員を抱え、2023年度に510億ドル以上の収益を上げた。"
)

tpl["languages"]["ko"] = (
    "나이키(Nike, Inc.)는 미국의 다국적 기업으로, 세계 최대의 운동화 및 의류 공급업체입니다. "
    "1964년 1월 25일 빌 바워먼과 필 나이트가 블루 리본 스포츠(Blue Ribbon Sports)로 설립했으며, "
    "1971년 5월 30일 공식적으로 나이키로 사명을 변경했습니다. "
    "회사명은 그리스 신화의 승리의 여신 니케(Nike)에서 유래했습니다. "
    "상징적인 스우시 로고는 포틀랜드 주립대 학생 캐롤린 데이비슨이 35달러에 디자인했습니다. "
    "'Just Do It' 슬로건은 1988년에 만들어져 광고 역사상 가장 유명한 태그라인 중 하나가 되었습니다. "
    "2003년 컨버스를 인수했으며 마이클 조던의 에어 조던 브랜드를 소유하고 있습니다. "
    "르브론 제임스와 세리나 윌리엄스 등 많은 최고 운동선수들을 후원하고 있습니다. "
    "나이키는 73,000명 이상의 직원을 고용하고 있으며, 2023 회계연도에 510억 달러 이상의 수익을 창출했습니다."
)

tpl["languages"]["pt"] = (
    "Nike, Inc. é uma corporação multinacional americana, a maior fornecedora mundial de calçados e "
    "vestuário esportivo. Fundada em 25 de janeiro de 1964 por Bill Bowerman e Phil Knight como Blue Ribbon Sports, "
    "a empresa foi renomeada Nike, Inc. em 30 de maio de 1971. O nome Nike vem da deusa grega da vitória. "
    "O logotipo Swoosh foi desenhado por Carolyn Davidson por 35 dólares. O slogan 'Just Do It' tornou-se um dos "
    "mais famosos da história da publicidade. Nike adquiriu a Converse em 2003 e possui a marca Air Jordan. "
    "A empresa patrocina vários atletas como LeBron James e Serena Williams. "
    "Nike emprega mais de 73.000 pessoas e gerou mais de 51 bilhões de dólares em receita em 2023."
)

tpl["languages"]["ru"] = (
    "Nike, Inc. — американская многонациональная корпорация, крупнейший в мире поставщик спортивной обуви "
    "и одежды. Основана 25 января 1964 года Биллом Бауэрманом и Филом Найтом как Blue Ribbon Sports, "
    "компания была переименована в Nike, Inc. 30 мая 1971 года. Название Nike происходит от греческой "
    "богини победы. Логотип Swoosh был создан Кэролин Дэвидсон за 35 долларов. Слоган 'Just Do It' стал "
    "одним из самых известных в истории рекламы. Nike приобрела Converse в 2003 году. "
    "Компания спонсирует многих спортсменов, включая Леброна Джеймса и Серену Уильямс. "
    "В Nike работает более 73 000 человек. В 2023 финансовом году выручка превысила 51 миллиард долларов."
)

tpl["languages"]["ar"] = (
    "نايك إنك هي شركة أمريكية متعددة الجنسيات، وهي أكبر مورد في العالم للأحذية والملابس الرياضية. "
    "تأسست في 25 يناير 1964 على يد بيل باورمان وفيل نايت تحت اسم بلو ريبون سبورتس، "
    "وتم تغيير الاسم إلى نايك إنك في 30 مايو 1971. اسم نايك مأخوذ من إلهة النصر اليونانية. "
    "شعار سووش صممته كارولين ديفيدسون مقابل 35 دولاراً. شعار 'Just Do It' أصبح من أشهر شعارات الإعلان. "
    "استحوذت نايك على كونفيرس في 2003 وتمتلك علامة إير جوردان التجارية. "
    "ترعى الشركة العديد من الرياضيين مثل ليبرون جيمس وسيرينا ويليامز. "
    "توظف نايك أكثر من 73,000 شخص وحققت إيرادات تجاوزت 51 مليار دولار في 2023."
)

(ROOT / "nike" / "brand.json").write_text(json.dumps(tpl, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ Nike brand.json written!")

# 验证
d = json.loads((ROOT / "nike" / "brand.json").read_text())
en = d["languages"]["en"]
cjk = {"zh-CN","ja","ko"}
all_ok = True
for lang, content in d["languages"].items():
    if lang == "en": continue
    c = len(content)
    t = 800 if lang in cjk else 1500
    eq = content == en
    ok = c >= t and not eq
    if not ok: all_ok = False
    print(f"  {'✅' if ok else '❌'} Nike {lang}: {c} chars (thresh={t}){' =EN!' if eq else ''}")
print(f"Nike 全部通过: {all_ok}")
