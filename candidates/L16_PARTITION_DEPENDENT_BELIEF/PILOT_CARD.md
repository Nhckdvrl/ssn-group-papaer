# L16 — Bounded Pilot Card

**Freeze date:** 2026-09-11, before model outputs.  
**Authorization:** **E01 + conditional E02 only.**  
**Goal:** kill the topic cheaply unless the specific partition-induced-prior signature survives strong-model reasoning and confound controls.

---

# 0. Decision to be made

The pilot answers one question:

> **Does an informationally irrelevant repartitioning of an unchanged hypothesis space induce a reproducible, directional change in LLM credence toward the partition-specific ignorance prior, despite normal reasoning and explicit recognition of partition equivalence?**

A generic prompt effect is a **kill**, not a weaker success.

---

# 1. Models and inference

Use the same two local model families as the recent bounded pilots:

- **Qwen3-32B**
- **Mistral-Small-24B**

This is a pilot, not the final model population.

Primary mode:

- normal reasoning / CoT allowed;
- greedy decoding;
- seed `0`;
- `max_tokens = 1024`;
- identical system prompt across conditions;
- no few-shot examples that reveal the expected partition effect.

**Direct/no-reasoning mode is not a primary condition.** It may be run as a cheap diagnostic after prompts are frozen, but an effect that exists only when reasoning is blocked does not save the topic.

---

# 2. Stimuli

Primary clean grid from `DATA_AND_GOLD.md`:

- 48 independent base scenarios;
- 4 domains × 12 bases;
- 9 atomic mutually exclusive/exhaustive hypotheses per base;
- fixed target `H1`;
- all atoms and evidence byte-identical across matched conditions;
- only the partition map changes.

Per base in E01:

1. `FLAT`
2. `M2`
3. `M3a`
4. `M3b`
5. `M9`

Total primary E01 cells per model: **48 × 5 = 240**.  
Two models: **480 cells**.

Classic Fox/Rottenstreich/Ding/Feldman anchor items may be run separately. They do not enter the primary causal estimate.

---

# 3. Smoke run

Before the full E01 run:

- 4 bases, one from each domain;
- all 5 partition conditions;
- both models if possible;
- total = 40 cells.

Smoke may fix only:

- formatting;
- parser bugs;
- tokenizer/logprob plumbing;
- truncation;
- invalid mutually-exclusive/exhaustive construction.

Smoke may **not** change effect thresholds, primary contrasts, or scientific interpretation after outputs are seen.

Any pipeline change is recorded in `EXPERIMENTS.md` before the full run.

---

# 4. E01 — Same world, different partition

## Primary contrast

For scenario `i`:

`Delta29_i = P_i(H1 | M2) - P_i(H1 | M9)`

Account B predicts `Delta29 > 0` because the target singleton is pulled toward `1/2` under `M2` and `1/9` under `M9`.

## Secondary preregistered signature

Let:

`P_M3 = (P_M3a + P_M3b)/2`

Expected directional ordering:

`P_M2 > P_M3 > P_M9`

Also report:

- partition spread;
- `|P_M3a - P_M3b|`;
- FLAT-relative signed pull toward each condition's `1/M` anchor;
- parse-failure rate;
- per-domain paired effects.

## Statistics

Independent unit = base scenario.

Use scenario bootstrap (10,000 resamples) retaining all matched cells for each resampled base.

Primary report per model family:

- mean `Delta29` and 95% bootstrap CI;
- median `Delta29`;
- proportion of scenarios with `Delta29 > 0`;
- proportion satisfying `M2 > M3 > M9`;
- domain-stratified mean `Delta29`.

No cell-level significance tests.

---

# 5. E01 survival gate

E01 proceeds to E02 **only if both model families** satisfy all primary conditions:

1. mean `Delta29 >= 0.05` (at least a 5 percentage-point shift);
2. scenario-bootstrap 95% CI lower bound for mean `Delta29 > 0`;
3. at least **65%** of independent scenarios have `Delta29 > 0`;
4. at least **3 of 4 domains** have positive mean `Delta29`;
5. CoT/normal-reasoning outputs are parseable on at least 95% of cells.

Additionally, the mechanism remains plausible only if:

- mean/median `M3` lies between `M2` and `M9` in aggregate;
- arbitrary `M3a/M3b` regrouping sensitivity is substantially smaller than the `M2-M9` contrast. Pre-registered warning boundary: `mean |M3a-M3b| > 0.5 × mean |M2-M9|` means the clean cell-count account is not established and E02 must treat semantic grouping as a live confound.

If either model family is approximately invariant, or only the weaker family shows a large effect, **KILL the current route**. Do not pivot to "some models are biased."

---

# 6. E02 — Is this a partition prior, or just prompt sensitivity?

Run E02 only after E01 passes the survival gate.

## E02-A: explicit equivalence awareness

For all 48 bases, present matched `M2` and `M9` descriptions and ask separately:

> Do these displays contain different atomic possibilities or different evidence about which possibility occurs?

Gold: **NO**.

To support the planned dissociation, both model families must achieve **>= 90% equivalence accuracy**.

If the model simply thinks the displays encode different worlds/evidence, the exciting claim is unsupported.

## E02-B: explicit arbitrary-group disclaimer

Rerun the primary probability query on a preregistered 24-base balanced subset with the sentence:

> `The grouping is only a display convention; it does not add, remove, or change any possibility or evidence.`

Use `M2`, one fixed `M3`, and `M9`.

A strong target signature is not merely an implicit misunderstanding; it survives explicit equivalence information.

Required to keep the locked paper identity alive on both model families:

- `Delta29_disclaimer` remains positive with bootstrap lower bound > 0;
- mean `Delta29_disclaimer >= 0.025`;
- and retains at least **50%** of the corresponding no-disclaimer E01 effect on the same 24 bases.

If the effect collapses under one explicit sentence that states the already-correct extensional relation, current C2 is too weak for the intended paper identity and requires re-selection before any further experiment.

## E02-C: readout robustness

On the same 24-base subset, obtain a non-numeric relative readout if the local vLLM stack exposes next-token logits.

Prompt ending:

```text
A = the target proposition is true
B = the target proposition is not true
Which is more plausible? Answer only A or B.
```

Prevalidate that the answer labels are cleanly scored tokens for each tokenizer. Record normalized logit mass / log-odds for A versus B **before generation**.

The expected directional test is only cross-partition:

`logit_A(M2) > logit_A(M9)` / corresponding log-odds shift.

This readout is not called calibrated probability.

If the phenomenon is strong in verbal percentages but absent in this independent readout, the broad word **belief** is not licensed. Stop and re-select before reframing as confidence-elicitation behavior.

## E02-D: stronger-evidence attenuation

For the same 24-base subset, use the preconstructed stronger-evidence counterpart from `DATA_AND_GOLD.md` and repeat `M2/M3/M9`.

Classic partition-prior account predicts attenuation as diagnostic evidence strengthens.

This is a mechanism discriminator, not an absolute probability benchmark. Report the ratio:

`attenuation = |Delta29_strong| / |Delta29_weak|`

A ratio < 1 supports the classic account. Failure to attenuate does not alone falsify C1, but if the total E02 pattern also lacks `1/M` directionality, the remaining result compresses into generic prompt sensitivity and the current paper identity dies.

---

# 7. Accounts decided by the pilot

| Account | E01 | Equivalence | Disclaimer | `1/M` / evidence pattern | Verdict |
|---|---|---|---|---|---|
| A: extensional/partition-invariant belief | near-zero | correct | near-zero | none | kill phenomenon |
| B: partition-induced ignorance prior | directional M2>M3>M9 | correct | persists | stronger under weak evidence | target survives |
| C: generic prompt sensitivity | noisy/non-directional | variable | unstable | no `1/M` law | kill current identity |
| D: semantic grouping | M3a/M3b large | may be correct | variable | grouping-content dependent | kill/reselect |
| E: verbal confidence artifact | verbal only | correct | may persist | non-numeric readout null | kill/reselect |

---

# 8. Hard stop rules

Immediately archive / enter the next K-ID if:

- E01 survival gate fails;
- effect only exists without CoT;
- effect is restricted to one model family;
- matched alternatives/order control removes it;
- E02 reveals no equivalence knowledge;
- result is generic non-directional semantic-invariance failure;
- only the verbal numeric scale moves;
- a direct current owner of the locked computation appears.

**Forbidden rescue narratives without a new selection audit:**

- "partitioning prompts affects LLMs";
- "confidence is prompt sensitive";
- "more options lower confidence";
- "grouping evidence changes decisions";
- "reasoning fixes the bias";
- "we can debias with a prompt";
- "we found a weak-model-only cognitive bias."

---

# 9. What happens after E02

Nothing is automatically authorized.

If B survives with both families, write a pilot report and **return to selection**. Re-run the ownership audit on the exact observed magnitude/readout before any:

- broader model sweep;
- natural deployment task;
- downstream abstention/decision C3;
- mechanism/hidden-state experiment;
- mitigation method.

If the paper identity changes, authorization expires.

> **Evidence survives claim mutation; authorization does not.**

---

# READY STATE

## **READY TO RUN**

The pilot has fixed data units, prompts, readouts, accounts, thresholds, statistics, and kill rules. No additional search/design stage is required before smoke.