# WALL-AU — Turn-taking: semantic prediction vs acoustic/prosodic endpointing

Date: 2026-09-15
Status: EXHAUSTED AS STANDALONE GENERATOR

## Mother question
Human turn transitions are often too fast to be purely reactive, motivating predictive turn-completion models. In voice agents, does semantic/syntactic completeness provide causal information about turn yielding beyond acoustic silence and prosody, or are modern acoustic/prosodic signals already sufficient for the latency–false-interruption tradeoff?

## Direct-owner lineage
This is a longstanding spoken-dialogue research program rather than a new voice-LLM question.

- Maier, Hough & Schlangen, Interspeech 2017, *Towards Deep End-of-Turn Prediction for Situated Spoken Dialogue Systems*, explicitly contrasts reactive silence thresholds with predictive turn-taking and compares live lexical and acoustic feature sets under a common LSTM architecture, finding useful incremental language-model features and improved latency/cut-in behavior.
- Modern voice-agent systems already deploy semantic endpointing or multimodal acoustic+semantic turn detectors.
- Udupa et al. (2026), *Endpoint Anticipation for Low-Latency Spoken Dialogue*, explicitly shifts from reactive EOT detection to proactive forecasting and demonstrates speculative LLM/TTS execution before observed turn completion.
- Sharon et al. (2026-09-10), *Less can be More: What Aspects of Speech Drive End-of-Turn Detection*, performs a controlled acoustic/prosodic/semantic ablation and reports that acoustic+prosodic cues give the best accuracy-latency balance while adding text increases premature detections.

## Why the apparent modern tension is not enough
Production semantic-endpointing systems and the latest controlled result point in different directions, but the obvious conditioning variables are corpus, language, dialogue type, label construction, transcript latency, and evaluation policy. Reconciliation would therefore likely become dataset/regime characterization rather than a theory-first mechanism question.

## Verdict
No L-series. Scientifically relevant to the user's voice-agent engineering, but not a sufficiently unowned ACL-Main question under the current search bar.

## Anti-resurrection
Do not revive as:
- VAD vs semantic endpointing benchmark;
- acoustic/prosodic/text feature ablation;
- proactive endpoint anticipation as novelty;
- latency vs false interruption curves on a new language/domain;
- semantic EOT for the user's robot pipeline as a paper by itself.
