# AI + rules scoring for LexSim: reliability, explainability, fairness of LLM grading

Scope note: builds on `LexSim manbalar asosi/hujjat_tuzish.md` §5 (which only named LexRubric and GradeLegal in one line each). Research done 2026-11-21 with ~17 web calls; several papers were read only at abstract level — marked where so. "UNVERIFIED" = not confirmed from a primary text in this session.

## 1. Evidence on LLM-as-a-judge agreement with human graders, and known biases

### Takeaway
With a detailed rubric plus a model answer, frontier reasoning LLMs reach human-level agreement on some legal exams (QWK 0.91 in German public law, matching human inter-rater 0.91) but only moderate agreement on harder/longer tasks (QWK 0.60 criminal law), and without a rubric agreement collapses (QWK 0.31). Across general essay scoring, LLM–human agreement is typically "moderate" (0.30–0.80), judges differ hugely in severity, change behaviour across model versions, are swayed by writing style, and cave to user rebuttals. So the LLM must be anchored, constrained and audited, never trusted raw.

### Cited Findings
**Legal-domain agreement**
- GradeLegal (Al Zubaer, Wendlinger, Nonn, Granitzer, Mitrović, arXiv 2605.21076, May 2026): 27 LLMs grading German law exams on the 0–18 scale (pass = 4). Datasets: 71 criminal-law take-home answers (~6,600 words each) and 16 public-law mock-state-exam answers (~2,700 tokens). Human inter-rater QWK for public law = 0.911 ± 0.066. — [arXiv 2605.21076 (HTML)](https://arxiv.org/html/2605.21076)
  - QWK by prompt context (best model; criminal | public): task-agnostic 0.311 | 0.576; +rubric 0.557 | 0.846; +sample solution 0.465 | 0.793; **+rubric+solution 0.599 | 0.911 (GPT-5)**. Gemini-2.5-Pro runner-up 0.565 | 0.884. Random baseline −0.053 | 0.068. — same source
  - Rubric helped more than a sample solution; both together were best. — same source
  - Reasoning models were best; best non-reasoning (GPT-4.1) 0.478 criminal. Small/legal-specialised open models (Saul-7B, EuroLLM) failed format or had near-zero agreement. — same source
  - Ensembles (min or median of 3 open models) improved up to +0.15 QWK over the best member (Open-S min: 0.488 vs 0.336 criminal), but not in every condition. — same source
  - Error distribution, criminal law, GPT-5 full context: only 12.2% exact match; 27.7% of answers over-graded by ≥2 points, 30.0% under-graded by ≥2. Public law GPT-5: 29% exact, 33% +1. (Reading as an over-grading tendency in criminal law is my interpretation, not stated by authors.) — same source
  - Authors' recommendation: use LLM grading for formative feedback and self-assessment; validate per domain and exam format before any summative use. Total inference cost ≈ $280. — same source
  - Prior work cited there: Strecker et al., Gemini 2.5 Pro QWK 0.764 (public law, rubric+solution); Wendlinger et al., best ≈ 0.058 in criminal law. — same source
- LexRubric (Chen, Li, Hu et al., arXiv 2606.09389, EMNLP 2026 Main): 649 Chinese legal tasks (consultation + judicial exam), 14 scenarios, **12,337 expert-written atomic criteria** across six dimensions: Legal Accuracy, Reasoning & Logic, Completeness, Clarity & Structure, Task Compliance, Ethics & Safety. — [arXiv 2606.09389 (HTML)](https://arxiv.org/html/2606.09389)
  - Each item is binary (met/not met) with weight −10…+10 (negative = penalty items). Score = sum of met item weights ÷ max positive total. The judge checks each item independently, returns explanation + Boolean, **never a holistic score**. Judge Qwen3.6-27B, temperature 0. — same source
  - Human validation: 50 instances × 6 models × 3 legal experts. Item-level agreement 79.36%, **Cohen's κ 0.589** (moderate). Model-ranking agreement much higher: Kendall τ-b 0.800, Spearman 0.886, pairwise accuracy 90%. — same source
  - Swapping judges (GLM-5.1, Kimi K2.6, GPT-5) preserved rankings (τ-b 0.974–0.987). The top-3 models were statistically indistinguishable under paired bootstrap, so authors warn to treat small score differences as non-significant. — same source
- "Grading Machines: Can AI Exam-Grading Replace Law Professors?" (Cope, Frankenreiter, Hirst, Posner, Schwarcz, Thorley; SSRN Dec 2025; J. Law & Empirical Analysis 2026): GPT-5 graded final exams in civil procedure, contracts, torts and corporations from top-30 US law schools. Correlations with professors were "consistently high", sometimes approaching a professor re-grading their own exams; strongest with detailed rubrics. Authors recommend AI as a **check on human grading** (flag sharp divergences for a second look), not a replacement. Exact correlations not retrieved. — [UChicago Law](https://www.law.uchicago.edu/node/114769); [SSRN 5851362](https://papers.ssrn.com/abstract=5851362); [ABA Journal](https://www.abajournal.com/web/article/ai-can-be-used-for-grading-law-school-exams-but-should-it-be)

**General essay scoring**
- ASAP human–human QWK ranges 0.61–0.85 across the 8 prompts. The best 2012 vendor system averaged 0.78, close to the human average. (Search-snippet summary.) — [NSF PAR](https://par.nsf.gov/servlets/purl/10524948)
- Zero-shot GPT-4 on ASAP was near-random on some prompts (Set 1 QWK 0.042, Set 7 0.081). Few-shot helped but stayed below SOTA. Snippet only. — [arXiv 2401.06431](https://arxiv.org/pdf/2401.06431)
- A 2025 synthesis reports LLM–human essay agreement mostly 0.30–0.80 (moderate to good). Snippet only. — [Springer 2026](https://link.springer.com/article/10.1007/s44163-026-01002-y)
- Pre-registered rater-effects audit (Sunkavalli, arXiv 2608.29517, 2026): 12 LLM judges from 4 providers on 2,377 essays (ENEM Portuguese + ASAP). — [arXiv 2608.29517](https://arxiv.org/abs/2608.29517)
  - Judge–human correlations sat in a narrow .47–.56 band.
  - Severity spread was 219 points on ENEM's 0–1000 scale; on ASAP the panel spread was 15–33% of the range, versus ~1% between trained humans.
  - All 5 model-version contrasts shifted severity significantly (up to 133 points). One judge was deprecated mid-study.
  - Replication gave self-consistency (φ ≥ .80 at k ≤ 2) but not human-level accuracy: **averaging makes scores stable, not correct.**

**Biases**
- Zheng et al. 2023 (MT-Bench / Chatbot Arena, NeurIPS 2023): GPT-4 judge reaches >80% agreement with human preferences, the same level as human–human. The paper documents position, verbosity and self-enhancement bias. — [arXiv 2306.05685](https://arxiv.org/html/2306.05685v4). The specific 85% (GPT-4 vs expert, no ties) and 81% (human–human) figures come from my memory of the paper and were not re-read: UNVERIFIED.
- A 2026 re-test found some classic biases weakened on current models: position bias "negligible" across tested models, with style bias now dominant. Single study, snippet only. — [arXiv 2604.23178](https://arxiv.org/html/2604.23178)
- Rubric option ordering produces position bias in pointwise rubric scoring. Averaging over balanced permutations of rubric order reveals the bias and improves human correlation. — [arXiv 2602.02219](https://arxiv.org/html/2602.02219)
- Implicit style bias (arXiv 2603.18765, 2026): with content held constant, style perturbations (informal phrasing penalised most) shifted essay grades significantly (p < 0.05, Cohen's d 0.64–4.25). The bias **persisted despite explicit counter-bias instructions** and was weaker in math and code. — [arXiv 2603.18765](https://arxiv.org/html/2603.18765)
- Sycophancy under rebuttal (Kim & Khashabi, Findings EMNLP 2025): judges endorse a user's counter-argument more when it arrives as a follow-up turn than when both are evaluated together. Detailed reasoning persuades even when it is wrong, and casual pushback sways more than formal critique. Abstract only, no numbers. — [arXiv 2509.16533](https://arxiv.org/abs/2509.16533); [ACL Anthology](https://preview.aclanthology.org/new-sigs/2025.findings-emnlp.1222/)
- Intra-rater inconsistency: LLM judges have low intra-rater reliability across runs, "almost arbitrary in the worst case" (Haldar & Hockenmaier, Findings EMNLP 2025). Abstract only. — [arXiv 2510.27106](https://arxiv.org/abs/2510.27106)

### Inferences
- For LexSim, "rubric + model answer + reasoning model" is the minimum viable configuration. Without a rubric, expect roughly QWK 0.3–0.6.
- Long, complex outputs (moot debates, hearing transcripts) resemble GradeLegal's criminal-law case (long, many issues). Expect QWK ≈ 0.5–0.6 at best, so per-criterion decomposition and human review routing are needed.
- ChatGPT and Gemini behind a browser proxy mean an unknown, silently changing model version. The version-instability finding (up to 133-point severity shifts) means LexSim must re-run its gold set periodically and whenever the UI model changes.
- Sycophancy matters directly for appeals: never let the student argue with the same judge conversation. Re-grade in a fresh session with the appeal attached as a structured claim, not as a chat turn.
- Style bias against informal phrasing will hit STT transcripts, which are inherently informal. See §5.

### Gaps
- Exact per-subject correlations in "Grading Machines" were not retrieved (the SSRN PDF was not opened).
- No study found that measures length/verbosity bias specifically in legal-exam grading.
- No numeric data was found on rebuttal-induced grade changes.

## 2. Rubric-anchored grading design (analytic rubrics, evidence quotes, CoT, ordering, few-shot, decomposition)

### Takeaway
The best evidence favours (a) analytic, point-based rubrics, ideally atomic binary items with signed weights (LexRubric), (b) a reference answer, and (c) per-criterion judgments that produce criterion-linked evidence before an aggregate. No head-to-head study of "score-then-justify vs justify-then-score" was found. The defensible default is rationale and evidence first, then the score.

### Cited Findings
- Adding a rubric gave the largest single gain: public law 0.576 → 0.846, criminal 0.311 → 0.557. A sample solution on top raised them to 0.911 / 0.599. GradeLegal did **not** test few-shot or stepwise pipelines (listed as a limitation). — [arXiv 2605.21076](https://arxiv.org/html/2605.21076)
- LexRubric judges each atomic item independently (explanation + Boolean) and aggregates deterministically. Negative-weight items encode errors such as unsafe or overconfident advice. — [arXiv 2606.09389](https://arxiv.org/html/2606.09389)
- AutoSCORE (AAAI): extract rubric-relevant components first, then judge and score, then give traceable justifications linked to evidence. It argues that without explicit per-criterion checking it is unclear whether LLM raters apply consistent standards. Snippet only. — [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/42123/46084)
- Atomic, self-contained rubric items gave low "flakiness" across 5 repeated binary judgments in an agentic-rubric study. Snippet only. — [arXiv 2601.04171](https://arxiv.org/pdf/2601.04171)
- Autorubric offers a unified framework for rubric-based LLM evaluation (not read in detail). — [arXiv 2603.00077](https://arxiv.org/html/2603.00077)
- Detailed rubrics track professors' grades more closely than minimal guidance ("Grading Machines"). — [UChicago Law](https://www.law.uchicago.edu/node/114769)
- Balanced permutation of rubric option order improves human correlation. — [arXiv 2602.02219](https://arxiv.org/html/2602.02219)

### Inferences (proposed LexSim judge prompt design)
1. **Decompose per criterion, batched.** Each call is 20–60 s, so one call per atomic item is too slow (a rubric with 15–25 items would take 5–25 minutes). Batch about 4–8 related binary items per call, grouped by dimension. Use LexRubric's six dimensions as the template, adding "Procedure/Advocacy" for hearings.
2. **Atomic binary items with signed weights** in place of 1–5 holistic scales. For example: "+5 Cites IPK 149 as basis for return", "+3 Requests a specific sum", "−8 Misstates burden of proof", "−10 Advises falsifying evidence". This makes deterministic aggregation, explanation ("you met 11/15 items") and appeals per item possible.
3. **Output schema per item:** `{id, verdict: met|not_met|cannot_judge, evidence_quotes: [verbatim strings ≤ 40 words], rationale ≤ 2 sentences}`. Rationale and evidence come first, verdict last. The LLM never outputs the total.
4. **Include the reference answer and the case file**, and tell the model to judge legal substance, not style or register: "do not reward length, formality or confident tone". Evidence shows such instructions do **not** remove style bias (arXiv 2603.18765), so the deterministic layer must still guard against it (§3).
5. **Few-shot anchors:** 1–2 short mentor-graded excerpts per difficult item (a "met" and a "not met" example). This is untested in the legal studies, so treat it as a hypothesis to A/B test on the gold set.
6. **Shuffle item order between samples** to wash out rubric-order position effects.

### Gaps
- No primary study was found that directly compares CoT vs no-CoT, or score-first vs reasoning-first, for rubric grading.
- No evidence was found on optimal batch size (items per call) versus accuracy.

## 3. Verification layer: evidence checking, caps, overrides, self-consistency, routing

### Takeaway
Self-consistency (k samples) reliably improves stability and, in ensembles, sometimes accuracy (up to +0.15 QWK), but stability is not validity. Verification must therefore combine deterministic checks (quote matching, required-element presence, ethics rules) with disagreement-based human routing.

### Cited Findings
- Min or median aggregation over 3 judges improved QWK by up to 0.15 over the best single member in GradeLegal. — [arXiv 2605.21076](https://arxiv.org/html/2605.21076)
- Replication yields self-consistency (φ ≥ .80 with k ≤ 2) but not accuracy. Budget replications for stability and human-anchored calibration for validity. — [arXiv 2608.29517](https://arxiv.org/abs/2608.29517)
- Forcing deterministic output (no sampling) can hurt agreement with humans. Snippet only. — [arXiv 2601.11783](https://arxiv.org/pdf/2601.11783) / [arXiv 2609.13824](https://arxiv.org/pdf/2609.13824) (the source paper is ambiguous in the search summary)
- Stable repeated scores do not necessarily agree with humans (local-judge study using mean of 3 and SD). — [arXiv 2609.13824](https://arxiv.org/pdf/2609.13824)
- "Grading Machines" proposes divergence flagging: route exams where AI and human differ sharply to a second look. — [UChicago Law](https://www.law.uchicago.edu/node/114769)

### Inferences (proposed deterministic layer)
1. **Quote verification.** Normalise text (lowercase, unify Uzbek Latin/Cyrillic, strip punctuation, unify ʻ/'/` apostrophes in oʻ and gʻ), then check every `evidence_quote` against the transcript or document by fuzzy substring match (for example, token-level Levenshtein ratio ≥ 0.85 to tolerate STT noise).
   - A `met` verdict with no verifiable quote is downgraded to `cannot_judge`, and its positive points are withheld ("cap when evidence is missing").
   - Fabricated quotes are counted, and a hallucination rate above a threshold invalidates the whole sample.
2. **Deterministic items override the LLM.** These are the enumerable requisites from hujjat_tuzish.md §2: court, parties, claim value, duty formula, attachments, signature. Rules compute them, and the LLM is not asked about them at all.
3. **Ethics hard rules.** Regex/keyword triggers plus an LLM flag for misconduct: advising false evidence, threatening a witness, disclosing confidential information, contempt in a hearing. Any confirmed trigger caps the total, for example at "fail" or 40%, and always routes to a mentor. Never let positive items offset it.
4. **Self-consistency under latency limits.** Use k = 3 samples per batch. With no temperature control, a fresh chat each time, and shuffled item order, the samples come out naturally different. If both ChatGPT and Gemini are available, use them as two judges: a cross-model ensemble reduces self-preference and family bias.
   - Per binary item: majority vote.
   - Total: median.
   - Run calls in parallel where the proxy allows. Three parallel calls cost about 60 s of wall time.
5. **Routing rules to a human mentor:**
   - any item with a split vote (2–1) whose |weight| ≥ 5;
   - SD of the total across samples > 10% of max;
   - cross-model disagreement > 1 grade band;
   - quote-verification failure;
   - ethics trigger;
   - score near the pass/fail boundary (±5%);
   - every appeal.
6. **Length/style guard.** Log word count and formality features next to the score. Periodically regress score on length within gold-set grade levels, and alert if the coefficient is significant.

### Gaps
- No published numbers were found on how often LLM judges fabricate evidence quotes in grading. The fuzzy-match threshold of 0.85 is a design guess.

## 4. Calibration, validation, drift monitoring, confidence reporting

### Takeaway
Validate on a mentor-graded gold set using the metrics the literature uses: QWK for ordinal totals, Cohen's κ for binary items, and exact/adjacent agreement. Treat human–human agreement as the ceiling, and re-audit whenever the model version may have changed. Report severity (mean offset), not only correlation.

### Cited Findings
- Benchmarks:
  - Human inter-rater QWK 0.911 in public law. — [arXiv 2605.21076](https://arxiv.org/html/2605.21076)
  - ASAP human–human QWK 0.61–0.85. — [NSF PAR](https://par.nsf.gov/servlets/purl/10524948)
  - LexRubric item κ 0.589 with 3 experts on 50 instances. — [arXiv 2606.09389](https://arxiv.org/html/2606.09389)
- GradeLegal itself calls its 16-answer public-law estimate "preliminary" because QWK is sensitive to score distribution. — [arXiv 2605.21076](https://arxiv.org/html/2605.21076)
- Evaluate judges with rater-effects methods (severity, halo, reliability, version drift), not agreement alone, and re-audit at version changes. Use identity canaries to detect silent model swaps. — [arXiv 2608.29517](https://arxiv.org/abs/2608.29517)
- Correct systematic offsets of LLM essay scores with small human-labelled sets rather than trusting raw scores (snippet). — [arXiv 2604.00259](https://arxiv.org/html/2604.00259)
- A statistical framework exists for assessing autograders ("Skewed Score", not read). — [arXiv 2507.03772](https://arxiv.org/pdf/2507.03772)
- Rankings are more stable than absolute scores under repeated judging. — [arXiv 2610.19159](https://arxiv.org/pdf/2610.19159) (snippet)

### Inferences (proposed validation protocol)
1. **Gold set.** About 30–50 artefacts per task type (hearing, moot, document), spread across quality levels on purpose, each double-graded by 2 mentors per item. Compute mentor–mentor κ/QWK first, since that is the ceiling. If mentors disagree, fix the rubric wording before blaming the AI. 16 items proved too few in GradeLegal, so aim for ≥ 30.
2. **Acceptance thresholds** (proposed, not from a standard):
   - item κ ≥ 0.6 (LexRubric achieved 0.59);
   - total QWK ≥ 0.7, or within 0.1 of mentor–mentor;
   - |mean offset| ≤ 5% of scale;
   - adjacent-band agreement ≥ 90%.

   Below thresholds, the feature is labelled "practice/formative only", in line with GradeLegal's own recommendation.
3. **Offset calibration.** Fit a per-task linear or isotonic mapping from AI totals to mentor totals on the gold set, and re-fit when drift is detected.
4. **Drift monitoring.** Run a weekly canary: re-grade about 10 fixed gold items and track mean offset, κ, quote-failure rate and latency. Alert if the offset moves more than 5% or κ drops by more than 0.1. Because the proxy hides model versions, this is the only drift detector available.
5. **Confidence to students.** Show per-item verdicts with the quoted evidence, an agreement indicator ("3/3 judges agreed" vs "split, mentor will review"), and a band (score ± spread across samples), not a single precise number. LexRubric's finding that the top-3 models are statistically indistinguishable supports presenting bands.

### Gaps
- No legal-education study was found that reports students' reactions to confidence displays.

## 5. Legal-domain studies, and regulatory guidance (EU AI Act)

### Takeaway
The 2025–2026 legal evidence (GradeLegal, LexRubric, Grading Machines) uniformly says LLM grading is promising with rubrics but should be a supplement or check, or formative-only, pending per-domain validation. Under the EU AI Act, AI that evaluates learning outcomes is high-risk (Annex III 3(b)). Uzbekistan is not bound by it, but it is a useful design benchmark for human oversight and explanation rights.

### Cited Findings
- GradeLegal, LexRubric and Grading Machines: see §1.
- A survey of rubric judges for open-text legal answers (not read in this session). — [arXiv 2610.19992](https://arxiv.org/pdf/2610.19992)
- Annex III point 3(b) lists as high-risk: "AI systems intended to be used to evaluate learning outcomes, including when those outcomes are used to steer the learning process" in education institutions at all levels. — [EU AI Act Service Desk, Annex III](https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3)
- The Commission's Service Desk says grading or feedback systems for assignments that count towards a final evaluation are in scope. A system used only to inform a teacher's instruction, and not to determine grades, is not. — [Service Desk: education](https://ai-act-service-desk.ec.europa.eu/en/education-and-vocational-training)
- Article 86: a person affected by a decision taken on the basis of an Annex III high-risk system (except point 2) that produces legal or similarly significant effects can obtain "clear and meaningful explanations of the role of the AI system in the decision-making procedure and the main elements of the decision taken". — [artificialintelligenceact.eu Art. 86](https://artificialintelligenceact.eu/article/86/)
- Providers need a conformity assessment (Art. 43). A Digital Omnibus agreement reportedly moves the application date for Annex III systems to 2 Dec 2027. This comes from a single secondary source and is UNVERIFIED. — [CASRAI](https://casrai.org/news/ai-act-annex-iii)
- Further duties are known from the Regulation but were not re-read here (UNVERIFIED in this session): human oversight (Art. 14), logging (Art. 12), transparency to deployers (Art. 13), and deployer obligations (Art. 26). — [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

### Inferences
- LexSim practice scores are formative and outside Annex III scope per the Service Desk. Once scores count towards a course grade or certification, LexSim falls into the high-risk pattern. The design should therefore already include:
  - human oversight, with a mentor signing off any summative grade;
  - logs of the prompts, model and version label, raw outputs, and verification results for each score;
  - per-decision explanations (item verdicts + evidence);
  - an appeal path.
- **Appeals protocol:**
  1. The student contests specific items, not the total, attaching a quote or argument.
  2. A fresh-session re-grade covers only those items, with k = 3 and the appeal presented neutrally as "a reviewer claims X; check against the transcript". This avoids the follow-up-turn sycophancy framing.
  3. A deterministic check confirms the appeal's quoted evidence exists.
  4. If the re-grade result is unchanged or split, the item goes to a mentor, whose decision is final and is added to the gold set.
  5. Every appeal outcome is logged, and the appeal-overturn rate per item is a quality KPI: an item overturned often has bad wording.

### Gaps
- No Uzbek regulation on AI in education assessment was searched or found.
- Article 86's applicability to education decisions was not verified against official guidance.

## 6. Fairness for STT transcripts and Uzbek-language input

### Takeaway
ASR errors are unevenly distributed across speaker groups (WER 0.35 vs 0.19 by race in commercial English ASR), and Uzbek ASR WER is roughly 9–25% even for fine-tuned Whisper models. LLM graders also penalise informal style. Grading a spoken performance on a raw transcript therefore risks penalising accent, dialect and recognition noise rather than legal skill.

### Cited Findings
- Koenecke et al., PNAS 117(14):7684–7689 (2020). Five commercial ASR systems (Amazon, Apple, Google, IBM, Microsoft), tested on 19.8 h of matched audio. — [PMC7149386](https://pmc.ncbi.nlm.nih.gov/articles/PMC7149386)
  - Average WER was 0.35 for Black speakers and 0.19 for white speakers; 0.41 for Black men versus 0.30 for Black women.
  - The gap persisted on identical phrases, which points to the acoustic models.
- Uzbek ASR (mostly self-reported model cards, not peer-reviewed):
  - BuzzASR (Whisper-large-v3 fine-tune): WER 25.64% on FLEURS, 11.84% on Common Voice 25. — [Hugging Face](https://huggingface.co/BuzzASR/uzbek)
  - NavAI whisper-medium: macro-WER 9.73% on 4 test sets. — [Friendli](https://friendli.ai/models/navai-uz/whisper-base-uzbek)
  - An older peer-reviewed end-to-end model reached WER 14.3% with 207 h of data. — [PMC9147241](https://pmc.ncbi.nlm.nih.gov/articles/PMC9147241)
  - ElevenLabs makes conflicting vendor claims: Scribe at 15.9% vs 3.1% FLEURS WER, and Whisper-v3 at 96.7%. Treat these as unreliable. — [ElevenLabs](https://elevenlabs.io/speech-to-text/uzbek)
- Style perturbations (informal phrasing) shift LLM essay grades, with effect sizes d up to 4.25, and the bias persists despite counter-bias instructions. — [arXiv 2603.18765](https://arxiv.org/html/2603.18765)

### Inferences
- Tell the judge explicitly that the input is an automatic transcript containing recognition errors, and that it must not penalise grammar, disfluencies, filler words or misrecognised words. The style-bias evidence says the instruction alone is not enough, so the controls below are also needed.
- **Fuzzy quote matching**, tolerant of transcript errors (see §3). Keep audio timestamps for each quoted span so a mentor can listen to the original on appeal.
- **Score substance, not form, in oral tasks.** Map rubric items to content ("raised objection to hearsay", "cited article X"). Exclude fluency items from the LLM. If delivery matters, grade it separately and deterministically (timing, interruptions) or by a mentor.
- **Pre-clean transcripts deterministically:**
  - unify the Latin and Cyrillic scripts;
  - normalise legal terms with a domain dictionary (for example, map variant forms of "даъво/da'vo/davo" and "ИПК/IPK" to one form);
  - optionally use ASR confidence scores to mark low-confidence words with `[?]`.
- **Fairness audit:** in the gold set, include speakers with different regional accents and genders, and compare the AI-minus-mentor offset across groups. Also compare AI scores on the ASR transcript with AI scores on a human-corrected transcript of the same audio. The difference measures the penalty caused by STT errors.
- **Uzbek-language LLM quality is an open risk.** GradeLegal found legal-specialised and small or regional models performed poorly. ChatGPT and Gemini are likely stronger in Uzbek, but no Uzbek legal-grading benchmark exists. Validate on the Uzbek gold set before relying on them, and consider letting the judge reason in English or Russian while quoting the Uzbek original verbatim. That last idea is an untested hypothesis.

### Gaps
- No peer-reviewed Uzbek ASR benchmark for current models, and no study of LLM grading quality in Uzbek, were found.
- No study was found that measures how ASR errors propagate into LLM grading scores. LexSim would have to measure this itself.
