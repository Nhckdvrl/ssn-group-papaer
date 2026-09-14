# WALL-Y — Value of Information for Clarification

Date: 2026-09-15
Status: EXHAUSTED AS A STANDALONE GENERATOR

## Mother question
When a task contains missing but queryable information, when should an agent act under uncertainty and when should it pay an interaction cost to ask a clarifying question?

## Old ancestry
This is a classical value-of-information / optimal experiment-design question, not an LLM-specific benchmark problem.

## Direct ownership
- ACL 2018 already used expected value of perfect information to rank clarification questions.
- NAACL Findings 2025 explicitly studies when an LM should ask for clarification and models utility via intent uncertainty.
- ACL 2026, *Value of Information: A Framework for Human–Agent Communication*, directly formulates clarify-or-commit as expected downstream utility gain minus communication cost.
- ACL Findings 2026, *Structured Uncertainty guided Clarification for LLM Agents*, applies EVPI to structured tool-parameter uncertainty and separates specification uncertainty from model uncertainty.
- 2026 work also documents a recognition–behavior gap: models can recognize ambiguity yet rarely ask, but this phenomenon now sits inside the active clarification/VoI program.

## Verdict
The old decision-theoretic question and the modern LLM operationalization are both directly occupied. Another domain, tool API, benchmark, uncertainty estimator, or clarification policy would be a descendant, not a new Main-level scientific question.

## Anti-resurrection
Do not revive as ambiguity detection, when-to-ask, ask-vs-act thresholds, expected value of clarification, tool-parameter disambiguation, or recognition-vs-clarification behavior unless an independent older theory yields a qualitatively different prediction on the same decision quantity.
