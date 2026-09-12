# 2026-09-12 — Continued Topic Search II

**Target:** ACL / EMNLP / NAACL Main  
**Rule:** multi-paper pressure preferred; anti-resurrection first; no survivor quota.

## Rejected in this round

### Local step validity vs global proof validity

**RQ:** When an LLM verifier judges every reasoning step as locally plausible, does it actually verify a globally valid proof object, including acyclic dependency, premise scope, and non-circularity?

**Why we cannot do it:** ACL 2026 *Hard2Verify* already identifies conflating local step validity with global proof correctness as a major verifier failure and explicitly includes circular reasoning / invalid setup; 2026 research-level proof-verification work further compares global checking against strict step-context verification. The intended local-vs-global parent is therefore directly occupied.

**Decision:** KILL CURRENT FORM / fresh collision. Do not create a new candidate.

### Speech-LLM gain beyond transcripts

**RQ:** When an end-to-end Speech LLM outperforms an ASR→LLM cascade, is the gain due to linguistic information absent from transcripts, or mainly speaker/channel/paralinguistic shortcuts?

**Why we cannot do it:** 2026 work already directly tests when Speech LLMs are behaviorally/mechanistically equivalent to cascades, while CP-Bench, S2S-Arena, and Unified Audio Schema explicitly separate transcript-level, paralinguistic, and non-linguistic information. The proposed decomposition is therefore already a current speech-LLM parent rather than an independent Main-level question.

**Decision:** KILL CURRENT FORM.

### Function-preserving reparameterization vs unit-level interpretability

**RQ:** If a Transformer is changed by a function-preserving symmetry, do claims that a particular neuron/head/coordinate is intrinsically important remain identifiable?

**Why we cannot do it:** Transformer parameter-space permutation/rotation symmetries are already established, and 2026 work explicitly studies representation measurements under function-preserving reparameterizations. This also strongly overlaps the active L22 identifiability theme; broadening L22 from embedding coordinates to generic interpretability units does not automatically create a new paper identity.

**Decision:** DO NOT CREATE NEW CANDIDATE; overlaps active L22 / current symmetry-identifiability literature.

### Exact n-gram exposure → frequency vs contextual diversity

**RQ:** With internet-scale exact n-gram counts, can we determine whether language-model lexical/factual learning is governed more by raw exposure count or by diversity of contexts?

**Why we cannot do it:** TACL 2024 already models LM learning curves using frequency-adjusted contextual diversity, and 2025 controlled pretraining work directly manipulates contextual diversity to study factual and OOD generalization. Infini-gram mini makes exposure easier to measure, but does not create a new scientific parent.

**Decision:** KILL CURRENT FORM.

### Document-level fairness vs independent-source fairness in multi-document summarization

**RQ:** If one viewpoint is repeated across many near-duplicate documents, should a fair summary represent document counts or independent information sources?

**Why we cannot do it:** NAACL 2025 *Coverage-based Fairness in Multi-document Summarization* is itself motivated by redundancy invalidating proportional document-level representation and proposes Equal Coverage / Coverage Parity to account for it. Near-duplicate reposting is a narrower redundancy case unless a qualitatively different independently grounded source variable is found.

**Decision:** KILL CURRENT FORM.

## Duplicate / previously killed parents encountered again

### Study/report multiplicity in evidence synthesis

**RQ:** Should multiple papers from one underlying clinical study count as multiple pieces of evidence?

**Why not reopen:** This is the existing L06 study-identity parent. Recent systematic-review work further clusters multiple reports belonging to one study and explicitly warns that paper-level handling overweights multiply published studies.

**Decision:** DUPLICATE HIT ON L06 — no new K ID.

### Generic contamination causality

**RQ:** Does benchmark exposure causally raise evaluation performance, rather than merely correlate with it?

**Why not promote:** Controlled contamination-injection work already manipulates contamination amount/stage/format and measures score inflation; later work studies persistence/re-emergence after post-training. The causal parent is occupied.

**Decision:** REJECT / occupied parent; no new candidate.

### Rubric reasoning vs final judge policy

**RQ:** Do criterion-level judgments/rationales actually causally determine an LLM judge's final score?

**Why not promote:** Recent LLM-judge work directly studies rubric interference, criterion-level meta-evaluation, and dependency/redundancy between rubric dimensions. The natural decomposition is already crowded and increasingly directly owned.

**Decision:** KILL CURRENT FORM.

## Round status

No new survivor promoted in this round. Current active portfolio remains unchanged. Continue broad search rather than lowering the bar.
