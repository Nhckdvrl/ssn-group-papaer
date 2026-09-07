# Current Research-Question Search — 2026-09-07 Active Search

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Pilot-authorized candidates in `good/`:** **3 — L02, L03, L04**  
**Authoritative killed ledger on disk:** through **K157**  
**Next ledger kill ID:** **K158**

> `good/` now contains **L02, L03, L04**.
> All are **PILOT-AUTHORIZED / NOT MAINLINE APPROVED**.
> L04 was restored only after its previously conditional GOOD DATA gate was concretely repaired with exact Eesthetic/Paralex gold.

---

# Critical rule — classic problems are allowed and actively preferred

A pre-LLM classic NLP problem is **not** a novelty failure merely because it was studied in 1991, 2001, or 2011.

Preferred shape:

> **A durable classical NLP/language object + a modern capability or measurement operation that restores a quantity older task formulations discarded, canonicalized, discretized, or made inaccessible.**

Fatal compression is not:

> “This is a classic problem.”

Fatal compression is:

> “This is the already-published modernization of that classic problem.”

For every lead, search the parent through 2024–2026 and test whether the decisive prediction / measurement rewrite / conclusion is already owned.

---

# Current good candidates

## L02 — Semantic Role Completion ≠ Referential Commitment

**Status: PILOT-AUTHORIZED / NOT MAINLINE APPROVED.**

Core RQ:

> When an argument is omitted, does understanding that the semantic role exists license recovery of a concrete discourse entity, or must generative IE first establish that a specific referent actually exists?

Primary substrate: SemEval-2010 Task 10 DNI/INI + recoverable DNI links.

Fragile point: must demonstrate a generative task-definition/modeling consequence, not merely DNI-vs-INI competence.

---

## L03 — Table Value ≠ Observation Status

**Status: PILOT-AUTHORIZED / NOT MAINLINE APPROVED.**

Core RQ:

> In real statistical tables, can a system recover the typed observation denoted by a cell—including provider-defined non-value states—rather than scalarizing every cell or treating all non-values as generic missingness?

Primary substrate: U.S. Census ACS estimate/annotation pairs; independent provider replication required for Main.

Fragile point: must show documentation-conditioned semantics / evaluation consequence rather than Census-code memorization.

---

## L04 — Morphological Inflection Has Realization Cardinality

**Status: PILOT-AUTHORIZED / NOT MAINLINE APPROVED.**

### Corrected parent

Do **not** claim:

- defectivity is new;
- overabundance is new;
- sets of forms are a new representation idea;
- LLMs are the first systems able to complete paradigms.

ACL 2020 already owns full-paradigm generation/paradigm-size discovery, and TACL 2022 explicitly notes that overabundance was canonicalized to one form and that sets of forms would be richer.

The surviving parent is a measurement-validity question:

> **Does canonical single-target inflection evaluation preserve conclusions about morphological generalization once the natural zero/one/many realization relation is restored?**

### Why GOOD DATA is now genuinely YES

Beniamine et al. (LREC-COLING 2024), *Eesthetic: A Paralex Lexicon of Estonian Paradigms*, releases a machine-readable paradigm lexicon whose `forms` representation includes:

- `lexeme`;
- `cell`;
- `overabundance_tag`;
- `defectiveness_tag`;
- orthographic/phonological forms.

The Paralex standard explicitly distinguishes:

- `#DEF#` = defective form/cell state;
- `#MISSING#` = source/transcription information missing.

Eesthetic also represents multiple alternate forms for one lexeme×cell as separate rows.

Thus the independently extractable action mapping is:

- `NO_FORM` = defective / `#DEF#`;
- `ONE_FORM` = one licensed non-defective realization;
- `MULTIPLE_FORMS` = multiple licensed alternate rows/forms for the same lexeme×cell.

This directly repairs the exact gate that caused the prior demotion.

### Main novelty danger

Reviewer compression:

> “TACL's suggested set-of-forms extension implemented on Eesthetic, plus defectivity.”

The only defensible rebuttal is empirical:

> the paper is not claiming the representation; it tests whether the canonical measurement simplification preserves or reverses scientific/model-generalization conclusions.

If the pilot cannot support that consequence, **KILL**.

Full card: `good/L04_REALIZATION_CARDINALITY.md`.

---

# Latest fresh lead audit

## Lead A — Split-antecedent coreference as set-valued antecedence

Not a new lead after repository-wide re-check: this parent is already recorded as **K061 — Split-Antecedent Referential Composition**.

Fresh search makes the kill even stronger:

- ACL 2016 *The More Antecedents, the Merrier* explicitly resolves multi-antecedent anaphors;
- COLING 2020 *Free the Plural* introduces unrestricted split-antecedent anaphora resolution on ARRAU;
- BlackboxNLP 2025 directly asks whether LLMs identify possible referents in split-antecedent / plural-reference ambiguity.

Do not allocate a new kill ID. This is an anti-resurrection confirmation of K061.

---

## Pending K158 — Arabic diacritization: single reference ≠ all valid diacritizations

**Verdict: KILL / NOVELTY_PARENT_COLLISION.**

Attraction:
- natural ambiguity;
- multiple valid outputs;
- exact human/expert data can exist;
- superficially ideal single-reference→set-valued modernization.

Direct collision:

**Mohamed & Mubarak, EMNLP 2025 Main, *Advancing Arabic Diacritization: Improved Datasets, Benchmarking, and State-of-the-Art Models*.**

The paper explicitly introduces **multi-reference diacritization**, augments the standard WikiNews benchmark with multiple valid diacritizations, updates scoring to accept any licensed reference, and provides expert-reviewed WikiNews-2024 data.

Reviewer compression:

> “EMNLP 2025 multi-reference diacritization with another model/dataset.”

No model change rescues the parent.

---

## Pending K159 — Semantic parsing: one utterance ≠ one logical form under genuine ambiguity

**Verdict: KILL / NOVELTY_PARENT_COLLISION.**

Direct collision:

**Stengel-Eskin, Rawlins & Van Durme, ICLR 2024, *Zero and Few-shot Semantic Parsing with Ambiguous Inputs*.**

Its explicit parent is that semantic-parsing datasets commonly assume a one-to-one natural-language→formal-representation mapping even when language is ambiguous. It introduces AmP, evaluates distributions over multiple possible logical forms, and calls for ambiguity to be represented explicitly in data/evaluation.

Reviewer compression:

> “AmP / ICLR 2024, but with a different ambiguity source or newer LLM.”

This is almost exactly the modernization generator we were searching for, which is why the candidate must die immediately.

---

## Pending K160 — Pronunciation/G2P: word form ≠ one pronunciation

**Verdict: KILL CURRENT FORM / NOVELTY_PARENT_COLLISION.**

Attraction:
- pronunciation variation is a real classic object;
- one spelling may license multiple pronunciations;
- ASR/TTS/G2P naturally expose set-valued outputs.

Why it dies:
- pronunciation lexicon standards have long represented multiple valid pronunciations;
- classic ASR work explicitly models regional, speaking-style, and name-pronunciation variants;
- 2025 *Graph Connectionist Temporal Classification for Phoneme Recognition* directly attacks the single-pronunciation supervision assumption by training over a graph of alternative valid phoneme sequences and reports improved recognition.

Reviewer compression:

> “Known pronunciation-variant lexicons / alternative-pronunciation graph training, moved to a general LLM generator.”

The output-cardinality rewrite is already computationally operationalized, so an LLM version is not a new parent.

---

# Search lesson from this pass

The generator

> **single output → multiple valid outputs**

has an unusually high collision rate. Coreference, semantic parsing, Arabic diacritization, pronunciation, MT, GEC, and many generation tasks already explicitly modernize it.

The more promising subcase is therefore not generic multiplicity. Prefer cases where all three are true:

1. **0 / 1 / many or typed state is itself a scientifically meaningful latent quantity**, not merely reference diversity;
2. existing natural data expose that quantity independently;
3. restoring it can change a mature task's scientific conclusion, not merely improve fairness of exact-match scoring.

This is why L03 and the corrected L04 survive where generic multi-reference ideas die.

---

# K157 reminder — MapTask collaborative plan

K157 remains killed after full modern-parent audit.

The classic MapTask data survived REAL OBJECT and GOOD DATA, but 2026 *Seeing Is Not Sharing*, *Humans' ALMANAC*, and *CollabSim* already modernize participant-specific common ground / partner state / collaborative action on essentially the same task family.

Reviewer compression:

> “Existing 2026 MapTask collaborative-state work, but at whole-route granularity.”

Do not resurrect.

---

# Search target from here

Current scoreboard:

# **3 / 5**

Approved paper mainline:

# **NONE**

Continue searching for at most two more candidates, but do not lower the bar below L02/L03/L04.

Highest-priority generator:

> **A mature NLP task had to condition away / merge / proxy a natural state. The state has existing independent gold. Modern generation or measurement makes the state directly recoverable. Restoring it could reverse an established model/evaluation conclusion.**

Prefer:

- IE / QA / document understanding;
- tables;
- MT / generation evaluation only if not generic multi-reference;
- dialogue with external state;
- speech only if the target is not generic prosody/pronunciation variation;
- morphology only if outside already-covered realization-cardinality parent;
- information retrieval / structured prediction where a hidden technical restriction has external gold.

Avoid immediately:

- generic multiple-valid-reference stories;
- split-antecedent coreference;
- semantic-parsing ambiguity distributions;
- Arabic multi-reference diacritization;
- pronunciation-variant set generation;
- MapTask/common-ground/shared-plan modernization;
- LexSub generation distribution;
- logical metonymy covert-event recovery;
- PP ambiguity;
- ellipsis open recovery;
- generic prosody→meaning tests.

**Repository note:** L04 and `good/README.md` have been updated. K158–K160 above are fully audited but still need to be appended to the authoritative `failed/KILLED_LEDGER.md`; do not advance the authoritative ledger index until that append is completed.
