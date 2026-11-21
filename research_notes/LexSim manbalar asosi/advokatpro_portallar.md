# AdvokatPro va O'zbekistondagi huquqiy amaliyot portallari — LexSim uchun manba tahlili

Tadqiqot sanasi: 2026-11-20. Usul: WebFetch va curl orqali saytlarni to'g'ridan-to'g'ri ochish (advokatpro.uz, norma.uz, buxgalter.uz, lex.uz, advice.uz, paruz.uz) va WebSearch. Qaysi sayt ochilmagani har bo'limda yozilgan.

## 1. AdvokatPro nima, uni kim yuritadi, u rasmiymi, qanday bo'limlari bor, bepulmi yoki pullikmi, foydalanish shartlari qanday

### Takeaway
AdvokatPro (https://advokatpro.uz) xususiy tijorat startapi. U lex.uz matnlari ustiga qurilgan AI-yordamchi, kundalik sinxronlanadigan qonun bazasi, izohli hujjat shablonlari, advokatlar katalogi (konsultatsiya marketpleysi) va advokat uchun mijoz/ish kabinetini beradi. U Advokatlar palatasining rasmiy platformasi emas, saytda Palata bilan hech qanday aloqa ko'rsatilmagan. Shartlarga ko'ra sayt dizayni, dasturi va baza tuzilmasi AdvokatProga tegishli, qonun matnlari esa lex.uz ochiq manbasidan olinadi. Demak LexSim qonun matnlarini to'g'ridan-to'g'ri lex.uz'dan olishi kerak, AdvokatPro'ning AI izohlari, shablon matnlari va UI'sidan esa faqat g'oya darajasida (dizayn uchun namuna sifatida) foydalanish mumkin.

### Cited Findings
- **Domen va nomi:** https://advokatpro.uz, sahifa sarlavhasi "Advokat Pro — Huquqiy hujjatlar tizimi". Footerda "© 2026 Advokat Pro" yozilgan. Yuridik shaxs (MChJ nomi, STIR) ko'rsatilmagan. Kontaktlar: Telegram @thesharofiddin va support@advokatpro.uz — [advokatpro.uz](https://advokatpro.uz/uz-latn)
- **O'zini qanday tanishtiradi:** "O'zbekiston qonunchiligi bo'yicha sun'iy intellekt yordamchisi. Oddiy odamga o'z vaziyatini tushunishga, advokatga esa kundalik ishni tezlashtirishga yordam beradi." Disklaymer: "advokatning o'rnini bosmaydi va yuridik xulosa bermaydi" — [advokatpro.uz](https://advokatpro.uz/uz-latn)
- **Rasmiylik:** bosh sahifada, katalogda va shartlarda Advokatlar palatasi yoki Adliya vazirligi tilga olinmagan. Katalog sahifasida Palataga havola yo'q va advokat litsenziyasini tekshirish tartibi tasvirlanmagan — [advokatlar](https://advokatpro.uz/uz-latn/advokatlar). Shartlarda faqat "advokatlar haqiqiy litsenziya ma'lumotlarini berishi shart" deyilgan — [shartlar](https://advokatpro.uz/uz-latn/shartlar)
- **Navigatsiya (aniq URL'lar):**
  - Qonunlar bazasi: /uz-latn/moddalar
  - Qonun o'zgarishlari: /uz-latn/qonun-ozgarishlari
  - Advokatlar: /uz-latn/advokatlar
  - Kabinet / "Bepul so'rash": /uz-latn/dashboard
  - Tadbirkor kabineti: /uz-latn/dashboard/tadbirkor
  - Advokat sifatida kirish: /uz-latn/login?role=lawyer
  - Maxfiylik siyosati: /uz-latn/maxfiylik
  - Foydalanish shartlari: /uz-latn/shartlar
  - Tillar: o'zbek (lotin va kirill), rus, ingliz
  - Manba: [advokatpro.uz HTML](https://advokatpro.uz/uz-latn)
- **Qonun bazasi:** 14 158 modda, 185 ta qonun va kodeks, har kuni lex.uz bilan solishtiriladi. Eng katta kodekslar (moddalar soni): FK 1197, JPK 774, MJtK 674, MK 594, FPK 513, SK 500, BK 419, JK 406, IPK 390, YHQ (VM №172, 2022) 369, MSIYuK 309 — [advokatpro.uz](https://advokatpro.uz/uz-latn)
- **Modda sahifasining tuzilishi** (misol: FPK 149):
  - asl matn va "lex.uz'dagi asl matn" havolasi;
  - "Oddiy tilda" bloki: "Nimani anglatadi / Kimga tegishli / Amalda";
  - "Izoh sun'iy intellekt tomonidan tayyorlangan, rasmiy sharh emas" degan belgi;
  - modda bo'yicha bepul savol berish formasi va qo'shni moddalar;
  - Manba: [FPK 149 sahifasi](https://advokatpro.uz/uz-latn/moddalar/fpk-149)
- **Qonun o'zgarishlari lentasi:**
  - Har bir yozuvda turi ("O'zgartirildi", "Yangi modda", "Kuchini yo'qotdi", "Hujjatning yangi tahriri", "lex.uz'da yangi"), o'zgartirgan hujjat (masalan, O'RQ-1168…O'RQ-1190, PF-242), kuchga kirish sanasi va "Avvalgi tahrir" matni beriladi.
  - Holat: 186 ta hujjat kuzatilmoqda, oxirgi tekshiruv 21.11.2026 05:32.
  - Manba: [qonun-ozgarishlari](https://advokatpro.uz/uz-latn/qonun-ozgarishlari)
- **Imkoniyatlar:**
  - AI qidiruv ("AI o'zidan modda to'qimaydi", modda topilmasa ochiq aytadi);
  - hujjat tahlili ("Shartnoma, ariza, buyruq, sud hujjati, rasm yoki sayt sahifasini yuklang");
  - advokat uchun mijozlar va ishlar kabineti;
  - YaTT uchun soliq kalendari, 1 mlrd chegarasi va jarimalar nazorati, Didox'dan tushumlarni avtomatik olish (ERI bilan);
  - chet elliklar uchun "turist rejimi";
  - Manba: [advokatpro.uz](https://advokatpro.uz/uz-latn)
- **Tariflar:**
  - Bepul — 0 so'm: oyiga 5 hujjat, 5 AI savol, 3 vaziyat tahlili; faqat PDF va lotin yozuvi; hujjatlar 7 kun saqlanadi.
  - Fuqaro Plus — 25 000 so'm/oy.
  - Advokat Pro — 249 000 so'm/oy: 14 kun bepul sinov, karta talab qilinmaydi; sinovda 200 AI so'rov va 50 hujjat.
  - Bir martalik — 5 000 so'm/hujjat ("tez orada").
  - Qo'shimcha 50 AI xabar — 15 000 so'm.
  - To'lov inPAY orqali.
  - Manba: [advokatpro.uz#tariflar](https://advokatpro.uz/uz-latn)
- **Advokatlar katalogi (marketpleys):**
  - Filtrlar: shahar va soha (oila, mehnat, jinoyat, fuqarolik nizolari, ijara, meros, ko'chmas mulk, qarz/kredit, YHQ/ma'muriy, biznes/soliq, migratsiya); saralash reyting, tajriba va narx bo'yicha.
  - To'lov konsultatsiya tugaguncha platformada ushlab turiladi.
  - Advokatdan 25% komissiya olinadi.
  - Manba: [advokatlar](https://advokatpro.uz/uz-latn/advokatlar)
- **Foydalanish shartlari (oxirgi yangilanish 15.09.2026):**
  - "AI javoblari ma'lumot xarakteriga ega".
  - Sayt dizayni, dasturi va baza tuzilmasi AdvokatProga tegishli; qonun matnlari lex.uz ochiq manbasidan olinadi.
  - "Siz yaratgan hujjatlar sizga tegishli".
  - Tizimni buzish va avtomatik ommaviy so'rovlar taqiqlangan.
  - Xizmat "bor holida" beriladi; javobgarlik so'nggi 12 oyda to'langan summa bilan cheklangan.
  - Nizolar O'zbekiston qonunchiligi bo'yicha hal qilinadi.
  - Manba: [shartlar](https://advokatpro.uz/uz-latn/shartlar)

### Inferences
- AdvokatPro'da LexSim'ga to'g'ridan-to'g'ri foydali "advokat metodikasi", kurs, imtihonga tayyorlov yoki sud amaliyoti dayjesti bo'limi yo'q. U kontent bazasi emas, mahsulot dizayni bo'yicha raqib/namuna sifatida qimmatli. LexSim uchun quyidagi andozalar foydali:
  - "Oddiy tilda: Nimani anglatadi / Kimga tegishli / Amalda" uch qismli modda izohi;
  - "AI o'zidan modda to'qimaydi" tamoyili (javob faqat topilgan moddaga tayanadi — LexSim'dagi AI-sudya yoki AI-mijoz uchun grounding qoidasi sifatida);
  - shablon maydoni yonida "nima uchun kerak" izohi va huquqiy asos moddalari;
  - qonun o'zgarishlari lentasi va "avvalgi tahrir" (LexSim'da norma versiyasini ko'rsatish uchun).
- Saytning AI izohlari xatolardan xoli bo'lmasligi mumkin. Masalan, FPK 149 izohida xususiy shikoyat uchun "10 kunlik muddat" misol tariqasida aytilgan, lekin bu muddat modda matnida yo'q — **tasdiqlanmagan**, FPK bilan tekshirish kerak. LexSim AdvokatPro izohlarini manba sifatida ishlatmasligi kerak.
- Shartlarda nusxa ko'chirish to'g'ridan-to'g'ri taqiqlanmagan, ammo dizayn va baza tuzilmasiga mulkiy huquq e'lon qilingan va avtomatik ommaviy so'rovlar taqiqlangan. Shuning uchun AdvokatPro'ni skreyp qilish yoki uning shablon/izoh matnlarini ko'chirish ruxsatsiz mumkin emas, deb hisoblash kerak. Havola berish va g'oyalardan ilhomlanish mumkin. Hamkorlik uchun kontakt: support@advokatpro.uz.
- Qonun o'zgarishlari lentasida 7-yanvar 2027 gacha bo'lgan sanalar bor, bugun esa 2026-11-20. Bu kelajakdagi kuchga kirish sanalari yoki ma'lumotdagi xato bo'lishi mumkin — **tasdiqlanmagan**.

### Gaps
- Operator yuridik shaxsi aniqlanmadi: MChJ nomi, STIR va asoschi (Telegram nomidan "Sharofiddin" deb taxmin qilish mumkin) — **tasdiqlanmagan**.
- Advokat kabineti (CRM) funksiyalari, ya'ni ish kartochkasi va muddatlar qanday ishlashi, faqat login orqali ko'rinadi, shuning uchun o'rganilmadi.
- Kurslar, imtihonga tayyorlov, kalkulyatorlar (davlat boji, penya, da'vo muddati) bor-yo'qligini tasdiqlovchi ma'lumot topilmadi. Bosh sahifada faqat YaTT soliq kalendari va jarima nazorati tilga olingan.
- Mobil ilova shartlarda tilga olingan, lekin do'kon havolasi topilmadi.

## 2. AdvokatPro qanday shablon/hujjat namunalarini beradi va ularda qaysi maydonlar bor

### Takeaway
Ochiq sahifalarda faqat bir nechta shablon nomi ko'rinadi: Qarz shartnomasi (asosi FK 732–736), Ijara shartnomasi, Mehnat shartnomasi va Xizmat shartnomasi. Fuqarolar uchun "16 ta tayyor shablon, izohlar bilan" deyilgan. To'liq ro'yxat va maydonlar faqat ro'yxatdan o'tgandan keyin ko'rinadi. Da'vo arizasi, iltimosnoma, apellyatsiya shikoyati, ishonchnoma, order va advokat so'rovi shablonlari ochiq qismda tasdiqlanmadi.

### Cited Findings
- **Shablonlar haqida sayt nima deydi:**
  - "Qonunga tayangan shablonlar. Har bir hujjat aniq moddalarga asoslangan. Maydon yonidagi izoh nima uchun kerakligini aytadi."
  - Misol: "Qarz shartnomasi · PDF · DOCX · Huquqiy asos FK 732, 733, 734, 735, 736".
  - Manba: [advokatpro.uz](https://advokatpro.uz/uz-latn)
- **Ochiq HTML'da topilgan shablon nomlari:** "Ijara shartnomasi", "Mehnat shartnomasi", "Qarz shartnomasi", "Xizmat shartnomasi". Yana namuna savollar ham bor: "Apellyatsiya shikoyati berish muddati qancha (FPK)?", "Da'vo arizasini qaytarish asoslari (FPK)". Ular shablon emas, AI savol misollari — [advokatpro.uz](https://advokatpro.uz/uz-latn), [dashboard](https://advokatpro.uz/uz-latn/dashboard)
- **Sudda yaroqliligi haqidagi FAQ:** "Shablonlar tegishli kodeks moddalarining majburiy talablari asosida tuzilgan va DOCX'da tahrirlanadi. Sudga topshirishdan oldin ish holatiga moslashtiring" — [advokatpro.uz#savollar](https://advokatpro.uz/uz-latn)

### Inferences
- LexSim uchun asosiy foydali g'oya — "maydon + izoh + huquqiy asos moddasi" uchligi. Hujjat tuzish mashqida har bir maydonni qonundagi majburiy rekvizitga bog'lash mumkin; masalan, da'vo arizasi maydonlarini FPK'dagi da'vo arizasi mazmuniga oid moddaga bog'lash. Shunda baholash rubrikasi avtomatik chiqadi: "majburiy rekvizit bormi?". Rekvizitlarni AdvokatPro'dan emas, kodeks matnidan (lex.uz) olish kerak.

### Gaps
- 16 ta shablonning to'liq ro'yxati va maydonlari: login talab qilinadi, ko'rib bo'lmadi.
- Advokatga xos hujjatlar (order, advokat so'rovi, ishonchnoma) bor-yo'qligi noma'lum.

## 3. AdvokatPro advokat amaliyoti metodikasini e'lon qiladimi (sud majlisiga tayyorgarlik, konsultatsiya chek-listlari)

### Takeaway
Yo'q. Ochiq qismda metodik materiallar, chek-listlar, kurslar yoki sud amaliyoti dayjestlari topilmadi. LexSim baholash rubrikalari uchun bu manba yaramaydi. Rubrikalarni boshqa joydan olish kerak: protsessual kodekslar, Palata/Adliya materiallari va advice.uz'dagi "namunadan foydalanishda tekshiriladigan narsalar" ro'yxati (4-bo'limga qarang).

### Cited Findings
- Bosh sahifa bo'limlari faqat qonunlar bazasi, o'zgarishlar, advokatlar, tariflar, imkoniyatlar, "Biz haqimizda" va FAQ'dan iborat — [advokatpro.uz](https://advokatpro.uz/uz-latn)
- Platformaning o'z ta'rifi: "vaziyatni tushunish, to'g'ri moddani topish va advokat bilan uchrashuvga tayyorlanish uchun vosita" — [advokatpro.uz](https://advokatpro.uz/uz-latn)

### Inferences
- "Advokat bilan uchrashuvga tayyorlanish" g'oyasi LexSim'dagi "mijoz konsultatsiyasi" ssenariysiga mos keladi. LexSim AI-mijozni AdvokatPro foydalanuvchisiga o'xshatib qurishi mumkin: mijoz vaziyatni o'z so'zlari bilan aytadi, talaba esa moddalarni topib, savol berishi kerak.

### Gaps
- Advokatlar palatasining rasmiy metodik qo'llanmalari va malaka imtihoni testlari topilmadi (4-bo'limdagi paruz.uz qismiga qarang).

## 4. Boshqa O'zbek huquqiy portallari bilan solishtirish (shablonlar, qo'llanmalar, qayta foydalanish cheklovlari)

### Takeaway
- **lex.uz** (Adliya vazirligi qoshidagi "Adolat" markazi): qonun matnlari uchun asosiy rasmiy manba va LexSim normalarining yagona to'g'ri manbasi. U yerda alohida "namunaviy shakllar" bo'limi yo'q. Lekin "Huquqiy tushuntirishlar", "Qo'llanmalar", BHM kalkulyatori va "Namunaviy nizom" / "Namunaviy kontrakt" filtrlari bor.
- **NORMA MChJ** (norma.uz, nrm.uz, buxgalter.uz): eng boy shakllar katalogi ("Юридик ёрдамчи": da'vo arizasi, sud uchun ishonchnoma, talabnoma, qarz hisob-kitobi) va "Javob beramiz" savol-javob xizmati. Ammo kontent mualliflik huquqi bilan himoyalangan va ruxsatsiz ko'chirish to'g'ridan-to'g'ri taqiqlangan.
- **advice.uz** ("Madad" NNT): bepul huquqiy maslahat portali. Sudga murojaat hujjatlari namunalari va "namunani moslashtirish/topshirishdan oldin tekshirish" chek-listi bor; bu rubrika uchun foydali.
- **Advokatlar palatasi saytlari** (paruz.uz / advokatuz.uz): ochilmadi yoki bo'sh. advokat.uz ham ochilmadi.

### Cited Findings
**lex.uz**
- Menyuda HUQUQIY TUSHUNTIRISHLAR (/uz/explanation), Qo'llanmalar (/uz/qollanma), Hisobotlar shakllari (/uz/forms), BHM Kalkulyatori (/uz/bhm), sharh.lex.uz, Qonunchilik to'plami (/uz/law_collection), Foydalanish shartlari (/agreement) bor. Alohida "namunaviy shakllar" bo'limi yo'q — [lex.uz](https://lex.uz/uz/)
- Footer: "© O'zbekiston Respublikasi Adliya vazirligi qoshidagi "Adolat" milliy huquqiy axborot markazi davlat muassasasi" — [lex.uz](https://lex.uz/uz/)
- lex.uz/agreement ochilganda maxfiylik siyosati matni chiqdi, foydalanish shartlari emas. /uz/agreement esa 404 qaytardi. Siyosatda "Milliy baza O'zbekiston Respublikasi qonunchiligiga ko'ra rasman ro'yxatdan o'tgan tizim hisoblanadi" deyilgan — [lex.uz/agreement](https://lex.uz/agreement)
- Advokat ordeni shakli bo'yicha alohida normativ hujjat bor: 08.04.2009 dagi №1938, "advokat tomonidan ishni yuritish uchun order shaklini tasdiqlash to'g'risida". Bu nom qidiruv natijasidan olingan, matn ochilmadi — [lex.uz/docs/1468902](https://lex.uz/docs/1468902)
- 2023-yil 1-fevraldan QR-kodli "Elektron advokat orderi" an'anaviy order bilan tenglashtirildi. Advokat so'rovi shakliga va unga ilova qilinadigan order nusxasiga oid talablar bekor qilindi, so'rovni elektron yuborish mumkin bo'ldi — [president.uz](https://www.president.uz/oz/lists/view/5228)
- Advokatura to'g'risidagi qonun — [lex.uz/acts/-54503](https://lex.uz/acts/-54503)
- Advokatura raqamlashtirildi: malaka imtihoniga ariza berish to'liq raqamli. Advokatlar soni 2022-yilda 4 577 ta edi, 2026-yilda 7 732 ta — [gov.uz/adliya](https://gov.uz/oz/adliya/news/view/204859)

**norma.uz / nrm.uz / buxgalter.uz (NORMA MChJ)**
- norma.uz bo'limlari:
  - elektron mahsulotlar;
  - gazeta.norma.uz (obuna);
  - seminarlar (seminar.cpr.uz), vebinarlar (webinar.cpr.uz), kurslar (buxgalter.academy), testlar (bir.uz);
  - "Bizning sharhlar", "Qonunchilikda yangi", NHH loyihalari;
  - onlayn baza nrm.uz.
  - Alohida hujjat namunalari bo'limi yo'q.
  - Manba: [norma.uz](https://www.norma.uz/uz/)
- norma.uz footeri: "© «NORMA» МЧЖ, 2007-2026 й. Барча ҳуқуқлар ҳимояланган." va "Сайт материалларини ресурс маъмурияти розилигисиз кўчириб олиш тақиқланади." — [norma.uz](https://www.norma.uz/uz/)
- buxgalter.uz "Жавоб берамиз" savol-javob xizmati:
  - ekspertlar javob beradi; javoblar "shaxsiy fikr" deb belgilangan;
  - mavzular buxgalteriya, soliq, mehnat va huquq (tadbirkorlik, fuqarolik/oila, jinoyat, sudgacha va sud jarayoni);
  - sahifada 15 tadan, taxminan 164 sahifa;
  - Buxgalter Pro pullik tarifi bor, lekin qaysi javoblar pullik ekani ko'rsatilmagan;
  - Manba: [buxgalter.uz/uz/questions](https://buxgalter.uz/uz/questions/)
- buxgalter.uz footeri: "© «NORMA» МЧЖ, 2019–2026. Барча ҳуқуқлар ҳимояланган" va xuddi shu ko'chirish taqiqi — [buxgalter.uz/uz/questions](https://buxgalter.uz/uz/questions/)
- buxgalter.uz "Шакллар" bo'limi:
  - Kategoriyalar: Buxgalteriya hisobi, Soliq hisobi, Kadrlar hisobi (mehnat shartnomasi, ta'til, intizomiy), "Юридик ёрдамчи" (soliq nazorati, korporativ, shartnomalar, ishonchnomalar, shikoyat va da'volar).
  - "Даъволар билан ишлаш" ichida: iqtisodiy nizo bo'yicha da'vo arizasi shabloni, kompaniyaning sudda vakillik uchun ishonchnomasi, da'voga ilova qilinadigan qarz hisob-kitobi, qarzni undirish talabnomasi.
  - Narx yoki kirish shartlari ko'rsatilmagan.
  - Manba: [buxgalter.uz/uz/forms](https://buxgalter.uz/uz/forms/)
- buxgalter.uz'dagi alohida namunalar va maqolalar: "Даъвони қайтариб олиш аризаси намунаси" va "Даъво аризаси суддан кўриб чиқилмай қайтиб келмаслиги учун қандай тайёрланади" — [buxgalter.uz text177453](https://buxgalter.uz/uz/publish/doc/text177453_davoni_qaytarib_olish_arizasi_namunasi), [buxgalter.uz text176941](https://buxgalter.uz/ru/publish/doc/text176941_davo_arizasi_suddan_kurib_chiqilmay_qaytib_kelmasligi_uchun_qanday_tayerlanadi)

**advice.uz ("Madad" NNT)**
- Sahifa: "Судга мурожаат ҳужжатлари намуналари", 250 773 marta o'qilgan.
- U Oliy sud rasmiy sayti va sudlarning interaktiv xizmatlari portalidagi namunalarga yo'naltiradi. U yerdagi namunalar: oilaviy va aliment nizolari bo'yicha da'volar; uy-joy, meros va mulk nizolari; mehnat nizolari; qarz, zarar va shartnomaviy talablar; protsessual iltimosnomalar; apellyatsiya, kassatsiya va taftish shikoyatlari; iqtisodiy va ma'muriy sudlarga arizalar.
- Manba: [advice.uz/uz/documents/1554](https://advice.uz/uz/documents/1554)
- Shu sahifadagi chek-list:
  - Namunaga kiritilishi kerak: vakolatli sudning aniq nomi, taraflarning to'liq ma'lumotlari, nizoning haqiqiy holatlari, talabning mazmuni va hisob-kitobi, dalillar, ilovalar ro'yxati.
  - Mulkiy talabda da'vo bahosi, undiriladigan summa hisob-kitobi va davlat boji ko'rsatiladi.
  - Topshirishdan oldin tekshiriladi: sudning vakolati, murojaat muddati o'tmaganligi, davlat boji to'langanligi, vakilning vakolati.
  - "Ундаги матнни ўзгартирмасдан топшириш мумкин эмас".
  - Manba: [advice.uz/uz/documents/1554](https://advice.uz/uz/documents/1554)
- Boshqa bo'limlar: "Юридик хизмат (ҳуқуқий ҳужжат намуналари)", "Адвокат хизмати", "Бепул ҳуқуқий ёрдам", "Юридик луғат", Pro bono, bepul huquqiy yordam vaucheri, "Wakil AI", forum, "Топ 10 савол". Footer: "© 2019-2026 "Мадад" муассаса шаклидаги нодавлат нотижорат ташкилоти", alohida "Фойдаланиш шартлари" sahifasi bor — [advice.uz](https://advice.uz/uz/documents/1554)
- advice.uz'da Palata saytlari paruz.uz / advokatuz.uz deb ko'rsatilgan. Telefonlar: +998 71 261-61-43, 261-61-49. Bu ma'lumot ikkilamchi manbadan — [advice.uz/ru/document/2171](https://www.advice.uz/ru/document/2171)

**Advokatlar palatasi va advokat.uz**
- advokatuz.uz 301 kodi bilan http://paruz.uz/ ga yo'naltiradi. paruz.uz faqat "Lawyers" so'zidan iborat 1 KB'li stub sahifa qaytardi: menyu ham, kontent ham yo'q — to'g'ridan-to'g'ri tekshiruv, 2026-11-20 ([paruz.uz](http://paruz.uz/))
- advokatlarpalatasi.uz domeni DNS'da topilmadi (ENOTFOUND). advokat.uz HTTP 522 qaytardi (Cloudflare, server javob bermadi) — to'g'ridan-to'g'ri tekshiruv, 2026-11-20.

### Inferences
**Qayta foydalanish matritsasi (LexSim uchun):**

| Manba | Nimani olish mumkin | Cheklov |
|---|---|---|
| lex.uz | Kodeks va qonun matnlari (rasmiy, ochiq). Rekvizitlar (masalan, da'vo arizasi mazmuni), muddatlar va boj stavkalari shu yerdan olinadi | Davlat muassasasi kontenti. Iqtibos va manba havolasini berish kerak. Foydalanish shartlari matni ochilmadi — **tasdiqlanmagan** |
| AdvokatPro | UX g'oyalari: izohli maydonlar, "oddiy tilda" bloki, o'zgarishlar lentasi | Dizayn, kod va baza tuzilmasi operatorga tegishli. Skreyp taqiqlangan. AI izohlarida xato bo'lishi mumkin. Faqat havola berish yoki ruxsat olish mumkin |
| NORMA (norma.uz, nrm.uz, buxgalter.uz) | Faqat ma'lumot uchun: qanday shablonlar mavjudligi va mavzular ro'yxati | Ruxsatsiz ko'chirish to'g'ridan-to'g'ri taqiqlangan. Matnlarni olish uchun NORMA MChJ bilan litsenziya kerak |
| advice.uz | "Namunani moslashtirish va tekshirish" chek-listi — rubrika uchun g'oya; namunalar katalogining tuzilishi | NNT kontenti, "Фойдаланиш шартлари" bor (matni o'qilmadi). Erkin qayta yozish va havola berish xavfsizroq. Matnni ko'chirish uchun ruxsat so'rash kerak |
| Oliy sud sayti va sudlarning interaktiv portali | Sudga murojaatlarning rasmiy tavsiyaviy namunalari (advice.uz ma'lumotiga ko'ra) | Bu tadqiqotda ochilmadi — **tasdiqlanmagan** |

- LexSim hujjat tuzish moduli uchun eng huquqiy toza yo'l:
  - rekvizitlarni FPK, IPK, JPK va MSIYuK moddalaridan lex.uz orqali olish;
  - order va so'rov shaklini lex.uz'dagi №1938 (2009) hujjatidan va 2022 yilgi president.uz qaroridan olish;
  - shablon matnlarini o'zi yozish.
- Elektron orderning joriy etilishi va advokat so'roviga qo'yiladigan shakl talablarining bekor qilinishi sababli, LexSim'dagi "advokat so'rovi" mashqi qat'iy blankani emas, mazmuniy rekvizitlarni baholashi kerak.

### Gaps
- Advokatlar palatasining hozirgi rasmiy sayti, metodik qo'llanmalari, malaka imtihoni test bazasi va "e-advokat"/elektron order platformasi domeni aniqlanmadi: paruz.uz bo'sh, advokatlarpalatasi.uz mavjud emas.
- advokat.uz tarkibi aniqlanmadi (HTTP 522).
- Oliy sud (sud.uz) va interaktiv portal (my.sud.uz?) namunalari to'g'ridan-to'g'ri tekshirilmadi — **tasdiqlanmagan**.
- lex.uz foydalanish shartlari matni olinmadi: /agreement maxfiylik siyosatini ko'rsatdi.
- NORMA shakllari pullikmi yoki bepulmi, sahifada ko'rsatilmagan.
- Huquqiy kalkulyatorlar (davlat boji, penya, da'vo muddati) bo'yicha topilgani faqat lex.uz'dagi BHM kalkulyatori (/uz/bhm). Boshqa portallardagi kalkulyatorlar qidirilmadi.
