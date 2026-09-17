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
