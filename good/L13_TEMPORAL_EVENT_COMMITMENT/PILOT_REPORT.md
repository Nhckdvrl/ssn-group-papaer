# L13 Pilot Report — 2026-09-11

Runs: `results/pilot_v1/`. Five checkpoints, four families
(Qwen3-8B, Qwen3-32B, Llama-3.1-8B-Instruct, Olmo-3-7B-Instruct-DPO, Gemma-3-12B-IT).
All numbers are label-probability mass averaged over 6 option permutations, paired
bootstrap over the 40 base scenarios (10k resamples, 95% percentile CI).

**These results are provisional: `before_neutral` gold has not yet been human-validated
(`DATA_AND_GOLD.md` §6), and the ghost-node detector is a lexical heuristic.**

---

## 1. C1 — REJECTED as stated

Asked directly, models do **not** over-commit on an unresolved `before`-clause.

| model | `after` P(YES) | `before_neutral` P(ND) | `neutral_gap` |
|---|---|---|---|
| Gemma-3-12B | 0.997 | 0.864 | +0.045 [+0.004, +0.101] |
| Qwen3-8B | 0.989 | 0.752 | +0.005 [−0.040, +0.049] |
| Llama-3.1-8B | 0.654 | 0.594 | +0.108 [+0.080, +0.138] |
| Olmo-3-7B | 0.549 | 0.263 | −0.017 [−0.050, +0.001] |

The matched non-temporal control shows the middle label is available and used. Olmo-3
answers `NO` for both unresolved conditions (0.73 / 0.65) — a label-usage property, not
a temporal effect; this is exactly what the control was for.

**The original bet lost.** Models represent the non-veridicality of `before`.

## 2. C2 — SUPPORTED, but with an important restriction

Same passage, same probe, after the model writes its own chronological timeline
(difference-in-differences against a paraphrase-first arm of matched form):

| model | `timeline − paraphrase` on `before_neutral` |
|---|---|
| Gemma-3-12B | **+0.332** [+0.227, +0.442] |
| Qwen3-32B | **+0.325** [+0.209, +0.444] |
| Qwen3-8B | **+0.171** [+0.084, +0.270] |
| Llama-3.1-8B | **+0.098** [+0.075, +0.121] |
| Olmo-3-7B | **+0.075** [+0.019, +0.142] |

Five checkpoints, four families, all positive, no CI covering zero. On the matched
non-temporal passage the effect is zero (Gemma −0.000, Qwen3-8B +0.000).

**Restriction (E05).** A *non-generative* temporal demand — the model answers a
multiple-choice ordering question with a single letter, so no declarative sentence
about the target event enters the context — does **not** reproduce the effect:
`order_mc − topic_mc` on `before_neutral` is +0.020 (Qwen3-8B), −0.019 (Llama),
+0.072 (Olmo), +0.014 (Gemma). C4 (internal contamination by the connective's
representation) is therefore **not supported** and is withdrawn as framed.

The effect lives at the point where the model **emits a structured representation**,
not in comprehension.

## 3. The finding that actually carries the project (E04)

> **All numbers in this section are v2-detector numbers.** The v1 lexical detector was
> found defective during author adjudication (it counted a copied `before`-clause as an
> assertion) and every v1 figure is superseded. See `data/GOLD_AUDIT_v1.md`: v2 was
> validated against 160 hand-adjudicated generations, agreement 159/160, and its single
> error is a false negative, so all rates below are **lower bounds**.

Rate at which the target event is emitted as a plain realized node of the structure:

**Plain timeline** ("List the events described in this passage in chronological order"):

| model | `before_neutral` | `before_cancel` | non-temporal control |
|---|---|---|---|
| Qwen3-32B | **1.00** | 0.35 | 0.10 |
| Llama-3.1-8B | **0.98** | 0.90 | 0.10 |
| Gemma-3-12B | **0.93** | 0.50 | 0.10 |
| Olmo-3-7B | **0.48** | 0.23 | 0.13 |
| Qwen3-8B | **0.45** | 0.18 | 0.10 |

The matched non-temporal open proposition ("Maya planned to submit the application")
is instantiated at ~0.10 in every model. The temporal construction, not the
uncertainty, is what forces instantiation.

**With an explicit prohibition** ("List only the events that actually happened … Do not
list events that did not happen **or whose occurrence the passage leaves open**"):

| model | `before_neutral` | `before_cancel` |
|---|---|---|
| Llama-3.1-8B | 0.98 → **1.00** (+3%) | 0.90 → **0.43** (−53%) |
| Olmo-3-7B | 0.48 → **0.63** (+32%) | 0.23 → **0.15** (−33%) |
| Gemma-3-12B | 0.93 → **0.78** (−16%) | 0.50 → **0.25** (−50%) |
| Qwen3-8B | 0.45 → **0.20** (−56%) | 0.18 → **0.03** (−86%) |

In all four the instruction removes **explicitly cancelled** events far more
effectively than **unresolved** ones; in two of four it does not reduce the unresolved
case at all. Qwen3-8B does respond to the instruction, so "instruction-resistant" is a
property of most, not all, of the set — stated that way rather than as a universal.

Hand-verified examples: under `before_cancel`, Gemma emits
`The crew put out the fire.` and `The crew never put out the fire.` in the same
four-line timeline; Qwen3-32B emits `Marcus returned the library book.` and
`Marcus never returned the library book.`

Secondary observation: the emitted order frequently follows surface clause order rather
than chronology (`Before A, B` listed as A then B), so what is produced is closer to
mention transcription than to ordering.

## 4. Status of the claims

| claim | status |
|---|---|
| C1 separability under direct probing | **rejected** — models defer correctly |
| C2 timeline-induced actualization | **supported** (5 checkpoints, 4 families), mediated by emitted text |
| C3 update asymmetry | **weakened** — the raw contrast is floor-confounded; the floor-aware `gold_update_*` version leaves Gemma symmetric (+0.024) and Olmo asymmetric (+0.502) |
| C4 internal representational coupling | **not supported** (E05) — withdrawn as framed |
| **C5 (new)** structure-building collapses `unresolved` into `realized`, and is instruction-resistant | **supported, provisional** — needs a validated detector and human gold |

## 5. Kill rule

The `PILOT_CARD.md` kill rule does **not** fire: conditions (3) and (5) fail
(|timeline effect| ≫ 3pp; large cross-family heterogeneity, 0.075→0.332).

## 6. Honest weaknesses

1. `before_neutral` gold is not human-validated. Blocking for any paper-level claim.
2. The ghost-node rate uses a lexical detector; §3 is currently descriptive-grade
   evidence promoted to a load-bearing role, which is not acceptable as-is.
3. E05's null removes the mechanistic route the project was originally going to take.
   What remains is a generation-time phenomenon, which is a different (and more
   applied) paper identity.
4. Reviewer compression risk is now: *"models are influenced by their own generated
   text."* The paraphrase control and the E04 instruction-resistance answer it, but
   only if §3 is made rigorous.

## 7. Next decisive step

Not more models. In order:

1. **Validate the gold and the detector.** Human annotation of `before_neutral`
   (§6 of `DATA_AND_GOLD.md`) and a human-checked sample of ghost-node judgements.
2. **Push the instruction manipulation to its limit.** If a one-shot demonstration, an
   explicit three-state output format (`realized / unresolved / not-realized`), or a
   direct "for each event, state whether the passage guarantees it happened" schema
   still leaves `unresolved` collapsed, the finding is strong and applied. If a
   three-state schema fixes it completely, the finding shrinks to "ask for the right
   schema", and the project must be re-audited.

Step 2 is the cheapest question that can still kill the project.

---

# Addendum — E06: does an explicit three-state schema repair the collapse? (2026-09-11)

This was the preregistered kill question from §7. Two forms, all five checkpoints:

- **E06a (free):** the model builds its own table, `<event> :: realized | unresolved |
  not-realized`, with the three statuses defined in the prompt. Its own row for the
  target event is parsed.
- **E06b (forced slot):** the same task with permuted neutral status codes, with the
  target's table row teacher-forced up to the status slot, so the status is scored
  rather than parsed (6 permutations).

## Result — the schema does not repair it, but the picture is not uniform

`before_neutral`, free table, status assigned to the target event:

| model | realized | unresolved | not-realized | absent |
|---|---|---|---|---|
| Llama-3.1-8B | **0.65** | 0.13 | 0.13 | 0.10 |
| Gemma-3-12B | **0.45** | 0.45 | 0.05 | 0.05 |
| Qwen3-8B | **0.43** | 0.28 | 0.15 | 0.15 |
| Olmo-3-7B | 0.28 | **0.38** | 0.05 | 0.30 |
| **Qwen3-32B** | 0.05 | **0.50** | 0.33 | 0.13 |

Forced slot, `before_neutral`: P(REALIZED) is modal for Llama (0.53), Olmo (0.61),
Gemma (0.56) and Qwen3-8B (0.43); Qwen3-32B is the exception (0.12).

## The honest reading

1. **The kill rule does not fire.** In four of five checkpoints, a first-class
   `unresolved` slot does not recover the judgement the same model gives when asked
   directly (Gemma 0.864 → 0.229; Qwen3-8B 0.752 → 0.128).
2. **Part of that drop is a format effect, not a temporal effect.** The matched
   non-temporal control loses open-state mass too (Qwen3-8B +0.589 vs +0.624 on
   `before_neutral`; Gemma +0.310 vs +0.635). Only Gemma shows a large
   temporal-specific excess (+0.325). **E06b is therefore not the load-bearing
   evidence**; E04's instruction-resistance is.
3. **Scale reverses it — and that sharpens the claim rather than killing it.**
   Qwen3-32B builds the three-state table correctly (unresolved 0.50, realized 0.05).
   Yet the *same checkpoint* lists the unresolved event as a plain node in a plain
   timeline **100%** of the time, and its downstream commitment shift is the largest
   in the set (`timeline − paraphrase` = **+0.325** [+0.209, +0.444]).

   So the collapse is not "the model cannot represent the open state". It is a
   property of **the representation it is asked to produce**: given a plain timeline —
   the representation every event-graph / timeline-extraction / agent-state pipeline
   actually asks for — even a model that demonstrably knows the three states
   instantiates the unresolved event unconditionally.
4. **A matched contrast makes this concrete.** The same open proposition introduced
   non-temporally ("Maya planned to submit the application") is simply *omitted* from
   the table (absent 0.85–0.88). Introduced in a `before`-clause, it is listed — and
   listed as realized. The temporal construction, not the uncertainty, is what forces
   instantiation.

## Consequences for the project

- **C5 is refined**, not withdrawn: *a plain timeline representation is not
  truth-preserving; unresolved events are instantiated as realized, and neither an
  explicit prohibition (E04) nor, in most models, an explicit `unresolved` slot (E06)
  repairs it — even in a model that assigns the correct status when the schema asks
  for one.*
- **New durability risk, declared:** the schema-level collapse weakens sharply from
  Qwen3-8B to Qwen3-32B. Before any paper-level claim, a within-family scale ladder is
  now mandatory (Qwen3 0.6B/1.7B/4B/8B/14B/32B are all in the local cache). If the
  plain-timeline collapse also disappears with scale, the applied claim dies; if only
  the schema version does, the paper's target is the plain-timeline representation.
- Human validation of `before_neutral` gold and of the ghost-node detector remains
  blocking, and is now the first item, since §3 and §4 above are both detector-based.

## Next

1. Human validation (gold + detector sample).
2. Qwen3 scale ladder on the plain-timeline collapse and on `timeline − paraphrase`.

Nothing else should be run before those two.

---

# Addendum 2 — E07: Qwen3 scale ladder, and the corrected detector (2026-09-11)

Addendum 1 raised a durability risk: the schema-level collapse looked weaker at 32B, so
a within-family ladder was declared mandatory. It was run on six Qwen3 checkpoints with
identical items, probes and controls.

| Qwen3 | plain-timeline ghost rate, `before_neutral` | non-temporal control | direct P(NOT_DETERMINED) | `timeline − paraphrase` commitment shift |
|---|---|---|---|---|
| 0.6B | 0.475 | 0.10 | 0.387 | +0.122 [+0.085, +0.163] |
| 1.7B | 0.400 | 0.10 | 0.617 | +0.159 [+0.066, +0.250] |
| 4B | 0.475 | 0.10 | 0.695 | +0.379 [+0.275, +0.486] |
| 8B | 0.450 | 0.10 | 0.752 | +0.171 [+0.084, +0.270] |
| **14B** | **0.975** | 0.10 | 0.696 | +0.293 [+0.146, +0.442] |
| **32B** | **1.000** | 0.10 | 0.126 | +0.325 [+0.209, +0.444] |

**The durability risk is resolved in the opposite direction to the worry.** The
plain-timeline collapse does not decay with scale; it **jumps** between 8B and 14B and
is total at 32B, while the matched non-temporal control stays flat at 0.10 across all
six checkpoints. The commitment shift is present at every scale with no downward trend.

Note the dissociation this produces inside a single checkpoint: Qwen3-32B assigns
`unresolved` correctly when the schema asks for it (Addendum 1: 0.50 unresolved vs 0.05
realized), yet instantiates the same event as a plain realized node **100%** of the time
when asked for an ordinary timeline, and shows the second-largest commitment shift.
Ability to represent the open state is not the binding constraint; the representation
being requested is.

Direct competence is not monotone either: P(NOT_DETERMINED) rises 0.39 → 0.75 through
8B and then collapses to 0.13 at 32B, which answers `NO` — a pragmatic inference the
probe wording excludes. Olmo-3 does the same. This is reported as a distinct behaviour,
not pooled with answering `YES`.

## Corrections carried out in this pass

1. **Detector defect found and fixed** (`src/ghost_detect.py` v2; `data/GOLD_AUDIT_v1.md`).
   Qwen3-8B's `before_neutral` rate was inflated from a true 0.45 to 1.00 by v1.
   All §3 figures are now v2 and were re-derived from the stored raw generations.
2. **v2 validated** on 160 hand-adjudicated generations: 159/160, single error
   conservative. Reported rates are lower bounds.
3. **Gold upheld for all 40 items**, with item-level `pragmatic_bias` recorded
   (14 `no_leaning`, 4 `yes_leaning`, 22 `neutral`) as the nuisance covariate the
   `before` norming literature identifies.
4. **External validation remains open** and is the only blocking item left: the author
   adjudicated the gold, which is not independent annotation.

## Claim state after this pass

| claim | status |
|---|---|
| C1 direct over-commitment | **rejected** |
| C2 timeline-induced actualization | **supported**, 9 checkpoints, 4 families, no scale decay |
| C3 update asymmetry | **weakened**, floor-confounded |
| C4 internal coupling without generation | **rejected** (E05) |
| **C5 plain-timeline instantiation of unresolved events** | **supported**, strengthens with scale, ~0.10 non-temporal control, partially instruction-resistant |
