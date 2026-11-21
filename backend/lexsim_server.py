#!/usr/bin/env python3
"""LexSim backend v1 — sud zali (iqtisodiy ish, IPK).

LexSim_Backend_Spec.md kontraktini bajaradi: /api/v1/sessions, /interactions, /turns, /documents,
/finish, /events, /report, /appeal. Faqat Python standart kutubxonasi + psycopg (RAG bazasidan
modda nomi va havolasini olish uchun).

Zanjir (har bir talaba gapida):
  normallashtirish -> harakat aniqlash (qoidalar) -> umumiy qoidalar (G1–G6) -> bosqich ishlovchisi
  (ssenariy + muhim lahzalar) -> RAG (modda tekshiruvi, manbalar) -> NPC replikalari -> eventlar.
Bosqichdan bosqichga faqat kod o'tkazadi. LLM bu versiyada ishlatilmaydi (engine="scripted").

Muhit o'zgaruvchilari:
  LEXSIM_DSN            PostgreSQL (law_chunks jadvali)
  LEXSIM_RAG_URL        qidiruv xizmati, standart http://127.0.0.1:8090
  LEXSIM_RAG_TIMEOUT    soniya, standart 15
  LEXSIM_BACKEND_HOST/PORT  standart 0.0.0.0:8100
  LEXSIM_STATE_DB       sessiyalar uchun SQLite fayl, standart ~/lexsim/backend/sessions.db
  LEXSIM_SECURE_COOKIE  1 bo'lsa cookie Secure bilan
"""
import copy
import hashlib
import hmac
import json
import os
import random
import re
import secrets
import sqlite3
import sys
import threading
import time
import traceback
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from textnorm import normalize, exact_refs  # noqa: E402  (RAG bilan bir xil normallashtirish)
import monitor as M  # noqa: E402  (kuzatuv paneli)
import voice as V  # noqa: E402  (TTS/STT orqali Gradio xizmatlari)
import nlu as NLU  # noqa: E402  (erkin javobni variantga moslash)
import store as ST  # noqa: E402  (case_state, xAPI, o'qituvchi, zaxira)
import procedure as PROC  # noqa: E402  (talaba tashabbusi: savol, iltimosnoma, e'tiroz, kelishuv; aniqlashtirish)
import aihub_llm as AIH  # noqa: E402  (vaqtinchalik LLM: AIHUB orqali Gemini/ChatGPT)
import caselab as LAB  # noqa: E402  (sohalar, foydalanuvchi caselari, AI bilan case tuzish)
import rubric as RB  # noqa: E402  (tushuntiriladigan baholash: bandlar + iqtibos)
import adversary as ADV  # noqa: E402  (raqib-«shaxmatchi»: xatolarni kuzatish va muzokarada foydalanish)
import tactics as TAC  # noqa: E402  (AI raqib/sudya taktikalari va talaba reaksiyasi)
import review as RV  # noqa: E402  (3-bosqich: mentor navbati, audit, oltin to'plam)
import npc as NPC  # noqa: E402  («Ish yo'li»/maslahat/DXM: tayyor javob yo'q bo'lsa — AI qahramon)
import moot as MOOT  # noqa: E402  («Bahs» — jamoaviy sud: sudya qarori, doimiy gaplar)

PROTOCOL = 1
VERSION = "1.5.0"
FEATURES = ["adversary", "tactics", "review-queue", "ai-fallback-judge", "npc-reply", "rubric-explain", "case-visibility", "case-solutions", "domains", "case-lab", "moot-cases", "moot-judge", "moot-lines", "stt-priority", "powers-excuse-first", "levels", "reveal-options", "silence", "scripted", "nlu", "store", "xapi", "prerender", "chatterbox",
            "reply-bank", "voice-key", "tts-duration", "live-procedure", "cors", "turn-engine", "auto-prerender", "scenario-package", "voice-health", "turn-emotion", "turn-gesture", "turn-reactions", "reprimand-ladder", "voice-palette-alias", "tts-cache-free", "turn-presence", "interaction-context", "store-any-kind", "store-ttl", "store-owner-404", "stt-confidence", "stt-timings", "unclear-reask", "turn-audio", "gpu-alert", "human-situations", "profanity-ladder", "nlu-situations"]
PENDING = set()            # LLM javobi kutilayotgan sessiyalar (async turn)
RUBRIC_VERSION = "court-2026.11.1"   # v1.5: manbali og'irliklar (SQE2 50/50)
DSN = os.environ.get("LEXSIM_DSN", "")
RAG_URL = os.environ.get("LEXSIM_RAG_URL", "http://127.0.0.1:8090")
RAG_KEY = os.environ.get("LEXSIM_API_KEY", "")
# LLM (serverdagi colibri Qwen3.6, OpenAI uslubidagi API). Faqat raqib advokat replikalarini yozadi;
# javob tekshiruvdan o'tmasa yoki vaqt tugasa — shablon ishlatiladi.
LLM_ON = os.environ.get("LEXSIM_LLM") == "1"
LLM_URL = os.environ.get("LEXSIM_LLM_URL", "http://192.168.88.110:8000/v1/chat/completions")
LLM_KEY = os.environ.get("LEXSIM_LLM_KEY") or os.environ.get("COLI_API_KEY", "")
LLM_MODEL = os.environ.get("LEXSIM_LLM_MODEL", "qwen3.6-colibri")
LLM_TIMEOUT = float(os.environ.get("LEXSIM_LLM_TIMEOUT", "150"))
LLM_PROVIDER = os.environ.get("LEXSIM_LLM_PROVIDER", "openai")   # openai (Qwen/Gemini API) | aihub
LLM_KEYS = set((os.environ.get("LEXSIM_LLM_KEYS") or "answer,rebut,on_motion,closing").split(","))
LLM_STATS = {"calls": 0, "ok": 0, "fallback": 0, "last_ms": None, "last_error": None}
# Kuzatuv panelidan ish paytida o'zgartiriladigan sozlamalar (settings.json da saqlanadi)
SETTINGS_FILE = HERE / "settings.json"
SETTINGS = {"llm": LLM_ON, "rag": True, "llm_timeout": LLM_TIMEOUT, "tts": "mms", "stt": "gpu", "sem": True}
SETTINGS.update({k: v for k, v in M.load_json(SETTINGS_FILE, {}).items() if k in SETTINGS})
def _secret(env, fname):
    v = os.environ.get(env, "")
    if v:
        return v
    f = HERE / fname
    if not f.exists():
        f.write_text(secrets.token_urlsafe(32))
        os.chmod(f, 0o600)
    return f.read_text().strip()


LEXSIM_KEY = _secret("LEXSIM_KEY", ".lexsim_key")        # server-to-server (frontend Next serveri) kaliti
ADMIN_TOKEN = os.environ.get("LEXSIM_ADMIN_TOKEN", "")
if not ADMIN_TOKEN:
    _tf = HERE / ".admin_token"
    if not _tf.exists():
        _tf.write_text(secrets.token_urlsafe(24))
        os.chmod(_tf, 0o600)
    ADMIN_TOKEN = _tf.read_text().strip()
RAG_TIMEOUT = float(os.environ.get("LEXSIM_RAG_TIMEOUT", "15"))
STATE_DB = os.environ.get("LEXSIM_STATE_DB", str(HERE / "sessions.db"))
SECURE_COOKIE = os.environ.get("LEXSIM_SECURE_COOKIE") == "1"
SCEN = json.load(open(HERE / "scenarios.json", encoding="utf-8"))["scenarios"]
ROLES = json.load(open(HERE / "roles.json", encoding="utf-8"))   # rollar uslubi, lahzalar, maslahatchi
AIH.init(ROLES, SCEN)
SEMCFG = json.load(open(HERE / "semantic.json", encoding="utf-8"))  # maʼno boʻyicha baholash namunalari
OPTIONS = json.load(open(HERE / "options.json", encoding="utf-8"))["stages"]   # darajalar uchun variantlar
REPLIES = json.load(open(HERE / "replies.json", encoding="utf-8"))               # raqibning tayyor javoblari banki
LEVELS = {
    "beginner": {"modes": ["option", "text", "voice"], "silence": None, "hints": True, "feedback": "all"},
    "intermediate": {"modes": ["text", "voice"], "silence": 60, "hints": True, "feedback": "serious"},
    "advanced": {"modes": ["voice", "text"], "silence": 30, "hints": False, "feedback": "none"},
}
SERIOUS = {"order", "injection", "bribe", "false_claim", "stage", "unexamined", "recusal_unfounded", "improper_evidence"}
SEM_URL = os.environ.get("LEXSIM_SEM_URL", "http://127.0.0.1:8091/rerank")    # GPU reranker (teskari SSH tunnel)
SEM_KEY = os.environ.get("LEXSIM_RERANK_KEY", "")
SEM_TIMEOUT = float(os.environ.get("LEXSIM_SEM_TIMEOUT", "5"))
_sem_cache = {}

EMOTIONS = {"neutral", "impatient", "upset", "confused", "uncertain", "calm", "reassured"}
GESTURES = {"none", "nod", "shake-head", "sigh", "lean-in", "check-watch", "show-phone",
            "offer-envelope", "withdraw-envelope", "stand"}
SERVICES = {None, "archive-reference", "pension-recalculation", "refer-elsewhere", "written-complaint"}
EVIDENCE = {"passport", "workbook-photos", "employer-details", "pension-decision", "witness-statement"}
NOTIFY = {"sms", "written", "none"}

OBJECTIVES = [("reach-desk", "Sud zaliga kirish"), ("clarify", "Ishning asosiy holatlarini aniqlash"),
              ("document", "Talabni yozma rasmiylashtirish"), ("finish", "Sud majlisini yakunlash")]

FACTS = {
    "F1": "Vakilning vakolati ishonchnoma bilan tasdiqlandi.",
    "F2": "Ijara shartnomasi va imzolangan hisob-fakturalar sudda o'qildi.",
    "F3": "Obyekt topshirish dalolatnomasi bilan rasmiylashtirilmagan, lekin javobgar undan uch oy foydalangan.",
    "F4": "Da'vo qilingan penya asosiy qarzning qariyb 12 foiziga teng; uni kamaytirish masalasi ko'tarildi.",
}

# Sudya shablonlari (data/sud/bosqichlar_ipk.json bilan bir xil)
T = {
    "ASK_AGAIN_RAD": "{role_name}, savolga javob bering: sud tarkibiga rad qilish to'g'risida arzingiz bormi?",
    "ASK_AGAIN_RIGHTS": "{role_name}, protsessual huquq va majburiyatlaringiz tushunarlimi?",
    "ASK_AGAIN_PRE": "{role_name}, ishni mazmunan ko'rishdan oldin iltimosnomangiz bormi? Bo'lsa, ayting; bo'lmasa, yo'qligini bildiring.",
    "LATE_RECUSAL": "Rad qilish to'g'risidagi arz ish mazmunan ko'rilishidan oldin bildiriladi. Rad asosi keyinroq ma'lum bo'lgan bo'lsa, "
                    "buni asoslab ayting: qaysi holat va qachon ma'lum bo'ldi? Aks holda sud ishni ko'rishda davom etadi.",
    "RISE": "Sud kirib kelmoqda, o'rningizdan turing!",
    "SIT": "O'tiring.",
    "OPEN": "Sud majlisi ochiq deb e'lon qilinadi. Namuna tumanlararo iqtisodiy sudida «A» MChJning yakka tartibdagi "
            "tadbirkor «B»ga nisbatan ijara shartnomasi bo'yicha asosiy qarz va penya undirish to'g'risidagi da'vo arizasi "
            "bo'yicha iqtisodiy ish ko'rib chiqiladi.",
    "CLERK_REPORT": "Hurmatli sud, sud majlisiga taraflarning vakillari kelgan.",
    "ASK_POWERS": "{role_name}, vakolatingizni tasdiqlovchi hujjatni taqdim eting.",
    "POWERS_OK": "Vakolat tekshirildi.",
    "POWERS_AGAIN": "{role_name}, vakolatingizni tasdiqlovchi hujjat — ishonchnomani taqdim etishingiz kerak.",
    "POWERS_MISSING": "Vakolat hujjati taqdim etilmadi, bu bayonnomaga qayd etiladi.",
    "RECUSAL": "Ish raislik qiluvchi sudya tomonidan yakka tartibda ko'riladi. Sud majlisi kotibi ishtirok etmoqda. "
               "Ishda ishtirok etuvchi shaxslarga rad qilish huquqi tushuntiriladi. Sud tarkibiga yoki kotibga rad bildirasizmi?",
    "RECUSAL_DENY": "Sud joyida maslahatlashib, ajrim chiqardi: rad qilish to'g'risidagi arizani qanoatlantirish rad etilsin, "
                    "chunki qonunda nazarda tutilgan asoslar keltirilmadi.",
    "RIGHTS": "Sizlarga protsessual huquq va majburiyatlaringiz tushuntiriladi: dalillar taqdim etish, iltimosnoma berish, "
              "boshqa ishtirokchilarga savol berish, sud muzokaralarida qatnashish huquqiga egasiz. Huquqlaringiz tushunarlimi?",
    "PRE_MOTIONS": "Ishni mazmunan ko'rishdan oldin iltimosnomalaringiz bormi?",
    "MERITS_P": "Ishni mazmunan ko'rishga o'tamiz. Da'vogar vakili, da'vo talablaringizni quvvatlaysizmi? "
                "Talablaringiz va ularning asoslarini bayon qiling.",
    "MERITS_D": "Ishni mazmunan ko'rishga o'tamiz. So'z da'vogar vakiliga beriladi.",
    "ASK_ADMIT": "Javobgar vakili, da'vo talablarini tan olasizmi? Fikringizni bayon qiling.",
    "EVIDENCE": "Sud dalillarni tekshirish tartibini belgilaydi: avval ish materiallaridagi yozma dalillar. "
                "2022-yil 1-apreldagi 32-P-sonli ijara shartnomasi va imzolangan hisob-fakturalar o'qib eshittiriladi.",
    "EVIDENCE_ASK_P": "Da'vogar vakili, javobgar obyekt dalolatnoma bilan topshirilmaganini aytmoqda. Bunga munosabatingiz?",
    "EVIDENCE_ASK_D": "Javobgar vakili, yozma dalillarga fikringiz bormi? Iltimosnomangiz bo'lsa, bayon qiling.",
    "PENALTY_ASK_D": "Javobgar vakili, da'vogarning penya talabiga munosabatingiz?",
    "HEAR_OTHER": "Iltimosnoma bo'yicha boshqa taraf fikrini eshitamiz. {other}, fikringiz?",
    "DEFER": "Penyani kamaytirish masalasi hal qiluv qarorini qabul qilishda, ishning barcha holatlari inobatga olingan "
             "holda hal qilinadi. Taraflarning fikrlari bayonnomaga kiritildi.",
    "ASK_MORE": "Ishda ishtirok etuvchi shaxslarda qo'shimcha materiallar bormi?",
    "DEBATES_P": "Qo'shimcha materiallar bo'lmaganligi sababli sud muzokaralariga o'tiladi. Birinchi bo'lib da'vogar so'zga chiqadi.",
    "DEBATES_D": "Qo'shimcha materiallar bo'lmaganligi sababli sud muzokaralariga o'tiladi. Birinchi bo'lib da'vogar so'zga chiqadi.",
    "FLOOR_D": "So'z javobgar vakiliga beriladi.",
    "TO_CHAMBER": "Sud hal qiluv qarorini qabul qilish uchun maslahatxonaga kiradi.",
    "VERDICT": "O'zbekiston Respublikasi nomidan hal qiluv qarorining xulosa qismi o'qib eshittiriladi: da'vo arizasi qisman "
               "qanoatlantirilsin. Javobgardan da'vogar foydasiga 25 620 433 so'm 19 tiyin asosiy qarz, 30 405 so'm penya va "
               "33 000 so'm pochta xarajati undirilsin. Respublika byudjetiga 573 220 so'm 27 tiyin davlat boji undirilsin. "
               "Da'voning qolgan qismi rad qilinsin.",
    "AFTER_VERDICT": "Hal qiluv qarori bir oy o'tgach qonuniy kuchga kiradi, ustidan bir oy ichida shikoyat qilish mumkin. "
                     "O'tiring. Sud majlisi yopiq deb e'lon qilinadi.",
    "W_STAND": "{role_name}, sudga tik turib murojaat qiling.",
    "W_REPEAT": "Iltimos, fikringizni aniqroq takrorlang.",
    "W_SILENCE": "{role_name}, javob bering.",
    "W_SILENCE_SOFT": "{role_name}, sud sizning javobingizni kutmoqda.",
    "W_BRIBE": "Sudga ta'sir o'tkazishga urinish qonunga zid. Bu holat bayonnomaga qayd etiladi.",
    "CLOSED": "Sud majlisi yopilgan. Yakunlash tugmasini bosing.",
    "W_ADDRESS": "{role_name}, sudga «Hurmatli sud» deb murojaat qiling.",
    "W_NOT_NOW": "Bu masala hozirgi bosqichda ko'rilmaydi. {when}",
    "W_UNEXAMINED": "Muzokaralarda sud majlisida tekshirilmagan holat va dalillarga tayanishga haqingiz yo'q. "
                    "Fikringizni tekshirilgan dalillar doirasida qaytadan bayon qiling.",
    "W_ORDER": "Sud majlisi tartibini buzmang. Takrorlansa, chora ko'riladi.",
    "W_ROLE": "Sud majlisida faqat ish bo'yicha gapiring.",
    "W_NO_NORM": "{ref} bo'yicha norma sud tomonidan aniqlanmadi. Qaysi qonun hujjatiga tayanayotganingizni aniqlashtiring.",
    "LEAVE": "Sud majlisi tartibi qayta-qayta buzilgani sababli, sud majlisi to'xtatiladi. Bu holat bayonnomaga qayd etiladi.",
}

# Raqib (AI) replikalari — ssenariydagi strategiya bo'yicha
OPP = {
    "javobgar-vakili": {   # talaba da'vogar bo'lsa, raqib — javobgar vakili
        "name": "Javobgar vakili",
        "recusal": "Hurmatli sud, rad bildirmaymiz.",
        "rights": "Huquqlarimiz tushunarli, hurmatli sud.",
        "pre": "Hurmatli sud, iltimosnomamiz yo'q.",
        "answer": "Hurmatli sud, da'voni tan olmaymiz. Obyekt bizga topshirish dalolatnomasi bilan topshirilmagan. "
                  "To'g'ri, joydan uch oy foydalanganmiz, lekin bunday katta summa va penya adolatsiz.",
        "motion": "Hurmatli sud, da'vo qilingan penya majburiyat buzilishi oqibatlariga nomutanosib. Fuqarolik kodeksining "
                  "326-moddasiga asosan uni kamaytirishni so'rab iltimosnoma beraman.",
        "closing": "Hurmatli sud, qarzning mavjudligini inkor etmaymiz, lekin obyekt dalolatnoma bilan topshirilmagan va "
                   "penya juda katta. Penyani kamaytirishingizni so'raymiz.",
    },
    "davogar-vakili": {    # talaba javobgar bo'lsa, raqib — da'vogar vakili
        "name": "Da'vogar vakili",
        "recusal": "Hurmatli sud, rad bildirmaymiz.",
        "rights": "Huquqlarimiz tushunarli, hurmatli sud.",
        "pre": "Hurmatli sud, iltimosnomamiz yo'q.",
        "claim": "Hurmatli sud, da'vo talablarimizni to'liq quvvatlaymiz. 2022-yil 1-apreldagi 32-P-sonli ijara shartnomasi "
                 "bo'yicha javobgar ijara haqini to'lamagan. Fuqarolik kodeksining 544-moddasiga asosan 25 620 433,19 so'm "
                 "asosiy qarz va shartnomaning 8.5-bandiga asosan 3 040 580,45 so'm penya undirishni so'raymiz.",
        "rebut": "Hurmatli sud, javobgar obyektdan foydalangan va hisob-fakturalarni imzolagan. Bu ijara munosabati amalda "
                 "bajarilganini ko'rsatadi.",
        "on_motion": "Hurmatli sud, penya shartnomada taraflar kelishuvi bilan yozma belgilangan, javobgar uni imzolagan. "
                     "Kamaytirishga asos yo'q deb hisoblaymiz.",
        "closing": "Hurmatli sud! Sud majlisida tekshirilgan ijara shartnomasi va imzolangan hisob-fakturalar javobgarning "
                   "to'lov majburiyatini tasdiqlaydi. Fuqarolik kodeksining 544-moddasi va shartnomaning 6.4-bandiga asosan "
                   "asosiy qarzni, 8.5-bandiga asosan penyani undirishni so'raymiz.",
    },
}

ROLE_NAME = {"davogar-vakili": "Da'vogar vakili", "javobgar-vakili": "Javobgar vakili"}

# Sudya shablonlarining protsessual asosi (IPK, RAG bazasida tasdiqlangan norm_id)
T_ART = {
    "RISE": ["IPK-167"], "SIT": ["IPK-167"], "OPEN": ["IPK-165"], "ASK_POWERS": ["IPK-165", "IPK-62"],
    "POWERS_OK": ["IPK-62"], "POWERS_AGAIN": ["IPK-62"], "POWERS_MISSING": ["IPK-62"],
    "ASK_AGAIN_RAD": ["IPK-22"], "LATE_RECUSAL": ["IPK-22"],
    "RECUSAL": ["IPK-165", "IPK-20", "IPK-21"], "RECUSAL_DENY": ["IPK-22", "IPK-23"], "RIGHTS": ["IPK-165"],
    "PRE_MOTIONS": ["IPK-169"], "EVIDENCE": ["IPK-168"], "HEAR_OTHER": ["IPK-169"], "DEFER": ["IPK-169", "FK-326"],
    "ASK_MORE": ["IPK-173"], "DEBATES_P": ["IPK-173"], "DEBATES_D": ["IPK-173"], "FLOOR_D": ["IPK-173"],
    "TO_CHAMBER": ["IPK-175"], "VERDICT": ["IPK-186", "IPK-179"], "AFTER_VERDICT": ["IPK-192", "IPK-262"],
    "W_ADDRESS": ["IPK-167"], "W_STAND": ["IPK-167"], "W_ORDER": ["IPK-167"], "W_UNEXAMINED": ["IPK-173"],
}
# Hisobotdagi "article" (faqat bazada tasdiqlangan moddalar)
KM_ARTICLE = {("any", "KM1"): "IPK-62", ("davogar-vakili", "KM2"): "FK-544", ("javobgar-vakili", "KM2"): "FK-578",
              ("davogar-vakili", "KM3"): "FK-262", ("javobgar-vakili", "KM3"): "FK-326", ("any", "KM4"): "IPK-173"}
KM_MAXLOSS = {"KM1": 7, "KM2": 15, "KM3": 15, "KM4": 7}
# Sudya shablonlarining ohangi (v15 §3): kalit -> (emotion, gesture, tinglovchilar munosabati)
SCOLD = [("principal", "uncertain"), ("secretary", "neutral")]
T_STYLE = {
    "OPEN": ("calm", "none", None), "SIT": ("calm", "none", None), "POWERS_OK": ("calm", "nod", None),
    "POWERS_AGAIN": ("uncertain", "lean-in", None), "POWERS_MISSING": ("neutral", "shake-head", [("principal", "upset")]),
    "RECUSAL_DENY": ("neutral", "shake-head", None),
    "ASK_AGAIN_RAD": ("uncertain", "lean-in", None), "ASK_AGAIN_RIGHTS": ("uncertain", "lean-in", None),
    "ASK_AGAIN_PRE": ("uncertain", "lean-in", None), "LATE_RECUSAL": ("calm", "lean-in", None),
    "W_ORDER": ("upset", "shake-head", SCOLD), "W_BRIBE": ("upset", "shake-head", [("principal", "upset"), ("secretary", "uncertain")]),
    "W_ROLE": ("impatient", "shake-head", SCOLD), "W_NOT_NOW": ("impatient", "shake-head", SCOLD),
    "W_NO_NORM": ("uncertain", "lean-in", None), "W_UNEXAMINED": ("impatient", "shake-head", SCOLD),
    "LEAVE": ("upset", "stand", [("principal", "upset")]), "CLOSED": ("neutral", "none", None),
    "VERDICT": ("neutral", "none", None), "AFTER_VERDICT": ("calm", "none", None),
    "W_REPEAT": ("uncertain", "lean-in", None),
}
ROLE_VOICE = {"judge": "elder_m", "secretary": "female", "opponent": "female_alt"}   # npcTurn.audio uchun (frontend xaritasi bilan bir xil)
SHORT_OK = {"ha", "xa", "yo'q", "yoq", "tushunarli", "bor", "mavjud", "roziman", "rozimiz", "bildirmaymiz", "bildiramiz",
            "bildiraman", "qilmaymiz", "yo'qmi"}
YESNO_STAGES = ("rad", "huquqlar", "oldingi", "qoshimcha")
AI_JUDGE_MAX = int(os.environ.get("LEXSIM_AI_JUDGE_MAX", "12"))     # bitta majlisda AI sudya javoblari chegarasi
REC_STRONG = (r"rad (bildir|qil)\w*(?! ?ma)", r"otvod", r"отвод")
REC_GROUNDS = (r"ishonch\w* yo'q", r"xolis emas", r"\btanish", r"qarindosh", r"manfaatdor", r"g'araz", r"bir tomonlama",
               r"\bdo'st", r"aloqasi bor")
REC_WHO = (r"\bsud\w*", r"kotib", r"ekspert", r"tarjimon", r"mutaxassis", r"prokuror")


def recusal_intent(nt):
    """«Rad bildiraman» yoki asos bilan («sudyaga ishonchim yo'q, u javobgarning tanishi»)."""
    neg = has(nt, r"rad bildirma", r"rad qilma", r"rad (qilish|bildirish)\w* (arz|ariza)\w* yo'q")
    return not neg and (has(nt, *REC_STRONG) or (has(nt, *REC_GROUNDS) and has(nt, *REC_WHO)))
# So'kinish (o'zbekcha va ruscha, normalize lotinga o'giradi) — etika, darhol tanbeh
PROFANITY = tuple(NLU.PROF)                      # bitta ro'yxat — nlu.py
_AUDIO_DUR = {}


def nlu_situation(utt):
    """«Ish yo'li» va DXM uchun (v1.4.6): vaziyat + har bir qahramon uchun tayyor, prerender qilingan odamdek javob."""
    nt = normalize(utt)
    for sit in PROC.CFG.get("nlu_situations", []):
        if sit.get("maxWords") and len(nt.split()) > sit["maxWords"]:
            continue                                     # «qaytaring» faqat qisqa gapda («pulni qaytarib bering» emas)
        pats = NLU.PROF if sit.get("prof") else sit.get("patterns", [])
        if any(re.search(p, nt) for p in pats) or (sit.get("cyrillic") and len(CYR.findall(utt)) >= 3):
            out = {"id": sit["id"], "tone": sit["tone"], "note": sit["note"], "ethics": sit["id"] == "profanity",
                   "replies": {r: {"emotion": v["emotion"], "lines": v["lines"], "voices": PROC.CFG["nlu_voices"].get(r, ["male"])}
                               for r, v in sit["replies"].items()}}
            if sit.get("action"):
                out["action"] = sit["action"]            # repeat_last: frontend shu qahramonning oxirgi gapini qayta ijro etadi
            return out
    return None


def repeat_intent(nt):
    """Talaba gapni qayta so'rayapti («eshitmadim, qaytaring»)."""
    sit = next((x for x in PROC.CFG.get("nlu_situations", []) if x.get("id") == "repeat"), None)
    return bool(sit) and len(nt.split()) <= sit.get("maxWords", 7) and any(re.search(p, nt) for p in sit["patterns"])


def build_vocab():
    """Ish lug'ati: STT ishonchi va «ma'nosiz gap» tekshiruvi uchun."""
    texts = [t for t, _ in canonical_lines()] + list(T.values()) + list(FACTS.values())
    for f in ("options.json", "replies.json", "semantic.json", "roles.json", "intents.json", "scenarios.json"):
        try:
            texts.append((HERE / f).read_text(encoding="utf-8"))
        except OSError:
            pass
    V.set_vocab([normalize(x) for x in texts])


def audio_ref(text, voice):
    """Keshda tayyor bo'lsa — npcTurn.audio (v1.4.5). id ga fayl vaqti qo'shiladi: ovoz yangilansa — yangi URL."""
    f = V.cached_file(text, voice)
    if not f:
        return None
    try:
        st = f.stat()
    except OSError:
        return None
    key = (f.name, int(st.st_mtime))
    if key not in _AUDIO_DUR:
        _AUDIO_DUR[key] = V.mp3_duration_ms(f.read_bytes())
    aid = f"{f.stem}-{int(st.st_mtime)}"
    return {"id": aid, "url": f"/api/v1/voice/cache/{aid}.mp3", "durationMs": _AUDIO_DUR[key], "voice": voice}

VIOL_INFO = {   # tur: (ayirilgan ball, sabab, modda)
    "address": (2, "Sudga «Hurmatli sud!» deb murojaat qilinmadi.", "IPK-167"),
    "seated": (2, "Sudga tik turib murojaat qilinmadi.", "IPK-167"),
    "silence": (2, "Sud savoliga belgilangan vaqtda javob berilmadi.", None),
    "citation": (3, "Mavjud bo'lmagan modda keltirildi — sudni chalg'itish xavfi.", None),
    "order": (10, "Sud majlisi tartibi qo'pol buzildi (haqorat).", "IPK-167"),
    "injection": (5, "Sud majlisida ish bo'yicha bo'lmagan gap (rolni buzishga urinish).", None),
    "stage": (3, "Masala hozirgi bosqichda ko'rilmaydi.", "IPK-165"),
    "unexamined": (5, "Muzokarada sudda tekshirilmagan holatga tayanildi.", "IPK-173"),
    "recusal_unfounded": (2, "Rad qilish uchun qonunda nazarda tutilgan asos keltirilmadi.", "IPK-20"),
    "bribe": (100, "Sudga ta'sir o'tkazishga urinish — kasbiy etikaning jiddiy buzilishi.", None),
    "improper_evidence": (10, "Noqonuniy yo'l bilan olingan dalil (shaxsiy yozishmalar) — kasbiy etikaning qo'pol buzilishi.", None),
    "false_claim": (5, "Ish materiallariga zid da'vo (masalan, imzolangan hujjatni inkor etish) — sudni chalg'itish.", None),
    "disorder": (3, "Sud majlisi tartibi takroran buzildi — ogohlantirishlarga qaramay.", None),
    "interrupt": (2, "Sud gapi bo'lindi: gap oxirigacha tinglanmadi.", "IPK-167"),
}
REFLECT = {
    "davogar-vakili": "Javobgar dalolatnoma yo'qligini aytganda sizning eng kuchli javobingiz qaysi dalilga tayandi va nega?",
    "javobgar-vakili": "Haqiqiy sud asosiy qarzni to'liq undirdi, lekin penyani keskin kamaytirdi. Sizningcha, buning sababi nimada?",
}


def art_label(nid):
    """"FK-326" -> "FK 326-modda"; plenum -> "OXS163 4-band"."""
    if not nid:
        return None
    code, _, num = nid.partition("-")
    return f"{code} {num[1:]}-band" if num.startswith("p") else f"{code} {num}-modda"


_UZ1 = re.compile(r"(?<=[OoGg])['’‘`ʼ]")
_UZ2 = re.compile(r"(?<=\w)['’‘`](?=\w)")


def uz_norm(x):
    """Rasmiy o'zbek imlosi: oʻ/gʻ uchun ʻ (U+02BB), tutuq uchun ʼ (U+02BC). JSON ichida rekursiv."""
    if isinstance(x, str):
        return _UZ2.sub("ʼ", _UZ1.sub("ʻ", x)) if any(c in x for c in "'’‘`ʼ") else x
    if isinstance(x, list):
        return [uz_norm(v) for v in x]
    if isinstance(x, dict):
        return {k: uz_norm(v) for k, v in x.items()}
    return x

# Muhim lahzalar uchun manbalar (RAG bazasidagi norm_id)
KM_NORMS = {
    "KM1": ["IPK-62", "IPK-64", "IPK-167"],
    "KM2": ["FK-544", "FK-578", "FK-541", "OXS234-p9"],
    "KM3": ["FK-326", "FK-262", "FK-333", "OXS163-p4"],
    "KM4": ["IPK-173"],
}


def now_iso():
    d = datetime.now(timezone.utc)
    return d.strftime("%Y-%m-%dT%H:%M:%S.") + f"{d.microsecond // 1000:03d}Z"


def has(nt, *pats):
    return any(re.search(p, nt) for p in pats)


# ---------------------------------------------------------------- RAG va norma ma'lumotlari
class Norms:
    """RAG bazasidan modda nomi/havolasi (kesh) va qidiruv xizmati."""

    def __init__(self):
        self.known, self.info, self.ok = set(), {}, False
        if not DSN:
            print("OGOHLANTIRISH: LEXSIM_DSN yo'q — norma tekshiruvi o'chiq", flush=True)
            return
        try:
            import psycopg
            with psycopg.connect(DSN) as db:
                for nid, title, url, doc_title, dtype, art, punkt, amend in db.execute(
                        "SELECT DISTINCT ON (norm_id) norm_id, title, lex_url, doc_title, doc_type, article_no, punkt, amendments "
                        "FROM law_chunks WHERE valid_to IS NULL ORDER BY norm_id, chunk_id"):
                    self.known.add(nid)
                    dates = sorted(re.findall(r"(\d{2})\.(\d{2})\.(\d{4})", " ".join(amend or [])),
                                   key=lambda d: (d[2], d[1], d[0]))
                    self.info[nid] = {"title": title, "url": url, "doc_title": doc_title, "type": dtype,
                                      "art": str(punkt or art or ""),
                                      "edition": f"{dates[-1][2]}-{dates[-1][1]}-{dates[-1][0]}" if dates else None}
            self.ok = True
            print(f"Normalar: {len(self.known)} ta norm_id yuklandi", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"OGOHLANTIRISH: RAG bazasiga ulanib bo'lmadi: {e}", flush=True)

    def source(self, nid):
        i = self.info.get(nid)
        if not i or not (i["url"] or "").startswith(("https://lex.uz/", "https://www.lex.uz/")):
            return None
        doc = re.sub(r"^[\d.\s]+", "", (i["doc_title"] or ""))
        doc = re.sub(r"(?i)^o.zbekiston respublikasining\s+", "", doc).strip()
        if doc.isupper():
            doc = doc.capitalize()
        if i["type"] == "plenum":
            band = i["title"].rsplit(" — ", 1)[-1]
            org = "Oliy xo'jalik sudi" if nid.startswith("OXS") else "Oliy sud"
            title = f"{org} Plenumi qarori — {band}"
        else:
            title = f"{doc} — {i['title']}"
        src = {"title": title[:200], "officialUrl": i["url"], "verifiedAt": None}   # mentor tasdiqlamaguncha
        if i.get("art"):
            src["articleNumber"] = art_label(nid)
        if i.get("edition"):
            src["effectiveAt"] = i["edition"]          # oxirgi tahrir sanasi (lex.uz izohidan)
        return src

    def text(self, nid, limit=900):
        """Modda matni bazadan (RAG natijasida matn yo'q) — AI sudyaga manba sifatida. Kesh bilan."""
        c = self.__dict__.setdefault("_txt", {})
        if nid in c:
            return c[nid]
        if not (self.ok and DSN and nid in self.known):
            return None
        try:
            import psycopg
            with psycopg.connect(DSN, connect_timeout=3) as db:
                rows = db.execute("SELECT text_latn FROM law_chunks WHERE norm_id=%s AND valid_to IS NULL ORDER BY chunk_id",
                                  (nid,)).fetchall()
            t = re.sub(r"\s+", " ", " ".join(r[0] for r in rows)).strip()[:limit] or None
        except Exception as e:  # noqa: BLE001
            print(f"NORMS.text {nid}: {type(e).__name__}", flush=True)
            return None
        if len(c) > 500:
            c.clear()
        c[nid] = t
        return t

    def search(self, q, case_type="IPK", k=5):
        if not SETTINGS["rag"]:
            return {"results": [], "related": [], "confident": False, "skipped": True}
        try:
            req = urllib.request.Request(RAG_URL + "/search", data=json.dumps(
                {"q": q[:1500], "case_type": case_type, "k": k}).encode(), headers={"Content-Type": "application/json", **({"X-API-Key": RAG_KEY} if RAG_KEY else {})})
            with M.part("rag"), urllib.request.urlopen(req, timeout=RAG_TIMEOUT) as r:
                res = json.loads(r.read())
            M.note(rag_inner=res.get("ms"))
            return res
        except Exception as e:  # noqa: BLE001
            return {"error": str(e), "results": [], "related": [], "confident": False}


NORMS = None


# ---------------------------------------------------------------- case laboratoriyasi (caselab.py)
def lab_rag(story, case_type, hint="", codes=None):
    """Holat bo'yicha bazadan mos moddalar: {norm_id: {label, url, title}} — AI faqat shulardan tanlaydi."""
    out, raw = {}, 0
    qs = [story[:1500]] + ([story[-1500:]] if len(story) > 1500 else []) + ([hint + ". " + story[:400]] if hint else [])
    rag_ct = case_type if case_type in ("IPK", "FPK") else None    # RAG xizmati faqat IPK/FPK filtrini biladi —
    for q in qs:                                                  # qolganlari (JPK, MAM) uchun filtrsiz + kod bo'yicha saralash
        r = NORMS.search(q, rag_ct, k=5 if rag_ct else 12)
        if r.get("error"):
            print(f"CASELAB rag xato: {r['error'][:120]}", flush=True)
        raw += len(r.get("results") or [])
        for x in (r.get("results") or []):
            nid = x.get("norm_id")
            if codes and nid and not any(nid.startswith(c + "-") for c in codes):
                continue
            src = NORMS.source(nid) if nid else None
            if src and nid not in out:
                out[nid] = {"label": art_label(nid), "url": src["officialUrl"], "title": NORMS.info.get(nid, {}).get("title") or ""}
    if raw and not out:
        print(f"CASELAB rag: {raw} natija, lekin lex.uz manbasi topilmadi", flush=True)
    return out


def lab_allowed(case):
    """Muallif tahririda: faqat bazada bor moddalar qoladi."""
    out = {}
    legal = case.get("legal") if isinstance(case, dict) else None
    for x in legal if isinstance(legal, list) else []:
        nid = x.get("normId") if isinstance(x, dict) and isinstance(x.get("normId"), str) else None
        src = NORMS.source(nid) if nid and NORMS and nid in NORMS.known else None
        if src:
            out[nid] = {"label": art_label(nid), "url": src["officialUrl"]}
    return out


def sem_scores(key, text):
    """Talaba gapini lahza namunalari bilan solishtirish (GPU reranker). None — reranker ishlamadi."""
    a = SEMCFG["anchors"].get(key)
    if not a or not SETTINGS.get("sem") or not SEM_KEY:
        return None
    ck = (key, text)
    if ck in _sem_cache:
        return _sem_cache[ck]
    if V.gpu_down("rerank"):                         # GPU reranker o'chiq — kutmasdan kalit so'zlar bilan
        return None
    pos, neg = a["pos"], a["neg"] + SEMCFG["common_neg"]
    fal = [f["text"] if isinstance(f, dict) else f for f in a.get("false", [])]
    t0 = time.time()
    try:
        req = urllib.request.Request(SEM_URL, method="POST", data=json.dumps({"query": text[:1500], "texts": pos + neg + fal}).encode(),
                                     headers={"Content-Type": "application/json", "X-Key": SEM_KEY})
        with M.part("rerank"), urllib.request.urlopen(req, timeout=SEM_TIMEOUT) as r:
            sc = json.loads(r.read())["scores"]
    except Exception as e:  # noqa: BLE001
        V.gpu_failed("rerank")
        M.count("sem_fail", f"{type(e).__name__}")
        return None
    res = {"pos": round(max(sc[:len(pos)]), 3), "neg": round(max(sc[len(pos):len(pos) + len(neg)]), 3),
           "false": round(max(sc[len(pos) + len(neg):]), 3) if fal else 0.0, "ms": round((time.time() - t0) * 1000)}
    if fal:
        fs = sc[len(pos) + len(neg):]
        res["false_i"] = max(range(len(fs)), key=lambda i: fs[i])
    M.count("sem_ok")
    if len(_sem_cache) > 2000:
        _sem_cache.clear()
    _sem_cache[ck] = res
    return res


def sem_level(r):
    """(daraja, materiallarga_zidmi). Kalit soʻz darajasi bilan solishtirish chaqiruvchida."""
    if not r:
        return None, False
    th = SEMCFG["thresholds"]
    if r["false"] >= th["false"] and r["false"] > r["pos"]:
        return 0, True
    if r["pos"] >= th["good"] and r["pos"] > r["neg"]:
        return 3, False
    if r["pos"] >= th["partial"] and r["pos"] > r["neg"]:
        return 2, False
    return 0, False

# ---------------------------------------------------------------- LLM (raqib advokat)
CYR = re.compile(r"[\u0400-\u04FF]")
LEAK = re.compile(r"qanoatlantiril|undirilsin|rad (qilin|etil)sin|hal qiluv qarori|sun'iy intellekt|\bai\b|\bmodel\b|prompt|namuna")
DENY = re.compile(r"(hisob-?faktura\w*[^.]{0,40}(imzolanmagan|mavjud emas|yo'q|soxta|qalbaki))|foydalanmagan|shartnoma\w* (tuzilmagan|yo'q)")
def llm_check(out, student, template, allowed_refs=None, numbers="", who="opponent"):
    """LLM chiqishini tekshirish: None — rad etildi (shablon ishlatiladi)."""
    out = re.sub(r"<think>.*?(</think>|$)", "", out, flags=re.S).strip().strip('"').strip()
    out = re.sub(r"^\w[\w' ]{0,25} vakili:\s*", "", out)          # "Javobgar vakili:" prefiksini olib tashlash
    out = re.sub(r"\b(FK|IPK)-(\d+)\s+(modda\w*)", r"\1 \2-\3", out)
    out = re.sub(r"\b(FK|IPK)-(\d+)\b(?!-)", r"\1 \2-modda", out)
    if not (20 <= len(out) <= 600) or CYR.search(out):
        return None, "uzunlik/kirill"
    sents = re.split(r"(?<=[.!?])\s+", out)
    out = " ".join(sents[:3])
    if out[-1] not in ".!?":
        out = out.rsplit(".", 1)[0] + "." if "." in out else None
        if not out:
            return None, "chala gap"
    n = normalize(out)
    if LEAK.search(n) or DENY.search(n):
        return None, "taqiqlangan mazmun"
    allowed = normalize(student + " " + template + " " + (numbers or ""))
    for num in re.findall(r"\d[\d.,]*", n):
        if num.rstrip(".,") not in allowed:
            return None, f"yangi raqam {num}"
    refs = set(exact_refs(n))
    refs |= {"FK-" + x for x in re.findall(r"fuqarolik kodeks\w*\s+(\d+)", n)}
    refs |= {"IPK-" + x for x in re.findall(r"protsessual kodeks\w*\s+(\d+)", n)}
    for r in refs:
        if (NORMS.ok and r not in NORMS.known) or (allowed_refs is not None and r not in allowed_refs):
            return None, f"ruxsat etilmagan modda {r}"
    if who == "judge":                                   # sudya o'ziga «Hurmatli sud» demaydi
        out = re.sub(r"^\s*(Sudya|Raislik qiluvchi)\s*:\s*", "", out)
        out = re.sub(r"\s*Hurmatli sud[,!]?\s*", " ", out).strip()
        out = re.sub(r"([.!?]\s+)([a-zʻʼ'‘’])", lambda m: m.group(1) + m.group(2).upper(), out)
        return (out[0].upper() + out[1:]) if out else None, (None if out else "bo'sh")
    head, rest = out[:14], out[14:]
    out = head + re.sub(r"\s*Hurmatli sud[,!]?\s*", " ", rest).replace("  ", " ")    # takroriy murojaatni olib tashlash
    out = re.sub(r"([.!?]\s+)([a-zʻʼ'‘’])", lambda m: m.group(1) + m.group(2).upper(), out)   # gap boshi — bosh harf
    if not n.startswith("hurmatli sud"):
        out = "Hurmatli sud, " + out[0].lower() + out[1:]
    return out, None


LEVEL_STYLE = {"beginner": "Qisqa va yumshoq gapir, namunaga yaqin qol.",
               "intermediate": "Raqib bo'l: talaba gapidagi eng zaif joyni top va unga aniq e'tiroz bildir.",
               "advanced": ("Shaxmatchi raqib bo'l: talabaning har xatosini kutib tur, uning o'zi aytgan gapini unga qarshi "
                            "ishlat, javobsiz qolgan e'tirozni qayta ko'tar; bir qadam oldinni o'ylab, keyingi bosqichga "
                            "zamin tayyorla. Faqat haqiqatan aytilgan gap va ish faktlari — yolg'on va soxta dalil yo'q.")}


def llm_prompt(name, role, key, student, level="beginner"):
    r, g = ROLES[role], ROLES["advokat_umumiy"]
    lz = r["lahzalar"][key]
    sysm = (f"Sen iqtisodiy suddagi {name.lower()}san: {r['kim']} O'zbek tilida, lotin yozuvida gapir. "
            f"Pozitsiyang: {r['pozitsiya']}\nUslub: " + " ".join(g["uslub"]) +
            "\nTaqiq: " + "; ".join(r["taqiq"]) + ". Faqat shu moddalarni tilga olishing mumkin: " + ", ".join(r["ruxsat_moddalar"]) +
            ". Javobing 2 ta gapdan oshmasin. " + LEVEL_STYLE.get(level, ""))
    user = (f"Raqib aytdi: \"{student[:500]}\"\nVazifang: {lz['maqsad']}\n"
            f"Namuna (shu ma'noda, raqib gapiga moslab ayt): {lz['namuna']}")
    return sysm, user, lz["namuna"], set(r["ruxsat_moddalar"])


STAGE_UZ = {"ishtirokchilar": "ishtirokchilarni aniqlash", "rad": "rad bildirish", "huquqlar": "huquqlarni tushuntirish",
            "oldingi": "iltimosnomalar", "tushuntirish": "taraflarning tushuntirishlari", "dalillar": "dalillarni tekshirish",
            "penya": "penya bo'yicha iltimosnoma", "qoshimcha": "qo'shimcha materiallar", "muzokara": "sud muzokaralari",
            "yakun": "yakun"}


def llm_aihub(name, role, key, student, level, numbers, ctx=None):
    student = LAB.redact(student)[0]                     # shaxsiy ma'lumot AI'ga bormasin (telefon, pasport, JSHSHIR...)
    sysm, user, template, allowed = llm_prompt(name, role, key, student, level)
    sc = next(iter(SCEN.values()))
    ctx = ctx or {}
    user = ("ISH FAKTLARI: " + sc.get("ai_facts", "") + "\n" +
            (f"MAJLIS BOSQICHI: {STAGE_UZ.get(ctx.get('stage'), ctx.get('stage'))}\n" if ctx.get("stage") else "") +
            ("OXIRGI GAPLAR:\n" + "\n".join(ctx["history"]) + "\n" if ctx.get("history") else "")
            + ("RAQIB KUZATUVI (talabaning zaif joylari — ulardan qonuniy foydalan, faqat haqiqatan aytilganini keltir): "
               + "; ".join(ctx["weak"]) + "\n" if ctx.get("weak") else "") + user)
    LLM_STATS["calls"] += 1
    t0 = time.time()
    with M.part("llm"):
        out, model, ms, why = AIH.ask(sysm, user, float(SETTINGS["llm_timeout"]))
    res = None
    if out:
        res, why = llm_check(out, student, template, allowed, numbers)
    LLM_STATS["last_ms"] = round((time.time() - t0) * 1000)
    LLM_STATS["ok" if res else "fallback"] += 1
    LLM_STATS["last_error"] = why
    M.count("llm_ok" if res else "llm_fallback", None if res else why)
    M.note(llm={"ms": LLM_STATS["last_ms"], "ttft_ms": None, "chunks": 1, "model": model,
                "result": "ok" if res else "shablon", "why": why, "key": key})
    print(f"LLM aihub/{model} {LLM_STATS['last_ms']} ms {'OK' if res else 'shablon (' + str(why) + ')'}: {(res or out or '')[:120]!r}", flush=True)
    return res


JUDGE_ALLOWED = None
TAC.load(HERE / "tactics.json")                          # AI raqib va sudya taktikalari (modul yuklanganda — testlar ham ko'radi)
LEGAL_Q = re.compile(r"\bmodda|\bkodeks|\bqonun|\bplenum|\bhuquq|\bmumkinmi\b|\bshartmi\b|\bqanday asos|\bqaysi asos|\?")


def llm_judge(eng, student, purpose, template):
    """Tayyor javob topilmaganda — AI sudya (har qanday darajada). None: shablon ishlatiladi.
    Chegaralar: qaror chiqarmaydi, yangi fakt/raqam/modda yo'q (llm_check), 1–2 gap, joriy bosqich savoliga qaytaradi."""
    global JUDGE_ALLOWED
    student = LAB.redact(student)[0]                     # shaxsiy ma'lumot AI'ga bormasin
    if JUDGE_ALLOWED is None:
        JUDGE_ALLOWED = {a for arts in T_ART.values() for a in (arts or [])} | set(ROLES.get("advokat_umumiy", {}).get("ruxsat_moddalar", []))
        for r in ROLES.values():
            JUDGE_ALLOWED |= set(r.get("ruxsat_moddalar", []) if isinstance(r, dict) else [])
    s = eng.s
    sc = SCEN[s["scenarioId"]]
    ctx = eng.llm_ctx()
    allowed = set(JUDGE_ALLOWED)
    srcs = []
    if LEGAL_Q.search(normalize(student)) and NORMS and NORMS.ok and SETTINGS["rag"]:   # huquqiy savol — lex.uz'dan manba
        r = NORMS.search(student[:600], s.get("case_type") or "IPK")
        if r.get("confident"):
            for x in (r.get("results") or [])[:3]:
                nid = x.get("norm_id")
                txt = NORMS.text(nid) if nid else None
                if txt:
                    srcs.append(f"[{art_label(nid)}] {x.get('title', '')}: {txt}")
                    allowed.add(nid)
    sysm = ("Sen O'zbekiston iqtisodiy sudining tajribali va xushmuomala sudyasisan. O'quv sud majlisini IPK tartibida olib boryapsan. "
            f"Talaba — {ROLE_NAME.get(s['student_role'], 'taraf vakili')}. Odamdek, lekin sud odobi bilan gapir: talabaning gapiga "
            "aniq munosabat bildir (tan ol yoki nega mumkin emasligini qisqa tushuntir) va majlisni joriy bosqich savoliga qaytar. "
            "Ish bo'yicha qaror chiqarma, kim haqligini aytma, yangi fakt, raqam yoki sana o'ylab topma. Faqat shu moddalarni "
            "tilga olishing mumkin: " + ", ".join(sorted(allowed)) + ". O'zbek tilida, lotin yozuvida, 1–2 gap."
            + (" Talaba huquqiy savol berdi: MANBALAR'dagi moddaga tayanib, sud nimani tekshirishini qisqa ayt "
               "(ish natijasini oldindan aytma). Manbada javob bo'lmasa, buni taraf o'zi asoslashi kerakligini ayt." if srcs else ""))
    user = ("ISH FAKTLARI: " + sc.get("ai_facts", "") + "\n"
            f"MAJLIS BOSQICHI: {STAGE_UZ.get(ctx.get('stage'), ctx.get('stage'))}\n"
            + ("OXIRGI GAPLAR:\n" + "\n".join(ctx["history"]) + "\n" if ctx.get("history") else "")
            + ("MANBALAR (lex.uz, rasmiy matn):\n" + "\n".join(srcs) + "\n" if srcs else "")
            + f"TALABA HOZIR AYTDI: \"{student[:600]}\"\nVAZIYAT: {purpose}\n"
            f"Shu ma'nodagi tayyor gap (talaba gapiga moslab, o'z so'zing bilan ayt): {template}")
    LLM_STATS["calls"] += 1
    t0 = time.time()
    with M.part("llm"):
        if LLM_PROVIDER == "aihub":
            out, model, ms, why = AIH.ask(sysm, user, float(SETTINGS["llm_timeout"]), tail="Faqat sudya gapini yoz (1–2 gap)")
        else:
            out, model, why = None, None, "provayder yo'q"
    res = None
    if out:
        res, why = llm_check(out, student, template + " " + " ".join(srcs), allowed, sc.get("numbers", ""), who="judge")
    LLM_STATS["last_ms"] = round((time.time() - t0) * 1000)
    LLM_STATS["ok" if res else "fallback"] += 1
    LLM_STATS["last_error"] = why
    M.count("llm_judge_ok" if res else "llm_judge_fallback", None if res else why)
    print(f"LLM judge {LLM_STATS['last_ms']} ms {'OK' if res else 'shablon (' + str(why) + ')'}: {(res or out or '')[:120]!r}", flush=True)
    return res


def llm_opponent(name, role, key, student, level="beginner", numbers="", ctx=None):
    if LLM_PROVIDER == "aihub":
        return llm_aihub(name, role, key, student, level, numbers, ctx)
    if not LLM_KEY:
        LLM_STATS["last_error"] = "kalit yo'q"
        return None
    sysm, user, template, allowed = llm_prompt(name, role, key, student, level)
    body = {"model": LLM_MODEL, "stream": True, "max_tokens": 130, "temperature": 0.4,
            "messages": [{"role": "system", "content": sysm}, {"role": "user", "content": user}]}
    if "googleapis.com" in LLM_URL:                  # Gemini (OpenAI-mos): o'ylashsiz — birinchi so'z tezroq
        body["reasoning_effort"] = "none"
    else:                                            # Qwen (colibri)
        body["enable_thinking"] = False
    LLM_STATS["calls"] += 1
    t0, out, ttft, chunks = time.time(), "", None, 0
    tmo = float(SETTINGS["llm_timeout"])
    try:
        req = urllib.request.Request(LLM_URL, data=json.dumps(body).encode(), headers={
            "Content-Type": "application/json", "Authorization": "Bearer " + LLM_KEY})
        with M.part("llm"), urllib.request.urlopen(req, timeout=tmo) as r:
            for raw in r:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:") or line == "data: [DONE]":
                    continue
                d = json.loads(line[5:])
                if d.get("choices"):
                    piece = d["choices"][0].get("delta", {}).get("content") or ""
                    if piece:
                        chunks += 1
                        ttft = ttft or (time.time() - t0) * 1000
                    out += piece
                if time.time() - t0 > tmo:
                    raise TimeoutError("LLM vaqti tugadi")
                if len(re.findall(r"[.!?](\s|$)", out)) >= 2:   # 2 ta gap yetarli — erta to'xtatamiz
                    break
        res, why = llm_check(out, student, template, allowed, numbers)
    except Exception as e:  # noqa: BLE001
        res, why = None, f"{type(e).__name__}: {e}"
    LLM_STATS["last_ms"] = round((time.time() - t0) * 1000)
    LLM_STATS["ok" if res else "fallback"] += 1
    LLM_STATS["last_error"] = why
    M.count("llm_ok" if res else "llm_fallback", None if res else why)
    M.note(llm={"ms": LLM_STATS["last_ms"], "ttft_ms": round(ttft) if ttft else None, "chunks": chunks,
                "result": "ok" if res else "shablon", "why": why, "key": key})
    print(f"LLM {LLM_STATS['last_ms']} ms {'OK' if res else 'shablon (' + str(why) + ')'}: {(res or out)[:120]!r}", flush=True)
    return res


# ---------------------------------------------------------------- sessiya saqlash
_db_lock = threading.Lock()
_sess_locks, _sess_cache = {}, {}


def db():
    c = sqlite3.connect(STATE_DB, check_same_thread=False)
    c.execute("CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, data TEXT, updated REAL)")
    return c


_DB = None


def save(s):
    with _db_lock:
        _DB.execute("INSERT OR REPLACE INTO sessions VALUES (?,?,?)", (s["id"], json.dumps(s, ensure_ascii=False), time.time()))
        _DB.commit()


def load(sid):
    if sid in _sess_cache:
        return _sess_cache[sid]
    with _db_lock:
        r = _DB.execute("SELECT data FROM sessions WHERE id=?", (sid,)).fetchone()
    if r:
        d = json.loads(r[0])
        if d.get("pending") and sid not in PENDING:     # server qayta ishga tushgan — tugallanmagan turn
            d["pending"] = None
        _sess_cache[sid] = d
        return d
    return None


def lock_for(sid):
    with _db_lock:
        return _sess_locks.setdefault(sid, threading.Lock())


# ---------------------------------------------------------------- dvigatel
class ApiError(Exception):
    def __init__(self, status, code, message, retry_after=None):
        super().__init__(message)
        self.status, self.code, self.message, self.retry_after = status, code, message, retry_after


class Engine:
    """Bitta so'rov davomida eventlarni yig'adi va sessiya holatini o'zgartiradi."""

    def __init__(self, s, dry=False):
        self.s, self.events = s, []
        self.dry, self.would_llm = dry, False          # dry: LLM kerak bo'ladimi — oldindan tekshirish
        self.forced, self.voice = {}, False              # forced: xato variant tanlansa lahza darajasi chegarasi
        self.cur_tid = None
        self.next_engine, self.next_grounding = None, None   # keyingi npcTurn manbasi: bank | llm | script

    # --- event va turn yordamchilari
    def emit(self, typ, payload):
        self.s["sequence"] += 1
        ev = {"eventId": "evt_" + uuid.uuid4().hex, "sequence": self.s["sequence"], "sessionId": self.s["id"],
              "timestamp": now_iso(), "type": typ, "payload": payload}
        self.s["events"].append(ev)
        self.events.append(ev)

    def add_turn(self, speaker, text, emotion=None, role=None, scene=None, articles=None):
        idx = len(self.s["turns"])
        t = {"id": f"t_{idx + 1}", "index": idx, "speaker": speaker, "text": text, "at": now_iso()}
        if emotion:
            t["emotion"] = emotion
        if role:
            t["role"] = role
        if scene:
            t["scene"] = scene
        if articles:
            t["articles"] = [{"id": a, "label": art_label(a), "url": NORMS.info[a]["url"]}
                             for a in articles if a in NORMS.info]
        self.s["turns"].append(t)
        return t

    def user(self, text):
        t = self.add_turn("user", text)
        self.emit("dialogue.userTurn", {"turn": t})
        return t

    def say(self, role, text, gesture="none", reveal=(), scene=None, art=None, emotion=None, reactions=None):
        """Bitta turn = bitta so'zlovchi. role: judge | secretary | opponent | system.
        emotion/gesture/reactions (v15 §3, §7.3): ovoz ohangi, yuz va harakat bir-biriga mos bo'lsin."""
        s = self.s
        st = PROC.TEXT_STYLE.get(text) if role == "judge" else None
        if st:
            emotion = emotion or st[0]
            gesture = gesture if gesture != "none" else st[1]
            reactions = reactions or st[2]
        if s.get("strong_pending") and role in ("judge", "opponent") and not self.dry:   # talaba kuchli dalil keltirdi
            if role == "judge":
                reactions = list(reactions or []) + [("opponent", "uncertain")]
            else:
                gesture = gesture if gesture != "none" else "lean-in"
                s["strong_pending"] = False
        if scene:
            s.setdefault("scene", {}).update(scene)
        tag, grounding = self.next_engine or "script", self.next_grounding
        self.next_engine = self.next_grounding = None
        if role == "system":
            t = self.add_turn("system", text, scene=scene)
            t["engine"] = "script"
            self.emit("dialogue.npcTurn", {"turn": t, "revealedFactIds": []})
            return t
        if role == "judge":
            base = emotion or {"shake-head": "neutral", "lean-in": "uncertain", "nod": "calm"}.get(gesture, "calm")
            meter = self.emotion()                         # sabr tugayotgan bo'lsa — yuzda ham ko'rinsin
            emo = meter if meter in ("upset", "impatient") and base in ("calm", "neutral") else base
        elif role == "opponent":
            emo = emotion or "calm"
        else:
            emo = emotion or "neutral"
        t = self.add_turn("npc", text, emo, role, scene, art)
        if gesture in GESTURES and gesture != "none":
            t["gesture"] = gesture
        if reactions:
            t["reactions"] = [{"role": r, "emotion": e} for r, e in reactions if r != role][:5]
        t["engine"] = tag                                    # frontend: ko'rsatish/log uchun
        if not self.dry:
            au = audio_ref(text, ROLE_VOICE.get(role, "male"))
            if au:
                t["audio"] = au
        if grounding:
            t["grounding"] = grounding
        new = [f for f in reveal if f not in s["facts"]]
        for f in new:
            s["facts"][f] = t["index"]
        self.emit("dialogue.npcTurn", {"turn": t, "revealedFactIds": new})
        if role == "judge":
            s["npc"] = {"emotion": emo, "intensity": 0.5 if emo in ("neutral", "calm") else 0.7}
            self.emit("npc.emotion", {"npcId": "sudya", "emotion": emo, "intensity": s["npc"]["intensity"]})
            if gesture in GESTURES and gesture != "none":
                self.emit("npc.gesture", {"npcId": "sudya", "clip": gesture})
        if len(s["facts"]) >= 2:
            self.objective("clarify")
        return t

    def npc(self, text, gesture="none", reveal=(), scene=None, art=None, emotion=None, reactions=None):
        return self.say("judge", text, gesture, reveal, scene, art, emotion, reactions)

    def t(self, key, gesture="none", reveal=(), scene=None, **fmt):
        """Sudya shabloni + uning IPK asosi + ohangi (T_STYLE)."""
        text = T[key].format(**fmt) if fmt else T[key]
        emo, g, rx = T_STYLE.get(key, (None, "none", None))
        return self.npc(text, gesture if gesture != "none" else g, reveal, scene, T_ART.get(key), emo, rx)

    def unclear(self, nt, tid):
        """v1.4.5 §5: matn bo'sh / ≤ 2 so'z va mazmunsiz / ish lug'atiga umuman tegmaydi."""
        s = self.s
        if s["stage"] == "yakun" or (s.get("optdec") or {}).get(tid):
            return False
        rest = re.sub(r"[^\w' ]", " ", re.sub(r"\bhurmatli\s+sud\w*", " ", nt))
        words = [w for w in rest.split() if w]
        if not words:
            return True
        vocab = V._VOCAB["stems"]
        if not vocab:
            return False
        if len(words) <= 2:
            if s["stage"] in YESNO_STAGES and any(w in SHORT_OK for w in words):
                return False
            return not any(len(w) >= 5 and w[:5] in vocab for w in words)
        content = [w for w in words if len(w) >= 3 and w not in V.STOP]
        return bool(content) and not any(w[:5] in vocab for w in content)

    def reprimand(self, kind, tid, speak=True):
        """Kuchayib boradigan tanbeh (v15 §7.2): bir xil xato takrorlansa — qattiqroq; har xil so'zlar bilan."""
        s, R = self.s, PROC.CFG["reprimand"]
        lv = s.get("level", "beginner")
        c = s.setdefault("repr_count", {})
        c[kind] = n = c.get(kind, 0) + 1
        i = min(n - 1, 3 if lv == "advanced" else 2)
        soft = kind in ("address", "seated") and n > 3          # murojaat shakli: 3-martadan keyin har gal rasmiy ogohlantirish emas
        if soft:
            i = 1
            speak = speak and n % 3 == 0
        st = R["steps"][i]
        self.viol(kind, tid)
        v = s["violations"][-1]
        v["points"], v["step"] = st["points"][lv], i + 1
        if not v["points"]:
            v["free"] = True                               # beginner, 1-marta: eslatma, ball yo'q
        if st.get("ethics"):
            self.viol("disorder", tid)
        self.meters(-3 * (i + 1), -1 if i else 0)
        if speak:
            vs = R[kind][i]
            line = vs[(n + (s.get("seed") or 0)) % len(vs)].format(role_name=self.rn())
            self.npc(line, gesture=st["gesture"], emotion=st["emotion"], reactions=SCOLD,
                     art=["IPK-167"] if i < 2 else None)

    def clerk(self, key, scene=None):
        return self.say("secretary", T[key], scene=scene, art=T_ART.get(key))

    def system(self, text, scene):
        return self.say("system", text, scene=scene)

    def reply_context(self, key):
        """Raqib nimaga javob beryapti: odatda talabaning oxirgi gapi; yakuniy nutqda — oxirgi 3 ta gapi."""
        users = [t["text"] for t in self.s["turns"] if t["speaker"] == "user"]
        return " ".join(users[-3:]) if key == "closing" else (users[-1] if users else "")

    def pick_reply(self, key):
        """Tayyor javoblar banki: talaba gapiga eng mos variant (reranker). (variant, baho) yoki (None, None)."""
        bank = REPLIES["bank"].get(self.s["opponent_role"], {}).get(key)
        if not bank:
            return None, None
        ctx = self.reply_context(key)
        cands = [v for v in bank if not v.get("generic") and v["id"] not in self.s.get("used_replies", [])]
        texts, owner = [], []
        for i, v in enumerate(cands):
            for w in v["when"]:
                texts.append(w)
                owner.append(i)
        sc = nlu_rerank(ctx, texts) if texts and ctx else None
        per = {}
        for score, i in zip(sc or [], owner):
            per[i] = max(score, per.get(i, 0.0))
        good = [(i, sc_) for i, sc_ in per.items() if sc_ >= REPLIES["threshold"]]
        bi = PROC.pick_tie(good, self.s.get("seed"), f"{key}:{len(self.s['turns'])}") if good else None
        best = per.get(bi, max(per.values()) if per else 0.0)
        generic = next((v for v in bank if v.get("generic")), bank[0])
        if bi is not None and best >= REPLIES["threshold"]:
            return cands[bi], round(best, 3)
        return (None, round(best, 3)) if sc is not None else (generic, None)

    def opp(self, key, reveal=()):
        o = OPP[self.s["opponent_role"]]
        lz = ROLES[self.s["opponent_role"]].get("lahzalar", {}).get(key)
        line = lz["namuna"] if lz else o[key]
        v, score = self.pick_reply(key)
        bank = REPLIES["bank"].get(self.s["opponent_role"], {}).get(key)
        if bank is not None:
            log = {"key": key, "source": "bank", "id": v["id"] if v else None, "score": score}
            self.next_engine = "bank"
            if v and not v.get("generic"):                   # mos tayyor javob — darhol
                line = v["text"]
                self.s.setdefault("used_replies", []).append(v["id"])
                self.s["engine_used"] = "scripted"
            elif (SETTINGS["llm"] and lz
                  and not self.s["flags"].get("llm_used_this_turn")):   # kutilmagan gap — LLM (v1.5: hamma darajada, 202 bilan)
                self.s["flags"]["llm_used_this_turn"] = True
                if self.dry:
                    self.would_llm = True
                else:
                    last = self.reply_context(key)
                    gen = llm_opponent(o["name"], self.s["opponent_role"], key, last, self.s.get("level", "beginner"), ctx=self.llm_ctx(),
                                   numbers=SCEN[self.s["scenarioId"]].get("numbers", ""))
                    self.s["engine_used"] = "llm" if gen else "scripted"
                    log.update(source="llm" if gen else "generic")
                    if gen:
                        self.next_engine, self.next_grounding = "llm", {"articleIds": exact_refs(normalize(gen))}
                    line = gen or next((x["text"] for x in bank if x.get("generic")), line)
            else:                                            # mos variant yo'q — umumiy javob
                line = next((x["text"] for x in bank if x.get("generic")), line)
                log["source"] = "generic"
            if not self.dry:
                self.s.setdefault("reply_log", []).append(log)
                M.count("reply_" + log["source"])
            return self.say("opponent", line, reveal=reveal)
        if (SETTINGS["llm"] and lz and key in LLM_KEYS and self.s.get("level") == "advanced"
                and not self.s["flags"].get("llm_used_this_turn")):          # beginner/intermediate — LLM yo'q (≤ 2 s)
            self.s["flags"]["llm_used_this_turn"] = True
            if self.dry:
                self.would_llm = True
            else:
                last = next((t["text"] for t in reversed(self.s["turns"]) if t["speaker"] == "user"), "")
                gen = llm_opponent(o["name"], self.s["opponent_role"], key, last, self.s.get("level", "beginner"), ctx=self.llm_ctx(),
                                   numbers=SCEN[self.s["scenarioId"]].get("numbers", ""))
                self.s.setdefault("llm_log", []).append({"key": key, "used": bool(gen), "text": gen})
                self.s["engine_used"] = "llm" if gen else "scripted"
                if gen:
                    self.next_engine, self.next_grounding = "llm", {"articleIds": exact_refs(normalize(gen))}
                line = gen or line
        return self.say("opponent", line, reveal=reveal)

    def repeat_last(self):
        """Talabaning oldingi gapidan keyin aytilgan NPC gaplarini (sudya/kotib/raqib) aynan qayta aytadi — audio keshdan."""
        turns = self.s["turns"]
        users = [i for i, t in enumerate(turns) if t.get("speaker") == "user"]
        if len(users) < 2:
            return False
        block = [t for t in turns[users[-2] + 1: users[-1]] if t.get("speaker") == "npc" and t.get("text")]
        if not block:
            return False
        for t in block[-3:]:
            self.say(t.get("role") or "judge", t["text"], t.get("gesture") or "none", (), None, None, t.get("emotion"))
        return True

    def ai_judge(self, text, purpose, template, tid=None):
        """Tizimda aniq javob yo'q — AI sudya suhbatni davom ettiradi (v1.5). True: AI javob berdi (yoki dry-run'da beradi)."""
        s = self.s
        words = [w for w in re.sub(r"[^\w' ]", " ", normalize(text)).split() if len(w) >= 2]
        if (not SETTINGS["llm"] or s["flags"].get("llm_used_this_turn") or len(words) < 4
                or s.get("ai_judge_n", 0) >= AI_JUDGE_MAX or s["stage"] == "yakun"):
            return False
        s["flags"]["llm_used_this_turn"] = True
        if self.dry:
            self.would_llm = True
            return True
        gen = llm_judge(self, text, purpose, template)
        if not gen:
            return False
        s["ai_judge_n"] = s.get("ai_judge_n", 0) + 1
        s["engine_used"] = "llm"
        self.next_engine, self.next_grounding = "llm", {"articleIds": exact_refs(normalize(gen))}
        self.npc(gen, gesture="lean-in", emotion="calm")
        s.setdefault("llm_log", []).append({"key": "judge", "used": True, "text": gen, "purpose": purpose})
        return True

    def llm_ctx(self, n=10):
        """LLM uchun majlis konteksti: bosqich va oxirgi gaplar (kim nima dedi)."""
        who = {"user": ROLE_NAME.get(self.s["student_role"], "Talaba"), "judge": "Sudya", "opponent": OPP[self.s["opponent_role"]]["name"],
               "secretary": "Kotib"}
        hist = []                                        # NPC gaplari speaker="npc", kimligi role'da — avval tarixga tushmasdi
        for t in self.s["turns"][-n:]:
            k = t.get("role") if t.get("speaker") == "npc" else t.get("speaker")
            if k in who and t.get("text"):
                hist.append(f"{who[k]}: {LAB.redact(t['text'][:300])[0] if k == 'user' else t['text'][:300]}")
        return {"stage": self.s["stage"], "history": hist, "weak": ADV.weak_points(self.s)}

    def objective(self, oid):
        for o in self.s["objectives"]:
            if o["id"] == oid and not o["done"]:
                o["done"] = True
                self.emit("objective.updated", {"objectiveId": oid, "done": True})

    def status(self, st):
        if self.s["status"] != st:
            self.s["status"] = st
            self.emit("session.status", {"status": st})

    def emotion(self):
        p, tr = self.s["meters"]["patience"], self.s["meters"]["trust"]
        if p < 25:
            return "upset"
        if p < 45:
            return "impatient"
        if tr >= 72:
            return "reassured"
        if tr >= 55:
            return "calm"
        return "neutral"

    def meters(self, dp=0, dt=0):
        m = self.s["meters"]
        m["patience"] = max(0, min(100, m["patience"] + dp))
        m["trust"] = max(0, min(100, m["trust"] + dt))

    def km(self, kid, level, turn_id):
        if kid in self.forced:
            level = min(level, self.forced[kid])
        level = min(level, PROC.cap_for(self))           # aniqlashtirish so'ralgan bosqichda — chegaralangan
        if level >= 4 and kid in ("KM2", "KM3", "KM4"):
            self.s["strong_pending"] = True              # kuchli dalil: raqib ikkilanadi, keyin lean-in bilan javob beradi
        cur = self.s["km"].get(kid)
        if cur is None or level > cur["level"]:
            self.s["km"][kid] = {"level": level, "turn": turn_id}
        per = self.s.setdefault("dec_km", {}).setdefault(turn_id, {})
        per[kid] = max(level, per.get(kid, 0))

    def sem(self, key, text, tid, kw):
        """Kalit soʻz darajasi (kw) + maʼno darajasi. Maʼno 3 dan oshmaydi: 4 uchun modda keltirish kerak."""
        r = sem_scores(key, text)
        lv, false = sem_level(r)
        if r is not None:
            self.s.setdefault("sem", {}).setdefault(tid, {})[key] = {**r, "level": lv, "kw": kw}
        if false:
            if not self.dry:
                f = SEMCFG["anchors"][key]["false"][r.get("false_i", 0)]
                self.viol("false_claim", tid, f.get("why") if isinstance(f, dict) else None)
            return min(kw, 1)
        return max(kw, lv or 0)

    def viol(self, kind, turn_id, why=None):
        self.s["violations"].append({"kind": kind, "turn": turn_id, **({"why": why} if why else {})})

    def rn(self):
        return ROLE_NAME[self.s["student_role"]]

    # --- asosiy kirish
    def opening(self):
        s = self.s
        self.objective("reach-desk")
        if not s["turns"]:
            self.clerk("RISE", scene={"everyoneStands": True, "judgeIn": False, "witnessIn": False})
            self.system("Sudya zalga kirdi.", {"judgeIn": True})
            self.t("SIT", scene={"everyoneStands": False})
            self.t("OPEN", gesture="nod")
            self.clerk("CLERK_REPORT")
            self.t("ASK_POWERS", role_name=self.rn())
            s["stage"] = "ishtirokchilar"

    def turn(self, text):
        u = self.user(text)
        self.process(text, u["id"])

    def process(self, text, tid):
        s = self.s
        s["flags"]["llm_used_this_turn"] = False
        nt = normalize(text)
        if repeat_intent(nt) and self.repeat_last():     # «eshitmadim, qaytaring» — oxirgi gaplar o'sha ovozda, ballsiz
            PROC._note(self, tid, "info", "Talaba gapni qayta so'radi — takrorlandi, ball ayirilmadi.")
            return self.check_leave()
        ev = TAC.evaluate(s, nt, text, tid) if not self.dry else None   # ochiq taktikaga javob (tushmadi / chiqdi / tushdi)
        if ev:
            rec, res = ev
            t = TAC._by_id(rec["id"])
            tone = "good" if res in ("avoided", "recovered") else "bad"
            PROC._note(self, tid, tone, f"Taktika «{t['name']}»: " + {"avoided": "tuzoqqa tushmadingiz", "recovered": "tuzoqdan chiqib ketdingiz",
                       "fell": "tuzoqqa tushdingiz"}[res] + ". " + ("" if res == "avoided" else t["debrief"]["remedy"]),
                       rec.get("points", 0), ", ".join(t.get("refs", [])) or None)
        if not self.dry:
            ADV.record(s, text, nt, tid)                 # raqib kuzatuv daftari: tan olishlar va zaif joylar
        stage_before = s["stage"]
        pres = s.pop("presence_now", None) or {}       # frontend signali (v15 B2): javob paytidagi holat
        if isinstance(pres.get("standing"), bool):
            s["standing"] = pres["standing"]

        if s["stage"] == "yakun":
            self.t("CLOSED")
            return

        # --- pora / bosim / yolg'on ko'rsatuvga undash -> etika nolga
        if has(nt, r"\bpora", r"pul (beraman|beramiz|tashlay|qilib)", r"konvert", r"sovg'a (qil|ber)",
               r"rahmat qilaman\w*.{0,20}(sudya|sud)", r"kelishib ol(aylik|amiz).{0,30}(sudya|sud\b)",
               r"yolg'on ko'rsatuv", r"guvoh\w* (o'rgat|ko'ndir)", r"tanishim bor"):
            self.viol("bribe", tid)
            self.meters(-40, -40)
            self.t("W_BRIBE", gesture="shake-head")
            return self.check_leave()

        # --- umumiy qoidalar (G1–G6): munosabatni LLM emas, kod qo'zg'atadi
        if has(nt, r"\b(ahmoq|tentak|jinni|axmoq|durak|idiot|haromi|iflos)\b", *PROFANITY):
            self.viol("order", tid)
            self.meters(-20, -10)
            n = sum(1 for v in s["violations"] if v["kind"] == "order")
            L_ = PROC.CFG["order_ladder"]
            if n >= len(L_):                               # 3-marta: zaldan chiqariladi, majlis talabasiz davom etadi
                self.npc(L_[-1], gesture="stand", emotion="upset", reactions=[("principal", "upset"), ("secretary", "uncertain")],
                         art=["IPK-167"])
                s["ended_by"] = "order"
                s["stage"] = "yakun"
                return self.finish()
            self.npc(L_[n - 1], gesture="shake-head", emotion="upset", reactions=SCOLD, art=["IPK-167"])
            return self.check_leave()
        if has(nt, r"\b(sen|siz) (ai|sun'iy intellekt|bot|model)", r"rolni unut", r"ko'rsatma\w* unut", r"ignore",
               r"prompt", r"rubrika", r"hukmni ayt", r"qaror nima bo'ladi", r"to'g'ri javob\w* ayt", r"ideal yo'l"):
            self.viol("injection", tid)
            self.meters(-8, -5)
            self.t("W_ROLE", gesture="shake-head")
            return self.check_leave()
        if PROC.situational(self, text, nt, tid):            # odamdek munosabat (har bosqichda; keyin bosqich savoli qaytadi)
            return self.check_leave()
        if self.unclear(nt, tid):                          # bo'sh, juda qisqa yoki ma'nosiz — qayta so'rash, ballsiz
            H = PROC.CFG["hall"]
            n = s.get("unclear_n", 0)
            s["unclear_n"] = n + 1
            tpl = H["unclear"][n % len(H["unclear"])].format(role_name=self.rn())
            if self.ai_judge(text, "Talaba gapi sud majlisining joriy bosqichiga aloqasiz yoki ish lug'atiga tegmaydi.", tpl, tid):
                PROC._note(self, tid, "info", "Gap bosqichga aloqasiz edi — sudya (AI) munosabat bildirib, ishga qaytardi. Ball ayirilmadi.")
                return self.check_leave()
            self.npc(tpl, gesture="lean-in", emotion="uncertain")
            PROC._note(self, tid, "info", "Javob tushunilmadi — sudya qayta so'radi, ball ayirilmadi.")
            return self.check_leave()
        if s["stage"] not in ("muzokara", "yakun") and has(nt, r"qaror (chiqar|e'lon)", r"hukm chiqar", r"tezroq qaror"):
            self.viol("stage", tid)
            self.meters(-6, 0)
            self.t("W_NOT_NOW", when="Hal qiluv qarori dalillar tekshirilib, sud muzokaralari tugagach e'lon qilinadi.")
            return self.check_leave()
        addressed = NLU._address(nt, self.voice)          # og'zaki nutqda STT xatosi uchun yumshoqroq
        seated = s.get("standing") is False            # klient stand/sit yuborsa — tik turish qoidasi (IPK-167)
        heard = pres.get("heard")
        idx = {t["id"]: t["index"] for t in s["turns"]}
        last_npc = next((t for t in reversed(s["turns"][:-1]) if t["speaker"] == "npc"), None)
        interrupted = bool(heard and last_npc and heard in idx and idx[heard] < last_npc["index"])
        quiet = s["stage"] == "ishtirokchilar" and has(nt, *PROC.CFG["powers_excuse"]["patterns"])   # avval mazmunga javob
        if not addressed:
            self.reprimand("address", tid, speak=not seated and not quiet)   # bir gapda bitta tanbeh: o'tirish ustun
        if seated:
            self.reprimand("seated", tid, speak=not quiet)
        if interrupted and not self.dry:                 # frontend kafolati buzildi (v16 B2) — faqat log, tanbeh yo'q
            M.count("presence_heard_mismatch")
            print(f"presence: heardTurnId={heard} oxirgi NPC gapi {last_npc['id']} emas (sessiya {s['id']})", flush=True)
        H = PROC.CFG["hall"]
        words = len(text.split())
        if words > H["too_long_words"] or (pres.get("spoken") or 0) > H["too_long_seconds"]:   # juda uzun monolog
            s["too_long_n"] = s.get("too_long_n", 0) + 1
            self.npc(H["too_long"][(s["too_long_n"] - 1) % len(H["too_long"])], gesture="lean-in", emotion="calm")
        if (s.get("level") == "advanced" and s["stage"] in ("tushuntirish", "dalillar") and not s["flags"].get("interrupted")
                and words >= 30 and random.Random(f"{s.get('seed')}:{len(s['turns'])}").random() < 0.5):
            s["flags"]["interrupted"] = True             # raqib gapni bo'ladi — sudya tartibni tiklaydi
            self.say("opponent", H["interrupt_opp"], gesture="lean-in", emotion="upset")
            self.npc(H["interrupt_judge"].format(opp=OPP[s["opponent_role"]]["name"]), gesture="shake-head",
                     emotion="impatient", reactions=[("opponent", "uncertain")])
        refs = exact_refs(nt)
        s["cited"].extend(r for r in refs if r not in s["cited"])
        bad = [r for r in refs if NORMS.ok and r not in NORMS.known]
        if bad:
            self.viol("citation", tid)
            self.meters(-4, -4)
            self.t("W_NO_NORM", ref=bad[0].replace("-", " ") + "-modda")

        # --- kech bildirilgan rad (IPK 22): e'tiborsiz qolmasin, bosqich o'zgarmaydi
        if s["stage"] not in ("ishtirokchilar", "rad", "yakun") and recusal_intent(nt):
            if not s["flags"].get("late_recusal"):
                s["flags"]["late_recusal"] = True
                self.t("LATE_RECUSAL")
                PROC._note(self, tid, "info", "Rad ish mazmunan ko'rilishidan oldin bildiriladi; keyin — faqat asos keyin ma'lum bo'lsa.",
                           article="IPK 22-modda")
                return self.check_leave()
            self.t("RECUSAL_DENY")
            self.viol("recusal_unfounded", tid)
            return self.check_leave()

        # --- talaba tashabbusi (savol, iltimosnoma, e'tiroz, kelishuv) va aniqlashtirish
        self.cur_tid = tid
        if PROC.handle(self, text, nt, tid):
            return self.check_leave()
        if PROC.maybe_reask(self, text, nt, tid):
            return self.check_leave()

        # --- bosqich ishlovchisi
        getattr(self, "st_" + s["stage"])(text, nt, tid)
        if "claim" in self.forced:
            s["scores"]["claim"] = min(s["scores"].get("claim", 0), self.forced["claim"])
        self.maybe_tactic()
        return self.check_leave()

    def exploit(self):
        """Raqib yakuniy nutqida talabaning haqiqiy xatolarini sudga eslatadi (o'z so'zlarini iqtibos qilib)."""
        if self.dry:
            return
        rn = self.rn()
        side = rn[0].lower() + rn[1:] if rn else "raqib vakili"
        for line, _turn, _kind in ADV.exploit_lines(self.s, side):
            self.say("opponent", LAB.redact(line)[0], "lean-in", emotion="neutral")

    def maybe_tactic(self):
        """Bosqichga mos qonuniy taktika (tactics.json): raqib yoki sudya oldindan yozilgan gapni aytadi."""
        s = self.s
        if self.dry or s["stage"] in ("yakun",) or s.get("status") != "in-progress":
            return
        t = TAC.pick(s, s["stage"])
        if not t:
            return
        line = t["line"].format(role_name=self.rn()) if "{role_name}" in t["line"] else t["line"]
        turn = self.say("opponent", line, "lean-in", emotion="neutral") if t["speaker"] == "opponent" else \
            self.npc(line, gesture="lean-in", emotion="neutral")
        TAC.open_tactic(s, t, (turn or {}).get("id") if isinstance(turn, dict) else s["turns"][-1]["id"])

    def check_leave(self):
        if self.s["meters"]["patience"] <= 0 and self.s["status"] == "in-progress":
            self.t("LEAVE", gesture="stand")
            self.s["ended_by"] = "patience"
            self.finish()

    def rag_note(self, q, tid):
        """RAG: talaba gapiga eng yaqin moddalar (hisobot manbalari va modda tekshiruvi uchun)."""
        if self.dry:
            return {"results": []}
        r = NORMS.search(q, self.s["case_type"])
        if r.get("results"):
            self.s["rag"].append({"turn": tid, "confident": r.get("confident"),
                                  "norms": [x["norm_id"] for x in r["results"]], "related": r.get("related", [])[:4],
                                  "ms": r.get("ms")})
        return r

    # --- bosqichlar (data/sud/bosqichlar_ipk.json, soddalashtirilgan)
    def st_ishtirokchilar(self, text, nt, tid):
        s = self.s
        excuse = has(nt, *PROC.CFG["powers_excuse"]["patterns"])   # bahona/inkor «ishonchnoma» so'zidan ustun
        if not excuse and has(nt, r"ishonchnoma", r"vakolat", r"doverennost", r"доверенност"):
            self.km("KM1", 4, tid)
            self.meters(4, 6)
            self.t("POWERS_OK", gesture="nod", reveal=["F1"])
            self.t("RECUSAL")
            s["stage"] = "rad"
        elif not s["flags"].get("powers_asked"):
            s["flags"]["powers_asked"] = True
            ex = PROC.CFG["powers_excuse"]
            if has(nt, *ex["patterns"]):                   # «uyda qolib ketdi» — odamdek: tushunadi, lekin talab o'zgarmaydi
                self.npc(ex["first"][(s.get("seed") or 0) % len(ex["first"])], gesture="lean-in", emotion="uncertain",
                         reactions=[("principal", "uncertain")], art=["IPK-62"])
            else:
                self.t("POWERS_AGAIN", role_name=self.rn())
            PROC._note(self, tid, "bad", PROC.CFG["powers_note"], article="IPK 62-modda")
        else:
            if has(nt, *PROC.CFG["powers_excuse"]["patterns"]):
                self.npc(PROC.CFG["powers_excuse"]["then"], gesture="sigh", emotion="neutral")
            self.km("KM1", 1, tid)
            self.meters(-6, -4)
            if s.get("level") == "advanced":             # oqibat: vakolatsiz vakil majlisga qo'yilmaydi (IPK-62)
                self.npc(PROC.J["NO_POWERS"], gesture="shake-head", art=["IPK-62"])
                s["ended_by"] = "no_powers"
                s["stage"] = "yakun"
                return self.finish()
            self.t("POWERS_MISSING")
            self.t("RECUSAL")
            s["stage"] = "rad"

    def st_rad(self, text, nt, tid):
        RC = PROC.CFG["recusal"]
        recusal = recusal_intent(nt) or (has(nt, r"rad (bildir|qil)\w*(?! ?ma)", r"otvod") and not has(nt, r"rad bildirma", r"rad qilma", r"\byo'q\b"))
        answered = recusal or has(nt, r"\byo'q\b", r"bildirmay", r"e'tiroz\w* yo'q", r"ishonamiz", r"kerak emas", r"\bnet\b", r"нет",
                                  r"\bshart emas", r"rad qilmay")
        if not answered and not self.s["flags"].get("rad_asked"):    # savolga aloqasiz javob — bir marta qayta so'raladi
            self.s["flags"]["rad_asked"] = True
            self.t("ASK_AGAIN_RAD", role_name=self.rn())
            PROC._note(self, tid, "info", "Rad bosqichida savolga javob berilmadi: rad arzingiz bor-yo'qligini ayting.")
            return
        if (recusal and has(nt, r"\bkeyin", r"\boxirida", r"so'ngra", r"ko'rib bo'lin", r"ko'rilgach", r"\bkeyinroq")
                and not self.s["flags"].get("recusal_postpone")):   # «rad huquqidan oxirida foydalanaman» — noto'g'ri tushuncha
            self.s["flags"]["recusal_postpone"] = True
            self.npc(RC["postpone"], gesture="lean-in", emotion="uncertain", art=["IPK-22"])
            PROC._note(self, tid, "info", "Rad qilish ish mazmunan ko'rilishidan oldin bildiriladi — keyinga qoldirilmaydi.")
            return
        if recusal and has(nt, r"\byosh\b", r"tajriba", r"yoqma", r"ko'rinish", r"kayfiyat", r"qiyofa", r"\bayol\b", r"\berkak\b"):
            who = RC["who"]["kotib" if "kotib" in nt else ("sudya" if "sudya" in nt else "any")]
            self.viol("recusal_unfounded", tid)
            self.npc(RC["weak"].format(who=who), gesture="shake-head", emotion="neutral", art=T_ART.get("RECUSAL_DENY"))
        elif recusal:
            self.viol("recusal_unfounded", tid)
            self.t("RECUSAL_DENY")
        self.opp("recusal")
        self.t("RIGHTS")
        self.s["stage"] = "huquqlar"

    def st_huquqlar(self, text, nt, tid):
        if not has(nt, r"tushun", r"\bha\b", r"\byo'q\b", r"savol", r"ma'lum", r"\baniq", r"bilaman", r"tanish") \
                and not self.s["flags"].get("rights_asked"):
            self.s["flags"]["rights_asked"] = True
            self.t("ASK_AGAIN_RIGHTS", role_name=self.rn())
            return
        self.opp("rights")
        self.t("PRE_MOTIONS")
        self.s["stage"] = "oldingi"

    def st_oldingi(self, text, nt, tid):
        s = self.s
        if not has(nt, r"iltimosnoma", r"so'ra", r"\byo'q\b", r"guvoh", r"ekspert", r"dalil", r"talab", r"chaqir", r"qo'sh",
                   r"\bha\b", r"\bbor\b") and not s["flags"].get("pre_asked"):
            s["flags"]["pre_asked"] = True
            self.t("ASK_AGAIN_PRE", role_name=self.rn())
            return
        if has(nt, r"iltimosnoma", r"so'rayman") and not has(nt, r"iltimosnoma\w* yo'q", r"\byo'q\b"):
            self.npc("Iltimosnomangiz ishni mazmunan ko'rish davomida, tegishli bosqichda hal qilinadi.", art=["IPK-169"])
        self.opp("pre")
        if s["student_role"] == "davogar-vakili":
            self.t("MERITS_P")
        else:
            self.t("MERITS_D")
            self.opp("claim")
            self.t("ASK_ADMIT")
        s["stage"] = "tushuntirish"

    def st_tushuntirish(self, text, nt, tid):
        s = self.s
        self.rag_note(text, tid)
        if s["student_role"] == "davogar-vakili":
            lvl = 0
            if has(nt, r"shartnoma"):
                lvl += 1
            if has(nt, r"25 ?620 ?433", r"25,6 ?mln", r"asosiy qarz"):
                lvl += 1
            if has(nt, r"fk\w* ?544", r"ijara haq", r"foydalanganlik uchun haq", r"6\.4"):
                lvl += 1
            if has(nt, r"peny|neustoyk", r"8\.5"):
                lvl += 1
            lvl = min(self.sem("claim_davogar", text, tid, lvl), PROC.cap_for(self))
            s["scores"]["claim"] = lvl
            s["claim_penya"] = s.get("claim_penya") or has(nt, r"peny|neustoyk", r"8\.5")
            self.meters(2, 3 * lvl)
            self.opp("answer", reveal=["F3"])
            self.t("EVIDENCE", reveal=["F2"])
            self.t("EVIDENCE_ASK_P")
        else:
            lvl = 0
            if has(nt, r"dalolatnoma", r"topshirilmagan", r"topshirish hujjat"):
                lvl += 2
                self.km("KM2", 2, tid)
            if has(nt, r"fk\w* ?57[8]", r"fk\w* ?541", r"578", r"541"):
                lvl += 1
                self.km("KM2", 4 if lvl >= 3 else 3, tid)
            km2 = self.sem("KM2_javobgar", text, tid, s.get("dec_km", {}).get(tid, {}).get("KM2", 0))
            if km2:
                self.km("KM2", km2, tid)
                lvl = max(lvl, km2)
            if has(nt, r"peny|neustoyk"):
                lvl += 1
            s["scores"]["claim"] = min(lvl, 4)
            self.meters(2, 3 * lvl)
            self.opp("rebut", reveal=["F3"] if lvl >= 2 else [])
            self.t("EVIDENCE", reveal=["F2"])
            self.t("EVIDENCE_ASK_D")
        s["stage"] = "dalillar"

    def st_dalillar(self, text, nt, tid):
        s = self.s
        self.rag_note(text, tid)
        if s["student_role"] == "davogar-vakili":
            lvl = 0
            if has(nt, r"foydalan"):
                lvl += 1
            if has(nt, r"hisob-?faktura", r"faktura", r"schet"):
                lvl += 1
            if has(nt, r"fk\w* ?544", r"6\.4", r"ijara haq"):
                lvl += 1
            if has(nt, r"fk\w* ?578", r"boshqa hujjat", r"amalda bajarilgan", r"tan ol"):
                lvl += 1
            lvl = self.sem("KM2_davogar", text, tid, min(lvl, 4))
            self.km("KM2", min(lvl, 4), tid)
            self.meters(0, 3 * lvl)
            if s.get("claim_penya", True):               # raqib moslashadi: penya talab qilinmagan bo'lsa — iltimosnoma ham yo'q
                self.opp("motion", reveal=["F4"])
                self.t("HEAR_OTHER", other="Da'vogar vakili")
                s["stage"] = "penya"
            else:
                s.setdefault("km_na", []).append("KM3")
                self.t("ASK_MORE")
                s["stage"] = "qoshimcha"
        else:
            mp = s.get("motion_penalty")
            if mp and not (has(nt, r"peny|neustoyk") and has(nt, r"kamaytir")):   # erta berilgan iltimosnoma — endi hal qilinadi
                self.penalty_defendant(mp["text"], normalize(mp["text"]), mp["tid"], first=True)
                lv = s["km"].get("KM3", {}).get("level", 0)
                PROC._note(self, tid, "good" if lv >= 3 else "info",
                           "Oldinroq berilgan penya iltimosnomangiz endi eshitildi va qaror qabul qilishda hal qilinadi.",
                           article=_confirmed("FK-326"))
            else:
                self.penalty_defendant(text, nt, tid, first=True)

    def penalty_defendant(self, text, nt, tid, first):
        s = self.s
        kw_motion = has(nt, r"peny|neustoyk") and has(nt, r"kamaytir", r"kamayt", r"umenshen")
        sem3 = self.sem("KM3_javobgar", text, tid, 0)       # boshqa soʻzlar bilan aytilgan iltimosnoma ham tanilsin
        if kw_motion or sem3 >= 3:
            lvl = 2 if kw_motion else 0
            if has(nt, r"fk\w* ?326", r"\b326\b"):
                lvl += 1
            if has(nt, r"nomutanosib", r"mulkiy ahvol", r"bajarilish daraja", r"moliyaviy ahvol", r"qisqa muddat", r"uch oy"):
                lvl += 1
            lvl = max(lvl, sem3)
            self.km("KM3", lvl, tid)
            self.meters(2, 4 * lvl)
            self.t("HEAR_OTHER", reveal=["F4"], other="Da'vogar vakili")
            self.opp("on_motion")
            self.t("DEFER", gesture="nod")
            self.t("ASK_MORE")
            s["stage"] = "qoshimcha"
        elif first:
            if has(nt, r"dalolatnoma", r"fk\w* ?578", r"fk\w* ?541"):
                cur = s["km"].get("KM2", {}).get("level", 0)
                self.km("KM2", min(4, cur + 1), tid)
            self.t("PENALTY_ASK_D")
            s["stage"] = "penya"
        else:
            self.km("KM3", max(1 if has(nt, r"peny|neustoyk") else 0, sem3), tid)
            self.t("DEFER")
            self.t("ASK_MORE")
            s["stage"] = "qoshimcha"

    def st_penya(self, text, nt, tid):
        s = self.s
        self.rag_note(text, tid)
        if s["student_role"] == "davogar-vakili":
            lvl = 0
            if has(nt, r"shartnoma", r"kelishilgan", r"kelishuv", r"imzolagan"):
                lvl += 1
            if has(nt, r"8\.5"):
                lvl += 1
            if has(nt, r"fk\w* ?262", r"yozma", r"fk\w* ?333", r"ayb"):
                lvl += 1
            if has(nt, r"kechiktir", r"muddat", r"o'z vaqtida"):
                lvl += 1
            lvl = self.sem("KM3_davogar", text, tid, min(lvl, 4))
            self.km("KM3", min(lvl, 4), tid)
            self.meters(0, 3 * lvl)
            self.t("DEFER", gesture="nod")
            self.t("ASK_MORE")
            s["stage"] = "qoshimcha"
        else:
            self.penalty_defendant(text, nt, tid, first=False)

    def st_qoshimcha(self, text, nt, tid):
        s = self.s
        if s["student_role"] == "davogar-vakili":
            self.t("DEBATES_P")
        else:
            self.t("DEBATES_D")
            self.opp("closing")
            self.exploit()
            self.t("FLOOR_D")
        s["stage"] = "muzokara"

    def st_muzokara(self, text, nt, tid):
        s = self.s
        self.rag_note(text, tid)
        if has(nt, r"menda ma'lumot", r"eshitganman", r"eshitishimcha", r"aytishlaricha", r"boshqa ijarachi", r"bilishimcha", r"guvoh\w* bor"):
            s["flags"]["unexamined"] = s["flags"].get("unexamined", 0) + 1
            self.viol("unexamined", tid)
            self.meters(-8, -5)
            if s["flags"]["unexamined"] == 1:
                self.say("opponent", PROC.CFG["opponent"][s["opponent_role"]]["object_unexamined"], gesture="shake-head",
                         emotion="upset")
                self.t("W_UNEXAMINED", gesture="shake-head")
                return
        lvl = 1
        if has(nt, r"shartnoma", r"hisob-?faktura", r"faktura", r"dalolatnoma"):
            lvl += 1
        if refs := exact_refs(nt):
            lvl += 1 if any(r in KM_NORMS["KM2"] + KM_NORMS["KM3"] for r in refs) else 0
        if has(nt, r"so'rayman", r"so'raymiz", r"undirish", r"kamaytir", r"rad etish"):
            lvl += 1
        lvl = self.sem("KM4_davogar" if s["student_role"] == "davogar-vakili" else "KM4_javobgar", text, tid, min(lvl, 4))
        if s["flags"].get("unexamined"):
            lvl = min(lvl, 2)
        self.km("KM4", min(lvl, 4), tid)
        s["closing_turn"] = tid
        if s["student_role"] == "davogar-vakili":
            self.t("FLOOR_D")
            self.opp("closing")
            self.exploit()
        self.announce()
        s["stage"] = "yakun"

    def announce(self):
        self.t("TO_CHAMBER")
        self.system("Sud maslahatxonaga kirdi.", {"judgeIn": False})
        self.clerk("RISE", scene={"everyoneStands": True})
        self.system("Sudya zalga qaytdi.", {"judgeIn": True})
        self.t("VERDICT", gesture="nod")
        self.t("AFTER_VERDICT", scene={"everyoneStands": False})

    def st_yakun(self, text, nt, tid):
        self.t("CLOSED")

    # --- yakun va baholash
    def finish(self):
        s = self.s
        self.status("evaluating")
        s["report"] = evaluate(s)
        o = s["report"]["outcome"]
        s["outcome"] = o
        self.objective("finish")
        self.status("report-ready")


# ---------------------------------------------------------------- baholovchi (data/sud/baholash_rubrikasi.md)
# v1.5 (reports/LexSim baholash metodikasi.md): SQE2 bo'yicha huquq va ko'nikma 50/50.
#   Huquq (50): huquqiy asos 25 + tartib-taomil 15 + kasbiy etika 10 (SQE2: «legally correct», «comprehensive», «ethics»).
#   Ko'nikma (50): faktlar 20 + nutq 20 + hujjat 10. Avvalgi 30/15/15/15/15/10 ning manbasi yo'q edi.
CRIT = [("legal", "Huquqiy asos", 25), ("facts", "Faktlar va dalillar", 20), ("procedure", "Tartib-taomil", 15),
        ("communication", "Sud odobi va nutq", 20), ("ethics", "Kasbiy etika", 10), ("document", "Hujjat va rasmiylashtirish", 10)]
CRIT_BASIS = {
    "legal": "Asos: SQE2 — huquqni to'g'ri va to'liq qo'llash; Jessup — huquq eng og'ir mezon. Normalar: FK 326, 541, 544; OXS 163, 234.",
    "facts": "Asos: SQE2 «case analysis»; Jessup — faktlar 20; IPK 68 — faqat oshkor qilingan dalil.",
    "procedure": "Asos: IPK tartibi — vakolat (62), rad (20–23), dalillarni tekshirish (168), muzokara (173).",
    "communication": "Asos: SQE2 advokatlik ko'nikmalari; IPK 167 — sudga murojaat va tartib.",
    "ethics": "Asos: SQE2 — etika alohida mezon; Advokatning kasb etikasi qoidalari (2013); qo'pol buzilish — natija 0.",
    "document": "Asos: SQE2 «writing and drafting»; Price Media yozma ish mezonlari — nima so'raladi, qaysi asosda, qaysi dalil bilan.",
}

OUTCOMES = {
    "excellent": ("A'lo", "Siz sud majlisini tartibga to'liq rioya qilgan holda, kuchli huquqiy dalillar bilan o'tkazdingiz."),
    "average": ("O'rtacha", "Asosiy bosqichlardan o'tdingiz, lekin ayrim muhim lahzalarda huquqiy asos yoki tartib yetishmadi."),
    "poor": ("Qoniqarsiz", "Sud majlisida jiddiy tartib buzilishlari yoki huquqiy asosning yo'qligi kuzatildi."),
    "failed": ("Muvaffaqiyatsiz", "Kasbiy etika jiddiy buzilgani sababli natija nolga tushirildi."),
}

IDEAL = {
    "davogar-vakili": [("KM1", "Vakolatni ishonchnoma bilan tasdiqlash"),
                       ("claim", "Talab va summani aniq bayon qilish (shartnoma, 6.4-band, FK-544)"),
                       ("KM2", "Dalolatnoma e'tiroziga foydalanish fakti va imzolangan hisob-fakturalar bilan javob berish"),
                       ("KM3", "Penya asosini keltirish (8.5-band, yozma kelishuv, kechiktirish)"),
                       ("KM4", "Muzokarada faqat tekshirilgan dalillarga tayanish")],
    "javobgar-vakili": [("KM1", "Vakolatni ishonchnoma bilan tasdiqlash"),
                        ("KM2", "Topshirish dalolatnomasi masalasini FK-578/FK-541 bilan ko'tarish"),
                        ("KM3", "FK-326 bo'yicha penyani kamaytirishni mezonlari bilan so'rash"),
                        ("KM4", "Muzokarada faqat tekshirilgan dalillarga tayanish")],
}

BETTER = {
    ("davogar-vakili", "KM2"): "Hurmatli sud, javobgar obyektdan uch oy foydalanganini o'zi tan oldi va hisob-fakturalarni imzolagan. "
                               "Bu ijara munosabati amalda bajarilganini tasdiqlaydi; Fuqarolik kodeksining 544-moddasi va shartnomaning "
                               "6.4-bandiga ko'ra ijara haqi to'lanishi shart.",
    ("davogar-vakili", "KM3"): "Hurmatli sud, penya shartnomaning 8.5-bandida taraflar tomonidan yozma kelishilgan, javobgar to'lovni "
                               "muddatida amalga oshirmagan. Shu sababli penyani kamaytirishga asos yo'q deb hisoblaymiz.",
    ("javobgar-vakili", "KM2"): "Hurmatli sud, Fuqarolik kodeksining 578-moddasiga ko'ra bino topshirilishi dalolatnoma yoki topshirishga "
                                "doir boshqa hujjat bilan rasmiylashtiriladi. Bunday hujjat imzolanmagan.",
    ("javobgar-vakili", "KM3"): "Hurmatli sud, da'vo qilingan penya majburiyat buzilishi oqibatlariga nomutanosib. Fuqarolik kodeksining "
                                "326-moddasiga asosan, javobgar obyektdan qisqa muddat foydalanganini va mulkiy ahvolini inobatga olib, "
                                "penyani kamaytirishingizni so'rayman.",
    ("any", "KM1"): "Hurmatli sud, vakolatimni tasdiqlovchi ishonchnomani taqdim etaman.",
    ("any", "KM4"): "Hurmatli sud! Sud majlisida tekshirilgan ijara shartnomasi va hisob-fakturalar shuni ko'rsatadiki, ... "
                    "Shu asosda ... ni so'rayman.",
}


def lvl_from_count(n, table):
    for lim, lv in table:
        if n <= lim:
            return lv
    return table[-1][1]


def evaluate(s):
    role = s["student_role"]
    km = {k: v["level"] for k, v in s["km"].items()}
    vio = {}
    for v in s["violations"]:
        if v.get("free"):                                # beginner 1-eslatma — baholanmaydi
            continue
        vio.setdefault(v["kind"], []).append(v["turn"])
    user_turns = [t for t in s["turns"] if t["speaker"] == "user"]

    na = set(s.get("km_na", []))                   # qo'llanmagan lahzalar (masalan, penya talab qilinmagan)
    legal_parts = [km.get("KM2", 0)] + ([km.get("KM3", 0)] if "KM3" not in na else [])
    legal = round(sum(legal_parts) / len(legal_parts))
    legal = max(0, legal - len(vio.get("citation", [])))
    facts_lvl = min(4, s["scores"].get("claim", 0) + (1 if km.get("KM2", 0) >= 3 else 0)) if role == "davogar-vakili" \
        else min(4, max(km.get("KM2", 0), s["scores"].get("claim", 0)))
    proc = 4
    hints = s.get("hints", [])
    if km.get("KM1", 0) < 3:
        proc = min(proc, 2)
    proc -= min(3, len(vio.get("stage", [])) + len(vio.get("recusal_unfounded", [])))
    if len(vio.get("unexamined", [])) >= 1:
        proc = min(proc, 3 if len(vio["unexamined"]) == 1 else 2)
    if "KM4" not in km:
        proc = min(proc, 2)
    comm = lvl_from_count(len(vio.get("address", [])) + len(vio.get("seated", [])) + len(vio.get("silence", []))
                          + len(vio.get("interrupt", [])),
                          [(0, 4), (1, 3), (3, 2), (999, 1)])
    if user_turns and sum(len(t["text"]) for t in user_turns) / len(user_turns) < 25:
        comm = min(comm, 2)
    ethics = 4 - min(4, 2 * len(vio.get("order", [])) + 2 * len(vio.get("injection", [])) + 4 * len(vio.get("bribe", []))
                     + len(vio.get("false_claim", [])) + 2 * len(vio.get("improper_evidence", []))
                     + len(vio.get("disorder", [])))
    doc_lvl = km.get("KM3", 0) if role == "javobgar-vakili" else km.get("KM4", 0)
    d = s.get("document") or {}
    if s.get("documentSubmitted") and len((d.get("nextStep") or "").strip()) > 40:
        doc_lvl = max(doc_lvl, 3)
    levels = {"legal": legal, "facts": facts_lvl, "procedure": max(0, proc), "communication": comm,
              "ethics": max(0, ethics), "document": doc_lvl}

    first_user = user_turns[0]["id"] if user_turns else None

    def tids(*kms):
        out = [s["km"][k]["turn"] for k in kms if k in s["km"]]
        return out or ([first_user] if first_user else [])

    expl = {
        "legal": f"Muhim lahzalar: dalolatnoma bahsi (KM2) — {km.get('KM2', 0)}/4, penya masalasi (KM3) — {km.get('KM3', 0)}/4."
                 + (f" Mavjud bo'lmagan modda keltirildi: {len(vio['citation'])} marta." if vio.get("citation") else "")
                 + (" Javoblar ma'nosi bo'yicha ham tekshirildi (reranker)." if s.get("sem") else ""),
        "facts": "Shartnoma, hisob-fakturalar va summalarni qanchalik aniq ishlatganingiz baholandi.",
        "procedure": f"Vakolat (KM1): {'tasdiqlandi' if km.get('KM1', 0) >= 3 else 'tasdiqlanmadi'}. Bosqichni buzish: "
                     f"{len(vio.get('stage', []))}, tekshirilmagan dalilga tayanish: {len(vio.get('unexamined', []))}."
                     + (f" Maslahat: {len(hints)} marta (jami balldan −{5 * len(hints)})." if hints else ""),
        "communication": f"«Hurmatli sud» murojaatisiz gaplar: {len(vio.get('address', []))}."
                         + (f" O'tirib gapirilgan: {len(vio['seated'])}." if vio.get("seated") else ""),
        "ethics": "Tartib va rolga hurmat." + (f" Haqorat: {len(vio['order'])}." if vio.get("order") else "")
                  + (f" Rolni buzishga urinish: {len(vio['injection'])}." if vio.get("injection") else "")
                  + (" Sudga ta'sir o'tkazishga urinish — natija nolga tushirildi." if vio.get("bribe") else "")
                  + (f" Ish materiallariga zid da'vo: {len(vio['false_claim'])}." if vio.get("false_claim") else ""),
        "document": "Iltimosnoma yoki yakuniy nutqning tuzilishi: nima so'ralyapti, qaysi asosda, qaysi dalil bilan.",
    }
    sup = {"legal": tids("KM2", "KM3"), "facts": tids("KM2"), "procedure": tids("KM1", "KM4"),
           "communication": vio.get("address", [])[:3] or tids("KM1"), "ethics": (vio.get("order", []) + vio.get("injection", []))[:3] or tids("KM4"),
           "document": tids("KM3" if role == "javobgar-vakili" else "KM4")}
    criteria = []
    total = 0
    for cid, label, mx in CRIT:
        sc = round(mx * levels[cid] / 4)
        total += sc
        criteria.append({"id": cid, "label": label, "score": sc, "max": mx, "explanation": expl[cid] + " " + CRIT_BASIS[cid],
                         "supportingTurnIds": [t for t in sup[cid] if t]})
    tac_fb, tac_pts = TAC.report(s)                   # taktikalar: tushmadi +2, chiqib ketdi +1, tushdi −2
    total = max(0, min(100, total + tac_pts))
    total = max(0, total - 5 * len(hints) - 10 * len(s.get("reveals", [])))   # maslahat −5, variantlarni ochish −10
    zeroed = len(vio.get("order", [])) >= 3 or bool(vio.get("bribe"))
    if zeroed:
        total = 0
    if s.get("ended_by") in ("patience", "no_powers"):
        oid = "poor"
    elif zeroed:
        oid = "failed"
    else:
        oid = "excellent" if total >= 85 else "average" if total >= 60 else "poor"
    outcome = {"id": oid, "title": OUTCOMES[oid][0], "description": OUTCOMES[oid][1]}

    # fikr-mulohaza: 3 kuchli, 3 xato, 1 mentor
    def srcs(kid):
        return [x for x in (NORMS.source(n) for n in KM_NORMS.get(kid, [])) if x][:3]

    names = {"KM1": "Vakolatni tasdiqlash", "KM2": "Topshirish dalolatnomasi bahsi", "KM3": "Penya masalasi",
             "KM4": "Sud muzokarasi"}
    strengths, errors = [], []
    for kid in ("KM1", "KM2", "KM3", "KM4"):
        if kid in na:
            continue
        lv = km.get(kid)
        item = {"title": names[kid], "relatedTurnIds": tids(kid), "sources": srcs(kid)}
        if lv is not None and lv >= 3:
            strengths.append({**item, "kind": "strength", "message": f"{names[kid]}: yaxshi bajarildi ({lv}/4)."})
        else:
            errors.append({**item, "kind": "error",
                           "message": f"{names[kid]}: {'bajarilmadi' if lv is None else f'zaif bajarildi ({lv}/4)'}. "
                                      f"Ideal yo'lga va «Qanday aytish kerak edi» bo'limiga qarang."})
    if vio.get("address"):
        errors.append({"kind": "error", "title": "Sudga murojaat", "relatedTurnIds": vio["address"][:3],
                       "message": "Sudga har doim «Hurmatli sud» deb murojaat qilinadi (IPK-167).",
                       "sources": [x for x in [NORMS.source("IPK-167")] if x]})
    real = {"kind": "mentor-review", "title": "Haqiqiy sud qanday hal qilgan",
            "message": "Haqiqiy ishda sud hisob-fakturalar va foydalanish faktiga tayanib asosiy qarzni to'liq undirgan, "
                       "penyani esa FK-326 bo'yicha 3 040 580,45 so'mdan 30 405 so'mgacha kamaytirgan. Bu baholash avtomatik — "
                       "mentor tekshiradi.",
            "relatedTurnIds": [first_user] if first_user else [], "sources": srcs("KM3")[:1] + srcs("KM2")[:1]}
    feedback = strengths[:3] + errors[:3] + tac_fb[:3] + ADV.report(s)[:2] + [real]

    weakest = min((k for k in ("KM2", "KM3", "KM1", "KM4") if ((role, k) in BETTER or ("any", k) in BETTER) and k not in na),
                  key=lambda k: km.get(k, -1))
    orig_turn = next((t for t in s["turns"] if t["id"] == s["km"].get(weakest, {}).get("turn")), None)
    better = {"original": orig_turn["text"] if orig_turn else "(bu lahzada gapirilmadi)",
              "improved": BETTER.get((role, weakest)) or BETTER[("any", weakest)],
              "why": f"{names[weakest]} — bu ssenariyning muhim lahzasi; javob aniq huquqiy asos va dalilga tayanishi kerak."}
    ideal = [{"step": step, "done": (km.get(k, 0) >= 3) if k.startswith("KM") else s["scores"].get(k, 0) >= 3}
             for k, step in IDEAL[role] if k not in na]
    other = "sud-ijara-javobgar" if role == "davogar-vakili" else "sud-ijara-davogar"
    return {
        "sessionId": s["id"], "scenarioId": s["scenarioId"], "rubricVersion": RUBRIC_VERSION,
        "scoreTotal": int(total), "zeroedByEthics": zeroed, "outcome": outcome, "criteria": criteria,
        "feedback": feedback, "betterAnswer": better, "idealPath": ideal,
        "nextScenario": {"id": other, "title": SCEN[other]["public"]["title"],
                         "reason": "Xuddi shu ishni qarshi tomon vakili sifatida o'tib ko'ring."},
        "reviewStatus": "needs-mentor", "appeal": None,
        "decisions": decisions(s), "hints": len(hints), "reflect": REFLECT.get(role),
        "level": s.get("level", "beginner"), "reveals": len(s.get("reveals", [])),
        "inputModes": {m: sum(1 for t in user_turns if t.get("inputMode", "text") == m) for m in ("option", "text", "voice")},
        "turns": s["turns"], "facts": facts_list(s), "factsTotal": len(FACTS), "evaluatedAt": now_iso(),
    }


def _ts(iso):
    try:
        return datetime.strptime(iso[:23], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc).timestamp()
    except (TypeError, ValueError):
        return None


KM_STAGE = {("any", "KM1"): "ishtirokchilar", ("davogar-vakili", "KM2"): "dalillar", ("javobgar-vakili", "KM2"): "tushuntirish",
            ("davogar-vakili", "KM3"): "penya", ("javobgar-vakili", "KM3"): "dalillar", ("any", "KM4"): "muzokara"}
KM_NAMES = {"KM1": "Vakolatni tasdiqlash", "KM2": "Topshirish dalolatnomasi bahsi", "KM3": "Penya masalasi",
            "KM4": "Sud muzokarasi"}


def _hint_for(role, stage):
    h = ROLES["maslahatchi"]["bosqichlar"].get(stage, {})
    return h.get(role, h)


def _confirmed(nid):
    return art_label(nid) if nid and (not NORMS.ok or nid in NORMS.known) else None


def decisions(s):
    """Qarorlar jurnali (COURT_BACKEND.md §4.2): har bir talaba gapi — nima so'ralgan, nima dedi, ball, sabab, yaxshiroq javob."""
    role, out = s["student_role"], []
    t0 = _ts(s.get("startedAt")) or _ts(s.get("createdAt")) or 0
    prompt = None
    for t in s["turns"]:
        if t["speaker"] != "user":
            if t["speaker"] == "npc":
                prompt = t["text"]
            continue
        tid, at = t["id"], max(0, round((_ts(t["at"]) or t0) - t0))
        entries = []
        for v in s["violations"]:
            if v["turn"] != tid:
                continue
            pts, why, art = VIOL_INFO.get(v["kind"], (0, None, None))
            pts = v.get("points", pts)                   # tanbeh zinapoyasi: nechanchi marta ekaniga qarab
            why = v.get("why") or why                    # aniq sabab (qaysi fakt bilan zid) bo'lsa — o'sha
            better = None
            if v["kind"] == "address":
                better = t["text"] if t["text"].lower().startswith("hurmatli sud") else "Hurmatli sud, " + t["text"]
            elif v["kind"] == "unexamined":
                better = _hint_for(role, "muzokara").get("namuna")
            entries.append({"tone": "bad" if pts else "info", "points": pts,
                            "why": why + (" (eslatma, ball ayirilmadi)" if not pts and why else ""), "better": better,
                            "article": _confirmed(art)})
        for kid, lv in s.get("dec_km", {}).get(tid, {}).items():
            key = (role, kid) if (role, kid) in KM_ARTICLE else ("any", kid)
            art = _confirmed(KM_ARTICLE.get(key))
            semv = next((v for k2, v in s.get("sem", {}).get(tid, {}).items() if k2.startswith(kid) or (kid == "KM2" and k2 == "claim_davogar")), None)
            if lv >= 3:
                why = None
                if lv == 3 and semv and semv["level"] == 3 and semv["kw"] < 3:
                    why = f"Fikr to'g'ri (ma'no bo'yicha moslik {semv['pos']:.2f}), lekin to'liq ball uchun modda raqamini ayting."
                entries.append({"tone": "good", "points": 0 if lv == 4 else round(KM_MAXLOSS[kid] / 4), "why": why,
                                "better": None, "article": art, "semantic": semv})
            else:
                h = _hint_for(role, KM_STAGE.get(key, ""))
                entries.append({"tone": "bad", "points": round(KM_MAXLOSS[kid] * (4 - lv) / 4),
                                "why": f"{KM_NAMES[kid]}: zaif bajarildi ({lv}/4). " + (h.get("xato") or ""),
                                "better": BETTER.get((role, kid)) or BETTER.get(("any", kid)) or h.get("namuna"),
                                "article": art})
        od = s.get("optdec", {}).get(tid)
        if od and od.get("tone") == "bad":         # xato variant: uning izohi ustun, ball dvigatel hisobida qoladi
            pts = sum(e["points"] for e in entries if e["tone"] == "bad") or od.get("points", 0)
            good_opt = next((o["text"] for o in stage_options({**s, "stage": t.get("stage")}) if o["tone"] == "good"), None) \
                if t.get("stage") else None
            entries = [{"tone": "bad", "points": pts, "why": od.get("why"), "better": good_opt,
                        "article": _confirmed(od.get("article"))}]
        entries += s.get("dec_notes", {}).get(tid, [])
        if od and od.get("tone") == "good" and not entries:
            entries = [{"tone": "good", "points": 0, "why": None, "better": None, "article": _confirmed(od.get("article"))}]
        if t.get("sttLow"):
            entries = [{"tone": "info", "points": 0, "why": "Ovoz aniq tanilmadi — qayta so'raldi, ball ayirilmadi.",
                        "better": None, "article": None}]
        for e in entries or [{"tone": None, "points": 0, "why": None, "better": None, "article": None}]:
            out.append({"at": at, "prompt": prompt, "chose": t["text"], "inputMode": t.get("inputMode", "text"),
                        **({"optionId": od["optionId"], "optionTone": od.get("tone")} if od else {}), **e,
                        "points": int(e.get("points") or 0)})          # kontrakt: number, hech qachon null
    for r in s.get("reveals", []):
        out.append({"at": r["at"], "prompt": None, "chose": "Variantlar ochildi", "tone": "info", "points": 10,
                    "why": "Variantlar ko'rsatildi (−10 ball).", "better": None, "article": None, "inputMode": "option"})
    for h in s.get("hints", []):
        out.append({"at": h["at"], "prompt": None, "chose": f"Maslahat olindi: {h['title']}", "tone": "info", "points": 5,
                    "why": "Maslahatdan foydalanildi (−5 ball).", "better": None, "article": None})
    out.sort(key=lambda d: d["at"])
    return out


def hint(s):
    """Maslahatchi: joriy bosqichda talaba nima qilishi kerak (faqat tutorial)."""
    st = s["stage"] if s["turns"] else "ochilish"
    h = ROLES["maslahatchi"]["bosqichlar"].get(st, {})
    h = h.get(s["student_role"], h)
    rol = ROLE_NAME[s["student_role"]].lower()
    return {"stage": st, "title": h.get("sarlavha", ""), "todo": h.get("nima_qilish", ""),
            "example": h.get("namuna", "").replace("{rol}", rol), "commonMistake": h.get("xato", ""),
            "sources": [x for x in (NORMS.source(n) for n in h.get("moddalar", [])) if x]}


def facts_list(s):
    return [{"id": f, "text": FACTS[f], "unlockedAtTurn": i} for f, i in s["facts"].items()]


def frozen(obj):
    """Javobning mustaqil nusxasi: idempotent qayta yuborishda birinchi javob AYNAN qaytsin
    (snapshot ichidagi turns/objectives sessiyaning jonli ro'yxatlariga havola bo'lmasin)."""
    return json.loads(json.dumps(obj, ensure_ascii=False))


def stage_options(s):
    """Joriy bosqich variantlari (server ko'rinishi, tone bilan). Tartib seed bo'yicha aralashtiriladi."""
    st = OPTIONS.get(s.get("stage"), {})
    opts = st.get(s["student_role"]) or st.get("any") or []
    rol = ROLE_NAME[s["student_role"]].lower()
    opts = [dict(o, text=o["text"].replace("{rol}", rol)) for o in opts]
    random.Random(f"{s.get('seed')}:{s.get('stage')}").shuffle(opts)
    return opts


def level_view(s):
    lv = s.get("level", "beginner")
    cfg = LEVELS[lv]
    active = s["status"] == "in-progress" and s.get("stage") not in (None, "ochilish", "yakun") and s["turns"]
    revealed = s.get("stage") in s.get("revealed", [])
    show = active and (lv == "beginner" or (lv == "intermediate" and revealed))
    modes = list(cfg["modes"]) + (["option"] if lv == "intermediate" and revealed else [])
    fb = None
    if cfg["feedback"] != "none" and s.get("last_feedback"):
        f = s["last_feedback"]
        if cfg["feedback"] == "all" or f.get("serious"):
            fb = {k: f[k] for k in ("tone", "message", "article") }
            if f.get("optionId"):
                fb["optionId"] = f["optionId"]
    return {"level": lv, "inputModes": modes, "optionsRevealed": bool(revealed and lv == "intermediate"),
            "silenceSec": cfg["silence"], "hintsAllowed": cfg["hints"], "feedback": fb,
            "options": [{"id": o["id"], "text": o["text"], "kind": o["kind"]} for o in stage_options(s)] if show else []}


def snapshot(s):
    return {
        "protocol": PROTOCOL, "sessionId": s["id"], "sequence": s["sequence"], "status": s["status"], "mode": s["mode"],
        "engine": s.get("engine_used") or ("llm" if SETTINGS["llm"] else "scripted"),
        "scenario": SCEN[s["scenarioId"]]["public"],
        "meters": dict(s["meters"]) if s["mode"] == "tutorial" else None,
        "npc": dict(s["npc"]), "turns": s["turns"], "facts": facts_list(s), "factsTotal": len(FACTS),
        **level_view(s),
        "pending": bool(s.get("pending")), "scene": s.get("scene") or {"judgeIn": False, "everyoneStands": False, "witnessIn": False},
        "standing": s.get("standing"),
        "objectives": s["objectives"], "objects": s["objects"], "document": s["document"],
        "documentSubmitted": s["documentSubmitted"], "outcome": s["outcome"], "startedAt": s["startedAt"],
        "seed": s.get("seed"),
    }


def new_session(scenario_id, mode, seed, owner, level="beginner"):
    sc = SCEN[scenario_id]
    sid = "sim_" + secrets.token_urlsafe(18)
    role = sc["student_role"]
    return {
        "id": sid, "owner_hash": hashlib.sha256(owner.encode()).hexdigest(), "scenarioId": scenario_id,
        "mode": mode, "seed": seed, "level": level, "status": "briefing", "sequence": 0, "events": [], "turns": [],
        "facts": {}, "objectives": [{"id": i, "label": label, "done": False} for i, label in OBJECTIVES],
        "objects": {"envelope": "disabled", "phone": "disabled"},
        "document": {"service": None, "applicantName": "", "periodFrom": "", "periodTo": "", "employer": "",
                     "evidence": [], "nextStep": "", "notify": "none"},
        "documentSubmitted": False, "outcome": None, "startedAt": None, "createdAt": now_iso(),
        "student_role": role, "opponent_role": "javobgar-vakili" if role == "davogar-vakili" else "davogar-vakili",
        "case_type": sc["case_type"], "stage": "ochilish", "meters": {"patience": 70, "trust": 50},
        "npc": {"emotion": "neutral", "intensity": 0.5}, "km": {}, "violations": [], "flags": {}, "scores": {},
        "cited": [], "rag": [], "idem": {}, "report": None, "ended_by": None,
    }


# ---------------------------------------------------------------- HTTP
RATE = {"sessions": 20, "turns": 30, "interactions": 60, "documents": 60, "appeal": 5, "tts": 90, "stt": 20,
        "tts_key": 300, "stt_key": 120, "nlu": 600, "store": 600, "moot_judge": 20, "lab_draft": 6, "npc": 60}
PRERENDER = {}            # jobId -> holat
_rate, _rate_lock = {}, threading.Lock()


def rate_wait(key, limit):
    """429 dan keyin necha soniyada joy bo'shaydi."""
    t = time.time()
    with _rate_lock:
        q = sorted(x for x in _rate.get(key, []) if t - x < 60)
    return 60 - (t - q[-limit]) if len(q) >= limit else 1


def rate_ok(key, limit):
    t = time.time()
    with _rate_lock:
        q = [x for x in _rate.get(key, []) if t - x < 60]
        if len(q) >= limit:
            _rate[key] = q
            return False
        q.append(t)
        _rate[key] = q
        return True


def validate_draft(d):
    if not isinstance(d, dict):
        raise ApiError(422, "validation_failed", "Hujjat ma'lumotlari noto'g'ri")
    lim = {"applicantName": 120, "periodFrom": 10, "periodTo": 10, "employer": 200, "nextStep": 1200}
    out = {}
    for k, n in lim.items():
        v = d.get(k, "")
        if not isinstance(v, str) or len(v) > n:
            raise ApiError(422, "validation_failed", "Hujjat maydoni noto'g'ri yoki juda uzun")
        out[k] = v
    if d.get("service") not in SERVICES:
        raise ApiError(422, "validation_failed", "Xizmat turi noto'g'ri")
    ev = d.get("evidence", [])
    if not isinstance(ev, list) or len(ev) > 8 or any(e not in EVIDENCE for e in ev):
        raise ApiError(422, "validation_failed", "Dalillar ro'yxati noto'g'ri")
    if d.get("notify", "none") not in NOTIFY:
        raise ApiError(422, "validation_failed", "Xabar berish turi noto'g'ri")
    out.update(service=d.get("service"), evidence=ev, notify=d.get("notify", "none"))
    return out


CORS_ORIGINS = {o.strip().rstrip("/") for o in (os.environ.get("LEXSIM_CORS_ORIGINS") or
                "https://lexlab.e-investment.uz,https://lexsim.e-investment.uz,http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()}
CORS_HEADERS = "Content-Type, X-Admin-Token, X-LexSim-Key, X-LexSim-Owner"
CORS_EXPOSE = "X-Duration-Ms, X-Word-Timings, X-Word-Timings-Source, X-TTS-Cache, Retry-After"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "LexSim/1"

    def end_headers(self):
        """CORS: faqat ruxsat etilgan frontend manbalari (cookie bilan — Allow-Credentials)."""
        origin = (self.headers.get("Origin") or "").rstrip("/") if hasattr(self, "headers") and self.headers else ""
        if origin in CORS_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
            self.send_header("Access-Control-Expose-Headers", CORS_EXPOSE)
        self.send_header("Vary", "Origin")
        super().end_headers()

    def do_OPTIONS(self):
        origin = (self.headers.get("Origin") or "").rstrip("/")
        self.send_response(204 if origin in CORS_ORIGINS else 403)
        if origin in CORS_ORIGINS:
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", CORS_HEADERS)
            self.send_header("Access-Control-Max-Age", "600")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (self.address_string(), fmt % args))

    def send_text(self, text, code=200):
        b = text.encode()
        self._st = code
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def send_json(self, code, obj, cookie=None, headers=None):
        self._st = code
        b = json.dumps(uz_norm(obj), ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(b)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def err(self, e):
        h = {"Retry-After": str(max(1, int(e.retry_after or 5)))} if (e.status == 429 or e.retry_after) else None   # 429 — doim Retry-After; 503 judge_pending ham
        self.send_json(e.status, {"error": {"code": e.code, "message": e.message}}, headers=h)

    def owner(self):
        for part in (self.headers.get("Cookie") or "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == "lexsim_owner" and v:
                return v
        return None

    def body(self, limit=16 * 1024):
        n = int(self.headers.get("Content-Length") or 0)
        if n > limit:
            raise ApiError(413, "payload_too_large", "So'rov juda katta")
        raw = self.rfile.read(n) if n else b""
        if not raw:
            return {}
        try:
            v = json.loads(raw)
        except ValueError:
            raise ApiError(400, "invalid_json", "So'rov formati noto'g'ri")
        if not isinstance(v, dict):
            raise ApiError(422, "validation_failed", "So'rov formati noto'g'ri")
        return v

    def route(self):
        p = self.path.split("?", 1)[0]
        for pre in ("/api/v1", "/v1"):
            if p.startswith(pre + "/") or p == pre:
                return p[len(pre):] or "/"
        return p

    def do_GET(self):
        try:
            p = self.route()
            if p in ("/monitor", "/monitor/"):
                b = (HERE / "monitor.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                return self.wfile.write(b)
            if p == "/admin/stats":
                self.admin()
                st = M.stats(dict(SETTINGS))
                st["voice"].update(V.STATS)
                vh = voice_health()
                st["voice"].update(servedFromCache=vh["servedFromCache"], servedTotal=vh["servedTotal"],
                                   coverage=vh["coverage"], autoPrerender=vh["autoPrerender"])
                return self.send_json(200, st)
            if p == "/rubrics" or p.startswith("/rubrics/"):     # «Nimaga asoslanib?» — mezonlar, bandlar, manbalar (ochiq)
                rid = p.rsplit("/", 1)[1] if p != "/rubrics" else None
                if rid and rid not in RB.RUBRICS:
                    raise ApiError(404, "not_found", "Rubrika topilmadi")
                src = RB.SOURCES
                return self.send_json(200, {"rubric": RB.public(rid), "sources": src} if rid else
                                      {"rubrics": [{"id": r["id"], "version": r["version"], "title": r["title"]} for r in RB.RUBRICS.values()],
                                       "sources": src})
            if p == "/review/queue" or p == "/review/stats" or p.startswith("/review/"):   # mentor (admin token)
                self.admin()
                q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                try:
                    if p == "/review/queue":
                        return self.send_json(200, {"items": RV.queue((q.get("kind") or [None])[0], (q.get("status") or ["pending"])[0])})
                    if p == "/review/stats":
                        return self.send_json(200, RV.stats())
                    return self.send_json(200, {"item": RV.get(p.rsplit("/", 1)[1])})
                except RV.ReviewError as e:
                    raise ApiError(e.status, e.code, e.message)
            if p == "/domains":
                return self.send_json(200, {"domains": LAB.DOMAINS, "source": LAB.STAT_URL})
            if p in ("/cases", "/moot/cases") or p.startswith(("/cases/", "/moot/cases/")):
                self.need_key()
                return self.lab_get(p)
            if p == "/health":
                return self.send_json(200, {"ok": True, "protocol": PROTOCOL, "version": VERSION, "features": FEATURES, "queue_depth": len(PENDING),
                                            "rag_db": NORMS.ok, "moot": MOOT.STATS, "npc": NPC.STATS, "llm": {"enabled": SETTINGS["llm"], "provider": LLM_PROVIDER, **LLM_STATS, **({"aihub": AIH.stats()} if LLM_PROVIDER == "aihub" else {})},
                                            "norms": len(NORMS.known), "scenarios": list(SCEN), "voice": voice_health()})
            if p == "/metrics":
                local = self.client_address[0] in ("127.0.0.1", "::1") and not self.headers.get("X-Real-IP")   # nginx orqali kelgani lokal emas
                if not (local or self.s2s()
                        or hmac.compare_digest((self.headers.get("X-Admin-Token") or "").encode(), ADMIN_TOKEN.encode())):
                    raise ApiError(401, "unauthorized", "metrics: lokal yoki token bilan")
                return self.send_text(prom_metrics())
            m2 = re.fullmatch(r"/store/cases/([\w.-]+)", p)
            if m2:
                self.need_key(admin_ok=False)
                own = self.headers.get("X-LexSim-Owner")
                if not own:                              # v1.5: majburiy (frontend bilan kelishilgan)
                    M.count("store_get_without_owner")
                    raise ApiError(422, "validation_failed", "X-LexSim-Owner sarlavhasi majburiy")
                try:
                    return self.send_json(200, ST.case_get(m2.group(1), own))
                except ST.StoreError as e:
                    return self.store_err(e)
            m2 = re.fullmatch(r"/teacher/cohorts/([\w.-]+)/(summary|hotspots)", p)
            if m2:
                self.need_key()
                f = ST.cohort_summary if m2.group(2) == "summary" else ST.cohort_hotspots
                return self.send_json(200, f(m2.group(1)))
            m2 = re.fullmatch(r"/voice/prerender/([\w-]+)", p)
            if m2:
                self.need_key()
                job = PRERENDER.get(m2.group(1))
                if not job:
                    raise ApiError(404, "job_not_found", "Bunday ish yo'q")
                return self.send_json(200, {k: job[k] for k in ("jobId", "done", "total", "failed", "finished", "waiting") if k in job})
            if p == "/voice/status":
                se = SETTINGS["stt"]
                fb = V.STT[se].get("fallback")
                if se.startswith("gpu") and gpu_state()["stt"] is not False:
                    stt_state, stt_eng = "gpu", se
                elif self.voice_up("stt", fb or se):
                    stt_state, stt_eng = "cpu", fb or se
                else:
                    stt_state, stt_eng = None, None
                return self.send_json(200, {"tts": "server" if self.voice_up("tts", SETTINGS["tts"]) else None,
                                            "stt": stt_state, "voices": list(V.VOICES),
                                            "ttsEngine": SETTINGS["tts"], "sttEngine": stt_eng,
                                            "gpu": gpu_state()})
            if p == "/scenarios":
                return self.send_json(200, {"scenarios": [v["public"] for v in SCEN.values()]})
            mc = re.fullmatch(r"/voice/cache/([0-9a-f]{64})(?:-\d+)?\.mp3", p)
            if mc:                                       # npcTurn.audio.url — cookie yoki kalit bilan
                if not (self.owner() or self.s2s()):
                    raise ApiError(403, "forbidden", "Avval sessiya oching")
                f = V.CACHE / (mc.group(1) + ".mp3")
                if not f.is_file():
                    raise ApiError(404, "not_found", "Audio topilmadi")
                b = f.read_bytes()
                self._st = 200
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(b)))
                self.send_header("Cache-Control", "private, max-age=31536000, immutable")
                self.send_header("X-Duration-Ms", str(V.mp3_duration_ms(b)))
                self.end_headers()
                return self.wfile.write(b)
            m = re.fullmatch(r"/sessions/([\w-]+)(/events|/report|/hint)?", p)
            if not m:
                raise ApiError(404, "not_found", "Topilmadi")
            s = self.own(m.group(1))
            if m.group(2) == "/events":
                q = self.path.split("?", 1)[1] if "?" in self.path else ""
                after = int((re.search(r"after=(\d+)", q) or [0, 0])[1])
                return self.send_json(200, {"events": [e for e in s["events"] if e["sequence"] > after],
                                            "snapshot": snapshot(s)})
            if m.group(2) == "/hint":
                if s["mode"] != "tutorial" or not LEVELS[s.get("level", "beginner")]["hints"]:
                    raise ApiError(409, "hints_disabled", "Bu rejim yoki darajada maslahatchi o'chirilgan")
                h = hint(s)
                if "preview=1" not in self.path:         # maslahat olindi: bosqich uchun bir marta −5 ball
                    with lock_for(s["id"]):
                        hs = s.setdefault("hints", [])
                        if s["status"] == "in-progress" and h["stage"] not in [x["stage"] for x in hs]:
                            t0 = _ts(s.get("startedAt")) or time.time()
                            hs.append({"stage": h["stage"], "title": h["title"], "at": max(0, round(time.time() - t0))})
                            save(s)
                            M.count("hints")
                return self.send_json(200, {"hint": h})
            if m.group(2) == "/report":
                if s["status"] != "report-ready" or not s["report"]:
                    raise ApiError(409, "report_not_ready", "Hisobot hali tayyor emas")
                return self.send_json(200, {"report": s["report"]})
            return self.send_json(200, {"snapshot": snapshot(s)})
        except ApiError as e:
            self.err(e)
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"XATO GET {self.path}: {e!r}\n")
            self.err(ApiError(500, "internal", "Ichki xatolik"))

    def voice(self, kind):
        """Ovoz: TTS — JSON {text, engine?} -> audio/wav; STT — xom audio (webm/ogg/wav) -> {text}."""
        M.note(kind=kind)
        owner = self.owner()
        if self.s2s():                                   # frontend Next serveri: X-LexSim-Key (+ X-LexSim-Owner)
            owner, limit = "key:" + (self.headers.get("X-LexSim-Owner") or "anon")[:80], RATE[kind + "_key"]
        elif owner:
            limit = RATE[kind]
        else:
            raise ApiError(403, "forbidden", "Avval sessiya oching")
        tts_body, free = None, False
        if kind == "tts":
            tts_body = self.body()
            tx, vc = tts_body.get("text"), V.resolve_voice(tts_body.get("voice") or "male")
            free = isinstance(tx, str) and vc is not None and V.cached(tx, vc)   # keshdan — limitga sanalmaydi
        rkey = f"{kind}:" + hashlib.sha256(owner.encode()).hexdigest()
        if not free and not rate_ok(rkey, limit):
            raise ApiError(429, "rate_limited", "Juda ko'p so'rov. Biroz kuting.", retry_after=rate_wait(rkey, limit))
        q = self.path.split("?", 1)[1] if "?" in self.path else ""
        eng = (re.search(r"engine=(\w+)", q) or [None, None])[1]
        t0 = time.time()
        try:
            if kind == "tts":
                body = tts_body
                text = body.get("text")
                voice = V.resolve_voice(body.get("voice") or "male") or body.get("voice")
                eng = body.get("engine") or eng or SETTINGS["tts"]
                if not isinstance(text, str) or not text.strip() or len(text) > 600:
                    raise ApiError(422, "validation_failed", "text 1–600 belgi bo'lishi kerak")
                if voice not in V.VOICES:
                    raise ApiError(422, "validation_failed", "voice: elder_m, male, female, female_alt yoki palitra nomi (judge_m2, lawyer_f1 ...)")
                if eng == "chatterbox_gpu" and not self.voice_up("tts", eng):
                    eng = "mms"                              # GPU kompyuter o'chiq — tez zaxira ovoz
                if not self.voice_up("tts", eng):
                    raise ApiError(404, "voice_unavailable", "Ovoz xizmati hozir ishlamayapti")
                with M.part("tts"):
                    mp3, hit = V.tts_mp3(text, voice, eng)
                    TTS_SERVE["hit" if hit else "miss"] += 1
                    if not V.cached(text, voice, gpu_only=True) and len(MMS_SERVED) < 500:
                        MMS_SERVED.add((text, voice))            # GPU qaytgach klonlangan ovozda qayta yoziladi
                M.note(voice={"type": "tts", "engine": eng, "voice": voice, "cache": hit, "chars": len(text),
                              "ms": round((time.time() - t0) * 1000)})
                self._st = 200
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(mp3)))
                self.send_header("Cache-Control", "private, max-age=86400")
                self.send_header("X-TTS-Cache", "hit" if hit else "miss")
                dur = V.mp3_duration_ms(mp3)
                self.send_header("X-Duration-Ms", str(dur))
                self.send_header("X-Word-Timings", json.dumps(V.word_timings(text, dur)))
                self.send_header("X-Word-Timings-Source", "estimate")
                self.end_headers()
                return self.wfile.write(mp3)
            n = int(self.headers.get("Content-Length") or 0)
            if n > 3 * 1024 * 1024:
                raise ApiError(413, "payload_too_large", "Audio juda katta (3 MB dan oshmasin)")
            if n < 100:
                raise ApiError(422, "validation_failed", "Audio bo'sh")
            audio = self.rfile.read(n)
            eng = eng or SETTINGS["stt"]
            if eng.startswith("gpu") and not self.voice_up("stt", eng):
                eng = V.STT[eng]["fallback"]                  # GPU kompyuter o'chiq — CPU Kotib
            if not self.voice_up("stt", eng):
                raise ApiError(404, "voice_unavailable", "Nutqni tanish xizmati hozir ishlamayapti")
            with M.part("stt"):
                r = V.stt_full(audio, eng)
            ms = round((time.time() - t0) * 1000)
            M.note(voice={"type": "stt", "engine": r["engine"], "seconds": r["audioSeconds"], "ms": ms})
            print(f"STT {r['engine']} {r['audioSeconds']} s audio -> {ms} ms {r['timings']} conf={r['confidence']}", flush=True)
            return self.send_json(200, {"text": r["text"], "confidence": r["confidence"], "lowConfidence": r["lowConfidence"],
                                        "engine": r["engine"], "audioSeconds": r["audioSeconds"], "ms": ms,
                                        "timings": r["timings"]})
        except V.VoiceError as e:
            raise ApiError(422 if "noto'g'ri" in str(e) or "o'qib" in str(e) or "qisqa" in str(e) or "bo'sh" in str(e)
                           else 502, "voice_failed", str(e))
        except (TimeoutError, OSError) as e:
            raise ApiError(504, "voice_timeout", f"Ovoz xizmati javob bermadi ({type(e).__name__})")

    @staticmethod
    def voice_up(kind, eng):
        port = (V.TTS if kind == "tts" else V.STT)[eng]["port"]
        st = next((v for k, v in M.SERVICES.items() if f"({port})" in k), None)
        return st is None or st["up"]                    # hali tekshirilmagan bo'lsa — urinib ko'ramiz

    def s2s(self):
        k = self.headers.get("X-LexSim-Key") or ""
        ok = bool(k) and hmac.compare_digest(k.encode(), LEXSIM_KEY.encode())
        own = self.headers.get("X-LexSim-Owner")
        if ok and own is not None and not re.fullmatch(r"[A-Za-z0-9_-]{8,64}", own):
            raise ApiError(422, "validation_failed", "X-LexSim-Owner: studentHash (8–64 belgi, hex)")
        return ok

    def lab_owner(self):
        own = self.headers.get("X-LexSim-Owner") or ""
        if not re.fullmatch(r"[A-Za-z0-9_-]{8,64}", own):
            raise ApiError(422, "validation_failed", "X-LexSim-Owner kerak (8–64 belgi)")
        return own

    def is_admin(self):
        return hmac.compare_digest((self.headers.get("X-Admin-Token") or "").encode(), ADMIN_TOKEN.encode())

    def lab_get(self, p):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        adm = self.is_admin()
        me = None if adm and not self.headers.get("X-LexSim-Owner") else self.lab_owner()
        try:
            if p in ("/cases", "/moot/cases"):
                dom = (q.get("domain") or [None])[0]
                items = LAB.listing(me, dom, (q.get("scope") or ["all"])[0], adm)
                if p == "/moot/cases":
                    items = [x for x in items if "moot" in x["modes"] and x["status"] == "approved"]
                return self.send_json(200, {"cases": items})
            m = re.fullmatch(r"/cases/([\w-]{3,40})/solutions", p)
            if m:
                return self.send_json(200, {"solutions": LAB.solutions(me, m.group(1), adm, code=(q.get("code") or [None])[0])})
            m = re.fullmatch(r"/cases/drafts/(d_[0-9a-f]{12})", p)
            if m:
                return self.send_json(200, {"draft": LAB.get_draft(me, m.group(1))})
            m = re.fullmatch(r"/(moot/)?cases/([\w-]{3,40})", p)
            if m:
                return self.send_json(200, {"case": LAB.get(me, m.group(2), adm, full=bool(m.group(1)), code=(q.get("code") or [None])[0])})
        except LAB.LabError as e:
            raise ApiError(e.status, e.code, e.message)
        raise ApiError(404, "not_found", "Topilmadi")

    def lab_post(self, p, body):
        if not isinstance(body, dict):
            raise ApiError(422, "validation_failed", "JSON obyekt kerak")
        try:
            m = re.fullmatch(r"/cases/([\w-]{3,40})/review", p)
            if m:
                if not self.is_admin():
                    raise ApiError(401, "unauthorized", "Faqat mentor (admin token)")
                LAB.review(m.group(1), body.get("decision"), body.get("note") or "")
                return self.send_json(200, {"case": LAB.get(None, m.group(1), admin=True)})
            me = self.lab_owner()
            prof = lambda t: has(normalize(t), *PROFANITY)  # noqa: E731
            m = re.fullmatch(r"/cases/([\w-]{3,40})/solutions", p)
            if m:
                vfn = lambda vid, side, _c=m.group(1): MOOT.by_id(vid, side, owner=me, case_id=_c)  # noqa: E731
                return self.send_json(201, {"solution": LAB.add_solution(me, m.group(1), body, prof, vfn, body.get("code"))})
            m = re.fullmatch(r"/solutions/(sol_[0-9a-f]{10})", p)
            if m:
                sol = LAB.edit_solution(me, m.group(1), body, prof, self.is_admin())
                return self.send_json(200, {"solution": sol, "deleted": sol is None})
            m = re.fullmatch(r"/cases/([\w-]{3,40})/visibility", p)
            if m:
                return self.send_json(200, {"case": LAB.set_visibility(me, m.group(1), body.get("visibility"))})
            if p == "/cases/drafts":
                if not rate_ok("lab:" + me, RATE["lab_draft"]):
                    raise ApiError(429, "rate_limited", "Juda ko'p so'rov. Biroz kuting.", retry_after=60)
                if LLM_PROVIDER != "aihub" or not AIH.enabled():
                    raise ApiError(503, "llm_unavailable", "Til modeli ulanmagan")
                st_ = body.get("story") if isinstance(body.get("story"), str) else ""
                ans = body.get("answers") if isinstance(body.get("answers"), str) else ""
                story = (st_[:4000 - min(len(ans), 1200) - 30] + ("\nQo'shimcha javoblar: " + ans[:1200] if ans else ""))
                did = LAB.start_draft(me, body.get("domain"), story, AIH.ask_task, lab_rag, NORMS.known if NORMS and NORMS.ok else None)
                return self.send_json(202, {"draft": {"id": did, "status": "working"}}, headers={"Retry-After": "10"})
            cid = None if p == "/cases" else p.rsplit("/", 1)[1]
            if not isinstance(body.get("case"), dict):
                raise ApiError(422, "validation_failed", "case obyekt bo'lishi kerak")
            case, issues = LAB.save(me, body.get("case"), body.get("domain"), NORMS.known if NORMS and NORMS.ok else None,
                                    lab_allowed(body.get("case")), cid, body.get("visibility") or "public")
            return self.send_json(201 if cid is None else 200, {"case": case, "issues": issues})
        except LAB.LabError as e:
            raise ApiError(e.status, e.code, e.message)
        except (AttributeError, TypeError, KeyError, ValueError) as e:     # noto'g'ri tuzilgan JSON — 500 emas, 422
            print(f"CASELAB 422: {type(e).__name__}: {e}", flush=True)
            raise ApiError(422, "validation_failed", "Ma'lumot tuzilishi noto'g'ri")

    def need_key(self, admin_ok=True):
        if self.s2s():
            return
        if admin_ok and hmac.compare_digest((self.headers.get("X-Admin-Token") or "").encode(), ADMIN_TOKEN.encode()):
            return
        raise ApiError(401, "unauthorized", "X-LexSim-Key noto'g'ri yoki yo'q")

    def store_err(self, e):
        self.send_json(e.status, {"error": {"code": e.code, "message": e.message, **e.extra}})

    def admin(self):
        tok = self.headers.get("X-Admin-Token") or ""
        if not hmac.compare_digest(tok.encode(), ADMIN_TOKEN.encode()):
            raise ApiError(401, "unauthorized", "Admin token noto'g'ri")

    def own(self, sid):
        s = load(sid)
        if not s:
            raise ApiError(404, "session_not_found", "Sessiya topilmadi")
        tok = self.owner() or ""
        if not hmac.compare_digest(hashlib.sha256(tok.encode()).hexdigest(), s["owner_hash"]):
            raise ApiError(403, "forbidden", "Bu sessiya sizga tegishli emas")
        return s

    def do_PUT(self):
        self._st = 500
        M.begin("store")
        try:
            p = self.route()
            m = re.fullmatch(r"/store/cases/([\w.-]+)", p)
            if not m:
                raise ApiError(404, "not_found", "Topilmadi")
            self.need_key(admin_ok=False)
            if not rate_ok("store:" + (self.headers.get("X-LexSim-Owner") or "anon"), RATE["store"]):
                raise ApiError(429, "rate_limited", "Juda ko'p so'rov. Biroz kuting.")
            n = int(self.headers.get("Content-Length") or 0)
            if n > ST.MAX_STATE + 4096:
                raise ApiError(413, "payload_too_large", "Ish holati juda katta")
            try:
                body = json.loads(self.rfile.read(n) or b"{}")
            except ValueError:
                raise ApiError(400, "invalid_json", "So'rov formati noto'g'ri")
            try:
                self.send_json(200, ST.case_put(m.group(1), body, self.headers.get("X-LexSim-Owner")))
            except ST.StoreError as e:
                self.store_err(e)
        except ApiError as e:
            self.err(e)
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            self.err(ApiError(500, "internal", "Ichki xatolik"))
        finally:
            M.end(self._st)

    def do_POST(self):
        self._st = 500
        M.begin("other")
        try:
            self._post()
        finally:
            M.end(self._st)

    def _post(self):
        try:
            p = self.route()
            if p in ("/voice/tts", "/voice/stt"):
                return self.voice(p.rsplit("/", 1)[1])
            big = p in ("/xapi/statements", "/voice/prerender", "/moot/judge", "/cases") or p.startswith("/cases/")   # katta tana — 512 KB gacha (bahs bayonnomasi, case)
            body = {} if p == "/admin/voice/clone" else self.body(512 * 1024 if big else 16 * 1024)
            if p == "/admin/voice/clone":
                self.admin()
                q = self.path.split("?", 1)[1] if "?" in self.path else ""
                name = (re.search(r"name=([\w-]+)", q) or [None, ""])[1]
                n = int(self.headers.get("Content-Length") or 0)
                if not (100 < n <= 3 * 1024 * 1024):
                    raise ApiError(422, "validation_failed", "Audio namuna 5–10 s, 3 MB gacha bo'lsin")
                try:
                    info = V.cb_clone(self.rfile.read(n), name)
                except V.VoiceError as e:
                    raise ApiError(422, "voice_failed", str(e))
                except OSError as e:
                    raise ApiError(502, "voice_failed", f"GPU Chatterbox javob bermadi ({type(e).__name__})")
                return self.send_json(200, {"ok": True, "name": name, "info": info, "voices": sorted(V.cb_voices())})
            if p in ("/cases/drafts", "/cases") or re.fullmatch(r"/cases/[\w-]{3,40}(/review|/solutions|/visibility)?|/solutions/sol_[0-9a-f]{10}", p):
                self.need_key()
                return self.lab_post(p, body)
            m_rv = re.fullmatch(r"/review/(rv_[0-9a-f]{12})", p)
            if m_rv:                                    # mentor qarori: approve | adjust | reject
                self.admin()
                try:
                    return self.send_json(200, {"item": RV.decide(m_rv.group(1), body, (self.headers.get("X-Reviewer") or "mentor")[:64])})
                except RV.ReviewError as e:
                    raise ApiError(e.status, e.code, e.message)
            if p == "/npc/history":                     # frontend ssenariy gaplarini ham suhbat xotirasiga yozadi
                self.need_key()
                items = body.get("items") if isinstance(body.get("items"), list) else []
                NPC.remember(self.headers.get("X-LexSim-Owner") or "", body, items[:20])
                return self.send_json(200, {"ok": True})
            if p == "/npc/reply":                       # situation/match/clarify bo'lmasa — AI qahramon
                self.need_key()
                if not rate_ok("npc:" + (self.headers.get("X-LexSim-Owner") or "anon"), RATE["npc"]):
                    raise ApiError(429, "rate_limited", "Juda ko'p so'rov. Biroz kuting.", retry_after=10)
                if not SETTINGS["llm"] or LLM_PROVIDER != "aihub" or not AIH.enabled():
                    raise ApiError(503, "npc_unavailable", "Til modeli ulanmagan")
                try:
                    r = NPC.reply(body, AIH.ask_task, lambda t: has(normalize(t), *PROFANITY), LAB.redact,
                                  owner=self.headers.get("X-LexSim-Owner") or "", repeat_fn=lambda u: repeat_intent(normalize(u)))
                except NPC.NpcError as e:
                    raise ApiError(e.status, e.code, e.message, retry_after=10 if e.code == "npc_pending" else None)
                return self.send_json(200, {"reply": r})
            if p == "/moot/judge":
                self.need_key()
                if not rate_ok("moot:" + (self.headers.get("X-LexSim-Owner") or "anon"), RATE["moot_judge"]):
                    raise ApiError(429, "rate_limited", "Juda ko'p so'rov. Biroz kuting.", retry_after=10)
                if LLM_PROVIDER != "aihub" or not AIH.enabled():
                    raise ApiError(503, "judge_unavailable", "Til modeli ulanmagan. Dastlabki baho ko'rsatiladi.")
                try:
                    v = MOOT.judge(body, AIH.ask_task, lambda t: has(normalize(t), *PROFANITY), owner=self.headers.get("X-LexSim-Owner"))
                except MOOT.JudgeError as e:
                    raise ApiError(e.status, e.code, e.message, retry_after=15 if e.code == "judge_pending" else None)
                return self.send_json(200, {"verdict": v, "verdictId": MOOT.key_of(body)[:16], "explain": MOOT.explain_of(body)})
            if p == "/nlu/match":
                self.need_key()
                if not rate_ok("nlu:" + (self.headers.get("X-LexSim-Owner") or "anon"), RATE["nlu"]):
                    raise ApiError(429, "rate_limited", "Juda ko'p so'rov. Biroz kuting.")
                M.note(kind="nlu")
                try:
                    res = NLU.match(body, normalize, nlu_rerank, exact_refs,
                                    lambda r: (not NORMS.ok) or r in NORMS.known, art_label)
                except ValueError as e:
                    raise ApiError(422, "validation_failed", str(e))
                sit = nlu_situation(body.get("utterance") or "")
                if sit:
                    res["situation"] = sit                 # frontend: «tushunmadim» o'rniga qahramonning odamdek javobi
                top = (res.get("match") or (res.get("alternatives") or [{}])[0]) or {}
                M.count("nlu_" + ("match" if res.get("match") else (res.get("reason") or "none")))
                print(f"NLU {res.get('reason') or 'match'} sit={(sit or {}).get('id')} top={top.get('id')}:{top.get('score')} engine={res['engine']} "
                      f"cands={len(body.get('candidates') or [])} words={len((body.get('utterance') or '').split())} "
                      f"mode={body.get('inputMode') or 'text'} {res['ms']} ms", flush=True)   # matnsiz — maxfiylik
                return self.send_json(200, res)
            if p == "/xapi/statements":
                self.need_key(admin_ok=False)
                try:
                    ids, stored = ST.xapi_put(body.get("statements", body) if isinstance(body, dict) else body)
                    return self.send_json(200, {"stored": stored, "ids": ids})
                except ST.StoreError as e:
                    return self.store_err(e)
            if p == "/voice/prerender":
                self.need_key()
                items = body.get("items")
                if not isinstance(items, list) or not (1 <= len(items) <= 1000) or not all(
                        isinstance(i, dict) and isinstance(i.get("text"), str) and 0 < len(i["text"]) <= 600
                        and (i.get("voice") or "male") in V.VOICES for i in items):
                    raise ApiError(422, "validation_failed", "items: 1–1000 ta {text ≤ 600, voice}")
                jid = "pr_" + secrets.token_urlsafe(8)
                PRERENDER[jid] = {"jobId": jid, "done": 0, "total": len(items), "failed": [], "finished": False}
                threading.Thread(target=run_prerender, args=(jid, items, body.get("engine") or SETTINGS["tts"]),
                                 daemon=True).start()
                return self.send_json(202, {"jobId": jid, "total": len(items)})
            if p == "/admin/settings":
                self.admin()
                for k, typ in (("llm", bool), ("rag", bool), ("sem", bool), ("llm_timeout", (int, float)), ("tts", str), ("stt", str)):
                    if k in body:
                        bad = (not isinstance(body[k], typ) or isinstance(body[k], bool) and typ != bool
                               or (k == "llm_timeout" and not 10 <= body[k] <= 300)
                               or (k == "tts" and body[k] not in V.TTS) or (k == "stt" and body[k] not in V.STT))
                        if bad:
                            raise ApiError(422, "validation_failed", f"{k} noto'g'ri")
                        SETTINGS[k] = body[k]
                SETTINGS_FILE.write_text(json.dumps(SETTINGS))
                print(f"Sozlamalar o'zgardi: {SETTINGS}", flush=True)
                return self.send_json(200, {"settings": SETTINGS})
            if p == "/sessions":
                M.note(kind="sessions")
                M.count("sessions")
                return self.create(body)
            m = re.fullmatch(r"/sessions/([\w-]+)/(interactions|turns|documents|finish|appeal)", p)
            if not m:
                raise ApiError(404, "not_found", "Topilmadi")
            sid, act = m.groups()
            M.note(kind=act)
            s = self.own(sid)
            if not rate_ok(f"{sid}:{act}", RATE.get(act, 60)):
                raise ApiError(429, "rate_limited", "Juda ko'p so'rov. Biroz kuting.")
            with lock_for(sid):
                s = load(sid)
                if act == "appeal":
                    return self.appeal(s, body)
                cid = body.get("clientTurnId") if act == "turns" else body.get("clientActionId")
                if not isinstance(cid, str) or not (8 <= len(cid) <= 64):
                    raise ApiError(422, "validation_failed", "clientTurnId/clientActionId noto'g'ri")
                if cid in s["idem"]:                     # idempotentlik: birinchi javobning aynan o'zi
                    code, resp = s["idem"][cid]
                    return self.send_json(code, resp)
                if s.get("pending") and act in ("turns", "finish", "documents"):
                    raise ApiError(409, "turn_pending", "Raqib advokat javob tayyorlamoqda. Biroz kuting.")
                M.note(stage=s["stage"])
                eng = Engine(s)
                if act == "turns" and SETTINGS["llm"] and self.needs_llm(s, body):
                    return self.async_turn(s, eng, body, cid)
                getattr(self, "a_" + act)(eng, body)
                resp = frozen({"events": eng.events, "snapshot": snapshot(s)})
                s["idem"][cid] = (200, resp)
                with M.part("db"):
                    save(s)
                return self.send_json(200, resp)
        except ApiError as e:
            self.err(e)
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"XATO POST {self.path}: {e!r}\n")
            import traceback
            traceback.print_exc()
            self.err(ApiError(500, "internal", "Ichki xatolik"))

    def needs_llm(self, s, body):
        """Shu gap raqib LLM javobini talab qiladimi — sessiya nusxasida quruq yurgizib tekshiriladi."""
        if s["status"] != "in-progress" or not s["turns"]:
            return False
        try:
            text, mode, opt, low = self.resolve_turn(s, body)
        except ApiError:
            return False
        if low:
            return False
        c = copy.deepcopy({k: v for k, v in s.items() if k not in ("events", "idem")})
        c["events"], c["idem"] = [], {}
        c["sequence"] = s["sequence"]
        e = Engine(c, dry=True)
        e.forced = dict((opt or {}).get("km") or {})
        try:
            e.turn(text)
        except Exception:  # noqa: BLE001
            return False
        return e.would_llm

    def async_turn(self, s, eng, body, cid):
        """202: talaba gapi darhol qaytadi, raqib javobi keyin /events?after=N orqali keladi (§4.1 A)."""
        text, mode, opt, low = self.resolve_turn(s, body)
        u = eng.user(text)
        u["inputMode"], u["stage"] = mode, s.get("stage")
        self.apply_option(eng, opt, u["id"])
        s["pending_forced"], s["pending_voice"] = eng.forced, mode == "voice"
        s["pending"] = {"turn": u["id"], "since": time.time()}
        n_user = sum(1 for t in s["turns"] if t["speaker"] == "user")
        fill = PROC.CFG.get("fillers", {}).get("judge") or []
        if fill and n_user - s.get("filler_at", -99) >= 3:      # kutishni yashirish: har 3 navbatda ko'pi bilan 1 marta
            s["filler_at"] = n_user
            eng.npc(fill[((s.get("seed") or 0) + n_user) % len(fill)])
        eng.emit("session.status", {"status": s["status"]})
        resp = frozen({"events": eng.events, "snapshot": snapshot(s)})
        s["idem"][cid] = (202, resp)
        save(s)
        PENDING.add(s["id"])
        threading.Thread(target=run_async_turn, args=(s["id"], text, u["id"]), daemon=True).start()
        return self.send_json(202, resp)

    def create(self, body):
        owner, cookie = self.owner(), None
        if not owner:
            owner = secrets.token_urlsafe(32)
            cookie = (f"lexsim_owner={owner}; HttpOnly; SameSite=Lax; Path=/; Max-Age=2592000"
                      + ("; Secure" if SECURE_COOKIE else ""))
        if not rate_ok("owner:" + hashlib.sha256(owner.encode()).hexdigest(), RATE["sessions"]):
            raise ApiError(429, "rate_limited", "Juda ko'p so'rov. Biroz kuting.")
        scid = body.get("scenarioId")
        if scid not in SCEN:
            raise ApiError(404, "scenario_not_found", "Bunday ssenariy yo'q")
        mode = body.get("mode") or "tutorial"
        if mode not in ("tutorial", "assessment"):
            raise ApiError(422, "validation_failed", "mode noto'g'ri")
        seed = body.get("seed")
        if seed is None:
            seed = random.randint(1, 2 ** 31 - 1)
        elif not isinstance(seed, int):
            raise ApiError(422, "validation_failed", "seed butun son bo'lishi kerak")
        level = body.get("level") or "beginner"
        if level not in LEVELS:
            raise ApiError(422, "validation_failed", "level: beginner, intermediate yoki advanced")
        s = new_session(scid, mode, seed, owner, level)
        _sess_cache[s["id"]] = s
        save(s)
        self.send_json(200, {"snapshot": snapshot(s)}, cookie=cookie)

    # --- mutatsiyalar
    def a_interactions(self, eng, body):
        s, act = eng.s, body.get("action")
        if act not in ("start", "sit-at-desk", "enter-room", "open-terminal", "inspect-phone", "stand", "sit",
                       "reveal-options", "silence"):
            raise ApiError(422, "validation_failed", "action noto'g'ri")
        if act in ("stand", "sit"):                      # talaba tik turdi / o'tirdi (IPK-167 qoidasi uchun)
            s["standing"] = act == "stand"
            ctx = body.get("context") if isinstance(body.get("context"), dict) else {}
            dur = ctx.get("during") if isinstance(ctx.get("during"), dict) else {}
            if (act == "stand" and dur.get("role") in ("opponent", "witness", "expert") and s["status"] == "in-progress"
                    and s.get("stage") != "yakun"):      # raqib gapirayotganda turdi — yengil eslatma, ballsiz
                n = s["flags"].get("sit_ok_n", 0)
                s["flags"]["sit_ok_n"] = n + 1
                if n % 3 == 0:
                    H = PROC.CFG["hall"]
                    eng.npc(H["sit_ok"][(n // 3) % len(H["sit_ok"])], emotion="calm", gesture="nod")
            return
        if act == "start":
            if s["status"] == "briefing":
                s["startedAt"] = now_iso()
                eng.status("in-progress")
            return
        if s["status"] != "in-progress":
            raise ApiError(409, "session_not_active", "Sessiya faol emas")
        if act == "sit-at-desk":
            if s.get("standing") is None:                # B1: holat noma'lum bo'lsa — talaba o'tirgan deb hisoblanadi
                s["standing"] = False
            eng.opening()
        lv = s.get("level", "beginner")
        if act == "reveal-options":                      # intermediate: variantlarni ochish, bosqich uchun bir marta −10
            if lv == "advanced":
                raise ApiError(422, "options_disabled", "Bu darajada variantlar yo'q")
            if lv == "intermediate" and s.get("stage") not in s.setdefault("revealed", []):
                s["revealed"].append(s["stage"])
                t0 = _ts(s.get("startedAt")) or time.time()
                s.setdefault("reveals", []).append({"stage": s["stage"], "at": max(0, round(time.time() - t0))})
        if act == "silence" and s["turns"] and s.get("stage") != "yakun":   # klient jimlik chegarasi o'tganini xabar qiladi
            if lv == "advanced":
                eng.viol("silence", s["turns"][-1]["id"])
                eng.t("W_SILENCE", role_name=eng.rn())
            elif lv == "intermediate":
                eng.t("W_SILENCE_SOFT", role_name=eng.rn())

    def resolve_turn(self, s, body):
        """TurnRequest -> (text, inputMode, option|None, stt_low). §2.2."""
        lv = s.get("level", "beginner")
        oid, text = body.get("optionId"), body.get("text")
        if (oid is None) == (text is None):
            raise ApiError(422, "validation_failed", "optionId yoki text — aniq bittasi kerak")
        mode = body.get("inputMode") or ("option" if oid else "text")
        if mode not in ("option", "text", "voice"):
            raise ApiError(422, "validation_failed", "inputMode: option, text yoki voice")
        opt = None
        if oid is not None:
            if lv == "advanced":
                raise ApiError(422, "options_disabled", "Bu darajada variantlar yo'q")
            if lv == "intermediate" and s.get("stage") not in s.get("revealed", []):
                raise ApiError(409, "options_hidden", "Variantlar yopiq. Avval variantlarni oching (−10 ball).")
            opt = next((o for o in stage_options(s) if o["id"] == oid), None)
            if not opt:
                raise ApiError(422, "option_not_found", "Bunday variant yo'q")
            text, mode = opt["text"], "option"
        if not isinstance(text, str) or not (1 <= len(text.strip()) <= 800):
            raise ApiError(422, "validation_failed", "Matn 1–800 belgi bo'lishi kerak")
        stt = body.get("stt") or {}
        low = mode == "voice" and isinstance(stt.get("confidence"), (int, float)) and stt["confidence"] < NLU.TH["stt_min"]
        pr, clean = body.get("presence"), {}
        if isinstance(pr, dict):                         # noto'g'ri maydonlar e'tiborga olinmaydi
            if isinstance(pr.get("heardTurnId"), str):
                clean["heard"] = pr["heardTurnId"][:64]
            sp = pr.get("spokenSeconds")
            if isinstance(sp, (int, float)) and not isinstance(sp, bool) and 0 <= sp <= 600:
                clean["spoken"] = float(sp)
            if isinstance(pr.get("standing"), bool):
                clean["standing"] = pr["standing"]
        s["presence_now"] = clean
        return text.strip(), mode, opt, low

    def a_turns(self, eng, body):
        s = eng.s
        if s["status"] != "in-progress":
            raise ApiError(409, "session_not_active", "Sessiya faol emas")
        if not s["turns"]:
            raise ApiError(409, "dialogue_not_started", "Suhbat hali boshlanmagan")
        text, mode, opt, low = self.resolve_turn(s, body)
        u = eng.user(text)
        u["inputMode"], u["stage"] = mode, s.get("stage")
        if low:                                    # STT ishonchi past — qayta so'raymiz, ball ayirmaymiz
            u["sttLow"] = True
            eng.t("W_REPEAT")
            return
        self.apply_option(eng, opt, u["id"])
        eng.voice = mode == "voice"
        eng.process(text, u["id"])
        set_feedback(s, u["id"])

    @staticmethod
    def apply_option(eng, opt, tid):
        if not opt:
            return
        eng.forced = dict(opt.get("km") or {})
        eng.s.setdefault("optdec", {})[tid] = {"optionId": opt["id"], **{k: opt.get(k) for k in ("tone", "why", "points", "article", "violation")}}
        if opt.get("tone") == "bad" and opt.get("violation") and not eng.dry:
            eng.viol(opt["violation"], tid)

    def a_documents(self, eng, body):
        s = eng.s
        if s["status"] != "in-progress":
            raise ApiError(409, "session_not_active", "Sessiya faol emas")
        if s["documentSubmitted"]:
            raise ApiError(409, "document_locked", "Hujjat allaqachon yuborilgan")
        d = validate_draft(body.get("draft"))
        if body.get("submit") is True:
            if d["service"] is None:
                raise ApiError(422, "service_required", "Xizmat turini tanlang")
            s["document"], s["documentSubmitted"] = d, True
            eng.objective("document")
        else:
            s["document"] = d

    def a_finish(self, eng, body):
        s = eng.s
        if s["status"] == "report-ready":
            return
        if s["status"] != "in-progress":
            raise ApiError(409, "session_not_active", "Sessiya faol emas")
        eng.finish()

    def appeal(self, s, body):
        reason = body.get("reason")
        if not isinstance(reason, str) or not (10 <= len(reason.strip()) <= 1500):
            raise ApiError(422, "validation_failed", "Sabab 10–1500 belgi bo'lishi kerak")
        if s["status"] != "report-ready" or not s["report"]:
            raise ApiError(409, "report_not_ready", "Hisobot hali tayyor emas")
        s["report"]["appeal"] = {"at": now_iso(), "reason": reason.strip()}
        s["report"]["reviewStatus"] = "needs-mentor"
        save(s)
        self.send_json(200, {"report": s["report"]})


def set_feedback(s, tid):
    """Darhol fikr-mulohaza (beginner — har javob, intermediate — faqat jiddiy xato).
    Variant tanlangan bo'lsa — uning tone va article'i shu yerda (tanlangandan keyin) oshkor qilinadi."""
    od = s.get("optdec", {}).get(tid)
    _set_feedback(s, tid)
    if od and s.get("last_feedback", {}).get("turn") == tid:
        f = s["last_feedback"]
        f["optionId"], f["tone"] = od["optionId"], od.get("tone") or f["tone"]
        if od.get("tone") == "good":
            f["message"] = "To'g'ri: " + (od.get("why") or "tanlov to'g'ri.")
        f["article"] = f.get("article") or _confirmed(od.get("article"))


def _set_feedback(s, tid):
    od = s.get("optdec", {}).get(tid)
    if od and od.get("tone") == "bad":            # tanlangan variantning o'z izohi aniqroq (mentor yozgan)
        kinds = {v["kind"] for v in s["violations"] if v["turn"] == tid}
        s["last_feedback"] = {"tone": "bad", "message": od.get("why"), "article": _confirmed(od.get("article")),
                              "serious": bool(kinds & SERIOUS) or od.get("violation") in SERIOUS, "turn": tid}
        return
    vs = [v for v in s["violations"] if v["turn"] == tid]
    if vs:
        v = vs[0]
        pts, why, art = VIOL_INFO.get(v["kind"], (0, None, None))
        s["last_feedback"] = {"tone": "bad", "message": v.get("why") or why, "article": _confirmed(art), "serious": v["kind"] in SERIOUS, "turn": tid}
        return
    od = s.get("optdec", {}).get(tid)
    if od and od.get("tone") == "bad":
        s["last_feedback"] = {"tone": "bad", "message": od.get("why"), "article": _confirmed(od.get("article")),
                              "serious": od.get("violation") in SERIOUS, "turn": tid}
        return
    notes = s.get("dec_notes", {}).get(tid)
    if notes and not s.get("dec_km", {}).get(tid):
        f = notes[-1]
        s["last_feedback"] = {"tone": f["tone"] if f["tone"] in ("good", "bad") else "info", "message": f["why"],
                              "article": f.get("article"), "serious": False, "turn": tid}
        return
    kms = s.get("dec_km", {}).get(tid, {})
    if kms:
        kid, lv = next(iter(kms.items()))
        key = (s["student_role"], kid) if (s["student_role"], kid) in KM_ARTICLE else ("any", kid)
        good = lv >= 3
        gw = good_why(s, KM_STAGE.get(key, ""))
        msg = ((f"To'g'ri: {gw}" if gw else f"{KM_NAMES[kid]}: to'g'ri yo'nalish.") if good else
               f"{KM_NAMES[kid]}: zaif. " + (_hint_for(s["student_role"], KM_STAGE.get(key, "")).get("xato") or ""))
        s["last_feedback"] = {"tone": "good" if good else "bad", "message": msg, "article": _confirmed(KM_ARTICLE.get(key)),
                              "serious": False, "turn": tid}
        return
    t = next((x for x in s["turns"] if x["id"] == tid), {})
    stage = t.get("stage") or ""
    if stage == "tushuntirish" and s["student_role"] == "davogar-vakili":     # da'vo talabi: nima yetishmadi
        nt = normalize(t.get("text", ""))
        parts = [("shartnoma (32-P)", r"shartnoma"), ("qarz summasi", r"25 ?620|asosiy qarz|summa"),
                 ("huquqiy asos (FK 544-modda)", r"544|ijara haq"), ("penya asosi (8.5-band)", r"peny|neustoyk|8\.5")]
        miss = [n for n, pat in parts if not re.search(pat, nt)]
        if not miss:
            s["last_feedback"] = {"tone": "good", "message": "To'g'ri: " + good_why(s, stage), "article": _confirmed("FK-544"),
                                  "serious": False, "turn": tid}
        else:
            s["last_feedback"] = {"tone": "bad", "message": "Talabda yetishmadi: " + ", ".join(miss) + ".",
                                  "article": _confirmed("FK-544"), "serious": False, "turn": tid}
        return
    gw = good_why(s, stage) if stage in ("rad", "huquqlar", "oldingi", "qoshimcha") else None
    art = next((o.get("article") for o in (OPTIONS.get(stage, {}).get("any") or []) if o.get("tone") == "good"), None)
    s["last_feedback"] = {"tone": "good" if gw else "info", "message": f"To'g'ri: {gw}" if gw else "Qabul qilindi.",
                          "article": _confirmed(art) if gw else None, "serious": False, "turn": tid}


def good_why(s, stage):
    """Bosqichdagi to'g'ri javobning izohi (beginner: nega to'g'ri)."""
    st = OPTIONS.get(stage, {})
    opts = st.get(s["student_role"]) or st.get("any") or []
    return next((o.get("why") for o in opts if o.get("tone") == "good"), None)


def nlu_rerank(query, texts):
    if not SEM_KEY or V.gpu_down("rerank"):
        return None
    try:
        req = urllib.request.Request(SEM_URL, method="POST", data=json.dumps({"query": query[:1500], "texts": texts[:50]}).encode(),
                                     headers={"Content-Type": "application/json", "X-Key": SEM_KEY})
        with M.part("rerank"), urllib.request.urlopen(req, timeout=SEM_TIMEOUT) as r:
            return json.loads(r.read())["scores"]
    except Exception as e:  # noqa: BLE001
        V.gpu_failed("rerank")
        M.count("sem_fail", type(e).__name__)
        return None


def run_prerender(jid, items, engine):
    job = PRERENDER[jid]
    for i, it in enumerate(items):
        while time.time() - V.LIVE["t"] < 25:      # STT birinchi: talaba gapirayotganda render GPU'ni band qilmaydi
            job["waiting"] = "jonli STT — GPU bo'shashini kutyapti"
            time.sleep(2)
        job.pop("waiting", None)
        for attempt in range(41):                    # GPU o'chiq bo'lsa ~20 daqiqagacha kutadi, MMS bilan almashtirmaydi
            try:
                V.tts_mp3(it["text"], it.get("voice") or "male", engine, strict=engine == "chatterbox_gpu")
                break
            except Exception as e:  # noqa: BLE001
                if engine != "chatterbox_gpu" or attempt == 40:
                    job["failed"].append({"index": i, "error": type(e).__name__})
                    break
                job["waiting"] = "GPU javob bermayapti — kutilmoqda"
                time.sleep(30)
        job.pop("waiting", None)
        job["done"] = i + 1
    job["finished"] = True
    print(f"Prerender {jid}: {job['done'] - len(job['failed'])}/{job['total']} tayyor ({engine})", flush=True)


TTS_SERVE = {"hit": 0, "miss": 0}          # talabaga berilgan ovozlar: keshdan / yangi (maqsad: ≥ 90 % keshdan)
FRONT_LINES = HERE / "voice_lines.json"   # frontend lines.json («Ish yo'li» xonalari); yangisi kelsa — shu faylni almashtiring
AUTO = {"jobId": None, "canonical": 0, "missingAtStart": 0}


def canonical_lines():
    """Tizim aytadigan barcha doimiy gaplar (text, voice) — prerender va qamrov uchun. Yangi gap qo'shilsa avtomatik tushadi."""
    names, items = list(ROLE_NAME.values()), []
    for k, t in T.items():
        v = "female" if k in ("RISE", "CLERK_REPORT") else "elder_m"
        try:
            if "{" not in t:
                items.append((t, v))
            elif "{role_name}" in t:
                items += [(t.format(role_name=n), v) for n in names]
            elif "{other}" in t:
                items += [(t.format(other=n), v) for n in names]
        except (KeyError, IndexError):
            pass
    J = PROC.J
    for t in J.values():
        if isinstance(t, str):
            items += [(t.format(opp=n.lower()), "elder_m") for n in names] if "{opp}" in t else [(t, "elder_m")]
    for st in J["RESUME"].values():
        for t in st.values():
            items += [(x, "elder_m") for x in (t if isinstance(t, list) else [t])]
    for st in PROC.CFG["reask_text"].values():
        for v in st.values():
            for t in (v if isinstance(v, list) else [v]):
                items += [(t.format(role_name=n), "elder_m") for n in names] if "{role_name}" in t else [(t, "elder_m")]
    for sit in PROC.CFG.get("situations", []):
        for t in sit["lines"] + sit.get("early_lines", []):
            items += [(t.format(role_name=n), "elder_m") for n in names] if "{role_name}" in t else [(t, "elder_m")]
    ex, rc = PROC.CFG["powers_excuse"], PROC.CFG["recusal"]
    items += [(t, "elder_m") for t in ex["first"] + [ex["then"]] + PROC.CFG["order_ladder"] + [rc["postpone"]]]
    items += [(rc["weak"].format(who=w), "elder_m") for w in rc["who"].values()]
    for sit in PROC.CFG.get("nlu_situations", []):
        for role, v in sit["replies"].items():
            for vc in PROC.CFG["nlu_voices"].get(role, ["male"]):
                items += [(t, vc) for t in v["lines"]]
    items += [(t, "elder_m") for t in PROC.CFG.get("fillers", {}).get("judge", [])]
    items += [(t, "elder_m") for t in PROC.CFG["hall"]["sit_ok"]]
    for t in PROC.CFG["hall"]["unclear"]:
        items += [(t.format(role_name=n), "elder_m") for n in names] if "{role_name}" in t else [(t, "elder_m")]
    for kind in ("seated", "address", "interrupt"):
        for step in PROC.CFG["reprimand"][kind]:
            for t in step:
                items += [(t.format(role_name=n), "elder_m") for n in names] if "{role_name}" in t else [(t, "elder_m")]
    H = PROC.CFG["hall"]
    items += [(H["clerk_minutes"], "female"), (H["interrupt_opp"], "female_alt")] + [(t, "elder_m") for t in H["too_long"]]
    items += [(H["interrupt_judge"].format(opp=n), "elder_m") for n in names]
    for qs in PROC.CFG["questions"].values():
        items += [(q["answer"], "female_alt") for q in qs]
    for o in PROC.CFG["opponent"].values():
        items += [(t, "female_alt") for t in o.values() if isinstance(t, str)]
    for moments in REPLIES["bank"].values():
        for vs in moments.values():
            items += [(v["text"], "female_alt") for v in vs]
    for o in OPP.values():
        items += [(t, "female_alt") for k, t in o.items() if k != "name"]
    for rid in OPP:
        for lz in ROLES.get(rid, {}).get("lahzalar", {}).values():
            if lz.get("namuna"):
                items.append((lz["namuna"], "female_alt"))
    items += MOOT.LINES                                  # «Bahs» sudyasi va kotibi
    for t_, who in TAC.lines():                          # taktika gaplari (raqib — female_alt, sudya — elder_m)
        if who == "judge":
            items += [(t_.format(role_name=n), "elder_m") for n in names] if "{role_name}" in t_ else [(t_, "elder_m")]
        else:
            items.append((t_, "female_alt"))
    try:
        items += [(ln["text"], ln.get("voice") or "male") for ln in json.load(open(FRONT_LINES, encoding="utf-8"))["lines"]]
    except (OSError, ValueError, KeyError):
        pass
    seen, out = set(), []
    for t, v in items:
        if t and (t, v) not in seen and v in V.VOICES:
            seen.add((t, v))
            out.append((t, v))
    return out


def coverage():
    lines = canonical_lines()
    ready = sum(1 for t, v in lines if V.cached(t, v, gpu_only=True))
    return {"canonical": len(lines), "ready": ready}


MMS_SERVED = set()        # talabaga MMS ovozida berilgan (klon keshda yo'q) gaplar


def _cb_reachable():
    try:
        with urllib.request.urlopen(V.CB_GPU + "/config", timeout=5) as r:
            return r.status == 200
    except Exception:  # noqa: BLE001
        return False


def auto_prerender(delay=20, every=600):
    """Fonda, har 10 daqiqada: klonlangan ovozda yo'q doimiy gaplarni va MMS'da berilgan gaplarni render qiladi.
    GPU kompyuter o'chiq bo'lsa — kutadi, qaytgach o'zi davom etadi (talaba kutmaydi)."""
    time.sleep(delay)
    while True:
        try:
            _auto_once()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
        time.sleep(every)


def _auto_once():
    job = PRERENDER.get(AUTO["jobId"]) if AUTO["jobId"] else None
    if job and not job["finished"]:
        return
    lines = canonical_lines()
    missing = [{"text": t, "voice": v} for t, v in lines if not V.cached(t, v, gpu_only=True)]
    missing += [{"text": t, "voice": v} for t, v in list(MMS_SERVED) if not V.cached(t, v, gpu_only=True)]
    AUTO.update(canonical=len(lines), missingAtStart=len(missing))
    if not missing or V.gpu_down("chatterbox") or not _cb_reachable():
        return
    MMS_SERVED.clear()
    jid = "pr_auto_" + secrets.token_urlsafe(5)
    PRERENDER[jid] = {"jobId": jid, "done": 0, "total": len(missing), "failed": [], "finished": False}
    AUTO["jobId"] = jid
    print(f"Avto-prerender {jid}: {len(missing)} ta gap", flush=True)
    run_prerender(jid, missing, "chatterbox_gpu")


def gpu_state():
    """GPU kompyuter qismlari: monitor tekshiruvi (10 s) + oxirgi xato (30 s). None — hali tekshirilmagan."""
    out = {}
    for name, port in (("chatterbox", 8092), ("stt", 8093), ("rerank", 8091)):
        st = next((v for k, v in M.SERVICES.items() if f"({port})" in k), None)
        out[name] = None if st is None else bool(st["up"]) and not V.gpu_down(name)
    return out


def _alert(msg):
    """Loyiha egasiga xabar: Telegram (LEXSIM_ALERT_TG_TOKEN + LEXSIM_ALERT_TG_CHAT). Sozlanmagan bo'lsa — faqat log."""
    print("OGOHLANTIRISH:", msg, flush=True)
    tok, chat = os.environ.get("LEXSIM_ALERT_TG_TOKEN"), os.environ.get("LEXSIM_ALERT_TG_CHAT")
    if not (tok and chat):
        return
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": "LexSim: " + msg}).encode()
        urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/sendMessage", data=data, timeout=10).read()
    except Exception as e:  # noqa: BLE001
        print("Xabar yuborilmadi:", type(e).__name__, flush=True)


def gpu_alert_loop(every=30, after=120):
    """GPU qismlari 2 daqiqadan ko'p o'chiq bo'lsa — bir marta xabar; qaytganda — yana xabar."""
    since, alerted = None, False
    while True:
        time.sleep(every)
        try:
            st = gpu_state()
            down = [k for k, v in st.items() if v is False]
            if down:
                since = since or time.time()
                if not alerted and time.time() - since >= after:
                    alerted = True
                    _alert(f"GPU kompyuter javob bermayapti ({', '.join(down)}) — {int(time.time() - since)} s. "
                           "STT sekin (CPU), yangi gaplar MMS ovozida.")
            else:
                if alerted:
                    _alert(f"GPU kompyuter qaytdi ({int(time.time() - since)} s o'chiq edi).")
                since, alerted = None, False
        except Exception:  # noqa: BLE001
            traceback.print_exc()


def voice_health():
    """/health uchun: qaysi dvigatel, GPU qismlari (oxirgi 30 s da xato bo'lmagan), keshdagi audio soni."""
    try:
        cache = sum(1 for _ in V.CACHE.glob("*.mp3"))
    except OSError:
        cache = None
    served = TTS_SERVE["hit"] + TTS_SERVE["miss"]
    job = PRERENDER.get(AUTO["jobId"]) if AUTO["jobId"] else None
    return {"tts": SETTINGS["tts"], "stt": SETTINGS["stt"], "cacheFiles": cache,
            "gpu": gpu_state(),
            "coverage": coverage(), "servedFromCache": round(TTS_SERVE["hit"] / served, 3) if served else None,
            "stt": V.stt_health(),
            "servedTotal": served,
            "autoPrerender": {k: job[k] for k in ("jobId", "done", "total", "finished")} if job else None}


def prom_metrics():
    st = M.stats(dict(SETTINGS))
    out = ["# HELP lexsim_component_ms So'rov qismlari vaqti (ms), oxirgi 400 so'rov",
           "# TYPE lexsim_component_ms gauge"]
    for comp, v in st["components"].items():
        for q in ("p50", "p95", "avg", "max"):
            if v[q] is not None:
                out.append(f'lexsim_component_ms{{component="{comp}",stat="{q}"}} {v[q]}')
        out.append(f'lexsim_component_calls{{component="{comp}"}} {v["calls"]}')
    for k, v in st["counters"].items():
        out.append(f'lexsim_events_total{{event="{k}"}} {v}')
    out.append(f'lexsim_tts_served_total{{cache="hit"}} {TTS_SERVE["hit"]}')
    out.append(f'lexsim_tts_served_total{{cache="miss"}} {TTS_SERVE["miss"]}')
    c = st["counters"]
    bank, gen, llm = c.get("reply_bank", 0), c.get("reply_generic", 0), c.get("reply_llm", 0)
    tot = bank + gen + llm
    out += [f'lexsim_reply_total{{source="{k}"}} {v}' for k, v in (("bank", bank), ("generic", gen), ("llm", llm))]
    out += [f"lexsim_reply_fallback_ratio {round((gen + llm) / tot, 4) if tot else 0}",
            f"lexsim_reply_llm_ratio {round(llm / tot, 4) if tot else 0}"]
    out += [f"lexsim_queue_depth {len(PENDING)}", f"lexsim_inflight {len(st['inflight'])}",
            f"lexsim_llm_enabled {int(bool(SETTINGS['llm']))}",
            f"lexsim_tts_cache_hits_total {V.STATS['tts_cache_hit']}", f"lexsim_tts_cache_miss_total {V.STATS['tts_cache_miss']}"]
    for name, sv in st["services"].items():
        out.append(f'lexsim_service_up{{service="{name}"}} {int(sv["up"])}')
    if st["system"].get("cpu") is not None:
        out.append(f"lexsim_host_cpu_percent {st['system']['cpu']}")
    return "\n".join(out) + "\n"


PROC.init(sys.modules[__name__])


def run_async_turn(sid, text, tid):
    M.begin("turns")
    st = 200
    try:
        with lock_for(sid):
            s = load(sid)
            M.note(stage=s["stage"])
            eng = Engine(s)
            eng.forced, eng.voice = s.get("pending_forced") or {}, s.get("pending_voice", False)
            try:
                eng.process(text, tid)
                set_feedback(s, tid)
            except Exception:  # noqa: BLE001
                st = 500
                traceback.print_exc()
                eng.npc("Sud majlisida qisqa texnik tanaffus. Fikringizni qaytadan bayon qiling.")
            s["pending"] = None
            with M.part("db"):
                save(s)
    except Exception:  # noqa: BLE001
        st = 500
        traceback.print_exc()
    finally:
        PENDING.discard(sid)
        M.end(st)


def main():
    global NORMS, _DB
    NORMS = Norms()
    _DB = db()
    ST.init(STATE_DB)
    LAB.init(STATE_DB)
    RB.load(HERE / "rubrics.json")                    # baholash mezonlari (manbalari bilan)
    RV.init(STATE_DB)                                 # uch bosqichli tekshiruv: tizim → AI → mentor
    MOOT.ON_EXPLAIN = RV.route_moot
    NPC.ON_REPLY = lambda ref, p: RV.enqueue("npc_reply", ref, ["tasodifiy audit (3 %)"], p, sample=True) \
        if random.random() < RV.AUDIT_RATE else None
    try:                                                # tizim caselari: mavjud ssenariylar
        LAB.seed_system([("s_ijara", "lease", LAB.system_from_scenario(json.load(open(HERE / "scenarios" / "sud-ijara.json", encoding="utf-8"))))])
    except (OSError, ValueError, KeyError) as e:
        print(f"OGOHLANTIRISH: tizim caselari yuklanmadi: {e}", flush=True)
    threading.Thread(target=ST.backup_loop, args=(STATE_DB, 14, lambda m: print(m, flush=True)), daemon=True).start()
    build_vocab()
    threading.Thread(target=gpu_alert_loop, daemon=True).start()
    if os.environ.get("LEXSIM_AUTO_PRERENDER", "1") == "1":
        threading.Thread(target=auto_prerender, daemon=True).start()

    def targets():
        h = {"Authorization": "Bearer " + LLM_KEY} if LLM_KEY else {}
        return [("RAG qidiruv (8090)", RAG_URL + "/health", {}),
                ("LLM Qwen (8000)", LLM_URL.rsplit("/chat/", 1)[0] + "/models", h),
                ("TTS MMS (7008)", "http://127.0.0.1:7008/", {}), ("TTS Chatterbox (7002)", "http://127.0.0.1:7002/", {}),
                ("TTS Chatterbox GPU (8092)", V.CB_GPU + "/config", {}),
                ("Reranker GPU (8091)", SEM_URL.rsplit("/", 1)[0] + "/health", {"X-Key": SEM_KEY} if SEM_KEY else {}),
                ("STT NavAI (7003)", "http://127.0.0.1:7003/", {}), ("STT Kotib (7009)", "http://127.0.0.1:7009/", {}),
                ("STT GPU (8093)", "http://127.0.0.1:8093/config", {})]
    M.start(targets)
    static = [v for v in T.values() if "{" not in v] + [v for o in OPP.values() for k, v in o.items() if k != "name"]
    static += [lz["namuna"] for r in ("davogar-vakili", "javobgar-vakili") for lz in ROLES[r]["lahzalar"].values()]
    def prewarm():
        V.prewarm(static, "mms", lambda m: print(m, flush=True))
        jobs = [(T[k], "elder_m") for k in T if "{" not in T[k]] + [(T["RISE"], "female"), (T["CLERK_REPORT"], "female")]
        jobs += [(lz["namuna"], v) for r in ("davogar-vakili", "javobgar-vakili") for lz in ROLES[r]["lahzalar"].values()
                 for v in ("female_alt", "male")]
        n = 0
        for text, v in jobs:
            try:
                V.tts_mp3(text, v)
                n += 1
            except Exception as e:  # noqa: BLE001
                print(f"TTS mp3 prewarm xato: {e}", flush=True)
        print(f"TTS mp3 kesh: {n}/{len(jobs)} tayyor", flush=True)
    threading.Thread(target=prewarm, daemon=True).start()
    host = os.environ.get("LEXSIM_BACKEND_HOST", "0.0.0.0")
    port = int(os.environ.get("LEXSIM_BACKEND_PORT", "8100"))
    print(f"LexSim backend v1: http://{host}:{port}/api/v1  ssenariylar={list(SCEN)}  RAG={RAG_URL}  "
          f"LLM={'yoqilgan ' + LLM_URL if LLM_ON else 'o\'chiq'} kalit={'bor' if LLM_KEY else 'yo\'q'}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
