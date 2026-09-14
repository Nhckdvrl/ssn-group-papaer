# WALL-AM — Clarification: uncertainty vs value of information

Date: 2026-09-15
Status: EXHAUSTED / DIRECTLY OWNED

## Mother question
When should an interactive agent ask a clarification question rather than act? A common heuristic is to ask when model confidence is low. Classical Bayesian decision theory gives a sharper answer: information is valuable only insofar as it can change the optimal decision enough to justify its acquisition cost. High uncertainty therefore need not imply that asking is useful.

## Direct-owner assassination
This exact distinction is already directly owned in modern NLP/LLM agents.

- Dong et al., ACL 2026 Main, *Value of Information: A Framework for Human–Agent Communication*, explicitly criticizes confidence-threshold approaches and introduces a decision-theoretic VoI rule that balances expected utility improvement from clarification against user cognitive cost across multiple domains.
- Suri et al., Findings ACL 2026, *Structured Uncertainty guided Clarification for LLM Agents*, separates specification uncertainty from model uncertainty and uses Expected Value of Perfect Information over tool parameters to select questions and stopping decisions.
- Rao & Daumé III, ACL 2018, already used neural Expected Value of Perfect Information to rank clarification questions.
- EACL 2024 and NAACL Findings 2025 separately study when uncertainty should trigger clarification.

## Verdict
No L-series. The exact old-decision-theory correction—uncertainty is not equivalent to value of asking—is now an ACL 2026 Main framing and a broader active program.

## Anti-resurrection
Do not revive as:
- confidence threshold vs clarification utility;
- VoI/EVPI for tool-calling or other new agent domains;
- user-cost-aware clarification as novelty;
- structured uncertainty for asking questions;
- another clarification benchmark or training reward based on information gain.
