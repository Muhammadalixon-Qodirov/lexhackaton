"""AIHUB (brauzer orqali Gemini / ChatGPT) — vaqtinchalik LLM provayderi.

Rasmiy API kaliti bo'lmagan davr uchun. Javob 6–40 s keladi, shuning uchun faqat `advanced` darajada,
bank javobi mos kelmaganda chaqiriladi (async 202). Chiqish odatdagidek `llm_check` dan o'tadi.

Sxema:
  1) tanishtirish (primer) — har modelga yangi suhbatda BIR MARTA: ish faktlari, ikkala raqib roli,
     ruxsat etilgan moddalar, taqiqlar, javob formati. AI «TAYYOR» deb javob beradi;
  2) har savol — qisqa paket (rol + vazifa + namuna + talaba gapi). Asosiy qoidalar paketda ham bor,
     shuning uchun suhbat yo'qolsa ham (AIHUB qayta ishga tushsa) AI noto'g'ri gapirmaydi;
  3) tugash belgisi — javob «#TAMOM» bilan tugashi shart. Yo'q bo'lsa — chala deb hisoblanadi
     va keyingi so'rovdan oldin AI qayta tanishtiriladi;
  4) har REPRIME_EVERY so'rovdan keyin qayta tanishtirish (suhbat uzayib sekinlashmasin).

Sozlash (env): LEXSIM_LLM_PROVIDER=aihub, LEXSIM_AIHUB_URL, LEXSIM_AIHUB_TOKEN_GEMINI,
LEXSIM_AIHUB_TOKEN_CHATGPT, LEXSIM_AIHUB_MODELS (tartib, standart "chatgpt,gemini": ChatGPT barqarorroq ~14 s, Gemini 8–29 s).
"""
import json
import os
import re
import threading
import time
import urllib.error
import urllib.request

URL = os.environ.get("LEXSIM_AIHUB_URL", "http://127.0.0.1:9090").rstrip("/")
TOKENS = {"gemini": os.environ.get("LEXSIM_AIHUB_TOKEN_GEMINI", ""),
          "chatgpt": os.environ.get("LEXSIM_AIHUB_TOKEN_CHATGPT", "")}
ORDER = [m for m in (os.environ.get("LEXSIM_AIHUB_MODELS") or "chatgpt,gemini").split(",") if TOKENS.get(m)]
END = "#TAMOM"
# ChatGPT/Gemini suhbat to'lganda yoki limitda shunday deydi — yangi suhbat ochish kerak
NEW_CHAT = re.compile(r"new chat|start a new|maximum length|conversation is too long|too long|limit|"
                      r"yangi suhbat|yangi chat|новый чат", re.I)
REPRIME_EVERY = 20
PRIMER = ""

STATE = {m: {"lock": threading.Lock(), "primed": False, "since_prime": 0, "calls": 0, "ok": 0,
             "no_end": 0, "errors": 0, "last_ms": None, "ms": [], "last_error": None} for m in TOKENS}


def enabled():
    return bool(ORDER)


def _lst(x):
    if isinstance(x, list):
        return x
    try:
        return json.loads(x.replace("'", '"')) if isinstance(x, str) and x.startswith("[") else [x]
    except ValueError:
        return [x]


def build_primer(roles, scenarios):
    """Tanishtirish matni: roles.json + scenarios.json dan (mentor tahrirlasa — avtomatik yangilanadi)."""
    g = roles.get("advokat_umumiy", {})
    sc = next(iter(scenarios.values()))
    b = sc["public"].get("briefing", {})
    parts = [
        "Sen LexSim — huquqshunos talabalar uchun o'quv sud simulyatorida sud majlisi qahramonlarini o'ynaysan: "
        "ko'pincha raqib advokatni, ba'zan sudyani. Har so'rovning boshida kim ekaning aytiladi — faqat o'sha rolda gapir. "
        "Bu o'quv mashg'ulot, haqiqiy ish emas. Bu suhbatda menga faqat «[LEXSIM SUD]» bilan boshlanadigan "
        "so'rovlar keladi. Har biriga shu ko'rsatmalar bo'yicha javob ber.",
        "RAQIB ADVOKAT bo'lganingda: real iqtisodiy sud majlisidagi tajribali advokatdek fikrla va gapir. Talaba qarshi tarafning vakili — "
        "u sud jarayonini mashq qilyapti. Sen unga jonli, kuchli, lekin halol raqib bo'lishing kerak: o'z mijozing "
        "manfaatini himoya qil, talaba aytgan aniq gapga javob ber (umumiy gap emas), uning gapidagi zaif joyni ko'rsat, "
        "lekin faqat ish faktlari va ruxsat etilgan moddalar doirasida. Talabaga maslahat berma, uning o'rniga "
        "gapirma, sud qarorini bashorat qilma. Har so'rovda majlis bosqichi va oxirgi gaplar beriladi — ularni "
        "hisobga ol, avval aytilganini takrorlama va o'zingga zid gapirma.",
        "ISH: " + b.get("workplace", "Iqtisodiy sud") + ". " + sc.get("ai_facts", ""),
    ]
    for rid in ("davogar-vakili", "javobgar-vakili"):
        r = roles.get(rid)
        if not r:
            continue
        parts.append(f"ROL «{rid}»: {r['kim']} Pozitsiya: {r['pozitsiya']} "
                     f"Faqat shu moddalarni tilga olishing mumkin: {', '.join(_lst(r['ruxsat_moddalar']))}. "
                     f"Taqiq: {'; '.join(_lst(r['taqiq']))}.")
    parts.append("USLUB: " + " ".join(_lst(g.get("uslub", []))))
    parts.append("SUDYA bo'lganingda: xushmuomala, lekin qat'iy; talaba gapiga munosabat bildir va majlisni joriy bosqich "
                 "savoliga qaytar; ish bo'yicha qaror chiqarma, kim haqligini aytma; o'zingga «Hurmatli sud» dema.")
    parts.append(
        "JAVOB FORMATI (qat'iy): faqat so'rovda ko'rsatilgan qahramonning sudda aytadigan gapi; 1–2 gap; o'zbek tilida, lotin yozuvida; "
        "advokat bo'lsang «Hurmatli sud» faqat javob boshida bir marta, keyingi gapda takrorlanmasin; uslubdagi misol iboralarni qolip qilib "
        "takrorlama, har safar raqib gapiga mos o'z so'zlaring bilan boshla; markdown, ro'yxat, izoh, tarjima, qo'shtirnoq yo'q; yangi raqam yoki summa o'ylab topma; "
        f"ro'yxatda yo'q moddani aytma. Javob oxirida alohida «{END}» yoz — bu javob tugaganini bildiradi.")
    parts.append("Tushungan bo'lsang, hozir faqat bitta so'z yoz: TAYYOR")
    return "\n\n".join(parts)


def init(roles, scenarios):
    global PRIMER
    PRIMER = build_primer(roles, scenarios)


def _post(model, prompt, fresh, timeout):
    body = json.dumps({"prompt": prompt, "model": model, "fresh": fresh}).encode()
    req = urllib.request.Request(URL + "/ask", data=body, headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + TOKENS[model]})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return (d.get("response") or "").strip(), d.get("model") or model


def _prime(model, timeout):
    st = STATE[model]
    try:
        txt, got = _post(model, PRIMER, True, timeout)
        st["primed"] = got == model and "TAYYOR" in txt.upper()
        st["last_error"] = None if st["primed"] else f"tanishtirish javobi: {txt[:60]!r} ({got})"
    except Exception as e:  # noqa: BLE001
        st["primed"], st["last_error"] = False, f"tanishtirish: {type(e).__name__}: {e}"
    st["since_prime"] = 0
    return st["primed"]


def _pick():
    """Bo'sh modelni tanlaydi (ikkala AI parallel ishlaydi); hammasi band bo'lsa — birinchisini kutadi."""
    for m in ORDER:
        if STATE[m]["lock"].acquire(blocking=False):
            return m
    STATE[ORDER[0]]["lock"].acquire()
    return ORDER[0]


def ask(sysm, user, timeout=60, tail=None):
    """-> (matn | None, model, ms, why). Matn «#TAMOM» siz qaytadi."""
    if not ORDER:
        return None, None, 0, "AIHUB tokeni yo'q"
    m = _pick()
    st = STATE[m]
    t0 = time.time()
    try:
        prompt = (f"[LEXSIM SUD]\n{sysm}\n{user}\n"
                  f"{tail or 'Faqat raqib gapini yoz (1–2 gap)'}, oxirida {END}")
        txt, got = "", m
        for _attempt in (1, 2):
            if not st["primed"] or st["since_prime"] >= REPRIME_EVERY:
                _prime(m, timeout)                     # yangi (toza) suhbat + tanishtirish
            left = timeout - (time.time() - t0)
            if left < 10:
                break
            st["calls"] += 1
            st["since_prime"] += 1
            txt, got = _post(m, prompt, False, left)
            if got != m:                              # AIHUB boshqa modelga o'tib ketdi — u tanishtirilmagan
                st["primed"] = False
            if END in txt:
                break
            # belgi yo'q: chala javob, «yangi suhbat oching» / suhbat juda uzun / limit xabari —
            # yangi suhbat ochib, tanishtirib, bir marta qayta so'raymiz (vaqt yetsa)
            st["no_end"] += 1
            st["primed"] = False
            st["last_error"] = "tugash belgisi yo'q" + (" (yangi suhbat talabi)" if NEW_CHAT.search(txt) else "")
            if time.time() - t0 > timeout * 0.5:
                break
        ms = round((time.time() - t0) * 1000)
        st["last_ms"] = ms
        st["ms"] = (st["ms"] + [ms])[-30:]
        if END not in txt:
            return None, got, ms, "tugash belgisi yo'q (chala yoki format buzilgan)"
        txt = re.sub(r"\s*#\s*TAMOM\W*", " ", txt).strip()
        st["ok"] += 1
        st["last_error"] = None
        return txt, got, ms, None
    except urllib.error.HTTPError as e:
        st["errors"] += 1
        st["last_error"] = f"HTTP {e.code}"
        return None, m, round((time.time() - t0) * 1000), f"AIHUB HTTP {e.code}"
    except Exception as e:  # noqa: BLE001
        st["errors"] += 1
        st["last_error"] = f"{type(e).__name__}: {e}"
        return None, m, round((time.time() - t0) * 1000), f"AIHUB {type(e).__name__}"
    finally:
        st["lock"].release()


def stats():
    out = {}
    for m in ORDER:
        st = STATE[m]
        ms = sorted(st["ms"])
        out[m] = {k: st[k] for k in ("primed", "calls", "ok", "no_end", "errors", "last_ms", "last_error")}
        out[m]["median_ms"] = ms[len(ms) // 2] if ms else None
    return out


def ask_task(prompt, timeout=60):
    """Alohida topshiriq (masalan, bahs sudyasi): toza suhbatda, tanishtirishsiz. -> (matn | None, model, ms, why).
    Toza suhbat raqib tanishtiruvini o'chiradi — keyingi raqib so'rovi qayta tanishtiradi."""
    if not ORDER:
        return None, None, 0, "AIHUB tokeni yo'q"
    m = _pick()
    st = STATE[m]
    t0 = time.time()
    try:
        st["calls"] += 1
        txt, got = _post(m, f"{prompt}\nJavob oxirida {END} yoz.", True, timeout)
        st["primed"] = False
        ms = round((time.time() - t0) * 1000)
        if END not in txt:
            st["no_end"] += 1
            m_ = re.search(r"\{.*\}", txt or "", re.S)          # belgi tushib qolgan, lekin JSON butun — qabul qilamiz
            try:
                json.loads(m_.group(0)) if m_ else None
            except ValueError:
                m_ = None
            if not m_:
                return None, got, ms, "tugash belgisi yo'q"
        st["ok"] += 1
        return re.sub(r"\s*#\s*TAMOM\W*", " ", txt).strip(), got, ms, None
    except Exception as e:  # noqa: BLE001
        st["errors"] += 1
        st["primed"] = False
        st["last_error"] = f"{type(e).__name__}: {e}"
        return None, m, round((time.time() - t0) * 1000), f"AIHUB {type(e).__name__}"
    finally:
        st["lock"].release()
