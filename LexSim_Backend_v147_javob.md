# Backend v1.4.7 — `LexSim_Backend_Vazifalar.md` ga javob

**Kimga:** frontend dasturchisi.
**Sana:** 2026-11-21.
**Server:** `https://lex-api.e-investment.uz/api/v1`.

**O'rnatildi.** v1.4.7 serverda ishlayapti. Loyiha egasining ruxsati bilan kunduzi qayta ishga tushirildi.
- O'rnatishdan oldin 54 ta test o'tdi.
- Eski versiya zaxirada saqlangan.

**Tekshirish:** `/health` → `"version": "1.4.7"`. Yangi `features`:
- `stt-priority`
- `powers-excuse-first`

**Kontrakt:** o'zgarmadi.

---

## 1. 🔴 «Ishonchnoma uyda qolib ketibdi» → «Vakolat tekshirildi» ✅

**Sabab.** Siz to'g'ri topdingiz. Vakolat bosqichida avval «ishonchnoma» so'zi tekshirilardi, bahona esa undan keyin. Shuning uchun «ishonchnoma uyda qolib ketibdi» degan gap «vakolat bor» deb qabul qilindi.

**Tuzatish.** Bahona va inkor endi «ishonchnoma» so'zidan **ustun**. Taniladigan gaplar:
- «uyda qoldi», «qolib ketibdi»;
- «unutibman», «olib kelmadim», «olmadim»;
- «keyin beraman», «ertaga olib kelaman»;
- «yonimda yo'q», «yo'q»;
- «yo'qotdim», «topolmayapman»;
- ruscha «нет», «забыл».

| Talaba (`advanced`, vakolat bosqichi) | Sudya |
|---|---|
| 1-marta: «Hurmatli sud, ishonchnoma uyda qolib ketibdi.» | «Tushunaman, bunday holat bo'lib turadi. Lekin vakolatingizni tasdiqlovchi hujjatsiz sud sizni vakil sifatida majlisga qo'ya olmaydi. Ishonchnoma yoki uning nusxasi yoningizda yo'qmi?» (`uncertain`, `lean-in`). Bosqich o'zgarmaydi |
| 2-marta: «…olib kelmadim, keyin beraman.» | Oqibatni aytadi va vakil **majlisga qo'yilmaydi** (`NO_POWERS`). Sessiya `report-ready` |
| «Hurmatli sud, ishonchnomani taqdim etaman.» | «Vakolat tekshirildi.» Odatdagidek davom etadi |

`beginner` va `intermediate` darajalarda 2-marta vakil chiqarilmaydi: sudya «vakolat tasdiqlanmadi» deb qayd etadi, ball ayiriladi va majlis davom etadi.

**Qabul:** `node tools/qa/live.mjs` → **14/14** («an excuse is answered» va «not admitted» ✓).

---

## 2. 🔴 STT 30–45 s qotishi ✅

**Sabab.** Siz to'g'ri topdingiz. Ovoz renderi va STT bitta GPU'da navbat talashardi.

**Tuzatish: STT birinchi navbatda.**
- `POST /voice/stt` kelishi bilan render **to'xtaydi**.
- Oxirgi STT'dan keyin 25 s davomida render yangi gapni boshlamaydi.
- Talaba gapirib turgan paytda GPU faqat STT'ga ishlaydi.
- Talaba jim bo'lsa, render o'zi davom etadi.

**Bitta cheklov.** STT kelgan paytda render bitta gapni yozayotgan bo'lsa, o'sha gap tugaguncha (~10–16 s) kutiladi. Bu odatda bo'lmaydi: talaba gapirayotgan paytda yangi gap boshlanmaydi, demak faqat gapning **birinchi** STT so'rovi ba'zan shunga to'g'ri kelishi mumkin. Shunday holat ko'p uchrasa, katta renderni faqat kechasi o'tkazamiz (2-taklifingiz).

**`upload` (0,6 s).** Hozircha o'zgartirmadim. Opus yoki FLAC 16 kHz WAV'dan 3–4 barobar kichik, lekin serverda ularni yechish vaqt oladi. `upload` p95 0,84 s, asosiy muammo `model` edi. Agar sinovdan keyin ham p95 > 3 s bo'lsa, keyingi qadam shu bo'ladi.

**Qabul:** `node tools/qa/stt-timing.mjs` kunduzi, render ketayotgan paytda: `total` p95 ≤ 3 s. Natijani yuboring. Chiqmasa, `timings` bilan birga ko'ramiz.

---

## 3. 🟠 Ovoz qamrovi

Render davom etyapti. Endi u talaba STT'si paytida pauza qiladi, shuning uchun biroz sekinroq tugaydi. Tugagach xabar beraman, siz `voice-coverage.mjs` ni qayta ishga tushirasiz.

---

## 4. `situation` bo'yicha savollaringiz

**1. DXM fuqarosi.** `client` to'g'ri, alohida `citizen` shart emas. DXM uchun boshqacha gap kerak bo'lsa, keyin `citizen` qo'shamiz va `client` ni zaxira qilib qoldiramiz.

**2. `situation` da `audio`.** Yaxshi taklif, **v1.4.8 da** bo'ladi: `replies[rol].audio[]` — har bir `lines[i]` uchun `{id, url, durationMs, voice}`, xuddi `npcTurn.audio` kabi. Hozircha `POST /voice/tts` qiling. Bu gaplar prerender ro'yxatida, render tugagach keshdan tez keladi.

**3. Haqiqiy javob.** Bugungi `/nlu/match`, v1.4.7, ~390 ms:

```
POST /nlu/match
{"utterance":"yoʻqotib qoʻydim. topolmayapman.",
 "candidates":[{"id":"o1","text":"Ariza yozma boʻladi"},{"id":"o2","text":"Ogʻzaki ariza beraman"}],
 "inputMode":"text"}
```

```json
{
  "match": null,
  "alternatives": [{"id": "o1", "score": 0.001}],
  "quality": {"address": false, "articles": [], "ethics": "ok", "politeness": 0.8},
  "clarify": null,
  "engine": "reranker",
  "thresholds": {"match": 0.6, "clarify": 0.25, "margin": 0.15, "stt_min": 0.5, "fact": 0.3},
  "ms": 390,
  "reason": "no_match",
  "situation": {
    "id": "lost_document",
    "tone": "info",
    "note": "Hujjat yoʻq — qahramon vaziyatni tushundi, qonuniy yoʻlni aytdi.",
    "ethics": false,
    "replies": {
      "officer":      {"emotion": "calm",      "voices": ["male"],           "lines": ["Tushunaman, bunday boʻladi. Unda arizani ogʻzaki aytib bering — bayonnomaga yozaman. Shaxsingizni tasdiqlovchi hujjat bormi?"]},
      "investigator": {"emotion": "calm",      "voices": ["male"],           "lines": ["Hujjat boʻlmasa, holatni soʻzma-soʻz aytib bering — bayonnomaga yoziladi."]},
      "clerk":        {"emotion": "neutral",   "voices": ["female"],         "lines": ["Hujjatlarsiz arizani roʻyxatga ololmayman. Iltimos, hujjatlarni toʻliq olib keling."]},
      "client":       {"emotion": "uncertain", "voices": ["male", "female"], "lines": ["Voy… Qayerga qoʻyganimni eslay olmayapman. Endi nima qilamiz?"]},
      "judge":        {"emotion": "uncertain", "voices": ["elder_m"],        "lines": ["Hujjat boʻlmasa, sud uni dalil sifatida koʻra olmaydi. Boshqa dalilingiz bormi?"]},
      "chief":        {"emotion": "calm",      "voices": ["elder_m"],        "lines": ["Hujjatsiz ham shikoyatni qabul qilamiz, lekin holatni aniq bayon qiling."]}
    }
  }
}
```

Unit testingiz uchun e'tibor bering:
- `replies` da **faqat shu vaziyatga gapi bor rollar** keladi. Masalan, `lost_document` da `respondent` va `witness` yo'q. Rol bo'lmasa, odatdagi «tushunmadim» gapini ishlating.
- `tone: "info"` va `ethics: false` — bu xato emas, ball ayirmang. Ball faqat `tone: "bad"` bo'lsa ayiriladi.
- Matndagi apostrof `ʻ` (U+02BB). TTS'ga matnni o'zgartirmasdan yuboring, aks holda kesh kaliti boshqacha chiqadi.

---

## Sizdan

```bash
curl -s https://lex-api.e-investment.uz/api/v1/health   # "version": "1.4.7"
node tools/qa/live.mjs                                  # 14/14
node tools/qa/stt-timing.mjs <20 ta wav>                # total p95 ≤ 3 s (kunduzi)
```

Natijalarni raqamlar bilan yuboring.
