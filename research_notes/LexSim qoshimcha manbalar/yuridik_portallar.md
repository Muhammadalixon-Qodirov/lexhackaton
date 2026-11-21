# Yuridik yordam va huquqiy axborot portallari: advokat.uz, advice.adliya.uz, norma.uz, advokatpro.uz — LexSim uchun manba sifatida

Tadqiqot sanasi: 2026-11-20 (server vaqti 21.11.2026). Usul: curl va WebFetch orqali to'g'ridan-to'g'ri ochildi, Wayback Machine CDX/snapshotlari ishlatildi. Har bir topilmada qayerdan olingani yozilgan. Avvalgi topilmalar takrorlanmaydi (`research_notes/LexSim manbalar asosi/advokatpro_portallar.md`, `reports/LexSim manbalar asosi.md`), faqat yangilari qo'shilgan.

## 1. advice.adliya.uz: kim yuritadi, qaysi savollar ko'p, Q&A ochiqmi, LexSim konsultatsiya urug'i sifatida ishlata oladimi, shartlar

### Takeaway
advice.adliya.uz alohida Adliya vazirligi xizmati emas. U ochiladi va **advice.uz** bilan aynan bir xil saytni ko'rsatadi: "Мадад" NNT yuritadigan bepul huquqiy maslahat portali. U Adliya vazirligi va Buyuk Britaniya elchixonasi hamkorligida, Citizens Advice modeli asosida yaratilgan. Portalda tematik maqolalar, har bo'limda "Савол-жавоблар" va "Ҳаётий мисоллар" sahifalari, Top-10 savol va onlayn chat bor. Hammasi login'siz ochiq. "Ҳаётий мисоллар" formati ("фуқаро Д. ... Ечим: Оила кодекси 39-модда ...") LexSim konsultatsiya ssenariylari uchun eng yaxshi urug' manbai. Lekin ochiq qayta foydalanish litsenziyasi yo'q, shuning uchun faqat faktlarni qayta yozib, havola bilan ishlatish kerak.

### Cited Findings
- **Domen.** https://advice.adliya.uz HTTP 200 bilan `/uz` ga ochiladi. Sahifa sarlavhasi "Advice.uz", footerda "© 2019-2026 "Мадад" муассаса шаклидаги нодавлат нотижорат ташкилоти". https://advice.uz → 302 → advice.uz/uz, kontent bir xil — to'g'ridan-to'g'ri curl tekshiruvi, 2026-11-20 ([advice.adliya.uz](https://advice.adliya.uz/uz); [advice.uz](https://advice.uz/uz)). Xulosa: bu bitta portal ikki domenda. Adliya domeni rasmiy maqom berganmi yoki shunchaki ko'zgu (mirror)mi, aniqlanmadi.
- **Kelib chiqishi.** Portalni yaratish vazifasi Prezidentning 09.01.2019 dagi "Жамиятда ҳуқуқий онг ва ҳуқуқий маданиятни юксалтириш тизимини тубдан такомиллаштириш тўғрисида"gi Farmonida belgilangan. "Бирламчи бепул ҳуқуқий маслаҳат" loyihasi Adliya vazirligi va Buyuk Britaniya elchixonasi bilan hamkorlikda, "Citizens Advice" tajribasi asosida amalga oshirilgan. Bureaular 2019-yilda 28 ta edi, 2022-yilda 73 taga yetgan — [advice.uz/uz/page/about](https://advice.uz/uz/page/about)
- **Hozirgi hajm (bosh sahifa hisoblagichlari, 2026-11-20).** 149 ta huquqiy maslahat byurosi (Toshkent viloyati 17, Farg'ona 17, Samarqand 14 va h.k.); "Кунлик бепул юридик ёрдам" bloki: 1008 ishonch telefoni — 331, 1148 ishonch telefoni — 443, onlayn murojaatlar — 301, oflayn murojaatlar — 1230; jami tayyorlangan protsessual hujjatlar — 10 069. Saytda yana USAID / Tetra Tech DPK moliyalashtirishi haqida yozuv bor — [advice.uz/uz](https://advice.adliya.uz/uz). Hisoblagichlar kunlikmi yoki jami ekanini sahifa aniq aytmaydi — **tasdiqlanmagan**.
- **Maslahat tartibi.** Onlayn maslahatchi dushanba–juma 09:00–13:00 va 14:00–18:00 ishlaydi. Chat murojaatlari "Жисмоний ва юридик шахсларнинг мурожаатлари тўғрисида"gi qonun bo'yicha ko'rib chiqilmaydi, ularga real vaqtda javob beriladi. "Порталда жойлаштирилган барча маълумотлар ... тавсиявий характерга эга" — [about](https://advice.uz/uz/page/about). Sahifada "24/7 AI ёрдамчи" va "Wakil AI" bo'limi ham bor — [bosh sahifa](https://advice.adliya.uz/uz)
- **Kategoriyalar taksonomiyasi (≈60 bo'lim).**
  - Yuqori menyu: Меҳнат муносабатлари, Оилавий муносабатлар, Суд-ҳуқуқ масалалари, Фуқаролик/Миграция, Соғлиқни сақлаш, Ижтимоий ҳимоя, Таълим.
  - To'liq ro'yxatda yana: Pensiya va nafaqalar, Ишдаги муаммолар, Nikohni bekor qilish va aliment, Uy-joy, yer va ko'chmas mulk, Uy-joy ijarasi, Korrupsiya, Huquqni muhofaza qiluvchi organlar, Majburiy ijro, Харид ва хизматларда ҳуқуқлар (iste'molchi), Судга мурожаат ва ҳуқуқий ҳимоя, Transport/Avtohuquq, One ID va YaIDXP, Давлат хизматлари ва электрон мурожаатлар, Tadbirkorlik, Soliqlar, Bank, Notarial xizmatlar, Юридик хизмат (ҳуқуқий ҳужжат намуналари), Advokat xizmati, Bepul huquqiy yordam, Mediatsiya, Intellektual mulk va boshqalar.
  - Manba: [advice.uz/uz](https://advice.adliya.uz/uz)
- **Bo'limlardagi hujjatlar soni** (kategoriya sahifasidagi `/uz/document/{id}` havolalar soni, o'zim sanadim):

  | Bo'lim | Hujjatlar |
  |---|---|
  | Mehnat munosabatlari (cat/673) | 130 |
  | Transport (73) | 102 |
  | Sudga murojaat va huquqiy himoya (611) | 82 |
  | Nogironlik (590) | 81 |
  | Ta'lim (65) | 78 |
  | Davlat xizmatlari va elektron murojaatlar (72) | 69 |
  | Notarial (701) | 56 |
  | Gender (589) | 54 |
  | Uy-joy/yer (59) | 40 |
  | Sog'liq (63) | 36 |
  | Fuqarolik (61) | 33 |
  | Pensiya (64) | 31 |
  | Bank (71) | 30 |
  | Iste'molchi (74) | 24 |
  | Tadbirkorlik (69) | 22 |
  | Huquqni muhofaza organlari (549) | 21 |
  | Uy-joy ijarasi (645) | 13 |
  | Advokat xizmati (722) | 11 |
  | Hujjat namunalari (600) | 10 |
  | Ishdagi muammolar (719) | 8 |

  Manba: [cat/673](https://advice.uz/uz/category/673), [cat/611](https://advice.uz/uz/category/611) va boshqalar. Bu murojaat statistikasi emas, kontent hajmi.
- **Eng ko'p so'raladigan savollar ("ТОП-10 саволлар", 2026-11-20).**
  1. Bolalar nafaqasi;
  2. Sirtqi o'qiyotgan xodimga haq saqlangan ta'til;
  3. Tezlik oshirish bayonnomasi 48 soatda rasmiylashtirilmasa;
  4. Aliment to'lovchining xorijga chiqish taqiqini bekor qilish;
  5. Ishsizlik nafaqasi;
  6. Uy-joy subsidiyasi;
  7. Nikohni sud tartibida bekor qilish;
  8. O'zboshimcha egallangan yerga egalik huquqi;
  9. 30 yillik ijaraga berilgan ekin maydonlari;
  10. Elektron bilaguzukni rad etish.

  Manba: [advice.uz/uz](https://advice.adliya.uz/uz)
- **"Савол-жавоблар" sahifalari** (har bir bo'limga bitta yig'ma sahifa). Misollar: Oila — [document/2079](https://advice.uz/uz/document/2079) (65 532 marta o'qilgan), Sog'liq — 2088, Pensiya — 2085, Ta'lim — 2080, Sudga murojaat — 2091, Huquqni muhofaza organlari — 2837, Gender — 2821, Nogironlik — 2829, Xorijdagi fuqarolar — 2826. Javoblar normaga havola qiladi (masalan, VM 550- va 808-son qarorlari, "garov kamida 250 BHM") — [document/2079](https://advice.uz/uz/document/2079)
- **"Ҳаётий мисоллар" sahifalari** (qisqa fabula + "Ечим" + modda + "Муҳим" ogohlantirish):
  - Oila — [document/2256](https://advice.uz/uz/document/2256) (33 918 o'qish): homilador xotin bilan ajrashish (OK 39), alohida yashayotgan otaning bolalar bilan ko'rishishi, ota-onalik huquqidan mahrum qilinganning alimenti, bobo-buvidan ta'minot (OK 123), to'y xarajatlarini qaytarish.
  - Sudga murojaat — [document/2260](https://advice.uz/uz/document/2260) (31 015 o'qish): tadbirkorga nisbatan yuqori turuvchi prokuror roziligisiz jinoyat ishi qo'zg'atilishi (JPK 331), koloniyadagi mahkum bilan uchrashuv (JIK 117).
  - Boshqa ID'lar: Sog'liq — 2257, Pensiya — 2270, Gender — 2822.
- **Mehnat bo'limidagi mavzular (cat/673, cat/719):**
  - ishga qabul qilishni rad etish, dastlabki sinov, mehnat shartnomasini o'zgartirish va bekor qilish asoslari;
  - qisqartirishda kim ishda qoladi, ommaviy bo'shatish, ishdan bo'shatish nafaqasi, bo'shatishda hisob-kitob;
  - homilador va 3 yoshgacha bolali ayollar kafolatlari, haq saqlanmaydigan ta'til;
  - mehnat nizolarini ko'rish, yakka nizolarni sudda ko'rish, "Иш ҳақи кечиктирилса компенсация тўланадими?", xodimning moddiy javobgarligi.
  - Manba: [cat/673](https://advice.uz/uz/category/673), [cat/719](https://advice.uz/uz/category/719)
- **Sudga murojaat bo'limi (cat/611)** protsessual mavzularni qamraydi: даъво муддати, "Давлат божи калькулятори", apellyatsiya/kassatsiya, ariza ko'rmasdan qoldirish, sirtdan ish yuritish, "Қарз берилганлигини гувоҳлар орқали исботлаш", iqtisodiy ish (birinchi instansiya, sud xarajatlari), ma'muriy ish, himoya orderi — [cat/611](https://advice.uz/uz/category/611). Kalkulyator sahifasi ochib tekshirilmadi.
- **Forum** hozir bo'sh ("Хеч нима топилмади"), mavzu ochish uchun login kerak — [advice.uz/uz/forum](https://advice.uz/uz/forum). Demak fuqarolarning asl savollari (xom matn) ochiq bazada yo'q. Chat yozishmalari e'lon qilinmaydi.
- **Shartlar.** Footerdagi "Фойдаланиш шартлари" havolasi `/uz/page/how-it-works` ga olib boradi. U sahifada faqat maxfiylik siyosati (shaxsiy ma'lumotlar: FISh, telefon, e-mail) va bo'limlar hamda chatdan foydalanish yo'riqnomasi bor. Kontentni ko'chirish yoki qayta foydalanish haqida band ham, litsenziya ham yo'q (sahifadan "кўчир", "муаллиф", "интеллектуал" so'zlarini qidirdim — topilmadi). "Регламент" sahifasida asosiy matn chiqmadi — [how-it-works](https://advice.uz/uz/page/how-it-works), [regulations](https://advice.uz/uz/page/regulations)
- **Barqaror URL'lar.** Hujjatlar `https://advice.uz/uz/document/{id}`, bo'limlar `/uz/category/{id}`; tillar /uz, /oz, /ru, /en.
- **Yangilanish.** Yangiliklar har kuni chiqadi (20.11.2026, 19.11.2026 sanali yangiliklar); "Savol-javob" sahifalarida yangi normalar bor (masalan, VM 808-son qarori) — [bosh sahifa](https://advice.adliya.uz/uz)

### Inferences
- LexSim konsultatsiya modulida "Ҳаётий мисоллар" sahifalarini **ssenariy urug'i** sifatida ishlatish mumkin. Ish tartibi: fabula qayta yoziladi (ism, shahar, summalar o'zgartiriladi), "Ечим"dagi modda lex.uz'da tekshiriladi va AI-mijozning yashirin "to'g'ri javob" kaliti sifatida saqlanadi. "Муҳим" bloki tuzoq savol bo'ladi; masalan, OK 39 dagi cheklov xotinning o'zi talab qilganda qo'llanmaydi.
- Mehnat yo'li uchun eng ko'p material shu portalda: 130 + 8 hujjat. Bo'shatish, kechiktirilgan ish haqi uchun kompensatsiya, qisqartirish va moddiy javobgarlik — tayyor konsultatsiya va da'vo mavzulari.
- O'g'irlik/politsiya yo'li uchun "Huquqni muhofaza organlari" (cat/549, Q&A 2837) va 2260 dagi JPK misollari foydali. DXM yo'li uchun "Davlat xizmatlari va elektron murojaatlar" (cat/72, 69 hujjat) va "One ID ва ЯИДХП" bo'limlari foydali.
- Taksonomiya: advice.uz kategoriyalarini LexSim'dagi "AI case from user story" klassifikatori uchun yorliqlar to'plami sifatida olish mumkin (Mehnat / Oila-aliment / Uy-joy-ijara / Pensiya-nafaqa / Iste'molchi / Transport / Sudga murojaat / Huquqni muhofaza / Davlat xizmatlari). Kategoriya nomlari faktik ro'yxat, ijodiy asar emas.
- RAG korpusi sifatida **to'liq matnni yuklab olish tavsiya etilmaydi**. Litsenziya yo'q, matnlar Madad NNT mualliflik mehnati. Huquqiy sof yo'l: RAG lex.uz normalariga asoslanadi, advice.uz'ga faqat havola qilinadi ("qo'shimcha o'qish"). To'liq foydalanish uchun Madad NNT bilan memorandum kerak; portalda "Ҳамкорлик тўғрисида меморандумлар" bo'limi bor, ya'ni hamkorlik amaliyoti mavjud ([about](https://advice.uz/uz/page/about)).
- O'qishlar soni (65 532, 33 918, 31 015) va Top-10 qaysi mavzular ko'proq qiziqtirishini taxminan ko'rsatadi: oila/aliment, nafaqalar, mehnat ta'tillari, yo'l harakati jarimalari, yer. Bu murojaatlar statistikasi emas.

### Gaps
- advice.adliya.uz'ning Adliya vazirligiga rasmiy aloqasi (subdomen berilgani, operator shartnomasi) hujjat bilan tasdiqlanmadi — **tasdiqlanmagan**.
- Murojaatlarning kategoriyalar bo'yicha statistikasi (qaysi soha bo'yicha nechta murojaat) e'lon qilinmagan. Bosh sahifada faqat umumiy hisoblagichlar bor; "Амалга оширилган ишлар (инфографика)" havolasi ochilmadi.
- Davlat boji kalkulyatori sahifasi va "Wakil AI" ochib tekshirilmadi.
- Mehnat bo'limi uchun alohida "Savol-javob" yoki "Hayotiy misollar" sahifasi kategoriya sahifasidan topilmadi (boshqa ID ostida bo'lishi mumkin).

## 2. advokat.uz: nima u va foydali kontenti bormi

### Takeaway
advokat.uz bugun ishlamaydi: http HTTP 522 (Cloudflare), https ulanishni bermaydi. Wayback Machine'ga ko'ra bu domen 2017-yilgacha **"Karamatov va advokatlar" advokatlik firmasi**ning (xususiy tijorat firmasi; Palata ham, katalog ham emas) sayti bo'lgan. Keyin domen 2024-yilda **karamatov.uz** ga yo'naltirilgan, 2025-yil avgustdagi snapshotda esa bo'sh nginx sahifa. Firma sayti karamatov.uz da hozir ham ishlaydi. Unda shablonlar, "Буква закона" tushuntirishlari, blog va savol-javob bazasi bor, lekin yangiliklar 2017–2018-yillarda to'xtagan. LexSim uchun ahamiyati past.

### Cited Findings
- Hozirgi holat: `http://advokat.uz` → 522, `https://advokat.uz` → ulanish yo'q (curl 000) — to'g'ridan-to'g'ri tekshiruv, 2026-11-20.
- Wayback CDX yillik holatlari: 2003–2017 — 200; 2018–2019 — 301; 2021 — 200 (Parallels Plesk standart sahifasi); 2022 va 2024 — 301; 2025-02 — 522 — [web.archive.org CDX](http://web.archive.org/cdx/search/cdx?url=advokat.uz&output=txt&fl=timestamp,statuscode&collapse=timestamp:4)
- 2017-02 snapshot: sarlavha "Karamatov - ", matnda "KARAMATOV VA ADVOKATLAR", info@advokat.uz, tel. (+99871) 268-60-59 — [snapshot 20170206](http://web.archive.org/web/20170206110322/http://advokat.uz/)
- 2024-03 snapshot `https://karamatov.uz/` ga yo'naltirilgan (Location sarlavhasi). Sahifa: "Адвокатская Фирма "KARAMATOV VA ADVOKATLAR"", Toshkent, Tamaraxonum ko'chasi 9A. Bo'limlar: Шаблоны ("популярные образцы исковых заявлений, договоров, жалоб, претензий ... с рекомендациями по их заполнению"), "Буква закона" (normalar tushuntirishi), Блог, Полезное (davlat organlari kontaktlari), huquqiy atamalar lug'ati. Oxirgi yangilik 10.01.2018 — [snapshot 20240326](http://web.archive.org/web/20240326040236/http://advokat.uz/)
- 2025-08 snapshot: "Welcome to nginx!" — [snapshot 20250813](http://web.archive.org/web/20250813110216/http://www.advokat.uz/)
- karamatov.uz hozir HTTP 200 bilan ochiladi (rus tilida). Xizmatlar (jismoniy shaxslar: oilaviy nizolar, jinoyat jarayoni, meros, pensiya; yuridik shaxslar: xo'jalik nizolari, kadrlar maslahatchisi, advokatlik auditi) va "Вопросы и ответы — Поиск по базе вопросов и ответов" bor — [karamatov.uz](https://karamatov.uz/)

### Inferences
- advokat.uz'ni LexSim manbalari ro'yxatidan chiqarish kerak. U o'lik domen va rasmiy organ emas.
- karamatov.uz shablonlari va Q&A'si eskirgan bo'lishi mumkin (2018-yildan keyin yangilanmagan; yangi FPK/IPK 2018-yildan, yangi Mehnat kodeksi 2023-yildan kuchga kirgan). Ular hozirgi kodekslarga mos kelmasligi ehtimoli katta. Xususiy firma kontenti mualliflik huquqi bilan himoyalangan, foydalanish shartlari topilmadi. Tavsiya: ishlatmaslik, eng ko'pi bilan xizmat turlari ro'yxatini (konsultatsiya kategoriyalari) g'oya sifatida olish.

### Gaps
- Domenning hozirgi egasi (WHOIS, .uz registratori) tekshirilmadi.
- karamatov.uz'dagi Q&A bazasi hajmi va sanalari o'rganilmadi.

## 3. norma.uz: qaysi bo'limlar foydali, nima bepul va nima pullik, qayta foydalanish shartlari aniq qanday

### Takeaway
norma.uz — NORMA MChJ'ning tijorat portali. Ochiq qismda: "Қонунчиликдаги янгиликлар" (har kuni yangilanadigan qisqa sharhlar), "Бизнинг шарҳлар", НҲҲ лойиҳалари va "Қонун ҳужжатлари тўплами". Pullik qismda: elektron mahsulotlar (Norma AQT, nrm.uz), gazeta obunasi, seminar va kurslar. "Жавоб берамиз" xizmati va shakllar buxgalter.uz da joylashgan (avvalgi yozuvga qarang). Qayta foydalanish shartlari qat'iy: materiallardan foydalanish **faqat alohida kelishuv asosida va uning shartlarida** mumkin; ruxsatsiz ko'chirish taqiqlangan; buzish "qonunchilikni buzish" deb e'lon qilingan.

### Cited Findings
- **Foydalanish shartlari sahifasi** (05.05.2015): materiallardan, shu jumladan gazetalar va "Norma" axborot-qidiruv tizimlaridagi materiallardan foydalanish "фақат материаллардан фойдаланиш тўғрисида келишув асосида ва шартларида амалга оширилиши мумкин". "ЮҚОРИДА КЎРСАТИЛГАН ШАРТЛАРГА РИОЯ ҚИЛМАСЛИК ЎЗБЕКИСТОН РЕСПУБЛИКАСИ ҚОНУНЧИЛИГИНИ БУЗИШ ҲИСОБЛАНАДИ." Giperhavola va iqtibos uchun alohida istisno sahifada ko'rsatilmagan (WebFetch xulosasi) — [norma.uz foydalanish shartlari](https://www.norma.uz/uz/bosh_sahifa/saytda_joylashtirilgan_materiallardan_foydalanish_shartlari)
- **Footer:** "Сайт материалларини ресурс маъмурияти розилигисиз кўчириб олиш тақиқланади. © «NORMA» МЧЖ, 2007-2026". Manzil: Toshkent, Tallimarjon ko'chasi 1/1, call-markaz 1172 — [norma.uz](https://www.norma.uz/uz/)
- **Ochiq bo'limlar va URL'lar:**
  - `/uz/qonunchilikda_yangi/` — sharhlar. 2026-11 dagi misollar: "Тўловга қобилиятсизлик ишлари онлайнга ўтади: 1 декабрдан нима ўзгаради", "Жарима 60 кунда тўланмаса автомашина жарима майдончасига жойлаштирилади", "Экстремизм учун жавобгарлик чоралари ўзгартирилди", "Тадбиркорлик субъектларининг ҳуқуқий ҳимояси кучайтирилмоқда".
  - `/uz/bizning_sharhlar/`, `/uz/nhh_loyihalari`, `/uz/sobraniya_zakonodatelstva`, RSS (`/scripts/rss/3600`).
  - Manba: [norma.uz](https://www.norma.uz/uz/)
- **Pullik / obuna bo'limlari:** "Электрон маҳсулотлар" (`/glavnaya/fayly_dlya_skachivaniya`, products.norma.uz, `/updates/`), gazeta obunasi (gazeta.norma.uz/uz/obuna), seminar.cpr.uz, webinar.cpr.uz, buxgalter.academy, bir.uz testlari, knigi.uz — [norma.uz](https://www.norma.uz/uz/)
- **Kontakt formasi mavzulari:** "4. Служба «Мы отвечаем»", "5. Служба поиска документов". Ya'ni "Javob beramiz" NORMA'ning xizmati (savol yuborish shakli) — [norma.uz](https://www.norma.uz/uz/bosh_sahifa/saytda_joylashtirilgan_materiallardan_foydalanish_shartlari)
- **buxgalter.uz bepulligi:** NORMA 04.04.2020 da buxgalter.uz "яқин вақт мобайнида бепул ресурс бўлиб қолади" deb e'lon qilgan, tijorat modeliga o'tish "яхши вақтлар келгунча" kechiktirilgan, portal o'quvchilar savollariga yuristlar tushuntirishlarini e'lon qiladi (WebFetch xulosasi). Hozirgi narxlar ko'rsatilmagan — [norma.uz yangilik](https://www.norma.uz/uz/kompaniya_yangiliklari/buxgalter_uz_yaqin_vaqt_mobaynida_bepul_resurs_bulib_qoladi)
- Mehnat kodeksi va iqtisodiy nizolarga oid sharhlar uchun alohida ochiq "Kodeks sharhi" bo'limi norma.uz bosh sahifasida topilmadi. Bunday kontent pullik Norma AQT/nrm.uz ichida yoki buxgalter.uz "Kadrlar" bo'limida bo'lishi mumkin — **tasdiqlanmagan**.

### Inferences
- LexSim uchun norma.uz'ning qonuniy foydasi: (1) "Qonunchilikdagi yangiliklar" ni o'qib, qaysi norma o'zgarganini bilish va keyin uni lex.uz'da tekshirish; (2) havola berish. Matn, Q&A javoblari va shakllarni RAG korpusiga kiritish yoki ko'chirish NORMA MChJ bilan yozma kelishuvsiz **mumkin emas**. Shartlarda "foydalanish" keng ta'riflangan, shuning uchun hatto avtomatik indekslash (skreyp) ham xavfli.
- NORMA ta'lim mahsulotlariga ega (buxgalter.academy, bir.uz testlari). Shu sabab LexSim uchun potentsial litsenziya yoki hamkorlik partnyori bo'lishi mumkin, ayniqsa iqtisodiy nizolar va kadrlar ishi bo'yicha. Bu taxmin, NORMA bilan aloqa qilinmagan.

### Gaps
- Norma AQT / nrm.uz obuna narxlari topilmadi (nrm.uz bosh sahifasida narx ochiq ko'rsatilmagan).
- "Javob beramiz" javoblari bepulmi yoki faqat obunachilar uchunmi, norma.uz'da aniq yozilmagan.
- Iqtibos/giperhavola uchun maxsus ruxsat bor-yo'qligi shartlar sahifasida ko'rsatilmagan.

## 4. advokatpro.uz: avvalgi topilmalardan tashqari nima yangi

### Takeaway
Muhim yangilik yo'q. Ko'rsatkichlar avvalgidek: 14 158 modda, 185 qonun va kodeks, "16 ta tayyor shablon, izohlar bilan". Yangi topilganlar ikkita: (1) sitemap'da 87 ta pastki sitemap bor va faqat ochiq modda sahifalari (`/uz-latn/moddalar/...`) indekslangan; shablonlar, Q&A yoki sud amaliyoti sahifalari ochiq indeksda yo'q; (2) "Qonun o'zgarishlari" lentasida yangi Mehnat kodeksining **8¹-moddasi** (13.11.2026, "Меҳнат ва машғулотлар соҳасида шаҳвоний шилқимликка йўл қўймаслик") paydo bo'lgan. Bu LexSim mehnat yo'li uchun dolzarb yangi norma.

### Cited Findings
- Bosh sahifadagi ichki havolalar faqat shular: /advokatlar, /dashboard, /dashboard/tadbirkor, /login, /maxfiylik, /moddalar, /qonun-ozgarishlari, /shartlar va namuna modda sahifalari (mehk-8-1, nhhq-24, nhhq-28). Yangi bo'lim (shablonlar katalogi, kalkulyator, talabalar uchun, API) yo'q — [advokatpro.uz](https://advokatpro.uz/uz-latn)
- O'zgarishlar lentasidan: "Yangi · Mehnat kodeksi · 8¹-modda · 13.11.2026 · Mehnat va mashg'ulotlar sohasida shahvoniy shilqimlikka yo'l qo'ymaslik"; "«Normativ-huquqiy hujjatlar to'g'risida»gi qonun · 24-modda · 13.11.2026" — [advokatpro.uz](https://advokatpro.uz/uz-latn)
- Sitemap: `sitemap.xml` 87 ta pastki sitemapdan iborat. 0-sitemap'da kodeks indekslari (`/moddalar/kodeks/advq`, `/avtoroyxat` va h.k.), 1-, 2- va 86-sitemaplarda faqat `/uz-latn/moddalar/...` URL'lari (186, 30, 130, 2415 ta) — [sitemap.xml](https://advokatpro.uz/sitemap.xml)
- Oxirgi lex.uz solishtiruvi: "21.11, 05:32" — [advokatpro.uz](https://advokatpro.uz/uz-latn)

### Inferences
- MehK 8¹ (shahvoniy shilqimlik) normasini LexSim mehnat ssenariylariga "yangi norma" tuzog'i sifatida qo'shish mumkin. Matnni lex.uz'dan olish va kuchga kirish sanasini tekshirish shart — **tasdiqlanmagan** (faqat AdvokatPro lentasidan).
- Avvalgi xulosa o'zgarmaydi: AdvokatPro'dan faqat UX g'oyalari olinadi, kontent emas.

### Gaps
- Login ortidagi 16 shablon ro'yxati hali ham ko'rilmagan.

## 5. Tavsiya: LexSim nima oladi va nima olmaydi

### Takeaway
To'rt portalning hech biri ochiq litsenziya bermaydi. Eng foydalisi advice.uz/advice.adliya.uz: kategoriyalar, "Ҳаётий мисоллар" va "Савол-жавоблар". Ulardan **faktlar va tuzilma** (qayta yozilgan holda) va havola olish mumkin. NORMA kontenti kelishuvsiz umuman ishlatilmaydi. advokat.uz o'lik. AdvokatPro faqat UX namunasi.

### Cited Findings
- advice.uz'da kontentni qayta ishlatish bo'yicha band yo'q; "Фойдаланиш шартлари" maxfiylik va foydalanish yo'riqnomasidan iborat — [how-it-works](https://advice.uz/uz/page/how-it-works)
- NORMA: faqat kelishuv asosida — [norma.uz shartlar](https://www.norma.uz/uz/bosh_sahifa/saytda_joylashtirilgan_materiallardan_foydalanish_shartlari)
- AdvokatPro: dizayn, dastur va baza tuzilmasi operatorga tegishli, avtomatik ommaviy so'rovlar taqiqlangan — [shartlar](https://advokatpro.uz/uz-latn/shartlar) (avvalgi yozuvdan)

### Inferences
| Manba | LexSim OLISHI MUMKIN | OLMASLIGI KERAK |
|---|---|---|
| advice.uz / advice.adliya.uz | Kategoriyalar ro'yxati (domen taksonomiyasi); "Hayotiy misollar"dan qayta yozilgan fabulalar (ism, summa, joy o'zgartirilgan), modda esa lex.uz'dan tekshirilgan; Top-10 mavzulardan ustuvorlik g'oyasi; `document/{id}` havolalari "qo'shimcha o'qish" uchun; "Muhim" ogohlantirishlar g'oyasi (tuzoq savollar) | Javob matnlarini so'zma-so'z ko'chirish, to'liq saytni RAG uchun skreyp qilish (ruxsatsiz), byurolar ekspertlarining ismlari va shaxsiy ma'lumotlari |
| norma.uz (+buxgalter.uz, nrm.uz) | Mavzu borligini bilish, "qonunchilikda yangi" orqali o'zgarishlarni kuzatish (keyin lex.uz), havola | Har qanday matn, Q&A, shakl, sharh — NORMA MChJ bilan yozma kelishuvsiz; avtomatik indekslash |
| advokat.uz / karamatov.uz | Hech narsa (o'lik domen; firma sayti eskirgan). Ko'pi bilan xizmat kategoriyalari g'oyasi | Shablonlar va Q&A (eskirgan va mualliflik huquqi bilan himoyalangan) |
| advokatpro.uz | UX g'oyalari, yangi normalar haqida signal (masalan, MehK 8¹), keyin lex.uz'da tekshirish | AI izohlar, shablon matnlari, baza tuzilmasi, skreyp |

- AI-case-from-user-story funksiyasi uchun: foydalanuvchi hikoyasini advice.uz kategoriyalariga o'xshash yorliqlar bilan tasniflash; har bir yorliqqa lex.uz'dagi asosiy kodeks/modda to'plamini biriktirish; ssenariy faktlarini generatsiya qilish; "to'g'ri javob" kalitini faqat lex.uz moddasiga bog'lash.
- Madad NNT bilan hamkorlik memorandumi (portal memorandumlar tuzgan) LexSim'ga "Hayotiy misollar"ni rasmiy ruxsat bilan ishlatish imkonini beradi va "ssenariy qayerdan olingan?" savoliga kuchli javob bo'ladi. Bu tavsiya, kelishuv hali yo'q.

### Gaps
- Hech bir portalda CC yoki boshqa ochiq litsenziya topilmadi. Huquqiy maslahat (ruxsat so'rash) LexSim jamoasi tomonidan amalga oshirilishi kerak.
