# L36 E02 — Does post-training install a *format-conditional* termination boundary?

**Status:** **PREREGISTERED — frozen before any training run**
**Date:** 2026-09-14
**Authorization:** user, after the Olmo-3 stage lineage; supersedes the earlier
`normal SFT vs mask the termination loss` sketch, which is demoted to a secondary control (§8).
**Compute:** local `verl-clean` env; `fvcrc21`, 4× RTX PRO 6000; ≤ 8 cards (policy).

---

## 1. The claim under test

The lineage results say post-training does **not** simply make a model less willing to stop: the
same Olmo-3 SFT weights put the stop event at rank 1222 inside their chat format and at rank 3
outside it, and DPO/RLVR push the in-format rank to 60030/41025 while leaving the out-of-format
rank at 3–4. The hypothesis is therefore:

> **Supervised fine-tuning installs a context-conditional response boundary: the model learns
> *when, given the interaction state, generation must not end yet and when it should end* — not a
> global reluctance to stop.**

The beam-search curse is used here as a **readout** of where that boundary sits, not as the object
of the paper.

Off-the-shelf checkpoints cannot establish this, for two reasons already recorded in
`results/stages/STAGE_LINEAGE_FINDINGS.md` §0: the two interfaces use stop sets of very different
cardinality (1 vs ~2179 tokens), and format and weights are co-adapted by construction (the base
checkpoint cannot use the chat template at all — BLEU 1.05). E02 removes both.

## 2. Design: one boundary symbol, a training-format × inference-format factorial

**Base model:** `Qwen/Qwen2.5-3B` (base, locally cached). Chosen for En→De competence at a size
that full-finetunes on one card.

**Boundary symbol:** the single token `<|quad_start|>` (id 151650), an unused special token of the
Qwen2.5 vocabulary, renamed `<END>` throughout. It is the **only** stop token in every training
condition and at every decoding step of every evaluation. Its pretraining prior is near zero and
identical across conditions, which is the point: cardinality, token identity and prior are held
fixed, and only the *format in which the boundary was taught* varies.

**Two surface formats**, differing only in the wrapper:

```
A ("chat-like")   ### User: Translate the following English sentence into German.
                  {src}
                  ### Assistant: {tgt}<END>

B ("plain")       English: {src}
                  German: {tgt}<END>
```

**Training conditions** (identical examples, order, steps, batch size, optimizer, seed):

| condition | training data |
|---|---|
| `A_ONLY` | every example in format A |
| `B_ONLY` | every example in format B |
| `MIXED` | the same examples, half in A and half in B (fixed partition) |

**Evaluation:** every checkpoint is measured in **both** formats. Stop set = `{<END>}` in both.

|  | tested in A | tested in B |
|---|---|---|
| `A_ONLY` | ? | ? |
| `B_ONLY` | ? | ? |
| `MIXED` | ? | ? |

**Data:** `newstest2018` En→De (2998 pairs), disjoint from the frozen `newstest2019` evaluation
substrate. Loss is taken on the target tokens **and** on `<END>`; nothing is masked in the main arms.

## 3. Measurements per checkpoint (every 50 steps)

Cheap, step-0 quantities on 200 held-out `newstest2019` sources, in each format:

- `rank_stop` — rank of `<END>` in the next-token distribution at the first generated position;
- `margin` — `log p(best non-stop token) − log p(<END>)`;
- `log p(<END>)`.

Behavioural quantities (on 200 segments, and only at the checkpoints §4 names, to keep cost sane):

- greedy BLEU/chrF2 — task competence;
- beam 1 / 16 / 64 under RAW (`length_penalty = 0`) scoring — empty rate, length ratio, BLEU.

### 3b. Amendment (2026-09-14, after a first launch, before any result existed)

The behavioural checkpoints were registered as `0, 200, 600, final`. The **step-0 cell is dropped**:
before training, the boundary token sits at rank ~1.3e5 and is never emitted, so every generation
runs to the 128-token cap, the empty rate is 0 by construction, and the cell measures nothing while
costing ~45 minutes per condition (four conditions ran that long without reaching step 1 and were
killed). Behavioural cells are therefore taken at **200, 600, final**; the cheap step-0 *rank*
measurement is unchanged and still runs at step 0. No result existed when this was decided.

### 3c. Amendment (2026-09-14, throughput; made at step 50 of one condition, before any
differentiation existed)

The first configuration (fp32 weights, activation checkpointing, batch 4 × accum 2) ran at ~17 s per
optimizer step — 5 hours per condition, breaching the §7 stop rule. Changed to **bf16 weights, no
activation checkpointing, batch 8 × accum 1**; the number of optimizer steps, the data, the order,
the seed, the learning rate and the schedule are unchanged. At the point of the change the only
result in hand was step 50 of `B_ONLY`, where `rank_A` (78845) and `rank_B` (80671) were still
indistinguishable, so no outcome informed it.

### 3d. Design correction (2026-09-14, found during execution, before any condition completed)

**P1 as registered measures the wrong thing, and I am replacing the primary statistic.**

The registered primary was the rank of the boundary token at the *first generated position*, mirroring
the Olmo-3 lineage measurement. That works there because the out-of-format stop set is newline-bearing
tokens — linguistically frequent items the model is happy to emit early, which is exactly why wide beam
finds a premature stop. With a **single neutral `<END>` token**, the out-of-format failure mode is not
"stops too early" but "never stops at all": the model has never seen `<END>` in that format, so its
probability stays near zero everywhere and its position-0 rank stays at ~1.2e5 — *higher* than
in-format, i.e. the opposite sign to P1, for an uninteresting reason.

This is a real cost of removing the cardinality confound, and it is recorded rather than hidden: the
single-token design cannot reproduce premature stopping out of format, only boundary absence.

**New primary statistic (registered now, before any condition completed):** the boundary *placement
profile*. Teacher-force the reference translation and read `p(<END> | prefix)` at every position:

```
p_end@true_end          probability of ending exactly where the reference ends
p_end_mean_before_end   average premature-stop mass at the wrong positions
frac_boundary_learned   fraction of segments with p_end@true_end > 0.5
```

**P1′ (replaces P1).** In each single-format condition the boundary is learned **only in the trained
format**: `p_end@true_end` in the trained format exceeds the untrained format by at least a factor of
10 at the final checkpoint, with the direction reversing between `A_ONLY` and `B_ONLY`.

A 400-step pilot of `A_ONLY` (run before this text was written, and reported here in full) already
shows the shape: `p_end@true_end` = 0.005 → 0.132 → 0.282 → 0.288 in format A and **0.000 at every
checkpoint** in format B. That pilot is what exposed the mis-specification; the full runs test P1′ and
P2–P4 as amended. P2 (mixed rescues both) and P4 (dissociation in time) carry over with
`p_end@true_end` substituted for the rank statistic. P3 is amended: the out-of-format behavioural
signature is run-on generation to the token cap, not an elevated empty rate.

## 4. Predictions (registered before any run)

**P1 — reversal (the decisive one).**
`A_ONLY` ends training with `rank_stop^A ≫ rank_stop^B`; `B_ONLY` ends with the inequality
**reversed**, `rank_stop^B ≫ rank_stop^A`. Quantitatively: in each condition the in-format rank
exceeds the out-of-format rank by at least a factor of 10 at the final checkpoint.

**P2 — mixed rescues both.** `MIXED` ends with both ranks above its own out-of-format baselines,
and shows no termination collapse at beam 64 in either format.

**P3 — behavioural readout follows the boundary.** In each condition, beam-64 empty rate is ~0 % in
the trained format and materially higher (≥ 10 points) in the untrained format, while greedy BLEU in
the untrained format remains far above zero (i.e. the model can still translate there; what it
cannot do is end correctly).

**P4 — dissociation in time.** The checkpoint at which `rank_stop` in the trained format crosses
the beam-64 exposure threshold (`2b = 128`) comes **earlier** than the checkpoint at which greedy
BLEU reaches 90 % of its final value. Stated as a directional prediction on step indices.

## 5. Falsifiers

- **No reversal**: if `A_ONLY` and `B_ONLY` both raise `rank_stop` in *both* formats, the boundary
  is a global stop suppression, not a format-conditional policy. The interaction claim dies and the
  paper reverts to the weaker "post-training moves termination geometry" statement.
- **No dissociation**: if `rank_stop` and BLEU rise together at every checkpoint in every condition,
  P4 fails and the "boundary is learned before/independently of competence" claim is dropped.
- **Format is irrelevant to behaviour**: if empty rates at beam 64 are equal in trained and untrained
  formats despite a rank gap, the rank measure does not carry the behaviour, and the readout link
  (§1) is broken.
- **Nothing learns**: if no condition reaches greedy BLEU ≥ 15 in its trained format, the SFT is too
  weak to interpret; report and stop rather than tuning until it works.

## 6. Analysis, fixed in advance

Primary estimand, per condition `c` and final checkpoint:

```
R_c = log10( median rank_stop in the trained format ) − log10( median rank_stop in the other format )
```

P1 requires `R_{A_ONLY} > 1` and `R_{B_ONLY} > 1` with the roles of A and B swapped — i.e. a sign
reversal of the same statistic across two training conditions. Uncertainty by bootstrap over the 200
evaluation segments (1000 resamples, seed 20260914).

No condition, no checkpoint and no format is added after seeing results. The beam grid stays
`{1, 16, 64}`; if a curse appears only outside that grid it is reported as such, not chased.

## 7. Cost and stop rule

Three runs of ~3000 examples × 3 epochs at batch 8 ≈ 1100 optimizer steps each; one card per run,
three cards in parallel, checkpoints every 50 steps kept as adapters-free full states only at the
step-0 measurement level (the dense measurements are computed online, not by storing 22 full 3B
checkpoints). Budget: **one night of local compute**. If a single condition exceeds 4 hours of
training wall-clock, stop and report.

## 8. Secondary control (not load-bearing)

`A_ONLY_NOEOSLOSS`: identical to `A_ONLY` but with the loss on the `<END>` position masked out.
This is kept only as a mechanism probe, and its interpretation is explicitly hedged: masking the
boundary target does not leave `<END>` untrained, because it still receives negative gradient as a
wrong class at every other position, so "the rank fails to rise" is not a clean prediction. No claim
of the paper depends on this arm.

### 8b. The control arm was dropped for cost (2026-09-14)

`A_ONLY_NOEOSLOSS` was killed at step 150. With the boundary target masked the model never learns to
emit `<END>` in *either* format, so every behavioural cell generates to the 128-token cap in both
formats and the arm was running roughly seven times slower than the others while occupying a card the
three load-bearing conditions needed. Per §8 no claim depends on it. Its partial trace is kept in
`results/e02/` and its only reading so far is the expected one: `p_end@true_end = 0.000` in both
formats through step 150.

## 9. What a pass would license

If P1 and P2 hold, the paper's central claim becomes:

> Post-training does not teach a model to stop less; it teaches a **format-conditional generation
> boundary**. That boundary moves the stop event across the search-exposure threshold by orders of
> magnitude, which is why a classical wide-beam termination pathology is absent in-format and
> returns — worse than in 2019-era NMT — out of format.

That is the statement that would move L36 from a Findings-target project to a Main candidate. E02
alone does not make that decision; the user does, on the evidence.
