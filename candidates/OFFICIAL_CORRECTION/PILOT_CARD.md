# Official Correction — Minimum Decisive Pilot

## Pilot goal

Determine whether a model presented with an original scholarly statement and its official correction recovers the current proposition, and identify whether failures come from retrieval/salience or update reasoning.

## 1. Stage 0 — data audit first

Before GPU:
- sample >=300 linked correction notices;
- compute Tier A/B/C/D yield;
- verify at least two semantic correction types have enough cases;
- manually audit 50 extracted old→new pairs.

If proposition-level gold yield is inadequate, KILL before model experiments.

## 2. Pilot set

Target 100–200 Tier A/B correction instances, balanced where possible across:
- numeric/table corrections;
- textual factual corrections;
- method/qualifier corrections;
- at least two journal/publisher templates.

Use metadata-only corrections as negative controls, not positive semantic examples.

## 3. Conditions

For each instance:
1. ORIGINAL ONLY;
2. CORRECTION ONLY;
3. ORIGINAL + CORRECTION;
4. CORRECTION + ORIGINAL (order reversal);
5. BOTH + explicit update relation;
6. BOTH + matched newer-but-not-corrective distractor.

Optional retrieval condition embeds the pair among unrelated papers.

## 4. Models

Two strong open models from different families are sufficient for the decisive pilot. Add closed models only after the data/estimand survives.

## 5. Outputs

Structured output:
- current proposition/value;
- which source controls the answer;
- whether the original proposition remains valid;
- optional short rationale.

Primary scoring must use proposition/value correctness, not rationale quality.

## 6. Primary comparisons

### Update preservation
BOTH vs gold corrected proposition.

### Original dominance
Does adding the original article reduce correction-only correctness?

### Relation necessity
Explicit update link vs unlabeled pair.

### Recency control
Official correction vs merely newer contradictory text.

## 7. Outcome branches

### A — Models reliably respect corrections
Paper becomes a preservation/equivalence result: explicit version-state machinery may be dispensable when correction relations are accessible.

Must show robustness across publisher templates and nontrivial textual corrections.

### B — Original dominates despite correction
Promote strongly if retrieval is correct but the model still returns superseded content. This supports explicit update-state representation.

### C — Boundary by correction type
Promote if numeric replacements work but distributed/methodological corrections fail, or if explicit relation metadata removes the gap. This yields a decision map.

### D — Task trivial by cue/date
KILL if simple recency or lexical markers solve essentially everything and no meaningful scholarly-update question remains.

## 8. Promotion criteria

Promote only if:
- data gold is direct;
- failure/success is not reducible to date sorting;
- at least one nontrivial correction category exists at scale;
- the result changes a scientific NLP design/evaluation conclusion.

A correction-notice classification benchmark alone is not enough.