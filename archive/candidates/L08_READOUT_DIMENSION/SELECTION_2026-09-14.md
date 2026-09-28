# L08 — Selection verdict after the depth re-audit  `2026-09-14`

**Supersedes** [`FRESH_SELECTION_2026-09-13.md`](FRESH_SELECTION_2026-09-13.md).
Target: ACL / EMNLP / NAACL Main.

---

## 1. What this pass did

The 2026-09-13 reopening left `C3.2` — the intervention-locus sign boundary — as the
load-bearing novelty, and authorized no compute. This pass did two things before
spending any:

1. **Extended the owner audit.** Two owners were missing: Song et al. (ICASSP 2026),
   which directly owns "protocol changes the pruning conclusion" on the same benchmark
   and the same intervention family, and UniComp (EMNLP 2026 Main), which is the live
   target. A third, RAC (arXiv 2509.12464), partially owns "CoT error accumulates after
   pruning". See `RELATED_WORK_AND_NOVELTY.md` §0.
2. **Re-derived `C3.2` from the raw runs.** It does not survive. See
   `AUDIT_2026-09-14_DEPTH_CONFOUND.md`.

## 2. The two findings that changed the verdict

**`C3.2` is not identified by its own design.** The E10 "controlled" contrast matches
the existence of a chain, not answer depth — the number of decoding steps taken under
the intervention before the answer is emitted. That differs by 1.7-3.4x between the two
cells, in the same direction in all five models, and biases the ratio toward exactly the
`< 1` readings that form the readout half. Depth-matched: readout conditions
significantly `< 1` fall from 7 of 10 to 2 of 8, and the severity control `prune0p25`
falls from 1.34 [1.19, 1.50] to **1.24 [0.96, 1.47], null** — so the one argument that
excluded "pruning simply hits harder" is gone. Only a no-crossing count survives, and a
no-crossing count with the severity confound reopened is not a Main contribution.

**The discarded variation is the finding.** Fitting depth instead of matching it away:
15 estimable conditions, 5 model families, readout truncation + magnitude pruning +
quantization. Retention decays with answer depth in **14 of 15** trajectory-carried
conditions and in **1 of 15** prompt-recoverable ones; the difference is significant in
the predicted direction in 8 and in the wrong direction in **0**. Same model, same
intervention, same free-generation protocol, same long-chain regime.

## 3. The reconstructed paper identity

> **What compression damages under free generation is not a capability. It is the part
> of the answer the model must carry through its own generated prefix.**

- **C1 — prerequisite, prior-owned.** Protocol and depth change the apparent damage.
  Owned by Wen et al. and Song et al.; cited, reproduced more cleanly, never claimed.
- **C2 — load-bearing.** The depth-by-provenance law, confirmed by a design that
  manipulates provenance **within item** with depth randomised (E12).
- **C3 — consequence.** Re-estimate load-bearing published comparisons — UniComp's
  `knowledge bias` rows, Takeshita et al.'s Table 3 — at matched provenance and depth.

This is a different identity from both the 2026-09-13 fresh Selection and the
intervention-locus framing. The scientific question survives; the narrative does not.

## 4. Why this clears the Main bar where `C3.2` did not

| dimension | judgment |
|---|---|
| question importance | **strong** — UniComp is a 2026 EMNLP Main headline built on a comparison where capability, answer format and answer depth are confounded by construction, and its own unexplained GPQA-Diamond anomaly is this law's prediction, conjectured by them and untested |
| mother phenomenon | **strong** — capability-dependent degradation is established by Takeshita, UniComp, ThinkSLM, ICLR 2026. Nothing is bet on the phenomenon existing |
| C1 novelty | **none, and not claimed** |
| C2 novelty | **no owner found.** The owners predict a *level* shift from protocol; this is a *slope* in depth, and a slope that is zero on one side. A+B+C+D do not imply it |
| identification | **strong once E12 runs; weak now.** The law is currently observational in `L` and provenance is confounded with dataset. That is the whole content of E12 |
| explanatory depth | **improved.** The previous identity was explicitly not a mechanism paper (C2.3, five rejected accounts). Provenance is a mechanism-level variable, and E07/E08 are already its within-item counterpart |
| evidence breadth | **model breadth good, compression breadth inadequate.** Magnitude pruning + RTN cannot carry a claim about compression; E12 adds Wanda / SparseGPT / AWQ-GPTQ at UniComp's settings |
| consequence | **potentially strong** — conditional on C3 |
| upper bound | **PASS**, with C2 load-bearing and unconfirmed |

## 5. Conceptual correction, applied across the package

`readout channel (computation intact)` vs `parameters (computation damaged)` is
**withdrawn**. E00 gives hidden-state identity and exact reversibility for a *fixed*
forward pass only. Over a free-running trajectory, a changed emitted token at step `t`
changes the prefix and therefore `h_{t+1}`, so upstream computation diverges. The terms
are now `readout-locus` and `parameter-locus`, defined by what is modified. Expression-
versus-computation is an account to be tested, not a fact.

## 6. Kill rules

Preregistered in `E12_PREREGISTRATION.md` §6. L08 returns to ARCHIVED if within-item
provenance does not reproduce the dissociation; if it holds for readout truncation but
for none of Wanda/SparseGPT/AWQ/GPTQ; if an open-ended long-generation knowledge cell
decays like GSM8K (the flat MMLU slope was the chance floor); or if randomising depth
removes the effect (it was difficulty).

**Forbidden rescues, recorded in advance:** retreating to "multiple choice and
generation still differ" (owned), to the `C3.2` no-crossing count (demoted), or to a
benchmark-auditing paper.

## 7. Verdict

```yaml
prior_verdict: REOPEN_SERIOUS_SELECTION_PASS           # 2026-09-13
owner_audit_complete: false -> true                    # Song et al., UniComp, RAC added
c1_protocol_effect: OWNED_PREREQUISITE_NOT_CLAIMED
c3_2_intervention_locus_boundary: NOT_IDENTIFIED_DEMOTED
c2_depth_by_provenance_law: NO_OWNER_FOUND / LOAD_BEARING / OBSERVATIONAL
c3_published_reestimation: CONDITIONAL_ON_C2
successful_result_upper_bound: PASS
main_level_growth_path: PASS
new_compute_authorized: true                           # E12 only, bounded
compute_policy: local venv; idle cards on fvcrc10/11/12/13/15; max 4 cards
verdict: REOPEN_SERIOUS / IDENTITY_RECONSTRUCTED / E12_AUTHORIZED
```

E12 is authorized in the order given in its §9: build arm D and run its validity
ablation first, because it is the step with a real chance of returning "the design does
not work".

---

# AMENDMENT — identification review, same day

The verdict in §7 above authorized E12 as a `capability × provenance` 2x2. **That
authorization is withdrawn.** An identification review rejected the design, and it was
right to.

## A1. Why the 2x2 does not identify anything

Arm B (GSM8K with the solution supplied) turns "solve" into "read and verify"; arm D
(MMLU with a derived intermediate required) adds sequential computation to a knowledge
task. A perfect crossover would have been equally well explained by *"conditions
requiring more sequential computation are more fragile"*. Arm D's corruption ablation
validates arm D's construct; it does not show C and D are computationally equivalent up
to state provenance.

The variable was also loose. `prompt-recoverable` cannot carry the weight: MMLU's
candidates are in the prompt but *which one is correct* is not, and GSM8K's problem
statement is in the prompt throughout. `The answer string is in the prompt` is not
`task-critical state is externally recoverable`.

## A2. The object, restated better

> **trajectory-mediated compression damage** — the share of compression-induced failure
> that arrives because the context the current step conditions on was itself produced
> under the same treatment, rather than because the current step's computation is
> damaged.

Governing variable: **trajectory dependence** / external re-groundability. Central
claim: *compression errors compound with dependence on treatment-generated context, not
with output length or semantic capability per se.*

The instrument is **prefix clamping**, not task reconstruction. The compressed model
executes its own forward pass at every step, so direct per-step damage is fixed at 100%
of steps; only the emitted token is overridden to a reference trajectory for steps
`< k`. `k` varies mediation alone. This is the separation E07 could not make, and —
because the model is never modified mid-generation — it applies unchanged to Wanda,
SparseGPT, AWQ and GPTQ, which an E07-style weight-swapping schedule does not.

## A3. One addition to the reviewed design

A two-arm clamp is confounded: the reference prefix is both *untreated* and *correct*.
A third arm is required — reference corrupted to a matched task-error rate — giving

```
  Y(T,R) - Y(T,F)     total mediation
  Y(T,R) - Y(T,R̃)     the part explained by prefix content being worse
  Y(T,R̃) - Y(T,F)     residual: produced-under-the-same-perturbation, beyond content
```

The residual is what separates a new object from ordinary exposure bias. If it is ~0,
the ceiling drops toward Findings — recorded before the run, not after.

## A4. What the existing evidence is now worth

The 14/15-vs-1/15 slope table is **motivation, not result**. It shows depth sensitivity
is not generic to long generation; it does not say what switches it. It is on the
forbidden-rescue list.

## A5. Revised owner position

Two more owners crowd the half of the story about reasoning trajectories: RAC (ICLR
2026) and AYOT (arXiv 2608.01078) both fix reasoning-task compression by calibrating on
self-generated traces. *"Compression hurts reasoning because standard methods ignore
reasoning traces"* is unwritable. Neither decomposes the effect, and neither has a
condition under which the amplification is absent. `Reasoning as Compression`
(2603.08462) supplies the formal language for the CoT-as-bridge framing and owns it.

The reviewer attack to beat is no longer "protocol matters" — it is **"this is exposure
bias"**. See `RELATED_WORK_AND_NOVELTY.md` §0.5b.

## A6. Revised verdict

```yaml
e12_capability_x_provenance: WITHDRAWN_NOT_IDENTIFIED
scientific_object: trajectory-mediated compression damage
governing_variable: trajectory dependence / external re-groundability
instrument: prefix clamping (+ corrupted-reference control, + state refresh)
observational_slope_table: MOTIVATION_ONLY / FORBIDDEN_RESCUE
dominant_reviewer_attack: exposure_bias
successful_result_upper_bound: PASS
new_compute_authorized: false
stage_1_authorized_after: runner validation in E12_PREREGISTRATION.md §9
stage_3_sota_compression_authorized_after: Stage 1 outcome
verdict: SERIOUS / HIGH-UPSIDE / HOLD FOR E12 IDENTIFICATION REDESIGN
```

The scientific question is better than it was this morning and better than the
intervention-locus version it replaced. What is missing is not models and not
benchmarks. It is one causal intervention clean enough that no alternative explanation
survives.
