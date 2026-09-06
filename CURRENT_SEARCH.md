# Current Research-Question Search — 2026-09-06 Active Search

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Pilot-authorized candidates in `good/`:** 1 — L02  
**Current target:** find additional five-gate candidates without lowering the bar.

> Search status after the first post-L02 assassination batch:
>
> - **15 additional candidate families killed:** K061–K075
> - **A-level live leads:** 0 at this checkpoint
> - **B-level live leads:** 3
>
> This is intentional. A lead is not promoted merely because it sounds natural.

---

# A-level strong live leads

## None yet

No newly searched lead has survived enough parent-level novelty work to deserve A-level status.

---

# B-level search leads

## B1 — Reported Proposition ≠ Speaker/Narrator Commitment

### Plain-language object
A document can contain the sentence “The minister said the drug is safe” without the journalist/narrator asserting that the drug is safe.

### Candidate RQ
> When a model extracts, summarizes, or answers from reported speech, can it distinguish **what proposition is present in the text** from **who is committed to that proposition**?

### Why this might be a real new axis
Classical opinion/factuality resources represent sources/holders, but modern generative NLP may collapse:
1. proposition recovery;
2. source attribution;
3. narrator/author endorsement.

This is more specific than quote attribution (K063) and potentially broader than binary factuality.

### Data/gold candidates to audit
- MPQA opinion holder/source annotations;
- FactBank / source-relative factuality;
- reported-speech / attribution corpora;
- naturally occurring news, not synthetic stories.

### Immediate kill test
KILL if recent 2024–2026 LLM work already owns **source-relative commitment / endorsement under reported speech** as the parent, or if the only novelty is “LLMs make attribution errors.”

### Status
**LIVE — parent audit required.**

---

## B2 — Correct Answer ≠ Complete Answer Set

### Plain-language object
For “Which countries border Germany?”, naming France is **correct**, but it is not a **complete answer**.

### Candidate RQ
> In open-ended/list QA, do current evaluation and generative models conflate **answer correctness** with **answer completeness/exhaustivity**?

### Why this might be a real new axis
A single supported item and a complete set are different semantic quantities. Generative QA makes partial-but-fluent answers especially natural, while many older QA metrics were designed around one/few reference strings.

### Data/gold candidates to audit
- QAMPARI / list QA resources;
- AmbigQA / ASQA only if their gold structure genuinely supports completeness;
- Wikidata-derived list questions only if gold completeness is independently defensible.

### Immediate kill test
KILL if list-QA/exhaustiveness papers already make correctness-vs-completeness the parent contribution, or if KB incompleteness destroys trustworthy gold.

### Status
**LIVE — parent + gold audit required.**

---

## B3 — Event Mention ≠ Event Instance Cardinality

### Plain-language object
“The bell rang twice” contains one event-denoting phrase but describes more than one ringing occurrence.

### Candidate RQ
> Does event extraction correctly represent **how many event instances a mention commits to**, rather than assuming one trigger span equals one event instance?

### Why this might be a real new axis
Event extraction often operationalizes an event instance around a trigger/mention. Quantification, coordination, iteration, and habitual language can break a simple 1-trigger ↔ 1-instance assumption.

### Data/gold candidates to audit
- Rich ERE guidelines/corpus, which allow multiple event tags in some coordinated time/place cases;
- event genericity/specificity resources;
- search specifically for event cardinality/iteration annotations before treating the data gate as viable.

### Immediate kill test
KILL if no natural corpus provides reliable instance-cardinality gold, or if event genericity/quantification literature already owns the parent.

### Status
**LIVE BUT DATA-RISKY — data/gold audit first.**

---

# Terminal results from this batch

The following attractive shapes were searched and rejected; details are now recorded as K061–K075 in `failed/KILLED_LEDGER.md`:

- split-antecedent referential composition;
- NIL-aware generative entity linking;
- quote speaker attribution;
- event mention vs occurrence/factuality;
- singleton detection vs coreference linking;
- atomic citation scope;
- dialogue slot mention vs commitment;
- relative temporal relation vs absolute temporal anchoring;
- event similarity vs event identity;
- GEC correction vs rewriting;
- faithfulness vs factuality;
- unordered set vs sequence generation;
- exact span vs semantic argument in generative IE;
- discourse sense vs argument attachment;
- entity-level relation vs mention-level evidence.

---

# Search rule for the next batch

For each live lead:

1. identify the classical parent and exact natural data;
2. search 2024–2026 ACL/EMNLP/NAACL + neighboring venue ownership;
3. write Account A / Account B before any pilot;
4. attack with reviewer compression;
5. audit whether gold is independently trustworthy;
6. either:
   - promote to A-level and complete a Candidate Card; or
   - append the next K-number and remove it from this file.

> **No GPU until all five gates are YES.**
