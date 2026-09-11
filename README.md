# SSN Group Paper: Research Workflow

Target: NAACL Main, continuously calibrated against strong ACL / EMNLP / NAACL work.

## Workflow Documents

1. [Research Topic Search](RESEARCH_TOPIC_SEARCH.md): find natural questions with a credible contribution path.
2. [Topic Search Playbook](TOPIC_SEARCH_PLAYBOOK.md): optional generators, not approval rules.
3. [Research Topic Selection](RESEARCH_TOPIC_SELECTION.md): evaluate RQ, idea, and contribution separately; authorize bounded pilots and full studies separately.
4. [Research Execution](RESEARCH_EXECUTION.md): develop evidence, explanation, breadth, consequence, and a current contribution through explicit stage gates.
5. [Local Agent Start](LOCAL_AGENT_START.md): safe startup and source-of-truth rules, without duplicated experiment queues.

## Workflow Revision: 2026-09-11

This revision addresses process failures exposed by L12, not just its candidate wording:

- A good RQ, a promising idea, strong evidence, and a mature contribution are separate judgments.
- A successful pilot does not mean the full study is sufficient.
- Main calibration must identify missing intellectual advances and necessary workload, not similar section headings.
- Novelty review tests both the strongest compression and the strongest surviving contribution.
- A proposed experiment must be useful even after asking what its strongest positive result would actually establish.
- Unexpected findings can redirect the study; a new title cannot upgrade old evidence.
- HOLD is a bounded decision, not indefinite protection of sunk cost.

The detailed [L12 process retrospective](RESEARCH_EXECUTION.md#12-l12-retrospective-what-the-workflow-missed) explains what should have changed at earlier decision points. This workflow revision does not rerun experiments or issue new verdicts for every project.

## Project State and Repository Practice

[CURRENT_SEARCH.md](CURRENT_SEARCH.md) is a dated portfolio index. Read the concrete candidate's latest status and the latest user request before action. Historical priorities and directory names are not permanent authorization.

[candidates/README.md](candidates/README.md), [good/README.md](good/README.md), and [failed/KILLED_LEDGER.md](failed/KILLED_LEDGER.md) retain portfolio and decision history. This entry page intentionally does not duplicate candidate priorities, metrics, or next kill IDs.

Ordinary execution edits only the selected concrete project. Root maintenance requires explicit scope. Preserve concurrent work and keep large raw experiment artifacts outside git with provenance pointers. Inspect outgoing history before merging/pushing main.
