# Local Agent Start — Task-Specific Research Handoff

Updated: 2026-09-12. Target: ACL / EMNLP / NAACL Main.

## 1. First decide what task this is

Read the latest user request, sync `main`, inspect divergence/dirty files, then classify the task:

- **TOPIC SEARCH** → read `CURRENT_SEARCH.md`, `RESEARCH_TOPIC_SEARCH.md`, `TOPIC_SEARCH_PLAYBOOK.md`, and the anti-resurrection records needed for the prospective lead.
- **CANDIDATE SELECTION / REVIEW** → read the concrete candidate package plus `RESEARCH_TOPIC_SELECTION.md`; consult search records/ledger for ownership history.
- **EXPERIMENT EXECUTION** → read the concrete candidate’s latest status/ledger plus `RESEARCH_EXECUTION.md`; do not reload the entire search playbook unless the claim mutates.
- **WORKFLOW MAINTENANCE** → read the affected root documents and preserve their separate responsibilities.

Do **not** automatically load SEARCH + SELECTION + EXECUTION as one giant checklist. The workflow is staged on purpose.

## 2. Source-of-truth order

1. latest user request;
2. current remote `main`;
3. concrete candidate’s latest README / claims / experiment ledger when working on a candidate;
4. the root document for the current stage;
5. `CURRENT_SEARCH.md` as dated portfolio/taste;
6. historical search rounds / killed ledger for provenance and anti-resurrection.

Directory names and old handoff commands are not authorization.

## 3. Stage-specific authorization

A search lead is not a selected candidate.

A serious candidate is not pilot-authorized.

A pilot approval is not approval of a full study or manuscript identity.

A materially mutated RQ/claim/explanation requires re-selection before broad confirmation or scale-up.

Do not rerun an experiment because an old root note says “next.” The current candidate ledger and current authorization control execution.

## 4. Current topic taste

For open-ended search, current preference is model science:

> **stable anomaly → mechanism; training/post-training dynamics; reasoning computation; representation → causal use; old empirical laws under modern model regimes.**

Strongly deprioritize new data/benchmark/RAG/retrieval/metric/annotation/workflow topics unless the scientific question is exceptional and clearly transcends that framing.

Do not let easy gold choose the research question.

## 5. During work

Keep load-bearing evidence traceable:

> **claim → experiment → config/code → data → raw result → conclusion**

Respect project boundaries. Preserve concurrent work. Keep large regenerable artifacts outside git with provenance pointers where appropriate. Inspect outgoing history before publishing.

Report what actually changed: search judgment, selection judgment, evidence, contribution, or readiness. Do not call documentation changes experimental validation, or a local effect a Main-ready paper.
