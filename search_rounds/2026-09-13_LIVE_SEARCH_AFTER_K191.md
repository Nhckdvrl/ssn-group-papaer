# 2026-09-13 — Live Search After K191

**Purpose:** persistent rolling log for the current search round so network interruption does not cause repeated rediscovery. Any seriously investigated dead route is recorded here immediately.

**Rule:** only `PILOT-AUTHORIZED` candidates are surfaced as actionable topics. `MAYBE` / `SERIOUS` / blocked ideas stay internal and are either killed or fully selected before user-facing promotion.

---

## Hook A — Final-layer hidden-state angular jump

**Status:** `UNDER OWNER ASSASSINATION`  
**Origin:** Shibata et al., Findings EACL 2026, *Suppressing Final Layer Hidden State Jumps in Transformer Pretraining*.

Observed mother phenomenon:
- many open-weight Transformer LMs show small angular displacement through middle layers but a disproportionately large jump at/near the final layer;
- the jump grows over pretraining/checkpoints;
- jump-suppressing regularization (JREG) reduces the phenomenon and modestly improves downstream performance;
- the parent interprets the jump as possible over-reliance on final layers / under-utilization of middle layers, but does not directly establish why this late reconfiguration emerges.

Primary source: https://aclanthology.org/2026.findings-eacl.64/

### Current assassination question

Before considering a candidate, test whether the jump is already explained by known output-interface / Pre-LN dynamics:
- residual-stream norm growth with depth;
- final RMSNorm + LM-head geometry;
- last-layer specialization for vocabulary/readout alignment;
- logit-lens / tuned-lens evidence that intermediate states require affine translation toward final readout;
- deep-layer redundancy / pruning literature;
- whether the apparent angular jump is a scale/normalization artifact rather than a distinct computation.

**Do not promote unless:** there remains a substantial unresolved causal inference after combining these owners, with a decisive operation whose success would not be an obvious consequence of existing work.
