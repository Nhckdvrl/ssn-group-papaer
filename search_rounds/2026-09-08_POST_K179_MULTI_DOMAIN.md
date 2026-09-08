# Multi-domain search pass after K179 — 2026-09-08

**Target:** NAACL Main, aligned to ACL / EMNLP / NAACL Main and award-level paper identity.

**Authoritative state entering this pass:** Approved Mainline = NONE; PILOT-AUTHORIZED = L03, L04; killed ledger through K179; next unused kill ID = K180.

This pass did **not** modify selection doctrine. It searched multiple mother domains and did not lower the bar to fill a quota.

## 1. Reconciliation: the three rough leads in the handoff are already closed

The repository is ahead of the handoff text:

- **K177 — Evidence Aggregation Rule under Conflicting Studies — KILL CURRENT FORM.** ConflictingQA / conflict-aware evidence synthesis already owns the broader parent; study-level sample-size/precision/quality manipulations are currently an extension cell.
- **K178 — Learned Distribution vs Decoding Policy for Repeated-Sequence Statistics — KILL CURRENT FORM.** ACL 2026 repeated-sequence statistics + existing local/global decoding-distribution work make the attribution sweep an obvious follow-up rather than a new paper identity.
- **K179 — Label Definitions vs Examples in New Category Learning — KILL CURRENT FORM.** EMNLP 2025 label-definition receptivity + mature ICL demonstration work already bracket the decomposition.

Therefore **next unused kill ID remains K180**.

## 2. Fresh tracks searched and rapidly rejected / not promoted

### A. Explicit structure still load-bearing in LLM structured prediction

RQ sketch: Is explicit global structural inference still scientifically necessary once an LLM can directly generate a structured output?

**Do not promote.** EACL 2026 *Mapping the Course for Prompt-based Structured Prediction* directly combines LLM prompting with combinatorial inference and concludes that symbolic/structured inference remains valuable for consistency and accuracy. The broad modeling-decision parent is occupied.

### B. Human annotation disagreement as the target rather than single-label gold

RQ sketch: Does single-label evaluation erase a load-bearing distribution of legitimate human judgments, and can LLMs recover that distribution?

**Do not promote.** ACL 2025 work directly studies LLM confidence under annotation disagreement; ACL 2026 directly studies whether LLM sampling/ensembles reproduce human label variation in NLI. The modern LLM-era parent is active and direct.

### C. Generic dynamic/version-aware QA

RQ sketch: Should QA answer from the current state of a changing document rather than a stale version?

**Do not promote in generic form.** DynaQuest (ACL Findings 2025) explicitly builds QA from Wikipedia version updates. A generic “documents change, QA should update” story is occupied.

### D. Scientific-paper revision / edit intent

RQ sketch: What scientific information changes across paper revisions, and can LLMs recognize why an edit was made?

**Do not promote in generic form.** ARIES, Re3/Re3-Sci, EMNLP 2024 edit-intent classification, and the ACL 2026 revision survey make scientific revision itself a mature NLP space. A revision-only framing is insufficient.

### E. Primary/secondary source provenance in scientific QA

RQ sketch: Is an answer supported in the same sense when its evidence is a review/synthesis rather than a primary study?

**Not promoted.** Current evidence-based QA, attribution, multi-document scientific QA, PubMed QA/retrieval, and scientific evidence synthesis are crowded. No clean independent action/gold variable was found in this pass that creates a distinct Main-level story.

## 3. One surviving fresh lead — NOT a candidate yet

# Scholarly Record Versioning: Original Claim ≠ Current Valid Claim

**Status:** SURVIVING LEAD / DATA-AUDIT REQUIRED / NOT PILOT-AUTHORIZED.

### One-sentence RQ

> When a published scientific article receives an official correction, corrigendum, erratum, or corrected republication, can a literature system identify which proposition is still part of the current scholarly record rather than answering from a superseded statement in the original version?

### Simple example

An original article contains a quantitative or methodological statement. A later official correction explicitly replaces that statement or changes the interpretation. A scientific QA/synthesis system sees both records. Which claim should it propagate as current evidence?

### Why the object is natural

The scholarly record is explicitly dynamic rather than immutable. PubMed/NLM officially links original articles to errata, corrected-and-republished articles, and updates. Crossref/Crossmark records post-publication updates such as correction, corrigendum, erratum, partial retraction, new version, and clarification, and describes these as editorially significant changes that may affect interpretation or credit.

This is not the same as generic temporal QA: the state transition is **editorially adjudicated by the scholarly record itself**.

This is also deliberately **not** framed as retraction awareness: 2025–2026 work already directly tests whether LLMs/tools recognize and avoid retracted literature.

### Why it could be outcome-robust

If systems correctly follow corrections, the question becomes what operations make scholarly-record status recoverable and when it transfers across publisher/update types.

If they systematically preserve superseded claims, there is a direct failure of scientific QA/synthesis semantics.

If behavior depends on whether the correction is lexical, numerical, methodological, or interpretive, that gives a natural boundary/decision map.

Thus the paper need not exist only if one surprising error rate appears.

### Data Gate: what is already real

**Relationship-level gold exists:**

- NLM creates official links between original articles and errata / corrected-and-republished articles / updates.
- Crossref Crossmark exposes machine-readable update relationships and controlled update types.

### Data Gate: the unresolved load-bearing problem

**Relationship gold is not proposition gold.** NLM explicitly does not reliably distinguish publisher errors from errors of scientific logic/methodology, because journal editors do not label this consistently. Many corrections may be author-name, formatting, reference, or other non-substantive changes.

The decisive estimand requires a trustworthy mapping such as:

`old proposition -> official correction operation -> current proposition/status`

We must not infer “substantive scientific change” ourselves at scale merely from the presence of an erratum link.

### Required next audit before promotion

1. Sample PubMed/Crossref correction pairs across publishers.
2. Measure how often the notice itself explicitly exposes a machine-extractable replacement, deletion, addition, or qualification of a proposition.
3. Separate metadata-only/minor corrections without inventing scientific labels.
4. Search specifically for NLP / IR / scientometrics work on **correction-aware claim-level QA/synthesis**, not merely retraction detection, document versioning, or edit classification.
5. Only if proposition-level direct gold is sufficiently available, build the full candidate card and perform reviewer compression.

### Current reviewer compression threat

> “Dynamic QA / retraction-awareness, but on corrigenda.”

The only viable rebuttal would be a paper identity centered on **editorially adjudicated supersession of scientific propositions**, with direct proposition-level gold and a consequence for scientific evidence synthesis. If that cannot be established, kill.

## 4. Round verdict

No new PILOT-AUTHORIZED candidate was created in this pass.

That is intentional: several intuitive spaces were already occupied at the modern parent level. The only fresh lead that survived broad novelty screening has a promising natural object and official relationship gold, but has **not** yet passed the proposition-level DIRECT-GOLD gate.

**State after this pass remains:**

- Approved Mainline = NONE
- PILOT-AUTHORIZED = L03, L04
- killed ledger = through K179
- next kill ID = K180
- new watch lead = Scholarly Record Versioning / official correction-aware claim supersession
