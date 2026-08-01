# Chanel brand.json 写入
import json
from pathlib import Path

ROOT = Path("/workspace/pinpai-ai-in")

tpl = json.loads((ROOT / "chanel" / "brand.json").read_text())
tpl["names"] = {"zh-CN":"香奈儿","en":"Chanel","fr":"Chanel","es":"Chanel","de":"Chanel","ja":"シャネル","ko":"샤넬","pt":"Chanel","ru":"Chanel","ar":"شانيل"}
tpl["founding_year"] = 1910
tpl["founding_location"] = "巴黎"
tpl["founding_location_en"] = "Paris"
tpl["founder"] = "可可·香奈儿（Coco Chanel）"
tpl["official_website"] = "https://www.chanel.com"
tpl["main_business"] = ["高级时装","香水","化妆品","珠宝","手表"]
tpl["current_slogan"] = "La mode se démode, le style jamais."
tpl["description_zh"] = "香奈儿（Chanel）是法国巴黎创立的顶级奢侈品牌，1910年由可可·香奈儿创立。以经典的小黑裙、Chanel No.5香水、粗花呢套装和2.55手袋闻名。双C标志是全球最知名的奢侈品符号之一。"
tpl["languages"] = {}

tpl["languages"]["en"] = (
    "Chanel is a French luxury fashion house founded in 1910 by Coco Chanel in Paris. "
    "The brand is renowned for its timeless elegance, pioneering the concept of casual chic and the little black dress. "
    "Chanel No. 5 perfume, launched in 1921, remains the most famous fragrance in the world with its distinctive floral aldehyde scent. "
    "The Chanel suit, introduced in the 1920s, revolutionized women's fashion by replacing corseted silhouettes with comfortable, tailored jackets and skirts. "
    "The iconic 2.55 handbag, created in February 1955, features the signature quilted pattern, shoulder chain strap, and the 'Mademoiselle Lock'. "
    "The interlocking double-C logo was created by Coco Chanel herself and has become one of the most recognizable luxury symbols globally. "
    "After Coco Chanel's death in 1971, the brand saw a renaissance under Karl Lagerfeld, who served as creative director from 1983 until his death in 2019. "
    "Lagerfeld modernized the brand while honoring its heritage, introducing the Chanel 19 bag and reinventing the classic tweed jacket. "
    "The brand's haute couture collections are presented during Paris Fashion Week at the Grand Palais. "
    "Chanel's watch division produces the iconic J12 ceramic watches, first introduced in 1999. "
    "The company remains privately held by the Wertheimer family, with annual revenue exceeding $15 billion. "
    "Chanel operates approximately 310 boutiques worldwide across fashion, fragrance, and accessories. "
    "The brand is particularly known for its strict control over distribution and pricing, never discounting products. "
    "Chanel's fine jewelry collections feature the Comète, Coco Crush, and Bijoux de Diamants lines. "
    "The Gabrielle Chanel Fragrance and the Bleu de Chanel for men are among the brand's best-selling scents. "
    "Chanel's Les Exclusifs collection offers 15 rare fragrances crafted by in-house perfumers. "
    "The brand's makeup line is famous for products like Rouge Coco lipstick and Vitalumière foundation. "
    "Chanel's No. 5 L'EAU and Chance perfumes continue the brand's olfactory legacy. "
    "The company employs over 28,000 people worldwide and maintains workshops in Paris for haute couture. "
    "Chanel is one of the most valuable luxury brands globally, consistently ranked in the top 5 by Interbrand. "
    "The brand's commitment to craftsmanship is exemplified by its 40,000-square-foot atelier in Paris. "
    "Chanel acquired 26 luxury fashion-focused suppliers between 2018 and 2023. "
    "The House of Chanel remains a symbol of French luxury and timeless style."
)

tpl["languages"]["zh-CN"] = (
    "香奈儿（Chanel）是1910年由可可·香奈儿在巴黎创立的法国顶级奢侈品牌。"
    "品牌以永恒的优雅著称，率先提出了休闲时髦（casual chic）的概念和小黑裙。"
    "1921年推出的香奈儿No.5香水以其独特的醛花香味成为世界上最著名的香水。"
    "20世纪20年代推出的香奈儿套装用舒适定制的夹克和裙子取代了束腰裙，彻底改变了女性时尚。"
    "标志性的2.55手袋于1955年2月诞生，采用标志性的菱格纹、肩链带和「Mademoiselle Lock」锁扣。"
    "双交C标志由可可·香奈儿本人设计，已成为全球最知名的奢侈品符号之一。"
    "1971年可可·香奈儿去世后，品牌在卡尔·拉格斐的带领下重获新生。"
    "拉格斐自1983年起担任创意总监，直至2019年去世。他在尊重传统的同时现代化了品牌，"
    "推出了Chanel 19手袋并重新诠释了经典的粗花呢夹克。"
    "高级定制系列在巴黎时装周期间于大皇宫发布。"
    "香奈儿手表部门生产标志性的J12陶瓷手表，首款于1999年推出。"
    "公司仍由韦特海默家族私人持有，年收入超过150亿美元。"
    "香奈儿在全球经营约310家精品店，涵盖时装、香水和配饰。"
    "品牌以其对分销和定价的严格控制而闻名，从不打折销售产品。"
    "香奈儿高级珠宝系列包括Comète、Coco Crush和Bijoux de Diamants等系列。"
    "香奈儿拥有28,000多名员工，在巴黎设有高级定制工坊。"
    "品牌对手工艺的承诺体现在其在巴黎40,000平方英尺的定制工坊上。"
    "2018年至2023年间，香奈儿收购了26家奢侈品时尚供应商。"
    "香奈儿仍然象征着法国奢华和永恒风格。"
)

tpl["languages"]["fr"] = (
    "Chanel est une maison de couture française de luxe fondée en 1910 par Coco Chanel à Paris. "
    "La marque est réputée pour son élégance intemporelle et a lancé le concept du chic décontracté et de la petite robe noire. "
    "Le parfum Chanel No. 5, lancé en 1921, reste le parfum le plus célèbre au monde. "
    "Le tailleur Chanel, introduit dans les années 1920, a révolutionné la mode féminine. "
    "Le sac 2.55 emblématique, créé en février 1955, est un incontournable. "
    "Le logo au double C entrelacé est devenu un symbole de luxe mondialement reconnu. "
    "Après la mort de Coco Chanel en 1971, Karl Lagerfeld a revitalisé la marque de 1983 à 2019. "
    "La montre J12 en céramique, lancée en 1999, est une icône de l'horlogerie. "
    "L'entreprise reste détenue par la famille Wertheimer avec un chiffre d'affaires de plus de 15 milliards de dollars. "
    "Chanel ne propose jamais de remises et contrôle strictement sa distribution. "
    "La maison emploie plus de 28 000 personnes dans le monde et possède des ateliers à Paris. "
    "Chanel est l'une des marques de luxe les plus précieuses au monde."
)

tpl["languages"]["es"] = (
    "Chanel es una casa de moda francesa fundada en 1910 por Coco Chanel en París. "
    "La marca es famosa por su elegancia atemporal y por introducir el concepto de chic informal y el vestido negro. "
    "El perfume Chanel No. 5, lanzado en 1921, sigue siendo la fragancia más famosa del mundo. "
    "Chanel revolucionó la moda femenina en los años 1920. "
    "El icónico bolso 2.55, creado en febrero de 1955, es un clásico. "
    "El logotipo de doble C es un símbolo de lujo reconocido mundialmente. "
    "Karl Lagerfeld revitalizó la marca desde 1983 hasta 2019. "
    "El reloj J12 de cerámica, lanzado en 1999, es un icono relojero. "
    "Chanel sigue siendo propiedad de la familia Wertheimer. "
    "La marca nunca ofrece descuentos. Emplea a más de 28.000 personas."
)

tpl["languages"]["de"] = (
    "Chanel ist ein französisches Luxusmodehaus, das 1910 von Coco Chanel in Paris gegründet wurde. "
    "Die Marke ist für ihre zeitlose Eleganz bekannt und hat das Konzept legerer Chic und das kleine Schwarze eingeführt. "
    "Das Parfüm Chanel No. 5, 1921 eingeführt, ist der berühmteste Duft der Welt. "
    "Chanel revolutionierte in den 1920er Jahren die Damenmode. "
    "Die ikonische 2.55-Handtasche, kreiert im Februar 1955, ist ein Klassiker. "
    "Das Doppel-C-Logo ist ein weltweit anerkanntes Luxussymbol. "
    "Karl Lagerfeld belebte die Marke von 1983 bis 2019 neu. "
    "Die J12-Keramikuhr, 1999 eingeführt, ist eine Uhrenikone. "
    "Chanel befindet sich noch immer im Besitz der Familie Wertheimer. "
    "Die Marke gewährt niemals Rabatte. Sie beschäftigt über 28.000 Mitarbeiter."
)

tpl["languages"]["ja"] = (
    "シャネルは1910年にココ・シャネルによってパリで創業されたフランスの高級ファッションブランドである。"
    "時代を超えたエレガンスで知られ、カジュアルシックとリトルブラックドレスの概念を広めた。"
    "1921年に発売されたシャネルNo.5は、世界で最も有名な香水である。"
    "1920年代に発表されたシャネルのスーツは女性ファッションに革命をもたらした。"
    "1955年2月に誕生した2.55バッグはブランドの象徴である。"
    "ダブルCロゴは世界的に認知された高級シンボルである。"
    "カール・ラガーフェルドは1983年から2019年までクリエイティブディレクターを務め、ブランドを活性化した。"
    "1999年発売のJ12セラミックウォッチは時計業界のアイコンである。"
    "シャネルは今もヴェルトハイマー家が所有している。"
    "ブランドは決して割引を行わない。28,000人以上の従業員を擁する。"
)

tpl["languages"]["ko"] = (
    "샤넬은 1910년 코코 샤넬이 파리에서 설립한 프랑스 명품 패션 하우스입니다. "
    "이 브랜드는 시대를 초월한 우아함으로 유명하며 캐주얼 시크와 리틀 블랙 드레스의 개념을 도입했습니다. "
    "1921년 출시된 샤넬 No.5는 세계에서 가장 유명한 향수입니다. "
    "1920년대 샤넬 수트는 여성 패션에 혁명을 일으켰습니다. "
    "1955년 2월에 탄생한 아이코닉 2.55 핸드백은 브랜드의 상징입니다. "
    "더블 C 로고는 세계적으로 인정받는 명품의 상징입니다. "
    "칼 라거펠트는 1983년부터 2019년까지 크리에이티브 디렉터로 활동하며 브랜드를 부활시켰습니다. "
    "1999년 출시된 J12 세라믹 시계는 시계 아이콘입니다. "
    "샤넬은 여전히 베르트하이머 가문이 소유하고 있습니다. "
    "이 브랜드는 절대 할인을 하지 않습니다. 28,000명 이상의 직원을 고용하고 있습니다."
)

tpl["languages"]["pt"] = (
    "Chanel é uma casa de moda francesa fundada em 1910 por Coco Chanel em Paris. "
    "A marca é famosa pela sua elegância intemporal e por introduzir o conceito de chique casual e o vestido preto. "
    "O perfume Chanel No. 5, lançado em 1921, continua a ser a fragrância mais famosa do mundo. "
    "Chanel revolucionou a moda feminina nos anos 1920. "
    "A icónica bolsa 2.55, criada em fevereiro de 1955, é um clássico. "
    "O logótipo de duplo C é um símbolo de luxo reconhecido mundialmente. "
    "Karl Lagerfeld revitalizou a marca de 1983 a 2019. "
    "O relógio J12 de cerâmica, lançado em 1999, é um ícone relojoeiro. "
    "Chanel continua propriedade da família Wertheimer. "
    "A marca nunca oferece descontos. Emprega mais de 28.000 pessoas."
)

tpl["languages"]["ru"] = (
    "Chanel — французский дом высокой моды, основанный в 1910 году Коко Шанель в Париже. "
    "Бренд славится своей вневременной элегантностью и концепцией повседневного шика и маленького черного платья. "
    "Духи Chanel No. 5, выпущенные в 1921 году, остаются самыми известными в мире. "
    "Костюм Chanel произвел революцию в женской моде в 1920-х годах. "
    "Знаменитая сумка 2.55, созданная в феврале 1955 года, является классикой. "
    "Логотип с двойной буквой C — всемирно признанный символ роскоши. "
    "Карл Лагерфельд возродил бренд с 1983 по 2019 год. "
    "Керамические часы J12, выпущенные в 1999 году, стали часовой иконой. "
    "Chanel по-прежнему принадлежит семье Вертхаймеров. "
    "Бренд никогда не предоставляет скидки. В компании работает более 28 000 человек."
)

tpl["languages"]["ar"] = (
    "شانيل هي دار أزياء فرنسية فاخرة أسستها كوكو شانيل في باريس عام 1910. "
    "تشتهر العلامة التجارية بأناقتها الخالدة ومفهوم الأناقة الكاجوال والفستان الأسود القصير. "
    "عطر شانيل نمبر 5، الذي أطلق في عام 1921، يبقى العطر الأكثر شهرة في العالم. "
    "بدلة شانيل أحدثت ثورة في أزياء النساء في عشرينيات القرن العشرين. "
    "حقيبة 2.55 الشهيرة، التي ابتكرت في فبراير 1955، هي من كلاسيكيات الموضة. "
    "شعار CC المزدوج هو رمز فاخر معترف به عالمياً. "
    "كارل لاغرفيلد أعاد إحياء العلامة التجارية من 1983 حتى 2019. "
    "ساعة J12 الخزفية، التي أطلقت في 1999، هي أيقونة في عالم الساعات. "
    "شانيل لا تزال مملوكة لعائلة فيرتهايمر. "
    "العلامة التجارية لا تقدم تخفيضات أبداً. توظف أكثر من 28,000 شخص."
)

(ROOT / "chanel" / "brand.json").write_text(json.dumps(tpl, ensure_ascii=False, indent=2), encoding="utf-8")
print("✅ Chanel brand.json written!")

# 验证
d = json.loads((ROOT / "chanel" / "brand.json").read_text())
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
    print(f"  {'✅' if ok else '❌'} Chanel {lang}: {c} chars (thresh={t}){' =EN!' if eq else ''}")
print(f"Chanel 全部通过: {all_ok}")
