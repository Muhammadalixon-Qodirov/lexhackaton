"""Saqlash: "Ish yo'li" holati (case_state), xAPI statement ombori, o'qituvchi hisobotlari, kunlik zaxira.

LexSim_Backend_AI_Toliq_Topshiriq.md §7.1, §7.2, §8.5. SQLite (sessions.db bilan bir fayl, alohida jadvallar).
Shaxsiy ma'lumot saqlanmaydi: talaba faqat hash (studentHash / xAPI actor.account.name) bilan.
"""
import json
import re
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

_lock = threading.Lock()
_db = None
MAX_STATE = 512 * 1024
DAY = 86400
TTL = {"dxm-session": 7 * DAY, "hearing": 7 * DAY}     # qolgan turlar (case, index ...) — DEFAULT_TTL
DEFAULT_TTL = 180 * DAY


def _expired(kind, updated, now=None):
    return (now or time.time()) - updated > TTL.get(kind, DEFAULT_TTL)


def purge():
    """Muddati o'tgan hujjatlarni o'chiradi (soatlik zaxira sikli chaqiradi). -> o'chirilganlar soni."""
    now, n = time.time(), 0
    with _lock:
        rows = _db.execute("SELECT id, kind, updated FROM case_state").fetchall()
        old = [r[0] for r in rows if _expired(r[1], r[2], now)]
        for cid in old:
            _db.execute("DELETE FROM case_state WHERE id=?", (cid,))
            n += 1
        if n:
            _db.commit()
    return n


class StoreError(Exception):
    def __init__(self, status, code, message, extra=None):
        super().__init__(message)
        self.status, self.code, self.message, self.extra = status, code, message, extra or {}


def init(path):
    global _db
    _db = sqlite3.connect(path, check_same_thread=False)
    _db.executescript("""
    CREATE TABLE IF NOT EXISTS case_state(id TEXT PRIMARY KEY, owner TEXT, kind TEXT, state TEXT,
                                          version INTEGER, updated REAL);
    CREATE TABLE IF NOT EXISTS xapi(id TEXT PRIMARY KEY, actor TEXT, verb TEXT, object TEXT, cohort TEXT,
                                    ts TEXT, score REAL, success INTEGER, data TEXT, stored REAL);
    CREATE INDEX IF NOT EXISTS xapi_cohort ON xapi(cohort);
    CREATE INDEX IF NOT EXISTS xapi_actor ON xapi(actor);
    """)
    _db.commit()


def _iso(t):
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


# ---------------------------------------------------------------- case_state (optimistic locking)
def case_get(cid, owner):
    """Faqat egasi o'qiydi. Boshqa talabaning hujjati — 404 (mavjudligi ham bilinmasin)."""
    with _lock:
        r = _db.execute("SELECT id, owner, kind, state, version, updated FROM case_state WHERE id=?", (cid,)).fetchone()
    if not r or (owner is not None and r[1] != owner) or _expired(r[2], r[5]):
        raise StoreError(404, "case_not_found", "Ish topilmadi")
    return {"id": r[0], "owner": r[1], "kind": r[2], "state": json.loads(r[3]), "version": r[4], "updatedAt": _iso(r[5])}


def case_put(cid, body, owner=None):
    """owner — X-LexSim-Owner (ustun); bo'lmasa body.owner. kind — istalgan tur (case, index, dxm-session, hearing ...)."""
    if not re.fullmatch(r"[\w.-]{4,80}", cid):
        raise StoreError(422, "validation_failed", "Ish id noto'g'ri")
    owner = owner or body.get("owner")
    kind, state, ver = body.get("kind"), body.get("state"), body.get("version")
    if not isinstance(owner, str) or not isinstance(kind, str) or not isinstance(state, (dict, list)):
        raise StoreError(422, "validation_failed", "owner, kind va state (obyekt) kerak")
    if not re.fullmatch(r"[\w.-]{1,40}", kind):
        raise StoreError(422, "validation_failed", "kind: 1–40 belgi (harf, raqam, . _ -)")
    raw = json.dumps(state, ensure_ascii=False)
    if len(raw) > MAX_STATE:
        raise StoreError(413, "payload_too_large", "Ish holati juda katta (512 KB dan oshmasin)")
    with _lock:
        r = _db.execute("SELECT version, owner, kind, updated FROM case_state WHERE id=?", (cid,)).fetchone()
        if r is not None and _expired(r[2], r[3]):       # muddati o'tgan — yangidek
            _db.execute("DELETE FROM case_state WHERE id=?", (cid,))
            r = None
        if r is None:
            if ver not in (None, 0):
                raise StoreError(409, "version_conflict", "Bunday ish hali saqlanmagan", {"version": 0})
            new = 1
        else:
            if r[1] != owner:                            # boshqa talabaniki — mavjudligi ham bilinmasin
                raise StoreError(404, "case_not_found", "Ish topilmadi")
            if ver != r[0]:
                raise StoreError(409, "version_conflict", "Ish boshqa joyda o'zgargan, qayta o'qing",
                                 {"version": r[0]})
            new = r[0] + 1
        _db.execute("INSERT OR REPLACE INTO case_state VALUES (?,?,?,?,?,?)", (cid, owner, kind, raw, new, time.time()))
        _db.commit()
    return {"id": cid, "version": new}


# ---------------------------------------------------------------- xAPI
def _actor(st):
    a = st.get("actor") or {}
    acc = a.get("account") or {}
    return acc.get("name") or a.get("mbox_sha1sum") or a.get("openid") or "anonim"


def _cohort(st):
    ctx = st.get("context") or {}
    ext = ctx.get("extensions") or {}
    for k, v in ext.items():
        if k.rstrip("/").endswith("cohort") and isinstance(v, str):
            return v
    grp = (ctx.get("team") or {}).get("name")
    return grp or ctx.get("registration") or ""


def xapi_put(statements):
    if isinstance(statements, dict):
        statements = [statements]
    if not isinstance(statements, list) or not (1 <= len(statements) <= 200):
        raise StoreError(422, "validation_failed", "1–200 ta statement yuboring")
    ids, now, stored = [], time.time(), 0
    with _lock:
        for st in statements:
            if not isinstance(st, dict) or not isinstance(st.get("verb"), dict) or not isinstance(st.get("object"), dict):
                raise StoreError(422, "validation_failed", "Har bir statement'da actor, verb, object bo'lsin")
            a = st.get("actor") or {}
            if a.get("mbox") or a.get("name"):          # maxfiylik: ism va email serverda saqlanmaydi
                raise StoreError(422, "validation_failed", "actor anonim bo'lsin (account.name = studentHash)")
            sid = st.get("id") or str(uuid.uuid4())
            res = st.get("result") or {}
            score = (res.get("score") or {}).get("raw")
            cur = _db.execute("INSERT OR IGNORE INTO xapi VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (sid, _actor(st), st["verb"].get("id", ""), st["object"].get("id", ""), _cohort(st),
                         st.get("timestamp") or _iso(now), score if isinstance(score, (int, float)) else None,
                         None if res.get("success") is None else int(bool(res.get("success"))),
                         json.dumps(st, ensure_ascii=False), now))
            stored += cur.rowcount            # id bo'yicha idempotent: takror yuborilgan statement qayta yozilmaydi
            ids.append(sid)
        _db.commit()
    return ids, stored


def _dur(s):
    m = re.fullmatch(r"P(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?", s or "")
    if not m:
        return 0.0
    h, mi, se = (float(x) if x else 0.0 for x in m.groups())
    return h * 3600 + mi * 60 + se


def _rows(cohort):
    with _lock:
        return [json.loads(r[0]) | {"_actor": r[1]} for r in
                _db.execute("SELECT data, actor FROM xapi WHERE cohort=? ORDER BY ts", (cohort,)).fetchall()]


def _ext(st, name):
    for src in ((st.get("result") or {}).get("extensions") or {}, (st.get("context") or {}).get("extensions") or {}):
        for k, v in src.items():
            if k.rstrip("/").endswith(name):
                return v
    return None


def cohort_summary(cohort):
    out = {}
    for st in _rows(cohort):
        a = out.setdefault(st["_actor"], {"studentHash": st["_actor"], "cases": set(), "scores": [], "errors": 0,
                                           "hints": 0, "timeSec": 0.0, "lastActivity": None})
        verb = st["verb"].get("id", "").rsplit("/", 1)[-1]
        res = st.get("result") or {}
        obj = st["object"].get("id", "")
        if verb in ("completed", "passed", "failed", "scored"):
            a["cases"].add(obj)
            raw = (res.get("score") or {}).get("raw")
            if isinstance(raw, (int, float)):
                a["scores"].append(raw)
            a["timeSec"] += _dur(res.get("duration"))
        if res.get("success") is False or _ext(st, "tone") == "bad":
            a["errors"] += 1
        if verb == "hinted" or _ext(st, "hint"):
            a["hints"] += 1
        a["lastActivity"] = st.get("timestamp") or a["lastActivity"]
    students = []
    for a in out.values():
        sc = a.pop("scores")
        a["cases"] = len(a["cases"])
        a["avgScore"] = round(sum(sc) / len(sc), 1) if sc else None
        a["timeSec"] = round(a["timeSec"])
        students.append(a)
    return {"cohortId": cohort, "students": sorted(students, key=lambda x: x["studentHash"]), "statements": sum(1 for _ in _rows(cohort))}


def cohort_hotspots(cohort, limit=10):
    spots = {}
    for st in _rows(cohort):
        res = st.get("result") or {}
        if not (res.get("success") is False or _ext(st, "tone") == "bad"):
            continue
        obj = st["object"]
        key = obj.get("id", "")
        name = ((obj.get("definition") or {}).get("name") or {})
        h = spots.setdefault(key, {"objectId": key, "title": next(iter(name.values()), None) if isinstance(name, dict) else None,
                                   "errors": 0, "students": set(), "articles": {}})
        h["errors"] += 1
        h["students"].add(st["_actor"])
        art = _ext(st, "article")
        if art:
            h["articles"][art] = h["articles"].get(art, 0) + 1
    res = []
    for h in spots.values():
        h["students"] = len(h["students"])
        h["articles"] = [k for k, _ in sorted(h["articles"].items(), key=lambda kv: -kv[1])]
        res.append(h)
    return {"cohortId": cohort, "hotspots": sorted(res, key=lambda x: (-x["errors"], x["objectId"]))[:limit]}


# ---------------------------------------------------------------- kunlik zaxira (14 kun)
def backup_loop(db_path, keep=14, log=print):
    d = Path(db_path).resolve().parent / "backups"
    d.mkdir(exist_ok=True)
    while True:
        try:
            n = purge()
            if n:
                log(f"Ombor: muddati o'tgan {n} ta hujjat o'chirildi")
        except Exception as e:  # noqa: BLE001
            log(f"Ombor tozalash xatosi: {e!r}")
        name = d / f"sessions-{datetime.now(timezone.utc):%Y%m%d}.db"
        if not name.exists():
            try:
                src, dst = sqlite3.connect(db_path), sqlite3.connect(str(name))
                with dst:
                    src.backup(dst)
                src.close()
                dst.close()
                for old in sorted(d.glob("sessions-*.db"))[:-keep]:
                    old.unlink()
                log(f"Zaxira: {name.name}")
            except Exception as e:  # noqa: BLE001
                log(f"Zaxira xatosi: {e!r}")
        time.sleep(3600)
