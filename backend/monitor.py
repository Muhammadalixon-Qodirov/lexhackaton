"""LexSim kuzatuv (monitoring): har bir so'rov qaysi qismda qancha vaqt olganini o'lchaydi,
xizmatlar holatini va server yuklanishini tekshiradi, sekin joylar uchun tavsiya beradi.

Talaba matni saqlanmaydi — faqat vaqtlar, bosqich nomi va natija turi.
"""
import collections
import contextlib
import json
import os
import threading
import time
import urllib.error
import urllib.request
import uuid

_local = threading.local()
_lock = threading.Lock()
RECENT = collections.deque(maxlen=400)      # tugagan so'rovlar
INFLIGHT = {}                               # hozir bajarilayotganlar
COUNTERS = collections.Counter()            # llm_ok, llm_fallback, hints, sessions, errors ...
FALLBACK_REASONS = collections.Counter()
SERVICES = {}                               # nom -> {up, ms, error, checked}
SYSTEM = {"cpu": None, "load": None, "mem": None, "procs": [], "checked": None}
STARTED = time.time()


# ---------------------------------------------------------------- so'rov vaqtlari
def begin(kind, stage=None):
    ctx = {"id": uuid.uuid4().hex[:10], "kind": kind, "stage": stage, "t0": time.time(),
           "phase": "dvigatel", "phase_t0": time.time(), "parts": {"rag": 0.0, "llm": 0.0, "db": 0.0, "tts": 0.0, "stt": 0.0, "rerank": 0.0},
           "llm": None, "rag_inner": None}
    _local.ctx = ctx
    with _lock:
        INFLIGHT[ctx["id"]] = ctx
    return ctx


@contextlib.contextmanager
def part(name):
    ctx = getattr(_local, "ctx", None)
    if ctx is None:
        yield
        return
    prev = ctx["phase"]
    ctx["phase"], ctx["phase_t0"] = name, time.time()
    t = time.time()
    try:
        yield
    finally:
        ctx["parts"][name] = ctx["parts"].get(name, 0.0) + (time.time() - t) * 1000
        ctx["phase"], ctx["phase_t0"] = prev, time.time()


def note(**kw):
    ctx = getattr(_local, "ctx", None)
    if ctx is not None:
        ctx.update(kw)


def count(key, reason=None):
    with _lock:
        COUNTERS[key] += 1
        if reason:
            FALLBACK_REASONS[reason[:60]] += 1


def end(status=200):
    ctx = getattr(_local, "ctx", None)
    if ctx is None:
        return
    _local.ctx = None
    total = (time.time() - ctx["t0"]) * 1000
    p = ctx["parts"]
    rec = {"ts": round(ctx["t0"], 3), "kind": ctx["kind"], "stage": ctx["stage"], "status": status,
           "total": round(total), "rag": round(p["rag"]), "llm": round(p["llm"]), "db": round(p["db"]),
           "tts": round(p["tts"]), "stt": round(p["stt"]), "rerank": round(p["rerank"]),
           "engine": round(max(0.0, total - p["rag"] - p["llm"] - p["db"] - p["tts"] - p["stt"] - p["rerank"])),
           "rag_inner": ctx.get("rag_inner"), "llm_info": ctx.get("llm"), "voice": ctx.get("voice")}
    with _lock:
        INFLIGHT.pop(ctx["id"], None)
        RECENT.append(rec)
        if status >= 500:
            COUNTERS["errors"] += 1


# ---------------------------------------------------------------- xizmatlar va tizim
def _probe(url, headers=None, timeout=4):
    t = time.time()
    try:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            r.read(2000)
            return True, round((time.time() - t) * 1000), None
    except urllib.error.HTTPError as e:              # javob bor — xizmat tirik
        return e.code < 500, round((time.time() - t) * 1000), f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001
        return False, round((time.time() - t) * 1000), type(e).__name__


def _services_loop(targets):
    while True:
        for name, url, hdr in targets():
            up, ms, err = _probe(url, hdr)
            SERVICES[name] = {"up": up, "ms": ms, "error": err, "checked": time.time()}
        time.sleep(10)


PROC_NAMES = [("colibri", "LLM (Qwen colibri)"), ("tools/api.py", "RAG (bge-m3 + reranker)"),
              ("lexsim_server", "LexSim backend"), ("postgres", "PostgreSQL (RAG bazasi)"),
              ("mms", "TTS MMS"), ("uaz", "TTS Chatterbox"), ("chatterbox", "TTS Chatterbox"),
              ("kotib", "STT Kotib"), ("navai", "STT NavAI"), ("stt", "STT"), ("whisper", "STT")]


def _proc_label(pid):
    try:
        cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode("utf-8", "replace").lower()
    except OSError:
        return None
    for key, label in PROC_NAMES:
        if key in cmd:
            return label
    return (cmd.split(" ")[0].rsplit("/", 1)[-1] or "?")[:30]


def _system_loop():
    tck = os.sysconf("SC_CLK_TCK")
    page = os.sysconf("SC_PAGE_SIZE")
    ncpu = os.cpu_count() or 1
    prev_cpu, prev_proc, prev_t = None, {}, time.time()
    labels = {}
    while True:
        try:
            v = [int(x) for x in open("/proc/stat").readline().split()[1:]]
            idle, tot = v[3] + v[4], sum(v)
            if prev_cpu:
                d = tot - prev_cpu[1]
                SYSTEM["cpu"] = round(100 * (1 - (idle - prev_cpu[0]) / d), 1) if d else 0
            prev_cpu = (idle, tot)
            SYSTEM["load"] = [float(x) for x in open("/proc/loadavg").read().split()[:3]]
            mi = {}
            for line in open("/proc/meminfo"):
                k, val = line.split(":")
                mi[k] = int(val.split()[0]) // 1024
            SYSTEM["mem"] = {"total_mb": mi["MemTotal"], "avail_mb": mi["MemAvailable"],
                             "used_pct": round(100 * (1 - mi["MemAvailable"] / mi["MemTotal"]), 1)}
            now, cur, groups = time.time(), {}, {}
            dt = now - prev_t
            for pid in os.listdir("/proc"):
                if not pid.isdigit():
                    continue
                try:
                    st = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()
                    ticks = int(st[11]) + int(st[12])
                    rss = int(st[21]) * page // (1024 * 1024)
                except (OSError, IndexError, ValueError):
                    continue
                cur[pid] = ticks
                if pid in prev_proc and dt > 0:
                    pct = 100 * (ticks - prev_proc[pid]) / tck / dt
                    if pct > 0.5 or rss > 500:
                        if pid not in labels:
                            labels[pid] = _proc_label(pid)
                        g = groups.setdefault(labels[pid] or "?", {"name": labels[pid] or "?", "cpu": 0.0, "rss_mb": 0, "n": 0})
                        g["cpu"] += pct
                        g["rss_mb"] += rss
                        g["n"] += 1
            prev_proc, prev_t = cur, now
            labels = {p: labels[p] for p in labels if p in cur}
            procs = sorted(groups.values(), key=lambda g: -g["cpu"])[:8]
            for g in procs:
                g["cpu"] = round(g["cpu"], 1)
                g["cores"] = round(g["cpu"] / 100, 1)
            SYSTEM["procs"], SYSTEM["ncpu"], SYSTEM["checked"] = procs, ncpu, now
        except Exception as e:  # noqa: BLE001
            SYSTEM["error"] = repr(e)
        time.sleep(3)


def start(service_targets):
    threading.Thread(target=_services_loop, args=(service_targets,), daemon=True).start()
    threading.Thread(target=_system_loop, daemon=True).start()


# ---------------------------------------------------------------- statistika va tavsiyalar
def _pct(xs, q):
    if not xs:
        return None
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(q * (len(xs) - 1))))]


def stats(settings):
    now = time.time()
    with _lock:
        recent = list(RECENT)
        inflight = [{"kind": c["kind"], "stage": c["stage"], "phase": c["phase"],
                     "elapsed_ms": round((now - c["t0"]) * 1000), "phase_ms": round((now - c["phase_t0"]) * 1000)}
                    for c in INFLIGHT.values()]
        counters, reasons = dict(COUNTERS), FALLBACK_REASONS.most_common(5)
    muts = [r for r in recent if r["kind"] in ("turns", "interactions", "finish", "documents", "tts", "stt")]
    comps = {}
    grand = sum(r["total"] for r in muts) or 1
    for c in ("rag", "llm", "engine", "db", "tts", "stt", "rerank"):
        xs = [r[c] for r in muts if r[c] > 0]
        comps[c] = {"calls": len(xs), "avg": round(sum(xs) / len(xs)) if xs else None, "p50": _pct(xs, .5),
                    "p95": _pct(xs, .95), "max": max(xs) if xs else None,
                    "share": round(100 * sum(r[c] for r in muts) / grand, 1)}
    tot = [r["total"] for r in muts]
    vo = [r["voice"] for r in muts if r.get("voice")]
    voice = {"tts_cache_hits": sum(1 for v in vo if v.get("cache")), "tts_calls": sum(1 for v in vo if v["type"] == "tts"),
             "stt_calls": sum(1 for v in vo if v["type"] == "stt"),
             "stt_rtf": round(sum(v["ms"] / 1000 / v["seconds"] for v in vo if v["type"] == "stt" and v.get("seconds"))
                              / max(1, sum(1 for v in vo if v["type"] == "stt" and v.get("seconds"))), 1) or None}
    by_stage = {}
    for r in muts:
        if r["kind"] != "turns":
            continue
        b = by_stage.setdefault(r["stage"] or "?", {"n": 0, "sum": 0, "max": 0, "rag": 0, "llm": 0})
        b["n"] += 1
        b["sum"] += r["total"]
        b["max"] = max(b["max"], r["total"])
        b["rag"] += r["rag"]
        b["llm"] += r["llm"]
    stages = [{"stage": k, "n": v["n"], "avg": round(v["sum"] / v["n"]), "max": v["max"],
               "rag_avg": round(v["rag"] / v["n"]), "llm_avg": round(v["llm"] / v["n"])} for k, v in by_stage.items()]
    stages.sort(key=lambda x: -x["avg"])
    llm_infos = [r["llm_info"] for r in muts if r.get("llm_info")]
    ttft = [i["ttft_ms"] for i in llm_infos if i.get("ttft_ms")]
    last5 = [r for r in muts if now - r["ts"] < 300]
    return {
        "now": now, "uptime_s": round(now - STARTED), "settings": settings,
        "requests": {"total": len(muts), "last5min": len(last5), "p50": _pct(tot, .5), "p95": _pct(tot, .95),
                     "max": max(tot) if tot else None},
        "components": comps, "stages": stages, "voice": voice, "inflight": inflight,
        "llm": {"ok": counters.get("llm_ok", 0), "fallback": counters.get("llm_fallback", 0),
                "ttft_p50": _pct(ttft, .5), "reasons": reasons},
        "counters": counters, "services": SERVICES, "system": SYSTEM,
        "recent": recent[-60:][::-1],
        "advice": advice(comps, counters, ttft, llm_infos, settings, voice),
    }


def advice(comps, counters, ttft, llm_infos, settings, voice=None):
    out = []
    llm, rag, eng, db = comps["llm"], comps["rag"], comps["engine"], comps["db"]
    if llm["calls"] and llm["share"] >= 40:
        out.append({"level": "warn", "part": "LLM",
                    "text": f"Vaqtning {llm['share']}% LLM'da (o'rtacha {llm['avg'] / 1000:.0f} s, p95 {llm['p95'] / 1000:.0f} s).",
                    "fix": "Variantlar: (1) LLM'ni o'chirib, shablon gaplar bilan tez ishlash; (2) kutish vaqtini 60 s ga tushirish — "
                           "sekin javob o'rniga shablon chiqadi; (3) tashqi API (Claude) yoki GPU'li server — 1–3 s."})
    if ttft and llm_infos:
        tot = [i["ms"] for i in llm_infos if i.get("ms")]
        if tot and _pct(ttft, .5) / max(1, _pct(tot, .5)) > 0.7:
            out.append({"level": "info", "part": "LLM",
                        "text": f"LLM vaqtining katta qismi birinchi tokengacha ({_pct(ttft, .5) / 1000:.0f} s) — model promptni o'qiyapti.",
                        "fix": "Promptni qisqartirish (roles.json dagi uslub va taqiqlar) yoki tezroq model. Javob uzunligi deyarli ta'sir qilmaydi."})
    n_llm = counters.get("llm_ok", 0) + counters.get("llm_fallback", 0)
    if n_llm >= 3 and counters.get("llm_fallback", 0) / n_llm > 0.3:
        out.append({"level": "warn", "part": "LLM sifati",
                    "text": f"LLM javoblarining {100 * counters['llm_fallback'] // n_llm}% tekshiruvdan o'tmadi — shablon ishlatildi.",
                    "fix": "Sabablar ro'yxatiga qarang. Vaqt tugasa — kutish vaqtini oshiring; mazmun xato bo'lsa — namuna/promptni tuzating yoki modelni almashtiring."})
    if rag["calls"] and rag["p95"] and rag["p95"] > 6000:
        out.append({"level": "warn", "part": "RAG",
                    "text": f"RAG sekin: p95 {rag['p95'] / 1000:.1f} s (o'rtacha {rag['avg'] / 1000:.1f} s).",
                    "fix": "Variantlar: (1) lexsim-rag xizmatida LEXSIM_RERANK_N=8 → 4; (2) RAG'ni o'chirish — modda tekshiruvi bazadagi "
                           "ro'yxat bo'yicha ishlayveradi, faqat hisobotdagi qo'shimcha manbalar kamayadi; (3) GPU."})
    if eng["p95"] and eng["p95"] > 300:
        out.append({"level": "info", "part": "Dvigatel", "text": f"Dvigatel p95 {eng['p95']} ms — kutilganidan sekin.",
                    "fix": "Odatda <50 ms. Server CPU yuklanishini tekshiring."})
    if db["p95"] and db["p95"] > 200:
        out.append({"level": "info", "part": "Saqlash", "text": f"SQLite saqlash p95 {db['p95']} ms.",
                    "fix": "Disk band. Sessiya ko'p bo'lsa — eski sessiyalarni tozalash yoki PostgreSQL'ga o'tish."})
    tts, stt = comps["tts"], comps["stt"]
    if tts["calls"] and tts["p50"] and tts["p50"] > 5000:
        out.append({"level": "warn", "part": "TTS",
                    "text": f"Ovozlashtirish sekin: p50 {tts['p50'] / 1000:.0f} s ({settings.get('tts')}).",
                    "fix": "Variantlar: (1) TTS = MMS (≈2 s); (2) Chatterbox'ni faqat shablon gaplar uchun oldindan yozib keshlash; "
                           "(3) brauzerning o'z ovozi (speechSynthesis) — o'zbekcha sifati past."})
    if stt["calls"] and stt["p50"] and stt["p50"] > 8000:
        rtf = (voice or {}).get("stt_rtf")
        out.append({"level": "warn", "part": "STT",
                    "text": f"Nutqni tanish sekin: p50 {stt['p50'] / 1000:.0f} s ({settings.get('stt')}"
                            + (f", 1 s audioga {rtf} s" if rtf else "") + ").",
                    "fix": "Variantlar: (1) NavAI ↔ Kotib almashtirib solishtirish; (2) talaba gapini 10–15 s bilan cheklash; "
                           "(3) whisper-small yoki faster-whisper (int8) — 3–5 barobar tez; (4) matn kiritishni asosiy qoldirish."})
    cpu = SYSTEM.get("cpu")
    if cpu is not None and cpu > 90:
        top = SYSTEM["procs"][0]["name"] if SYSTEM.get("procs") else "?"
        out.append({"level": "warn", "part": "Server CPU", "text": f"CPU {cpu}% band, eng ko'p: {top}.",
                    "fix": "Chatterbox va STT bir vaqtda ishlamasin; sinov paytida keraksiz xizmatlarni to'xtating."})
    mem = SYSTEM.get("mem")
    if mem and mem["used_pct"] > 90:
        out.append({"level": "warn", "part": "RAM", "text": f"RAM {mem['used_pct']}% band.", "fix": "Keraksiz modellarni to'xtating."})
    for name, s in SERVICES.items():
        if not s["up"]:
            out.append({"level": "error", "part": name, "text": f"{name} javob bermayapti ({s['error']}).",
                        "fix": "systemctl status bilan tekshiring. Backend uni ishlatsa — shablonga o'tadi, lekin sifat pasayadi."})
    if not settings.get("llm"):
        out.append({"level": "info", "part": "LLM", "text": "LLM o'chiq — raqib shablon gaplar bilan gapiradi.", "fix": ""})
    if not out:
        out.append({"level": "ok", "part": "Hammasi", "text": "Sekin joy topilmadi.", "fix": ""})
    return out


def load_json(path, default):
    try:
        return json.load(open(path))
    except (OSError, ValueError):
        return default
