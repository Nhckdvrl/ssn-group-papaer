# CT09 — Read, Then Remember? Cross-Channel Information Handoff in Hybrid LMs

Registered 2026-09-27 as CANDIDATE / inference-only RECON.
**Status: KILLED AFTER E00 (2026-09-27), `CT-KILL-20260927-5`** (`docs/E00_RESULTS.md`). In one
sentence: after one attention lookup, Qwen3.5-4B's recurrent channel keeps only a partial trace of
the retrieved value, H = 0.108 [0.104, 0.112] of attention's log-odds. That trace is
retrieval-specific (unrelated read 0.002, same value as text ≈ 0), but it is below the frozen 0.20
bar, and the carrier (short-conv window vs matrix state) is unidentified.

## Question (the only one)

> Once attention has retrieved an exact item, can the recurrent channel carry that item after
> the attention memory is removed?

2609.04434 (*What Attention Recalls and Recurrence Controls*) and CT05 show where a fact lives
**before** it is looked up (KV, not recurrent state). Nobody has tested where it goes **after**
attention reads it. In Qwen3.5 (3×GDN → 1×attention, ×8) the attention output at token t feeds the
higher GDN layers, so the retrieved item *can* be written into their state. Whether released
checkpoints do this is the empirical question.

Not a CT05 resurrection: CT05 measured R before lookup (ρ ≈ 0). CT09 measures R after a lookup,
starting from a recurrent state that provably carries no A/B information (a shared donor state).

## Selection-stage decisions (2026-09-27)

- "When does a hybrid LM actually need attention?" (token-level attention-gain concentration) is
  **not registered**: L2A (Learning When to Attend, Amazon Science) already does token-wise gating of
  global attention (~80% skipped), and FlowHN does attention/SSM token routing.
- Discipline from CT05–08: run only if (phenomenon exists) + (manipulation at the same scale and
  regime) + (missing variable not owned). Here the channel split is causally established on the
  same model and the intervention is a direct cache cut, so no latent variable is guessed.

## Nearest priors

| Prior | Owns | Not covered |
|---|---|---|
| 2609.04434 What Attention Recalls… | split-prefill / state-swap **before the query** | fate of an item after attention reads it |
| OLMo Hybrid (2604.03444); Reasoning Primitives (2604.21454) | state tracking → recall compositions | recall → state (reverse direction), not tested causally in a cache |
| Learning to Forget Attention | training-time consolidation of retrievals into weights | within-inference transfer into recurrent state |
| DART | decode KV from recurrent states (reverse direction, trained) | native attention → recurrence |
| Component ablation (2603.22473); Where Should LoRA Go? | delete / adapt components; topology matters | information flow between components |
| L2A, FlowHN | whether to call attention | where retrieved content goes |
| LatentPort (2609.25053) | hybrid state handoff **across models** (4B→9B) | within-model attention→recurrence handoff |

## Layout

- `docs/E00_PROTOCOL.md` — frozen conditions, estimand and gates.
- `src/prep.py` items; `src/handoff.py` cache surgery; `src/e00.py` runner; `src/smoke.py` plumbing.
- `src/env.sh` — runtime, same as CT05.
