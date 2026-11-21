#!/usr/bin/env python3
"""Lex.uz hujjatini moddalarga ajratib, RAG uchun JSONL yozadi.

Ishlatish:
    python3 tools/lex_extract.py FK1=111181 FK2=180550 IPK=3523891 FPK=3517334

Har bir argument: KOD=lex.uz_hujjat_ID. Natija: data/lex/<KOD>.jsonl
Til: lang=4 (o'zbek, lotin). Kirill uchun --lang 3.

Eslatma: lex.uz foydalanish shartlariga rioya qiling, so'rovlar orasida pauza bor.
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

UA = "Mozilla/5.0 (LexSim research; contact via project team)"
NOISE = [
    "Ҳужжатга таклиф юбориш", "Аудиони тинглаш", "Ҳужжат элементидан ҳавола олиш",
    "Hujjatga taklif yuborish", "Audioni tinglash", "Hujjat elementidan havola olish",
]
ARTICLE_RE = re.compile(r"^(\d+)(?:(?:\s*-\s*|\s+)(\d+))?\s*-modda\.\s*(.*)$")   # «7-modda», «7-1-modda», «7 1 -modda» (7¹)
REF_RE = re.compile(r"(\d+(?:\s*[—-]\s*\d+)?)(?:\s*,\s*(?=\d))?")


def fetch(doc_id: str, lang: int, cache_dir: str) -> str:
    path = os.path.join(cache_dir, f"{doc_id}_lang{lang}.html")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read()
    url = f"https://lex.uz/docs/{doc_id}?lang={lang}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        s = r.read().decode("utf-8", "replace")
    os.makedirs(cache_dir, exist_ok=True)
    open(path, "w", encoding="utf-8").write(s)
    time.sleep(3)  # serverni yuklamaslik uchun
    return s


def clean(fragment: str) -> str:
    t = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S)
    t = re.sub(r"<br\s*/?>|</p>|</div>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    for n in NOISE:
        t = t.replace(n, " ")
    t = re.sub(r"[ \t ]+", " ", t)
    t = re.sub(r"\s*\n\s*", "\n", t).strip()
    return t


BLOCK_RE = re.compile(r'<div class="([A-Z_]+) lx_[a-z_]+"([^>]*)>')


def extract(code: str, doc_id: str, lang: int, cache_dir: str):
    """Hujjatni bloklarga bo'lib, moddalarni yig'adi.

    Lex.uz bloklari: CLAUSE_DEFAULT — modda sarlavhasi, ACT_TEXT/BY_DEFAULT — amaldagi matn,
    COMMENT — LexUZ sharhi yoki "Oldingi tahrirga qarang" havolasi,
    CHANGES_ORIGINS — o'zgartirish izohi, TEXT_HEADER_DEFAULT — bob/bo'lim sarlavhasi.
    """
    s = fetch(doc_id, lang, cache_dir)
    title_m = re.search(r"<title>(.*?)</title>", s, re.S)
    doc_title = re.sub(r"\s+", " ", html.unescape(title_m.group(1))).strip() if title_m else code
    prefix = re.sub(r"\d+$", "", code)  # FK1, FK2 -> FK (moddalar raqami umumiy)
    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lang_name = "uz-Latn" if lang == 4 else "uz-Cyrl" if lang == 3 else str(lang)

    blocks = []
    ms = list(BLOCK_RE.finditer(s))
    for k, m in enumerate(ms):
        end = ms[k + 1].start() if k + 1 < len(ms) else len(s)
        el = re.search(r"lx_mo\(event,(-?\d+)\)", m.group(2))
        hidden = "display:none" in m.group(2)
        blocks.append((m.group(1), el.group(1) if el else None, hidden, clean(s[m.end():end])))

    out, cur, chapter = [], None, ""

    def close():
        if cur:
            cur["text_latn"] = "\n".join(cur.pop("_body")).strip()
            cur["lexuz_comment"] = "\n".join(cur.pop("_comment")).strip()
            cur["amendments"] = cur.pop("_amend")
            cm = re.search(r"mazkur Kodeksning(.*?)-moddalar", cur["lexuz_comment"])
            cur["refs_same_code"] = (
                [f"{prefix}-{r.replace(' ', '')}" for r in re.findall(r"\d+(?:\s*[—-]\s*\d+)?", cm.group(1))]
                if cm else []
            )
            out.append(cur)

    for cls, el_id, hidden, text in blocks:
        if cls == "CLAUSE_DEFAULT":
            m = ARTICLE_RE.match(text.split("\n")[0].strip())
            if m:
                close()
                num, title = m.group(1) + (f".{m.group(2)}" if m.group(2) else ""), m.group(3).strip()   # 7¹ -> "7.1" (bazadagi format: FK-173.1)
                cur = {
                    "norm_id": f"{prefix}-{num}", "code": prefix, "article_no": num, "title": title,
                    "chapter": chapter, "_body": [], "_comment": [], "_amend": [],
                    "lex_url": f"https://lex.uz/docs/{doc_id}#{el_id}" if el_id else f"https://lex.uz/docs/{doc_id}",
                    "doc_title": doc_title, "doc_id": doc_id, "lang": lang_name,
                    "fetched_at": fetched, "valid_to": None,
                }
            continue
        if cls == "TEXT_HEADER_DEFAULT":
            close()
            cur = None
            if text:
                chapter = text.split("\n")[0].strip()
            continue
        if cur is None or not text:
            continue
        if cls in ("ACT_TEXT", "BY_DEFAULT") and not hidden:
            cur["_body"].append(text)
        elif cls == "CHANGES_ORIGINS":
            cur["_amend"].append(text.strip("() "))
        elif cls in ("COMMENT", "COMMENTLEXUZ"):
            t = text.replace("Oldingi tahrirga qarang.", "").replace("LexUZ sharhi", "").strip()
            if t:
                cur["_comment"].append(t)
    close()
    return out


CODE_REF_RE = re.compile(r"\b(FK|FPK|IPK|JPK|JK|MK|MJtK)(?:ning|ni|ga|da)?\s+(\d+)(?:\s*[—-]\s*\d+)?-modda")


def extract_plenum(code: str, doc_id: str, lang: int, cache_dir: str):
    """Plenum qarori: moddalar o'rniga raqamlangan bandlar ("1.", "2." ...)."""
    s = fetch(doc_id, lang, cache_dir)
    title_m = re.search(r"<title>(.*?)</title>", s, re.S)
    doc_title = re.sub(r"\s+", " ", html.unescape(title_m.group(1))).strip() if title_m else code
    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ms = list(BLOCK_RE.finditer(s))
    out, cur = [], None
    preamble = []

    def close():
        if cur:
            text = "\n".join(cur.pop("_body")).strip()
            cur["text_latn"] = text
            cur["refs_codes"] = sorted({f"{a}-{b}" for a, b in CODE_REF_RE.findall(text)})
            cur["amendments"] = cur.pop("_amend")
            out.append(cur)

    for k, m in enumerate(ms):
        end = ms[k + 1].start() if k + 1 < len(ms) else len(s)
        cls, attrs = m.group(1), m.group(2)
        if "display:none" in attrs:
            continue
        text = clean(s[m.end():end])
        if not text:
            continue
        el = re.search(r"lx_mo\(event,(-?\d+)\)", attrs)
        if cls == "ACT_TEXT":
            pm = re.match(r"^(\d+)\.\s", text)
            if pm:
                close()
                cur = {
                    "norm_id": f"{code}-p{pm.group(1)}", "code": code, "punkt": pm.group(1),
                    "title": doc_title, "_body": [text], "_amend": [],
                    "lex_url": f"https://lex.uz/docs/{doc_id}#{el.group(1)}" if el else f"https://lex.uz/docs/{doc_id}",
                    "doc_id": doc_id, "lang": "uz-Latn" if lang == 4 else str(lang),
                    "fetched_at": fetched, "valid_to": None, "doc_type": "plenum",
                }
            elif cur:
                cur["_body"].append(text)
            else:
                preamble.append(text)
        elif cls == "CHANGES_ORIGINS" and cur:
            cur["_amend"].append(text.strip("() "))
    close()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docs", nargs="+", help="KOD=ID, masalan IPK=3523891")
    ap.add_argument("--lang", type=int, default=4)
    ap.add_argument("--plenum", action="store_true", help="Plenum qarorlari (bandlar bo'yicha)")
    ap.add_argument("--out", default="data/lex")
    ap.add_argument("--cache", default="data/lex/_cache")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for spec in a.docs:
        code, _, doc_id = spec.partition("=")
        rows = (extract_plenum if a.plenum else extract)(code, doc_id, a.lang, a.cache)
        path = os.path.join(a.out, f"{code}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{code}: {len(rows)} ta yozuv -> {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
