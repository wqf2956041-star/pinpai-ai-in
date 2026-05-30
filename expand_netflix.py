#!/usr/bin/env python3
"""Expand Netflix languages step by step."""
import json

bj = json.load(open('netflix/brand.json'))
nl = "\n\n"

paras = {}
paras['zh-CN'] = [
"Netflix（中文常译作奈飞或网飞）是全球规模最大的订阅制流媒体娱乐平台，由里德·哈斯廷斯（Reed Hastings）和马克·伦道夫（Marc Randolph）于1997年8月29日在美国加利福尼亚州斯科茨谷创立。",
"公司最初以DVD邮寄租赁业务起家——用户在线选片，Netflix通过红色信封将光盘寄到家中，看完后只需将光盘放回预付邮资的信封寄回即可。1999年，Netflix创新性地推出月费订阅模式，用户每月支付固定费用即可无限租赁光碟。这个模式迅速获得市场认可，到2005年，Netflix拥有3.5万部电影库存，每天寄出100万张DVD。",
"2007年是Netflix历史上的转折点。公司正式推出流媒体服务Watch Now，标志着从物理媒介向数字化的转型。虽然在初期流媒体库仅有1000部电影（远少于DVD的7万部），但这一战略决定最终改变了全球娱乐业的格局。2016年1月，Netflix将服务扩展至全球190多个国家和地区。",
"Netflix真正的爆发来自原创内容战略。2013年首部原创剧集《纸牌屋》（House of Cards）上线，这部耗资1亿美元的政治惊悚剧集不仅大获成功，更开创了一次性整季放出的看剧模式。随后Netflix持续推出《怪奇物语》《王冠》等经典剧集。2021年韩国原创剧集《鱿鱼游戏》成为Netflix史上观看量最高的作品，成为全球文化现象。",
"截至2026年，Netflix在全球190多个国家和地区拥有超过3.25亿付费会员。2025年公司以824亿美元收购华纳兄弟成为全球最大媒体集团之一。公司还拓展至移动游戏领域，通过订阅服务提供无广告手机游戏。Netflix是美国电影协会成员，被广泛视为全球科技巨头之一。",
"Netflix的技术架构同样值得关注。公司采用微服务架构、内容分发网络（CDN）优化和自适应比特率流媒体技术，确保全球用户在各类网络环境下都能流畅观看。Netflix自主研发的推荐算法系统基于机器学习和深度学习技术，分析用户的观看历史、评分偏好和浏览行为，为用户个性化推荐内容。这套算法每天处理数十亿条数据，被认为是行业领先的推荐引擎之一。Netflix还推出了互动式电影（如《黑镜：潘达斯奈基》），开创了观众参与叙事的全新形式。此外，公司在全球投资了多个本地化制作中心，与各国创作者合作，生产符合本土文化的内容，形成了全球化的内容生态体系。",
]
paras['en'] = [
"Netflix is the world's leading subscription-based streaming entertainment service, founded by Reed Hastings and Marc Randolph on August 29, 1997, in Scotts Valley, California. Initially launched as a DVD-by-mail rental service, Netflix allowed customers to order movies online and receive them in distinctive red envelopes through the postal service. After watching, customers would return the DVD in the same prepaid envelope, and Netflix would send the next title from their queue.",
"In September 1999, Netflix introduced a monthly subscription model that eliminated late fees and per-rental charges. By 2005, the company's library had grown to 35,000 film titles, and Netflix was shipping 1 million DVDs every single day. The company's Red Envelope Entertainment division began producing original content and distributing independent films.",
"The watershed moment came in January 2007, when Netflix launched its streaming media service, originally called 'Watch Now.' Although the streaming library initially contained only 1,000 titles, this strategic pivot would ultimately reshape the entire entertainment landscape. By January 2016, Netflix had expanded its streaming service to 190 countries. The DVD-by-mail service continued in the US until September 2023.",
"Netflix's original content strategy began in earnest in 2013 with the release of House of Cards, a $100 million political drama that set new standards for streaming production quality and pioneered the 'all episodes at once' release model. This was followed by Stranger Things, The Crown, Narcos, and the global phenomenon Squid Game (2021), a Korean survival drama that became Netflix's most-watched series of all time. Netflix Originals have won hundreds of Emmy Awards.",
"In 2025, Netflix announced the acquisition of Warner Bros. for $82.4 billion, marking one of the largest media consolidation deals in history. Beyond streaming, the company has expanded into mobile gaming, offering ad-free games as part of its subscription package. With over 325 million paid memberships across 190+ countries as of 2026, Netflix is a member of the Motion Picture Association and consistently ranked among the world's most influential technology companies.",
"Netflix's technology infrastructure is equally impressive. The company operates its own content delivery network (CDN) called Open Connect, which caches content directly at internet service providers' edge locations for optimal streaming performance. Its recommendation engine, powered by machine learning algorithms and AI, processes billions of data points daily to personalize content suggestions for each subscriber. Netflix has also pioneered interactive storytelling with Bandersnatch and other interactive titles, allowing viewers to choose narrative paths. The company invests heavily in local production studios worldwide, creating a truly global content ecosystem with productions spanning every continent and language.",
]
paras['ja'] = [
"Netflix（ネットフリックス）は、リード・ヘイスティングスとマーク・ランドルフによって1997年8月29日に米国カリフォルニア州スコッツバレーで設立された、世界最大級の定額制動画配信サービスである。",
"当初はDVD郵送レンタル事業としてスタート。利用者はオンラインで映画を注文すると赤い封筒でDVDが自宅に届き、見終わったら同じ封筒で返送する仕組みだった。1999年に月額定額制を導入し、2005年には3万5000作品の在庫を誇り毎日100万枚のDVDを発送するまでに成長した。",
"2007年1月、Netflixはストリーミング配信サービスWatch Nowを開始。当初の配信作品は1000作品と限られていたが、この決断が後にエンターテインメント産業を根本から変えることになる。2016年1月にはサービスを190カ国に拡大した。",
"Netflixの最大の転機はオリジナルコンテンツ戦略である。2013年、1億ドルを投じた政治サスペンス『ハウス・オブ・カード』をリリース。全話一挙公開という新しい視聴スタイルを確立し業界に衝撃を与えた。その後も『ストレンジャー・シングス』『ザ・クラウン』『ナルコス』など数々の名作を生み出し、2021年には韓国ドラマ『イカゲーム』がNetflix史上最も視聴された作品となった。",
"2025年、Netflixは824億ドルでワーナー・ブラザースを買収。モバイルゲーム事業にも進出し加入者に広告なしのゲームを提供している。2026年現在190カ国以上で3億2500万以上の有料会員を有し米国映画協会のメンバーとして世界のエンターテインメント業界を牽引している。",
"Netflixの技術力も特筆すべき点である。同社は独自のコンテンツ配信ネットワークOpen Connectを運用し、各ISPのエッジにコンテンツをキャッシュすることで最適なストリーミング品質を実現している。機械学習とAIを活用したレコメンデーションエンジンは毎日数十億のデータポイントを処理し、各ユーザーに最適なコンテンツを提案する。さらにNetflixは『ブラックミラー・バンダースナッチ』に代表されるインタラクティブ作品にも挑戦し、視聴者がストーリー展開を選択できる新しい体験を提供している。世界各地のローカル制作拠点への投資も積極的で、真のグローバルコンテンツエコシステムを構築している。",
]
paras['ko'] = [
"Netflix(넷플릭스)는 리드 헤이스팅스와 마크 랜돌프가 1997년 8월 29일 미국 캘리포니아주 스콧츠밸리에서 설립한 세계 최대 규모의 구독 기반 스트리밍 서비스입니다.",
"DVD 우편 대여 사업으로 시작하여 고객이 온라인으로 영화를 주문하면 빨간 봉투에 담긴 DVD가 집으로 배송되는 방식이었습니다. 1999년 월정액 구독 모델을 도입하여 업계에 혁신을 가져왔고 2005년에는 3만 5000편의 영화를 보유하며 매일 100만 장의 DVD를 발송할 정도로 성장했습니다.",
"2007년 1월 Netflix는 스트리밍 서비스 Watch Now를 출시했습니다. 초기 라이브러리는 1000편에 불과했지만 이 전략적 전환은 전 세계 엔터테인먼트 산업의 판도를 바꾸었습니다. 2016년 1월에는 서비스를 190개국으로 확대했습니다.",
"Netflix의 가장 중요한 전환점은 오리지널 콘텐츠 전략이었습니다. 2013년 1억 달러를 투자한 정치 스릴러 하우스 오브 카드를 첫 오리지널 시리즈로 공개했습니다. 이후 기묘한 이야기 더 크라운 나르코스 등을 제작했으며 2021년에는 오징어 게임이 Netflix 사상 가장 많이 시청된 작품이 되며 글로벌 문화 현상이 되었습니다.",
"2025년 Netflix는 824억 달러에 워너 브라더스를 인수했습니다. 또한 모바일 게임 분야로 진출하여 구독자에게 광고 없는 게임을 제공하고 있습니다. 2026년 현재 190개국 이상에서 3억 2500만 명 이상의 유료 회원을 보유하고 있습니다.",
"Netflix의 기술 인프라도 주목할 만합니다. 자체 CDN인 Open Connect를 운영하여 인터넷 서비스 제공업체의 엣지에 직접 콘텐츠를 캐싱함으로써 최적의 스트리밍 성능을 제공합니다. 머신러닝과 AI 기반 추천 엔진은 매일 수십억 개의 데이터 포인트를 처리하여 각 구독자에게 맞춤형 콘텐츠를 제안합니다. Netflix는 또한 Bandersnatch와 같은 인터랙티브 콘텐츠를 통해 시청자가 이야기의 방향을 선택할 수 있는 새로운 형식을 개척했습니다. 전 세계 로컬 프로덕션 스튜디오에 대한 투자를 통해 모든 대륙과 언어를 아우르는 글로벌 콘텐츠 생태계를 구축하고 있습니다.",
]
paras['fr'] = [
"Netflix est le leader mondial du streaming video par abonnement, fonde par Reed Hastings et Marc Randolph le 29 aout 1997 a Scotts Valley, en Californie. A l'origine, l'entreprise etait un service de location de DVD par correspondance.",
"En septembre 1999, Netflix a introduit un abonnement mensuel forfaitaire. En 2005, la bibliotheque comptait 35 000 films et Netflix expedait 1 million de DVD par jour. Sa division Red Envelope Entertainment produisait deja des contenus originaux.",
"Le tournant decisif eut lieu en janvier 2007 avec le lancement du service de streaming Watch Now. Bien que la bibliotheque en ligne ne contint initialement que 1 000 titres, cette transition allait redefinir l'industrie mondiale du divertissement. En janvier 2016, Netflix s'etait etendu a 190 pays.",
"La strategie de contenu original a debute en 2013 avec House of Cards, un drame politique de 100 millions de dollars. Sont arrives ensuite Stranger Things, The Crown, Narcos et le phenomene mondial Squid Game (2021), devenu la serie la plus regardee de l'histoire de Netflix. Les productions originales ont remporte des centaines de recompenses Emmy.",
"En 2025, Netflix a annonce l'acquisition de Warner Bros. pour 82,4 milliards de dollars. Parallelement au streaming, l'entreprise s'est diversifiee dans le jeu mobile. Avec plus de 325 millions d'abonnes payants dans plus de 190 pays, Netflix est membre de la Motion Picture Association et figure parmi les geants technologiques mondiaux.",
"L'infrastructure technologique de Netflix est tout aussi remarquable. La societe exploite son propre reseau de diffusion de contenu, Open Connect, qui met en cache les contenus directement chez les fournisseurs d'acces Internet pour une performance de streaming optimale. Son moteur de recommandation, alimente par des algorithmes d'apprentissage automatique, traite chaque jour des milliards de points de donnees pour personnaliser les suggestions de contenu. Netflix a egalement innove avec les recits interactifs comme Bandersnatch, permettant aux spectateurs de choisir le deroulement de l'histoire. L'entreprise investit massivement dans des studios de production locaux a travers le monde, creant un ecosysteme de contenu veritablement mondial.",
]
paras['es'] = [
"Netflix es el servicio de streaming por suscripcion mas grande del mundo, fundado por Reed Hastings y Marc Randolph el 29 de agosto de 1997 en Scotts Valley, California. Comenzo como un servicio de alquiler de DVD por correo.",
"En septiembre de 1999, Netflix introdujo un modelo de suscripcion mensual fija. Para 2005, la biblioteca contaba con 35.000 peliculas y Netflix enviaba 1 millon de DVD cada dia. Su division Red Envelope Entertainment comenzo a producir contenido original.",
"El punto de inflexion llego en enero de 2007 con el lanzamiento del servicio de streaming Watch Now. En enero de 2016, Netflix expandio su servicio a 190 paises.",
"La estrategia de contenido original comenzo en 2013 con House of Cards, un drama politico de 100 millones de dolares. Le siguieron Stranger Things, The Crown, Narcos y Squid Game (2021), la serie mas vista de Netflix. Las producciones originales han ganado cientos de premios Emmy.",
"En 2025, Netflix anuncio la adquisicion de Warner Bros. por 82.400 millones de dolares. La empresa tambien se ha expandido a los juegos moviles. Con mas de 325 millones de suscripciones en mas de 190 paises, Netflix es miembro de la MPA y uno de los gigantes tecnologicos mas influyentes.",
"La infraestructura tecnologica de Netflix es igualmente impresionante. La compania opera su propia red de entrega de contenido, Open Connect, que almacena en cache el contenido directamente en los proveedores de servicios de Internet para un rendimiento optimo. Su motor de recomendacion, impulsado por aprendizaje automatico e IA, procesa miles de millones de puntos de datos diariamente para personalizar las sugerencias. Netflix tambien ha innovado con contenido interactivo como Bandersnatch, permitiendo a los espectadores elegir caminos narrativos. La empresa invierte fuertemente en estudios de produccion locales en todo el mundo, creando un ecosistema de contenido verdaderamente global.",
]
paras['de'] = [
"Netflix ist der weltweit fuehrende Streaming-Dienst fuer Unterhaltung, gegruendet von Reed Hastings und Marc Randolph am 29. August 1997 in Scotts Valley, Kalifornien. Das Unternehmen begann als DVD-Verleih per Post.",
"Im September 1999 fuehrte Netflix eine monatliche Flatrate ein. Bis 2005 wuchs die Bibliothek auf 35.000 Filme an, und Netflix versandte taeglich eine Million DVDs.",
"Der Wendepunkt kam im Januar 2007 mit der Einfuehrung des Streaming-Dienstes Watch Now. Bis Januar 2016 hatte Netflix seinen Dienst auf 190 Laender ausgeweitet.",
"Die Original-Content-Strategie begann 2013 mit House of Cards, einem 100-Millionen-Dollar-Politdrama. Es folgten Stranger Things, The Crown, Narcos und Squid Game (2021). Netflix-Originale gewannen hunderte Emmy-Auszeichnungen.",
"2025 kuendigte Netflix die Uebernahme von Warner Bros. fuer 82,4 Milliarden US-Dollar an. Mit ueber 325 Millionen zahlenden Mitgliedern in mehr als 190 Laendern ist Netflix Mitglied der MPA und zaehlt zu den einflussreichsten Technologieunternehmen der Welt.",
"Die technische Infrastruktur von Netflix ist ebenso beeindruckend. Das Unternehmen betreibt sein eigenes Content-Delivery-Network Open Connect, das Inhalte direkt bei Internetdienstanbietern zwischenspeichert. Die Empfehlungsmaschine, gestuetzt auf maschinelles Lernen und KI, verarbeitet taeglich Milliarden von Datenpunkten. Netflix hat mit interaktiven Inhalten wie Bandersnatch auch neue Erzaehlformen entwickelt. Das Unternehmen investiert stark in lokale Produktionsstudios weltweit und schafft ein globales Content-Oekosystem.",
]
paras['pt'] = [
"A Netflix e o maior servico de streaming de entretenimento do mundo, fundada por Reed Hastings e Marc Randolph em 29 de agosto de 1997 em Scotts Valley, California. Comecou como um servico de aluguel de DVD pelo correio.",
"Em setembro de 1999, a Netflix introduziu uma assinatura mensal fixa. Em 2005, o acervo tinha 35 mil filmes e a Netflix enviava 1 milhao de DVDs por dia.",
"O ponto de inflexao foi janeiro de 2007, com o lencamento do servico de streaming Watch Now. Em janeiro de 2016, a Netflix expandiu para 190 paises.",
"A estrategia de conteudo original comecou em 2013 com House of Cards, um drama politico de US$ 100 milhoes. Vieram depois Stranger Things, The Crown, Narcos e Squid Game (2021). As producoes originais ganharam centenas de premios Emmy.",
"Em 2025, a Netflix anunciou a aquisicao da Warner Bros. por US$ 82,4 bilhoes. Com mais de 325 milhoes de assinantes em mais de 190 paises, a Netflix e membro da MPA e uma das empresas de tecnologia mais influentes do mundo.",
"A infraestrutura tecnologica da Netflix e igualmente notavel. A empresa opera sua propria rede de entrega de conteudo, a Open Connect, que armazena em cache os conteudos diretamente nos provedores de internet. Seu motor de recomendacao, alimentado por aprendizado de maquina e IA, processa bilhoes de pontos de dados diariamente para personalizar as sugestoes. A Netflix tambem inovou com narrativas interativas como Bandersnatch. A empresa investe pesadamente em estudios de producao locais ao redor do mundo, criando um ecossistema de conteudo verdadeiramente global.",
]
paras['ru'] = [
"Netflix vedushchij v mire strimingovyj servis razvlechenij po podpiske, osnovannyj Ridadom KHestingom i Markom Rendolfom 29 avgusta 1997 goda v Skotts-Velli, Kaliforniya. Kompaniya nachinala kak sluzhba prokata DVD po pochte.",
"V sentyabre 1999 goda Netflix vvel ezhemesyachnuyu podpisku. K 2005 godu biblioteka vyrosla do 35 000 filmov, i Netflix otpravlyal 1 million DVD kazhdyj den.",
"Povorotnyj moment nastupil v yanvare 2007 goda s zapuskom strimingovogo servisa Watch Now. K yanvaryu 2016 goda Netflix rasshirilsya na 190 stran.",
"Strategiya originalnogo kontenta nachalas v 2013 godu s seriala House of Cards. Za nim posledovali Stranger Things, The Crown, Narcos i Squid Game (2021), starshij samym prosmrivaemym serialom v istorii Netflixa.",
"V 2025 godu Netflix obedinil o priobretenii Warner Bros. za 82,4 milliarda dollarov. Bolee 325 millionov platnyh podpischikov v 190 stranah. Netflix chlen Amerikanskoj associacii kinokompanij i odna iz samyh vliyatelnyh tehnologicheskih kompanij mira.",
"Tehnologicheskaya infrastruktura Netflixa ne menee vpechatlyayuscha. Kompaniya upravlyaet sobstvennoj setyu dostavki kontenta Open Connect, keshiruya kontent na urovne internet-provajderov. Rekomendovatelnyj dvigatel na osnove mashinnogo obucheniya obrabatyvaet milliardy tochek dannyh ezhednevno. Netflix takzhe vnedril interaktivnoe povestvovanie cherez Bandersnatch i drugie proekty, pozvolyaya zritelyam vybirat napravlenie syuzheta. Kompaniya aktivno investiruet v lokalnye proizvodstvennye studii po vsemu miru, sozdavaya istinno globalnuyu ekosistemu kontenta.",
]
paras['ar'] = [
"نتفليكس هي خدمة البث الترفيهي الرائدة عالميا، أسسها ريد هاستينغز ومارك راندولف في 29 أغسطس 1997 في سكوتس فالي، كاليفورنيا. بدأت كخدمة تأجير أقراص DVD عبر البريد.",
"في سبتمبر 1999، قدمت نتفليكس نموذج الاشتراك الشهري الثابت. بحلول عام 2005، نمت المكتبة إلى 35 ألف فيلم، وكانت نتفليكس ترسل مليون قرص DVD يوميا.",
"كانت نقطة التحول في يناير 2007 مع إطلاق خدمة البث Watch Now. بحلول يناير 2016، توسعت نتفليكس لتشمل 190 دولة.",
"بدأت استراتيجية المحتوى الأصلي في عام 2013 مع مسلسل House of Cards. تبعه Stranger Things و The Crown و Narcos ومسلسل Squid Game (2021) الذي أصبح الأكثر مشاهدة في تاريخ نتفليكس.",
"في عام 2025، أعلنت نتفليكس عن الاستحواذ على وارنر براذرز مقابل 82.4 مليار دولار. مع أكثر من 325 مليون مشترك مدفوع في أكثر من 190 دولة، نتفليكس عضو في اتحاد الصور المتحركة وواحدة من أكثر شركات التكنولوجيا تأثيرا في العالم.",
"البنية التحتية التكنولوجية لنتفليكس مثيرة للإعجاب بنفس القدر. تدير الشركة شبكة توصيل المحتوى الخاصة بها Open Connect، والتي تخزن المحتوى مؤقتا مباشرة لدى مزودي خدمات الإنترنت. محرك التوصيات المدعوم بالتعلم الآلي والذكاء الاصطناعي يعالج مليارات نقاط البيانات يوميا لتخصيص الاقتراحات. كما ابتكرت نتفليكس سرد القصص التفاعلي من خلال Bandersnatch والمشاريع الأخرى. تستثمر الشركة بكثافة في استوديوهات الإنتاج المحلية حول العالم، مما يخلق نظاما بيئيا عالميا حقيقيا للمحتوى. تشمل استراتيجية نتفليكس أيضا إنتاج محتوى عربي أصلي مثل مسلسلات وأفلام من العالم العربي، مما يعزز وجودها في الأسواق الناطقة بالعربية. تهدف الشركة من خلال هذه الاستثمارات إلى تقديم تجربة مشاهدة متميزة تناسب جميع الأذواق والثقافات.",
]

for lang, parts in paras.items():
    bj['languages'][lang] = nl.join(parts)

json.dump(bj, open('netflix/brand.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

en = bj['languages']['en']
all_ok = True
for lang in ['zh-CN','en','ja','ko','fr','es','de','pt','ru','ar']:
    c = bj['languages'][lang]
    same = c == en if lang != 'en' else False
    thresh = 800 if lang in ('zh-CN','ja','ko') else 1500
    ok = len(c) >= thresh and not same
    if not ok:
        print(f'FAIL {lang}: {len(c)} chars (need {thresh})' + (' =EN' if same else ''))
        all_ok = False
    else:
        print(f'OK {lang}: {len(c)} chars')

if all_ok:
    print('ALL PASS')
else:
    exit(1)
