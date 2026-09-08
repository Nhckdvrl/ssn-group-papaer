# L07 Claim Ledger

**Current paper status:** data gate only; no model or paper claim is approved.

| ID | Exact claim | Role | Nearest work / distinction | Evidence | Status |
|---|---|---|---|---|---|
| D0 | A reproducible random sample of PubMed records that are both `Published Erratum` and PMC-linked contains enough publisher-licensed proposition-level old→new updates for a 150–300 item pilot and a diverse Main-scale expansion. | Blocking data claim | NLM licenses the document relation, but prior meta-research warns that many errata are bibliographic or minor. | E000: 10.99% confirmed T1 yield; 40 reviewed T1 across 33 journals and four substantive classes | **Supported for pilot acquisition** |
| C1 | Given an original paper and its official correction, a model may fail to return only the currently licensed proposition. | Core scientific claim | Unlike temporal QA and generic context conflict, authority comes from an editorial update relation rather than recency or majority evidence. | Not run; blocked by D0 | Hypothesis |
| C2 | Success depends on update locality/modality and on whether supersession is represented explicitly, rather than only on document recency/order. | Mechanism/boundary | Must be separated from temporal salience and context-order effects. | Not run; blocked by D0 | Hypothesis |
| C3 | Scientific QA/IE ingestion may need proposition-state or update-aware indexing instead of flat document aggregation. | NLP consequence | This is justified only if C1/C2 change answers or false-override behavior. | Not run; blocked by D0 | Hypothesis |

## Promotion discipline

- E000 can support or reject **D0 only**. It cannot establish model behavior.
- A parser hit is not gold. Tier 1/2 status requires publisher-authored text that explicitly licenses both sides, or an exact location plus a deterministic original-article lookup.
- Manual reviewers may verify direct evidence but may not infer an unstated correction.
- If D0 fails, L07 is NO-GO in its present form; no synthetic rescue set is allowed.
- D0's support authorizes acquisition and a minimum model pilot only. The model-facing C1–C3 remain hypotheses.
