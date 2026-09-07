# Current Research-Question Search — 2026-09-07 Active Search

**Target:** NAACL Main  
**Approved paper mainline:** NONE  
**Pilot-authorized candidates in `good/`:** **3 — L02, L03, L04**  
**Authoritative killed ledger on disk:** through **K161**  
**Next ledger kill ID:** **K162**

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

## Recently closed K158–K161

- **K158 — Arabic diacritization: single reference ≠ all valid diacritizations.** KILL: EMNLP 2025 directly modernizes multi-reference diacritization.
- **K159 — Semantic parsing: one utterance ≠ one logical form under genuine ambiguity.** KILL: ICLR 2024 AmP directly owns ambiguity-aware multi-parse evaluation.
- **K160 — Pronunciation/G2P: word form ≠ one pronunciation.** KILL CURRENT FORM: alternative-pronunciation supervision/graphs already operationalize the set-valued output.
- **K161 — OCR 1-best transcript ≠ OCR evidence.** KILL: ICCVW 2025 directly propagates OCR confidence + top-k hypotheses into downstream information extraction; EACL Industry 2026 further crowds OCR-vs-image MLLM document IE.

These kills reinforce that a productive **idea generator is not itself a selection requirement**. Do not keep mining one generator after it starts dominating the search.

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

# Search-doctrine correction — diversity, outcome robustness, paper-level novelty

This section **supersedes any earlier wording that makes one generator “highest priority.”**

## 1. Search breadth is a hard process requirement

Do **not** take one promising pattern (e.g. output-unit rewrite, premature commitment, single→multiple, Old Problem/New Method) and spend the whole search inside it.

Every serious search pass should deliberately cover several different paper identities / generators, for example:

1. **Natural unresolved NLP object** — a durable open question visible in ACL/EMNLP/NAACL work.
2. **Old Problem / New Method** — modern methods enable a scientific operation that used to be impractical or inaccessible.
3. **Data-first reverse search** — mature natural datasets expose two variables whose relationship has not been scientifically exploited.
4. **Measurement / evaluation reconstruction** — a standard metric/task definition may measure the wrong quantity.
5. **Representation / intermediate-state question** — an old explicit representation may be obsolete, or may remain load-bearing.
6. **Methodological/scientific-discovery question** — a new method allows stronger intervention, decomposition, attribution, or validation.
7. **Contradictory accounts in existing literature** — two plausible explanations make different predictions on natural data.
8. **Classic task modernization outside language-theory-heavy topics** — IE, QA, MT, summarization, dialogue, speech, document understanding, IR, structured prediction, generation/evaluation, morphology, etc.

A pass should normally inspect leads from **multiple tracks**, not 3–5 variants of one underlying template.

## 2. Do not gamble the paper on a rare/failure phenomenon

A candidate is weak if its paper only exists when:

> “models unexpectedly fail / hallucinate / show bias X.”

Before pilot authorization, require an **outcome-robust scientific question**:

- Account A wins → publishable scientific conclusion A.
- Account B wins → publishable scientific conclusion B.
- principled heterogeneity → publishable boundary/conditional conclusion.
- a reasonable near-null result should still answer an important pre-specified question, not simply erase the paper.

The experiment may of course kill a candidate because data are invalid, manipulation fails, task has no leverage, or the resulting effect is too tiny/noisy to support any scientific conclusion. But **the candidate must not be designed so that only one exciting phenomenon creates the story**.

Do not search primarily for:
- “will models make this mistake?”;
- “can we find a surprising failure?”;
- “does bias/phenomenon X appear in LLMs?”;
- “maybe ranking reverses.”

Prefer:
- “which of two plausible accounts better describes the natural object?”;
- “is an established modeling/evaluation assumption valid under the modern regime?”;
- “under what boundary is representation/method A necessary versus safely removable?”;
- “what scientific quantity does the mature task actually measure?”

## 3. Novelty is paper-level, not neighborhood purity

Do **not** require every scientific sub-question, object, distinction, dataset, or broad parent neighborhood to be untouched.

Prior work may already study:
- the classic object;
- one component distinction;
- one stage of the pipeline;
- the dataset;
- a related measurement;
- a neighboring LLM capability.

What must remain new enough is the **load-bearing paper identity**: the specific scientific relation / framing / decisive comparison / measurement consequence / synthesis that supports our narrative and core claims.

Fresh literature assassination should therefore ask:

> “Could a reviewer cite one or a small set of papers and accurately say that they already establish the same paper-level story and decisive conclusion?”

If YES → KILL.

If prior work only supplies ingredients, background distinctions, or neighboring evidence, that is **not automatically fatal** if our paper has a genuinely new scientific narrative and decisive contribution.

Reviewer compression remains mandatory:

> “This is just ______.”

But the blank must compress the **actual proposed paper**, not merely name its broad field.

## 4. Old Problem / New Method is one generator, not the project definition

Continue using it because it has produced strong candidates, but do not let it narrow the entire project.

A completely contemporary natural NLP problem is allowed if it has:
- durable object;
- simple explanation;
- trustworthy data;
- genuine scientific tension;
- nontrivial paper-level novelty;
- decisive C1→C2→C3.

Likewise, a methodology/measurement paper can be valid even when the base scientific object is old.

## 5. Good data remains non-negotiable

The correction above **does not weaken Gate 3**.

No:
- “after verifying”;
- “likely extractable”;
- “should support”;
- author-invented load-bearing labels;
- synthetic worlds merely to manufacture leverage.

The exact gold required for the decisive estimand must already be verified before `good/`.

---

# Search target from here

Current scoreboard:

# **3 / 5**

Approved paper mainline:

# **NONE**

Continue searching for at most two more candidates, but do not lower the bar below L02/L03/L04.

Search policy:

> **Run a diversified portfolio of search tracks. No single generator is authoritative.**

For each pass, deliberately include both classic and contemporary objects, and both task/measurement and scientific-question routes. Use the strongest available natural data early, but do not reverse-search only one kind of annotation schema.

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

**Repository note:** `good/` contains L02/L03/L04. The authoritative killed ledger is now through K161; next kill ID is K162.

---

# Good-candidate package registration — 2026-09-07

The three current pilot-authorized candidates have now been converted from single cards into **canonical per-candidate research packages**:

- good/L02_REFERENTIAL_COMMITMENT/
- good/L03_TYPED_OBSERVATION/
- good/L04_REALIZATION_CARDINALITY/

Each package contains:
- README.md — authoritative RQ / accounts / outcome robustness / C1→C2→C3;
- RELATED_WORK_AND_NOVELTY.md — paper-level ownership and collision map;
- DATA_AND_GOLD.md — exact data/gold contract and validity kills;
- RESEARCH_PLAN.md — pilot, outcome branches, full development roadmap, pre-mainline checklist.

This structure is now the authoritative format for every future promoted good candidate.

The legacy top-level good/L02_*.md, L03_*.md, and L04_*.md files remain only as backward-compatible entry points.

The candidate template has also been corrected to make two questions mandatory before compute:

1. **If the expected phenomenon does not occur, what is the paper?**
2. **What part of the full paper-level story is actually new?**

Future searches/promotions must use these package and template rules.
