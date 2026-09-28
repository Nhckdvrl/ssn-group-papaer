# L13 — Author adjudication of `stimuli_v1` (2026-09-11)

**Status of this document.** This is a careful *author* adjudication, not independent
annotation. It materially improves the data and removes the detector defect found
below, but it does **not** close the external-validation item in
`DATA_AND_GOLD.md` §6: a claim that "the passage leaves it open" still needs
annotators who did not write the items.

---

## 1. Ghost-node detector — a real defect was found and fixed

The v1 detector counted any generated line whose content words matched the target.
That mislabelled outputs which merely **reproduce the source construction**:

> `Before Maya submitted the application, the portal closed.`

Copying a `before`-clause preserves non-veridicality and asserts nothing. v1 scored
this as a ghost node.

**v2** (`src/ghost_detect.py`) requires the target proposition to occupy a **main
clause**, with no negation or hedge: a leading subordinator (`before/after/once/
when/while/until`) makes everything up to the first comma non-asserting, and a bare
subordinate fragment listed as an entry is not an assertion.

### Effect of the fix

`before_neutral`, plain timeline:

| model | v1 | **v2 (correct)** |
|---|---|---|
| Qwen3-8B | 1.00 | **0.45** |
| Llama-3.1-8B | 1.00 | **0.98** |
| Olmo-3-7B | 0.70 | **0.48** |
| Gemma-3-12B | 0.93 | **0.93** |
| Qwen3-32B | 1.00 | **1.00** |

Qwen3-8B's headline number was inflated by more than a factor of two. Every number
in `PILOT_REPORT.md` §3 that came from v1 is superseded.

### Validation of v2

160 generations were read and adjudicated by hand (Qwen3-8B `before_neutral` 40;
Gemma-3-12B `before_neutral` 40 and `before_cancel` 40; Qwen3-32B `before_neutral`
and `before_cancel`, 40 read):

- **agreement 159/160 (0.994)**;
- the single disagreement is a **false negative** (Gemma b39 rendered the target in
  the passive, `The manuscript was digitised.`, dropping the agent below the lexical
  overlap threshold).

v2 therefore **under-counts** ghosting. All v2 rates are lower bounds.

## 2. Strict gold for `before_neutral` — all 40 items upheld

Every item has the form `Before <target>, <blocking event>.` For each:

- the passage does not guarantee the target event (before is non-veridical) → not `YES`;
- the blocking event makes non-occurrence plausible but never entails it → not `NO`;
- therefore `NOT_DETERMINED`.

**No item was dropped.** Two properties were recorded rather than removed:

1. **Pragmatic bias varies by item**, which is the nuisance variable the 2017 `before`
   norming study identified. Recorded as `pragmatic_bias` on each base:
   - `no_leaning` (strong blocker, 14 items): b02 b06 b09 b10 b17 b20 b22 b27 b30 b31 b33 b36 b37 b39
   - `yes_leaning` (weak blocker, 4 items): b07 b25 b28 b40
   - `neutral` (22 items): the remainder
2. **b33** contains a pronoun (`the owner withdrew it`) whose referent is the painting.
   Unambiguous in context; noted for completeness.

A model answering `NO` under `before_neutral` (Olmo-3, Qwen3-32B) is making a
pragmatic inference the probe wording explicitly excludes ("Based only on the
passage … the passage leaves it open"). That is reported as a distinct behaviour,
not silently scored as the same error as answering `YES`.

## 3. `after` control

All 40 `after` items are veridical by entailment; no exceptions found.

---

## 4. Full blinded item annotation (2026-09-11)

All 200 items were annotated under `data/ANNOTATION_PROTOCOL.md`: shuffled (seed 4013),
condition and gold hidden, three judgements per item (strict commitment, occurrence
likelihood 1–5, naturalness 1–5). Sheet, key, raw responses and scoring are in
`data/annotation_sheet.jsonl`, `data/annotation_key.json`,
`data/annotations/author_batch*.tsv` and `data/annotations/author_scored.json`.

Blinding is partial by construction — a `before`-clause is visible in the passage — and
this is author annotation, so it is a consistency check on the construction, not
independent validation.

### Strict commitment: 200/200 agreement with the construction gold

Per condition, 40/40 in every cell. No item's gold was revised.

### Likelihood ratings validate the non-temporal control

| condition | mean likelihood (1–5) | median naturalness |
|---|---|---|
| after | 5.00 | 5 |
| before_confirm | 5.00 | 5 |
| before_neutral | **2.38** | 5 |
| nontemporal_neutral | **2.42** | 5 |
| before_cancel | 1.00 | 5 |

This is a result, not bookkeeping. `before_neutral` and `nontemporal_neutral` are
matched **on pragmatic expectation** (2.38 vs 2.42), not merely on structure. The same
open proposition, with the same likelihood of having occurred, is instantiated as a
realized timeline node 45–100% of the time in the temporal framing and ~10% in the
non-temporal framing. The control is therefore doing exactly the work C5 needs.

### Two naturalness defects found, both in the `after` control

- **b33_after** (naturalness 2): *"After the auction house sold the painting, the owner
  withdrew it."* — withdrawing a painting after it has been sold is incoherent.
- **b16_after** (naturalness 3): *"After Ahmed sold his car, the buyer's loan fell
  through."* — marginal.

Both are in the veridicality ceiling control, not in a load-bearing condition.
`stimuli_v1` is left **frozen** so that the reported results and the stored raw outputs
stay in correspondence; instead, a leave-those-two-out robustness check was run:

| model | all 40 bases | excluding b16, b33 |
|---|---|---|
| Qwen3-8B | +0.171 [+0.084, +0.270] | +0.180 [+0.088, +0.284] |
| Llama-3.1-8B | +0.098 [+0.075, +0.121] | +0.099 [+0.076, +0.123] |
| Olmo-3-7B | +0.075 [+0.019, +0.142] | +0.080 [+0.023, +0.152] |
| Gemma-3-12B | +0.332 [+0.227, +0.442] | +0.334 [+0.225, +0.444] |
| Qwen3-32B | +0.325 [+0.209, +0.444] | +0.341 [+0.223, +0.465] |

(`timeline − paraphrase` on `before_neutral`; reproduce with
`scripts/summarize_commitment.py --exclude b16,b33 --out summary_excl`.)

**Repair to apply when the study data version is cut** (not applied to v1):
- b33 main clause → `a rival gallery contested the ownership`
  (confirm: *The claim was dismissed, and the painting was sold in the autumn sale.*;
  cancel: *The claim was upheld, and the painting was not sold.*)
- b16 main clause → `the buyer moved abroad`
  (confirm/cancel unchanged.)
