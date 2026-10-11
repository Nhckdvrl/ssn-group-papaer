# L17 — Pilot Card

**Candidate:** What Does a Speech LLM Learn About a Speaker?  
**Status:** PILOT-AUTHORIZED — **E01 only**  
**Date:** 2026-09-11

## Locked RQ

> When a speech LLM improves after a few transcribed examples from one speaker, what actually generalizes to new utterances: a speaker-global state, a sublexical acoustic–phonetic mapping, or mainly lexical/textual context from the demonstrations?

## Mother phenomenon

Roll et al. (EMNLP 2025 Main) establish robust in-context speaker/variety adaptation for Phi-4 Multimodal, with the strongest same-speaker advantage around 4–6 demonstrations. The phenomenon is inherited; reproducing it is not the contribution.

## Accounts

- **A — sublexical recalibration:** speaker-specific benefit transfers preferentially when demonstrations cover target-relevant phone contexts, even though target words never appeared.
- **B — global talker conditioning:** same speaker helps broadly, largely independent of target-relevant phone coverage.
- **C — lexical/textual contextual bias:** transcript-only context recovers most of the benefit; matched same-vs-other-speaker audio contributes little.

## E01 — Frozen pilot

Primary dataset: L2-ARCTIC.

For a fixed target utterance and fixed demonstration transcripts, cross:

1. **audio source**
   - target speaker;
   - another same-L1/variety speaker reading the exact same demonstration transcripts;
   - transcript-only;
2. **phonetic coverage**
   - HIGH target-phone bigram/trigram coverage;
   - LOW coverage.

Main slice requires zero target content-word overlap with the demonstrations.

Primary model: Phi-4 Multimodal, using the mother paper's normal ASR/ICL interface. Primary shot regime: 4–6 shots; freeze one count after the data-feasibility audit rather than scanning for the best sign.

## Primary outcomes

1. WER against human transcript gold.
2. `SA_p = WER(other_speaker,p) - WER(same_speaker,p)`.
3. Primary discriminating interaction: `SA_HIGH - SA_LOW`.
4. Phone-context rescue on seen-vs-unseen canonical phone contexts.
5. Text-only recovery fraction.

## Hard data gate before GPU

PASS only if all are true:

- enough target speakers have a same-L1 donor who recorded the same scripts;
- exact demo transcript IDs can be held fixed under the speaker swap;
- target utterance never occurs in context;
- zero target content-word overlap is feasible at useful scale;
- HIGH and LOW phone-coverage sets are clearly separated while shot count, transcript length and audio duration remain reasonably matched;
- primary inference has a nontrivial number of independent speakers, not merely many utterances from two speakers.

If not, **STOP / RECONSTRUCT DATA**, not synthetic-TTS rescue.

## Interpretation map

### A-like result

`SA_HIGH > SA_LOW` robustly under unseen target words.

Interpretation: rapid adaptation is at least partly sublexical/talker-specific acoustic–phonetic recalibration.

Next authorized decision: return to selection for second-family replication + finer phonetic generalization. Do not jump to arbitrary hidden-state scans.

### B-like result

Robust same-speaker benefit but little HIGH-vs-LOW interaction.

Interpretation: adaptation is more global speaker/talker conditioning than pattern-specific recalibration.

Next decision: distinguish speaker identity from variety/accent state under the same paper identity.

### C-like result

Text-only recovers most improvement and matched same-vs-other-speaker audio has little residual effect.

Interpretation: the apparent human-like speaker adaptation is largely linguistic contextual bias rather than talker-specific recalibration.

This still answers the locked RQ. It may **not** mutate into a generic `text dominates multimodal ICL` paper because that parent is occupied.

### No mother effect under matched design

If neither same-speaker nor text/audio conditions reproduce a meaningful ICL benefit under the frozen setup, **ARCHIVE**. Do not search weak models/prompts/shots for a rescue.

## Successful-result test

The strongest A-like result must establish more than correlation between speaker match and WER. The matched-transcript swap holds lexical context constant; unseen target words prevent trivial word repetition; the HIGH×LOW manipulation tests whether the speaker advantage follows target-relevant sublexical exposure. Together these distinguish A from B/C.

The strongest B-like result remains meaningful because it rules against sublexical coverage as the primary adaptation unit under the tested regime.

The strongest C-like result is meaningful only as a correction to the mother paper's speaker-adaptation interpretation, not as another modality-ablation paper.

## Anti-L12 / anti-L13 identity fence

Forbidden fallback identities without fresh selection:

- generic audio-vs-text attribution;
- generic attention/induction-head analysis;
- speaker embedding probing;
- layer localization;
- semantic/acoustic retrieval method;
- prompt engineering;
- `speech ICL improves ASR`;
- `one model family behaves differently`;
- a better-WER method with no scientific answer.

## Pilot budget

E01 is a **bounded identification pilot**, not a full paper program. First perform the no-GPU data audit. Then run only the frozen factorial subset needed to estimate the account-separating interaction. Full model/corpus expansion requires re-selection after E01.
