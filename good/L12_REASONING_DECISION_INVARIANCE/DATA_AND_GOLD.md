# L12 — Data, Evidence, and Identification

**Core principle:** the parent already supplies the behavioral phenomenon. Our evidence must identify *why* reasoning training changes sensitivity to framing/presentation.

The exact mechanistic tool is open. The evidence standard is not.

---

## 1. Primary behavioral substrate

Use matched risky-decision materials from:

ACL 2026 Outstanding Paper  
**“Mind the (DH) Gap!”**  
https://aclanthology.org/2026.acl-long.479/

Useful controlled axes include:
- gain vs loss framing;
- description vs experience/history;
- option order;
- explanation manipulations;
- equivalent underlying prospects.

Do not create a huge new benchmark unless the mechanism requires a narrowly targeted extension.

---

## 2. Core unit of analysis

The natural unit is a **matched decision set**:

> same underlying choice structure  
> + controlled change in representation/interface  
> → compare behavior and internal computation.

Record:
- exact underlying probabilities/payoffs;
- surface condition;
- option order;
- reasoning/no-reasoning mode;
- model/checkpoint;
- generated rationale if any;
- final choice;
- probability/logit/log-prob signal where available;
- internal states required by the chosen mechanism method.

---

## 3. Preferred model substrate

A shared-base matched-branch design is strongly preferred over unrelated model comparisons.

A currently verified OLMo 3 design is:
- common base: `allenai/Olmo-3-7B`;
- instruct SFT branch: `allenai/Olmo-3-7B-Instruct-SFT`;
- reasoning SFT branch: `allenai/Olmo-3-7B-Think-SFT`;
- optional later DPO/final checkpoints within each branch.

Official model cards list the same `Olmo-3-7B` base for the Instruct and Think SFT branches.

The correct scientific comparison is **not** to pretend that Instruct-SFT was trained into Think-SFT. Prefer:
> base→Instruct change vs base→Think change,

and then use within-branch later stages only if they sharpen the mechanism.

The exact checkpoint family may change if a cleaner public matched design becomes available.

---

## 4. Identification targets

### Canonicalization claim
Evidence should show more than behavioral invariance.

Possible evidence:
- cross-frame task-relevant representations become more similar;
- framing identity becomes less causally influential;
- patching a frame-specific state no longer shifts choice;
- a shared decision variable emerges across conditions.

### Policy-override claim
Possible evidence:
- frame identity remains decodable/causally recoverable;
- decision behavior becomes invariant anyway;
- manipulating a late choice-related signal restores or changes frame sensitivity.

### Deliberation claim
Possible evidence:
- invariance depends on reasoning mode or generated computation;
- no-think/direct modes retain stronger framing effects;
- causal intervention on reasoning states changes the invariance.

### Boundary claim
Possible evidence:
- arithmetic-transparent decisions show invariance;
- structurally matched but less directly arithmeticizable decisions do not.

No single implementation is mandatory.

---

## 5. Critical distinction: decodability ≠ causal use

A linear probe that can decode:
> “gain frame” vs “loss frame”

does not prove the model uses that information for choice.

Likewise, weak decodability does not prove the information is absent.

A Main-level mechanism paper should, when feasible, combine:
- representation evidence;
- behavioral evidence;
- a causal or intervention-based test.

Probe-only work is below the intended paper identity.

---

## 6. Natural controls

Recommended controls include:
- direct answer vs reasoning mode;
- matched choice with surface-only change;
- option/order controls;
- equivalent payoff/probability structure;
- non-decision arithmetic controls where useful;
- checkpoints before/after the suspected training transition.

Use only controls that sharpen the scientific distinction.

---

## 7. Boundary-data extensions

If the initial mechanism is clear, a small targeted extension can test whether the effect generalizes beyond easy expected-value arithmetic.

Good extensions preserve:
- uncertainty;
- equivalent underlying decision structure;
- controlled presentation changes.

Avoid drifting into a generic cognitive-bias benchmark.

---

## 8. Evidence risks

Watch for:
- output-format differences masquerading as mechanism;
- reasoning-length differences;
- different answer tokenization;
- probe leakage;
- unrelated model-family confounds;
- prompt wording artifacts;
- generated-CoT faithfulness assumptions;
- interpreting activation similarity as semantic equivalence without intervention.

---

## 9. Data / identification kill conditions

Kill/reconstruct if:
- the parent behavioral effect does not reproduce in any usable same-family checkpoint comparison;
- the branch/stage comparison changes too many factors to support the claim;
- internal measurements cannot distinguish representation from policy use;
- the entire result reduces to output-format or prompt artifacts;
- only a generic “reasoning models are less biased” result remains.

A preferred mechanism losing is **not** a kill condition.
