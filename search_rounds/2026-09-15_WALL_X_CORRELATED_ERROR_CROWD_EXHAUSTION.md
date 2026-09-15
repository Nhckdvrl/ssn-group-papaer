# WALL-X — Correlated Errors and the Wisdom of LLM Crowds

Date: 2026-09-15
Status: EXHAUSTED AS A STANDALONE GENERATOR

## Mother question
When individual agent accuracy is held fixed, how does dependence among their errors determine whether voting, selection, or debate can yield collective improvement?

## Old ancestry
The question predates LLMs: Condorcet-style jury results, ensemble theory, and bias–variance–covariance analyses all make independence or error correlation load-bearing for collective gain.

## Direct modern ownership
- ICML 2025, *Correlated Errors in Large Language Models*, evaluates 350+ models and directly measures substantial shared-error structure, including correlations induced by shared architecture/provider and strong correlations even across strong heterogeneous models. It also studies downstream consequences.
- ACL Findings 2026, *Demystifying Multi-Agent Debate: The Role of Confidence and Diversity*, theoretically and empirically makes initial viewpoint diversity and calibrated confidence central to debate success; homogeneous agents with uniform updates cannot reliably improve expected correctness.
- 2026 work on diversity collapse / interaction tax studies how communication itself erases useful diversity in multi-agent teams.

## Why no candidate
A decisive experiment that fixes marginal accuracy while varying error correlation would be clean, but it is now a direct descendant of an active program rather than an unowned scientific question. Moving to another benchmark, larger agents, or another aggregation rule is not enough.

## Anti-resurrection
Do not revive as:
- same-model vs different-model voting;
- diversity-aware debate;
- correlated-error-adjusted majority vote;
- error overlap as explanation of ensemble gain;
- more agent-count scaling under correlated errors;
- interaction erases diversity;
- persona prompting as a diversity source.
