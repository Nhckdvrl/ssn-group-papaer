# L14 — Bounded Pilot Card

**Registered:** 2026-09-11  
**Authorization:** ONE bounded kill-oriented pilot after stimulus audit.  
**Paper mainline:** NOT APPROVED.

## 1. Question the pilot must answer

> **Is there evidence that current LLM negation robustness is target-insensitive — i.e. models or negation-focused interventions correctly react to proposition-level negation but over-apply polarity reversal when `not` is metalinguistic?**

The pilot is not authorized to answer generic questions about negation representations, layers, or function vectors.

---

## 2. E01 — Two-sided target-selection profile

### Data

Use **40–60 human-audited lexical/discourse bases** from the contract in `DATA_AND_GOLD.md`.

For each base score at minimum:
- POS control;
- DN;
- MN;
- non-negated / explicit paraphrase control.

The same world-state target proposition is used within a base.

### Models

Start with **two open model families** with different training lineages and enough capability that failure cannot be dismissed as general incompetence.

A third family is allowed only if the first two disagree enough that family heterogeneity determines the go/no-go decision.

Do not run a model zoo.

### Primary quantities

Per base/model:

- `DN_correct`: model reverses the world-state proposition when negation is descriptive;
- `MN_correct`: model preserves the world-state proposition when negation rejects the wording/representation;
- `negation_blindness`: DN error conditional on passing the positive/paraphrase control;
- `metalinguistic_overnegation`: MN error conditional on passing the positive/paraphrase control.

Report paired uncertainty over **bases**, not generations.

### E01 success signal

A stable two-sided dissociation exists that is not explained by lexical-control failures and is not driven only by scalar-implicature items.

E01 alone does **not** authorize a paper.

---

## 3. E02 — Predeclared negation-sensitivity intervention

Use an intervention from prior work rather than inventing one after inspecting E01.

Primary intervention is the warning-based framing illustrated in Barreto & Jana (Findings EMNLP 2025):

> **Pay attention to any negation and distractors (sentences which don't make sense).**

Their task then asks the ordinary True/False question. For L14, freeze the warning sentence verbatim and append the unchanged L14 proposition-level response instruction. Do not tune its wording on pilot results.

Source:
- https://aclanthology.org/2025.findings-emnlp.761/

Apply the same intervention to the exact E01 items.

### Primary causal contrast

For each model compute paired changes:

- `ΔDN = DN_correct(warning) - DN_correct(baseline)`
- `ΔMN = MN_correct(warning) - MN_correct(baseline)`

The strongest prospective result is:

> `ΔDN > 0` while `ΔMN < 0`

or an equivalent continuous probability shift showing that greater target-agnostic sensitivity to `not` improves ordinary negation but increases metalinguistic over-negation.

This is the pilot's main contribution test because it changes how an existing negation-improvement result should be interpreted.

### Required specificity controls

- POS/paraphrase controls must not degrade comparably;
- the trade-off must survive after removing scalar-implicature items;
- label-order/token controls for scored open models;
- paired analysis within lexical base.

---

## 4. E03 — Context account, conditional authorization only

Do **not** run E03 if E01/E02 show no target-selection leverage.

If the route survives, use the already-audited classical manipulation:

- context licenses MN before `not X`;
- no/pre-DN context;
- later correction resolves the reading.

Use independent forks at matched textual checkpoints to estimate world-state commitment without feeding probe answers back into the continuation.

Accounts:

### A — polarity-first / repair

The model initially moves toward propositional negation after `not X`; later corrective context repairs the state. Pre-context has limited ability to prevent this move.

### B — context-sensitive target selection

Pre-disambiguating context changes the interpretation of `not` immediately; the MN trajectory need not pass through the descriptively negated world state.

This is the first allowed explanatory development. Generic hidden-state probing is not authorized before this behavioral discrimination is attempted.

---

## 5. Hard kill rules

Archive the route after E01/E02 if any of the following holds:

1. capable models are essentially ceiling on DN and MN, leaving no consequential target-selection issue;
2. the warning/intervention produces no meaningful DN–MN differential and E01 contains no independent strong target-selection pattern;
3. apparent MN failures disappear after lexical/paraphrase controls;
4. the signal is confined to `some→all` / implicature-cancellation examples;
5. human audit shows unstable intended readings or world-state gold;
6. a fresh direct owner is found for the DN-improvement/MN-over-negation trade-off or the same target-selection computation.

Do **not** respond to a kill by adding probes, layers, more prompts, or more models.

---

## 6. Promotion rule

Return the candidate to **RE-SELECTION**, not automatic full study, if E01/E02 produce a stable signal.

A promotion review must answer:

1. What is the current paper identity after seeing the result?
2. Does the exact winning claim still survive the ownership audit?
3. Does E03 actually distinguish the remaining live accounts?
4. Is there enough non-scalar subtype breadth to support `negation-target selection` rather than one construction?
5. Does the result change a real conclusion about negation robustness, not just benchmark coverage?

Only then may the project become GO-TO-FULL-STUDY.

---

## 7. Pre-pilot checklist

- [ ] 40–60 bases drafted from human/classical sources and author linguistic judgment, not LLM-generated main data.
- [ ] independent human audit of a sufficient pilot subset for naturalness, target reading, and world-state gold.
- [ ] scalar cases are a minority / non-load-bearing.
- [x] exact warning intervention frozen from prior work.
- [ ] two model families and decoding/scoring protocol frozen.
- [ ] analysis operates over paired bases.
- [ ] no hidden-state/mechanistic experiment queued before E01/E02 decision.

# Verdict

**PILOT-AUTHORIZED, STRICTLY BOUNDED.**

Authorization means the candidate has survived the prospective novelty/data audit enough to justify this decision experiment. It does not mean L14 is a viable Main paper yet.
