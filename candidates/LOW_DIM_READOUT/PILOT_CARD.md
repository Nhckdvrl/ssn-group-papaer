# Low-Dimensional Readout — Minimum Decisive Pilot

## Pilot question

> Does reasoning collapse under readout truncation because each next step needs richer information, or because small per-step errors compound autoregressively?

## 1. Minimal design

Use two open models and three task families:
- MMLU-like knowledge;
- SQuAD-like QA;
- GSM8K + one second reasoning set.

For every task run:
- FULL readout;
- 50% random-coordinate truncation;
- several masks/seeds.

Then on reasoning cases run the decisive intervention:
- FREE generation under truncation;
- TEACHER-FORCED generation under the same truncation.

## 2. Decisive predictions

### Accumulation account
- teacher-forced gold next-token probabilities remain close to full;
- free trajectories diverge early and errors compound;
- restoring full readout after one bad step can recover only when context has not diverged too far;
- long non-reasoning generations show similar length sensitivity.

### Intrinsic reasoning-readout account
- teacher-forced next-step prediction is already strongly damaged;
- short reasoning steps can be fragile despite little generation history;
- long non-reasoning controls remain robust.

### Geometry account
- random projection / learned low-rank projection differs sharply from simple coordinate deletion at matched dimension.

## 3. Minimum sample

~200–500 examples per task are enough for the first causal diagnostic if compute allows; use matched difficulty subsets and bootstrap CIs.

Do not expand model count before the teacher-forcing comparison is clear.

## 4. Secondary interventions

If pilot survives:
- truncate only reasoning tokens;
- truncate only answer tokens;
- truncate at one chosen step then restore;
- compare base/instruct/reasoning-tuned checkpoints;
- select degrading vs improving dimensions from parent methodology;
- test projection dimensionality continuously rather than only 50%.

## 5. Promotion branches

### A — Teacher forcing largely rescues
Promote as **autoregressive amplification masquerading as representation fragility**.

### B — Teacher forcing does not rescue
Promote as **reasoning-specific readout capacity/geometry requirement**.

### C — Strong task/model boundary
Promote if boundary is stable and mechanistically explained.

### D — Pure sequence-length effect
Potential kill unless this itself overturns the original interpretation in a broad, convincing way.

### E — Weak/no reproducible contrast
KILL.

## 6. Main-level requirement

A Main paper must end with a conclusion larger than “GSM8K is sensitive.” It should tell NLP researchers what a low-dimensional representation intervention does and does not reveal about model capability.