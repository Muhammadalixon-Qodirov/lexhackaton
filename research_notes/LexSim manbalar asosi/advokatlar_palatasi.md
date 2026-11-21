# Chamber of Advocates of Uzbekistan (Advokatlar palatasi) and the rules on advocates' conduct: source inventory for LexSim

Research date: 2026-11-20. Method: lex.uz pages were downloaded and their text was extracted and read directly, by article. Everything marked **[read]** was checked in the source text itself. Everything marked **[unverified]** comes only from search snippets, secondary aggregators or a summary of part of a page.

General note on licensing: lex.uz is the official National Legislation Database run by the Ministry of Justice and is free to read. Under Uzbek copyright law, normative legal acts are generally not copyright-protected. No explicit lex.uz reuse licence was found ([unverified], gap). nrm.uz is a commercial aggregator: it serves as a secondary source only, and reuse of its consolidated texts is not licensed.

---

## 1. The Chamber's official website and what it publishes

### Takeaway
The Chamber's current official site is **paruz.uz**, and advokatuz.uz redirects to it. The site is an Angular single-page app with sections for posts, a lawyer search, webinars, a gallery and polls. Its documents (ethics rules, exam question list) could not be machine-read. By regulation, the Chamber **must** publish the list of qualification-exam questions on its official website.

### Cited Findings
- **[read]** `https://advokatuz.uz` returns 301 to `http://paruz.uz`, then to `https://paruz.uz/`, which returns 200. The page is titled "Lawyers" and is an Angular SPA. Routes found in the JS bundle: `posts/:slug`, `post/:slug`, `lawyer-search`, `lawyer/:username`, `webinars`, `gallery`, `poll`, `register`, `auth`, `search`, `sitemap`. No static document links appear in the HTML. — [paruz.uz](https://paruz.uz/)
- advice.uz lists the Chamber's official sites as paruz.uz / advokatuz.uz. Address: Tashkent, Buyuk Ipak yo'li 471; phone +998 71 261-61-43 / 261-61-49. **[unverified]** — [advice.uz](https://www.advice.uz/uz/document/2171)
- **[read]** Legal status: the Chamber is a non-commercial organisation with compulsory membership for all advocates. Its tasks include "контроль за соблюдением адвокатами законодательства, Правил профессиональной этики адвокатов, адвокатской тайны и присяги адвоката". — Law No. 349-I, Arts. 12¹–12⁴, [lex.uz/docs/58372](https://lex.uz/docs/58372)
- **[read]** Governing act on how the Chamber is organised: Cabinet of Ministers Resolution No. 112 of 27.05.2008, "Ўзбекистон Республикаси адвокатлар палатаси фаолиятини ташкил этиш тўғрисида". — [lex.uz/docs/1359515](https://lex.uz/docs/1359515) (title read; body not read)
- **[read]** The Regulation on Qualification Commissions (MoJ reg. No. 3637, 07.07.2025), para. 33, says each specialisation has a list of about 150–200 questions, approved by the Chamber Chairman, "Адвокатлар палатасининг расмий веб-сайтида эълон қилиниб… доимий равишда янгилаб борилади". Para. 32 says exams are broadcast live on the Chamber's or regional branches' official website. — [lex.uz/docs/7619714](https://lex.uz/docs/7619714)
- **[read]** Presidential Decree PF-5441 (2018) ordered an "Ethics Commission" (Комиссия по этике) under the Chamber to develop "стандартов оказания квалифицированной юридической помощи и других стандартов адвокатской деятельности". It also ordered an electronic lawyer-search service, an e-library and an electronic "Адвокат" journal. — [lex.uz/docs/3731058](https://lex.uz/docs/3731058)

### Inferences
- The question list, ethics rules text and any standards most likely sit inside `paruz.uz/posts/...` pages, served through a JS API. To use them, someone must open the site in a browser and save the files by hand.
- The lawyer-search registry (`lawyer-search`) could serve as a reference for realistic names and firm types. Real persons must not be copied into the simulation.

### Gaps
- The exact URL of the published 150–200-question lists on paruz.uz was not found, because the SPA content is not crawlable with the tools used.
- Whether the Chamber has published a nizom/ustav, legal-aid standards (from the PF-5441 Ethics Commission), model client contracts or methodical recommendations was not verified.
- Whether the PF-5441 Ethics Commission standards were ever adopted was not found.

---

## 2. Advocates' Professional Ethics Rules (Адвокатнинг касб этикаси қоидалари / Правила профессиональной этики адвокатов)

### Takeaway
The latest edition found is the **"Адвокатнинг касб этикаси қоидалари", Annex No. 8 to the decision of the II Conference of the Chamber of Advocates of 27.09.2013**. It has 63 points in 7 chapters. It replaced the 2008 Rules, adopted by the founding conference on 12.09.2008. A 2023 draft new edition, which included a controversial point 55 restricting advocates' public criticism of state bodies, was **withdrawn on 1 November 2023**. No later edition was found. The full official text is **not** on lex.uz, which shows that the Rules are a Chamber (self-regulatory) act and not a registered state act. It is reachable through nrm.uz (secondary).

### Cited Findings
**Editions and status**
- 2013 edition: "Адвокатнинг касб этикаси Қоидалари (ЎзР Адвокатлар палатасининг II Конференциясининг 27.09.2013 й. қарорига 8-илова)". The page shows no amendments and no status flag. A summary of the page gives 63 points in chapters I. General (1–7), II. Prestige and dignity (8–18), III. Relations among advocates (19–28), IV. Relations with client (29–52), V. Relations with law-enforcement, courts and other bodies (53–56), VI. Relations with Chamber and qualification commissions (57–60), VII. Final (61–63). **[read via summarising fetch; not verified line by line]** — [nrm.uz doc 549533](https://nrm.uz/contentf?doc=549533_advokatning_kasb_etikasi_qoidalari_(o%E2%80%98zr_advokatlar_palatasining_ii_konferenciyasining_27_09_2013_y_qaroriga_8-ilova)&products=1_vse_zakonodatelstvo_uzbekistana)
- 2008 edition: "Правила профессиональной этики адвокатов Республики Узбекистан (Приняты Учредительной конференцией Палаты адвокатов 12 сентября 2008 года)". nrm.uz marks it "Документ утратил силу". zakon.kz shows it as in force from 31.12.2008, which is outdated and contradicts nrm.uz. Use the 2013 edition. — [nrm.uz doc 358598](https://nrm.uz/contentf?doc=358598_pravila_professionalnoy_etiki_advokatov_respubliki_uzbekistan_%28prinyaty_uchreditelnoy_konferenciey_palaty_advokatov_12_sentyabrya_2008_goda%29&products=1_vse_zakonodatelstvo_uzbekistana); [zakon.kz](https://online.zakon.kz/Document/?doc_id=30469209)
- An academic article describes the current code as "7 chapters and 65 rules". This contradicts the 63 points found on nrm.uz and is probably an error or a different count. **[unverified]** — [inlibrary.uz](https://inlibrary.uz/index.php/iqro/article/download/80430/81952/106937)
- 2023 draft: a new edition of the Rules was circulated in October 2023. Its new point 55 would have barred advocates from publishing material in media or social networks that criticised state bodies or officials, insulted them, or could breed distrust of reforms. The Chamber's press service said its leadership opposed point 55. — [kun.uz 24.10.2023](https://kun.uz/news/2023/10/24/advokatlar-erkinligini-cheklash-taklif-qilinmoqda-tashabbuskor-deyilgan-organning-ozi-bunga-qarshi-chiqdi); [gazeta.uz 23.10.2023](https://www.gazeta.uz/oz/2023/10/23/lawyers/)
- **[read]** On 1 Nov 2023 a working group found it "not advisable" to adopt the new ethics rules and the revised inspection-commission regulation. The draft was taken off the agenda. Working-group member Muhiddin Rahimov said this. — [kun.uz 02.11.2023](https://kun.uz/news/2023/11/02/advokatlarning-soz-erkinligini-cheklovchi-loyiha-kun-tartibidan-olib-tashlandi)
- **[read]** The Rules are still referenced as binding in 2024–2025 acts. Example: the Qualification Commissions Regulation (2025), para. 3: commissions act according to "Адвокатнинг касб этикаси қоидалари". — [lex.uz/docs/7619714](https://lex.uz/docs/7619714). A June 2024 MoJ order on trainees and assistants requires supervisors to familiarise trainees with the Rules. — [lex.uz/acts/-6951674](https://lex.uz/acts/-6951674) (title read; that clause [unverified])
- **[read]** Legal force: Law 349-I Art. 7 says advocates must observe "Правила профессиональной этики адвокатов". Art. 14 says breaching them leads to disciplinary measures. Art. 16 says systematic or single gross breach can end the licence. — [lex.uz/docs/58372](https://lex.uz/docs/58372)

**Key rules (2013 edition, point numbers from a summarising read of nrm.uz; verify against the full text before quoting)**
- *Honesty to court / process:* p.55 comply with procedural law and respect the court; p.54 no deliberate delay of proceedings; p.48 do not induce false testimony; p.43 arguments must be grounded in law, and the advocate must tell the client if claims are baseless; pp.18 and 36 the advocate may rely on documents from the client unless forgery is known.
- *Conflict of interest:* p.40 must refuse a mandate where interests conflict, where the advocate previously acted in the case as judge, prosecutor, investigator or expert, or where a relative is an official in the case; partners with conflicting clients need written consent of all; p.32 no new mandate that hinders an existing one; p.38 terminate the contract if a disqualifying ground appears later.
- *Advocate secrecy (advokatlik siri):* p.13 no time limit, and only the client can release the advocate; p.14 exceptions are client consent, consultation with colleagues the client did not object to, and the advocate's self-defence; p.15 scope; p.16 a separate file must be kept; p.17 the duty extends to assistants, trainees and staff; p.11 no testimony on secret matters.
- *Client relations:* p.29 law and ethics take precedence over the client's wishes; p.30 the advocate explains options and the client decides; pp.31 and 42 no guarantee of outcome and no unfounded hopes; p.33 no financial dependence on the client; p.34 no familiar relations; p.35 return originals on termination; p.39 appointed defence requires personal participation, and insolvency is no ground to refuse; p.41 notify the client before withdrawing; p.47 duty to appeal in certain cases.
- *Fees:* p.49 the advocate is entitled to a fee and expenses; p.50 the fee is set by agreement in a written contract, taking complexity and similar factors into account; p.51 a success fee is allowed if stated in the contract. This differs from the 2008 edition, which said to avoid success fees except in property disputes. p.52 no taking client property as security, except an advance.
- *Courtroom and authorities:* p.22 notify the court or investigator in advance of an unavoidable absence; p.56 objections must be made with decorum; p.11 do not discuss the case with witnesses, victims or experts outside the procedure, and do not promise results through personal ties with officials; p.53 role before these bodies.
- *Colleagues:* p.19 respect and help colleagues; p.20 do not lure another advocate's client; p.21 do not disparage colleagues or officials or comment on a colleague's fee; pp.23–24 joint representation; p.26 contact the opposing party only with the consent or presence of its counsel; p.27 warn the colleague first, then complain to the Chamber.
- *Advertising / media:* the 2013 edition has no explicit advertising rule. p.6 dignity, p.9 reputation, and p.21 public statements (for example, no calling a denying client guilty, no insults). The 2008 edition, p.2.4, prohibited self-advertising except place, time and types of legal aid. — [nrm.uz 358598](https://nrm.uz/contentf?doc=358598_pravila_professionalnoy_etiki_advokatov_respubliki_uzbekistan_%28prinyaty_uchreditelnoy_konferenciey_palaty_advokatov_12_sentyabrya_2008_goda%29&products=1_vse_zakonodatelstvo_uzbekistana)
- *Discipline:* p.7 liability under the Law; p.61 an advocate may request an explanation from the regional board, which cannot refuse; p.62 no discipline for acting on the regional board's explanation; p.63 a minor breach is not a ground for discipline.

### Inferences
- LexSim use: the 63 points are a good **scoring rubric**. Examples: penalise "guaranteeing a win" (pp.31/42), contacting the opposing party directly when it has counsel (p.26), disparaging opposing counsel (p.21), arriving late without notifying the court (p.22), or disclosing client facts (pp.13–15). They also work as **hints** ("p.31: do not promise outcome") and as citations in AI-judge or disciplinary feedback.
- Licence: a Chamber self-regulatory text. No open licence was found. Quote point numbers with short paraphrases instead of bulk-copying nrm.uz's text.

### Gaps
- The official primary copy of the 2013 Rules (Chamber site or PDF) was not located. nrm.uz is secondary and its status flag was not shown.
- It is not confirmed whether any Chamber conference after 2013 (for example in 2018–2026) amended the Rules. None was found.
- The exact wording of the points was not read line by line. Point numbers come from a summarising fetch and need manual verification.

---

## 3. Laws: "Advokatura to'g'risida" (349-I) and the Law on guarantees of advocates' activity (721-I)

### Takeaway
Two framework laws exist. The user's working title "…advokatlarning maqomi kafolatlari" is not the official one. Law 721-I is officially titled "Адвокатлик фаолиятининг кафолатлари ва адвокатларнинг ижтимоий ҳимояси тўғрисида" / "О гарантиях адвокатской деятельности и социальной защите адвокатов". Both are on lex.uz and current. 349-I is consolidated to 08.05.2025, and 721-I was last amended by ZRU-963 of 20.09.2024.

### Cited Findings
**Law No. 349-I of 27.12.1996 "Адвокатура тўғрисида" / "Об адвокатуре"** (Uz: [lex.uz/docs/54503](https://lex.uz/docs/54503), Ru: [lex.uz/docs/58372](https://lex.uz/docs/58372), version at 08.05.2025: [lex.uz/mact/-54503?ONDATE=08.05.2025](https://lex.uz/mact/-54503?ONDATE=08.05.2025+00)) **[read]**
- Articles: 1 tasks; 3 advocate (citizen, higher legal education, licence); 3¹ acquiring status (licence, then **oath within 3 months**, then join or form a firm); 4–4⁴ forms (bureau, firm, collegium, legal consultation); 6 rights; 7 duties; **7¹ advocate's request**; 8 assistant; 8¹ trainee; **9 advocate secrecy**; **9¹ agreement (contract) on legal aid**; 10 guarantees; 11 pay; 12¹–12⁴ Chamber; 13 qualification commissions; 13¹ suspension of status; **14 disciplinary liability**; 15–16 suspension and termination of licence; 17 MoJ.
- Art. 6 rights: represent clients in all bodies; collect and present evidence; request certificates and documents from state and other bodies; obtain expert opinions with client consent; interview persons with their consent; copy case materials; meet the client privately without limits, including in detention; file motions and complaints and receive reasoned written replies; insure liability; and (ZRU-786, 03.08.2022) **request an expert examination in economic, civil and administrative proceedings** and require the court to attach and evaluate it.
- Art. 7 duties: observe law, the Ethics Rules, secrecy and the oath. **No mandate if the advocate acts or acted for a party with conflicting interests** (ZRU-542, 2019). Do not use powers to the client's detriment. Do not abandon a criminal defence. Raise qualifications at least once every 3 years. A state-paid advocate may not refuse because of the client's insolvency (ZRU-915, 27.02.2024). May not be in state service. AML reporting duties apply.
- Art. 7¹ advocate's request: sent to state and other bodies; reply within **15 days**; **5 days** to say the information is not held; a shorter term once proceedings have begun (the WebFetch summary says 3 working days); **a copy of the order (ордер) must be attached**; may be filed electronically.
- Art. 9 secrecy covers the fact of seeking help, the questions, the substance of advice, and all conversation content. Disclosure or use by the advocate, assistant, trainee or staff is prohibited.
- Art. 14: breaching the law, the Ethics Rules, secrecy or the oath leads to disciplinary measures. Proceedings are opened only by a qualification commission or the Higher Qualification Commission.

**Law No. 721-I of 25.12.1998** (Ru: [lex.uz/docs/1321](https://lex.uz/docs/1321), Uz: [lex.uz/docs/29626](https://lex.uz/docs/29626)) **[read]**
- Art. 2 principles: independence; strict observance of the Ethics Rules, secrecy and the oath; use of lawful means only.
- **Art. 3 oath (full text):** «Торжественно клянусь честно и добросовестно выполнять свой профессиональный долг, последовательно защищать права и свободы человека, хранить адвокатскую тайну, строго соблюдать Конституцию и законы Республики Узбекистан». It is taken at a qualification-commission session.
- **Art. 4 powers:** "Полномочия адвоката на ведение конкретного дела удостоверяются **ордером**". The advocate has equal rights with other participants at all stages. Rights: study case materials; private meetings from the moment of detention; request expert examination in economic, civil and administrative cases; use recording devices (in court only with the presiding judge's permission, per the lex.uz comment on CPC Art. 19). Duties: advise on rights and obligations; **do not take a position that worsens the client's situation**; appeal a decision that is unlawful from the client's standpoint.
- Art. 5 independence; Art. 6 inviolability (home, office, transport, communications; a criminal case may be opened only by senior prosecutors; no submission or private court ruling may target the advocate's legal position); **Art. 7 non-interference:** it is prohibited to demand any special permit **other than the order and the advocate's ID**, and to demand explanations about secret matters.
- Amendments seen in the text: ZRU-198 (2008), ZRU-411 (2016), ZRU-446 (2017), ZRU-651 (2020), ZRU-786 (2022), ZRU-963 (20.09.2024, Art. 1).

**Order form**
- **[read]** The old MoJ order No. 1938 of 08.04.2009 on the order form lost force on 01.02.2023. It was replaced by **MoJ order No. 1-мх of 31.01.2023, "Об утверждении формы ордера на ведение дела адвокатом" (reg. No. 3417, 31.01.2023)**. The 2009 annex shows the bilingual layout: "Адвокат томонидан ишни олиб боришга ОРДЕР №___", the name of the firm, the advocate's name, a tear-off stub. — [lex.uz/docs/1468904](https://lex.uz/docs/1468904) (Ru), [lex.uz/docs/1468902](https://lex.uz/docs/1468902) (Uz)

### Inferences
- In LexSim's police-station / DXM visit scenario, the rule is that the advocate shows only the **order and ID** (721-I Art. 7; PF-5441 also abolished other requirements). If an officer demands anything else, that is an interference event the student should recognise and object to. The student should also invoke the right to a private meeting from the moment of detention (721-I Art. 4).
- Drafting module: an "advokat so'rovi" template should include addressee, legal basis (349-I Art. 7¹), requested information, the 15-day deadline, and an attached copy of the order.
- Economic and civil hearings: the right to request an expert examination and demand that it be evaluated (349-I Art. 6; 721-I Art. 4) is a concrete scoring point.

### Gaps
- The lex.uz document ID for MoJ order No. 3417 (31.01.2023), which holds the current order form, was not retrieved.
- No official template for an advocate's request (advokat so'rovi) or a model legal-aid contract (Art. 9¹) was found.
- The exact shortened deadline in Art. 7¹ once proceedings have begun ("3 working days") comes from a summary and was not re-read verbatim.

---

## 4. Qualification exam (programme, question bank, scoring)

### Takeaway
The exam is governed by the **Regulation on Qualification Commissions, MoJ reg. No. 3637 of 07.07.2025** (in force, with lex.uz editions dated 10.10.2025 and 17.08.2026). It is an **oral interview of 5 random questions** from a published list of 150–200 per specialisation. Each answer is scored 0–10, and the pass mark is **60%**. The question lists themselves were not found online. A good freely available proxy is the 2025 case-and-question set from the MoJ Institute for Retraining of Legal Personnel.

### Cited Findings
- **[read]** Reg. 3637, paras. 28–44 ([lex.uz/docs/7619714](https://lex.uz/docs/7619714)):
  - para. 28: the exam is held within 1 month of applying through the "Юридик ёрдам" information system;
  - para. 32: oral interview in one room, audio and video recorded, streamed live on the Chamber's site;
  - para. 33: topics. **Civil and economic specialisation:** advokatura, civil law, civil procedure, economic procedure, administrative court procedure. **Administrative and criminal specialisation:** advokatura, criminal law, criminal procedure, administrative liability. 150–200 questions each, approved by the Chamber Chairman and published and updated on the Chamber's site;
  - para. 34: 5 random questions, 30 minutes to prepare;
  - para. 35: no talking, no materials or devices;
  - para. 36: follow-up questions only within the scope of the original questions;
  - para. 37: answers must be precise and **at most 3 minutes per question**;
  - para. 38: 0–10 points per answer from each member;
  - para. 41: pass at **≥60%** of the maximum;
  - para. 44: the result goes to the "Лицензия" system;
  - Commission composition (para. 8): 7 members, at least 4 of them advocates, 2-year term.
- **[read]** The earlier regulation, MoJ No. 1921 of 14.03.2009, lost force on 10.10.2025. — [lex.uz/acts/1458645](https://lex.uz/acts/1458645)
- **[read]** Regulation on the Higher Qualification Commission, MoJ No. 1920 of 14.03.2009 (title read; it handles appeals against commission exam decisions, paras. 23–28). — [lex.uz/docs/1459048](https://lex.uz/docs/1459048)
- **[read]** PF-5441 cut the mandatory internship from 6 to 3 months and the re-sit wait from 1 year to 6 months, and called for transparent exams, including online broadcast. — [lex.uz/docs/3731058](https://lex.uz/docs/3731058). Reg. 3637 para. 27 also bars re-sitting within 6 months.
- **[read]** MoJ Institute for Retraining and Advanced Training of Legal Personnel, "Advokatlarning malakasini oshirish" course: *methodical materials for the final exam in case and interview form*, approved 23.07.2025 and based on the curriculum of 23.04.2025, 22 pp. Content: competency list (consultations; drafting claims and complaints; representation in civil, economic and administrative courts; criminal defence; "Advokatlik kasb etikasi qoidalarini bilish"); pass/fail criteria; **25+ case studies**. Examples: an advocate's licence suspended over a breach of secrecy (case 2); representing "UzBuild Group" in an economic court contract dispute (cases 5–6, with a 0.5% daily penalty and a pledged truck); bankruptcy (7); shareholder rights (8–10); defence access to protocols (19); inadmissible search evidence (20); a plea agreement (21); denial of an advocate in an administrative detention (23). — [uzmarkaz.uz PDF](https://www.uzmarkaz.uz/uploads/2025/07/advokatlardasturkazusvasavollar1.pdf)

### Inferences
- LexSim can mirror the official exam format in an "exam mode": 5 random questions, 30-minute preparation, at most 3 minutes per answer, 0–10 per answer, 60% pass. This gives a defensible scoring basis grounded in Reg. 3637.
- The uzmarkaz cases (especially 5, 6, 7 and 19–23) are directly usable as **scenario seeds** for economic-court and police-station modules. They are a public government institute publication, freely downloadable, with no open licence stated, so paraphrase and attribute.

### Gaps
- The Chamber-approved 150–200-question lists were not found (they are probably on paruz.uz behind the SPA).
- Whether Reg. 3637 was amended on 17.08.2026 and what changed was not checked.

---

## 5. Presidential decrees and other acts on advocacy reform

### Takeaway
The key reform act is **Decree PF-5441 of 12.05.2018**. It strengthened independence, required ID-and-order-only access to detainees, allowed phones, cameras and recorders at client meetings, created a Chamber Ethics Commission for standards, and digitised the profession. Later operational acts cover e-licensing and trainees.

### Cited Findings
- **[read]** PF-5441, 12.05.2018, "О мерах по коренному повышению эффективности института адвокатуры и расширению независимости адвокатов" (Ru [lex.uz/docs/3731058](https://lex.uz/docs/3731058); Uz [lex.uz/docs/3731060](https://lex.uz/docs/3731060)). Its diagnosis includes obstruction of advocates' access to clients, and violations by advocates caused by incompetence and bad faith. Measures:
  - the Ethics Commission for legal-aid standards;
  - qualification classes for advocates;
  - licence termination only through the courts, at the MoJ's request on the Higher Qualification Commission's conclusion;
  - discipline opened only by qualification commissions;
  - **advocates may use mobile phones, cameras and recorders when meeting clients**;
  - **no documents may be demanded other than the advocate's ID and order**;
  - a portal for real-time notification of planned visits to detainees;
  - automatic electronic assignment of state-paid advocates;
  - an electronic lawyer search.
- Cabinet of Ministers Resolution No. 432 of 05.08.2022 on licensing advocates through a special electronic system. It is cited by the lex.uz comment in 721-I Art. 1 as the current licensing procedure. A grep of the page also matched "lost force" text, so its status is **[unverified]**. — [lex.uz/docs/6143599](https://lex.uz/docs/6143599)
- MoJ order No. 3517 of 04.06.2024, "Regulation on the organisation of activities of advocate's trainee and assistant" (title read). — [lex.uz/acts/-6951674](https://lex.uz/acts/-6951674)

### Inferences
- PF-5441's access rules (phones and recorders allowed; only ID and order) give the police-station module concrete "correct behaviour" checkpoints. The student should know about pre-notifying the visit through the portal and should push back on demands for extra permits.

### Gaps
- Presidential acts after 2018 on advocacy (for example on state-guaranteed legal aid, the 2024 amendments behind ZRU-915, or 2025–2026 reforms) were not systematically searched.

---

## Quick inventory table (for LexSim)

| # | Document | Date / edition | Official URL | Status | LexSim use | Licence |
|---|---|---|---|---|---|---|
| 1 | Law 349-I "Advokatura to'g'risida" | 27.12.1996; ed. 08.05.2025 | [Uz](https://lex.uz/docs/54503) / [Ru](https://lex.uz/docs/58372) | In force [read] | AI judge and opponent knowledge base; citations (Arts. 6, 7, 7¹, 9, 14); scoring | Official, free; normative act |
| 2 | Law 721-I on guarantees of advocates' activity | 25.12.1998; last amend. ZRU-963 20.09.2024 | [Ru](https://lex.uz/docs/1321) / [Uz](https://lex.uz/docs/29626) | In force [read] | Oath text; order rule (Art. 4); police-station interference checks (Art. 7) | Official, free |
| 3 | Адвокатнинг касб этикаси қоидалари | Conf. decision 27.09.2013, annex 8; 2023 draft withdrawn | [nrm.uz 549533](https://nrm.uz/contentf?doc=549533_advokatning_kasb_etikasi_qoidalari_(o%E2%80%98zr_advokatlar_palatasining_ii_konferenciyasining_27_09_2013_y_qaroriga_8-ilova)&products=1_vse_zakonodatelstvo_uzbekistana) (secondary) | Presumed in force [partly read] | Main ethics scoring rubric; hints; disciplinary feedback | Chamber act; no open licence |
| 4 | Ethics Rules 2008 | 12.09.2008 | [nrm.uz 358598](https://nrm.uz/contentf?doc=358598_pravila_professionalnoy_etiki_advokatov_respubliki_uzbekistan_%28prinyaty_uchreditelnoy_konferenciey_palaty_advokatov_12_sentyabrya_2008_goda%29&products=1_vse_zakonodatelstvo_uzbekistana) | Lost force | Historical only | — |
| 5 | PF-5441 Decree | 12.05.2018 | [Ru](https://lex.uz/docs/3731058) / [Uz](https://lex.uz/docs/3731060) | In force [read] | Police-station access rules; context | Official, free |
| 6 | Reg. on Qualification Commissions (MoJ 3637) | 07.07.2025; eds. 10.10.2025, 17.08.2026 | [lex.uz/docs/7619714](https://lex.uz/docs/7619714) | In force [read] | Exam-mode format and scoring (5 questions, 0–10, 60%) | Official, free |
| 7 | Reg. on Higher Qualification Commission (MoJ 1920) | 14.03.2009 | [lex.uz/docs/1459048](https://lex.uz/docs/1459048) | In force (not flagged) | Appeal and discipline scenarios | Official, free |
| 8 | Order form (MoJ 1-мх, reg. 3417) | 31.01.2023 | ID not found; old form at [1468904](https://lex.uz/docs/1468904) | In force [unverified text] | Drafting template; document check at the police station | Official, free |
| 9 | Chamber organisation (CM Res. 112) | 27.05.2008 | [lex.uz/docs/1359515](https://lex.uz/docs/1359515) | Title only | Background | Official, free |
| 10 | Trainee/assistant regulation (MoJ 3517) | 04.06.2024 | [lex.uz/acts/-6951674](https://lex.uz/acts/-6951674) | Title only | The student-as-trainee role | Official, free |
| 11 | Institute case-and-question set | 23.07.2025 | [uzmarkaz.uz PDF](https://www.uzmarkaz.uz/uploads/2025/07/advokatlardasturkazusvasavollar1.pdf) | [read] | Scenario seeds; question bank | Government publication; no licence stated |
| 12 | Chamber website | — | [paruz.uz](https://paruz.uz/) | Live (SPA) | Should hold the question lists and Rules; needs manual download | Unknown |
