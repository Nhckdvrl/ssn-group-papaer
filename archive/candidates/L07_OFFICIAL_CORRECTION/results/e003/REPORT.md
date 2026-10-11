# E003 Checkpoint Report

**Status:** paused cleanly on 2026-09-09; no model process or partial model output remains.

## Purpose

E003 scales natural item acquisition after E000–E002b without weakening the scientific object. Its target is at least 150 instances in which publisher-authored text explicitly licenses X→Y and the model-facing historical article excerpt contains X but not Y.

## Completed work

| Stage | Result | Evidence boundary |
|---|---:|---|
| Deterministic draw | 4,100 candidates, seed 20260910 | Drawn from the frozen E000 frame after excluding all 500 E000 IDs |
| Accepted expansion | 4,000 notices | One pre-boundary candidate lacked `ErratumFor` and was replaced deterministically |
| Identity validation | 4,000/4,000 | PubMed relation/PMCID plus exact correction-JATS PMID match |
| Parser triage | 582 exact-replacement candidates | Triage only; not gold |
| Rule proposals | 140 pairs from 72 notices | Review proposals only; not gold and not a yield estimate |

The remaining parser counts are 32 location-plus-new, 1,194 numeric/symbolic, 1,231 metadata/nonpropositional, 36 semantic-unaligned, and 925 unusable/ambiguous. The rule proposals span eight extraction patterns; exact counts are in `pair_extraction_summary.json`.

## Interrupted work

Qwen2.5-14B was configured as an optional recall aid over the 582 exact-replacement notices. The process was terminated before the run completed to stop compute consumption. Because the program commits outputs only after all batches finish, no `llm_pair_proposals.jsonl`, raw generations, or summary exists. Therefore there is no LLM-extractor result to interpret, and the 140 rule candidates are the only current proposal set.

## Reproducibility and storage

- `data/raw/e003/sample.json` freezes sample IDs, seed, parent-frame hash, and deterministic replacement.
- `results/e003/manifest.json` records counts plus hashes for downloaded/parsed artifacts.
- NCBI XML and the 4,000-notice parsed cache are ignored because they are reproducibly downloadable/generated and total about 75 MB.
- `data/processed/e003/pair_candidates.jsonl` is the compact, versioned proposal artifact; CSV review views are generated locally and ignored.

## Resume point

Resume at E003c only if model-assisted recall justifies its compute. Otherwise review the 140 deterministic proposals first. In either route, proposal merge, manual gold verification, linked-original X-present/Y-absent validation, question construction, and the E004 free-generation experiment remain unstarted. The ordered protocol and claim/stop rules are in [EXPERIMENTS.md](../../EXPERIMENTS.md).
