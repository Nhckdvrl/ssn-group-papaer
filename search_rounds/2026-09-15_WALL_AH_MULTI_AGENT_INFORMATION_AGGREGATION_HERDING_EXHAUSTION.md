# WALL-AH — Multi-agent debate: information aggregation vs herding

Date: 2026-09-15
Status: EXHAUSTED / DIRECT PROGRAM EXISTS

## Mother question
Classical collective-intelligence theory values independent judgments because their errors can cancel, while social-learning theory warns that observing others can create conformity, information cascades, and herding. Multi-agent LLM debate simultaneously claims benefits from diversity and from communication. Does communication aggregate genuinely independent information or destroy it by inducing social copying?

## Direct-owner audit
The core explanatory distinction is already actively studied in LLM multi-agent debate.

- Zhu et al., ACL Findings 2026, *Demystifying Multi-Agent Debate: The Role of Confidence and Diversity*, directly grounds MAD in human deliberation/collective decision theory. It identifies diversity of initial viewpoints and calibrated confidence communication as the two missing mechanisms in vanilla MAD, develops theory for homogeneous agents/uniform updates, and compares against majority vote.
- ACL Findings 2025 empirically studies group conformity in multi-agent LLM systems, showing alignment with numerical majorities and high-status/intelligent agents.
- 2026 work explicitly decomposes answer convergence with counterfactual conditions into spontaneous instability, stance-induced conformity, and reasoning-induced persuasion; reported conformity is often harmful (correct-to-wrong flips dominate in relevant settings).
- Free-MAD and related work already introduce anti-conformity/consensus-free protocols motivated by the same failure mode.

## Verdict
No L-series. Wisdom-of-crowds versus herding is now a direct explanatory program in MAD, not an unowned old-theory bridge.

## Anti-resurrection
No:
- debate vs majority vote;
- diversity as the missing mechanism;
- conformity/correct-to-wrong flip rate as novelty;
- information cascades in generic LLM debate;
- confidence-weighted debate as a new mechanism;
- new tasks/models/protocols demonstrating the same aggregation–conformity tradeoff.
