# 2026-09-12 — Source-Bounded Evidence Search

**Target:** ACL / EMNLP / NAACL Main  
**Search mode:** award-topic provenance → quiet professional workflow → hidden benchmark simplification → direct-owner assassination.  
**Rule:** no survivor quota; compact rejection notes only.

## Survivor

### L25 — Evidence Exists Somewhere ≠ One Source Establishes It

**Status:** SERIOUS / PRE-PILOT — DATA-CONSTRUCTION AUDIT — NO COMPUTE  
Package: `candidates/L25_SOURCE_BOUNDED_EVIDENCE/`

**RQ:** When all required facts are present somewhere across several valid documents, can an LLM preserve which source supports which fact when the decision rule requires one source to establish the whole claim, or does it fuse the context into a single bag of evidence?

**Origin:** patent novelty provides a real single-source rule, while inventive step/obviousness permits justified combinations. PatentMatch discarded EPO Y citations because they were semantically too close to X for its matching task; FiNE-Patents filters inventive-step rejections; PANORAMA includes §102/§103 and shows retrieval/paragraph identification is easier than the final novelty/non-obviousness judgment. The candidate asks whether **rule-conditioned evidence fusion** is the missing operation.

**Closest collision:** PANORAMA already owns generic §102/§103 classification. L25 survives only through a matched causal intervention holding atomic evidence fixed while manipulating source partition and aggregation rule.

## Compact rejections from this search

### Generic patent novelty / §102-vs-§103 classification — KILL
**Question:** Can LLMs distinguish novelty from non-obviousness in real patent examination?  
**Why not:** PANORAMA already directly benchmarks §102 / §103 / ALLOW with full decision trails and cited prior art. Another model sweep or prompt method is an occupied benchmark cell.

### Prior-art retrieval / feature matching — KILL
**Question:** Can LLMs retrieve the patent passages that disclose claim features and decide novelty?  
**Why not:** PatentMatch, PANORAMA and SIGIR 2026 FiNE-Patents already own retrieval, paragraph identification, feature-level disclosure and single-document novelty workflows.

### EPO X-vs-A semantic relevance — KILL
**Question:** Can a model tell novelty-prejudicing prior art from background prior art by semantic matching?  
**Why not:** this is essentially the original PatentMatch task, with millions of examiner-labeled claim–paragraph pairs.

### Generic multi-source evidence aggregation — KILL
**Question:** Does combining more independent sources improve verification?  
**Why not:** multi-source fact verification already studies source-aware fusion, disagreement and aggregation. The interesting axis is not “more sources” but **when the governing inference rule forbids or permits composition**.

### Generic context/source admissibility — DO NOT PROMOTE
**Question:** Can an LLM distinguish text present in context from text admissible as evidence?  
**Why not:** this is already emerging as an explicit long-context/RAG source-boundary object, including a 2026 working manuscript. L25 is narrower in a different way: all documents can be valid, independent and relevant; only their **composition under a particular inference rule** changes.

## Search takeaway

A useful topic-provenance pattern appeared here:

> **Look at what mature datasets intentionally throw away because it makes the learning problem awkward.**

PatentMatch's discarded Y category and FiNE-Patents' filtered inventive-step cases are not automatically a research contribution. But together with PANORAMA's decision-stage failure and the old single-source-vs-combination doctrine, they expose a clean scientific question that the simplified benchmarks could not ask.

Next action is **data-only E00**, not model compute: verify that PANORAMA contains enough two-reference §103 cases with examiner rationales that identify complementary feature coverage and complete released prior-art text. If not, kill L25 before building anything.
