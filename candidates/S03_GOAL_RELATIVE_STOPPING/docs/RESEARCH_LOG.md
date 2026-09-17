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
