# L07 — Related Work and Paper-Level Novelty

**Candidate:** Official Correction ≠ Current Scholarly Claim

---

## 1. Official scholarly update infrastructure

### NLM / PubMed

NLM explicitly creates links between:
- original articles;
- erratum/correction notices;
- retractions;
- corrected-and-republished articles;
- updates.

NLM treats corrections to text, graphs, tables, and similar content as errata and links the notice to the original record.

Official source:
- https://www.nlm.nih.gov/bsd/policy/errata.html

### Crossref / Crossmark

Crossmark records editorially significant updates and defines update types including:
- correction;
- corrigendum;
- erratum;
- clarification;
- partial retraction;
- retraction;
- new version;
- withdrawal.

Crossref explicitly says separate update records are for changes likely to affect interpretation or crediting, while minor spelling/formatting changes need not be registered.

Official sources:
- https://www.crossref.org/documentation/crossmark/participating-in-crossmark/
- https://www.crossref.org/documentation/register-maintain-records/maintaining-your-metadata/registering-updates/

This supports the scientific object:
> an official update changes the status of the scholarly record.

## 2. Direct old→new proposition evidence exists

PMC correction notices often state exact replacements.

Examples:
- “The sentence should read … instead of …”
- figure/table “should read … instead of …”
- corrected funding, method, numeric, and interpretation statements.

Representative examples:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12014900/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10478380/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11837133/

This matters because the core target can be publisher-authored rather than adjudicated by our annotators.

## 3. Closest NLP neighborhoods

### LLM self-correction
TACL 2024 surveys automated correction and asks when LLMs can correct their own outputs.

Sources:
- https://aclanthology.org/2024.tacl-1.27/
- https://aclanthology.org/2024.tacl-1.78/

Not our object:
- those papers concern model-generated errors and feedback;
- our correction is an external scholarly editorial operation over a published source.

### Factuality correction
ACL 2026 FactCorrector corrects factual errors in generated long-form responses using structured feedback.

Source:
- https://aclanthology.org/2026.acl-long.2147/

Not our object:
- generated answer → corrected generated answer;
- not original scholarly proposition → official publisher update → current scholarly proposition.

### Scientific-paper critique
CLAIMCHECK studies whether LLM critiques of scientific papers are grounded.

Source:
- https://aclanthology.org/2025.findings-emnlp.1185/

Not our object:
- critique/verification is different from applying an official supersession relation.

## 4. What prior work already owns

Already owned:
- temporal QA;
- dynamic knowledge;
- factual conflict;
- retraction detection;
- self-correction;
- external-feedback correction;
- scientific claim verification.

We cannot claim:
- papers can contain errors;
- corrections exist;
- newer documents may supersede older ones.

## 5. New paper-level story

The proposed identity is:

1. scholarly infrastructure externally marks an update relation;
2. some correction notices give direct old→new proposition replacements;
3. the model sees the original and correction;
4. the task is not “which is newer?” but “which proposition is **currently licensed** by the scholarly record?”;
5. direct generation is compared with explicit update-state handling;
6. the result changes how scientific QA/IE should ingest corrected literature.

## 6. Reviewer compression

### Attack 1
> “Temporal QA with an erratum timestamp.”

Fatal if the only signal is date ordering.

Rebuttal:
> official correction is an adjudicated semantic operation; a newer paper that merely disagrees does not have the same status.

### Attack 2
> “Retraction awareness.”

Rebuttal:
> retraction is mostly document-level invalidation; this task includes local proposition replacement inside an otherwise valid article.

### Attack 3
> “LLM correction with external feedback.”

Rebuttal:
> the source to be updated is the scholarly record, and the update relation is publisher-defined, not model feedback.

## 7. Kill-level collision definition

KILL if a prior paper already:
- constructs natural original↔official-correction pairs;
- extracts proposition-level old→new gold;
- evaluates current-claim QA/IE;
- compares flat document aggregation against explicit update/supersession modeling;
- and reaches the same scholarly-state conclusion.

A generic temporal/retraction/factual-correction paper is not sufficient to kill.

## 8. Data-yield danger is scientific, not cosmetic

Meta-research shows many errata are trivial/minor.

One medical-publication study found:
- 557 articles associated with errata;
- 24.2% had at least one major error materially affecting interpretation.

Source:
- https://pubmed.ncbi.nlm.nih.gov/24662621/

A newer specialty review also reports that many authorship/text corrections are trivial.

Therefore:
> “all errata” is not the dataset.

The candidate lives only if a sufficiently large **substantive proposition-update** subset can be extracted with direct publisher evidence.

## 9. Current novelty verdict

**YES, current audit.**

Closest work supplies neighboring correction/factuality concepts, but not the same official-scholarly-supersession paper identity.

## 10. Execution-time collision re-audit — 2026-09-08

Closest current ACL-family comparisons kept beside E000 and the next pilot:

- **Knowledge Conflicts for LLMs: A Survey** (EMNLP 2024): context-memory and inter-context conflict taxonomy, but no publisher-authorized update edge or current-scholarly-proposition gold. https://aclanthology.org/2024.emnlp-main.486/
- **UnSeenTimeQA** (ACL 2025): synthetic time-sensitive reasoning designed to avoid memorization; unlike L07's natural editorial authority relation. https://aclanthology.org/2025.acl-long.94/
- **Assessing and Mitigating Medical Knowledge Drift and Conflicts in LLMs** (Findings of EMNLP 2025): changing/conflicting clinical guidance, not local correction of a published proposition. https://aclanthology.org/2025.findings-emnlp.38/
- **MRAG** (Findings of EMNLP 2025): temporal retrieval/ranking over time-sensitive evidence, not supersession licensed by the publisher. https://aclanthology.org/2025.findings-emnlp.167/

Correction-specific meta-research and datasets do exist, including a 2000–2023 JACS correction-notice dataset and studies of citation/practice. They strengthen the natural-object and scale case but do not evaluate current-claim QA/IE or flat-vs-update-state modeling. ACL Anthology's own correction policy is especially relevant: errata must be read alongside the original, while downstream consumers may not propagate updates reliably. https://aclanthology.org/info/corrections/

**Strongest post-audit reviewer compression:** “filter substantive errata, then run temporal QA.” The next pilot must defeat this by crossing official update authority with order/recency controls and flat versus explicit update state. A plain “models can copy the replacement sentence” result is still fatal.
