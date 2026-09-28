# L17 — Experiment Ledger

**Status:** E01 AUTHORIZED, NOT RUN  
**Date:** 2026-09-11

## E00 — Data-feasibility audit

**Compute:** no model inference.  
**Purpose:** verify that natural repeated-script speech supports the frozen matched intervention.

Required outputs:

- eligible target speakers and same-L1/variety donor speakers;
- exact shared script/transcript IDs;
- feasible target/demo cells after zero target content-word overlap;
- HIGH/LOW target-phone bigram/trigram coverage separation;
- word-count and audio-duration balance diagnostics;
- final frozen speaker/utterance/demo manifest and hash.

**Gate:** if the natural data do not provide enough valid matched cells, stop. Synthetic voice conversion/TTS is not an authorized replacement for the primary identification design.

## E01 — Matched-transcript speaker swap × phonetic coverage

**Status:** AUTHORIZED CONDITIONAL ON E00 PASS.

### Linked claim

The unit of rapid in-context talker adaptation can be distinguished among sublexical recalibration, global talker conditioning, and lexical/text contextual biasing.

### Fixed factors

- context audio source: target speaker / same-variety other speaker / text-only;
- target-relevant phonetic coverage: HIGH / LOW;
- exact demo transcripts fixed across speaker-source conditions;
- target audio fixed;
- target reference fixed;
- main slice: zero target content-word overlap;
- normal ASR ICL setting; no forced direct/no-reasoning manipulation.

### Model

Primary: Phi-4 Multimodal, compatible release used by the EMNLP 2025 mother-paper pipeline where available.

### Primary independent unit

Speaker.

### Primary metric

WER against human reference transcript.

### Primary contrast

`[WER(other,HIGH)-WER(same,HIGH)] - [WER(other,LOW)-WER(same,LOW)]`

### Secondary diagnostics

- same-speaker main effect;
- text-only recovery fraction;
- phone-context error rescue on demonstration-covered vs uncovered contexts;
- per-speaker heterogeneity;
- target baseline-difficulty stratification fixed independently of E01 outcomes if used.

### Account map

- positive speaker×coverage interaction → supports sublexical recalibration;
- same-speaker main effect with weak interaction → supports global talker conditioning;
- large text-only recovery + weak acoustic donor effects → supports lexical/text contextual bias;
- no meaningful ICL gain → archive current route.

### Invalid expansions before re-selection

Do not run:

- model zoo;
- arbitrary layer/probe scans;
- attention-head hunting;
- semantic/acoustic retrieval optimization;
- alternate shot-count search for a better sign;
- TTS/voice-clone primary replacements;
- fine-tuning/steering methods.

E01 first resolves the scientific account. Any material claim change triggers selection again.
