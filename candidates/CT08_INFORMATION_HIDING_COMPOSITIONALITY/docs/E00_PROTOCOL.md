# CT08 E00 — operational protocol (frozen 2026-09-27, before any E00 model call)

Refines the E00 gate in `../README.md`. Nothing here was chosen after seeing E00 outputs.

## Arms (all Qwen3-8B family, non-thinking, temperature 0.7, top_p 0.8, 1 sample per instance)
- **A — RLM-Qwen3-8B** (`mit-oasys/rlm-qwen3-8b-v0.1`) as root, Qwen3-8B sub-calls.
- **B — Qwen3-8B zero-shot** as root in the identical harness, Qwen3-8B sub-calls.
- **C — Qwen3-8B flat** (full context + question, YaRN factor 4; descriptive only).

Harness: `alexzhang13/rlm` at `3a63ff4` (2026-01-29, the model-release state; `vendor/rlm_v01`),
local REPL, depth 1, max 20 iterations, 4096 max tokens per root turn and per sub-call. System
prompt: the paper's Qwen3-8B prompt (appendix C, (1a) + diff (1d)), minus the context-metadata
sentence, which `3a63ff4` injects as its own assistant message. Root prompt = the OOLONG
question. Served by vLLM 0.11 (`verl-clean`).

## Data
OOLONG-synth, all 10 domains (8 test + trec_coarse, spam from validation). None appears in
RLM-Qwen3-8B's LongBenchPro training. Context lengths 16,384 and 32,768. 20 instances per
domain × length (seed 0), so 400 instances per arm. Score = the RLM repo's OOLONG `_synth_score`.

## Gate (both required, else KILL)
1. **Learned transfer:** mean score A − B ≥ 5 points, paired bootstrap (instances) 95% CI > 0.
2. **Isomorphism:** each root trajectory is reduced to a skeleton, the sequence of API names and
   control keywords (`llm_query`, `print`, `len`, `split`, `for`, `FINAL_VAR`, ...) parsed from its
   REPL code, with all literals and user identifiers removed. For every (task type, length) cell,
   compute the mean normalised edit distance between skeletons of *different domains*. Required:
   A's mean < B's, paired bootstrap over cells, 95% CI of the difference < 0. The training
   trajectories are not public, so this cross-domain isomorphism (the paper's own notion) replaces
   "closer to training-style skeletons" in the README.

## Descriptive
Leakage = share of REPL-output characters shown to the root that are verbatim payload lines, per
arm and domain. Iterations, sub-calls, failures to finish.
