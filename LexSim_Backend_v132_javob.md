# BACKEND_V13_REPLY.md ga javob — backend v1.3.2

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `http://192.168.88.110:8100/api/v1`.
**Eslatma:** sizning xatingiz `/health` → `1.2.0` holatida yozilgan. Undan keyin `1.3.1` chiqdi (B1, B5, B6, B7 — [LexSim_Backend_v3_javob.md](LexSim_Backend_v3_javob.md)). Bu hujjat qolgan so'rovlarga javob.

| | Holat |
|---|---|
| B1 `features` | ✅ siz yozgan nomlar bilan, `scripted` va `chatterbox` ham bor |
| B2 bank 60–80 ta + `fallback_ratio` | ✅ bank **57 ta** variant (25 tadan). `/metrics`: `lexsim_reply_fallback_ratio`, `lexsim_reply_llm_ratio` |
| B3 variantlar | ✅ v1.3.1 da qayta yozilgan (1 to'g'ri + 2 deyarli to'g'ri + 1 qo'pol). Har bir variantning izohi bor |
| B4 STT | ✅ **tezlik: GPU STT ulandi, 5 s audio ~1 s** (mezon ≤ 3 s). `confidence` hali `null` — 2-bo'lim |
| B5 aniq `feedback` | ✅ zid fakt nomlanadi. To'g'ri javobda nega to'g'ri ekani va modda aytiladi |
| B6, B7 | ✅ (v1.3.1) |
| `contracts.schema.json` bo'yicha CI | ✅ `tests/test_contract.py` |
| `lines.json` — 97 ta gap | ✅ Chatterbox GPU'da render qilinmoqda, rollarga mos ovozlar bilan |
| §5 moddalarni lex.uz matni bilan solishtirish | ✅ 3-bo'lim |

---

## 1. Bajarilgan ishlar

### B1
```
GET /health → "version": "1.3.2",
"features": ["levels","reveal-options","silence","scripted","nlu","store","xapi","prerender","chatterbox",
             "reply-bank","voice-key","tts-duration"]
```

### B2 — bank 57 ta variant

| Raqib | Lahza | Variantlar |
|---|---|---|
| Javobgar vakili (talaba — da'vogar) | `answer` — da'voga e'tiroz | 12 |
| | `closing` — yakuniy nutq | 9 |
| Da'vogar vakili (talaba — javobgar) | `rebut` — e'tirozga javob | 14 |
| | `on_motion` — penya iltimosnomasiga | 13 |
| | `closing` | 9 |

**Yangi mavzular:**
- foydalanish muddati qisqa;
- moliyaviy ahvol;
- summa noto'g'ri;
- kelishuv taklifi;
- imzoni inkor etish;
- obyekt sifati;
- kreditor zarari (FK 260);
- aybsizlik (FK 333);
- qisman kamaytirish;
- bo'lib to'lash;
- tekshirilmagan holatga tayanish va boshqalar.

**`/metrics`:**
```
lexsim_reply_total{source="bank|generic|llm"}
lexsim_reply_fallback_ratio   # (generic + llm) / jami — bankdan mos javob topilmagan ulush
lexsim_reply_llm_ratio        # LLM'ga tushgan ulush (faqat advanced)
```

### B5 — aniq izohlar

**Materiallarga zid gap:** qaysi fakt bilan zid ekani aytiladi. Talaba "dalolatnoma imzolangan edi" desa:
> «Ish materiallarida topshirish dalolatnomasi yoʻq (F3) — sudga mavjud boʻlmagan dalilni aytish uni chalgʻitadi.»

Boshqa zid gaplarga ham aniq izoh bor:
- hisob-fakturalarni inkor etish → F2;
- foydalanmaganlik → F3;
- penya shartnomada yo'q → 8.5-band;
- tekshirilmagan holat → IPK 173.

Hammasi [backend/semantic.json](backend/semantic.json) da, mentor tahrirlaydi.

**To'g'ri javob (beginner):** bir jumla bilan nega to'g'ri ekani va modda aytiladi:
> «Toʻgʻri: Vakilning vakolati ishonchnoma bilan tasdiqlanadi (IPK 62-modda) va sudga «Hurmatli sud» deb murojaat qilinadi.»

- Har bosqichning to'g'ri variantida `why` maydoni bor.
- Matn bilan javob berilganda ham shu izoh ishlatiladi.
- **Da'vo talabi to'liq bo'lmasa**, maqtov o'rniga nima yetishmagani aytiladi: «Talabda yetishmadi: penya asosi (8.5-band).»

### CI — kontrakt testi

`tests/test_contract.py` to'liq oqimni yurgizadi: ikkala ssenariy × uchala daraja, ochilishdan hisobotgacha. Har bir javob sizning `contracts.schema.json` ingizga qarshi tekshiriladi:
- `Snapshot`;
- har bir `MutationResponse`;
- `Assessment`;
- `Hint`.

**Natija: hammasi mos.** `jsonschema` kutubxonasi serverda yo'q (o'rnatish server egasining ruxsatini talab qiladi). Shuning uchun sxemada ishlatilgan kalit so'zlar uchun kichik validator yozildi: `type`, `properties`, `required`, `enum`, `const`, `items`, `anyOf` va chegaralar.

**Jami testlar:** 15 ta (14 unit + 1 kontrakt), hammasi yashil. `tools/backend_sinov.py` integratsiya sinovi ham o'tdi.

### `lines.json` — 97 ta gap

- **Render:** server tomonda Chatterbox GPU'da, har bir gap o'z ovozi bilan (`elder_m` 37, `male` 36, `female` 20, `female_alt` 4). Tugagach, `/voice/tts` shu matn va ovoz uchun keshdan ~5–60 ms da qaytaradi.
- **Sizning `prerender.mjs` skriptingiz** baribir ishlaydi. Ro'yxat o'zgarsa yoki yangi gap qo'shilsa, faqat yangilari render qilinadi, qolganlari keshdan olinadi.
- **Matn o'zgarmaydi.** Siz yuborgan `ʻ`/`ʼ` saqlanadi. Bir xil `{text, voice}` har doim bir xil keshga tushadi.
- **Ovozlar haqida:** rollar uchun haqiqiy ovozlar hali klonlanmagan, namunalar va rozilik kerak. Hozircha "Standart ovoz" va rolga qarab balandlik filtri ishlatiladi. Klonlangach, ular qayta render qilinadi.

---

## 2. B4 — STT: GPU'ga o'tkazildi

- **STT endi GPU kompyuterda ishlaydi** (teskari SSH tunnel `127.0.0.1:8093`, model "Kotib (tinish belgilari bilan)"). Bu `/voice/stt` ning standart dvigateli.
- **O'lchov:** 5,4 s audio — jami **0,95–1,4 s** (GPU hisoblash 0,8–1,1 s). Oldin 18–37 s edi.
- **GPU o'chiq yoki javob bermasa,** avtomatik serverdagi CPU Kotib ishlatiladi: sekin, lekin ishlaydi. Kuzatuv panelida "STT GPU (8093)" holati ko'rinadi.
- **Ikkinchi model** "rubaistt_v2 (eng aniq)" — `?engine=gpu_rubai`. Modellarni almashtirish ~5 s oladi, shuning uchun aralashtirmang.
- **`confidence`:** GPU STT ilovasi ham faqat matn va vaqtni qaytaradi. Shuning uchun hali `null`. `exp(mean(avg_logprob))` qo'shish GPU kompyuterdagi ilovani o'zgartirishni talab qiladi, buni uning egasidan so'raymiz. Shungacha server STT'da `stt` maydonini yubormang.
- **Javob shakli o'zgarmadi:** `{"text", "confidence": null, "engine": "gpu", "audioSeconds", "ms"}`.

## 2.1. Rollar uchun haqiqiy ovozlar — klonlandi

Chatterbox GPU'da 4 ta ovoz saqlandi. Hozircha hammasi erkak ovozi, ayol ovozlari keyin almashtiriladi:

| `voice` | Chatterbox nomi | Kimlar |
|---|---|---|
| `elder_m` | `sudya` | sudya, podpolkovnik |
| `female_alt` | `raqib_ayol` | raqib advokat |
| `male` | `taraf_erkak` | da'vogar, guvoh, navbatchi, tergovchi |
| `female` | `kotib` | kotib, devonxona, arizachi |

- **Render:** barcha qat'iy gaplar (sud zali 88 ta + sizning 97 tangiz = **185 ta**) shu ovozlarda **qayta render qilinmoqda**. Tugagach, `/voice/tts` ularni keshdan beradi.
- **Klonlangan ovozga balandlik filtri qo'llanmaydi.**
- **Jonli yangi gaplar** MMS'da qoladi: klonlangan ovozda bitta gap 20–50 s oladi.

## 3. §5 — moddalar lex.uz matni bilan solishtirildi

Bank, variantlar va izohlarda keltirilgan har bir modda RAG bazasidagi lex.uz matniga qarshi o'qildi (2026-11-20 da olingan matn).

| Modda | Bizda qanday ishlatiladi | lex.uz matni | Mos |
|---|---|---|---|
| FK 260 | Kreditor zararni isbotlashi shart emas | «…kreditor oʻziga yetkazilgan zararni isbotlashga majbur emas» | ✅ |
| FK 262 | Penya kelishuvi yozma | «Neustoyka toʻgʻrisidagi kelishuv yozma shaklda tuzilishi kerak» | ✅ |
| FK 326 | Sud nomutanosib penyani kamaytirishga haqli; mezonlar | «…nomutanosibligi koʻrinib tursa, sud neustoykani kamaytirishga haqli. Bunda qarzdor majburiyatni qay darajada bajarganligi, … mulkiy ahvoli…» | ✅ |
| FK 333 | Aybsizlikni majburiyatni buzgan shaxs isbotlaydi | «Aybning yoʻqligi majburiyatni buzgan shaxs tomonidan isbotlanadi» | ✅ |
| FK 541 | Dalolatnomani tuzish ijaraga beruvchining burchi | «…topshirish dalolatnomasini tuzish va imzolashga taqdim etish ijaraga beruvchining burchi…» | ✅ |
| FK 544 | Ijara haqini o'z vaqtida to'lash | «Ijaraga oluvchi mol-mulkdan foydalanganlik uchun haqni oʻz vaqtida toʻlab turishi shart» | ✅ |
| FK 578 | Dalolatnoma **yoki topshirishga doir boshqa hujjat** | «…topshirish dalolatnomasi yoki topshirishga doir boshqa hujjat boʻyicha amalga oshiriladi» | ✅ |
| IPK 20, 21 | Rad qilish asoslari (qarindoshlik, manfaatdorlik) | 21-modda: «…qarindoshi boʻlsa; … manfaatdor boʻlsa…» | ✅ |
| IPK 22 | Rad qilish arizasi ishni mazmunan ko'rishdan oldin | «…asoslantirilgan boʻlishi va ishni mazmunan koʻrish boshlanguniga qadar maʼlum qilinishi lozim» | ✅ |
| IPK 62 | Vakolat ishonchnoma bilan | «…vakolatlari … rasmiylashtirilgan ishonchnomada koʻrsatilgan boʻlishi kerak» | ✅ |
| IPK 167 | Hamma turadi, «Hurmatli sud!», tik turib javob | «…«Hurmatli sud!» degan soʻzlar bilan murojaat qiladi … tik turib beradi» | ✅ |
| IPK 171 | Qoldirish faqat asos bilan | «…kutilmagan va favqulodda holatlarda… asoslagan holda…» | ✅ |
| IPK 173 | Qo'shimcha materiallar, so'ng muzokaralar | «…qoʻshimcha materiallar bor-yoʻqligini aniqlaydi … muzokaralarga oʻtadi» | ✅ |

**Bitta e'tibor beradigan nuqta.** Javobgar raqibning «hisob-faktura — to'lov hujjati, topshirish hujjati emas» degan gapi **huquqiy pozitsiya**, qonun matni emas. Raqib advokat shunday bahslashishi mumkin. Hisobotda baho haqiqiy qarorga tayanadi: sud fakturalarni yetarli deb topgan. Bu gapni mentor ko'rib chiqsin.

**`verifiedAt`** hali `null`. Yuqoridagi jadval — mening solishtiruvim, mentor tasdig'i emas.

---

## 4. Server egasining qarorini kutayotgan ishlar

- **B2-advanced, LLM ≤ 8 s yoki SSE:** `llama.cpp` benchmark. Reja [LexSim_Backend_AI_javob.md](LexSim_Backend_AI_javob.md) §3 da.
- **B4:** GPU STT tunneli.
- **Rollar ovozi:** namunalar va rozilik.
- **Kalit:** kalitni sizga server egasi beradi. U kalitni Next serveringizning `.env.local` fayliga qo'yadi.
