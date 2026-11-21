# Rhetorical, Psychological and Negotiation Pressure Techniques in Court and Settlement, and How Judges Test Advocates (technique catalog for the LexSim AI opponent and AI judge)

Scope note: the research evidence below is cited. The **technique cards** (Uzbek terms, example lines, signals, counters, student mistakes) are design material for the simulator. Each card rests on the cited findings, but the wording, the example lines and the Uzbek terms are my own suggestions, not quotations, and they are labelled as inferences. Running example used throughout: **"Ijara qarzi + neustoyka" (rent debt plus contractual penalty)**. The landlord (Plaintiff, "Da'vogar") claims 120 mln so'm in rent arrears plus 0.5%/day penalty, about 180 mln so'm in penalty. The tenant (Defendant, "Javobgar") argues partial payment, defects in the premises, and that the penalty is disproportionate. A secondary example is a supply contract ("yetkazib berish shartnomasi") with late delivery.

Tool note: pon.harvard.edu and pubmed could not be fetched (domain blocked), so PON claims rely on search-result snippets of PON pages. The Englich (2006) review was read in full from the PDF.

---

## Key Question 1: Courtroom persuasion techniques (anchoring, primacy/recency, framing, contrast, scarcity/deadline, concession-then-pivot, strategic silence, status/confidence, fairness appeals, labelling, narrative, repetition)

### Takeaway
The strongest research base is for **numeric anchoring of legal decision-makers**. Experienced judges assimilate their decisions toward numbers they know are irrelevant (even dice rolls), expertise does not protect them, and the opposing advocate's counter-number is itself pulled toward the first anchor. Moderately strong evidence exists for **stealing thunder** (disclosing your own weakness first raises credibility), **story coherence** (the story model), **repetition-induced truth** and **primacy/recency** (direction depends on timing). In LexSim, the AI opponent should use these and the AI judge should be subtly susceptible to them, so students learn the counters: re-anchoring with a justified number, consider-the-opposite, and a coherent counter-story.

### Cited Findings

**Anchoring of judges (core evidence)**
- Englich, Mussweiler & Strack (2006), "Playing Dice with Criminal Sentences," *Personality and Social Psychology Bulletin* 32:188–200. Legal professionals were influenced by sentencing demands even when the demands were randomly determined, including by throwing dice, and "expertise and experience did not reduce this effect." — [PubMed](https://pubmed.ncbi.nlm.nih.gov/16382081/); [LBS listing](https://www.london.edu/faculty-and-research/academic-research/p/playing-dice-with-criminal-sentences-the--influence-of-irrelevant)
- Study design (from Englich's own 2006 review): practising judges and prosecutors with an **average of 13 years' experience**, a shoplifting case, and a prosecutor demand that was explicitly random, either **3 vs 9 months probation**. Higher demand produced higher sentences. In the dice study the dice were **loaded** to land on 3 or 9. 79% of participants said the dice demand was irrelevant to their decision, yet the anchoring effect persisted. — [Englich 2006, "Blind or Biased? Justitia's Susceptibility to Anchoring Effects in the Courtroom," Law & Policy 28(4)](https://www.hf.uni-koeln.de/data/dppsenglich/File/PDFSStudien/LawPol28.pdf)
- Realistic anchors work too. A journalist asking judges whether the sentence would be "higher or lower than one year" vs "three years" anchored decisions, and so did a courtroom heckler shouting "Give him five years!" vs "Set him free!" (Englich 2005). — [Englich 2006](https://www.hf.uni-koeln.de/data/dppsenglich/File/PDFSStudien/LawPol28.pdf)
- **The opposing advocate gets anchored too.** Defence attorneys facing a 34-month (vs 12-month) prosecution demand recommended higher sentences themselves. None of them reported adapting to the prosecutor deliberately. Mediation analysis showed that "it is the biased defense attorney's demand that most strongly pulls the final sentencing decision towards the prosecutor's sentencing demand." — [Englich 2006](https://www.hf.uni-koeln.de/data/dppsenglich/File/PDFSStudien/LawPol28.pdf)
- **Confidence does not equal immunity.** Experienced criminal-law judges felt much more certain than inexperienced ones, but "certainty and bias were not correlated." — [Englich 2006](https://www.hf.uni-koeln.de/data/dppsenglich/File/PDFSStudien/LawPol28.pdf)
- **Order matters.** When the defence's demand came first, there was "no anchoring effect for the prosecution". Argument quality did not offset the anchor: judges recognised strong vs weak defence arguments, but the strength of the arguments did not change the sentences (Englich & Rost 2006). "The prosecutor's influence… is exerted much more by the sentencing demand itself than by its supporting arguments." — [Englich 2006](https://www.hf.uni-koeln.de/data/dppsenglich/File/PDFSStudien/LawPol28.pdf)
- **Civil damages and judges.** In "Inside the Judicial Mind" (Guthrie, Rachlinski & Wistrich, 86 Cornell L. Rev. 777, 2001), 167 federal magistrate judges were tested. They were "just as susceptible as other experts and laypersons" to anchoring, but less susceptible to framing. In the damages problem, an irrelevant anchor (a frivolous motion to dismiss for failing the $75,000 jurisdictional minimum) gave a mean award of **$882,000 vs $1.25 million** with no anchor. — [Cornell scholarship](https://scholarship.law.cornell.edu/facpub/814/); [Vanderbilt IR](https://ir.vanderbilt.edu/handle/1803/5624). A later follow-up reported awards **29% lower** after the same jurisdictional-minimum anchor. — summarised via [Volokh/Reason](https://reason.com/volokh/2021/06/09/the-bizarre-effects-of-anchoring/) (secondary)
- **Debiasing ("consider the opposite").** Mussweiler, Strack & Pfeiffer (2000, PSPB 26(9):1142–1150) found that generating reasons why the anchor is inappropriate reduces anchoring, including among car experts. (Note: LBS lists a conflicting volume/page, so verify.) — [LBS listing](https://www.london.edu/faculty-and-research/academic-research/o/overcoming-the-inevitable-anchoring-effect--considering-the-opposi)
- Mechanism (selective accessibility): judges test whether the anchor is correct, which makes anchor-consistent information more accessible. Experts may find more such information, not less. — [Englich 2006](https://www.hf.uni-koeln.de/data/dppsenglich/File/PDFSStudien/LawPol28.pdf)

**Primacy and recency**
- Lund (1925) found that whichever side was read first was more persuasive ("law of primacy"). Cromwell (1950) found recency, and current consensus is that both occur. — [Wikipedia: Law of primacy in persuasion](https://en.wikipedia.org/wiki/Law_of_primacy_in_persuasion) (secondary)
- Miller & Campbell (1959) used recorded trial material. A delay between the two messages favoured **recency**, and a delay after both messages (before judgment) favoured **primacy**. — [changingminds.org summary](https://changingminds.org/explanations/theories/recency_effect.htm) (secondary; verify against the original)
- Engel, Timme & Glöckner (2020) mock-trial study: an early leaning did not strengthen over the trial. Summary: "primacy and coherence still count – they just don't control… that last word [recency] may be where the real courtroom power lies." People high in need for cognition and people familiar with the topic show more primacy. — [Temple Law, "Brain Lessons: Order as a Form of Persuasion"](https://law.temple.edu/aer/2022/05/02/brain-lessons-order-as-a-form-of-persuasion/); [Stetson PDF](https://www2.stetson.edu/advocacy-resource-center/wp-content/uploads/2022/05/ORDER-AS-A-FORM-OF-PERSUASION-May-2022.pdf)

**Narrative and story model**
- Pennington & Hastie's story model: decision-makers build a causal story of the evidence and then match it to verdict categories. A story with greater **coverage** (it explains more of the evidence) and **coherence** is more likely to be accepted. Evidence presented in story order vs issue order influenced verdicts (Pennington & Hastie 1992, JPSP 62(2):189–206). — [Open University](https://www.open.edu/openlearn/society-politics-law/law/jury-decision-making-whats-the-story); [Hastie & Pennington, Colorado L. Rev.](https://lawreview.colorado.edu/wp-content/uploads/2026/02/Hastie-Pennington.pdf); [Cambridge, Inside the Juror](https://www.cambridge.org/core/books/inside-the-juror/story-model-for-juror-decision-making/61051A1D12C7F7FA58DD4424EA7D03F3)
- Caveat: the story model was developed for jurors. Its application to professional economic-court judges is an inference, not something the sources establish.

**Stealing thunder (concede the weakness first)**
- Williams, Bourgeois & Croyle (1993), *Law and Human Behavior* 17:597–609, ran two mock trials (one criminal, one civil asbestos/smoking). Revealing the negative information oneself "significantly reduced the impact of negative information", and path analysis showed the effect worked **through enhanced credibility**. — [OJP abstract](https://ojp.gov/ncjrs/virtual-library/abstracts/effects-stealing-thunder-criminal-and-civil-trials); [Purdue News](https://www.purdue.edu/uns/html4ever/2005/050401.Williams.law.html)
- Timing of the disclosure within a trial did not seem to moderate the effect. — [Cardiff ORCA paper](https://orca.cardiff.ac.uk/174975/1/Disclosure%20and%20identification%20information%20increase%20the%20benefits%20of%20stealing%20thunder.pdf)

**Repetition (illusory truth)**
- Hasher, Goldstein & Toppino (1977): repeated statements were rated more true. The Dechêne et al. (2010) meta-analysis (PSPR 14:238–257) confirmed the "truth effect". The dominant mechanism is **processing fluency**. The 2010 meta-analysis is dated and its no-delay-moderation finding has been challenged. — [Springer, Cognitive Research 2021](https://link.springer.com/article/10.1186/s41235-021-00301-5); [PMC8116821](https://pmc.ncbi.nlm.nih.gov/articles/PMC8116821)
- No source found that tests a specific "rule of three" in courts. It is practitioner lore (see Gaps).

**Framing (loss vs gain) in litigation**
- Rachlinski (1996), "Gains, Losses, and the Psychology of Litigation," 70 S. Cal. L. Rev. 113: litigants' risk choices depend on whether outcomes are framed as gains or losses. Korobkin & Guthrie predict settlement rates depend on whether a settlement offer is perceived as a gain or a loss. — [Cornell scholarship](https://scholarship.law.cornell.edu/facpub/795); [Judgment and Decision Making 2008](https://dlab.sauder.ubc.ca/sjdm/journal/8610/jdm8610.html)
- Judges were less susceptible to framing than other decision-makers in Guthrie et al. (2001). — [Vanderbilt IR](https://ir.vanderbilt.edu/handle/1803/5624)

**Contrast and reciprocal concession (door in the face)**
- Cialdini et al. (1975, JPSP 31:206–215): after refusing a large request (two years of volunteering), **50%** agreed to a smaller one (a zoo trip) vs **17%** who heard only the small request. The mechanism is a perceived concession that creates a reciprocity obligation, plus contrast. A direct replication appeared in 2021. — [Wikipedia: Door-in-the-face](https://en.wikipedia.com/wiki/Door-in-the-face_technique); [EBSCO](https://ebsco.com/research-starters/psychology/door-face-technique)
- PON warns that the technique can backfire if the counterpart senses manipulation. — [PON](https://www.pon.harvard.edu/daily/dispute-resolution/the-door-in-the-face-technique-will-it-backfire-nb/)

**Ethical boundary (court)**
- BSB Core Duty 1, the duty to the court, overrides other duties. "You must not knowingly or recklessly mislead or attempt to mislead the court". rC6 extends this to submissions and to questions that suggest facts to witnesses. The duty to the client is subject to the duty to the court (rC4). — [BSB Handbook](https://www.barstandardsboard.org.uk/the-bsb-handbook.html?q=mislead); [BSB core duties](https://www.barstandardsboard.org.uk/for-barristers/compliance-with-your-obligations/the-core-duties.html)
- ABA Model Rule 4.1 "puffing" protection does not extend to statements to a tribunal, which fall under Rule 3.3 (candour). — [UT CLE materials](https://utcle.org/ecourses/OC7931/get-asset-file/asset_id/43512) (secondary)

### Inferences

#### Technique cards: courtroom (for the AI opponent; the student must recognise and counter)

**C1. Numeric anchoring — "Raqamli langar" (langar effekti)**
- *Mechanism:* the first concrete number becomes the judge's reference point. Selective accessibility means evaluating it makes supporting facts salient (Englich 2006).
- *Example lines:* "Your Honour, by any reasonable measure the tenant's damage to our client is at least 300 million so'm. We claim only 120 million in debt and 180 million in penalty." Or, from the supplier side: "Market practice for such delays is 1% per day. Our contract says 0.5%, which is already modest."
- *Stage:* opening explanations (first statement of claim amount) and closing.
- *Signals:* a number stated early and confidently with no calculation behind it. Rhetorical "at least" or "minimum". Comparison with an inflated "real" figure.
- *Counter:* (1) do not counter-propose a number inside the opponent's frame before defusing it. (2) Name the anchor ("the figure of 300 million is unsupported by the case file"). (3) Re-anchor with your own calculated figure tied to objective criteria (actual paid amounts, the statutory/court-reduced penalty, the key-rate comparison). (4) Use consider-the-opposite: give the judge reasons why the anchor is wrong (Mussweiler et al. 2000). If procedure allows, state your number first (Englich & Rost order effect).
- *Student mistakes:* "splitting the difference" (anchored counter-demand, as the defence attorneys were in Englich 2005). Arguing only about the quality of arguments while leaving the number unchallenged (argument quality did not offset the anchor).
- *Ethical boundary:* a claimed amount must have a good-faith basis in law and fact. An invented number presented as fact to the court is misleading the court.

**C2. Primacy and recency — "Birinchi va oxirgi taassurot effekti"**
- *Mechanism:* first-heard and last-heard material is weighted more, depending on delays (Miller & Campbell 1959; Engel et al. 2020).
- *Example:* the opponent opens with "This is a case about a tenant who stopped paying for 8 months and still uses the premises" and closes with the same sentence.
- *Stage:* opening explanations and closing (prения).
- *Signals:* a rehearsed "headline" sentence at the start and end.
- *Counter:* open your own explanations with your theme, not with a rebuttal of theirs. Use your last word to restate your one-sentence theory plus your number.
- *Mistake:* spending the opening reacting point by point to the opponent, which hands them the frame.

**C3. Framing (loss vs gain) — "Ramkalash: yo'qotish/foyda"**
- *Mechanism:* the same outcome feels different when framed as a loss vs a gain (Rachlinski 1996). Judges are somewhat resistant (Guthrie et al. 2001), but parties in settlement are not.
- *Example (to the court):* "Every day without payment, our client loses 650,000 so'm." *(To the opposing party in settlement):* "If you refuse, you risk losing 300 million. Settling at 150 avoids that loss."
- *Stage:* closing and settlement.
- *Counter:* reframe the same numbers as a gain ("the claimant's own documents show 40 million already received") and return to expected-value arithmetic.

**C4. Concession-then-pivot / stealing thunder — "Kichik yon berish va burilish" / "Zaif nuqtani oldindan ochish"**
- *Mechanism:* volunteering one's own weakness raises perceived credibility (Williams et al. 1993) and mirrors reciprocal-concession dynamics (Cialdini 1975).
- *Example:* "We accept that the claimant notified us of the defect only once and orally. But that is exactly why the penalty clause, not the defect, is the real issue." Or from the claimant: "We concede that 40 million was paid in March. Even so, 120 million remains, and the penalty accrues on it."
- *Stage:* opening explanations and evidence.
- *Signals:* "We will be honest with the court…" followed by a minor concession, then a large claim.
- *Counter:* accept the concession formally (ask that it be recorded in the minutes), then separate it from the pivot ("the concession of the payment confirms our calculation; it does not establish the penalty"). The student can also steal their own thunder first.
- *Mistake:* treating the concession as a win and relaxing, or ignoring it, and so losing the chance to lock it in.

**C5. Strategic silence and pacing — "Strategik sukut va sur'at"**
- *Mechanism:* pauses after key points and after the opponent's answer create pressure to fill silence and make the point salient. (No legal-specific study found, so this is an inference.)
- *Example:* after the student answers, the AI opponent pauses, then: "So the tenant admits it used the premises during all eight months?"
- *Counter:* answer once and stop. Do not over-explain into the silence.

**C6. Confidence and status display — "Ishonch va maqom namoyishi"**
- *Mechanism:* certainty cues are read as accuracy cues. Englich shows confidence is uncorrelated with correctness, even in judges.
- *Example:* "Any experienced commercial lawyer knows that courts never reduce a contractual penalty agreed by business entities."
- *Signals:* absolute words ("never", "any lawyer knows"), appeals to seniority, no citation.
- *Counter:* calmly ask for the norm or authority. Cite the legal basis for penalty reduction. (Verify the exact Uzbek Civil Code article on court reduction of neustoyka before use; I did not verify it in this research.)
- *Boundary:* misstating the law to the court is misleading the court (BSB rC3; ABA 3.3).

**C7. Fairness / good-faith appeal — "Adolat va insofga murojaat (vijdonlilik)"**
- *Example:* "Our client kept its promise; it is only fair that the tenant keeps its promise."
- *Counter:* agree with the principle and turn it around ("fairness is exactly why a penalty of 150% of the debt is disproportionate").

**C8. Labelling the opponent's argument — "Yorliq yopishtirish"**
- *Example:* "The defendant's 'defects' argument is a classic delay tactic."
- *Counter:* do not argue with the label. Restate your argument neutrally with evidence (inspection act, correspondence) and ask the court to assess the evidence.
- *Boundary:* personal attacks or insults against the opponent cross into improper conduct.

**C9. Theme and story — "Hikoya orqali ishontirish (syujet)"**
- *Mechanism:* the story with the best coverage and coherence wins (Pennington & Hastie).
- *Counter:* the student must offer an alternative causal story that explains all key documents (payments, defect letters, the penalty clause), not just attack the opponent's story.

**C10. Repetition / rule of three — "Takrorlash va uchlik qoidasi"**
- *Mechanism:* fluency produces perceived truth (Hasher 1977; Dechêne 2010).
- *Example:* "Eight months of use. Eight months of silence. Eight months without payment."
- *Counter:* do not repeat the opponent's slogan, even to deny it. Substitute your own phrase.

**C11. Contrast / door-in-the-face — "Kontrast va rad-keyin-chekinish"**
- *Example:* first claim the full 180 million penalty, then "as a gesture, we are ready to accept 90 million."
- *Counter:* evaluate the second number on its own merits against your BATNA and the likely court reduction, not against the first number.

---

## Key Question 2: Negotiation and settlement pressure tactics, and the PON-recommended counters

### Takeaway
First offers reliably anchor outcomes (Galinsky & Mussweiler 2001). The antidote is focusing on your own alternatives, the opponent's reservation price, or your own target, all of which negated the anchor effect. PON's general counter-playbook is: recognise the tactic, name it, don't bid against yourself, test claims of limited authority, ignore ultimatums and respond to substance, and re-anchor with objectively justified numbers. Puffing about value or settlement intentions is tolerated under ABA Model Rule 4.1 cmt. [2]. Invented facts, such as fake rival offers, false statements about evidence or false authority limits on material matters, are not.

### Cited Findings
- **First offers as anchors.** Galinsky & Mussweiler (2001), JPSP 81(4):657–669, three experiments. The first offer predicted outcomes face to face and by email. **Focusing on alternatives, the opponent's reservation price, or one's own target negated the first-offer effect.** — [Kellogg](https://www.kellogg.northwestern.edu/faculty/research/detail/2001/first-offers-as-anchors-the-role-of-perspective-taking); [LBS](https://www.london.edu/faculty-and-research/academic-research/f/first-offers-as-anchors-the-role-of-perspective-taking-and-negotiator-focus)
- When the seller makes the first offer the final price tends to be higher, and vice versa. — [HBS Working Knowledge (Galinsky)](https://hbswk.hbs.edu/archive/when-to-make-the-first-offer-in-negotiations). A reported anchor-outcome correlation of about .85 comes from a secondary review; I did not verify it in the primary text.
- Extreme anchors can backfire. An offer extreme enough to offend can end talks, and the counteroffer acts as a weaker anchor (the "anchor zone"). — [PON: what is anchoring](https://www.pon.harvard.edu/uncategorized/what-is-anchoring-in-negotiation); [Group Decision & Negotiation 2023](https://link.springer.com/article/10.1007/s10726-023-09813-5); [JDM: "Winning a battle but losing the war"](https://dlab.sauder.ubc.ca/sjdm/journal/12/121025/jdm121025.html)
- **PON counter to an aggressive anchor:** don't counter before defusing it, because an early counter implies the anchor is within the bargaining zone. Pause, re-anchor with a data-supported number, justify it with objective criteria, name the anchor if needed, or ignore it and table your intended offer. — [PON: Dealmaking and the anchoring effect](https://pon.harvard.edu/daily/dealmaking-daily/dealmaking-grappling-with-anchors-in-negotiation); [PON: Price anchoring 101](https://pon.harvard.edu/daily/negotiation-skills-daily/price-anchoring-101/)
- **PON "10 hardball tactics"** list (seen via snippets): extreme demands, commitment tactics/limited authority, take-it-or-leave-it, trying to make you flinch, good cop/bad cop, nibbling (small last-minute demands) and others. — [PON 10 hard-bargaining tactics](https://www.pon.harvard.edu/daily/batna/10-hard-bargaining-tactics); [AMP version](https://www.pon.harvard.edu/daily/batna/10-hardball-tactics-in-negotiation/?amp)
  - *Limited authority / "my hands are tied":* check whether the commitment tactic is genuine. If it is, negotiate with someone with greater authority. — same source
  - *Take-it-or-leave-it:* offers should rarely be non-negotiable. Ignore the framing, focus on content, make a counteroffer meeting both sides' needs. "Don't bid against yourself by reducing your demands." — same source. Ultimatums "ratchet up the odds of competition, impasse, and capitulation". Propose cross-issue trade-offs and insist on reciprocal concessions. — [PON Negotiation Briefings May 2018](https://www.pon.harvard.edu/publication/negotiation-briefings/may-2018/)
  - *Good cop/bad cop:* recognise that the two are coordinating. Sutton & Rafaeli (1991) describe sequential, simultaneous and single-negotiator variants. The counter is to **name the dynamic aloud** (attributed to Shell). — [PON Good cop bad cop](https://www.pon.harvard.edu/daily/batna/the-good-cop-bad-cop-negotiation-strategy/)
  - Hardball tends to trigger reciprocal hardball because negotiators mirror each other. — [PON hardball tag](https://www.pon.harvard.edu/tag/hardball-tactics/)
  - *Flinching:* listed as a tactic. **No PON-specific counter was retrieved** (see Gaps).
- **Ethics of negotiation statements.** ABA Model Rule 4.1 cmt. [2]: "estimates of price or value placed on the subject of a transaction and a party's intentions as to an acceptable settlement of a claim" ordinarily are not material facts. ABA Formal Op. 06-439 defines puffing as statements on which parties would not ordinarily be expected justifiably to rely, and applies it to caucused mediation too. — [ABA Ethics 2000 Rule 4.1 report](https://www.americanbar.org/groups/professional_responsibility/policy/ethics_2000_commission/e2k_rule41rem/); [ABA Litigation: negotiation, zealous advocacy, limits of deception](https://www.americanbar.org/groups/litigation/resources/newsletters/commercial-business/negotiation-zealous-advocacy-limits-of-deception/); [Cal. Bar Formal Op. 2015-194, puffing in negotiations](https://calbar.ca.gov/Portals/0/documents/ethics/Opinions/2015-194%20(12-0007)%20Puffing%20in%20Negotiations%20FINAL%2012-29-15.pdf)
  - Misstating the existence or size of other offers is a statement of fact that cmt. 2 does not excuse when material. — [PLI Patent Law Center](https://patentlawcenter.pli.edu/?p=4482) (commentary)
  - Some states, such as Virginia, are stricter than the ABA. — [UT CLE](https://utcle.org/ecourses/OC7931/get-asset-file/asset_id/43512)
- PON on deception: be prepared for dirty tricks, and verify claims. — [PON: Unethical negotiation tactics](https://www.pon.harvard.edu/daily/negotiation-skills-daily/negotiation-skills-tips-dealing-with-deception-at-the-bargaining-table/?amp)

### Inferences

#### Technique cards: settlement ("kelishuv bitimi" talks)

**N1. Extreme first offer — "Haddan tashqari birinchi taklif"**
- *Example (claimant):* "Our client will sign a settlement at 290 million, full debt and 95% of the penalty, payable in 10 days."
- *Counter:* prepare your BATNA (the likely court outcome with penalty reduction, costs, time) and your target before the meeting. Defuse the offer ("that figure ignores the 40 million paid and the court's power to reduce penalties"), then re-anchor (for example, 80 million debt plus 10 million penalty over 3 months).
- *Mistake:* immediately offering "half". *Boundary:* aggressive but lawful (puffing about value).

**N2. Good cop / bad cop — "Yumshoq va qattiq juftlik"**
- *Example:* the AI director says "We'll see you in court and claim everything". The AI lawyer says "Let me see if I can persuade him… if you can go to 200 today."
- *Counter:* name it ("I see we have two roles here; let's look at the numbers on their merits"). Treat both as one party.

**N3. Nibbling — "Oxirgi daqiqa qo'shimcha talab (chimchilash)"**
- *Example:* after agreement on 150 million: "Oh, and of course the tenant also covers our legal costs and the state fee."
- *Counter:* make every add-on conditional on a reciprocal concession ("then the payment term becomes 6 months"), or reopen the whole package. Use a written term sheet.

**N4. Take-it-or-leave-it / ultimatum — "Yo shu, yo hech narsa"**
- *Counter (PON):* ignore the framing, respond to substance, propose cross-issue trades (instalments, waiver of penalty in exchange for prompt payment of the debt). Don't bid against yourself.

**N5. False or artificial deadline — "Soxta muddat bosimi"**
- *Example:* "This offer expires when the hearing resumes in 20 minutes."
- *Counter:* test it ("What specifically changes at that time?"). Remember the court-process alternative. Ask the court for a recess for settlement if needed.
- *Boundary:* a real deadline is lawful. A false factual claim (for example "the court has already decided") is deception.

**N6. Limited authority — "Cheklangan vakolat"**
- *Example:* "I am authorised only up to 220 million; the director won't approve less."
- *Counter (PON):* verify it. Ask who has authority and whether they can join. Check the power of attorney ("ishonchnoma") scope.
- *Boundary:* lying about authority on a material matter is a false statement of fact. A posture about settlement intentions is puffing.

**N7. Flinch — "Hayratlanish reaksiyasi (flinch)"**
- *Example:* "Ninety million?! That's an insult; my client will laugh at me."
- *Counter (inference; no PON counter found):* do not immediately soften. Silence, then justify your number with criteria.

**N8. Contrast / rejection-then-retreat — "Rad etib-keyin chekinish"**
- See C11. The counter is comparing against the BATNA, not against the first demand.

**N9. Deception that crosses the line (the AI opponent must not do this; the AI judge or debrief should flag it)**
- Fake competing offers, nonexistent documents ("we have a witness who saw the defects repaired"), misstating the contents of the contract, threats of criminal complaint to gain civil leverage. The last item is a common ethics prohibition in US states. It was not verified in this research, so treat it as unverified.

---

## Key Question 3: How judges test advocates, and what good responses look like

### Takeaway
Judges and moot guides converge on one model answer: listen to the actual question; answer it directly first (yes/no, then explain); engage with the hypothetical as framed, then distinguish it; know in advance what you can concede and never concede what you cannot afford to; then segue back to your theme. Evasion is the cardinal sin. Some practitioner sources disagree on how freely to concede.

### Cited Findings
- Aldisert, *Winning on Appeal* (1996 ed., p. 332), as cited: judges detect evasive answers and dislike them, so do not postpone answers. — [Vail, Journal of Appellate Practice & Process](https://journals.librarypublishing.arizona.edu/appellate/article/2614/galley/2737/download)
- Evading questions from the bench is "an almost certain way to anger the appellate court." — [Legal Intelligencer, "How not to foul up your appeal, part 3"](https://law.com/thelegalintelligencer/2019/03/11/how-not-to-foul-up-your-appeal-part-3-the-appellate-oral-argument)
- Counsel may be rebuked for failing to respond promptly and directly. — [Volokh](https://volokh.com/?p=16707)
- **Yes/no sequencing:** (1) "yes" or "no"; (2) the explanation needed to show why the answer supports or does not undermine your position; (3) a segue back to your argument. — [ABA Appellate Issues, "Top tips for top-notch oral argument answers" (2022)](https://www.americanbar.org/groups/judicial/publications/appellate_issues/2022/winter/top-tips-for-top-notch-oral-argument-answers/) (snippet; the page returned 403 when fetched); [Duke moot court tips](https://law.duke.edu/life/mootcourt/tips)
- **Hypotheticals:** don't fight the hypothetical if you can avoid it, so long as you don't concede your case. Answer it as framed, then compare or contrast it with the case, focusing on principles and distinctions. — [Minnesota Bench & Bar, "The art of the answer" (2024)](https://mnbar.org/resources/publications/bench-bar/2024/05/20/the-art-of-the-answer-how-to-respond-effectively-to-questions-at-oral-argument); [Above the Law](https://abovethelaw.com/2017/11/oral-advocacy-one-weird-trick-to-help-you-answer-questions/)
- **Concessions:** know in advance what to concede, and never give up what you can't afford to lose. — [Georgetown, "May It Please the Court"](https://www.law.georgetown.edu/wp-content/uploads/2019/08/May-It-Please-the-Court-Preparing-for-Competition-and-Advanced-Oral-Argument.pdf). A contrary view (Lavine) holds that concessions can make you look weak. — [J. App. Prac. & Process](https://journals.librarypublishing.arizona.edu/appellate/article/2666/galley/2789/download)
- Chief Justice Roberts, reflecting on his advocacy, said he would "listen a little more carefully to what the questions are" (reported secondhand). — [Minnesota Bench & Bar](https://mnbar.org/resources/publications/bench-bar/2024/05/20/the-art-of-the-answer-how-to-respond-effectively-to-questions-at-oral-argument)
- Questions are an opportunity to learn what concerns the judge, so welcome them. — [Carlton Fields](https://www.carltonfields.com/insights/publications/as-an-advocate-welcome-questions-from-the-bench); [ABA, questions to ask before you answer (2025)](https://www.americanbar.org/groups/judicial/resources/appellate-issues/2025-winter/questions-ask-before-answer-during-appellate-oral-argument)

### Inferences

#### Technique cards: AI judge tests ("Sudyaning sinov usullari")

**J1. Socratic chain — "Sokratcha so'roq zanjiri"**
- *Example:* "Is the penalty a measure of liability? Must liability be proportionate to the harm? Is 180 million proportionate to an 8-month delay on 120 million?"
- *Good response:* answer each link honestly. Spot the link where you must disagree and say so explicitly with a reason.
- *Mistake:* agreeing to every step and then being trapped.

**J2. Hypothetical — "Faraziy savol"**
- *Example:* "Suppose the tenant had paid everything one day late. Would you still claim a full 0.5% penalty for that day? And if it were 0.5% for 1,000 days?"
- *Good response:* answer as framed ("Yes, the clause would apply"), then distinguish ("but here the debtor ignored three written demands") and return to the theme.
- *Mistake:* "That's not our case, Your Honour" (fighting the hypothetical).

**J3. Abrupt interruption — "Keskin to'xtatish"**
- *Good response:* stop immediately, answer the new question, and bridge back with a short phrase ("…which brings me back to the calculation"). Don't say "I'll come to that later" unless you really will, very shortly.

**J4. Time pressure — "Vaqt bosimi"**
- *Example:* "You have one minute. What is your single strongest point?"
- *Good response:* a prepared one-sentence theory of the case plus the number.

**J5. "Give me your single best authority" — "Eng kuchli huquqiy asos"**
- *Good response:* one norm or one ruling, its exact provision, and why it controls. Don't list five.

**J6. Testing concessions — "Tan olishni sinash"**
- *Example:* "So you agree the tenant used the premises in all eight months?"
- *Good response:* concede what the evidence makes undeniable (credibility, per Williams 1993) and refuse a concession that is fatal, with a reason. Pre-plan the "concede / never concede" list (Georgetown).

**J7. Challenging the anchor (AI judge as a debiasing model)**
- The judge asks the claimant: "How exactly was 300 million calculated?" This models consider-the-opposite (Mussweiler 2000), and students learn to prompt it themselves.

**J8. "I don't know" handling**
- *Good response:* admit it and offer to provide it in writing, rather than guess. Guessing risks misleading the court (BSB rC3).

#### Simulator design inferences
- The AI judge could carry a small, configurable anchoring susceptibility (for example, the award drifts toward the first unrebutted number). This reflects the evidence that expertise does not remove anchoring, and the effect drops when the student defuses or re-anchors with justification or speaks first (Englich & Rost order effect).
- Debrief scoring could check whether the student (a) named the tactic, (b) avoided an anchored counter-number, (c) answered judge questions with direct answer, explanation, then segue, (d) made only safe concessions.
- The AI opponent should be bounded: puffing about value and settlement intentions is allowed, while false statements of material fact, misleading the court, insults and threats are disallowed and flagged.

### Gaps
- **Uzbek-specific sources not found.** I found no text of the Uzbek Rules of Professional Ethics of Advocates (the lex.uz decree UP-5441 of 12 May 2018 refers to them, but the text was not retrieved — [lex.uz](https://lex.uz/acts/3731058)). The Ministry of Justice PDF I retrieved turned out to be the ethics rules for MoJ employees (Order No. 43-um, 24 Feb 2020), not advocates, so it is not relevant to courtroom conduct. The exact Uzbek Civil Code article on court reduction of neustoyka, and the Economic Procedural Code provisions on settlement agreements and mediation, were not verified. They should be checked on lex.uz before being cited in LexSim.
- **Not retrieved:** PON's specific counter to flinching, and full PON article texts (the domain was blocked, so snippets only).
- **No empirical source found** for the "rule of three", strategic silence, or status/confidence displays in courtroom advocacy specifically. These cards are based on practitioner convention and general psychology.
- The Galinsky & Mussweiler effect sizes were not verified from the primary text.
- The Miller & Campbell (1959) details come from a secondary summary only.
- **Not found:** UK judges' talks (for example Lord Neuberger) and Jessup/Vis Moot judging guides. US appellate guidance stands in for them.
- The Mussweiler, Strack & Pfeiffer (2000) volume and page details conflict between sources.
- The evidence applies to criminal sentencing, US civil damages and juries. Transfer to professional Uzbek economic-court judges is an inference.
