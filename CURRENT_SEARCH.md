# Current Research State — 2026-09-11

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Active serious candidates:** **L14 only**  
**Current phase:** **BROAD SEARCH OPEN + L14 PRE-PILOT AUDIT**

---

## Portfolio reset

The previous active portfolio has been archived. Existing code, data, and results are preserved for reproducibility, but none carries current experiment authorization.

Archived in this reset:

- **L03 — Table Value ≠ Observation Status**
- **L06 — Study Identity Is Not Document Identity**
- **L07 — Official Correction ≠ Current Scholarly Claim**
- **L08 — Readout-Dimension / Compression Evaluation**
- **L09 — RLVR Disagreement: Erased or Suppressed?**
- **L10 — From Failure to Action**
- **L12 — Reasoning-Induced Invariance / Trajectory Takeover**
- **L13 — Temporal Order ≠ Event Realization**

L02, L04, and L11 were already historical / killed routes.

### Why reset rather than rescue

The decisive lesson from L12/L13 and the fresh portfolio audit is:

> **A topic is not selected once. We continuously select the paper we are actually writing.**

A materially changed RQ, estimand, explanation, central claim, or reviewer takeaway is a new candidate. Existing evidence may be inherited; old authorization and old novelty approval may not.

Good data, strong effects, clean interventions, and a natural question are individually insufficient if the strongest successful result is still reviewer-compressible to existing work or cannot develop into an independently valuable Main-level inference.

---

# Current serious candidate — L14

## Negation of the World, or Negation of the Words?

Canonical package: `candidates/L14_METALINGUISTIC_NEGATION/`

Plain example:

> **The movie wasn't good — it was excellent.**

The speaker does not deny that the movie reached the weaker state *good*; the speaker rejects *good* as an inadequate description and replaces it with the stronger *excellent*.

Contrast:

> **The movie wasn't good — it was terrible.**

Here `not` genuinely negates the world-state proposition.

### RQ

> **Does an LLM identify the semantic level targeted by `not` — world proposition versus linguistic representation — before applying polarity, or does it default to propositional negation and repair only when context forces reinterpretation?**

### Why it is currently serious

- classical, immediately understandable phenomenon;
- simple controlled data plus existing human psycholinguistic materials;
- current LLM negation work largely treats polarity sensitivity as monotonically desirable;
- exact searches did not find a modern LLM paper owning metalinguistic-negation target selection;
- prospective development is fixed in advance: **target selection → default-repair vs context-sensitive processing → consequence for negation-robustness interventions**;
- a particularly strong consequence is a trade-off where methods that reduce ordinary negation blindness worsen metalinguistic over-negation.

### Current status

**SERIOUS CANDIDATE / PRE-PILOT.** Not mainline-approved and not authorized for broad experiments. First verify the controlled English stimulus contract and run one bounded kill-oriented pilot only if the final data/novelty audit remains clean.

---

# Search objective

The preferred new topic style is the one exemplified by strong classic-problem modernizations:

> **durable and immediately understandable problem → simple natural/controlled data with hard gold → genuinely unresolved LLM-era question → interesting decisive experiment → broader consequence for actual NLP/LLM behavior.**

The ideal question should be understandable from one example, but should not reduce to “does the model know a textbook linguistic distinction?”

Classic parents are assets, not novelty failures. The novelty burden is on the **modern scientific question, inference, and development path**.

The user currently prefers this style over TableQA / statistical-table work.

---

# Pre-pilot requirement for every new serious candidate

Before any compute authorization, record:

1. **One-sentence RQ + plain example.**
2. **Strongest plausible successful result:** what exactly would readers learn?
3. **Prospective paper identity:** what would the paper be after the first result, not just before it?
4. **Ownership:** strongest current `Prior A + B + C = our paper` compression and the surviving independent contribution.
5. **Development-path novelty:** audit the most likely next claim(s), so a positive/negative pilot cannot silently drift into already-owned territory.
6. **Data/gold/identification:** natural or minimally controlled substrate with truth independent of the evaluated model.
7. **Main-level progression:** how the paper deepens beyond its first effect without generic probe/patch/model-zoo padding.
8. **Stop condition:** what result or ownership fact kills the route rather than triggering automatic rescue.

A pilot is authorized only when the candidate is paper-shaped enough that the expected next development remains worth testing.

---

# Durable workflow rule

Search, selection, and execution form a loop:

`SEARCH → SELECT → PILOT → RE-SELECT CURRENT PAPER IDENTITY → DEVELOP → RE-SELECT → PAPER / ARCHIVE`

Claim mutation requires return to selection, not merely a wording update to related work.

**Evidence survives claim mutation; authorization does not.**
