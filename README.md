# SSN Group Paper — Research Repository

**Framework reset: 2026-09-28**

The repository is organized by **research stage**, not by topic.

A domain such as AI4Quant, MoE, hybrid models, speech, VLA, etc. should **not** become a new top-level folder. Topic-specific work belongs in `workbench/`; reusable background material belongs in `library/`.

## Canonical flow

> **SEARCH → WORKBENCH → CANDIDATE → PAPER**

The key rule is:

> **Search does not need to invent the final paper idea.**

Search only needs to identify an important problem territory worth serious exploration. The actual paper question, finding, mechanism, or method is allowed to emerge from strong-baseline reproduction and experiments inside the workbench.

## Top-level structure

| path | role |
|---|---|
| `search/` | topic-search philosophies; decides what is worth exploring |
| `workbench/` | baseline reproduction, analyses, failures, observations, changing hypotheses |
| `candidates/` | current paper candidates only; currently **0** |
| `library/` | reusable territory map, anchor papers/blogs, deep literature/artifact archives |
| `failed/` | durable global anti-resurrection / kill evidence |
| `archive/` | read-only historical candidates, old “good” packages, retired search systems and experiments |

There is deliberately **no top-level `observations/`**. A stable observation stays with the workbench that produced it until it helps crystallize an actual candidate.

## 1. Search

`search/` contains only search philosophies:

- `search/sasano-taste/`
- `search/our-taste/`

A search result should look like:

> “This problem territory is important enough to inhabit; here is the object / baseline / line we should start from.”

It does **not** need to predict the final result, method, or paper title.

No experiments, topic folders, or candidate IDs belong under `search/`.

## 2. Workbench

`workbench/` is the main research space.

Default behavior:

> **strong baseline → reproduce → strengthen / understand → exploratory analysis → successes + failures → stable knowledge → candidate (maybe)**

A workbench owns its own observations. Hypotheses may change freely. Negative results, large drops, broken assumptions, and unexpectedly strong baselines are useful gradients.

A workbench may end as:
- a candidate;
- a paused knowledge asset;
- a failed line with reusable lessons.

It does **not** need to become a paper.

## 3. Candidates

Only create a directory under `candidates/` after a workbench has naturally produced a clear, important, defensible paper identity.

Current candidates: **0**.

Historical candidate packages are under `archive/candidates/`.

## 4. Library

Before broad web search, check:

1. `library/TERRITORY_BANK.md`
2. `library/KEY_PAPERS.md`
3. `library/BLOGS_REPORTS.md`
4. `library/deep/`

The library is reference material, not a candidate list.

## 5. Failed / Archive

`failed/` is active anti-resurrection knowledge.

`archive/` is read-only history. Old status labels inside it are historical only and never authorize new work.

## Repository rules

- top-level folders represent **stage/function**, never a topic;
- no new `search_rounds/` process dumps;
- no candidate ID during search or early exploration;
- observations stay local to a workbench;
- paused workbenches may remain as knowledge assets;
- topic-specific experiments belong in `workbench/`, not in a search lane;
- current state is determined by this README plus the relevant current-stage README.
