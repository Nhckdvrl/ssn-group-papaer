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
