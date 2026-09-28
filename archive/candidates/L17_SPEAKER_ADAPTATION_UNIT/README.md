# L17 — What Does a Speech LLM Learn About a Speaker?

**Status:** **PILOT-AUTHORIZED — E01 only**  
**Date:** 2026-09-11  
**Target:** ACL / EMNLP / NAACL Main

## Locked research question

> **When a speech LLM improves after a few transcribed examples from one speaker, what actually generalizes to new utterances: a speaker-global state, a sublexical acoustic–phonetic mapping, or mainly lexical/textual context from the demonstrations?**

Plain example:

> After hearing several transcribed utterances from a Korean-accented English speaker, the model recognizes a new word from that same person better. Did it learn **how this speaker realizes sounds**, did it merely learn a global speaker/accent identity, or did the transcripts simply make likely words easier to guess?

The paper is **not** another `speech ICL improves WER` study. That phenomenon is already established. The scientific object is the **unit of rapid adaptation / generalization**.

## Why this question is live

Roll et al. (EMNLP 2025 Main) show a large and stable mother phenomenon in Phi-4 Multimodal: about 50 seconds of audio–transcript context reduces WER substantially; same-speaker examples are especially useful at intermediate shot counts. They interpret the pattern as an early speaker-specific acoustic calibration followed by broader variety-level adaptation, but their same- vs different-speaker examples are randomly sampled rather than transcript-matched. Their released paper/code explicitly leaves the precise adaptation mechanism open.

This is a classic scientific question rather than an invented LLM taxonomy. Human speech-perception work has long asked what talker adaptation learns: signal normalization, a global talker model, lexical adjustment, or sublexical phonetic recalibration that transfers to unseen words.

## Competing accounts

### A — sublexical acoustic–phonetic recalibration

The model learns how this speaker maps acoustic realizations onto phonetic categories. Speaker-specific benefit should therefore transfer to **unseen words** especially when demonstrations cover the phonetic contexts needed by the target.

Primary prediction: a positive interaction between **speaker match** and **phonetic-context coverage** under zero lexical overlap.

### B — global talker / accent conditioning

The examples establish a speaker- or accent-level state, but the adaptation is not tied to the specific sublexical patterns observed in the examples.

Primary prediction: same-speaker audio helps, but its benefit is largely insensitive to target-relevant phonetic coverage once amount of context is matched.

### C — lexical / textual contextual biasing

Much of the apparent adaptation comes from transcript-side lexical, orthographic, or language-model information rather than learning the speaker’s realization system.

Primary prediction: text-only demonstrations recover most of the gain; once demonstration transcripts are held exactly fixed, same-speaker versus other-speaker audio contributes little and phonetic-coverage interactions are weak.

These are answers to the same RQ. The project does not need one preselected effect to exist.

## Natural substrate

Primary: **L2-ARCTIC**, with CMU-ARCTIC as a clean native-speech corroboration axis.

Why this substrate is unusually useful:

- real recorded speech and human transcripts;
- many utterances per speaker;
- repeated scripted material across speakers enables **the identical demonstration transcript to be rendered by different speakers**;
- L1/accent and speaker metadata allow target-speaker vs same-variety other-speaker comparisons;
- orthographic gold supports ordinary WER; canonical pronunciations allow deterministic phone-context coverage without LLM-generated gold.

The original EMNLP 2025 code already loads L2-ARCTIC, CMU-ARCTIC, HEC and Speech Accent Archive and provides a reproducible Phi-4-MM ICL pipeline. Reuse it rather than rebuild the task.

## E01 — authorized bounded pilot

**Goal:** decide whether the established speaker-adaptation gain is speaker-global, sublexically targeted, or mostly textual/contextual.

Use Phi-4-MM and the mother paper's ordinary ASR prompt. For each target utterance, construct paired demonstration sets with **zero target content-word overlap** and the same number/duration of examples.

Factor 1 — demonstration audio source:

1. target speaker;
2. another speaker from the same L1/variety reading the **same demonstration transcripts**;
3. text-only version of those same transcripts.

Factor 2 — target-relevant phonetic coverage:

1. HIGH: demonstrations maximize coverage of target phone bigrams/trigrams;
2. LOW: demonstrations minimize that coverage subject to length/lexical constraints.

The transcript set is identical across speaker-source conditions. Target audio and reference are identical across every condition.

Primary statistics:

1. ordinary WER change from zero-shot;
2. speaker-match effect: `WER(other-speaker) - WER(same-speaker)`;
3. key interaction: `(speaker-match effect in HIGH) - (speaker-match effect in LOW)`;
4. phone-level error rescue on target phone contexts seen vs unseen in demonstrations, after G2P of reference/hypothesis;
5. text-only recovery fraction relative to multimodal ICL.

Pilot scope: a predeclared subset with enough same-transcript speaker pairs; 4–6 shots is the first target regime because the mother paper reports its strongest same-speaker advantage there. Do not scan shot counts for the best sign.

## Hard pre-run data gate

Before model inference, verify programmatically:

- the chosen speakers truly share the same scripted demonstration transcripts;
- every target has enough HIGH and LOW candidate sets under zero content-word overlap;
- HIGH and LOW phone coverage are well separated while total words/audio duration are matched;
- speaker-source conditions use exactly the same transcript IDs;
- no target utterance itself appears in the context;
- primary independent unit is speaker, not repeated generations.

If these constraints cannot be satisfied at reasonable scale, stop rather than manufacture synthetic speech.

## E01 decision map

- **A-like interaction:** speaker match matters selectively when target-relevant phone contexts were exposed → promote `phonetic recalibration / sublexical generalization` for a second-model replication and finer phonetic analysis.
- **B-like main effect without interaction:** adaptation is talker-global rather than pattern-specific → retain the same RQ; next work must distinguish speaker identity from accent/variety conditioning, not rename the paper as a generic hidden-state mechanism.
- **C-like text dominance:** the human-like speaker-adaptation interpretation is overstated; multimodal examples mainly provide linguistic context → retain the same RQ and test whether the conclusion replicates across Phi-4/Qwen3-Omni. Do not fall back to generic `text is important in MICL`, which ACL Findings 2026 already owns.
- **No reproducible ICL benefit at all under the matched design:** archive. Do not search for a weaker model or a different prompt to rescue the story.

## Anti-L12 / anti-L13 identity fence

The following are **not** authorized fallback identities:

- generic audio-vs-text modality attribution;
- generic attention analysis;
- `speech ICL works` / another ASR benchmark;
- generic acoustic example retrieval;
- another semantic+acoustic KNN method;
- speaker embedding probing;
- `later encoder layers matter`;
- prompt engineering;
- weak-model-only adaptation;
- a method paper whose scientific claim is merely better WER.

Any move to those identities requires fresh selection/novelty review.

## Pre-mortem claim-mutation stress test

Natural successful development paths were checked before authorization:

1. **phonetic recalibration** → distinct from existing SICL performance papers because it requires matched-transcript speaker swaps plus transfer to unseen lexical items and target-relevant phone contexts;
2. **global talker conditioning** → still answers the locked unit-of-generalization RQ, but must be distinguished from ordinary speaker identification/embedding work before full-study promotion;
3. **lexical/text dominance** → scientifically meaningful only as a revision of the claimed human-like speaker adaptation under a matched design; it may not mutate into generic MICL modality analysis.

The paper survives E01 only if the result supports one of these locked scientific accounts without requiring a new headline object.

## Main-level development path if E01 is informative

1. reproduce with a second architecture (Qwen3-Omni or another open speech LLM supporting interleaved MICL);
2. separate talker-specific from variety-level generalization using same-L1 and cross-L1 speaker donors;
3. test a prediction derived from the identified unit, e.g. context selection by **diagnostic phonetic coverage** versus semantic KNN / generic acoustic similarity, while preserving the same scientific claim;
4. validate on a second natural corpus, not merely more utterances from the same speakers.

The practical selection result is supporting consequence, not the source of novelty.

## Current verdict

```yaml
natural_question: PASS
established_mother_phenomenon: PASS
internal_semantic_collision: PASS_NO_COLLISION_FOUND
external_parent_ownership: PASS_WITH_CLOSE_NEIGHBORS
hard_gold: PASS
controlled_identification: PASS_SUBJECT_TO_DATA_GATE
outcome_robustness: PASS
anti_claim_mutation_stress_test: PASS
pilot: E01_ONLY
verdict: PILOT-AUTHORIZED
```
