"""«Ish yo'li», maslahat va DXM: tayyor javob topilmaganda — AI qahramon (POST /npc/reply).

Tartib (frontend): situation → match → clarify → **AI qahramon** → umumiy «tushunmadim».
Chegaralar (tizim tekshiradi, AI emas):
  * qahramon faqat o'z rolida, ish faktlari doirasida gapiradi; yangi raqam/sana o'ylab topmaydi;
  * modda raqami faqat frontend bergan `articles` ro'yxatidan (yo'q bo'lsa — umuman aytilmaydi);
  * 1–3 gap, kirill yo'q, so'kinish yo'q; talaba gapida shaxsiy ma'lumot bo'lsa — AI'ga yuborilmasdan yashiriladi;
  * bir xil so'rov — bir xil javob (kesh); AI kech qolsa 503 npc_pending, keyin xuddi shu so'rov keshdan oladi.
"""
import hashlib
import json
import re
import threading
import time

PERSONA = {
    "client": "advokatga yordam so'rab kelgan oddiy fuqaro (mijoz). Xavotirda, huquqiy atamalarni yaxshi bilmaydi, o'z holatini oddiy so'z bilan aytadi",
    "officer": "ichki ishlar bo'limi navbatchi qismining navbatchisi. Rasmiy, qisqa, JPK tartibiga rioya qiladi",
    "investigator": "tergovchi. Rasmiy, aniq savol beradi, so'roq tartibiga rioya qiladi",
    "chief": "tergov bo'limi boshlig'i. Shikoyatni rasmiy qabul qiladi, aniq talabni so'raydi",
    "clerk": "sud devonxonasi xodimi. Hujjatlar qabuli bo'yicha qisqa va aniq",
    "secretary": "sud majlisi kotibi. Rasmiy va qisqa",
    "judge": "sudya. Xushmuomala, lekin qat'iy; qaror chiqarmaydi, tartibga qaytaradi",
    "respondent": "javobgar tomon vakili. O'z pozitsiyasini himoya qiladi, odobli",
    "witness": "guvoh. Faqat o'zi ko'rgan-eshitganini aytadi, taxmin qilmaydi",
    "citizen": "Davlat xizmatlari markaziga kelgan fuqaro. Oddiy til bilan gapiradi",
    "operator": "Davlat xizmatlari markazi xodimi. Xushmuomala, xizmat tartibini tushuntiradi",
}
EMO = {"client": "uncertain", "citizen": "uncertain", "officer": "neutral", "investigator": "neutral", "chief": "neutral",
       "clerk": "neutral", "secretary": "neutral", "judge": "calm", "respondent": "neutral", "witness": "uncertain",
       "operator": "calm"}
WAIT_S = 22
CACHE = {}
LOCK = threading.Lock()
SLOTS = threading.BoundedSemaphore(4)
ON_REPLY = None                                          # server: review (3 % audit)
MEMORY = {}                                              # suhbat xotirasi: (ega, conversationId) -> oxirgi gaplar
MEM_N, MEM_TTL = 16, 3 * 3600
STATS = {"calls": 0, "ok": 0, "cached": 0, "pending": 0, "failed": 0, "last_ms": None, "last_error": None}
ART = re.compile(r"(?<![\d.])(\d{1,4}(?:[.-]\d{1,3}){0,3}) ?-? ?(?:modda\w*)", re.I)
CYR = re.compile(r"[А-Яа-яЁё]")


class NpcError(Exception):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def _s(x, n):
    return re.sub(r"\s+", " ", x[:n * 2]).strip()[:n] if isinstance(x, str) else ""


def validate(body):
    if not isinstance(body, dict):
        raise NpcError(422, "validation_failed", "JSON obyekt kerak")
    sp = body.get("speaker")
    if sp not in PERSONA:
        raise NpcError(422, "validation_failed", "speaker: " + ", ".join(PERSONA))
    utt = _s(body.get("utterance"), 800)
    if len(utt.split()) < 2:
        raise NpcError(422, "validation_failed", "utterance juda qisqa")
    hist = body.get("history") if isinstance(body.get("history"), list) else []
    facts = body.get("facts") if isinstance(body.get("facts"), list) else []
    arts = body.get("articles") if isinstance(body.get("articles"), list) else []
    return sp, utt, hist[-8:], [_s(f, 300) for f in facts[:12] if isinstance(f, str)], [_s(a, 40) for a in arts[:20] if isinstance(a, str)]


def prompt_of(body, sp, utt, hist, facts, arts):
    h = "\n".join(f"{_s(x.get('speaker'), 20)}: {_s(x.get('text'), 300)}" for x in hist if isinstance(x, dict))
    return (
        f"Sen huquqshunos talabalar uchun o'quv simulyatoridagi qahramonsan: {PERSONA[sp]}.\n"
        f"Ish: {_s(body.get('caseKind'), 40) or 'noma`lum'}; bosqich: {_s(body.get('stage'), 40) or '-'}; "
        f"joriy vazifa: {_s(body.get('goal'), 200) or '-'}.\n"
        "QOIDALAR:\n"
        "1) Faqat o'z rolingda, odamdek, 1–3 qisqa gap bilan javob ber. O'zbek tilida, lotin yozuvida.\n"
        "2) Talaba (advokat) gapiga aniq munosabat bildir. U savol bersa — ish faktlari doirasida javob ber; "
        "fakt bo'lmasa «bilmayman» yoki «eslay olmayapman» de. Yangi raqam, summa yoki sana o'ylab topma.\n"
        "3) Huquqiy maslahat berma (bu talabaning ishi); suhbatni joriy vazifa tomon olib bor.\n"
        + (f"4) Modda raqamini faqat shulardan ayt: {', '.join(arts)}.\n" if arts else "4) Modda raqamini umuman aytma.\n")
        + "5) Talaba qo'pol bo'lsa — rolingga mos ranjib, xushmuomala javob ber.\n\n"
        + ("ISH FAKTLARI:\n- " + "\n- ".join(facts) + "\n" if facts else "")
        + (f"OXIRGI GAPLAR:\n{h}\n" if h else "")
        + f"TALABA HOZIR AYTDI: \"{utt}\"\n\nFaqat qahramon gapini yoz, izohsiz."
    )


def check(out, utt, facts, arts):
    """-> (matn | None, sabab). AI chiqishini tizim tekshiradi."""
    t = re.sub(r"^\s*[\w' ]{0,25}:\s*", "", (out or "").strip().strip('"'))
    t = t.replace("—", "-").replace("–", "-")
    if not (5 <= len(t) <= 500) or CYR.search(t):
        return None, "uzunlik/kirill"
    sents = re.split(r"(?<=[.!?])\s+", t)
    t = " ".join(sents[:3]).strip()
    allowed_nums = " ".join([utt] + facts + arts)
    for num in re.findall(r"\d[\d.,]*", t):
        if num.rstrip(".,") not in allowed_nums:
            return None, f"yangi raqam {num}"
    okarts = {re.sub(r"\D.*", "", a.split()[-1]) for a in arts if a.split()}
    for m in ART.finditer(t):
        if m.group(1) not in okarts:
            return None, f"ruxsat etilmagan modda {m.group(1)}"
    return t, None


def _mem_key(owner, body):
    cid = body.get("conversationId")
    if not isinstance(cid, str) or not re.fullmatch(r"[\w.-]{4,64}", cid):
        return None
    return hashlib.sha256(f"{owner}|{cid}".encode()).hexdigest()[:24]


def _merge(stored, given):
    """Server xotirasi + frontend yuborgan tarix (takrorsiz, tartib saqlanadi), oxirgi MEM_N ta."""
    out, seen = [], set()
    for x in list(stored) + list(given):
        if not isinstance(x, dict) or not _s(x.get("text"), 5):
            continue
        k = (_s(x.get("speaker"), 20), _s(x.get("text"), 300))
        if k in seen:
            continue
        seen.add(k)
        out.append({"speaker": k[0], "text": k[1]})
    return out[-MEM_N:]


def remember(owner, body, items):
    """Suhbatga gap qo'shish (frontend ssenariy gaplarini ham shu bilan yuborishi mumkin)."""
    mk = _mem_key(owner, body)
    if not mk:
        return
    with LOCK:
        now = time.time()
        for k in [k for k, v in MEMORY.items() if now - v["at"] > MEM_TTL]:
            MEMORY.pop(k, None)
        ent = MEMORY.setdefault(mk, {"at": now, "items": []})
        ent["items"] = _merge(ent["items"], items)
        ent["at"] = now


def reply(body, ask_fn, profane_fn=None, redact_fn=None, owner="", repeat_fn=None):
    sp, utt, hist, facts, arts = validate(body)
    if redact_fn:
        utt = redact_fn(utt)[0]
    mk = _mem_key(owner, body)
    with LOCK:
        stored = list(MEMORY.get(mk, {}).get("items", [])) if mk else []
    hist = _merge(stored, hist)
    if repeat_fn and repeat_fn(utt):                     # «eshitmadim, qaytaring» — AI'siz, shu qahramonning oxirgi gapi
        last = next((x["text"] for x in reversed(hist) if x["speaker"] == sp), None)
        if last:
            return {"speaker": sp, "text": last, "emotion": EMO.get(sp, "neutral"), "engine": "repeat"}
    key = hashlib.sha256(json.dumps({"b": {k: body.get(k) for k in ("speaker", "caseKind", "stage", "goal",
                                                                     "facts", "articles")}, "h": hist, "u": utt},
                                    ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    now = time.time()
    with LOCK:
        for k in [k for k, v in CACHE.items() if now - v["at"] > 3600]:
            CACHE.pop(k, None)
        if len(CACHE) > 5000:
            for k in sorted(CACHE, key=lambda x: CACHE[x]["at"])[:500]:
                CACHE.pop(k, None)
        ent = CACHE.get(key)
        fresh = ent is None or (ent["reply"] is None and ent["event"].is_set())
        if fresh:
            ent = CACHE[key] = {"at": now, "reply": None, "error": None, "event": threading.Event()}
    STATS["calls"] += 1
    if not fresh and ent["reply"]:
        STATS["cached"] += 1
        remember(owner, body, [{"speaker": "you", "text": utt}, {"speaker": sp, "text": ent["reply"]["text"]}])
        return ent["reply"]
    if fresh:
        def work():
            t0 = time.time()
            if not SLOTS.acquire(timeout=60):
                ent["error"] = "navbat to'la"
                ent["event"].set()
                return
            try:
                txt, model, ms, why = ask_fn(prompt_of(body, sp, utt, hist, facts, arts), 60)
                t, why2 = check(txt, utt, facts, arts) if txt else (None, why)
                if t and profane_fn and profane_fn(t):
                    t, why2 = None, "taqiqlangan so'z"
                if t:
                    ent["reply"] = {"speaker": sp, "text": t, "emotion": EMO.get(sp, "neutral"), "engine": "llm"}
                    if ON_REPLY:                          # 3-bosqich: tasodifiy audit (review.py)
                        try:
                            ON_REPLY(key[:16], {"speaker": sp, "caseKind": body.get("caseKind"), "stage": body.get("stage"),
                                                "utterance": utt, "facts": facts, "reply": t})
                        except Exception:  # noqa: BLE001
                            pass
                else:
                    ent["error"] = why2 or "javob yo'q"
            except Exception as e:  # noqa: BLE001
                ent["error"] = type(e).__name__
            finally:
                SLOTS.release()
            STATS["last_ms"] = round((time.time() - t0) * 1000)
            STATS["ok" if ent["reply"] else "failed"] += 1
            STATS["last_error"] = ent["error"]
            print(f"NPC {sp} {STATS['last_ms']} ms {'OK' if ent['reply'] else ent['error']}", flush=True)
            ent["event"].set()
        threading.Thread(target=work, daemon=True).start()
    ent["event"].wait(WAIT_S)
    if ent["reply"]:
        remember(owner, body, [{"speaker": "you", "text": utt}, {"speaker": sp, "text": ent["reply"]["text"]}])
        return ent["reply"]
    if ent["event"].is_set():
        raise NpcError(503, "npc_unavailable", "Qahramon hozir javob bera olmadi.")
    STATS["pending"] += 1
    raise NpcError(503, "npc_pending", "Qahramon javob o'ylayapti. Birozdan keyin xuddi shu so'rovni qayta yuboring.")
