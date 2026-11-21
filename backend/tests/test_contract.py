"""Kontrakt testi: backend javoblari frontendning contracts.schema.json (JSON Schema 2020-12) sxemalariga mosmi.

Serverda: cd ~/lexsim/backend && ../venv/bin/python -m unittest -v tests.test_contract
jsonschema kutubxonasi o'rnatilmagan, shuning uchun sxemada ishlatilgan kalit so'zlar uchun kichik validator:
type, properties, required, enum, const, items, anyOf, minimum/maximum, minLength/maxLength, maxItems, minItems.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
os.environ.setdefault("LEXSIM_STATE_DB", tempfile.mktemp(suffix=".db"))
os.environ["LEXSIM_DSN"] = ""
import lexsim_server as L  # noqa: E402

L.NORMS = L.Norms()
L.SETTINGS.update(llm=False, sem=False, rag=False)
SCHEMA = json.load(open(HERE / "contracts" / "contracts.schema.json", encoding="utf-8"))["$defs"]
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def check(v, s, path="$"):
    """Xatolar ro'yxati (bo'sh — mos)."""
    errs = []
    if "anyOf" in s:
        if all(check(v, alt, path) for alt in s["anyOf"]):
            errs.append(f"{path}: anyOf variantlarining hech biriga mos emas ({json.dumps(v, ensure_ascii=False)[:80]})")
        return errs
    if "const" in s and v != s["const"]:
        return [f"{path}: const {s['const']!r} kutilgan, {v!r} keldi"]
    if "enum" in s and v not in s["enum"]:
        return [f"{path}: {v!r} enum {s['enum']} ichida emas"]
    t = s.get("type")
    if t:
        ts = t if isinstance(t, list) else [t]
        ok = False
        for x in ts:
            if x == "integer":
                ok |= isinstance(v, int) and not isinstance(v, bool)
            elif x == "number":
                ok |= isinstance(v, (int, float)) and not isinstance(v, bool)
            elif x == "boolean":
                ok |= isinstance(v, bool)
            else:
                ok |= isinstance(v, TYPES[x])
        if not ok:
            return [f"{path}: tur {t} kutilgan, {type(v).__name__} keldi"]
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if "minimum" in s and v < s["minimum"]:
            errs.append(f"{path}: {v} < minimum {s['minimum']}")
        if "maximum" in s and v > s["maximum"]:
            errs.append(f"{path}: {v} > maximum {s['maximum']}")
    if isinstance(v, str):
        if len(v) < s.get("minLength", 0):
            errs.append(f"{path}: satr juda qisqa")
        if "maxLength" in s and len(v) > s["maxLength"]:
            errs.append(f"{path}: satr {len(v)} > maxLength {s['maxLength']}")
    if isinstance(v, list):
        if "maxItems" in s and len(v) > s["maxItems"]:
            errs.append(f"{path}: {len(v)} > maxItems {s['maxItems']}")
        if len(v) < s.get("minItems", 0):
            errs.append(f"{path}: minItems {s['minItems']}")
        if "items" in s:
            for i, x in enumerate(v):
                errs += check(x, s["items"], f"{path}[{i}]")
    if isinstance(v, dict):
        for k in s.get("required", []):
            if k not in v:
                errs.append(f"{path}: majburiy maydon yo'q: {k}")
        for k, sub in s.get("properties", {}).items():
            if k in v:
                errs += check(v[k], sub, f"{path}.{k}")
    return errs


def run_flow(scid, level="beginner", texts=None, options=True):
    s = L.new_session(scid, "tutorial", 42, "owner-token", level)
    snaps, muts = [L.frozen(L.snapshot(s))], []
    for act in ("start", "sit-at-desk"):
        eng = L.Engine(s)
        if act == "start":
            s["startedAt"] = L.now_iso()
            eng.status("in-progress")
        else:
            eng.opening()
        muts.append(L.frozen({"events": eng.events, "snapshot": L.snapshot(s)}))
    h = L.hint(s)
    while s["stage"] != "yakun":
        eng = L.Engine(s)
        opts = L.stage_options(s)
        text = next(o["text"] for o in opts if o["tone"] == "good") if opts else "Hurmatli sud, tushunarli."
        u = eng.user(text)
        u["inputMode"], u["stage"] = "option", s["stage"]
        L.Handler.apply_option(eng, next((o for o in opts if o["text"] == text), None), u["id"])
        eng.process(text, u["id"])
        L.set_feedback(s, u["id"])
        muts.append(L.frozen({"events": eng.events, "snapshot": L.snapshot(s)}))
    eng = L.Engine(s)
    eng.finish()
    muts.append(L.frozen({"events": eng.events, "snapshot": L.snapshot(s)}))
    return snaps, muts, L.frozen(s["report"]), h


class Contract(unittest.TestCase):
    def assertValid(self, v, name):
        errs = check(L.uz_norm(v), SCHEMA[name])
        self.assertFalse(errs, f"{name}: " + "; ".join(errs[:6]))

    def test_flows_match_schema(self):
        for scid in L.SCEN:
            for level in ("beginner", "intermediate", "advanced"):
                snaps, muts, report, h = run_flow(scid, level)
                for sn in snaps:
                    self.assertValid(sn, "Snapshot")
                for m in muts:
                    self.assertValid(m, "MutationResponse")
                self.assertValid(report, "Assessment")
                self.assertValid(h, "Hint")


if __name__ == "__main__":
    unittest.main()
