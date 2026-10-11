# CT08 E00 — Results and Verdict (2026-09-27)

Protocol: `E00_PROTOCOL.md`, frozen and committed (`15ff99a`) before any model call.
Raw: `results/e00/arm_{A,B,C}.jsonl`. Readouts: `results/e00_summary.txt` (`src/analyze_e00.py`) and
`results/e00_failure_modes.txt` (`src/failure_modes.py`, descriptive).
Run log (including one mis-routed restart, corrected before analysis): `logs/E00_LAUNCH.md`.

400 OOLONG-synth instances (10 domains unseen by RLM-Qwen3-8B × 16k/32k × 20).
Timeouts are scored 0 under the same rule for both arms: A 3, B 5. The local REPL has no execution
timeout, so these instances were still unfinished when the rest of the arm had completed.

## Verdict: both gates fail — **KILL**

| | A: RLM-Qwen3-8B | B: Qwen3-8B, same harness | C: Qwen3-8B flat |
|---|---|---|---|
| mean OOLONG score | **0.274** | **0.346** | 0.515 |
| errors (context overflow etc.) + timeouts | 28 | 25 | 0 |

- **Gate 1 (learned transfer):** A − B = **−7.2 points**, 95% CI [−12.8, −1.7]. The released
  natively recursive model is *worse* than the untrained model in the same harness on unseen
  domains. A is below or equal to B in 8 of the 10 domains.
- **Gate 2 (isomorphism):** cross-domain skeleton distance is A 0.762 vs B 0.737 (27 cells),
  A − B = +0.026 [−0.002, 0.056]. A's root trajectories are no more isomorphic across domains
  than the untrained model's.
- A post-hoc bound (does not change the verdict): 26 of A's answers return a variable name
  literally (`FINAL(answer_text)`, the template error the RLM authors report patching in their
  data). Counting all 26 as correct gives A − B ≈ −0.7, still far from +5.

## What the arms actually did (descriptive)

- A answers within a median of **2** root iterations, makes **no sub-call in 75%** of instances,
  and in 19% of instances emits code and the final answer in the same first turn, before seeing
  any REPL output.
- "Hiding" is not realised at this scale. The root sees about a fifth to a quarter of the payload
  verbatim anyway (A 21%, B 25% of the context; of all REPL output shown to the root, 47% / 66% is
  payload lines). Most instances never delegate to a sub-call (A 75%, B 69%).
- The harness itself costs 17–24 points against plain full-context reading at ≤ 32k.

## Why this closes the question at feasible scale

The CT08 triad needs one regime where three things hold at once: (i) the visible arms (MIXED /
SEPARATE-VISIBLE) fit in context; (ii) an RLM-style model shows learned transfer; (iii) its
trajectories are isomorphic across domains. At ≤ 32k on the only public natively recursive model,
(ii) and (iii) both fail and the RLM does not actually hide the payload. The published transfer
effect (RL at 30B, 32k→2M) lives exactly where the visible arms cannot exist, so separation vs
hiding cannot be contrasted at matched length within the envelope. Scaling to 30B RL is outside
it (README). This is the frozen kill branch, not a rescue candidate.

## Limits

Single released SFT checkpoint, the harness from its release commit, the prompt reconstructed from
the paper appendix, OOLONG-synth only, ≤ 32k, one sample per instance. None of these is varied
further (stop-loss rule).
