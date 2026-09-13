# L08 — Current Mainline (reconstructed 2026-09-14, after the depth re-audit)

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

> **What compression damages under free generation is not a capability. It is the part
> of the answer that the model must carry through its own generated prefix.**
>
> Retention decays with answer depth when the answer is *trajectory-carried* — it
> exists only in the tokens the model has already emitted — and does not decay at all
> when the answer stays *prompt-recoverable* at the moment of emission. The
> knowledge-versus-reasoning ordering the compression literature reports is, to first
> order, this provenance ordering, because knowledge benchmarks are scored on
> prompt-recoverable answers and reasoning benchmarks on trajectory-carried ones.

Stated as an estimand: an apparent capability-fragility ordering is not identified by a
cross-benchmark compression comparison, because

```
observed selectivity = f(answer provenance, answer depth, intervention, capability)
```

and in the comparisons the field runs, the first two vary with the fourth by
construction. Capability label alone does not define fragility.

## 3. The evidence, on the existing runs

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
The only thing that differs is whether the answer survives in the prompt.

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
- **C2 — load-bearing.** The depth-by-provenance law of §2-§3, established by a design
  that manipulates provenance **within item**.
- **C3 — consequence.** Re-estimate a small number of load-bearing published
  comparisons under matched provenance and depth, and report how much of the reported
  capability ordering survives.

## 7. Stop rule

L08's Main route is killed if **E12** returns any of:

- provenance manipulated within item does not reproduce the slope dissociation;
- the dissociation appears only under readout truncation and not under a real pruning
  or quantization method (Wanda / SparseGPT / AWQ / GPTQ);
- an open-ended long-generation knowledge cell decays like GSM8K, i.e. the flat MMLU
  slope was the multiple-choice chance floor after all;
- the dissociation is explained by item difficulty once depth is randomised.

**The failure may not be rescued** by retreating to "but multiple choice and generation
still differ", or to the `C3.2` no-crossing count. Both are covered by §5.
