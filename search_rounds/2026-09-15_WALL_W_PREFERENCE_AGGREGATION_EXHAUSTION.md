# WALL-W — Scalar Reward under Heterogeneous Preference Aggregation

Date: 2026-09-15
Status: EXHAUSTED AS A STANDALONE GENERATOR

## Mother question
If each individual annotator has a well-defined scalar utility, does pooling heterogeneous pairwise preferences still admit any single scalar reward? If not, what does standard RLHF/DPO learn when the population preference relation is not rationalizable by one utility function?

## Why this was a real old problem
The mother problem predates RLHF. Random-utility / Bradley–Terry style models assume pairwise choices can be represented through differences in a scalar utility. Social-choice theory studies what happens when individually coherent preferences are aggregated and shows that aggregate relations can violate properties required by a single ordering.

## Direct modern ownership
The residual is now directly occupied.

- Work on RLHF as social choice explicitly treats reward modeling as preference aggregation rather than ordinary noisy regression.
- AAAI 2025, *Axioms for AI Alignment from Human Feedback*, argues that Bradley–Terry–Luce reward learning and broad generalizations fail basic social-choice axioms and develops alternative aggregation rules.
- 2026, *The Representation–Rationalizability Tradeoff in Reward Learning*, directly starts from heterogeneous annotators whose pooled pairwise preferences can contain Condorcet cycles, so no scalar reward can satisfy all comparisons. It derives an exact tradeoff between representation richness and aggregation inconsistency, and extends the result to DPO.
- Related work already studies heterogeneous feedback through personalization, reward aggregation, probabilistic opinion pooling, Nash / non-transitive preference optimization, and social-choice formulations.

## Strongest residual considered
> Suppose every individual annotator is internally scalar-rationalizable, but the pooled population is not. Which statistical projection does standard reward learning select, and can optimizing that projection produce a policy preferred by no constituent annotator?

This initially looked stronger than generic "preferences can be cyclic" because the non-rationalizability is created by aggregation rather than individual irrationality.

## Why it is not a new Main-level question
The 2026 representation–rationalizability work already owns essentially this object: heterogeneous individually structured preferences, pooled cycles, impossibility of a single scalar reward, the projection induced by a learned representation, and the extension to DPO. Social-choice RLHF and axiomatic aggregation work also own the broader intellectual framing.

A new paper that merely moves from synthetic to larger LLM preference datasets, changes the aggregation rule, or measures more cycles would be a descendant of an active program rather than a new scientific question.

## Anti-resurrection
Do not revive as:
- "Bradley–Terry is wrong for human preferences";
- annotator heterogeneity causes cycles;
- scalar reward cannot represent all raters;
- social-choice axioms for RLHF;
- DPO under non-transitive preferences;
- majority/Borda/Nash aggregation comparisons;
- real-data validation of pooled non-rationalizability;
- same question with LLM judges instead of humans.

A future reopening would require a distinct older theory that fixes a new conditioning variable and yields opposite predictions on the same aggregation quantity, not another aggregation method.
