# LexSim: umumiy arxitektura

**Kimga:** hamkorlar, hakamlar, texnik mutaxassislar.
**Holat:** 2026-11-21, backend v1.5.0 jonli ishlayapti.

LexSim — huquqshunos talabalar uchun virtual amaliyot. Talaba advokat rolida:
- sud majlisini o'tkazadi;
- mijoz bilan maslahatlashadi;
- politsiyaga ariza beradi;
- DXM'ga murojaat qiladi;
- jamoaviy bahsda qatnashadi.

Sudya, raqib, kotib va mijozni tizim o'ynaydi: gapiradi, talabaning ovozini tushunadi, qonunga tayanadi va oxirida har bir ballni dalil bilan tushuntiradi.

---

## 1. Umumiy sxema

```
Talaba (brauzer)
   │  lexlab / lexsim.e-investment.uz — Next.js
   ▼
Frontend serveri ── kalitlar faqat shu yerda, brauzerga chiqmaydi
   │  HTTPS API (lex-api.e-investment.uz)
   ▼
┌──────────────── ILOVA SERVERI ───────────────────────────────┐
│ LexSim backend (Python)                                      │
│  ├─ Sud majlisi dvigateli (IPK bosqichlari, tanbeh, ajrim)   │
│  ├─ NLU — erkin gapni tushunish                              │
│  ├─ Javob tanlash: ssenariy → bank → LLM → zaxira           │
│  ├─ Raqib strategiyasi: taktikalar + talaba xatolarini kuzatish │
│  ├─ Baholash: «qoida + AI» rubrikasi, tushuntirish bilan     │
│  ├─ Case laboratoriyasi, jamoaviy bahs, mentor navbati       │
│  └─ Ovoz boshqaruvi (kesh, oldindan yozish, navbat)          │
│ LLM adapteri — provayderga bog'liq emas                      │
│ SQLite: sessiyalar, caselar, yechimlar, mentor qarorlari     │
└──────────▲────────────────────────────────────────────────────┘
           │ shifrlangan teskari tunnellar (ichki xizmatlar internetga ochilmagan)
┌──────────┴──────── BILIM SERVERI ────────────────────────────┐
│ RAG xizmati: PostgreSQL + pgvector, bge-m3 embedding         │
│ Qonunlar korpusi (lex.uz): ~4 800 bo'lak, 10 kodeks va qonun │
│ Zaxira ovoz va STT (protsessorda)                            │
└──────────▲────────────────────────────────────────────────────┘
           │ teskari tunnel
┌──────────┴──────── GPU SERVERI (NVIDIA RTX) ─────────────────┐
│ O'zbekcha TTS (Chatterbox, ovoz klonlash)                    │
│ O'zbekcha STT (Kotib)                                        │
│ Reranker (bge-reranker-v2-m3, cross-encoder)                 │
└───────────────────────────────────────────────────────────────┘
```

**Nega uch qatlam:**
- og'ir hisoblash (ovoz va reranker) GPU'da;
- bilim bazasi alohida;
- ilova yengil va tez: server javobi 40–75 ms.

Ichki serverlar internetga ochilmagan. Ular ilova serveriga o'zlari ulanadi, uzilsa 5–10 soniyada o'zi tiklanadi.

---

## 2. Asosiy texnologiyalar

| Qatlam | Texnologiya | Vazifasi |
|---|---|---|
| Frontend | Next.js, Netlify | 3D sud zali, "Ish yo'li", bahs xonasi, mentor sahifasi |
| Backend | Python (standart kutubxona), SQLite | API, sud dvigateli, baholash |
| Qidiruv (RAG) | PostgreSQL + **pgvector** (HNSW), **pg_trgm** | ma'no va so'z bo'yicha gibrid qidiruv |
| Embedding | **BAAI/bge-m3** (1024 o'lcham, ko'p tilli) | qonun moddalarini «ma'no vektori»ga aylantirish |
| Reranker | **BAAI/bge-reranker-v2-m3** (568M, fp16, GPU) | 30 nomzoddan eng to'g'ri 5 modda; erkin gapni variantga moslash |
| TTS | **Chatterbox**, o'zbek tiliga moslangan, ovoz klonlash | sudya, kotib, raqib, mijoz ovozlari |
| STT | **Kotib** (o'zbekcha, tinish belgilari bilan) | talaba nutqini matnga aylantirish |
| LLM | provayderga bog'liq bo'lmagan adapter | tayyor javob bo'lmaganda qahramon nutqi, bahs sudyasi, case tuzish |
| Tunnellar | SSH reverse tunnel, systemd | xavfsiz ulanish, avtomatik tiklanish |
| Kuzatuv | `/health`, `/metrics`, monitor paneli | GPU, STT tezligi, ovoz qamrovi, AI holati |

---

## 3. AI qatlami: qanday ishlaydi

### 3.1. Javob tanlash zanjiri
Har bir talaba gapiga javob shu tartibda tanlanadi:

1. **Qoidalar:** so'kinish, rolni buzishga urinish, «Hurmatli sud» murojaati.
2. **Tanish vaziyatlar:** «ishonchnoma uyda qoldi», «qaytaring», ruscha gap.
3. **Talaba tashabbusi:** iltimosnoma, guvoh, e'tiroz.
4. **Ssenariy va javoblar banki:** reranker ma'no bo'yicha moslaydi.
5. **LLM:** faqat yuqoridagilar mos kelmasa.
6. **Zaxira gap:** LLM javobi tekshiruvdan o'tmasa.

Natija: sud majlisidagi javoblarning ~99 % i tekshirilgan matn (ssenariy ~93 %, bank ~6 %). LLM faqat «bo'shliqlarni» to'ldiradi.

### 3.2. LLM'ni huquqiy domenga moslashtirish
Model to'g'ridan-to'g'ri ishlatilmaydi. U qahramonga aylantiriladigan to'rt qatlam ichida ishlaydi:

| Qatlam | Nima qiladi |
|---|---|
| **Rol va persona** | Har bir qahramon (sudya, raqib advokat, mijoz, navbatchi, tergovchi, DXM xodimi) uchun: kimligi, pozitsiyasi, uslubi, taqiqlari, ruxsat etilgan moddalar. Daraja bo'yicha kuch: `beginner` yumshoq, `advanced` «shaxmatchi» raqib |
| **Bilimga bog'lash (RAG)** | Talaba huquqiy savol bersa, lex.uz korpusidan 3 tagacha modda **rasmiy matni** bilan beriladi. Model faqat shularga tayanadi |
| **Kontekst** | Ish faktlari, majlis bosqichi, oxirgi 10–16 gap, talabaning hozirgacha zaif joylari |
| **Javob tekshiruvi** | Yangi raqam, ruxsatsiz modda, kirill, so'kinish yoki qaror chiqarish bo'lsa, javob tashlanadi va tayyor gap aytiladi |

Shaxsiy ma'lumot (telefon, pasport, JSHSHIR, karta, e-pochta) modelga yuborilishidan **oldin** yashiriladi.

### 3.3. Raqib strategiyasi
- **Taktikalar katalogi:** tadqiqot asosida 60 ta usul. Shulardan hozirgi ishda 8 tasi faol: raqam bilan langar, yon berib burilish, shior takrorlash, sudyaning sinov savollari va boshqalar. Hammasi qonuniy, yolg'on va soxta dalil yo'q.
- **Kuzatuv daftari:** raqib talabaning tan olishlari, javobsiz qolgan e'tirozlari va xato moddalarini yozib boradi. Yakuniy nutqda ularni talabaning **o'z so'zlari bilan** sudga eslatadi.
- **Natija:** har bir tuzoq uchun «tushmadi», «chiqib ketdi» yoki «tushdi» deb belgilanadi va ballga qo'shiladi.

### 3.4. Baholash: «qoida + AI»
- AI ball qo'ymaydi. U aniq savollarga «ha» yoki «yo'q» deydi va talabaning gapidan **iqtibos** keltiradi. Server iqtibosni bayonnomadan tekshiradi va ballni o'zi hisoblaydi.
- Mezonlar standartlarga bog'langan:
  - Jessup (xalqaro moot);
  - SQE2 (Angliya advokatlik imtihoni);
  - Adliya vazirligining 3637-son Nizomi.
- **Uch bosqichli tekshiruv:**
  - tizim tekshiradi;
  - AI shubhali ishni mentorga yuboradi, AI «yaxshi» deganlarining 3 % i ham tasodifiy auditga tushadi;
  - mentor qaror qiladi.

  Mentor qarorlaridan AI'ning aniqligi avtomatik o'lchanadi (Koen kappasi, maqsad ≥ 0,61).

---

## 4. Ovoz tizimi
- **4 ta rol ovozi**, klonlash orqali.
- **Oldindan yozish:** tizim aytadigan barcha doimiy gaplar (444 ta) GPU'da oldindan yoziladi va keshga qo'yiladi. Shuning uchun talaba javobni pauzasiz eshitadi.
- **STT birinchi navbatda:** talaba gapirsa, ovoz yozish to'xtab turadi va GPU STT'ga bo'shaydi.
- **Uzun nutq:** 60 soniyagacha, jim joylardan bo'laklab tanitiladi.
- **O'zbekcha sonlar** raqamga aylantiriladi: «besh yuz qirq to'rtinchi moddasiga» → «544-moddasiga».
- **Ishonch bahosi:** tanish ishonchsiz bo'lsa, matn javob deb qabul qilinmaydi va sudya qayta so'raydi.

---

## 5. Bilim bazasi (RAG)

| Hujjat | Moddalar |
|---|---|
| Fuqarolik kodeksi (1–2-qism) | 1 196 |
| Iqtisodiy protsessual kodeks | 390 |
| Fuqarolik protsessual kodeksi | 513 |
| Mehnat kodeksi | 594 |
| Jinoyat-protsessual kodeksi | 773 |
| Jinoyat kodeksi | 406 |
| Murojaatlar, Davlat boji, Advokatura, Advokatlik kafolatlari to'g'risidagi qonunlar | 114 |
| Plenum qarorlari (Oliy sud, Oliy xo'jalik sudi) | bandma-band |

- Manba faqat lex.uz. Har bir bo'lakda havola, olingan sana va matn xeshi saqlanadi.
- Qonun o'zgarsa, faqat o'zgargan moddalar yangilanadi.
- Ishonch past bo'lsa (< 0,3), modda aytilmaydi va javob to'qilmaydi.

---

## 6. Xavfsizlik va ishonchlilik
- **Kalitlar faqat serverda.** Talaba tuzlangan xesh bilan aniqlanadi. Bir talaba boshqasining ishini ko'ra olmaydi.
- **CORS** faqat bizning saytlarga ruxsat beradi. So'rovlar soni chegaralangan. Ichki xizmatlar internetga ochilmagan.
- **Shaxsiy ma'lumot:** logga talaba matni yozilmaydi. Ma'lumot muddat o'tgach avtomatik o'chiriladi (majlis 7 kun, case 180 kun). Har kuni zaxira nusxa olinadi.
- **Yangilash:** 109 ta avtomatik test, alohida sinov nusxasi, zaxira olish. Xato bo'lsa, eski versiya avtomatik qaytadi. Qayta ishga tushirish ~7 soniya.
- **Barqarorlik:** GPU o'chsa ham tizim ishlaydi. Ovozlar keshdan chiqadi, STT protsessorga, RAG rerankersiz rejimga o'tadi.

---

## 7. Raqamlar

| Ko'rsatkich | Qiymat |
|---|---|
| Qonunlar bazasi | ~4 800 bo'lak, 10 hujjat |
| RAG qidiruvi | ~0,9 s |
| STT | ~2,2 s / gap; qisqa gaplarda xato (WER) 7,8 % |
| Server javobi | 40–75 ms |
| Oldindan yozilgan ovoz | 444 gap |
| Avtomatik testlar | 109 |
| Sohalar | 11 (Oliy sud 2025 statistikasi bo'yicha tartiblangan) |
| Taktikalar katalogi | 60 usul, 8 tasi faol |

---

## 8. Keyingi qadamlar
1. **Modelni o'z ma'lumotimizda moslashtirish (fine-tune):** mentorlar baholagan «oltin to'plam» va haqiqiy bahs bayonnomalari yig'ilgach.
2. **Tezlik:** LLM javobini 2–4 soniyaga tushirish (ajratilgan API kanali).
3. **Yangi ssenariylar:** yetkazib berish (24 %), kommunal (19 %), kredit (13 %).
4. **STT'ni** haqiqiy talaba ovozlari to'plamida sinash va sozlash.
5. **Mentor tasdig'i:** ssenariylar va AI bahosini rasmiy tasdiqlash.
