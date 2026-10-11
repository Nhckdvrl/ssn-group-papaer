# L08 — Re-audit of the E10 "controlled" contrast  `2026-09-14`

**Trigger.** The 2026-09-13 reopening made `C3.2` (the intervention-family sign
boundary) load-bearing. Before authorizing any confirmatory compute, the inherited
evidence for `C3.2` was re-derived from the raw runs.

**Result.** `C3.2` is **not identified** by the E10 design. The contrast the package
calls "protocol and output length held fixed" does not hold output depth fixed.

Reproduce: `$PY scripts/analyze_depth.py` (writes `results/depth_audit.json`).

---

## 1. The defect

E10's controlled ratio is `rel(mmlu_gen_cot) / rel(gsm8k_gen_cot)`. Both cells are
free generation with a chain, which the package treated as matched depth. The
quantity that matters is not whether a chain exists but **where in the generated
trajectory the answer-bearing token sits**, because E07 already established that the
damage is *positional*: what matters is whether the answer-bearing tokens were
produced under the intervention.

That quantity is not matched. Measured on the full model, so pre-treatment:

| model | `mmlu_gen_cot` p10/p50/p90 | `gsm8k_gen_cot` p10/p50/p90 | median ratio |
|---|---|---|---|
| Llama 3.1 8B It | 46 / 84 / 207 | 21 / 40 / 77 | **2.1x** |
| Mistral 7B v0.3 | 11 / 76 / 173 | 13 / 34 / 78 | **2.2x** |
| OLMo-3 7B base | 28 / 128 / 307 | 21 / 44 / 212 | **2.9x** |
| Phi-4-mini It | 59 / 132 / 253 | 20 / 39 / 76 | **3.4x** |
| Qwen 2.5 7B It | 68 / 138 / 220 | 38 / 80 / 148 | **1.7x** |

Five models out of five, always in the same direction: the knowledge cell requires
**1.7-3.4x more decoding steps under the intervention before the answer is emitted**.
The token budgets differ too (512 for MMLU, 400 for GSM8K).

The bias has a known sign. Deeper answers are more damaged, so the numerator cell is
systematically penalised and the controlled ratio is biased **downward** — toward the
`< 1` readings that constitute the readout half of `C3.2`.

## 2. Re-estimation with depth matched

Per-item retention among items the full model answers correctly, reweighted by
answer-position stratum onto the GSM8K distribution, paired bootstrap B = 4000.
Cells below a 2% floor are `n/e`.

| model | intervention | locus | as published | **depth-matched** | 95% CI | sign |
|---|---|---|---|---|---|---|
| Llama 3.1 8B It | prune 25% | parameter | 1.23 | 1.24 | [0.96, 1.47] | **null** |
| Llama 3.1 8B It | prune 40% | parameter | 2.45 | 4.95 | [1.85, 9.27] | > 1 |
| Llama 3.1 8B It | quant 4-bit | parameter | 1.27 | 1.30 | [0.94, 1.73] | **null** |
| OLMo-3 7B base | prune 40% | parameter | 0.89 | 0.91 | [0.74, 1.08] | null |
| Phi-4-mini It | prune 40% | parameter | 5.41 | 10.76 | [4.60, 27.33] | > 1 |
| Phi-4-mini It | quant 4-bit | parameter | 0.99 | 1.29 | [0.92, 1.65] | null |
| Qwen 2.5 7B It | quant 4-bit | parameter | 3.66 | 3.55 | [2.65, 4.91] | > 1 |
| Llama 3.1 8B It | readout, last | readout | 0.54 | **1.00** | [0.45, 1.75] | **null** |
| Llama 3.1 8B It | readout, random | readout | 0.58 | **1.19** | [0.42, 2.30] | **null** |
| Mistral 7B v0.3 | readout, first | readout | 0.44 | 0.59 | [0.20, 1.11] | **null** |
| Mistral 7B v0.3 | readout, last | readout | 0.34 | **0.68** | [0.31, 1.10] | **null** |
| OLMo-3 7B base | readout, first | readout | 0.62 | 0.51 | [0.18, 0.93] | < 1 |
| OLMo-3 7B base | readout, last | readout | 0.43 | 0.65 | [0.36, 1.00] | < 1 |
| Qwen 2.5 7B It | readout, first | readout | 0.83 | **1.23** | [0.66, 2.00] | **null** |
| Qwen 2.5 7B It | readout, random | readout | 0.70 | **1.05** | [0.32, 2.38] | **null** |

| locus | significantly < 1 | null | significantly > 1 |
|---|---|---|---|
| readout | 2 of 8 | 6 | 0 |
| parameter | 0 of 7 | 4 | 3 of 7 |

**What survives:** the no-crossing statement. Zero of fifteen conditions cross.

**What does not survive:**

1. The **per-condition significance**. Readout conditions significantly `< 1` fall from
   7 of 10 to 2 of 8. The headline `0.27` for Llama readout-first is `n/e` at the floor
   once the estimand is per-item retention.
2. **The severity control, which was the load-bearing rebuttal.** `prune0p25` was the
   one condition proving "severity is not the explanation" — a mild prune with no
   protocol inflation to remove, reported at 1.34 [1.19, 1.50]. Depth-matched it is
   **1.24 [0.96, 1.47], null**. The three surviving `> 1` conditions are two severe
   40% prunes and one quantization. **Severity is no longer excluded as the
   explanation of the parameter half.**

A no-crossing count across fifteen conditions, with the severity confound reopened,
is not a load-bearing Main contribution. `C3.2` is demoted.

## 3. What the audit found instead

Matching depth away discards the informative variation. Fitting it instead:
logistic regression of per-item retention on `log2(1 + L)`, where `L` is the full
model's answer position. `L` is pre-treatment; retention conditions on the full model
being correct, so cell difficulty is conditioned out.

| model | intervention | locus | slope, MMLU | slope, GSM8K | difference |
|---|---|---|---|---|---|
| Llama 3.1 8B It | prune 25% | parameter | -0.16 [-0.50, 0.16] | **-0.99** [-1.35, -0.67] | **-0.83** [-1.33, -0.36] |
| Llama 3.1 8B It | prune 40% | parameter | -0.22 [-0.77, 0.25] | **-1.35** [-2.07, -0.83] | **-1.12** [-1.99, -0.37] |
| Llama 3.1 8B It | quant 4-bit | parameter | -0.19 [-0.52, 0.08] | **-0.95** [-1.29, -0.65] | **-0.75** [-1.20, -0.31] |
| Llama 3.1 8B It | readout, last | readout | -0.35 [-0.89, 0.25] | **-0.48** [-0.85, -0.11] | -0.13 [-0.81, 0.50] |
| Llama 3.1 8B It | readout, random | readout | -0.49 [-1.08, 0.20] | **-0.69** [-1.11, -0.29] | -0.20 [-1.05, 0.52] |
| Mistral 7B v0.3 | readout, first | readout | -0.27 [-0.80, 0.21] | **-0.85** [-1.43, -0.39] | -0.58 [-1.34, 0.13] |
| Mistral 7B v0.3 | readout, last | readout | **-0.75** [-1.35, -0.33] | **-0.83** [-1.36, -0.41] | -0.08 [-0.75, 0.66] |
| OLMo-3 7B base | prune 40% | parameter | -0.06 [-0.31, 0.12] | **-0.82** [-1.29, -0.48] | **-0.75** [-1.25, -0.31] |
| OLMo-3 7B base | readout, first | readout | -0.03 [-0.27, 0.34] | **-0.42** [-0.86, -0.03] | -0.39 [-0.96, 0.08] |
| OLMo-3 7B base | readout, last | readout | -0.23 [-0.46, 0.01] | **-0.68** [-1.03, -0.38] | **-0.45** [-0.87, -0.09] |
| Phi-4-mini It | prune 40% | parameter | -0.33 [-0.79, 0.13] | -0.31 [-1.20, 0.62] | 0.01 [-1.04, 1.00] |
| Phi-4-mini It | quant 4-bit | parameter | -0.24 [-0.57, 0.07] | **-1.45** [-1.86, -1.12] | **-1.20** [-1.71, -0.74] |
| Qwen 2.5 7B It | quant 4-bit | parameter | 0.11 [-0.28, 0.50] | **-0.78** [-1.13, -0.46] | **-0.89** [-1.42, -0.39] |
| Qwen 2.5 7B It | readout, first | readout | -0.39 [-0.92, 0.20] | **-1.32** [-1.77, -0.97] | **-0.93** [-1.69, -0.30] |
| Qwen 2.5 7B It | readout, random | readout | -0.50 [-1.22, 0.29] | **-1.24** [-1.90, -0.73] | -0.74 [-1.78, 0.16] |

Fifteen estimable conditions, five model families, both intervention loci:

| | count |
|---|---|
| MMLU slope significantly negative | **1 of 15** |
| GSM8K slope significantly negative | **14 of 15** |
| difference significant in the predicted direction | 8 of 15 |
| difference significant in the **wrong** direction | **0 of 15** |

Under the same model, the same intervention, the same free-generation protocol and
the same "long chain" regime, retention decays with answer depth when the answer is
carried by the model's own chain, and **does not decay at all** when the answer
remains recoverable from the prompt at answer time.

This is not a nuisance covariate. It is the effect.

## 4. Consequences for the paper identity

- Depth is not a control variable to be matched away. It is the explanatory axis.
- The distinction that organises the data is not `knowledge` vs `reasoning`, and not
  `parameter locus` vs `readout locus`. It is **where the answer comes from at the
  moment it is emitted**: recoverable from the prompt, or carried by the model's own
  generated prefix.
- `C3.2` becomes a secondary, descriptive observation. The depth-by-provenance law
  becomes the load-bearing claim, and it needs an experiment in which provenance is
  manipulated **within item**, because in E10 it is perfectly confounded with dataset.

## 5. Known limitations of this audit

The audit is observational in `L`:

1. `L` is not randomised. Among full-model-correct items, longer chains are plausibly
   harder, and compression may hurt harder items more. The MMLU cell is the internal
   control — it has the same difficulty-length coupling and shows no decay — but this
   is an argument, not an identification.
2. MMLU is 4-way multiple choice, so a reviewer will propose that its flat slope is a
   chance floor. Against this: retention sits at ~0.75 under `prune0p25` (far above a
   chance-driven floor) and at ~0.02 under readout truncation (far below chance, so
   parse failure, not guessing, dominates). The measure is not pinned at either end.
   It is still not a clean answer, and the confirmatory design must include an
   **open-ended long-generation knowledge cell**.
3. Provenance is confounded with domain: MMLU is general knowledge, GSM8K is
   arithmetic. Nothing here separates "prompt-recoverable" from "not arithmetic".

All three are removed by the same design, preregistered in `E12`.
