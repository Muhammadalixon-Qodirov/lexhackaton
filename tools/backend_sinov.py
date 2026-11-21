#!/usr/bin/env python3
"""LexSim backend v1 — to'liq sud majlisini oxirigacha o'tkazuvchi sinov (faqat standart kutubxona).

    python3 tools/backend_sinov.py                 # http://192.168.88.110:8100, ikkala rol
    python3 tools/backend_sinov.py http://host:8100 sud-ijara-javobgar
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
import uuid
from http.cookiejar import CookieJar

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://192.168.88.110:8100").rstrip("/") + "/api/v1"
ONLY = sys.argv[2] if len(sys.argv) > 2 else None

SCRIPTS = {
    "sud-ijara-davogar": [
        "Hurmatli sud, da'vogar vakiliman, vakolatimni tasdiqlovchi ishonchnomani taqdim etaman.",
        "Hurmatli sud, rad bildirmaymiz.",
        "Hurmatli sud, huquqlarimiz tushunarli.",
        "Hurmatli sud, iltimosnomamiz yo'q.",
        "Hurmatli sud, 32-P-sonli ijara shartnomasi bo'yicha javobgar ijara haqini to'lamagan. FK 544-moddaga va "
        "shartnomaning 6.4-bandiga asosan 25 620 433,19 so'm asosiy qarz va 8.5-band bo'yicha penya undirishni so'raymiz.",
        "Hurmatli sud, javobgar joydan foydalangan va hisob-fakturalarni imzolagan, bu FK 544-moddaga ko'ra ijara haqini "
        "to'lash majburiyatini tasdiqlaydi.",
        "Hurmatli sud, penya shartnomaning 8.5-bandida yozma kelishilgan, javobgar to'lovni muddatida qilmagan.",
        "Hurmatli sud, qo'shimcha materiallarimiz yo'q.",
        "Hurmatli sud! Sudda tekshirilgan ijara shartnomasi va hisob-fakturalar asosida FK 544-moddaga ko'ra asosiy qarz "
        "va penyani undirishni so'raymiz.",
    ],
    "sud-ijara-javobgar": [
        "Hurmatli sud, javobgar vakiliman, ishonchnomamni taqdim etaman.",
        "Hurmatli sud, rad bildirmayman.",
        "Hurmatli sud, tushunarli.",
        "Hurmatli sud, iltimosnomam yo'q.",
        "Hurmatli sud, da'voni qisman tan olmaymiz: obyekt topshirish dalolatnomasi bilan topshirilmagan, FK 578-modda "
        "talab qilgan hujjat yo'q.",
        "Hurmatli sud, FK 326-moddaga asosan penyani kamaytirishni so'rab iltimosnoma beraman: penya nomutanosib, "
        "mijoz uch oy foydalangan va moliyaviy ahvoli og'ir.",
        "Hurmatli sud, qo'shimcha materiallar yo'q.",
        "Hurmatli sud! Tekshirilgan shartnoma va hisob-fakturalar asosida FK 326-moddaga ko'ra penyani kamaytirishni so'rayman.",
    ],
}


def call(op, method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method, headers={"Content-Type": "application/json"},
                                 data=json.dumps(body).encode() if body is not None else None)
    t = time.time()
    try:
        with op.open(req, timeout=300) as r:
            return r.status, json.loads(r.read()), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), time.time() - t


APOS = re.compile(r"[A-Za-zʻʼ][\'’‘][A-Za-z]")
EMO = {"neutral", "impatient", "upset", "confused", "uncertain", "calm", "reassured"}
PREFIX = re.compile(r"^(Kotib|Sudya|Da.vogar vakili|Javobgar vakili)\s*:")


def texts(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, list):
        for v in x:
            yield from texts(v)
    elif isinstance(x, dict):
        for v in x.values():
            yield from texts(v)


def check_snapshot(sn):
    """Frontend kontrakti (COURT_BACKEND.md §8.2) — Zod o'rniga Python tekshiruvi."""
    sc = sn["scenario"]
    assert isinstance(sc["durationMinutes"], str), "durationMinutes satr emas"
    assert set(sc["briefing"]) >= {"workplace", "position", "authority", "task"}, "briefing obyekt emas"
    assert sc["roomId"] == "court-economic", sc["roomId"]
    assert isinstance(sn["options"], list), "options yo'q"
    for t in sn["turns"]:
        if t["speaker"] == "npc":
            assert t.get("role") in ("judge", "secretary", "opponent", "witness", "expert"), ("role", t)
            assert t.get("emotion") in EMO, ("emotion", t)
            assert not PREFIX.match(t["text"]), ("prefiks", t["text"][:40])
    bad = [x for x in texts(sn) if APOS.search(x)]
    assert not bad, ("imlo", bad[:2])


def wait_pending(op, sid, r, seq):
    """202 bo'lsa — /events?after=N orqali raqib javobini kutish."""
    events = list(r["events"])
    while r["snapshot"].get("pending"):
        time.sleep(1.5)
        st, r, _ = call(op, "GET", f"/sessions/{sid}/events?after={events[-1]['sequence']}")
        assert st == 200, (st, r)
        events += r["events"]
    return events, r["snapshot"]


def run(scid):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    print(f"\n=== {scid} ===")
    st, r, _ = call(op, "POST", "/sessions", {"scenarioId": scid, "mode": "tutorial"})
    assert st == 200, (st, r)
    check_snapshot(r["snapshot"])
    sid = r["snapshot"]["sessionId"]
    print("sessiya:", sid, "| holat:", r["snapshot"]["status"])
    for a in ("start", "sit-at-desk", "stand"):
        st, r, dt = call(op, "POST", f"/sessions/{sid}/interactions", {"action": a, "clientActionId": uuid.uuid4().hex})
        assert st == 200, (st, r)
    for t in r["snapshot"]["turns"]:
        print(f"  [{t.get('role') or t['speaker']}] {t['text'][:110]}", t.get("scene") or "")
    st, h, _ = call(op, "GET", f"/sessions/{sid}/hint")
    assert st == 200 and h["hint"]["sources"], h
    seq = r["snapshot"]["sequence"]
    for text in SCRIPTS[scid]:
        cid = uuid.uuid4().hex
        st, r, dt = call(op, "POST", f"/sessions/{sid}/turns", {"text": text, "clientTurnId": cid})
        assert st in (200, 202), (st, r)
        first = r
        events, snap = wait_pending(op, sid, r, seq) if st == 202 else (r["events"], r["snapshot"])
        seqs = [e["sequence"] for e in events]
        assert seqs == list(range(seq + 1, seq + 1 + len(seqs))), "sequence uzluksiz emas"
        seq = snap["sequence"]
        check_snapshot(snap)
        print(f"\nTALABA ({st}, {dt:.1f} s{'' if st == 200 else ', keyin kutildi'}): {text[:80]}")
        for e in events:
            if e["type"] == "dialogue.npcTurn":
                t = e["payload"]["turn"]
                print(f"  -> [{t.get('role') or t['speaker']}] {t['text'][:120]}",
                      ("| fakt: " + ",".join(e["payload"]["revealedFactIds"])) if e["payload"]["revealedFactIds"] else "")
        last_cid, last_text, last_first, last_st = cid, text, first, st
    for _ in range(2):
        st2, r2, _ = call(op, "POST", f"/sessions/{sid}/turns", {"text": last_text, "clientTurnId": last_cid})
        assert st2 == last_st and r2 == last_first, "idempotentlik ishlamadi"
    st, r, _ = call(op, "POST", f"/sessions/{sid}/finish", {"clientActionId": uuid.uuid4().hex})
    assert st == 200 and r["snapshot"]["status"] == "report-ready", (st, r)
    st, rep, _ = call(op, "GET", f"/sessions/{sid}/report")
    assert st == 200, (st, rep)
    rep = rep["report"]
    bad = [x for x in texts(rep) if APOS.search(x)]
    assert not bad, ("hisobot imlosi", bad[:2])
    for f in rep["feedback"]:
        for src in f["sources"]:
            assert src["officialUrl"].startswith("https://lex.uz/"), src
    assert isinstance(rep.get("decisions"), list) and "hints" in rep, "decisions/hints yo'q"
    print(f"\nNATIJA: {rep['scoreTotal']}/100 — {rep['outcome']['title']} | maslahat: {rep['hints']}")
    for c in rep["criteria"]:
        print(f"  {c['id']:14} {c['score']:>2}/{c['max']}  {c['explanation'][:90]}")
    for d in rep["decisions"]:
        if d["tone"] in ("bad", "info") or d["points"]:
            print(f"  [{d['tone']}] {d['at']}s −{d['points']}  {(d['why'] or '')[:70]}  {d['article'] or ''}")
    st, r, _ = call(urllib.request.build_opener(), "GET", f"/sessions/{sid}")
    assert st == 403, st
    print("kontrakt: OK | 403: OK | idempotentlik (3x): OK | sequence: OK | imlo: OK | manbalar: OK")


for scid in ([ONLY] if ONLY else SCRIPTS):
    run(scid)
print("\nHammasi muvaffaqiyatli.")
