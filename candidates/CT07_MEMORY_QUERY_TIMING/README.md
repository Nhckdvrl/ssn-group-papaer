# CT07 — When Does the Memory Query Become Available?
## Intra-action emergence of exact-memory demand in tool-using agents

**Status: KILLED AFTER E00 (2026-09-27), `CT-KILL-20260927-3`** — frozen rule 1 (no deployable leverage). See `docs/E00_RESULTS.md`.
One sentence: the query that locates the exact value forms while the value is being written (tau: the first value token's query hits the source block 42% vs 13% before it), so no control-prefix boundary exists at which memory could be selected before binding (R_PREVALUE 0.13–0.22).
Registered 2026-09-27. It grows out of three CT05 E01 facts (`candidates/CT05_EXACT_MEMORY_DEMAND`):

1. Under window eviction, long-history dependence sits on **argument values**, not tool identity
   (KVWIN2 share of loss: tau value 99% / name 0%; SWE value 81% / name 3%).
2. Attention from the **whole future action's** queries recovers 99% / 93% of the budgeted-eviction
   oracle (25% / 50% budget). Deployable pre-action attention recovers 36% / 23%.
3. Recurrence carry lands on control tokens (tau name 0.455 nats/token), not values (0.011).

Between the two endpoints of fact 2, nothing is known. The question is **at which point inside a
structured action (header → tool name → argument key → first value token) the history-attention of
the model's own already-generated prefix becomes a good enough memory query to locate the old
exact values it is about to copy.**

## Nearest priors (checked 2026-09-27)

| Prior | Owns | Does not ask |
|---|---|---|
| Query Visibility Audit (2607.11942) | query-aware vs query-agnostic compression change method rankings | timing inside a generated action |
| AgentKV (2609.14872) | phase-level (think / act / tool) future-query subspaces, per-phase query buffers | granularity *within* one act |
| Quest, Lookahead Q-Cache, INTRA (2605.05806) | query-aware page selection; pseudo future queries; attention queries as a retriever in a separate pre-generation pass | how query quality evolves along the decoded prefix (INTRA states it does not analyse this) |
| FLARE | retrieval triggered mid-generation in open text | structured-action control prefix as the query |
| DualTune, ToolRobustBench | selection / schema / argument-binding stage decomposition | what history each stage needs |
| Tool-call dependency probing (2605.25310) | output→argument dependency edges linearly decodable at call-boundary tokens (Qwen3-32B) | intra-action timing; KV selection |
| SideQuest, StateComp, Execution Provenance | last-use / safe-to-replace / provenance of tool values | when the query forms (value liveness was **not** registered for this reason) |

## Files

- `docs/E00_PROTOCOL.md` — frozen before running.
- `src/e00.py` — runner (reuses CT05 `cachelib.py`, `render.py`, `env.sh`).
- `src/analyze_e00.py` — recovery curves and decision rule.
