#!/usr/bin/env python3
"""data/lex/*.jsonl -> law_chunks (PostgreSQL + pgvector), bge-m3 embedding bilan.

Qoidalar — LexSim_RAG_Qollanma.md §3–4, §7:
  * bitta modda — bitta bo'lak; matn > 2000 belgi bo'lsa xatboshilar bo'yicha ~1500 belgili bo'laklar (FK-544#1, #2);
  * embed_text = "KOD N-modda. Sarlavha\\n" + matn; search_text = normalize(embed_text) (textnorm — RAG bilan bir xil);
  * o'zgarmagan (content_hash bir xil) qatorga tegilmaydi; o'zgargani yangilanadi; yo'qolgan bo'lakka valid_to qo'yiladi
    (faqat shu kodning hamma fayli berilganda).

Ishlatish (server, DSN env da):
  python lex_ingest.py --dry data/lex/MK.jsonl ...      # nima o'zgarishini ko'rsatadi
  python lex_ingest.py data/lex/MK.jsonl ...            # yozadi (embedding CPU'da)
"""
import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import date

sys.path.insert(0, os.environ.get("LEXSIM_TOOLS", "/opt/lexsim/tools"))
from textnorm import normalize  # noqa: E402

CASE_TYPES = {"FK": ["IPK", "FPK"], "IPK": ["IPK"], "FPK": ["FPK"], "MK": ["FPK"],
              "JPK": ["JPK"], "JK": ["JPK"], "MUR": ["FPK", "IPK", "JPK", "MAM"], "DBQ": ["IPK", "FPK"],
              "ADQ": ["IPK", "FPK", "JPK"], "AKQ": ["IPK", "FPK", "JPK"]}
FILES_OF = {"FK": {"FK1", "FK2"}}          # bir kod bir nechta faylda
LIMIT, PART = 2000, 1500


def label(code, num):
    return f"{code} {num}-modda"


def expand(refs):
    out = []
    for r in refs or []:
        m = re.fullmatch(r"([A-Z]+\d*)-(\d+)\s*[—–-]\s*(\d+)", r)
        if m and int(m.group(3)) - int(m.group(2)) < 60:
            out += [f"{m.group(1)}-{i}" for i in range(int(m.group(2)), int(m.group(3)) + 1)]
        elif re.fullmatch(r"[A-Z]+\d*-[\w-]+", r):
            out.append(r)
    seen = []
    for x in out:
        if x not in seen:
            seen.append(x)
    return seen[:80]


def chunks(art):
    text = art["text_latn"].strip()
    head = f"{label(art['code'], art['article_no'])}. {art['title']}".strip()
    if len(text) <= LIMIT:
        return [(art["norm_id"], text, head + "\n" + text)]
    parts, cur = [], ""
    for para in text.split("\n"):
        if cur and len(cur) + len(para) + 1 > PART:
            parts.append(cur)
            cur = para
        else:
            cur = (cur + "\n" + para) if cur else para
    if cur:
        parts.append(cur)
    return [(f"{art['norm_id']}#{i}", p, head + "\n" + p) for i, p in enumerate(parts, 1)]


def rows_of(paths):
    out, codes_files = [], {}
    for p in paths:
        fname = os.path.basename(p).rsplit(".", 1)[0]
        for line in open(p, encoding="utf-8"):
            a = json.loads(line)
            if a.get("valid_to") or not a.get("text_latn", "").strip():
                continue
            codes_files.setdefault(a["code"], set()).add(fname)
            for cid, text, emb in chunks(a):
                out.append({
                    "chunk_id": cid, "norm_id": a["norm_id"], "doc_type": "code", "code": a["code"],
                    "article_no": a["article_no"], "punkt": None, "title": a["title"], "chapter": a.get("chapter"),
                    "text_latn": text, "search_text": normalize(emb), "embed_text": emb,
                    "lexuz_comment": a.get("lexuz_comment"), "refs": expand(a.get("refs_same_code")),
                    "amendments": a.get("amendments") or [], "case_types": CASE_TYPES.get(a["code"], ["IPK", "FPK"]),
                    "lex_url": a["lex_url"], "doc_id": a.get("doc_id"), "doc_title": a.get("doc_title"),
                    "fetched_at": a.get("fetched_at"), "content_hash": hashlib.sha256(text.encode()).hexdigest()})
    full = {c for c, fs in codes_files.items() if fs >= FILES_OF.get(c, fs)}
    return out, full


COLS = ["chunk_id", "norm_id", "doc_type", "code", "article_no", "punkt", "title", "chapter", "text_latn", "search_text",
        "embed_text", "lexuz_comment", "refs", "amendments", "case_types", "lex_url", "doc_id", "doc_title", "fetched_at",
        "content_hash"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--update", action="store_true", help="mavjud kodlarni ham yangilash (ehtiyot bo'ling)")
    ap.add_argument("--batch", type=int, default=8)
    a = ap.parse_args()
    import psycopg
    rows, full = rows_of(a.files)
    codes = sorted({r["code"] for r in rows})
    with psycopg.connect(os.environ["LEXSIM_DSN"]) as db:
        have = {cid: (h, vt) for cid, h, vt in db.execute(
            "SELECT chunk_id, content_hash, valid_to FROM law_chunks WHERE code = ANY(%s)", (codes,))}
        # Bazada allaqachon bor kodlar (FK, IPK, FPK) boshqa quvur bilan yozilgan — ularga tegmaymiz,
        # faqat bazada umuman yo'q modda (norm_id) qo'shiladi. --update bilan to'liq yangilash.
        old_codes = {cid.split("-")[0] for cid in have}
        have_norm = {cid.split("#")[0] for cid in have}
        if a.update:
            new = [r for r in rows if r["chunk_id"] not in have]
            changed = [r for r in rows if r["chunk_id"] in have and (have[r["chunk_id"]][0] != r["content_hash"] or have[r["chunk_id"]][1])]
            keep = {r["chunk_id"] for r in rows}
            stale = [cid for cid, (h, vt) in have.items() if vt is None and cid not in keep and cid.split("-")[0] in full]
        else:
            new = [r for r in rows if r["code"] not in old_codes or r["norm_id"] not in have_norm]
            changed, stale = [], []
        by = {}
        for r in new:
            by.setdefault(r["code"], [0, 0])[0] += 1
        for r in changed:
            by.setdefault(r["code"], [0, 0])[1] += 1
        print(f"bo'laklar: jami {len(rows)}, yangi {len(new)}, o'zgargan {len(changed)}, eskirgan {len(stale)}; kodlar {codes}; to'liq {sorted(full)}")
        print("kod bo'yicha [yangi, o'zgargan]:", by)
        if stale:
            print("eskirgan (namuna):", stale[:15])
        if a.dry:
            return
        todo = new + changed
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("BAAI/bge-m3", device="cpu")
        model.max_seq_length = 1024
        t0, done = time.time(), 0
        for i in range(0, len(todo), 64):
            part = todo[i:i + 64]
            vecs = model.encode([r["embed_text"] for r in part], batch_size=a.batch, normalize_embeddings=True)
            with db.transaction():
                for r, v in zip(part, vecs):
                    vals = [r[c] for c in COLS] + ["[" + ",".join(f"{x:.6f}" for x in v) + "]", "BAAI/bge-m3"]
                    db.execute(
                        f"INSERT INTO law_chunks ({','.join(COLS)}, embedding, embedding_model, valid_to) "
                        f"VALUES ({','.join(['%s'] * len(COLS))}, %s::vector, %s, NULL) "
                        f"ON CONFLICT (chunk_id) DO UPDATE SET " + ", ".join(f"{c}=EXCLUDED.{c}" for c in COLS[1:]) +
                        ", embedding=EXCLUDED.embedding, embedding_model=EXCLUDED.embedding_model, valid_to=NULL", vals)
            done += len(part)
            el = time.time() - t0
            print(f"  {done}/{len(todo)}  {el:.0f} s  (~{el / done * (len(todo) - done):.0f} s qoldi)", flush=True)
        if stale:
            db.execute("UPDATE law_chunks SET valid_to=%s WHERE chunk_id = ANY(%s) AND valid_to IS NULL", (date.today(), stale))
        db.commit()
        print("tayyor:", db.execute("SELECT code, count(*) FROM law_chunks WHERE valid_to IS NULL GROUP BY code ORDER BY 2 DESC").fetchall())


if __name__ == "__main__":
    main()
