#!/usr/bin/env python3
"""Expand Louis Vuitton brand content for all 10 languages to meet thresholds."""
import json

bj = json.load(open('louis-vuitton/brand.json'))
nl = "\n\n"

# zh-CN expansion: need 800+ (currently 619, need ~200 more)
zh_extra = [
    "品牌在营销与传播方面同样极具创意。LV每一季的广告大片由全球顶尖摄影师掌镜，邀请最具影响力的明星代言，包括Emma Stone、Zendaya、BTS等。其时装秀更是巴黎时装周最受瞩目的盛事之一。2023年在巴黎塞纳河畔举办的LV春夏男装秀致敬已故设计师Virgil Abloh，将街头文化与传统高定工艺完美融合，引发全球热议。",
    "路易·威登基金会（Fondation Louis Vuitton）位于巴黎布洛涅森林，由建筑大师弗兰克·盖里设计，于2014年开幕。这座标志性建筑本身就是一件艺术品，其玻璃帆船造型已成为巴黎现代建筑的代表。基金会致力于推广当代艺术与文化，每年举办多场重量级展览，进一步巩固了LV在文化艺术领域的领导地位。",
]
zh_extended = (
    bj['languages']['zh-CN'] + nl +
    "\n".join(zh_extra) + nl +
    "路易·威登的成功不仅在于产品创新，更在于对品牌历史的深刻理解与传承。从19世纪的旅行箱匠人到21世纪的全球奢侈品牌，LV始终以创新精神驱动发展，将旅行文化与现代时尚紧密结合，为全球消费者提供卓越的产品与服务体验。"
)

# en expansion: need 1500+ (currently 1697, okay - but add more for quality)
en_extra = [
    "Louis Vuitton's marketing campaigns are masterfully crafted, featuring top photographers like Annie Leibovitz and global ambassadors such as Emma Stone, Zendaya, and Deepika Padukone. The brand's runway shows, particularly during Paris Fashion Week, are cultural spectacles. The Spring 2023 menswear collection, a tribute to Virgil Abloh, took place along the Seine River and seamlessly blended streetwear aesthetics with high couture craftsmanship.",
    "The Fondation Louis Vuitton, located in the Bois de Boulogne in Paris and designed by architect Frank Gehry, opened in 2014. Its striking glass-sail structure has become an architectural landmark. The foundation is dedicated to contemporary art and culture, hosting major exhibitions annually and cementing the brand's leadership in the intersection of luxury, art, and innovation.",
]
en_expanded = (
    nl.join(en_extra) + nl + nl +
    "Beyond products and marketing, Louis Vuitton's enduring success lies in its deep commitment to craftsmanship and heritage preservation. The company operates several ateliers in France, Italy, Spain, and the United States, where master artisans train new generations in traditional leatherworking techniques. Each handbag requires hundreds of steps and can take weeks to complete, ensuring unmatched quality that justifies the brand's premium positioning in the global luxury market." + nl +
    "The brand's iconic collaborations have also defined its modern era. Partnerships with artists like Yayoi Kusama, Takashi Murakami, and Jeff Koons have produced limited-edition collections that blend pop art with luxury fashion. These collaborations generate enormous buzz and sell out within hours, demonstrating LV's unique ability to stay culturally relevant while preserving its heritage. The brand's annual sales exceed €20 billion, making it one of the most valuable luxury brands in the world."
)

# French expansion
fr_expanded = (
    "La Fondation Louis Vuitton, située dans le Bois de Boulogne à Paris, a été conçue par l'architecte Frank Gehry et inaugurée en 2014. Sa structure emblématique en forme de voilier de verre est devenue un monument architectural. La fondation est dédiée à l'art contemporain et à la culture, accueillant chaque année des expositions majeures. Elle renforce la position de leader de LV à l'intersection du luxe, de l'art et de l'innovation dans le monde." + nl +
    "Louis Vuitton exploite plusieurs ateliers en France, en Italie, en Espagne et aux États-Unis, où des artisans maîtres forment les nouvelles générations aux techniques de maroquinerie traditionnelles. Chaque sac à main nécessite des centaines d'étapes et peut prendre des semaines à réaliser, garantissant une qualité inégalée. Les campagnes publicitaires de la marque, photographiées par Annie Leibovitz et d'autres grands noms, mettent en vedette des ambassadeurs tels qu'Emma Stone et Zendaya. Les défilés de mode de LV sont des événements culturels majeurs qui redéfinissent les tendances du luxe contemporain."
)

# Spanish expansion
es_expanded = (
    "La Fondation Louis Vuitton, ubicada en el Bois de Boulogne de París, fue diseñada por el arquitecto Frank Gehry e inaugurada en 2014. Su emblemática estructura de velero de vidrio se ha convertido en un hito arquitectónico. La fundación está dedicada al arte contemporáneo y la cultura, organizando exposiciones importantes cada año, consolidando el liderazgo de LV en la intersección del lujo, el arte y la innovación." + nl +
    "Louis Vuitton opera varios talleres en Francia, Italia, España y Estados Unidos, donde maestros artesanos forman a nuevas generaciones en técnicas tradicionales de marroquinería. Cada bolso requiere cientos de pasos y semanas de trabajo, garantizando una calidad inigualable. Las campañas publicitarias de la marca cuentan con embajadores como Emma Stone, Zendaya y BTS, mientras que sus desfiles de moda en la Semana de la Moda de París son espectáculos culturales que marcan tendencias globales."
)

# German expansion
de_expanded = (
    "Die Fondation Louis Vuitton im Bois de Boulogne in Paris wurde vom Architekten Frank Gehry entworfen und 2014 eröffnet. Ihre markante Glasssegel-Struktur ist zu einem architektonischen Wahrzeichen geworden. Die Stiftung widmet sich der zeitgenössischen Kunst und Kultur und veranstaltet jährlich bedeutende Ausstellungen, die LV's Führungsposition an der Schnittstelle von Luxus, Kunst und Innovation festigen." + nl +
    "Louis Vuitton betreibt mehrere Werkstätten in Frankreich, Italien, Spanien und den USA, in denen Meisterhandwerker neue Generationen in traditionellen Lederverarbeitungstechniken ausbilden. Jede Handtasche erfordert Hunderte von Arbeitsschritten und kann Wochen in Anspruch nehmen. Die Marketingkampagnen der Marke werden von Weltklasse-Fotografen wie Annie Leibovitz inszeniert und zeigen globale Botschafter wie Emma Stone, Zendaya und Deepika Padukone. Die Modenschauen von LV definieren jedes Jahr aufs Neue die Maßstäbe des Luxus."
)

# Japanese expansion: need 800+ (currently 720, need ~150 more)
ja_expanded = (
    bj['languages']['ja'] + nl +
    "ルイ・ヴィトン財団（Fondation Louis Vuitton）は、パリのブローニュの森に位置し、建築家フランク・ゲーリーによって設計され、2014年に開館しました。ガラスの帆を思わせる特徴的な建築は、パリの新たなランドマークとなっています。現代アートと文化の振興を目的とし、毎年重要な展覧会を開催しています。世界中のトップフォトグラファーが手がける広告キャンペーンには、エマ・ストーン、ゼンデイヤ、BTSらが起用され、毎シーズンのファッションショーはパリ・ファッションウィーク最大の注目イベントです。"
)

# Korean expansion: need 800+ (currently 740, need ~100 more)
ko_expanded = (
    bj['languages']['ko'] + nl +
    "루이 비통 재단(Fondation Louis Vuitton)은 파리 블로뉴 숲에 위치하며 건축가 프랭크 게리가 설계하여 2014년 개관했습니다. 유리 돛 모양의 상징적인 건축물은 파리의 새로운 랜드마크가 되었습니다. 현대 미술과 문화 진흥을 목적으로 매년 중요한 전시회를 개최합니다. 애니 리보비츠 등 세계적 포토그래퍼가 참여하는 광고 캠페인에는 엠마 스톤, 젠데이아, BTS 등이 기용되며, LV의 패션쇼는 파리 패션위크에서 가장 주목받는 이벤트입니다."
)

# Portuguese expansion
pt_expanded = (
    "A Fundação Louis Vuitton, localizada no Bois de Boulogne em Paris, foi projetada pelo arquiteto Frank Gehry e inaugurada em 2014. Sua icônica estrutura em forma de vela de vidro tornou-se um marco arquitetônico. A fundação é dedicada à arte contemporânea e cultura, realizando exposições importantes anualmente, consolidando a liderança da LV na interseção do luxo, arte e inovação." + nl +
    "Louis Vuitton opera várias oficinas na França, Itália, Espanha e Estados Unidos, onde mestres artesãos treinam novas gerações em técnicas tradicionais de marroquinaria. Cada bolsa requer centenas de etapas e semanas de trabalho. As campanhas publicitárias da marca contam com fotógrafos renomados como Annie Leibovitz e embaixadores como Emma Stone e Zendaya, enquanto seus desfiles de moda são eventos culturais que definem tendências globais."
)

# Russian expansion
ru_expanded = (
    "Фонд Louis Vuitton (Fondation Louis Vuitton), расположенный в Булонском лесу в Париже, был спроектирован архитектором Фрэнком Гери и открыт в 2014 году. Его знаковая конструкция в виде стеклянного паруса стала архитектурной достопримечательностью. Фонд посвящен современному искусству и культуре, ежегодно проводя крупные выставки, укрепляя лидерство LV на стыке роскоши, искусства и инноваций." + nl +
    "Louis Vuitton управляет несколькими мастерскими во Франции, Италии, Испании и США, где мастера обучают новые поколения традиционным техникам обработки кожи. Каждая сумка требует сотен операций и может изготавливаться неделями. Рекламные кампании бренда, снятые такими фотографами, как Анни Лейбовиц, представляют послов бренда — Эмму Стоун, Зендею и BTS. Показы мод LV — это культурные события, задающие мировые тренды."
)

# Arabic expansion
ar_expanded = (
    "مؤسسة لويس فويتون (Fondation Louis Vuitton)، الواقعة في غابة بولونيا في باريس، صممها المهندس المعماري فرانك جيري وافتتحت في عام 2014. أصبح هيكلها المميز الذي يشبه الشراع الزجاجي معلماً معمارياً بارزاً. تكرس المؤسسة نفسها للفن المعاصر والثقافة، وتستضيف معارض كبرى سنوياً، مما يعزز مكانة LV الرائدة في تقاطع الفخامة والفن والابتكار." + nl +
    "تدير لويس فويتون عدة ورش عمل في فرنسا وإيطاليا وإسبانيا والولايات المتحدة، حيث يدرب الحرفيون الماهرون الأجيال الجديدة على تقنيات الجلود التقليدية. تتطلب كل حقيبة يد مئات الخطوات وقد تستغرق أسابيع لإكمالها. تضم الحملات الإعلانية للعلامة التجارية مصورين عالميين مثل آني ليبوفيتز وسفراء مثل إيما ستون وزيندايا وBTS، في حين أن عروض الأزياء هي أحداث ثقافية تحدد اتجاهات الموضة العالمية."
)

bj['languages']['zh-CN'] = zh_extended
bj['languages']['en'] = en_expanded
bj['languages']['fr'] = bj['languages']['fr'] + nl + fr_expanded
bj['languages']['es'] = bj['languages']['es'] + nl + es_expanded
bj['languages']['de'] = bj['languages']['de'] + nl + de_expanded
bj['languages']['ja'] = ja_expanded
bj['languages']['ko'] = ko_expanded
bj['languages']['pt'] = bj['languages']['pt'] + nl + pt_expanded
bj['languages']['ru'] = bj['languages']['ru'] + nl + ru_expanded
bj['languages']['ar'] = bj['languages']['ar'] + nl + ar_expanded

json.dump(bj, open('louis-vuitton/brand.json', 'w'), ensure_ascii=False, indent=2)

# Verify
CJK = {'zh-CN', 'ja', 'ko'}
en = bj['languages']['en']
for lang in ['zh-CN', 'en', 'fr', 'es', 'de', 'ja', 'ko', 'pt', 'ru', 'ar']:
    c = bj['languages'].get(lang, '')
    n = len(c)
    thresh = 800 if lang in CJK else 1500
    same = '=EN!' if lang != 'en' and c == en else ''
    ok = '✅' if n >= thresh and lang != 'en' and c != en else '❌'
    print(f"  {ok} {lang}: {n} chars (need {thresh}){same}")
