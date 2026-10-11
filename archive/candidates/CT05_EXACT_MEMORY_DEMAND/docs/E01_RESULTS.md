# CT05 E01 — Results and Verdict

Run 2026-09-27. Protocol: `E01_PROTOCOL.md` (frozen before data; amendments 1–2 recorded there).
Raw: `results/e01/*.jsonl`. Readouts: `results/e01_summary.txt` (`src/analyze_e01.py`),
`results/e01_copy_split.txt` (`src/analyze_copy.py`).

Scale: Qwen3.5-9B 182 checkpoints / 2292 events; Qwen3-8B 188 / 2450; 79 trajectories
(40 SWE-smith, 39 APIGen-MT). 54 SWE checkpoints skipped (history > 12k tokens).

## Verdict: Kill A fires — **KILL**

Both pre-registered conditions hold:

| Readout A | Qwen3.5-9B (hybrid) | Qwen3-8B (Transformer) |
|---|---|---|
| `rho_2 = 1 − dNLL(KVWIN_2)/dNLL(TEXTWIN_2)` | **−0.005** [−0.034, 0.024] | 0.025 [−0.036, 0.069] |
| `rho_4` | **−0.010** [−0.047, 0.013] | 0.008 [−0.103, 0.037] |
| hybrid-specific leverage `rho_H − rho_T` (k=2 / 4) | −0.031 [−0.072, 0.031] / −0.018 [−0.056, 0.076] | |
| per-event recurrence carry `dBOTH − dKV`, median | **0.001 nats** (mean 0.56, CI [0.47, 0.65]) | n/a |

95% CIs are trajectory-bootstrap, on the 182 checkpoints both models completed.

Evicting the KV of old events costs Qwen3.5-9B exactly as much as deleting their text and
re-prefilling: the recurrent state, which has absorbed those events, gives back nothing
measurable at the window level, in either harness. For events whose deletion matters
(dTEXT > 1 nat, n = 601), hiding only their KV already produces 86% of the deletion effect;
the recurrent state's knowledge of the event restores 13% when KV is gone, and swapping out the
recurrent state alone (KV intact) costs 7%.

## Why: the dependence sits on verbatim copying

A target token is "copy-from-e" if the target trigram ending at it occurs in event e.
Copy tokens are 11% of target tokens but carry 60% of the KV-hide damage on important events.

| Qwen3.5-9B, important events | copy-from-e tokens | other tokens |
|---|---|---|
| KV-hide dNLL | 5474 | 3703 |
| recurrence carry (BOTH − KV) | 83 | 1300 |
| carry share | **1%** | 26% |

This is the *What Attention Recalls and Recurrence Controls* dissociation (2609.04434),
reproduced on natural agent decisions: exact strings (paths, IDs, reservation numbers) come
only from attention; recurrence carries a quarter of the non-verbatim influence. Agent actions
are dominated by the first kind.

The motivating example fails directly. The tau-bench **policy system prompt**, the proposal's
case of "important but carried semantically by recurrence", has dKV 16.6 ≈ dTEXT 16.2 nats and
needs its exact KV in 95% of checkpoints. SWE task descriptions: dKV 7.8 vs dTEXT 8.5.

## Readouts B and C (recorded; do not change the verdict)

- **B, structure holds.** 41% of events have |dKV| < 0.05; the top 10% of events carry 92% of
  positive demand (Transformer 88%). 26% of important events do not need their KV (dKV < 0.2),
  but the Transformer shows 22%. That redundancy comes from later tokens, not from recurrence.
- **C, the demand is predictable only with foresight.** Budgeted block eviction, recovery of
  the oracle's gain over random (Qwen3.5-9B, 25% / 50% of history kept):

  | signal | 25% | 50% |
  |---|---|---|
  | attention from the future action's own queries (not deployable) | 0.99 | 0.93 |
  | SnapKV-style window + header attention (deployable) | 0.36 | 0.23 |
  | recency | 0.34 | 0.09 |
  | DeltaS state drift | 0.09 | 0.02 |
  | event surprisal (LM stand-in for HAM/HOLA) | −0.51 | −0.64 |

  Hybrid-native signals (drift, surprisal) are the weakest. The only strong predictor is
  knowing the action's queries, which is the query-aware retrieval problem that Quest, Lookahead
  Q-Cache and AgentKV's phase-query buffers already address, and none of them needs recurrence.

## Other observations (not claims)

- Cross-model agreement of per-event exactness demand: Spearman 0.36 (dTEXT 0.47). Demand is
  partly a property of the trajectory and partly of the model.
- Qwen3.5-9B depends slightly *more* on exact KV than Qwen3-8B (KV-hide share of deletion effect
  0.90 vs 0.82). The two models also differ in training data and in gated attention, so this is
  not attributable to the recurrent layers.
- 7% (hybrid) and 13% (Transformer) of single-event KV hides *lower* the NLL of the logged action,
  i.e. those events act as distractors.
- Methodology: Qwen3-8B depends on attention-sink tokens and Qwen3.5 (gated attention) does not.
  Any KV intervention compared across these families must protect the sink (Amendment 2).

## What this does and does not show

- It covers Qwen3.5-9B, sequential GDN hybrids and teacher-forced logged actions. A parallel
  hybrid (Falcon-H1) or free-running own actions could differ. Under the stop-loss rule these are
  **not** run: each would be a rescue that adds a model-family or decoding condition to a claim
  whose central quantity is zero on the pre-registered model.
- It does not show that recurrence *cannot* carry agent history. SWAX (2509.24552) shows that
  training with short or stochastic attention windows forces the recurrent part to learn
  long-range memory, and learnable-eviction hybrids (2510.20787) train for KV scarcity. What it
  shows is that current production hybrids are not trained that way. Their recurrent state gives
  agent decisions almost no "compressed influence" to allocate against.

## Addendum (2026-09-27, post-kill, no new model calls): tool identity vs argument values

Requested check for a possible "control first, retrieval second" shape. Target tokens are split
into tool/command name, parameter key, parameter value, prose and syntax
(`src/analyze_action.py` → `results/e01_action_split.txt`).

| window eviction (keep system+task+last k) | tau: name | tau: value | swe: name | swe: value |
|---|---|---|---|---|
| Qwen3.5-9B KVWIN2, share of loss | 0% | 99% | 3% | 81% |
| Qwen3.5-9B KVWIN2, first-name-token dNLL > 1 nat | 0% of ckpts | | 21% of ckpts | |
| Qwen3.5-9B KVWIN0, first-name-token dNLL > 1 nat | **6%** | | 88% | |
| Qwen3-8B KVWIN0, first-name-token dNLL > 1 nat | **77%** | | 85% | |

- Under realistic windows (k = 2, 4) the eviction cliff sits almost entirely on argument values:
  99% of the loss in tau and 81–86% in SWE. Tool identity mostly depends on the last couple of
  events, which the window keeps.
- Identity is not history-free. For single-event KV hides on important events, name tokens are
  the most sensitive *per token* (tau 1.24, SWE 3.35 nats/token), because the choice is
  concentrated in one token and usually driven by a recent event.
- Recurrence carry (BOTH − KV) lands on names and syntax, not values: tau names get 0.455
  nats/token vs 0.011 for values. This is the retrieval/control split once more.
- One striking contrast, recorded here but **not a claim**: with every conversational event's
  KV hidden (KVWIN0), Qwen3.5-9B still predicts the tau tool name (6% of checkpoints affected),
  while Qwen3-8B loses it (77%). SWE shows no such difference (88% vs 85%). The two models differ
  in family and training, and no recurrent-state swap exists for window rows, so this cannot be
  attributed to recurrence.
- Verdict on the side question: the "control vs lookup" separation is visible in the data, but it
  is not registered as a topic (ToolGen / dispatch decomposition, LAQ, AgentKV nearby).
