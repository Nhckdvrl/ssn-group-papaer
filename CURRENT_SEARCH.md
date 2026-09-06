# Current Research-Question Search — 2026-09-06 Active Search

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Pilot-authorized candidates in `good/`:** 1 — L02  
**Current target:** find additional five-gate candidates without lowering the bar.

> Latest terminal audit:
>
> - K076 — answer correctness vs completeness: **KILL**
> - K077 — event mention vs instance cardinality: **KILL**
> - K078 — reported proposition vs speaker commitment: **KILL**
> - K079 — lexical trigger vs semantic event: **KILL**
> - **A-level live leads: 0**
>
> The event-cardinality and light-verb leads both reached unusually strong data/representation grounding, but parent-level novelty still failed. They must not be resurrected merely with cleaner data or newer LLMs.

---

# What the latest batch taught us

## 1. A natural old distinction is not enough

Several mature NLP formalisms already contain distinctions that modern systems sometimes ignore. That does **not** create a new parent by itself.

The key novelty test remains:

> Has prior work already made the consequences of ignoring that distinction the scientific question?

For event cardinality, Gantt et al. 2023 already did so through event individuation.  
For trigger/event mismatch, trigger-sharing and co-referent-trigger work already did so.

## 2. Cleaner gold cannot rescue occupied parent novelty

TimeBank + AQUAINT provided 103 naturally annotated event-cardinality instances. That was excellent data, but the scientific parent was already owned.

## 3. Search next outside the saturated event/coreference/commitment neighborhoods

Immediate next search should prioritize mature NLP objects where a hidden distinction may still be load-bearing in generative modeling:

- semantic equivalence / paraphrase versus entailment direction;
- answer/evidence licensing beyond generic answerability;
- document-level scope and attribution outside generic commitment;
- semantic parsing outputs where canonicalization may erase distinctions;
- information status / recoverability in generation;
- reference and entity status not reducible to coreference or NIL linking;
- evaluation units in established generation tasks where modern free-form outputs changed the old assumption.

---

# A-level strong live leads

## None at this checkpoint

No candidate is kept alive merely to maintain momentum.

---

# Search discipline

For every new lead:

1. state the natural object and plain-language example;
2. write two plausible accounts before searching for effects;
3. identify exact natural data and independent gold;
4. search the classical parent plus 2024–2026 ACL/EMNLP/NAACL and neighboring venues;
5. attack with “This is just ____”;
6. promote only if all five gates are clearly YES.

> **No GPU until all five gates are YES.**
