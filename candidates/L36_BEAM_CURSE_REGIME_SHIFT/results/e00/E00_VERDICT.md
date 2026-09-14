# L36 E00 — Verdict

**Date:** 2026-09-14
**Protocol:** [`../../E00_INSTRUMENT_AND_PROVENANCE_AUDIT.md`](../../E00_INSTRUMENT_AND_PROVENANCE_AUDIT.md) (pre-registered and committed before any model was run: `ab76807`)
**Compute:** local `verl-clean` env; `fvcrc21`, 4× RTX PRO 6000, ≤4 cards concurrently (cap is 8).

## Verdict

```yaml
gate_A_substrate:        PASS (with a recorded reproducibility finding; amended to A.3')
metric_validation:       PASS (exact agreement with sacrebleu 2.4.3 on all 22 cells)
gate_B_positive_control: CONDITIONAL PASS  (B.6.1 pass on the primary system; B.6.2 fails,
                                            and fails *significantly in the opposite direction*)
gate_C_modern_model:     PASS (google/gemma-3-12b-it selected substrate-blind; Tower/ALMA banned)
gate_D_power:            FAIL (MDE 2.71-3.18 BLEU vs the 1.0 BLEU equivalence margin)
overall:                 HOLD L36 — E01 NOT AUTHORIZED
```

Gate D failing is by itself decisive under the protocol (§4: "MDE > 1.0 BLEU → HOLD. Do not expand
the substrate or pool models post hoc"). But the substantive reason to stop is Gate B, and it is
worse for the candidate than a power problem: **the sentence-level law that E01's primary estimand
was going to test does not exist on classic systems — it runs the other way.**

---

## Gate A — substrate (PASS, with a finding)

1997 aligned segments of `newstest2019` En→De; `u` per ACL-2022 eq. (1) from the official WMT
reference and the independently authored Freitag et al. (2020) `AR` reference. Frozen and hashed
before any model was loaded: `substrate_manifest.json`.

The predeclared A.3 agreement check failed (Spearman `rho = 0.904` passes; same-quartile
`0.692 < 0.80`), which triggered A.3's own instruction to resolve the edit-distance unit against
the authors' material. Doing so produced a **reproducibility finding** worth carrying into any
future write-up (`gateA_unit_resolution.md`):

- the paper's **Figure 1** MT-ende levels (≈3.5/8.5/14/23% by length bucket) are **not reproducible
  under eq. (1)** in any unit — they grow ∝ sentence length, which no per-segment length-normalised
  quantity does;
- the paper's **Figure 6** bins (`u ∈ [0,0.33]/(0.33,0.66]/(0.66,1]`) *are* consistent with our
  reconstruction, and pick out the character-level reading (0.05% of segments above `u = 1`, vs
  3.3% for word-level).

Resolution: character-level primary, and the gate was **tightened** to A.3′ — every stratified
result must hold under **both** readings. All Gate B results below do.

## Metric validation (PASS)

`src/mt_metrics.py` (13a BLEU, multi-reference, closest-ref BP, exp smoothing; chrF2 char-order 6,
β=2) vs vendored upstream sacrebleu 2.4.3: **max |difference| = 0.0000** over all 22 generation
cells × {full, random-500} subsets (`metric_validation.json`). Tolerance was 0.05.

## Gate B — classic positive control

Primary system `facebook/wmt19-en-de`; secondary `Helsinki-NLP/opus-mt-en-de`. Beam grid
`{1,4,8,16,32,64}`, `b_ref = 4`, `b_large = 64`, two scoring semantics, full contract logged per
cell.

### The curse reproduces — but only under unnormalised scoring

`facebook/wmt19-en-de`, multi-reference BLEU over all 1997 segments:

| beam | RAW BLEU | RAW chrF2 | RAW len-ratio | RAW empty % | NORM BLEU | NORM len-ratio |
|---|---|---|---|---|---|---|
| 1 | 43.81 | 68.70 | 1.103 | 0.00 | 43.81 | 1.103 |
| 4 | 47.76 | 69.24 | 1.050 | 0.05 | 47.35 | 1.068 |
| 8 | 48.46 | 68.57 | 1.016 | 1.25 | 48.07 | 1.054 |
| 16 | 47.57 | 65.81 | 0.948 | 5.36 | 48.83 | 1.049 |
| 32 | 46.10 | 64.37 | 0.915 | 6.66 | 48.76 | 1.045 |
| 64 | **40.80** | 59.17 | 0.820 | **13.12** | **48.89** | 1.041 |

`D_all(RAW) = −6.96` BLEU, with the textbook signature: outputs shorten (1.05 → 0.82 of reference
length) and 13% of segments collapse to an **empty** hypothesis. Under `NORM` the same checkpoint
shows **no curse at all** — quality rises monotonically to beam 64.

### B.6.1 — the curse is visible in the high-`u` stratum: **PASS**

| system | reading | `D(U_high)` | 95% CI | B.6.1 |
|---|---|---|---|---|
| fsmt | `u_char` | −3.88 | [−5.92, −2.10] | **pass** |
| fsmt | `u_word` | −3.70 | [−6.07, −1.57] | **pass** |
| marian | `u_char` | −0.59 | [−1.58, +0.42] | fail |
| marian | `u_word` | −0.74 | [−1.67, +0.25] | fail |

The gate is decided on the primary system, so B.6.1 passes. The secondary system shows only a mild
curse (`D_all = −1.67`), reported as declared.

### B.6.2 — uncertainty conditioning: **FAILS, with the sign reversed**

| system | reading | `D(U_low)` | `D(U_high)` | `CURSE = D_high − D_low` | 95% CI |
|---|---|---|---|---|---|
| fsmt | `u_char` | −11.34 | −3.88 | **+7.47** | [+2.89, +12.18] |
| fsmt | `u_word` | −10.90 | −3.70 | **+7.20** | [+2.41, +12.28] |
| marian | `u_char` | −2.77 | −0.59 | **+2.17** | [+0.74, +3.70] |
| marian | `u_word` | −2.65 | −0.74 | **+1.92** | [+0.36, +3.39] |

The predeclared direction was `CURSE ≤ −1.0` with the CI upper bound below 0. Observed: positive,
with CIs excluding zero, on **both** classic systems and **both** `u` readings. The beam-search
curse on this substrate is **monotonically stronger at LOW intrinsic uncertainty**
(`fsmt`, relative: Q1 −20.1%, Q2 −15.9%, Q3 −11.8%, Q4 −9.6%).

Per §B.6 this is a **CONDITIONAL PASS**: E01 could formally proceed but could never claim to have
reproduced the sentence-level uncertainty-conditioned law. In practice it is worse than that — see
"Why this stops the candidate".

### What the classic curse actually is here (`curse_decomposition.json`)

| | Q1 (low `u`) | Q2 | Q3 | Q4 (high `u`) |
|---|---|---|---|---|
| fsmt empty-rate @ beam 64 | 13.8% | 16.0% | 13.0% | 9.6% |
| fsmt `D` | −11.34 | −8.16 | −5.11 | −3.88 |
| fsmt `D` on segments non-empty in both cells | **+0.79** | **+2.01** | **+1.76** | **+0.82** |
| marian empty-rate @ beam 64 | 0% | 0% | 0% | 0% |
| marian `D` | −2.77 | −1.70 | −1.78 | −0.59 |

On the primary system the entire curse is the **empty/degenerate-hypothesis channel**; once
segments that go empty are excluded, widening the beam *improves* quality in every stratum. The
secondary system never emits an empty output and still shows a (smaller) curse via shortening
(length ratio 0.957 → 0.919). This is the Koehn & Knowles / Stahlberg & Byrne length-and-termination
pathology, not a diffuse degradation, and its `u`-conditioning is inherited from where empties land
and from how much BLEU a stratum had to lose.

## Gate C — modern model provenance (PASS)

Banned by disclosed WMT19 evaluation lineage, with citation (`../../E00_...md` §C.1):

- `Unbabel/TowerInstruct-*` — TowerBlocks-v0.2 card lists **"WMT14 to WMT21 — General Translation"**;
- `haoranxu/ALMA-*` — ALMA §3.2: *"we collect human-written test datasets from WMT'17 to WMT'20"*,
  which contains `newstest2019` itself.

Substrate-blind screen (newstest2018, first 300 segments, greedy, frozen prompt, **no beam sweep,
no newstest2019**):

| model | chrF2 | BLEU | malformed | eligible | clears bar |
|---|---|---|---|---|---|
| `google/gemma-3-12b-it` | **68.35** | 42.05 | 0.0% | yes | yes |
| `NousResearch/Meta-Llama-3.1-8B-Instruct` | 67.03 | 40.83 | 0.0% | yes | yes |
| `Qwen/Qwen2.5-14B-Instruct` | 63.08 | 37.10 | 3.7% | yes | yes |
| `Qwen/Qwen2.5-7B-Instruct` | 61.47 | 32.72 | 0.7% | yes | yes |

Selected and frozen: **`google/gemma-3-12b-it`** (`gateC_screen.json`).
(`meta-llama/Llama-3.1-8B-Instruct` is gated for this account; the ungated `NousResearch` mirror of
the same weights was screened instead, recorded as such.)

Memorization probe C.4: see `contamination_probe.json`.

## Gate D — power (FAIL)

Paired bootstrap over segments (1000 resamples, seed 20260914), `D(U_high)` on 499 segments:

| system / semantics | reading | SE | MDE (80% power) | required |
|---|---|---|---|---|
| fsmt RAW | `u_char` | 0.97 | **2.71** | ≤ 1.0 |
| fsmt RAW | `u_word` | 1.13 | **3.18** | ≤ 1.0 |
| fsmt NORM | `u_char` | 0.40 | **1.13** | ≤ 1.0 |
| fsmt NORM | `u_word` | 0.45 | **1.25** | ≤ 1.0 |

The frozen substrate cannot resolve the §5 equivalence margin of 1.0 BLEU in a single uncertainty
quartile — not even in the low-variance `NORM` regime. E01's law-break criterion #1 ("bootstrap 95%
CI for `D_modern(U_high)` lies entirely above −1.0 BLEU") is therefore unreachable by construction,
and §4 forbids enlarging the substrate or pooling models to fix it.

---

## Why this stops the candidate, beyond the failed power gate

L36's identity is: *an old conditional law (intrinsic uncertainty → beam-search pathology) breaks in
the LLM regime; find the condition that changed.* E00 was supposed to establish that the law exists
in our hands. Instead:

1. **The sentence-level version of the law is not there classically — it is reversed.** On two
   classic En→De systems, under both `u` readings, wide-beam damage concentrates in the *low*-`u`
   quartile. E01's declared primary estimand is the `beam × u` interaction; classically that
   interaction has the opposite sign. "Modern models don't show it either" would then be a
   comparison to a baseline that never showed it.
   ACL-2022's actual claim is *task-level* (MT vs GEC) and their beam range runs to 1000; this audit
   does not refute that. It refutes the within-MT, sentence-level reading that L36 built on.
2. **The classic/modern contrast reproduces inside a single 2019 encoder-decoder.** Flipping
   `length_penalty` from 0.0 to 1.0 on `facebook/wmt19-en-de` turns `−6.96` BLEU into `+1.54` BLEU
   across beam 4→64. TACL-2025's LLM sweep runs on HuggingFace generation defaults, i.e. the
   normalised regime. That is `SELECTION.md` §10 **Outcome B** (the reversal is a scoring/stopping
   convention), which the Selection says kills the Main route — and E00 reached it without the
   modern arm.
3. **What is left is a termination-geometry question**, not a law break: "do modern decoder-only
   LLMs also collapse to empty/short hypotheses under unnormalised beam search?" That is
   `SELECTION.md` §4 account B, a smaller paper, and it no longer needs the uncertainty substrate
   that gave L36 its claimed identification advantage.

## Recommendation

**HOLD L36.** Do not run E01 as specified. Total cost of reaching this: one afternoon on four local
cards, 22 classic-system generation cells plus a 4-model screen — no training runs.

Cheap things that could still be authorized, each as a *new* gate rather than a rescue of this one:

- **B-ext (one hour):** extend the classic grid to beams 128/256/512 on `facebook/wmt19-en-de`, the
  range where ACL-2022's own Figure 2 puts the catastrophic drop (−6% at 500, −20% at 1000), to test
  whether the `u`-conditioning ever turns over. The predeclared grid stopped at 64 and the anti-rescue
  clause (§B.7) forbids extending it inside this gate. If the reversal survives beam 512, the
  sentence-level law is dead and that is a publishable negative result about a well-cited paper in
  its own right — but it is **not** the L36 story.
- **A re-scoped candidate** built on termination geometry (empty/short-hypothesis rate under matched
  unnormalised scoring, classic vs modern), with an estimand whose variance is compatible with the
  substrate, and without claiming the uncertainty law as its mother phenomenon.

Both are new Selections. Neither is authorized here.
