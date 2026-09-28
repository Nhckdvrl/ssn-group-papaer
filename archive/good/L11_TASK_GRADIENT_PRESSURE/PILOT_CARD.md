# L11 — Minimum Decisive Pilot Card

**Status:** PILOT-AUTHORIZED  
**Purpose:** resolve the cheapest load-bearing uncertainty, not miniaturize the whole paper.

> This card is a starting point. The execution agent may choose an equivalent or better experiment if it answers the same scientific uncertainty more decisively.

---

## Pilot question

> In one reproducible high-gradient/low-gradient task contrast, does the difference come mainly from individual score sensitivity, from aggregation/coherence, or from a large mismatch between raw parameter movement and actual policy movement?

---

## Minimal setup

- one open model close to the parent setup;
- one high-contrast task pair;
- objective verifier/reward;
- limited number of checkpoints/steps;
- enough rollout-level information to decompose the aggregate gradient.

A same-domain Arithmetic/MATH-style pair is preferred if reproducible, but not mandatory.

---

## Minimum outputs

At least recover:
- task gradient norm ordering;
- local learning-gain ordering;
- reward/advantage/length controls;
- one or more decomposition quantities that can separate plausible accounts.

If feasible, add:
- local policy KL or another function-space movement measurement.

---

## Informative branches

### A — Per-example sensitivity dominates
Follow output/token representation and probability geometry.

### B — Aggregation/coherence dominates
Follow token/example directional structure and design a within-task causal manipulation.

### C — Raw parameter loudness collapses in function space
Reframe toward cross-task pressure measurement.

### D — Mixed mechanism
Find a clean boundary or diagnostic map.

### E — Another explanation appears
Reconstruct around it if it is stronger and identifiable.

No branch is privileged in advance.

---

## Pilot kill conditions

Kill/demote only if:
- the parent anomaly cannot be reproduced;
- the discrepancy becomes trivial after one known confound;
- measurements are too unstable to support mechanism claims;
- the remaining story is merely “another gradient-balancing method.”

Do **not** kill because the initially preferred account loses.

---

## Promotion criterion

After the pilot, keep/promote only if there is a believable route to:

> **new scientific explanation or measurement principle  
> + decisive evidence  
> + consequence for multi-task LLM post-training  
> + paper identity comparable to strong ACL/EMNLP/NAACL Main work.**
