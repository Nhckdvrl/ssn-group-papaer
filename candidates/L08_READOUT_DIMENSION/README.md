# L08 — Readout-Dimension / Compression Evaluation Route

**Status:** **KILLED — MECHANISTIC MAIN ROUTE — 2026-09-14**

`Delta_refresh = +0.0000 [-0.102, +0.102]`; the preregistered kill rule fires.
Verdict and numbers: [`results/e13/RESULTS.md`](results/e13/RESULTS.md).
Stage 1 evidence, which stands: [`results/e12/PROGRESS.md`](results/e12/PROGRESS.md).  
**Former status:** REOPEN — SERIOUS (2026-09-13); ARCHIVED / NO-GO (2026-09-11)  
**Target:** ACL / EMNLP / NAACL Main

Current verdict: [`SELECTION_2026-09-14.md`](SELECTION_2026-09-14.md)
Current identity: [`MAINLINE.md`](MAINLINE.md)
Why it changed: [`AUDIT_2026-09-14_DEPTH_CONFOUND.md`](AUDIT_2026-09-14_DEPTH_CONFOUND.md)
Redesigned experiment, **not yet authorized**: [`E12_PREREGISTRATION.md`](E12_PREREGISTRATION.md)
Superseded: [`FRESH_SELECTION_2026-09-13.md`](FRESH_SELECTION_2026-09-13.md), [`MAINLINE_2026-09-10_SUPERSEDED.md`](MAINLINE_2026-09-10_SUPERSEDED.md)

> **What the 2026-09-14 pass found.** The 2026-09-13 reopening made the
> intervention-locus sign boundary (`C3.2`) load-bearing. Re-deriving it from the raw
> runs before spending compute showed it is **not identified by its own design**: the
> "controlled" contrast does not match answer depth, and the severity control that
> excluded "pruning simply hits harder" goes null once it does. `C3.2` is demoted.
> The variation it was matching away is what matters: depth sensitivity is **not** a
> generic property of long generation — 14 of 15 conditions on one side, 1 of 15 on the
> other, 0 crossings. That is motivation, not a result.
>
> **A same-day identification review then rejected the first E12 design** (a
> `capability × provenance` 2x2) because its arms changed the computation rather than
> isolating provenance. The object is restated as **trajectory-mediated compression
> damage** — how much of the damage arrives because the context a step conditions on was
> itself produced under the treatment — and the instrument is **prefix clamping**, which
> holds per-step damage fixed and varies mediation alone. No treatment compute is
> authorized until the Stage 1 runner passes its validation.

## Why the old archive no longer blocks Selection

The 2026-09-11 archive was not a null result and was not a direct-owner kill. L08 had undergone major paper-identity reconstruction during execution, and the stricter post-L12 workflow required the reconstructed claim to independently re-earn novelty and Main-level contribution.

That fresh audit has now been completed.

The surviving paper identity is not `which embedding dimensions matter?` and not the already-owned generic statement `multiple choice != open generation after pruning`.

The current RQ is:

> **When does a local compression error compound into a sequence-level capability failure?** Specifically: how much of the damage is the current step's computation being damaged, and how much is the current step conditioning on context that was itself produced under the same perturbation?

The inherited evidence shows that retention falls with answer depth in 14 of 15 conditions on one side and 1 of 15 on the other, across five model families and three intervention families, with zero crossings. That establishes only that depth sensitivity is not generic to long generation. It does not identify what switches it on: in the inherited data the two sides differ by dataset, and therefore by trajectory dependence, domain, answer format and difficulty together.

`evaluation protocol matters` is fully owned (Wen et al. 2026; Song et al., ICASSP 2026) and is claimed nowhere here. The live target is UniComp (EMNLP 2026 Main), whose `knowledge bias` headline compares a multiple-choice knowledge set against a free-form CoT reasoning set with no length control, and whose own unexplained GPQA-Diamond anomaly is this law's prediction. See `RELATED_WORK_AND_NOVELTY.md` §0 for the full owner audit.

## Preserved assets

All historical code, configs, experiment logs, results, audits, claims, and `MAINLINE.md` remain in this directory for reproducibility and evidence inheritance.

Historical results are **not retroactively declared confirmatory** by this status change.

**Authorized compute:** none. Stage 1 of `E12_PREREGISTRATION.md` is authorized only after its §9 runner validation passes; Stage 3 (SOTA compression) only against the Stage 1 outcome. Local environment
(`/home/xiang/miniconda3/envs/verl-clean/bin/python`), idle cards on
`fvcrc10/11/12/13/15`, **at most four cards at a time**.