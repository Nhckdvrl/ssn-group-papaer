# L08 — What Compression Evaluation Can and Cannot Establish

> **The current mainline is [MAINLINE.md](MAINLINE.md).** This file is the record of
> how the project reached it: the audit of the parent result, the factorial that
> reframed the research question, and the four competing accounts that motivated it.
> Where the two disagree, `MAINLINE.md` is authoritative.
>
> Reading order: [MAINLINE.md](MAINLINE.md) -> [CLAIMS.md](CLAIMS.md) ->
> [EXPERIMENTS.md](EXPERIMENTS.md) -> [PARENT_AUDIT.md](PARENT_AUDIT.md) ->
> [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md) §11.

---

**Status:** ACTIVE EXECUTION — reconstructed mainline, see MAINLINE.md
**Target:** ACL / EMNLP / NAACL Main
**Canonical package:** this directory
**Last updated:** 2026-09-10
**Supersedes:** the candidate-stage framing "Low-Dimensional Readout Preserves
Knowledge but Breaks Reasoning" (kept in `RESEARCH_PLAN.md`, `PILOT_CARD.md`,
`DATA_AND_GOLD.md`, `RELATED_WORK_AND_NOVELTY.md` as the entry-point record).

---

## 1. Why the framing changed before any experiment was run

The candidate package took the parent's contrast at face value: MMLU and SQuAD-v2
survive halving the readout, GSM8K collapses, therefore reasoning is the fragile
capability, therefore explain *why reasoning needs more readout dimensions*.

`PARENT_AUDIT.md` re-derives what the parent's own tables support. Two things:

1. **SQuAD-v2 did not visibly survive.** The reported metric is lm-eval's
   `best_exact`, which sweeps a no-answer threshold and is floored at the
   unanswerable fraction of SQuAD-2.0 dev = 5945/11873 = **50.07%**. All four
   truncated conditions report exactly **50.07**. The apparent survival is
   consistent with a total collapse hidden by the metric floor.
2. **COPA / DROP / HellaSwag are not independently readable** as printed (duplicated
   columns; sub-chance COPA at full readout). We build nothing on them.

What survives the audit is a comparison of **one** ranking task against **one**
generation task, differing simultaneously along three axes:

| | MMLU (survives) | GSM8K (collapses) |
|---|---|---|
| **Protocol** | rank K = 4 supplied candidates | arg max over V ≈ 150k |
| **Depth** | 1 scored decision | ~10^2 sequential decisions |
| **Content** | factual recall | multi-step computation |

Reading that as a *capability* result picks one of three confounded factors. That is
a hypothesis, not the phenomenon. Asking "why is reasoning more dimension-hungry"
would build the paper on top of an assumption we have not tested — and would be
exactly the "EMNLP 2025 + more benchmarks" paper the candidate audit warned about.

**This does not weaken L08 — it is the anomaly.** The parent's own framing is that
LLM sensitivity is mysteriously "task dependent" and deserves a dedicated study. The
dedicated study's first job is to find the axis.

## 2. Research question

> **Does halving an LLM's final readout damage the *capability* being exercised, or
> the *decision protocol* through which that capability is read out — and what law
> governs which decisions survive?**

The intervention is a pure readout intervention. With keep-set `S`,

```
logits'_t = W_U[:, S] h_t[S] = logits_t − W_U[:, S^c] h_t[S^c]
                                        └────── r_t ──────┘
```

Every transformer weight and every layer's computation is untouched. Truncation adds
a single large but *fixed-by-the-model* perturbation `−r_t` to the logit vector. Task
outcome then depends on how `r_t` interacts with the decision being taken, not on
what the decision is "about":

- **Bounded ranking (K candidates).** Only the differences of `r_t` across K specific
  rows of `W_U` matter, against the model's margin. Small K → likely survival.
- **Unconstrained arg max (V ≈ 150k).** The target must beat *every* one of ~150k
  perturbed competitors. This is an extreme-value problem: the max of many perturbed
  competitors clears a fixed margin far more easily than any one of them does.
- **Sequential depth L.** L such decisions, each of which must survive, and each of
  which changes the context for the next.

Nothing in that account mentions knowledge or reasoning. If it is right, the parent's
asymmetry is a **decision-complexity** asymmetry that reasoning benchmarks merely
happen to sit at the far end of.

## 3. Competing accounts (live, with different predictions)

| | Account | Core prediction |
|---|---|---|
| **A** | **Capability** — reasoning genuinely needs a wider readout subspace per step | Long free generation on *knowledge* content survives while GSM8K collapses at matched length |
| **B** | **Protocol** — bounded ranking survives, unconstrained arg max does not | MMLU collapses as soon as it is scored generatively, at matched content |
| **C** | **Depth** — per-step damage is mild; autoregression compounds it | Teacher-forced next-step quality stays high while free-running collapses; failure rate grows with chain length |
| **D** | **Geometry** — specific coordinates, not their number, carry the load | Sensitivity depends on which half is removed and transfers across tasks by mask, not by task family |

A and B/C/D are separated by the **same factorial** (§4), so no experiment is spent
on only one account. The candidate package's "Account D — evaluation artifact" is not
listed as a competing account any more: `PARENT_AUDIT.md` shows it is already
partially *true* of the parent's SQuAD-v2 number, so E01 measures it rather than
treating it as a threat to be ruled out.

## 3b. What the factorial returned (E01 + E02, 2026-09-10)

Relative performance `acc(mask)/acc(full)`, both models, both structured masks.
Full table in `results/e01_table.txt`; contrast tests in `scripts/analyze_e02.py`.

| cell | protocol / depth / content | Llama first | Llama last | Qwen first | Qwen last |
|---|---|---|---|---|---|
| `mmlu_rank` | rank K=4 / single / knowledge | 0.889 | 0.914 | 1.003 | 0.977 |
| `mmlu_gen_letter` | argmax / short / knowledge | 0.837 | 0.662 | 0.989 | 0.827 |
| **`mmlu_gen_cot`** | argmax / long / **knowledge** | **0.030** | **0.161** | **0.146** | **0.011** |
| `gsm8k_gen_direct` | argmax / short / reasoning | 0.650 | 0.125 | 0.952 | 0.792 |
| `gsm8k_gen_cot` | argmax / long / reasoning | 0.109 | 0.237 | 0.138 | 0.076 |

Three findings, against the pre-registered read-out rule:

1. **The axis is depth, not content.** MMLU knowledge, evaluated by long free
   generation, retains **0.030** of full-readout accuracy — the same order as the
   parent's GSM8K collapse (0.012). The *same items* scored by ranking retain 0.889.
   Nothing about what the model knows differs between those two rows.
2. **Content carries nothing systematic, and its sign is wrong for Account A.** At
   matched protocol and length, reasoning content is if anything slightly *more*
   robust than knowledge content (long-generation gaps −0.08, −0.08, +0.01, −0.07).
3. **Protocol is real but second-order.** `mmlu_rank` beats `mmlu_gen_letter` in all
   four model x mask cells (+0.05, +0.25, +0.01, +0.15), consistently but well below
   the depth effect.

Plus **C1.1 confirmed**: our own SQuAD-v2 run reproduces the parent's flat `best_exact`
(50.30 under full, first and last alike, relative performance 1.000) while
`HasAns_exact` falls from 78.07 to 25.76. The metric reports perfect preservation of
a task that lost two thirds of its accuracy.

**Consequence for the mainline.** The parent's knowledge-vs-reasoning asymmetry is
accounted for by two *measurement* properties of its task pair — output length and
scoring protocol — and not by the capability being exercised. Account A (capability)
is weakened; Accounts B and C are both live, with C dominant.

The paper cannot stop here. "Long greedy generation degrades more under a large
perturbation" is, on its own, compressible to an expected fact. What makes this a
mechanism paper is C2: *why* a readout perturbation that a single decision absorbs
destroys a chain of them.

## 4. Mainline claim architecture

- **C1 — Locate the axis.** A protocol × depth × content factorial over the parent's
  own tasks, plus an artifact-free re-measurement of SQuAD-v2. Establishes which
  factor the collapse tracks.
- **C2 — The law.** A quantitative link from the readout perturbation to decision
  survival: per-decision margin, candidate-set size K, chain length L. Predicts
  end-task accuracy from teacher-forced per-token quantities, with no content term.
  The interesting result is where the law *fails*, if it does.
- **C3 — Consequence.** Redundancy measured by ranking benchmarks (which is how
  essentially all embedding-truncation and compression evidence is collected) does
  not transfer to generative deployment. States what must be measured instead.

## 5. Outcome robustness

Every branch is a Main-level paper:

- **B/C win** → the field's headline "50% of dimensions are redundant" is a statement
  about a scoring protocol, and the parent's own reasoning interpretation is a
  confound. Corrective, general, and it re-reads a large literature.
- **A wins** → there *is* a reasoning-specific readout requirement, now established
  against the protocol and depth controls that the parent lacked; C2 localises it.
- **C2's law fails on reasoning only** → reasoning errors are non-recoverable in a way
  ordinary generation errors are not; that is a mechanism claim about CoT.
- **C2's law over-predicts collapse** → chains are error-correcting; also a mechanism.

The paper does not require the GSM8K gap to be large on any particular model.

## 6. What would kill this

- The factorial comes out fully descriptive: every cell moves and nothing separates
  protocol, depth and content.
- The whole effect is a decoding/format nuisance that disappears under any sane
  re-scoring, with no general consequence (i.e. not even the corrective paper stands).
- A 2026 paper is found that already runs the protocol/depth decomposition of the
  readout intervention.

## 7. Directory map

- [PARENT_AUDIT.md](PARENT_AUDIT.md) — what the parent does and does not establish
- [CLAIMS.md](CLAIMS.md) — claim ledger
- [EXPERIMENTS.md](EXPERIMENTS.md) — experiment registry
- [ENVIRONMENT.md](ENVIRONMENT.md) — environment, models, reproduction commands
- [RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md) — candidate-stage novelty record
- [RESEARCH_PLAN.md](RESEARCH_PLAN.md), [PILOT_CARD.md](PILOT_CARD.md), [DATA_AND_GOLD.md](DATA_AND_GOLD.md) — candidate-stage package
- `src/`, `scripts/`, `configs/`, `results/`
