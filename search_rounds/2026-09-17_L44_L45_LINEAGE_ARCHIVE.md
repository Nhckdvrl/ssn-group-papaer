# 2026-09-17 — L44/L45 Lineage Archive

**Final state:** `CLOSED / ARCHIVED`  
**Kill registration:** `K193` in `failed/KILLED_LEDGER_CONTINUATION.md`  
**No active candidate survives from this lineage.**

---

## 1. Scientific line that was explored

The lineage began from a simple standing question:

> When visible multi-step reasoning disappears through training, has the computation itself become more automatic, or has the reasoning merely moved inside the model?

It was progressively sharpened from workspace dependence (L44), to causal algorithm preservation, to the more independent L45 question:

> If two matched models learn the same function through different explicit algorithms, does full internalization preserve the taught procedural identity or erase/canonicalize it?

The scientific questions remain interesting. The archive decision concerns the available identification path, not a negative answer to those questions.

---

## 2. L44: J-space route — stopped on construct validity

The first causal instrument attempted to operationalize automaticity as reduced dependence on a shared J-space / global-workspace-like computation.

The audit found that J-direction ablation on the target open model produced substantial generic language damage and was geometrically concentrated in high-gain Jacobian transport directions. Stronger matched controls showed some reasoning selectivity, but the intervention could not cleanly separate workspace dependence from generic susceptibility to high-gain residual disruption.

Therefore no expensive internalization trajectory was interpreted through this instrument.

**Lesson:** a causal intervention that damages the target task more than a random control is not sufficient; it must identify the intended construct rather than generic computational fragility.

---

## 3. Reconstruction route — useful but owner-crowded

Interchange intervention / causal abstraction offered a cleaner causal object: intervene on an explicit intermediate variable and ask whether downstream computation follows the counterfactual value.

A cheap explicit-CoT probe succeeded at the token level (`IIA=1.000`) but full-residual hidden-state patching did not produce a clean internal variable substitution. More importantly, the broad question "does internalization preserve the explicit algorithm or replace it with a shortcut?" was judged too close to 2026 internalization / latent-reasoning trajectory work to support an independent paper identity merely by adding a stronger causal instrument.

This motivated L45 rather than another L44 instrument swap.

---

## 4. L45: procedural-history question

L45 introduced a matched causal comparison:

> Hold the function, inputs, answers, architecture, optimization budget and final direct-answer objective fixed; vary only the explicit algorithm used as the training rationale. After the rationale disappears, does the final causal algorithm retain that procedural history?

Two symmetric modular-arithmetic procedures were built with matched prompt/output structure and matched trace length. The plan was to perform DAS / causal-abstraction analysis only after both procedure arms produced stable, comparable fully-internalized models.

### Behavioral prerequisite

A unified recipe was frozen before any DAS result:

- learning rate: `5e-5`;
- curriculum: `250 steps / removed token`;
- fully-internalized final phase: `4500 steps`.

The gate required held-out S5 accuracy `>= 0.95` across independent forward-presentation seeds.

Final result:

| seed | A | B |
|---|---:|---:|
| 0 | 1.000 | 1.000 |
| 1 | 1.000 | 0.006 |
| 2 | 1.000 | 0.330 |
| 3 | 0.922 | 1.000 |
| **pass count** | **3/4** | **2/4** |

The locked elimination rule fired.

All runs were healthy until the final step where the last visible reasoning token disappeared. The fully-internalized transition was therefore not a stable experimental endpoint. A reversal diagnostic (`A_rev_s0=0.969`, `B_rev_s0=1.000`) did not support simple operand position as the main behavioral cause.

No DAS was run and no mechanistic treatment effect was computed.

---

## 5. Why successful-run filtering is not allowed

The mechanistic dependent variable is the final causal algorithm. The failed behavioral transition is itself an optimization-basin event that may be correlated with that causal algorithm.

Selecting only seeds that retained the task would therefore condition on a post-treatment variable upstream of the mechanistic measurement. The surviving B runs, for example, could be precisely the runs that entered a particular internal algorithmic basin.

This selection bias cannot be repaired after the fact by shuffled interventions, more DAS controls, more seeds, or a second localization method.

---

## 6. Final decision

The lineage is closed.

Do not continue by:

- another J-space variant;
- another causal-localization instrument;
- a third procedure pair on the same endpoint;
- additional seed filtering;
- further LR/curriculum rescue after seeing this gate;
- a renamed latent-deliberation / algorithm-migration / automaticity framing built on the same dependency.

The broader area may only be revisited as a genuinely new candidate if a **stable fully-internalized substrate already exists independently of the hypothesis**, and the new scientific question passes a fresh owner/novelty audit before mechanistic experiments are designed.

---

## 7. Durable methodological lessons

1. **Validate the instrument before training a trajectory.** L44 saved substantial compute by failing the J-space construct gate early.
2. **Validate the endpoint before interpreting its mechanism.** L45 saved a misleading DAS result by requiring multi-seed behavioral stability first.
3. **Do not condition mechanistic inference on treatment-dependent survival.** A competence gate can reveal survivor bias rather than merely filter noisy models.
4. **A stronger instrument does not create a new scientific question.** The reconstruction route was still too close to existing owners until the procedural-history question was independently formulated.
5. **Repeated rescue pressure is itself evidence.** When a lineage repeatedly requires new instruments, new task constructions and new training repairs before any primary scientific quantity exists, stop rather than manufacture a favorable laboratory.

**Archive verdict:** substantial work was useful as negative evidence about feasibility and experimental design, but there is no surviving L44/L45 Main candidate.