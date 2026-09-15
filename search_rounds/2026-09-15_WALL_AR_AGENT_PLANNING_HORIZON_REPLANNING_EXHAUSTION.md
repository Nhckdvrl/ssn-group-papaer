# WALL-AR — LLM-agent planning horizon: full plan vs feedback-driven replanning

Date: 2026-09-15
Status: EXHAUSTED / ACTIVE DIRECT PROGRAM

## Mother question
Explicit long-horizon plans can improve global coherence, but in interactive environments every new observation can invalidate future plan steps. How should an agent trade off open-loop planning horizon against receding-horizon feedback/replanning? Does plan value decay predictably with transition uncertainty or observation arrival rate?

## Direct-owner audit
The exact planning-horizon axis is already being isolated in LLM-agent research.

- Otani et al. (CAIS 2026), *Do Agents Need to Plan Step-by-Step? Rethinking Planning Horizon in Data-Centric Tool Calling*, holds environment/tools fixed and swaps only single-step planning versus full-horizon planning with lazy replanning, analyzing task topology and tool robustness.
- 2026 long-horizon-agent work explicitly imports receding-horizon control/MCTS and limited commitment, arguing that plans should commit only to near-term actions and replan after observations.
- Contemporary stale-plan/state-aware runtime work directly studies when fresh observations invalidate previously generated plans.

## Verdict
No L-series. Adding transition uncertainty or a replanning-frequency sweep would be a natural extension of an existing planning-horizon/MPC program rather than an independent inherited scientific question.

## Anti-resurrection
Do not revive as:
- ReAct vs plan-and-execute;
- full-horizon vs single-step planning;
- replanning-frequency sweeps;
- stale-plan failures in generic agents;
- MPC/receding-horizon control imported into LLM agents as novelty.
