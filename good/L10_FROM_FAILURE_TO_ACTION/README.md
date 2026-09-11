# L10 — From Failure to Action

**Status:** **ARCHIVED / NO-GO — 2026-09-11**  
**Former status:** A / PILOT-AUTHORIZED / Rank 1  
**Target:** historical ACL / EMNLP / NAACL Main candidate

> **Final archive decision:** do not run L10-E01/E02 under the current paper identity.

## Why archived

The natural question remains attractive: a model may remember that an action failed and still repeat it. The proposed untouched-history decomposition (outcome memory → attribution → replacement policy → actual action) is methodologically clean.

Fresh ownership review, however, shows that recent tool-agent work already studies closely related diagnosis→correction→self-repair transitions after execution failures. Under the successful-result test, even the cleanest expected L10 outcome—memory/attribution/policy correct but action wrong, repaired by an explicit replacement instruction—can be compressed to a finer decomposition of an already-established self-repair gap rather than a new Main-level explanatory principle.

The released first pilot also contains only ten strict action-pair templates. More data or hidden-state analysis would not solve the contribution problem.

## Preserved assets

- `DATA_AND_GOLD.md`
- `RELATED_WORK_AND_NOVELTY.md`
- `RESEARCH_PLAN.md`
- `PILOT_CARD.md`
- scripts/configs/data prepared for the pilot

**No current experiment is authorized from this package.**