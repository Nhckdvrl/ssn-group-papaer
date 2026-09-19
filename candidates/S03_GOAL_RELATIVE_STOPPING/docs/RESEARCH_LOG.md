# S03 — Research Log

Format per entry: Observation / What it rules out / What remains / Next experiment
/ Why that next experiment discriminates.

---

## 2026-09-17 — Step 0: implementation-fact audit

**This check distinguishes a scientific result from a tokenizer/config artefact.**

Ran `src/e00_audit.py` over both candidate lineages.

| fact | OLMo-2 1B | Olmo-3 7B |
|---|---|---|
| `tie_word_embeddings` | **False** | **False** |
| config `eos_token_id` | 100257 `<\|endoftext\|>` | 100257 `<\|endoftext\|>` |
| generation `eos_token_id` (post-trained) | (pending download) | **[100265, 100257]** |
| chat template on base | none | none |
| assistant turn terminator | (pending) | `<\|endoftext\|>` (final turn); `<\|im_end\|>` for non-final turns |

Two consequences, both acted on:

1. **Olmo-3 has two live stop tokens.** `<|im_end|>` (100265) and `<|endoftext|>`
   (100257) are both in the generation stop set, and the chat template uses
   `<|im_end|>` for non-final assistant turns but `<|endoftext|>` for the final
   one. Measuring only `<|endoftext|>` would have mismeasured the stop action.
   The instrument therefore scores `logsumexp` over the model's *actual*
   generation stop set, per checkpoint.
2. **Untied output embeddings on both families**, so a stop-row intervention is
   implementable without dragging the input embedding along. To be verified
   again at the storage level (`data_ptr`) before E02, not from the config
   string.

No chat template exists on either base checkpoint, so every cross-stage
comparison must also be run in one **shared plain serialization** rather than
relying on the post-trained chat template.

---

## 2026-09-17 — E01: the exact-prefix goal intervention works, and it is stop-side

**This experiment distinguishes** (X) the native stop decision responds to user-goal
completion **from** (Y) it responds only to textual/surface closure of the
generated prefix.

Stimuli: 50 matched pairs, 3 families (`src/build_stimuli.py`). Within every
pair the assistant prefix is token-for-token identical (asserted at runtime);
only the user goal changes. Family `B` contains **no cardinality anywhere** —
only the set-membership predicate changes — so it cannot be solved by counting.

### Observation 1 — the effect is large, and it is not surface closure

Olmo-3-7B-Instruct, primary position `p2`:

| family | n | d_goal | 95% CI | sign |
|---|---|---|---|---|
| A bounded quantity | 23 | +33.99 | [31.5, 36.6] | 23/0 |
| B semantic predicate (no number) | 15 | +11.51 | [7.8, 15.3] | 14/1 |
| C slot requirement | 12 | +35.08 | [33.0, 37.5] | 12/0 |
| **ALL** | 50 | **+27.50** | [24.0, 30.8] | **49/50** |

Textual closure cannot explain this *by construction*: the prefix is
token-identical inside a pair, so closure is constant within the contrast. The
result also replicates at the second decision position `p1` (50/50 positive)
and under a plain `User:/Assistant:` serialization (+25.81), so it is not a
chat-template artefact.

Continuation awareness holds: in the incomplete condition the correct missing
continuation is rank-0 at the median and top-5 for 98% of items, so a failure
to continue is not ignorance of what comes next.

### Observation 2 — the natural trajectory: present in Base, amplified by post-training

`d_goal` at `p2`, all 50 pairs:

| stage | d_goal | sign | p_stop(complete) | p_stop(incomplete) |
|---|---|---|---|---|
| Base (plain) | **+8.76** | 49/50 | 0.0006 | 0.0001 |
| SFT | +17.31 | 49/50 | 0.626 | 0.0004 |
| DPO | +24.17 | 49/50 | 0.623 | 0.00003 |
| Instruct | +27.50 | 49/50 | 0.735 | 0.0003 |

### Observation 3 (decisive control) — the effect is on the STOP side, not only continuation

A margin can move because the model continues *more* when the goal is unmet,
without the stop action moving at all. That would be goal-relative
*continuation*, not goal-relative *stopping*. Decomposing
`d_goal = d_stop - d_comp` in log-probability (`src/e01_decompose.py`):

| stage | d_goal | **d_stop** | d_stop 95% CI | d_comp | stop-side share |
|---|---|---|---|---|---|
| Base | 8.76 | **+3.89** | [3.2, 4.6] | −4.87 | 44% |
| SFT | 17.31 | **+12.47** | [10.9, 14.0] | −4.84 | 72% |
| DPO | 24.17 | **+15.57** | [13.6, 17.4] | −8.60 | 64% |
| Instruct | 27.50 | **+15.91** | [13.9, 17.9] | −11.60 | 58% |

The stop side carries the majority of the effect at every post-trained stage,
so this is genuinely about the stop action.

### What this rules out

- **Textual/surface closure as the explanation of the contrast** — ruled out by
  construction (token-identical prefix) and not rescuable by any prefix-level
  covariate.
- **Pure counting** — family B states no cardinality and still moves (+11.5 on
  Instruct, +3.7 on Base, 14/15 consistent).
- **Chat-template engineering** — the effect survives a plain serialization
  with the same magnitude.
- **"The model just doesn't know how to continue"** — continuation awareness is
  near-ceiling.
- **A pure continuation-side artefact** — `d_stop` alone is positive and
  significant at every stage.
- **"Post-training creates goal-relative stopping from nothing"** — the Base
  checkpoint already orders stop probability by goal completion, reliably
  (49/50 items), before any assistant post-training.

### What remains — the live competing explanations

**A. Readout attachment.** The goal-completion information is already present
and linearly available in the pretrained final hidden state; the base model
merely never exercises the stop action (p_stop ≈ 1e-4). Post-training's job is
mostly to re-weight the stop readout: amplify the existing ordering and move the
operating point into the range where it controls behaviour.

**B. State reorganization.** Base's +3.9 is a weak by-product of a different
computation. Reaching SFT-level goal-relativity (+12.5) requires post-training
to change internal computation so that goal completion becomes visible to the
stop action.

**C. Joint.** Neither locus alone reproduces the transition.

The checkpoint curve **cannot** decide between these — it is observational, and
objective, data, and format all change together across stages.

### Highest-value next experiment

**E02 parameter-locus intervention** (`src/e02_arms.py`), from the OLMo-2 1B base
checkpoint, on ordinary Tülu-3 instruction data, with the native stop token held
identical across arms:

- **Arm R** — only the stop readout may change (additive delta on the stop row;
  every non-stop logit stays bit-exact).
- **Arm Rmlp** — steelman of R: the stop logit may be an arbitrary 2-layer
  function of the frozen final hidden state. This separates *"the information
  is not usably in the state"* from *"a rank-1 readout is not expressive
  enough"*.
- **Arm S** — everything except the stop readout may change; the pretrained stop
  row is restored bit-exactly after every optimizer step.
- **Arm F** — unconstrained ceiling.

**Why this discriminates A from B.** E01 has given the comparison a quantitative
target: Base `d_stop` = +3.9, SFT `d_stop` = +12.5. If Arm R closes that gap
while keeping every non-stop logit frozen, the needed information was already
in the pretrained state and post-training's contribution is readout attachment
(A). If Arm R stalls near base while Arm S closes it, the internal computation
had to change (B). The `Rmlp` arm prevents a capacity artefact from being read
as an information claim.

**Required co-metric.** Arms are only comparable if they achieve comparable
*generic* stopping competence. Each arm must therefore also report held-out
response-boundary discrimination on ordinary instruction data (goal-independent).
An arm that cannot stop at all has not failed the goal test — it has failed to
train.

---

## 2026-09-17 — Design change: Layer C moves from OLMo-2 1B to Olmo-3 7B base

**This is an execution change, not a claim change.** The mother question, the
identification logic, and the four-arm parameter-locus design are untouched.

### What was observed

The same E01 instrument, in the same format-matched plain serialization, on the
OLMo-2 1B lineage (`d_stop`, all 50 pairs and by family):

| stage | ALL | A bounded | B semantic (no number) | C slots |
|---|---|---|---|---|
| Base | +1.83 | +0.53 | +1.02 | +5.34 |
| SFT | +5.03 | +3.32 | **+1.53** [0.1, 2.7] | +12.67 |
| DPO | +7.53 | +7.04 | **+2.12** [0.4, 3.6] | +15.22 |

versus Olmo-3 7B, same instrument, same format:

| stage | ALL | A bounded | B semantic | C slots |
|---|---|---|---|---|
| Base | +3.89 | +4.15 | +1.66 | +6.19 |
| SFT | +8.09 | — | — | — |
| DPO | +12.30 | +17.57* | **+8.61** [5.5, 11.9] | +20.45* |

(*chat-format numbers for the by-family split.)

### Why this forces a model change

At 1B the semantic-predicate family — the one family that states **no
cardinality anywhere**, and therefore the one that decides whether this is more
than counting — barely moves even in the fully post-trained checkpoint
(`d_stop` +2.12, CI touching 0.4). Layer C asks whether a constrained arm can
close the Base→post-training gap. On family B at 1B that gap is +1.0 → +2.1,
which is not resolvable against the noise floor.

**This is not a knowledge artefact.** Continuation awareness is essentially
identical at the two scales (family B: correct missing token top-5 for 93% of
items at both 1B and 7B, median rank 0). The 1B genuinely has weaker
goal-relative stopping on semantic goals; it does not merely fail to know the
answer. Per `RESEARCH_EXECUTION.md` §4, running the causal arms where the
reference effect is below attainable resolution would produce a difference
between two near-zero effects, which is not a training-mechanism result.

### Decision

Layer C runs from `allenai/Olmo-3-1025-7B` (base), which is already local and is
the same base whose natural trajectory E01 measured. The OLMo-2 1B trajectory is
retained as a secondary scale observation, not as the causal substrate.

### Implementation consequences, checked

- **Stop set for E02 is `<|endoftext|>` only.** Olmo-3 lists `<|im_end|>` as a
  second generation stop id, but in the single-turn training template
  `<|im_end|>` occurs only inside the loss-masked prompt. Including it would
  have arm R learning a delta on a token the assistant never emits. The arms
  therefore use exactly one stop row, which is also what makes the
  readout-vs-state contrast clean.
- **Memory.** Arms R and Rmlp need no gradient through the transformer at all
  (every model parameter is frozen, so the only gradient path is
  `h -> readout`); the base forward runs under `no_grad`. Only S and F need real
  training, with 8-bit AdamW and gradient checkpointing to fit 7B on one card.

### What this does NOT change

The 1B results stay in the record exactly as measured. No family, stimulus, or
metric was dropped, and the model change is justified by a resolution argument
that was stated before any arm was trained — not by an arm result.

---

## 2026-09-17 — Adopted family D: a lexically matched control for the slot family

`src/build_stimuli_d.py`, `stimuli/e01_pairs_d.jsonl` (12 pairs).

**This control distinguishes** (X) the stop shift reflects whether the user's
goal is already satisfied **from** (Y) it reflects plain lexical priming — in
family C only the *incomplete* prompt contains the missing field's words, so a
model that merely checks "have I already emitted the string the prompt names?"
would produce the same result.

Family D holds the lexical content constant and flips only the polarity:

```
complete:   "report the name and occupation, but not the country of birth"
incomplete: "report the name, occupation, and country of birth, but not the
             year of birth"
```

Both prompts contain "country of birth" verbatim, both contain the same
"but not the ..." negation frame, and both share the replayed two-line prefix
and the same competitor token.

| checkpoint | n | d_goal | **d_stop** | 95% CI | stop-side share |
|---|---|---|---|---|---|
| Olmo-3 7B base | 12 | 11.22 | **+6.51** | [5.6, 7.3] | 58% |
| OLMo-2 1B base | 12 | 5.90 | **+4.99** | [4.3, 5.6] | 84% |
| OLMo-2 1B SFT | 12 | 10.58 | **+9.37** | [8.5, 10.2] | 89% |
| OLMo-2 1B DPO | 12 | 16.12 | **+12.76** | [11.8, 13.7] | 79% |

**What this rules out.** Lexical priming as the explanation of the slot-family
effect. The effect survives with the missing field's words present in *both*
prompts, and the stop-side share is *higher* here (79–89%) than in family C,
not lower. It also rules out "the model is just reacting to seeing a field name
it has not yet printed".

Family D is adopted as a standing control and is run alongside the frozen
primary instrument. It is kept in a separate file so the 50-pair A/B/C
instrument stays exactly as it was when first run.

---

## 2026-09-17 — Layer C targets, measured in exactly the E02 format

Arm 0 must be measured in the format the arms are trained and evaluated in, not
in the plain serialization. Grafting the SFT chat template onto the base
checkpoint and scoring only `<|endoftext|>` (the E02 stop set):

| | ALL | A bounded | B semantic | C slots |
|---|---|---|---|---|
| **Arm 0 (base, grafted)** `d_stop` | **+2.58** [2.1, 3.0] | +2.40 | +1.42 | +4.36 |
| **natural SFT** `d_stop` | **+12.50** [11.0, 14.0] | +13.43 | +6.76 | +17.87 |

Headroom is ~10 log-units on the primary aggregate and is well above the noise
floor in every family, so the four arms are resolvable. These two rows are the
frozen reference points the arms are read against.

**A fact that shapes the interpretation.** In this chat format the Olmo-3 base
checkpoint already has near-ceiling *generic* boundary competence
(`boundary_auc` = 0.9988; log p(stop) = −1.29 at a true response boundary vs
−14.08 response-internally). So the arms are not being asked to learn "stop
somewhere sensible" from scratch — the pretrained model can already do that in
this format. What they are being asked to acquire is specifically the
*goal-relative* part. This makes the readout-vs-state contrast sharper, and it
means a failed arm cannot be dismissed as "it never learned to stop at all" —
but the `boundary_auc` co-metric is still reported per arm to check that.

---

## 2026-09-17 — E02 compute pathology found and fixed (before any arm result)

The first S-arm attempt ran at **>70 s per optimizer step**, which would have
made the causal experiment unaffordable. Rather than accept a degraded design,
the step was profiled directly:

```
fwd 0.25  loss 0.00  bwd 0.51  clip 0.03  opt 0.18  freeze 0.00  TOTAL 0.98
peak mem 58.8 GB
```

The training math was never the problem. Three real causes, all fixed:

1. **Gradient checkpointing was on for no reason.** A 7B S/F arm peaks at ~59GB
   of a 96GB card without it. Now opt-in (`--grad-ckpt`), off by default.
2. **The loss upcast the entire `[B, T, 100278]` logit tensor to float32**,
   which OOM-ed the first S sweep outright. Replaced with `chunked_ce`, and the
   eval now scores only supervised positions.
3. **Rendering the chat template was single-threaded CPU work** that dominated
   wall-clock and was repeated in every run. The tokenized dataset is now cached
   to disk. This is also a scientific improvement: every arm now provably trains
   on byte-identical inputs in an identical order.

Measured after the fix: **2.1 s per optimizer step** (16 sequences), a ~35x
speedup. Batch geometry is now identical across all arms and sweeps:
`bs 4 x accum 4 = 16 sequences/step, max_len 768`.

Because the geometry changed, the R and Rmlp learning-rate sweeps were **re-run
from scratch** under the final configuration rather than carried over.

---

## 2026-09-17 — E02 learning-rate selection (per arm, by held-out CE only)

LR is selected **per arm** on held-out cross-entropy over ordinary instruction
data, never on the E01 goal effect. The arms differ by six orders of magnitude
in trainable-parameter count (R: 4,097; Rmlp: 2,098,177; S/F: ~7B), so a single
shared LR would handicap the constrained arms and manufacture the very result
the experiment is testing for.

`val_loss` is comparable **within** an arm's sweep, which is all it is used for.
(The R and Rmlp sweeps evaluated on different numbers of val batches, so their
absolute `val_loss` values are not comparable to each other; the final runs all
use the same evaluation size.)

All four sweeps, 120 steps, identical batch geometry and identical cached data:

| arm | trainable | lr | val_loss | boundary_auc | selected |
|---|---|---|---|---|---|
| R | 4,097 | 3e-4 | 0.75676 | 0.9995 | |
| R | | 1e-3 | 0.75587 | 0.9998 | |
| R | | **3e-3** | **0.75581** | 0.9997 | ✓ |
| R | | 1e-2 | 0.75895 | 0.9992 | |
| Rmlp | 2,098,177 | 3e-4 | 0.75578 | 0.9998 | |
| Rmlp | | **1e-3** | **0.75478** | 0.9998 | ✓ |
| Rmlp | | 3e-3 | 0.75478 | 0.9998 | |
| Rmlp | | 1e-2 | 0.75530 | 0.9999 | |
| S | ~7.3B | 5e-6 | 0.67572 | 0.9982 | |
| S | | 1e-5 | 0.64371 | 0.9995 | |
| S | | **2e-5** | **0.63250** | 0.9998 | ✓ |
| S | | 5e-5 | 0.64756 | 0.9999 | |
| F | ~7.3B | 5e-6 | 0.67583 | 0.9981 | |
| F | | 1e-5 | 0.64373 | 0.9995 | |
| F | | **2e-5** | **0.63267** | 0.9998 | ✓ |
| F | | 5e-5 | 0.64718 | 0.9999 | |

**Every arm selects an interior optimum of its grid**, so no selected LR is a
boundary artefact, and no arm was left at an LR that merely failed to train.
S and F independently land on 2e-5, which is also the published Tülu-3 / OLMo-2
SFT learning rate — a reassuring external check rather than a tuned choice.

Note that `val_loss` is only comparable *within* a column here: the constrained
arms can move a single logit, so their achievable loss reduction is structurally
much smaller than S/F's. The cross-arm comparison that matters is `boundary_auc`
(generic stopping competence, near-ceiling everywhere) and `d_stop` (the goal
effect), not `val_loss`.

---

## 2026-09-17 — E02 RESULT: the parameter locus is not the bottleneck

**This experiment distinguishes** (A) the goal information is already present and
usably readable in pretrained states, so post-training mainly has to attach the
stop action to it **from** (B) post-training must reorganize internal
computation before user-goal completion can control termination.

All arms: Olmo-3 7B base, the same 12,000 ordinary Tülu-3 instruction-response
examples in the same order (byte-identical cached tokenization), the same format,
the same batch geometry (16 sequences/step, max_len 768), 750 steps, per-arm LR
selected on held-out CE only. Stop set = `<|endoftext|>` only. Seed 0.

### Primary: `d_stop` on the 50-pair A/B/C instrument

| | trainable params | **d_stop** | 95% CI | val_loss | boundary_auc |
|---|---|---|---|---|---|
| **Arm 0** base, no training | 0 | **+2.58** | [2.1, 3.0] | — | 0.9988 |
| **Arm R** stop readout only | **4,097** | **+7.58** | [6.4, 8.8] | 0.7563 | 0.99978 |
| **Arm Rmlp** MLP readout on frozen state | 2,098,177 | **+7.05** | [6.1, 8.0] | 0.7543 | 0.99987 |
| **Arm S** everything *but* the stop row | 7,298,011,136 | **+7.93** | [6.9, 8.9] | 0.6238 | 0.99993 |
| **Arm F** everything | 7,298,011,136 | **+7.72** | [6.7, 8.7] | 0.6236 | 0.99993 |
| *natural SFT (orientation only)* | *full recipe* | *+12.50* | *[11.0, 14.0]* | — | — |

Family D (lexically matched): R +12.93, Rmlp +11.04, S +9.94, F +9.79.

### Observation

1. **Every trained arm moves far above base, and all four are statistically
   indistinguishable from each other.** The confidence intervals overlap
   heavily; no arm is even nominally outside another's interval.
2. **Arm R matches full SFT while changing 4,097 parameters** — one output row's
   additive delta — with *every non-stop logit bit-exactly identical to the
   pretrained model* (verified, not assumed; see Gate C).
3. **Capacity is not the limit.** Rmlp gives the readout a 500x larger,
   nonlinear function of the same frozen hidden state and gains nothing
   (+7.05 vs +7.58).
4. **Changing 7.3B internal parameters buys nothing here either.** S and F are
   *much better language models* after training (val_loss 0.624 vs 0.756) yet
   are no better at goal-relative stopping than the 4,097-parameter readout.
5. Generic stopping competence is at ceiling in every arm
   (boundary_auc 0.9998–0.9999), so no arm's result is a failure-to-train
   artefact.

### What this rules out

- **Explanation B (state reorganization is necessary).** Arm S was free to
  change all 7.3B internal parameters and every non-stop output row; it did not
  exceed an arm that changed nothing but the stop row. More decisively, Arm R
  reached the same place with the internal computation provably untouched.
- **"The readout just isn't expressive enough" as a rescue of B.** Rmlp tests
  exactly that and does not help.
- **"Arm R never learned to stop."** Its boundary_auc is 0.99978 and its
  log p(stop) at a true boundary is −0.42.

### What remains

**A is supported: at this budget the goal information is already present in the
pretrained final hidden state in a form a linear stop readout can use, and what
post-training contributes is attaching the stop action to it.** The parameter
locus is not the binding constraint — every locus reaches the same place.

**The honest open question is the remaining gap to natural SFT (+7.6 vs +12.5).**
This is *not* identified as a locus effect: our arms saw 12k examples for 750
steps, while the released SFT checkpoint saw the full Tülu-3 recipe. The gap is
confounded with data and compute scale. The identified claim is the
**arm-vs-arm** comparison under matched budget; the natural SFT row is an
orientation point, not a control.

### Highest-value next experiments

1. **Seed replication** (running) — confirm the four-arm equivalence is not seed
   noise.
2. **Budget ladder on Arm R vs Arm F.** Train both at 250 / 750 / 2250 steps. If
   the two curves rise together and stay indistinguishable, the gap to natural
   SFT is a data/compute effect and the locus conclusion holds at every budget.
   If F pulls away from R only at large budget, then state change *is*
   load-bearing but only beyond some scale — a different and more interesting
   law. **This is the experiment that decides whether the headline is
   "readout suffices" or "readout suffices up to a budget".**


---

## 2026-09-17 — Seed replication, a pairing bug, and the sharpened estimate

### Seed 1 replicates the four-arm equivalence

`d_stop`, 50 pairs, seed 1 (seed 0 in brackets):

| arm | d_stop seed 1 | [seed 0] |
|---|---|---|
| R | +6.90 [5.9, 7.9] | [+7.58] |
| Rmlp | +7.04 [6.2, 7.9] | [+7.05] |
| S | +8.19 [7.1, 9.2] | [+7.93] |
| F | +8.14 [7.1, 9.1] | [+7.72] |

Same ordering, same magnitudes. The four-arm result is not seed noise.

### A pairing bug, found and fixed

Comparing arms by whether their mean confidence intervals overlap is weak: the
arms are evaluated on the *same* items, so item-to-item variance is shared and
should be differenced out. Writing the paired test surfaced a real defect:
**three `item_id` labels collide** (two ordered-list topics share their first 18
characters, and two family-B items share `missing` and prefix length), so keying
on `item_id` silently merged those items and reported n=47 instead of 50.

Fixed two ways: the paired analysis keys on **row order**, which is identical
across every run and asserted against the carried `item_id`; and the generator
now disambiguates colliding labels. The per-file analyses were never affected —
they iterate rows, not a dict — so no previously reported number changes.

### Sharpened estimate: paired within-item contrasts, both seeds pooled

| contrast | n | mean diff | 95% CI | sign p | +/− |
|---|---|---|---|---|---|
| R − base | 50 | **+4.66** | [3.92, 5.42] | 3.7e-11 | 47/3 |
| Rmlp − base | 50 | +4.47 | [3.88, 5.04] | 9.1e-14 | 49/1 |
| S − base | 50 | +5.48 | [4.73, 6.17] | 2.3e-12 | 48/2 |
| F − base | 50 | +5.35 | [4.62, 6.02] | 2.3e-12 | 48/2 |
| **S − R** | 50 | +0.81 | [0.17, 1.48] | **0.20** | 30/20 |
| **F − R** | 50 | +0.69 | [0.06, 1.34] | **0.48** | 28/22 |
| **Rmlp − R** | 50 | −0.19 | [−0.48, 0.08] | 0.12 | 19/31 |

> **Readout-only recovers 87% of the base → full-SFT gain
> (4.66 of 5.35 log-units), changing 4,097 parameters with every non-stop
> logit bit-exactly frozen.**

### The honest reading

The large effect (base → any trained arm, ~+5 log-units, 47–49 of 50 items) is
robust and locus-independent. The residual state contribution is **small and not
consistent across items**: `S − R` and `F − R` have mean CIs that just exclude
zero, but their sign tests are null (30/20 and 28/22), so the mean is carried by
a subset of items rather than a broad shift. The correct statement is therefore
*not* "state adaptation contributes nothing", but:

> **Stop-readout adaptation over a frozen pretrained state accounts for the
> large majority of acquired goal-relative stopping; whatever internal-state
> adaptation adds on top is small and item-dependent.**

Capacity is not the limit either: `Rmlp − R` is if anything negative.

### Still open, and queued

The gap to the released SFT checkpoint (+7.9 vs +12.5) remains confounded with
data/compute scale. The **budget ladder** (R and F at 250 / 750 / 2250 steps) is
running and is what decides whether the headline is "readout adaptation
suffices" or "readout adaptation suffices up to a budget".

---

## 2026-09-17 — BUDGET LADDER: the headline changes to "readout suffices *up to a budget*"

**This experiment distinguishes** (X) readout adaptation suffices — R and F rise
together at every budget, so the gap to the released checkpoint is purely
data/compute **from** (Y) readout adaptation suffices only up to a budget — F
pulls away once the budget is large enough, so internal-state change is
load-bearing beyond some scale.

Same corpus, order, format, geometry and per-arm LR as the main run; only the
number of optimizer steps varies. Seed 0.

| steps | R `d_stop` | F `d_stop` | **F − R (paired)** | 95% CI | sign p | +/− |
|---|---|---|---|---|---|---|
| 0 (base) | +2.58 | +2.58 | — | | | |
| 250 | +6.37 | +7.34 | +0.97 | [0.44, 1.50] | 0.065 | 32/18 |
| 750 | +7.58 | +7.72 | **+0.14** | [−0.56, 0.83] | 0.67 | 27/23 |
| 2250 | +8.69 | **+10.78** | **+2.09** | [0.91, 3.26] | **0.015** | 34/16 |
| *natural SFT* | | *+12.50* | | | | |

### Correction to the previous entry

**The preceding entry's reading was budget-specific and is superseded.** The
main four-arm experiment was run at 750 steps, which is — by coincidence —
exactly where the R/F gap is at its *minimum*. Reading "readout adaptation
suffices, 87% of the gain, locus is not the bottleneck" off that single budget
was overconfident. At 2250 steps the full arm pulls clearly ahead, consistently
across items (34/16, sign p = 0.015).

The "87% of the base→full-SFT gain" figure remains correct **as a statement
about the 750-step budget**, and only that.

### Observation

- **R decelerates; F does not.** R goes +6.37 → +7.58 → +8.69 (gains of +1.21,
  +1.11 over 3x budget each) while F goes +7.34 → +7.72 → +10.78 (+0.38, then
  +3.06). R looks like it is saturating; F is still climbing toward the natural
  SFT level.
- **F's late gain is not general language-model improvement.** F's held-out CE
  *worsens* after step 450 (0.626 → 0.659 — it is overfitting the 12k corpus),
  while its goal-relative stopping keeps rising. So the extra goal-relativity is
  being acquired specifically, not as a by-product of getting better at the
  corpus.
- Generic stopping competence stays at ceiling in both arms at every rung
  (`boundary_auc` ≥ 0.9995), so no rung is a failure-to-train artefact.

### Current reading of the parent question

Acquisition of goal-relative stopping has **two components with different budget
scaling**:

1. **A large, cheap, readout-attachable component.** Most of the effect is
   available immediately from the frozen pretrained state through a 4,097-
   parameter stop-readout delta — the goal information is already there and
   already linearly readable. This saturates.
2. **A slower component that requires internal-state change.** Closing the
   remaining distance to post-training-level goal-relative stopping needs the
   internal computation to change, and that part keeps accruing with budget.

This is outcome 4 in the registered list (hybrid acquisition), with added
structure the plan did not anticipate: the two components are separated not by
which is bigger but by **how they scale with training budget**. Reporting either
component alone would misdescribe the phenomenon.

### Status and next step

**Seed 1 of the full ladder is running.** The 2250-step divergence rests on one
seed so far and must replicate before it is load-bearing. Until then this entry
records a strong but single-seed finding, not a settled result.

---

## 2026-09-17 — Budget ladder replicated (2 seeds): the two-component law holds

`F@2250` replicates almost exactly across seeds: **+10.78** (s0) and **+10.84**
(s1). Pooling both seeds, paired over the 50 items:

| steps | R `d_stop` | F `d_stop` | **F − R (paired)** | 95% CI | sign p | +/− |
|---|---|---|---|---|---|---|
| 0 (base) | +2.58 | +2.58 | — | | | |
| 250 | +6.70 | +7.50 | +0.80 | [0.31, 1.31] | **0.00094** | 37/13 |
| 750 | +7.24 | +7.93 | +0.69 | [0.06, 1.34] | 0.48 | 28/22 |
| 2250 | +8.47 | **+10.81** | **+2.34** | [1.25, 3.43] | **0.0026** | 36/14 |
| *natural SFT* | | *+12.50* | | | | |

### Second correction, in the other direction

With both seeds pooled, `F − R` is **positive at every budget**, and at 250
steps it is now strongly consistent across items (37/13, sign p = 0.00094). The
750-step rung, where the single-seed run showed a null, is the outlier rather
than the rule.

So the earlier framing "at 750 steps the locus does not matter" was an artefact
of one budget in one seed. **Internal-state adaptation contributes at every
budget tested.** What changes with budget is the *size* of that contribution.

### Settled reading of the parent question

Acquisition of goal-relative stopping decomposes into two components that differ
in how they scale with training budget:

1. **A large, immediately available readout component.** From the frozen
   pretrained state, a **4,097-parameter** additive delta on the single stop
   output row — with every non-stop logit bit-exactly unchanged — lifts
   `d_stop` from +2.58 to +6.70 within 250 steps, i.e. roughly half the distance
   to the released post-trained checkpoint. The goal information is already in
   the pretrained final hidden state and already linearly readable. Giving the
   readout 500x more capacity and a nonlinearity (Rmlp) adds nothing, so this
   component is limited by the state, not by the readout.
   **This is the "reuse" half of the answer.**

2. **A smaller but growing state component.** Full adaptation beats the frozen
   state at every budget, and the margin grows from +0.80 (250 steps) to +2.34
   (2250 steps) while the readout route saturates (R: +6.70 → +7.24 → +8.47,
   decelerating). Notably F's late gain is **not** general language-model
   improvement — its held-out CE worsens after step 450 while its goal-relative
   stopping keeps rising.
   **This is the "new computation" half.**

The registered outcome this matches is #4, hybrid acquisition — but with
structure the plan did not anticipate: the two components are distinguished by
their **budget scaling**, not by which is larger. Reporting either alone
misdescribes the phenomenon, and reporting a single budget can flip the apparent
answer.

### Methodological lesson worth keeping

A four-arm parameter-locus comparison at **one** training budget is not
identified. Both of this project's wrong readings came from reading a locus
conclusion off a single budget — first "locus doesn't matter", then "locus only
matters at large budget". Only the ladder, replicated, gave the stable law. Any
future arm comparison in this project must be run at more than one budget.

---

## 2026-09-18 — Normalizer-free recomputation: the residual is continuation suppression, not a stronger stop readout

Zero GPU; recomputed from the raw logits already stored in every result row
(`src/e01_rawlogit.py`).

### Why this was necessary

The headline used `d_stop = Δ log p(STOP)`. Since
`log p_stop = z_stop − log Z`, that quantity carries a whole-vocabulary
normalizer difference between two *different* prompts. A locus claim of the form
"this part is the stop readout, that part is internal state" must not rest on a
term that any change to the rest of the vocabulary can move.

Three gauges, all from the same rows. `d_goal` (the margin) is exactly
normalizer-free and is the behaviourally decisive quantity, since stopping
happens when STOP outranks the continuation.

| | **d_goal** (gauge-free) | Δlog p_stop | Δlog p_cont | Δz_stop | **Δz_cont** | Δlog Z |
|---|---|---|---|---|---|---|
| base | 7.50 | 2.58 | −4.92 | 8.16 | **+0.65** | 5.58 |
| R@250 | 11.70 | 6.70 | −5.00 | 12.36 | **+0.67** | 5.66 |
| R@750 | 12.22 | 7.24 | −4.98 | 12.88 | **+0.67** | 5.64 |
| R@2250 | 13.53 | 8.47 | −5.06 | **14.19** | **+0.67** | 5.73 |
| F@250 | 11.39 | 7.50 | −3.89 | 10.86 | −0.53 | 3.36 |
| F@750 | 12.28 | 7.93 | −4.35 | 11.25 | −1.03 | 3.32 |
| F@2250 | 18.80 | 10.81 | −7.99 | 13.32 | **−5.48** | 2.51 |
| natSFT | 17.33 | 12.50 | −4.84 | 11.94 | **−5.40** | −0.56 |

### Observation

1. **R's `Δz_cont` is pinned at +0.67, identical to base, at every budget.**
   This is not a statistical finding but a structural one: R cannot change the
   continuation logit at all. It also serves as a live freeze check on the eval
   path, and it passes.
2. **F's margin advantage at 2250 is continuation suppression.** `Δz_cont` goes
   −0.53 → −1.03 → **−5.48**: as the budget grows, F increasingly *suppresses
   the correct next item* when the goal is already satisfied. That is a change
   to the content computation, not a stronger stop action.
3. **On the stop side against an unchanged background, R beats F everywhere**
   (`Δz_stop`: R 12.36/12.88/14.19 vs F 10.86/11.25/13.32), and R@2250 (14.19)
   even exceeds the released post-trained checkpoint (11.94).
4. **Real post-training does the same thing F does.** natSFT's `Δz_cont` is
   −5.40, essentially F@2250's −5.48. The continuation-suppression component is
   not an artefact of our training setup; it is what the released recipe
   produces too.

### Claim wording, corrected as flagged

Do **not** write "a growing pure internal-state component". Two reasons: the S
arm also lets the non-stop output rows move, so it was never "state only"; and
the residual's signature is continuation-side, not stop-side. The defensible
statement is:

> **a large stop-readout component, plus a growing residual that requires
> adaptation beyond the stop readout and whose signature is goal-conditioned
> suppression of the continuation.**

This is stronger than the previous wording, not weaker: the residual now has an
identified character instead of being a leftover.

### Revised two-component reading

1. **Stop attachment.** Cheap, saturating, fully supported by the frozen
   pretrained state. A 4,097-parameter delta on one output row extracts *more*
   goal-sensitivity on the stop logit than full SFT does. Capacity is not the
   limit (Rmlp adds nothing). **The pretrained state already contains the goal
   information and already exposes it to a linear stop readout.**
2. **Continuation suppression.** Requires changing parameters outside the stop
   row, grows with budget, and is what the released checkpoint also does. This
   is what the readout route structurally cannot do.

Behavioural stopping needs both: the model must both raise STOP and lower what
it would otherwise say next.

### Open, and running

Whether component 2 is *internal computation* or merely *non-stop output rows*
is not yet identified — the F and S arms both allow both. `Sbody` (the strict
state-only arm: entire output head frozen bit-exactly, only the transformer body
and input embeddings move) is running at 250/750/2250 alongside S. All five arms'
freezes are now verified on the actual Olmo-3 7B model, including `Sbody`'s whole
head being byte-identical.

Also fixed: `e02_verify_freeze.py` took its checkpoint from a hard-coded
`olmo2-1b` constant after Layer C had moved to Olmo-3 7B. It is now a CLI
argument, runs one arm per process, keeps the fp32 reference on CPU, and checks
the 7B arms in bf16 with SGD (a 7B fp32 model plus Adam state is ~116GB; the
freeze claim is dtype-independent).

---

## 2026-09-18 — Raw-logit decomposition: the residual is CONTINUATION SUPPRESSION, not a better stop readout

Zero GPU. Recomputed from the raw logits already stored in every result file
(`src/e01_rawlogit.py`).

### Why the gauge matters

The headline had been `d_stop = Δ log p(STOP)`. But
`log p_stop = z_stop − log Z`, so `d_stop` carries a whole-vocabulary
normalizer term from two *different* prompts. That term is not a property of
the stop action, so a **parameter-locus** claim must not rest on it. The
`dlogZ` column below shows the term is large and, crucially, **differs
systematically by arm** (R ≈ 5.7 throughout, F falls 3.36 → 2.51, natSFT −0.56).

Three gauges, all exact:

```
d_goal  = dz_stop − dz_cont        gauge-free; decides stop-vs-continue
d_stop  = dz_stop − dlogZ          probability gauge; behavioural but vocabulary-wide
dz_stop = w_stop · (h_complete − h_incomplete)     the stop readout itself
```

### The table

| | `d_goal` | `dz_stop` | `dz_cont` | `dlogZ` |
|---|---|---|---|---|
| base | 7.50 | 8.16 | +0.65 | 5.58 |
| R@250 | 11.70 | 12.36 | +0.67 | 5.66 |
| R@750 | 12.22 | 12.88 | +0.67 | 5.64 |
| R@2250 | 13.53 | **14.19** | **+0.67** | 5.73 |
| F@250 | 11.39 | 10.86 | −0.53 | 3.36 |
| F@750 | 12.28 | 11.25 | −1.03 | 3.32 |
| F@2250 | 18.80 | **13.32** | **−5.48** | 2.51 |
| natSFT | 17.33 | **11.94** | **−5.40** | −0.56 |

Paired against base, both seeds pooled, 50 items:

| contrast | `dz_stop` | sign | `dz_cont` | sign | `d_goal` |
|---|---|---|---|---|---|
| R@2250 − base | **+6.04** [5.00, 7.09] | 49/1 | **+0.01** [−0.01, 0.04] | 25/14 | +6.03 |
| F@2250 − base | +5.16 [3.98, 6.33] | 44/6 | **−6.14** [−7.25, −5.04] | 3/47 | +11.30 |
| natSFT − base | +3.78 [2.29, 5.30] | 37/13 | −6.05 [−7.70, −4.49] | 8/42 | +9.83 |

### What this changes

**The previous "growing state component" was not a stronger stop readout.**

1. **On the stop readout axis, readout-only is the best arm, not the worst.**
   `dz_stop` gain over base: R **+6.04** > F +5.16 > natSFT +3.78. A
   4,097-parameter delta extracts *more* goal sensitivity from the frozen
   pretrained state than full fine-tuning does, and more than the released
   post-trained checkpoint has.
2. **R's continuation side is pinned at exactly zero** (+0.01, CI [−0.01, 0.04]).
   That is structural — R cannot touch a non-stop logit — and it doubles as an
   independent confirmation that the freeze held at evaluation time.
3. **F's and natSFT's extra behavioural margin is continuation suppression.**
   F's total gain +11.30 splits almost evenly into stop-readout +5.16 and
   continuation-suppression +6.14. For the released checkpoint the
   continuation half (+6.05) is the *larger* one.
4. **It is the continuation half that grows with budget**, not the readout half:
   F's `dz_cont` goes −0.53 → −1.03 → −5.48 while its `dz_stop` moves only
   10.86 → 13.32, tracking R's 12.36 → 14.19.

### Corrected statement of the result

> Goal-relative stopping is acquired through **two mechanisms in different
> parameter loci, doing different jobs**:
>
> 1. **the stop readout learns to read goal completion off an already-sufficient
>    pretrained state** — 4,097 parameters suffice, extra capacity adds nothing
>    (Rmlp), and this route alone matches or beats full fine-tuning *on the stop
>    logit itself*;
> 2. **the content computation learns to suppress the correct continuation once
>    the goal is satisfied** — which the stop readout structurally cannot do,
>    and which is what keeps growing with training budget.
>
> Ordinary post-training does both, and in the released checkpoint the
> continuation-suppression half is the larger contributor to the behavioural
> stopping margin.

This supersedes both earlier readings ("locus doesn't matter" and "a growing
state component strengthens goal-relative stopping"). It is also a sharper
answer to the parent question than the registered outcome list anticipated:
the reuse-vs-new-computation dichotomy is wrong not because the answer is
"hybrid", but because **the two loci are not competing to do the same job.**

### Open

`S` (may move non-stop output rows) vs `Sbody` (strict state-only, entire head
frozen) at 250/750/2250 is running. That separates "the residual is internal
computation" from "the residual is the rest of the output head" — the two are
still confounded in `F`.

---

## 2026-09-18 — Sbody settles it: the residual is INTERNAL COMPUTATION, and the two routes do different jobs

**This experiment distinguishes** (X) the "beyond the stop readout" residual is
genuine internal-computation change **from** (Y) it lives in the *rest of the
output head*, which `F` and `S` both leave free and which would be a much weaker
claim.

New arm `Sbody`: the **entire** output head is frozen — stop row and all
100,277 non-stop rows — so only the transformer body and input embeddings may
move. 6,887,272,448 trainable parameters. Freeze verified bit-exact on the
actual Olmo-3 7B checkpoint after real optimizer steps (`ENTIRE lm_head
byte-identical: PASS`).

Seed 0, same corpus/order/format/geometry/LR as every other arm:

| | `d_goal` | `dz_stop` | `dz_cont` |
|---|---|---|---|
| base | 7.50 | 8.16 | +0.65 |
| R@250 / @750 / @2250 | 11.35 / 12.59 / 13.81 | 12.02 / 13.25 / **14.48** | +0.67 / +0.67 / **+0.67** |
| Sbody@250 / @750 / @2250 | 11.54 / 12.10 / 17.73 | 10.42 / 10.26 / **12.73** | −1.11 / −1.84 / **−5.00** |
| S@2250 (non-stop rows free) | 18.16 | 13.43 | −4.73 |
| F@2250 (everything free) | 17.97 | 13.09 | −4.88 |
| natSFT | 17.33 | 11.94 | −5.40 |

### Observation

1. **`Sbody` ≈ `S` ≈ `F` at every budget.** With the entire output head frozen,
   the strict state-only arm reproduces full fine-tuning (d_goal 17.73 vs 18.16
   vs 17.97 at 2250). **The residual is internal computation.** It is not the
   non-stop output rows, which `Sbody` cannot touch.
2. **Both routes raise the stop readout's goal sensitivity, by opposite means.**
   `dz_stop = w_stop · (h_complete − h_incomplete)` goes 8.16 → 14.48 when only
   `w_stop` may move (R, h frozen) and 8.16 → 12.73 when only `h` may move
   (Sbody, `w_stop` byte-frozen). Rotating the readout toward the goal direction
   and reshaping the state to align with the frozen readout are close to
   interchangeable for this term.
3. **Only the state route can suppress the continuation.** R's `dz_cont` is
   pinned at +0.67 by construction; Sbody drives it to −5.00, matching S, F and
   the released checkpoint (−4.73, −4.88, −5.40). This is the whole source of
   the state route's larger behavioural margin.

### Settled answer to the parent question

> Goal-relative stopping is acquired by **two routes that are not competing to
> do the same job**.
>
> - **Reading**: making goal completion visible to the stop action. Pretraining
>   already supplies this almost fully (`dz_stop` = 8.16 at base, 47/3 items),
>   and either locus can sharpen it — 4,097 readout parameters do it slightly
>   better than 6.9B internal parameters.
> - **Clearing**: suppressing the still-plausible continuation once the goal is
>   satisfied. This requires changing internal computation; a stop readout
>   cannot do it at any capacity, and it is what keeps growing with budget and
>   what the released post-trained checkpoint mostly relies on.
>
> Behavioural stopping is the sum of the two. The classic framing
> "reuse vs new representation" fails not because the answer is "both" but
> because **the stop action's sensitivity and the competitor's suppression are
> different problems with different parameter loci.**

### Still to confirm

- Seed 1 for the `Sbody` ladder.
- Arm 0 is currently measured through a slightly different eval code path than
  the arms (`device_map="cuda"` vs in-process), which costs ~0.06 logits of bf16
  path noise — immaterial to every effect above, but the artifact should use one
  path. Fix: measure base as an `lr=0` R run, which is bit-identical to base by
  the zero-init construction and goes through the arms' own path.

---

## 2026-09-18 — External lineages: the effect follows the END-OF-TURN token, not the family

**This experiment distinguishes** (X) goal-relative stopping is a property of
assistant stopping acquisition **from** (Y) it is an artefact of OLMo's token
wiring, where one native `<|endoftext|>` happens to serve both document-end and
turn-end.

Two independent non-OLMo lineages were chosen precisely because they use the
*opposite* stopping architecture — a **separate end-of-turn token**:

| family | document-end token | end-of-turn token |
|---|---|---|
| OLMo-3 7B | `<\|endoftext\|>` | *same token* |
| Qwen2.5 7B | `<\|endoftext\|>` | `<\|im_end\|>` |
| Llama-3.1 8B | `<\|end_of_text\|>` | `<\|eot_id\|>` |

Both tokens are scored **separately** on every checkpoint, so base and instruct
are compared on an identical token set (using each checkpoint's own generation
stop set would silently change the measured quantity between stages).
Native chat format; base checkpoints get the instruct template grafted.

`dz_stop`, 50 pairs:

| checkpoint | document-end | sign | **end-of-turn** | sign |
|---|---|---|---|---|
| Qwen2.5 base | −2.60 | 6/44 | **+3.79** [3.1, 4.5] | 46/3 |
| Qwen2.5 Instruct | +6.96 | 47/3 | **+6.94** [5.7, 8.2] | 48/2 |
| Llama-3.1 base | −0.04 | 24/25 | **+2.47** [2.0, 2.9] | 45/5 |
| Llama-3.1 Instruct | −2.57 | 8/42 | **+6.63** [5.6, 7.6] | 48/2 |

### Observation

1. **The effect lives on the token that actually ends the turn**, in both
   new-EOT families, at both stages. It is not a general "this text is
   finishing" signal: in Llama-3.1 Instruct the document-end token moves
   *against* goal completion (−2.57, 8/42) while the turn-end token moves
   strongly with it (+6.63, 48/2). That double dissociation is only possible in
   an architecture where the two tokens are distinct — which is exactly why
   these families were chosen.
2. **The base-checkpoint finding replicates in both lineages.** Goal-sensitive
   ordering on the turn-end token is already present before any instruction
   tuning: Qwen +3.79 (46/3), Llama +2.47 (45/5), alongside OLMo-3's +8.16
   (47/3). Three lineages, two stopping architectures, same qualitative
   structure.
3. **Post-training amplifies it, it does not create it**: Qwen 3.79 → 6.94,
   Llama 2.47 → 6.63.

### A second, independent vindication of the gauge caution

The `d log p` column disagrees with `dz_stop` *in sign* in several cells — e.g.
Qwen2.5 base document-end is `dz_stop` = −2.60 but `d log p` = +2.68. A
whole-vocabulary normalizer difference between two prompts can flip the apparent
direction of the effect. Every locus and architecture claim in this project is
therefore stated on the raw stop logit or the gauge-free margin, never on
`d log p` alone.

### What this rules out

- OLMo-specific token wiring as the source of the phenomenon.
- "The model just detects that text is ending" — the document-end token
  dissociates from the turn-end token, and in one case moves the wrong way.
- "Instruction tuning creates the goal-sensitivity" — it is present at base in
  all three lineages.

---

## 2026-09-18 — Sbody replicated; final Layer C table

Seed 1 of the strict state-only ladder reproduces seed 0, including the
budget-growing continuation suppression:

| | seed 0 | seed 1 |
|---|---|---|
| Sbody@250 `d_goal` / `dz_cont` | 11.54 / −1.11 | 11.12 / +0.04 |
| Sbody@750 | 12.10 / −1.84 | 12.73 / −2.31 |
| Sbody@2250 | 17.73 / −5.00 | 19.80 / −5.62 |

### Final Layer C result — paired vs Arm 0, both seeds, 50 items

| contrast | **`dz_stop`** (reading) | **`dz_cont`** (clearing) | `d_goal` (behaviour) |
|---|---|---|---|
| **R** — 4,097 readout params, state frozen | **+6.03** [5.00, 7.09] 49/1 | **0.00** [0.00, 0.00] **0/0** | +6.03 |
| **Sbody** — 6.9B body params, whole head frozen | +5.30 [4.13, 6.44] 46/4 | **−5.98** [−7.13, −4.84] 4/46 | **+11.27** |
| **F** — everything free | +5.16 [3.97, 6.33] 44/6 | −6.15 [−7.26, −5.06] 3/47 | **+11.31** |

`R − Arm0` on the continuation side is now *exactly* 0.00 with a 0/0 sign count.
That is not rounding: with Arm 0 measured through the arms' own evaluation path,
R's non-stop logits are bit-identical to the pretrained model's on all 50 items.
The freeze is confirmed end-to-end, by the measurement rather than by assertion.

`Sbody ≈ F` on every column while having the entire output head byte-frozen.

### Final statement of the acquisition law

> **Reading and clearing are different problems with different parameter loci.**
>
> - **Reading** — making goal completion visible to the stop action. Pretraining
>   already supplies most of it (`dz_stop` = +8.16 at Arm 0, 47/3, at
>   p(stop) ≈ 1e-4). Either locus sharpens it and they are close to
>   interchangeable: 4,097 readout parameters give +6.03, 6.9B internal
>   parameters give +5.30.
> - **Clearing** — suppressing the still-plausible continuation once the goal is
>   satisfied. A stop readout cannot do this *at all* (exactly 0.00, by
>   construction), at any capacity (Rmlp). Internal-state change gives −5.98,
>   matching full fine-tuning and the released checkpoint, and it is the half
>   that grows with training budget.
>
> Behavioural stopping is the sum. The reuse-vs-new-representation dichotomy
> fails not because the answer is "both", but because the two loci are not
> competing to do the same job.

Established across three lineages and two stopping architectures (Layer A
external check). **Stopping here per the pre-agreed scope: no layer probing, no
SAE, no circuit localisation, no model zoo.** Next step is paper structure.

---

## 2026-09-18 — Rmlp budget ladder: correcting the capacity claim (the 750-step trap, third occurrence)

The capacity control `Rmlp` (2,098,177-parameter nonlinear readout over the same
frozen state) existed only at 750 steps. By this project's own rule — a locus
comparison at one budget is not identified — that was a gap. Filled at 250 and
2250, both seeds.

Paired within item, both seeds, `Rmlp − R`:

| budget | `dz_stop` (reading) | sign | `dz_cont` (clearing) | sign |
|---|---|---|---|---|
| 250 | **+0.42** [0.29, 0.56] | 44/6, p=3.2e-08 | **0.00** [0.00, 0.00] | **0/0** |
| 750 | −0.14 [−0.43, 0.15] | 22/27, p=0.57 | **0.00** | **0/0** |
| 2250 | **+1.18** [0.75, 1.61] | 41/9, p=5.6e-06 | **0.00** | **0/0** |

### Correction

**"Readout capacity is not the limit" was a 750-step statement and is wrong as a
general claim.** A nonlinear readout does beat a linear one on the reading term,
reliably, at both 250 (+0.42) and 2250 (+1.18) steps. The 750-step rung — the
one the original four-arm experiment used — is the only budget where the
contrast is null.

That is now the **third** time the 750-step budget has produced a misleading
single-point reading:

1. `F − R` was null at 750 → "the parameter locus does not matter";
2. `F − R` at 750 was the ladder's minimum → "the state component only appears
   at large budget";
3. `Rmlp − R` is null at 750 → "readout capacity is not the limit".

All three were wrong in a different direction, and all three were corrected by
the same instrument run at more than one budget. This is worth a methods
paragraph in the paper, not just a footnote.

### What survives, and is strengthened

The load-bearing claim is untouched:

> **`dz_cont` for `Rmlp − R` is exactly 0.00, with a 0/0 sign count, at every
> budget.** A 2-million-parameter nonlinear readout over the frozen pretrained
> state cannot move the continuation logits *at all* — not weakly, exactly zero.
> This is structural, and it is the sharpest possible form of the claim that
> **clearing is impossible for any readout at any capacity and any budget.**

And the reading term's decomposition is only mildly revised: of the readout
route's total reading gain at 2250 (R: +6.03 over Arm 0), roughly +1.2 is
attributable to readout expressivity and the rest to what a single linear row
can already extract. Rmlp@2250 still reaches only `d_goal` 14.71, far short of
Sbody/F at 17.7–19.8, and the entire shortfall is the clearing term.

**Revised wording:** the readout route's ceiling is *partly* a capacity ceiling
on the reading term, and *absolutely* a structural ceiling on the clearing term.

---

## 2026-09-18 — Scaling the claim: 3-family causal replication started, and a cross-family finding about "base"

The parameter-locus conclusion rested on OLMo-3-7B alone, which is the claim's
weakest point given how wide the claim now is. Starting a full core causal
replication on two more lineages, chosen for the opposite stopping architecture.

**Step 0 first, as always.** All three are untied at the storage level
(`data_ptr` check, not the config string), so the readout/state factorization is
implementable. Gate C re-verified bit-exact on each new family, and critically
**on the token the arms actually train**:

| family | arms train on | Gate C |
|---|---|---|
| OLMo-3 7B | `<\|endoftext\|>` (shared) | PASS |
| Qwen2.5 7B | **`<\|im_end\|>`**, not its eos | PASS |
| Llama-3.1 8B | **`<\|eot_id\|>`**, not its eos | PASS |

Using `tok.eos_token_id` would have trained arm R's delta on a token the
assistant never emits in two of the three families. Two further implementation
facts found and fixed: Llama-3.1 base ships **no pad token** (now falls back,
with an assertion that pad can never collide with the stop token), and learning
rates do **not** transfer across families — OLMo's R selects 3e-3 while Qwen and
Llama both select 1e-3. Each family gets its own sweep on held-out CE.

### Finding: how much "clearing" a base model already has varies enormously

| base checkpoint | `dz_stop` (turn-end token) | **`dz_cont`** |
|---|---|---|
| OLMo-3 7B | +8.16 | **+0.67** |
| Qwen2.5 7B | +3.82 | **−12.45** |
| Llama-3.1 8B | +2.47 | **−7.34** |

Verified through two independent measurement paths for Qwen (−12.48 vs −12.45).

**Qwen2.5 and Llama-3.1 "base" checkpoints already do continuation clearing;
OLMo-3 base does essentially none.** The natural reading is that these bases are
not clean document continuers — Qwen2.5 base even ships a chat template — while
OLMo-3 base is. That is a corroboration rather than a problem: *the family whose
base is the purest pretrained document model is exactly the one with no
clearing*, which is what one predicts if clearing is an assistant-specific
adaptation.

### Two consequences for how the claims must be worded

1. **The locus claim is unaffected**, because it is stated as a *change from
   Arm 0*, not an absolute level. R's `dz_cont` is pinned at whatever its base
   is, so `R − Arm0` on the clearing term must be exactly 0 in every family;
   `Sbody − Arm0` must be negative. That is the replication target.
2. **The developmental claim must stay OLMo-only.** For Qwen and Llama the
   base→instruct contrast is *not* a clean pretraining→post-training contrast,
   since their bases already contain assistant-like adaptation. The earlier
   "pretraining already makes goal completion visible but not actionable" claim
   is licensed by OLMo-3's lineage, and the other two families corroborate the
   parameter-locus decomposition, not the developmental timeline. Do not blur
   these.

Also: "R's `dz_cont` is pinned at +0.67" was an OLMo-specific phrasing. The
general statement is **"R cannot change the clearing term at all, so
`R − Arm0` is identically zero."**

---

## 2026-09-19 — Qwen2.5-7B replication: the structural claim replicates exactly, the reading claim does NOT

Full core causal replication on Qwen2.5-7B (Arm0 / R / Sbody / F, 3 budgets,
3 seeds; arms train on `<|im_end|>`, Gate C verified bit-exact on that token).
Reported against Qwen's own Arm 0 (`dz_stop` 3.82, `dz_cont` −12.45), since the
locus claim is a *change from* Arm 0.

| | Δ`dz_stop` (reading) | Δ`dz_cont` (clearing) |
|---|---|---|
| R @250 / 750 / 2250 | +0.57 / **−1.35** / **−1.74** | **0.00 / 0.00 / 0.00** |
| Sbody @250 / 750 / 2250 | +3.15 / +2.99 / +3.99 | +1.96 / +2.56 / −4.75 |
| F @250 / 750 / 2250 | +8.02 / +8.18 / +8.95 | +1.40 / +3.40 / −1.79 |

### What replicated — the load-bearing structural claim

**R's clearing term is pinned at exactly −12.45, change 0.00, at every budget.**
Different family, different tokenizer, different turn-end token, different
stopping architecture: a stop readout still **cannot touch the clearing term at
all**. This is the claim the paper rests on and it is now exact in two families.

### What did NOT replicate — "reading is readout-attachable"

On OLMo, R alone gained `dz_stop` **+6.03**. On Qwen, R **loses** ground
(−1.74 at 2250). This is a real failure to replicate and must not be spun.

**It is not a failed arm.** R trains well: val_loss 1.022 → 0.822 and
`boundary_auc` **0.965 → 0.999**. It improves *generic* boundary stopping a lot
while *reducing* goal-relative stop promotion.

### Candidate explanation, and the trade-off it implies

| Arm 0 | generic `boundary_auc` | R's contribution to reading |
|---|---|---|
| OLMo-3 7B | **0.99543** (near ceiling) | **+6.03** |
| Qwen2.5 7B | **0.96463** (clearly short) | **−1.74** |

With only one row of freedom, generic boundary calibration and goal-relative
modulation **compete for the same degree of freedom**. Where the base already
handles generic stopping (OLMo), the readout can spend itself on goal-relativity;
where it does not (Qwen), the readout spends itself on base-rate calibration
first, and goal-relativity degrades.

This is a post-hoc explanation from two families. It is recorded as a
**pre-registered prediction** before the deciding data exists:

> **Prediction (made before any Llama R arm has run).** Llama-3.1-8B's Arm 0
> `boundary_auc` determines the sign of R's reading contribution. High
> (≳0.99, OLMo-like) → R gains on `dz_stop`. Low (≲0.97, Qwen-like) → R is flat
> or negative.

Llama is a genuine adjudicator: its base `dz_cont` is −7.34, between OLMo's
+0.67 and Qwen's −12.45. Llama's Arm 0 was launched *before* its R arms, so the
predictor is fixed in advance.

### Consequence for the paper's claims

- **Narrow**: "post-training can acquire the reading term through readout
  adaptation alone" must become conditional on the base's generic stopping
  competence. It is not a general law.
- **Keep**: reading and clearing are different problems in different loci, and
  **clearing is structurally unreachable by any readout** — exact 0.00 in both
  families, at every budget, at any capacity (Rmlp).

Status: 3 Qwen R@seed1 runs backfilling (they were interrupted when the old
scheduler was replaced); Llama at 10/28. Numbers above use the seeds available.

---

## 2026-09-19 — THREE-FAMILY RESULT: prediction confirmed; one law is universal, one is not

Both replications complete: Qwen2.5-7B 28/28 and Llama-3.1-8B 28/28
(Arm0 / R / Sbody / F × 250/750/2250 × 3 seeds each).

### The pre-registered prediction was confirmed

Recorded before any Llama R arm existed: *Llama's Arm 0 `boundary_auc` decides
the sign of R's reading contribution; low (≲0.97) → R flat or negative.*

| Arm 0 | generic `boundary_auc` | R's Δ`dz_stop` @2250 |
|---|---|---|
| OLMo-3 7B | 0.99543 | **+6.03** |
| Qwen2.5 7B | 0.96463 | **−1.84** |
| Llama-3.1 8B | **0.90473** (lowest) | **−1.31** |

Llama came in lowest and its R arm is negative at every budget, as predicted.
With n=3 families only the *sign* prediction is claimed; no monotone
quantitative relationship is asserted (Qwen and Llama invert in magnitude).

### The universal law — exact in 3 families and 2 architectures

Paired against each family's **own** Arm 0, @2250:

| family | arm | Δ`dz_stop` (reading) | sign | Δ`dz_cont` (clearing) | sign |
|---|---|---|---|---|---|
| OLMo-3 | R | +6.03 [+5.00,+7.09] | 49/1 | **+0.00 [0.00,0.00]** | **0/0** |
| | Sbody | +5.30 [+4.13,+6.44] | 46/4 | −5.98 [−7.13,−4.84] | 4/46 |
| | F | +5.16 [+3.97,+6.33] | 44/6 | −6.15 [−7.26,−5.06] | 3/47 |
| Qwen2.5 | R | −1.84 [−2.57,−1.14] | 13/37 | **+0.00 [0.00,0.00]** | **0/0** |
| | Sbody | +3.99 [+3.02,+4.94] | 42/8 | −4.75 [−5.67,−3.77] | 5/45 |
| | F | +8.95 [+7.42,+10.40] | 45/5 | −1.79 [−2.65,−0.87] | 11/39 |
| Llama-3.1 | R | −1.31 [−1.86,−0.75] | 11/39 | **+0.00 [0.00,0.00]** | **0/0** |
| | Sbody | +0.29 [−0.32,+0.89] | 29/21 | −2.66 [−3.72,−1.64] | 13/37 |
| | F | +0.43 [−0.23,+1.11] | 29/21 | −1.99 [−2.91,−1.08] | 16/34 |

> **In every family, at every budget, at every seed, and at any readout
> capacity, a stop readout changes the clearing term by *exactly zero*, while
> internal-state adaptation always changes it.**

This holds across a shared-EOS architecture (OLMo reuses `<|endoftext|>`) and
two distinct-EOT architectures (`<|im_end|>`, `<|eot_id|>`). The same statement
is true at 250 steps, where the state arms' clearing change even flips sign in
Qwen (+1.96) — the direction is family- and budget-dependent, but the
*reachability* is absolute: |Δclearing| = 0 for R and > 0 for the state arms,
without exception.

### The law that is NOT universal

"Post-training acquires the reading term through readout adaptation alone" is
**OLMo-specific**. R gains +6.03 there and *loses* ground in both other
families. Worse for generality, on Llama even the state arms barely move reading
at 2250 (Sbody +0.29, F +0.43, both null by sign test) while still moving
clearing. So the reading term is not a stable cross-family phenomenon at all.

This must be reported as a negative result, not buried.

### Revised headline

The paper's central claim narrows to something cleaner and better supported:

> **Goal-relative stopping requires two changes, and only one of them is
> reachable from the stop readout.** Suppressing the still-plausible
> continuation once the goal is satisfied — the *clearing* term — is
> structurally unreachable by any stop readout, at any capacity, at any budget,
> in every model family tested; it requires internal-state change. How much the
> stop readout can additionally sharpen the *reading* of goal completion is
> family-dependent and trades off against the generic boundary calibration the
> readout must also perform.

The OLMo-only developmental result (pretraining already makes goal completion
visible at an inactive operating point) stays labelled as OLMo-only, since the
Qwen and Llama bases are not clean document continuers.

---

## 2026-09-19 — RETRACTIONS, and the reframing they force

Two statements written earlier in this log are **withdrawn**. Both are left in
place above with this entry as their correction, rather than silently edited.

### Retraction 1 — "goal-relative stopping requires two changes"

Not true. Llama-3.1 acquires goal-relative stopping mostly through the
continuation side: at 2250 steps `Sbody` moves `dz_stop` by only +0.29
(null by sign test, 29/21) while moving `dz_cont` by −2.66 and `d_goal` by
+2.95. There is no law that both components must change.

Correct statement: *goal-relative stopping can be acquired by changing either
side of the stop-versus-continue competition; which routes are accessible
depends on the parameter locus and the pretrained state.*

### Retraction 2 — "Qwen and Llama bases are not clean document continuers"

This was excuse-making for inconvenient data. Both are official pretrained base
checkpoints: Qwen2.5-7B's card lists `Training Stage: Pretraining` and states
that SFT/RLHF is still required for conversation; Llama-3.1-8B is likewise the
pretrained base with a separately instruction-tuned sibling. Nothing licenses
calling them contaminated.

The honest — and more interesting — statement is:

> **Different pretrained families already expose radically different termination
> geometries under the same assistant serialization.** Base `dz_cont` is +0.67
> (OLMo-3), −7.34 (Llama-3.1) and −12.45 (Qwen2.5); base generic `boundary_auc`
> is 0.995, 0.905 and 0.965. This is a finding about pretraining, not a defect
> in the checkpoints.

### Two candidate explanations tested and BOTH FALSIFIED

I tried to explain why readout adaptation helps OLMo and hurts the others.

**(a) Initial-gradient alignment.** Arm R's gradient has a closed form,
`dL/dd = mean_t (p_stop(t) − 1[tgt=stop]) h_t`, so `(−dL/dd)·v` should predict
the sign of R's reading change. It does not: `−g·v` is **positive** in Qwen
(+97.5) and Llama (+8.7), which predicts improvement, yet both degrade. The raw
gradient direction is not the Adam update direction, and the interior term only
pushes back once training has raised stop probability. **Rejected.**

**(b) Boundary-direction geometry.** With
`b = mean(h at true boundaries) − mean(h at interior)`, the hypothesis was that
`sign(cos(b, v))` separates the families. It does not: `cos(b,v)` = **0.597**
(OLMo), **0.601** (Qwen), 0.358 (Llama). Qwen is indistinguishable from OLMo on
the proposed predictor and behaves oppositely. **Rejected.**

The learned deltas do confirm R is doing generic boundary work everywhere —
`cos(d,b)` = +0.067 / +0.055 / +0.162, all positive — but `cos(d,b)` is small,
so `d` is mostly *not* along `b`, and a two-direction picture is insufficient.

**No mechanism for the family dependence is currently supported.** The
`boundary_auc` correlate stays a descriptive observation with one confirmed
held-out sign prediction, and must be written as such — not as a law, and not in
the abstract.

### What this leaves, and it is stronger than what it replaces

The result that survives everything is not about two components. It is:

> **Assistant stopping is not an EOS-calibration problem. It is a goal-conditioned
> competition between terminating the turn and continuing task-relevant content.**
> Measured as `d_goal = Δz_stop − Δz_cont`, internal-state adaptation improves
> this competition in **all three families even with the entire output head
> byte-frozen** (+11.27 / +8.73 / +2.95; sign 49/1, 47/3, 37/13), while
> stop-readout adaptation ranges from strongly beneficial to actively harmful
> (+6.03 / −1.84 / −1.31) *despite improving generic boundary detection in every
> family*.

The Qwen result is the sharpest single fact in the project: `boundary_auc`
0.965 → 0.999 while goal-relative reading goes **down**. That separates
**learning where responses end** from **learning when the user's task is done**,
and it is exactly the distinction the mother question was about.

### Next: the within-family causal test

The cheap explanations failed, so the account needs a causal handle rather than
another family. Running now: inside OLMo-3, remove a controlled fraction λ of
the stop row's projection onto `b`, which degrades **generic** boundary
competence while leaving hidden states, data, and every other parameter
untouched.

| λ | Arm 0 `boundary_auc` |
|---|---|
| 0 | 0.99543 (original) |
| 0.5 | **0.92451** (≈ Llama's 0.90473) |
| 1.0 | 0.38373 |
| 1.5 | 0.19358 |

If R's `Δd_goal` flips from +6.03 to ≈0 or negative at λ=0.5 — same model, same
state, same data, one manipulated quantity — the boundary-competence account
becomes causal rather than correlational.

---

## 2026-09-19 — Causal test: the boundary-competence account is FALSIFIED, and its premise is false

Within OLMo-3, removed a fraction λ of the stop row's projection onto the
generic boundary direction b, leaving hidden states, data, optimiser and every
other parameter untouched. Arm R then trained identically (lr 3e-3, 2250 steps,
2 seeds).

### First reading — and why it is WRONG

The paired Δ against each λ's own Arm 0 looked like a strong monotone effect:

| λ | Arm 0 auc | Δ`d_goal` (R − Arm 0) |
|---|---|---|
| 0 | 0.99543 | +6.03 |
| 0.5 | 0.92451 | +10.51 |
| 1.0 | 0.38373 | +14.90 |

**This is a baseline artefact and must not be read as "degradation helps R".**
Checking the absolute levels:

| λ | Arm 0 `d_goal` | **R `d_goal`** | R `dz_stop` |
|---|---|---|---|
| 0 | 7.49 | **13.53** | 14.19 |
| 0.5 | 3.17 | **13.68** | 14.35 |
| 1.0 | −1.14 | **13.77** | 14.43 |

**Arm R converges to the same endpoint regardless of how badly the stop row was
degraded** (13.53 / 13.68 / 13.77), from starting points of `dz_stop`
8.16 / 3.84 / −0.47. The growing Δ is entirely the lowered baseline. R also
restores generic `boundary_auc` to ~0.9998 in every condition.

### What the experiment actually showed

The intervention manipulated the **initialization**, not the **demand on
capacity**. A 4,097-parameter linear readout with 2250 steps is not scarce in
the relevant sense: it simply re-learns the removed boundary component and
converges to the same optimum.

That incidentally **falsifies the premise of the trade-off account**. If a
single degree of freedom were genuinely being consumed by generic boundary
calibration, the endpoint would depend on how much generic work remained. It
does not.

### Score so far on explaining the cross-family difference

| attempt | verdict |
|---|---|
| initial-gradient alignment `(−g)·v` | positive in Qwen/Llama yet both degrade — **rejected** |
| boundary-direction geometry `cos(b,v)` | OLMo 0.597 vs Qwen 0.601, indistinguishable — **rejected** |
| boundary-competence trade-off | R's endpoint is initialization-invariant; capacity scarcity is false — **rejected** |

Worse for the original story: the **cross-family correlation and the
within-family causal manipulation of the same variable point in opposite
directions**. Cross-family, lower Arm 0 `boundary_auc` went with a worse R;
within-family, degrading `boundary_auc` leaves R's endpoint unchanged. The
Llama held-out sign hit is therefore downgraded from "confirmed prediction" to
**an unexplained correlation that its own causal test does not support**, and it
must not appear in the paper as a mechanism or as a validated prediction.

**The cross-family difference in whether readout adaptation helps is currently
unexplained.** The most likely remaining source is that what is linearly
available in the frozen state h differs by family — a property of pretraining,
not of the readout's budget — but that is a hypothesis, not a result.

### Unaffected

Everything load-bearing survives, because none of it depended on the
explanation:

> On `d_goal`, internal-state adaptation improves the stop-versus-continue
> competition in **all three families with the entire output head byte-frozen**
> (+11.27 / +8.73 / +2.95; sign 49/1, 47/3, 37/13), while stop-readout
> adaptation ranges from +6.03 to −1.84 despite improving generic boundary
> detection everywhere.

A useful new fact also falls out: **arm R's learned readout is
initialization-invariant** — same endpoint from a healthy, a Llama-like, and a
destroyed stop row. Whatever limits the readout route, it is not where it
starts.

---

## 2026-09-19 — Phase 0: repo sanitation, and the two measurement defects that force Phase 1

No new model runs. This entry re-bases the repo on what the evidence currently
supports and records two defects that invalidate how the project has been
talking about *acquisition*.

### Defect 1 — the "natural trajectory" was not measured on one action

`Layer B` in `docs/RESULTS.md` compared Base / Instruct-SFT / DPO / Instruct on
each checkpoint's **own** generation-config stop set. The logs are unambiguous:

```
base:     stop_ids=[100257]           (['<|endoftext|>'])
sft:      stop_ids=[100257, 100265]   (['<|endoftext|>', '<|im_end|>'])
dpo:      stop_ids=[100257, 100265]
instruct: stop_ids=[100257, 100265]
```

Base is scored on one token; every post-trained stage on a two-token logsumexp.
The measured **action changes along the curve**, so the rise in `d_goal` is not
a longitudinal measurement of one stop decision. The table is now titled
CONFOUNDED in `docs/RESULTS.md` and the raw files are untouched. Replacement
rule, binding on all future trajectory work: *score the same exact termination
token at every checkpoint, and report any other stop token separately.*

### Defect 2 — the chain that was measured is not OLMo-3's real chain

The repo wrote `Base → SFT → DPO → Instruct`. The real chain is

```
Base → Think-SFT → Instruct-SFT → DPO → RLVR (= Instruct)
```

with Instruct-SFT warm-started from Think-SFT, not trained from Base.
**Verified locally rather than taken from the model card** — parameter distance
between released checkpoints on three probed tensors:

| tensor | `|InstSFT−Base|` | `|InstSFT−ThinkSFT|` | `|ThinkSFT−Base|` |
|---|---|---|---|
| `layers.10.self_attn.q_proj` | 23.15 | **9.56** | 21.51 |
| `layers.20.mlp.down_proj` | 39.71 | **17.41** | 36.77 |
| `lm_head` | 178.95 | **55.09** | 169.40 |

Instruct-SFT is ~2.3× closer to Think-SFT than to Base on every probe. So the
old first arrow (`Base → SFT`) spans **two** training stages, and any
"post-training does X at SFT" reading of that curve is unidentified.

### What Phase 1 can actually use

The released intermediate checkpoints, checked against the HF refs API today:

| stage | repo | intermediates |
|---|---|---|
| pretraining | `allenai/Olmo-3-1025-7B` | 1487 branches (`stage1-step*`, `stage2-*`, `stage3-step*`) |
| Think-SFT | `allenai/Olmo-3-7B-Think-SFT` | 43 (`step1000` … `step43000`) + `main` |
| Instruct-SFT | `allenai/Olmo-3-7B-Instruct-SFT` | **none** — `main` only |
| DPO | `allenai/Olmo-3-7B-Instruct-DPO` | **none** — `main` only |
| RLVR | `allenai/Olmo-3-7B-Instruct` | 8 (`step_050` … `step_400`) + `main` |

So the trajectory is dense inside Think-SFT and inside RLVR, and single-point at
Instruct-SFT and DPO. That is enough to localise *which stage* carries the
transition, which is all Phase 1 has to decide. Dense pretraining coverage is
available if the base-side question becomes load-bearing.

### Code defects fixed

* `src/e01_run.py` — `STAGE_REPOS` defined `"qwen2.5-7b"` **twice**; the second
  literal silently discarded the first (including its `sft` key). Merged. No
  result changes: the discarded `sft` entry pointed at the same Instruct repo
  the surviving `graft-template` donor logic already selected.
* `src/e02_threefamily.py` — OLMo's 750-step runs live in `results/e02/final/`
  (`config.json` confirms `steps: 750`), not in `results/e02/budget/`, so the
  750-step table silently dropped OLMo's `R` and `F` rows, and the family label
  printed only on the `R` row and so disappeared with it. Arms now resolve over
  a list of path templates and the label prints on the first surviving row.
  Recovered rows (paired vs OLMo Arm 0): `R@750` Δ`d_goal` **+4.72**
  [+3.98,+5.48] 48/2, Δ`dz_stop` +4.72, Δ`dz_cont` +0.00; `F@750` **+4.79**
  [+4.06,+5.46] 47/3, +3.09, −1.70.
* Confirmed **not** a defect: `repl/{qwen,llama}_R_st1_s0` is a same-path
  zero-update Arm 0 (`"lr": 0.0`), not a contaminated 1-step run. Noted in the
  source so it is not re-litigated.

### README re-based

The README led with *"Reading and clearing are different problems with
different parameter loci"*, which the 2026-09-19 retractions had already
withdrawn, and presented `Δdz_cont^R = 0` as a finding when arm R holds every
non-stop logit fixed by construction. Rewritten around what survives
(phenomenon, turn-end-token dissociation, base sensitivity, head-frozen causal
result, boundary≠goal distinction) with an explicit do-not-revive list carrying
all three rejected mechanisms and both trajectory defects above.

### Next

Phase 1, as specified: the real fixed-token trajectory over
Base → Think-SFT(dense) → Instruct-SFT → DPO → RLVR(dense), one frozen E01
instrument, `<|endoftext|>` as the scored stop action at every checkpoint,
reporting `d_goal`, `dz_stop`, `dz_cont` and continuation awareness. Its only
job is to say **where** the transition is, so Phase 2's supervision-source
decomposition starts from the true incoming checkpoint.
