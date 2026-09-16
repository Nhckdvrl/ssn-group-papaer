# Selected Topics — Sasano-Taste Search

Started: 2026-09-16

Purpose: record only questions that survive real nearest-prior novelty checking, fit Sasano/Main scientific taste, and whose **actual experiment is itself scientific rather than mainly an evaluation exercise**.

## Admission rule

A topic can enter this file only when all of the following are true:

1. **Worth asking:** the question is understandable without elaborate framing and there is a natural reason a reviewer would want to know the answer.
2. **Real difference:** nearest prior work does not already answer the same parent question; the difference is not merely a new model, dataset, language, condition, or exact experimental cell.
3. **Correct scientific width:** the parent RQ, claim scope, and Related Work neighborhood are calibrated against ACL / EMNLP / NAACL Main and Sasano-approved work.
4. **Scientific experiment, not evaluation disguised as science:** after stripping away the Introduction rhetoric, the main experiment must study a phenomenon, learning/representation/behavioral law, causal relation, trade-off, or natural process. If the work reduces to constructing a dataset and comparing methods/metrics/robustness/leaderboards, do not select it.
5. **Data path is natural and realistic:** do not require large synthetic benchmark construction, hard-to-obtain ground truth, or an artificial dataset merely to make the question measurable.
6. **Exploratory rather than anomaly gambling:** several plausible outcomes should remain scientifically interpretable, but this alone is not sufficient for selection.
7. **Feasible:** there is a cheap initial experiment that directly reduces uncertainty without large pretraining or a massive annotation campaign.

Mechanistic depth, surprising results, large model sweeps, and complex methods are not admission requirements.

---

## Current selections

**None. Current selected topic count = 0. This is intentional.**

### Explicitly cancelled registrations

- **S01 — Omission ≠ Neutrality / effective default semantics in tool calls:** cancelled/demoted. It is already recorded as F06 in `FAILED_TOPICS.md`; the Main-level parent compresses to underspecified tool intent / argument completion, leaving only an exact API-default subcase.
- **S02 / C2 — AI Rewrite ≠ Semantic Change:** registration cancelled. The high-level framing looked scientific, but the actual experimental object collapses into synthetic rewrite-data construction + semantic-preservation validation + comparison of LSC methods/metrics/robustness. Real post-LLM corpora lack clean semantic-change ground truth; synthetic paired rewrites provide ground truth only by making the central data artificial. This is precisely the evaluation/benchmark/metric-validity direction the search should avoid.

Do **not** revive either topic by adding more models, more datasets, more metrics, or broader rhetoric.
