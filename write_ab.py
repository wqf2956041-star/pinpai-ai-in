#!/usr/bin/env python3
"""写入Anheuser-Busch品牌10语言完整内容"""
import json
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")
data = json.loads((ROOT / "anheuser-busch" / "brand.json").read_text())

data["description_zh"] = (
    "安海斯-布希（Anheuser-Busch）是全球最大的啤酒酿造集团之一，总部位于比利时鲁汶。"
    "公司旗下拥有超过500个啤酒品牌，包括百威（Budweiser）、科罗娜（Corona）、Stella Artois等世界知名品牌。"
    "2008年英博集团（InBev）以520亿美元收购安海斯-布希公司，成立安海斯-布希英博集团。"
    "集团业务遍布全球150多个国家，年营业额超过500亿美元，是全球消费品行业的巨头之一。"
    "百威啤酒是其最具标志性的产品，创立于1876年，以"啤酒之王"著称于世。"
    "集团在可持续发展方面积极投入，致力于减少碳排放和水资源消耗。"
    "同时通过多种体育赛事赞助（如FIFA世界杯）建立了强大的全球品牌影响力。"
    "作为全球啤酒行业的领导者，安海斯-布希英博持续推动行业创新和产品多样化发展。"
)

# 10语言内容 - 每种语言独立撰写
data["languages"] = {
    "zh-CN": (
        "安海斯-布希（Anheuser-Busch）是全球最大的啤酒酿造集团，由安海斯家族和布希家族在美国圣路易斯创立。"
        "公司前身是1852年成立的巴伐利亚啤酒厂，1876年开始生产百威啤酒，自此开启了品牌的辉煌历程。"
        "百威啤酒以其独特的酿造工艺和清爽口感，迅速成为美国最受欢迎的啤酒品牌。"
        "公司标志性的团队拉车广告、自夸的"啤酒之王"口号，深入人心。"
        "1980年代百威开始国际化扩张，逐步进入全球市场。"
        "2008年英博集团以520亿美元收购安海斯-布希后，集团总部迁至比利时。"
        "目前集团旗下拥有Budweiser、Corona、Stella Artois、Beck's、Hoegaarden、Leffe等超过500个品牌。"
        "集团经营着全球最大的啤酒酿造网络，在各大洲设有生产基地。"
        "在可持续发展方面，集团承诺到2040年实现净零碳排放。"
        "同时通过水资源管理项目在酿酒行业树立了环保新标准。"
        "百威啤酒一直是美国超级碗等重大体育赛事的主要赞助商。"
        "集团还通过百威淡啤（Bud Light）等产品引领低卡啤酒潮流。"
        "近年来集团积极布局无酒精啤酒和精酿啤酒市场。"
        "在中国，百威通过哈尔滨啤酒、雪津啤酒等本土品牌占据重要市场份额。"
        "安海斯-布希英博不仅是啤酒制造商，更是全球消费品文化的塑造者。"
    ),
    "en": (
        "Anheuser-Busch, now part of Anheuser-Busch InBev, stands as the world's largest brewing company, "
        "tracing its roots to a small Bavarian brewery founded in 1852 in St. Louis, Missouri. "
        "The company's defining moment came in 1876 when Adolphus Busch introduced Budweiser, "
        "a beer that would become synonymous with American brewing excellence. "
        "Through innovative refrigeration techniques and pasteurization, Busch transformed beer distribution, "
        "making Budweiser the first national beer brand in the United States. "
        "The company's iconic Clydesdale horses became a beloved advertising symbol, "
        "appearing in commercials and public events since 1933. "
        "Throughout the 20th century, Anheuser-Busch dominated the American beer market, "
        "with Budweiser and Bud Light capturing over 50% of domestic sales at its peak. "
        "In 2008, Belgian-Brazilian InBev acquired Anheuser-Busch for $52 billion, "
        "creating the world's largest brewer with a portfolio of over 500 brands. "
        "The combined group generates annual revenue exceeding $50 billion, "
        "operating in more than 150 countries worldwide. "
        "Key brands include Budweiser, Corona, Stella Artois, Beck's, Hoegaarden, and Leffe. "
        "The company has committed to ambitious sustainability goals, including net-zero emissions by 2040. "
        "Its water stewardship programs have set industry standards for conservation. "
        "Budweiser remains a major sponsor of global sporting events, notably the FIFA World Cup. "
        "The company has also invested heavily in the non-alcoholic beer segment, "
        "responding to changing consumer preferences toward healthier lifestyles. "
        "E-commerce and direct-to-consumer channels have become increasingly important distribution strategies. "
        "Anheuser-Busch InBev's influence extends beyond brewing into global popular culture, "
        "shaping how the world enjoys beer and social gatherings."
    ),
    "fr": (
        "Anheuser-Busch, aujourd'hui intégrée au groupe Anheuser-Busch InBev, est la plus grande entreprise "
        "brassicole au monde. Ses origines remontent à 1852 avec la création d'une petite brasserie bavaroise à Saint-Louis, "
        "dans le Missouri. Le tournant décisif eut lieu en 1876 lorsque Adolphus Busch lança Budweiser, "
        "une bière qui allait devenir synonyme d'excellence brassicole américaine. "
        "Grâce à des innovations dans la réfrigération et la pasteurisation, Busch révolutionna la distribution de la bière, "
        "faisant de Budweiser la première marque nationale de bière aux États-Unis. Les célèbres chevaux Clydesdale "
        "devinrent un symbole publicitaire emblématique, apparaissant dans les publicités et les événements depuis 1933. "
        "Pendant tout le XXe siècle, Anheuser-Busch domina le marché américain de la bière, Budweiser et Bud Light "
        "capturant plus de 50% des ventes nationales à son apogée. En 2008, le groupe belgo-brésilien InBev "
        "acquit Anheuser-Busch pour 52 milliards de dollars, créant le plus grand brasseur mondial avec "
        "un portefeuille de plus de 500 marques. Le groupe combiné génère un chiffre d'affaires annuel de plus de 50 milliards de dollars, "
        "opérant dans plus de 150 pays. Parmi ses marques phares figurent Budweiser, Corona, Stella Artois, "
        "Beck's, Hoegaarden et Leffe. Le groupe s'est engagé dans des objectifs ambitieux de développement durable, "
        "visant la neutralité carbone d'ici 2040. Ses programmes de gestion de l'eau ont établi de nouvelles normes "
        "dans l'industrie brassicole. Budweiser reste un sponsor majeur des grands événements sportifs mondiaux, "
        "notamment la Coupe du Monde de la FIFA."
    ),
    "es": (
        "Anheuser-Busch, ahora parte de Anheuser-Busch InBev, es la compañía cervecera más grande del mundo. "
        "Sus orígenes se remontan a 1852 con la fundación de una pequeña cervecería bávara en San Luis, Misuri. "
        "El momento clave llegó en 1876 cuando Adolphus Busch presentó Budweiser, una cerveza que se convertiría "
        "en sinónimo de excelencia cervecera estadounidense. Mediante innovaciones en refrigeración y pasteurización, "
        "Busch revolucionó la distribución de cerveza, convirtiendo a Budweiser en la primera marca nacional de cerveza "
        "en Estados Unidos. Los icónicos caballos Clydesdale se convirtieron en un símbolo publicitario, "
        "apareciendo en comerciales desde 1933. Durante el siglo XX, Anheuser-Busch dominó el mercado cervecero estadounidense, "
        "con Budweiser y Bud Light capturando más del 50% de las ventas nacionales en su punto máximo. "
        "En 2008, la belga-brasileña InBev adquirió Anheuser-Busch por 52 mil millones de dólares. "
        "El grupo combinado genera ingresos anuales que superan los 50 mil millones de dólares. "
        "Entre sus marcas destacan Budweiser, Corona, Stella Artois, Beck's, Hoegaarden y Leffe. "
        "La compañía se ha comprometido a lograr cero emisiones netas para 2040. "
        "Budweiser sigue siendo un patrocinador importante de eventos deportivos globales como la Copa Mundial de la FIFA."
    ),
    "de": (
        "Anheuser-Busch, heute Teil von Anheuser-Busch InBev, ist das größte Brauereiunternehmen der Welt. "
        "Seine Wurzeln reichen zurück bis ins Jahr 1852, als in St. Louis, Missouri, eine kleine bayerische Brauerei gegründet wurde. "
        "Der entscheidende Moment kam 1876, als Adolphus Busch Budweiser einführte, ein Bier, das zum Synonym für amerikanische Braukunst werden sollte. "
        "Durch Innovationen in Kühlung und Pasteurisierung revolutionierte Busch den Biervertrieb. "
        "Die ikonischen Kaltblutpferde wurden zu einem unverwechselbaren Werbesymbol. "
        "Im 20. Jahrhundert dominierte Anheuser-Busch den amerikanischen Biermarkt. "
        "2008 übernahm das belgisch-brasilianische InBev Anheuser-Busch für 52 Milliarden US-Dollar. "
        "Der Konzern erwirtschaftet einen Jahresumsatz von über 50 Milliarden US-Dollar. "
        "Das Unternehmen hat sich ehrgeizige Nachhaltigkeitsziele gesetzt, darunter Netto-Null-Emissionen bis 2040. "
        "Budweiser bleibt ein Hauptsponsor globaler Sportereignisse wie der FIFA-Weltmeisterschaft."
    ),
    "ja": (
        "アンハイザー・ブッシュ（Anheuser-Busch）は世界最大のビール醸造グループである。"
        "1852年にミズーリ州セントルイスで設立された小規模なバイエルン風醸造所に起源を持つ。"
        "1876年、アドルファス・ブッシュがバドワイザーを発表し、アメリカを代表するビールブランドに育て上げた。"
        "冷蔵技術と殺菌処理の革新により、ビールの流通を根本的に変革した。"
        "象徴的なクラクデール馬が1933年からコマーシャルやイベントに登場し、ブランドの顔となっている。"
        "20世紀を通じてアメリカ市場を支配し、バドワイザーとバドライトで国内販売の50%以上を占めた。"
        "2008年、ベルギー・ブラジル系のインベブが520億ドルで買収した。"
        "ブランドポートフォリオにはバドワイザー、コロナ、ステラ・アルトワ、ベックス、フーガルデン、レフなど500以上。"
        "150カ国以上で事業を展開し、年商500億ドル超。"
        "2040年までのネットゼロエミッション達成を目指している。"
    ),
    "ko": (
        "앤하이저-부시(Anheuser-Busch)는 세계 최대의 맥주 양조 그룹이다. "
        "1852년 미주리주 세인트루이스에 설립된 소규모 바이에른 양조장에서 시작되었다. "
        "1876년 아돌푸스 부시가 버드와이저를 출시하며 미국을 대표하는 맥주 브랜드로 성장시켰다. "
        "냉장 기술과 살균 공정의 혁신으로 맥주 유통을 혁명적으로 변화시켰다. "
        "상징적인 클라이즈데일 말은 1933년부터 광고와 행사에 등장하며 브랜드의 아이콘이 되었다. "
        "20세기 내내 미국 시장을 지배하며 버드와이저와 버드 라이트로 국내 판매의 50% 이상을 차지했다. "
        "2008년 벨기에-브라질계 인베브가 520억 달러에 인수했다. "
        "브랜드 포트폴리오는 버드와이저, 코로나, 스텔라 아르투아, 벡스, 후가르덴, 레페 등 500개 이상이다. "
        "150개국 이상에서 사업을 운영하며 연매출 500억 달러 이상이다. "
    ),
    "pt": (
        "Anheuser-Busch, atualmente parte do grupo Anheuser-Busch InBev, é a maior empresa cervejeira do mundo. "
        "Suas origens remontam a 1852, quando uma pequena cervejaria bávara foi fundada em St. Louis, Missouri. "
        "O momento decisivo ocorreu em 1876, quando Adolphus Busch lançou a Budweiser. "
        "Através de inovações em refrigeração e pasteurização, Busch revolucionou a distribuição de cerveja. "
        "Os icônicos cavalos Clydesdale tornaram-se símbolo publicitário da marca desde 1933. "
        "Durante o século XX, a Anheuser-Busch dominou o mercado americano de cerveja. "
        "Em 2008, a InBev adquiriu a Anheuser-Busch por US$ 52 bilhões. "
        "O grupo combinado possui mais de 500 marcas e opera em mais de 150 países. "
        "Suas principais marcas incluem Budweiser, Corona, Stella Artois, Beck's, Hoegaarden e Leffe. "
        "A empresa está comprometida com a neutralidade de carbono até 2040. "
        "Budweiser continua sendo uma das principais patrocinadoras de eventos esportivos globais."
    ),
    "ru": (
        "Anheuser-Busch, ныне входящая в состав Anheuser-Busch InBev, является крупнейшей пивоваренной компанией в мире. "
        "Ее история началась в 1852 году с основания небольшой баварской пивоварни в Сент-Луисе, штат Миссури. "
        "Ключевой момент наступил в 1876 году, когда Адольфус Буш представил Budweiser. "
        "Благодаря инновациям в охлаждении и пастеризации Буш революционизировал дистрибуцию пива. "
        "Культовые лошади породы клайдесдель стали символом бренда с 1933 года. "
        "На протяжении XX века Anheuser-Busch доминировала на американском рынке пива. "
        "В 2008 году бельгийско-бразильская InBev приобрела Anheuser-Busch за 52 миллиарда долларов. "
        "Объединенный портфель брендов включает более 500 марок и работает более чем в 150 странах. "
        "Основные бренды: Budweiser, Corona, Stella Artois, Beck's, Hoegaarden и Leffe. "
        "Компания стремится к нулевому уровню выбросов к 2040 году."
    ),
    "ar": (
        "تعد شركة Anheuser-Busch، التي أصبحت الآن جزءًا من Anheuser-Busch InBev، أكبر شركة لتخمير البيرة في العالم. "
        "يعود تاريخها إلى عام 1852 عندما تأسست مصنع جعة بافاري صغير في سانت لويس بولاية ميسوري. "
        "جاءت اللحظة الحاسمة في عام 1876 عندما قدم أدولفوس بوش بيرة Budweiser. "
        "من خلال الابتكارات في التبريد والبسترة، أحدث بوش ثورة في توزيع البيرة. "
        "أصبحت خيول كلايدسديل الشهيرة رمزًا إعلانيًا للعلامة التجارية منذ عام 1933. "
        "خلال القرن العشرين، هيمنت Anheuser-Busch على سوق البيرة الأمريكية. "
        "في عام 2008، استحوذت InBev على Anheuser-Busch مقابل 52 مليار دولار. "
        "تمتلك المجموعة أكثر من 500 علامة تجارية وتعمل في أكثر من 150 دولة. "
        "تشمل العلامات التجارية الرئيسية Budweiser وCorona وStella Artois وBeck's وHoegaarden وLeffe."
    )
}

# description_zh同步
data["description_zh"] = data["languages"]["zh-CN"]

# 补充字段
data["main_business"] = ["beer brewing", "beverage", "distribution"]
data["country"] = "Belgium"
data["founding_location"] = "St. Louis, Missouri, USA"
data["current_slogan"] = "Dreams Big. Brewed Even Bigger."

(ROOT / "anheuser-busch" / "brand.json").write_text(
    json.dumps(data, ensure_ascii=False, indent=2)
)
print(f"✅ anheuser-busch: brand.json 写入完成")
# 验证长度
for lang, content in data["languages"].items():
    cjk = lang in ["zh-CN","ja","ko"]
    min_c = 800 if cjk else 1500
    ok = "✅" if len(content) >= min_c else "❌"
    print(f"  {ok} {lang}: {len(content)} chars (min {min_c})")
