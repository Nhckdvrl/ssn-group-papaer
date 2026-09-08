# Research Topic Selection — Authoritative Compact Standard

**Target:** ACL / EMNLP / NAACL Main  
**Aspirational bar:** Best / Outstanding / Best Theme Paper  
**Principle:** easy to understand, hard to answer.

This document is the authoritative **topic-selection** workflow. It is independent from project execution.  
Do not turn it into a longer checklist unless a new rule is proven necessary by a real failure.

---

## 0. North Star

Start from the **research question**, not the method.

A strong topic should be explainable with:
1. one sentence stating the RQ;
2. one ordinary-language example showing why it is interesting;
3. two or more plausible answers/accounts;
4. a clear reason why ACL/NLP should care before seeing the result.

Do not chase a topic because it is hot, because a method is fashionable, because one paper has an obvious future-work sentence, or because one search direction was mentioned recently.

Use recent ACL / EMNLP / NAACL papers, PaperNotes, and relevant ICLR / ICML / NeurIPS work as a **map of strong paper shapes and occupied space**, not as a list of topics to imitate.

Use Sasano-lab topics only to calibrate naturalness and question style. The external quality bar is top-conference Main/Outstanding work.

There is no promotion quota. Zero survivors in a round is acceptable.

---

# Stage 1 — Broad Search

Search several distinct mother domains in every round. Do not spend a whole round generating siblings of one idea.

Useful generators include:
- a natural unresolved NLP object;
- a classic modeling choice whose assumptions changed in the foundation-model era;
- two factors that previous work conflated;
- a measurement/task definition that may target the wrong quantity;
- a natural dataset exposing a scientific relation nobody has properly exploited;
- two plausible explanations of an established result;
- a new scientific operation/intervention that makes an old question answerable.

These are **search generators, not topic requirements**.

For each rough lead, write only:
- one-sentence RQ;
- plain example;
- why it matters;
- likely natural data;
- obvious closest collision.

Generate broadly first. Do not run compute and do not fill a full Candidate Card yet.

---

# Stage 2 — Six Hard Questions

A lead survives only if all six are defensible.

## Q1. Is the RQ itself natural and interesting?

- Does the object exist independently of our hypothesis?
- If model names, dataset names, and methods disappear, does the question still matter?
- Can a reviewer understand the interest from one simple example?
- Is the question durable rather than tied to a temporary API/model trend?

Reject method-first, benchmark-cell, or artificially manufactured objects.

## Q2. Is there real scientific tension rather than an obvious answer?

There must be at least two ex-ante plausible accounts, modeling choices, or explanations.

Ask:
> If I told a reviewer the result in advance, would they say “of course”?

If yes, the claim is probably too trivial.

A good axis is not merely:
- “does the model know X?”;
- “does failure X occur?”;
- “probe A differs from probe B?”;
- “method A beats method B?”

The answer must change how we understand, model, measure, or design the NLP problem.

## Q3. Do we have direct, simple, high-quality data and gold?

Data is a first-class gate, not an implementation detail.

Prefer:
1. existing natural corpora/resources;
2. real logs/records/system states;
3. published human materials/annotations;
4. small controlled materials only when the gold is independently defensible.

For the load-bearing estimand, explicitly write:

> **external observation / released annotation / real state → exact scientific quantity**

Kill if the mapping is only a proxy such as “label X probably means Y.”

Strong negative prior:
- large bespoke synthetic datasets;
- LLM-generated main data or gold;
- author-created ontologies/labels carrying the main conclusion;
- massive data construction before the RQ is secured.

The dataset should be as simple as possible while still exactly representing the scientific question.

## Q4. Is there a genuinely new paper-level story?

Novelty does **not** require the entire topic or every subquestion to be untouched.

Prior work may already own:
- the object;
- a dataset;
- one distinction;
- one component experiment;
- one neighboring claim.

What must be new enough is the load-bearing combination of:

> **framing + idea + decisive comparison/operation + core claim + consequence**

We require a **new narrative, new idea, and new core claim** at paper level.

Mandatory reviewer attack:

> **“This is just ______.”**

If one or a small set of papers can accurately compress the whole proposed paper, kill it.

If prior work only supplies ingredients but our scientific story and decisive conclusion are genuinely different, it may survive.

## Q5. Is this a research space, not a one-effect bet?

Before compute, the topic should naturally contain roughly three meaningful subquestions, for example:
- core comparison / scientific answer;
- mechanism / attribution;
- boundary / heterogeneity;
- modeling or evaluation consequence;
- generalization / cost / robustness decision map.

Several outcomes must remain scientifically useful:
- Account A wins;
- Account B wins;
- a principled boundary appears;
- a meaningful preservation/equivalence result appears.

If the paper disappears when the first exciting effect is absent, reject it.

## Q6. Does it look like a Main-level paper before we run it?

Compare the candidate with at least **3 concrete high-level ACL/EMNLP/NAACL papers**, preferably including:
- one Best/Outstanding/Theme paper;
- one paper with a similar paper identity;
- one close scientific/technical neighbor.

Align explicitly on:
- RQ breadth;
- naturalness/importance;
- claim breadth and novelty;
- data/gold;
- identification/decisiveness;
- C1 → C2 → C3;
- consequence for NLP;
- whether the story is memorable and independently interesting.

Current local survivors are **not** the quality benchmark.

---

# Stage 3 — Novelty Assassination

Only deep-audit the best leads.

Search:
- classical parent work;
- 2024–2026 ACL / EMNLP / NAACL;
- newest papers from PaperNotes / ACL Anthology / arXiv / OpenReview;
- relevant ICLR / ICML / NeurIPS when paper identity overlaps;
- dataset/resource documentation.

The goal is not to prove “nobody has ever touched this.”  
The goal is to determine exactly what prior work owns and what our paper would uniquely own.

For each serious lead record:
1. closest parent;
2. closest modern collision;
3. what they already establish;
4. what they do not establish;
5. our new narrative / idea / claim;
6. exact condition under which the lead should be killed.

Do this **before GPU**.

---

# Stage 4 — Promotion

A candidate becomes **PILOT-AUTHORIZED** only after a compact Candidate Card is complete and all hard questions pass.

Promotion never means mainline approval.

The minimum paper architecture must already be visible:

- **C1 — Core scientific answer**
- **C2 — Mechanism / explanation / boundary**
- **C3 — What NLP should change because of C1+C2**

Then run the smallest decisive pilot.

After the pilot, re-audit:
- data validity;
- novelty;
- interpretation;
- claim scale;
- C1→C2→C3;
- top-conference alignment.

A candidate can and should still be killed after compute.

---

# Immediate Kill Signals

Kill early when:
- the RQ is obvious/trivial;
- the object exists mainly because we constructed it;
- novelty is only a new model/language/dataset/prompt;
- the whole paper requires one surprising failure;
- data/gold only proxy the claimed quantity;
- a close paper already owns the same narrative and core conclusion;
- the topic is a crowded trend with no durable independent scientific axis;
- the project needs huge infrastructure before we can tell whether the question matters;
- C1→C2→C3 requires padding rather than natural development.

---

# Compact Candidate Card

Before compute, answer only:

1. **RQ**
2. **Plain example + why ACL cares**
3. **Account A / Account B / possible boundary**
4. **Exact natural data + direct gold mapping**
5. **Closest papers + reviewer compression**
6. **What is genuinely new: narrative / idea / core claim**
7. **Research-space map: at least ~3 natural subquestions**
8. **Outcome map: why A/B/boundary/null remain informative**
9. **C1 → C2 → C3**
10. **Minimum decisive pilot + exact kill conditions**
11. **Top-conference alignment against ≥3 concrete papers**

If this compact card is hard to state clearly, the topic is probably not ready.

---

# Governing Rules

> Question first, method second.

> The example should make the interest obvious.

> Natural data and direct gold before compute.

> Do not bet the paper on one phenomenon.

> Novelty is paper-level ownership, not an untouched neighborhood.

> Ingredients may be old; the narrative, idea, and core claim must be genuinely ours.

> Claims must not be “of course” claims.

> Search broadly; assassinate narrowly.

> Search locally, judge globally.

> Easy to understand, hard to answer.
