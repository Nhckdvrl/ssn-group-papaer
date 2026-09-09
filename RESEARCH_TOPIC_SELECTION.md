# Research Topic Selection — Authoritative Candidate Evaluation

**Target:** ACL / EMNLP / NAACL Main  
**Aspirational bar:** Best / Outstanding / Best Theme / unusually strong paper identity  
**North star:** **Easy to understand, hard to answer.**

This file decides whether a concrete research question deserves the smallest decisive pilot. Search generators belong elsewhere; execution begins only after authorization.

---

# 0. Promotion semantics

- **KILL** — the scientific case or natural paper space collapses.
- **HOLD** — potentially strong, but one blocking audit remains.
- **SERIOUS CANDIDATE** — deserves deeper data/novelty work, but not target-model compute.
- **PILOT-AUTHORIZED** — all pre-pilot gates are materially passed.

**PILOT-AUTHORIZED does not mean paper-mainline-approved.** No candidate is protected by sunk cost or directory location.

---

# Gate 1 — Natural and important RQ

Ask whether the problem is real, durable, meaningful for NLP/LLMs, easy to explain, method-independent, and non-obvious.

Reject benchmark cells, method-first questions, obscure distinctions, and generic competence reporting.

**PASS:** easy to understand, important enough to anchor a Main paper, hard to answer.

---

# Gate 2 — Genuine scientific tension

A candidate needs real uncertainty, not merely an unmeasured number.

Prefer multiple plausible explanatory accounts, a consequential contested modeling/measurement decision, or a mechanism/boundary question where different outcomes change understanding.

A/B is useful but not mandatory. Keep the explanatory space open when more accounts are natural.

**PASS:** multiple scientifically meaningful outcomes are plausible before the experiment.

---

# Gate 3 — Data / evidence identify the claim

For every load-bearing claim write:

> **data / observation / controlled manipulation / intervention → scientific quantity → claim**

Audit unit of analysis, gold/state vs estimand, ambiguity, leakage, manipulation leverage, and naturalness.

Prefer natural data, official/provider-defined state, real human behavior, published materials, benchmark-native gold when it truly matches the estimand, and controlled causal interventions.

Constructed stimuli are allowed when minimal, natural, interpretable, independently defensible, and not an elaborate hypothesis-shaped synthetic world.

Canonical warning: **L02 died because UCCA DNI/INI did not provide gold for whether a specific filler was supported by the current discourse. Gold ≠ estimand.**

**PASS:** the evidence is the simplest credible route that directly identifies the scientific quantity.

---

# Gate 4 — Paper-level novelty and ownership

Novelty is not ingredient novelty.

Prior work may own the object, dataset, parent phenomenon, method, distinction, or one subclaim. What must remain distinctly ours is:

> **framing/narrative + decisive scientific operation + central conclusion + consequence**

Search classic parent work, current ACL/EMNLP/NAACL, direct follow-ups, and relevant ICLR/ICML/NeurIPS.

Mandatory reviewer compression:

> **“This is just ______.”**

If one or a few papers accurately compress the entire proposed paper, **KILL**.

Do not kill merely because the parent is old or one ingredient exists. Do kill “existing paper + another model/dataset/probe/cleaner control” when that is the whole identity.

**PASS:** a strong reviewer would recognize an independent paper beside the nearest work.

---

# Gate 5 — Outcome robustness and scientific depth

Do not authorize a topic whose value depends on one lucky effect.

Ask:

> **If the first expected account loses, does the RQ still produce a meaningful answer?**

Healthy outcomes include another account, meaningful boundary, correction, preservation/equivalence that resolves a consequential question, or causal repair.

A useful paper often grows from:
> core answer → why/where/when/validation → consequence

**PASS:** the RQ survives hypothesis failure and has natural depth without padding.

---

# Gate 6 — Main-level calibration

Compare continuously with the strongest structurally relevant ACL / EMNLP / NAACL Main work; use award papers as high-end calibration, not templates.

Compare RQ scale, scientific tension, data/gold, identification, full-paper novelty, depth, consequence, and memorability.

Mechanistic work needs causal discrimination; measurement work needs construct validity.

Ask:

> **If the result were strong and clean, would this look like an independent Main contribution or a competent narrow study?**

**PASS:** capable of sitting beside strong Main work on its load-bearing dimensions.

---

# Gate 7 — Anomaly robustness

When a candidate starts from an “established anomaly,” audit whether it is actually established.

Evidence strength, strongest to weakest:
1. multiple independent works with large/stable effects and public artifacts;
2. one strong Main/award parent with public artifacts plus cheap independent reproduction;
3. one strong parent whose phenomenon is cheaply reproducible;
4. one opaque/single-setting report whose effect is seed/setup sensitive.

Check effect size/stability, model/setting breadth, public code/data/config, and whether independent reproduction is required before mechanism work.

A paper report is not automatically an established phenomenon.

**PASS:** the project is not secretly gambling its existence on a fragile parent effect.

---

# Gate 8 — Why-space / narrative-space

After finding an anomaly or gap, map the surrounding **natural explanatory space**, not only exact-title collisions.

Lay out the most dangerous recent Main/top-venue work and ask:
- what broad explanations are already owned?
- what natural mechanisms/boundaries/consequences remain?
- does the RQ remain natural without naming a layer, metric, feature direction, output format, or intervention?
- can the full narrative remain ours without technical compression?

Canonical warning: **L11 died because the broad gradient/learning-pressure why-space became crowded; preserving novelty forced the project toward narrow coherence/output-format/function-space cells and reintroduced phenomenon risk.**

If novelty survives only after shrinking the claim into a technical corner, default **KILL / HOLD** even when that corner is technically new.

**PASS:** after surrounding literature is laid out, a broad, natural, independent explanatory space remains.

---

# Deep audit before pilot authorization

Record compactly inside the candidate package:

1. **RQ** — one sentence, example, importance, uncertainty.
2. **Scientific accounts** — plausible explanations and distinguishing observations.
3. **Data/evidence** — source, identification chain, validity, artifacts.
4. **Novelty** — closest ownership, reviewer compression, surviving identity.
5. **Outcome robustness** — informative branches, depth, consequence.
6. **Main calibration** — strongest structural references and weakest dimension.
7. **Anomaly robustness** — how established the parent really is.
8. **Why-space** — what nearby work owns and whether broad explanation space remains.
9. **Minimum decisive pilot** — cheapest load-bearing uncertainty and kill/reconstruct logic.

Do not create duplicate checklist files.

---

# Pilot design rule

The first pilot is not a miniature full paper. Resolve the cheapest load-bearing uncertainty first.

Good first pilots include data/gold audit, exact parent reproduction, matched causal fork, teacher-forcing vs free-running, controlled branch/checkpoint comparison, or one decisive boundary.

Do not begin with a model zoo, dozens of datasets, expensive scaling, or decorative ablations.

---

# Kill / reconstruct logic

A hypothesis losing is not a topic failure.

**RECONSTRUCT** when another account wins, a meaningful boundary appears, or a stronger explanation emerges.

**KILL** when data cannot identify the quantity, the anomaly is too fragile, the narrative is owned, why-space collapses to technical corners, remaining claims are trivial/narrow, or no credible Main consequence remains.

Do not protect sunk cost.

---

# Final authorization test

Before target-model compute, all must be materially YES:

1. Worth knowing?
2. Natural and easy to explain?
3. Genuinely non-obvious?
4. Evidence really identifies the claim?
5. Paper-level identity remains ours?
6. More than one outcome remains useful?
7. Enough natural depth for a Main paper?
8. Comparable to strong ACL/EMNLP/NAACL Main work?
9. If anomaly-based, is the parent phenomenon robust enough?
10. After the strongest neighboring literature is laid out, is the natural why-space still broad?

Any material NO blocks promotion.

> **Judge the question, evidence, ownership, robustness, and paper shape — not how clever the method sounds.**
