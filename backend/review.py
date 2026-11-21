"""Uch bosqichli tekshiruv — 3-bosqich: mentor navbati, tasodifiy audit va «oltin to'plam».

Andoza: jamiyat_fikri / goku reputation-service (Stage-1 Algorithm Gate → Stage-2 AI Judge → Stage-3 Human Review).
LexSim'da:
  1) TIZIM — qoidalar: so'kinish, manbasiz modda, shaxsiy ma'lumot, majburiy qismlar (rubric/caselab/npc);
  2) AI — bandlar bo'yicha «ha/yo'q + iqtibos», case qoralamasi, qahramon javobi; o'zi «mentorga yuborish» sababini belgilaydi
     (iqtibos topilmadi, yurishlar kelishmadi, etika, chegaraga yaqin);
  3) MENTOR — shu yerda: navbat, qaror (tasdiqlash / tuzatish / rad), har qaror audit jurnalida.
     AI mentorga yubormagan ishlardan 3 % i tasodifiy auditga tushadi (AI «yaxshi» degan ishni ham kimdir ko'rib turadi).
     Mentor qarorlari AI bilan solishtiriladi → kelishuv (%) va Koen kappasi: AI qanchalik ishonchli ekanini o'lchaydi.
"""
import json
import random
import secrets
import sqlite3
import threading
import time

AUDIT_RATE = 0.03
KINDS = ("moot_verdict", "case", "solution", "npc_reply")
_db = None
_lock = threading.Lock()


class ReviewError(Exception):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def init(path):
    global _db
    _db = sqlite3.connect(path, check_same_thread=False, timeout=10)
    _db.execute("PRAGMA journal_mode=WAL")
    _db.executescript("""
    CREATE TABLE IF NOT EXISTS review_items(id TEXT PRIMARY KEY, kind TEXT, ref TEXT, reasons TEXT, payload TEXT,
        sample INTEGER, status TEXT, decision TEXT, note TEXT, reviewer TEXT, created REAL, decided REAL);
    CREATE INDEX IF NOT EXISTS review_status ON review_items(status, kind);
    CREATE UNIQUE INDEX IF NOT EXISTS review_ref ON review_items(kind, ref);
    CREATE TABLE IF NOT EXISTS review_audit(at REAL, item TEXT, action TEXT, reviewer TEXT, detail TEXT);
    """)
    _db.commit()


def enqueue(kind, ref, reasons, payload, sample=False):
    """AI «mentorga» degan yoki tasodifiy audit — navbatga (bir ish bir marta)."""
    if _db is None or kind not in KINDS or not ref:
        return None
    rid = "rv_" + secrets.token_hex(6)
    with _lock:
        cur = _db.execute("INSERT OR IGNORE INTO review_items VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                          (rid, kind, ref, json.dumps(reasons, ensure_ascii=False), json.dumps(payload, ensure_ascii=False),
                           1 if sample else 0, "pending", None, None, None, time.time(), None))
        if cur.rowcount:
            _db.execute("INSERT INTO review_audit VALUES (?,?,?,?,?)", (time.time(), rid, "enqueue", "system",
                                                                        json.dumps(reasons, ensure_ascii=False)))
        _db.commit()
    return rid if cur.rowcount else None


def route_moot(ref, explain, rnd=random.random):
    """2-bosqich natijasi: AI o'zi yuborgan (needsMentor) yoki 3 % tasodifiy audit."""
    if not explain:
        return None
    if explain.get("needsMentor"):
        return enqueue("moot_verdict", ref, [r.get("reason") for r in explain.get("routing", [])], explain)
    if rnd() < AUDIT_RATE:
        return enqueue("moot_verdict", ref, ["tasodifiy audit (3 %)"], explain, sample=True)
    return None


def _row(r, full=False):
    rid, kind, ref, reasons, payload, sample, status, decision, note, reviewer, created, decided = r
    out = {"id": rid, "kind": kind, "ref": ref, "reasons": json.loads(reasons or "[]"), "sample": bool(sample),
           "status": status, "note": note, "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(created))}
    if decision:
        out["decision"] = json.loads(decision)
    if full:
        out["payload"] = json.loads(payload or "null")
    return out


def queue(kind=None, status="pending", limit=100):
    q, a = "SELECT * FROM review_items WHERE status=?", [status]
    if kind:
        q += " AND kind=?"
        a.append(kind)
    return [_row(r) for r in _db.execute(q + " ORDER BY sample ASC, created ASC LIMIT ?", a + [limit])]


def get(rid):
    r = _db.execute("SELECT * FROM review_items WHERE id=?", (rid,)).fetchone()
    if not r:
        raise ReviewError(404, "review_not_found", "Topilmadi")
    return _row(r, full=True)


def decide(rid, body, reviewer="mentor"):
    """decision: approve (AI to'g'ri) | adjust (bandlarni tuzatish: {"items": {"claimant:F2": "no", ...}}) | reject."""
    if not isinstance(body, dict) or body.get("decision") not in ("approve", "adjust", "reject"):
        raise ReviewError(422, "validation_failed", "decision: approve | adjust | reject")
    items = body.get("items") if isinstance(body.get("items"), dict) else {}
    if body["decision"] == "adjust" and not items:
        raise ReviewError(422, "validation_failed", "adjust uchun items kerak: {\"claimant:F2\": \"yes\"|\"no\"}")
    if any(v not in ("yes", "no", "na") for v in items.values()):
        raise ReviewError(422, "validation_failed", "items qiymati: yes | no | na")
    note = (body.get("note") or "")[:1000] if isinstance(body.get("note"), str) else ""
    if body["decision"] == "reject" and not note:
        raise ReviewError(422, "validation_failed", "Rad etishda izoh majburiy")
    with _lock:
        r = _db.execute("SELECT status FROM review_items WHERE id=?", (rid,)).fetchone()
        if not r:
            raise ReviewError(404, "review_not_found", "Topilmadi")
        if r[0] != "pending":
            raise ReviewError(409, "already_decided", "Bu ish allaqachon ko'rib chiqilgan")
        dec = {"decision": body["decision"], "items": items}
        _db.execute("UPDATE review_items SET status=?, decision=?, note=?, reviewer=?, decided=? WHERE id=?",
                    ({"approve": "approved", "adjust": "adjusted", "reject": "rejected"}[body["decision"]],
                     json.dumps(dec, ensure_ascii=False), note or None, reviewer[:64], time.time(), rid))
        _db.execute("INSERT INTO review_audit VALUES (?,?,?,?,?)",
                    (time.time(), rid, body["decision"], reviewer[:64], json.dumps({"items": items, "note": note}, ensure_ascii=False)))
        _db.commit()
    return get(rid)


def stats():
    """AI va mentor kelishuvi (faqat moot bandlari): oltin to'plam. Kappa — Koen (ha/yo'q)."""
    rows = _db.execute("SELECT payload, decision, sample FROM review_items WHERE kind='moot_verdict' "
                       "AND status IN ('approved','adjusted')").fetchall()
    a = b = c = d = 0                                     # AI ha & mentor ha, AI ha & mentor yo'q, AI yo'q & ha, yo'q & yo'q
    per = {}
    for payload, decision, sample in rows:
        ex, dec = json.loads(payload or "{}"), json.loads(decision or "{}")
        fix = dec.get("items") or {}
        for side, sd in (ex.get("sides") or {}).items():
            for it in sd.get("items", []):
                if it.get("method") != "ai" or it.get("met") not in ("yes", "no"):
                    continue
                ai = it["met"] == "yes"
                hum = fix.get(f"{side}:{it['id']}", it["met"]) == "yes"
                p = per.setdefault(it["id"], [0, 0])
                p[0] += 1
                p[1] += ai == hum
                if ai and hum:
                    a += 1
                elif ai:
                    b += 1
                elif hum:
                    c += 1
                else:
                    d += 1
    n = a + b + c + d
    po = (a + d) / n if n else None
    pe = (((a + b) * (a + c) + (c + d) * (b + d)) / (n * n)) if n else None
    kappa = round((po - pe) / (1 - pe), 3) if n and pe is not None and pe < 1 else None
    counts = {k: v for k, v in _db.execute("SELECT status, COUNT(*) FROM review_items GROUP BY status")}
    return {"queue": counts, "goldItems": n, "agreement": round(po, 3) if po is not None else None, "kappa": kappa,
            "target": {"kappa": 0.61, "note": "Landis–Koch «sezilarli» darajasi; undan past — AI bahosi faqat mashq uchun"},
            "perItem": {k: {"n": v[0], "agreement": round(v[1] / v[0], 2)} for k, v in sorted(per.items())},
            "auditRate": AUDIT_RATE}
