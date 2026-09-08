# L02 — Research Plan and Development Roadmap

> **Final route decision, 2026-09-08: NO-GO for the current Main-paper design.**
> E000–E000c, E001a and E001b completed. Read [the verdict](RESEARCH_VERDICT.md)
> and [support contract](data/SUPPORT_CONTRACT.md) before any further study.
> The roadmap below is a superseded proposal, not an executable protocol.

> **2026-09-08 amendment:** E000 ran on the recovered training release. Interpretation
> and context-supported filling cannot be collapsed into the old DNI/INI-to-action mapping.
> See [results](experiments/E000_data_audit/RESULTS.md) and
> [E001 draft](experiments/E001_pilot/PROTOCOL_DRAFT.md). The inherited roadmap below
> is not an executable protocol. Do not run blanket INI-as-overcommitment scoring.

**Goal:** turn a promising distinction into a decisive NAACL Main-level paper about whether referential-status factorization remains load-bearing in generative implicit-argument extraction.

---

## Phase 0 — Reproducibility and data contract

1. Obtain and parse SemEval-2010 Task 10 data.
2. Reproduce published DNI/INI/filler-link counts.
3. Export a deterministic target table with status and filler gold.
4. Manually audit only the parser, not the labels.
5. Freeze the mapping before target-model experiments.

**Exit condition:** every evaluated item has unambiguous externally determined gold.

---

## Phase 1 — Minimum decisive pilot

Use a modest stratified sample, not FrameNet-wide engineering.

### Conditions

1. **Direct free-form generation**
2. **Structured direct output** with SPECIFIC_REFERENT or NON_SPECIFIC
3. **Explicit two-stage factorization**
   - status first;
   - filler only if specific.
4. **Independent role/type probe**

### Model set

Use a small but heterogeneous current set:
- at least one strong open model;
- at least one strong closed/general model if available;
- optionally a conventional implicit-argument baseline for historical anchoring.

Do not turn model breadth into the paper.

### Primary estimands

- non-specific overcommitment;
- referential-status accuracy;
- filler accuracy on specific cases;
- role understanding conditional on referential error;
- effect of output factorization: direct vs explicit status→filler.

---

## Phase 2 — Decide whether the paper exists

### Promote signal A — factorization remains load-bearing

Evidence pattern:
- role/type knowledge remains good;
- direct generation overcommits on non-specific omissions;
- explicit status→filler factorization reduces unsupported entity commitment without simply degrading recall.

Paper conclusion:
> free-form generative IE confuses semantic completion with grounded entity recovery; referential status remains a necessary state.

### Promote signal B — factorization is safely removable

Evidence pattern:
- strong models preserve referential status;
- direct generation matches factorized systems;
- no meaningful cost appears on specific filler recovery;
- result replicates beyond a tiny subset.

Paper conclusion:
> a classical explicit pipeline distinction has become unnecessary under identified modern conditions.

### Promote signal C — principled boundary

Evidence pattern:
- direct generation is safe only under specific discourse/evidence conditions;
- boundary can be predicted from natural variables such as distance/salience/frame class.

Paper conclusion:
> factorization is conditionally load-bearing, yielding a decision rule for when generative IE needs explicit referential typing.

### Kill

KILL if:
- near ceiling everywhere with no modeling consequence and no informative boundary;
- differences are tiny/noisy/model-idiosyncratic;
- only one weak model exhibits overcommitment;
- the story collapses to DNI/INI classification;
- new literature owns the same paper-level story.

---

## Phase 3 — C1: establish the scientific relation

Run the full test on the verified dataset.

Report:
- direct vs factorized systems;
- specific vs non-specific cases;
- filler and status separately;
- uncertainty intervals and paired significance/equivalence tests;
- pre-specified effect sizes.

For preservation claims, use equivalence or non-inferiority framing rather than “p > .05”.

---

## Phase 4 — C2: explain why / where

Priority analyses:

1. **Role knowledge vs commitment**
   - does the model know the participant type but still invent an entity?
2. **Discourse evidence**
   - distance to gold filler;
   - explicit antecedent strength.
3. **Distractor salience**
   - does a salient compatible entity trigger false commitment?
4. **Frame/predicate class**
   - which semantic environments preserve or break the distinction?
5. **Prompt/output intervention**
   - direct answer vs typed status→filler;
   - concise abstention versus natural-language explanation.

Avoid speculative mechanistic analysis unless it is needed to explain a robust behavioral boundary.

---

## Phase 5 — C3: consequence for generative IE

The paper should end with a substantive task/evaluation consequence.

Possible deliverables:
- a typed output contract for generative implicit-argument extraction;
- an evaluation protocol that does not reward unsupported specificity;
- evidence that explicit status modeling is unnecessary under certain regimes;
- a boundary-aware formulation deciding when direct generation is safe.

The contribution is strongest if it changes an established modeling/evaluation assumption rather than merely adding another score.

---

## Phase 6 — Replication and generality

Only after the core result survives:

1. verify FrameNet extraction;
2. replicate on a larger or different domain;
3. test whether the same conclusion holds across current model families;
4. test whether it generalizes to one closely related grounded IE setting only if that extension is scientifically natural.

Do not pad the paper with unrelated tasks.

---

## Paper skeleton

### Introduction
- natural omitted-role problem;
- modern free-form generation changes the old factorization assumption;
- two plausible accounts;
- decisive question.

### Section 2 — Background and ownership
- null instantiation;
- classical task decomposition;
- modern document/generative argument extraction;
- precise novelty boundary.

### Section 3 — Data and estimand
- external gold;
- direct vs factorized output;
- role/status/filler decomposition.

### Section 4 — C1
- is the boundary preserved?

### Section 5 — C2
- why / where does preservation or failure occur?

### Section 6 — C3
- what should generative IE model/evaluate?

### Section 7 — Robustness / replication

---

## Promotion checklist to paper mainline

Do **not** approve mainline until all are true:

- [ ] exact data/gold pipeline reproduced;
- [ ] result is stable across more than one serious model;
- [ ] Account A, B, or boundary conclusion is clearly supported;
- [ ] effect is not just generic hallucination;
- [ ] explicit factorization comparison is decisive;
- [ ] paper-level novelty re-audit still survives;
- [ ] C3 changes a real modeling/evaluation conclusion;
- [ ] reviewer compression cannot reduce the paper to “DNI/INI with LLMs.”
