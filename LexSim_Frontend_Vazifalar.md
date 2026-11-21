# LexSim — frontend uchun vazifalar (backend v1.4.5 / v1.4.6 dan keyin)

**Kimga:** frontend dasturchisi.
**Sana:** 2026-11-21.
**Server:** `https://lex-api.e-investment.uz/api/v1`. v1.4.5 va v1.4.6 bugun **22:05** da o'rnatiladi.

**Batafsil:**
- [LexSim_Backend_Vazifalar_javob.md](LexSim_Backend_Vazifalar_javob.md) — v1.4.5: STT, `npcTurn.audio`, qayta so'rash;
- [LexSim_Backend_v146_odamdek.md](LexSim_Backend_v146_odamdek.md) — v1.4.6: odamdek javoblar.

**Tartib:** 1 → 7. Har bir ish oxirida "Qabul" bandi bor.

---

## 0. Nega

21-noyabr jonli sinovida "Ish yo'li" va DXM'da talaba kutilmagan narsa yozsa yoki gapirsa, qahramonlar har safar «Kechirasiz, tushunmadim» dedi:
- so'kinishga ham («boshligingni sikkaman», «pashol naxuy»);
- mazmunli gapga ham («yordam bera olmayman», «yoʻqotib qoʻydim»).

Bu robotdek eshitiladi.

Backend endi bunday vaziyatlarni taniydi va har bir qahramon uchun **tayyor, odamdek, ovozlashtirilgan javob** beradi. Uni ijro etish sizning qismingiz (1-ish).

---

## 1. `/nlu/match` → `situation`: «tushunmadim» o'rniga odamdek javob (eng muhimi)

**Nima keladi.** `/nlu/match` javobida ixtiyoriy `situation` maydoni bo'ladi:

```json
"situation": {
  "id": "profanity" | "lost_document" | "refusal" | "russian" | "offtopic",
  "tone": "bad" | "info",
  "ethics": true,
  "note": "So'kinish — kasbiy etikaning qo'pol buzilishi.",
  "replies": {
    "client":  {"emotion": "upset", "voices": ["male", "female"], "lines": ["…", "…"]},
    "officer": {"emotion": "impatient", "voices": ["male"], "lines": ["…"]}
  }
}
```

`replies` kalitlari sizning `CaseSpeaker` bilan bir xil: `client`, `officer`, `investigator`, `chief`, `clerk`, `secretary`, `judge`, `respondent`, `witness`.

**Qilish kerak:**
1. `/nlu/match` javobini o'qiyotgan joyda: `situation` bor va `replies[hozirgi_so'zlovchi]` mavjud bo'lsa, umumiy «tushunmadim» gapi o'rniga shu gapni ijro eting.
   - Variant tanlash: bir sessiyada navbat bilan, ketma-ket bir xil gap chiqmasin.
   - So'zlovchi uchun javob bo'lmasa, hozirgidek «tushunmadim».
2. **Yuz va ovoz:**
   - `emotion` ni aktyor yuziga qo'ying;
   - ovoz `voices` dan, aktyor jinsiga mos bo'lsin. Masalan, theft'dagi mijoz ayol, demak `female`.
   - TTS'ga matnni **o'zgartirmasdan** yuboring, chunki gaplar shu matn bilan prerender qilinadi.
3. **Baholash:**
   - `tone: "bad"` → bu gapni xato deb hisobot va logga yozing, izoh — `situation.note`;
   - `ethics: true` → etika mezoni bo'yicha baholang. Bu holda `quality.ethics` ham `"violation"` bo'ladi.
4. **Oqim:** bosqich o'zgarmasin. Qahramon javobidan keyin talabaning savoli yoki navbati ochiq qolsin.
5. **DXM:** DXM sessiyasida ham talabaning erkin gapini `/nlu/match` ga yuboring (`candidates` — o'sha paytdagi variantlar). `situation` kelsa, xuddi shunday ijro eting. Hozir DXM'da «pashol naxuy» ga kampir «Men tushunmayman bu ishlarni…» deydi.

**Ustunlik tartibi:**
1. `situation`;
2. `match`;
3. `clarify`;
4. umumiy «tushunmadim».

**Qabul (22:05 dan keyin):**

| "Ish yo'li"da yozing | Kutilgan javob |
|---|---|
| labour, mijozga: «boshligingni sikkaman» | Mijoz: «Nima?! Bunaqa gaplarni sizdan kutmagan edim…» (`upset`), hisobotda etika xatosi |
| labour, mijozga: «man yordam bera olmayman» | Mijoz: «Qanday qilib?! Men sizga umid bilan kelgandim…» |
| theft, navbatchiga: «yoʻqotib qoʻydim. topolmayapman.» | Navbatchi: «Tushunaman, bunday bo'ladi. Unda arizani og'zaki aytib bering…» |
| istalgan xonada: «ishlaringiz qalay?» | O'sha qahramonning «ishga qaytaylik» gapi |
| DXM: «pashol naxuy» | Kampir yoki xodimning so'kinishga munosabati, etika xatosi |

`voice-coverage.mjs` bu gaplarning hammasi `hit` ekanini ko'rsatsin. Avtomatik render o'rnatilgandan keyin ~1 soatda yozib bo'ladi.

---

## 2. `npcTurn.audio`: ovozni javob bilan birga olish

Sud zalidagi har bir `npcTurn` da, gap keshda tayyor bo'lsa, quyidagi maydon bo'ladi:
```json
"audio": {"id": "…-1795232101", "url": "/api/v1/voice/cache/….mp3", "durationMs": 2928, "voice": "elder_m"}
```

**Qilish kerak:**
- `audio` bor va `audio.voice` siz shu rol uchun tanlagan ovoz bilan bir xil bo'lsa, `POST /voice/tts` qilmang. `audio.url` ni to'g'ridan-to'g'ri yuklang (cookie yoki kalit bilan) va javob bilan bir vaqtda oldindan yuklab qo'ying.
- Ovoz boshqacha bo'lsa yoki `audio` yo'q bo'lsa, hozirgidek `POST /voice/tts`.
- URL `immutable`, uni brauzer keshiga qo'yish mumkin. Ovoz yangilansa, URL o'zgaradi.

**Qabul:** sud zalida ochilishdan muzokaragacha TTS so'rovlari soni kamida 90 % ga kamaysin. Har bir sud gapi pauzasiz eshitilsin.

---

## 3. STT ishonchi: noto'g'ri tanilgan gapni yubormaslik

`POST /voice/stt` javobida endi `confidence` (0–1), `lowConfidence` va `timings` bor.

**Qilish kerak:**
1. `lowConfidence: true` bo'lsa, matnni javob sifatida **yubormang**. Aktyor ovoz chiqarib qayta so'rasin: siz qilgan «Kechirasiz, tushunmadim…» gaplari.
2. Boshqa holatlarda `turns` ga yuborayotganda `stt: {"confidence": <son>, "durationMs": <audio ms>}` ni qo'shing. Backend `confidence < 0,5` bo'lsa, sudya qayta so'raydi va ball ayirmaydi.
3. "Ish yo'li"da `/nlu/match` ga ham `stt.confidence` ni yuboring.

**Qabul:** shovqin yoki ma'nosiz audio javob sifatida ketmaydi, aktyor qayta so'raydi. Aniq gap esa odatdagidek ishlaydi.

---

## 4. STT tezligini o'lchash

Backend o'lchovi (GPU yoniq, server ichida, 6 s audio): **p50 1,8 s, p95 2,4 s**. Sizda ~4 s chiqqan edi.

**Qilish kerak:**
1. 20 ta ovozli javob uchun yozib boring:
   - mikrofon to'xtagan payt;
   - so'rov yuborilgan payt;
   - javob kelgan payt;
   - javobdagi `timings` (`convert`, `upload`, `model`, `total`).
2. Audioni **16 kHz, mono, 16-bit WAV** da yuboring (`Content-Type: audio/wav`). Shunda serverda formatni o'zgartirish umuman bo'lmaydi.
3. Natijani yuboring. Vaqt qayerga ketayotganini birga ko'ramiz: Netlify, internet yoki server.

**Qabul:** 20 ta o'lchov jadvali, p50 va p95.

---

## 5. Sud zali: yangi xatti-harakatlarni ko'rsatish

Bular backend'ning o'zida bajariladi, siz faqat to'g'ri ko'rsatishingiz kerak.

| Holat | Backend nima yuboradi | Sizdan |
|---|---|---|
| «ha» yoki ma'nosiz gap | sudya qayta so'raydi (`uncertain` / `lean-in`), `decisions` → `info` | ko'rsatish, ball ayirmaslik |
| So'kinish | 1–2 marta ogohlantirish (`upset`), 3-marta zaldan chiqarish, `status: report-ready` | 3-holatda majlisni yakunlab, hisobotni ochish |
| «mijozimni qamang», «uyda qolib ketibdi» va hokazo | odamdek javob, tegishli `emotion` va `reactions` | `reactions` ni tinglovchilar yuziga qo'yish |

**Qabul:** `node tools/qa/live.mjs` → 8/8. Yangi yo'llarni QA'ga qo'shing:
- «ha» → qayta so'rash;
- 3 marta so'kinish → `report-ready`;
- «uyda qolib ketibdi» (`advanced`) → ikkinchi safar vakil majlisga qo'yilmaydi.

---

## 6. `male` ovozi o'zgardi

Loyiha egasining so'rovi bilan `male` ovozi almashtirildi. Bu ovoz mijoz, guvoh, navbatchi va tergovchi rollarida ishlatiladi.
- Brauzer yoki CDN keshida eski `male` audiolari qolgan bo'lsa, tozalang. Ayniqsa `lines.json` gaplari uchun kesh kaliti matnga bog'liq bo'lsa.
- `npcTurn.audio` URL'lari o'zi yangilanadi.

**Qabul:** "Ish yo'li"dagi erkak rollar yangi ovozda gapiradi.

---

## 7. O'rnatishdan keyin tekshirish

22:05 dan keyin yoki ertaga ertalab:

```bash
curl -s https://lex-api.e-investment.uz/api/v1/health   # "version": "1.4.6", voice.stt, voice.coverage
node tools/qa/voice-coverage.mjs                         # FAIL 0; case 115/115
node tools/qa/live.mjs                                   # 8/8
```

Natijalarni raqamlar bilan yuboring. Har bir ish uchun «Qabul» bajarildi yoki bajarilmadi, sababi bilan.

---

## Keyinroq: loyiha egasining qarorlaridan keyin

| Ish | Nimani kutadi |
|---|---|
| `POST /records` uchun rozilik oynasi va "O'qituvchiga yuborish" tugmasi | saqlash siyosati (E6) |
| Ovozlar palitrasi (`scene.voices`) | ovoz namunalari (E3) |
| Erkin gapga jonli javob (LLM) | tez LLM kaliti (E5) |
