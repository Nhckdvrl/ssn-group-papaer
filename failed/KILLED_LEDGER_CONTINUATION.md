# Killed Research-Question Ledger — Continuation

This file continues `failed/KILLED_LEDGER.md` where the historical ledger on `main` is stale. It is still a cumulative anti-resurrection ledger, not a one-file-per-topic archive.

**Continuation date:** 2026-09-17  
**Authoritative continuation begins:** **K193**  

> A new model, seed, procedure pair, curriculum, causal-localization method, or renamed framing does not reopen a killed parent question. Reopening requires a new scientific object that survives a fresh Selection audit independently of the failed lineage.

---

# K193 — L45: Does Internalization Preserve Procedural History?

**Status:** `ARCHIVED / NO-GO — PILOT FAILED — NO MECHANISTIC RESULT`  
**Date:** 2026-09-17  
**Primary failure:** `OTHER — UNSTABLE_FULLY_INTERNALIZED_ENDPOINT / IDENTIFICATION_FAILURE`  
**Secondary:** `DECISIVENESS_FAILURE`, `WORKLOAD_PATH_FAILURE`

## Locked scientific question

> If two otherwise matched models learn the same function through different explicit algorithms, does fully internalizing the reasoning preserve the taught causal algorithmic identity, or erase/canonicalize procedural history?

The intended experiment held the function, architecture, examples, prompt, answer, optimizer, update budget, and final direct-answer objective fixed while changing only the explicit procedure used during training. A causal-abstraction / interchange-intervention analysis was planned only after both procedure arms produced stable, behaviorally comparable fully-internalized endpoints.

## Why the pilot stops before DAS

The behavioral gate was intentionally placed before any mechanistic measurement. Under the frozen unified recipe selected only on behavioral competence — `lr=5e-5`, `250 steps/token`, `4500 final steps` — the four independent forward-presentation seeds gave:

| seed | Algorithm A S5 held-out | Algorithm B S5 held-out |
|---|---:|---:|
| 0 | 1.000 | 1.000 |
| 1 | 1.000 | 0.006 |
| 2 | 1.000 | 0.330 |
| 3 | 0.922 | 1.000 |
| **passes at >=0.95** | **3/4** | **2/4** |

The pre-declared rule was that `B <= 2/4` eliminates the procedure pair. It fired.

The failure is not adequately described as "Algorithm B is hard." Both arms can fail, and every run remains healthy until the final transition from `28/29` removed reasoning tokens to `29/29`: the point at which the last external scratchpad token disappears and the computation must become fully internal. B is more fragile and can collapse catastrophically, but A also missed the functional threshold on one seed.

A presentation-reversal diagnostic did **not** support the earlier positional explanation as the main behavioral cause: at seed 0, reverse-presentation S5 held-out accuracy was `A=0.969`, `B=1.000`. Thus the dominant obstacle is the instability of the fully-internalized endpoint under the current task × model × stepwise-internalization setup, not a simple first-two-vs-last-two operand position effect.

## Why successful-seed filtering is forbidden

A downstream causal-algorithm comparison would have to condition on which runs happened to survive the final internalization transition. That selection occurs **upstream of every DAS/control analysis** and is plausibly coupled to the optimization basin and therefore to the final internal algorithm itself.

Keeping only successful A/B endpoints would therefore compare a biased subset of training trajectories. No shuffled intervention, matched corruption, DAS capacity control, extra seed, or second localization method can repair that selection bias after the fact.

Accordingly:

> **No DAS was run. No S5 mechanistic IIA, causal-algorithm score, or procedural-inheritance effect was ever computed.**

This archive is a feasibility / identification failure. It is **not** evidence that procedural inheritance is absent.

## What was learned before the stop

1. The symmetric explicit procedures were learnable and generalized compositionally; the experimental construction itself was not a lookup-table trick.
2. In the explicit-CoT positive control, token-level interchange of the taught intermediate produced the exact counterfactual downstream answer with `IIA = 1.000`. This validated the basic counterfactual semantics of the task.
3. An earlier apparent A/B competence gap was partly a training-recipe artifact: `lr=1e-4` could destroy B, while a unified lower-LR/slower curriculum could bring both arms to `1.000` on some seeds. This repair was completed before any causal measurement.
4. Even after freezing that unified recipe, the final fully-internal transition remained seed-unstable. That instability is the decisive blocker.

## Lineage-level reason to stop rescuing

L45 arose only after the preceding L44 lineage had already consumed multiple increasingly specialized routes:

- **L44 / J-space:** abandoned because the intervention did not cleanly identify workspace dependence; J-direction ablation strongly damaged generic computation and was entangled with high-gain Jacobian transport.
- **L44 reconstruction / causal algorithm identity:** narrowed after a 2026 nearest-owner audit showed that the broad "does internalization preserve the explicit algorithm or learn a shortcut?" mother question was already too close to existing internalization work.
- **L45 / procedural history:** introduced a genuinely more independent matched question, but its fully-internalized endpoint failed the pre-mechanistic stability gate above.

Each individual stop was correct. Taken together, however, the repeated need to replace the instrument, sharpen the object, redesign the task, and repair the training endpoint is itself evidence that the current leverage is insufficient. Continuing by trying a third procedure pair, another internalization curriculum, another localization method, or another toy function would turn the programme into phenomenon hunting.

## Hard anti-resurrection rule

**Do not reopen L45 by:**

- filtering to successful seeds;
- adding more seeds until a clean subset appears;
- tuning the frozen curriculum or LR after the gate result;
- swapping in another A/B procedure pair on the same unstable endpoint and calling it the same pilot;
- replacing DAS with another causal-localization method;
- returning to J-space / workspace ablation;
- renaming the question as latent deliberation, algorithm preservation, algorithm migration, procedural inheritance, or automaticity while keeping the same experimental dependency.

A future project may revisit the broader scientific area only if it begins from an **independently stable internalization substrate** whose multi-seed fully-internal endpoint is established before the procedural-history hypothesis is introduced, and the resulting question passes a fresh owner/novelty audit as a new candidate.

## Reusable assets / lessons

Preserve rather than rerun:

- symmetric same-function / different-explicit-procedure task construction;
- treatment-fraction curriculum mapping;
- exact source→recipient counterfactual interchange harness;
- token-level positive control (`IIA=1.000`);
- the rule that endpoint competence/stability must be established across independent seeds **before** causal algorithm identity is measured;
- the lesson that competence-conditioned mechanistic analysis can create survivor bias when endpoint failure is treatment- or basin-dependent.

**Final disposition:** `K193 / ARCHIVED / DO NOT RESCUE WITH ANOTHER INSTRUMENT OR PROCEDURE PAIR`.