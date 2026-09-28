# L13 Parent Audit — Why this is not a resurrection

Date: 2026-09-11. Re-check literature before any promotion.

The killed ledger contains three neighbours that must be cleared explicitly.

## K064 — Event Mention ≠ Event Occurrence (KILL, NOVELTY_PARENT_COLLISION)

**Killed because:** event factuality / modality / negation are established labelling
tasks; MAVEN-FACT already benchmarks LLMs on event factuality. Reviewer compression:
"event factuality for LLM event extraction."
**Reopen condition recorded in the ledger:** *a new structural relation goes beyond
factuality/modality labels and changes the task definition itself.*

**How L13 satisfies it.** L13 does not propose to measure, improve, or benchmark
factuality labelling. Its estimand is a **relation between two computations**:

> does computing a temporal relation `R(E1, E2)` change the model's realization
> commitment on `E2`?

The load-bearing evidence is a **manipulation**, not a label distribution:
(a) the temporal connective is varied with everything else held constant, and
(b) the task is varied so that timeline construction is or is not forced before the
same realization probe. Factuality is the *readout*, not the object. A factuality
benchmark cannot answer this question because it never varies the temporal
construction or the timeline-construction demand while holding the proposition fixed.

**Residual risk:** a reviewer may still compress L13 to "factuality with before/after."
The defence is the coupling/intervention structure and the timeline-order manipulation;
if the pilot shows no coupling and no asymmetry, that defence weakens and L13 must be
re-audited rather than rewritten as a benchmark.

## K068 — Relative Temporal Relation ≠ Absolute Calendar Commitment (KILL)

Killed because TReMu owns temporal anchoring / normalization / unanswerability. L13
never asks for an absolute time and never asks whether a time is recoverable. Its
open state is about **whether an event exists at all**, not about which timestamp it
carries. Different scientific quantity — the ledger's reopen condition is met.

## K069 / K077 / K078 (event identity, individuation, speaker commitment)

- **K069 / K077** own *how many* events and *which are the same* event. L13 fixes the
  event and asks whether it is realized.
- **K078** owns source-relative / speaker commitment under reported speech. L13's
  non-veridicality comes from a temporal connective in the narrator's own assertion,
  with no embedding predicate and no attribution.

## Rule for this package

If the pilot forces the claim to shrink into "a cleaner factuality test set", that is a
K064 resurrection and the correct action is KILL, not a rename.
