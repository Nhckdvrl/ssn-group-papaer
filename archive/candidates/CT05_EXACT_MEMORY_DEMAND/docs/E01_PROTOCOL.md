# CT05 E01 — Exactness-Demand Map on Natural Agent Trajectories

Frozen 2026-09-27, before any trajectory-level result was seen.
Only the smoke/noise tests in `src/smoke.py`, `src/noise.py` (synthetic code text) had been run.

## Question

In a hybrid LM that has already absorbed an agent's history into its recurrent state, which past
events still need their **exact attention KV** at a decision point, and is that demand predicted by
signals the field already uses (recency, role, attention, state drift, surprisal)?

## Data (natural, logged, not constructed for this study)

- `swe`: SWE-bench/SWE-smith-trajectories shard 0 — SWE-agent harness, text commands.
- `tau`: Salesforce/APIGen-MT-5k — tau-bench airline/retail harness, native function calls.
- `src/prep.py` seed 0, 40 trajectories per source, <=3 decision checkpoints each (early/mid/late),
  histories <= 12k tokens. Target = the logged next action message, teacher-forced.
- Event = one harness message (system / task / assistant / think / call / obs / user).

## Models

- Hybrid: Qwen3.5-9B (24 Gated DeltaNet + 8 full-attention layers).
- Transformer control: Qwen3-8B (same lab, all-attention).
- Replication (only after the gates below are read): Qwen3.5-4B.

## Interventions at the decision chunk (history prefilled once)

| code | KV of event i at decision | recurrent state | later-token KV |
|---|---|---|---|
| FULL | visible | full | full |
| KV_i | hidden (attention layers only) | full (has absorbed e_i) | full |
| REC_i (hybrid) | visible | state of history-without-e_i | full |
| BOTH_i (hybrid) | hidden | state of history-without-e_i | full |
| TEXT_i | e_i deleted, whole history re-prefilled | — | — |
| KVWIN_k | hide all events except system, task, last k | full | full |
| TEXTWIN_k | delete those events' text and re-prefill (compaction-like) | — | — |

All rows of one checkpoint run in one batch with an in-batch FULL row (in-batch duplicate KL = 0
exactly; cross-batch noise 2e-4 nats/token on Qwen3.5-4B).

## Primary observable

`dNLL = NLL_cond(target) − NLL_full(target)` summed over target tokens (nats), plus mean per-token
`KL(p_full || p_cond)`. SWE also reports the command-block (action) subset.

## Pre-registered readouts and kill gates

**A. Compression leverage (does recurrence carry evicted history at all?).**
Recurrence retention `rho_k = 1 − dNLL(KVWIN_k)/dNLL(TEXTWIN_k)`, k in {2,4}, pooled by checkpoint.
The same quantity on Qwen3-8B measures what later-token KV alone retains.
Hybrid-specific leverage `= rho_H − rho_T`. Also `BOTH_i − KV_i` (the part of e_i's effect that
the recurrent state supplies once exact KV is gone).
*Kill A:* hybrid-specific leverage < 0.10 and median per-event `BOTH_i − KV_i` indistinguishable
from 0 → recurrence does not provide compressed influence for agent history in current hybrids;
the "exact vs compressed" allocation question has no object.

**B. Structure.** Share of events with `dNLL(KV_i)` < 0.05 nats; concentration (share of total
demand held by the top 10% events); exactness vs importance: events with large `TEXT_i` but small
`KV_i`.
*Kill B:* demand is diffuse (top-10% share < 30%) or no feature set predicts per-event demand
(checkpoint-grouped CV Spearman < 0.2).

**C. Existing signals.** Rank events by recency, role prior, length, FULL-run decision-token
attention mass, DeltaS state drift (their Eq. 3: mean over GDN layers of
`||S_after − S_before||_F / ||S_before||_F` over the event), and event surprisal (mean LM NLL of
the event tokens; HAM/HOLA use recurrent prediction error — surprisal is the LM-level stand-in and
is labelled as such). Evaluate by (i) Spearman with `dNLL(KV_i)` within checkpoint, and
(ii) budgeted multi-event eviction: keep top events by each signal under 25/50% of history tokens,
hide the rest, measure dNLL; single-event `KV_i` ranking is the reference ("one-shot oracle").
*Kill C:* the best existing signal recovers >= 90% of the oracle's dNLL reduction at both budgets.

**D.** Live agent success is **not** part of E01. It is only designed if A–C survive.

## Amendment 1 (2026-09-27, after a 2-checkpoint Qwen3.5-4B plumbing test; no full-data result seen)

- Budget/ranking analyses (C) move to **blocks**: each message split into <=256-token blocks,
  single-block KV-hide gives the block oracle. At message granularity one large tool output
  exceeds the budget and every policy selects the same set (seen in the plumbing test).
- The attention signal computed from the target tokens' queries uses the future action and is
  relabelled `attn_future` (a query-aware upper reference, not deployable). The deployable
  signal is `attn_deploy`: mean of SnapKV-style attention from the last 32 history tokens and
  from the assistant-header tokens that precede the action.
- DeltaS drift is computed per block (their chunk unit) and per message.
- Plumbing test observation, recorded so it is not later mistaken for a finding: in the one SWE
  checkpoint, `KVWIN_2` (hide KV, keep recurrence) hurt more than `TEXTWIN_2` (delete text and
  re-prefill). rho can therefore be negative; readout A reports it signed.

## Amendment 2 (2026-09-27, after 1 hybrid + 3 transformer checkpoints of the full run)

Hiding the system message's KV cost Qwen3-8B +36.7 nats while deleting the system text cost
-2.8: an attention-sink artifact (Qwen3 attends heavily to the first tokens; Qwen3.5's gated
attention does not). Since this would make every hybrid-vs-Transformer contrast a sink contrast,
the first 4 tokens are never hidden in any KV intervention (StreamingLLM convention), for both
models. The partial run was discarded (`results/e01_nosink_discarded/`) and restarted.

## Things this experiment cannot establish

- Teacher-forcing a logged (Claude/xLAM) action measures the model's dependence when predicting
  that action; it is not the model's own free-running decision.
- REC_i/BOTH_i use a state computed from a shorter history paired with KV at full positions
  (State-swap construction; partly out-of-distribution, as its authors note).
- Single-event deletions under-count redundant information; KVWIN/budget rows address this.
