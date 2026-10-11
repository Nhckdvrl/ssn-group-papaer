# L19 experiment ledger

| id | run | claim served | status |
|---|---|---|---|
| E01-a | `SHORT-SUPPORT` seed 1 | matched-supervision baseline | not started |
| E01-b | `LONG-FULL` seed 1 | treatment | not started |
| E01-c | `SHORT-SUPPORT` seed 2 | seed stability / kill condition 1 | not started |
| E01-d | `LONG-FULL` seed 2 | seed stability / kill condition 1 | not started |
| E01-base | untrained ProLong-512k-Base, evaluation only | anchor for outcome D | not started |
| E01-pc1 | `UC-UC`: UltraChat block A + UltraChat block B | mother positive control, short arm | not started |
| E01-e | NQ-only `SHORT-SUPPORT` seed 1 | dilution diagnostic, conditional on outcome B | not authorized |
| E01-f | NQ-only `LONG-FULL` seed 1 | dilution diagnostic, conditional on outcome B | not authorized |
| E01-pc2 | `UC-CHATQA2`: UltraChat block A + ChatQA2 | mother positive control, long arm | not started |

The positive control is structurally identical to the main contrast: the same 10k
UltraChat block A is held fixed and the *second* 10k block is swapped between a short
dataset (more UltraChat) and a long dataset (ChatQA2). Same example count, same
optimizer steps. It is the parent's dataset swap embedded in our pilot regime, so its
gap and the matched-supervision gap are measured with the same noise.

Common to E01-a..d: `Llama-3-8B-ProLong-512k-Base`, 20,000 examples (10k NQ + the same
10k UltraChat), 1 epoch, 32 examples/optimizer step, lr 2e-5 cosine→2e-6, warmup 3%,
AdamW(0.9, 0.95), bf16, DeepSpeed ZeRO-2, completion-only loss.

Evaluation for every run: MMLU 0-shot / BBH 3-shot CoT / LAMBADA 0-shot / GSM8K 4-shot
CoT, per the parent's Appendix B. Primary statistic is the macro over the four.

## Measured throughput (smoke, 2026-09-12)

`LONG-FULL` smoke, 128 NQ + 128 UltraChat examples, 4x RTX PRO 6000 Blackwell Max-Q,
DeepSpeed ZeRO-2, bf16, gradient checkpointing, completion-only sparse loss, 24k cap:
**10.42 min of training for ~1.85M context tokens = 2,962 tok/s aggregate**, 69/96 GB
per GPU. Model staged in bf16 on local NVMe (loading from the NFS cache cost ~40 min
per run before this).

Projected training cost, from that number:

| N | stage 1 (PC) | stage 2 (main, 2 seeds) | total |
|---|---|---|---|
| 2,000 | 2.1 h | 5.7 h | **7.8 h** |
| 5,000 | 5.2 h | 14.3 h | 19.5 h |
| 10,000 | 10.5 h | 28.5 h | 39.0 h |

**N=2,000 is the first rung**, per the ladder in the pilot card. Worst case — the
positive control fails at both rungs — the route stops having spent ~7 h.

Also added, free: the untrained `Llama-3-8B-ProLong-512k-Base` is evaluated on the same
four benchmarks. Without it, outcome D cannot be distinguished from "SFT at this budget
moves nothing at all".

## Stage 1 as actually run (N=2,000)

| run | items | context tokens | loss tokens | wall |
|---|---|---|---|---|
| `PC-UC-UC` seed 1 | 4,000 | 4.7M | 3.609M | 30 min |
| `PC-UC-CHATQA2` seed 1 | 3,954 | 20.6M | 1.991M | ~1.9 h |

Two asymmetries, both inherited from the parent's design rather than introduced by us,
and recorded so they are not mistaken for our main contrast:

- 46 ChatQA2 records exceed the 32k cap and are dropped (3,954 vs 4,000 items);
- the ChatQA2 arm's gradient norm runs ~26 against the UltraChat arm's ~2.4 at the same
  learning rate, because its targets are long summary-style answers. With clipping at 1.0
  the ChatQA2 arm is clipped on essentially every step and the UltraChat arm is not, so
  part of any gap between them is a clipping asymmetry rather than data quality. **The
  main contrast is immune to this**: `SHORT-SUPPORT` and `LONG-FULL` share their targets
  token for token, so their gradient scales are comparable by construction. This is a
  concrete instance of the matched design being cleaner than the dataset swap it replaces,
  and it bounds how much the positive control can be asked to certify;
- the positive-control arms are **not** loss-token matched (3.609M vs 1.991M), because
  swapping UltraChat for ChatQA2 swaps the targets too. That is exactly what the parent
  compares, and exactly the confound E01's main contrast removes — where the two arms
  are matched to the token.

## Stage 1, first attempt — instrument failure, not a result (2026-09-12)

| run | MMLU | BBH | LAMBADA | GSM8K | macro |
|---|---|---|---|---|---|
| untrained base | 62.90 | 56.11 | 76.69 | 62.09 | **64.45** |
| `PC-UC-UC` | 60.02 | 58.41 | 73.39 | 38.82 | 57.66 |
| `PC-UC-CHATQA2` | 48.92 | 45.44 | 73.86 | 23.12 | 47.84 |

Positive-control gap **-9.82** against the parent's +5.96, and **both arms below the
untrained base** — kill condition 3. Artifacts kept under `results/broken_v1/`.

**Root cause, diagnosed rather than assumed.** Training loss started at 7.9 and stayed
flat, where the same data and model give 0.95. Direct comparison showed our sparse
completion-only loss is exact (1.2201 vs the model's built-in 1.2201) and gradient
checkpointing innocent. The fault is in `transformers/trainer.py`:

```python
if (not self.model_accepts_loss_kwargs or num_items_in_batch is None) and ...:
    loss = loss / self.current_gradient_accumulation_steps
```

`LlamaForCausalLM.accepts_loss_kwargs` is True, so transformers >=5 **skips** that
division, assuming `compute_loss` normalised by `num_items_in_batch`. Ours normalises per
example. Every accumulated step was therefore 8x too large (7.9/8 = 0.99, matching the
true loss; reported grad_norm 20-43). Gradient clipping at 1.0 absorbed the magnitude but
turned all 125 steps into clipped unit-norm updates, which is what damaged the model.

Fixed by forcing `model_accepts_loss_kwargs = False`. Deliberately **not** fixed by
switching to token-level normalisation: NQ answers are ~3 tokens against UltraChat's
~400, so token normalisation would shrink the NQ block to under 1% of the gradient —
and that block is the one the experiment manipulates. Verified after the fix: loss 1.036,
grad_norm 5.68.

**What the base anchor bought.** Without it the only visible symptom would have been
"positive control has the wrong sign", and the preregistered ladder would have escalated
to N=5,000 and spent another 5 GPU-hours confirming a bug. With it, "SFT damaged the
model" was immediate and the response was repair, not escalation.

**Workflow lesson recorded:** check the *absolute* value of training loss at step 1
against a known reference, not just that the job runs. 7.9 on UltraChat for an 8B model
was impossible on its face.

## The real cause was learning rate, not budget (2026-09-12)

After fixing the 8x gradient bug the damage barely moved: `PC-UC-UC` macro 57.66 -> 58.10,
GSM8K 38.82 -> 38.74. Two further hypotheses were tested rather than assumed.

**Evaluation format mismatch — ruled out.** GSM8K, 4-shot CoT, limit 200:

| | raw few-shot | chat template |
|---|---|---|
| untrained base | 64.5 | **70.0** |
| `PC-UC-UC` lr 2e-5 | 40.0 | 38.5 |

The base model *gains* from the chat template (it retains Llama-3-Instruct chat ability),
while the SFT'd model is flat. Format is not the cause; under the SFT-favouring protocol
the gap widens.

**Learning rate scaled to batch size — confirmed.**

| GSM8K (limit 200, raw 4-shot) | |
|---|---|
| untrained base | 64.5 |
| lr 2e-5 | 40.0 |
| **lr 5e-6** | **52.0** |
| parent's UltraChat-SFT (published) | 54.69 |

The parent uses lr 2e-5 with a **4M-token batch**; ours is ~37k tokens per optimizer
step, roughly two orders of magnitude smaller, so the same nominal lr is a vastly larger
relative step. At 5e-6 our UltraChat arm lands at 52.0 against their published 54.69 —
the regime is commensurable after all. Default lr changed to 5e-6 for every run.

**Two earlier diagnoses of ours were wrong and are corrected here, not quietly dropped:**

- "both arms below base = instrument failure" (kill condition 3) would have flagged the
  parent's own published UltraChat run: their 4-benchmark macro is 60.41 against our
  untrained base's 64.45. SFT from an instruct-derived base is *expected* to cost a few
  points. The discriminating criterion is whether the dataset swap reproduces the
  parent's direction, not whether an arm sits above base.
- "we are in a damage valley that needs 1B tokens to escape" was wrong. It was an
  lr/batch-size mismatch. The estimate it produced (94 GPU-h per run for parent
  commensurability, 400+ h for the programme) is therefore void.

A Qwen3-1.7B-Base route was prepared as a cheap fallback (~2.5 h for the whole
programme) and is **not** needed; `src/sft_data.py` now carries both Llama-3 and Qwen
chat formats, verified to keep the arms' loss tokens byte-identical under either. Held in
reserve, since Qwen3-8B-Base is also cached and is a raw base at the parent's scale.

## Log

- 2026-09-12 — **run order corrected before any training.** The driver had the positive
  control last, which would have spent ~40 GPU-hours on the treatment before learning
  whether the regime has identification power at all. Reordered to a PC-first budget
  ladder (N=2,000, one escalation to 5,000, hard stop). Worst case is now a ~4-hour
  stop instead of a two-day one. N is set by the positive control only; treatment data
  is not consulted.
- 2026-09-12 — pair set built and frozen: 10,000 pairs, 9,132 distinct pages, median
  context 133 vs 13,084 tokens (98.4x), identical targets. sha256 b0e71fdf...

- 2026-09-11 — power section added to the pilot card before any run.
- 2026-09-11 — parent paper read in full; no length-controlled experiment exists in it.
  Table 1 re-analysis recorded. NQ length audit on 3 shards: 18.4% of raw examples give
  clean pairs, 6.5% survive the frozen length window. Design frozen in `PILOT_CARD.md`.
