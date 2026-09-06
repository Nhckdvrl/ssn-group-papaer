# SSN Group Paper — NAACL Main Research Question Repository

**Primary target:** NAACL Main  
**Calibration:** ACL / EMNLP / NAACL Main, especially Best / Outstanding / Best Theme papers.

> **Current state: CLEAN SLATE**
>
> **Approved mainline: NONE**
>
> **Active good candidates: NONE**
>
> **Rule: KILL BEFORE COMPUTE if any hard gate is clearly NO.**

This repository is not a benchmark collection or an idea dump. It is a **research-question selection ledger**.

The goal is to find:

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
├── failed/
│   ├── README.md
│   ├── TEMPLATE.md
│   └── <one file per killed topic>.md
└── good/
    ├── README.md
    └── TEMPLATE.md
```

## `failed/`

Every topic that is seriously considered and then rejected must be recorded here.

A failure record must state **why it died**, not merely that it died.

Allowed primary failure types:

- **NOVELTY_PARENT_COLLISION** — closest prior work already owns the parent scientific question / decisive prediction / conclusion.
- **DATA_GOLD_FAILURE** — data cannot be made natural/credible enough, or gold is not independently defensible.
- **NO_NEW_AXIS** — question is mainly a competence test, benchmark cell, or textbook distinction without pre-result scientific tension.
- **REAL_OBJECT_FAILURE** — object is too artificial, method-first, model-specific, or not durably important.
- **DECISIVENESS_FAILURE** — only one quirky positive outcome is interesting; null/reverse outcomes teach little.
- **WORKLOAD_PATH_FAILURE** — too much infrastructure/data construction is required before the RQ itself is secured.
- **PAPER_SCALE_FAILURE** — cannot naturally grow into C1 → C2 → C3 without padding.
- **CROWDED_PARENT** — exact collision may be absent, but reviewer compression places the topic inside an already saturated scientific parent.
- **OTHER** — must be explained precisely.

A topic may have several failure types, but one **primary kill reason** must be named.

## `good/`

Only candidates that pass **all five hard gates** may enter `good/`.

A file in `good/` does **not** mean “accepted paper mainline.” It means:

> **The question is strong enough to justify a minimum decisive pilot.**

Promotion to a paper mainline requires surviving the pilot and another novelty / interpretation audit.

---

# 2. Hard Gate 1 — REAL OBJECT

Start from a real NLP/language object, not from a method or fashionable model category.

High-prior objects include:

- lexical semantics;
- semantic access;
- compositional / implicit meaning;
- factual / parametric knowledge;
- linguistic inference;
- ambiguity / syntax / discourse;
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

Two mandatory tests:

> **If “LLM”, model names, and dataset names disappear, is the question still important?**

> **Would an ACL/EMNLP/NAACL reviewer understand why this matters before seeing our result?**

If importance requires explaining a concept we invented, risk is high.

Durability matters: the question should survive model/API turnover.

---

# 3. Hard Gate 2 — NEW AXIS

We do not need a new field. We need a **new scientific relation inside a real object**.

Preferred shapes:

1. **Two factors previously conflated**
   - e.g. fact possession ≠ access through a particular surface form.

2. **Wrong measurement/unit**
   - e.g. hard sense count vs contextual diversity;
   - whole NLI hypothesis vs atomic inference units.

3. **Competing theories predict differently**
   - e.g. compositional semantics predicts X while a plausible heuristic predicts Y.

4. **An old result depended on an assumption that modern model classes change**
   - not “old task + LLM”;
   - must identify the load-bearing assumption and the changed prediction/measurement/method.

Before compute, write:

> **Account A predicts X.**

> **Account B predicts Y.**

Both accounts must be plausible **before** results exist.

Default warning signs:

- “theoretically X and Y differ; does the model know that?”;
- “probe A and probe B disagree”;
- “language output and numeric output differ”;
- “correct answer = X, failure = Y.”

Those are usually competence/evaluation observations unless attached to a genuinely important new proposition.

---

# 4. Hard Gate 3 — GOOD DATA

Data is a selection criterion, not an implementation detail.

Priority:

### Best
Existing natural dataset / corpus / resource already containing the needed variation.

### Also strong
Existing published human or linguistic experimental materials.

### Acceptable
Small controlled stimuli grounded in established theory/formal rules with independently defensible gold.

Default high-risk:

- large template-generated datasets;
- bespoke synthetic worlds;
- author-created ontology;
- unnatural stories written only to isolate a contrast;
- LLM-generated main data;
- LLM-generated questions plus LLM judge;
- author intuition as the decisive label source.

Mandatory questions:

> **Did the scientific object exist before our hypothesis?**

> **Can the gold be justified without the same class of LLM being evaluated?**

Preferred gold sources:

- existing annotations/resources;
- human judgments;
- published linguistic analysis;
- formal derivation;
- deterministic algorithms;
- independent corpus evidence.

If data validity is unclear:

> **KILL BEFORE COMPUTE.**

---

# 5. Hard Gate 4 — NEW PARENT

Novelty is judged at the **parent scientific question**, not at title/dataset wording level.

For every candidate, search for ownership of:

- parent RQ;
- decisive prediction;
- core scientific conclusion;
- measurement rewrite;
- causal estimand;
- old-assumption rewrite.

Mandatory reviewer attack:

> **This is just ______.**

The rebuttal must be:

> **No. The scientific quantity / prediction / relation / measurement / conclusion is different.**

The following are not enough:

- another dataset;
- another model;
- another language;
- cleaner controls;
- larger scale;
- more prompts;
- mechanism added later.

Minimum pre-pilot novelty calibration:

- several strong same-identity ACL/EMNLP/NAACL papers;
- nearest direct collisions;
- older theoretical/task parent when relevant.

Local lab fit never overrides a close parent collision.

---

# 6. Hard Gate 5 — DECISIVE PAPER

A Main paper does not need a huge engineering stack.

A good question should naturally support:

### C1 — Core finding
What did we actually establish about the new axis?

### C2 — Why / boundary
Why does it happen, or where does the relation hold/fail?

### C3 — Consequence
What changes in theory, evaluation, measurement, interpretation, method, or practical decision?

This is **claim architecture**, not experiment count.

Do not pad weak questions with:

- many models;
- many prompts;
- extra languages;
- extra benchmarks;
- activation patching;
- mechanism work unrelated to the claim.

## Outcome robustness

Before pilot, map multiple outcomes:

- Account A wins;
- Account B wins;
- heterogeneous principled boundary;
- reversal;
- null that rules out a plausible theory.

Danger:

> **Only a surprising model failure produces a paper.**

That is phenomenon gambling.

## Evidence depth

Use the simplest evidence strong enough for the claim:

- behavioral / measurement claim → strong controls, decomposition, robustness;
- causal / mechanistic claim → causal interventions;
- classical law → test law and assumptions;
- evaluation claim → prove the new measurement changes interpretation/conclusions.

Mechanism is an escalation path, not a rescue device.

---

# 7. The five mandatory YES answers

A candidate reaches a pilot only when all are clearly YES:

1. **REAL OBJECT** — natural, important, durable?
2. **NEW AXIS** — genuine non-obvious relation with ≥2 plausible accounts?
3. **GOOD DATA** — simple credible data + independent gold?
4. **NEW PARENT** — parent-level novelty survives “This is just X”?
5. **DECISIVE PAPER** — multiple outcomes informative; C1→C2→C3 natural and manageable?

If any core answer is clearly NO:

# **KILL**

Not “run a little and see.”

---

# 8. Immediate kill signals

Default KILL / strong negative prior when:

- the object is invented for the experiment;
- RQ is essentially “does the model know X ≠ Y?”;
- only a quirky failure is interesting;
- bespoke synthetic data is necessary;
- gold relies on LLM-as-judge or author intuition;
- closest parent already owns the proposition;
- novelty is only dataset/model/language/prompt/scale;
- mechanism is being added to make a weak question look deep;
- huge infrastructure is required before a decisive answer exists;
- the topic is a fast-moving agent/RL/prompt/API race without a durable scientific axis;
- reviewer compression places the work in an already crowded generic category.

---

# 9. Preferred search region

Highest priority:

- lexical semantics / semantic access;
- compositional / implicit meaning;
- factual / parametric knowledge;
- linguistic inference;
- established linguistic phenomena;
- structured semantic/NLP relations;
- evaluation / measurement units inside stable NLP tasks.

Conditional:

- causal interpretability;
- diffusion/generation dynamics;
- efficiency/compression;
- Japanese-specific phenomena.

Low priority by default:

- generic agents;
- generic RAG;
- prompt optimization;
- LLM-as-judge / LLM-as-annotator;
- broad cognitive-bias transplantation;
- behavioral-economics phenomenon hunting;
- typology/documentation policy;
- bespoke synthetic worlds;
- mechanism-first feature hunting.

---

# 10. Main / Outstanding paper shape we imitate

We imitate **paper shape**, not topic:

> **A concrete object already worth caring about + one overlooked scientific axis + credible/simple identification + a conclusion that changes how the object is understood.**

Reference shapes include:

- ACL 2026 Best — imperfective paradox: compositional semantics vs teleological heuristic;
- ACL 2026 Outstanding — grammaticality ≠ constructional meaning;
- ACL 2026 RedirectQA — fact possession ≠ surface-form access;
- EMNLP 2025 Outstanding — classical generative/discriminative result revisited under a changed model class;
- EMNLP 2025 Outstanding filler-gap — causal internal evidence used to test a concrete syntactic theory;
- NAACL 2025 Outstanding NLI — evaluation unit changed to atomic inference;
- ACL 2025 Outstanding Zipf — “meaning” operationalized through contextual diversity.

Common denominator:

> **Concrete object. Hard axis. Credible measurement. Changed understanding.**

---

# 11. Mandatory Candidate Card before GPU

Every candidate must fit on one page using [CANDIDATE_CARD.md](CANDIDATE_CARD.md):

- one-sentence RQ;
- why ACL/NLP cares;
- Account A vs Account B;
- exact data + independent gold;
- closest parent;
- reviewer compression: “This is just ____”;
- why that compression is false;
- outcome map;
- C1 / C2 / C3;
- minimum decisive pilot;
- five-gate verdict.

If the card is complicated, the topic is probably too complicated.

---

# 12. Governing principles

> **The object should exist before us.**

> **The question should be understandable before the method.**

> **The data should be trustworthy before the experiment.**

> **The tension should exist before the result.**

> **The new axis should change understanding, not merely add another benchmark dimension.**

> **Novelty belongs to the parent scientific question, not the dataset or wording.**

> **Use the simplest evidence strong enough for the claim.**

> **Search locally, judge globally.**

> **The question should look important to ACL / EMNLP / NAACL before it looks clever to us.**
