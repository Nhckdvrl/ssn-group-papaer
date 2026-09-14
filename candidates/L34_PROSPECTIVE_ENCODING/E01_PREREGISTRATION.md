# L34 E01 — Preregistration

**Date frozen:** 2026-09-14
**Authorization:** `SELECTION.md` §11 — *PILOT-AUTHORIZED — E01 ONLY*
**Compute:** local `verl-clean` env; idle A100-80GB on `fvcrc10/12/13/15`; **at most 8 cards at a time** (user override 2026-09-14 of the earlier 4-card cap).

---

## 1. Question this experiment resolves

Does an access policy learned **before** a fact is encountered selectively change how that fact is
subsequently written into parameters — or is the PIT gain generic plasticity (B) or retrieval-policy
specialization (C)?

## 2. Substrate

Programmatically generated bioS-style biographies (`src/bios.py`), fixed generator seed.
Six independent attributes, partitioned into two mirrored query families:

| family | attributes |
|---|---|
| **A** | `birth_date`, `university`, `work_city` |
| **B** | `birth_city`, `company`, `major` |

The partition is **fixed before any run**. Family main effects cancel exactly in the primary
estimand (a triple difference), so the partition need not be difficulty-matched.
`birth_city` and `work_city` draw from **disjoint** city pools so that "answer with a city" cannot
transfer across families.

Person sets are disjoint: `FORMAT` (format grounding), `OLD`, `PIT`, `NEW`.

## 3. Frozen training order

```
Phase 0a  FORMAT bios + balanced FORMAT QA        (shared trunk)
Phase 0b  OLD bios                                (shared trunk)   <- OLD facts encoded here
Phase 1   access curriculum, ARM-SPECIFIC QA on PIT persons        <- the manipulation
Phase 2   NEW bios                                (identical across arms)  <- NEW facts encoded here
```

- Phase 1 QA is about `PIT` persons whose biographies are **never shown**: it teaches an access
  policy, not facts. This mirrors PIT's "QA before the document".
- Phase 2 data, order, and optimizer schedule are **byte-identical across arms** at a given seed.
- **No post-document instruction tuning** before the primary evaluation (`SELECTION.md` §5.6).

## 4. Arms

| arm | Phase 1 content | role |
|---|---|---|
| `PIT_A` | 3 family-A attributes × PIT persons | causal arm |
| `PIT_B` | 3 family-B attributes × PIT persons | mirrored causal arm |
| `PIT_BAL` | half persons A-only, half B-only | balanced control |
| `NO_PIT` | Phase 1 skipped | mother-effect reference (budget **not** matched; declared) |

`PIT_A` and `PIT_B` are exactly matched in person count, QA count, token count, and optimizer budget.
Seeds: 3 per arm (vary Phase-1/Phase-2 data order and dataloader RNG). Trunk is shared across all
arms and seeds — declared limitation: seed variance covers Phase 1/2 only.

## 5. Primary measurement

Fixed QA prompt; **per-token NLL of the gold answer** (`SELECTION.md` §7, and the L32 lesson that
generation EM carries termination/output-processing confounds). No generation is used anywhere in
the primary path.

Secondary (pre-declared, non-decisive):
- forced-choice rank of the gold value against 15 distractors drawn from the same attribute pool
  (accuracy@1, MRR) — no decoding, no string extraction;
- held-out paraphrase templates (2 per attribute, never trained) for the same two measures.

Let `S(arm, age, family)` = mean over persons × attributes of `-NLL_per_token`.

```
PREF(arm, age)   = S(arm, age, A) - S(arm, age, B)
CROSSOVER(age)   = PREF(PIT_A, age) - PREF(PIT_B, age)
PROSPECTIVE      = CROSSOVER(NEW) - CROSSOVER(OLD)      <- PRIMARY ESTIMAND
```

Independent unit: **person**. CIs: BCa bootstrap over persons (10k resamples), nested with seed
averaging; seed-level replication reported separately.

## 6. Gates (frozen before any run)

- **G0 — mother / instrument gate.** `NO_PIT` vs `PIT_BAL` on NEW facts must show a material
  PIT-style advantage in gold-answer NLL. If the parent phenomenon is absent in this instrument,
  E01 fails at the instrument level → escalate model scale **once** (3B → 7B/8B, declared here, not
  model shopping), then STOP.
- **G1 — first-stage access specialization.** Measured on **OLD** facts at the post-Phase-1
  checkpoint: `CROSSOVER_post-phase1(OLD) > 0` with bootstrap CI excluding 0, i.e. `PIT_A` and
  `PIT_B` move the A−B preference in **opposite** directions. If the manipulation cannot produce
  mirrored specialization on knowledge the model already has, the access curriculum has no leverage
  → **STOP**, do not interpret the NEW phase.
- **G2 — primary prospective gate.** `PROSPECTIVE > 0`, mirror-consistent (both arms contribute in
  their predicted directions, not one arm alone), person-bootstrap CI excluding 0, and
  **≥ 0.02 nats/token** in magnitude. A 1–2 % relative wiggle is not a result.
- **G3 — construct gate.** The crossover must survive on held-out paraphrase templates. If only the
  trained template shows it, this is template memorization → **STOP**, no prompt search.

## 7. Outcome → account map (frozen)

| observation | conclusion |
|---|---|
| G1 passes, `PROSPECTIVE > 0` and material, OLD crossover small | **Account A — prospective encoding** |
| G1 passes, CROSSOVER(NEW) ≈ CROSSOVER(OLD), `PROSPECTIVE ≈ 0` | **Account C — retrieval-policy specialization**; strong claim rejected |
| G0 passes, no family crossover anywhere, NEW overall improves | **Account B — generic plasticity**; selective claim rejected |
| G1 fails | instrument failure → STOP |
| crossover only on trained templates | construct failure → STOP |

A null is allowed to kill L34. No post-hoc conversion into a knowledge-injection method paper.

## 8. Anchor and escalation

Pilot anchor: **Qwen2.5-3B (base)**, full fine-tuning, bf16, gradient checkpointing, one A100-80GB
per run (12 runs = 4 arms × 3 seeds, plus one shared trunk). Escalation to a 7B/8B base is
authorized **only** by a G0 failure, exactly once, and must repeat the identical protocol.

## 9. What is not authorized

Model zoo, domain sweeps, RAG, prompt/template search after seeing the sign, real-world knowledge
corpora, mechanistic probing, or a PIT-improvement method paper.
