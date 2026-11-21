# LexSim funksiyalar auditi: har bir yo'nalish va uning huquqiy/kontent asosi

Manbalar faqat loyihaning mahalliy fayllari (veb ishlatilmadi). "Source" o'rnida `fayl:qator` beriladi. Maxfiy fayllar (.env, *.key, LEXSIM_REMOTE_KEY.txt, tokenlar) ochilmadi. Frontend kodi (Next.js, `src/server/scenarios/...`) bu papkada **yo'q**, shuning uchun "Ish yo'li" (mehnat/o'g'irlik) va DXM mantiqi faqat backendga kelgan qismlari bo'yicha (voice_lines.json, contracts.schema.json, intents.json) baholandi.

Tekshiruv usuli: kod va JSON'dagi har bir modda havolasi loyihaning o'z lex.uz korpusi (`data/lex/*.jsonl`, `fetched_at: 2026-11-20`, har bir yozuvda `lex_url`) bilan solishtirildi: modda raqami bor-yo'qligi va sarlavhasi mos kelishi. Bu korpusdagi **amaldagi tahrir**ni anglatadi, lekin rasmiy lex.uz bilan qayta solishtirish o'rnini bosmaydi.

## 1. Qaysi funksional yo'nalishlar bor va ularni qaysi fayllar bajaradi

### Takeaway
Backend'da to'liq "dvijok" faqat bitta ish uchun bor: iqtisodiy sud, ijara qarzi va penya (`sud-ijara-davogar` / `sud-ijara-javobgar`). Mehnat ("labour") va o'g'irlik/politsiya ("theft") yo'llari, DXM va da'vo arizasi tuzish frontendda ishlaydi. Backend ular uchun faqat ovoz keshi, NLU, saqlash va kontrakt sxemasini beradi.

### Cited Findings

**Funksiyalar jadvali (nima qiladi, qaysi fayllarda):**

| # | Funksiya / yo'nalish | Nima qiladi | Asosiy fayllar |
|---|---|---|---|
| F1 | Iqtisodiy sud majlisi "sud-ijara" | IPK bosqichlari bo'yicha chiziqli FSM: ochilish → vakolat → rad → huquqlar → iltimosnomalar → mazmunan → dalillar → muzokara → maslahatxona → qaror. Sudya shablonlari, raqib replikalari | `backend/lexsim_server.py:131-187` (T), `:189-218` (OPP), `:1081+` (bosqichlar), `backend/scenarios.json`, `backend/scenarios/sud-ijara.json`, `data/sud/bosqichlar_ipk.json`, `data/sud/ssenariy_ijara_qarzi.json` |
| F2 | "Jonli" protsedura (talaba tashabbusi) | Savol, iltimosnoma (penya/dalil/qoldirish), e'tiroz, kelishuv. Qayta so'rash, erta iltimosnoma, vaziyatlar (mijozga zid gap, jinoiy jazo so'rash, rus tili, mavzudan tashqari, hayajon) | `backend/procedure.py:1-10, 154-223`, `backend/intents.json` (judge, situations, recusal, order_ladder) |
| F3 | Mehnat ishi yo'li ("labour") | Bosqichlar: consult → draft → filing → chamber → hearing. Ishga tiklash (Sardor N. / «Namuna Savdo» MChJ) | Frontend (bu yerda yo'q). Backend: `backend/voice_lines.json` (gaplar), `contracts.schema.json` `CaseKind`, `StageId`, `CaseActRequest`, `Ruling`, `ClaimDraft` |
| F4 | O'g'irlik / politsiya yo'li ("theft") | report (navbatchi qism) → interview (tergovchi so'rog'i) → complaint (bo'lim boshlig'iga shikoyat) | Frontend. Backend: `backend/voice_lines.json` (theft qatorlari), `contracts.schema.json` `CaseKind=theft` |
| F5 | DXM (davlat xizmatlari markazi), "Yo'qolgan staj" | Fuqaroga xizmat tanlash va hujjat qoralamasi (arxiv ma'lumotnomasi, pensiyani qayta hisoblash ...) | `backend/lexsim_server.py:116-118` (SERVICES/EVIDENCE/NOTIFY), `:1728-1747` (validate_draft), `:2398-2410` (a_documents), `contracts.schema.json:641` (DocumentDraft), `LexSim_Backend_Spec.md:154, 283, 476-487` |
| F6 | Da'vo arizasi tuzish (ClaimDraft) | Mehnat ishi uchun da'vo arizasi "konstruktori": sud turi, javobgar, talab, faktlar, dalillar, ilovalar, nusxalar, imzo | `contracts.schema.json:6987` (ClaimDraft). Backend'da ClaimDraft'ni tekshiradigan yoki baholaydigan kod topilmadi (`grep ClaimDraft backend/*.py`: natija yo'q) |
| F7 | Konsultatsiya (mijoz bilan suhbat) | Labour "consult" bosqichi: mijoz faktlarni aytadi, rozilik, "Qonun bo'yicha qilaylik" | `backend/voice_lines.json` (consult qatorlari), frontend |
| F8 | NLU (erkin gapni variantga moslash) | `/api/v1/nlu/match`: GPU reranker (bge-reranker-v2-m3) yoki leksik moslik. Pora, qo'pollik, so'kinish ro'yxatlari. "Ish yo'li"/DXM uchun `nlu_situation` (so'kinish, hujjat yo'q, mijozni tashlab ketish, rus tili, mavzudan tashqari) | `backend/nlu.py:1-30`, `backend/lexsim_server.py:258-268`, `backend/intents.json` (`nlu_situations`, `nlu_voices`) |
| F9 | Ma'no bo'yicha baholash (semantic) | Har bir muhim lahza (KM) uchun pos/neg/false namunalari. Reranker ballari bilan daraja 2/3 qo'yiladi, 4-daraja uchun modda kalit so'zi kerak | `backend/semantic.json` (`thresholds` 0.5/0.2/0.7, "Kalibrlash: 2026-11-21, 12 ta sinov gapi") |
| F10 | Baholash / rubrika | 6 mezon: legal 30, facts 15, procedure 15, communication 15, ethics 15, document 10. Buzilishlar jadvali, KM1–KM4, maslahat uchun −5, variantni ochish uchun −10, pora bo'lsa yoki 3 marta haqorat bo'lsa natija 0 | `backend/lexsim_server.py:296-311` (VIOL_INFO), `:1343-1344` (CRIT), `:1389-1523` (evaluate), `data/sud/baholash_rubrikasi.md`, `RUBRIC_VERSION="court-v1"` (`:56`) |
| F11 | Maslahatchi (hint) | Tutorial rejimida bosqich bo'yicha "nima qilish, namuna, keng tarqalgan xato, moddalar" | `backend/lexsim_server.py:1538-1625`, `backend/roles.json` (`maslahatchi.bosqichlar`, `moddalar` 110-253-qatorlar) |
| F12 | Moddalar / iqtiboslar (Source) | Sudya shablonlariga norm_id biriktiriladi (T_ART), hisobotda KM_NORMS bo'yicha `sources` (faqat lex.uz URL, `verifiedAt: null`) | `backend/lexsim_server.py:223-233` (T_ART, KM_ARTICLE), `:341-346` (KM_NORMS), `:359-416` (Norms.source) |
| F13 | RAG huquqiy qidiruv | Postgres `law_chunks` (`valid_to IS NULL`) va RAG servisi `/search` (k=5, case_type=IPK). Korpus `tools/lex_extract.py` bilan lex.uz'dan olingan | `backend/lexsim_server.py:58, 359-416`, `LexSim_RAG_Qollanma.md:20-45`, `data/lex/*.jsonl`, `data/lex/plenum/*.jsonl`, `data/lex/_cache/*.html` |
| F14 | LLM raqib | Raqib javoblari uchun ixtiyoriy LLM (`qwen3.6-colibri`). `llm_check` sizib chiqish (LEAK), inkor (DENY), kirill va ruxsatsiz raqamlarni tekshiradi | `backend/lexsim_server.py:62-68, 470-606`, `backend/aihub_llm.py` |
| F15 | Ovozlar (TTS/STT) | Chatterbox klon ovozlari (GPU) yoki MMS. Prerender keshi | `backend/voice.py`, `backend/voices.json`, `backend/voice_lines.json`, `ovoz_namunalar/` |
| F16 | Shikoyat (appeal) va mentor ko'rigi | Talaba hisobotga e'tiroz bildiradi (`reviewStatus: needs-mentor`) | `backend/lexsim_server.py:2420-2431` |

### Inferences
- Huquqiy jihatdan "chuqur" ishlangan yo'nalish faqat F1 (IPK + FK, korpus bilan bog'langan). F3–F7 matnlari protsessual normalarga yaqin yozilgan, lekin backend ularni modda bilan bog'lamaydi.

### Gaps
- Frontend kodi (labour/theft FSM, ClaimDraft baholash qoidalari, DXM ssenariysi `dxm-yoqolgan-staj.ts`) bu papkada yo'q. Ularning ichida qanday moddalar keltirilgani tekshirilmadi.

## 2. Har bir yo'nalish qanday huquqiy kontentga tayanadi va u qayerdan olingan

### Takeaway
F1 (iqtisodiy sud) kontenti lex.uz'dan olingan mahalliy korpusga bog'langan va tekshirilgan. Kodda keltirilgan har bir IPK/FK moddasi korpusda bor va sarlavhasi mos keladi. Mehnat va o'g'irlik yo'llarida protsessual matnlar bor (FPK va JPK mazmuni), lekin modda raqami deyarli yo'q, Mehnat kodeksi va JPK/JK esa korpusga umuman olinmagan. DXM va ClaimDraft uchun hech qanday huquqiy manba qayd etilmagan.

### Cited Findings

**Korpus provenansi:**
- FK1 (`lex.uz/docs/111181`, FK 1-qism, 21.12.1995), FK2 (`180550`, 29.08.1996), IPK (`3523891`, 24.01.2018), FPK (`3517334`, 22.01.2018). Hammasi `fetched_at: 2026-11-20`, `lang: uz-Latn`, `valid_to: null`, har bir modda uchun `lex_url` anchor bilan — `data/lex/IPK.jsonl:1`, `data/lex/FK1.jsonl:1`, `data/lex/FPK.jsonl:1`. Hajmi: FK 1179, FPK 430, IPK 346 modda (korpusni sanash).
- Plenumlar: OXS163 (Oliy xo'jalik sudi, 15.06.2007, 163-son, mulkiy javobgarlik/neustoyka, 20 band, `lex.uz/docs/-1636810`) va OXS234 (01.12.2011, 234-son, mulk ijarasi, 19 band, `lex.uz/docs/-2004613`) — `data/lex/plenum/OXS163.jsonl:1`, `OXS234.jsonl:1`.
- RAG rejasida JPK (`111463`) P1 deb belgilangan, lekin **olinmagan**. MJtK/MSIYuK "keyinroq". OXS283 (protsessual muddatlar, `-2712887`) rejada P0, lekin `data/lex/plenum/` da fayli yo'q — `LexSim_RAG_Qollanma.md:32-45`.
- Mehnat kodeksi rejada tilga olingan (`2-ai-qismi.md:267`), lekin `LexSim_RAG_Qollanma.md` jadvalida yo'q va korpusda ham yo'q.
- `Norms` faqat `valid_to IS NULL` bo'laklarni yuklaydi va `effectiveAt` ni lex.uz izohidagi oxirgi o'zgartirish sanasidan oladi. `verifiedAt` doim `None` ("mentor tasdiqlamaguncha") — `backend/lexsim_server.py:369-377, 394-401`.
- Ssenariy manbasi: "Iqtisodiy sud hal qiluv qarori (2023), ish raqami va barcha ismlar olib tashlangan", `mentorApproved: false`, `status: "qoralama — mentor tekshirishi kerak"` — `data/sud/ssenariy_ijara_qarzi.json:4-10`. Asl hujjat `sud keys.docx`: matn qatlamida atigi ~52 belgi bor (ichi rasm/skan), shuning uchun summalarni mashinada tekshirib bo'lmadi.
- Advokatlik etikasi: "Advokatlarning kasb odobi qoidalari (Advokatlar palatasi, 2013) — umumiy tamoyillar ... To'liq matni Lex.uz'da ochilmadi, mentor tekshirsin" — `data/sud/rollar.md:10`.
- Ovozlar: Chatterbox kodi `gokhaneraslan/chatterbox-finetuning`, MIT litsenziyasi — `GPU_Xizmatlar_Reranker_Chatterbox.md:133`. Rozilik qoidasi — `Chatterbox_Serverga_Ulash.md:81`. Bitta klon (PREZIDENT.ogg'dan olingan "taraf_erkak") egasining so'rovi bilan olib tashlangan — `backend/voices.json` (`_izoh_male`).

**Yo'nalishlar bo'yicha huquqiy kontent:**

| Funksiya | Ishlatiladigan normalar / kontent | Manba qayd etilganmi |
|---|---|---|
| F1 sud-ijara | IPK 20, 21, 22, 23, 62, 64, 165, 167, 168, 169, 171, 173, 175, 179, 186, 192. FK 260, 262, 326, 333, 541, 544, 578. OXS234-p9, OXS163-p4 (va `p12` ssenariyda). Shartnomaning 6.4 va 8.5-bandlari (o'ylab topilmagan, real ishdan) | Ha: korpus lex_url. Ssenariy "real qaror (2023)", raqami yashirilgan |
| F2 jonli protsedura | IPK 62, 169, 171. Vaziyatlar uchun izohlar (masalan, "Iqtisodiy sudda jinoiy jazo so'ralmaydi", "Sud ishlari davlat tilida yuritiladi; tarjimondan foydalanishga haqli") | Qisman: intents.json'da modda raqamisiz izohlar |
| F3 labour | Matnlar FPK mazmuniga mos: arizani 10 kun ichida qabul qilish (FPK 192), vakil guvoh bo'la olmaydi (FPK 56), apellyatsiya muddati 1 oy (FPK 385), JK 238 (yolg'on ko'rsatuv uchun ogohlantirish), "ishga tiklash qismi darhol ijro etilsin". Faktlar: 9–10-oktabr ishga kelmagan, 14-oktabr buyrug'i (47-k), 4,2 mln oylik, 5 yil staj | Modda raqami faqat JK 238 da. Mehnat kodeksining biror moddasi backend'da keltirilmagan |
| F4 theft | Ariza yozma yoki og'zaki (bayonnoma), anonim xabar ish qo'zg'atishga sabab bo'lmaydi, yolg'on xabar uchun ogohlantirish, "darhol ko'riladi; tekshiruv kerak bo'lsa — o'n sutkadan kechiktirmay", jabrlanuvchi huquqlari, tergovchi ustidan boshliqqa yoki prokurorga shikoyat | Modda raqami yo'q. "Bu Kodeks talabi" deyiladi, lekin qaysi modda ekani ko'rsatilmagan. JPK korpusda yo'q |
| F5 DXM | Enumlar: archive-reference, pension-recalculation, refer-elsewhere, written-complaint. Dalillar: passport, workbook-photos, employer-details, pension-decision, witness-statement. Spec: "Personaj ... modda keltirmaydi" | Yo'q. Pensiya, mehnat staji yoki DXM reglamentiga oid hech qanday hujjat korpusda yoki kodda yo'q |
| F6 ClaimDraft | court: district/regional/economic. demand: reinstate/punish/apology. pretrial, email, copies (0–5), signed | Yo'q. Da'vo arizasi rekvizitlari (FPK) bilan bog'lanmagan |
| F8 NLU | So'kinish, pora va qo'pollik regex ro'yxatlari, ostonalar | Huquqiy emas. Ostonalar "2026-11-21 kalibrlash" asosida (`nlu.py:11-13`) |
| F9 semantic | KM namunalari. 4-daraja uchun modda kalit so'zi kerak | `semantic.json` `_izoh`: 12 ta sinov gapi bilan kalibrlangan |
| F10 rubrika | VIOL_INFO: address/seated/order/interrupt → IPK 167; stage → IPK 165; unexamined → IPK 173; recusal_unfounded → IPK 20. Pora (−100), noqonuniy dalil (−10), false_claim (−5) — modda yo'q | Protsessual qismi IPK bilan bog'langan. Etika qismi manbasiz |
| F11 hints | `roles.json` `moddalar` ro'yxatlari (IPK-165, IPK-62, IPK-167 ...) | Ha, norm_id orqali korpusga |
| F13 RAG | FK, IPK, FPK va 2 ta plenum | Ha (lex.uz, 2026-11-20) |

**Korpus bilan solishtirilgan modda havolalari (fayl:qator → korpusdagi sarlavha):**

Iqtisodiy protsessual kodeks (IPK, lex.uz/docs/3523891):
- IPK 20 "Sudyani rad qilish", 21 "Prokurorni, ekspertni, ... rad qilish", 22 "Rad qilish haqidagi arizalar" — `backend/options.json:57` ("IPK 20–22-moddalar"), `lexsim_server.py:226`, `:305` (IPK-20). ✔ mos.
- IPK 23 "Rad qilish to'g'risidagi arizani hal etish tartibi" — `lexsim_server.py:226` (RECUSAL_DENY). ✔
- IPK 62 "Vakilning vakolatlarini rasmiylashtirish" — `lexsim_server.py:224-225, 233, 342`, `backend/intents.json:287` (powers_note), `backend/options.json:12`. ✔ (oxirgi tahrir: OʻRQ-683, 21.04.2021)
- IPK 64 "... vakolatlarini tekshirish" — `lexsim_server.py:342`, `data/sud/ssenariy_ijara_qarzi.json:142`. ✔
- IPK 165 "Sud majlisi" — `lexsim_server.py:224-226, 304`, `backend/options.json:95`. ✔
- IPK 167 "Sud majlisidagi tartib" (o'rnidan turish, «Hurmatli sud!», tik turib gapirish) — `lexsim_server.py:224, 230, 297-310, 1488`. ✔ Matn mazmuni ham mos.
- IPK 168 "Dalillarni tekshirish" — `lexsim_server.py:227`. ✔
- IPK 169 "Sudning ... arizalari va iltimosnomalarini hal qilishi" — `backend/procedure.py:154, 156, 207, 211, 214, 216`, `backend/options.json:134`, `lexsim_server.py:227`. ✔
- IPK 171 "Sud muhokamasini keyinga qoldirish" — `backend/procedure.py:221, 223`. ✔ (OʻRQ-541, 2019 tahriri)
- IPK 173 "Sud muzokaralari" — `backend/options.json:437, 475, 515`, `backend/semantic.json:119, 135`, `lexsim_server.py:228, 306, 345`. ✔
- IPK 175 "... maslahatxonaga kirishi", 179 "Hal qiluv qarorining mazmuni", 186 "Hal qiluv qarorini e'lon qilish" — `lexsim_server.py:229`. ✔
- IPK 192 "Hal qiluv qarorining qonuniy kuchga kirishi" (1 oy) — `lexsim_server.py:170, 229`. ✔ Lekin "bir oy ichida shikoyat" qismi aslida IPK 262 ga tegishli (1 oy, `data/lex/IPK.jsonl` IPK-262), T_ART'da IPK-262 yo'q.
- IPK 118 "Sud xarajatlarining taqsimlanishi" — `data/sud/ssenariy_ijara_qarzi.json:142`, `data/namunaviy_dialoglar.md:116`. ✔ (OʻRQ-888, 2024-01-01 dan)

Fuqarolik kodeksi (FK, lex.uz/docs/111181 va 180550):
- FK 260 "Neustoyka tushunchasi" (kreditor zararni isbotlashga majbur emas) — `backend/intents.json:248`, `backend/replies.json:323`. ✔ Matn mos.
- FK 262 "Neustoyka to'g'risidagi kelishuvning shakli" (yozma shakl) — `backend/options.json:348-349, 402-403`, `backend/replies.json:151, 299`, `lexsim_server.py:234`. ✔
- FK 326 "Neustoykani kamaytirish" — `lexsim_server.py:198, 228, 234, 1374, 1497` (`:319` faqat docstring misoli), `backend/options.json:271-272, 303, 314, 325-326, 359-360, 391, 402, 413, 514, 525`, `backend/replies.json:108, 116, 131, 154, 161, 167, 288, 387`, `backend/roles.json:99, 188, 210, 241`, `backend/scenarios/sud-ijara.json:324`. ✔ Mezonlar (bajarilish darajasi, mulkiy ahvol, kreditor manfaati) korpus matniga mos.
- FK 333 "Majburiyatlarni buzganlik uchun javobgarlik asoslari" — `backend/options.json:182-183, 314-315`, `backend/replies.json:360, 434`. ✔
- FK 541 "Ijaraga oluvchiga mol-mulkni topshirish" — `backend/replies.json:184` ("Dalolatnomani tuzish ijaraga beruvchining burchi edi, FK 541-modda"), `lexsim_server.py:343, 1358`. Raqam mavjud, lekin talqin zaif (pastga qarang).
- FK 544 "Mol-mulkdan foydalanganlik uchun haq to'lash" — `lexsim_server.py:208, 215, 233, 343, 1355, 1367`, `:2486`, `backend/options.json:171-172, 194, 225-226, 260-261, 271, 474, 485, 525-526`, `backend/replies.json:10, 129, 187, 259, 398, 413, 448`, `backend/roles.json:74, 157, 178, 231`, `backend/scenarios/sud-ijara.json:303`. ✔
- FK 578 "Bino yoki inshootni topshirish" (dalolatnoma yoki topshirishga doir boshqa hujjat) — `lexsim_server.py:233, 343, 1371`, `backend/options.json:214-215, 225, 485-486`, `backend/replies.json:13, 124, 176, 179, 425, 427`, `backend/roles.json:166`, `backend/scenario_pkg.py:55`, `backend/scenarios/sud-ijara.json:115, 304`. ✔
- Ssenariyda qo'shimcha: FK 8, 234, 324 — `data/sud/ssenariy_ijara_qarzi.json:142` (sarlavhalari tekshirilmadi, kodda ishlatilmaydi).

Plenumlar:
- OXS234-p9 (ijara haqini o'z vaqtida to'lash, FK 544 ikkinchi qismiga havola) — `lexsim_server.py:343`. ✔ Mazmun mos.
- OXS163-p4 (FK 326 bo'yicha kamaytirish, "eng kam miqdori FK 327 foizlaridan kam bo'lmasligi") — `lexsim_server.py:344`. ✔
- OXS163-p12 — `data/sud/ssenariy_ijara_qarzi.json:108, 142` (mazmuni tekshirilmadi).

Boshqa kodekslar (korpusda yo'q, tekshirib bo'lmaydi):
- Jinoyat kodeksi 238-modda (yolg'on ko'rsatuv) — `backend/voice_lines.json:343` (labour, guvohni ogohlantirish).
- Namunaviy dialoglarda FPK 225 "Ishni mazmunan ko'rishning boshlanishi" va FPK 248 "Sudning hal qiluv qarorini o'qib eshittirish" "o'xshash norma" sifatida IPK ishida keltirilgan — `data/namunaviy_dialoglar.md:47, 116`. FPK raqamlari korpusda bor va sarlavhalari mos.

**Labour qatorlari va FPK korpusi (modda raqami ilovada yo'q, mazmun solishtirildi):**
- "Sudya o'n kun ichida ajrim chiqaradi" (`voice_lines.json`, filing) ↔ FPK 192: "...ariza sudga kelib tushgan kundan e'tiboran o'n kundan kechiktirmay yakka tartibda hal etadi". ✔
- "vakil vakillik munosabati bilan bilgan holatlar bo'yicha guvoh bo'la olmaydi" (chamber) ↔ FPK 56 "Guvoh". ✔
- "Qaror ustidan bir oy ichida apellyatsiya shikoyati" (hearing) ↔ FPK 385. ✔

### Inferences
- F1 uchun "Manba bo'lmasa, modda yo'q" qoidasi (`LexSim_Backend_Spec.md:411-412, 432`) amalda bajariladi. KM_ARTICLE izohida ham "faqat bazada tasdiqlangan moddalar" deyilgan (`lexsim_server.py:232`). Kodda ishlatiladigan IPK/FK raqamlaridan birortasi ham korpusda yo'q emas.
- Labour matnlari FPK'ga yaxshi mos keladi, demak muallif FPK'dan foydalangan. Lekin bu bog'lanish hech qayerda yozib qo'yilmagan, shuning uchun foydalanuvchiga manba ko'rsatib bo'lmaydi.

### Gaps
- OXS163-p12, FK 8/234/324 mazmuni bu auditda o'qilmadi.
- JK 238, JPK (ariza qabul qilish muddatlari, anonim xabar, jabrlanuvchi huquqlari, shikoyat tartibi) va Mehnat kodeksi (ishdan bo'shatish asoslari, tushuntirish xati talab qilish, majburiy progul haqi) bo'yicha mahalliy manba yo'q. Ularni faqat lex.uz bilan tekshirish mumkin.

## 3. Zaif yoki manbasiz joylar, eskirgan tahrir xavfi, o'ylab topilgan va faqat demo uchun qilingan qismlar

### Takeaway
Eng katta xavflar: (a) mehnat yo'li Mehnat kodeksiga umuman bog'lanmagan (2023-yildan amaldagi yangi kodeks bilan solishtirilmagan); (b) o'g'irlik yo'li JPK/JK'siz; (c) DXM va ClaimDraft faqat enum va checkboxdan iborat demo shakllar, huquqiy rekvizitlarga bog'lanmagan; (d) asosiy qarordagi summalar (penya 3 040 580,45 → 30 405) skan hujjat bilan mashinada tekshirilmagan; (e) etika jazolari manbasiz; (f) plenumlar tugatilgan Oliy xo'jalik sudiniki (2007, 2011).

### Cited Findings

**Funksiyalar bo'yicha zaif joylar:**

| Funksiya | Zaif / manbasiz joy | Dalil (fayl:qator) |
|---|---|---|
| F1 | Real qaror summalari (asosiy qarz 25 620 433,19, penya 3 040 580,45 → 30 405, davlat boji 573 220,27, pochta 33 000) faqat qo'lda ko'chirilgan. Asl `sud keys.docx` skan bo'lgani uchun ularni mashinada tekshirib bo'lmaydi. Penyaning ~1 % gacha (100 baravar) kamaytirilishi g'ayrioddiy, raqam xatosi bo'lishi mumkin | `lexsim_server.py:166-169, 1496-1498`, `data/sud/ssenariy_ijara_qarzi.json:107` |
| F1 | Hisob-fakturalar yig'indisi da'vo summasiga teng emas, bu ataylab qoldirilgan ("mentor ko'rib chiqsin") | `data/sud/ssenariy_ijara_qarzi.json` E2 `note` |
| F1 | Butun ssenariy hali `mentorApproved: false`, `status: qoralama` | `data/sud/ssenariy_ijara_qarzi.json:4-10` |
| F1 | Barcha manbalarda `verifiedAt: null`. Hech bir modda mentor tasdiqlagan deb belgilanmagan | `lexsim_server.py:398` |
| F1 | "ustidan bir oy ichida shikoyat qilish mumkin" jumlasi IPK-192 ga bog'langan, aslida bu muddat IPK-262 da | `lexsim_server.py:170, 229` |
| F1 | FK 541 talqini: "Dalolatnomani tuzish ijaraga beruvchining burchi" — FK 541 mol-mulkni topshirish haqida. Dalolatnoma talabi esa FK 578 da (bino/inshoot uchun) | `backend/replies.json:184` |
| F1 | Namunaviy dialoglarda IPK ishi uchun FPK 225/248 "o'xshash norma" deb keltirilgan. Iqtisodiy ishda tegishli IPK moddasini ko'rsatish kerak | `data/namunaviy_dialoglar.md:47, 116` |
| F1 | Plenumlar Oliy xo'jalik sudining 2007 (163) va 2011 (234) yilgi qarorlari. Ularning kuchda ekani yoki Oliy sud Plenumi keyinroq yangi qaror qabul qilgani tekshirilmagan. `Norms.source` ularni "Oliy xo'jalik sudi Plenumi qarori" deb ko'rsatadi | `data/lex/plenum/*.jsonl:1`, `lexsim_server.py:392-394` |
| F1 | Sud ibora va dialoglari "qoralama ... aniq so'z shakllarini mentor tekshirishi kerak" | `data/sud_iboralari.md:3`, `data/sud/rollar.md:4` |
| F2 | Vaziyat izohlari ("davlat tilida yuritiladi; tarjimon", "jinoiy jazo so'ralmaydi", "mijoz manfaatiga zid") modda raqamisiz. Til normasi IPK'da bor, lekin bog'lanmagan | `backend/intents.json` (`situations`) |
| F3 | Mehnat kodeksi bo'yicha birorta ham modda yo'q: ishga kelmaslik asosida bo'shatish, kasallik varaqasi, tushuntirish xati so'ralmagani, "majburiy progul" haqi. "Ikki kun ishga kelmagan. Bo'shatish qonuniy" bahsi qaysi tahrirga asoslangani noma'lum | `backend/voice_lines.json` (labour consult/hearing qatorlari) |
| F3 | Qaror e'lon qilinishining ikki varianti ("rad etilsin" / "qanoatlantirilsin") va "ishga tiklash qismi darhol ijro etilsin" modda bilan bog'lanmagan. FPK korpusida "ishga tiklash" so'zi faqat FPK 449 da topildi, darhol ijro haqidagi modda aniqlanmadi | `voice_lines.json` hearing, FPK korpus qidiruvi |
| F3 | Ism va joy nomlari to'qima ("Namuna Savdo" MChJ, sudya B. Islomov, ish raqami 2-1407/26, buyruq 47-k). Bu o'quv uchun normal, lekin real ishga asoslanganmi, noma'lum | `voice_lines.json` |
| F4 | "o'n sutkadan kechiktirmay", "anonim xabar ish qo'zg'atishga sabab bo'la olmaydi", "Bu Kodeks talabi" — JPK raqamlarisiz. JPK korpusga olinmagan | `voice_lines.json` theft report, `LexSim_RAG_Qollanma.md:32` |
| F5 | DXM hujjati faqat enum (4 xizmat, 5 dalil turi, 3 xabar turi) va bo'sh matn maydonlaridan iborat. Spec bu enumlar faqat "Yo'qolgan staj" uchun ekanini tan oladi. Hujjat baholashda yagona mezon — `nextStep` 40 belgidan uzun bo'lsa, `document` darajasi kamida 3 bo'ladi | `lexsim_server.py:116-118, 1424-1425, 1728-1747`, `LexSim_Backend_Spec.md:487` |
| F5 | DXM endpoint'i (`/documents`) va baholash sud sessiyasida ham ishlaydi. Sud ssenariysi uchun "service_required" talabi ma'nosiz | `lexsim_server.py:2398-2410` |
| F6 | ClaimDraft — sof checkbox/enum: `demand` ∈ {reinstate, punish, apology}, `respondent` ∈ {company, director}, `court` ∈ {district, regional, economic}, `facts`/`evidence`/`attachments` — ≤32 belgilik ID'lar. Matn kiritish va real to'ldirish yo'q. Backend uni tekshirmaydi ham | `contracts.schema.json:6987-7010`, backend'da ClaimDraft kodi yo'q |
| F6 | `court` enumida "district/regional/economic" bor. Mehnat nizolari fuqarolik ishlari bo'yicha sudlar tasarrufida, bunday sud nomlari ham rasmiy nomlarga mos kelmaydi (masalan, "fuqarolik ishlari bo'yicha tumanlararo sud") | `contracts.schema.json` ClaimDraft |
| F10 | Etika jazolari (pora −100, noqonuniy dalil −10, false_claim −5, injection −5) va natijani 0 ga tushirish qoidasi hech qanday norma bilan bog'lanmagan. Advokatlik odob qoidalari matni ochilmagan | `lexsim_server.py:296-311, 1471-1474`, `data/sud/rollar.md:10` |
| F10 | Ball vaznlari (30/15/15/15/15/10) va 85/60 chegaralari mualliflik tanlovi. Biror metodik manbaga havola yo'q | `lexsim_server.py:1343-1344, 1479` |
| F9/F8 | Ostonalar 12 ta sinov gapida kalibrlangan, mentor eval to'plami hali yo'q | `semantic.json` `_izoh`, `nlu.py:11-13` |
| F14 | LLM raqib qo'shimcha moddalar "o'ylab topishi" mumkin. Himoya: `llm_check` va `allowed_refs` bor, lekin modda raqamlarini korpus bilan solishtirish faqat `numbers` ro'yxati bo'yicha qilinadi | `lexsim_server.py:473-506`, `scenarios.json` (`numbers`) |
| F15 | Ovoz klonlari bir nechta real yozuvlardan olingan (BETOFIQ.ogg, "Turing sud kelyabdi.mp3"). Rozilik faqat bitta holatda hujjatlashtirilgan (PREZIDENT klonining olib tashlanishi) | `backend/voices.json` |

### Inferences
- "Eski Mehnat kodeksi va yangi 2023 Mehnat kodeksi" xavfi: backend bu kodeksdan birorta modda keltirmagani uchun bevosita xato yo'q. Lekin frontend (yoki talaba hisobotlari) eski MK raqamlaridan (masalan, eski kodeksdagi 100-modda) foydalanayotgan bo'lsa, buni bu yerdan aniqlab bo'lmaydi. Frontendni alohida tekshirish kerak.
- "Eski IPK raqamlari" xavfi past: korpus 2018 IPK'ning amaldagi tahriri, barcha raqamlar mos keldi.

### Gaps
- Frontend fayllari yo'q bo'lgani uchun ClaimDraft "to'g'ri javob" kalitlari, labour/theft hisobotidagi moddalar va DXM ssenariy matnlari tekshirilmadi.
- Penya summasi (30 405) asl qarorda qanday ekanini bilish uchun `sud keys.docx` (skan) yoki public.sud.uz'dagi asl qaror bilan qo'lda solishtirish kerak.

## 4. Nimani olib tashlash yoki soddalashtirish mumkin va nima uchun rasmiy manba kerak

### Takeaway
Manbaga bog'langan yagona yadro — F1 (IPK+FK+2 plenum). Uni saqlab, mentor tasdig'ini (`verifiedAt`) qo'shish kerak. Demo shakllar (DXM DocumentDraft, ClaimDraft) yoki haqiqiy rekvizitlarga bog'lanishi kerak, yoki ochiq "demo" deb belgilanishi kerak. Mehnat va o'g'irlik yo'llari uchun Mehnat kodeksi, JPK va JK korpusga olinishi kerak, aks holda ulardagi huquqiy da'volarni ko'rsatmaslik lozim.

### Cited Findings
- DXM enumlari "hozir faqat 'Yo'qolgan staj' uchun", kontraktni ssenariydan dinamik qilish rejalashtirilgan — `LexSim_Backend_Spec.md:487`.
- Spec qoidasi: "Personaj huquqiy maslahat bermaydi, modda keltirmaydi" (DXM) va "Hech qachon model xotirasidan modda keltirmaslik" — `LexSim_Backend_Spec.md:383, 432`.
- RAG rejasidagi bajarilmagan qismlar: JPK (P1), OXS283 (P0), MJtK/MSIYuK — `LexSim_RAG_Qollanma.md:32-45`.
- Advokatlar odob qoidalari matni ochilmagan — `data/sud/rollar.md:10`.

**Tavsiyalar jadvali:**

| Funksiya | Olib tashlash / soddalashtirish | Kerakli rasmiy manba |
|---|---|---|
| F1 | AFTER_VERDICT'ga IPK-262 ni qo'shish. `replies.json:184` dagi FK 541 talqinini FK 578 ga o'tkazish yoki olib tashlash. `namunaviy_dialoglar.md` dagi FPK 225/248 ni IPK ekvivalentiga almashtirish | public.sud.uz'dagi asl hal qiluv qarori (summalar, penyani kamaytirish asoslari). Oliy sud Plenumining neustoyka va ijara bo'yicha amaldagi qarorlari (OXS163/234 kuchdami yoki almashtirilganmi) |
| F1/F12 | `verifiedAt` ni mentor tasdiqlagan normalar uchun to'ldirish jarayonini qo'shish | lex.uz amaldagi tahrir sanasi (`effectiveAt` allaqachon izohdan olinadi) |
| F2 | Vaziyat izohlariga norm_id qo'shish (til — IPK'dagi til moddasi; vakilning mijozga zid harakati — "Advokatura to'g'risida"gi qonun / odob qoidalari) | Advokatlar kasb odobi qoidalari (Advokatlar palatasi), "Advokatura to'g'risida"gi qonun |
| F3 labour | Mehnat kodeksi (2022-yil 28-oktabrda qabul qilingan, 2023-yil 30-apreldan amalda; bu sana lex.uz'da tekshirilishi kerak) korpusga olinmaguncha qarorda modda ko'rsatmaslik. Faktlarni yangi MK asoslari bilan solishtirish | Mehnat kodeksi (yangi tahrir), FPK (allaqachon bor: 56, 192, 385). Oliy sud Plenumining mehnat nizolari bo'yicha qarori. Real ishga tiklash qarorlari (public.sud.uz) |
| F4 theft | JPK'ni olish (`tools/lex_extract.py JPK=111463`) va JK'ni qo'shish. "o'n sutka", anonim xabar, ogohlantirish, shikoyat tartibini moddalarga bog'lash | JPK, JK (238 va o'g'irlik moddasi), IIV tartib hujjatlari |
| F5 DXM | Enum shaklini ochiq "o'quv demosi" deb belgilash yoki soddalashtirish. `nextStep > 40 belgi` mezonini olib tashlash yoki almashtirish. Sud sessiyasida `/documents` ni o'chirish | DXM davlat xizmati reglamenti (arxiv ma'lumotnomasi, mehnat stajini tasdiqlash, pensiyani qayta hisoblash), pensiya to'g'risidagi qonun |
| F6 ClaimDraft | `demand: punish/apology` va `court` enumlarini real variantlarga yaqinlashtirish. Rekvizitlar ro'yxatidan (FPK'dagi da'vo arizasi shakli va ilovalar moddalari) checklist qilish. Yoki erkin matn + rekvizit tekshiruvi | FPK: da'vo arizasining shakli/mazmuni va ilovalar moddalari (korpusda bor, raqamlari bu auditda aniqlanmadi). Davlat boji stavkalari |
| F10 | Etika jazolarini Advokatlar odob qoidalari bandlariga bog'lash yoki "mualliflik rubrikasi" deb belgilash | Advokatlar kasb odobi qoidalari, rubrika metodikasi (mentor) |
| F15 | Har bir klon ovoz uchun rozilik yozuvini saqlash | Ovoz egalarining yozma roziligi; "Shaxsga doir ma'lumotlar to'g'risida"gi qonun (`LexSim_Backend_Spec.md:562` da tilga olingan) |

### Inferences
- Eng arzon foyda: F1'dagi 3 ta kichik tuzatish (IPK-262, FK-541 talqini, FPK→IPK), mentor tasdig'i va asl qaror summalarini tekshirish. Eng katta bo'shliq: labour/theft/DXM uchun manbalar korpusi yo'q. Hozirgi holatda bu yo'llar "huquqiy jihatdan tekshirilmagan demo" deb ko'rsatilishi kerak.

### Gaps
- Mehnat kodeksining aniq qabul qilingan va kuchga kirgan sanasi, JK 238 ning hozirgi matni, OXS163/OXS234 ning kuchdaligi lex.uz'da tekshirilmagan (bu audit faqat mahalliy fayllar bilan cheklangan).
- FPK'dagi da'vo arizasi rekvizitlari moddalari raqami bu auditda aniqlanmadi.
