# CT07 E00 — Intra-Action Query Emergence (frozen 2026-09-27, before any E00 output)

## Question

Inside one logged tool action, when does the history-attention of the already-generated prefix
become a memory query good enough to choose which old history blocks to keep for the upcoming
exact argument values?

## Material (unchanged from CT05 E01)

- Qwen3.5-9B; `CT05/data/checkpoints.jsonl`; CT05 rendering (`render.py`) and 256-token blocks.
- Teacher-forced logged actions. Token classes follow `CT05/src/analyze_action.py`:
  tau = name / key / value / syntax (Qwen3.5 XML tool call); swe = prose / name / value / syntax
  (last ``` command block).
- Checkpoints whose target has no value token are excluded.

## Stage queries (strictly causal)

A query at decision position p predicts token p+1. Stage s uses the mean attention (over heads,
the 8 full-attention layers, and the query positions) of the FULL forward pass, cumulatively
from decision position 0 up to the stage boundary b_s:

| stage | boundary b_s (inclusive) | sees |
|---|---|---|
| `DEPLOY` | CT05 reference: mean of the last-32-history-token window and the header queries | nothing of the action |
| `HDR` | last header position (predicts the first target token) | nothing of the action |
| `PROSE` (swe) | position predicting the opening ``` token | the reasoning prose |
| `TOOL` | last tool/command-name token | tool identity |
| `KEY` (tau) | last token of the first argument key | tool + first key |
| `PREVALUE` | position predicting the first value token | everything except values |
| `FUTURE` | all positions up to the last target-predicting one | the whole action, values included (CT05 `attn_future`) |

No stage before `FUTURE` includes any value token.

## Policies and outcome

- Ranking signals: each stage query above, plus `oracle` (CT05 E01 single-block KV-hide dNLL),
  `random` (seed 0), and a **lexical key control** (`LEXKEY`, tau only): blocks ranked by the count
  of the first argument key's tokens they contain (deployable at `KEY`, no model). For swe the
  lexical control counts the command-name tokens (`LEXNAME`).
- Budgets: keep 25% / 50% of history tokens (greedy knapsack by score, as in CT05). Sink tokens
  always kept.
- Eviction time: hidden blocks are masked only for query rows from `PREVALUE` on, so the prefix
  is produced with full history and eviction happens right before value binding.
- Outcome `G` = summed dNLL of the value tokens against an in-batch FULL row.

## Primary readout

`R_s = (G_DEPLOY − G_s) / (G_DEPLOY − G_FUTURE)`, pooled per source (tau, swe) and budget, with
trajectory-bootstrap 95% CIs. `R_DEPLOY = 0`, `R_FUTURE = 1`.

## Frozen decision rule

- **KILL** if `R_PREVALUE < 0.3` at both budgets in both sources. The good query appears only
  once values are being written, so there is no deployable leverage.
- **KILL (trivial mechanism)** if, in tau, `LEXKEY` reaches ≥ 80% of `R_PREVALUE` at both budgets.
  The "query" would then be plain key-string matching in the old tool outputs. For swe, the
  analogous check uses `LEXNAME`.
- **STRUCTURE PRESENT → return to Selection** (not pilot) if `R_PREVALUE ≥ 0.5` at ≥ 1 budget in
  **both** sources, bootstrap lower bound > 0.2, and the lexical control is not ≥ 80% of it.
- Anything else is ambiguous and, under the stop-loss rule, counts against the topic. It is
  reported, not rescued with new stages, models or data.
- `R_TOOL`, `R_KEY`, `R_PROSE` locate *where* the jump happens. They are descriptive and do
  not rescue a failed rule.

## Secondary (descriptive)

Within-checkpoint Spearman between each stage's block attention and the CT05 block oracle. Also
the per-query-position attention trace (query position × block, stored fp16) for later curves.

## Known limits

Teacher-forced logged actions, not the model's own generations. Whether the argument-slot label
is lexically present in history is the main confound (hence `LEXKEY`). The model is a single
hybrid, but only attention layers enter the stage signals, so nothing here is hybrid-specific.
