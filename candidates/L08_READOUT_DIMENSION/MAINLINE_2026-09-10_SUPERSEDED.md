# L08 — Current Mainline (reconstructed 2026-09-10, after E01-E09)

**Supersedes** the framing in `README.md` §2-§4. `README.md` is kept as the record of
how the project got here; this file is what the project is now.

---

## 1. The reconstruction, and why it happened

L08 began as "why does readout truncation preserve knowledge but destroy reasoning?"
`PARENT_AUDIT.md` showed that question presupposes its answer, so C1 became "on which
axis does the bottleneck live?" — and the factorial answered it (protocol and length,
not capability).

We then spent five experiments hunting the mechanism behind the surviving phenomenon.
All five candidate mechanisms are **causally rejected**, each with its own control:

| account | test | verdict |
|---|---|---|
| a fixed vocabulary prior is installed | E03b, vs a norm-matched random vector | rejected |
| extreme-value competition over ~150k tokens | E04, survival vs candidate-set size | rejected — flat beyond K≈8 |
| capture by repetition attractors | E05, `no_repeat_ngram` removes the attractor | rejected — degeneration 0.87→0.006, accuracy 0.109→0.089 |
| per-step prediction is badly damaged | E04, top-1 agreement | rejected — 0.62–0.92 |
| structural/control tokens are selectively demoted | E09, class × margin stratification | rejected — does not replicate across models |

Two partial contributors are quantified and survive: a monotone margin law (E06) and
an emission/termination failure worth about a third of the gap (E08). Neither is a
mechanism a paper can be built on.

**Conclusion drawn honestly:** the damage this intervention does is *diffuse*. There
is no single mechanism to find, and continuing to look is sunk cost. The contribution
is not the mechanism. It is what the mechanism hunt incidentally proved about how the
field measures.

## 2. The claim

> **Controlling evaluation protocol *and output length* removes most or all of the
> evidence for capability-selective compression damage. What survives the controls
> separates interventions that damage a model's computation from interventions that
> damage only its ability to express that computation.**

This is a claim about **capability attribution** — which capability a compression
method is said to have damaged — not about whether benchmarks overstate a compressed
model's usability. That second sentence is already prior work (§3.1) and we do not
claim it.

### The core observation, on four model families

Relative performance under readout truncation. `mmlu_rank` and `mmlu_gen_cot` use the
**same MMLU items**; only the rule for reading the answer out of the model differs.

| model | mask | `mmlu_rank` | `mmlu_gen_cot` | ratio |
|---|---|---|---|---|
| Llama 3.1 8B Instruct | first | 0.889 | **0.030** | 30x |
| Llama 3.1 8B Instruct | last | 0.914 | **0.161** | 5.7x |
| Qwen 2.5 7B Instruct | first | 1.003 | **0.146** | 6.9x |
| Qwen 2.5 7B Instruct | last | 0.977 | **0.011** | 89x |
| OLMo-3 7B (base) | first | 0.966 | **0.204** | 4.7x |
| OLMo-3 7B (base) | last | 0.958 | **0.243** | 3.9x |
| Phi-4-mini Instruct | first | 0.501 | **0.018** | 28x |
| Phi-4-mini Instruct | last | 0.541 | **0.000** | >500x |
| Mistral 7B v0.3 (base) | first | 0.952 | **0.523** | 1.8x |
| Mistral 7B v0.3 (base) | last | 0.907 | **0.318** | 2.9x |

Ten of ten conditions, five model families, base and instruction-tuned: ranking
retains 0.50-1.00 of full-readout accuracy while the identical knowledge read out by
generation retains 0.000-0.243.

Mistral is the weakest of the five and is reported as such: it is a base checkpoint
whose long-generation baselines are low (`mmlu_gen_cot` 0.220, `gsm8k_gen_cot` 0.326),
so its ratios are the least powered. Its protocol pair is nonetheless matched to
0.003 (rank 0.625, one generated token 0.628).

Phi-4-mini additionally shows that the parent's premise is itself model-dependent: its
ranking-protocol retention is 0.50-0.54, not the 0.89-1.00 of Llama and Qwen. "Half
the readout dimensions are redundant" is not even true under the protocol that
produced it, once the model is changed.

### The comparison the field actually runs

Whenever the literature concludes that compression damages reasoning selectively, the
evidence is a comparison between a **ranking-scored** knowledge or classification
benchmark and a **generation-scored** reasoning benchmark. That single comparison
varies three things at once — protocol, output length, and content — and the first two
dominate:

| the same MMLU items, the same model, the same intervention | relative accuracy |
|---|---|
| scored by ranking 4 candidates (the parent's protocol) | **0.889** |
| scored by generating one token | 0.837 |
| scored by generating a chain of reasoning | **0.030** |

Nothing about the model's knowledge differs between those rows. The control the
literature never runs is the third one: **knowledge content under long generation**.

## 3. What is ours, stated against the nearest prior work

`RELATED_WORK_AND_NOVELTY.md` §11 records a genuine collision. **"The Benchmark
Illusion" (arXiv 2606.17609, June 2026)** independently established that pruned models
pass multiple-choice evaluation while failing open generation on the same questions,
and that the answer is demoted rather than erased. We cite it as support and as
replication of the protocol effect on a different task family; we do not claim it.

Four things remain ours, and the paper rests on them rather than on the protocol
observation:

1. **Output length as a factor separate from protocol.** In our data it is the larger
   of the two: rank 0.889 -> one generated token 0.837 -> generated chain 0.030. Prior
   work compares protocols and does not vary length.
2. **The content axis at matched protocol and matched length.** No prior work compares
   knowledge content against reasoning content *inside* a protocol. This is the only
   comparison that can license a capability claim, and it is the object of the paper.
3. **The intervention-family boundary** (§3b) — the positive result, with no
   counterpart in prior work.
4. **The parent correction**: three separate conclusions of an EMNLP 2025 Main
   (People's Choice) paper dissolve under the controlled version.

| the parent's conclusion | under ranking | under generation |
|---|---|---|
| knowledge/reading survive, reasoning collapses | reproduced | **knowledge collapses too** (rel 0.030) |
| SQuAD-v2 retains 96.5-99.9% of performance | `best_exact` 50.30, rel **1.000** | `HasAns_exact` 78.07 -> 25.76, rel **0.33** |
| which half is removed "does not have an impact", indicating inefficient representation space usage | ratio **1.0x** | ratio up to **13.0x** |

## 3b. The headline result (E10, complete 2026-09-11)

Two contrasts on the same data. The first is how the literature establishes
capability-selective compression damage; the second holds evaluation protocol and
output length fixed. Ratios of relative performance, paired bootstrap over items,
B = 10000. A ratio is reported only when the full-precision baseline exceeds 0.05 and
the denominator cell has not been driven to the floor — otherwise it is **n/e**, not a
large number, because a floor effect is not a selectivity effect.

| model | intervention | touches | uncontrolled | **controlled** | 95% CI |
|---|---|---|---|---|---|
| Llama 3.1 8B It | prune 25% | parameters | 1.34 | **1.34** | [1.19, 1.50] |
| Llama 3.1 8B It | prune 40% | parameters | 13.54 | **3.15** | [1.95, 5.53] |
| Llama 3.1 8B It | quant 4-bit | parameters | 1.97 | **1.49** | [1.26, 1.78] |
| Qwen 2.5 7B It | quant 4-bit | parameters | 5.86 | **4.42** | [3.48, 5.76] |
| Phi-4-mini It | prune 40% | parameters | 12.79 | **5.00** | [3.11, 8.96] |
| Phi-4-mini It | quant 4-bit | parameters | 1.33 | 1.06 | [0.93, 1.21] |
| OLMo-3 7B base | prune 40% | parameters | 1.05 | 1.01 | [0.88, 1.15] |
| Qwen 2.5 7B It | prune 40% | parameters | n/e | n/e | denominator at floor |
| Llama 3.1 8B It | readout, first | readout only | 8.12 | **0.27** | [0.10, 0.53] |
| Llama 3.1 8B It | readout, last | readout only | 3.86 | **0.68** | [0.47, 0.95] |
| Qwen 2.5 7B It | readout, first | readout only | 7.26 | 1.06 | [0.71, 1.55] |
| Qwen 2.5 7B It | readout, last | readout only | 12.83 | **0.15** | [0.00, 0.38] |
| OLMo-3 7B base | readout, first | readout only | 3.18 | **0.67** | [0.47, 0.94] |
| OLMo-3 7B base | readout, last | readout only | 1.96 | **0.50** | [0.36, 0.66] |
| Mistral 7B v0.3 | readout, first | readout only | 1.96 | 1.08 | [0.73, 1.57] |
| Mistral 7B v0.3 | readout, last | readout only | 1.40 | **0.49** | [0.32, 0.72] |
| Phi-4-mini It | readout, first/last | readout only | n/e | n/e | both cells at floor |

**Holding protocol and length fixed removes 29.5% to 152% of the apparent
capability-selectivity.** For readout interventions it removes more than all of it.

### The boundary, stated by direction and significance

An earlier version of this file claimed the two sets of controlled ratios do not
overlap numerically. With OLMo-3 pruning (1.01) and Phi-4 quantization (1.06) that is
no longer true and the claim is withdrawn. What the complete data support is stronger,
because it is stated with uncertainty rather than as a numeric partition:

| intervention touches | significantly < 1 | null | significantly > 1 |
|---|---|---|---|
| **only the readout channel** (computation intact) | **6 of 8** | 2 | **0** |
| **the parameters** (computation damaged) | **0** | 2 | **5 of 7** |

Fifteen estimable conditions, five model families, three intervention families, and
**not one crosses in the wrong direction**. No readout intervention makes reasoning
significantly more fragile than knowledge at matched protocol and length; no parameter
intervention makes it significantly more robust.

Severity is not the explanation. A deliberately mild prune (25% of weights, no protocol
inflation at all: uncontrolled 1.34) still shows genuine selectivity — 1.34, CI
[1.19, 1.50] — while a severe readout truncation with an uncontrolled ratio of 8.12
shows the opposite sign (0.27).

The controlled factorial therefore does more than correct a number. It **separates
damage to a model's computation from damage to its ability to express that
computation**, which the uncontrolled comparison cannot do at all. That is the paper's
positive contribution.

### The cells are difficulty-matched, so the contrast is not about task difficulty

The obvious objection to any cross-cell comparison is that the cells differ in
difficulty. For the contrasts that carry the argument they do not. Full-readout
accuracy per cell:

| model | `mmlu_rank` | `mmlu_gen_letter` | `mmlu_gen_cot` | `gsm8k_gen_cot` |
|---|---|---|---|---|
| Llama 3.1 8B It | 0.683 | 0.681 | 0.667 | 0.786 |
| Qwen 2.5 7B It | 0.744 | 0.739 | 0.667 | 0.840 |
| OLMo-3 7B (base) | 0.644 | 0.645 | 0.515 | 0.626 |
| Phi-4-mini It | 0.679 | 0.675 | 0.710 | 0.812 |

The protocol contrast (`mmlu_rank` vs `mmlu_gen_letter`) is matched to within
**0.002-0.005 in every model** — the same items, the same prompt string, the same
single decision, and the same undamaged accuracy. Only the rule for reading the answer
out differs. The content contrast (`mmlu_gen_cot` vs `gsm8k_gen_cot`) is matched to
within 0.1-0.2.

The one badly matched cell is `gsm8k_gen_direct` (0.160 for Llama, 0.250 for Qwen).
It is the lowest-power cell in the design and is the one that produced the single
reversal in the pre-registered depth contrast; it is reported, not relied on.

### Severity is not what separates the families

The obvious objection is that pruning simply hits harder than readout truncation. It
does not explain the pattern, and this is already covered by the severity note in §3b:
a deliberately mild prune (25% of weights, uncontrolled ratio 1.34, i.e. no protocol
inflation to remove) still shows genuine selectivity at 1.34 [1.19, 1.50], while a
severe readout truncation with an uncontrolled ratio of 8.12 has the opposite sign at
0.27. The separation is between what the intervention touches, not how hard it hits.

## 4. The corroborating decomposition

After the confound is removed, the corrected picture is not "we don't know". It is a
substantive answer to the question the field actually cares about:

- At matched protocol and matched output length, **reasoning content is not more
  fragile than knowledge content**. The content contrast is inconsistent across models
  for short generation (+0.19/+0.54 vs +0.04/+0.04) and its sign is *negative* for long
  generation (−0.08, −0.08, +0.01, −0.07) — reasoning is if anything slightly more robust.
- Conditional on a truncated model producing a well-formed GSM8K answer, that answer
  is as accurate as the full model's (0.868–1.000 vs 0.782–0.850) and its arithmetic
  is 94.5–100% correct. The computation is intact; the expression of it is not.
- Handing the model its answer marker turns a literal **0.000** into **0.178** (E08).

## 5. What makes this Main-level rather than a correction

Breadth is load-bearing, and it is the current work item:

1. **Multiple intervention families** — readout truncation (changes no computation),
   magnitude pruning and weight quantization (change computation). E10, running.
2. **Multiple model families** — currently Llama 3.1 8B and Qwen 2.5 7B; needs a third
   and fourth from the local cache (Gemma 3, Mistral, OLMo 3, Phi-4).
3. **A boundary, not just a negation.** If parameter interventions *do* show genuine
   content-selectivity at matched protocol while readout interventions do not, that
   difference is a diagnostic the field can use: it separates damage to computation
   from damage to expression. That outcome is a better paper than the pure negation,
   and the design returns it either way.

## 6. Outcome robustness

- The confound reproduces across families → the claim is general; the field's
  capability-selectivity evidence is protocol-manufactured.
- It reproduces for readout but not for pruning/quantization → a boundary result and a
  diagnostic; the claim narrows to "interventions that leave computation intact produce
  apparent capability-selectivity that is entirely expressive".
- It fails to reproduce anywhere but readout truncation, and readout truncation is
  judged too narrow to carry a paper → **kill**, recorded in §7.

## 7. Stop rule

L08 is killed if, after E10 and the model-family extension:
- the protocol confound is confined to the single parent intervention, **and**
- no boundary between families is established, **and**
- the remaining claim is a correction to one paper's three numbers.

That would be a Findings-scale contribution at best and the project should stop rather
than be padded.
