# Backend — frontend v14 javobiga javob

**Kimga:** frontend jamoasi.
**Sana:** 2026-11-21.
**Server:** `https://lex-api.e-investment.uz/api/v1`. Kontrakt o'zgarmadi.
**Testlar:** 32/32 yashil, shu jumladan sizning 2–5-ishlaringiz uchun 5 ta yangi test.

## Sizning ishlaringiz

| # | Muammo | Holat | Sabab va nima qilindi |
|---|---|---|---|
| 1 | Keshda yo'q gap TTS'da `504 FileNotFoundError` | ✅ | Yangi serverda `ffmpeg` yo'q edi. O'rnatildi. Keshda yo'q gap endi ~4 s da `200`, `X-TTS-Cache: miss`. STT ham `ffmpeg` ga bog'liq edi, u ham tuzatildi: 4 s audio ~4 s da taniladi. |
| 2 | Sudya savoli ochiq turganda e'tiroz tanilmaydi | ✅ | Raddiya bosqichida e'tiroz endi ikki xil ko'riladi (pastda). Asossiz «Hurmatli sud, eʼtiroz bildiraman.» ham taniladi va rad etiladi. |
| 3 | Erta bosqichda o'rinsiz harakat "to'g'ri" deb baholanadi | ✅ | Noto'g'ri bosqichdagi savol, iltimosnoma yoki e'tirozga sudya tushuntirish beradi va o'z savolini qaytaradi. Bosqich o'zgarmaydi. Feedback `info`: «Bu harakat keyingi bosqichda qilinadi: …». «Iltimosnomalaringiz bormi?» bosqichida keyinga qoldirish iltimosnomasi ko'rib chiqiladi (IPK 171). |
| 4 | Vakolat qayta so'ralganda feedback «Qabul qilindi» | ✅ | Feedback `bad`: «Sudya vakolatni tasdiqlovchi hujjatni so'radi: avval ishonchnomani taqdim eting (IPK 62-modda).» |
| 5 | Sudya bir xil savolni so'zma-so'z qaytaradi | ✅ | Har bosqichda 2–3 variant, navbat bilan aytiladi. Variantlar oldindan yozilmoqda (prerender). |
| 6 | `LEXSIM_REMOTE_KEY` | ⏳ | Kalitni loyiha egasi shaxsan beradi. |

**2-ish: raddiya bosqichida e'tiroz.** Raddiya bosqichi — sudya «…Bunga munosabatingiz?» deb so'ragan joy.
- Gapda mazmun bo'lsa, u bosqich javobi sifatida baholanadi va majlis davom etadi. Masalan: «…eʼtiroz bildiraman, chunki javobgar joydan foydalangan va fakturalarni imzolagan».
- Mazmun bo'lmasa, sud e'tiroz bo'yicha qaror chiqaradi va bosqich o'zgarmaydi:
  - asos aytilgan bo'lsa, «Sud e'tirozni qabul qildi…»;
  - asos aytilmagan bo'lsa, «E'tiroz rad etildi…».
- Javobgar vakilining «da'voga e'tirozimiz bor: …» degan gapi avvalgidek asosiy javob hisoblanadi.

## Yangi
  
**CORS.** Ruxsat berilgan manbalar:
- `https://lexlab.e-investment.uz`
- `http://localhost:3000`
- `http://127.0.0.1:3000`

Brauzerdan to'g'ridan-to'g'ri chaqirsangiz, `fetch(..., {credentials: "include"})` ishlating. `lexsim_owner` cookie `Secure; SameSite=Lax`. `lexlab` va `lex-api` bir saytdan (`e-investment.uz`), shuning uchun cookie yuboriladi.

Preflight ham ishlaydi: `OPTIONS` → `204`. Ruxsat etilgan sarlavhalar:
- `Content-Type`
- `X-Admin-Token`
- `X-LexSim-Key`
- `X-LexSim-Owner`

`Expose-Headers` da `X-Duration-Ms`, `X-Word-Timings`, `X-TTS-Cache` bor. Boshqa manzil kerak bo'lsa, ayting.

**LLM (`advanced`).** Vaqtincha boshqa model ishlatiladi:
- javob 7–20 s, tanishtirishdan keyingi birinchi javob ~20 s;
- bu yo'l faqat bankda mos javob topilmaganda ishlaydi va so'rov `202` + `/events` bilan keladi;
- chiqish avvalgidek tekshiriladi, o'tmasa bank javobi beriladi.

**Eski server.** `192.168.88.110:8100` o'chirildi.

## Tekshirish

```bash
curl -s https://lex-api.e-investment.uz/api/v1/health
curl -si -X OPTIONS https://lex-api.e-investment.uz/api/v1/sessions \
  -H 'Origin: https://lexlab.e-investment.uz' -H 'Access-Control-Request-Method: POST' | grep -i access-control
cd lexsim-web && node tools/qa/live.mjs      # kutilgan natija: 8/8
```
