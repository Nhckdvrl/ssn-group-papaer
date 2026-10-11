# L15 — Experiment Ledger

**Authorization:** `PILOT_CARD.md`, E01–E03 only. Mainline NOT APPROVED.
Any change to RQ, estimand, mechanism, central claim, or reviewer compression stops
execution and returns to selection.

---

## E01 / E02 — same-null detectability curve and competence-vs-integration

**Preregistered 2026-09-11, before any model output was inspected.**

### Linked claim

> C1 (candidate). For an identical visible null result, model posteriors do not scale
> with stated counterfactual detectability the way the stated observation model requires,
> **while** the same model, in the same context, reports `P(null|H)` correctly.

E01 supplies the detectability curve; E02 supplies the paired competence probe. They run
in one pass over the same items because the dissociation requires an identical context.

### Alternatives this run must be able to distinguish

| Account | Prediction that separates it |
|---|---|
| A. observation-conditioned inference | posterior tracks gold across `s`; KNI rate low |
| B. null-result heuristic (integration failure) | `P1_NULL` accurate, `P2_NULL` flat/compressed across `s`; KNI rate high |
| C. generic Bayes-arithmetic failure | `P2_ARITH` fails as badly as the framed items |
| D. observation-model ignorance | `P1_NULL` also fails; no dissociation to report |
| E. surface-wording artefact | effect present under one null wording only |
| F. prior anchoring / no update at all | `P2_NULL ≈ p` everywhere and `P2_POS` also ≈ `p` |

Accounts C, D, E and F are kill or reduce-to-known outcomes, not nuisance controls.

### Design

- Items: `data/items.jsonl`, 180 = 12 scenarios × priors {.2,.5,.8} × sensitivities
  {.05,.25,.50,.75,.95}, `f = 0`, threshold `.20`.
- Frames: access, search, monitoring (non-medical, 9 scenarios) and diagnostic
  (3 scenarios, **transfer condition only**).
- The visible outcome sentence is held identical across the sensitivity grid; the
  validator (`scripts/validate_stimuli.py`) fails the build if it is not.
- Conditions (`src/prompts.py`): `P1_NULL`, `P2_NULL` (primary), `P2_HANDED`,
  `P2_POS`, `P0_PRIOR`, `P2_ARITH`, `P3_DECIDE`.
- Answer modes: `direct` (answer only) and `cot` (brief reasoning allowed).
  **`cot` is primary for the kill decision**: if a capable model tracks the
  detectability-conditioned posterior when allowed to reason, the route dies, and it
  must not be rescued by having blocked computation.
- Null wording: two surface paraphrases per scenario for `P1_NULL`, `P2_NULL`, `P3_DECIDE`.
- Total prompt cells: 2,982 per model.

### Models

Two families: `Qwen/Qwen3-32B` (chat template with `enable_thinking=False`, so the
reasoning axis is ours and not the template's) and
`mistralai/Mistral-Small-24B-Instruct-2501`. A third family only if model heterogeneity
decides the outcome.

### Independent unit

The **scenario** (12), not the prompt cell. All confidence intervals resample scenarios.
Grid cells within a scenario share wording and are not independent observations.

### Parsing and exclusions

Fixed before inspection (`src/scoring.py`): last `ANSWER:` line; decimal in [0,1], or
`x%` → `x/100`; `yes`/`no` for `P3_DECIDE`. Anything else is INVALID and is reported as
coverage, never silently dropped. Decoding is greedy (`temperature=0`, `seed=0`), so
repeated generations are not treated as extra scientific units.

### Primary outcomes

1. `KNI rate = P(Err_post ≥ .10 | Err_obs ≤ .05)` (DATA_AND_GOLD §5).
2. Mean Spearman between model posterior and gold posterior across `s`, per curve.
3. Compression ratio: observed posterior range across `s` ÷ gold range.
4. Monotonicity violations across adjacent `s`.
5. Control contrasts: framed − arithmetic MAE; handed − stated-rate MAE;
   positive-counterpart MAE; prior-only MAE.

### Interpretation and stop conditions

- **Kill** if, in `cot` mode, both families track the gold posterior (mean Spearman
  ≥ .8 and compression ratio ≥ .7) — the phenomenon does not exist at this scale.
- **Kill** if `P2_ARITH` error is of the same size as framed error — the finding reduces
  to generic probability arithmetic.
- **Kill** if `P1_NULL` fails together with `P2_NULL` (obs-known rate low) — there is no
  competence/integration dissociation to sell.
- **Kill** if the pattern survives only in the diagnostic frame, or only under one null
  wording.
- **Continue to E03** only if at least one family shows high obs-known rate together with
  a materially high KNI rate across ≥2 non-medical frames.

E03 is not authorized until E02 is read against these conditions.

### Run record

| date | model | tag | GPU | wall | raw |
|---|---|---|---|---|---|
| 2026-09-11 | Qwen/Qwen3-32B | pilot_v1 | 0 | 463 s | `results/pilot_v1/qwen3_32b/` |
| 2026-09-11 | mistralai/Mistral-Small-24B-Instruct-2501 | pilot_v1 | 1 | 254 s | `results/pilot_v1/mistral_small_24b/` |

Pipeline change made **after the smoke check and before the primary run**, applied
uniformly to all 2,982 cells of both models: `cot` `max_tokens` 640 -> 1024 (observed
smoke maximum 566; the change removes a truncation-driven coverage risk). No prompt,
metric, threshold or gold was changed at any point after outputs were inspected.

### Outcome — KILL

Kill conditions 1 and 2 both fired, in both families. See `PILOT_REPORT.md`.
In the primary `cot` mode: mean Spearman vs gold 0.989 / 0.945, compression ratio
0.985 / 0.929, KNI rate 0.003 / 0.014, with obs-known rate 1.000 and every control
clean. In `direct` mode the failure is general (the `f=0` positive counterpart and the
bare-arithmetic control fail by the same margin), so it is not null-evidence specific.

**E03 was never authorized to run** and was not run: it is conditional on E02 showing an
integration gap.
