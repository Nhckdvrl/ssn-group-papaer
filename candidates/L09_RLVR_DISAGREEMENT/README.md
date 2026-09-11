# L09 — RLVR Disagreement: Erased or Suppressed?

**Status:** **ARCHIVED / NO-GO — 2026-09-11**  
**Former status:** SERIOUS CANDIDATE / A-  
**Target:** historical ACL / EMNLP / NAACL Main candidate

> **Final archive decision:** stop this route before probes, patching, steering, or matched-RLVR training.

## Why archived

The behavioral parent is real: RLVR-style reasoning can worsen agreement with repeated human-annotation distributions. But the proposed erasure-versus-suppression explanation is now too compressed by neighboring work on RLVR entropy/diversity collapse, ambiguity representation, and post-training reorganization of latent policy states.

The strongest reviewer compression is:

> **“Known RLVR disagreement degradation + known policy/entropy collapse + hidden-state preservation/readout diagnostics on a human-disagreement target.”**

That does not mean the exact experiment has already been run. It means the likely positive results would be difficult to turn into an independently valuable Main-level explanatory principle. This route also has a high risk of repeating L12's failure mode: probe → patch → state intervention → increasingly abstract paper identity without a new owned scientific object.

A new, independently novel explanation would be required before the behavioral parent is reopened.

## Preserved assets

- `DATA_AND_GOLD.md`
- `RELATED_WORK_AND_NOVELTY.md`
- `RESEARCH_PLAN.md`

**No current experiment is authorized from this package.**