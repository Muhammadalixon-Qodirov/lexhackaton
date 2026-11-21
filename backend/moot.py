"""«Bahs» - jamoaviy sud: sudya qarori (/moot/judge) va sudyaning doimiy gaplari.

Qoidalar (frontend LexSim_Bahs_Backend.md, 4-bo'lim):
  * mezonlar: participation 20 · manners 15 · facts 30 · rebuttal 20 · legal 15 (jami 100);
  * bu bahs g'olibi, haqiqiy da'vo bo'yicha qaror emas - «da'vo qanoatlantirilsin» yo'q;
  * uydirma yo'q: ish materiallarida bo'lmagan modda raqami qarordan olib tashlanadi;
  * so'kingan tomonning `manners` = 0; farq ≤ 2 ball - durang;
  * bir xil bayonnoma - bir xil natija (kesh).
Model javobi faqat xom ashyo: ballar chegaralanadi, jami, g'olib va so'nggi gap shu yerda hisoblanadi.
"""
import hashlib
import json
import re
import threading
import time

try:
    import rubric as RB          # tushuntiriladigan baholash (bandlar + iqtibos); yuklanmasa - eski umumiy baho
except ImportError:              # pragma: no cover
    RB = None

CRITERIA = [("participation", "Soʻzdan foydalanish", 20), ("manners", "Sud odobi", 15),
            ("facts", "Faktlar va dalillar", 30), ("rebuttal", "Raqibga javob", 20), ("legal", "Huquqiy asos", 15)]
SIDES = ("claimant", "respondent")
SIDE_UZ = {"claimant": "daʼvogar", "respondent": "javobgar"}
DRAW_MARGIN = 2
WAIT_S = 22                     # frontend 25 s kutadi
CACHE_TTL = 3 * 3600            # xona umri

# Matnlar aynan frontenddagidek (kesh matn bo'yicha topiladi)
LINES = [("Sud kirib kelmoqda, oʻrningizdan turing!", "female")] + [(t, "elder_m") for t in [
    "Oʻtiring.",
    "Soʻz daʼvogar vakiliga beriladi. Daʼvo talablaringiz va ularning asoslarini bayon qiling.",
    "Soʻz javobgar vakiliga beriladi. Daʼvo talablariga munosabatingizni bildiring.",
    "Daʼvogar tomoni, javobgarga savolingiz bormi?",
    "Javobgar tomoni, savolga javob bering.",
    "Javobgar tomoni, daʼvogarga savolingiz bormi?",
    "Daʼvogar tomoni, savolga javob bering.",
    "Dalillarni tekshirishga oʻtamiz. Daʼvogar tomoni, dalillaringizni koʻrsating.",
    "Javobgar tomoni, dalillaringiz va eʼtirozlaringiz.",
    "Sud muzokaralariga oʻtiladi. Soʻz daʼvogar vakiliga beriladi.",
    "Soʻz javobgar vakiliga beriladi.",
    "Daʼvogar tomoni, replika huquqidan foydalanasizmi?",
    "Javobgar tomoni, replika huquqidan foydalanasizmi?",
    "Vaqt tugadi. Rahmat.",
    "Sud muzokaralari tugadi. Sud qaror qabul qilish uchun maslahatxonaga kiradi.",
    "Sud taraflarning chiqishlarini eshitdi va baholadi.",
    "Sud majlisi yopiq deb eʼlon qilinadi.",
]]

CACHE = {}                      # hash -> {"at", "verdict" | None, "error", "event"}
LOCK = threading.Lock()
STATS = {"calls": 0, "ok": 0, "cached": 0, "pending": 0, "failed": 0, "last_ms": None, "last_error": None}


class JudgeError(Exception):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def _s(x, n):
    """Matn: uzun chiziq → «-», bo'shliqlar siqiladi, uzunlik chegaralanadi."""
    return re.sub(r"[ \t]+", " ", x[:n * 2].replace("\u2014", "-").replace("\u2013", "-"))[:n] if isinstance(x, str) else ""


def validate(body):
    if not isinstance(body, dict):
        raise JudgeError(422, "validation_failed", "So'rov JSON obyekt bo'lishi kerak")
    case, tr, players = body.get("case"), body.get("transcript"), body.get("players")
    if not isinstance(case, dict) or not isinstance(tr, list) or not isinstance(players, list):
        raise JudgeError(422, "validation_failed", "case, transcript va players kerak")
    if len(tr) > 400 or len(players) > 12:
        raise JudgeError(422, "validation_failed", "Bayonnoma juda uzun")
    for t in tr:
        if not isinstance(t, dict) or t.get("side") not in SIDES + ("court", "system", None):
            raise JudgeError(422, "validation_failed", "transcript yozuvi noto'g'ri")
    return case, tr, players


def key_of(body):
    keep = {k: body.get(k) for k in ("case", "agenda", "transcript", "players", "participants")}
    return hashlib.sha256(json.dumps(keep, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def materials_text(case):
    parts = [_s(case.get("title"), 300), _s(case.get("claim"), 2000)]
    for k in ("facts", "evidence"):
        for f in case.get(k) or []:
            if isinstance(f, dict):
                parts += [_s(f.get("title"), 200), _s(f.get("text"), 1500)]
    for sd in (case.get("side") or {}).values():
        if isinstance(sd, dict):
            for k in ("task", "confidential"):
                parts += [_s(x, 600) for x in sd.get(k) or []]
    return "\n".join(p for p in parts if p)


ART = re.compile(r"(?<![\d.])(\d{1,4}(?:[.-]\d{1,3}){0,3}) ?-? ?(?:modda|moddasi|moddasining|moddaga|moddalar|statya|стат)", re.I)   # chegaralangan — ReDoS yo'q


def _unsourced(text, allowed):
    return any(m.group(1) not in allowed for m in ART.finditer(text))


def _clean(text, allowed, n=400):
    """Manbasiz modda raqami bo'lgan gaplarni olib tashlaydi."""
    sents = re.split(r"(?<=[.!?])\s+", _s(text, n * 2).strip())
    return " ".join(x for x in sents if x and not _unsourced(x, allowed))[:n]


def prompt_of(case, agenda, tr):
    lines = []
    for t in tr:
        if t.get("side") in SIDES:
            lines.append(f"[{t.get('seq')}] {SIDE_UZ[t['side']]} · {_s(t.get('name'), 40)} ({_s(t.get('step'), 12)}): {_s(t.get('text'), 1200)}")
    trs = "\n".join(lines)[-18000:]
    crit = "; ".join(f"{i} (0-{mx}): {lb}" for i, lb, mx in CRITERIA)
    return (
        "Sen O'zbekiston iqtisodiy sudi sudyasisan. Talabalar o'quv bahsini (moot court) o'tkazdi. "
        "Vazifang - qaysi tomon BAHSDA yaxshiroq chiqqanini baholash. Bu haqiqiy da'vo bo'yicha qaror emas.\n"
        "QOIDALAR:\n"
        "1) Faqat quyidagi ish materiallari va bayonnomaga tayan. Yangi fakt, summa yoki modda raqamini o'ylab topma. "
        "Ish materiallarida yo'q faktga tayangan chiqish uchun ball kamaytir va izohda ayt.\n"
        "2) Mazmunni baholang: dalil materiallarga mosmi, raqibning aniq gapiga javob berildimi, o'z zaif joyini qanday yopdi. "
        "Kalit so'zlarni sanash emas.\n"
        "3) Bayonnoma nutqdan olingan (STT) - imlo xatosi uchun ball kamaytirma.\n"
        "4) «Da'vo qanoatlantirilsin» dema.\n"
        f"MEZONLAR: {crit}.\n\n"
        f"ISH: {_s(case.get('title'), 300)}\nTALAB: {_s(case.get('claim'), 1500)}\n"
        f"MATERIALLAR:\n{materials_text(case)[:9000]}\n\n"
        f"BAYONNOMA:\n{trs}\n\n"
        "Faqat JSON qaytar, boshqa matnsiz:\n"
        '{"criteria":[{"id":"facts","claimant":0,"respondent":0,"note":"1-2 gap"}, ...5 ta mezon],'
        '"ruling":["3-5 qisqa gap: sud nimani eshitdi, har tomonning kuchli va zaif joyi"],'
        '"players":[{"name":"...","note":"1-2 gap shaxsiy tavsiya"}]}'
    )


def _json_of(txt):
    m = re.search(r"\{.*\}", txt or "", re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


def build(case, tr, players, raw, profane_fn):
    """Model javobidan (raw) tekshirilgan verdict yasaydi. raw bo'lmasa - None."""
    allowed = set(m.group(1) for m in ART.finditer(materials_text(case)))
    got = {c.get("id"): c for c in (raw.get("criteria") or []) if isinstance(c, dict)}
    rude = {sd: any(profane_fn(_s(t.get("text"), 1200)) for t in tr if t.get("side") == sd) for sd in SIDES}
    spoke = {sd: sum(1 for t in tr if t.get("side") == sd and _s(t.get("text"), 5)) for sd in SIDES}
    crit, totals = [], {sd: 0 for sd in SIDES}
    for cid, label, mx in CRITERIA:
        c = got.get(cid) or {}
        row = {"id": cid, "label": label, "max": mx}
        for sd in SIDES:
            try:
                v = int(round(float(c.get(sd, 0))))
            except (TypeError, ValueError):
                v = 0
            v = max(0, min(mx, v))
            if cid == "manners" and rude[sd]:
                v = 0
            if not spoke[sd]:
                v = 0
            row[sd] = v
            totals[sd] += v
        note = _clean(c.get("note"), allowed, 300)
        if cid == "manners" and any(rude.values()):
            note = (note + " " if note else "") + "Haqorat qilgan tomonga sud odobi bo'yicha 0 ball."
        row["note"] = note
        crit.append(row)
    d = totals["claimant"] - totals["respondent"]
    winner = None if abs(d) <= DRAW_MARGIN else ("claimant" if d > 0 else "respondent")
    ruling = [x for x in (_clean(r, allowed, 300) for r in (raw.get("ruling") or []) if isinstance(r, str))
              if x and not re.search(r"qanoatlantiril|undirilsin|rad etilsin|ustun|g'olib|gʻolib|durang", x, re.I)][:4]
    ruling = (["Sud taraflarning chiqishlarini eshitdi va baholadi."] + ruling)[:5]
    ruling.append(f"Bahsda {SIDE_UZ[winner]} tomoni ustun keldi." if winner else "Bahs durang bilan yakunlandi.")
    pnotes = {_s(p.get("name"), 60): _clean(p.get("note"), allowed, 300) for p in (raw.get("players") or []) if isinstance(p, dict)}
    pl = []
    for p in players:
        if not isinstance(p, dict):
            continue
        mine = [t for t in tr if t.get("by") == p.get("id")]
        pl.append({"id": _s(p.get("id"), 64), "name": _s(p.get("name"), 60), "side": p.get("side"),
                   "words": sum(len(_s(t.get("text"), 1200).split()) for t in mine),
                   "speeches": len({t.get("step") for t in mine}), "note": pnotes.get(_s(p.get("name"), 60), "")})
    return {"winner": winner, "totals": totals, "criteria": crit, "ruling": ruling, "players": pl}


# ---------------------------------------------------------------- rubrika bo'yicha baholash (v1.5)
RUNS = 1                         # AIHUB sekin (20-60 s); tez API kaliti bilan 3 ga oshiriladi (ko'pchilik ovozi)
PUNKT = re.compile(r"(?<![\d.])(\d{1,4}(?:\.\d{1,3})?) ?-? ?(?:punkt|band)", re.I)


def _rule_fn(case, tr, agenda, profane_fn):
    mats = materials_text(case)
    arts = {m.group(1) for m in ART.finditer(mats)}
    punkts = {m.group(1) for m in PUNKT.finditer(mats)}
    by = {sd: [t for t in tr if t.get("side") == sd and _s(t.get("text"), 3)] for sd in SIDES}

    def ids(lst):
        return [str(t.get("seq")) for t in lst][:3]

    def rule(it, sd):
        mine = by[sd]
        r = it.get("rule")
        if r == "cited_material_norm":
            hit = [t for t in mine if any(m.group(1) in arts for m in ART.finditer(_s(t.get("text"), 1200)))
                   or any(m.group(1) in punkts for m in PUNKT.finditer(_s(t.get("text"), 1200)))]
            return bool(hit), ids(hit), "materiallardagi norma tilga olindi" if hit else "materiallardagi norma tilga olinmadi"
        if r == "unsourced_norm":
            hit = [t for t in mine if any(m.group(1) not in arts for m in ART.finditer(_s(t.get("text"), 1200)))]
            return bool(hit), ids(hit), "materiallarda yo'q modda keltirildi" if hit else "manbasiz modda yo'q"
        if r == "spoke_all_turns":
            steps = [a.get("id") for a in agenda or [] if isinstance(a, dict) and a.get("side") == sd]
            if not steps:
                return None, [], "kun tartibi berilmagan"
            done = {t.get("step") for t in mine}
            miss = [x for x in steps if x not in done]
            return not miss, ids(mine), "hamma so'zda gapirdi" if not miss else f"gapirilmagan so'z: {', '.join(map(str, miss))}"
        if r == "closing":
            hit = [t for t in mine if str(t.get("step") or "").startswith("close")]
            return bool(hit), ids(hit), "muzokarada chiqdi" if hit else "muzokarada chiqmadi"
        if r == "address_court":
            hit = [t for t in mine if "hurmatli sud" in re.sub(r"\s+", " ", _s(t.get("text"), 1200).lower())]
            return bool(hit), ids(hit), "«Hurmatli sud» deb murojaat qildi" if hit else "«Hurmatli sud» murojaati yo'q"
        if r == "profanity":
            hit = [t for t in mine if profane_fn(_s(t.get("text"), 1200))]
            return bool(hit), ids(hit), "haqoratli so'z ishlatildi" if hit else "haqorat yo'q"
        return None, [], "qoida yo'q"
    return rule


def _short(ask, n=110):
    a = ask[0].lower() + ask[1:] if ask else ""
    return a if len(a) <= n else a[:n].rsplit(" ", 1)[0] + "…"


def build_rubric(case, tr, players, res):
    """Rubrika natijasidan (bandlar + dalil) frontend MootVerdict shaklini yig'adi - ballni server hisoblaydi."""
    R = RB.RUBRICS["moot"]
    sd = res["sides"]
    crit = []
    for d in R["dims"]:
        row = {"id": d["id"], "label": d["label"], "max": d["max"]}
        for side in SIDES:
            row[side] = int(round(next(c["score"] for c in sd[side]["criteria"] if c["id"] == d["id"])))
        diff = []
        for it in (x for x in R["items"] if x["dim"] == d["id"]):
            a = next(x for x in sd["claimant"]["items"] if x["id"] == it["id"])
            b = next(x for x in sd["respondent"]["items"] if x["id"] == it["id"])
            if (a["met"] == "yes") != (b["met"] == "yes"):
                who = "daʼvogar" if (a["met"] == "yes") == (it["weight"] > 0) else "javobgar"
                diff.append((abs(it["weight"]), f"{who} foydasiga: {_short(it['ask'], 80)}"))
        row["note"] = ("Farq - " + "; ".join(t for _, t in sorted(diff, reverse=True)[:2]) + ".") if diff else "Bu mezonda tomonlar teng."
        crit.append(row)
    totals = {}
    for side in SIDES:                                   # etika chegarasi (capTotal) bajarilgan bo'lsa — jami shu chegaradan oshmaydi
        raw = sum(c[side] for c in crit)
        caps = [it["capTotal"] for it in R["items"] if it.get("capTotal") is not None
                and any(x["id"] == it["id"] and x["met"] == "yes" for x in sd[side]["items"])]
        totals[side] = min([raw] + caps)
    dd = totals["claimant"] - totals["respondent"]
    margin = R.get("routing", {}).get("drawMargin", DRAW_MARGIN)
    winner = None if abs(dd) <= margin else ("claimant" if dd > 0 else "respondent")
    ruling = ["Sud taraflarning chiqishlarini eshitdi va baholadi."]
    tips = {}
    for side in SIDES:
        its = sd[side]["items"]
        good = sorted((x for x in its if x["met"] == "yes" and x["weight"] > 0), key=lambda x: -x["weight"])
        bad = sorted((x for x in its if x["met"] == "no" and x["weight"] > 0), key=lambda x: -x["weight"])
        neg = [x for x in its if x["met"] == "yes" and x["weight"] < 0]
        uz = SIDE_UZ[side].capitalize()
        if good:
            ruling.append(f"{uz} tomonining kuchli jihati: {_short(good[0]['ask'])}.")
        if neg:
            ruling.append(f"{uz} tomoni: {_short(neg[0]['ask'])} - bu ballni kamaytirdi.")
        elif bad:
            ruling.append(f"{uz} tomonida yetishmadi: {_short(bad[0]['ask'])}.")
        tips[side] = bad[0]["ask"] if bad else None
    ruling = ruling[:5] + [f"Bahsda {SIDE_UZ[winner]} tomoni ustun keldi." if winner else "Bahs durang bilan yakunlandi."]
    pl = []
    for p in players:
        if not isinstance(p, dict):
            continue
        mine = [t for t in tr if t.get("by") == p.get("id")]
        tip = tips.get(p.get("side"))
        pl.append({"id": _s(p.get("id"), 64), "name": _s(p.get("name"), 60), "side": p.get("side"),
                   "words": sum(len(_s(t.get("text"), 1200).split()) for t in mine),
                   "speeches": len({t.get("step") for t in mine}),
                   "note": f"Keyingi safar: {_short(tip, 140)}." if tip else "Jamoangiz barcha asosiy bandlarni bajardi."})
    return {"winner": winner, "totals": totals, "criteria": crit, "ruling": ruling, "players": pl}


def explain_of(body):
    """Bahs qarorining izohi: har band, dalil (bayonnomadagi aniq gap), manba, mentorga yuborish sababi."""
    ent = CACHE.get(key_of(body))
    return ent.get("explain") if ent else None


def by_id(vid, side=None, owner=None, case_id=None):
    """Yechimga biriktirish: bahs sudyasining haqiqiy qarori (server keshidan). Faqat o'sha egasi so'ragan va
    o'sha case bo'yicha qaror; tomon o'yinchilar ro'yxatidan olinadi (talaba o'zi tanlay olmaydi)."""
    if not isinstance(vid, str) or not re.fullmatch(r"[0-9a-f]{16}", vid):
        return None
    with LOCK:
        ent = next((v for k, v in CACHE.items() if k.startswith(vid) and v.get("verdict")), None)
    if not ent or (case_id and ent.get("caseId") != case_id):
        return None
    owners = ent.get("owners") or {}
    oh = _ohash(owner) if owner else None
    if oh not in owners:                                  # bu bahs ishtirokchisi emas
        return None
    v = ent["verdict"]
    side = owners[oh] or side
    return {"verified": True, "winner": v["winner"], "totals": v["totals"], "side": side,
            "won": (v["winner"] == side) if side and v["winner"] else None}


def _ohash(owner):
    return hashlib.sha256(("moot:" + (owner or "")).encode()).hexdigest()[:24]


AI_SLOTS = threading.BoundedSemaphore(4)
ON_EXPLAIN = None                                        # server: review.route_moot                 # bir vaqtda ko'pi bilan 4 ta AI baholash


def judge(body, ask_fn, profane_fn, owner=None, owner_side=None):
    """-> verdict. ask_fn(prompt, timeout) -> (matn|None, model, ms, why). Kutish 22 s; kech qolsa ish fonda davom etadi
    va natija keshga tushadi - xuddi shu so'rov qayta kelsa darhol qaytadi (503 judge_pending + Retry-After)."""
    case, tr, players = validate(body)
    if not any(t.get("side") in SIDES and _s(t.get("text"), 5) for t in tr):
        raise JudgeError(422, "validation_failed", "Bayonnomada tomonlarning chiqishi yo'q")
    k = key_of(body)
    now = time.time()
    with LOCK:
        for kk in [x for x, v in CACHE.items() if now - v["at"] > CACHE_TTL]:
            CACHE.pop(kk, None)
        ent = CACHE.get(k)
        fresh = ent is None or (ent["verdict"] is None and ent["event"].is_set())   # oldingi urinish xato bilan tugagan
        if fresh:
            if len(CACHE) > 2000:                         # xotira chegarasi: eng eskisini chiqarish
                for kk in sorted(CACHE, key=lambda x: CACHE[x]["at"])[:200]:
                    CACHE.pop(kk, None)
            owners = {}                                   # kim bu qarorni yechimiga biriktira oladi: {egasi_xeshi: tomon}
            for x in (body.get("participants") or [])[:12]:
                if isinstance(x, dict) and isinstance(x.get("owner"), str) and x.get("side") in SIDES + (None,):
                    owners[_ohash(x["owner"])] = x.get("side")
            if owner:
                owners.setdefault(_ohash(owner), owner_side)
            ent = CACHE[k] = {"at": now, "verdict": None, "error": None, "event": threading.Event(), "owners": owners,
                              "caseId": _s((case.get("id") if isinstance(case, dict) else "") or "", 64) or None}
    STATS["calls"] += 1
    if not fresh and ent["verdict"]:
        STATS["cached"] += 1
        return ent["verdict"]
    if fresh:
        def work():
            t0 = time.time()
            if not AI_SLOTS.acquire(timeout=120):
                ent["error"] = "AI navbati to'la"
                STATS["failed"] += 1
                ent["event"].set()
                return
            try:
                if RB is not None and "moot" in RB.RUBRICS:   # v1.5: bandlar + tasdiqlangan iqtibos
                    rtr = [{"id": str(t.get("seq")), "side": t.get("side"), "text": _s(t.get("text"), 1200),
                            "step": t.get("step")} for t in tr if t.get("side") in SIDES]
                    res, errs = RB.grade("moot", list(SIDES), rtr, materials_text(case),
                                         _rule_fn(case, tr, body.get("agenda") or [], profane_fn), ask_fn,
                                         runs=RUNS, seed=int(k[:8], 16), timeout=90)
                    if res is None:
                        ent["error"] = "; ".join(errs) or "AI javob bermadi"
                    else:
                        ent["explain"] = res
                        ent["verdict"] = build_rubric(case, tr, players, res)
                        if ON_EXPLAIN:                    # 3-bosqich: mentor navbati / tasodifiy audit (review.py)
                            try:
                                ON_EXPLAIN(k[:16], {**res, "caseId": ent.get("caseId"), "verdict": ent["verdict"]})
                            except Exception as e:  # noqa: BLE001
                                print(f"MOOT review navbati xato: {e}", flush=True)
                else:
                    txt, model, ms, why = ask_fn(prompt_of(case, body.get("agenda") or [], tr), 90)
                    raw = _json_of(txt) if txt else None
                    if raw is None:
                        ent["error"] = why or "javob JSON emas"
                    else:
                        ent["verdict"] = build(case, tr, players, raw, profane_fn)
            except Exception as e:  # noqa: BLE001
                ent["error"] = f"{type(e).__name__}: {e}"
            STATS["last_ms"] = round((time.time() - t0) * 1000)
            STATS["ok" if ent["verdict"] else "failed"] += 1
            STATS["last_error"] = ent["error"]
            print(f"MOOT judge {STATS['last_ms']} ms {'OK' if ent['verdict'] else ent['error']}", flush=True)
            AI_SLOTS.release()
            ent["event"].set()
        threading.Thread(target=work, daemon=True).start()
    ent["event"].wait(WAIT_S)
    if ent["verdict"]:
        return ent["verdict"]
    if ent["event"].is_set():
        raise JudgeError(503, "judge_unavailable", "Sudya hozir qaror chiqara olmadi. Dastlabki baho ko'rsatiladi.")
    STATS["pending"] += 1
    raise JudgeError(503, "judge_pending", "Sudya hali qaror yozyapti. Birozdan keyin xuddi shu so'rovni qayta yuboring.")
