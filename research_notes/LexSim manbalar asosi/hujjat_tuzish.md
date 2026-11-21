# Hujjat tuzish: Yurxizmat, rasmiy konstruktorlar va LexSim uchun hujjat rekvizitlari

Fetch method: yurxizmat.uz and lex.uz pages were downloaded directly with curl on 2026-11-20 and their text was extracted. That makes the quotes below primary text. The sites my.sud.uz, id.sud.uz and e-sud.uz did not respond from this environment (connection failed, HTTP 000), so the e-filing section relies on search snippets only. my.gov.uz loaded, but service search returned 404, so it also relies on snippets. Statute quotes are in the original Uzbek Cyrillic as published on lex.uz.

## 1. Yurxizmat: what it is, who runs it, which documents, how the flow works, cost and terms

### Takeaway
Yurxizmat.uz is a free "Legal Tech" self-service system for building documents from templates. It is run by the "Adolat" National Legal Information Centre under the Ministry of Justice and was launched in test mode on 1 April 2021. Its flow is template-based fill-in-the-blanks: the user fills short labelled fields and they are merged into fixed legal text with a live preview. The user does not write free-form text and the system does not check legal substance.

### Cited Findings
- The domain is https://yurxizmat.uz. The page title reads "Ўз-ўзига ҳуқуқий хизмат кўрсатиш тизими", and the footer reads "© 2024 Адлия вазирлиги қошидаги “Адолат” миллий ҳуқуқий ахборот маркази". — [yurxizmat.uz](https://yurxizmat.uz)
- The site defines itself as "ҳуқуқшунос (адвокат) иштирокисиз ҳуқуқий ҳужжатларни (аризалар, шартномалар, ташкилотларнинг таъсис ҳужжатлари в.ҳ.) автоматлаштирилган ҳолда (конструктор) электрон шаклда тайёрлаш, қайта ишлаш ва фойдаланиш имконини берувчи электрон тизим". Its stated audience is small and medium business, low-income people and other citizens or organisations. — [yurxizmat.uz](https://yurxizmat.uz)
- Launch: "www.yurxizmat.uz ... ахборот тизими 2021 йил 1 апрель куни тест режимида ишга туширилди". — [yurxizmat.uz/uz/about](https://yurxizmat.uz/uz/about)
- A news article from the early rollout reports about 300 templates in 6 sections (contracts, applications, court documents, corporate, personnel, notarial), downloadable as doc/pdf, fillable on the site and printable, and in test mode. — [buxgalter.uz](https://buxgalter.uz/oz/publish/doc/text173679_yurxizmat_uz_sayti_test_rejimida_shartnomalar_namunalari_bilan_ishlamoqda)
- The home page describes a 3-step user flow: "Ҳужжатни танланг → Ҳужжатни тўлдиринг (ажратилган майдонларни тўлдиринг) → Кўчириб олинг (маъқул шаклда юклаб олинг)". — [yurxizmat.uz](https://yurxizmat.uz)
- Top-level categories, as shown on the page:
  - Шартномалар
  - Аризалар (юридик/жисмоний шахслар, болаларга оид, илтимосномалар)
  - Шахсий таркибга оид ҳужжатлар (ариза, билдиргилар, буйруқлар, далолатномалар)
  - Нотариал тасдиқланадиган ҳужжатлар (аризалар, васиятномалар, ишончномалар, нотариал шартномалар)
  - Судга оид ҳужжатлар
  - Корпоратив ҳужжатлар (талабномалар, уставлар, далолатномалар ва баённомалар)

  Source: [yurxizmat.uz/uz/category/court-claims](https://yurxizmat.uz/uz/category/court-claims)
- The court-documents section has three groups:
  - Даъво аризалар, split by dispute type: меҳнат, уй-жой, никоҳ/алимент/оилавий, зарар етказиш, мерос/васиятнома, автотранспорт, бошқа низолар.
  - Аризалар: суд ҳужжатларидан нусха; даъво талабига аниқлик, ўзгартириш, воз кечиш; даъвони таъминлаш ва хатлаш; иш юритишни тугатиш ва тиклаш; ижро.
  - Баённомалар: апелляция, кассация шикоятлари; илтимосномалар.

  Source: [yurxizmat.uz/uz/category/court-claims](https://yurxizmat.uz/uz/category/court-claims)
- Sample claim titles include "Меросни қабул қилиб олиш муддатини тиклаш тўғрисида даъво ариза" and "Боланинг мол-мулкини қайтариш юзасидан даъво аризаси". Sample court applications include "Туғилганлик фактини белгилаш тўғрисида ариза", "Суд буйруғини бекор қилиш тўғрисида ариза" and "Даъво талаблари миқдорини камайтириш тўғрисида ариза". — [court-claims](https://yurxizmat.uz/uz/category/court-claims), [court-applications](https://yurxizmat.uz/uz/category/court-applications)
- The most-downloaded documents include the labour contract, sale contract, lease, and "Никоҳдан ажратиш ҳақида даъво ариза". — [yurxizmat.uz](https://yurxizmat.uz)
- **Anatomy of one claim template** (document 2562, "Иш берувчининг ишга қабул қилишга оид ҳаракатларини қонунга хилоф деб топиш ва етказилган зарарларни ундириш тўғрисида даъво аризаси"). Source: [yurxizmat.uz/uz/document/2562](https://yurxizmat.uz/uz/document/2562)
  - The form has 3 field groups:
    - "Даъво ариза реквизитлари": суд номи (autocomplete from a `CourtsDictionary`, `data-column="court_name"`) and ариза санаси.
    - "Тарафларнинг реквизитлари": даъвогар ФИО, яшаш манзили, телефон, e-mail; жавобгар ташкилот номи, манзили, СТИР, телефон, e-mail.
    - "Даъво ариза мазмуни": case-specific facts such as the claimant's school and field of study, the date the claimant applied for the job, the date of the respondent's reply letter, the date of the employment office letter, and the hidden vacancy.
  - All fields are plain `<input type="text">` (16 inputs). Only the court field uses a dictionary, and no validation attributes were found in the HTML.
  - The preview shows a fixed body of text with the field values merged in: the header ("Фуқаролик ишлари бўйича ... суди", Даъвогар/Жавобгар blocks), the title "ДАЪВО АРИЗАСИ", a narrative of the facts, the legal basis (Меҳнат кодексининг 119-, 320-моддалари; ФПК 270¹–270⁵), and a numbered "суддан ... сўрайман" prayer.
  - Download is offered as DOCX and PDF.
  - Observation: this template has no "илова қилинадиган ҳужжатлар рўйхати" block and no signature block in the preview text, although FPK art. 189 requires both (see §2). That is a useful teaching point: even official templates may miss requisites. (The preview text was read directly; it is possible the block is added on export, which was not checked.)
- Registration is by mobile phone number or OneID (id.egov.uz). Registered users can reuse their saved standard personal data in later templates ("Ҳужжат намуналарида стандарт маълумотлардан такрор фойдаланиш"). — [yurxizmat.uz/uz/faq](https://yurxizmat.uz/uz/faq)
- **Cost and terms (public offer):**
  - "«Юрхизмат.уз» расмий сайтидан фойдаланиш бепул ҳисобланади". Sections for legal entities and some documents may be paid "прескурант асосида".
  - Using the site's documents to prepare procedural documents for others commercially is prohibited without a written contract with the centre.
  - The user is responsible for the accuracy of the data they enter.
  - Use by minors is regulated (age 14–18 needs parental consent).

  Source: [yurxizmat.uz/uz/page/offer](https://yurxizmat.uz/uz/page/offer)
- A paid custom-drafting service also exists: "процессуал ва бошқарувга оид ҳужжатларни буюртмага асосан тайёрлаб бериш", contact legaltech@adolatmarkazi.uz, (55) 510-47-87. — [yurxizmat.uz/uz/page/order](https://yurxizmat.uz/uz/page/order)
- advice.uz is a separate, non-governmental source of court and application templates. — [advice.uz](https://www.advice.uz/oz/category/600)

### Inferences
- Yurxizmat's model is "slot filling into a fixed text", which is exactly what LexSim should not copy one-to-one. A student who fills slots learns nothing about structure. Its field grouping (court requisites / party requisites / substance) is still a good skeleton for LexSim's form sections.
- For LexSim: the student writes the free-text parts (facts, legal basis, prayer) and fills the structured parts (court, parties, claim value, attachments). The structured parts get exact automatic checks; the free-text parts get rubric or keyword checks.
- The court-name dictionary pattern (autocomplete from a court registry) maps directly to a LexSim check for "correct court and correct jurisdiction".

### Gaps
- The current template count (the about-300 figure dates from 2021) and whether "test mode" has officially ended were not found.
- Whether DOCX export adds the attachments and signature blocks was not checked, because the download requires login.
- No evidence was found of any substantive validation (for example, checking claim value against the duty paid).

## 2. Mandatory requisites, attachments and return grounds: IPK (economic), FPK (civil), JPK (crime report), plus the Murojaatlar law

### Takeaway
IPK arts. 149, 151 and 155, FPK arts. 189, 191 and 195, and JPK arts. 322–324 give an exact, enumerable list of requisites and defects. That suits per-item automatic checking. A defect in form or content leads to **return** of the claim (qaytarish: IPK 155, FPK 195), and a returned claim can be refiled once corrected. The "fix the defects within up to 10 days" notice exists in the current text, but only for claims transferred from another court type (IPK 152 part 3, FPK 192 part 2). Neither code uses the phrase "ҳаракатсиз қолдириш" (0 matches in either text).

### Cited Findings: IPK (Иқтисодий процессуал кодекс), [lex.uz/docs/3523891](https://lex.uz/docs/3523891)
- **Art. 149, "Даъво аризасининг шакли ва мазмуни".** The claim is filed in writing and signed by the claimant or their representative. It must state:
  1. ариза берилаётган суднинг номи;
  2. ишда иштирок этувчи шахсларнинг номи (ФИО), жойлашган ери (почта манзили) ёки яшаш жойи;
  3. агар даъво баҳоланиши лозим бўлса, даъвонинг баҳоси;
  4. даъво талабларига асос бўлган ҳолатлар;
  5. даъво талабларининг асосларини тасдиқловчи далиллар;
  6. ундирилаётган ёки низолашилаётган сумманинг ҳисоб-китоби;
  7. даъвогарнинг қонунчиликка асослаб келтирган талаблари, and for several respondents, the demands against each of them (wording per ЎРҚ-683, 21.04.2021);
  8. маълумотлар about compliance with the pre-trial (талабнома) procedure, if the law or the contract requires it;
  9. илова қилинаётган ҳужжатларнинг рўйхати.

  Phone, fax and e-mail are optional ("кўрсатилиши мумкин"). Motions (илтимосномалар) may be included. Related demands may be joined in one claim.
- **Art. 150.** The claimant must send copies of the claim, and of attachments the other parties do not have, to the respondent and third parties. Since ЎРҚ-607 (10.03.2020) this can be done electronically through the information system.
- **Art. 151, "Даъво аризасига илова қилинадиган ҳужжатлар".** Documents confirming:
  1. давлат божи ва почта харажатлари тўланганлигини;
  2. копия жавобгар ва учинчи шахсларга юборилганлигини;
  3. талабнома тартибига риоя этилганлигини (агар назарда тутилган бўлса);
  4. даъво талабларига асос бўлган ҳолатларни;
  5. даъвогарнинг ЮШ/ЯТТ сифатида давлат рўйхатидан ўтганлигини;
  6. вакилнинг имзолаш ваколатини.

  Special additions:
  - A claim to compel conclusion of a contract must include the draft contract.
  - Investment disputes require the investment contract.
  - **New part 4 (ЎРҚ-1165, 14.08.2026):** where jurisdiction was changed by agreement of the parties, including chosen extraterritorial jurisdiction, the document confirming that agreement must be attached.
- **Art. 152.** The judge decides acceptance, refusal, return or transfer within **5 days** of receipt, by ruling (ажрим). Part 3 (ЎРҚ-833, 26.04.2023): when a claim arrives from a civil or administrative court and does not meet arts. 149–151, the judge notifies the claimant within 5 days and gives up to **10 days** to fix the defects.
- **Art. 155, "Даъво аризасини қайтариш".** The claim is returned if:
  - 1) the form and content of art. 149 are not observed;
  - 1¹) the art. 152 part 3 instruction was not complied with in time;
  - 2) it is unsigned, or signed by an unauthorised person, or by a person whose position or name is not given;
  - 3) the case is outside this court's jurisdiction;
  - 4) linked demands are mixed between civil or administrative courts and the economic court;
  - 5) there is no proof that copies were sent to the respondent and third parties;
  - 6) there is no proof of payment of duty and postage, and no motion for deferral or instalments (or the motion was refused);
  - 7) there is no proof of the pre-trial талабнома procedure where it is required;
  - 7¹) there is no proof of mandatory mediation where it is required;
  - 8) unrelated demands are joined;
  - 9) there is no proof of the required prior recourse to a bank;
  - 10) a withdrawal request was received before acceptance.

  The return ruling can be appealed, and a corrected claim may be refiled in the general order.
- **Art. 107 (кўрмасдан қолдириш, i.e. leaving without consideration after acceptance).** Grounds:
  - a parallel case between the same parties;
  - an arbitration agreement;
  - the claim is unsigned or signed by an unauthorised person;
  - prior bank recourse was not made;
  - the талабнома procedure was not followed;
  - mediation was not followed;
  - and others.
- **Art. 114 (даъвонинг баҳоси).** Claim value is the sum claimed (for money claims) or the value of the property. Penalty (неустойка) amounts stated in the claim are included. Multiple independent demands are summed. If the value is stated wrongly, the court determines it.
- **Art. 113.** Duty grounds, deferral, exemption and refund are set by law (the State Duty Law, §3).

### Cited Findings: FPK (Фуқаролик процессуал кодекс, 22.01.2018), [lex.uz/docs/3517337](https://lex.uz/docs/3517337)
- **Art. 189, "Аризанинг мазмуни".** The claim must state:
  1. суд номи;
  2. даъвогар ФИО, яшаш жойи (an organisation gives its name, address and реквизитлар), and the representative's ФИО and address if a representative files;
  3. жавобгар ФИО, яшаш жойи (an organisation gives its name, address and реквизитлар);
  4. даъвогарнинг талаби;
  5. даъво баҳоси (агар баҳоланса);
  6. ҳолатлар ва уларни тасдиқловчи далиллар;
  7. судгача ҳал қилиш тартибига риоя (агар назарда тутилган бўлса);
  8. иловалар рўйхати.

  Further rules:
  - It is signed by the claimant or their representative, and a representative must attach a power of attorney (ишончнома).
  - A prosecutor or a body filing in someone else's interest must name that person.
  - Phone and e-mail are optional. **Giving an e-mail counts as consent to receive summonses and judgments electronically.**
- **Art. 191 (attachments).** Documents confirming:
  1. the circumstances the claim is based on;
  2. the pre-trial procedure, if it is required;
  3. payment of duty and postage (ЎРҚ-496, 11.10.2018);
  4. the representative's authority.

  Art. 190 covers copies of the claim and its attachments.
- **Art. 192.** Acceptance is decided within **10 days** (as amended by ЎРҚ-887, in force 01.01.2024). Part 2: for claims transferred from an economic or administrative court, the claimant is notified of defects against arts. 189–191 and given time to fix them.
- **Art. 195 (қайтариш).** The claim is returned if:
  - 1) it was filed by a person lacking legal capacity;
  - 2) the representative has no authority;
  - 3) the court lacks jurisdiction;
  - 4) **art. 189 requirements were not observed**;
  - 4¹) the art. 192 part 2 instruction was not met;
  - 5) unrelated demands are joined;
  - 6) it was withdrawn before acceptance;
  - 7) there is no proof of duty or postage payment, or no deferral motion;
  - 9) mediation was not followed where required.

  Item 8 is absent in the current text and was presumably repealed (unverified). The return ruling can be appealed, and refiling is allowed.
- FPK arts. 270⁶–270⁸ (and the Yurxizmat template's reference to FPK 270¹–270⁵) relate to special proceedings in chapter 27¹-type sections. This was **not verified**, so do not rely on that template citation.

### Cited Findings: JPK (Жиноят-процессуал кодекс, 22.09.1994), [lex.uz/docs/111460](https://lex.uz/docs/111460)
- **Art. 322.** The occasions (сабаблар) for opening a criminal case are:
  1. шахсларнинг аризалари;
  2. ташкилотлар ва мансабдор шахслар хабарлари;
  3. ОАВ хабарлари;
  4. information detected directly by the investigator or prosecutor;
  5. айбини бўйнига олиш ҳақидаги арз.

  The **ground** (асос) is information indicating signs of a crime.
- **Art. 323.** Anonymous, unsigned, forged-signature or fictitious-name reports cannot be a reason to open a case.
- **Art. 324, "Шахсларнинг аризалари".**
  - A report can be written or oral, and a written one must be signed by the reporter.
  - An oral report is recorded in a protocol (баённома). The protocol must contain the reporter's identity, place of residence and work, and personal ID document details; if there is no ID, identity is verified in other ways.
  - The reporter is warned of criminal liability for knowingly false reporting, and the warning is recorded and signed by them.
  - The circumstances are recorded in the reporter's own words, as close to verbatim as possible.
  - Both the reporter and the receiving official sign the protocol.
- **Art. 329.** Reports are registered and decided immediately, or within **10 days (сутка)** if checking is needed. The prosecutor may extend this up to 1 month in listed cases (long expertise, distant witnesses, new circumstances). During the pre-investigation check, only listed actions are allowed.
- Related articles: art. 325 (case on the victim's complaint), art. 330 (decisions on the report), art. 333 (refusal to open a case), art. 335 (forwarding a report by jurisdiction).

### Cited Findings: Murojaatlar law (for the DXM/police written complaint and ariza), ЎРҚ-445 of 11.09.2017, [lex.uz/docs/3336169](https://lex.uz/docs/3336169)
- **Art. 5.** Appeals can be oral, written or electronic. Their types are ариза, таклиф and шикоят, and all forms carry equal weight.
- **Art. 6 (requirements).**
  - An individual gives their ФИО and place of residence; a legal entity gives its full name and postal address.
  - Required: the exact name of the body, the addressee official's position and/or name, and the essence of the appeal (моҳият).
  - E-mail and phone are optional.
  - A written appeal must be signed (if the applicant cannot sign, the person who wrote it for them signs and adds their name).
  - A representative must attach proof of authority.
- **Art. 28 (terms).** An ариза or шикоят is considered within **15 days**, or up to 1 month if extra checking is needed. The head may extend this by at most 1 more month and must notify the applicant. A таклиф is considered within up to 1 month.
- **Art. 29 (left without consideration).** Anonymous appeals; appeals through a representative without proof of authority; appeals not meeting other requirements of the law.

### Inferences
- A requisite checklist for the LexSim auto-checker:
  - IPK claim: 9 content items (art. 149) + 6 attachment items (art. 151) + signature, giving about 16 binary checks. Each check maps to a return ground in art. 155, so feedback can cite the article ("qaytariladi: IPK 155-m. 1-q. 6-b.").
  - FPK claim: 8 content items (art. 189) + 4 attachment items (art. 191) + signature/ишончнома.
  - Crime report: signed and non-anonymous (JPK 323, 324); identity and address; the facts (what, when, where, who); for an oral report, the false-report warning acknowledged.
  - Complaint (murojaat): addressee body and official, applicant's ФИО and address, moҳият, signature, representative's authority.
- Map errors to legal outcomes so that the simulator returns a realistic court ruling ("Ажрим: даъво аризаси қайтарилсин") rather than a score only.
- IPK has items FPK lacks (calculation of the sum, art. 149 item 6; registration as a legal entity or sole trader, art. 151 item 5; proof copies were sent to the parties, art. 155 item 5). These are good "trap" differences for exercises where the student must pick the court.

### Gaps
- Whether a **new Criminal Procedure Code** has been adopted by November 2026 that renumbers arts. 322–335 was not checked. The lex.uz header still shows the 1994 JPK.
- The repealed FPK art. 195 item 8 was not confirmed.
- The Labour Code articles cited in the Yurxizmat template (119 and 320) were not verified against the 2022 Labour Code.

## 3. e-sud / my.sud.uz e-filing and the state duty (davlat boji) rules

### Takeaway
State duty is set by the Law "Давлат божи тўғрисида" (ЎРҚ-600, 06.01.2020). For property claims it is **4% of claim value in civil courts** and **2% in economic courts**, with a minimum of 1 БҲМ in both. The current online filing portal is my.sud.uz, but it could not be reached here, so its form fields are unverified.

### Cited Findings
- **State Duty Law, annex "Давлат божи ставкаларининг миқдорлари"** — [lex.uz/docs/4680944](https://lex.uz/docs/4680944)
  - Civil courts (item 1):
    - а) a property claim pays 4% of claim value, at least 1 БҲМ;
    - б) a claim against decisions or actions of organisations or officials not arising from public-law relations pays 1 БҲМ;
    - в) divorce pays 2 БҲМ;
    - г) a repeat divorce pays 4 БҲМ;
    - е) a non-property or non-valued claim (housing lease change or termination, release of property from attachment, and so on) pays 2 БҲМ;
    - ж) special proceedings pay 1 БҲМ (no duty for establishing paternity, birth facts and similar);
    - з) an appeal, cassation or revision complaint pays 50% of the first-instance rate;
    - и) a copy of a document pays 2% of БҲМ per page.

    Notes: if property is divided in a divorce, duty is calculated on the claim value under "а". Small business entities pay 50% of the rate for sub-items е and и, as the note reads.
  - Economic courts (item 2): а) a property claim pays 2% of claim value, at least 1 БҲМ; б) a non-property claim pays 10 БҲМ.
  - Arts. 8 and 9 list exemptions in civil and economic courts. The law also lets shareholders in joint-stock company disputes defer payment.
- **БҲМ (base calculation amount):** 412,000 so'm, raised to **440,000 so'm from 1 September 2026** by Decree ПФ-115 of 23.06.2026. This is reported by buxgalter.uz, a secondary source; the decree text was not opened. — [buxgalter.uz](https://buxgalter.uz/uz/publish/doc/text215802_2026_yil_1_sentyabrdan_boshlab_qanday_bhm_va_mhtekmdan_foydalanamiz)
- **E-filing:**
  - The current Supreme Court portal is my.sud.uz. Users register in the "Shaxsiy kabinet", choose the court and the type of filing, enter the data, attach documents and send. This comes from a search-engine summary of gov.uz and buxgalter pages that were not opened, so it is **unverified**. — [gov.uz news](https://gov.uz/oz/xovostuman/news/view/246342)
  - Legal entities can also file an economic claim from the my.soliq.uz tax cabinet. — [buxgalter.uz](https://buxgalter.uz/oz/publish/doc/text158245_qanday_qilib_sudga_tugri_ofisdan_davo_arizasi_berish_mumkin)
  - A UNDP handbook describes the older E-SUD system (2016). — [UNDP E-SUD handbook](https://www.undp.org/node/134736), [UNDP court applications handbook](https://www.undp.org/sites/g/files/zskgke326/files/migration/uz/un_uzb_Handbook_Procedures_for_individual_court_applications.pdf)
- Under IPK art. 150 part 2, copies of the claim may be sent to the parties electronically through the information system. — [lex.uz/docs/3523891](https://lex.uz/docs/3523891)

### Inferences
- The duty calculator is easy to auto-check in LexSim:

  `duty = max(rate × claim_value, 1 БҲМ)`, where `rate` = 0.04 (civil) or 0.02 (economic).

  `claim_value` includes penalties (IPK 114). The student types the amount, and the system compares it with the correct figure. A wrong or missing payment proof leads to a return (IPK 155 item 6, FPK 195 item 7).
- Use a configurable БҲМ constant (440,000 so'm from 01.09.2026, unverified) so scenarios stay valid.

### Gaps
- The exact my.sud.uz form fields and steps were not obtained, because the site is unreachable from here (connection failed) and only a snippet was available.
- Whether there is an upper cap on duty, or other recent changes to the annex, was not checked beyond the text read (item 2 was cut off after "в").
- Postage fees (почта харажатлари) amounts were not found.

## 4. my.gov.uz forms for LexSim's DXM scenarios (archive-reference, pension-recalculation, written-complaint)

### Takeaway
Only partial information was found. The archive reference service and its administrative regulations exist, and pension recalculation is increasingly done proactively without an application. No exact form fields were retrieved.

### Cited Findings
- The archive agency lists the service "Ish haqi va ish stajini tasdiqlash haqida arxiv ma'lumotnomasi berish". The regulations for archive services were approved by Cabinet of Ministers resolution No. 597 of 23.09.2021, and an amendment (No. 393, 20.07.2026) appears on lex.uz. All of this is from search snippets. — [lex.uz/docs/5654569](https://www.lex.uz/acts/-5654569), [gov.uz/archive](https://gov.uz/oz/archive/general-menu/4558)
- The legacy portal page for the service "Mehnat faoliyatini tasdiqlash to'g'risidagi arxiv ma'lumotnomasini olish" — [oldmy.gov.uz/oz/service/223](https://oldmy.gov.uz/oz/service/223)
- Pension: news reports that some recalculations happen without an application (for example, when first-group disability is assigned), with a decision within 10 days. These are secondary sources. — [anhor.uz](https://anhor.uz/uzl/news/pensiya-xizmatlar-arizasiz), [daryo.uz](https://daryo.uz/p/718826/). The legacy pension service page is [oldmy.gov.uz/oz/service/975](https://oldmy.gov.uz/oz/service/975), and the related resolution is ПҚ-353 of 31.10.2023 ([lex.uz/docs/-6650097](https://lex.uz/docs/-6650097), relevance not verified).
- my.gov.uz loads, but service search by URL returned 404 when fetched directly. — [my.gov.uz](https://my.gov.uz)
- The written complaint in DXM falls under the Murojaatlar law, arts. 5, 6, 28 and 29 (see §2). — [lex.uz/docs/3336169](https://lex.uz/docs/3336169)

### Inferences
- Model the DXM forms on the Murojaatlar law art. 6 requisites plus service-specific fields. For archive-reference, plausible fields are the employer organisation, period of work, position, and the purpose (salary or length of service). Treat these field lists as **unverified design assumptions**.

### Gaps
- The exact field lists, document requirements, fees and processing times for the archive-reference and pension-recalculation applications on my.gov.uz were not retrieved. To get them, open the service cards in a browser that is logged in through OneID.

## 5. Design patterns for drafting assessment in legal-education tools

### Takeaway
No tool specific to drafting pleadings was found. The literature on rubric-based legal grading supports a rubric made of atomic, weighted items, combined with LLM or keyword checks for free text and a human or reference answer as an anchor.

### Cited Findings
- LexRubric: expert-written rubric items, "each rubric item specifies a concrete requirement that a response should satisfy or avoid", weighted from −10 to +10, which allows penalties for errors. — [arXiv 2606.09389](https://arxiv.org/pdf/2606.09389)
- With a sample solution plus a rubric, reasoning LLMs approximated expert grading of German public-law case solutions, reaching agreement up to 0.91 (quadratic weighted kappa). — [arXiv 2605.21076](https://arxiv.org/pdf/2605.21076)
- A survey of grading open-text legal answers with "rubric judges". — [arXiv 2610.19992](https://arxiv.org/pdf/2610.19992)
- A faculty member built a rubric for legal memos from their own past feedback. — [Northeastern](https://learning.northeastern.edu/ai-gallery-post-creating-a-grading-rubric-using-claude/)
- Learnosity offers AI-assisted scoring for law-school essays, with the human grader having final say. — [Learnosity](https://learnosity.com/ai-assisted-scoring-feedback/essay-with-sources/law-school-case-study)

### Inferences (proposed LexSim design, synthesised from the sources above)
1. **Realistic blank document**, not checkboxes. Show an A4-style editor with an empty header, title, body, prayer, attachments and signature. Structured slots (court, parties, ФИО, address, СТИР, claim value, duty, date) are typed by the student; there is no "pick the correct option".
2. **Two-layer checking:**
   - (a) Deterministic checks for enumerable requisites (IPK 149 / FPK 189 / JPK 324 / Murojaat art. 6). Examples:
     - the court name matches the scenario's correct jurisdiction;
     - the respondent's name and address match the case file;
     - the claim value equals the sum of demands plus penalty;
     - the duty equals the correct formula;
     - the attachment list includes the required items (duty receipt, proof copies were sent, талабнома if the contract requires it, registration certificate, ишончнома if signed by a representative);
     - the signature is present.
   - (b) Rubric or LLM checks for free text: the facts cover the key events (date, contract, breach); the legal norm is cited correctly; the demand is specific and enforceable ("ундириш сўрайман: X сўм"); demands are linked (not unrelated, IPK 155 item 8).
3. **Legal-consequence feedback.** Each failed check returns the real outcome and its article. For example, a missing proof of sending copies leads to "Даъво аризаси қайтарилсин (ИПК 155-м. 5-б.)", and a missing signature leads to return (IPK 155 item 2) or, after acceptance, leaving without consideration (IPK 107 item 3). The student can then fix the claim and refile, mirroring the rule that a return does not block refiling (IPK 155, last part).
4. **Common-defect bank** for distractor scenarios, taken directly from IPK 155, FPK 195 and IPK 107:
   - wrong court;
   - unsigned claim, or signed by an unauthorised representative;
   - no duty paid, or the wrong amount;
   - copies not sent to the parties;
   - талабнома not sent when the contract requires it;
   - unrelated demands joined;
   - civil and economic demands mixed;
   - no calculation of the sum;
   - anonymous crime report.
5. **Time-limit layer.** IPK 152 (5 days to decide acceptance), FPK 192 (10 days), JPK 329 (10 days, extendable to 1 month), Murojaatlar art. 28 (15 days, extendable to 1 month). The simulator can advance the clock and produce the authority's response.
6. **Templates as optional scaffolding**, in the Yurxizmat style: the student gets a skeleton only at an easier difficulty level, or loses points for using it.

### Gaps
- No published study of automated assessment specifically for pleadings or claims, or of Uzbek legal-education drafting tools, was found.
