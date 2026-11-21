"""Case laboratoriyasi: sohalar, tizim va foydalanuvchi caselari, AI bilan case tuzish.

Oqim:
  1) talaba soha tanlaydi (DOMAINS) va muammoni o'z so'zi bilan yozadi;
  2) shaxsiy ma'lumot yashiriladi (telefon, pasport, JSHSHIR, e-pochta, karta);
  3) RAG bazasidan (lex.uz nusxasi) mos moddalar olinadi - AI faqat shulardan tanlaydi;
  4) AI tuzilgan case yozadi (MootCase shakli + savollar + muvozanat);
  5) server tekshiradi: uydirma modda olib tashlanadi, majburiy qismlar, muvozanat, maxfiy faktlar soni;
  6) muallif saqlaydi → «review» (faqat o'ziga ko'rinadi) → mentor tasdiqlasa «approved» (hammaga, bahsga).
Manbalar: reports/LexSim manbalar asosi.md (sohalar va statistika - stat.sud.uz, 2025).
"""
import hashlib
import json
import re
import secrets
import sqlite3
import threading
import time

STAT_URL = "https://stat.sud.uz/"
D = lambda i, g, t, court, ct, share, modes, codes, note="": {   # noqa: E731
    "id": i, "group": g, "title": t, "court": court, "caseType": ct, "share2025": share, "modes": modes,
    "codes": codes, "note": note}
# share2025 - iqtisodiy sudlar shartnomaviy nizolari ichida (119 042 ish) yoki fuqarolik ishlari ichida; manba stat.sud.uz
DOMAINS = [
    D("supply", "iqtisodiy", "Yetkazib berish", "economic", "IPK", 24.2, ["moot"], ["FK", "IPK"]),
    D("communal", "iqtisodiy", "Kommunal xizmatlar", "economic", "IPK", 19.1, ["moot"], ["FK", "IPK"]),
    D("credit", "iqtisodiy", "Kredit", "economic", "IPK", 12.7, ["moot"], ["FK", "IPK"]),
    D("sale", "iqtisodiy", "Oldi-sotdi", "economic", "IPK", 11.0, ["moot"], ["FK", "IPK"]),
    D("services", "iqtisodiy", "Haq evaziga xizmat", "economic", "IPK", 8.1, ["moot"], ["FK", "IPK"]),
    D("lease", "iqtisodiy", "Ijara", "economic", "IPK", 5.1, ["court", "moot"], ["FK", "IPK"]),
    D("construction", "iqtisodiy", "Pudrat va qurilish", "economic", "IPK", 3.8, ["moot"], ["FK", "IPK"]),
    D("civil", "fuqarolik", "Fuqarolik-huquqiy nizolar (qarz, zarar)", "civil", "FPK", 34.6, ["moot"], ["FK", "FPK"]),
    D("labour", "fuqarolik", "Mehnat nizolari", "civil", "FPK", 2.2, ["path", "moot"], ["MK", "FPK"]),
    D("theft", "jinoyat", "Jinoyat haqida ariza (o'g'irlik)", "police", "JPK", None, ["path"], ["JPK", "JK"],
      "Bahs rejimi yo'q"),
    D("dxm", "ma'muriy", "Davlat xizmatlari markazi murojaati", "dxm", "MAM", None, ["path"], ["MUR"]),
]
DOM = {d["id"]: d for d in DOMAINS}
# RAG uchun sohaga xos qo'shimcha so'rov (butun hikoya bo'yicha qidiruv asosiy moddalarni o'tkazib yuborishi mumkin)
RAG_HINT = {
    "supply": "yetkazib berish shartnomasi tovar kech yetkazish neustoyka sifatsiz tovar",
    "communal": "kommunal xizmat energiya ta'minoti to'lov qarzi neustoyka",
    "credit": "kredit shartnomasi qarzni qaytarish foiz neustoyka",
    "sale": "oldi-sotdi shartnomasi tovar narxi to'lov sifat",
    "services": "haq evaziga xizmat ko'rsatish shartnomasi to'lov",
    "lease": "ijara shartnomasi ijara haqi mulkni topshirish neustoyka",
    "construction": "pudrat shartnomasi ishni topshirish qabul qilish sifat muddat",
    "civil": "qarz shartnomasi zarar undirish majburiyat",
    "labour": "mehnat shartnomasini bekor qilish ishga tiklash majburiy progul haqi",
    "theft": "jinoyat to'g'risida ariza o'g'irlik jinoyat ishini qo'zg'atish",
    "dxm": "jismoniy shaxs murojaati ko'rib chiqish muddati",
}

STATUS = ("review", "approved", "rejected")
MAX_STORY = 4000
DISCLAIMER = "Oʻquv ishi. Nomlar, summalar va sanalar oʻzgartirilgan; haqiqiy shaxslarga aloqasi yoʻq."

# ---------------------------------------------------------------- shaxsiy ma'lumotlarni yashirish
PII = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "[e-pochta]"),
    (re.compile(r"(?<!\w)@[A-Za-z][\w]{4,31}"), "[telegram]"),
    (re.compile(r"\b[A-ZА-ЯЎҚҒҲ]{2}[\s-]?\d{7}\b", re.I), "[pasport]"),
    (re.compile(r"\b\d{14}\b"), "[JSHSHIR]"),
    (re.compile(r"\b(?:\d[ -]?){16}\b"), "[karta]"),
    (re.compile(r"(?:\+?998[\s.-]?|\b8[\s.-]?)?\(?\d{2,3}\)?[\s.-]?\d{2,3}[\s.-]?\d{2}[\s.-]?\d{2}\b"), "[telefon]"),
]


def redact(text):
    n = 0
    for rx, rep in PII:
        text, k = rx.subn(rep, text)
        n += k
    return text, n


# ---------------------------------------------------------------- saqlash
_db = None
_lock = threading.Lock()


def init(path):
    global _db
    _db = sqlite3.connect(path, check_same_thread=False, timeout=10)
    _db.execute("PRAGMA journal_mode=WAL")                # bir nechta ulanish bir faylda — «database is locked» bo'lmasin
    _db.executescript("""
    CREATE TABLE IF NOT EXISTS lab_cases(id TEXT PRIMARY KEY, owner TEXT, domain TEXT, status TEXT, source TEXT,
                                         data TEXT, note TEXT, created REAL, updated REAL);
    CREATE INDEX IF NOT EXISTS lab_cases_domain ON lab_cases(domain, status);
    CREATE TABLE IF NOT EXISTS lab_solutions(id TEXT PRIMARY KEY, case_id TEXT, owner TEXT, name TEXT, side TEXT,
                                             approach TEXT, verdict TEXT, visibility TEXT, created REAL, updated REAL);
    CREATE INDEX IF NOT EXISTS lab_solutions_case ON lab_solutions(case_id, visibility);
    """)
    cols = {r[1] for r in _db.execute("PRAGMA table_info(lab_cases)")}
    if "share" not in cols:                              # v1.5: yopiq case - havola kodi bilan
        _db.execute("ALTER TABLE lab_cases ADD COLUMN share TEXT")
    _db.commit()


def _oh(owner):
    return hashlib.sha256(("lab:" + (owner or "")).encode()).hexdigest()[:24]


class LabError(Exception):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


# ---------------------------------------------------------------- tekshiruv
ART = re.compile(r"(?<![\d.])(\d{1,4}(?:[.-]\d{1,3}){0,3}) ?-? ?(?:modda|moddasi|moddasining|moddaga)", re.I)   # chegaralangan


def _s(x, n):
    """Matnni tozalash; uzun chiziq «-»/«-» → «-» (loyiha egasining talabi)."""
    return re.sub(r"\s+", " ", x[:n * 2].replace("\u2014", "-").replace("\u2013", "-")).strip()[:n] if isinstance(x, str) else ""


def _items(lst, prefix, n=12):
    out = []
    for i, x in enumerate((lst or [])[:n]):
        if isinstance(x, str):
            x = {"title": x[:80], "text": x}
        if isinstance(x, dict) and _s(x.get("text"), 5):
            out.append({"id": f"{prefix}{i + 1}", "title": _s(x.get("title"), 120) or _s(x.get("text"), 60),
                        "text": _s(x.get("text"), 800)})
    return out


def _strs(lst, n, m=400):
    return [_s(x, m) for x in (lst or [])[:n] if _s(x, 3)]


def normalize_case(raw, domain, allowed, known=None):
    """AI yoki muallif bergan caseni MootCase shakliga keltiradi va muammolarni (issues) qaytaradi.
    allowed: {norm_id: {"label","url","title"}} - faqat shu moddalarga havola qilish mumkin."""
    raw = raw if isinstance(raw, dict) else {}
    D_ = lambda x: x if isinstance(x, dict) else {}       # noqa: E731  (noto'g'ri turdagi maydon — bo'sh)
    L_ = lambda x: x if isinstance(x, list) else []       # noqa: E731
    nums = {re.sub(r"\D.*", "", nid.split("-", 1)[1]) for nid in allowed if "-" in nid}
    issues = []

    def clean(t, n):
        t = _s(t, n)
        bad = [m.group(1) for m in ART.finditer(t) if m.group(1) not in nums]
        if bad:
            issues.append(f"manbasiz modda olib tashlandi: {', '.join(bad)}")
            t = ART.sub(lambda m: m.group(0) if m.group(1) in nums else "[modda - mentor tekshiradi]", t)
        return t

    side = {}
    for sd in ("claimant", "respondent"):
        s = D_(D_(raw.get("side")).get(sd))
        side[sd] = {"task": [clean(x, 300) for x in _strs(s.get("task"), 4)],
                    "confidential": [clean(x, 300) for x in _strs(s.get("confidential"), 4)]}
    legal = []
    for x in L_(raw.get("legal")):
        nid = x.get("normId") if isinstance(x, dict) else x
        if not isinstance(nid, str):
            continue
        if nid in allowed and (known is None or nid in known):
            legal.append({"normId": nid, "label": allowed[nid]["label"], "url": allowed[nid]["url"],
                          "why": _s(x.get("why") if isinstance(x, dict) else "", 200)})
        elif nid:
            issues.append(f"bazada yo'q modda olib tashlandi: {_s(str(nid), 30)}")
    facts = [{**f, "text": clean(f["text"], 800)} for f in _items(L_(raw.get("facts")), "f")]
    evidence = [{**e, "text": clean(e["text"], 800)} for e in _items(L_(raw.get("evidence")), "e", 8)]
    parties = raw.get("parties") if isinstance(raw.get("parties"), dict) else {}
    case = {
        "title": clean(raw.get("title"), 120), "domain": domain,
        "court": _s(raw.get("court"), 120) or {"economic": "Tumanlararo iqtisodiy sud", "civil": "Fuqarolik ishlari bo'yicha tuman sudi"}.get(DOM[domain]["court"], ""),
        "summary": clean(raw.get("summary"), 600),
        "parties": {"claimant": _s(parties.get("claimant"), 120), "respondent": _s(parties.get("respondent"), 120)},
        "claim": clean(raw.get("claim"), 600), "facts": facts, "evidence": evidence, "side": side,
        "points": {sd: [[_s(w, 40) for w in g[:4] if _s(w, 2)] for g in L_(D_(raw.get("points")).get(sd))[:6]
                        if isinstance(g, list)] for sd in ("claimant", "respondent")},
        "legal": legal,
        "balance": {k: clean(D_(raw.get("balance")).get(k), 300) for k in
                    ("claimant_strong", "claimant_weak", "respondent_strong", "respondent_weak")},
        "questions": [clean(q, 300) for q in _strs(L_(raw.get("questions")), 6, 300)],
        "disclaimer": DISCLAIMER,
    }
    issues += check(case)
    return case, issues


def _redact_deep(x):
    if isinstance(x, str):
        return redact(x)
    if isinstance(x, list):
        out, n = [], 0
        for v in x:
            v2, k = _redact_deep(v)
            out.append(v2)
            n += k
        return out, n
    if isinstance(x, dict):
        out, n = {}, 0
        for k_, v in x.items():
            if k_ in ("url", "normId", "id", "domain"):
                out[k_] = v
                continue
            v2, k = _redact_deep(v)
            out[k_] = v2
            n += k
        return out, n
    return x, 0


def check(case):
    """Bahsga tayyorlik qoidalari (frontend LexSim_Bahs_Backend.md, 7-bo'lim)."""
    out = []
    if not case["title"] or not case["claim"]:
        out.append("sarlavha yoki talab yo'q")
    if not case["parties"]["claimant"] or not case["parties"]["respondent"]:
        out.append("taraflar ko'rsatilmagan")
    if len(case["facts"]) < 3:
        out.append("faktlar kam (kamida 3 ta)")
    if not case["evidence"]:
        out.append("dalil yo'q")
    for sd, uz in (("claimant", "da'vogar"), ("respondent", "javobgar")):
        n = len(case["side"][sd]["confidential"])
        if not 2 <= n <= 4:
            out.append(f"{uz}: maxfiy faktlar {n} ta (2-4 kerak)")
        if not case["side"][sd]["task"]:
            out.append(f"{uz}: vazifa yo'q")
        if not case["balance"][f"{sd}_strong"] or not case["balance"][f"{sd}_weak"]:
            out.append(f"muvozanat: {uz}ning kuchli va zaif joyi ko'rsatilmagan")
    if not case["legal"]:
        out.append("huquqiy asos yo'q - mentor moddalarni qo'shadi")
    return out


# ---------------------------------------------------------------- AI qoralama
DRAFTS = {}                     # id -> {"at","owner","status","case","issues","error","event"}
DRAFT_TTL = 6 * 3600


def prompt_of(domain, story, allowed):
    d = DOM[domain]
    arts = "\n".join(f"- {nid}: {a['label']} - {a['title'][:140]}" for nid, a in allowed.items()) or "- (bazada mos modda topilmadi)"
    return (
        "Sen O'zbekiston huquqshunoslik talabalari uchun o'quv sud bahsi (moot court) ishlarini tuzuvchi tajribali yuristsan.\n"
        f"SOHA: {d['title']} ({d['group']}, sud: {d['court']}).\n"
        "Foydalanuvchi muammoni o'z so'zi bilan yozdi. Uni ikki tomon teng bahslasha oladigan o'quv ishiga aylantir.\n"
        "QOIDALAR:\n"
        "1) Faqat foydalanuvchi yozgan holatlarga tayan. Yangi muhim fakt, summa yoki sana o'ylab topma - "
        "yetishmasa, uni 'questions' ga savol qilib yoz va matnda [aniqlanmagan] deb qoldir.\n"
        "2) Haqiqiy ism va kompaniya nomlarini shartli nomlarga almashtir («A» MChJ, Sardor N. kabi).\n"
        "3) Huquqiy asos: faqat quyidagi ro'yxatdan normId tanla. Matnda ham faqat shu moddalarni tilga ol:\n"
        f"{arts}\n"
        "4) Ikkala tomonda ham kamida bitta kuchli va bitta zaif joy bo'lsin. Har tomonga 2-4 ta maxfiy fakt "
        "(faqat o'sha tomon biladi, foydalanuvchi holatidan kelib chiqsin).\n"
        "5) Bu o'quv ishi, haqiqiy maslahat emas.\n\n"
        f"FOYDALANUVCHI HOLATI:\n{story}\n\n"
        "Faqat JSON qaytar:\n"
        '{"title":"...","court":"...","summary":"2-3 gap","parties":{"claimant":"...","respondent":"..."},'
        '"claim":"talab","facts":[{"title":"...","text":"..."}],"evidence":[{"title":"...","text":"..."}],'
        '"side":{"claimant":{"task":["..."],"confidential":["..."]},"respondent":{"task":["..."],"confidential":["..."]}},'
        '"legal":[{"normId":"FK-333","why":"..."}],'
        '"balance":{"claimant_strong":"...","claimant_weak":"...","respondent_strong":"...","respondent_weak":"..."},'
        '"points":{"claimant":[["kalit","so\'z"]],"respondent":[["..."]]},"questions":["aniqlashtiruvchi savol"]}'
    )


def _json_of(txt):
    m = re.search(r"\{.*\}", txt or "", re.S)
    try:
        return json.loads(m.group(0)) if m else None
    except ValueError:
        return None


def start_draft(owner, domain, story, ask_fn, rag_fn, known=None):
    """-> draft id. Fonda ishlaydi (AI ~20-60 s). rag_fn(story, case_type) -> {norm_id: {label,url,title}}."""
    if domain not in DOM:
        raise LabError(422, "validation_failed", "Soha noto'g'ri")
    story = _s(story, MAX_STORY)
    if len(story) < 80:
        raise LabError(422, "validation_failed", "Holatni batafsilroq yozing (kamida 80 belgi)")
    story, n_pii = redact(story)
    now = time.time()
    with _lock:
        for k in [k for k, v in DRAFTS.items() if now - v["at"] > DRAFT_TTL]:
            DRAFTS.pop(k, None)
        if sum(1 for v in DRAFTS.values() if v["owner"] == _oh(owner) and not v["event"].is_set()) >= 2:
            raise LabError(429, "rate_limited", "Oldingi qoralama hali tayyorlanmoqda")
        did = "d_" + secrets.token_hex(6)
        ent = DRAFTS[did] = {"at": now, "owner": _oh(owner), "domain": domain, "status": "working", "case": None,
                             "issues": [], "error": None, "pii": n_pii, "event": threading.Event(), "ms": None}

    def work():
        t0 = time.time()
        try:
            ct = DOM[domain]["caseType"]
            codes = DOM[domain]["codes"] if ct not in ("IPK", "FPK") else None
            allowed = (rag_fn(story, ct, RAG_HINT.get(domain, ""), codes) if codes else rag_fn(story, ct, RAG_HINT.get(domain, ""))) if ct else {}
            ent["sources"] = len(allowed)
            raw, why = None, None
            for _try in (1, 2):                          # bitta qayta urinish (chala javob)
                txt, model, ms, why = ask_fn(prompt_of(domain, story, allowed), 120)
                raw = _json_of(txt)
                if raw is not None or time.time() - t0 > 150:
                    break
            if raw is None:
                ent["status"], ent["error"] = "failed", why or "AI javobi JSON emas"
            else:
                ent["case"], ent["issues"] = normalize_case(raw, domain, allowed, known)
                ent["status"] = "ready"
        except Exception as e:  # noqa: BLE001
            ent["status"], ent["error"] = "failed", f"{type(e).__name__}"
        ent["ms"] = round((time.time() - t0) * 1000)
        print(f"CASELAB draft {did} {domain} {ent['status']} {ent['ms']} ms rag={ent.get('sources')} {ent['error'] or ''}", flush=True)
        ent["event"].set()
    threading.Thread(target=work, daemon=True).start()
    return did


def get_draft(owner, did):
    ent = DRAFTS.get(did)
    if not ent or ent["owner"] != _oh(owner):
        raise LabError(404, "draft_not_found", "Qoralama topilmadi")
    out = {"id": did, "status": ent["status"], "domain": ent["domain"]}
    if ent["status"] == "ready":
        out.update(case=ent["case"], issues=ent["issues"], ms=ent["ms"], sources=ent.get("sources", 0))
    if ent["status"] == "failed":
        out["error"] = {"code": "draft_failed", "message": "AI caseni tuza olmadi. Qayta urinib ko'ring yoki holatni aniqroq yozing."}
    if ent["pii"]:
        out["redacted"] = ent["pii"]
    return out


# ---------------------------------------------------------------- caselar
SEL = "SELECT id, owner, domain, status, source, data, note, created, updated, share FROM lab_cases"


def _row(r, me=None, admin=False, full=False):
    cid, owner, domain, status, source, data, note, created, updated, share = r
    c = json.loads(data)
    mine = me is not None and owner == _oh(me)
    if not (full or mine or admin):
        c["side"] = {sd: {"task": v["task"], "confidential": []} for sd, v in c["side"].items()}   # maxfiy faktlar - faqat bahs xonasida
        c.pop("balance", None)
    c.update(id=cid, domain=domain, status=status, source=source, mine=mine, reviewNote=note if (mine or admin) else None,
             visibility="private" if status == "private" else "public",
             modes=c.get("modes") or DOM.get(domain, {}).get("modes", []),
             shareCode=share if (mine or admin) and status == "private" else None,
             solutions=_db.execute("SELECT COUNT(*) FROM lab_solutions WHERE case_id=? AND visibility='public'", (cid,)).fetchone()[0],
             createdAt=_iso(created), updatedAt=_iso(updated))
    return c


def _iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def save(owner, case, domain, known=None, allowed_ids=None, cid=None, visibility="public"):
    """visibility: public - mentor tasdig'idan keyin hammaga; private - faqat muallif va havola kodi borlarga (tekshiruvsiz)."""
    if visibility not in ("public", "private"):
        raise LabError(422, "validation_failed", "visibility: public | private")
    status = "review" if visibility == "public" else "private"
    if domain not in DOM:
        raise LabError(422, "validation_failed", "Soha noto'g'ri")
    if not isinstance(case, dict):
        raise LabError(422, "validation_failed", "case obyekt bo'lishi kerak")
    allowed = {x["normId"]: x for x in case.get("legal") or [] if isinstance(x, dict) and x.get("normId") in (allowed_ids or {})}
    allowed = {k: {"label": (allowed_ids or {})[k]["label"], "url": (allowed_ids or {})[k]["url"], "title": ""} for k in allowed}
    norm, issues = normalize_case(case, domain, allowed, known)
    norm, n_pii = _redact_deep(norm)                      # qo'lda kiritilgan maydonlarda ham shaxsiy ma'lumot yashiriladi
    if n_pii:
        issues.append(f"shaxsiy ma'lumot yashirildi: {n_pii} ta")
    blob = json.dumps(norm, ensure_ascii=False)
    if len(blob) > 64 * 1024:
        raise LabError(413, "payload_too_large", "Case juda katta")
    now = time.time()
    with _lock:
        if cid:
            r = _db.execute("SELECT owner, status FROM lab_cases WHERE id=?", (cid,)).fetchone()
            if not r or r[0] != _oh(owner):
                raise LabError(404, "case_not_found", "Case topilmadi")
            _db.execute("UPDATE lab_cases SET data=?, domain=?, status=?, note=NULL, updated=?, "
                        "share=COALESCE(share, ?) WHERE id=?", (blob, domain, status, now, secrets.token_urlsafe(9), cid))
        else:
            if status == "review" and _db.execute("SELECT COUNT(*) FROM lab_cases WHERE owner=? AND status='review'",
                                                  (_oh(owner),)).fetchone()[0] >= 10:
                raise LabError(429, "too_many_pending", "Tekshiruvni kutayotgan caselaringiz ko'p (10 ta)")
            if _db.execute("SELECT COUNT(*) FROM lab_cases WHERE owner=?", (_oh(owner),)).fetchone()[0] >= 100:
                raise LabError(429, "too_many_cases", "Caselar soni chegarasi (100 ta)")
            cid = "u_" + secrets.token_hex(5)
            _db.execute("INSERT INTO lab_cases (id, owner, domain, status, source, data, note, created, updated, share) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (cid, _oh(owner), domain, status, "user", blob, None, now, now, secrets.token_urlsafe(9)))
        _db.commit()
    return get(owner, cid), issues


def set_visibility(owner, cid, visibility):
    """Muallif caseni ochadi (→ mentor tekshiruvi) yoki yopadi (→ faqat o'zi va havola kodi borlar)."""
    if visibility not in ("public", "private"):
        raise LabError(422, "validation_failed", "visibility: public | private")
    with _lock:
        r = _db.execute("SELECT owner, status FROM lab_cases WHERE id=?", (cid,)).fetchone()
        if not r or r[0] != _oh(owner):
            raise LabError(404, "case_not_found", "Case topilmadi")
        new = "private" if visibility == "private" else ("approved" if r[1] == "approved" else "review")
        if new == "review" and _db.execute("SELECT COUNT(*) FROM lab_cases WHERE owner=? AND status='review'",
                                           (_oh(owner),)).fetchone()[0] >= 10:
            raise LabError(429, "too_many_pending", "Tekshiruvni kutayotgan caselaringiz ko'p (10 ta)")
        if new == "private":                              # yopilganda yangi havola kodi — eski havola ishlamaydi
            _db.execute("UPDATE lab_cases SET status=?, updated=?, share=? WHERE id=?",
                        (new, time.time(), secrets.token_urlsafe(9), cid))
        else:
            _db.execute("UPDATE lab_cases SET status=?, updated=? WHERE id=?", (new, time.time(), cid))
        _db.commit()
    return get(owner, cid)


def _visible(r, me, admin, code):
    if admin or (me is not None and r[1] == _oh(me)) or r[3] == "approved":
        return True
    return r[3] == "private" and isinstance(code, str) and bool(code) and \
        secrets.compare_digest(code.encode(), (r[9] or "").encode())


def get(me, cid, admin=False, full=False, code=None):
    r = _db.execute(SEL + " WHERE id=?", (cid,)).fetchone()
    if not r or not _visible(r, me, admin, code):
        raise LabError(404, "case_not_found", "Case topilmadi")
    return _row(r, me, admin, full)


def listing(me, domain=None, scope="all", admin=False):
    q, a = SEL + " WHERE 1=1", []
    if domain:
        q += " AND domain=?"
        a.append(domain)
    if scope == "mine":
        q += " AND owner=?"
        a.append(_oh(me))
    elif scope == "review" and admin:
        q += " AND status='review'"
    else:
        q += " AND (status='approved' OR owner=?)"
        a.append(_oh(me))
    out = []
    for r in _db.execute(q + " ORDER BY source='system' DESC, updated DESC LIMIT 200", a):
        c = _row(r, me, admin)
        out.append({k: c.get(k) for k in ("id", "title", "domain", "court", "summary", "status", "source", "mine",
                                           "visibility", "solutions", "updatedAt", "reviewNote")}
                   | {"modes": DOM.get(c["domain"], {}).get("modes", [])})
    return out


# ---------------------------------------------------------------- yechimlar (ishtirokchilarning yondashuvi)
SIDES = ("claimant", "respondent")


def _sol(r, me, admin=False):
    sid, case_id, owner, name, side, approach, verdict, vis, created, updated = r
    return {"id": sid, "caseId": case_id, "name": name or "Anonim", "side": side, "approach": approach,
            "verdict": json.loads(verdict) if verdict else None, "visibility": vis,
            "mine": me is not None and owner == _oh(me), "createdAt": _iso(created), "updatedAt": _iso(updated)}


def add_solution(me, cid, body, profane_fn=None, verdict_fn=None, code=None):
    """Talaba case bo'yicha yechimini (yondashuvi, dalillari, natijasi) qoldiradi; o'zi ochiq yoki yopiq qiladi."""
    get(me, cid, code=code)                               # case unga ko'rinmasa - 404
    if not isinstance(body, dict):
        raise LabError(422, "validation_failed", "JSON obyekt kerak")
    vis = body.get("visibility") or "private"
    side = body.get("side")
    if vis not in ("public", "private") or side not in SIDES + (None,):
        raise LabError(422, "validation_failed", "visibility: public | private; side: claimant | respondent | null")
    approach, n_pii = redact(_s(body.get("approach"), 4000))
    if len(approach) < 50:
        raise LabError(422, "validation_failed", "Yechimni batafsilroq yozing (kamida 50 belgi)")
    name = redact(_s(body.get("name"), 40))[0]
    if profane_fn and (profane_fn(approach) or profane_fn(name)):
        raise LabError(422, "ethics", "Matnda haqoratli so'z bor - yechim qabul qilinmadi")
    verdict = verdict_fn(body["verdictId"], side) if verdict_fn and body.get("verdictId") else None
    now = time.time()
    with _lock:
        if _db.execute("SELECT COUNT(*) FROM lab_solutions WHERE case_id=? AND owner=?", (cid, _oh(me))).fetchone()[0] >= 5:
            raise LabError(429, "too_many_solutions", "Bitta casega ko'pi bilan 5 ta yechim")
        sid = "sol_" + secrets.token_hex(5)
        _db.execute("INSERT INTO lab_solutions VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (sid, cid, _oh(me), name, side, approach, json.dumps(verdict, ensure_ascii=False) if verdict else None,
                     vis, now, now))
        _db.commit()
    out = _sol(_db.execute("SELECT * FROM lab_solutions WHERE id=?", (sid,)).fetchone(), me)
    if n_pii:
        out["redacted"] = n_pii
    return out


def solutions(me, cid, admin=False, code=None):
    get(me, cid, admin, code=code)
    rows = _db.execute("SELECT * FROM lab_solutions WHERE case_id=? AND (visibility='public' OR owner=?) "
                       "ORDER BY updated DESC LIMIT 200", (cid, _oh(me))).fetchall() if not admin else \
        _db.execute("SELECT * FROM lab_solutions WHERE case_id=? ORDER BY updated DESC LIMIT 200", (cid,)).fetchall()
    return [_sol(r, me, admin) for r in rows]


def edit_solution(me, sid, body, profane_fn=None, admin=False):
    """Muallif: visibility / approach / name ni o'zgartiradi, yoki {"delete": true}. Mentor: {"visibility": "hidden"}."""
    with _lock:
        r = _db.execute("SELECT * FROM lab_solutions WHERE id=?", (sid,)).fetchone()
        if not r or not (admin or r[2] == _oh(me)):
            raise LabError(404, "solution_not_found", "Yechim topilmadi")
        if body.get("delete"):
            _db.execute("DELETE FROM lab_solutions WHERE id=?", (sid,))
            _db.commit()
            return None
        vis = body.get("visibility", r[7])
        if r[7] == "hidden" and not admin:                # mentor yashirgan — muallif qayta ocholmaydi (o'chirishi mumkin)
            if "visibility" in body and vis != "hidden":
                raise LabError(403, "hidden_by_mentor", "Bu yechimni mentor yashirgan")
            vis = "hidden"
        if vis not in ("public", "private", "hidden") if (admin or r[7] == "hidden") else vis not in ("public", "private"):
            raise LabError(422, "validation_failed", "visibility: public | private")
        approach = redact(_s(body["approach"], 4000))[0] if "approach" in body else r[5]
        name = _s(body["name"], 40) if "name" in body else r[3]
        if len(approach) < 50 or (profane_fn and (profane_fn(approach) or profane_fn(name or ""))):
            raise LabError(422, "validation_failed", "Yechim matni qisqa yoki haqoratli so'z bor")
        _db.execute("UPDATE lab_solutions SET visibility=?, approach=?, name=?, updated=? WHERE id=?",
                    (vis, approach, name, time.time(), sid))
        _db.commit()
    return _sol(_db.execute("SELECT * FROM lab_solutions WHERE id=?", (sid,)).fetchone(), me, admin)


def review(cid, decision, note=""):
    if decision not in ("approve", "reject"):
        raise LabError(422, "validation_failed", "decision: approve | reject")
    with _lock:
        allowed_from = ("review",) if decision == "approve" else ("review", "approved")   # yopiq caseni mentor ocholmaydi
        n = _db.execute("UPDATE lab_cases SET status=?, note=?, updated=? WHERE id=? AND source='user' AND status IN (%s)"
                        % ",".join("?" * len(allowed_from)),
                        ("approved" if decision == "approve" else "rejected", _s(note, 500) or None, time.time(), cid,
                         *allowed_from)).rowcount
        _db.commit()
    if not n:
        raise LabError(404, "case_not_found", "Case topilmadi")


def seed_system(cases):
    """Tizim caselari (mentor tasdiqlagan ssenariylar) - har ishga tushishda yangilanadi."""
    now = time.time()
    with _lock:
        for cid, domain, case in cases:
            blob = json.dumps(case, ensure_ascii=False)
            _db.execute("INSERT INTO lab_cases (id, owner, domain, status, source, data, note, created, updated) "
                        "VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data, "
                        "domain=excluded.domain, updated=excluded.updated", (cid, "system", domain, "approved", "system", blob, None, now, now))
        _db.commit()


def system_from_scenario(pkg):
    """scenarios/sud-ijara.json -> MootCase (bahs uchun). Maxfiy faktlar brifingdagi 'secret' lardan."""
    b = pkg.get("briefing") or {}
    cl, rs = b.get("davogar-vakili") or {}, b.get("javobgar-vakili") or {}
    strip = lambda x: re.sub(r"^Maxfiy \(faqat siz bilasiz\):\s*", "", x)  # noqa: E731
    m = pkg.get("meta") or {}
    return {
        "title": m.get("title", ""), "domain": "lease", "court": (cl.get("workplace") or "").split(" · ")[0],
        "summary": m.get("summary", ""),
        "parties": {"claimant": "«A» MChJ (ijaraga beruvchi)", "respondent": "YaTT «B» (ijarachi)"},
        "claim": next((t for t in cl.get("task", []) if "undirish" in t), ""),
        "facts": [{"id": f["id"], "title": f["id"], "text": f["text"]} for f in pkg.get("facts", []) if f.get("id") != "F1"],
        "evidence": [{"id": e["id"], "title": e["title"], "text": e["title"]} for e in pkg.get("evidence", []) if e.get("id") != "E1"],
        "side": {"claimant": {"task": cl.get("task", []), "confidential": [strip(x) for x in cl.get("secret", [])]},
                 "respondent": {"task": rs.get("task", []), "confidential": [strip(x) for x in rs.get("secret", [])]}},
        "points": {}, "legal": [], "balance": {}, "questions": [], "disclaimer": DISCLAIMER,
        "tags": m.get("tags", []), "mentorApproved": bool(m.get("mentorApproved")),
        "modes": ["court", "moot"],
        "scenarioIds": {"claimant": (m.get("roles") or {}).get("davogar-vakili"),     # «Sud zali» - /scenarios dagi id
                        "respondent": (m.get("roles") or {}).get("javobgar-vakili")},
    }
