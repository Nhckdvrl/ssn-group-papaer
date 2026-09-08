# L07 Claim Ledger

**Current paper status:** scaled experiment authorized; no paper claim is approved.

| ID | Exact claim | Role | Nearest work / distinction | Evidence | Status |
|---|---|---|---|---|---|
| D0 | A reproducible random sample of PubMed records that are both `Published Erratum` and PMC-linked contains enough publisher-licensed proposition-level old→new updates for a 150–300 item pilot and a diverse Main-scale expansion. | Blocking data claim | NLM licenses the document relation, but prior meta-research warns that many errata are bibliographic or minor. | Corrected E000: 12.81% T1 yield (95% CI 9.49–16.13%); 33 reviewed T1 across 27 journals and four classes | **Supported for expansion** |
| C1 | Given an original paper and its official correction, a model may fail to return only the currently licensed proposition. | Core scientific claim | Unlike temporal QA and generic context conflict, authority comes from an editorial update relation rather than recency or majority evidence. | E002b: 10-item/3-model macro flat 70.0%; position-robust 56.7% | **Pilot-supported; not claim-ready** |
| C2 | Success depends on update locality/modality and on whether supersession is represented explicitly, rather than only on document recency/order. | Mechanism/boundary | Must be separated from temporal salience and context-order effects. | E002b: explicit +6.7 points macro; substantial candidate-position sensitivity; no clear document-order effect | **Pilot-supported boundary; not claim-ready** |
| C3 | Scientific QA/IE ingestion may need proposition-state or update-aware indexing instead of flat document aggregation. | NLP consequence | This is justified only if C1/C2 change answers or false-override behavior. | Not run; blocked by D0 | Hypothesis |

## Promotion discipline

- E000 can support or reject **D0 only**. It cannot establish model behavior.
- A parser hit is not gold. Tier 1/2 status requires publisher-authored text that explicitly licenses both sides, or an exact location plus a deterministic original-article lookup.
- Manual reviewers may verify direct evidence but may not infer an unstated correction.
- If D0 fails, L07 is NO-GO in its present form; no synthetic rescue set is allowed.
- E002b authorizes 150-item acquisition and generated-answer evaluation. Forced-choice pilot rates must not be reported as population failure rates.
