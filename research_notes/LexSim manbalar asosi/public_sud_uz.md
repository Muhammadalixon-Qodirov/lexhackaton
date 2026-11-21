# Official Uzbek court information portals (public.sud.uz, sud.uz, stat.sud.uz, my.sud.uz, Plenum resolutions) as a source base for LexSim

Research date: 2026-11-20. Method: direct HTTP fetches from this machine with curl and WebFetch, the sud.uz WordPress REST API, parsing of the stat.sud.uz Angular bundle and the XLSX files it links to, and web search.

**Access note (important):** `https://public.sud.uz`, `https://my.sud.uz` and `https://e-sud.uz` could **not** be fetched. curl returned code 000 and WebFetch failed with "unable to verify the first certificate". The `*.sud.uz` certificate chain is incomplete for non-Uzbek clients, and bypassing certificate verification was not permitted in this environment. So everything said below about the internal UI of public.sud.uz and my.sud.uz comes from secondary sources and is marked **[UNVERIFIED]**. These sites did load: `sud.uz` (including `/wp-json/`), `stat.sud.uz` and its XLSX files, `jadval2.sud.uz`, `exsud.sud.uz/decisions` (a 746-byte JS shell) and `lex.uz`.

## 1. What is public.sud.uz: sections, filters, document types, formats, anonymisation, URLs, API, terms

### Takeaway
public.sud.uz is the Supreme Court's official "Collection of Decisions" ("Qarorlar to'plami"). It publishes court acts that have entered into legal force, in anonymised form. It has separate sections per jurisdiction; the economic section is at `/report/ECONOMIC`. It is a JS single-page app with hash routes. No documented public API, bulk export or open-data licence was found. Its search filters and URL scheme for individual documents could not be checked because the site was unreachable from here.

### Cited Findings
- The sud.uz homepage footer and menu link to `https://public.sud.uz` and to `https://public.sud.uz/#!/sign/view`. The second looks like a document-verification (signature/QR check) route, which suggests a hash-routed AngularJS-style SPA. — [sud.uz homepage (fetched)](https://sud.uz/)
- The reforms portal describes the "Collection of Decisions" (public.sud.uz) as systematic publication of court decisions that have entered into legal force. It was introduced in 2017–2020, and about **2.5 million decisions** had been published by the time the page was written (page date not stated). — [reforms.alex-its.uz](https://reforms.alex-its.uz/en/direction-02_inner-02.html)
- An academic article (2025) says "All decisions of economic courts are published on the official website of the Supreme Court", cites `https://public.sud.uz/report/ECONOMIC` (accessed 20 Sept 2024), and analyses decisions from Dec 2018 to June 2024. — [Masadikov, AJEE 2025 (PDF)](https://ajee-journal.com/upload/attaches/att_1739570355.pdf)
- The same article cites decisions in this format: "Case no 4-10-2016/60 (Economic Court of Tashkent, 29 May 2020)" and "Case no 4-10-1809/177 (Supreme Court, 28 June 2019)". In other words, case number + court + date, with **no per-document URL**. This suggests stable deep links are not readily available or not commonly used. — [AJEE PDF](https://ajee-journal.com/upload/attaches/att_1739570355.pdf)
- **Legal basis for publication and anonymisation:** Supreme Court Plenum Resolution No. 04 of 21.02.2020, "On ensuring openness of court proceedings and the right to obtain information on courts' activities", para. 26. Texts are published under CPC art. 12 part 7, CrPC art. 19 part 11 and EPC art. 11 part 6. State secrets and other legally protected secrets are excluded. Decisions that have entered into force "may be published on the official website of the court **with depersonalisation (обезличивание)** or in full with the consent of the participants". Decisions that must be published by law (e.g. invalidation of a normative act) are published in full. The resolution was amended on 14.05.2022, 20.11.2023, 16.12.2024 and 29.04.2025. — [lex.uz/docs/4752673](https://lex.uz/docs/4752673)
- The same resolution, para. 27, requires that information on upcoming open hearings also be published on the court's official website. — [lex.uz/docs/4752673](https://lex.uz/docs/4752673)
- Earlier policy background: in 2019 Kun.uz reported that court decisions would be placed on the Internet, including on the Supreme Court website. — [kun.uz 2019-02-07](https://kun.uz/en/news/2019/02/07/court-decisions-in-uzbekistan-to-be-placed-on-the-internet)
- `https://sud.uz/robots.txt` disallows only `/wp-admin/`. The robots.txt for public.sud.uz could not be retrieved because of the certificate failure. — [sud.uz/robots.txt (fetched)](https://sud.uz/robots.txt)
- In November 2026 the sud.uz homepage linked a new PDF, `/wp-content/uploads/2026/11/restricted-links-and-materials.pdf` (title suggests "restricted links and materials"). Its contents were not read. — [sud.uz homepage (fetched)](https://sud.uz/)

### Inferences
- The sections almost certainly mirror the four jurisdictions: ECONOMIC, plus likely CIVIL, CRIMINAL and ADMINISTRATIVE. Only `/report/ECONOMIC` is confirmed by a source. The other path names are **[UNVERIFIED]**.
- The document types are likely first-instance hal qiluv qarori and ajrim, plus appellate/cassation qaror and ajrim (and hukm for criminal cases), since the Plenum resolution covers "texts of court decisions". Whether all types are published, and whether they come as HTML or PDF, is **[UNVERIFIED]**.
- Filters likely include court, region, case category, date and case number. This is **[UNVERIFIED]** and needs a manual check from an Uzbek IP or with a browser that has the full certificate chain.
- For LexSim, cite a decision as: court name + date + case number (e.g. "Toshkent shahar iqtisodiy sudi, 2020-05-29, ish № 4-10-2016/60") + "public.sud.uz, accessed DATE". Do not rely on deep links.
- **Scraping:** no terms of use were found. The decisions are anonymised official acts, and publication serves openness under Plenum Res. No. 04/2020. For an educational tool, the safer route is **manual curation** of a small corpus (tens to hundreds of decisions), re-anonymising and fictionalising facts, rather than bulk scraping. Get written confirmation from the Supreme Court IT department if bulk use is planned. This is a policy inference, not legal advice.
- **Limitations for LexSim:** anonymisation removes party names, so scenarios have to be rebuilt anyway. Decisions before 2023–2024 may apply repealed provisions; the Labour Code and the Administrative Procedure rules were revised, and the Plenum list shows many 2024–2026 amendments. Quality and length vary.

### Gaps
- The actual filters, document formats, date coverage start, per-document URL pattern, terms of use and robots.txt of public.sud.uz are all unverified because of the TLS failure.
- There is no confirmation of an API. The `exsud.sud.uz/decisions` route exists (a JS shell titled "Oliy sud") and may be a decision viewer for e-appeals, but its role is unverified.

## 2. Classifiers of case types and categories (which scenario types are most frequent)

### Takeaway
The official statistics (stat.sud.uz, Supreme Court Organisational-Control Department, "forma 10-a") give a usable category classifier with 2020–2025 volumes. Among economic **contract** disputes, the top categories in 2025 are supply (24%), communal services (19%), credit (13%), sale (11%), paid services (8%) and lease (5%). Civil cases are dominated by civil-law and family disputes.

### Cited Findings (all from XLSX files linked from https://stat.sud.uz, parsed by me)
Economic courts, 2025 annual file `https://stat.sud.uz/assets/uploads/economical/xls/eco-2025-12.xlsx` (published 11.02.2026):
- First-instance economic cases completed: 175,443 (2021), 277,862 (2022), 271,748 (2023), 436,086 (2024), **690,734 (2025)**. Of the 2025 cases, 649,523 were satisfied, 27,857 refused, 3,650 terminated and 9,704 left without consideration. — [eco-2025-12.xlsx](https://stat.sud.uz/assets/uploads/economical/xls/eco-2025-12.xlsx)
- Economic cases by category, 2025: disputes from **administrative-legal relations 550,832 (79.7%)**; civil-law disputes 124,271 (18.0%); insolvency 13,599 (2.0%); arbitration-related 919; corporate disputes 527; investment 144; competition 123; recognition of foreign decisions 95; legal facts 26. — [same file, sheet "иш тоифалари"](https://stat.sud.uz/assets/uploads/economical/xls/eco-2025-12.xlsx)
- Contract disputes in economic courts, 2025, total 119,042: supply (mahsulot yetkazib berish) 28,776 (24.2%); communal services 22,736 (19.1%); credit 15,115 (12.7%); sale (oldi-sotdi) 13,142 (11.0%); paid services 9,611 (8.1%); lease (ijara) 6,095 (5.1%); contracting (kontraktatsiya) 5,375 (4.5%); construction/work contract (pudrat) 4,487 (3.8%); leasing 3,219 (2.7%); insurance 2,226 (1.9%); loan (qarz) 1,235 (1.0%); carriage 284; telecom services 271. The 2020–2024 series are also in the file. — [same file, sheet "шартномавий низолар"](https://stat.sud.uz/assets/uploads/economical/xls/eco-2025-12.xlsx)
- Court-order (sud buyrug'i) procedure in economic courts fell to 392 cases (0.06%) in 2025. Tashkent city had the most economic cases (138,584). — [same file, sheet "Кўрилган ишлар (суд буйруги)"](https://stat.sud.uz/assets/uploads/economical/xls/eco-2025-12.xlsx)
- The economic file has other sheets: simplified procedure; contract conclusion, amendment, termination and invalidation; land; entrepreneurs; IP; investment; foreign judgments; foreign court requests; setting aside arbitral awards; enforcement of arbitral awards; enforcement-related applications; mediation. — [same file, table of contents](https://stat.sud.uz/assets/uploads/economical/xls/eco-2025-12.xlsx)

Civil courts, 2025 annual file `https://stat.sud.uz/assets/uploads/civil/xls/civil-2025-12.xlsx`:
- First-instance civil cases including court orders: 518,087 (2021) rising to **2,169,425 (2025)**. Excluding court orders the 2025 figure is 649,601. — [civil-2025-12.xlsx](https://stat.sud.uz/assets/uploads/civil/xls/civil-2025-12.xlsx)
- Civil categories, 2025 (excluding court orders): civil-law relations 224,817 (34.6%); family 134,229 (20.7%); housing 26,960 (4.2%); special proceedings 19,914 (3.1%); land 15,354 (2.4%); labour 14,343 (2.2%). The file also has 35 sheets broken down by subcategory: divorce, deprivation of parental rights, paternity, housing eviction/admission, unauthorised construction, reinstatement and wages, transactions, loan (qarz), credit, alimony, legal facts, arbitration, foreign judgments, IP, default (sirtdan) judgments, simplified procedure and mediation. — [same file](https://stat.sud.uz/assets/uploads/civil/xls/civil-2025-12.xlsx)

Administrative courts, 2025 file `https://stat.sud.uz/assets/uploads/administrative/xls/adm-2025-12.xlsx`:
- Sheets cover: public disputes at first instance; invalidation of decisions of administrative bodies; unlawful actions or inaction of officials; invalidation of hokim decisions; IP public disputes; decisions of the Pension Fund; applications by entrepreneurs; land. — [adm-2025-12.xlsx](https://stat.sud.uz/assets/uploads/administrative/xls/adm-2025-12.xlsx)

### Inferences
- The 79.7% "administrative-legal" share in economic courts most likely consists of mass state-initiated recoveries (taxes, fines, mandatory payments). These are high-volume but low-value for training. For LexSim's economic module, prioritise contract scenarios in this order: **supply → credit → sale → paid services/communal → lease → pudrat/construction → leasing → insurance**, plus **bankruptcy** and **corporate** as advanced levels.
- For the civil module: loan/credit recovery, family (divorce, alimony, property division), housing, and labour (reinstatement, wages).
- Use the "forma 10-a" category labels verbatim as LexSim's scenario taxonomy (Uzbek Latin labels are in the files).

### Gaps
- Criminal statistics files (`criminal-2025-12.xlsx`, `criminal-2026-6.xlsx`) were downloaded but not analysed by article.
- No official machine-readable classifier of "ish toifalari" codes, as used inside the courts' case-management system, was found.

## 3. Court statistics published by the Supreme Court

### Takeaway
stat.sud.uz is a static Angular app ("Sudlar faoliyati bo'yicha statistik ko'rsatkichlar"). It lists 119 downloadable files (XLSX/XLS/PDF) across four folders (economical 52, administrative 27, civil 20, criminal 20), with annual and half-year "asosiy ko'rsatkichlar". The latest are for 2025 (posted 11.02.2026) and the first half of 2026 (posted 10.08.2026). The files have stable URLs under `https://stat.sud.uz/assets/uploads/{economical|civil|administrative|criminal}/{xls|xlsv|pdf}/...`.

### Cited Findings
- Catalogue entries look like `{filename, period, date, xlsurl}`, for example "Iqtisodiy ishlar bo'yicha sudlarning 2026-yil 1-yarmidagi faoliyat yakunlarining asosiy ko'rsatkichlari", 10.08.2026, `assets/uploads/economical/xls/eco-2026-6.xlsx`. — [stat.sud.uz (bundle main.*.js parsed)](https://stat.sud.uz/)
- The economic series also includes single-topic files from 2015 to 2021: duration of proceedings, adjournments, ratio of registered to completed cases, expert examinations, simplified procedure, bankruptcy timelines, liquidation of bankrupt companies, pre-trial meetings, land disputes and IP. — [stat.sud.uz](https://stat.sud.uz/)
- The sud.uz "normative-documents" page lists Supreme Court open-data sets on data.egov.uz (XML/CSV/JSON/XLS/RDF). These are financial and budget data, not case data. — [sud.uz/normative-documents](https://sud.uz/normative-documents/)

### Inferences
- LexSim can bundle these figures as an "authoritative frequency" table for scenario prioritisation, and show learners things like "this type of dispute is X% of economic contract cases (Oliy sud statistikasi, 2025)".
- The statistics are aggregate only. They cannot be used for sourcing cases.

### Gaps
- No API was found. The files are updated by hand, roughly every half year.

## 4. Supreme Court Plenum resolutions database (economic procedure, penalties, limitation, lease, supply, evidence)

### Takeaway
sud.uz has a Plenum section (`/plenum/`) split into criminal, civil, administrative and economic lists. Each item links to the authoritative text on lex.uz (`https://lex.uz/docs/{id}`). The lists are current to 2026: the newest items are from 3 July 2026 (Nos. 18–20). Some recent items have no lex.uz link on sud.uz.

### Cited Findings
- Plenum index: `https://sud.uz/plenum/` → `/plenum/documents-economical/`, `/plenum/documents-civil/`, `/plenum/documents-administrative/`, `/plenum/documents-criminal/`. — [sud.uz/plenum](https://sud.uz/plenum/)
- Economic list, key items for LexSim (Plenum of the former Supreme Economic Court = OXS, or of the Supreme Court) — [sud.uz/plenum/documents-economical](https://sud.uz/plenum/documents-economical/):
  - Property liability for non-performance of obligations (penalties, damages) — 15.06.2007 No. 163 — https://lex.uz/docs/1636810
  - Delivery of goods of improper quality — 28.12.2007 No. 174 — https://lex.uz/docs/1643543; failure to take delivery of goods — No. 175 — https://lex.uz/docs/1643533
  - Law "On the contractual-legal basis of business entities" — 04.03.2002 No. 103 — https://lex.uz/docs/1643248
  - Conclusion, amendment and termination of business contracts — 18.12.2009 No. 203 — https://lex.uz/docs/2026051; settlement agreements — No. 204 — https://lex.uz/docs/2026218
  - Recognition of ownership — 19.11.2010 No. 220 — https://lex.uz/docs/1947974
  - **Property lease (ijara)** — 01.12.2011 No. 234 — https://lex.uz/docs/2004613
  - Arbitration (hakamlik) — 15.06.2012 No. 238 — https://lex.uz/docs/2483046; court orders — 05.12.2013 No. 254 — https://lex.uz/docs/2338574
  - Expert examination — 20.06.2014 No. 261 — https://lex.uz/docs/2453491; corporate disputes — No. 262 — https://lex.uz/docs/2453499
  - Invalidity of transactions — 28.11.2014 No. 269 — https://lex.uz/docs/2535141; videoconference hearings — No. 270 — https://lex.uz/docs/2534033
  - **Limitation period (da'vo muddati)** — 19.06.2015 No. 282 — https://lex.uz/docs/2712564; procedural time limits — No. 283 — https://lex.uz/docs/2712887
  - Leasing — 27.11.2015 No. 289 — https://lex.uz/docs/2851019; **construction pudrat** — 23.12.2016 No. 306 — https://lex.uz/docs/3106543; insurance — 29.11.2017 No. 45 — https://lex.uz/docs/3515213
  - **First-instance application of the Economic Procedural Code (EPC)** — 24.05.2019 No. 13 — https://lex.uz/docs/4395285
  - Court costs in economic cases — 19.12.2020 No. 36 — https://lex.uz/docs/5194320; **appeal** — 20.04.2021 No. 16 — https://lex.uz/docs/5416428; **cassation** — 27.11.2021 No. 36 — https://lex.uz/docs/5773005; **review (taftish)** — 25.06.2024 No. 21 — https://lex.uz/docs/7000816
  - Insolvency Law — 23.06.2025 No. 13 (no link on sud.uz); interim measures (da'voni ta'minlash) for civil, administrative and economic courts — 03.07.2026 No. 19; amendments — 16.12.2024 Nos. 38–39, 24.11.2025 No. 23, 03.07.2026 No. 20.
- Civil list highlights — [sud.uz/plenum/documents-civil](https://sud.uz/plenum/documents-civil/): "Sudning hal qiluv qarori haqida" 24.05.2019 No. 12; first-instance ajrims in civil cases 25.10.2019 No. 19; evidence and proof in civil cases 19.12.2020 No. 35; first-instance CPC application 19.05.2018 No. 14; preparation for trial 24.08.2018 No. 26; appeal 20.04.2021 No. 14; cassation 27.11.2021 No. 35; review 25.06.2024 No. 20; court costs 16.12.2024 No. 37; division of spouses' property 20.02.2023 No. 3; legal capacity 03.07.2026 No. 18; moral damages 28.04.2000 No. 7.
- Administrative list — [sud.uz/plenum/documents-administrative](https://sud.uz/plenum/documents-administrative/): administrative offences 30.11.2018 No. 35 (https://lex.uz/docs/4116801); appeal in administrative-offence cases 14.05.2022 No. 8 (https://lex.uz/docs/6034050); review 25.06.2024 No. 22 (https://lex.uz/docs/7002340); newly discovered circumstances in administrative courts 29.04.2025 No. 9.
- The page also links the lex.uz classifier of court-related normative acts (https://lex.uz/classifiers/7592) and the list of repealed court acts (https://lex.uz/docs/68425). — [sud.uz/plenum/documents-economical](https://sud.uz/plenum/documents-economical/)
- Plenum resolutions enter into force upon adoption. The Plenum meets at least once every four months. — [sud.uz/court-plenum](https://sud.uz/court-plenum/)

### Inferences
- In LexSim feedback, cite as: "O'zR Oliy sudi Plenumining 2019-yil 24-maydagi 13-son qarori, N-band" with a lex.uz link. lex.uz also offers point-level links ("Hujjat elementidan havola olish") and a version history, so the version-dated text can be stored.
- Many economic resolutions date from the OXS era (2002–2017). Check that they have not been repealed (lex.uz shows status) and that their article references match the current EPC and Civil Code.

### Gaps
- Not all items have lex.uz IDs on sud.uz (e.g. 2025 No. 13 on insolvency, 2026 Nos. 19–20). Their IDs need to be found on lex.uz.

## 5. my.sud.uz / e-sud e-filing: claim forms and fields

### Takeaway
my.sud.uz ("Sud organlarining interaktiv xizmatlar portali") is the official e-filing portal. Through a personal cabinet you file claims, applications, complaints, petitions and other procedural documents. It also offers simplified claim templates (`/claim-simples`), online case tracking, a state-duty calculator and a hearing calendar. Field-level details could not be verified.

### Cited Findings
- The sud.uz homepage links `https://my.sud.uz/claim-simples`, `https://my.sud.uz/#/#onlinetracking`, `https://my.sud.uz/#/#rules`, `https://cabinet.sud.uz/sign-in`, `https://billing.sud.uz` (payments and receipts), `https://qabul.sud.uz` (e-reception) and `https://vka.sud.uz` (videoconference). — [sud.uz (fetched)](https://sud.uz/)
- Filing steps per the Supreme Court's announcement (11.11.2026): register in "Shaxsiy kabinet", choose the court, choose the application type, enter the required data, attach documents and submit. Economic claims are possible for credit, sale, supply, lease and contracting disputes. Electronic submission does not mean automatic acceptance. — [gov.uz news 246342](https://gov.uz/ru/xovostuman/news/view/246342)
- my.sud.uz includes a "Calculator" for state duty in civil and economic cases (introduced 2017–2020). exsud.sud.uz ("Murojaat") handles e-appeals with online tracking and electronic receipt of decisions. — [reforms.alex-its.uz](https://reforms.alex-its.uz/en/direction-02_inner-02.html)
- The sud.uz FAQ (dated 04.08.2025) refers to the CPC art. 131 requirements for attachments, and says hearing dates are available in the my.sud.uz "Sud majlislari jadvali" section and on jadval.sud.uz. — [sud.uz/faq (via WP REST)](https://sud.uz/faq/)

### Inferences
- For LexSim's drafting module, build field schemas from the **procedural codes** (EPC requirements for the content of a da'vo arizasi; CPC art. 131 for attachments) rather than from my.sud.uz. The portal requires login (OneID or e-signature is likely, **[UNVERIFIED]**) and was unreachable.
- The categories that my.sud.uz explicitly supports for economic claims (credit, sale, supply, lease, contracting) match the top statistical categories in section 2. That is a good sign for scenario choice.

### Gaps
- The list of templates in `/claim-simples`, the form fields, the authentication method and the attachment rules could not be verified (TLS failure, login wall).

## 6. Hearing schedules and other official sources

### Takeaway
Hearing lists are public at jadval2.sud.uz, split by jurisdiction (criminal, civil, administrative, economic). lex.uz is the authoritative source for legislation and Plenum texts. It has a "Sud amaliyoti / Sud qarorlari" search tab.

### Cited Findings
- `https://jadval2.sud.uz/` ("Sud majlisiga tayinlangan ishlar ro'yxati") offers four lists: criminal, civil, administrative and economic courts. Court selection is client-side (sessionStorage), using jQuery and Bootstrap. — [jadval2.sud.uz (fetched)](https://jadval2.sud.uz/)
- lex.uz search has tabs "Sud amaliyoti" and "Sud qarorlari", filters for document type (including "Ajrim", "Hukm", "Sud amaliyoti"), status (amaldagi / o'z kuchini yo'qotgan), dates and language. It also links ai.lex.uz and sharh.lex.uz, and publishes "Foydalanish shartlari" and "Axborotni taqdim etish shartlari". — [lex.uz/uz/search/court (fetched)](https://lex.uz/uz/search/court)
- sud.uz also has Presidium pages (`/presedium/`), printed publications (`/printed-publications/`), a "Know your rights" section (`/know-your-rights/`) and regional court directories (`/regional-courts-info/...`). — [sud.uz](https://sud.uz/)

### Inferences
- The hearing lists can give realistic case captions and the typical mix of categories per court. They are a weak source, though, because they contain party names and are ephemeral. Do not store personal data.
- Use lex.uz as the **canonical citation target** for norms and Plenum resolutions in LexSim feedback (stable `docs/{id}` URLs, with version history).

### Gaps
- The coverage and depth of lex.uz "Sud qarorlari" compared with public.sud.uz were not assessed.
- The Ministry of Justice registry and the adliya.uz pages were not examined within this scope.
