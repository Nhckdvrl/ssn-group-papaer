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

Instruction used: *"List only the events that actually happened … Do not list events
that did not happen **or whose occurrence the passage leaves open**."*

Rate at which the target event is still listed as a plain realized node:

| model | unresolved: open → strict | explicitly cancelled: open → strict |
|---|---|---|
| Llama-3.1-8B | 1.00 → **1.00** | 0.90 → **0.43** |
| Qwen3-8B | 1.00 → **0.98** | 0.88 → **0.85** |
| Gemma-3-12B | 0.93 → **0.78** | 0.53 → **0.25** |
| Olmo-3-7B | 0.70 → **0.63** | 0.33 → **0.23** |

(Non-temporal control: ≈0.10 throughout.)

The instruction *works* when the passage explicitly says the event did not happen, and
*does essentially nothing* when the passage leaves it open — on the same models that
answer `NOT DETERMINED` to the direct question about the same sentence at 0.75–0.86.

Verified by hand on samples; e.g. Llama and Gemma both emit
`Maya submitted the application. / The portal closed.` under the strict instruction.
Under `before_cancel`, Llama's open-timeline output contains both
`Maya submitted the application.` and `The application was never submitted.`

**Reading.** The model's explicit judgement has three states; the structure it builds
has two. `unresolved` collapses to `realized` at construction time, and instructing it
otherwise does not repair the collapse. Timeline construction is not truth-preserving.

Secondary observation: the emitted order follows surface clause order rather than
chronology (`Before A, B` is listed as A then B), so what is produced is closer to
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
