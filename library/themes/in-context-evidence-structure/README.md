
# In-Context Evidence Structure

**Added:** 2026-10-05  
**Territory card:** [T16](../../../search/our-taste/TERRITORY_IN_CONTEXT_EVIDENCE_STRUCTURE_2026-10-05.md)  
**Workbench:** [in-context-evidence-structure](../../../workbench/in-context-evidence-structure/README.md)

## Scope
Frozen language models learning from examples whose statistical relation may differ:
- exchangeable / independent evidence;
- redundant / correlated evidence;
- noisy / conflicting evidence;
- evolving / regime-changing evidence;
- adaptive selection of set-like versus sequence-like aggregation.

## Central question
> When should demonstration order matter, and can the model tell the difference from the context itself?

## Explicit exclusions
- ordinary demonstration selection/order optimization;
- generic few-shot benchmark improvement;
- generic ICL forgetting;
- generic task vectors / representation probing;
- generic change-point detection;
- generic corrupted-demo robustness.

## Entry rule
Training-free first. Exact-gold procedural data and normative oracles before any white-box mechanism work.
