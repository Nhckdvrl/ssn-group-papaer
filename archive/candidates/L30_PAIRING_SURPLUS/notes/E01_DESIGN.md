# L30 E01 — Pre-registration

**Frozen:** 2026-09-13, before any IFEval outcome for any trained arm was computed.
**Authorization:** `PILOT-AUTHORIZED — E01 ONLY`.

Training for the 12 runs was launched immediately before this file was written;
the full configuration was already fixed in `src/` and is reproduced below. No
adapter had been evaluated, and no arm-wise IFEval number existed, when this
document was frozen. The only model measurements taken before freezing were the
instrument checks in §5, which are properties of the untuned base model and
carry no information about any contrast.

---

## 1. Estimand

The scientific object is the marginal causal value of the joint `X<->Y`
correspondence at fixed prompt marginal `P_X` and response marginal `P_Y`:

```
Pairing Surplus = Performance(P_XY) - Performance(P_X (x) P_Y)
```

This is an interventional training quantity, not a data-quality score and not a
mutual-information estimator. The manipulation is applied to the supervision
distribution only; the pretraining initialisation, the prompt pool, the response
pool and the optimisation budget are all held fixed.

## 2. Arms

One shared pool of 51,758 Alpaca-Cleaned pairs (`results/pool/`). Every arm
draws from this same pool, so the prompt marginal and the response marginal are
identical across arms by construction.

| Arm | Training sequence | Correspondence |
|---|---|---|
| **P** | `<bos><\|user\|>\n x_i \n<\|assistant\|>\n y_i <eos>` | correct |
| **S** | `<bos><\|user\|>\n x_{pi(i)} \n<\|assistant\|>\n y_i <eos>` | **wrong** |
| **D_mask** | same tokens/positions as P; response cannot attend to the instruction | **none** |
| **D_rt** | `<bos><\|assistant\|>\n y_i <eos>` (An et al. Response Tuning) | **none** |

`pi` is a fixed derangement (Sattolo's algorithm, seed 1730) — no example keeps
its own instruction. It is fixed across epochs, so S is a well-defined joint
distribution with the correct marginals, not resampled noise.

Loss is computed on response tokens only in **every** arm, matching An et al.:
their IT baseline also masks the prompt, so the IT–RT difference is pairing, not
prompt-token loss. This project therefore does not vary the loss mask at all;
WIT-style prompt-token weighting is a separate literature and is deliberately
absent from E01.

### What is matched between P and S

| Quantity | P vs S |
|---|---|
| prompt multiset | identical |
| response multiset | identical |
| loss-token count, **per example** | identical |
| example order / step assignment | identical (same seed) |
| optimiser, LR, schedule, clipping | identical |
| truncation | none in either arm (see §4) |

The only difference is which instruction each response is paired with.
**`Delta_corr = P - S` is therefore the artifact-free primary contrast.**

`D_mask` adds budget-and-position matching to a correspondence-free condition;
`D_rt` is the literature's own control and acts as the construct anchor. If
`D_mask` and `D_rt` disagree substantially, the difference is attributable to
serialisation/position rather than correspondence, and only `Delta_corr` remains
load-bearing. That contingency is recorded here, before the fact.

## 3. Quantities

```
Delta_pair  = P - D        what correct correspondence buys over no correspondence
Delta_wrong = D - S        whether wrong correspondence is worse than none
Delta_corr  = P - S        same-marginal causal value of correct correspondence
```

`D` denotes `D_mask` for the primary reading (budget-matched) with `D_rt`
reported alongside. The relative pattern, not the ranking alone, selects the
scientific account.

## 4. Configuration

Following An et al.'s Response Tuning repository:

- base model `google/gemma-2-2b` (**base**, not `-it`), bf16, eager attention
- data `yahma/alpaca-cleaned`; prompt = `instruction`, or `instruction\n\ninput`
- Tulu-style `<|user|>` / `<|assistant|>` delimiters
- LoRA r=64, alpha=16, dropout=0.1, all linear projections (83,066,880 params)
- AdamW, constant LR 1e-4, effective batch 64 (micro-batch 8 x accum 8)
- max_grad_norm 0.3, loss on response tokens only
- greedy decoding at evaluation

Deviations from the source, all fixed before any outcome was inspected and all
applied identically to every arm (so none can bias a contrast):

1. **bf16 backbone instead of 4-bit NF4.** The 96GB cards make quantisation
   unnecessary; removing it removes a noise source irrelevant to the estimand.
2. **3 epochs instead of 10.** 12 runs x 10 epochs is outside the pilot budget.
   This is the conservative direction for `Delta_wrong`: less exposure to the
   wrong mapping should, if anything, shrink the damage from S. Per-epoch
   adapters are saved so the training-length trajectory costs evaluation only.
3. **Segment-wise tokenisation** rather than string-matching a response
   template, making the loss mask and the D_mask boundary exact.
4. **Pool filter** `len(x) <= 768` and `len(y) <= 1024` tokens. This drops 2 of
   51,760 examples and caps the worst-case sequence at 1,417 tokens, so **no
   example is truncated under any pairing** — truncation cannot differ between
   P and S.

## 5. Instrument checks already passed (`src/test_masks.py`)

These concern the untuned base model only.

- **D_mask leaks nothing.** Swapping in a different instruction *of the same
  token length* — holding `block_from`, sequence length and every response
  position fixed — moves the D_mask response logits by exactly `0.0`, and by
  `0.0` again when the masked span is replaced with random token ids. The same
  swap under P moves them by 26.6.
- **The mask is really applied.** Masked vs unmasked on the same sequence
  differs by 26.0, so the bias is not being silently discarded.
- **Sliding-window guard.** Gemma-2 alternates full and sliding-window layers;
  the shared bias is valid only below the 4096-token window, and an assert
  fails if that is ever violated. The pool's worst case is 1,417.

Two earlier versions of this test failed for reasons that were *not* leakage —
a position-mismatched reference run, and comparing instructions of different
token length (which moves the response under RoPE). Both are documented in the
test file so the distinction is not lost.

A separate bug found during the throughput benchmark: wrapping only the target
Linears left `embed_tokens` (590M params, tied to `lm_head`) trainable. The
backbone is now frozen explicitly and the trainable count is 83,066,880, which
matches the hand-computed LoRA size.

## 6. Evaluation

**Primary:** IFEval (`google/IFEval`, 541 prompts), scored with the unmodified
Google Research verifier vendored at `src/instruction_following_eval/`. Greedy
decoding, `max_new_tokens=1024`, identical inference context for every arm.

**Primary metric:** strict prompt-level accuracy at **epoch 3**. Strict
instruction-level, and both loose variants, are reported as secondary; epochs 1
and 2 are reported as a trajectory. The untuned base model is evaluated as a
reference point.

**Unit of analysis: the prompt.** A prompt carries 1–3 constraints; these are
never treated as independent samples. Confidence intervals come from a bootstrap
that resamples **prompts** (clusters), with training seed treated as a second
variance component: seeds are resampled with the prompts so the interval covers
both evaluation and training variability. Seed-wise numbers are reported
individually, never only the mean.

**InFoBench is not run.** It needs an LLM judge, and adding a second benchmark
to look for a friendlier sign is precisely what this pilot is forbidden to do.

## 7. Outcome map — frozen

Taken from the candidate README, committed before results:

- **`P > D ~ S`** — correct correspondence teaches conditional control beyond the
  marginals. Establishes a pairing surplus; still not a Main paper by itself.
- **`P ~ D > S`** — the pretrained map plus marginal adaptation largely suffices,
  and wrong pairing damages it. The role of correct pairs is preservation, not
  teaching from scratch.
- **`P ~ S > D`** — semantic correctness is not load-bearing; prompt-conditioned
  training is doing the work. This **weakens the pairing story** and forces
  re-selection rather than a rescue.
- **`P ~ D ~ S`** — correspondence is not load-bearing at resolvable scale here.
  Only claimable if intervals are tight.

Heterogeneity across IFEval constraint families will **not** be promoted to a
finding. It is not a pre-motivated condition, and scanning categories after the
fact is explicitly out of scope.

## 8. Resolution rule — frozen

- stable `>= 3-4 pp` across seeds: potentially meaningful, carry to re-selection;
- `<= 2 pp` with intervals that still admit a real ~3–4 pp effect:
  **`HOLD — PILOT UNDER-RESOLVED`**, *not* "pairing does not matter";
- a substantive null requires intervals tight enough to exclude ~2–3 pp.

The IT–RT gaps in An et al. (InFoBench DRFR 0.77 -> 0.69 at Llama-3.1-8B,
0.79 -> 0.74 at Gemma-2-9B) are a **rough upper bound only**. Our controls are
stricter and our model is smaller, so the same-marginal effect may be much
smaller. Prior effect sizes are not an expectation.

## 9. Stop condition

E01 stops when the 12 runs are evaluated and the contrasts are reported with
prompt-clustered uncertainty. A positive result does **not** authorise C2:
the project returns to selection first. The pilot's deliverable is a trustworthy
answer, not a positive one.
