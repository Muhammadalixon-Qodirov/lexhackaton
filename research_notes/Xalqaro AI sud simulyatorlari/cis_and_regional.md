# Courtroom Simulation and AI Legal-Practice Training in the CIS and Other Non-English, Civil-Law Jurisdictions (for LexSim)

How to read the tags (all checks run 2026-11-20). **[V]**: I fetched the page and confirmed the cited content. **[V-part]**: I fetched the page but could only read part of it, because it was JavaScript-rendered, badly encoded or showed only an excerpt. Only the readable facts are cited. **[S]**: seen only in search-engine snippets or summaries and never fetched, so treat it as unverified. **[X]**: the fetch failed, so treat it as unverified. Searches were run in Russian, Uzbek (Latin), Kazakh, Ukrainian, Chinese, Korean, Turkish, Arabic and English.

## 1. Russian-language projects: court-hearing trainers, AI legal trainers, university LegalTech, and AI assistants from legal-database vendors

### Takeaway
Russia has no mainstream LLM courtroom simulator adopted by universities. The closest match to LexSim is **ChatCourt**, built by one independent developer on GigaChat. It covers first-instance arbitrazh (APK) proceedings, is in beta testing with students, uses a deterministic procedural engine, and has no legal RAG. The rest of the field is:
- scripted VR or desktop simulators sold to institutions (ProgramLab, about 1.69M RUB);
- a multi-agent trainer aimed at practising lawyers (LawMatic Trial);
- one-off "AI judge" mock trials (Tyumen);
- AI courses and AI-evaluation exercises (HSE, Tomsk) rather than role-play simulators.

ConsultantPlus and Garant now sell AI Q&A assistants, but neither has a courtroom simulator or an offer for students.

### Cited Findings
**ChatCourt: an independent, GigaChat-targeted AI trial trainer (the most relevant Russian project)**
- **Author and audience.** Written up on Habr by Alexey Fedorov ("zeroshot"), who calls himself an indie developer. The page shows the date as "16 November" without a year. He says it is intended for Russian universities ("Тренажёр предназначен для российских вузов") and asks for partnerships via Telegram @argmaster. — [Habr](https://habr.com/ru/articles/1108458/) [V]
- **What the student does.** The student plays plaintiff or defendant in a **first-instance arbitrazh (commercial) case**. An **AI judge**, an **AI opponent** and an **AI hint assistant** fill the other seats, and the AI judge issues the decision. Students are not graded on the outcome: instructors assess how the student conducts the process. — [Habr](https://habr.com/ru/articles/1108458/) [V]
- **Scope.** Six stages: preparation, preliminary hearing, trial, evidence and motions, closing arguments, decision. Three training cases are planned. Filing a claim, appeal, cassation and enforcement were deferred. — [Habr](https://habr.com/ru/articles/1108458/) [V]
- **Procedure is enforced in code.** The original idea was a deterministic, non-AI navigator based on the GPK and APK. It was later narrowed to first-instance APK proceedings. Design rule: "Код должен решать, что допустимо, а что делать дальше должна решать модель" ("Code should decide what is permissible; the model should decide what to do next"). — [Habr](https://habr.com/ru/articles/1108458/) [V]
- **Models.**
  - Production target is **GigaChat Ultra**; Claude Sonnet was used during development.
  - GigaChat accepts only one function call per step, while Sonnet made several. This forced a near-complete rewrite and a "guided" mode in which the engine picks the step type and offers the model 1–3 actions.
  - The author says GigaChat was recently withdrawn from commercial use and that developers received 50M free research tokens. This is his claim and was not checked.
  
  — [Habr](https://habr.com/ru/articles/1108458/) [V]
- **Architecture and memory.**
  - A synchronous modular monolith in Python, FastAPI and SQLite. LangGraph was rejected.
  - Before each call, a per-role "desk" is rebuilt from the case log. It has seven sections, including role position, case inventory and past hearing protocols, plus up to 15 role notes. These notes are the only long-term memory.
  
  — [Habr](https://habr.com/ru/articles/1108458/) [V]
- **Engineering lessons.**
  - Prompt caching via an `X-Session-ID` header raised the cache share from about 8% to about 44%. A full run fell from about 1.7M tokens on Sonnet to about 0.55M on GigaChat, with roughly 30% served from cache.
  - At temperature 0 the agents looped, and "Ноль GigaChat не принимает" (GigaChat rejects zero anyway). The tuned temperatures are judge 0.2, AI party and hints 0.3, service checks 0.01.
  - Fixes included 45 rejection codes with correction examples and a journal of rejected proposals. Empty responses fell from 30% to 0%, and a run completed in 62 calls and 7.5 minutes.
  
  — [Habr](https://habr.com/ru/articles/1108458/) [V]
- **Limitations the author admits.**
  - "Базы судебных решений и актуального законодательства в виде RAG за ними нет" (there is no RAG over case law or current legislation).
  - The text of the AI judge's decision is weak: "до настоящего судебного акта ему далеко" (it is far from a real judicial act).
  - Beta testing with students is under way and results are not yet published.
  - There is no demo or repository link, only the author's GitHub profile (github.com/argmaster-dev).
  
  — [Habr](https://habr.com/ru/articles/1108458/) [V]; mirror at [braintools.ru](https://www.braintools.ru/article/38641) [S]

**Other Russian simulators**
- **LawMatic Trial** (lawful.ru) is a Russian-language AI trainer, "Тренируйтесь в ведении судебных процессов с использованием ИИ" (practise conducting court proceedings with AI).
  - Operator: ООО «Лаборатория юридических исследований»; GitHub account "lawlabs".
  - Three modes:
    - **Trainer:** any topic and number of participants, with realistic events such as adjournments, corridor waits and disputes, at any court instance.
    - **Case conduct:** analysis of past hearings with up to 10 participants, audio transcription and deadline tracking.
    - **Debt collection.**
  - Different AI models can be assigned to different participants. Local models and the option to switch AI off for some participants are planned.
  - Free registration; iOS and macOS apps. It targets lawyers at management companies and homeowner associations, not students. No procedural code is named.
  
  — [lawful.ru](https://www.lawful.ru/) [V]
- **ProgramLab VR «Процедурный симулятор судебного заседания по гражданским делам»** (SKU ВЭП-ПССЗГ-01) is a commercial institutional product.
  - **Price:** 1,690,000 RUB excluding VAT.
  - **How it works:** the user plays one party in dialogue mode, choosing answers at each step, and can switch participant within a stage. Stage zero is «Анализ искового заявления» (analysis of the statement of claim).
  - **AI:** "Все виртуальные участники процесса, не управляемые пользователем, контролируются искусственным интеллектом" (all virtual participants the user does not control are run by AI). It acts within scenario logic "с соблюдением норм УПК". The page cites the criminal code (UPK) for a civil simulator, which is an inconsistency on the page.
  - **Platforms:** VR, desktop, WebGL or a touch board, over LAN or the internet, with instructor monitoring.
  - **Modes:** a training mode with hints and a final report, and an exam mode with no hints, a cap on wrong actions and a points score.
  
  — [ProgramLab product page](https://pl-llc.ru/catalog/ekonomika-i-predprinimatelstvo/virtualnye-trenazhery-dlya-spetsialistov-yuridicheskogo-profilya-/virtualnyy-vr-trenazher-protsedurnyy-simulyator-sudebnogo-zasedaniya-po-grazhdanskim-delam/) [V]. The catalogue reportedly also has administrative, arbitrazh and criminal versions at 1.69–2.19M RUB. — [ProgramLab catalogue](https://pl-llc.ru/catalog/ekonomika-i-predprinimatelstvo/virtualnye-trenazhery-dlya-spetsialistov-yuridicheskogo-profilya-/) [S]
- **I Litigator** (vc.ru post of 11.05.2020) is an online court-process simulator for law students and beginning lawyers. Cases are based on real practice and follow Russian procedural law. It has three difficulty levels, certificates, open mock trials on Zoom and paid entry. **No AI.** Its event page was ilitigator.ru/meropriyatiya; current status is unknown. — [vc.ru](https://vc.ru/tribuna/126258-advokaty-tozhe-hotyat-igrat) [V]

**Universities and judicial training**
- **Tyumen State University: "GAS «Нейро-Фемида»" as AI judge (May 2024).**
  - A mock trial ("все это было не по-настоящему", none of it was real) staged in the regional court's hall with real court staff.
  - About 20 students prepared for two months, using ChatGPT on the facts.
  - The case was an IP claim over an AI-generated engine part that Rospatent refused to register. The AI judge delivered an unrehearsed verdict in real time and denied the claim.
  - Lyubov Makarova, head of the regional judges' association: "решение по судьбе человека в зале суда должен принимать только человек" (only a human should decide a person's fate in the courtroom).
  
  — [Rossiyskaya Gazeta](https://rg.ru/2024/05/22/reg-urfo/v-tiumenskom-sude-reshenie-vpervye-vynesla-nejroset.html) [V]
- **Similar AI-themed mock trials** reportedly took place in Tyumen in 2023 and 2025, at Dubna University in April 2026, and at TSU ("first robot trial in the country"). — [Rambler](https://finance.rambler.ru/realty/56466400-tyumenskie-studenty-pravovedy-sorevnovalis-s-neyrosetyu-v-vynesenii-prigovorov/), [Tumen Today](https://tumentoday.ru/2025/03/17/v_tyumeni_proshlo_igrovoye_zasedaniye_po_delu_ob_iskusstvennom_intellekte/), [Dubna](https://dubna.ru/article/2026/04/yuristy-universiteta-dubna-prinyali-uchastie-v-sude-nad-iskusstvennym-intellektom), [Robogeek](https://robogeek.ru/obrazovatelnaya-robototehnika/kaznit-nelzya-pomilovat-v-tgu-vpervye-v-strane-sudili-robota) [S]
- **Tomsk State University Law Institute (article of 17.08.2026).**
  - Students in the «Цифровой юрист» (Digital Lawyer) programmes tested the startup **ExplainLaw**'s legal AI on **120 real legal-clinic cases** that already had teacher-verified answers. Six groups of 5–6 students took part in 2025–26.
  - Scoring rubric, six metrics on a 0–10 scale: accuracy of cited norms, relevance, source reliability, completeness of legal qualification, logic and structure, practical applicability.
  - Manual checks covered hyperlinks, cassation-court jurisdiction and whether clauses were current.
  - Teacher's view: AI is a "помощник, а не замена юриста" (an assistant, not a replacement for a lawyer). No court simulation.
  
  — [TSU news](https://news.tsu.ru/news/studenty-yui-tgu-protestirovali-yuridicheskiy-ii-na-120-realnykh-delakh/) [V]
- **MSAL (Kutafin University)** built a **VR criminalistics trainer** (9 June 2025). It was developed by ЦИРИТ and the Department of Criminalistics under Priority-2030 and covers photography, trace evidence, ballistics and crime-scene inspection. It "автоматически оценивает действия обучающихся" (automatically assesses students' actions) with detailed feedback. There is no court-trial component and AI use is not stated. — [msal.ru](https://msal.ru/news/v-universitete-imeni-o-e-kutafina-mgyua-razrabotan-vr-trenazher-po-kriminalistike/) [V]
- **MSAL** also runs a CPD programme «Право искусственного интеллекта» (from 24 Feb 2025) and live moot courts such as an energy-law moot in November 2023. — [msal.ru AI law](https://msal.ru/news/v-universitete-imeni-o-e-kutafina-mgyua-startuet-programma-povysheniya-kvalifikatsii-pravo-iskusstve/), [msal.ru moot](https://msal.ru/news/v-universitete-imeni-o-e-kutafina-mgyua-proshel-uchebnyy-sudebnyy-protsess-mutkort-v-sfere-energetich/) [S]
- **HSE course "AI for lawyers"** (HSE Nizhny Novgorod law, lawhub.hse.ru).
  - 68 academic hours, 40 of them contact hours; the next cohort runs 02.02.27–04.04.27; 35,000 RUB.
  - Tools named: **GigaChat, DeepSeek, Gamma, «Нейроюрист от Яндекс»**, plus 2 months of free access to "LawGPT".
  - Modules include AI in court systems, RAG for legal tasks and building your own legal AI service.
  - Practicums on preparing court documents and preparing for hearings with AI, and a team "кейс-чемпионат" (case championship). **No mock trial.**
  
  — [HSE](https://lawhub.hse.ru/aiinlaw) [V]
- **Other programmes and moots** (live students, no AI found):
  - An HSE–Netology online master's "LegalTech: автоматизация юридических процессов". — [Netology](https://netology.ru/programs/legaltech?programName=yurist-v-it) [S]
  - SPbU runs live moot courts. — [SPbU](https://law.spbu.ru/education/mootcourts/) [S]
  - MGIMO hosts a "Moscow ECHR model". [S] (search summary only)
- **RGUP (Russian State University of Justice), the training university of the Russian judiciary.** In a RAPSI interview (22 May 2026), rector Olga Tisen discussed digital record-keeping experiments in Moscow courts and "пилотного проекта по созданию проектов судебных решений с использованием нейротехнологий" (a pilot for drafting court decisions with neurotechnology). The headline mentions a "нейропомощник судьи" (neuro-assistant for judges). The excerpt mentions no student simulator. — [RAPSI](https://www.rapsinews.ru/legal_education_mm/20260522/311865279.html) [V-part]. RGUP also runs a "Правовое обеспечение цифрового правосудия" (legal support of digital justice) programme. — [rgup.ru](https://rgup.ru/pages/pravovoe-obespechenie-cifrovogo-pravosudiya) [S]

**AI assistants from legal-database vendors and LLM providers (used for research, not court simulation)**
- **ConsultantPlus «Задать вопрос»** (ai.conslegal.ru).
  - Answers legal and tax questions, "сразу же сделает подборку документов по теме из системы КонсультантПлюс" (immediately compiles a set of relevant documents from the ConsultantPlus system), handles follow-up questions and saves dialogue history.
  - Claims training on a corpus of more than 360M documents. Related tools: «Глубокий поиск» (deep search) and «Проверка договоров» (contract review).
  - Access terms go through service centres. No student or university offer is mentioned.
  
  — [consultant.ru](https://www.consultant.ru/about/nc/ai_inform/) [V]
- **Garant «ИСКРА»** reportedly launched in early 2025 after a beta on ГАРАНТ-AI. Version 2.0 adds an «Развернутый анализ» (detailed analysis) profile. It has four profiles (universal, court practice, document forms, normative-technical documents) and hides personal data from the AI. — [Spark (Garant press)](https://spark.ru/user/179153/blog/398868/garant-predstavil-novuyu-versiyu-pravovogo-ai-assistenta-ndash-iskra-2-0), [Spark](https://spark.ru/user/179153/blog/254102/kompaniya-garant-vipustila-servis-na-osnove-iskusstvennogo-intellekta) [S]. Tver State University's law faculty hosts a PDF guide titled "AI-ассистента Искра", which suggests classroom use. — [law.tversu.ru PDF](https://law.tversu.ru/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6NzMyNTc3LCJwdXIiOiJibG9iX2lkIn19--44e77186ff7defbae92b657dd6d1c7f5cf0f7d2e/AI-%D0%B0%D1%81%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BD%D1%82%D0%B0%20%D0%98%D1%81%D0%BA%D1%80%D0%B0.pdf) [S]
- **Pravo.ru** appears here as a media outlet, not a training-tool vendor.
  - On 26 Feb 2026 it covered China's SimCourt (details in section 3).
  - It quoted Maria Guzanova of PravoTech: "Проекты, аналогичные SimCourt, скорее подходят для образовательных и исследовательских целей" (projects like SimCourt suit educational and research purposes).
  - It also quoted Russian firms (ALRUD, KKMP) that use local or closed LLMs for confidentiality.
  
  — [Pravo.ru](https://pravo.ru/story/262385/) [V]. Habr also ran a SimCourt analysis on 25 Jan 2026. — [pubmag mirror](https://pubmag.ru/ru/short-news/habr-2026-01-25-multi-agent-systems-v-legaltech-kak-simuliatsiia-sudebnogo-protsessa-povyshaet-tochnost-predskazanii-razbor-simcourt/) [S]

### Inferences
- The Russian field falls into four separate groups: (a) scripted VR or desktop procedural simulators sold to institutions; (b) LLM prototypes built by individual developers; (c) novelty mock trials with an "AI judge"; (d) AI research assistants from legal-database vendors. **No product combines LLM role-play, retrieval grounded in statutes and a procedural engine.** That combination is LexSim's niche.
- ChatCourt is the most transferable blueprint. Its main lessons:
  - Hard-code the procedure and let the LLM fill content.
  - Narrow the scope to one procedure type at first instance.
  - Isolate each role's context.
  - Expect looping and tool-calling limits on national models.
  - Cache prompts to cut cost.
- Its two biggest gaps, weak decisions and no RAG, are exactly what grounding in Lex.uz would address.
- In Russia, sovereign models (GigaChat, Yandex) are the default for university deployments. The Uzbek parallel is the "national model" bot on LexAI (section 2).

### Gaps
- ChatCourt's publication year is not shown on the page. The context (GigaChat Ultra, "beta testing now") suggests 2025–2026, but that is unverified. No public demo, repository or beta results exist.
- I found no evidence of an AI courtroom simulator at MSAL, HSE, SPbU, MGIMO or RGUP. RGUP's "нейропомощник судьи" details were not readable in the excerpt.
- I found no Sber, Yandex or Pravo.ru product built specifically for courtroom training. I did not fetch Garant ИСКРА's official pages.
- ProgramLab does not explain what its "AI" is (scripted logic or an LLM), and its civil simulator page refers to the criminal code (UPK).

## 2. Kazakhstan and Uzbekistan (plus Kyrgyzstan, Belarus and Ukraine)

### Takeaway
I found **no AI courtroom role-play simulator** in Uzbekistan, Kazakhstan, Kyrgyzstan or Belarus. Ukraine has one small custom GPT on ChatGPT that simulates legal situations (JurLab).

Uzbekistan nevertheless has strong policy demand:
- Decree **PF-141 (21.08.2025)** orders "virtual sud" (virtual court) sessions and AI classes in judicial retraining from 1 Oct 2025, under a "nazariya — amaliyot — imitatsiya" (theory, practice, simulation) principle, at the new **Odil sudlov akademiyasi** (Justice Academy).
- The August 2025 decree on AI in the courts launched the "Digital Court" concept and an AI virtual consultant on my.sud.uz (planned from 1 Jan 2026).
- Lex.uz's operator runs **LexAI**, which includes a "national model" bot that answers only from lex.uz, with citations.
- **TSUL** has a **USD 14.5M KOICA** project on AI-based legal services for 2026–2030.

In Kazakhstan, the Academy of Justice's 2025–2027 concept says only that AI for "modelling court proceedings" is being studied.

### Cited Findings
**Uzbekistan: judicial training (the strongest demand signal for LexSim)**
- **Decree PF-141** (21.08.2025), on reforming the training of judicial personnel:
  - **Clause 1(d):** build "sunʼiy intellekt imkoniyatlaridan amaliyotda foydalanish koʻnikmalari" (practical skills in using AI).
  - **Clause 6(i):** from 1 Oct 2025, retraining courses introduce "“virtual sud” mashgʻulotlari" (virtual court sessions), meaning real-time observation of hearings and analysis of judges' procedural actions. The same clause adds "sunʼiy intellekt texnologiyalaridan foydalanish boʻyicha oʻquv darslari" (classes on using AI).
  - **Clause 6(j):** training is dual-form, under the "nazariya — amaliyot-imitatsiya" principle.
  - **Clause 13(g)(iv):** the Academy may use the Supreme Court's **"Adolat" information systems complex**.
  - **Annex 4:**
    - item 8: interactive e-courses and online assessment during 2025;
    - item 7: digitising the training process;
    - item 18: access to the "Adolat" information systems by September 2025;
    - item 21: connection to the national "Elektron taʼlim" (e-learning) network.
  - **Responsibility and timing:** Supreme Judicial Council Chair X.B. Yodgorov is responsible for implementation. The magistracy (master's programme) starts in 2026/2027.
  
  — [lex.uz PF-141](https://lex.uz/docs/-7696594) [V]
- **Odil sudlov akademiyasi** website:
  - Training follows "nazariya – amaliyot – imitatsiya" (theory, practice, simulation).
  - In specially equipped courtrooms, "sud jarayonlarining imitatsiyasi o‘tkazilib" (court proceedings are simulated), with trainees playing judge, prosecutor, advocate, plaintiff, defendant and witness.
  - In the "virtual court", trainees follow real proceedings in real time, analyse rulings and draft procedural documents, with access to AI tools.
  - Mentoring follows an "ustoz–shogird" (master–apprentice) model.
  
  — [sudacademy.uz](https://sudacademy.uz/general-information) [V]
- The Academy was created in 2025 on the base of the Supreme School of Judges. — [Gazeta.uz](https://www.gazeta.uz/oz/2025/08/22/academy-of-justice/) [S]

**Uzbekistan: AI in the courts (the environment LexSim's users will practise in)**
- **AI-in-courts decree, as reported on 26.08.2025:**
  - "Digital Court" concept;
  - pilot digital courtrooms in Tashkent by the end of 2025;
  - a platform for analysing normative legal acts for citizens, advocates, lawyers and judges from 1 Dec 2025;
  - **a legal-aid module on my.sud.uz from 1 Jan 2026**, where "sun’iy intellekt asosida ishlaydigan virtual maslahatchi huquqiy murojaatlarga javob berib boradi" (an AI virtual consultant will answer legal inquiries);
  - preliminary court information on the state services portal from 1 Mar 2026;
  - continuous improvement of judges' and court staff's digital literacy.
  
  — [UzA](https://uza.uz/en/posts/sudlar-faoliyatiga-suniy-intellekt-texnologiyalari-joriy-etiladi_753553) [V]
- **Zamon.uz on the same decree (22.08.2025)** adds:
  - before filing, users can obtain an AI estimate of "sud muhokamasining taxminiy natijasi hamda sarflanadigan xarajatlar" (the likely outcome and the costs);
  - court document drafts are generated automatically;
  - AI produces hearing minutes as text in real time;
  - nationwide rollout in 2026–2027.
  
  — [Zamon.uz](https://zamon.uz/uz/2025/08/22/endi-suniy-intellekt-yordamida-sud-muhokamasining-taxminiy-natijasini-bilish-mumkin-boladi-38216) [V]. **Conflict:** the UzA summary mentions AI calculation of court fees but not outcome prediction.

**Uzbekistan: AI over legal databases (Lex.uz)**
- **LexAI (ai.lex.uz)**, verified from the platform's own Uzbek interface strings:
  - **Operator:** "“Adolat” milliy huquqiy axborot markazi" (the "Adolat" National Legal Information Centre, which runs Lex.uz).
  - **Functions:** a 24/7 AI legal chatbot, online expert review of draft legislation, and a document constructor.
  - **Funding:** "davlat byudjeti ishtirokisiz" (no state budget), using private-sector partners' funds.
  - **CHAT-BOT-1** uses an external analytical resource and accepts free-form questions and "kazus" (case problems).
  - **CHAT-BOT-2** is "Milliy model asosida ishlangan bo’lib … faqat lex.uz ma’lumotlari doirasida javob beradi" (built on a national model; answers only within lex.uz data). It "hujjatning tegishli qismiga havola beradi" (links to the relevant part of the document used).
  - **Usage terms:** free query quota and paid tariffs. Answers are "tavsiyaviy" (advisory only).
  - **Partnerships:** "Biz … hamkorlik qilishga tayyormiz" (we are open to partnership on AI legal projects).
  
  — [ai.lex.uz](https://ai.lex.uz/) and its [Uzbek locale file](https://ai.lex.uz/i18n/locales/uz.json) [V; the HTML is a JS shell, so the text was read from the locale file]
- **Other Uzbek AI regulation:**
  - Ethics rules for AI-based solutions (No. 3787, 14.03.2026), requiring compliance with personal-data, informatisation and cybersecurity law. — [lex.uz 8083233](https://lex.uz/docs/8083233) [S]
  - An AI strategy to 2030 (PQ-358, 14.10.2024). — [lex.uz](https://www.lex.uz/docs/-7158604) [S]

**Uzbekistan: universities and hackathons**
- **TSUL, the Ministry of Justice and KOICA** signed a Protocol of Discussions for the project «Создание среды и развитие потенциала для юридических услуг на основе искусственного интеллекта в Узбекистане» (creating an environment and building capacity for AI-based legal services in Uzbekistan).
  - KOICA grant: **USD 14.5M**, phased over **2026–2030**.
  - Components: an AI legal-services platform, a digital legal library, an Uzbek–Korean legal centre, and AI and legal-tech training for TSUL students and faculty.
  - **No courtroom simulation is mentioned.** The page is undated; an image filename suggests 30 Apr 2026.
  
  — [tsul.uz](https://tsul.uz/ru/news/1387/Universitet/%D0%9C%D0%B8%D0%BD%D0%B8%D1%81%D1%82%D0%B5%D1%80%D1%81%D1%82%D0%B2%D0%BE-%D1%8E%D1%81%D1%82%D0%B8%D1%86%D0%B8%D0%B8,-KOICA-%D0%B8-%D0%A2%D0%93%D0%AE%D0%A3-%D0%B1%D1%83%D0%B4%D1%83%D1%82-%D1%86%D0%B8%D1%84%D1%80%D0%BE%D0%B2%D0%B8%D0%B7%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-%D1%8E%D1%80%D0%B8%D0%B4%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D1%83%D1%81%D0%BB%D1%83%D0%B3%D0%B8) [V]
- A TSUL journal article discusses AI in court summons systems. — [review.tsul.uz](https://review.tsul.uz/index.php/yfa/article/view/593) [S]
- **FairTech hackathon: "AI Competition & Consumer Protection Challenge 2026 — Respublika Hakatoni"**
  - Organisers: the Committee for Competition Development and Consumer Rights Protection, with RTAM.
  - **2–4 December 2026, Tashkent, 48 hours**, teams of 1–5, prize fund of 150 mln so‘m.
  - Track **AI-3 "Qonunchilik bo‘yicha yuridik assistent"** asks for "a language-model chatbot in Uzbek, Russian and English: rights, procedures, document templates, links to sources", using the open legislation database and the Committee's FAQ.
  
  — [hackaton.fairtech.uz](https://hackaton.fairtech.uz/) [V; JS site, text read from its own bundle]. I found no courtroom-specific LegalTech hackathon in Uzbekistan.

**Kazakhstan**
- **Academy of Justice Development Concept 2025–2027** (adopted 11 Feb 2025; article of 11 Sep 2025):
  - a new information system is being built to automate training;
  - AI for "білім беру процесіне де, сот процестерін модельдеуге де" (both teaching and modelling court proceedings) and for analysing practice "is being studied" ("пысықталуда");
  - a criminalistics polygon;
  - the magistracy received 605 applications and admitted 98.
  
  — [primeminister.kz](https://primeminister.kz/news/reviews/sot-toreligi-akademiiasynyn-2025-2027-zyldarga-arnalgan-damytu-tuzyrymdamasy-oku-procesine-cifrlyk-sesimder-engizilude-30534) [V]
- A news item titled "Академия правосудия внедряет ИИ при подготовке судей" (the Academy of Justice introduces AI into judges' training). — [ortcom.kz](https://ortcom.kz/ru/novosti/1757575984) [X: TLS certificate error]
- An interview says the Academy has added modules on AI, digital ethics and cybersecurity. — [vastane.kz](https://vastane.kz/gosnews/vysshij-sudebnyj-sovet-rk/146286-intervju-s-dmitriem-malahovym-o-podgotovke-sudej-v-akademii.html) [S]
- **Court AI for judges:**
  - Since 2022 the «Цифровая аналитика судебной практики» (digital court-practice analytics) service has had AI elements. It compares rulings, flags anomalies and "прогнозировать исход гражданского дела" (predicts the outcome of civil cases) across millions of court acts.
  - The IT community can build products through the Smart Bridge platform.
  - Robots draft alimony court orders and process travel restrictions.
  
  — [Pravo.ru, 23 Feb 2023](https://pravo.ru/news/245406/) [V]. A voluntary «Цифровой помощник судьи» (digital judge's assistant) is reportedly being rolled out. — [newshub.kz](https://newshub.kz/en/post/ii-pomoshhnika-dlia-sudei-mogut-nacat-ispolzovat-pri-rassmotrenii-administrativnyx-del-1786939601) [S]
- **KBTU and the Nazarbayev University AI lab** built an outcome-prediction service with the Supreme Court and NPP Atameken (reported 27 Sep 2019). It covers about 1.2M court acts from 2016 onward. Judges see similar cases, and citizens describe their dispute in their own words to "спрогнозировать вероятность успеха" (estimate the chance of success). It was in test mode and open only to judges. — [Informburo](https://informburo.kz/novosti/specialisty-kbtu-i-nazarbaev-universiteta-razrabotali-servis-dlya-prognozirovaniya-ishoda-sudebnyh-del.html) [V]
- **Adilet:** an AI legal consultant launched on adilet.zan.kz, reported on 25 Jun 2025 with few details. — [gov.kz](https://www.gov.kz/memleket/entities/adilet-kzl/press/news/details/1024183?lang=ru) [V-part]. The «Цифровой консультант» (digital consultant) in «Әділет» and «Е-Заң көмегі» reportedly dates from May 2025. — [Kazpravda](https://kazpravda.kz/n/minyust-vnedryaet-pravovye-servisy-s-literoy-e/) [S]. A private RAG assistant called "AdiletAI" also exists. — [adiletai.com](https://www.adiletai.com/) [S]
- **Universities:** Maqsut Narikbayev University finished runner-up at the AIFC Court Moot 2025, a live moot with no AI. — [mnu.kz](https://mnu.kz/ru/news/mnu-students-become-runners-up-at-the-international-moot-court-competition/) [S]. The AIFC Court held an event on "the future of legal education and AI". — [court.aifc.kz](https://court.aifc.kz/ru/events/budushhee-yuridicheskoj-professii-yuridicheskogo-obrazovaniya-i-iskusstvennyj-intellekt/) [S]

**Kyrgyzstan**
- **«Мыйзамчы»**, an AI assistant on Kyrgyz law built by Zhanybek Asirov (described as a future lawyer).
  - Fully operational since late July 2026; more than 1,500 users and more than 1,000 requests a day, including law students.
  - It combines a database with an AI agent. The model, data source and languages are not stated, and no link is given.
  
  — [exclusive.kz, 2 Nov 2026](https://exclusive.kz/ii-pomoshhnika-v-juridicheskih-voprosah-sozdal-student-iz-kyrgyzstana/) [V]
- **Supreme Court judge Inara Gilyazetdinova**, head of the judicial digitalisation working group (interview of 23 Oct 2026):
  - courts are moving to a single IT architecture;
  - e-justice amendments took effect on 1 Jan 2026;
  - an automated judge-evaluation module is being tested;
  - AI is planned for searching rulings and anonymising documents, plus online consultants for citizens;
  - a specialised information system is being built for the **Higher School of Justice** to support digital training;
  - "Мы не должны допустить, чтобы искусственный интеллект стал скрытым соавтором судебного акта" (we must not let AI become a hidden co-author of a judicial act).
  
  — [24.kg](https://24.kg/article/inara-gilyazetdinova-ii-ne-dolzhen-stanovitsya-soavtorom-sudebnogo-resheniya) [V]
- Kyrgyzstan and Russia planned a judicial cooperation agreement that includes joint educational programmes. — [RG, 1 Oct 2026](https://rg.ru/2026/10/01/v-kyrgyzstane-zainteresovalis-rossijskim-opytom-vnedreniia-ii-v-pravosudii.html) [S]

**Belarus**
- Brest students hold a grant to draft recommendations on AI in judicial activity. — [Zarya](https://zarya.by/news/community/studenty-iz-bresta-nikita-liczuk-i-pavel-marzan-razrabatyvayut-rekomendaczii-po-ispolzovaniyu-iskusstvennogo-intellekta-v-sudebnoj-deyatelnosti/) [S]
- A Ministry of Justice regional article on digitalising legal education says students use court-decision databases and AI assistants for case analysis. — [minobljust.gov.by](https://www.minobljust.gov.by/news/item/20574-tsifrovizatsiya-yuridicheskogo-obrazovaniya-vyzovy-i-perspektivy) [X: timeout; snippet only]
- I found no Belarusian simulator.

**Ukraine**
- **JurLab** (Zaporizhzhia Polytechnic; article of 13 Oct 2025):
  - Built by associate professor Yurii Gavrilov as a **custom GPT on ChatGPT**.
  - It began as a "simulator of legal situations" in which students act as "a prosecutor, lawyer, investigator or human rights defender" and make decisions.
  - It then gained a "legal core" through the **HUDOC (ECtHR) and OHCHR APIs**. No Ukrainian national legal sources are mentioned.
  - "JurLab was not created to replace the teacher, but to strengthen the student's thinking."
  
  — [zp.edu.ua](https://zp.edu.ua/en/all-news/jurlab-iak-shtuchnyj-intelekt-zminiuie-navchannia-iurystiv-en/) [V]; GPT link: [chatgpt.com/g/…jurlab](https://chatgpt.com/g/g-67dfbefde2a08191a7d7d471dd00a725-jurlab-trenazher-iuridichnogo-mislennia) [not fetched; needs a ChatGPT login]
- The National School of Judges ran AI trainings, for example "DIGITAL COACHING 360" in August 2025 and AI-in-courts sessions for Supreme Court judges in April 2026. I found no simulation. — [court.gov.ua](https://court.gov.ua/press/news/1864224) [S; which news item matches which event is uncertain]
- Ukrainian methodological papers recommend online trial simulations, with teachers as mentors. — [DonNU 2023](https://jpchdnu.donnu.edu.ua/article/download/13908/13805), [Odesa Law Academy](https://cuesc.org.ua/images/informlist/%D0%9C%D0%B0%D0%BA%D0%B5%D1%82%20advanced_training_OLA.pdf) [S]

### Inferences
- PF-141 creates a ready-made institutional buyer and use case. The Odil sudlov akademiyasi must run "virtual sud" sessions, AI classes, simulation-based dual training and online assessment. Today that apparently means physical mock courtrooms and observing real hearings, not AI role-play, so an Uzbek-language LLM simulator would fill a mandated slot.
- The Digital Court rollout (e-filing, AI-generated minutes, automatic document drafts, my.sud.uz consultant, 2026–2027) means students will soon practise in a digitised procedure. A simulator that reproduces e-filing and digital hearings would be more realistic than one that copies paper-era trials.
- LexAI's CHAT-BOT-2 pattern (national model, answers only from lex.uz, links to the exact provision) is a practical grounding design for LexSim's judge and prosecutor agents. LexAI's stated openness to partnership makes "Adolat" NLIC a candidate data or API partner.
- Kazakhstan and Kyrgyzstan have stated plans (AI for modelling court proceedings; a digital training system for the Higher School of Justice) but no product. That makes them regional expansion targets for Russian, Kazakh and Kyrgyz versions.

### Gaps
- I found no TSUL virtual courtroom, AI moot court or legal hackathon, despite searches in Uzbek, Russian and English. TSUL's news archive may hold items that are not indexed.
- I could not confirm that the my.sud.uz AI consultant actually launched on 1 Jan 2026; only the August 2025 plans were verified.
- I could not establish what "access to AI tools" in the Academy's "virtual sud" sessions consists of.
- I could not confirm whether LexAI offers an API to third parties, or which "national model" it uses.
- The Kazakh Academy of Justice item on ortcom.kz could not be fetched (certificate error). No Kazakh-language simulator was found.
- The interface languages of Мыйзамчы and the Adilet AI consultant are not stated.

## 3. Chinese, Korean and other civil-law examples (Turkish, Arabic)

### Takeaway
China leads clearly. It has three research-grade multi-agent LLM court simulators: SimCourt (Tsinghua), AgentsCourt with the SimuCourt benchmark (CAS), and AgentCourt (with public code). Chinese law schools also routinely use AI in mock trials and VR-plus-AI simulation software. The Gulf now has commercial AI mock courtrooms: Legaline's Meta Legal Space (UAE, October 2026) and Khabeer (Saudi Arabia). Turkey has a course-built MootGPT and a VR mock-court project. Korea's work is on the judiciary side (an in-house trial-support AI and AI training for judges) rather than student simulators.

### Cited Findings
**China: research simulators**
- **SimCourt**, "Chinese Court Simulation with LLM-Based Agent System" (arXiv 2508.17322; submitted 24 Aug 2025; Kaiyuan Zhang … Qingyao Ai, Yiqun Liu).
  - Built on "the real-world procedure structure of Chinese courts"; it replicates "all 5 core stages of a Chinese trial" with five courtroom roles.
  - Agents have memory, planning and reflection.
  - The simulated trials improved prediction of imprisonment, probation and fines. In expert annotation, agent responses beat real-trial judges and lawyers in many scenarios.
  - The arXiv page links no code repository.
  
  — [arXiv](https://arxiv.org/abs/2508.17322) [V]. Listed as Findings of ACL 2026. — [ACL Anthology preview](https://preview.aclanthology.org/ingest-acl/2026.findings-acl.411/) [S]
- **SimCourt details reported by Pravo.ru (26 Feb 2026):**
  - **Origin and purpose:** developed at Tsinghua as a cheaper alternative to students attending live hearings.
  - **Inputs:** defendant information, the indictment, evidence.
  - **Roles:** secretary, judge, prosecutor, defender, defendant. Each has memory, strategy and legal-database modules.
  - **Legal base:** 55,347 laws, plus LegalOne's 2M documents and 200,000 cases selected by the Supreme People's Court.
  - **Outputs:** a full transcript and a decision, described as "готовый учебный материал" (ready-made teaching material).
  - **Expert review, strengths:** 100% citation accuracy and good process management.
  - **Expert review, weaknesses:** AI judges were not impartial enough, AI lawyers were emotionless, and AI prosecutors asked leading questions that real judges would block. The system was weak on emotionally charged arguments and sudden turns.
  
  — [Pravo.ru](https://pravo.ru/story/262385/) [V]
- **AgentsCourt / SimuCourt** (arXiv 2403.02959; EMNLP 2024 Findings; Zhitao He … Kang Liu, Jun Zhao).
  - SimuCourt benchmark: 420 Chinese judgment documents (criminal, civil and administrative; first and second instance).
  - The framework runs court-debate simulation, legal-resource retrieval and decision refinement over a "Legal-KB" knowledge base.
  - It improved F1 on legal-article generation by 8.6% (first instance) and 9.1% (second instance).
  
  — [arXiv](https://arxiv.org/abs/2403.02959) [V]. A search summary attributes it to the CAS Institute of Automation [S].
- **AgentCourt**, "Simulating Court with Adversarial Evolvable Lawyer Agents" (arXiv 2408.08089; Guhong Chen … Min Yang).
  - Its "AdvEvol" method evolves lawyer agents through adversarial courtroom interaction over **1,000 civil cases**, gaining 12.1% on CourtBench.
  - **Code is public:** [github.com/relic-yuexi/AgentCourt](https://github.com/relic-yuexi/AgentCourt) has about 98 stars and 21 forks at fetch time. It is Python with a role config file, supports an offline local-LLM mode and uses ERNIE-Speed-128K. Its README says the code is still "being organized".
  
  — [arXiv](https://arxiv.org/abs/2408.08089) [V], [GitHub](https://github.com/relic-yuexi/AgentCourt) [V]. A Zhihu answer attributes it to CAS SIAT (Shenzhen). — [Zhihu](https://www.zhihu.com/question/666096174) [S]

**China: classroom use**
- **Huaqiao University (12 May 2025).**
  - A mock trial in the provincial first-class course *Civil Procedure Law*, led by Prof. Chen Weixing, on an "AI文生图著作权纠纷" (AI text-to-image copyright dispute).
  - During preparation, both sides used intelligent assistants for evidence analysis, document drafting and online simulated confrontation.
  - The trial included an "人工智能使用说明" (AI-use explanation) segment in which each side disclosed its AI use to the court.
  - The defence used open-source code to attack a simulated AI agent.
  
  — [hqu.edu.cn](https://jwc.hqu.edu.cn/info/1063/29964.htm) [V]
- **Shandong University (Qingdao), 27 Mar 2025.**
  - Uses the "模拟法庭仿真实训软件" (mock court simulation training software), a module of the "法学虚拟仿真实训平台软件（法源）" ("Fayuan" legal virtual simulation training platform).
  - "依托虚拟现实和人工智能技术" (built on VR and AI).
  - Students walk through the full process from evidence collection to trial, with multi-user online training and intelligent evaluation feedback, in an Evidence Law course.
  
  — [sdu.edu.cn](https://www.qdxq.sdu.edu.cn/info/1820/60481.htm) [V]
- **Beijing Politics and Law Vocational College** (Guangming opinion piece of 15 Oct 2025).
  - Uses DeepSeek and 北大法宝 GPT (Peking University Fabao GPT) to draft complaints.
  - AI plays opposing counsel and judge.
  - "Dynamic courtroom simulation" injects events: a judge's clarification when a step is skipped, jurisdictional objections, "evidence ambushes". A review report follows.
  - Workflow: "AI draft + student revision + teacher review". AI is a "催化剂而非快捷键" (a catalyst, not a shortcut).
  - Risks: wrong or outdated citations and over-dependence.
  - Examples are anonymised and no outcome data is given.
  
  — [Guangming](https://legal.gmw.cn/2025-10/15/content_38345399.htm) [V]
- China's national virtual-simulation lab platform lists a "模拟法庭" (mock court) project. — [ilab-x](https://www.ilab-x.com/details/page?id=6067&isView=true) [V-part: JS page, no details readable]. Zhang Wenxian argues for AI environments to practise courtroom debate, mediation, prosecution and adjudication. — [chinalaw.org.cn](https://www.chinalaw.org.cn/portal/article/index/id/34670/cid/72.html) [S]. A Guangdong University of Finance and Economics paper warns that "virtualised and entertainment-oriented" teaching can weaken legal thinking. — [GDUFE PDF](https://gaojiao.gdufe.edu.cn/cn/article/pdf/preview/92019efb-fa24-496d-8c59-bdce501b789c.pdf) [S]

**Korea**
- **Courts' in-house trial-support AI pilot (13 Feb 2026).**
  - Built on the judiciary's own platform, "챗GPT 같은 외부 AI에 의존하지 않고" (without relying on external AI such as ChatGPT), for security and judicial independence.
  - Integrates precedents, statutes, rules, practice manuals and commentaries, and shows sources so judges can verify answers.
  - Case summaries and issue analysis will be added.
  - "보조 도구일 뿐 판결을 대신하는 시스템이 아니다" (only a support tool, not a system that replaces judgment).
  
  — [Hankyung](https://www.hankyung.com/article/202602134488i) [V]. Reportedly a four-phase project, an AI guidebook for all judges (February 2026) and an 80-judge judicial AI advisory group (October 2026). — [Herald](https://www.heraldk.com/article/2026022321200023964), [Law Times](https://www.lawtimes.co.kr/news/articleViewAmp.html?idxno=228347) [S]
- The Judicial Research and Training Institute added an AI course to judges' mandatory five-yearly training (Chosun Ilbo, 1 Jul 2026). — [Nate/Chosun](https://news.nate.com/view/20260701n34518) [V-part: garbled encoding; only this general point was readable]
- **Intellicon (2020)** planned a "미래의 법률, AI 재판 시뮬레이션" ("the future of law: AI trial simulation") class for students and teachers at the Gyeongnam Future Education Theme Park, then due to open in July 2022. It would use "인공지능을 이용한 가상 모의재판" (virtual mock trials using AI). Current status is unknown. — [AI Times](https://www.aitimes.kr/news/articleView.html?idxno=16805) [V]
- **Law schools:**
  - The first "로스쿨 AI 챌린지" (Law School AI Challenge) drew 907 applicants. Tasks: analysing case records, searching for similar precedents and drafting legal opinions. — [Nate](https://m.news.nate.com/view/20260523n03538) [S]
  - AI teaching at law schools is mostly one-off lectures. — [Daum](https://v.daum.net/v/20260413050214360) [S]
  - **Japan:** the University of Tokyo held a May 2023 mock trial with GPT-4 as judge. — [IT Daily](https://www.itdaily.kr/news/articleView.html?idxno=231783) [S]

**Turkey**
- **MootGPT** (İbn Haldun University Faculty of Law journal, 2 Jan 2026; built in the Spring 2024–25 "AI and Law" course; Arık, Arık, Kaan and Erol).
  - An "AI-based interactive moot court preparation assistant" built from system and user prompts, using Input–Output, Chain-of-Thought, Expert and Tree-of-Thought prompting.
  - It runs role simulations of judge, opposing attorney and academic advisor on aviation law.
  - **Strengths:** language accuracy, argument structure, practice through simulation, time efficiency.
  - **Limitations:** hallucination, template-like outputs, "risk of erosion in critical thinking", privacy and ethics.
  
  — [DergiPark](https://dergipark.org.tr/tr/pub/ihuhfd/article/1825618) [V]
- **"VR ile Mahkeme"** (TÜBİTAK 3005 project «Hukuk Eğitiminde Sanal Gerçeklik Destekli Kurgusal Dava Simülasyonları», VR-supported fictional case simulations in legal education). Students "sanal mahkeme ortamlarında davaları deneyimleyebilir" (can experience cases in virtual courtrooms) via VR glasses, phone or computer. **No AI.** — [vrilemahkeme.com](https://www.vrilemahkeme.com/) [V]
- A commercial "Hukukçu Yapay Zeka" offers eight expert personas and a "yargılama simülasyonu" (trial simulation). — [Fullegal](https://www.fullegal.com/hukukcu-yapay-zeka) [S]. Live mini-hearing simulations and moot competitions also exist, for example at ÇAKÜ and HUBİTSEM. — [ÇAKÜ](https://yabom.karatekin.edu.tr/caku-hukuk-fakultesi-gelecegin-hukuku-yaz-okulu-117-kursu.karatekin), [Substack](https://turkiyehukuk.substack.com/p/hubitsem-kurgusal-durusma-yarsmasna) [S]

**Arabic-language**
- **Legaline "Meta Legal Space" (UAE)** was launched at the Dubai AI Festival (26–27 Oct 2026) as "أول محاكمة صورية تعمل بالذكاء الاصطناعي" (the first AI-powered mock trial) in MENA.
  - **Roles:** AI plays judge, clerk, witnesses and experts. Opposing counsel can be AI or a fellow student.
  - **Witnesses** have adjustable background, credibility and composure, and "يحجب كل شاهد معلومة واحدة على المتدرب أن يستخرجها" (each withholds one fact the trainee must extract by questioning).
  - **Procedures and forums:** litigation, arbitration or mediation, under UAE mainland law, DIFC or ADGM.
  - **Cases:** written by practising lawyers; commercial, civil and labour.
  - **Feedback:** a report on argument strength, procedural compliance and handling of objections, plus a leaderboard.
  - A licensed lawyer can sit as judge.
  - **Access:** "التسجيل مجاني" (registration is free). The article gives no direct URL.
  
  — [Arqam](https://arqam.news/605403/) [V]; also [FintechGate](http://www.fintechgate.net/255518) [S]
- **Khabeer (خبير, Saudi Arabia)** offers an interactive court simulation following the Saudi judicial system.
  - Roles: a virtual judge ("القاضي الافتراضي"), a virtual lawyer, an AI legal assistant and witnesses.
  - Four steps: upload the case; AI analysis with precedents; an interactive session; a results report with "تحليل الأداء" (performance analysis).
  - Free to start ("ابدأ الآن مجاناً"), with an App Store app. This is marketing copy.
  
  — [khaberai.com campaign page](https://compaign.khaberai.com/) [V]
- Egypt: a Sohag faculty held a mock "economic court" trying AI-related cases. — [khalfelhadth.com](https://khalfelhadth.com/149099) [S]

### Inferences
- The strongest design references for LexSim are:
  - **SimCourt:** a full procedural structure, a large national legal knowledge base, and transcript plus decision as teaching output.
  - **Legaline:** witnesses with hidden facts, forum-specific procedure, performance reports, and a human judge option.
  - **AgentCourt:** open code and a local-LLM option.
- SimCourt's reported weaknesses (a partial AI judge, unblocked leading questions) show that procedural guardrails must be enforced outside the LLM.
- Korea's model of in-house hosting and visible sources for judicial AI matches how Uzbek institutions are likely to judge data sovereignty. It is also relevant because of the KOICA-funded Uzbek–Korean legal centre at TSUL.

### Gaps
- I found no peer-reviewed study of learning outcomes for any of these simulators. MootGPT's findings are qualitative, and the Chinese classroom reports are press releases.
- Legaline's interface languages and URL are not stated in the verified article. Khabeer's claims are marketing.
- The ilab-x project details could not be read (JS-rendered page). The Korean JRTI article was mostly garbled.
- SimCourt has no public code. The ACL 2026 listing was not fetched.

## 4. How these projects handle local procedural codes, local languages and legal databases

### Takeaway
Two patterns dominate:
- **Procedure is enforced by deterministic code or scripted scenarios:** ChatCourt's APK engine, ProgramLab's scenario logic, SimCourt's fixed five stages, Legaline's forum-specific frameworks.
- **Legal grounding comes from retrieval over national corpora:** SimCourt's 55,347 laws plus LegalOne; ConsultantPlus's 360M+ documents; LexAI CHAT-BOT-2 restricted to lex.uz with provision-level links; the Korean courts' internal corpus with visible sources.

Several projects have no local grounding at all: ChatCourt has no RAG, and JurLab uses only ECtHR and UN sources. Language and model choices follow sovereignty: GigaChat in Russia, a "national model" on Lex.uz, in-house AI in Korea.

### Cited Findings
**Procedure handling**
- **ChatCourt:** "Код должен решать, что допустимо" (code decides what is permissible). It was narrowed to first-instance APK, and its "guided" mode lets the engine choose the step and offer 1–3 actions. — [Habr](https://habr.com/ru/articles/1108458/) [V]
- **ProgramLab:** AI participants act "в рамках логики работы по сценарию" (within the scenario logic), with training and exam modes and instructor monitoring. — [ProgramLab](https://pl-llc.ru/catalog/ekonomika-i-predprinimatelstvo/virtualnye-trenazhery-dlya-spetsialistov-yuridicheskogo-profilya-/virtualnyy-vr-trenazher-protsedurnyy-simulyator-sudebnogo-zasedaniya-po-grazhdanskim-delam/) [V]
- **SimCourt:** the "5 core stages of a Chinese trial", based on "the real-world procedure structure of Chinese courts". — [arXiv](https://arxiv.org/abs/2508.17322) [V]
- **Legaline:** a choice of litigation, arbitration or mediation under UAE mainland, DIFC or ADGM rules, with performance reports that include "procedural compliance". — [Arqam](https://arqam.news/605403/) [V]
- **Guangming:** injected procedural events (a judge's clarification when a step is skipped, jurisdictional objections). — [Guangming](https://legal.gmw.cn/2025-10/15/content_38345399.htm) [V]
- **Khabeer:** says its simulation follows the Saudi judicial system. — [Khabeer](https://compaign.khaberai.com/) [V]

**Grounding in legal databases**
- **SimCourt:** 55,347 laws, plus LegalOne's 2M documents and 200k SPC-selected cases; experts found 100% citation accuracy. — [Pravo.ru](https://pravo.ru/story/262385/) [V]
- **AgentsCourt:** a "Legal-KB" knowledge base. **AgentCourt:** a knowledge base that evolves through adversarial play. — [arXiv 2403.02959](https://arxiv.org/abs/2403.02959), [arXiv 2408.08089](https://arxiv.org/abs/2408.08089) [V]
- **ChatCourt:** no RAG over case law or current legislation, and weak decisions. — [Habr](https://habr.com/ru/articles/1108458/) [V]
- **JurLab:** HUDOC and OHCHR APIs only. — [zp.edu.ua](https://zp.edu.ua/en/all-news/jurlab-iak-shtuchnyj-intelekt-zminiuie-navchannia-iurystiv-en/) [V]
- **ConsultantPlus AI:** answers from current acts, court practice and expert materials, with document sets attached for verification. — [consultant.ru](https://www.consultant.ru/about/nc/ai_inform/) [V]
- **LexAI CHAT-BOT-2:** answers "faqat lex.uz ma’lumotlari doirasida" (only within lex.uz data) and links to the relevant part of the document. — [LexAI locale](https://ai.lex.uz/i18n/locales/uz.json) [V]
- **Korean court AI:** an internal corpus of precedents, statutes and manuals, showing sources so users can verify answers. — [Hankyung](https://www.hankyung.com/article/202602134488i) [V]
- **Kazakh court analytics:** millions of court acts, with anomaly detection and civil-outcome prediction. — [Pravo.ru](https://pravo.ru/news/245406/) [V]
- **Uzbek judges' Academy:** may use the Supreme Court's "Adolat" information systems complex. — [lex.uz PF-141](https://lex.uz/docs/-7696594) [V]

**Language and model sovereignty**
- ChatCourt targets GigaChat for Russian universities. — [Habr](https://habr.com/ru/articles/1108458/) [V]
- The HSE course teaches GigaChat, DeepSeek and «Нейроюрист от Яндекс». — [HSE](https://lawhub.hse.ru/aiinlaw) [V]
- LexAI uses a "national model". — [LexAI locale](https://ai.lex.uz/i18n/locales/uz.json) [V]
- Korean courts avoid external LLMs. — [Hankyung](https://www.hankyung.com/article/202602134488i) [V]
- Russian firms run local or closed LLMs for confidentiality. — [Pravo.ru](https://pravo.ru/story/262385/) [V]
- LawMatic plans locally installed models. — [lawful.ru](https://www.lawful.ru/) [V]
- AgentCourt supports an offline local LLM. — [GitHub](https://github.com/relic-yuexi/AgentCourt) [V]
- Uzbekistan's FairTech hackathon requires a legal chatbot in Uzbek, Russian and English with links to sources. — [FairTech](https://hackaton.fairtech.uz/) [V]
- Uzbekistan's 2026 AI ethics rules require compliance with personal-data and cybersecurity law. — [lex.uz 8083233](https://lex.uz/docs/8083233) [S]

**Assessment and feedback**
- ChatCourt: instructors grade conduct, not outcome. — [Habr](https://habr.com/ru/articles/1108458/) [V]
- ProgramLab: training mode with hints and a report; exam mode with points. — [ProgramLab](https://pl-llc.ru/catalog/ekonomika-i-predprinimatelstvo/virtualnye-trenazhery-dlya-spetsialistov-yuridicheskogo-profilya-/virtualnyy-vr-trenazher-protsedurnyy-simulyator-sudebnogo-zasedaniya-po-grazhdanskim-delam/) [V]
- Legaline: a report on argument strength, procedural compliance and objections, plus a leaderboard. — [Arqam](https://arqam.news/605403/) [V]
- Tomsk's six-metric rubric for judging AI output. — [TSU](https://news.tsu.ru/news/studenty-yui-tgu-protestirovali-yuridicheskiy-ii-na-120-realnykh-delakh/) [V]
- MSAL's VR trainer gives automatic assessment with detailed feedback. — [msal.ru](https://msal.ru/news/v-universitete-imeni-o-e-kutafina-mgyua-razrabotan-vr-trenazher-po-kriminalistike/) [V]

**Disclosure of AI use and guardrails**
- Huaqiao's AI-use explanation segment. — [hqu.edu.cn](https://jwc.hqu.edu.cn/info/1063/29964.htm) [V]
- LexAI: answers are advisory and create no rights or obligations. — [LexAI locale](https://ai.lex.uz/i18n/locales/uz.json) [V]
- Kyrgyz judge: AI must not be a "скрытым соавтором судебного акта" (hidden co-author of a judicial act). — [24.kg](https://24.kg/article/inara-gilyazetdinova-ii-ne-dolzhen-stanovitsya-soavtorom-sudebnogo-resheniya) [V]
- Tyumen: only a human should decide a person's fate. — [RG](https://rg.ru/2024/05/22/reg-urfo/v-tiumenskom-sude-reshenie-vpervye-vynesla-nejroset.html) [V]

**Quick reference**

| Project | Country / language | Type | How procedure is handled | Legal grounding | Access / status | Source |
|---|---|---|---|---|---|---|
| ChatCourt | Russia / RU | LLM trial trainer (student plays a party) | Deterministic first-instance APK engine | None (no RAG) | Beta with students; no public link | [Habr](https://habr.com/ru/articles/1108458/) |
| LawMatic Trial | Russia / RU | Multi-agent AI trainer for lawyers | Configurable events; any instance | Not stated | Free registration; iOS/macOS | [lawful.ru](https://www.lawful.ru/) |
| ProgramLab VR civil simulator | Russia / RU | Scripted VR or desktop simulator | Scenario tree; train and exam modes | Scenario content | 1.69M RUB licence | [pl-llc.ru](https://pl-llc.ru/catalog/ekonomika-i-predprinimatelstvo/virtualnye-trenazhery-dlya-spetsialistov-yuridicheskogo-profilya-/virtualnyy-vr-trenazher-protsedurnyy-simulyator-sudebnogo-zasedaniya-po-grazhdanskim-delam/) |
| JurLab | Ukraine / UA | Custom GPT for legal situations | Free-form role-play | HUDOC and OHCHR | ChatGPT GPT link | [zp.edu.ua](https://zp.edu.ua/en/all-news/jurlab-iak-shtuchnyj-intelekt-zminiuie-navchannia-iurystiv-en/) |
| LexAI | Uzbekistan / UZ | Legal chatbot (not a simulator) | n/a | lex.uz only (bot 2), with citations | Free quota plus tariffs | [ai.lex.uz](https://ai.lex.uz/) |
| SimCourt | China / ZH | Research multi-agent criminal trial | Fixed 5 stages | 55,347 laws plus LegalOne | Paper; no code | [arXiv](https://arxiv.org/abs/2508.17322) |
| AgentCourt | China / ZH | Research adversarial lawyer agents | Simulated court program | Evolving knowledge base | Public GitHub | [GitHub](https://github.com/relic-yuexi/AgentCourt) |
| Meta Legal Space (Legaline) | UAE / AR(?) | Commercial AI mock courtroom | Litigation, arbitration or mediation; UAE, DIFC or ADGM | Lawyer-written cases | Free registration | [Arqam](https://arqam.news/605403/) |
| Khabeer | Saudi Arabia / AR | AI court simulation and consultation | Saudi judicial system (claimed) | Precedents (claimed) | Free start; app | [Khabeer](https://compaign.khaberai.com/) |
| MootGPT | Turkey / TR | Course-built moot assistant | Prompt skeleton | Not described | Academic | [DergiPark](https://dergipark.org.tr/tr/pub/ihuhfd/article/1825618) |

### Inferences
- The architecture that works best combines three parts:
  1. a procedural state machine derived from the relevant code;
  2. LLM agents for each role with isolated context;
  3. retrieval over the official legal corpus, with provision-level citations.
- Simulators without the third part produce weak or unverifiable decisions (ChatCourt). Simulators without the first part depend on scripted trees (ProgramLab) or drift procedurally (SimCourt's leading-question problem).
- None of the verified projects runs in Uzbek, Kazakh or Kyrgyz. The only verified Uzbek-language legal LLM service is LexAI, a Q&A chatbot rather than a simulator.

### Gaps
- No verified project documents how it encodes a national procedural code: rule tables, state machines or prompts. ChatCourt gives the principle but not the encoding.
- I found no Uzbek-language legal LLM benchmarks and no evaluation of how well LexAI's "national model" answers.
- I did not confirm the interface languages for Legaline, the Kazakh Adilet AI consultant or the Kyrgyz Мыйзамчы.

## 5. Gaps and opportunities for an Uzbek AI court simulator (LexSim)

### Takeaway
The niche is open. I found no Uzbek-language (or Kazakh or Kyrgyz) AI courtroom role-play simulator. Meanwhile, the Uzbek state has created explicit demand: PF-141's "virtual sud", AI classes and simulation principle; the Digital Court rollout; and TSUL's KOICA AI-capacity project. It also offers building blocks: Lex.uz and LexAI's grounded national-model bot, which is open to partnership, and the "Adolat" information systems. LexSim can stand out by combining:
- a procedural engine for Uzbek law driven by code;
- citations grounded in Lex.uz;
- realistic AI role agents;
- assessment at the standard instructors expect.

### Cited Findings
**Demand**
- PF-141 mandates "virtual sud" sessions and AI classes in judicial retraining from 1 Oct 2025, "nazariya — amaliyot-imitatsiya" dual training, and interactive e-courses with online assessment (Annex 4, item 8). — [lex.uz PF-141](https://lex.uz/docs/-7696594) [V]
- The Academy currently runs mock trials in equipped courtrooms with trainees in every role, plus "virtual court" observation of real hearings. — [sudacademy.uz](https://sudacademy.uz/general-information) [V]
- The Digital Court concept, AI hearing minutes, automatic document drafts and the my.sud.uz AI consultant are being rolled out across 2025–2027. — [Zamon.uz](https://zamon.uz/uz/2025/08/22/endi-suniy-intellekt-yordamida-sud-muhokamasining-taxminiy-natijasini-bilish-mumkin-boladi-38216), [UzA](https://uza.uz/en/posts/sudlar-faoliyatiga-suniy-intellekt-texnologiyalari-joriy-etiladi_753553) [V]
- The TSUL–Ministry of Justice–KOICA project (USD 14.5M, 2026–2030) includes AI and legal-tech training for TSUL students and faculty. — [tsul.uz](https://tsul.uz/ru/news/1387/Universitet/%D0%9C%D0%B8%D0%BD%D0%B8%D1%81%D1%82%D0%B5%D1%80%D1%81%D1%82%D0%B2%D0%BE-%D1%8E%D1%81%D1%82%D0%B8%D1%86%D0%B8%D0%B8,-KOICA-%D0%B8-%D0%A2%D0%93%D0%AE%D0%A3-%D0%B1%D1%83%D0%B4%D1%83%D1%82-%D1%86%D0%B8%D1%84%D1%80%D0%BE%D0%B2%D0%B8%D0%B7%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D1%82%D1%8C-%D1%8E%D1%80%D0%B8%D0%B4%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B5-%D1%83%D1%81%D0%BB%D1%83%D0%B3%D0%B8) [V]
- Regional demand: Kazakhstan's Academy of Justice is studying AI "for modelling court proceedings". — [primeminister.kz](https://primeminister.kz/news/reviews/sot-toreligi-akademiiasynyn-2025-2027-zyldarga-arnalgan-damytu-tuzyrymdamasy-oku-procesine-cifrlyk-sesimder-engizilude-30534) [V]. Kyrgyzstan's Higher School of Justice is getting a digital training system. — [24.kg](https://24.kg/article/inara-gilyazetdinova-ii-ne-dolzhen-stanovitsya-soavtorom-sudebnogo-resheniya) [V]

**Building blocks**
- LexAI's CHAT-BOT-2 (national model; lex.uz-only answers; provision links) and its stated openness to partnership. — [LexAI locale](https://ai.lex.uz/i18n/locales/uz.json) [V]
- Government hackathons already ask for Uzbek, Russian and English legal LLM assistants with links to sources. — [FairTech](https://hackaton.fairtech.uz/) [V]

**Design lessons from verified projects**
- Hard-code procedure and let the model act inside it. Start with one procedure type at first instance and about three cases. Rebuild each role's memory "desk" per call. Tune temperatures. Use rejection codes. Cache prompts to cut tokens by roughly 3x. — [Habr ChatCourt](https://habr.com/ru/articles/1108458/) [V]
- Without legal RAG, AI decisions stay weak. With a large national legal base, SimCourt reached 100% citation accuracy. Its AI judge still lacked impartiality and its prosecutors' leading questions went unblocked. — [Habr ChatCourt](https://habr.com/ru/articles/1108458/), [Pravo.ru](https://pravo.ru/story/262385/) [V]
- Realism features worth copying:
  - witnesses who withhold a fact and have adjustable credibility and composure;
  - an AI or peer opponent;
  - a human judge option;
  - a performance report covering argument strength, procedural compliance and objections;
  - a leaderboard.
  
  — [Arqam/Legaline](https://arqam.news/605403/) [V]
- Teaching modes: training with hints versus an exam with points and instructor monitoring. — [ProgramLab](https://pl-llc.ru/catalog/ekonomika-i-predprinimatelstvo/virtualnye-trenazhery-dlya-spetsialistov-yuridicheskogo-profilya-/virtualnyy-vr-trenazher-protsedurnyy-simulyator-sudebnogo-zasedaniya-po-grazhdanskim-delam/) [V]. Grade conduct, not outcome. — [Habr](https://habr.com/ru/articles/1108458/) [V]
- Dynamic procedural events (jurisdictional objections, evidence ambushes, judge clarifications) and the "AI draft + student revision + teacher review" workflow. — [Guangming](https://legal.gmw.cn/2025-10/15/content_38345399.htm) [V]
- Realistic events such as adjournments and disputes. — [lawful.ru](https://www.lawful.ru/) [V]
- An AI-use disclosure step. — [hqu.edu.cn](https://jwc.hqu.edu.cn/info/1063/29964.htm) [V]
- Teacher-in-the-loop positioning. — [JurLab](https://zp.edu.ua/en/all-news/jurlab-iak-shtuchnyj-intelekt-zminiuie-navchannia-iurystiv-en/) [V]
- Output a full transcript plus a decision as teaching material. — [Pravo.ru](https://pravo.ru/story/262385/) [V]
- Price anchors:
  - ProgramLab: 1.69M RUB institutional licence. — [ProgramLab](https://pl-llc.ru/catalog/ekonomika-i-predprinimatelstvo/virtualnye-trenazhery-dlya-spetsialistov-yuridicheskogo-profilya-/virtualnyy-vr-trenazher-protsedurnyy-simulyator-sudebnogo-zasedaniya-po-grazhdanskim-delam/) [V]
  - HSE AI course: 35,000 RUB. — [HSE](https://lawhub.hse.ru/aiinlaw) [V]
  - Legaline and Khabeer: free registration. — [Arqam](https://arqam.news/605403/), [Khabeer](https://compaign.khaberai.com/) [V]
- Data-sovereignty expectations: in-house judicial AI in Korea; local models at Russian firms and in LawMatic's plans. — [Hankyung](https://www.hankyung.com/article/202602134488i), [Pravo.ru](https://pravo.ru/story/262385/), [lawful.ru](https://www.lawful.ru/) [V]

### Inferences
These are my recommendations; none of them is sourced.
- **Positioning:** present LexSim as a ready-made way to deliver PF-141's "virtual sud", AI classes and "imitatsiya" component. Pilot with the Odil sudlov akademiyasi (retraining) and TSUL (students, possibly inside the KOICA 2026–2030 framework).
- **Architecture:**
  - Encode each Uzbek procedural code as its own state machine, starting with one first-instance track such as civil or economic. Uzbekistan has separate civil, economic, criminal and administrative-court procedure codes; check the current texts on lex.uz.
  - Have the LLM agents (judge, opposing party, prosecutor, witness, clerk) act only through actions the engine permits.
  - Ground every legal claim in Lex.uz articles with provision-level links, following LexAI's bot-2 pattern, or partner with "Adolat" NLIC.
- **Fixing known failures:**
  - Add explicit objection and leading-question rules, plus a check on judicial neutrality.
  - Treat the AI's verdict as feedback, not an authoritative ruling.
  - Let a teacher or judge take the bench.
- **Uzbek-specific realism:** simulate the Digital Court workflow (e-filing, remote participation, AI-generated minutes or "sud majlisi bayonnomasi", automatic document drafts), because that is what graduates will meet from 2026–2027.
- **Languages:** support Uzbek (Latin and Cyrillic) and Russian. FairTech's Uzbek, Russian and English requirement shows what the state expects. A Russian version opens Kazakhstan, Kyrgyzstan and Russian-language faculties.
- **Assessment:** combine ChatCourt's conduct-based grading, Legaline's report dimensions and Tomsk's six-metric rubric into a transparent scorecard that teachers can audit.
- **Compliance:** follow Uzbekistan's AI ethics rules and personal-data law. Anonymise case materials and offer a deployment on a national or local model for judicial-academy use.
- **Differentiation:** none of the regional projects found combines a code-driven procedural engine, national-corpus grounding, local-language role agents and teacher-grade assessment. Those four together are LexSim's defensible niche.

### Gaps
- I found no data on how well Uzbek-language LLMs reason about law or follow procedure, and no Uzbek legal NLP benchmark.
- I found no learning-outcome evidence, beyond qualitative reports, that AI courtroom simulators improve students' advocacy.
- It is unknown whether the Odil sudlov akademiyasi or TSUL has procured or tendered any simulation software. No tender was found.
- It is unknown whether LexAI or Lex.uz offers an API, data licence or terms that would let a third-party simulator ground its answers in Lex.uz.
- Several leads could not be verified: the Kazakh Academy AI item on ortcom.kz (certificate error), the Belarus Ministry of Justice article (timeout), the ilab-x details (JS), the Korean JRTI article (encoding), Garant ИСКРА's official pages, and the HSE–Netology, SPbU and MGIMO pages. All are marked [S] or [X] above.
