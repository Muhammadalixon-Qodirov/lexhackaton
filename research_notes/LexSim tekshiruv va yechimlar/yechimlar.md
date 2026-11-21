# LexSim open problems: LLM API choice, grading validation without mentors, Uzbek STT

Scope: these notes build on `LexSim baholash metodikasi/ai_baholash.md` and do not repeat it. That file already covers the gold-set size of 30–50, the κ/QWK thresholds, the weekly canary, offset calibration and STT fairness auditing. Research date: 2026-11-21. Prices are list prices read on that date.

## A. A fast, reliable, affordable LLM API for Uzbek legal text (target ≤10 s, JSON output, temperature control)

### Takeaway
Replace AIHUB with a direct paid API. GPT-6 Luna ($0.10/$0.50 per 1M tokens) and Gemini 3.x Flash-class models give the best Uzbek-quality-per-dollar on the only current Uzbek leaderboard (UzLiB). At LexSim's workload either costs about **$20–150/month**. Run the judge on a cheap model, with a stronger Gemini model as a cross-check or escalation. Do not run the LLM judge locally on the RTX 3050: small open models score near chance on Uzbek.

### Cited Findings

**Uzbek quality evidence**

UzLiB leaderboard (Tahrirchi). It is a multiple-choice test of Uzbek spelling, word meaning, meaning in context and fill-in-the-blank, in Latin script only. Models run at temperature 1.0, random choice scores 0.25 and human quiz takers score 0.589. It does not cover Cyrillic Uzbek, code-switching with Russian or chat style. — [UzLiB LEADERBOARD](https://github.com/tahrirchi/uzlib/blob/main/LEADERBOARD.md); [azamat.ai summary, updated 14 Oct 2026](https://azamat.ai/en/articles/llm-benchmarks-uzbek-kyrgyz-azerbaijani-armenian-georgian/)

Overall UzLiB scores:

| Model family | Scores |
|---|---|
| Gemini, large | Gemini 4 Carbon 0.852, Gemini 4 Argon 0.844, Gemini 4 Neon 0.842, Gemini 3 Pro 0.826, Gemini 4 Hydrogen 0.823 |
| Gemini, Flash | Gemini 3.7 Flash 0.809, Gemini 3 Flash 0.795, Gemini 3.5 Flash 0.761 |
| OpenAI | GPT-6 Luna 0.809, GPT-5.6 Luna 0.714, GPT 5.2 0.662 |
| Anthropic | Claude Sonnet 5.5 0.781, Claude Opus 5.5 0.774 |
| DeepSeek | DeepSeek V4.1 Flash 0.748, DeepSeek-V4-Pro 0.646 |
| Old or cheap tiers | Gemini 2.5 Flash Lite 0.572, GPT 5 mini 0.529, GPT 5 nano 0.493 |

Claude Haiku is not on the board. — [UzLiB](https://github.com/tahrirchi/uzlib/blob/main/LEADERBOARD.md)

- **Open or local-size models on UzLiB:**

  | Model | Score |
  |---|---|
  | gpt-oss-120b | 0.549 |
  | Gemma 4 26B A4B | 0.548 |
  | Gemma 3 12B | 0.468 |
  | Gemma 3n | 0.437 |
  | Qwen3.5 9B | 0.431 |
  | Llama 3.3 70B | 0.429 |
  | Mistral Nemo | 0.41 |
  | Qwen3 8B | 0.385 |
  | Llama 3.1 8B | 0.375 |
  | Qwen3 4B | 0.345 |
  | Mistral 7B | 0.325 |

  Two Uzbek fine-tunes did not help: Behbudiy Mistral 7B Uz scored 0.420 and Llama 3.1 8B Uz scored 0.277. The exception is **NeuronAI-o'zbek_tili (4B) at 0.662**, which is above the human score. — [UzLiB](https://github.com/tahrirchi/uzlib/blob/main/LEADERBOARD.md)
- **TUMLU (ACL 2025)** uses school and entrance exams with 5-shot prompting at temperature 0. Its Uzbek scores are Claude 3.5 Sonnet 69.1%, GPT-4o 65.4% and Gemini 1.5 Pro 65.1%. These are 2024 models. — [arXiv 2502.11020](https://arxiv.org/abs/2502.11020), via [azamat.ai](https://azamat.ai/en/articles/llm-benchmarks-uzbek-kyrgyz-azerbaijani-armenian-georgian/)

**Pricing (USD per 1M tokens)**

- **OpenAI, Standard tier:**

  | Model | Input | Cached input | Output |
  |---|---|---|---|
  | gpt-6-luna | $0.10 | $0.01 | $0.50 |
  | gpt-5.6-luna | $0.20 | — | $1.20 |
  | gpt-5-mini | $0.25 | — | $2.00 |
  | gpt-5-nano | $0.05 | — | $0.40 |
  | gpt-6.1-terra | $1.00 | — | $5.00 |

  Batch is 50% off. "Fast mode" (formerly Priority) costs 2× Standard. Regional data-residency endpoints add 10%. — [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- **Gemini API, paid tier:**

  | Model | Input | Output |
  |---|---|---|
  | 3.1 Flash-Lite | $0.25 | $1.50 |
  | 3.5 Flash-Lite | $0.30 | $2.50 |
  | 3 Flash Preview | $0.50 | $3.00 |
  | 3.6 Flash / 3.8 Flash | $0.75 | $3.75 |
  | 4 Hydrogen | $1.50 | $7.50 |
  | 4 Argon / Carbon | $2.00 | $10.00 |

  Scheduled increases: 4 Argon and Carbon prices double on 1 Dec 2026, and 3.6/3.8 Flash prices double on 1 Jan 2027. Batch is about 50% off. Gemini 2.5 Flash will be routed to 3.5 Flash-Lite on 1 Dec 2026. — [Gemini API pricing](https://aistudio.google.com/docs/pricing)
- **Anthropic:**

  | Model | Input | Output |
  |---|---|---|
  | Claude Haiku 5.5 (prompts ≤100k) | $0.10 | $0.50 |
  | Claude Haiku 4.5 | $1 | $5 |
  | Claude Sonnet 5.5 | $2 | $10 |
  | Claude Opus 5.5 | $4 | $20 |

  Batch is 50% off. Claude 4.7 and later models use a tokenizer that produces about 30% more tokens for the same text. — [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- **DeepSeek:**

  | Model | Input, cache miss (off-peak / peak) | Output (off-peak / peak) |
  |---|---|---|
  | deepseek-flash (V4.1 Flash) | $0.15 / $0.30 | $0.60 / $1.20 |
  | deepseek-v4-pro | $0.66 / $1.32 | $1.98 / $3.96 |

  Both models support JSON output. Peak hours are 01–04 and 06–10 UTC on weekdays, which is 06–09 and 11–15 Tashkent time, overlapping class hours. — [DeepSeek pricing](https://api-docs.deepseek.com/quick_start/pricing)

**Availability from Uzbekistan**

- Uzbekistan is listed for the Gemini API and Google AI Studio. — [Gemini available regions](https://aistudio.google.com/docs/available-regions)
- Uzbekistan is listed as supported for the OpenAI API. Use from unsupported locations "may result in your account being blocked". — [OpenAI supported countries](https://developers.openai.com/api/docs/supported-countries)
- Uzbekistan is listed for Anthropic API access. — [Anthropic supported countries](https://anthropic.com/supported-countries)
- Anthropic accepts major credit cards. Enterprise customers can arrange invoices. — [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing)

**Data retention for student data**

- On the Gemini API paid tier, prompts and responses are not used to improve products. On the free tier they are. — [Gemini API pricing](https://aistudio.google.com/docs/pricing)
- Paid-tier prompts are logged "for a limited period of time solely for detecting violations of the Prohibited Use Policy". For guaranteed zero data retention, Google points to Vertex AI. — [Gemini ZDR](https://ai.google.dev/gemini-api/docs/zdr)
- A developer forum thread shows confusion about whether ZDR can be self-enabled on an AI Studio project. — [Google AI forum](https://discuss.ai.google.dev/t/how-to-request-zero-data-retention-zdr-for-a-gemini-developer-api-project/172806)

### Inferences

**Monthly cost estimate**

The workload is 50 students × 10 calls × 30 days = **15,000 calls/month**. At 6k input and 1.5k output tokens per call, that is **90M input + 22.5M output tokens/month**. The figures below use list prices with no caching and no batching. They are my arithmetic from the prices above.

| Model | Monthly cost |
|---|---|
| GPT-6 Luna | 9 + 11.25 = **~$20** |
| Claude Haiku 5.5 | ~$20, or ~$26 if its tokenizer adds 30% (unverified whether Haiku 5.5 uses the new tokenizer). Not on UzLiB, so its Uzbek quality is unknown. |
| DeepSeek Flash | $27 off-peak, $54 peak |
| Gemini 3.1 Flash-Lite | 22.5 + 33.75 = **~$56**. No UzLiB score; the older 2.5 Flash Lite scored 0.57. |
| GPT-5 mini | ~$68 (weak Uzbek, 0.53) |
| Gemini 3 Flash Preview | 45 + 67.5 = **~$113** (UzLiB 0.795) |
| Gemini 3.6/3.8 Flash | ~$152, rising to ~$304 from Jan 2027 |
| Gemini 4 Hydrogen | ~$304 |
| Claude Sonnet 5.5 | ~$405 |
| Gemini 4 Argon | ~$405, rising to ~$810 after 1 Dec 2026 |

Things that change these figures:
- **Reasoning tokens:** "thinking" output is billed as output, so a reasoning model can double or triple the output cost. For a ≤10 s target, set thinking effort to minimal or low.
- **Prompt caching:** if about half of each prompt (rubric, case file, system prompt) is a shared prefix, caching cuts input cost by roughly 40–45%.
- **Repeat sampling:** running the same judge 3 times for self-consistency triples the cost, but GPT-6 Luna stays under about $60/month.

**Recommendation**
- **Primary judge:** GPT-6 Luna. It is the cheapest model with a UzLiB score of about 0.81.
- **Alternative or cross-check:** Gemini 3 Flash or 3.x Flash. These are the most consistently strong on Uzbek per dollar.
- **Escalation:** send split verdicts or appeals to Gemini 4 Hydrogen or Argon, or to Claude Sonnet 5.5. This is about 10% of calls, so it adds roughly $30–80/month.
- **Use the API features:** official SDKs give structured outputs (JSON schema) and an explicit temperature setting. Where a reasoning model ignores temperature, use seed and low reasoning effort instead.
- **Keep two providers behind one adapter,** so an outage or a ban falls back automatically.

**Risks**
- **UzLiB measures linguistic knowledge, not legal reasoning or rubric grading,** and it runs at temperature 1.0. The ranking must be re-checked on the LexSim gold set.
- **Model names and prices change every few months.** Prices are scheduled to rise on 1 Dec 2026 and 1 Jan 2027. Pin model IDs and run the drift canary from `ai_baholash.md`.
- **Payment from Uzbekistan:** local Uzcard and Humo cards will not work. A Visa or Mastercard issued by an Uzbek bank in USD is the usual route, but I found no source confirming acceptance (unverified).
- **Student data and consent:** use paid tiers only, because the Gemini free tier trains on data. Strip names and IDs before sending. Disclose the use of a foreign processor to students.

**Local option (RTX 3050 8 GB)**

Not recommended as the judge:
- Every model that fits in 8 GB at 4-bit (Qwen3 4B/8B, Qwen3.5 9B, Llama 3.1 8B, Mistral 7B, Gemma 3n) scores 0.34–0.44 on UzLiB, which is closer to random (0.25) than to frontier models (0.8+).
- Gemma 3 12B scores 0.47 and would barely fit at Q4.
- Running it would also compete with STT and TTS for the GPU.
- The one exception worth a small pilot is **NeuronAI-o'zbek_tili 4B (0.662)**. It might do auxiliary jobs such as normalising transcripts or classifying Latin vs Cyrillic script, but not grading. Its licence, VRAM needs and speed were not checked (unverified).

### Gaps
- **Latency:** I found no independent latency measurement (time to first token, total time for 1.5k output tokens) for GPT-6 Luna, Gemini 3.x Flash or Haiku 5.5. Measure it on the VPS with the actual prompts. Typical non-reasoning output speeds of 100+ tokens/s would put 1.5k tokens in about 10–15 s, which is unverified. To meet ≤10 s, consider streaming, a shorter JSON output (around 600–800 tokens), or splitting rubric items into parallel calls.
- **Not researched:** Groq, Mistral and Qwen API pricing and terms. On UzLiB, the open models Groq typically hosts (Llama, Qwen, gpt-oss) score 0.38–0.55, and Mistral Nemo scores 0.41. That makes them weak choices for Uzbek whatever their speed.
- **OpenAI and Anthropic retention:** their API data-retention and ZDR terms were not fetched in this pass.
- **No Uzbek legal-domain benchmark exists.**

## B. Validating AI grading without many mentors

### Takeaway
Use statistics that make a small mentor-labelled set go further, chiefly prediction-powered inference (PPI). Add synthetic transcripts with planted errors to test whether the grader catches known faults. Literature shows judges miss more than half of planted errors, so this test is essential, but planted errors have to be checked for faithfulness.

### Cited Findings
- **Prediction-powered inference (PPI)** combines a small human "gold" set, which measures the judge's systematic error, with a large set of LLM-judged items to produce a bias-corrected estimate with a valid confidence interval. — [arXiv 2606.05308](https://arxiv.org/html/2606.05308); [Prediction-Powered Ranking, arXiv 2402.17826](https://arxiv.org/html/2402.17826v2)
- **Bayesian PPI** reduced confidence-interval width to 85% of the classical interval, which the authors equate to needing about 60% fewer human labels. — [arXiv 2405.06034](https://arxiv.org/pdf/2405.06034)
- **Small samples:** standard PPI intervals are asymptotic. For very small human sets, Predict-Then-Debias (Kluger et al., 2025) gives bootstrap intervals (seen in a search snippet only). A weaker judge widens the interval but does not make it invalid. — [search summary of arXiv 2601.05420 / 2605.31278](https://www.arxiv.org/pdf/2601.05420)
- **Binary rubric items as a measurement-error problem:** estimate the judge's sensitivity and specificity on a calibration set, then correct prevalence with the Rogan–Gladen, PPI or EIF estimators (snippet). — [arXiv 2601.20913](https://arxiv.org/pdf/2601.20913v1)
- **Planted errors (FBI benchmark):** 2,400 perturbed answers across 22 perturbation categories, built from 500 prompts. Even the best evaluator LLMs failed to detect the planted error in more than 50% of cases on average. — [arXiv 2406.13439](https://arxiv.org/html/2406.13439v2)
- **AUDIT (NeurIPS 2026)** warns that injected errors are not always faithful, so a planted "error" may not actually make the answer worse. It measures this directly. — [NeurIPS 2026](https://neurips.cc/virtual/2026/161258)
- **Judge Reliability Harness** is an open-source tool that generates synthetic perturbed validation suites for any LLM judge. — [arXiv 2603.05399](https://arxiv.org/html/2603.05399v1)
- **JudgeBench** pairs objectively correct responses with subtly wrong ones to test judges. — [arXiv 2410.12784](https://arxiv.org/pdf/2410.12784)

### Inferences (bootstrap protocol)

**1. Calibration set size.** Keep 30–50 double-marked items per task type, as in `ai_baholash.md`.
- Statistically, with n≈30 the 95% interval on κ is roughly ±0.2–0.25 (a standard approximation; my estimate). That is enough to separate "unusable" (<0.4) from "good" (>0.7), but not 0.6 from 0.7.
- So start with **n=30, double-marked by 2 mentors** (about 60 mentor-gradings in total). Treat the result as "provisional" until n≈60–80.

**2. Active sampling.** After the first 30, send mentors only the items where:
- the judges disagree;
- self-consistency samples are split;
- scores sit near a band boundary; or
- a quote check failed.

Use a small random sample (about 20%) to keep the PPI estimate unbiased, because PPI requires random sampling for its human labels.

**3. Multiple LLMs as a cross-check.** Run GPT-6 Luna and Gemini Flash in parallel on, say, 20% of traffic.
- Agreement between the two is not validity, since they can share biases.
- Use it only as a router: disagreement sends the item to a mentor, and agreement is not proof.

**4. Synthetic "known-quality" transcripts.** Build about 40–60 variants of 5–10 seed transcripts with one planted fault each, for example:
- a missed procedural deadline;
- a wrong code article (IPK / FPK);
- no objection to inadmissible evidence;
- a contradiction in the student's own argument;
- ASR-style noise only, as a control that should *not* change the score.

Report the detection rate per fault type. Have one mentor confirm each planted fault really lowers quality (the AUDIT caveat). This costs about 2–4 mentor-hours.

**5. Peer assessment and published moot scoresheets.**
- Students can grade anonymised transcripts with the same rubric.
- Moot scoresheets (Jessup, Vis and others) can serve as rubric anchors and score-band exemplars.
- Neither has been validated here; see Gaps.

**6. Dashboard.** Show these on top of the `ai_baholash.md` metrics:
- the PPI-corrected mean score per task, with its confidence interval;
- sensitivity and specificity per binary rubric item;
- the planted-error detection rate per fault type;
- the ASR-noise control shift, which should be about 0;
- the cross-model disagreement rate;
- the mentor queue size;
- week-over-week change in all of the above.

### Gaps
- No peer-assessment validity studies or published moot-scoresheet anchoring studies were retrieved in this pass. Peer-assessment reliability literature exists (for example Falchikov & Goldfinch 2000), but it was not verified here.
- No study was found that validates LLM legal grading in Uzbek.

## C. Uzbek STT accuracy and fairness

### Takeaway
The best-documented open Uzbek models are NavAI whisper-medium (macro WER 9.7%) and Clarion uzasr-large/base (8.1% / 9.4% on spontaneous speech). All of these numbers are self-reported. Generic Whisper turbo fine-tunes perform badly on spontaneous speech (38.6% WER). A medium-size model in int8 fits easily alongside TTS on 8 GB. The 30–45 s stalls are more likely a decoding or queue problem than a model-size problem.

### Cited Findings

**Reported accuracy**

- **NavAI whisper-medium-uzbek:** 769M parameters, Apache-2.0, trained on 753 h of human-transcribed audio. — [HF navai-uz](https://huggingface.co/navai-uz/whisper-medium-uzbek)

  | Test set | WER |
  |---|---|
  | FLEURS | 14.11% |
  | Common Voice 22 | 7.69% |
  | USC | 9.70% |
  | FeruzaSpeech | 7.41% |
  | Macro (mean of four) | 9.73% |

  Smaller models in the same family score as follows on macro WER:

  | Model | Macro WER |
  |---|---|
  | small (244M) | 11.57% |
  | base | 15.13% |
  | tiny | 18.13% |

  The card gives no VRAM or latency figures.
- **Kotib/uzbek_stt_v1:** a Whisper-medium fine-tune trained on about 1,600 h, Apache-2.0. — [HF Kotib](https://huggingface.co/Kotib/uzbek_stt_v1)
  - Overall 16.7% WER and 7.0% CER on 1,864 samples from 8 test sets.
  - Clean speech about 6–11%, noisy speech 12–24%, dialects 16–25%.
- **Clarion benchmark (vendor-run):** 311 clips (about 2 h) of spontaneous YouTube speech, updated 28 Oct 2026. — [Clarion benchmark](https://www.clarion.uz/en/benchmark)

  | Model | Parameters | WER |
  |---|---|---|
  | uzasr-large | 600M | 8.1% |
  | uzasr-base | 220M | 9.4% |
  | GigaAM-large, not fine-tuned | — | 14.4% |
  | whisper-large-v3-turbo-uzbek | 809M | 38.6% |

  Caveats:
  - The reference transcripts were re-checked only where Clarion's own model disagreed, which gave that model a +2.6-point advantage.
  - An earlier version (v0.2) was withdrawn for test-set overlap.
  - The weights' licence is not stated.
  - The annotations are open on Hugging Face as `rustam1221/uzbek-asr-benchmark-spontaneous`.
- **Commercial APIs:** no Uzbek WER was found for Google Chirp 3, Gemini Transcribe or ElevenLabs. Their good English and European-language WERs (about 3–7%) do not transfer to Uzbek. — [Coval 2026](https://www.coval.ai/blog/best-speech-to-text-providers-in-2026-independent-benchmarks-and-how-to-choose/); [Codesota](https://www.codesota.com/speech/stt-leaderboard)

**Speed and memory**
- A vendor blog reports Whisper Medium on an RTX 3050 at a real-time factor of about 0.16 in FP16 and about 0.11 in INT8, and about 1.5 GB of FP16 memory. The pages contradict each other on whether the 3050 has 6 or 8 GB, so these figures are low-confidence. — [GigaGPU](https://gigagpu.com/whisper-medium-rtf-by-gpu/)
- faster-whisper (CTranslate2) supports 8-bit quantisation on GPU with lower memory use than FP16. — [SYSTRAN faster-whisper](https://github.com/SYSTRAN/faster-whisper)

### Inferences

**Recommendation**
- **Benchmark the models on your own audio.** Build an Uzbek test set of about 1 h of real LexSim student audio (courtroom-style speech, Russian–Uzbek code-switching, regional accents) and transcribe it by hand. Use it to compare:
  - the current model;
  - NavAI whisper-medium, converted to CTranslate2 int8;
  - Clarion uzasr-base and uzasr-large (check the licence first);
  - Kotib v1.

  Report WER for legal terms separately, since misrecognised article numbers and terms matter most for grading.
- **Fix the stalls first.** The likely causes are Whisper long-form hallucination or repetition loops on silence, or the STT request queuing behind TTS on the same GPU. This is an inference, not measured. Mitigations:
  - VAD segmentation (Silero) with ≤30 s chunks;
  - `condition_on_previous_text=False`;
  - the compression-ratio and log-prob fallbacks, with capped `max_new_tokens`;
  - a hard 8 s timeout that retries on a smaller model (NavAI small, ~11.6% macro WER) or on CPU.
- **Avoid GPU contention with TTS:**
  - run each model as one persistent process with the model kept loaded, never reloaded per request;
  - put both behind a single GPU job queue in which STT has priority over TTS, because a student is waiting for STT;
  - cap TTS chunk length so a TTS job cannot hold the GPU for more than about 1–2 s;
  - measure VRAM with `nvidia-smi`. A medium model in int8 at about 1–2 GB plus a typical TTS model should fit in 8 GB, but this is unverified.
  - If contention persists, move TTS to CPU or pre-generate common judge phrases.
- **Fairness:** keep the transcript-vs-corrected-transcript grading comparison from `ai_baholash.md`. Add a WER breakdown by dialect and gender on the in-house test set, since Kotib shows dialect WER about 2× clean-speech WER.

**Cost:** the local models are free under Apache-2.0. The main cost is about 1 h of audio transcribed by hand (a student assistant, 6–10 hours of work).

**Risks:**
- all WERs are self-reported, on different test sets;
- the Clarion licence is unknown;
- Whisper fine-tunes can hallucinate text on silence.

### Gaps
- No independent Uzbek WER exists for Google Chirp 3, Gemini, Yandex SpeechKit, ElevenLabs, MMS or ISSAI's USC models in 2026.
- No measured VRAM or latency figures exist for these specific Uzbek checkpoints on an RTX 3050.
- The architecture of Clarion uzasr (whether it is CTC-based, and therefore less prone to hallucination loops) was not verified.
