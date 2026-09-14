# WALL-AA — Predictive Turn Projection vs Reactive Endpoint Detection

Date: 2026-09-15
Status: EXHAUSTED AS A RESEARCH-TOPIC GENERATOR

## Mother question
Does fluent low-latency turn-taking arise by predicting/projecting an interlocutor's upcoming completion, or by reacting to observed silence/endpoints after they occur?

## Old ancestry
Human turn-taking work has long argued that sub-second response gaps require anticipatory projection from linguistic and prosodic cues rather than pure silence detection.

## Direct ownership
- SIGDIAL 2021 explicitly implemented projection of upcoming turn completion in incremental spoken dialogue systems.
- SIGDIAL 2022 used signal manipulations to study prosodic information used by Voice Activity Projection models.
- LREC-COLING 2024 studied multilingual Voice Activity Projection.
- EACL 2026 directly analyzes lexical and temporal information driving turn-taking predictions in full-duplex dialogue models.
- IWSDS 2026 explicitly compares silence-threshold reactive models with predictive VAP models and concludes that predictive mechanisms are required for the studied turn-taking behavior.

## Verdict
The anticipatory-vs-reactive contrast and cue decomposition are already an active direct program. A new full-duplex model, language, cue ablation, or latency benchmark would not constitute a new scientific question.

## Anti-resurrection
Do not revive as semantic endpointing vs VAD, predictive turn-taking, lexical/prosodic cue ablation, or full-duplex turn-completion projection for the Main-topic search.
