# SSN Group Paper — NAACL Main Research Question Repository

**Primary target:** NAACL Main  
**Calibration:** ACL / EMNLP / NAACL Main, especially Best / Outstanding / Best Theme papers.

> **Current state: ACTIVE SEARCH**
>
> **Approved mainline: NONE**
>
> **Pilot-authorized good candidates: NONE**
>
> **Current live leads under audit: 2**
>
> **Rule: if any hard gate is clearly NO, KILL BEFORE COMPUTE.**

This repository is a **research-question selection and decision ledger**, not an idea dump.

We want:

> **A natural, durable NLP/language problem; one genuinely new scientific axis inside it; trustworthy simple data and independent gold; a parent-level novel question with multiple informative outcomes; and a small decisive experiment that can naturally grow into a Main paper.**

Short form:

> **Real object. New axis. Good data. New parent question. Decisive paper.**

Search principle:

> **Search locally, judge globally.**

Recent Sasano-lab work tells us where natural questions may live. ACL / EMNLP / NAACL Main determine whether a question is strong enough.

---

# 1. Repository structure

```
.
├── README.md
├── CANDIDATE_CARD.md
├── CURRENT_SEARCH.md
├── failed/
│   └── KILLED_LEDGER.md
└── good/
    └── README.md
```

## `failed/KILLED_LEDGER.md`

**All failed ideas live in one cumulative ledger. Do not create one file per killed topic.**

Every serious candidate that is rejected is appended to the ledger with:

- short name / RQ;
- date;
- status;
- **primary failure type**;
- secondary failure type(s);
- exact reason;
- closest collision when novelty is the issue;
- reviewer compression;
- what would have to change before reopening.

The purpose is anti-resurrection: a future idea with a new dataset/model/name should be recognized as the same dead parent when appropriate.

## `CURRENT_SEARCH.md`

This stores **live leads that look promising but have not yet passed all five gates**.

Do not put a lead into `good/` merely because it survived one novelty pass.

## `good/`

Only candidates that pass **all five hard gates** may enter `good/`.

Because good candidates should be rare, each promoted candidate may have its own completed Candidate Card / audit file.

A file in `good/` means:

> **pilot-authorized, not paper-mainline-approved.**

After the pilot, the candidate must survive another novelty/interpretation audit before becoming the mainline.

---

# 2. Failure taxonomy

Use these codes in the kill ledger.

| code | meaning |
|---|---|
| **NOVELTY_PARENT_COLLISION** | Prior work already owns the parent RQ, decisive prediction, measurement rewrite, causal estimand, or conclusion. |
| **CROWDED_PARENT** | No exact duplicate is necessary; reviewer compression places the idea inside an already saturated scientific parent. |
| **DATA_GOLD_FAILURE** | Natural data / independent gold cannot be secured credibly. |
| **NO_NEW_AXIS** | Mostly a competence test, textbook distinction, benchmark cell, or post-hoc failure story. |
| **REAL_OBJECT_FAILURE** | Object is artificial, method-first, model-specific, or insufficiently durable/important. |
| **DECISIVENESS_FAILURE** | Only one quirky positive outcome is interesting; null/reverse outcomes teach little. |
| **WORKLOAD_PATH_FAILURE** | Too much infrastructure/data reconstruction is required before the RQ is even secured. |
| **PAPER_SCALE_FAILURE** | Cannot naturally grow into C1 → C2 → C3 without padding. |
| **OTHER** | Must be explained precisely. |

A candidate can have several failure types, but it must have one **primary kill reason**.

---

# 3. Hard Gate 1 — REAL OBJECT

Start from a real NLP/language object, not from a method or fashionable model category.

High-prior objects include:

- lexical semantics;
- semantic access;
- compositional / implicit meaning;
- factual / parametric knowledge;
- linguistic inference;
- ambiguity, syntax, discourse;
- established linguistic phenomena;
- structured semantic/NLP relations;
- established NLP tasks whose evaluation or measurement unit may be wrong;
- representation/generation processes only when tied to a concrete language question.

Do **not** start from:

- SAE;
- activation patching;
- agent;
- RAG;
- diffusion LM;
- a cognitive bias;
- a new benchmark;
- “Old Problem / New Method” as a slogan.

Mandatory tests:

> **If “LLM”, model names, and dataset names disappear, is the question still important?**

> **Would an ACL/EMNLP/NAACL reviewer understand why this matters before seeing our result?**

Durability matters: the question should survive model/API turnover.

---

# 4. Hard Gate 2 — NEW AXIS

We need a **new scientific relation inside a real object**, not a new field.

Preferred shapes:

1. **Two factors previously conflated.**
2. **A wrong measurement/unit.**
3. **Two plausible theories/accounts make different predictions.**
4. **A classical result depended on a load-bearing assumption changed by modern model classes.**

Before compute, write:

> **Account A predicts X.**

> **Account B predicts Y.**

Both must be plausible before results exist.

Default warning signs:

- “theoretically X and Y differ; does the model know that?”;
- “probe A and probe B disagree”;
- “language and numeric outputs disagree”;
- “correct behavior = X; failure = Y.”

Those are usually competence/evaluation observations unless they instantiate a stronger scientific proposition.

---

# 5. Hard Gate 3 — GOOD DATA

Data is a first-order selection criterion.

Priority:

1. **Existing natural dataset / corpus / resource** already containing the needed variation.
2. **Published human / linguistic experiment materials.**
3. **Small theory-grounded controlled stimuli** with independently defensible gold.

Default high-risk:

- large template datasets;
- bespoke synthetic worlds;
- author-created ontology;
- unnatural stories written only to isolate a contrast;
- LLM-generated main data;
- LLM-generated question + LLM judge;
- author intuition as decisive gold.

Mandatory questions:

> **Did the scientific object exist before our hypothesis?**

> **Can the gold be justified without the same class of LLM being evaluated?**

If data validity is unclear:

> **KILL BEFORE COMPUTE.**

---

# 6. Hard Gate 4 — NEW PARENT

Novelty is judged at the **parent scientific-question level**, not title/dataset wording.

Search ownership of:

- parent RQ;
- decisive prediction;
- core conclusion;
- measurement rewrite;
- causal estimand;
- old-assumption rewrite.

Mandatory reviewer attack:

> **“This is just ______.”**

A valid rebuttal must identify a genuinely different:

- scientific quantity;
- prediction;
- structural relation;
- measurement;
- causal claim;
- theoretical conclusion.

Not enough:

- another dataset;
- another language;
- another model;
- more scale;
- more prompts;
- cleaner controls;
- mechanism added later.

Minimum pre-pilot novelty calibration should include strong same-identity ACL/EMNLP/NAACL papers, the nearest direct collisions, and older theoretical/task parents when relevant.

---

# 7. Hard Gate 5 — DECISIVE PAPER

A strong candidate should naturally form:

### C1 — Core answer
What new relation/law/measurement did we establish?

### C2 — Why / boundary
Why does it happen, or where does it hold/fail?

### C3 — Consequence
What changes in theory, evaluation, measurement, interpretation, method, or practical decision?

This is **claim architecture**, not experiment count.

Do not pad weak questions with model count, prompts, languages, benchmarks, or activation patching.

## Outcome robustness

Before pilot, several outcomes should remain informative:

- Account A wins;
- Account B wins;
- principled heterogeneity/boundary;
- reverse;
- null that rules out a plausible theory.

Danger:

> **Only a surprising model failure produces a paper.**

That is phenomenon gambling.

## Evidence depth

Use the simplest evidence strong enough for the claim:

- behavioral / measurement → controls, decomposition, robustness;
- causal / mechanistic → causal intervention;
- classical law → test law and assumptions;
- evaluation → validate the measurement and show changed conclusions.

Mechanism is an escalation path, not a rescue device.

---

# 8. The five mandatory YES answers

A candidate reaches a pilot only if all are clearly YES:

1. **REAL OBJECT** — natural, important, durable?
2. **NEW AXIS** — non-obvious relation with at least two plausible accounts?
3. **GOOD DATA** — simple credible data + independent gold?
4. **NEW PARENT** — parent-level novelty survives “This is just X”?
5. **DECISIVE PAPER** — multiple outcomes informative; C1→C2→C3 natural and manageable?

If any core answer is clearly NO:

# **KILL**

Not “run a little and see.”

---

# 9. Human-understandability / linguistic-complexity preference

The project does **not** optimize for “the most linguistically technical question.”

New search prior:

> **Prefer research questions that are natural and explainable in ordinary language.**

A linguistic phenomenon is welcome when:

- the real-world distinction is easy to explain;
- the scientific tension can be stated without a long formal-semantics lecture;
- the data/gold are already available and trustworthy;
- the paper identity is visible before technical machinery appears.

Strong negative prior for:

- highly specialized formal-semantic puzzles whose importance is difficult to communicate;
- questions requiring several pages of linguistic background before the RQ makes sense;
- distinctions that are interesting mainly to a narrow theoretical subcommunity;
- candidates where the user/reviewer must learn new linguistic terminology before understanding why the result matters.

This is a **search preference, not a lower scientific bar**.

A simple natural linguistic object can still be excellent. The point is:

> **Easy to understand, hard to answer.**

---

# 10. Immediate kill signals

Default KILL / strong negative prior when:

- scientific object is invented for the experiment;
- RQ is essentially “does the model know X ≠ Y?”;
- only a quirky failure is interesting;
- bespoke synthetic data is necessary;
- gold relies on LLM-as-judge or author intuition;
- closest parent owns the proposition;
- novelty is only dataset/model/language/prompt/scale;
- mechanism is being added to make a weak RQ look deep;
- huge infrastructure is required before a decisive answer exists;
- topic is a fast-moving agent/RL/prompt/API race without a durable scientific axis;
- reviewer compression places it in an already crowded generic category.

---

# 11. Preferred search region

Highest priority:

- semantic access / factual access;
- lexical meaning when the distinction is intuitive;
- implicit meaning and reference when explainable without heavy formalism;
- factual / parametric knowledge;
- language understanding / inference;
- discourse and document structure;
- stable NLP tasks with a questionable evaluation/measurement unit;
- natural generation/representation questions tied to a concrete behavior.

Still allowed, but lower priority:

- highly technical formal semantics;
- highly specialized syntax;
- niche linguistic phenomena whose motivation takes substantial background.

Conditional:

- causal interpretability;
- diffusion/generation dynamics;
- efficiency/compression;
- Japanese-specific phenomena.

Low priority by default:

- generic agents;
- generic RAG;
- prompt optimization;
- LLM-as-judge / annotator;
- broad cognitive-bias transplantation;
- behavioral-economics phenomenon hunting;
- typology/documentation policy;
- bespoke synthetic worlds;
- mechanism-first feature hunting.

---

# 12. Main / Outstanding paper shape to imitate

Imitate the **paper shape**, not the topic:

> **A concrete object already worth caring about + one overlooked scientific axis + credible/simple identification + a conclusion that changes how the object is understood.**

Reference shapes:

- ACL 2026 Best — imperfective paradox: compositional semantics vs teleological heuristic;
- ACL 2026 Outstanding — grammaticality ≠ constructional meaning;
- ACL 2026 RedirectQA — fact possession ≠ surface-form access;
- EMNLP 2025 Outstanding — classical generative/discriminative result revisited under a changed model class;
- EMNLP 2025 Outstanding filler-gap — causal internal evidence used to test concrete syntactic structure;
- NAACL 2025 Outstanding NLI — evaluation unit changed to atomic inference;
- ACL 2025 Outstanding Zipf — meaning operationalized through contextual diversity.

Common denominator:

> **Concrete object. Hard axis. Credible measurement. Changed understanding.**

---

# 13. Mandatory Candidate Card before GPU

Every serious candidate must first use [CANDIDATE_CARD.md](CANDIDATE_CARD.md):

- one-sentence RQ;
- why ACL/NLP cares;
- Account A vs Account B;
- exact data + independent gold;
- closest parent;
- reviewer compression;
- outcome map;
- C1 / C2 / C3;
- minimum decisive pilot;
- five-gate verdict.

If the card is complicated, the topic is probably too complicated.

---

# 14. Governing principles

> **The object should exist before us.**

> **The question should be understandable before the method.**

> **The data should be trustworthy before the experiment.**

> **The tension should exist before the result.**

> **The new axis should change understanding, not merely add another benchmark dimension.**

> **Novelty belongs to the parent scientific question, not the dataset or wording.**

> **Use the simplest evidence strong enough for the claim.**

> **Search locally, judge globally.**

> **Easy to understand, hard to answer.**

> **The question should look important to ACL / EMNLP / NAACL before it looks clever to us.**
