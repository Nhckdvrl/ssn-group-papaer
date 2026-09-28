# L17 — Related Work and Novelty Audit

Updated: 2026-09-11.

## Locked paper identity

> **What is the unit of rapid in-context speaker adaptation in speech LLMs: lexical/contextual bias, a global talker state, or sublexical acoustic–phonetic recalibration that transfers to unseen words?**

Do not broaden this to generic speech ICL, audio-vs-text attribution, or speaker adaptation performance.

## 1. Mother phenomenon — Roll et al., EMNLP 2025 Main

*In-Context Learning Boosts Speech Recognition via Human-like Adaptation to Speakers and Language Varieties* establishes the mother phenomenon in Phi-4 Multimodal.

What it owns:

- interleaved audio–transcript ICL for ASR;
- substantial WER reduction from a few examples;
- same-speaker vs different-speaker comparisons;
- strongest same-speaker advantage around 4–6 shots;
- the interpretation that early adaptation may be speaker-specific acoustic calibration and longer-context adaptation may become variety-level.

What it does **not** establish:

- same-speaker and different-speaker context are not transcript-matched; examples are randomly sampled from the relevant speaker pools;
- it does not hold demonstration text fixed while changing only who spoke it;
- it does not test transfer to unseen lexical items conditional on whether the relevant phonetic contexts were observed;
- it does not distinguish a speaker-global state from sublexical recalibration;
- the released repository explicitly lists understanding the precise adaptation mechanisms as future work.

Thus the parent paper supplies a strong phenomenon and a hypothesis, not the answer to L17.

## 2. Wang et al., ICASSP 2024 — Whisper speech ICL

*Can Whisper Perform Speech-Based In-Context Learning?* establishes test-time SICL for dialect, speaker and continuous speech recognition. It also reports analyses connected to phonological variation and dialect-specific lexical nuances.

Collision risk: high if L17 is stated as `does speech ICL use phonology or lexicon?`.

Surviving delta: L17 is not a component-importance inventory. It asks for the **generalization unit of talker adaptation** under an intervention where the exact same transcript is spoken by the target vs another speaker and then tests whether the target-speaker benefit transfers selectively to unseen words sharing sublexical contexts. The key estimand is the speaker-match × phonetic-coverage interaction, not general dialect phonology or lexical effects.

## 3. Li & Niehues, Findings ACL 2026 — multimodal ICL for low-resource ASR

*Multimodal In-context Learning for ASR of Low-resource Languages* directly separates text-only demonstrations from paired audio–text demonstrations, uses Phi-4 and Qwen3-Omni, studies attention over the two modalities, and finds an overall bias toward text.

This paper **owns generic audio-vs-text modality attribution**. Therefore L17 dies if its takeaway becomes merely `text matters more than audio` or `both modalities contribute`.

Surviving delta:

- their scientific target is learning unseen languages / low-resource ASR;
- they do not study a repeated talker with matched lexical content;
- they do not ask whether rapid speaker adaptation generalizes by observed phonetic context versus a global talker state;
- attention allocation is not the decisive evidence for L17.

## 4. TICL / TICL+ and example selection

Recent SICL work shows semantic text retrieval is useful and, for children's speech, adding acoustic reranking can further improve example selection.

These papers own a large part of the generic `pick better speech examples` method space. L17 therefore cannot sell `semantic + acoustic retrieval` as its novelty.

A later context-selection experiment is allowed only as a **prediction/consequence** of the scientific answer: e.g. if recalibration is sublexical, diagnostic phone-context coverage should matter beyond semantic KNN and generic acoustic similarity.

## 5. SALSA and supervised speech adaptation

SALSA (2026) learns steering activations for speech-aware LLM adaptation and reports that steering later encoder layers is especially effective, interpreting this as adaptation of higher-level acoustic/phonetic representations.

This owns neither in-context talker adaptation nor its generalization unit, but it makes `the encoder / later layers contain the adaptation` an insufficient paper identity. L17 must not mutate into layer localization.

## 6. Speech-ICL mechanism work in generation

2026 work on speech-language-model ICL in TTS studies acoustic features, linguistic structure and induction heads, including causal ablation of induction heads.

This means generic `speech ICL uses induction heads / acoustic features` is already a live mechanism parent. L17 remains distinct because its object is **recognition-side talker adaptation and transfer of a learned talker mapping to unseen lexical material**.

## 7. Classic human scientific parent

Human talker-adaptation and perceptual-learning work predates LLMs and supplies the scientific alternatives rather than a post-hoc taxonomy.

Relevant questions include:

- whether listeners normalize the incoming signal or adjust lexical/phonological representations;
- whether adaptation is talker-specific or transfers across talkers/accents;
- whether lexically guided evidence recalibrates sublexical phonetic categories;
- how far learning generalizes beyond the words heard during exposure.

L17 asks whether a modern speech LLM that is already claimed to show human-like adaptation implements an analogous generalization structure.

## Strongest reviewer compression

> Roll 2025 already shows speaker adaptation; Wang 2024 shows speech ICL can absorb phonological and lexical information; Findings ACL 2026 separates text/audio context; TICL+ combines semantic and acoustic selection. L17 is only a finer ablation of the same effect.

## Strongest surviving contribution

That compression misses the exact inference. None of those works establishes **what property learned from one talker transfers to a new utterance when lexical content is held fixed across the acoustic donor**. The proposed design creates a controlled dissociation unavailable in random example selection:

> identical demonstration words + different speaker acoustics × target-relevant phonetic coverage + unseen target words.

The key scientific answer is whether rapid speech-LLM adaptation behaves like sublexical phonetic recalibration, a global talker state, or linguistic contextual biasing. Those accounts make different predictions under the matched design.

## Internal semantic negative-memory audit

Searched `ssn-group-papaer`, `failed/KILLED_LEDGER.md`, current/archived candidate space, and `Interpretability-try` with speech/speaker/accent/phonetic/adaptation semantic terms.

Closest internal item: **K163 — ASR Transcript as Necessary Intermediate Representation**. It asks whether a transcript bottleneck is necessary versus direct end-to-end spoken interaction. That is a different RQ, estimand, intervention, and reviewer takeaway.

No historical project was found on:

- in-context speaker/talker adaptation;
- acoustic–phonetic recalibration;
- lexical versus speaker-specific information in speech ICL;
- talker-generalization units.

Verdict: **no internal semantic collision found**.

## Anti-L12 / L13 future-identity audit

Prechecked natural claim evolution:

- `sublexical recalibration exists` → viable only with matched transcript and unseen-word transfer; not generic audio contribution;
- `global speaker state dominates` → remains same locked RQ; full study requires speaker-vs-variety prediction, not a new probe paper;
- `text/context dominates` → remains a test of the human-like adaptation claim; forbidden to mutate into generic MICL modality bias;
- `better context selection` → supporting consequence only, because semantic/acoustic retrieval is already owned;
- `encoder/layers implement adaptation` → supporting mechanism only, because encoder steering/localization is crowded.

Current novelty verdict: **PILOT-AUTHORIZED, E01 only.** Full-study promotion requires E01 to resolve the locked scientific accounts and a refreshed 2026 literature audit before scaling.
