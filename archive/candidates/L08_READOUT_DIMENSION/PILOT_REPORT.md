# L08 — Pilot Report

**Date:** 2026-09-11
**Verdict:** **GO, on the reconstructed mainline in [MAINLINE.md](MAINLINE.md).**
**Environment:** [ENVIRONMENT.md](ENVIRONMENT.md). All results reproducible from
`results/` via the commands recorded there.

---

## 1. What was asked, and what the pilot answered

The candidate package asked: *why does readout truncation preserve knowledge but
destroy reasoning?* The pilot's first act was to audit whether that phenomenon is what
the parent established. It is not ([PARENT_AUDIT.md](PARENT_AUDIT.md)), and the
question as posed presupposes its own answer.

The pilot therefore answered a different and better-posed question — *on which axis
does the damage live?* — and then, when five mechanism accounts for the surviving
phenomenon were causally rejected, followed the evidence to where it actually pointed:
not at a mechanism inside the model, but at what the field's evidence can support.

## 2. Evidence, in the order it was established

### 2.1 The intervention is exact and confined  (E00, E00b)
The hook reproduces `W_U[:,S] h[S]` to 1.1e-05 in fp32, leaves every transformer
weight and every hidden state bit-identical, and is exactly reversible. The batched
rank scorer agrees with a naive single-sequence reference to 3.8e-05 with full arg-max
agreement. The `logit_bias` correction satisfies both algebraic identities it needs to.
Every later claim is an intervention claim; these audits are what make them claims.

### 2.2 The parent's three LLM conclusions dissolve  (E01)

| the parent's conclusion | under its ranking protocol | under generation |
|---|---|---|
| knowledge and reading survive, reasoning collapses | reproduced (MMLU rel 0.889) | the same MMLU knowledge collapses (rel **0.030**) |
| SQuAD-v2 retains 96.5-99.9% | `best_exact` 50.30, rel **1.000** | `HasAns_exact` 78.07 -> 25.76, rel **0.33** |
| which half is removed has no impact, "indicating inefficient representation space usage" | ratio **1.0x** | ratio up to **13.0x** |

The SQuAD number is a metric floor: `best_exact` sweeps a no-answer threshold and
cannot fall below the unanswerable fraction of the split, which for SQuAD-2.0 dev is
5945/11873 = **50.07%** — exactly the value the parent reports for all four truncated
conditions.

### 2.3 The axis is protocol and length, not capability  (E02, four model families)

Same MMLU items, same model, same intervention, three ways of reading out the answer:

| model | mask | `mmlu_rank` | `mmlu_gen_cot` | ratio |
|---|---|---|---|---|
| Llama 3.1 8B It | first / last | 0.889 / 0.914 | 0.030 / 0.161 | 30x / 5.7x |
| Qwen 2.5 7B It | first / last | 1.003 / 0.977 | 0.146 / 0.011 | 6.9x / 89x |
| OLMo-3 7B base | first / last | 0.966 / 0.958 | 0.204 / 0.243 | 4.7x / 3.9x |
| Phi-4-mini It | first / last | 0.501 / 0.541 | 0.018 / 0.000 | 28x / >500x |
| Mistral 7B v0.3 base | first / last | 0.952 / 0.907 | 0.523 / 0.318 | 1.8x / 2.9x |

Ten of ten conditions across five model families, base and instruction-tuned. The contrast is difficulty-matched: full-readout accuracy
on `mmlu_rank` and `mmlu_gen_letter` agrees to within **0.002-0.005 in every model**.

### 2.4 Five mechanism accounts, causally rejected  (E03b, E04, E05, E09)

| account | test, with its control | verdict |
|---|---|---|
| a fixed vocabulary prior is installed | add back `b̄`, against a norm-matched random vector | rejected — never beats the control |
| extreme-value competition over ~150k tokens | survival vs candidate-set size K | rejected — flat beyond K ~ 8 |
| capture by repetition attractors | `no_repeat_ngram_size=6` removes the attractor | rejected — degeneration 0.87 -> 0.006 while GSM8K accuracy goes 0.109 -> 0.089 |
| per-step prediction is badly damaged | top-1 agreement under truncation | rejected — 0.62-0.92 |
| structural tokens are selectively demoted | class x margin stratification | rejected — Llama 0/200, Qwen 200/200; tracks margin, not class |

Two partial contributors survive and are quantified: a monotone margin law (E06) and
an emission/termination failure worth about a third of the gap (E08: a literal 0.000
becomes 0.178 when the answer marker is supplied).

**The honest conclusion is that this intervention's damage is diffuse.** That is
recorded as a finding, not hidden: it is why the paper is not a mechanism paper.

### 2.5 The result the pilot actually found  (E10)

Controlling protocol and output length removes **29.5% to 111%** of the apparent
capability-selective damage — and what survives separates the intervention families:

| intervention touches | significantly < 1 | null | significantly > 1 |
|---|---|---|---|
| **only the readout channel** (computation intact) | **6 of 8** | 2 | **0** |
| **the parameters** (computation damaged) | **0** | 2 | **5 of 7** |

Fifteen estimable conditions, five model families, three intervention families, and
**not one crosses in the wrong direction**.

Severity is not the explanation: a mild 25% prune, which has no protocol inflation to
remove, still shows genuine selectivity (1.34, CI [1.19, 1.50]) while a severe readout
truncation shows the opposite sign (0.27).

## 3. Novelty, stated against the nearest collision

[RELATED_WORK_AND_NOVELTY.md](RELATED_WORK_AND_NOVELTY.md) §11 records that **"The
Benchmark Illusion" (arXiv 2606.17609, June 2026)** independently established that
pruned models pass multiple-choice while failing open generation. That observation is
theirs and is cited as prior work and as independent replication of our protocol
effect. What remains ours: output length as a factor separate from protocol (the
larger of the two in our data), the content axis at matched protocol and length, the
intervention-family boundary, and the parent correction.

The claim is about **capability attribution**, not benchmark usability.

## 4. Honest weaknesses

- The paper has no positive mechanism for readout truncation's damage. Five accounts
  were eliminated; the residual is diffuse. This is stated as a result.
- `gsm8k_gen_direct` has a full-readout accuracy of 0.16-0.25 and is the lowest-power
  cell; it produced the one reversal in the pre-registered depth contrast.
- Two conditions are not estimable because both cells hit the floor, and are reported
  as such rather than as large ratios.
- `allenai/Olmo-3-7B-Instruct-DPO` runs were invalid (broken full-readout baselines
  under raw few-shot prompts) and are quarantined in `results/_invalid/`.
- Base checkpoints matching the parent exactly were not used for the two original
  models; Llama 3.1 8B base is gated on this account.

## 5. What the paper still needs

1. ~~Mistral-7B as a fifth family; parameter interventions on OLMo-3 and Phi-4.~~ Done.
2. Random-mask seeds alongside first/last, to separate mask identity from mask
   geometry in the 13x result (E11, running).
2b. Within-item causal version of the depth axis: switch the mask on and off during a
   single generation (E07, running).
3. The corrected re-measurement stated as a positive recommendation: what *does*
   survive each compression family once protocol and length are controlled.
