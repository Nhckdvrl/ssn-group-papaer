# L08 — Readout-Dimension / Compression Evaluation Route

**Status:** **REOPEN — SERIOUS / IDENTITY RECONSTRUCTED / E12 AUTHORIZED — 2026-09-14**  
**Former status:** REOPEN — SERIOUS (2026-09-13); ARCHIVED / NO-GO (2026-09-11)  
**Target:** ACL / EMNLP / NAACL Main

Current verdict: [`SELECTION_2026-09-14.md`](SELECTION_2026-09-14.md)
Current identity: [`MAINLINE.md`](MAINLINE.md)
Why it changed: [`AUDIT_2026-09-14_DEPTH_CONFOUND.md`](AUDIT_2026-09-14_DEPTH_CONFOUND.md)
Authorized experiment: [`E12_PREREGISTRATION.md`](E12_PREREGISTRATION.md)
Superseded: [`FRESH_SELECTION_2026-09-13.md`](FRESH_SELECTION_2026-09-13.md), [`MAINLINE_2026-09-10_SUPERSEDED.md`](MAINLINE_2026-09-10_SUPERSEDED.md)

> **What the 2026-09-14 pass found.** The 2026-09-13 reopening made the
> intervention-locus sign boundary (`C3.2`) load-bearing. Re-deriving it from the raw
> runs before spending compute showed it is **not identified by its own design**: the
> "controlled" contrast does not match answer depth, and the severity control that
> excluded "pruning simply hits harder" goes null once it does. `C3.2` is demoted.
> The variation it was matching away is the finding — retention decays with answer
> depth only when the answer is carried by the model's own generated prefix, in 14 of
> 15 conditions against 1 of 15, with 0 crossings. That law is now `C2`, and E12 is
> authorized to test it with provenance manipulated within item.

## Why the old archive no longer blocks Selection

The 2026-09-11 archive was not a null result and was not a direct-owner kill. L08 had undergone major paper-identity reconstruction during execution, and the stricter post-L12 workflow required the reconstructed claim to independently re-earn novelty and Main-level contribution.

That fresh audit has now been completed.

The surviving paper identity is not `which embedding dimensions matter?` and not the already-owned generic statement `multiple choice != open generation after pruning`.

The current RQ is:

> **When compression appears to damage one capability more than another, is the ordering a property of the capability — or of where the answer comes from at the moment it is emitted: recoverable from the prompt, or carried by the model's own generated prefix?**

The inherited evidence holds the item, the model, the intervention and the protocol fixed and varies only how deep into the generated trajectory the answer sits. Retention falls with that depth when the answer exists only in the tokens the model has already emitted, and does not fall at all when the answer stays readable from the prompt — 14 of 15 conditions against 1 of 15, five model families, three intervention families, zero crossings.

`evaluation protocol matters` is fully owned (Wen et al. 2026; Song et al., ICASSP 2026) and is claimed nowhere here. The live target is UniComp (EMNLP 2026 Main), whose `knowledge bias` headline compares a multiple-choice knowledge set against a free-form CoT reasoning set with no length control, and whose own unexplained GPQA-Diamond anomaly is this law's prediction. See `RELATED_WORK_AND_NOVELTY.md` §0 for the full owner audit.

## Preserved assets

All historical code, configs, experiment logs, results, audits, claims, and `MAINLINE.md` remain in this directory for reproducibility and evidence inheritance.

Historical results are **not retroactively declared confirmatory** by this status change.

**Authorized compute:** E12 only, under `E12_PREREGISTRATION.md`. Local environment
(`/home/xiang/miniconda3/envs/verl-clean/bin/python`), idle cards on
`fvcrc10/11/12/13/15`, **at most four cards at a time**.