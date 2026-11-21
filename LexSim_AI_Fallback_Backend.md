# Tayyor javob bo'lmasa, AI suhbatni davom ettiradi (backend v1.5.0)

**Kimga:** frontend dasturchisi.
**Sana:** 2026-11-21.
**Holat:** kod tayyor, serverdagi alohida nusxada jonli AIHUB bilan sinovdan o'tdi (98 ta test). O'rnatish vaqti alohida xabar qilinadi.

---

## 1. Qoida (hamma joyda bir xil)

1. **Tizimda aniq javob bor** (ssenariy, bank, vaziyat, variant): tizim javob beradi. Tez, mentor tekshirgan matn.
2. **Aniq javob yo'q**: **AI** qahramonning o'z rolida javob beradi va suhbatni ishga qaytaradi.
3. **AI ishlamasa yoki tekshiruvdan o'tmasa**: avvalgidek tayyor gap («aniqroq ayting», «tushunmadim»).

**AI'ni tizim tekshiradi**, ya'ni u erkin emas:
- yangi raqam, summa yoki sana yo'q (faqat ish faktlari va talaba gapidagi raqamlar);
- modda raqami faqat ruxsat etilgan ro'yxatdan;
- 1–3 gap, kirill va so'kinish yo'q;
- qaror chiqarmaydi, huquqiy maslahat bermaydi.

Tekshiruvdan o'tmagan javob tashlanadi va tayyor gap aytiladi.

---

## 2. Sud zali (backend o'zi qiladi, sizdan deyarli hech narsa kerak emas)

Avval sudya **hech qachon** AI ishlatmasdi, raqib esa faqat `advanced` darajada AI ishlatardi. Endi:

| Holat | Avval | Endi |
|---|---|---|
| Talaba gapi bosqichga aloqasiz («mashinam ko'k rangda…») | «Aniqroq ayting» shabloni | **AI sudya:** «…ma'lumotingiz ishning predmetiga taalluqli emas; talabingizni aniqlashtiring: 32-P-sonli shartnoma asosida qancha summani…» |
| Javob to'liq emas («javobgar yomon odam, pulimizni bermadi») | Shablon savol | **AI sudya** aynan shu gapga mos aniqlashtiruvchi savol beradi |
| Raqib uchun tayyor javob yo'q | Faqat `advanced` darajada AI | **Hamma darajada** AI |

- Bitta majlisda AI sudya ko'pi bilan 12 marta gapiradi, qolgan joylarda shablon ishlatiladi.
- 4 so'zdan qisqa gaplarga AI ishlatilmaydi.
- `npcTurn.engine: "llm"` keladi. `audio` maydoni bo'lmaydi (gap oldindan yozilmagan), shuning uchun `POST /voice/tts` qiling.
- **Vaqt:** AIHUB bilan 9–50 s. Shuning uchun bunday gapga javob **`202`** bilan keladi, oldingi asinxron tartib o'zgarmagan: sudya «sud tinglayapti» degan to'ldiruvchi gapni aytadi, AI javobi `/events?after=N` orqali keladi.

**Sizdan:** `engine: "llm"` bo'lgan gapda kichik «AI» belgisini ko'rsating. Talaba bu gap oldindan yozilmaganini bilsin.

---

## 3. "Ish yo'li", maslahat, DXM: yangi `POST /npc/reply`

**Ustunlik tartibi endi:**
1. `situation`;
2. `match`;
3. `clarify`;
4. **`POST /npc/reply`**;
5. umumiy «tushunmadim».

### So'rov
```json
POST /api/v1/npc/reply
{
  "speaker": "client",
  "caseKind": "labour",
  "stage": "consult",
  "goal": "mijozdan ishdan bo'shatish holatlarini aniqlash",
  "utterance": "Siz ishdan bo'shatilishdan oldin rahbaringiz bilan janjallashganmidingiz?",
  "facts": ["14-oktabr kuni buyruq bilan bo'shatilgan…", "o'sha kunlari kasal bo'lgan…"],
  "articles": [],
  "history": [{"speaker": "you", "text": "…"}, {"speaker": "client", "text": "…"}]
}
```

| Maydon | Majburiy | Nima |
|---|---|---|
| `speaker` | ✅ | `client`, `officer`, `investigator`, `chief`, `clerk`, `secretary`, `judge`, `respondent`, `witness`, `citizen` (DXM fuqarosi), `operator` (DXM xodimi) |
| `utterance` | ✅ | talabaning gapi (≥ 2 so'z). Shaxsiy ma'lumot AI'ga yuborilishidan oldin yashiriladi |
| `facts` | tavsiya | shu qahramon biladigan faktlar (≤ 12 ta). **Qahramon faqat shulardan gapiradi**, yo'q narsaga «bilmayman» deydi |
| `goal` | tavsiya | joriy bosqich maqsadi: AI suhbatni shu tomonga olib boradi |
| `history` | tavsiya | oxirgi 8 gap |
| `articles` | ixtiyoriy | qahramon tilga olishi mumkin bo'lgan moddalar (`"MK 161-modda"`). Bo'sh bo'lsa, modda umuman aytilmaydi |
| `caseKind`, `stage` | ixtiyoriy | `labour` / `theft` / `dxm` va bosqich |

### Javob
```json
{"reply": {"speaker": "client", "text": "Yo'q, rahbarim bilan janjallashmaganman. Men faqat kasal bo'lgan kunlarim ishga chiqa olmasligimni telefon orqali aytgandim.", "emotion": "uncertain", "engine": "llm"}}
```

- **`503 npc_pending`** (`Retry-After: 10`): AI hali yozyapti. **Xuddi shu so'rovni** qayta yuboring, tayyor bo'lsa keshdan darhol keladi. Shu orada qahramon o'ylayotgandek ko'rsating («Hmm…» yoki «Bir daqiqa…»).
- **`503 npc_unavailable`**: AI javob bermadi yoki tekshiruvdan o'tmadi. Avvalgidek «tushunmadim» gapini aytsin.
- **`422`**: `speaker` noto'g'ri yoki `utterance` bo'sh. **`429`**: so'rov juda ko'p (daqiqasiga 60 ta).
- Bir xil so'rovga bir xil javob keladi (1 soat kesh).
- **Ovoz:** matn oldindan yozilmagan, shuning uchun `POST /voice/tts` ni `emotion` va qahramon ovozi bilan chaqiring.

### Jonli sinov (21-noyabr, AIHUB)

| Qahramon | Talaba | Javob | Vaqt |
|---|---|---|---|
| Mijoz (mehnat) | «Rahbaringiz bilan janjallashganmidingiz?» | «Yo'q, rahbarim bilan janjallashmaganman. Men faqat kasal bo'lgan kunlarim ishga chiqa olmasligimni telefon orqali aytgandim.» | 12 s |
| Navbatchi (o'g'irlik) | «Ariza uchun pasport shartmi yoki ID karta ham bo'ladimi?» | «…pasport ham, ID karta ham shaxsni tasdiqlovchi hujjat sifatida taqdim etilishi mumkin. Marhamat, hujjatingizni ko'rsating…» | 13 s |

Ikkala javob ham faktlar doirasida qoldi, yangi raqam yo'q, rolda.

---

## 4. Vaqt va kelajak

- **Hozir (AIHUB):** birinchi chaqiruv ~50 s, keyingilari 9–13 s.
- **Tez API kaliti** (loyiha egasi qarori, E5) bilan: 2–4 s. Shunda `npc_pending` deyarli chiqmaydi.
- `/health` da kuzatuv: `npc` (calls, ok, failed, last_ms) va `llm.aihub`.

---

## 5. Uch bosqichli tekshiruv: tizim → AI → mentor (yangi `/review`)

`jamiyat_fikri` loyihasidagi yondashuv (Algorithm Gate → AI Judge → Human Review) LexSim'ga moslandi:

| Bosqich | Kim | Nima qiladi |
|---|---|---|
| 1. **Tizim** | qoidalar | so'kinish, manbasiz modda, shaxsiy ma'lumot, majburiy qismlar, raqam va modda tekshiruvi |
| 2. **AI** | model | bandlar bo'yicha «ha/yo'q + iqtibos», qahramon javobi, case qoralamasi. Ishni mentorga **o'zi yuboradi**, agar: iqtibos topilmasa, yurishlar kelishmasa, etika buzilsa yoki ball chegaraga yaqin bo'lsa |
| 3. **Mentor** | odam | navbatdagini ko'radi: tasdiqlaydi, bandni tuzatadi yoki rad etadi. AI «yaxshi» degan ishlarning **3 %** i ham tasodifiy auditga tushadi |

Mentor qarorlari «oltin to'plam»ga yig'iladi va AI bilan kelishuv o'lchanadi (Koen kappasi). Maqsad: ≥ 0,61. Shunga yetguncha AI bahosi faqat mashq uchun.

### Marshrutlar (faqat `X-Admin-Token`, mentor sahifasi orqali)

| Usul | Yo'l | Nima |
|---|---|---|
| GET | `/review/queue?kind=moot_verdict\|npc_reply&status=pending` | Navbat: avval AI yuborganlari, keyin tasodifiy audit (`sample: true`) |
| GET | `/review/{id}` | To'liq ish: bahs izohi (har band, iqtibos, sabab) yoki qahramon javobi |
| POST | `/review/{id}` | `{"decision": "approve"}`, yoki `{"decision": "adjust", "items": {"claimant:F2": "no"}, "note": "..."}`, yoki `{"decision": "reject", "note": "..."}` (izoh majburiy) |
| GET | `/review/stats` | Navbat holati, `goldItems`, `agreement`, `kappa`, har band bo'yicha kelishuv, `auditRate` |

- `X-Reviewer: <mentor ismi>` sarlavhasini yuborsangiz, audit jurnaliga yoziladi.
- Bir ish ikki marta ko'rib chiqilmaydi (`409`).

**Sizdan (mentor sahifasi `/mentor`):**
1. «Bahs baholari» yorlig'i: navbat ro'yxati, ochilganda har band uchun AI qarori (✓/✗), talabaning iqtibosi va «To'g'ri / Noto'g'ri» tugmasi. Saqlash → `adjust` yoki `approve`.
2. «AI qahramon javoblari» yorlig'i (`npc_reply`): talaba gapi, qahramon javobi va faktlar → «Yaxshi» (`approve`) yoki «Yomon» (`reject`, izoh bilan).
3. «Statistika» paneli: kelishuv % va kappa, 0,61 maqsad chizig'i bilan.

## 6. Kodekslar bazada

Mehnat kodeksi, JPK, JK, Murojaatlar to'g'risidagi qonun (ZRU-445), Davlat boji to'g'risidagi qonun (ZRU-600), Advokatura to'g'risidagi qonun (349-I) va advokatlik faoliyati kafolatlari to'g'risidagi qonun (721-I) **RAG bazasiga yuklandi**, jami 2372 bo'lak.
- `GET /domains`: mehnat, jinoyat va DXM sohalaridagi «hali bazada yo'q» izohlari olib tashlandi.
- Endi bu sohalardagi caselar ham moddali bo'ladi. Masalan, o'g'irlik → JK 169, JPK 324; DXM → MUR 28.

---

## 7. «Eshitmadim, qaytaring» va suhbat xotirasi

**Muammo (jonli sinovda):** talaba kotibdan «qaytarib yubor» deb so'radi, qahramon esa «tushunmadim» dedi. Ikki sabab bor edi:
1. Qaytarish iltimosi tanilmasdi.
2. AI oldingi suhbatni bilmasdi:
   - sud zalida AI'ga faqat talabaning gaplari borardi, sudya, kotib va raqib gaplari tushib qolardi (backend xatosi, tuzatildi);
   - "Ish yo'li"da esa tarix umuman yuborilmagan bo'lishi mumkin.

### 7.1. Qaytarish: AI'siz, darhol
Tanilgan iboralar: «takrorlang», «eshitmadim», «eshitolmadim», «nima dedingiz», «tushunmay qoldim», «yana bir bor ayting», «qaytarib yuboring», «qaytaring», «повторите», «ещё раз». Faqat ≤ 7 so'zli gapda ishlaydi, shuning uchun «pulni qaytarib bermadi» kabi gap bunga tushmaydi.

- **Sud zali (backend o'zi):** talabaning oldingi gapidan keyin aytilgan NPC gaplari aynan o'sha rolda va keshdagi audio bilan qayta aytiladi. Bosqich o'zgarmaydi, ball ayirilmaydi.
- **"Ish yo'li" / DXM:** `/nlu/match` javobida `situation.id = "repeat"` va **`situation.action = "repeat_last"`** keladi. **Sizdan:** shu qahramonning oxirgi gapini qayta ijro eting. Oldidan ixtiyoriy ravishda `replies[speaker].lines[0]` («Albatta, qaytaraman.», prerender qilingan) aytilsin.

### 7.2. Suhbat xotirasi (`/npc/reply`)
- **`conversationId`** maydoni yangi (4–64 belgi, masalan `labour-<caseId>-consult`). Server shu suhbatning oxirgi 16 gapini saqlaydi (3 soat): talaba gaplari va AI javoblari.
- **Ssenariy gaplarini ham yuboring**, chunki ularni frontend aytadi va server bilmaydi:
  ```
  POST /api/v1/npc/history
  {"conversationId": "labour-…-consult", "items": [{"speaker": "client", "text": "Assalomu alaykum. Meni ishdan bo'shatishdi…"}]}
  ```
  Har bir qahramon gapi va talaba gapidan keyin bitta so'rov yuboring yoki bir nechtasini birga yuboring (≤ 20 ta).
- `history` maydonini ham yuborsangiz, server o'zi saqlagani bilan birlashtiriladi va takrorlar olib tashlanadi.
- **«Qaytaring» `/npc/reply` ga kelsa ham** AI chaqirilmaydi: shu qahramonning xotiradagi oxirgi gapi darhol qaytadi (`engine: "repeat"`).

**Qabul:**
1. Kotib gapirdi → talaba «eshitmadim, qaytaring» → kotib o'sha gapni takrorladi.
2. Mijoz bilan 5 ta gaplashilgan, keyin talaba «boshida qaysi sanani aytgandingiz?» deb so'radi → AI xotiradagi sanani aytadi (sana faktlarda bo'lishi kerak).
