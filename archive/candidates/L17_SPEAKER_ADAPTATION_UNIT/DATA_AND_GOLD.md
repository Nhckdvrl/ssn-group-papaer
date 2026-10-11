# L17 — Data and Gold Contract

## Primary natural data

### L2-ARCTIC

Use the same real speech substrate already used by the EMNLP 2025 mother paper.

Required fields:

- audio;
- human reference transcript;
- speaker identity;
- speaker L1 / variety;
- utterance/script identity or a transcript-normalized key.

The key design advantage is repeated scripted material across speakers: the same textual demonstration can be supplied with different acoustic realizations while the target utterance stays fixed.

### CMU-ARCTIC

Use as a secondary native-English corroboration axis if the repeated-script matching is sufficient. It is not required for E01 existence/identification.

## Gold

Primary task gold: the dataset's human reference transcript.

Primary metric: normalized WER under one frozen normalization pipeline.

Secondary diagnostic: phone error rate / phone-context rescue obtained by applying one deterministic pronunciation mapping (CMUdict where available plus a frozen G2P fallback). G2P is not the scientific gold; it only partitions target units by canonical phone-context exposure. The load-bearing outcome remains transcript correctness.

No LLM-generated labels are permitted.

## Scientific units

- primary independent unit: **speaker**;
- target utterances are repeated observations nested within speaker;
- demo sets are matched interventions, not independent speakers;
- repeated generations under deterministic/greedy decoding do not create new scientific units.

Inference should use speaker-level paired aggregation / bootstrap or a mixed model with speaker as the top-level sampling unit.

## E01 construction

For each target speaker `s`, target utterance `u`, and matched donor speaker `s'` from the same L1/variety:

1. choose a fixed demo transcript set `D` that both `s` and `s'` recorded;
2. require no demo utterance equals `u`;
3. require zero target **content-word** overlap between `D` and `u` for the main generalization slice;
4. build `D_high` and `D_low` sets that differ in canonical target-phone bigram/trigram coverage while matching shot count, approximate total words and audio duration;
5. render each transcript set in three context conditions:
   - target-speaker audio + transcript;
   - other same-variety speaker audio + the identical transcript;
   - transcript-only context;
6. append the exact same target audio and ask for transcription.

The speaker swap must change **only the acoustic realization of the demonstrations**, never the demonstration words.

## Main estimands

Let `WER(c, p)` be WER for context source `c` and phone-coverage level `p`.

Speaker advantage at coverage `p`:

`SA_p = WER(other_speaker, p) - WER(same_speaker, p)`

Primary interaction:

`PHONETIC_INTERACTION = SA_HIGH - SA_LOW`

Text recovery fraction should compare text-only improvement with the paired-audio improvement using a denominator-safe predeclared formula.

At the token/phone level, separately estimate whether errors involving phone contexts observed in the demonstrations are rescued more often than errors involving unseen contexts, under zero lexical overlap.

## Data gate before inference

A script must report, before any model output is inspected:

- number of candidate target speakers and matched same-L1 donors;
- number/proportion of shared script IDs;
- feasible target utterances after zero content-word overlap filtering;
- HIGH vs LOW phone-coverage separation;
- balance in demo word count and audio duration;
- distribution of target baseline difficulty if a frozen mother-paper result can supply it without running new models.

Reject / redesign before compute if:

- shared transcript pairing is too sparse;
- phone coverage is almost deterministic from lexical overlap;
- HIGH and LOW sets cannot be matched without large length/difficulty imbalance;
- only a tiny handful of speakers contributes valid pairs.

Do **not** replace the failed natural pairing with TTS-generated voice swaps for the primary pilot.

## Leakage / contamination controls

- demo target transcript never appears verbatim in context;
- no same audio file appears in demo and query;
- transcript IDs, speaker IDs and audio paths logged for every cell;
- use one frozen normalization and G2P mapping before scoring;
- selection is based only on reference/demo metadata, never model predictions or observed WER.

## Why this identifies the question

A same-speaker benefit with random examples does not tell us what was learned. A text-only gain does not tell us whether speaker information matters. The load-bearing identification is the **matched transcript speaker swap** crossed with **sublexical coverage**:

- transcript fixed → lexical information fixed;
- speaker swapped → talker acoustics change;
- phone coverage varied with target words held unseen → tests generalization structure;
- target audio fixed → task evidence is unchanged.

This is the smallest comparison that separates the locked accounts.
