"""Ovoz: serverdagi Gradio TTS/STT xizmatlarini backend orqali chaqirish (faqat standart kutubxona + ffmpeg).

TTS: matn -> WAV (MMS 7008 tez, Chatterbox 7002 tabiiyroq lekin sekin). Natija keshlanadi —
     sudyaning shablon gaplari ikkinchi marta darhol chiqadi.
STT: brauzer audiosi (webm/ogg/wav) -> ffmpeg bilan 16 kHz mono WAV -> NavAI 7003 yoki Kotib 7009.
"""
import collections
import hashlib
import json
import os
import re
import subprocess
import tempfile
import threading
import urllib.parse
import urllib.request
import time
import uuid
import wave
import io
from pathlib import Path

TTS = {"mms": {"port": 7008, "args": lambda t: [t, True], "timeout": 60},
       "chatterbox": {"port": 7002, "args": lambda t: [t], "timeout": 150},
       "chatterbox_gpu": {"port": 8092, "timeout": 60}}      # GPU kompyuter, teskari SSH tunnel orqali
CB_GPU = os.environ.get("LEXSIM_CHATTERBOX_GPU_URL", "http://127.0.0.1:8092").rstrip("/")
try:
    _VJ = json.load(open(Path(__file__).resolve().parent / "voices.json", encoding="utf-8"))
    CB_MAP = _VJ["chatterbox_gpu"]
    CB_FILTER = _VJ.get("chatterbox_gpu_filter", {})      # rol -> ffmpeg filtri (klon ustidan), masalan bitta klon ikki rolda
except (OSError, ValueError, KeyError):
    CB_MAP, CB_FILTER = {}, {}
_cb_lock = threading.Lock()              # /use_voice butun ilova uchun umumiy — use_voice+speak birga, navbat bilan
_cb_names = {"set": set(), "at": 0.0}
STT = {"navai": {"port": 7003, "timeout": 90}, "kotib": {"port": 7009, "timeout": 90},
       # GPU kompyuter (teskari SSH tunnel 8093): 5 s audio ~1 s. Model almashtirish ~5 s, shuning uchun bitta modelda qolamiz.
       "gpu": {"port": 8093, "timeout": 30, "model": "Kotib (tinish belgilari bilan)", "fallback": "kotib"},
       # 2026-11-21 o'lchovi (10 ta ma'lum matnli audio): Kotib WER 13 %, rubaistt_v2 26 % — asosiy model Kotib.
       # Modellarni almashtirish GPU'da ~20 s oladi: jonli so'rovlarda faqat bitta model ishlatilsin.
       "gpu_rubai": {"port": 8093, "timeout": 30, "model": "rubaistt_v2 (eng aniq)", "fallback": "kotib"}}
STT_MAX_S = 60          # talaba bir so'zda shuncha gapira oladi («Bahs»: 60 s gacha); avval 15 s da kesilardi
STT_CHUNK_S = 25        # model uchun bo'lak: jim joydan bo'linadi (Whisper turidagi modellar ~30 s oynada ishlaydi)
HOST = os.environ.get("LEXSIM_VOICE_HOST", "127.0.0.1")
CACHE = Path(os.environ.get("LEXSIM_TTS_CACHE", str(Path(__file__).resolve().parent / "tts_cache")))
CACHE.mkdir(exist_ok=True)
STATS = {"tts_cache_hit": 0, "tts_cache_miss": 0, "gpu_ok": 0, "gpu_fallback": 0}
# Frontend ovozlari (COURT_BACKEND.md §4.4). Serverda bitta o'zbek ovozi (MMS) bor — qolganlari undan
# rubberband bilan (balandlik/tezlik) hosil qilinadi. Chiqish: MP3, 24 kHz, mono.
VOICES = {
    "elder_m": "rubberband=pitch=0.86:tempo=0.92",     # sudya: past, sokin, biroz sekin
    "male": None,                                        # erkak taraf / guvoh: asl MMS ovozi
    "female": "rubberband=pitch=1.32",                   # kotib
    "female_alt": "rubberband=pitch=1.42:tempo=1.04",    # raqib vakili (ayol), ohangi balandroq
}
_locks = {7008: threading.Lock(), 7002: threading.Lock(), 7003: threading.Lock(), 7009: threading.Lock(),
          8093: threading.Lock()}
# har bir model bir vaqtda bitta so'rov — CPU to'lib qolmasin, lekin MMS sekin STT ni kutmaydi
SPEAKER = re.compile(r"(?m)^\s*(Kotib|Sudya|Da'vogar vakili|Javobgar vakili)\s*:\s*")


class VoiceError(Exception):
    pass


# "O'chirgich" (circuit breaker): GPU xizmati javob bermasa, 30 s davomida qayta urinmaymiz — har so'rov 5 s kutmasin
_down = {}
BREAK_S = 30


def gpu_down(name):
    return time.time() < _down.get(name, 0)


def gpu_failed(name):
    _down[name] = time.time() + BREAK_S


def _gradio(port, api, data, timeout, base=None):
    base = (base or f"http://{HOST}:{port}") + "/gradio_api"
    req = urllib.request.Request(f"{base}/call/{api}", data=json.dumps({"data": data}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        eid = json.loads(r.read())["event_id"]
    event, result = None, None
    with urllib.request.urlopen(f"{base}/call/{api}/{eid}", timeout=timeout) as r:
        for raw in r:
            line = raw.decode("utf-8", "replace").rstrip("\n")
            if line.startswith("event:"):
                event = line[6:].strip()
            elif line.startswith("data:") and event in ("complete", "error"):
                payload = line[5:].strip()
                if event == "error":
                    raise VoiceError(f"Gradio xatosi: {payload[:200]}")
                result = json.loads(payload, strict=False)
                break
    if result is None:
        raise VoiceError("Gradio javob bermadi")
    return result


def clean_text(text):
    """Turn matnidan «Kotib:», «Javobgar vakili:» kabi belgilarni olib tashlash."""
    text = SPEAKER.sub("", text).replace("ʻ", "'").replace("ʼ", "'")    # MMS lotin->kirill o'girgichi ' ni kutadi
    return re.sub(r"\s+", " ", text).strip()[:700]


def mp3_duration_ms(mp3):
    """MP3 davomiyligi: kadrlar sarlavhasidan (MPEG-1/2 Layer III), ID3 ni o'tkazib."""
    i, n, dur = 0, len(mp3), 0.0
    if mp3[:3] == b"ID3" and n > 10:
        i = 10 + ((mp3[6] & 0x7f) << 21 | (mp3[7] & 0x7f) << 14 | (mp3[8] & 0x7f) << 7 | (mp3[9] & 0x7f))
    rates = {3: (44100, 48000, 32000), 2: (22050, 24000, 16000), 0: (11025, 12000, 8000)}
    br1 = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320]
    br2 = [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]
    while i + 4 <= n:
        if mp3[i] != 0xFF or (mp3[i + 1] & 0xE0) != 0xE0:
            i += 1
            continue
        ver, bi, si, pad = (mp3[i + 1] >> 3) & 3, mp3[i + 2] >> 4, (mp3[i + 2] >> 2) & 3, (mp3[i + 2] >> 1) & 1
        if ver == 1 or bi in (0, 15) or si == 3:
            i += 1
            continue
        sr = rates[ver][si]
        br = (br1 if ver == 3 else br2)[bi] * 1000
        spf = 1152 if ver == 3 else 576
        size = int((spf // 8) * br / sr) + pad
        if size <= 0:
            break
        dur += spf / sr
        i += size
    return round(dur * 1000)


def word_timings(text, dur_ms):
    """Taxminiy so'z vaqtlari (MMS/Chatterbox so'z chegarasini bermaydi): davomiylik harf soniga mutanosib,
    boshida/oxirida ~5% jimlik. Lab-sinxron uchun yetarli taxmin."""
    words = re.findall(r"\S+", clean_text(text))
    if not words or dur_ms <= 0:
        return []
    lead = dur_ms * 0.05
    span = dur_ms * 0.9
    weights = [len(w) + 1 for w in words]
    tot, t, out = sum(weights), lead, []
    for w in weights:
        d = span * w / tot
        out.append([round(t), round(t + d * 0.92)])
        t += d
    return out


def to_mp3(wav, voice, af=None):
    if voice not in VOICES:
        raise VoiceError("Ovoz turi noto'g'ri")
    af = ",".join(x for x in ((VOICES[voice] if af is None else af), "aresample=24000") if x)
    p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "wav", "-i", "pipe:0", "-af", af,
                        "-ac", "1", "-ar", "24000", "-c:a", "libmp3lame", "-b:a", "64k", "-f", "mp3", "pipe:1"],
                       input=wav, capture_output=True, timeout=30)
    if p.returncode != 0 or not p.stdout:
        raise VoiceError("MP3 kodlashda xato")
    return p.stdout


def cb_voices(force=False):
    """GPU Chatterbox'dagi saqlangan ovozlar (60 s kesh). /lambda ro'yxatni yangilaydi, lekin faol ovozni ham
    o'zgartiradi — shuning uchun ovoz qulfi ostida chaqiriladi (tts_gpu har gapdan oldin use_voice qiladi)."""
    if force or time.time() - _cb_names["at"] > 60:
        if gpu_down("chatterbox"):
            raise VoiceError("Chatterbox GPU vaqtincha ishlamayapti")
        try:
            with _cb_lock:
                res = _gradio(0, "lambda", [], 15, base=CB_GPU)
        except Exception:
            gpu_failed("chatterbox")
            raise
        upd = res[0] if isinstance(res, list) and res else {}
        names = {ch[0] if isinstance(ch, list) else ch for ch in (upd.get("choices") or [])}
        _cb_names.update(set=names, at=time.time())
    return _cb_names["set"]


def _join_wavs(parts):
    out, params = io.BytesIO(), None
    with wave.open(out, "wb") as w:
        for b in parts:
            with wave.open(io.BytesIO(b)) as r:
                if params is None:
                    params = r.getparams()
                    w.setparams(params)
                w.writeframes(r.readframes(r.getnframes()))
    return out.getvalue()


def tts_gpu(text, voice):
    """(wav, native). Uzun matn gaplarga bo'linadi (bitta gap ~6–7 s)."""
    name = CB_MAP.get(voice)
    native = bool(name) and name in cb_voices()
    sents = [x for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()] or [text]
    parts = []
    if gpu_down("chatterbox"):
        raise VoiceError("Chatterbox GPU vaqtincha ishlamayapti")
    try:
        return _tts_gpu_run(name, native, sents, parts)
    except Exception:
        gpu_failed("chatterbox")
        raise


def _tts_gpu_run(name, native, sents, parts):
    with _cb_lock:
        _gradio(0, "use_voice", [name if native else "Standart ovoz"], 15, base=CB_GPU)
        for sent in sents:
            res = _gradio(0, "speak", [sent], TTS["chatterbox_gpu"]["timeout"], base=CB_GPU)
            f = res[0] if isinstance(res, list) else res
            parts.append(_cb_file(f))
    return (_join_wavs(parts) if len(parts) > 1 else parts[0]), native


def _cb_file(f):
    """Gradio fayli. GPU kompyuter Windows: path = C:\\Users\\..., shuning uchun tayyor url (shu tunnel manzilida
    bo'lsa) ishlatiladi, aks holda yo'l URL-kodlanadi."""
    url = f.get("url") if isinstance(f, dict) else None
    if not (url and url.startswith(CB_GPU + "/")):
        url = f"{CB_GPU}/gradio_api/file=" + urllib.parse.quote(f["path"], safe="/:")
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()


def cb_clone(audio, name):
    """Ovoz namunasini GPU Chatterbox'da klonlab saqlash."""
    if not re.fullmatch(r"[\w-]{2,40}", name):
        raise VoiceError("Ovoz nomi noto'g'ri")
    wav = _to_wav(audio, sr=24000, max_s=12)        # klonlash uchun 24 kHz, 12 s gacha (Chatterbox tavsiyasi 5–10 s)
    b = "----lexsim" + uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"ref.wav\"\r\n"
            f"Content-Type: audio/wav\r\n\r\n").encode() + wav + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request(f"{CB_GPU}/gradio_api/upload", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        path = json.loads(r.read())[0]
    with _cb_lock:
        res = _gradio(0, "clone", [{"path": path, "meta": {"_type": "gradio.FileData"}}, name], 60, base=CB_GPU)
    cb_voices(force=True)
    return res[-1] if isinstance(res, list) else str(res)


_ALIAS = re.compile(r"^[a-z][a-z0-9_]{1,23}$")


def resolve_voice(name):
    """Palitra nomi (judge_m2, lawyer_f1, secretary_f1 ...) -> mavjud ovoz. Palitra klonlanguncha vaqtinchalik.
    Jins nomdagi belgidan olinadi (_m / _f); noma'lum bo'lsa — None (422)."""
    if name in VOICES:
        return name
    if not isinstance(name, str) or not _ALIAS.match(name):
        return None
    m = re.search(r"_(m|f)\d*$", name)
    if not m:
        return None
    role = name.split("_", 1)[0]
    if m.group(1) == "f":
        return "female_alt" if role in ("lawyer", "opponent", "advocate", "witness", "expert") else "female"
    return "elder_m" if role in ("judge", "sudya") else "male"


def cached_file(text, voice="male"):
    """Keshdagi tayyor MP3 yo'li (avval klon, keyin MMS) yoki None. Yangi ovoz yaratmaydi."""
    t = clean_text(text)
    for k in ([f"gpu\0{voice}\0{n}\0{t}" for n in (True, False)] + [f"mms\0{voice}\0{t}"]):
        f = CACHE / (hashlib.sha256(k.encode()).hexdigest() + ".mp3")
        if f.is_file():
            return f
    return None


def cached(text, voice="male", gpu_only=False):
    """Gap keshda bormi (klonlangan ovozda; gpu_only=False bo'lsa MMS ham hisoblanadi). Yangi ovoz yaratmaydi."""
    t = clean_text(text)
    keys = [hashlib.sha256(f"gpu\0{voice}\0{n}\0{t}".encode()).hexdigest() + ".mp3" for n in (True, False)]
    if not gpu_only:
        keys.append(hashlib.sha256(f"mms\0{voice}\0{t}".encode()).hexdigest() + ".mp3")
    return any((CACHE / k).exists() for k in keys)


def tts_mp3(text, voice="male", engine="mms", strict=False):
    """(mp3_bytes, cache_hit). Asosiy WAV va har bir ovoz MP3'i alohida keshlanadi.
    chatterbox_gpu ishlamasa — avtomatik MMS (sifat pasayadi, lekin ovoz bor)."""
    text = clean_text(text)
    if engine == "chatterbox_gpu":
        try:
            native = CB_MAP.get(voice) in cb_voices()
            key = CACHE / (hashlib.sha256(f"gpu\0{voice}\0{native}\0{text}".encode()).hexdigest() + ".mp3")
            if key.exists():
                STATS["tts_cache_hit"] += 1
                return key.read_bytes(), True
            STATS["tts_cache_miss"] += 1
            wav, native = tts_gpu(text, voice)
            mp3 = to_mp3(wav, "male" if native else voice,       # klonlangan ovozga filtr kerak emas,
                         af=CB_FILTER.get(voice) if native else None)   # bitta klon ikki rolda bo'lsa — ohang farqi
            tmp = key.with_suffix(".tmp")
            tmp.write_bytes(mp3)
            tmp.replace(key)
            STATS["gpu_ok"] += 1
            return mp3, False
        except Exception:  # noqa: BLE001
            if strict:                                   # oldindan render: MMS bilan almashtirmaymiz, keyin qayta urinamiz
                raise
            STATS["gpu_fallback"] += 1
            engine = "mms"
    for native in (True, False):                 # oldindan Chatterbox'da render qilingan bo'lsa — o'sha (sifatliroq)
        gk = CACHE / (hashlib.sha256(f"gpu\0{voice}\0{native}\0{text}".encode()).hexdigest() + ".mp3")
        if gk.exists():
            STATS["tts_cache_hit"] += 1
            return gk.read_bytes(), True
    key = CACHE / (hashlib.sha256(f"{engine}\0{voice}\0{text}".encode()).hexdigest() + ".mp3")
    if key.exists():
        STATS["tts_cache_hit"] += 1
        return key.read_bytes(), True
    wav, _ = tts(text, engine)
    mp3 = to_mp3(wav, voice)
    tmp = key.with_suffix(".tmp")
    tmp.write_bytes(mp3)
    tmp.replace(key)
    return mp3, False


def tts(text, engine="mms"):
    """(wav_bytes, cache_hit)."""
    if engine not in TTS or engine == "chatterbox_gpu":
        raise VoiceError("TTS turi noto'g'ri")
    text = clean_text(text)
    if not text:
        raise VoiceError("Matn bo'sh")
    key = CACHE / (hashlib.sha256(f"{engine}\0{text}".encode()).hexdigest() + ".wav")
    if key.exists():
        STATS["tts_cache_hit"] += 1
        return key.read_bytes(), True
    STATS["tts_cache_miss"] += 1
    cfg = TTS[engine]
    with _locks[cfg["port"]]:
        res = _gradio(cfg["port"], "synth", cfg["args"](text), cfg["timeout"])
    f = res[0] if isinstance(res, list) else res
    path = f.get("path") if isinstance(f, dict) else None
    if not path:
        raise VoiceError("TTS fayl qaytarmadi")
    with urllib.request.urlopen(f"http://{HOST}:{cfg['port']}/gradio_api/file={path}", timeout=30) as r:
        wav = r.read()
    tmp = key.with_suffix(".tmp")
    tmp.write_bytes(wav)
    tmp.replace(key)
    return wav, False


def _is_pcm16k(audio, max_s=STT_MAX_S):
    """Frontend allaqachon 16 kHz mono 16-bit WAV yuborsa — ffmpeg shart emas (v1.4.5: STT tezligi)."""
    if audio[:4] != b"RIFF" or audio[8:12] != b"WAVE":
        return False
    try:
        import wave
        with wave.open(io.BytesIO(audio)) as w:
            return (w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == 16000
                    and w.getcomptype() == "NONE" and w.getnframes() / 16000 <= max_s)
    except Exception:  # noqa: BLE001
        return False


def _to_wav(audio, sr=16000, max_s=STT_MAX_S):
    if sr == 16000 and _is_pcm16k(audio, max_s):
        return audio
    with tempfile.TemporaryDirectory() as d:
        src, dst = Path(d) / "in", Path(d) / "out.wav"
        src.write_bytes(audio)
        p = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-t", str(max_s),
                            "-ar", str(sr), "-ac", "1", str(dst)], capture_output=True, timeout=30)
        if p.returncode != 0 or not dst.exists():
            raise VoiceError("Audio formatini o'qib bo'lmadi")
        return dst.read_bytes()


def _split_wav(wav, chunk_s=STT_CHUNK_S, sr=16000):
    """16 kHz mono 16-bit WAV -> ≤ chunk_s soniyali WAV bo'laklar; chegara eng jim 20 ms oynadan (so'z o'rtasida kesilmasin)."""
    import array
    import wave
    with wave.open(io.BytesIO(wav)) as w:
        pcm = w.readframes(w.getnframes())
    a = array.array("h")
    a.frombytes(pcm[: len(pcm) // 2 * 2])
    n, step = len(a), sr // 50                           # 20 ms
    out, start = [], 0
    while n - start > chunk_s * sr:
        lo, hi = start + int((chunk_s - 7) * sr), start + chunk_s * sr   # oxirgi 7 soniya ichidan eng jim joy
        best, cut = None, hi
        for i in range(lo, hi - step, step):
            e = sum(abs(x) for x in a[i:i + step:4])
            if best is None or e < best:
                best, cut = e, i + step // 2
        out.append(a[start:cut])
        start = cut
    out.append(a[start:])
    res = []
    for part in out:
        if len(part) < sr // 3:                          # 0,3 s dan qisqa qoldiq — tashlanadi
            continue
        b = io.BytesIO()
        with wave.open(b, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(part.tobytes())
        res.append(b.getvalue())
    return res


def _upload(port, wav):
    b = "----lexsim" + uuid.uuid4().hex
    body = (f"--{b}\r\nContent-Disposition: form-data; name=\"files\"; filename=\"a.wav\"\r\n"
            f"Content-Type: audio/wav\r\n\r\n").encode() + wav + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request(f"http://{HOST}:{port}/gradio_api/upload", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())[0]


def _forget(path):
    """Gradio yuklagan faylni o'chirish (faqat /tmp/gradio ichida)."""
    try:
        p = Path(path).resolve()
        if str(p).startswith("/tmp/gradio/") and p.is_file():
            p.unlink()
            if not any(p.parent.iterdir()):
                p.parent.rmdir()
    except OSError:
        pass


STT_LOG = collections.deque(maxlen=2000)   # (vaqt, dvigatel, ms, cpu_zaxira, past_ishonch) — /health uchun
_VOCAB = {"stems": set()}
STOP = {"va", "bu", "u", "men", "biz", "siz", "ham", "bilan", "uchun", "kerak", "edi", "emas", "bor", "yo'q", "deb",
        "endi", "shu", "bir", "ikki", "lekin", "ammo", "chunki", "agar", "mana", "hozir", "juda", "eng", "nima", "qanday"}


def set_vocab(texts):
    """Ish lug'ati (ssenariy, gaplar, variantlar) — confidence uchun. Asos: 5 harfli o'zak."""
    st = set()
    for t in texts:
        for w in _words(t):
            st.add(w[:5])
    _VOCAB["stems"] = st


def _words(t):
    t = (t or "").lower().replace("ʻ", "'").replace("ʼ", "'").replace("‘", "'").replace("’", "'")
    return re.findall(r"[a-zа-яёўқғҳ']{3,}", t)


def confidence(text, seconds):
    """0–1. Model bermagani uchun oddiy baho: lug'atdagi so'zlar ulushi, takrorlanish, nutq tezligi."""
    ws = [w for w in _words(text) if w not in STOP]
    allw = re.findall(r"\w+", text or "")
    if not allw:
        return 0.0
    stems = _VOCAB["stems"]
    known = (sum(1 for w in ws if w[:5] in stems) / len(ws)) if (ws and stems) else (1.0 if not ws else 0.5)
    rep_ = sum(1 for i, w in enumerate(ws) if w in ws[:i]) / max(1, len(ws))
    wps = len(allw) / max(0.5, seconds or 0.5)
    rate = 1.0 if 0.7 <= wps <= 4.5 else (0.5 if 0.3 <= wps <= 6 else 0.0)
    return round(max(0.0, min(1.0, 0.7 * known + 0.15 * rate + 0.15 * (1 - rep_))), 2)


def stt_health():
    now = time.time()
    day = [r for r in STT_LOG if now - r[0] < 86400]
    gpu = sorted(r[2] for r in day if r[1].startswith("gpu"))
    last = day[-1][1] if day else None

    def q(v, p):
        return v[min(len(v) - 1, int(len(v) * p))] if v else None
    return {"engine": last, "p50Ms": q(gpu, 0.5), "p95Ms": q(gpu, 0.95), "samples24h": len(day),
            "cpuFallbacks24h": sum(1 for r in day if r[3]), "lowConfidence24h": sum(1 for r in day if r[4])}


LIVE = {"t": 0.0}   # oxirgi jonli STT vaqti — prerender shu paytda GPU'ni bo'shatib turadi


def stt_full(audio, engine="navai"):
    """-> dict: text, confidence, lowConfidence, engine, audioSeconds, timings(ms). Vaqt o'lchovi bosqichma-bosqich."""
    t0 = LIVE["t"] = time.time()
    text, seconds, used, tm = _stt(audio, engine, {})
    tm["total"] = round((time.time() - t0) * 1000)
    conf = confidence(text, seconds)
    low = conf < 0.5
    STT_LOG.append((time.time(), used, tm["total"], not used.startswith("gpu"), low))
    return {"text": text, "confidence": conf, "lowConfidence": low, "engine": used, "audioSeconds": seconds, "timings": tm}


def stt(audio, engine="navai"):
    """(matn, audio_soniya) — eski interfeys."""
    r = stt_full(audio, engine)
    return r["text"], r["audioSeconds"]


def _stt(audio, engine, tm):
    if engine not in STT:
        raise VoiceError("STT turi noto'g'ri")
    t = time.time()
    wav = _to_wav(audio)
    tm.setdefault("convert", round((time.time() - t) * 1000))
    seconds = round(max(0, len(wav) - 44) / 32000, 1)       # 16 kHz * 2 bayt
    if seconds < 0.3:
        raise VoiceError("Audio juda qisqa")
    cfg = STT[engine]
    if engine.startswith("gpu") and gpu_down("stt"):
        STATS["stt_fallback"] = STATS.get("stt_fallback", 0) + 1
        return _stt(wav, cfg["fallback"], tm)
    parts = _split_wav(wav) if seconds > STT_CHUNK_S else [wav]
    texts = []
    try:
        with _locks[cfg["port"]]:
            tm["upload"], tm["model"] = 0, 0
            for part in parts:                           # uzun nutq — bo'laklab, ketma-ket (GPU bitta)
                t = time.time()
                path = _upload(cfg["port"], part)
                tm["upload"] += round((time.time() - t) * 1000)
                args = [{"path": path, "meta": {"_type": "gradio.FileData"}}] + ([cfg["model"]] if cfg.get("model") else [])
                try:
                    t = time.time()
                    r = _gradio(cfg["port"], "transcribe", args, cfg["timeout"])
                    tm["model"] += round((time.time() - t) * 1000)
                finally:
                    _forget(path)                        # maxfiylik: talaba ovozi diskda qolmasin (lokal Gradio)
                texts.append(((r[0] if isinstance(r, list) else str(r)) or "").strip())
            if len(parts) > 1:
                tm["chunks"] = len(parts)
        res = [" ".join(x for x in texts if x)]
    except Exception:  # noqa: BLE001
        if not cfg.get("fallback"):
            raise
        gpu_failed("stt")
        STATS["stt_fallback"] = STATS.get("stt_fallback", 0) + 1
        return _stt(wav, cfg["fallback"], tm)            # GPU ishlamasa — serverdagi CPU Kotib
    text = (res[0] if isinstance(res, list) else str(res)) or ""
    return fix_terms(text.strip()), seconds, engine, tm


# STT sud atamalarini tez-tez noto'g'ri taniydi — oddiy tuzatish lug'ati (kengaytirish mumkin)
TERM_FIXES = [
    (r"\bp[iey]n[gk]?y?a(ni|ning|ga|dan|si|ni)?\b", r"penya\1"),
    (r"\bneust[oa]yk", "neustoyk"),
    (r"\bishonch ?noma", "ishonchnoma"),
    (r"\biltimos ?noma", "iltimosnoma"),
    (r"\bdalolat ?noma", "dalolatnoma"),
    (r"\bhisob[ -]?faktura", "hisob-faktura"),
    (r"^hurmatli sud\b", "Hurmatli sud"),
    # 2026-11-21 sinovida tez-tez xato tanilgan sud atamalari (faqat aniq kontekstda — boshqa so'zlarga tegmasin)
    (r"\b(?:davogar|davomgar|bog'gar|bog'lar|dovogar)(\s+vakil)", r"da'vogar\1"),
    (r"\bjavobgarlikdan foydalangan", "javobgar undan foydalangan"),
    (r"\bvakolatli olgan\b", "vakolatli organ"),
    (r"\bob'ekt\b", "obyekt"),
    (r"\bhurmatli sut\b", "hurmatli sud"),
]


def fix_terms(text):
    for pat, rep in TERM_FIXES:
        text = re.sub(pat, rep, text, flags=re.I)
    return uz_numbers(text)


# ---------------------------------------------------------------- o'zbekcha son so'zlari -> raqam
# STT raqamlarni so'z bilan yozadi («besh yuz qirq to'rtinchi moddasiga»). Modda va summa tekshiruvi raqam bilan
# ishlaydi, shuning uchun ovozli javob ham «544-moddasiga» ko'rinishiga keltiriladi.
_UNITS = {"nol": 0, "bir": 1, "ikki": 2, "uch": 3, "to'rt": 4, "besh": 5, "olti": 6, "yetti": 7, "sakkiz": 8,
          "to'qqiz": 9, "o'n": 10, "yigirma": 20, "o'ttiz": 30, "qirq": 40, "ellik": 50, "oltmish": 60,
          "yetmish": 70, "sakson": 80, "to'qson": 90}
_MULT = {"yuz": 100, "ming": 1000, "million": 10 ** 6, "milliard": 10 ** 9}
_ORD = re.compile(r"^(.+?)(?:inchi|nchi)$")
_APOS = re.compile(r"[ʻʼ‘’`]")


def _num_word(w):
    """-> (qiymat, turi, tartib_sonmi) yoki None. turi: unit | mult."""
    w = _APOS.sub("'", w.lower())
    for base, ordinal in ((w, False), ((_ORD.match(w).group(1) if _ORD.match(w) else None), True)):
        if not base:
            continue
        if ordinal and base.endswith("k") and base[:-1] + "kki" in _UNITS:   # «ikkinchi» -> ikki
            base = base[:-1] + "kki"
        if ordinal and base + "i" in _UNITS:              # «oltinchi» -> olti, «yettinchi» -> yetti
            base = base + "i"
        if ordinal and base.endswith("t") and base + "ti" in _UNITS:
            base = base + "ti"
        if base in _UNITS:
            return _UNITS[base], "unit", ordinal
        if base in _MULT:
            return _MULT[base], "mult", ordinal
    return None


def uz_numbers(text):
    toks = re.split(r"(\s+)", text)
    words = [(i, t) for i, t in enumerate(toks) if t.strip()]
    out = list(toks)
    k = 0
    while k < len(words):
        run = []
        j = k
        while j < len(words):
            core = re.match(r"^([\w'ʻʼ‘’`]+)([.,;:!?]*)$", words[j][1])
            nw = _num_word(core.group(1)) if core else None
            if not nw:
                break
            if run and nw[1] == "unit" and run[-1][1][1] == "unit":
                pv = run[-1][1][0]                        # «sakkiz besh» — ikki alohida son; «yigirma besh» — bitta
                if pv < 10 or (pv >= 10 and nw[0] >= 10):
                    break
            run.append((j, nw, core.group(2)))
            j += 1
            if nw[2] or core.group(2):                    # tartib son yoki tinish belgisi — son shu yerda tugaydi
                break
        if not run:
            k += 1
            continue
        single = len(run) == 1
        w0 = _APOS.sub("'", re.sub(r"[.,;:!?]+$", "", words[run[0][0]][1]).lower())
        if single and not run[0][1][2] and (w0 in ("bir", "yuz", "ming", "o'n", "uch") or run[0][1][1] == "mult"):
            k += 1                                        # «bir oz», «yuz berdi», «ming rahmat» — son emas
            continue
        total, cur = 0, 0
        for _, (v, kind, _o), _p in run:
            if kind == "unit":
                cur += v
            elif v == 100:
                cur = (cur or 1) * 100
            else:
                total += (cur or 1) * v
                cur = 0
        n = total + cur
        last_j, (_, _, is_ord), punct = run[-1]
        val = str(n)
        if is_ord:                                        # «to'rtinchi moddasiga» -> «4-moddasiga»
            nxt = words[last_j + 1] if last_j + 1 < len(words) and not punct else None
            if nxt:
                out[nxt[0]] = f"{val}-{nxt[1]}"
                val = None
            else:
                val = f"{val}-chi{punct}"
                punct = ""
        first = words[run[0][0]][0]
        for idx in range(run[0][0], last_j + 1):          # son so'zlari o'rniga bitta raqam
            out[words[idx][0]] = ""
            if idx > run[0][0] and words[idx][0] - 1 >= 0:
                out[words[idx][0] - 1] = ""               # oradagi bo'shliq
        out[first] = (val + punct) if val is not None else ""
        if val is None and first + 1 < len(out):
            out[first + 1] = ""
        k = last_j + 1
    return re.sub(r"\s{2,}", " ", "".join(out)).strip()


def prewarm(lines, engine="mms", log=print):
    """Shablon gaplarni oldindan ovozlashtirish (fon oqimida)."""
    done = 0
    for t in lines:
        try:
            tts(t, engine)
            done += 1
        except Exception as e:  # noqa: BLE001
            log(f"TTS prewarm xato: {e}")
    log(f"TTS kesh: {done}/{len(lines)} shablon gap tayyor ({engine})")
