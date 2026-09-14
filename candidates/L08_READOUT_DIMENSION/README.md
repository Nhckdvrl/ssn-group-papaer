# L08 — Readout / Compression / Trajectory Route

## **FINAL STATUS: KILL FOR ACL / EMNLP / NAACL MAIN — DO NOT RECONSTRUCT**

**Finalized:** 2026-09-14  
**Canonical scientific autopsy:** [`FINAL_ARCHIVE_2026-09-14.md`](FINAL_ARCHIVE_2026-09-14.md)  
**Search-level anti-resurrection note:** [`../../search_rounds/2026-09-14_L08_FINAL_KILL_AND_LESSONS.md`](../../search_rounds/2026-09-14_L08_FINAL_KILL_AND_LESSONS.md)

> **This status supersedes every earlier `ARCHIVED`, `REOPEN`, `SERIOUS`, `HIGH-UPSIDE`, reconstructed-mainline, pilot, or mechanism-development status in this directory.**
>
> Historical `MAINLINE.md`, `CLAIMS.md`, `EXPERIMENTS.md`, Selection files, pilot files, configs, scripts, and results are preserved for reproducibility and methodological reuse. They are **not active paper claims or compute authorization**.

---

## Final reason

The project ultimately established a strong but insufficiently novel causal fact: under compression/model perturbation, replacing part of a perturbed self-generated trajectory with a clean/reference trajectory can substantially rescue downstream generation while the perturbation remains active on every model forward pass.

The Main-level route required a stronger residual mechanism: that compression makes an already-computed load-bearing state fail to remain effectively usable, so selectively re-grounding/replaying that state should rescue the compressed trajectory beyond a matched placebo.

The preregistered decisive test failed:

`Delta_refresh = [Y_T(state)-Y_T(placebo)] - [Y_0(state)-Y_0(placebo)] = +0.0000 [-0.102, +0.102]`.

For quant 4-bit on the same model/task:

- reference-prefix clamp rescue: `+0.2595 [0.191, 0.326]`;
- replay of the model's own already-correct downstream-relevant intermediate state: `+0.0179 [-0.045, 0.080]`.

Therefore the proposed state-carry / external-re-grounding mechanism is not supported. The surviving explanation is ordinary autoregressive error propagation under model perturbation: perturbation changes generated tokens, those tokens become future context, and replacing enough of the bad trajectory with a good one helps.

That causal shape is not enough for Main novelty given prior exposure-bias/self-recovery diagnostics and modern reasoning-aware compression work (including RAC / AYOT).

---

## Earlier routes are also closed

- **Protocol/readout effect:** owned by prior work; cannot carry novelty.
- **Intervention-locus capability-selectivity boundary:** killed by answer-depth confounding; the historical severity control becomes null after correct matching.
- **`prompt-recoverable vs trajectory-carried`:** retired invalid construct.
- **Capability × provenance 2×2:** non-identifying; it changed solve→verify / sequential-computation burden together with provenance.
- **Synthetic corrupted-prefix residual:** structurally confounded by prefix quality / severity / power trade-offs.
- **UniComp / knowledge-bias auditing:** cannot become the Main paper after the mechanism route failed.

---

## Permanent anti-resurrection rule

Do **not** reopen L08 Main by adding models, compressors, tasks, prompts, larger samples, new names, or new control arms to the same parent question.

In particular, do not fall back to:

- MC/ranking vs free generation;
- reference-clamp magnitude or dose response;
- readout-vs-parameter no-crossing counts;
- the old mild-pruning severity control;
- `trajectory dependence`, `external re-groundability`, `state carry`, or `prefix contamination` as renamed versions of the same remainder;
- possible state-refresh effects smaller than the preregistered resolution;
- a benchmark/evaluation paper built around knowledge-vs-reasoning compression gaps.

Only a genuinely different external scientific question could justify a new candidate, and it must cite `FINAL_ARCHIVE_2026-09-14.md` as an anti-resurrection parent.

---

## What may still be reused

Reuse **instrumentation and lessons**, not the dead paper claim:

- stable item-identity assertions;
- per-forward-pass intervention coverage checks;
- token-ID prefix clamping and self-clamp no-op validation;
- answer-depth extraction/matching;
- clamp dose-response machinery;
- prefix-quality auditing;
- fixed-prefix/teacher-forced diagnostics;
- the methodological lesson that a large mother effect does not imply a novel residual mechanism.

A Findings/short empirical remainder may exist, but there is **no default authorization to spend more compute or writing effort on it**.

For the full history, results, invalid controls, implementation bugs, forbidden rescues, and the new Residual-Mechanism selection rule, read the canonical final archive.
