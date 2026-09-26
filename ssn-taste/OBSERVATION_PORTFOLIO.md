# Observation Portfolio — Sasano-Taste Search

Last reset: 2026-09-26

This file is the **only entry point for fresh research directions** before an RQ exists.

Current portfolio: **empty**.

S01–S12 are historical failures and must not be copied back into this file as positive examples.

---

# Rule 0 — An Observation Card is not a candidate topic

An Observation Card records an already existing empirical result that may deserve explanation.

It is **not**:
- an Sxx topic;
- a research question;
- a mechanism hypothesis;
- a synthetic experiment idea;
- a literature gap.

No card may receive an Sxx number.

---

# Required card schema

## OXX — Short factual label

**Status:** RAW OBSERVATION | REPRODUCTION-PENDING | REPRODUCED | AUDIT-PASSED | KILL

### 1. Source
Exact paper / table / figure / Slack thread / existing experiment.

### 2. Exact observation
Record actual numbers, directions, subset differences, or stable behavior.

Do not write only “surprisingly better/worse”.

### 3. Natural setting
Why this observation exists independently of our custom experiment.

### 4. Baseline expectation
Write:

> Based on **X**, one would expect **Y**, but the observation is **Z**.

X must be documented:
- direct prior claim;
- accepted method assumption;
- clear capacity/information/logic bound;
- genuinely comparable earlier result.

“Intuitively”, “humans would”, or “more should help” is insufficient.

### 5. Stability evidence
What is known across:
- seeds;
- prompts/contexts;
- datasets/subsets;
- model families;
- scale.

If unknown, say so explicitly.

### 6. Source-author explanation
What explanation did the source already give?

### 7. Explanation ownership
Did the source already test that explanation?
Did appendix/follow-up work perform the decisive contrast?

### 8. Why unresolved
One precise unknown that remains after reading source + appendix + follow-ups.

### 9. Anchor reproduction plan
Smallest faithful reproduction of the original observation.

At this stage:
- do not add a new theory;
- do not build a synthetic micro-world;
- do not optimize a prompt for a stronger effect.

### 10. Reproduction result
Fill only after execution.

### 11. Surprise / direct-claim audit
After reproduction, decide whether the result still modifies a real prior/baseline.

### 12. Verdict
Only:
- **KILL**
- **AUDIT-PASSED → may form an RQ**

---

# Promotion rule

A card can leave this file for RQ formation only if:

1. the empirical anchor exists independently of our custom assay;
2. the direction is reproduced or supported by equivalently strong multi-source evidence;
3. the surprise/direct-prior baseline is documented;
4. the simplest trivial explanation does not already dissolve the result;
5. source / appendix / follow-up have not already completed the decisive explanation.

Even then, it is **not selected**.

The next stages are:
RQ formation → instrument preflight → Sxx registration.
