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

---

# Addendum 3 — E08 external validity, E10 mitigation, E11 moderation (2026-09-11)

## E11 — the effect is not "the model thinks it probably happened"

Ghost rate on `before_neutral`, split by the item-level `pragmatic_bias` recorded in the
gold audit:

| model | no_leaning (n=14) | neutral (n=22) | yes_leaning (n=4) |
|---|---|---|---|
| Qwen3-8B | **0.643** | 0.318 | 0.500 |
| Olmo-3-7B | **0.571** | 0.409 | 0.500 |
| Llama-3.1-8B | 0.929 | 1.000 | 1.000 |
| Gemma-3-12B | 0.857 | 0.955 | 1.000 |
| Qwen3-32B | 1.000 | 1.000 | 1.000 |

There is **no monotone increase** with yes-leaning bias, and in the two models with
headroom the rate is *highest* on items whose blocking event makes non-occurrence most
plausible. The plausibility account — the model instantiates the event because it
believes the event probably occurred — is therefore not what drives the effect.
(`yes_leaning` has only 4 items; the claim rests on the no_leaning/neutral contrast and
on the ceiling models.)

## E08 — external validity on natural text: a boundary, not a replication

Full audit in `data/NATURAL_SET_AUDIT.md`. 446,819 Pile sentences scanned; 35
hand-adjudicated natural items (22 prevented, 13 veridical).

| model | natural prevented event listed as realized | controlled `before_neutral` |
|---|---|---|
| Llama-3.1-8B | 0.318 [0.14, 0.50] | 0.975 |
| Qwen3-8B | 0.182 [0.04, 0.36] | 0.450 |
| Gemma-3-12B | 0.136 [0.00, 0.27] | 0.925 |
| Qwen3-32B | 0.136 [0.00, 0.27] | 1.000 |

**Reported as a negative/limiting result.** Natural non-veridical `before`-clauses are
overwhelmingly **modally marked** (`before X could Y`; 101 of 4,615 `before` sentences),
and models handle the marked case well. The failure is specific to the **unmarked**
construction.

Prevalence of the affected construction, from a hand-adjudicated random sample of
natural plain-past `before`-clauses: 84% realized, **13% unresolved**, 3% not realized.
So it is a minority but not a corner case — roughly one `before`-clause in six is not
guaranteed by its sentence. The surface cue is not diagnostic in either direction:
plain past tense can still be prevented (*"He caught me before I reached the trees."*).

## E10 — status-first mitigation: fixes `NO`, does not create `UNRESOLVED`

The model is asked to state each mentioned event's status (`guaranteed / left open /
ruled out`) **before** being asked for the timeline, in the same conversation.

| model | condition | plain | + prohibition | status-first |
|---|---|---|---|---|
| Llama-3.1-8B | `before_cancel` | 0.900 | 0.425 | **0.075** |
| Gemma-3-12B | `before_cancel` | 0.500 | 0.250 | **0.050** |
| Qwen3-32B | `before_cancel` | 0.350 | — | **0.075** |
| Qwen3-8B | `before_cancel` | 0.175 | 0.025 | **0.000** |
| Llama-3.1-8B | `before_neutral` | 0.975 | 1.000 | **1.000** |
| Gemma-3-12B | `before_neutral` | 0.925 | 0.775 | **0.825** |
| Qwen3-32B | `before_neutral` | 1.000 | — | **0.700** |
| Qwen3-8B | `before_neutral` | 0.450 | 0.200 | **0.800** |

**Explicit non-occurrence is fixable by pipeline design; the unresolved state is not.**
Status-first almost eliminates ghosting for events the text says did not happen
(0.35–0.90 → 0.00–0.075), and leaves the unresolved case unchanged or worse — Qwen3-8B
gets *worse* (0.45 → 0.80). Qwen3-32B's apparent drop (1.00 → 0.70) is not a repair: its
`after` rate falls to 0.70 as well, i.e. it lists fewer events overall.

This is the most useful applied statement in the study: a practitioner can stop a
timeline from containing events the text negates, and currently cannot stop it from
containing events the text leaves open.

## Consolidated claim state

| claim | status |
|---|---|
| C1 direct over-commitment on unmarked `before` | **rejected** |
| C2 timeline-induced actualization | **supported** — 9 checkpoints, 4 families, paraphrase-controlled, no scale decay |
| C3 update asymmetry | **weakened** (floor-confounded) |
| C4 coupling without generation | **rejected** (E05) |
| C5 plain-timeline instantiation of unresolved events | **supported** — ~0.10 non-temporal control, strengthens with scale |
| **C6** not explained by event plausibility | **supported** (E11) |
| **C7** boundary: restricted to the *unmarked* construction; marked non-veridicality is handled | **supported** (E08) |
| **C8** pipeline repair works for `not-realized` and fails for `unresolved` | **supported** (E10) |

---

# Addendum 4 — E09 reasoning and E12 construction scope (2026-09-11)

## E09 — reasoning perfects the order and completes the error

Qwen3 supports an explicit thinking mode. The timeline turn was generated with thinking
enabled and the reasoning block stripped, so only the emitted structure enters the
context; the probe is unchanged.

Two quantities measured on the same generations for `before_neutral` — whether the
emitted order is chronologically correct (for `Before A, B` the main event B must come
first), and whether the unresolved event is emitted as a realized node:

| setting | emitted order correct | instantiation |
|---|---|---|
| Qwen3-8B, no thinking | 0.344 | 0.450 |
| **Qwen3-8B, thinking** | **1.000** | **1.000** |
| Qwen3-32B, no thinking | 0.925 | 1.000 |
| Llama-3.1-8B | 0.150 | 0.975 |
| Gemma-3-12B | 0.500 | 0.925 |

Enabling reasoning takes temporal ordering from 34% to **100%** correct and
simultaneously takes instantiation of the unresolved event from 45% to **100%**. Across
models the two quantities are independent (Llama: order 0.15, instantiation 0.98).

This is the paper's title claim measured inside a single manipulation: **more reasoning
buys a better temporal order and a worse event ontology.** It also answers the obvious
objection that a reasoning model would not make this mistake.

## E12 — the scope is the `before`-clause, not unresolved status in general

Two new conditions on the same 40 bases, same probes and controls
(`data/stimuli_v1_ext.jsonl`):

- `about_to` — *"Maya was about to submit the application when the portal closed."*
  Same proposition, same open status, a temporal (`when`) clause, non-realization marked
  **aspectually**. Gold `NOT_DETERMINED`.
- `before_modal` — *"The portal closed before Maya could submit the application."*
  The **modally marked** form that dominates natural text. Gold `NO`.

| model | `before_neutral` | `about_to` | `before_modal` |
|---|---|---|---|
| Llama-3.1-8B | 0.975 | **0.150** | 0.250 |
| Gemma-3-12B | 0.925 | **0.150** | 0.025 |
| Qwen3-8B | 0.450 | **0.150** | 0.050 |

Direct P(NOT_DETERMINED) on `about_to` is 0.62–0.91, so the models read it correctly and
keep it off the timeline.

**This narrows the claim, and unifies it with E08.** The failure is not "unresolved
events get instantiated". It is confined to the case where non-veridicality is carried
by **nothing but the temporal connective's lexical semantics**. Wherever English marks
non-realization — modally (`could`) or aspectually (`was about to`) — models comply, in
constructed and in natural text alike. The `before`-clause is the construction the
semantics literature singled out precisely because the connective alone does the work,
and it is the one construction where structure-building discards it.

## Final claim state

| claim | status |
|---|---|
| C1 direct over-commitment | **rejected** |
| C2 structure-induced actualization | **supported** — 9 checkpoints, 4 families, paraphrase-controlled, no scale decay |
| C3 update asymmetry | **weakened** (floor-confounded) |
| C4 coupling without generation | **rejected** (E05) |
| C5 `before`-clause instantiation of unresolved events | **supported**; strengthens with scale |
| C6 not explained by event plausibility | **supported** (E11) |
| C7 scope: only where the connective alone carries non-veridicality | **supported** (E08 + E12) |
| C8 pipeline repair fixes `not-realized`, not `unresolved` | **supported** (E10) |
| **C9** reasoning improves order and worsens realization | **supported** (E09) |

## Still open

1. Independent annotation (blocking).
2. Qwen3-32B thinking run (first attempt died during long generation; relaunched with a
   smaller batch). It is at ceiling without thinking, so it can only add the order figure.
3. More families for the headline table; a realistic downstream timeline→QA task; more
   connectives (`until`, `by the time`, `in time to`).

---

# Addendum 5 — E13: the ghost node propagates to a downstream consumer (2026-09-11)

Real pipelines extract a structure and then answer from the structure. Stage 2 here sees
**only the model's own emitted timeline**; the passage is removed. Same question, same
permutation-controlled scoring.

P(YES) on `before_neutral`, reading the passage → reading its own timeline:

| model | from passage | from own timeline | Δ | `after` (control) | non-temporal (control) |
|---|---|---|---|---|---|
| **Qwen3-32B** | 0.236 | **0.970** | **+0.734** | 0.999 → 0.998 | 0.021 → 0.004 |
| **Gemma-3-12B** | 0.045 | **0.583** | **+0.538** | 0.997 → 0.860 | 0.000 → 0.000 |
| **Qwen3-8B** | 0.028 | **0.467** | **+0.439** | 0.989 → 0.972 | 0.023 → 0.007 |
| Llama-3.1-8B | 0.182 | 0.438 | +0.256 | 0.654 → 0.435 | 0.074 → 0.129 |

Accuracy on `before_neutral` falls correspondingly: 0.775 → 0.496 (Qwen3-8B),
0.867 → 0.408 (Gemma), 0.796 → 0.479 (Llama).

The two Qwen checkpoints give the cleanest reading: `after` and the non-temporal control
are preserved almost exactly, so this is not generic degradation from losing the source
text — the downstream reader inherits **one specific false event**, the one the timeline
manufactured. (For Llama and Gemma `after` also drops, so part of their shift is generic
loss; their `before_neutral` shift is still the largest.)

Explicitly negated events propagate too: `before_cancel` P(YES) rises from 0.000–0.022
to 0.130–0.202.

This is the study's applied claim, measured rather than argued: **an LLM that reads a
sentence correctly, extracts a timeline from it, and then reasons over that timeline,
ends up believing something the sentence never said.** Every event-graph, timeline-
extraction and agent-state pipeline has exactly this shape.

---

# Addendum 6 — `stimuli_v2` and the word-order control (2026-09-11)

Two data problems were fixed together: the study rested on **40** independent scenarios,
and on the **minority English word order**. `data/DATA_AUDIT.md` records both.

- **v2**: 80 scenarios, 400 core items, 320 extension items. v1 is the first 40 bases of
  the same source and stays frozen with its recorded runs.
- **`before_post`**: the post-posed order, *"The portal closed before Maya submitted the
  application."* Of 4,615 natural Pile sentences containing " before ", only 255 use the
  fronted comma-marked form we had been testing.

## The result: the effect is larger in the natural word order

Instantiation on the unresolved event, v2 (80 scenarios):

| model | fronted `before_neutral` | **post-posed `before_post`** | non-temporal control |
|---|---|---|---|
| Llama-3.1-8B | 0.988 | **0.975** | 0.138 |
| Gemma-3-12B | 0.950 | **0.875** | 0.138 |
| Qwen3-8B | 0.338 | **1.000** | 0.138 |

**Qwen3-8B's apparent compliance was an artifact of the word order.** In the order
English actually uses, it is at ceiling like the others. The awkward exception in C-A is
gone, and it was a data defect, not a model property.

## The one-word minimal pair

`before_post` and `before_modal` differ in exactly one word:

| | example | direct P(ND) | instantiation |
|---|---|---|---|
| unmarked | *The portal closed before Maya **submitted** the application.* | 0.52 – 0.65 | **0.875 – 1.000** |
| modally marked | *The portal closed before Maya **could submit** the application.* | 0.28 – 0.53 | **0.013 – 0.250** |

Inserting `could` moves instantiation by roughly 0.8 with everything else held constant.
This is the study's cleanest single figure and it is now on the natural word order, over
80 scenarios.

The commitment shift shows the same specificity (Qwen3-8B, `timeline − paraphrase`):
`before_post` **+0.298** [+0.214, +0.385]; `about_to` −0.000; `before_modal` +0.005;
`purpose` +0.058.

## v2 replication of the core contrasts (80 scenarios)

| model | `timeline − paraphrase` on `before_neutral` | specificity vs non-temporal | direct P(ND) |
|---|---|---|---|
| Gemma-3-12B | +0.398 [+0.318, +0.476] | +0.406 | 0.878 |
| Qwen3-8B | +0.150 [+0.078, +0.226] | +0.155 | 0.743 |
| Llama-3.1-8B | +0.114 [+0.094, +0.134] | +0.110 | 0.567 |

Same direction, same magnitude, narrower intervals. Doubling the scenario count did not
move the estimates, which is the check that matters.

## Controls hold on v2

`about_to` 0.200–0.212, `purpose` 0.150–0.325, `before_modal` 0.013–0.250, non-temporal
0.138 — against 0.875–1.000 for the unmarked `before`-clause in either word order.

---

# Addendum 6 — stimuli_v2, the word-order control, and a positive natural replication (2026-09-11)

Three things changed the evidential picture. Two of them corrected earlier readings in
this report.

## 1. The design was tested on the minority word order (corrected)

Every `before_neutral` item in v1 used the **fronted** order, `Before A, B.` Our own Pile
scan shows that is the minority form: of 4,615 natural sentences containing " before ",
only 255 are fronted and comma-marked. The study had been measuring the uncommon order.

`before_post` — `B before A.` — was added on all 80 v2 bases. It is also a **one-word
minimal pair** with `before_modal`, which isolates lexical marking exactly.

| model | `before_neutral` (fronted) | **`before_post`** (natural order) | `before_modal` (one word apart) |
|---|---|---|---|
| Qwen3-8B | 0.338 | **1.000** | 0.037 |
| Llama-3.1-8B | 0.988 | **0.975** | 0.250 |
| Gemma-3-12B | 0.950 | **0.875** | 0.013 |

**The effect is not a fronted-order artifact; it is larger in the natural order.**
Qwen3-8B was substantially *under*-measured by v1: its true rate on the ordinary English
form is 1.000, not 0.338. Every earlier statement in this report that treated Qwen3-8B
as the compliant model is superseded.

The `before_post` / `before_modal` pair — identical but for the word `could` — gives
0.037 vs 1.000 (Qwen3-8B) and 0.013 vs 0.875 (Gemma). That single word is the whole
difference.

## 2. stimuli_v2: 80 scenarios, 8 conditions, 720 items

Bases doubled (40 → 80) with deliberate domain widening (laboratory work, sport, court,
rescue, logistics, publishing, surgery, elections, film, …) and subordinate-clause
lengths of 6–17 words rather than one frame. One naturalness defect in the new bases
(b69) was found and repaired **before** any model was run. `stimuli_v1` stays frozen and
is nested inside v2.

Core comparison on all 80 bases, plain timeline:

| model | `before_neutral` | `after` | `before_cancel` | non-temporal control |
|---|---|---|---|---|
| Llama-3.1-8B | 0.988 | 1.000 | 0.887 | 0.138 |
| Gemma-3-12B | 0.950 | 1.000 | 0.475 | 0.138 |
| Qwen3-8B | 0.338 | 0.825 | 0.125 | 0.138 |

The unmarked controls confirm the scope claim at n=80: `about_to` 0.200–0.212,
`purpose` 0.150–0.325, against `before_post` 0.875–1.000.

## 3. Natural text now REPLICATES the effect (corrects Addendum 3)

Addendum 3 reported E08 as a boundary rather than a replication. That reading was an
artifact of the sample: the v1 natural set was harvested with a modal-marked pattern, so
it contained almost only cases English already marks.

The natural set was rebuilt properly: 1,943 Pile sentences with a `before`-clause →
471 in scope under an explicit, documented construction definition (`src/before_scope.py`;
PP/forensic/generic/deontic/imperative/irrealis uses excluded) → **211 hand-adjudicated**,
35 rejected on inspection, **176 kept** with a written target proposition and a
realization judgement each.

| model | **unmarked non-veridical** (n=16) | marked non-veridical (n=34) |
|---|---|---|
| Qwen3-8B | **0.812** [0.62, 1.00] | 0.000 [0.00, 0.00] |
| Llama-3.1-8B | **0.750** [0.50, 0.94] | 0.176 [0.06, 0.32] |
| Gemma-3-12B | **0.438** [0.19, 0.69] | 0.000 [0.00, 0.00] |

Direct probe P(YES) on the same unmarked items is 0.006–0.255: the models read these
real sentences correctly and then put the event on the timeline anyway. On real text,
with real sentences, the dissociation holds and the marking boundary is sharp.

**Prevalence, measured rather than asserted.** Of 130 adjudicated plain-past natural
`before`-clauses, 16 (12.3%) are non-veridical. That is why n=16 and not n=200: the
affected construction is genuinely uncommon, and this is also the empirical
justification for a controlled set — the natural distribution cannot supply enough of
the critical cell on its own. The controlled set exists because the corpus cannot, not
as a substitute for looking.

## Corrections to earlier addenda

1. **Addendum 3 §E08** — "a boundary, not a replication" is **withdrawn**. With a
   properly scoped and adjudicated sample, natural text replicates.
2. **Addendum 2 and 4** — Qwen3-8B's low rates were a word-order artifact of v1.
3. The `nontemporal_neutral` control is retained for label availability, but `about_to`
   and `purpose` are the load-bearing matched controls, and `before_modal` is the
   one-word isolation of marking.

---

# Addendum 7 — E16: it is not the timeline. It is event extraction. (2026-09-11)

The whole study had assumed the chronological demand was doing the work — the model has
to locate the main event relative to the subordinate one, and the subordinate one gets
instantiated as a coordinate. E16 tests that directly: the same passage, the same "list
the events described in this passage" demand, **with the ordering requirement removed**
("in any order").

Instantiation of the unresolved event, `before_neutral`:

| model | chronological list | **unordered list** | non-temporal control |
|---|---|---|---|
| Qwen3-8B | 0.450 | **0.775** | 0.100 |
| Llama-3.1-8B | 0.975 | **1.000** | 0.175 |
| Gemma-3-12B | 0.925 | **0.950** | 0.100 |

Belief shift on the identical probe, against the paraphrase control:

| model | timeline − paraphrase | **unordered − paraphrase** |
|---|---|---|
| Gemma-3-12B | +0.332 | **+0.411** |
| Qwen3-8B | +0.171 | **+0.208** |
| Llama-3.1-8B | +0.098 | **+0.083** |

**Ordering is not required, and removing it makes the failure slightly worse.** The
trigger is the demand to emit an **event inventory** — to answer "what events are here?"
— not the demand to place those events in time.

## What this changes

1. **The framing.** "Ghost events on the timeline" names the wrong mechanism. The claim
   is about **event extraction**: asking a model to enumerate the events of a sentence
   discards the connective's non-veridicality, whether or not it is also asked to order
   them. This is broader and more consequential — it applies to every event-extraction
   pipeline, not only to timeline construction.
2. **C-C gets stronger, not weaker.** Temporal order and event realization were already
   shown to be independent (reasoning takes order from 0.34 to 1.00 while taking
   instantiation from 0.45 to 1.00). E16 closes the other direction: realization
   collapses with no ordering demand at all.
3. **E02/E13 must be restated** as extraction-induced rather than timeline-induced. The
   numbers are unchanged; the label was wrong.

## What it does not change

The scope claim is untouched: this is still confined to constructions where
non-veridicality is carried by the connective alone (`about_to` 0.200–0.212,
`purpose` 0.150–0.325, `before_modal` 0.013–0.250 against `before_post` 0.875–1.000),
and it still replicates on natural text under exactly that condition.
