# L08 — KILLED (mechanistic Main route), 2026-09-14

> **Final verdict.** `Delta_refresh = +0.0000 [-0.102, +0.102]`. The preregistered kill
> rule in `E13_PREREGISTRATION.md` §7 fires. Trajectory mediation survives as a
> phenotype (C2a), but its instrument is owned by *Exposure Bias versus Self-Recovery*
> (EMNLP 2021), its residual is null, and no quantity separates it from RAC/AYOT, which
> own both the phenomenon and a fix. **There is no Main-level novelty left.**
> See `results/e13/RESULTS.md` and `results/e12/PROGRESS.md`.
>
> What remains is a clean piece of empirical work at Findings/short scale: a four-way
> validated clamp instrument, three interventions across two loci, and a monotone
> step-count dose-response that E07 could not obtain. That is a decision for the user,
> not a Main route.
>
> The text below is the mainline as it stood before E13 and is kept as the record.

---

# L08 — Mainline as of 2026-09-14 (superseded by the verdict above)

**Supersedes** `MAINLINE_2026-09-10_SUPERSEDED.md`, which is kept as the record of the
previous identity. The reconstruction was forced by
[`AUDIT_2026-09-14_DEPTH_CONFOUND.md`](AUDIT_2026-09-14_DEPTH_CONFOUND.md), which
showed the previous load-bearing claim was not identified by its own design.

---

## 1. What changed, and why

The 2026-09-13 reopening made `C3.2` load-bearing: at matched protocol and length,
readout-locus interventions make reasoning look robust while parameter-locus
interventions make it look fragile, with no crossing in fifteen conditions.

Re-deriving that from the raw runs before spending compute showed the design does not
support it. The "matched length" contrast matches the *existence* of a chain, not the
**answer depth** — how many decoding steps the model takes under the intervention
before emitting the answer. That differs by 1.7-3.4x between the two cells, in the
same direction in all five models, and E07 had already established that the damage is
positional in exactly this quantity.

Depth-matched, the readout half loses most of its significance (7 of 10 conditions
significantly `< 1` becomes 2 of 8) and — decisively — the severity control fails:
`prune0p25`, the single condition that ruled out "pruning simply hits harder", goes
from 1.34 [1.19, 1.50] to **1.24 [0.96, 1.47], null**. Severity is no longer excluded.

But the discarded variation turned out to be the finding.

## 2. The claim

> **Compression errors compound with dependence on treatment-generated context — not
> with output length, and not with semantic capability per se.**
>
> A local compression error becomes a sequence-level capability failure when later
> predictions causally depend on context that was produced under the same perturbation.
> Computation that can be re-grounded in a context the treatment did not touch breaks
> the amplification loop.

The scientific object is **trajectory-mediated compression damage**. Writing `T` for the
treatment, `Z` for the tokens the model has emitted and `Y` for the answer, compression
reaches the answer by two paths —

```
  direct      T -> Y                 the current step's computation is damaged
  mediated    T -> Z(T) -> Y         the context the current step conditions on was
                                     itself produced under the treatment
```

— and the second is the object. The governing variable is **trajectory dependence**
(equivalently, external re-groundability): whether the information needed for a correct
decision at step `t` is recoverable from a context that is not treatment-dependent.

**Wording that is no longer used.** An earlier draft of this file said `the part of the
answer the model must carry through its own generated prefix`, with the variable named
`prompt-recoverable vs trajectory-carried`. That binary does not survive scrutiny:
MMLU's candidate strings sit in the prompt but *which one is correct* does not, and
GSM8K's problem statement sits in the prompt throughout, so the model could in principle
re-derive rather than depend on its chain. `The answer string is in the prompt` is not
`task-critical state is externally recoverable`. The binary is retained only as the
observational correlate that motivated the question.

## 3. The evidence, on the existing runs — observational, and labelled as such

Logistic fit of per-item retention on `log2(1 + L)`, `L` = the full model's answer
position. `L` is pre-treatment; retention conditions on the full model being correct.
Fifteen estimable conditions, five model families, readout truncation and magnitude
pruning and weight quantization:

| | count |
|---|---|
| **prompt-recoverable** (`mmlu_gen_cot`) slope significantly negative | **1 of 15** |
| **trajectory-carried** (`gsm8k_gen_cot`) slope significantly negative | **14 of 15** |
| difference significant in the predicted direction | 8 of 15 |
| difference significant in the **wrong** direction | **0 of 15** |

Same model, same intervention, same free-generation protocol, same long-chain regime.
What differs is the dataset, and with it a bundle that includes trajectory dependence.

**This is a dissociation, not a mechanism.** It says depth sensitivity is not a generic
property of long generation — something that varies between these two cells switches it
on. It does not say what. In the inherited data trajectory dependence is confounded with
domain, answer format and item difficulty, so the table below motivates the question and
may never be presented as the result. Under the forbidden-rescue rule in
`E12_PREREGISTRATION.md` §8 it cannot be used to save the package either.

Two inherited results are the causal counterpart of this, and both were already run:

- **E07** varies *when* the intervention is applied within one item's trajectory.
  Truncating 64 early steps leaves 0.155; truncating ~336 late steps leaves 0.756.
  Its own conclusion was "what matters is whether the answer-bearing tokens were
  generated under truncation" — the within-item statement of the same law.
- **E08** supplies the answer marker to a truncated model and turns a literal 0.000
  into 0.178, with conditional accuracy at 0.868-1.000 and 94.5-100% of calculator
  steps correct. The trajectory-carried content is computed; it fails to be delivered.

## 4. What this is not, and the conceptual correction

The previous mainline wrote `readout locus (computation intact)` against
`parameters (computation damaged)`. **That is withdrawn.** E00 established that readout
truncation leaves the hidden state of a *fixed* forward pass unchanged and is exactly
reversible. It does not license the claim over a free-running trajectory: once
truncation changes the emitted token at step `t`, the prefix at `t+1` differs, so
`h_{t+1}` differs and the upstream computation diverges from then on. "Expression
damaged, computation intact" is a **hypothesis about free generation**, not a fact we
have shown, and a reviewer who works on causal or mechanistic inference will see it.

Everywhere in this package the operational terms are now:

- **readout-locus intervention** — the map from the final hidden state to logits;
- **parameter-locus intervention** — the transformer weights.

Both are defined by what is modified, independently of any outcome. The expression-
versus-computation reading is recorded as an account to be tested, not asserted.

## 5. Position against the owners

Three papers own things this package must not claim, and none owns the law above.

| owner | what it owns | what it does not have |
|---|---|---|
| **Takeshita et al.**, EMNLP 2025 Main (People's Choice) | dimension removal; the first causal-LM observation; "sensitivity is task dependent" | any control; the SQuAD number is a metric floor (C1.1) |
| **Wen et al.**, *The Benchmark Illusion*, 2026 | multiple-choice success ≠ open-generation usability after pruning, same question, answer demoted not erased | no depth axis; a level effect of protocol, not a slope in depth |
| **Song et al.**, *Demystifying the Roles of LLM Layers*, ICASSP 2026 | likelihood-vs-generation evaluation changes which layers look important; "task-, metric-, model-dependent" | same — protocol as a level effect; no within-generation depth, no provenance contrast |
| **UniComp**, EMNLP 2026 Main | the `knowledge bias` headline across pruning/quantization/distillation, 40+ datasets | does not control output length anywhere; its knowledge set is entirely multiple-choice and its reasoning set entirely free-form CoT |

**`evaluation protocol matters` is fully owned and is not claimed anywhere in this
package.** It is a prerequisite, stated in one paragraph with citations, not a result.

UniComp is the reason the question is live rather than manufactured. Its knowledge
column (MMLU, ARC, HellaSwag, PIQA, Winogrande) is multiple-choice throughout and its
reasoning column (GSM8K, MATH-500, GPQA-Diamond) is free-form CoT throughout, so
capability, answer format and answer depth are perfectly confounded in the comparison
that produces the headline. It also reports an anomaly it cannot explain — GPQA-Diamond
is more robust than GSM8K and MATH-500 — and conjectures in passing that this is
"likely attributable to its multiple-choice format". That conjecture is untested, it is
our law's prediction, and if it is right it does not rescue the headline: it dissolves
it, because the same mechanism applies to every row of the knowledge column.

## 6. The contribution structure

- **C1 — prerequisite, prior-owned.** Protocol and depth change the apparent damage on
  identical content. Cited to Wen et al. and Song et al.; our version is cleaner
  (same item, same prompt, same intervention, only the readout rule varies) and is
  reported as identification, **not as novelty**.
- **C2 — load-bearing.** Trajectory-mediated compression damage, established by a
  **selective causal intervention**: prefix clamping, which holds direct per-step damage
  fixed at every step and varies only how much of the conditioning context was produced
  under the treatment. E12 Stage 1. The observational slope table is the motivation for
  this experiment, not a substitute for it.
- **C3 — consequence.** Re-estimate a small number of load-bearing published
  comparisons under matched provenance and depth, and report how much of the reported
  capability ordering survives.

## 7. The reviewer attack this has to survive

The old danger was *"Song et al. and Wen et al. already showed protocol matters"*. That
is now handled: C1 is a prerequisite and is claimed nowhere.

The new danger is different and sharper:

> *"This is exposure bias under compression. Autoregressive models condition on their own
> mistakes. Everybody knows this."*

Two things defeat it, and the paper is not viable without both.

1. **Not every long generation shows the effect.** Classic exposure bias predicts
   accumulation wherever a model conditions on its own output. The §3 dissociation
   already indicates otherwise, observationally.
2. **The loop can be opened and closed by intervention.** Prefix clamping switches the
   mediation off while leaving per-step damage untouched; state refresh switches it back
   on selectively. Exposure bias is a statement about a train/inference prefix
   distribution mismatch; this is a decomposition of a *model perturbation* into direct
   and trajectory-mediated components, and when each occurs.

The corrupted-reference arm (`E12` §4) is what separates the two quantitatively. If the
residual after matching prefix error rate is ~0, the honest reading is ordinary error
propagation, which is adjacent to what RAC owns, and the ceiling drops.

## 8. Stop rule

Full outcome table in `E12_PREREGISTRATION.md` §8. The Main route is killed if clamped
and free-running depth slopes are equal; if the effect holds for readout truncation but
for none of Wanda / SparseGPT / AWQ / GPTQ; or if it holds on GSM8K but not on a second
computation family.

**Forbidden rescues:** "multiple choice and generation still differ" (owned); the
`C3.2` no-crossing count (demoted); the §3 observational slope table (motivation, not
result); a benchmark-auditing paper.
