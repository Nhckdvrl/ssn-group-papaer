# L03 — Minimum Decisive Pilot Card

This file is a compact pilot entry point. The authoritative detailed plan remains `RESEARCH_PLAN.md`.

## Pilot question

> Can models recover provider-defined observation states from real statistical tables and local documentation, and is explicit status typing still necessary?

## 1. Data

Use two providers:
- U.S. Census ACS estimate/annotation pairs;
- Eurostat/SDMX observation values + status flags.

Build a balanced pilot containing:
- ordinary numeric values;
- true zeros;
- provider-defined non-values;
- qualified observations such as estimated/provisional/low-reliability/suppressed where direct provider gold exists.

## 2. Conditions

For the same natural observation:
1. direct table/document-conditioned generation;
2. explicit status→value factorization;
3. documentation absent;
4. documentation present;
5. familiar-provider convention;
6. held-out / cross-provider convention.

## 3. Primary metrics

- observation-status accuracy / macro-F1;
- false scalarization rate;
- false generic-missingness rate;
- value accuracy conditional on status=VALUE;
- direct vs explicit-typing delta;
- cross-provider transfer;
- documentation gain.

## 4. Outcome branches

### A — Direct generation ≈ explicit typing across providers
Explicit provider-specific parsers may be dispensable; modern models can reconstruct observation semantics from documentation.

### B — Explicit typing clearly wins
Provider-defined observation status remains a load-bearing representation for real TableQA.

### C — Conditional boundary
Some states/providers transfer while suppression/reliability/unseen conventions fail. Build a decision map for when explicit typing is required.

### D — Census-only/code-memorization result
KILL/demote if cross-provider evidence does not support a general observation-state conclusion.

## 5. Main-level condition

The paper must change how real statistical TableQA represents or evaluates answers. A benchmark of sentinel-code decoding or generic missing values is insufficient.