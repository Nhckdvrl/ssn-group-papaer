# Current Research-Question Search — 2026-09-07 Active Search

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Pilot-authorized candidates in `good/`:** 1 — L02  
**Current target:** find additional five-gate candidates without lowering the bar.

> Latest terminal audit:
>
> - K080 — textually expressed relation vs contextually inferable relation: **KILL**
> - K081 — quantity mention vs exact scalar value: **KILL**
> - K082 — predicate sense state vs semantic role recovery: **KILL**
> - K083 — entity mention vs discourse entity / entity reification: **KILL**
> - K084 — OCR / physical order vs human reading order: **KILL**
> - **A-level live leads: 0**
> - **B-level live leads: 0**

---

# Stronger search rule learned on 2026-09-07

A mature old distinction is not enough, and even a plausible “old state vs generative output” story is not enough.

For a candidate to look like L02, require:

> **Old annotation/state → modern generation action has a natural, externally grounded correct/incorrect mapping.**

Examples:

- L02 works because DNI vs INI naturally maps to **generate a concrete filler vs abstain from concrete entity commitment**.
- K083 failed because referential/non-referential labels do **not** naturally map to **make a KG node vs do not make a KG node**; typed concept nodes are a legitimate alternative representation.
- K084 failed because explicit reading order already has a direct modern downstream intervention in EACL 2026.

This additional rule should be checked before deep novelty work.

---

# Immediate search program

Search outside the saturated event/coreference/NER/SRL neighborhoods.

Priority mature objects:

1. **Semantic parsing / meaning representation**
   - only distinctions with an unambiguous downstream/output action;
   - avoid generic AMR parsing, reentrancy/coreference, polarity/factuality, and sense inventory revisits.

2. **Machine translation / multilingual generation**
   - look for source distinctions that force a concrete target-side generation decision;
   - avoid generic hallucination, adequacy/fluency, gender-bias, and document-context variants unless a genuinely new parent emerges.

3. **Natural language generation / reference**
   - investigate old discourse-state variables only if modern free generation creates a natural action-level test;
   - immediately kill if reducible to existing REG/common-ground/reference-production work.

4. **Speech/transcript normalization**
   - only if an old annotation distinction changes what a modern generative transcript should preserve/remove and has independent gold;
   - avoid generic disfluency removal/correction, which is already active through ACL 2026.

5. **Evaluation-unit rewrites**
   - only where separating two pre-existing quantities changes a model/task conclusion, not merely metric granularity.

---

# Search discipline

For every serious lead:

1. state the natural object and plain-language example;
2. state the **modern action mapping** implied by the old gold;
3. write Account A and Account B before looking for an effect;
4. identify exact natural data and independent gold;
5. search the classical parent plus 2024–2026 ACL/EMNLP/NAACL and neighboring venues;
6. attack with “This is just ____”;
7. promote only if all five gates are clearly YES.

> **No GPU until all five gates are YES.**
