# Quarantined 2026-09-14 — item identity mismatch

`run_eval.load_items(cell, n, seed)` assigns ids **positionally** after shuffling a
subset of size `n`. So `gsm8k-0` at `n=200` is a *different question* than `gsm8k-0` at
`n=500`. Any run built at a different `n` than the reference run silently compares
different problems.

Verified: **all 21 main E12 clamp result files carry 0/500 gold mismatches against
`results/e01/llama31_8b_instruct/gsm8k_gen_cot__full.jsonl`.** Every reported C2a
number, the surgical residual and the foreign arm are unaffected.

Quarantined here:

| file | mismatched golds | consequence |
|---|---|---|
| `_bscheck/bs{8,32,128}.jsonl` | 98/100 | batch-size equivalence check invalid, must be redone at n=500 |
| `_bscheck2/bs{8,32,128}.jsonl` | 197/200 | same |
| `gsm8k_gen_cot__corrupted_ref__*.jsonl` | 489/500 | the temperature-sampled control prefixes |
| `gsm8k_gen_cot__readoutfirst__corrupted__f0.5.jsonl` | — | the clamp run that consumed them |

## This corrects a diagnosis, not just a file

The temperature-sampled control was already discarded on 2026-09-14 for failing the
prefix-quality audit (`on_task` 0.073 against the treated prefix's 0.415), and the
stated cause was "tau = 1.3 degenerates into multilingual garbage".

**That cause was wrong.** `make_corrupted_reference.py` built its item set at
`n + calib_n = 620` while the reference run was built at `n = 500`, so the control was
clamping each model to *another problem's solution*. `on_task 0.073` was measuring
exactly that. The temperature calibration — grid bracketing the target, two divergence
statistics selecting the same `tau = 1.3` — was fitting to a target computed across
mismatched items and means nothing.

The conclusion (control invalid, route abandoned) is unchanged. The reason on record
is now the correct one.

## Fixes applied

- `make_corrupted_reference.py`: evaluation items built at exactly `n`; calibration
  items drawn from a disjoint seed.
- `run_e12_clamp.py`, `run_e13_refresh.py`: `assert_item_identity()` compares every
  item's gold against the reference run and exits loudly on any mismatch.
