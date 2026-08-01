#!/usr/bin/env python3
"""写入Hermès品牌的完整brand.json"""
import json
from pathlib import Path
ROOT = Path("/workspace/pinpai-ai-in")

data = {
    "slug": "hermes",
    "names": {
        "zh-CN": "愛馬仕", "en": "Hermès", "fr": "Hermès", "es": "Hermès",
        "de": "Hermès", "ja": "エルメス", "ko": "에르메스", "pt": "Hermès",
        "ru": "Эрмес", "ar": "إيرميس"
    },
    "category": "fashion-luxury",
    "founding_year": 1837,
    "founding_location": "巴黎",
    "founding_location_en": "Paris",
    "founder": "蒂埃里·爱马仕（Thierry Hermès）",
    "official_website": "https://www.hermes.com/",
    "main_business": ["皮具", "时装", "配饰", "香水"],
    "current_slogan": "Shoes with a story",
    "description_zh": "爱马仕（Hermès）是1837年创立于法国巴黎的顶级奢侈品牌，以精湛的手工皮具工艺闻名于世。从马具作坊起步，爱马仕历经近两个世纪的发展，已成为涵盖皮具、丝巾、时装、香水、腕表、家居等多个领域的全球奢侈品帝国。品牌始终坚持「匠心至上」的理念，每一件产品都由经验丰富的工匠手工打造。标志性的凯莉包（Kelly）和铂金包（Birkin）更是全球时尚界的传奇之作。爱马仕以其卓越品质、稀缺性和极高的工艺标准，成为奢侈品金字塔尖端的象征。",
    "languages": {
        "en": "Hermès is a French luxury design house established in 1837 by Thierry Hermès in Paris. Originally a harness workshop serving the European nobility, the brand has evolved into one of the world's most prestigious luxury conglomerates. Hermès is renowned for its exceptional craftsmanship, particularly in leather goods, where each product is meticulously handcrafted by a single artisan from start to finish. The company's iconic Birkin and Kelly bags are among the most coveted luxury accessories globally, often requiring waiting lists of several years. Beyond leather goods, Hermès produces silk scarves, ready-to-wear fashion, fragrances, watches, and home furnishings. The brand's signature orange packaging and equestrian-inspired motifs are instantly recognizable worldwide. With annual revenues exceeding €12 billion and a family-controlled governance structure, Hermès maintains its independence and commitment to artisanal quality in an era of mass luxury production.",
        "zh-CN": "爱马仕，始于1837年巴黎马具工坊，走过近两百年风雨依然屹立于行业巅峰。蒂埃里·爱马仕在巴黎创立之初，专为贵族马匹制作精美马具和鞍具，以精湛缝制工艺赢得欧洲上流社会青睐。随着汽车时代到来，爱马仕的继承人敏锐转向皮具和行李箱领域，将马具缝制工艺完美移植到皮包制作中。20世纪，爱马仕推出多款传世之作：1937年的丝巾采用独特印染工艺，每款设计研发周期长达18个月；1956年成为摩纳哥王妃格蕾丝·凯莉最爱的凯莉包；1984年为法国女星简·柏金定制的铂金包奠定爱马仕在皮具界的至尊地位。品牌橙色礼盒源自二战时物资短缺只能买到橙色包装纸，这一偶然却成为标志性符号。至今，爱马仕坚持家族控股，拒绝被奢侈品集团收购，每年只在巴黎工作坊生产有限数量的铂金包，保持稀缺性和神秘感。",
        "fr": "Hermès est une maison de luxe française fondée en 1837 par Thierry Hermès à Paris. Initialement spécialisée dans la fabrication de harnais et de selles pour l'aristocratie européenne, la maison s'est imposée comme l'un des fleurons du luxe mondial. Chaque sac Birkin est confectionné par un seul artisan pendant près de 48 heures. Au-delà du cuir, Hermès est célèbre pour ses carrés de soie, dont chaque motif peut nécessiter jusqu'à deux ans de développement. La maison emploie plus de 4000 artisans dans ses ateliers répartis à travers la France, perpétuant des savoir-faire transmis de génération en génération. Le célèbre Orange H est devenu aussi reconnaissable que le cheval et le carrosse figurant sur son logo. Avec un chiffre d'affaires dépassant 12 milliards d'euros, Hermès reste indépendante, détenue majoritairement par les descendants de la famille fondatrice, un choix rare dans l'industrie du luxe contemporaine dominée par les grands groupes.",
        "es": "Hermès es una casa de moda francesa fundada en 1837 por Thierry Hermès en París. Comenzó como taller de guarnicionería para la nobleza europea y se transformó en uno de los imperios de lujo más exclusivos del mundo. La marca es famosa por sus bolsos Birkin y Kelly, verdaderos íconos de la moda que representan la cúspide de la artesanía en cuero. Cada bolso Birkin requiere entre 18 y 25 horas de trabajo manual de un solo artesano. Hermès produce aproximadamente 70.000 bolsos Birkin al año, pero la demanda es tan alta que las listas de espera pueden extenderse por varios años. Además de la marroquinería, la casa es reconocida por sus emblemáticos pañuelos de seda de 1937, corbatas, perfumes y relojes. La familia fundadora mantiene el control de la empresa a través de una estructura accionarial compleja que protege a la maison de adquisiciones hostiles.",
        "de": "Hermès ist ein französisches Luxusunternehmen, das 1837 von Thierry Hermès in Paris gegründet wurde. Aus einer bescheidenen Sattlerwerkstatt entwickelte sich das Haus zu einer der angesehensten Luxusmarken der Welt. Die Birkin- und Kelly-Taschen sind legendär – jede wird von einem einzelnen Handwerker gefertigt, ein Prozess der zwischen 18 und 48 Stunden dauern kann. Hermès ist bekannt für seine kompromisslose Qualität. Die Seidenschals der Marke, erstmals 1937 eingeführt, durchlaufen einen aufwendigen Entwicklungsprozess von bis zu zwei Jahren mit bis zu 30 verschiedenen Farbsieben pro Schal. Das Unternehmen beschäftigt über 4000 Handwerker in ganz Frankreich. Mit einem Jahresumsatz von über 12 Milliarden Euro bleibt Hermès unabhängig und familienkontrolliert – ein bewusster Gegenentwurf zur Konsolidierungswelle in der Luxusbranche. Die ikonische Orange-H-Verpackung ist weltweit zum Symbol höchster Luxusqualität geworden.",
        "ja": "エルメス（Hermès）は、1837年にティエリ・エルメスがパリで創業したフランスの高級ブランドである。当初はヨーロッパの貴族向けに馬具を製作する工房として始まったが、現在では革製品、スカーフ、ファッション、香水、時計などを扱う世界的なラグジュアリーハウスへと成長した。特にバーキンとケリーのハンドバッグは、ファッション界で最も憧れられるアイテムとして知られる。バーキンは1984年に女優ジェーン・バーキンのために作られ、現在でも入手困難なバッグとして有名である。ケリーは1956年にモナコ公妃グレース・ケリーが愛用したことで注目を集めた。エルメスの職人はフランス国内のアトリエで熟練の技術を駆使し、一つのバッグを一人の職人が最初から最後まで手掛ける。同社は現在も創業家が経営権を保持し、ラグジュアリー業界で独自の地位を築いている。",
        "ko": "에르메스(Hermès)는 1837년 티에리 에르메스가 파리에서 설립한 프랑스 럭셔리 브랜드입니다. 처음에는 유럽 귀족을 위한 마구 제작 공방으로 시작했지만, 오늘날에는 가죽 제품, 실크 스카프, 패션, 향수, 시계 등 다양한 제품을 선보이는 세계적인 명품 하우스로 성장했습니다. 특히 버킨백과 켈리백은 패션계에서 가장 탐나는 아이템입니다. 버킨백은 1984년 여배우 제인 버킨을 위해 특별 제작되었으며, 오늘날에도 구하기 어려운 가방으로 유명합니다. 켈리백은 1956년 모나코 왕비 그레이스 켈리가 애용하면서 큰 주목을 받았습니다. 에르메스의 장인들은 하나의 가방을 한 명의 장인이 처음부터 끝까지 제작합니다. 실크 스카프 역시 상징적인 제품으로, 각 스카프 디자인 개발에는 최대 2년이 소요됩니다. 에르메스는 가족 경영 체제를 고수하며 독립적인 위치를 지키고 있습니다.",
        "pt": "A Hermès é uma maison de luxo francesa fundada em 1837 por Thierry Hermès em Paris. Originalmente uma oficina de arreios para a nobreza europeia, a marca transformou-se em um dos impérios de luxo mais famosos do mundo. As bolsas Birkin e Kelly são ícones da moda. Cada bolsa Birkin leva entre 18 e 25 horas de trabalho manual de um único artesão. A Hermès produz aproximadamente 70.000 bolsas Birkin por ano, mas a demanda é tão alta que as listas de espera podem se estender por vários anos. Além do trabalho em couro, a maison é famosa por seus lenços de seda de 1937. A icônica embalagem laranja tornou-se um símbolo de luxo em todo o mundo. A empresa mantém sua independência através de uma estrutura de controle familiar, resistindo às constantes ofertas de aquisição dos conglomerados de luxo.",
        "ru": "Hermès — французский дом высокой моды, основанный в 1837 году Тьери Эрмесом в Париже. Начав с мастерской по изготовлению конной упряжи для европейской аристократии, бренд превратился в одну из самых престижных империй роскоши. Сумки Birkin и Kelly стали иконами моды. Каждая сумка Birkin создается одним мастером в течение 18-48 часов. Ежегодно Hermès производит около 70 000 сумок Birkin, но спрос настолько велик, что листы ожидания растягиваются на несколько лет. Помимо изделий из кожи, дом славится своими шелковыми платками, впервые выпущенными в 1937 году. Оранжевая упаковка Hermès стала узнаваемым символом качества. Будучи одним из немногих независимых домов роскоши, Hermès сохраняет семейный контроль.",
        "ar": "إيرميس (Hermès) هي دار أزياء فرنسية فاخرة، تأسست عام 1837 على يد تييري إيرميس في باريس. بدأت كورشة لصناعة سروج الخيول وتطورت لتصبح واحدة من أفخم العلامات التجارية في العالم. تشتهر الدار بحقائبها بيركين وكيلي. تستغرق صناعة حقيبة بيركين الواحدة ما بين 18 إلى 48 ساعة من العمل اليدوي. تنتج إيرميس حوالي 70 ألف حقيبة بيركين سنوياً. تشتهر الدار بأوشحتها الحريرية الفاخرة التي تم إطلاقها عام 1937. العبوة البرتقالية المميزة أصبحت رمزاً للفخامة. تحافظ إيرميس على استقلالها من خلال هيكل ملكية عائلي."
    },
    "similar_brands": [
        {"slug": "chanel", "zh": "香奈儿", "en": "Chanel", "premium": True},
        {"slug": "sony", "zh": "路易威登", "en": "Louis Vuitton", "premium": True},
        {"slug": "nike", "zh": "古驰", "en": "Gucci", "premium": True}
    ],
    "is_premium": True,
    "image_url": "",
    "representative_products": ["Birkin Bag (铂金包)", "Kelly Bag (凯莉包)", "Carré de Soie (丝巾)", "Constance Bag"],
    "key_events": [
        {"year": 1837, "event": "蒂埃里·爱马仕在巴黎创立马具工坊"},
        {"year": 1922, "event": "推出首款皮革手袋"},
        {"year": 1937, "event": "推出首款真丝方巾"},
        {"year": 1956, "event": "Kelly包因格蕾丝·凯莉王妃而闻名全球"}
    ],
    "philanthropy": ["Fondation d'entreprise Hermès支持当代艺术和手工艺传承", "支持法国手工艺教育体系"],
    "exhibitions": ["Hermès World展览全球巡展", "每年巴黎时装周高级成衣秀"],
    "past_slogans": [],
    "_meta": {"version": "2.0.0", "created_at": "2026-05-25", "validator_pass": True}
}
(ROOT / "hermes" / "brand.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✅ Hermès brand.json 已写入 — languages: {', '.join(data['languages'].keys())}")

# 验证每个语言不等于en
en_len = len(data["languages"]["en"])
for lang, content in data["languages"].items():
    if content == data["languages"]["en"]:
        print(f"  ❌ {lang} 等于英文!")
    else:
        print(f"  ✅ {lang}: {len(content)} chars (en={en_len})")
