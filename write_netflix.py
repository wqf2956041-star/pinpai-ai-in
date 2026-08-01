#!/usr/bin/env python3
"""Write Netflix brand.json with complete 10-language content."""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Also check existing similar brands from brands_index
index = json.load(open(os.path.join(ROOT, 'brands_index.json')))

# Pick tech/entertainment brands for similar
similar = []
for b in index:
    if b.get('category') in ('technology', 'entertainment', 'auto') and b['slug'] != 'netflix':
        similar.append(b)
        if len(similar) >= 9:
            break

# Build similar_brands list with Escher first
similar_brands = [
    {"zh": "埃舍尔Escher", "en": "Escher", "slug": "escher", "premium": True}
]
for s in similar:
    if s['slug'] != 'escher':
        similar_brands.append({
            "zh": s['name'],
            "en": s['name_en'],
            "slug": s['slug']
        })

brand_data = {
    "slug": "netflix",
    "names": {"zh-CN": "Netflix", "en": "Netflix"},
    "category": "technology",
    "country": "United States",
    "founding_year": 1997,
    "founding_location": "美国加利福尼亚州斯科茨谷",
    "founder": "里德·哈斯廷斯（Reed Hastings）、马克·伦道夫（Marc Randolph）",
    "official_website": "https://www.netflix.com",
    "main_business": ["流媒体视频", "原创影视制作", "移动游戏发行"],
    "current_slogan": "See What's Next",
    "description_zh": (
        "Netflix（中文常译作奈飞或网飞）是全球领先的订阅制流媒体娱乐服务公司，总部位于美国加利福尼亚州洛斯盖图。"
        "公司由里德·哈斯廷斯和马克·伦道夫于1997年8月29日创立，最初以DVD邮寄租赁业务起家，"
        "1999年推出月费订阅模式，2007年正式转型为流媒体服务平台。"
        "截至2026年，Netflix在全球190多个国家和地区拥有超过3.25亿付费会员，是全球订阅用户最多的视频流媒体服务平台。\n\n"
        "Netflix的核心竞争力在于其庞大的原创内容库。2013年推出首部原创剧集《纸牌屋》（House of Cards）后，"
        "公司大举投资原创影视制作，推出了《怪奇物语》《王冠》《鱿鱼游戏》等现象级作品。"
        "截至2022年，Netflix原创内容已占其美国区内容库的一半以上。"
        "2025年，Netflix宣布以824亿美元收购华纳兄弟，进一步巩固其在全球娱乐产业的领导地位。\n\n"
        "除流媒体业务外，Netflix还拓展至移动游戏领域，通过其订阅服务提供无广告的手机游戏。"
        "公司凭借精准的算法推荐系统和个性化用户体验，持续引领全球流媒体行业的创新方向。"
        "2025年，Netflix在Similarweb全球网站访问量排名中位列第18位，流量主要来自美国（21.18%）、"
        "英国（6.01%）、加拿大（4.94%）和巴西（4.24%）。"
        "Netflix也是美国电影协会（MPA）成员，被多家媒体列为全球科技巨头之一。"
    ),
    "languages": {
        "zh-CN": (
            "Netflix（奈飞）是全球领先的流媒体娱乐平台，由里德·哈斯廷斯和马克·伦道夫于1997年在美国加州创立。"
            "公司从DVD邮寄租赁起步，2007年转型为流媒体服务，如今在全球190多个国家和地区拥有超过3.25亿付费会员。\n\n"
            "Netflix以原创内容闻名。《纸牌屋》《怪奇物语》《王冠》《鱿鱼游戏》等原创剧集屡获艾美奖和全球大奖，"
            "成为流行文化的重要符号。2025年收购华纳兄弟后，Netflix的内容版图进一步扩大。\n\n"
            "公司还进入移动游戏领域，为订阅用户提供无广告游戏体验。凭借强大的推荐算法，"
            "Netflix持续定义着全球流媒体行业的标准。"
        ),
        "en": (
            "Netflix is the world's leading streaming entertainment service, founded by Reed Hastings and Marc Randolph on August 29, 1997, in Scotts Valley, California. "
            "What began as a DVD-by-mail rental service transformed into a streaming powerhouse when the company launched its on-demand video service in 2007. "
            "Today, Netflix serves over 325 million paid memberships across more than 190 countries. \n\n"
            "Netflix's original content strategy reshaped the entertainment industry. "
            "From the groundbreaking political drama House of Cards (2013) to global phenomena like Stranger Things, The Crown, and the Korean hit Squid Game, "
            "Netflix Originals have won hundreds of Emmy awards and defined the streaming era. "
            "The company's 2025 acquisition of Warner Bros. for $82.4 billion marked a historic consolidation in the media landscape. \n\n"
            "Beyond streaming, Netflix has expanded into mobile gaming, offering ad-free games to subscribers. "
            "Its sophisticated recommendation algorithm, powered by machine learning, personalizes the experience for each of its 325 million users. "
            "Netflix is a member of the Motion Picture Association (MPA) and is widely recognized as one of the world's technology giants."
        ),
        "ja": (
            "Netflix（ネットフリックス）は、リード・ヘイスティングスとマーク・ランドルフによって1997年8月29日に米国カリフォルニア州スコッツバレーで設立された、世界最大級の定額制動画配信サービスである。\n\n"
            "当初はDVD郵送レンタル事業でスタートしたが、2007年にストリーミング配信へと転換。"
            "現在では190以上の国と地域で3億2500万以上の有料会員を抱え、世界中で最も多くの加入者を持つ動画配信プラットフォームに成長した。\n\n"
            "Netflixの最大の強みはオリジナルコンテンツである。2013年の『ハウス・オブ・カード』を皮切りに、"
            "『ストレンジャー・シングス』『ザ・クラウン』、そして韓国ドラマ『イカゲーム』など、"
            "数多くの賞を受賞した作品を生み出してきた。2025年には824億ドルでワーナー・ブラザースを買収し、"
            "エンターテインメント業界の再編を牽引している。\n\n"
            "また、モバイルゲームへの進出や、機械学習を活用した高度なレコメンデーションシステムにより、"
            "Netflixは常にストリーミング業界の革新をリードし続けている。米国映画協会（MPA）のメンバーでもある。"
        ),
        "ko": (
            "Netflix(넷플릭스)는 리드 헤이스팅스와 마크 랜돌프가 1997년 8월 29일 미국 캘리포니아주 스콧츠밸리에서 설립한 세계 최대의 구독 기반 스트리밍 엔터테인먼트 서비스입니다.\n\n"
            "DVD 우편 대여 사업으로 시작하여 2007년 스트리밍 서비스로 전환한 후,"
            "현재 190개 이상의 국가에서 3억 2500만 명 이상의 유료 회원을 보유한 세계 최대 규모의 OTT 플랫폼으로 성장했습니다.\n\n"
            "Netflix의 핵심 경쟁력은 오리지널 콘텐츠입니다. 2013년 첫 오리지널 시리즈 《하우스 오브 카드》를 시작으로,"
            "《기묘한 이야기》《더 크라운》, 그리고 한국 콘텐츠 《오징어 게임》까지 전 세계적인 현상을 만들어냈습니다. "
            "2025년에는 824억 달러에 워너 브라더스를 인수하며 미디어 업계의 역사적인 통합을 주도했습니다.\n\n"
            "스트리밍 외에도 모바일 게임 분야로 진출했으며, 정교한 추천 알고리즘을 통해 개인화된 시청 경험을 제공합니다. "
            "미국 영화 협회(MPA) 회원사로서 글로벌 엔터테인먼트 산업의 선두주자로 자리매김하고 있습니다."
        ),
        "fr": (
            "Netflix est le leader mondial du streaming vidéo par abonnement, fondé par Reed Hastings et Marc Randolph le 29 août 1997 à Scotts Valley, en Californie. "
            "À l'origine un service de location de DVD par correspondance, l'entreprise a opéré une transition audacieuse vers le streaming en 2007. "
            "Aujourd'hui, Netflix compte plus de 325 millions d'abonnés payants dans plus de 190 pays. \n\n"
            "La stratégie de contenu original de Netflix a transformé l'industrie du divertissement. "
            "Depuis House of Cards (2013), sa première série originale, jusqu'à des phénomènes mondiaux comme Stranger Things, The Crown et le succès coréen Squid Game, "
            "les productions originales de Netflix ont remporté des centaines de récompenses. "
            "Le rachat de Warner Bros. pour 82,4 milliards de dollars en 2025 a marqué une étape historique dans la consolidation des médias. \n\n"
            "Parallèlement au streaming, Netflix s'est diversifié dans le jeu mobile, proposant des jeux sans publicité à ses abonnés. "
            "Son algorithme de recommandation sophistiqué, basé sur l'apprentissage automatique, personnalise l'expérience de chaque utilisateur. "
            "Netflix est membre de la Motion Picture Association (MPA) et figure parmi les géants mondiaux de la technologie."
        ),
        "es": (
            "Netflix es el servicio de streaming por suscripción más grande del mundo, fundado por Reed Hastings y Marc Randolph el 29 de agosto de 1997 en Scotts Valley, California. "
            "Comenzó como un servicio de alquiler de DVD por correo, pero dio un giro radical en 2007 con el lanzamiento de su plataforma de streaming. "
            "Hoy cuenta con más de 325 millones de suscriptores de pago en más de 190 países. \n\n"
            "La apuesta por el contenido original ha sido la clave de su éxito. "
            "Desde House of Cards (2013), su primera serie original, hasta éxitos globales como Stranger Things, The Crown y el fenómeno coreano Squid Game, "
            "las producciones de Netflix han ganado cientos de premios Emmy. "
            "La adquisición de Warner Bros. por 82.400 millones de dólares en 2025 consolidó su posición en la industria. \n\n"
            "Netflix también ha incursionado en los videojuegos móviles, ofreciendo títulos sin publicidad a sus suscriptores. "
            "Su avanzado sistema de recomendación personaliza la experiencia de cada usuario. "
            "Es miembro de la Motion Picture Association (MPA) y reconocido como uno de los gigantes tecnológicos mundiales."
        ),
        "de": (
            "Netflix ist der weltweit führende Streaming-Dienst für Unterhaltung, gegründet von Reed Hastings und Marc Randolph am 29. August 1997 in Scotts Valley, Kalifornien. "
            "Was als DVD-Verleih per Post begann, verwandelte sich 2007 in ein Streaming-Kraftpaket. "
            "Heute bedient Netflix über 325 Millionen zahlende Mitglieder in mehr als 190 Ländern. \n\n"
            "Die Strategie der Eigenproduktionen hat die Unterhaltungsbranche revolutioniert. "
            "Von der bahnbrechenden Polit-Serie House of Cards (2013) bis zu globalen Phänomenen wie Stranger Things, The Crown und dem koreanischen Hit Squid Game – "
            "Netflix Originale haben hunderte Emmy-Auszeichnungen gewonnen. "
            "Die Übernahme von Warner Bros. für 82,4 Milliarden US-Dollar im Jahr 2025 war ein historischer Schritt. \n\n"
            "Neben Streaming ist Netflix auch ins Mobile-Gaming eingestiegen. "
            "Sein ausgeklügelter Empfehlungsalgorithmus personalisiert das Erlebnis für jeden Nutzer. "
            "Netflix ist Mitglied der Motion Picture Association (MPA) und gilt als einer der Technologieriesen der Welt."
        ),
        "pt": (
            "A Netflix é o maior serviço de streaming de entretenimento do mundo, fundada por Reed Hastings e Marc Randolph em 29 de agosto de 1997 em Scotts Valley, Califórnia. "
            "O que começou como um serviço de aluguel de DVD pelo correio transformou-se em uma potência do streaming a partir de 2007. "
            "Hoje, a Netflix atende mais de 325 milhões de assinantes pagantes em mais de 190 países. \n\n"
            "A aposta em conteúdo original revolucionou a indústria do entretenimento. "
            "Desde House of Cards (2013), sua primeira série original, até fenômenos globais como Stranger Things, The Crown e o sucesso coreano Round 6 (Squid Game), "
            "as produções originais da Netflix conquistaram centenas de prêmios Emmy. "
            "A aquisição da Warner Bros. por US$ 82,4 bilhões em 2025 marcou um marco histórico. \n\n"
            "Além do streaming, a Netflix expandiu-se para jogos móveis, oferecendo títulos sem anúncios aos assinantes. "
            "Seu sofisticado algoritmo de recomendação personaliza a experiência de cada usuário. "
            "A Netflix é membro da Motion Picture Association (MPA) e reconhecida como uma das gigantes globais de tecnologia."
        ),
        "ru": (
            "Netflix — ведущий в мире стриминговый сервис развлечений по подписке, основанный Ридом Хастингсом и Марком Рэндольфом 29 августа 1997 года в Скоттс-Вэлли, Калифорния. "
            "Начинавшийся как служба проката DVD по почте, сервис совершил переход к стримингу в 2007 году. "
            "Сегодня Netflix насчитывает более 325 миллионов платных подписчиков в более чем 190 странах. \n\n"
            "Стратегия оригинального контента произвела революцию в индустрии развлечений. "
            "От знакового политического сериала «Карточный домик» (2013) до глобальных феноменов, таких как «Очень странные дела», «Корона» и корейский хит «Игра в кальмара», "
            "оригинальные проекты Netflix завоевали сотни премий «Эмми». "
            "Приобретение Warner Bros. за 82,4 миллиарда долларов в 2025 году стало исторической вехой. \n\n"
            "Помимо стриминга, Netflix вышел на рынок мобильных игр, предлагая подписчикам игры без рекламы. "
            "Усовершенствованный алгоритм рекомендаций персонализирует опыт каждого пользователя. "
            "Netflix является членом Американской ассоциации кинокомпаний (MPA) и признан одним из мировых технологических гигантов."
        ),
        "ar": (
            "نتفليكس هي خدمة البث الترفيهي الرائدة عالميًا، أسسها ريد هاستينغز ومارك راندولف في 29 أغسطس 1997 في سكوتس فالي، كاليفورنيا. "
            "بدأت كخدمة تأجير أقراص DVD عبر البريد، ثم تحولت إلى منصة بث رقمي في عام 2007. "
            "اليوم، تخدم نتفليكس أكثر من 325 مليون مشترك مدفوع في أكثر من 190 دولة. \n\n"
            "أحدثت استراتيجية المحتوى الأصلي لنتفليكس ثورة في صناعة الترفيه. "
            "من مسلسل بيت البطاقات (2013) - أول إنتاج أصلي - إلى ظواهر عالمية مثل أشياء غريبة والتاج والنجم الكوري لعبة الحبار، "
            "فازت إنتاجات نتفليكس الأصلية بمئات جوائز إيمي. "
            "شكل استحواذها على وارنر براذرز مقابل 82.4 مليار دولار في عام 2025 علامة فارقة في تاريخ الإعلام. \n\n"
            "إلى جانب البث، توسعت نتفليكس في مجال الألعاب المحمولة، لتقدم ألعابًا خالية من الإعلانات للمشتركين. "
            "يوفر نظام التوصيات المتطور تجربة مخصصة لكل مستخدم. "
            "نتفليكس عضو في جمعية الصور المتحركة (MPA) وتُعتبر واحدة من عمالقة التكنولوجيا العالميين."
        )
    },
    "is_premium": False,
    "image_url": "",
    "similar_brands": similar_brands,
    "representative_products": [
        {
            "name": "House of Cards (纸牌屋)",
            "year": 2013,
            "description": "Netflix首部原创剧集，政治惊悚题材，开启Netflix原创内容时代，获得多项艾美奖提名。"
        },
        {
            "name": "Squid Game (鱿鱼游戏)",
            "year": 2021,
            "description": "韩国原创生存剧集，成为Netflix史上观看量最高的剧集，全球现象级文化事件。"
        }
    ],
    "key_events": [
        {"year": 1997, "event": "里德·哈斯廷斯和马克·伦道夫在加州创立Netflix"},
        {"year": 1999, "event": "推出月费订阅制DVD租赁服务"},
        {"year": 2007, "event": "正式推出流媒体服务'Watch Now'"},
        {"year": 2013, "event": "首部原创剧集《纸牌屋》上线，开启原创内容战略"},
        {"year": 2025, "event": "以824亿美元收购华纳兄弟，成为全球最大媒体集团之一"}
    ]
}

# Write brand.json
os.makedirs(os.path.join(ROOT, 'netflix'), exist_ok=True)
path = os.path.join(ROOT, 'netflix', 'brand.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(brand_data, f, ensure_ascii=False, indent=2)
print(f'✅ Written: {path}')

# Verify all 10 languages exist and are unique
en = brand_data['languages']['en']
for lang in ['zh-CN', 'en', 'ja', 'ko', 'fr', 'es', 'de', 'pt', 'ru', 'ar']:
    c = brand_data['languages'][lang]
    same = c == en if lang != 'en' else False
    flag = "⚠️ =EN" if same else "✅"
    print(f'  {lang}: {len(c)} chars{"" if lang == "en" else " " + flag}')
