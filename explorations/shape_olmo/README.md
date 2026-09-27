# ShapeLab — OLMo matched-architecture microscope (exploration, not a candidate)

Opened 2026-09-28 at the user's direction after the CT05 Shape lineage was archived.
**Status: EXPLORATION.** No RQ, no CT number, no paper claim. A topic may be registered only after
an anomaly grows out of P2–P4 and passes the usual selection gate.

Search question (not an RQ): *when does changing the representation of the same computation
change which architecture is best?*

## Why this platform

The Olmo 3 / Olmo Hybrid family is matched in tokenizer, data and recipe. The mother phenomenon
already exists and is non-uniform: Li & Merrill, *Comparing Transformers and Hybrid Models at the
Token Level* (arXiv 2606.20936). No training is allowed in P0–P4.

## Phases

| phase | content | status |
|---|---|---|
| P0 | reproduce the token-level gap: prose content/function Δ, open–close bracket gaps, repeated-n-gram decay; filtered curves | in progress |
| P1 | reproduce the pronoun-memory / entity-tracking / structural-closure probe signs | — |
| P2 | natural-token disagreement mining | — |
| P3 | representation interventions on the same latent problem | — |
| P4 | natural-domain replication of the strongest signal | — |

## Checkpoint availability (checked 2026-09-28) — deviation from the plan

The **1B Transformer / Hybrid / Pure-RNN (GDN)** development runs of §6 are described as "released
by Merrill et al. (2026)", but no public identifier was found:
- not on the Hugging Face hub (allenai org search: hybrid / gdn / rnn / ladder / 1B);
- not in the OLMo-core official scripts or checkpoint CSVs (only the 7B stage CSVs);
- the `olmo-checkpoints.org` bucket serves known paths but cannot be listed. The run-name
  convention is known from OLMo-core history (`src/scripts/train/linear-rnns/1b/{control,
  gated_deltanet, hybrid_gated_deltanet++}.py`: 16 layers, d_model 2048, WSD with 1B-token
  anneals, save every 1000 steps), but the run names were supplied at launch.

What *is* public and is used instead:
- the 7B pair of the paper's main analysis: `allenai/Olmo-3-1025-7B` and `allenai/Olmo-Hybrid-7B`
  (`main`);
- matched **stage-1** branches for both, every 1000 steps (`stage1-step{N}`, 0 → ~1.41M;
  Hybrid 4.19M tokens/step). These are stable-phase checkpoints, **not WSD-annealed**, so the
  analogue of their Fig. 7 is T vs H at 7B without a Pure-RNN arm.

The missing Pure-RNN arm blocks the planned `H > max(T, R)` analysis. Options: ask the authors
(W. Merrill / Y. Li) for the 1B paths, or drop R. This is the user's call.

## Runtime

Scoring: `openslime` python + transformers 5.12.1 vendored from `fgvd` (same recipe as CT05),
which has `olmo_hybrid`. Tagging: `verl-clean` python (nltk 3.10, pandas).
