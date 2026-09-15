# L41 Registration Record

**Registered ID:** `L41`  
**Name:** **Does Parameter Learning Respect Semantic Commitment?**  
**Status:** `PILOT-AUTHORIZED — E01 ONLY`  
**Registered:** 2026-09-15  
**Target venue class:** ACL / EMNLP / NAACL Main  
**Origin:** `WALL-BE — semantic commitment / parametric factual uptake`

## Canonical scientific question

> **When language is used as training data, does a language model update its persistent world beliefs according to what the sentence semantically commits to, or mainly according to propositions that are mentioned / locally repeated?**

## Canonical project identity

This project studies the **language → parameter knowledge-acquisition operator**.

It is **not**:

- a test of whether LMs understand implicatives/factivity;
- a presupposition or veridicality benchmark;
- a generic negation paper;
- another belief-insertion method;
- another co-occurrence-vs-reasoning benchmark;
- an interpretability/mechanism project yet.

The identifying operation is the preregistered `manage/fail × polarity` two-way-implicative checkerboard, which makes **surface polarity and semantic commitment disagree** while measuring the same later neutral factual-belief quantity.

## Canonical documents

1. `PROJECT_BRIEF.md` — background, research question, hypotheses, desired paper narrative, novelty boundary, and initial experiment.
2. `PILOT_CARD.md` — frozen E01 protocol, gates, estimands, power/compute rules, and anti-gambling constraints.
3. `README.md` — compact candidate overview and ownership boundary.
4. `../../search_rounds/2026-09-15_WALL_BE_FINAL_SELECTION.md` — Selection audit and promotion rationale.

## Authorization boundary

`PILOT-AUTHORIZED — E01 ONLY` means:

- Selection is passed **on paper**;
- one bounded experiment is justified;
- no mother result or effect size has yet been established;
- no E02/full-study/model-zoo/mechanism expansion is authorized.

## E01 scientific discriminator

Critical conditions:

```text
M+ : managed to p       =>  p
M- : did not manage to p=> ¬p
F+ : failed to p        => ¬p
F- : did not fail to p  =>  p
```

Primary interaction:

```text
I = [U(M,+) - U(M,-)] - [U(F,+) - U(F,-)]
```

where `U` is the pre→post change in neutral Yes-vs-No log-odds about `p` after the training context has been removed.

A semantic-learning account predicts a checkerboard. Mention/co-occurrence and generic local-negation accounts do not.

## Pass / stop principle

The project is not authorized to search for a positive result.

A clean semantic checkerboard, a clean mention-dominant pattern, or a clean surface-polarity pattern can all be scientifically informative **provided**:

- the exact constructions pass the forward semantic-understanding gate;
- direct assertion/denial training produces resolvable signed factual uptake;
- the critical E01-B result is untouched by model/LR/prompt/verb shopping.

Instrument failure, lexical one-cell pathology, or post-hoc effect hunting does not justify reconstruction under the L41 name.
