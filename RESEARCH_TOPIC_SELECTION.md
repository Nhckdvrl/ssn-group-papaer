# Research Topic Selection — Authoritative Candidate Evaluation

**Target:** ACL / EMNLP / NAACL Main  
**Aspirational bar:** Best / Outstanding / Best Theme / unusually strong paper identity  
**North star:** **Easy to understand, hard to answer.**

This file answers one question only:

> **A concrete research question already exists. Is it strong enough to deserve a decisive pilot?**

How to search for topics belongs to **RESEARCH_TOPIC_SEARCH.md**.  
Idea generators belong to **TOPIC_SEARCH_PLAYBOOK.md**.  
Project execution belongs to **RESEARCH_EXECUTION.md**.

Do not put search priors or generator catalogs back into this file.

---

# 0. Promotion semantics

Possible decisions:

- **KILL** — scientific case collapses; record the serious parent in the killed ledger.
- **HOLD** — potentially interesting, but one blocking audit remains.
- **SERIOUS CANDIDATE** — worth deeper data/novelty work, but not yet authorized for target-model compute.
- **PILOT-AUTHORIZED** — the candidate has passed the pre-pilot gates strongly enough to justify the smallest decisive experiment.

**PILOT-AUTHORIZED does not mean mainline-approved.**

No candidate is protected by sunk cost, by being in good/, or by being one of the current six.

---

# Gate 1 — Natural and important research question

Ask:

- Is the underlying object/problem real, natural, and durable?
- Can the RQ be stated in one or two sentences?
- Can a simple example make the issue obvious?
- Would another NLP researcher agree this is worth knowing?
- Does the problem exist independently of our proposed method?
- Is the likely contribution broader than “model X gets Y% on dataset Z”?

Reject:
- artificial benchmark cells;
- obscure distinctions that need a long lecture before they matter;
- method-first questions;
- “does the LLM know X?” when the only outcome is competence reporting;
- questions whose likely reviewer reaction is:
  > “Of course. Why did this experiment need to be run?”

**PASS condition:** the question is easy to understand and important enough to plausibly anchor a Main paper.

---

# Gate 2 — Genuine scientific tension

A strong candidate needs a real uncertainty, not just an unmeasured number.

Preferred shape:
- at least two plausible competing accounts;
- or a consequential contested modeling/measurement decision;
- or a mechanism/boundary question where multiple outcomes would change understanding.

Examples:
- representation erased vs output suppressed;
- local-step bottleneck vs autoregressive accumulation;
- memory failure vs attribution failure vs policy/action failure;
- explicit intermediate state necessary vs safely inferable.

Competing Account A/B is a strong default, not a universal law. Measurement or methodology papers may instead revolve around:
- a broken construct;
- a load-bearing modeling assumption;
- a decision boundary.

**PASS condition:** before running the experiment, more than one scientifically meaningful answer is plausible.

---

# Gate 3 — Data / evidence really identify the claim

Data are part of the science, not an implementation detail.

For every load-bearing claim, write:

> **data / observation / controlled manipulation / intervention → scientific quantity → claim**

Then audit every arrow.

Ask:
- Is the unit of analysis correct?
- Does the gold/state actually mean the estimand?
- Is a proxy being silently substituted?
- Are missing/ambiguous states distinguished from negatives?
- Is the manipulation strong enough to separate the accounts?
- Is leakage or artifact risk controlled?
- Is the evidence natural enough for the intended conclusion?

Preferred evidence:
- natural existing data;
- official/provider-defined state;
- human behavior/labels;
- published experimental materials;
- benchmark-native gold when it truly matches the estimand;
- controlled causal interventions.

Constructed data are allowed when necessary, but must be:
- minimal;
- interpretable;
- natural;
- independently validated where needed;
- free of hypothesis-shaped shortcuts.

Canonical warning:

> **L02 died because UCCA DNI/INI did not provide gold for whether a specific filler was supported by the current discourse. Gold ≠ estimand.**

Do not rescue a mismatch by saying the label is “close enough.”

**PASS condition:** the evidence is the simplest credible route that genuinely identifies the scientific quantity.

---

# Gate 4 — Paper-level novelty and ownership

Novelty does not require every ingredient to be untouched.

Prior work may already own:
- the object;
- dataset;
- distinction;
- method component;
- one subclaim;
- the parent phenomenon.

What must remain distinctly ours is the load-bearing paper identity:

> **new framing/narrative + decisive idea/operation + central conclusion + consequence**

Mandatory novelty assassination:
- classic parent literature;
- recent ACL / EMNLP / NAACL;
- direct follow-ups;
- relevant ICLR / ICML / NeurIPS when appropriate;
- the latest work whenever the candidate’s story changes.

Mandatory reviewer-compression test:

> **“This is just ______.”**

If one or a few papers can accurately fill that blank and compress the whole proposed paper, **KILL**.

Do not kill merely because:
- the parent problem is old;
- the dataset has been used;
- one distinction is known;
- a nearby paper shares a component.

Do kill when our whole paper is effectively:
- an existing setup + another model;
- an existing paper + cleaner controls;
- an existing measurement paper + another benchmark;
- an existing mechanism paper + one extra probe.

**PASS condition:** a strong reviewer can recognize the proposed paper as a genuinely new paper beside the nearest work.

---

# Gate 5 — Outcome robustness and scientific depth

Do not authorize a topic whose entire paper depends on one lucky effect.

Ask:

> **If the first expected phenomenon is weak or absent, is there still a scientifically meaningful answer?**

Good forms:
- Account A wins → meaningful conclusion.
- Account B wins → meaningful conclusion.
- conditional/boundary result → meaningful conclusion.
- correction result → previous interpretation was wrong.
- preservation/equivalence → meaningful only when it resolves a real consequential question.

Depth can come from:
- mechanism/localization;
- boundary/heterogeneity;
- causal validation;
- measurement validation;
- generalization;
- repair/intervention;
- decision map;
- practical/scientific consequence.

A useful heuristic is:

- **C1 — core answer**
- **C2 — why / where / when / validation**
- **C3 — consequence / what changes**

Do not force exactly three claims if the paper identity needs another structure.

**PASS condition:** the candidate has a crisp center and a natural route to a full paper without padding.

---

# Gate 6 — Main-level calibration

Compare against the strongest **structurally relevant** ACL / EMNLP / NAACL Main work.

Best/Outstanding papers are useful high-end anchors, but do not mechanically imitate them.

For the paper identity at hand, compare the dimensions that actually matter:

- RQ scale;
- naturalness/importance;
- scientific tension;
- data/gold quality;
- identification/decisiveness;
- novelty of the full paper identity;
- depth beyond C1;
- consequence for NLP;
- breadth without padding;
- plain-language memorability.

For mechanistic work, expect stronger causal discrimination.  
For measurement work, expect stronger construct validation.  
For document/evidence work, expect stronger natural-data coverage.  
For methodology work, require an independently important diagnosis or decision, not only a score gain.

Ask:

> **If the result were strong and clean, would a Main reviewer see an independent scientific/methodological contribution, or just a competent study of a narrow cell?**

If the second, **KILL / HOLD**.

The current local candidates are never the quality benchmark.

**PASS condition:** the candidate looks capable of sitting beside strong Main work on the load-bearing dimensions of its own paper type.

---

# Deep audit before pilot authorization

Only candidates that survive all six gates reach this step.

Record the following compactly inside the candidate package:

## 1. RQ
- one-sentence question;
- plain example;
- why it matters;
- what is genuinely uncertain.

## 2. Scientific accounts
- competing accounts or contested decision;
- what observations distinguish them.

## 3. Data/evidence
- source/construction;
- identification chain;
- why valid;
- main artifact/leakage risks.

## 4. Novelty
- closest classic/modern work;
- what prior work already owns;
- reviewer compression;
- why that compression is false;
- our actual paper identity.

## 5. Outcome robustness / paper depth
- what if expected C1 is weak/absent;
- mechanism/boundary/validation routes;
- plausible C1/C2/C3 or equivalent;
- consequence.

## 6. Main-level calibration
- strongest structurally relevant references;
- dimensions on which this paper must match them;
- where the candidate is currently weaker.

## 7. Minimum decisive pilot
- smallest experiment/audit that can materially change the decision;
- informative outcome branches;
- exact kill/reconstruct conditions.

Do not create a separate duplicate candidate checklist.

---

# Pilot design rule

The first pilot is not a miniature full paper.

Its job is to resolve the cheapest load-bearing uncertainty.

Examples:
- data-yield audit before GPU;
- exact parent reproduction;
- teacher forcing vs free running;
- matched oracle/flat/wrong-state intervention;
- a controlled pre/post checkpoint comparison;
- a gold/estimand validity audit.

Do not begin with:
- a huge model zoo;
- dozens of benchmarks;
- expensive scaling;
- decorative analyses.

---

# Kill / reconstruct logic

A hypothesis losing is **not** automatically a topic failure.

Reconstruct when:
- another account wins;
- a meaningful boundary appears;
- a stronger explanation emerges.

Kill when:
- the data cannot identify the quantity;
- the manipulation has no scientific leverage;
- current literature owns the load-bearing narrative;
- all surviving claims are trivial;
- the research space collapses to one narrow cell;
- no credible Main-level consequence remains.

Do not protect a topic because much work has already been invested.

---

# Final authorization test

Before target-model compute, all must be materially YES:

1. **Worth knowing?**
2. **Natural and easy to explain?**
3. **Genuinely non-obvious?**
4. **Evidence really identifies the claim?**
5. **Paper-level identity remains ours?**
6. **More than one outcome remains scientifically useful?**
7. **Enough natural depth for a Main paper?**
8. **Comparable to strong ACL/EMNLP/NAACL Main work?**

Any material NO blocks promotion.

> **Judge the question, evidence, ownership, and paper shape — not how clever the method sounds.**
