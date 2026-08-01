#!/usr/bin/env python3
"""Set full 10-language content for Netflix brand.json, meeting CJK>=800 and non-CJK>=1500 thresholds."""
import json

bj = json.load(open('netflix/brand.json'))

# Language content with line breaks as \n
nl = "\n\n"

zh_cn_parts = [
"Netflix（中文常译作奈飞或网飞）是全球规模最大的订阅制流媒体娱乐平台，由里德·哈斯廷斯（Reed Hastings）和马克·伦道夫（Marc Randolph）于1997年8月29日在美国加利福尼亚州斯科茨谷创立。",
"公司最初以DVD邮寄租赁业务起家——用户在线选片，Netflix通过红色信封将光盘寄到家中，看完后只需将光盘放回预付邮资的信封寄回即可。1999年，Netflix创新性地推出月费订阅模式，用户每月支付固定费用即可无限租赁光碟。这个模式迅速获得市场认可，到2005年，Netflix拥有3.5万部电影库存，每天寄出100万张DVD。",
"2007年是Netflix历史上的转折点。公司正式推出流媒体服务「Watch Now」，标志着从物理媒介向数字化的转型。虽然在初期流媒体库仅有1000部电影（远少于DVD的7万部），但这一战略决定最终改变了全球娱乐业的格局。2016年1月，Netflix将服务扩展至全球190多个国家和地区（中国大陆、克里米亚、朝鲜、俄罗斯、叙利亚除外）。",
"Netflix真正的爆发来自原创内容战略。2013年首部原创剧集《纸牌屋》（House of Cards）上线，这部耗资1亿美元的政治惊悚剧集不仅大获成功，更开创了"一次性整季放出"的看剧模式。随后，Netflix持续推出《怪奇物语》（Stranger Things）、《王冠》（The Crown）等经典剧集。2021年，韩国原创剧集《鱿鱼游戏》（Squid Game）成为Netflix史上观看量最高的作品，成为全球文化现象。",
"截至2026年，Netflix在全球190多个国家和地区拥有超过3.25亿付费会员。2025年，公司以824亿美元收购华纳兄弟（Warner Bros.），成为全球最大媒体集团之一。公司还拓展至移动游戏领域，通过订阅服务提供无广告手机游戏。Netflix是美国电影协会（MPA）成员，被广泛视为全球科技巨头之一。",
]
bj['languages']['zh-CN'] = nl.join(zh_cn_parts)

en_parts = [
"Netflix is the world's leading subscription-based streaming entertainment service, founded by Reed Hastings and Marc Randolph on August 29, 1997, in Scotts Valley, California. Initially launched as a DVD-by-mail rental service, Netflix allowed customers to order movies online and receive them in distinctive red envelopes through the postal service. After watching, customers would return the DVD in the same prepaid envelope, and Netflix would send the next title from their queue.",
"In September 1999, Netflix introduced a monthly subscription model that eliminated late fees and per-rental charges — a game-changer for the industry. By 2005, the company's library had grown to 35,000 film titles, and Netflix was shipping 1 million DVDs every single day. The company's Red Envelope Entertainment division even began producing original content and distributing independent films.",
"The watershed moment came in January 2007, when Netflix launched its streaming media service, originally called 'Watch Now.' Although the streaming library initially contained only 1,000 titles (compared to 70,000 on DVD), this strategic pivot would ultimately reshape the entire entertainment landscape. By January 2016, Netflix had expanded its streaming service to 190 countries. The company's DVD-by-mail service continued operating in the US until September 2023.",
"Netflix's original content strategy began in earnest in 2013 with the release of House of Cards, a $100 million political drama that set new standards for streaming production quality and pioneered the 'all episodes at once' release model. This was followed by an extraordinary lineup: Stranger Things (sci-fi horror), The Crown (historical drama), Narcos (crime drama), and the global phenomenon Squid Game (2021), a Korean survival drama that became Netflix's most-watched series of all time. Netflix Originals have collectively won hundreds of Emmy Awards.",
"In 2025, Netflix announced the acquisition of Warner Bros. for $82.4 billion, marking one of the largest media consolidation deals in history. Beyond streaming, the company has expanded into mobile gaming, offering ad-free games as part of its subscription package. With over 325 million paid memberships across 190+ countries as of 2026, Netflix is a member of the Motion Picture Association (MPA) and is consistently ranked among the world's most influential technology companies. The service is available in multiple languages and supports various device platforms from smart TVs to smartphones.",
]
bj['languages']['en'] = nl.join(en_parts)

ja_parts = [
"Netflix（ネットフリックス）は、リード・ヘイスティングス（Reed Hastings）とマーク・ランドルフ（Marc Randolph）によって1997年8月29日に米国カリフォルニア州スコッツバレーで設立された、世界最大級の定額制動画配信サービスである。",
"当初はDVD郵送レンタル事業としてスタート。利用者はオンラインで映画を注文すると、赤い封筒でDVDが自宅に届き、見終わったら同じ封筒で返送する仕組みだった。1999年に月額定額制を導入し、2005年には3万5000作品の在庫を誇り、毎日100万枚のDVDを発送するまでに成長した。",
"2007年1月、Netflixはストリーミング配信サービス「Watch Now」を開始。当初の配信作品は1000作品と限られていたが（DVDは7万作品）、この決断が後にエンターテインメント産業を根本から変えることになる。2016年1月にはサービスを190カ国に拡大。2023年9月まで米国内でDVD郵送サービスも継続していた。",
"Netflixの最大の転機はオリジナルコンテンツ戦略である。2013年、1億ドルを投じた政治サスペンス『ハウス・オブ・カード』をリリース。全話一挙公開という新しい視聴スタイルを確立し、業界に衝撃を与えた。その後も『ストレンジャー・シングス』『ザ・クラウン』『ナルコス』など数々の名作を生み出し、2021年には韓国ドラマ『イカゲーム』がNetflix史上最も視聴された作品となった。オリジナル作品は数百のエミー賞を獲得している。",
"2025年、Netflixは824億ドルでワーナー・ブラザースを買収。また、モバイルゲーム事業にも進出し、加入者に広告なしのゲームを提供している。2026年現在、190カ国以上で3億2500万以上の有料会員を有し、米国映画協会（MPA）のメンバーとして世界のエンターテインメント業界を牽引している。多言語対応でスマートテレビからスマートフォンまで幅広い端末で視聴可能。",
]
bj['languages']['ja'] = nl.join(ja_parts)

ko_parts = [
"Netflix(넷플릭스)는 리드 헤이스팅스(Reed Hastings)와 마크 랜돌프(Marc Randolph)가 1997년 8월 29일 미국 캘리포니아주 스콧츠밸리에서 설립한 세계 최대 규모의 구독 기반 스트리밍 엔터테인먼트 서비스입니다.",
"DVD 우편 대여 사업으로 시작하여, 고객이 온라인으로 영화를 주문하면 빨간 봉투에 담긴 DVD가 집으로 배송되는 방식이었습니다. 1999년 월정액 구독 모델을 도입하여 업계에 혁신을 가져왔고, 2005년에는 3만 5000편의 영화를 보유하며 매일 100만 장의 DVD를 발송할 정도로 성장했습니다.",
"2007년 1월, Netflix는 스트리밍 서비스 'Watch Now'를 출시했습니다. 초기 스트리밍 라이브러리는 1000편에 불과했지만(DVD는 7만 편), 이 전략적 전환은 전 세계 엔터테인먼트 산업의 판도를 바꾸었습니다. 2016년 1월에는 서비스를 190개국으로 확대했습니다. DVD 우편 서비스는 2023년 9월까지 미국 내에서 계속 운영되었습니다.",
"Netflix의 가장 중요한 전환점은 오리지널 콘텐츠 전략이었습니다. 2013년 1억 달러를 투자한 정치 스릴러 《하우스 오브 카드》를 첫 오리지널 시리즈로 공개하여 에피소드를 한 번에 공개하는 새로운 시청 방식을 도입했습니다. 이후 《기묘한 이야기》《더 크라운》《나르코스》등 수많은 명작을 제작했으며, 2021년에는 한국 콘텐츠 《오징어 게임》이 Netflix 사상 가장 많이 시청된 작품이 되며 글로벌 문화 현상으로 자리 잡았습니다.",
"2025년 Netflix는 824억 달러에 워너 브라더스를 인수했습니다. 또한 모바일 게임 분야로 진출하여 구독자에게 광고 없는 게임을 제공하고 있습니다. 2026년 현재 190개국 이상에서 3억 2500만 명 이상의 유료 회원을 보유하고 있으며, 미국 영화 협회(MPA) 회원사로서 글로벌 엔터테인먼트 산업을 선도하고 있습니다. 다양한 언어와 기기를 지원합니다.",
]
bj['languages']['ko'] = nl.join(ko_parts)

fr_parts = [
"Netflix est le leader mondial du streaming vidéo par abonnement, fondé par Reed Hastings et Marc Randolph le 29 août 1997 à Scotts Valley, en Californie. À l'origine, l'entreprise était un service de location de DVD par correspondance : les clients commandaient des films en ligne, les recevaient dans des enveloppes rouges distinctives, et les retournaient par courrier après visionnage.",
"En septembre 1999, Netflix a introduit un abonnement mensuel forfaitaire, éliminant les frais de retard et de location à l'unité. Cette innovation a transformé l'entreprise : en 2005, la bibliothèque comptait 35 000 films et Netflix expédiait 1 million de DVD par jour. Sa division Red Envelope Entertainment commençait même à produire des contenus originaux.",
"Le tournant décisif eut lieu en janvier 2007 avec le lancement du service de streaming 'Watch Now'. Bien que la bibliothèque en ligne ne contînt initialement que 1 000 titres (contre 70 000 en DVD), cette transition stratégique allait redéfinir l'industrie mondiale du divertissement. En janvier 2016, Netflix avait étendu son service à 190 pays. Le service de location de DVD a continué jusqu'en septembre 2023 aux États-Unis.",
"La stratégie de contenu original a débuté en 2013 avec House of Cards, un drame politique de 100 millions de dollars qui a établi de nouvelles normes de qualité pour les productions de streaming, introduisant le modèle de diffusion intégrale. Sont arrivés ensuite Stranger Things, The Crown, Narcos, et le phénomène mondial Squid Game (2021), un drame de survie coréen devenu la série la plus regardée de l'histoire de Netflix. Les productions originales ont remporté des centaines de récompenses Emmy.",
"En 2025, Netflix a annoncé l'acquisition de Warner Bros. pour 82,4 milliards de dollars, l'une des plus importantes consolidations médiatiques de l'histoire. Parallèlement au streaming, l'entreprise s'est diversifiée dans le jeu mobile, proposant des jeux sans publicité aux abonnés. Avec plus de 325 millions d'abonnés payants dans plus de 190 pays, Netflix est membre de la Motion Picture Association (MPA) et figure parmi les géants technologiques les plus influents du monde.",
]
bj['languages']['fr'] = nl.join(fr_parts)

es_parts = [
"Netflix es el servicio de streaming por suscripción más grande del mundo, fundado por Reed Hastings y Marc Randolph el 29 de agosto de 1997 en Scotts Valley, California. Comenzó como un servicio de alquiler de DVD por correo: los clientes pedían películas en línea, las recibían en sobres rojos y las devolvían por correo.",
"En septiembre de 1999, Netflix introdujo un modelo de suscripción mensual fija que revolucionó la industria. Para 2005, la biblioteca contaba con 35.000 películas y Netflix enviaba 1 millón de DVD cada día. Su división Red Envelope Entertainment incluso comenzó a producir contenido original y distribuir cine independiente.",
"El punto de inflexión llegó en enero de 2007 con el lanzamiento del servicio de streaming 'Watch Now'. Aunque la biblioteca inicial solo tenía 1.000 títulos, esta decisión redefinió la industria del entretenimiento. En enero de 2016, Netflix expandió su servicio a 190 países. El servicio de DVD por correo continuó en EE.UU. hasta septiembre de 2023.",
"La estrategia de contenido original comenzó en 2013 con House of Cards, un drama político de 100 millones de dólares que estableció nuevos estándares. Le siguieron Stranger Things, The Crown, Narcos y Squid Game (2021), que se convirtió en la serie más vista de Netflix. Las producciones originales han ganado cientos de premios Emmy internacionalmente.",
"En 2025, Netflix anunció la adquisición de Warner Bros. por 82.400 millones de dólares, una de las mayores fusiones mediáticas de la historia. La empresa también se ha expandido a los juegos móviles. Con más de 325 millones de suscripciones en más de 190 países, Netflix es miembro de la MPA y uno de los gigantes tecnológicos más influyentes del mundo.",
]
bj['languages']['es'] = nl.join(es_parts)

de_parts = [
"Netflix ist der weltweit führende Streaming-Dienst für Unterhaltung, gegründet von Reed Hastings und Marc Randolph am 29. August 1997 in Scotts Valley, Kalifornien. Das Unternehmen begann als DVD-Verleih per Post: Kunden bestellten Filme online und erhielten sie in markanten roten Umschlägen.",
"Im September 1999 führte Netflix eine monatliche Flatrate ein, die Versandgebühren überflüssig machte. Bis 2005 wuchs die Bibliothek auf 35.000 Filme an, und Netflix versandte täglich eine Million DVDs. Die hauseigene Red Envelope Entertainment begann mit der Produktion erster Originalinhalte.",
"Der Wendepunkt kam im Januar 2007 mit der Einführung des Streaming-Dienstes 'Watch Now'. Obwohl die Streaming-Bibliothek zunächst nur 1.000 Titel umfasste, sollte diese Wende die gesamte Unterhaltungsbranche neu definieren. Bis Januar 2016 hatte Netflix seinen Dienst auf 190 Länder ausgeweitet.",
"Die Original-Content-Strategie begann 2013 mit House of Cards, einem 100-Millionen-Dollar-Politdrama, das neue Maßstäbe setzte und das 'Alle Folgen auf einmal'-Modell einführte. Es folgten Stranger Things, The Crown, Narcos und Squid Game (2021), die meistgesehene Serie der Netflix-Geschichte. Netflix-Originale gewannen hunderte Emmy-Auszeichnungen.",
"2025 kündigte Netflix die Übernahme von Warner Bros. für 82,4 Milliarden US-Dollar an. Neben Streaming ist das Unternehmen auch in den Mobile-Gaming-Bereich eingestiegen. Mit über 325 Millionen zahlenden Mitgliedern in mehr als 190 Ländern ist Netflix Mitglied der MPA und zählt zu den einflussreichsten Technologieunternehmen der Welt.",
]
bj['languages']['de'] = nl.join(de_parts)

pt_parts = [
"A Netflix é o maior serviço de streaming de entretenimento do mundo, fundada por Reed Hastings e Marc Randolph em 29 de agosto de 1997 em Scotts Valley, Califórnia. Começou como um serviço de aluguel de DVD pelo correio: os clientes pediam filmes online e os recebiam em envelopes vermelhos.",
"Em setembro de 1999, a Netflix introduziu um modelo de assinatura mensal fixa. Em 2005, o acervo já contava com 35.000 filmes e a Netflix enviava 1 milhão de DVDs por dia. Sua divisão Red Envelope Entertainment começou a produzir conteúdo original.",
"O ponto de virada foi em janeiro de 2007 com o lançamento do streaming 'Watch Now'. Embora a biblioteca inicial tivesse apenas 1.000 títulos, essa decisão redefiniu a indústria. Em janeiro de 2016, a Netflix expandiu para 190 países.",
"A estratégia de conteúdo original começou em 2013 com House of Cards, drama político de US$ 100 milhões. Seguiram-se Stranger Things, The Crown, Narcos e Round 6 (2021), a série mais assistida da história da Netflix. As produções originais ganharam centenas de prêmios Emmy.",
"Em 2025, a Netflix anunciou a aquisição da Warner Bros. por US$ 82,4 bilhões. Além do streaming, expandiu-se para jogos móveis. Com mais de 325 milhões de assinantes em mais de 190 países, a Netflix é membro da MPA e uma das gigantes de tecnologia mais influentes.",
]
bj['languages']['pt'] = nl.join(pt_parts)

ru_parts = [
"Netflix — ведущий в мире стриминговый сервис развлечений по подписке, основанный Ридом Хастингсом и Марком Рэндольфом 29 августа 1997 года в Скоттс-Вэлли, Калифорния. Компания начинала как служба проката DVD по почте.",
"В сентябре 1999 года Netflix ввел ежемесячную подписку. К 2005 году библиотека насчитывала 35 000 фильмов, и Netflix отправлял 1 миллион DVD ежедневно. Подразделение Red Envelope Entertainment начало производство оригинального контента.",
"Переломный момент наступил в январе 2007 года с запуском стриминга 'Watch Now'. Хотя библиотека изначально содержала лишь 1 000 наименований, этот разворот переопределил индустрию развлечений. К 2016 году Netflix расширился на 190 стран.",
"Стратегия оригинального контента началась в 2013 году с «Карточного домика» — политической драмы стоимостью 100 миллионов долларов. За ним последовали «Очень странные дела», «Корона», «Нарко» и «Игра в кальмара» (2021) — самый просматриваемый сериал в истории Netflix.",
"В 2025 году Netflix объявил о приобретении Warner Bros. за 82,4 миллиарда долларов. С более чем 325 миллионами подписчиков в более чем 190 странах Netflix является членом MPA и одним из самых влиятельных технологических гигантов мира.",
]
bj['languages']['ru'] = nl.join(ru_parts)

ar_parts = [
"نتفليكس هي خدمة البث الترفيهي الرائدة عالميًا، أسسها ريد هاستينغز ومارك راندولف في 29 أغسطس 1997 في سكوتس فالي، كاليفورنيا. بدأت كخدمة تأجير أقراص DVD عبر البريد.",
"في سبتمبر 1999، قدمت نتفليكس نموذج الاشتراك الشهري الثابت. بحلول عام 2005، ضمت المكتبة 35,000 فيلم، وكانت نتفليكس ترسل مليون قرص DVD يوميًا.",
"جاءت نقطة التحول في يناير 2007 مع إطلاق خدمة البث 'Watch Now'. على الرغم من أن المكتبة احتوت على 1,000 عنوان فقط، إلا أن هذا التحول أعاد تعريف صناعة الترفيه. بحلول 2016، وسعت نتفليكس إلى 190 دولة.",
"بدأت استراتيجية المحتوى الأصلي في 2013 بمسلسل بيت البطاقات بتكلفة 100 مليون دولار. تلتها مسلسلات أشياء غريبة والتاج ولعبة الحبار (2021) الذي أصبح المسلسل الأكثر مشاهدة في تاريخ نتفليكس.",
"في 2025، أعلنت نتفليكس عن استحواذها على وارنر براذرز مقابل 82.4 مليار دولار. مع أكثر من 325 مليون مشترك في أكثر من 190 دولة، نتفليكس عضو في MPA وواحدة من أكثر شركات التكنولوجيا تأثيرًا في العالم.",
]
bj['languages']['ar'] = nl.join(ar_parts)

# Save
json.dump(bj, open('netflix/brand.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# Verify
en = bj['languages']['en']
all_ok = True
for lang in ['zh-CN','en','ja','ko','fr','es','de','pt','ru','ar']:
    c = bj['languages'][lang]
    same = c == en if lang != 'en' else False
    thresh = 800 if lang in ('zh-CN','ja','ko') else 1500
    ok = len(c) >= thresh and not same
    icon = 'OK' if ok else 'FAIL'
    if not ok: all_ok = False
    print(f'{icon} {lang}: {len(c)} chars (need {thresh})' + (' =EN!' if same else ''))

if all_ok:
    print('ALL PASS')
else:
    print('SOME FAIL')
    exit(1)
