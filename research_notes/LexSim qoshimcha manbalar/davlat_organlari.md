# Davlat organlari saytlari LexSim uchun manba sifatida: sjco.uz, prokuratura.uz, tergov.uz

Tekshirish usuli: uchala sayt ham 2026-11-20/21 kunlari `curl` orqali bevosita ochildi. TLS yoki bloklash muammosi bo'lmadi. prokuratura.uz Vue SPA (bo'sh HTML) bo'lgani uchun uning ochiq JSON API'si JS bandle'dan topilib, to'g'ridan-to'g'ri so'raldi. Qidiruv natijalari faqat tashqi kontekst uchun ishlatildi. "TASDIQLANMAGAN" belgisi bilan berilgan narsalar o'zim tekshira olmagan da'volardir.

Avvalgi hisobot ([LexSim manbalar asosi.md](/home/xous/Desktop/gulom/lexhackaton/reports/LexSim%20manbalar%20asosi.md)) JPK 322–335 normalarini lex.uz'dan allaqachon yoritgan. Bu yerda ular takrorlanmaydi, faqat ularni to'ldiradigan idoraviy materiallar beriladi.

## 1. sjco.uz: kim yuritadi va LexSim undan nimaga tayanishi mumkin

### Takeaway
sjco.uz o'zini "Sudyalar oliy kengashi axborot tizimlari" kirish nuqtasi deb ataydi. Undagi yagona ma'lumot bazasi qaror.sjco.uz bo'lib, Kengashning 419 ta qarorini (2023–2026) PDF ko'rinishida beradi. PDF'lar IJRO.GOV.UZ tizimida ERI bilan tasdiqlangan va hujjat kodiga ega, ya'ni mazmuni haqiqiy ko'rinadi. Biroq domenning operatori shubhali: sahifada Google AdSense reklamasi bor, sayt umumiy xostingda turadi. Shuning uchun uni "Kengashning rasmiy sayti" deb hisoblamaslik kerak: hujjat matni uchun foydalanish mumkin, lekin manba sifatida PDF ichidagi IJRO kodi va lex.uz ko'rsatilsin. Odob-axloq kodeksi, malaka imtihoni testlari, sud amaliyoti sharhlari va statistika bu saytda **yo'q**.

### Cited Findings
- Bosh sahifa o'zini "O'zbekiston Respublikasi Sudyalar oliy kengashining axborot tizimlari va ochiq ma'lumot bazalariga kirish nuqtasi" deb ta'riflaydi. Unda faqat bitta bo'lim bor: "Qarorlar bazasi". Bu bazada qaror raqami, sana yoki so'z bo'yicha qidirish va PDF yuklab olish mumkin. Footer: "© O'zbekiston Respublikasi Sudyalar oliy kengashi" — [sjco.uz](https://sjco.uz/)
- Sahifadagi "Ma'lumotlarning maqomi" bandi bunday deydi: "Saytda joylashtirilgan hujjatlar rasmiy manbalardan olingan va ochiq axborot hisoblanadi. Ular axborot maqsadida qulay ko'rinishda taqdim etiladi. Hujjatning yuridik kuchga ega rasmiy nusxasi talab qilinsa, vakolatli organga murojaat qilish lozim." Bu matn sayt o'zini birlamchi rasmiy nashr deb da'vo qilmasligini ko'rsatadi — [sjco.uz](https://sjco.uz/)
- Sahifa kodida `pagead2.googlesyndication.com` (ca-pub-3201678344154874) skripti bor. Maxfiylik siyosati (oxirgi yangilanish 07.09.2026) Google Analytics, Google AdSense va DoubleClick reklama cookie'laridan foydalanilishini ochiq yozadi — [sjco.uz/maxfiylik-siyosati.html](https://sjco.uz/maxfiylik-siyosati.html)
- WHOIS ma'lumotlari: SJCO.UZ, registrator Arsenal-D, NS dns1–4.webspace.uz, yaratilgan 14-Jul-2021, yangilangan 14-Jun-2026, muddati 14-Jul-2027. Ro'yxatdan o'tkazuvchi tashkilot ko'rsatilmagan — whois.uz (`whois sjco.uz`, 2026-11-21 so'rovi)
- Kengashning eski domeni deb taxmin qilingan sjc.uz hozir cctld.uz/uzex "domen sotuvda" ko'rinishidagi to'xtab turgan (parking) sahifani ko'rsatadi — [sjc.uz](http://sjc.uz/)
- qaror.sjco.uz ro'yxatida yil filtri bor (2023–2026). Jami 419 ta qaror. Eng so'nggisi: № 2183 "Ayrim sudyalarni lavozimidan ozod etish to'g'risida", 29.10.2026. Qarorlarning asosiy turlari: sudyalarni tayinlash, ozod etish, navbatdagi o'n yillik muddatga tayinlash, vakolatni muddatidan ilgari tugatish, mukofotlash — [qaror.sjco.uz](https://qaror.sjco.uz/)
- URL sxemasi barqaror va raqamga asoslangan: HTML ko'rinishi `https://qaror.sjco.uz/pdfs/{raqam}`, PDF fayl esa `https://qaror.sjco.uz/storage/qarorlar/{raqam}.pdf` — [qaror.sjco.uz/pdfs/2166](https://qaror.sjco.uz/pdfs/2166)
- № 2166 qaror PDF'ining sarlavhasida "IJRO.GOV.UZ tizimi orqali ERI bilan tasdiqlangan, Hujjat kodi: MY68631763" yozuvi bor. Qaror "Sudyalar oliy kengashi to'g'risida"gi Qonunning 7 va 17-moddalari hamda PF-141 (21.08.2025) asosida qabul qilingan. U **Odil sudlov akademiyasining** "Sud faoliyati" magistraturasiga 60 o'rinli kvota belgilaydi (20 kunduzgi, 40 kechki). Imzo: Kengash raisi X. Yodgorov. PDF matn qatlamiga ega, pdftotext bilan o'qiladi — [qaror.sjco.uz/storage/qarorlar/2166.pdf](https://qaror.sjco.uz/storage/qarorlar/2166.pdf)
- Kengash faoliyatining huquqiy asosi "Sudyalar oliy kengashi to'g'risida"gi Qonun (O'RQ-427, 2017) — [lex.uz/docs/-3153668](https://lex.uz/uz/docs/-3153668). Unga 2021 yilda o'zgartirish kiritilgan — [lex.uz/docs/-5643174](https://lex.uz/uz/docs/-5643174)
- Kengash ma'lum qilishicha, sudyalik kurslariga kiruvchilar "talabgor" deb ataladi, "nomzod" emas. Kirish testlari va kursni tugatish nomzod bo'lishning sharti, so'ng bo'sh lavozimga ochiq tanlov o'tkaziladi — [kun.uz, 2023](https://kun.uz/news/2023/08/31/sudyalikka-talabgorlar-sinovlarda-nega-0-ball-olganiga-izoh-berildi)
- PF-141 (21.08.2025) bo'yicha talabgorlar uchun mezonlar: oliy yuridik ma'lumot, kamida 7 yil yuridik staj, yosh, tibbiy cheklovlar va xizmat intizomi — [anhor.uz](https://anhor.uz/uzl/yangiliklar/sudyalikka-nomzodlarni-saralash-mezonlar)
- Odob-axloq qoidalari: topilgan yagona rasmiy hujjat **sudyalar uchun emas**, balki **sud apparati xodimlari** uchun. Bu "Sud apparati xodimlarining odob-axloq qoidalari" (Oliy sud Rayosatining 30.05.2025 dagi RS-25-25-son qaroriga 1-ilova, 14 bet, kirill yozuvida) — [sud.uz/wp-content/uploads/2025/11/Odob.pdf](https://sud.uz/wp-content/uploads/2025/11/Odob.pdf)
- 08.06.2026 dagi Prezident farmoni Oliy sud huzurida komplayens-nazorat xizmatini tuzadi. Bu xizmat kasbiy etika talablariga rioya qilinishini ham kuzatadi. Shu farmon sudyalar daromadini elektron deklaratsiya qilish tizimini ham joriy etadi (01.09.2026 gacha) — [anhor.uz](https://anhor.uz/uzl/news/sudyalar-daromadlarini-deklaratsiya-qilish-tizimi)

### Inferences
- Mazmun haqiqiy ko'rinadi: hujjatlar IJRO ERI kodi bilan keladi va Kengash raisining imzosi bor. Operator esa noaniq. Reklama va umumiy xosting davlat organi saytiga xos emas. Ehtimol bu Kengash buyurtmasi bilan ishlaydigan pudratchi yoki norasmiy agregator. LexSim UI'da manbani "Sudyalar oliy kengashi qarori № X (IJRO kodi …)" deb ko'rsatishi kerak, "sjco.uz rasmiy sayti" deb emas.
- LexSim uchun foydasi cheklangan, lekin aniq:
  - AI generatsiyasida haqiqiy sudya ismlari va tayinlanishlarini **ishlatmaslik** kerak. Bu qarorlarda real shaxslar ko'rsatilgan.
  - "Sudya kim va qanday tayinlanadi" mavzusidagi o'quv modulida esa qaror turlari ko'rsatib beriladi: 5 yillik birinchi muddat, 10 yillik navbatdagi muddat, ozod etish asoslari.
- "Sudyalar oliy maktabi" hozir 2166-qarorda **Odil sudlov akademiyasi** deb atalmoqda. Qayta tashkil etilgan bo'lishi mumkin (TASDIQLANMAGAN). LexSim matnlarida yangi nom ishlatilsin.
- AI sudya xulq-atvorini sozlash uchun sjco.uz'da material yo'q. Buning o'rniga quyidagilardan foydalanish mumkin:
  - "Sudlar to'g'risida"gi Qonun (lex.uz)
  - Suddagi tartib haqidagi normalar (FPK/IPK/JPK)
  - Oliy sud Rayosatining RS-25-25 qoidalari (faqat sud apparati, masalan sud kotibi xulqi uchun)

### Gaps
- Kengashning hozirgi rasmiy veb-sayti qaysi domenda ekanini aniqlay olmadim. sjc.uz to'xtab turibdi, sjco.uz esa reklamali. Qidiruv ham rasmiy domenni bermadi ([websearch natijalari](https://anhor.uz/uzl/news/prezident-sudyalar-oliy-kengashi)).
- "Sudyalar odob-axloq kodeksi" degan alohida hujjat lex.uz'da yoki boshqa joyda topilmadi. U yo boshqa nom bilan qabul qilingan, yo umuman yo'q. Bu ochiq savol.
- Sudyalikka kirish testlarining savollari, formati va o'tish bali hech qayerda ochiq e'lon qilinganini topmadim.
- sjco.uz'da foydalanish shartlari yoki litsenziya yo'q (faqat maxfiylik siyosati bor). Rus va ingliz tilidagi versiyalar ham ko'rinmadi, faqat o'zbek lotin yozuvi bor.

## 2. prokuratura.uz: Bosh prokuratura sayti, undagi materiallar va ularni olish yo'li

### Takeaway
prokuratura.uz — Bosh prokuraturaning rasmiy sayti. Sahifa sarlavhasi "Бош прокуратура". Sayt to'liq JS SPA, lekin orqasida autentifikatsiyasiz ishlaydigan JHipster JSON API bor. Bu API orqali quyidagilarni toza ko'rinishda olish mumkin:
- 2026 yil yanvar–oktabr oylari uchun murojaatlar statistikasi
- normativ hujjatlar ro'yxati (lex.uz havolalari bilan)
- ochiq ma'lumotlar (asosan Excel)
- savol-javob, mavzular bo'yicha toifalangan

Saytda normativ matnning o'zi yo'q, faqat lex.uz'ga havolalar bor. Ariza yoki shikoyat shablonlari va prokurorning fuqarolik yoki iqtisodiy sudga qo'shilishi haqidagi tushuntirishlar API'da topilmadi.

### Cited Findings
- HTML'da faqat `<title>Бош прокуратура</title>` va `<meta name=description content="Bosh prokuratura">` bor. Kontent `/js/app.*.js` SPA orqali yuklanadi — [prokuratura.uz](https://prokuratura.uz/)
- SPA marshrutlari JS bandle'dan olindi. LexSim uchun muhimlari:
  - `/murojaatlar`, `/murojaat_monitoring`, `/my-applications` (sso.egov.uz OneID orqali kiriladi)
  - `/savol-javob`, `/sudlarda`, `/tadbirkorlik`, `/qonunchilik`, `/hujjatlar`, `/ochiqmalumot`
  - `/korrupsiyaxabar`, `/ishonchtel`, `/jinoyatchilikkaqarshi`, `/voyagayetmaganlar`, `/aliment`

  Tashqi havolalar: navbat.prokuratura.uz (qabulga navbat olish) va proacademy.uz — [prokuratura.uz/js/app.607e30b3.js](https://prokuratura.uz/js/app.607e30b3.js)
- `GET /api/murojaat-stats-for-web-page` "2026 yilning yanvar–oktabr oylarida ko'rib chiqilgan jismoniy va yuridik shaxslarning murojaatlari" statistikasini qaytaradi:

  | Ko'rsatkich | Qiymat |
  |---|---|
  | Jami murojaatlar | 333 327 |
  | Ko'rib chiqilgan | 199 211 |
  | Jarayonda | 5 231 |
  | Huquqi tiklangan shaxslar | 61 912 |
  | Jami qabul | 247 164 |
  | Sayyor va ommaviy qabul | 60 371 |

  Manba: [prokuratura.uz/api/murojaat-stats-for-web-page](https://prokuratura.uz/api/murojaat-stats-for-web-page)
- `GET /api/category-for-open-card-documents` hujjat toifalarini qaytaradi:
  - 14 — Normativ-huquqiy hujjatlar
  - 13 — NHH loyihalari
  - 12 — O'z kuchini yo'qotgan hujjatlar
  - 9 — Ichki idoraviy hujjatlar

  Har bir toifada lotin, kirill va rus tilidagi sarlavhalar bor — [API](https://prokuratura.uz/api/category-for-open-card-documents)
- `GET /api/documents-links-for-web-page?categoryId=14&page=0&size=N` sahifalangan ro'yxat qaytaradi. Har bir yozuvda sarlavha va lex.uz havolasi (`documentLink`) bor. Masalan:
  - Konstitutsiya → lex.uz/docs/20596
  - "Prokuratura to'g'risida"gi Qonun → lex.uz/docs/106197
  - PF "Prokuratura organlari to'g'risida" → lex.uz/docs/213387

  Ya'ni saytda normativ matnning o'zi emas, lex.uz'ga ishora turadi — [API](https://prokuratura.uz/api/documents-links-for-web-page?categoryId=14&page=0&size=10)
- `GET /api/category-for-open-card-all-for-web` ikki toifani qaytaradi: "Ochiq ma'lumotlar" (id 1) va "Apostil qo'yish davlat xizmati reyestri" (id 6). `open-data-for-web/?categoryId=1&page=0` esa asosan Excel fayllarni beradi: xizmat uylari, avtotransport, xarid komissiyalari tarkibi. Fayllar `/api/download/` orqali yuklanadi. Bular jinoyat yoki sud statistikasi emas, ma'muriy ma'lumotlar — [API](https://prokuratura.uz/api/open-data-for-web/?categoryId=1&page=0&size=50)
- `GET /api/blogs-case-for-web-page` savol-javob mavzularini qaytaradi:
  - Xizmatga qabul
  - Tadbirkorlar huquqlari
  - Prokuratura organlariga murojaat qilish
  - Bolalar va ayollar huquqlari
  - Energetika, qurilish va ekologiya sohasidagi qonunbuzilishlar
  - Mansabdor shaxslar jinoyatchiligi
  - va boshqalar

  `blogs-for-web-site/list?page=0&size=N` esa savol-javoblarning o'zini (HTML `answer` maydoni bilan, rus va o'zbek kirill tillarida) beradi. Ko'rilgan namunalar asosan kadrlar masalasiga oid edi — [API](https://prokuratura.uz/api/blogs-case-for-web-page), [API](https://prokuratura.uz/api/blogs-for-web-site/list?page=0&size=5)
- API ma'lumotlarida to'rt til maydoni bor: `titleUz` (kirill), `titleUzLat`/`nameUzLat`, `titleRu`, `nameEn`. Demak sayt uz-lat, uz-cyr, ru va qisman en tillarida ishlaydi — [API categories/all](https://prokuratura.uz/api/categories/all)
- Murojaat yuborish API'si: `api/save-murojaat`, `api/confirm-murojaat/`, `api/all-regions`, `api/districts-by-region/`. Kirish sso.egov.uz OneID orqali — [app.js](https://prokuratura.uz/js/app.607e30b3.js)

### Inferences
- Shikoyat bosqichi uchun prokuratura.uz'dan oladigan asosiy narsalar:
  - Haqiqiy murojaat oqimining tuzilmasi: OneID orqali kirish → hudud va tuman tanlash → matn → tasdiqlash → `my-applications` sahifasida holatni kuzatish. LexSim DXM/prokuraturaga shikoyat UI'sini shunga o'xshatib qurishi mumkin.
  - "Huquqi tiklangan" ulushi realistik o'yin balansi uchun: 61 912 / 199 211 ≈ 31%. Bu 2026 yil yanvar–oktabr ma'lumoti.
- API hujjatlashtirilmagan va norasmiy. Endpointlar yoki JS hash o'zgarishi mumkin. Shuning uchun real vaqtda bog'lanish o'rniga statik snapshot (sana bilan) korpusga saqlansin.
- Prokurorning fuqarolik yoki iqtisodiy ishlardagi roli va shikoyat tartibi uchun normativ asos baribir lex.uz'da:
  - "Prokuratura to'g'risida"gi Qonun lex.uz/docs/106197 (prokuratura API'si aynan shu havolani beradi)
  - "Jismoniy va yuridik shaxslarning murojaatlari to'g'risida"gi Qonun
  - FPK/IPK'dagi prokuror ishtiroki moddalari

### Gaps
- `/sudlarda` (prokurorning sudlardagi ishtiroki), `/qonunchilik` va `/tadbirkorlik` sahifalari mazmuni API'dan chiqarilmadi. Ular qaysi endpointga bog'langani topilmadi (ehtimol `news/page/category/...`). Prokurorning FPK/IPK'dagi ishtiroki bo'yicha tushuntiruvchi materiallar bor-yo'qligi TASDIQLANMAGAN.
- Jinoyatchilik statistikasi (o'g'irlik soni va h.k.) prokuratura.uz API'sida topilmadi.
- Shikoyat yoki apellatsiya namunalari (shablonlar) topilmadi.
- Foydalanish shartlari yoki mualliflik huquqi haqidagi sahifa topilmadi.
- "Tipik qonunbuzilishlar sharhi" kabi tahliliy hujjatlar topilmadi.

## 3. tergov.uz: qaysi organ va tergov yo'li uchun nimalar beradi

### Takeaway
tergov.uz — **Ichki ishlar vazirligi huzuridagi Tergov departamenti** sayti. Bu Tergov qo'mitasi emas, departament IIV tarkibida. Rahbari IIV vaziri o'rinbosari – Tergov departamenti boshlig'i polkovnik R. Ashropov. Sayt sarlavhasi yonida "Test rejimida" yozuvi bor.

LexSim'ning o'g'irlik yoki politsiya yo'li uchun eng qimmatli material — "Ko'p so'raladigan savollar" sahifasi. Unda aynan ariza, anonim xabar, muddatlar, ish materiallari bilan tanishish va xatlov haqida JPK'ga asoslangan javoblar bor, jumladan "qo'yim o'g'irlandi, arizam hal bo'lmayapti" degan savol. Bundan tashqari Oliy sud Plenumi qarorlarining .doc nusxalari va "Huquqiy asoslar" bo'limidagi lex.uz havolalari bor. Onlayn ariza o'rniga "Virtual qabulxona" bor: rahbarga murojaat yuboriladi va holati tekshiriladi.

### Cited Findings
- Sahifa sarlavhasi: "O'zbekiston Respublikasi Ichki ishlar vazirligi huzuridagi Tergov departamenti" (ruscha: "Следственный Департамент при Министерстве Внутренних дел"). Sarlavha yonida "Test rejimida" yozuvi bor. Til versiyalari: `/uz`, `/oz` (kirill), `/ru` — [tergov.uz](https://www.tergov.uz/)
- Qabul kunlari sahifasi: Ashropov Ramazon Axmatxo'jayevich — "IIV vaziri o'rinbosari – Tergov departamenti boshlig'i, polkovnik", har seshanba qabul qiladi. Manzil: Toshkent, Yakkasaroy t., Yu.Rajabiy ko'chasi, 1-uy. Sahifada hududiy tergov boshqarmalari rahbarlari ham telefonlari bilan berilgan — [tergov.uz/uz/reception](https://www.tergov.uz/uz/reception)
- Departament vazifalari: tergov amaliyotini tahlil qilish, IIO tergov bo'linmalarini muvofiqlashtirish, surishtiruv va dastlabki tergovda uslubiy yordam berish, o'ta murakkab va viloyatlararo jinoyatlarni bevosita tergov qilish — [tergov.uz/uz/menu/osnovnye-zadachi-i-funktsii-departamenta](https://www.tergov.uz/uz/menu/osnovnye-zadachi-i-funktsii-departamenta)
- "Faoliyatning huquqiy asoslari" sahifasi faqat lex.uz havolalaridan iborat:
  - Konstitutsiya
  - "Ichki ishlar organlari to'g'risida"gi O'RQ-407 (lex.uz/docs/3027843)
  - PF-5005
  - PQ-2898 (17.04.2017, tergov sohasini takomillashtirish; lex.uz/docs/3180665)
  - PF-5268 (2017)
  - 2020 yildagi farmon (old.lex.uz/docs/-4939467)
  - PQ-105 (28.01.2022, ishni sudga qadar yuritishda yagona idoralararo elektron hamkorlik tizimi; old.lex.uz/docs/-5840465)

  Manba: [tergov.uz/uz/menu/pravovye-osnovy-dejatelnosti](https://www.tergov.uz/uz/menu/pravovye-osnovy-dejatelnosti)
- Diqqat: shu sahifada 2020 yil 10 avgustdagi farmon ham "PF-5268" raqami bilan ko'rsatilgan. Bu ehtimol saytdagi xato, chunki PF-5268 — 2017 yilgi farmon. Raqamni lex.uz'dan tekshirish kerak — [tergov.uz](https://www.tergov.uz/uz/menu/pravovye-osnovy-dejatelnosti)
- "Ko'p so'raladigan savollar" sahifasidagi savollar (har biriga JPK moddalariga asoslangan javob berilgan, masalan xatlov uchun JPK 290). Ro'yxat to'liq ko'chirilgan:
  - Ko'char va ko'chmas mulkni xatlovdan chiqarish tartibi
  - Amnistiya aktini qo'llash
  - Jinoyat ishi materiallaridan nusxa olish mumkinmi
  - Tasdiqlanmagan ariza muallifining javobgarligi
  - Tuhmat qiluvchi arizalar yozilganda kimga va qanday murojaat qilish
  - Ish qo'zg'atish uchun ariza shartmi
  - Firibgarlik haqidagi arizam bo'yicha qanday chora ko'riladi va menga xabar beriladimi
  - "Uyimdagi bir bosh qo'yim o'g'irlandi, murojaatim hal qilinmayapti — arizam ko'rib chiqilmay qolishi mumkinmi, buning uchun javobgarlik bormi?"
  - Ism-sharif ko'rsatilmagan (anonim) ariza tekshiriladimi
  - Qo'shni bilan janjal haqidagi arizani ko'rib chiqish muddati qonunda belgilanganmi
  - (va xodimlar ta'tillari haqidagi savol)

  Manba: [tergov.uz/uz/question](https://www.tergov.uz/uz/question)
- "Virtual qabulxona" — Tergov departamenti boshlig'iga murojaat yuborish formasi. Maydonlar: ism, familiya, telefon, viloyat, tuman, manzil, matn, "savolimni nashr qilishga ruxsat beraman" belgisi. Murojaat holatini raqam va kod orqali tekshirish mumkin. Telegram bot ham bor: t.me/tergov_bot — [tergov.uz/uz/virtual](https://www.tergov.uz/uz/virtual)
- "Oliy sud Plenumi qarorlari" bo'limida qarorlar .doc/.docx ko'rinishida `/uploads/docs/{hash}.doc` manzillarida turadi (kirill yozuvida). Masalan, "Далиллар мақбуллигига оид жиноят-процессуал қонуни нормаларини қўллашнинг айрим масалалари тўғрисида" — [tergov.uz/uz/menu/postanovlenija-plenuma-verhovnogo-suda](https://www.tergov.uz/uz/menu/postanovlenija-plenuma-verhovnogo-suda)
- "Tergov amaliyoti" jurnali: ISSN 2181-2543, 08.09.2021 da 1209 raqami bilan ro'yxatga olingan, OAK ro'yxatiga kiritilgan. Saytdagi yuklab olish havolasi bo'sh (`/uploads/docs/`, 0.00 Mb) — [tergov.uz/uz/menu/seldstvennaja-praktika-](https://www.tergov.uz/uz/menu/seldstvennaja-praktika-)
- Bosh sahifadagi yangiliklar va "investigations" bo'limida real ishlar bo'yicha xabarlar bor. Masalan, "Yashnobod tumanida ikki mlrd so'm o'g'irlagan shaxslarga hukm chiqarildi", "Samarqandda kvartiradan 120 mln so'mlik oltin o'g'irlandi". Shuningdek "Qidiruvdagilar" (`/uploads/wanted/*.pdf`) bo'limi bor. `/uz/documents` sahifasi 404 qaytaradi — [tergov.uz](https://www.tergov.uz/)

### Inferences
- LexSim'ning o'g'irlik yo'li uchun FAQ — "talaba savoli → rasmiy javob" juftliklarining tayyor oltin to'plami. Ularni AI guvoh yoki jabrlanuvchi dialoglari va baholash rubrikasi uchun yuklab olish tavsiya etiladi. Ayniqsa quyidagi mavzular foydali:
  - anonim ariza (JPK 323)
  - ko'rib chiqish muddati (JPK 329)
  - ariza muallifining javobgarligi (JK 237 — bila turib yolg'on xabar)

  Moddaga havolalarni lex.uz'dagi JPK bilan solishtirib tekshirish kerak.
- Rasmiy nashr qoidasi: tergov.uz'dagi Plenum .doc fayllari ikkilamchi nusxa. Rasmiy matn sud.uz yoki lex.uz'dan olinsin, tergov.uz esa "qaysi Plenumlar tergovchi uchun muhim" degan tanlov ro'yxati sifatida ishlatilsin.
- Yangiliklar va qidiruvdagilar ro'yxatida real shaxslarning ma'lumotlari bor. Ularni korpusga olmaslik kerak. Ko'pi bilan anonimlashtirilgan holda syujet ilhomi sifatida ishlatish mumkin, chunki AI-generatsiya qilingan ishlar real shaxslarga o'xshab qolmasligi lozim.
- Onlayn ariza (jinoyat haqida xabar) tergov.uz orqali qabul qilinmaydi, saytda faqat rahbarga murojaat formasi bor. Shuning uchun LexSim'ning politsiyaga ariza bosqichi JPK 322–324 dagi yozma yoki og'zaki shaklga asoslansin, avvalgi hisobotda bayon qilinganidek.

### Gaps
- "Huquqiy maslahat" va "Ichki hujjatlar" sahifalari ochilmadi yoki tekshirilmadi.
- Tergov statistikasi (ochilgan ishlar va h.k.) saytda topilmadi.
- Jabrlanuvchi, guvoh va gumon qilinuvchi huquqlari bo'yicha alohida tushuntirish sahifasi topilmadi, faqat FAQ'da qisman bor.
- Foydalanish shartlari yoki mualliflik huquqi sahifasi topilmadi.
- Sayt "Test rejimida" yozuvini ko'rsatadi, demak URL'lar barqaror bo'lmasligi mumkin.

## 4. Kesishgan savollar: ochiq ma'lumot, huquqiy maqom, formatlar va LexSim olishi kerak bo'lgan aniq narsalar

### Takeaway
Uchala saytdan hech biri o'zi normativ matnning rasmiy manbasi emas. Normativ matnlar uchun hammasi lex.uz'ga ishora qiladi. sjco.uz bu haqda ochiq yozib qo'ygan ham. LexSim korpusiga quyidagilarni olish mumkin:
- (a) SJC qarorlari PDF'lari — faqat o'quv metama'lumoti sifatida
- (b) prokuratura API'sidan statistika va normativ hujjatlar ro'yxati snapshotlari
- (c) tergov.uz FAQ matni va huquqiy asoslar ro'yxati

Uchalasida ham ochiq litsenziya topilmadi. Shuning uchun matn olingach, iqtibos keltirilib, manba URL'i va olingan sana saqlansin.

### Cited Findings
- sjco.uz: hujjatlar "ochiq axborot", lekin "yuridik kuchga ega nusxa" emas — [sjco.uz](https://sjco.uz/)
- prokuratura.uz normativ bo'limi lex.uz havolalarini beradi — [API](https://prokuratura.uz/api/documents-links-for-web-page?categoryId=14&page=0&size=10)
- tergov.uz huquqiy asoslar bo'limi ham lex.uz havolalarini beradi — [tergov.uz](https://www.tergov.uz/uz/menu/pravovye-osnovy-dejatelnosti)
- Formatlar:

  | Sayt | Format | Til |
  |---|---|---|
  | sjco.uz | PDF (matn qatlami bor, IJRO kodi) | uz-lat |
  | prokuratura.uz | JSON API, Excel ochiq ma'lumotlar | uz-lat, uz-cyr, ru, en |
  | tergov.uz | HTML, .doc/.docx | uz, oz, ru |

  Manbalar: yuqoridagi sahifalar.

**Olinadigan yoki iqtibos keltiriladigan elementlar ro'yxati**

| # | Element | URL | Foydalanish |
|---|---|---|---|
| 1 | Tergov departamenti FAQ (11 ta savol-javob) | https://www.tergov.uz/uz/question | Politsiya yo'li dialoglari va rubrikasi. JPK bilan solishtirish kerak |
| 2 | Tergov departamenti huquqiy asoslari (PQ-2898, PQ-105 va b.) | https://www.tergov.uz/uz/menu/pravovye-osnovy-dejatelnosti | Iqtibos. Raqamlarni lex.uz'dan tekshirish |
| 3 | Plenum qarorlari ro'yxati (tergov uchun tanlangan) | https://www.tergov.uz/uz/menu/postanovlenija-plenuma-verhovnogo-suda | Ro'yxat sifatida. Matnni lex.uz yoki sud.uz'dan olish |
| 4 | Departament vazifalari | https://www.tergov.uz/uz/menu/osnovnye-zadachi-i-funktsii-departamenta | "Tergovchi kim" o'quv kartasi |
| 5 | Prokuratura murojaatlar statistikasi (2026 yanvar–oktabr) | https://prokuratura.uz/api/murojaat-stats-for-web-page | Shikoyat bosqichi balansi. Sanali snapshot |
| 6 | Prokuratura normativ hujjatlar ro'yxati | https://prokuratura.uz/api/documents-links-for-web-page?categoryId=14&page=0&size=100 | lex.uz ID'larini korpusga qo'shish |
| 7 | Prokuratura savol-javob mavzulari va javoblari | https://prokuratura.uz/api/blogs-case-for-web-page ; https://prokuratura.uz/api/blogs-for-web-site/list?page=0&size=50 | Murojaat bosqichi FAQ. Sifatini tekshirish kerak |
| 8 | "Prokuratura to'g'risida"gi Qonun | https://lex.uz/docs/106197 | Prokurorning roli (birlamchi manba) |
| 9 | SJC qarorlari (masalan № 2166, kvota) | https://qaror.sjco.uz/storage/qarorlar/2166.pdf | Sud tizimi moduli. Real ismlarni generatsiyada ishlatmaslik |
| 10 | "Sudyalar oliy kengashi to'g'risida"gi Qonun | https://lex.uz/uz/docs/-3153668 | Sudyalarni tanlash va tayinlash (birlamchi manba) |
| 11 | Sud apparati xodimlarining odob-axloq qoidalari (RS-25-25, 30.05.2025) | https://sud.uz/wp-content/uploads/2025/11/Odob.pdf | AI sud kotibi yoki xodim xulqi. Sudyaga taalluqli emas |

### Inferences
- AI sudya xulqi va baholash uchun uchala sayt ham asosiy manba bo'la olmaydi. Bu yo'nalish sud.uz va lex.uz kodekslariga tayanadi.
- Barcha manbalar uchun ishonchlilik darajasini korpus metama'lumotida belgilash tavsiya etiladi:
  - lex.uz — normativ
  - IJRO kodli PDF — rasmiy hujjat nusxasi
  - idoraviy FAQ — tushuntiruvchi
  - yangilik — faktik, real shaxslar bor

### Gaps
- Uchala sayt uchun ham robots.txt va foydalanish shartlari tekshirilmadi, faqat sjco.uz maxfiylik siyosati o'qildi. Ommaviy yuklab olishdan oldin robots.txt'ni tekshirish kerak.
- sjco.uz egasini rasmiy tasdiqlash uchun Kengashning rasmiy kanalidan (Telegram yoki matbuot xizmati) sjco.uz'ga havola topilmadi.
