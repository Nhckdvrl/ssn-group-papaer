# CT07 E00 — Results and Verdict (2026-09-27)

Protocol `E00_PROTOCOL.md` (frozen and committed in `b23e68e` before the run). Qwen3.5-9B,
178 CT05 checkpoints (115 tau, 63 swe; 4 without name/value tokens skipped), 79 trajectories.
Raw: `results/e00/*.jsonl`, per-query block attention `results/e00/att/*.npz`.
Readouts: `results/e00_summary.txt` (`src/analyze_e00.py`) and `results/e00_value_curve.txt`
(`src/value_curve.py`, descriptive, no model calls).

## Verdict: frozen KILL rule 1 fires (no deployable leverage) — **KILL**

`R_s = (G_DEPLOY − G_s) / (G_DEPLOY − G_FUTURE)`. G is the summed value-token dNLL when blocks are
evicted right before value binding. Trajectory-bootstrap 95% CIs.

| | tau @25% | tau @50% | swe @25% | swe @50% |
|---|---|---|---|---|
| R_HDR | −0.30 | −0.38 | 0.03 | 0.01 |
| R_TOOL | −0.34 | −0.22 | 0.21 | 0.22 |
| R_KEY (tau) / R_PROSE (swe) | 0.03 | −0.35 | 0.20 | 0.22 |
| **R_PREVALUE** | **0.16** [−0.04, 0.34] | **0.13** [−0.30, 0.40] | **0.21** [0.11, 1.00] | **0.22** [0.11, 0.92] |
| R_LEX (lexical control) | −0.13 | −0.88 | 0.22 | 0.25 |

In absolute terms (tau, 25% budget), mean value-token dNLL is: DEPLOY 12.8, PREVALUE 11.0,
FUTURE 1.1, oracle 6.4, random 22.3. Everything the action has produced *before* its first value
buys back about a sixth of what the whole action's queries buy. `R_PREVALUE < 0.3` in all four
cells. The lexical-key control does not explain anything, because there is nothing to explain.

## Where the query does form (descriptive)

The critical block is the oracle's top block, for checkpoints where it costs ≥ 1 nat. The table
gives the share of checkpoints where each stage query ranks that block in its top 1 / top 3:

| stage | tau hit@1 | tau hit@3 | swe hit@1 | swe hit@3 |
|---|---|---|---|---|
| DEPLOY | 0.08 | 0.31 | 0.15 | 0.48 |
| TOOL | 0.09 | 0.21 | 0.37 | 0.69 |
| KEY / PROSE | 0.12 | 0.38 | 0.33 | 0.64 |
| PREVALUE (cumulative) | 0.13 | 0.46 | 0.37 | 0.69 |
| query emitting value token 1, alone | **0.42** | 0.59 | 0.34 | 0.69 |
| cumulative through value token 1 | 0.19 | 0.58 | 0.39 | 0.73 |
| FUTURE | 0.47 | 0.77 | 0.50 | 0.81 |

- **tau.** No binding point sits before the value. Localisation rises gradually through
  TOOL → KEY → PREVALUE, and the sharp locator is the query that has just started writing the value
  (hit@1 0.42 vs 0.13 pre-value). This is induction-style copy lookup: the value's own first token
  addresses its source.
- **swe.** The command name already ranks the critical block about as well as the pre-value prefix
  does (hit@3 0.69 vs FUTURE 0.81). Even so, only ~20% of the oracle's value-token gain comes back,
  because SWE values (paths, line ranges, code) draw on several blocks, not one.
- Both patterns say the same thing: the query that selects exact memory is formed **by the act of
  binding itself**, not by the control prefix. No structured-action boundary exists at which a
  harness could stop, select memory, and then bind. (Under the stop-loss rule this descriptive
  reading does not rescue anything; the verdict comes from the frozen rule alone.)

## Limits

Teacher-forced logged actions, a single model (Qwen3.5-9B), a first-value-slot definition, and
budgeted eviction from CT05's block oracle. None of these is re-run: each would add a condition to
a quantity that is small in all four pre-registered cells.
