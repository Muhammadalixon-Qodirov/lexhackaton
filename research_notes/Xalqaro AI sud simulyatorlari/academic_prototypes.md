# Academic research prototypes and open-source LLM courtroom simulators (catalog and lessons for LexSim)

Scope: research systems and code repositories that simulate courtrooms or legal proceedings with LLM agents (judge, prosecutor/opposing counsel, defense, witnesses, parties, jurors), including legal-education and moot-court systems. Current to 20 November 2026. On that date every link below was checked with an HTTP request (curl) or through the GitHub, Hugging Face, arXiv and Crossref APIs. Star counts and "last push" dates are as of that day. I did not install or run any of the code.

## 1. Which LLM court-simulation systems exist? (paper, GitHub and demo links; whether code/data are released; whether each link works)

### Takeaway
There are at least 10 academic court-simulation systems with real papers. Four have open code and mature full-procedure designs: SimCourt (Chinese criminal), Civil Court (Chinese civil), AgentCourt and AgentsCourt/SimuCourt (Chinese). Three are oriented toward education: Princeton's AI-Assisted Moot Courts (US Supreme Court), CourtSim-LLM (Chinese mock trials, LoRA) and a 3D virtual trial platform from Shandong. Around them sit jury, bench-deliberation, procedural-strategy and dynamic-environment benchmarks, plus a fast-growing set of small hobby repos. Almost everything is in Chinese or English. I found no system for Uzbek, Russian or any Central Asian or post-Soviet procedure.

### Cited Findings

#### Verification legend
- "OK" means the URL returned HTTP 200, or the API confirmed the repo or dataset exists. "403-bot" means the publisher (ACM DL) blocks automated requests; for those I checked the DOI metadata through Crossref instead. "Not found" means no code link appeared in the paper's HTML or abstract.

#### A. Full-procedure courtroom simulators (academic, open code)
| # | System | Paper / venue | Code | Data / demo | Status |
|---|---|---|---|---|---|
| 1 | **SimCourt** (Chinese criminal trial) | [arXiv 2508.17322](https://arxiv.org/abs/2508.17322); [ACL Anthology 2026.findings-acl.411](https://aclanthology.org/2026.findings-acl.411/) (title there: "Chinese Court Simulation with LLM-Based Agents System") | [Miracle-2001/SimCourt](https://github.com/Miracle-2001/SimCourt): MIT, Python, 5 stars, last push 2026-09-30 | Dataset is in the same repo (`data/`); local Gradio demo (`python main.py`) | All links OK; code and data released |
| 2 | **Civil Court Simulation** (Chinese civil trial; same group as SimCourt) | [arXiv 2606.09632](https://arxiv.org/abs/2606.09632) (June 2026; no venue listed) | [foggpoy/Civil-Court](https://github.com/foggpoy/Civil-Court): MIT, 2 stars | `data/law_library.jsonl` and `data/selected_cases.jsonl` are in the repo ([repo tree](https://github.com/foggpoy/Civil-Court)); CLI only | OK; code and data released |
| 3 | **AgentCourt** (Chinese civil court; adversarially evolving lawyer agents) | [arXiv 2408.08089](https://arxiv.org/abs/2408.08089); [ACL Anthology 2025.findings-acl.304](https://aclanthology.org/2025.findings-acl.304/) | [relic-yuexi/AgentCourt](https://github.com/relic-yuexi/AgentCourt): **no license file**, 98 stars, 21 forks, last push 2026-11-09 | [HF dataset youzi517/AgentCourt](https://huggingface.co/datasets/youzi517/AgentCourt) (zh, not gated); [Bilibili video demo](https://www.bilibili.com/video/BV1aXpUe3E6A) | OK; code and data released, but unlicensed |
| 4 | **AgentsCourt** (first posted as **SimuCourt**; judicial decision-making through simulated court debate) | [arXiv 2403.02959](https://arxiv.org/abs/2403.02959); [EMNLP 2024 Findings](https://aclanthology.org/2024.findings-emnlp.549/). v1 title was "SimuCourt: Building Judicial Decision-Making Agents with Real-world Judgement Documents" ([ar5iv](https://ar5iv.labs.arxiv.org/html/2403.02959)) | [Zhitao-He/AgentsCourt](https://github.com/Zhitao-He/AgentsCourt): **no license**, 19 stars, last push 2024-12-30, 7-line README | `data/` folder and `court_records.json` are in the repo ([tree](https://github.com/Zhitao-He/AgentsCourt)) | OK; code released, documentation minimal |
| 5 | **J1-ENVS / J1-EVAL** ("Ready Jurist One"; interactive Chinese legal environments from consultation up to adjudication) | [arXiv 2507.04037](https://arxiv.org/abs/2507.04037) | Not found: the paper's HTML has no GitHub link. The run scripts `run_J1-ENVS.sh` ship in [LawThinker-agent](https://github.com/yxy-919/LawThinker-agent) | [HF CimoInkPool/J1-Eval_Dataset](https://huggingface.co/datasets/CimoInkPool/J1-Eval_Dataset) (Apache-2.0, zh/en, auto-gated) | Paper and dataset OK; no official environment repo found |
| 6 | **LawThinker** (agent evaluated inside J1-ENVS; verifies every retrieval) | [arXiv 2602.12056](https://arxiv.org/abs/2602.12056) | [yxy-919/LawThinker-agent](https://github.com/yxy-919/LawThinker-agent): MIT, 65 stars | Demo videos embedded in the README | OK |

#### B. Legal-education / moot-court systems
| # | System | Paper / venue | Code / data | Status |
|---|---|---|---|---|
| 7 | **AI-Assisted Moot Courts** (simulates questioning by specific US Supreme Court justices) | [arXiv 2603.04718](https://arxiv.org/abs/2603.04718); CSLAW '26, ACM, pp. 136-172 ([DOI page](https://dl.acm.org/doi/10.1145/3788646.3789536), 403-bot; metadata confirmed in [Crossref](https://api.crossref.org/works/10.1145/3788646.3789536)); [HF paper page](https://huggingface.co/papers/2603.04718) | [princeton-polaris-lab/ai-assisted-moot-courts](https://github.com/princeton-polaris-lab/ai-assisted-moot-courts): **no license**, 1 star; data linked from the README | OK (ACM page blocked for bots) |
| 8 | **CourtSim-LLM** (LoRA-fine-tuned LLM for Chinese mock-court education) | *Artificial Intelligence and Law* (Springer), published 2026-06-04 ([article](https://link.springer.com/article/10.1007/s10506-026-09511-y); [Crossref](https://api.crossref.org/works/10.1007/s10506-026-09511-y)) | Not found: no GitHub or HF link on the Springer page | Article page OK through curl (WebFetch hits an auth redirect); code not found |
| 9 | **Immersive and Multidimensional Virtual Court Trial Training Platform Driven by LLMs** (8 authors, School of Cyber Science and Technology, Shandong University of Political Science and Law) | ICCRD 2026 (18th Int'l Conf. on Computer Research and Development), ACM, 2026-01-23 ([DOI page](https://dl.acm.org/doi/10.1145/3796263.3796307), 403-bot; [Crossref](https://api.crossref.org/works/10.1145/3796263.3796307)) | Not found | Metadata verified; content not verified (see Gaps) |

#### C. Bench, jury and procedural-strategy simulators (adjacent but instructive)
- **SAMVAD**: an Indian judicial-deliberation simulator with a Judge, Prosecution Counsel, Defense Counsel and several Adjudicators, using RAG over the Indian Penal Code and the Constitution. [arXiv 2509.03793](https://arxiv.org/abs/2509.03793). No code link in the paper ([HTML](https://arxiv.org/html/2509.03793)).
- **AgentsBench ("Agents on the Bench")**: LLM agents simulate the collaborative deliberation of a judicial bench (Chinese). [arXiv 2412.18697](https://arxiv.org/abs/2412.18697), marked "Draft version; under review". No code link found.
- **LegalSim**: plaintiff and defendant agents act inside a JSON rules engine, and the simulator searches for procedural exploits. It was accepted at the NLLP workshop at EMNLP 2025 per the [arXiv 2510.03405](https://arxiv.org/abs/2510.03405) comment. No code link found ([HTML](https://arxiv.org/html/2510.03405)).
- **Strategic Courtroom Framework**: prosecution and defense teams of trait-conditioned agents argue over several rounds. [arXiv 2604.07028](https://arxiv.org/abs/2604.07028). I did not check whether code exists.
- **CyberJurors**: a multi-agent jury for e-commerce dispute verdicts, ICML 2026. [arXiv 2605.28369](https://arxiv.org/abs/2605.28369). Code at [YanhuiS/CyberJurors](https://github.com/YanhuiS/CyberJurors) (MIT); data at [HF piggi/VerdictBench](https://huggingface.co/datasets/piggi/VerdictBench) (CC-BY-NC-4.0, gated manually).
- **JuryBench**: bias and persuasion among LLM-simulated jurors in US criminal cases, accepted to EMNLP 2026 ([arXiv 2609.09887](https://arxiv.org/abs/2609.09887)). **12 Angry AI Agents**: a jury-deliberation benchmark built on the film's case ([arXiv 2605.01986](https://arxiv.org/abs/2605.01986)).
- **Investigating Multi-Agent Deliberation in Law**: courtroom-inspired multi-agent frameworks, AIDA2J workshop at ICAIL 2026 ([arXiv 2606.30906](https://arxiv.org/abs/2606.30906)).
- **Synthesizing the Virtual Advocate**: courtroom speech TTS in five Indic languages ([arXiv 2602.11172](https://arxiv.org/abs/2602.11172)). Code at [naturenurtureelite/Synthesizing-the-Virtual-Advocate](https://github.com/naturenurtureelite/Synthesizing-the-Virtual-Advocate) (no license, 0 stars).
- Background from before 2024: **Blind Judgement** trained nine per-justice models to simulate US Supreme Court rulings for 2010-2016 (AAAI-23 workshop) ([arXiv 2301.05327](https://arxiv.org/abs/2301.05327)).

#### D. Open-source (non-academic) courtroom simulator repos worth inspecting
- **moot-court-ai** ([baobaodawang-creater/moot-court-ai](https://github.com/baobaodawang-creater/moot-court-ai)): MIT, 3 stars. It simulates Chinese civil procedure with a clerk, claimant advocate, respondent advocate and judge, running on DeepSeek and Qwen.
- **moot-court-ai-lite** ([baobaodawang-creater/moot-court-ai-lite](https://github.com/baobaodawang-creater/moot-court-ai-lite)): **no license**, 1 star. It runs locally with FastAPI and React, and a finite-state machine (FSM) drives plaintiff, defendant and judge roles.
- **TrialSim** ([piprojectz/TrialSim](https://github.com/piprojectz/TrialSim)): MIT, created 2026-10-31. It is a US-style jury trial that runs fully on local Ollama models. A [live animated replay demo](https://piprojectz.github.io/TrialSim/runs/case_20261031_195613_195739/player.html) loads (OK).
- **courtroom-simulator-ai** ([E-Asrar-Haghighi/courtroom-simulator-ai](https://github.com/E-Asrar-Haghighi/courtroom-simulator-ai)): MIT, 4 stars, built on CrewAI. The user plays the defense. There is a [Loom video demo](https://www.loom.com/share/274944e4a316401db3cc03474addfdb9) (OK).
- **Lex Simulacra** ([prasad-gade05/Law_Courtroom_Simulator](https://github.com/prasad-gade05/Law_Courtroom_Simulator)): no license, built on LangGraph, Indian law through the Kanoon API.
- **JuryRigged** ([PatrickFanella/jury-rigged](https://github.com/PatrickFanella/jury-rigged)): GPL-3.0, TypeScript. It is a "real-time, multi-agent courtroom simulation" with deterministic phases, SSE streaming and jury voting.
- **Mock-Courtroom-** ([TejaswiWoonna/Mock-Courtroom-](https://github.com/TejaswiWoonna/Mock-Courtroom-)): CrewAI, no license. The code is committed as zip files, and a `.env` file is committed in the repo root.

#### E. "Courtroom" as a metaphor only (not legal simulators; low relevance)
- **PROClaim** uses plaintiff, defense and judge roles for claim verification ([arXiv 2603.28488](https://arxiv.org/abs/2603.28488); [code](https://github.com/mnc13/PROClaim)). **AUTOLAW** checks legal compliance through jury-style deliberation ([arXiv 2505.14015](https://arxiv.org/abs/2505.14015)). **Debate-Feedback** predicts legal judgments through debate ([arXiv 2504.05358](https://arxiv.org/abs/2504.05358)). **VulTrial** uses a mock court to detect software vulnerabilities ([arXiv 2505.10961](https://arxiv.org/abs/2505.10961)).

#### Naming pitfalls
- "SimuCourt" (a benchmark of 420 judgment documents inside AgentsCourt, [arXiv 2403.02959](https://arxiv.org/abs/2403.02959)) is a different project from "SimCourt" (the Tsinghua-group full-trial simulator, [arXiv 2508.17322](https://arxiv.org/abs/2508.17322)).
- An aggregator page describes "SimCourt" as court-scheduling optimization ([Emergent Mind](https://www.emergentmind.com/topics/simcourt)). That does not match the paper, so treat the page as unreliable.
- Projects named "Lex Simulacra" ([repo](https://github.com/prasad-gade05/Law_Courtroom_Simulator)) and "LegalSim" ([arXiv 2510.03405](https://arxiv.org/abs/2510.03405)) already exist, and both names are close to "LexSim".

### Inferences
- The most reusable academic code for LexSim is SimCourt (MIT, staged criminal trial) and Civil-Court (MIT, staged civil trial). Both are clean Python and can call any model through configuration. AgentCourt is the most popular repo but has no license, so treat it as reference only.
- The educational papers (CourtSim-LLM and the ICCRD 3D platform) are the closest to what LexSim is building, yet neither has released code. Their value to the team is evaluation design, not reusable software.
- The hobby repos from 2025-2026 are weak as research, but they are the best references for interaction (a human playing a role, objections, streaming, replay). The academic systems are almost all fully autonomous agent-vs-agent pipelines.

### Gaps
- I found no hosted public web demo for any of the academic systems (SimCourt, Civil Court, AgentCourt, AgentsCourt, Moot Courts). The only demos are local Gradio or CLI tools, or recorded videos.
- I could not verify the content of the ICCRD 2026 virtual trial platform paper. ACM returns 403 to automated requests and Crossref has no abstract. The description "LLMs plus 3D modeling, automated evaluation report after each trial" comes only from a search-engine snippet.
- I did not search CNKI or other Chinese-language venues. Chinese education journals may hold more mock-court LLM systems.
- I found no LLM courtroom simulator for Uzbek, Russian, Kazakh or any other Central Asian language or procedure.

## 2. How does each system work? (agent roles, procedure control, retrieval, fine-tuning vs prompting, evaluation, base models, languages)

### Takeaway
The serious systems all hard-code the procedure as fixed stages and let the LLM speak only inside a stage. They ground the agents with statute retrieval: exact lookup by article number, or embedding search over a curated law base. They run prompted general-purpose LLMs (DeepSeek-V3, Kimi, Qwen, GPT-4o-mini) rather than fine-tuned legal models. CourtSim-LLM, which uses role-specific LoRA, is the only exception. Evaluation combines judgment-outcome accuracy against real case records with expert pairwise or rubric judgments of each role's behaviour.

### Cited Findings

#### SimCourt (Chinese criminal trial)
- It follows the official structure of Chinese criminal trials: 5 stages (Trial Preparation, Trial Investigation, Evidence Presentation, Trial Debate, Final Statement) and 5 roles (Judge, Prosecutor, Attorney, Defendant, Stenographer). The output is a full 5-stage trial record plus a judgment document. Its input is the defendant's information, the indictment and the evidence. — [arXiv HTML 2508.17322](https://arxiv.org/html/2508.17322)
- The agents have memory, planning and reflection. Each courtroom agent has two tools: a legal-article retriever and a case retriever. The article retriever works over a law base of 55,347 Chinese laws (including all articles of the PRC Criminal Law) and "directly retriev[es] the content of legal provisions based on their names and numbers". The case retriever uses LegalOne, a commercial LLM search service ([legalone.com.cn](https://legalone.com.cn/)). — [arXiv HTML 2508.17322](https://arxiv.org/html/2508.17322)
- The base model is DeepSeek-V3, for SimCourt and for the three simulation baselines. The vanilla comparisons include GPT-3.5-turbo and DeepSeek-V3. — [arXiv HTML 2508.17322](https://arxiv.org/html/2508.17322)
- The repo has two modes. The simplified `main.py`/`agent.py` is faster and cheaper, for demos. The full `main_full.py`/`agent_full.py` adds strategy, memory and reflection. Stage prompts and role configuration live in `settings/` (`stage_prompt.json`, `example_role_config.json`, `example_role_config_wenxin.json`, `llm_api.json`), and the law base is in `resource/law.json`. LLM backends are pluggable, covering API-based and offline interfaces. — [SimCourt README](https://github.com/Miracle-2001/SimCourt)
- The repo also contains SimCourt's own re-implementations of the AgentCourt and AgentsCourt baselines under `experiments/judgment_prediction/other_methods/`. — [SimCourt repo tree](https://github.com/Miracle-2001/SimCourt)
- Language: Chinese. Role names in the code are 审判长 (presiding judge), 公诉人 (prosecutor), 辩护人 (defense counsel), 被告人 (defendant) and 书记员 (clerk). — [frontEnd.py](https://github.com/Miracle-2001/SimCourt/blob/HEAD/frontEnd.py)

#### Civil Court Simulation (Chinese civil trial)
- It has three roles (judge, plaintiff, defendant) and a separate summary model. The five stages are pre-trial preparation, court investigation, court debate, final statements and judgment. Every simulation is logged as structured JSON. — [Civil-Court README](https://github.com/foggpoy/Civil-Court); [arXiv 2606.09632](https://arxiv.org/abs/2606.09632)
- Memory has two parts. Short-term memory is the dialogue history within the current stage. Long-term memory is a set of structured summaries written after key stages (investigation and debate) that keep disputed issues, evidence, responsibility relations and key numbers. — [arXiv HTML 2606.09632](https://arxiv.org/html/2606.09632)
- Statute retrieval covers more than 17,000 commonly used Chinese provisions, embedded with text-embedding-v4 and searched by FAISS nearest-neighbour lookup. Each role first decides whether it needs legal support, then writes a natural-language query. Retrieval supports the parties' arguments in the debate and the judge at judgment. — [arXiv HTML 2606.09632](https://arxiv.org/html/2606.09632)
- The data come from CaseGen (real Chinese case materials). Models are mixed by role: Kimi-K2.5 as judge, Qwen3.5-27B as plaintiff and defendant, Kimi-K2.5 for summaries. DeepSeek and GLM configurations were also tested. — [arXiv HTML 2606.09632](https://arxiv.org/html/2606.09632)
- Each role and component can be given its own OpenAI-compatible endpoint (JUDGE_/PLAINTIFF_/DEFENDANT_/SUMMARY_/EMBEDDING_BASE_URL). Role profiles are plain text files: `prompt/profile/judge.txt`, `plaintiff.txt`, `defendant.txt`. — [Civil-Court README](https://github.com/foggpoy/Civil-Court)

#### AgentCourt (Chinese civil; AdvEvol)
- The roles are a judge, the plaintiff's lawyer, the defense lawyer and other participants. The workflow has three parts: pre-trial preparation, court proceedings (including a "free debate" phase) and knowledge construction (post-case reflection). — [arXiv HTML 2408.08089](https://arxiv.org/html/2408.08089); [README](https://github.com/relic-yuexi/AgentCourt)
- AdvEvol has the lawyer agents build three knowledge bases through self-play: a legal-provisions memory, an experience base of debate strategies, and a case library. It does so "eliminating the need for extensive manual annotation, fine-tuning, or specialized legal pre-training". 1,000 civil cases were simulated. — [arXiv HTML 2408.08089](https://arxiv.org/html/2408.08089)
- Each agent runs on GPT-4o-mini, and GPT-4o-mini also does the automatic evaluation. The baselines include GPT-4o-mini with RAG (BGE-M3 embeddings) and the legal LLMs HanFei-7B, LawyerLLaMA-13B and ChatLaw-33B. The README says they ran on ERNIE-Speed-128K through `example_role_config.json`, with a local-model option. — [arXiv HTML](https://arxiv.org/html/2408.08089); [README](https://github.com/relic-yuexi/AgentCourt)
- Evaluation uses CourtBench (124 multiple-choice questions generated by GPT-4o-mini from real case backgrounds and validated by senior lawyers). Professional lawyers also rated "cognitive agility, professional knowledge, logical rigor". The paper shows a mock-court sandbox UI where characters move around and talk in real time. — [arXiv HTML 2408.08089](https://arxiv.org/html/2408.08089)

#### AgentsCourt / SimuCourt
- The pipeline runs a court debate simulation (judge, plaintiff and defendant agents), retrieves legal resources and refines the judgment. It follows the sequence "opening remarks, court debate, precedent retrieval, and judgement". The judge first forms a preliminary judgment from the facts and the debate transcript, then refines it with retrieved law. In the second-instance setting the judge re-evaluates the case with new evidence. — [arXiv HTML 2403.02959](https://arxiv.org/html/2403.02959)
- The benchmark has 420 Chinese judgment documents from China Judgments Online covering criminal, civil and administrative cases at first and second instance, plus a large knowledge base, Legal-KB. — [arXiv 2403.02959](https://arxiv.org/abs/2403.02959)
- The repo contains BM25, Pyserini and rerank retrieval scripts (`retrieve_bm25.py`, `retrieve_pyserini.py`, `retrieve_rerank.py`), the role-play agents (`role/role_playing.py`, `main_court.py`) and per-case-type extraction prompts. — [repo tree](https://github.com/Zhitao-He/AgentsCourt)
- GPT-4 is the evaluator for civil and administrative judgments, scoring key-point precision and recall. Human evaluation is added on top. — [arXiv HTML 2403.02959](https://arxiv.org/html/2403.02959)

#### J1-ENVS / J1-EVAL and LawThinker
- J1-ENVS has six scenarios from Chinese legal practice at three levels of complexity, running from inquiry to adjudication. Non-legal roles (public, plaintiff, defendant) get behavioural traits at high, medium or low levels, with descriptions generated by GPT-4o. J1-EVAL scores both task performance and procedural compliance. 17 LLM agents were tested. — [arXiv 2507.04037](https://arxiv.org/abs/2507.04037); [HTML](https://arxiv.org/html/2507.04037)
- LawThinker follows an Explore-Verify-Memorize loop. A DeepVerifier runs after every retrieval and checks knowledge accuracy, fact-law relevance and procedural compliance. It uses 15 legal tools and keeps a memory for long-horizon tasks. — [arXiv 2602.12056](https://arxiv.org/abs/2602.12056); [README](https://github.com/yxy-919/LawThinker-agent)

#### AI-Assisted Moot Courts (Princeton/Stanford; English, US Supreme Court)
- The task is to simulate questioning by a specific justice during oral argument, using Supreme Court transcripts. There are two kinds of simulator. Prompt-based simulators use 3 prompt variants on Llama-3.3-70B-Instruct, Qwen3-32B, Gemini-2.5-Pro, GPT-4o and gpt-oss-120b. Agentic simulators give GPT-4o, gpt-oss-120b and Gemini-2.5-Pro tools: closed search over docket files and the justices' historical voting trends. — [arXiv HTML 2603.04718](https://arxiv.org/html/2603.04718)
- Evaluation has two layers. "Realism" uses adversarial tests for sycophancy plus human pairwise preference. "Pedagogical usefulness" measures legal-issue coverage, diversity of question types, fallacy detection and how competitive the tone is. — [arXiv 2603.04718](https://arxiv.org/abs/2603.04718)

#### CourtSim-LLM (Chinese legal education)
- The authors built the CourtSim-Law Dataset, a multi-turn dialogue corpus of adversarial courtroom debate and "syllogistic legal reasoning". They applied role-specific LoRA fine-tuning to a Chinese open-source legal LLM so that it can play the plaintiff and the defendant, and use in-context learning to simulate full proceedings. Evaluation used 11 indicators and a double-blind review by 15 senior legal experts. — [Springer abstract](https://link.springer.com/article/10.1007/s10506-026-09511-y)

#### Bench, jury and strategy simulators
- **SAMVAD**: a Judge, Prosecution and Defense Counsel, and several Adjudicators who deliberate over iterative rounds until they reach a consensus verdict. RAG over landmark Indian legal documents gives cited arguments. Tested on Qwen-2.5-7B and LLaMA-3-8B. — [arXiv 2509.03793](https://arxiv.org/abs/2509.03793); [HTML](https://arxiv.org/html/2509.03793)
- **AgentsBench**: GPT-4, GPT-3.5-Turbo and Qwen-7B, zero-shot, simulate a judicial bench predicting prison terms. Outputs are scored on performance, legality and further criteria. — [arXiv HTML 2412.18697](https://arxiv.org/html/2412.18697)
- **LegalSim**: agents pick actions from a 13-token action vocabulary (discovery requests, motions, meet-and-confer, sanctions and so on) governed by a JSON "rules-as-code" engine. A stochastic judge with calibrated grant rates decides. The policies compared are PPO, a contextual bandit combined with an LLM, a direct LLM policy (all LLM calls use GPT-4o) and a heuristic. — [arXiv 2510.03405](https://arxiv.org/abs/2510.03405); [HTML](https://arxiv.org/html/2510.03405)
- **Strategic Courtroom**: 9 traits grouped into 4 archetypes; 10 synthetic cases; 84 three-trait team configurations; more than 7,000 trials on DeepSeek-R1 and Gemini 2.5 Pro; an RL "Trait Orchestrator". — [arXiv 2604.07028](https://arxiv.org/abs/2604.07028)
- **CyberJurors**: Individual Verdict Chain-of-Thought (4 stages) combined with Jury Consensus Verdict (multi-round discussion and voting, with a precedent base). By default 17 agent jurors deliberate for up to 3 epochs. — [arXiv 2605.28369](https://arxiv.org/abs/2605.28369); [README](https://github.com/YanhuiS/CyberJurors)

#### Open-source repos: how they control procedure
- **moot-court-ai** uses "deterministic orchestration with Lobster workflows instead of agent-selected flow control ... Language models only produce material inside an assigned stage; they cannot advance the procedure themselves." Each side has its own isolated evidence workspace. — [README](https://github.com/baobaodawang-creater/moot-court-ai)
- **moot-court-ai-lite** has a 14-state one-way FSM: INIT → PLAINTIFF_STATEMENT → DEFENDANT_DEFENSE → EVIDENCE_PLAINTIFF/DEFENDANT (2 configurable rounds) → JUDGE_FOCUS → DEBATE_PLAINTIFF → DEBATE_DEFENDANT → FINAL_STATEMENT_PLAINTIFF → FINAL_STATEMENT_DEFENDANT → JUDGMENT → FINISHED. Each state has its own prompt file under `backend/prompts/stages/`. — [state_machine.py](https://github.com/baobaodawang-creater/moot-court-ai-lite/blob/HEAD/backend/core/state_machine.py)
- The moot-court-ai-lite design doc states the principle "代码控制流程，大模型只管生成台词" (code controls the flow; the LLM only generates the lines). It removed the clerk AI and replaced it with a Python state machine. It explains why OpenClaw, AutoGen and CrewAI were dropped: authentication complexity, sub-workflow sessions hanging because the clerk AI scheduled itself, and tokens wasted on "thinking about who should speak next". It cites AgentCourt and SimCourt as references. — [ARCHITECTURE.md](https://github.com/baobaodawang-creater/moot-court-ai-lite/blob/HEAD/ARCHITECTURE.md)
- **TrialSim** runs a fixed flow: openings → prosecution witnesses → defense witnesses (direct and cross, with objections) → closings and rebuttal → jury instructions → secret first ballot → deliberation → verdict. Agents write a private plan before speaking and a private honesty check afterwards, but see only the public record. After each question, opposing counsel decides privately whether to object, and the judge rules. A citation to an exhibit that is not in the evidence locker is flagged automatically. — [README](https://github.com/piprojectz/TrialSim)
- **courtroom-simulator-ai** is driven by user commands (`defense`, `examine`, `cross`). CrewAI agents play the judge, prosecutor, witnesses and jury, and LlamaIndex indexes documents in `legal_docs/` for the judge and prosecutor. At the end the user is scored 1-10 on persuasiveness, factual grounding and coherence. — [README](https://github.com/E-Asrar-Haghighi/courtroom-simulator-ai)
- **Lex Simulacra** has a LangGraph workflow (`core/state.py`, `core/workflow.py`), and the judge agent decides who speaks next (per the search-result summary). It uses Serper web search and the Indian Kanoon API. — [README](https://github.com/prasad-gade05/Law_Courtroom_Simulator)

### Inferences
- Agreement across independent teams (SimCourt, Civil Court, moot-court-ai, moot-court-ai-lite, JuryRigged, TrialSim) points to the pattern for LexSim: code or an FSM owns the procedure, and the LLM fills each turn. Free LLM turn-taking (a judge or clerk agent choosing the next speaker, as in Lex Simulacra) is the exception and has documented reliability costs.
- Exact lookup by code and article number (SimCourt) is the simplest defence against hallucinated statutes for a civil-law system. Embedding retrieval (Civil Court) handles natural-language questions. A strong design uses both.
- Fine-tuning appears only where a multi-turn courtroom dialogue corpus was built first (CourtSim-LLM). No Uzbek corpus of that kind is known, so prompting plus RAG is the realistic path for a hackathon.

### Gaps
- I did not confirm which base LLM AgentsCourt uses for its agents. The extract showed only GPT-4 as evaluator and LaWGPT as a baseline.
- CourtSim-LLM's base model is described only as "a Chinese open-source legal LLM"; the abstract does not name it. Whether its dataset is released is unknown.
- I did not see the full stage list or the role list for J1-ENVS's court-level scenarios, only the abstract and partial HTML.
- I did not confirm whether SimCourt's Gradio UI lets a human take over a role. The code I saw only shows agents speaking.

## 3. Which have a usable demo or can be run locally with modest effort? (hardware, API keys, license)

### Takeaway
No academic system has a hosted web demo. SimCourt (local Gradio) and Civil-Court (CLI) are the easiest serious systems to run: an API key for any OpenAI-compatible model is enough, with no GPU. TrialSim is the only one that runs fully offline, on consumer-GPU Ollama models, and it has a working browser replay demo. Licensing splits the field: SimCourt, Civil-Court, moot-court-ai, TrialSim, courtroom-simulator-ai, LawThinker and CyberJurors are MIT; AgentCourt, AgentsCourt, moot-court-ai-lite, Lex Simulacra and the Princeton moot-court repo have no license.

### Cited Findings
- **SimCourt**: Python 3.9+, conda and `pip install -r requirements.txt`. You configure an LLM provider in `settings/`, then run `python main.py` for the Gradio demo. `multirun.py` handles batch runs. The full mode is more expensive. MIT. — [README](https://github.com/Miracle-2001/SimCourt). The case retriever in the paper relies on a commercial service, LegalOne. — [arXiv HTML](https://arxiv.org/html/2508.17322)
- **Civil-Court**: Python 3.10+ with an OpenAI-compatible chat API and an embedding API. Run one case with `python run.py 0 0 --judge-model … --plaintiff-model … --defendant-model … --summary-model … --embedding-model …`, or a range of cases. There is no UI. MIT. — [README](https://github.com/foggpoy/Civil-Court)
- **AgentCourt**: `pip install -r requirements.txt`; edit `example_role_config.json` (the authors used ERNIE-Speed-128K, and a local model can be configured); `python main.py` simulates 1,000 cases. Data are on HF. There is a video demo on Bilibili. No license file. — [README](https://github.com/relic-yuexi/AgentCourt); [HF dataset](https://huggingface.co/datasets/youzi517/AgentCourt); [Bilibili](https://www.bilibili.com/video/BV1aXpUe3E6A)
- **AgentsCourt**: the README is 7 lines and has no setup instructions. No license. — [repo](https://github.com/Zhitao-He/AgentsCourt)
- **AI-Assisted Moot Courts**: Hydra and SLURM configs. Llama-3.3-70B needs vLLM on 4 GPUs, Qwen3-32B needs 2 GPUs, and the GPT-4o configuration needs only an API key. No license. — [README](https://github.com/princeton-polaris-lab/ai-assisted-moot-courts)
- **LawThinker**: conda Python 3.10, `bash src/run_J1-ENVS.sh`, J1-EVAL data from HF (auto-gated, Apache-2.0). MIT. — [README](https://github.com/yxy-919/LawThinker-agent); [HF](https://huggingface.co/datasets/CimoInkPool/J1-Eval_Dataset)
- **CyberJurors**: the API is configured in YAML (the README points to the third-party proxy yunwu.ai). Code is MIT. The dataset is CC-BY-NC-4.0 and gated manually. — [README](https://github.com/YanhuiS/CyberJurors); [HF](https://huggingface.co/datasets/piggi/VerdictBench)
- **TrialSim**: needs local Ollama with gemma4:12b, mistral-small3.2:24b and gpt-oss:20b. `trial.py` uses only the Python standard library. Optional local TTS uses Kokoro and Chatterbox. Each run produces a self-contained HTML report and an animated player. MIT. A [hosted replay](https://piprojectz.github.io/TrialSim/runs/case_20261031_195613_195739/player.html) works. — [README](https://github.com/piprojectz/TrialSim)
- **moot-court-ai-lite**: `./start.sh` starts the FastAPI backend (Python 3.12, OpenAI SDK, SQLite, ReportLab PDF export) and the React/Vite frontend on localhost:5173. You need an API key in `backend/.env`. The user presses "next step" to advance the trial, and output streams over SSE. No license. — [README](https://github.com/baobaodawang-creater/moot-court-ai-lite)
- **moot-court-ai**: Node.js 22+, Python 3.10+ and OpenClaw; run `scripts/setup.sh`, `init-case.sh` and `run-trial.sh`; fictional cases only. MIT. — [README](https://github.com/baobaodawang-creater/moot-court-ai)
- **courtroom-simulator-ai**: CrewAI ≥0.11, the OpenAI SDK, LlamaIndex and an OpenAI API key; CLI. MIT. — [README](https://github.com/E-Asrar-Haghighi/courtroom-simulator-ai)
- **Lex Simulacra**: Ollama `gpt-oss:120b-cloud` (needs an Ollama account), plus Serper and Indian Kanoon API keys; Windows `.bat` setup scripts. — [README](https://github.com/prasad-gade05/Law_Courtroom_Simulator)

### Inferences
- For a hackathon spike, the shortest path to a working staged trial is either Civil-Court (point its per-role endpoints at whichever multilingual model handles Uzbek best) or SimCourt's simplified Gradio mode. Swapping in Uzbek requires replacing the Chinese prompts (`settings/stage_prompt.json`, `prompt/profile/*.txt`) and the law base (`resource/law.json`, `data/law_library.jsonl`).
- Without a license, the default is all rights reserved. Code from AgentCourt, AgentsCourt, moot-court-ai-lite, Lex Simulacra and the Princeton repo should be read for ideas, not copied.
- A hosted demo can only show replays (TrialSim's player, the Bilibili and Loom videos). For the hackathon pitch, a recorded replay of a LexSim trial is a cheap, persuasive artefact.

### Gaps
- None of the code was executed, so the actual setup time, dependency breakage and token cost per trial are unverified. AgentCourt reports about 3,361 tokens per round ([arXiv HTML](https://arxiv.org/html/2408.08089)).
- I did not check whether SimCourt runs without LegalOne access, or whether the case retriever can simply be switched off.

## 4. What results and limitations do the authors report? (legal accuracy, realism, hallucinated statutes, procedural errors)

### Takeaway
The simulations do improve judgment prediction and often produce turns that experts rate as better than real participants. The recurring weaknesses are procedural legitimacy: a judge who does not police cross-examination, a prosecutor who asks improper questions, models that know the law but fail at "procedural execution". Others are sycophancy and weak push-back, anchoring in deliberation, memory and summary quality over long trials, and poor transfer across jurisdictions and languages.

### Cited Findings
- **SimCourt results**: simulated trials "better guide the system to predict the imprisonment, probation, and fine". Human experts found the agents' responses "even outperformed judges and lawyers from the real trials in many scenarios". The other simplified court simulators (AgentCourt, AgentsCourt) and PLJP "fail to consistently outperform vanilla methods across the six metrics". The evaluation used 200 LeCaRDv2 cases (40 charges × 5; first instance, one defendant) and 20 public trial videos with full records, rated on 30 expert aspects. — [arXiv HTML 2508.17322](https://arxiv.org/html/2508.17322)
- **SimCourt limitations** (rate at which experts preferred SimCourt over the real professionals):
  - Judge: 55% on "cross-examination legality control" and 65% on "impartial verbal interventions".
  - Prosecutor: only 40% on "lawful questioning". The authors read this as a gap in procedural legitimacy: "restrictions on leading questions, adherence to evidence sequence, and safeguarding of defendant rights".
  - Attorney: 85% on "balanced legal and emotional appeal".

  — [arXiv HTML 2508.17322](https://arxiv.org/html/2508.17322)
- **Civil Court**:
  - Staged simulation raised the total score from 5.11 to 5.19 (Kimi), 4.68 to 5.03 (DeepSeek) and 4.98 to 5.31 (GLM). The gains were concentrated in liability allocation; amount-sensitive reasoning and exact conclusion consistency "remain challenging".
  - Replacing the summary model with Qwen3-32B cut the total by 0.40, and with Qwen3-4B by 0.47. Removing statute retrieval dropped it from 5.47 to 5.09. A Qwen3-4B judge scored 4.54, against 5.39 for Qwen3.5-397B-A17B or GLM-5.

  — [arXiv HTML 2606.09632](https://arxiv.org/html/2606.09632)
- **AgentCourt**:
  - Evolved lawyers gained 12.1% on CourtBench and are "comparable to GPT-4o on dynamic courtroom tasks".
  - Specialized legal models "can accurately recite Articles of Civil Law ... but often fail to leverage them effectively in adversarial court debates". ChatLaw-33B often failed to produce valid responses in dynamic dialogue.
  - Limitations: dependence on an API and its latency (about 3,361 tokens per round), and the need for "further adaptations to generalize effectively across diverse legal systems and jurisdictions".

  — [arXiv HTML 2408.08089](https://arxiv.org/html/2408.08089)
- **AgentsCourt**: legal-article generation improved by 8.6 and 9.1 F1 points at first and second instance. GPT-4 reached only 13.6% and 22.8% in the first- and second-instance settings on the compared measure, and 35.4% accuracy on case-reason prediction, against 43.7% for LaWGPT. Limitations: the data cover only China Judgments Online, testing on other legal systems is "important", and "overall performance of agent systems is still unsatisfactory". — [arXiv HTML 2403.02959](https://arxiv.org/html/2403.02959)
- **J1-ENVS**: models "demonstrate solid legal knowledge, [but] struggle with procedural execution in dynamic settings". GPT-4o scores below 60% overall. Failures "stem not from knowledge deficits, but from limitations in procedural adherence and role interaction". — [arXiv 2507.04037](https://arxiv.org/abs/2507.04037); [HTML](https://arxiv.org/html/2507.04037)
- **LawThinker (hallucinated or inapplicable statutes)**: without step-level verification, "errors such as inapplicable statute citations ... propagate undetected". Verifying after every retrieval gives +24% over direct reasoning and +11% over workflow methods on J1-EVAL. — [arXiv 2602.12056](https://arxiv.org/abs/2602.12056)
- **AI-Assisted Moot Courts**:
  - Simulated questions are often judged realistic and recall the ground-truth legal issues well.
  - Weaknesses: "low diversity in question types and sycophancy". All simulators "struggle to push back against provocative, or adversarial, advocate behavior", and the best catch violations less than 40% of the time. Qualitatively, they are over-cooperative, misidentify sides and lose continuity in long contexts.
  - Gemini models rank best overall; Llama-3.3-70B does "remarkably well". Limitations: the work is specific to the US Supreme Court and relies on proxy metrics and limited human judgments.

  — [arXiv HTML 2603.04718](https://arxiv.org/html/2603.04718)
- **CourtSim-LLM**: about 1.5 times the baseline and nearly 2 times the other models on "text quality", "procedural integrity", "adversarial argumentation ability" and "judgment logic", as rated by 15 experts double-blind. — [Springer abstract](https://link.springer.com/article/10.1007/s10506-026-09511-y)
- **SAMVAD**: with Qwen-2.5-7B, RAG raised the grounding score from 0.21 to 0.42 and verdict consistency from "Medium" to "Very High". — [arXiv HTML 2509.03793](https://arxiv.org/html/2509.03793)
- **12 Angry AI Agents**: 17 of 18 runs ended in a hung jury, so "anchoring is the dominant failure mode". The same "open-minded" instruction changed Llama-4-Scout's behaviour and was ignored by GPT-4o. — [arXiv 2605.01986](https://arxiv.org/abs/2605.01986)
- **JuryBench**: across 20 LLMs and 432K decisions, emotional persuasion can backfire, juror-defendant background fit is a significant bias factor, and juror ideology shapes how severe verdicts are. — [arXiv 2609.09887](https://arxiv.org/abs/2609.09887)
- **LegalSim**: PPO wins most often, the bandit is the most consistently competitive, and "the LLM trails them". It finds procedurally valid but harmful "exploit chains". Its stated limitations are coarse rules, a stationary judge and a tokenized action space. — [arXiv 2510.03405](https://arxiv.org/abs/2510.03405); [HTML](https://arxiv.org/html/2510.03405)
- **Investigating Multi-Agent Deliberation in Law**: courtroom-inspired multi-agent setups reach "comparable overall performance to baseline" LLMs but produce "significantly distinct answers". — [arXiv 2606.30906](https://arxiv.org/abs/2606.30906)
- **Virtual Advocate (TTS)**: the models show "monotone authority", and performance dips in Bengali and Gujarati. — [arXiv 2602.11172](https://arxiv.org/abs/2602.11172)
- **Disclaimers**: SimCourt calls itself a research prototype whose outputs "may be incomplete, inaccurate, or inconsistent" ([README](https://github.com/Miracle-2001/SimCourt)). moot-court-ai is "Demo only" and uses fictional cases only ([README](https://github.com/baobaodawang-creater/moot-court-ai)).

### Inferences
- The weakest points SimCourt reports (judicial control of cross-examination, lawful questioning) are exactly what a law student most needs to practise. LexSim should enforce them with explicit rule checks and objection logic rather than trust the LLM.
- The sycophancy and anchoring results mean an LLM opponent will tend to give in to a confident student. Push-back has to be designed in through persona, explicit counter-argument requirements, or rule-triggered objections, and tested adversarially.
- Accuracy depends a lot on the judge and summary models (Civil Court). The strongest model should go to the judge, the summary and verification steps, and cheaper models to the parties and witnesses.

### Gaps
- Few papers measure hallucinated statutes directly. SimCourt avoids them by design (lookup by article number) but reports no hallucination rate. Only LawThinker targets inapplicable citations explicitly.
- No paper measured learning outcomes for law students (pre/post tests, or classroom use). All evaluations are of the system's outputs.

## 5. Concrete lessons for LexSim (law student picks a role; AI plays the others; Uzbek language; civil-law jurisdiction)

### Takeaway
The best template for LexSim is SimCourt's staged criminal-trial architecture combined with Civil Court's memory and statute-retrieval design, wrapped in a strict code-owned state machine of the kind used by moot-court-ai and moot-court-ai-lite. The Uzbek Criminal Procedure Code has the same skeleton of preparatory part, judicial investigation, judicial debates and last word, so the stage design transfers almost directly. The new work is Uzbek-language prompts, an Uzbek law base keyed by article (from lex.uz), anti-sycophancy design for the AI opponents, and a human-in-the-loop role slot, which most academic systems lack.

### Cited Findings (evidence the lessons rest on)
- The Uzbek CPC (Russian text on lex.uz) contains the procedural units "Подготовительная часть судебного заседания" (preparatory part of the court session), "Судебное следствие" (judicial investigation), which "начинается с оглашения государственным обвинителем…" (begins with the state prosecutor reading out the charge), "Судебные прения" (judicial debates, run under the rules of Article 449) and "последнее слово подсудимого" (the defendant's last word). — [lex.uz CPC (doc 111463)](https://lex.uz/docs/111463)
- A Tashkent City Court trial report says that under the CPC the debates run prosecutor, then victims, then defenders, then the accused, after the judge formally closes the judicial investigation. — [Kun.uz, 5 Feb 2024](https://kun.uz/en/news/2024/02/05/tashkent-criminal-court-wraps-up-investigation-in-doc-1-max-case)
- SimCourt's stages are Trial Preparation, Trial Investigation, Evidence Presentation, Trial Debate and Final Statement. — [arXiv HTML 2508.17322](https://arxiv.org/html/2508.17322)
- "Code controls the flow; the LLM only generates the lines." A free-routing clerk AI caused hung sessions and wasted tokens. — [moot-court-ai-lite ARCHITECTURE.md](https://github.com/baobaodawang-creater/moot-court-ai-lite/blob/HEAD/ARCHITECTURE.md); "[LLMs] cannot advance the procedure themselves" — [moot-court-ai](https://github.com/baobaodawang-creater/moot-court-ai)
- Statute grounding by exact name and number lookup — [SimCourt](https://arxiv.org/html/2508.17322); embedding plus FAISS retrieval over 17k provisions, where removing it costs 0.38 total points — [Civil Court](https://arxiv.org/html/2606.09632); verification after every retrieval — [LawThinker](https://arxiv.org/abs/2602.12056); automatic flagging of citations to exhibits that do not exist — [TrialSim](https://github.com/piprojectz/TrialSim)
- Summary and memory quality strongly affects judgment quality. — [Civil Court](https://arxiv.org/html/2606.09632)
- Isolated workspaces per role — [moot-court-ai](https://github.com/baobaodawang-creater/moot-court-ai); private and public channels — [TrialSim](https://github.com/piprojectz/TrialSim)
- A human can play the defense and get scored at the end — [courtroom-simulator-ai](https://github.com/E-Asrar-Haghighi/courtroom-simulator-ai); a "next step" button advances the trial, output streams over SSE, transcripts export to PDF — [moot-court-ai-lite](https://github.com/baobaodawang-creater/moot-court-ai-lite)
- Evaluation templates: 30 expert aspects with pairwise comparison against real transcripts — [SimCourt](https://arxiv.org/html/2508.17322); realism plus pedagogical usefulness, with adversarial sycophancy tests — [Moot Courts](https://arxiv.org/abs/2603.04718); 11 indicators rated by 15 experts double-blind — [CourtSim-LLM](https://link.springer.com/article/10.1007/s10506-026-09511-y); end-of-trial user scoring on persuasiveness, factual grounding and coherence — [courtroom-simulator-ai](https://github.com/E-Asrar-Haghighi/courtroom-simulator-ai)
- Cross-jurisdiction and cross-language transfer is an open problem, as flagged by [AgentsCourt](https://arxiv.org/html/2403.02959) and [AgentCourt](https://arxiv.org/html/2408.08089). Quality drops in lower-resource languages (TTS) — [Virtual Advocate](https://arxiv.org/abs/2602.11172)
- Specialized legal LLMs did worse than general models in dynamic courtroom dialogue. — [AgentCourt](https://arxiv.org/html/2408.08089)
- Fictional or synthetic cases with a hidden ground truth make outcomes scorable and avoid privacy problems. — [TrialSim](https://github.com/piprojectz/TrialSim); [moot-court-ai](https://github.com/baobaodawang-creater/moot-court-ai)

### Inferences (the lessons)
1. **Encode Uzbek procedure as a finite-state machine, not as LLM free play.** For criminal cases, a sequence like this fits:
   - preparatory part (opening, explaining rights, motions)
   - judicial investigation (charge read, defendant and witness examination, evidence)
   - judicial debates (prosecutor → victim → defense → accused)
   - defendant's last word
   - deliberation and verdict

   Each state defines who may speak, which actions are allowed (question, objection, motion, evidence submission) and when it ends. Use one prompt per state, as moot-court-ai-lite and SimCourt's `stage_prompt.json` do. The exact Uzbek stage list and article numbers must be checked against the current CPC on lex.uz by the team's legal advisor.
2. **Make the student's role a "human slot" in the FSM.** When the state's speaker is the student's role, the engine waits for input; otherwise the AI agent speaks. Let the student choose judge, prosecutor, defense or the civil parties. Academic systems are almost all agent-vs-agent, so the hackathon novelty lies here.
3. **Ground statutes by ID, then verify.** Build a small Uzbek law base keyed by code and article: start with the CPC, the Criminal Code and the articles the case needs. Give agents two tools, an exact article lookup and an embedding search. Require every citation to be one of the retrieved IDs and reject or flag any other, the way TrialSim treats exhibits. Add a cheap verifier pass (LawThinker-style) before the judge's ruling.
4. **Spend model quality where it matters.** Use the strongest Uzbek-capable model for the judge, the stage summaries and the verifier, and cheaper models for witnesses and minor roles, following Civil Court's per-role endpoints. Keep structured stage summaries (disputed issues, evidence, amounts) and do not pass raw transcripts forward.
5. **Design against sycophancy explicitly.** Give opposing agents mandates to push back ("must identify the weakest point of the student's last statement"). Let the AI judge rule on objections from a rules checklist: leading questions, order of evidence, defendant's rights, which are the gaps SimCourt found. Red-team the system with students who try to bully or flatter the AI.
6. **Separate private and public information.** The AI prosecutor must not see the student's private defense notes. Keep a public court record and per-role private memory, as in moot-court-ai and TrialSim.
7. **Use synthetic Uzbek cases with a hidden ground truth.** This gives scoring (was the verdict right, did the student find the key fact) without real case data. It also sidesteps the lack of a public Uzbek judgment corpus comparable to China Judgments Online.
8. **Turn the evaluation rubrics into student feedback.** Adapt SimCourt's 30 aspects and the Moot Courts pedagogical metrics into an end-of-trial report on procedural compliance, citation correctness, responsiveness to opposing arguments and persuasiveness, similar to courtroom-simulator-ai's 1-10 scoring.
9. **Treat Uzbek language quality as a first-class risk.** Every system found is Chinese or English. Test the candidate models on Uzbek legal register in Latin script (and in Cyrillic, if needed for Russian-language source law), and keep legal terminology consistent with a glossary injected into the prompts. TTS for Uzbek, if voice is used, will probably have the same "monotone"/quality-dip problems reported for lower-resource Indic languages.
10. **Reuse permissively licensed code and avoid name collisions.** SimCourt and Civil-Court (MIT) are the best starting skeletons. Unlicensed repos are for reading only. Check the "LexSim" name against the existing "Lex Simulacra" repo and "LegalSim" paper.
11. **Prompting plus RAG, not fine-tuning, for the hackathon.** Fine-tuning paid off only with a purpose-built multi-turn corpus (CourtSim-LLM), and specialized legal LLMs did worse than general models in dynamic dialogue (AgentCourt).

### Gaps
- I did not verify the Uzbek Civil Procedure Code's hearing stages or the current Uzbek-language CPC text. Only the Russian text on lex.uz was matched, using keyword hits rather than a full read.
- I found no Uzbek legal corpus, Uzbek courtroom dialogue dataset or Uzbek legal-LLM benchmark during this search. That belongs to an adjacent research track and is not covered here.
- No study measured whether LLM courtroom simulation improves law students' learning outcomes, so the pedagogical value of LexSim would need its own small user study.
