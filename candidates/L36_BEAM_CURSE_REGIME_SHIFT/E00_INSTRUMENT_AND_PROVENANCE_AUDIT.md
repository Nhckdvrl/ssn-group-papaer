# L36 E00 — Instrument and Provenance Audit

**Status:** **MANDATORY PRE-E01 GATE — NO E01 RUN UNTIL PASS**
**Date frozen:** 2026-09-14
**Authorization:** this document supersedes `SELECTION.md` §7 for execution order.
`SELECTION.md` authorizes E01; **E01 may not run until every gate below passes.**
**Compute:** local `verl-clean` env (`/home/xiang/miniconda3/envs/verl-clean/bin/python`);
local GPUs on `fvcrc21` (4× RTX PRO 6000, 97 GB); no new environments, no package installs.

---

## 0. Why this gate exists

L34 died after a full training campaign because the experimental quantities could not be mapped
onto the theoretical claim *after* the numbers existed. L36's advertised advantage is that its
first-stage quantities are externally fixed (human-reference disagreement, beam width, translation
quality). That advantage is only real if three things are true **before** any beam curve is looked at:

1. we actually reconstructed *the old quantity*, not a look-alike;
2. our decoding/scoring pipeline is capable of exhibiting the classic pathology at all;
3. the modern model is not disqualified by evaluation-lineage exposure, and was frozen before
   anyone saw its beam curve.

E00 tests exactly those three things, plus a fourth bookkeeping item (§5) that prevents the
"not significant ⇒ law broken" failure mode.

E00 does **not** run any modern beam sweep. The modern beam curve is E01 and is not to be
produced, inspected, or summarized while this gate is open.

---

## 1. Gate A — SAME-QUANTITY substrate reconstruction

### A.1 What must be rebuilt

Stahlberg, Kulikov & Kumar (ACL 2022), eq. (1):

For an `n`-way annotated sentence with references `y_1 ... y_n`,

```
      (1 / C(n,2)) * sum_{i<j} d_edit(y_i, y_j)
u := ------------------------------------------
              (1 / n) * sum_i |y_i|
```

with `d_edit` the Levenshtein distance. Their MT-ende substrate is the **official WMT19
English→German test set** (`newstest2019`, 1997 segments) paired with the **additional
human-authored "AR" reference** of Freitag et al. (2020) — i.e. `n = 2`, so

```
u = d_edit(y_wmt, y_ar) / ((|y_wmt| + |y_ar|) / 2).
```

Sources:
- paper: https://aclanthology.org/2022.acl-long.591/ (§2, eq. 1, footnote 2)
- AR reference: https://github.com/google/wmt19-paraphrased-references (`wmt19/ende/wmt19-ende-ar.ref`)
- WMT19 test set: https://data.statmt.org/wmt19/translation-task/test.tgz

### A.2 Forbidden substitutions

`u` **must** come from human-reference disagreement. Prohibited for the load-bearing quantity:
model token entropy, ensemble disagreement, LLM-judge ambiguity ratings, paraphrase-model
distance, sentence length alone, any model-derived score.

The paraphrase references (`ARP`, `WMTP`, `HQ*`) are **not** used for `u`: only `AR` is an
independently written translation (Freitag et al. 2020; ACL-2022 footnote 2). Using a
paraphrase-of-the-reference would measure paraphrasing instructions, not task ambiguity.

### A.3 Underdetermined detail — declared, not hidden

The ACL-2022 paper does not state the **unit** of the Levenshtein distance (character vs. word).
Both are computed. **Primary:** character-level. Secondary/robustness: word-level.

Character level is primary because it is the reading under which our reconstruction reproduces the
paper's Figure 1 for MT-ende (mean `u` in the 0.3–0.45 band, increasing monotonically with
reference length); the word-level reading lands near 0.6, above the plotted range.

**AMENDED 2026-09-14 → A.3′ (see `results/e00/gateA_unit_resolution.md`).** The original A.3
threshold below failed (`rho = 0.904` passes, same-quartile `0.692 < 0.80`). Per A.3's own
instruction the unit was resolved against the authors' material *before any generation existed*:
the paper's Figure 1 levels turn out not to be reproducible under eq. (1) at all, while its Figure 6
binning (`u ∈ [0,0.33]/(0.33,0.66]/(0.66,1]`) is consistent with the character-level reading
(0.05% of segments above 1, vs 3.3% word-level). Character level is primary, and the gate is
**tightened**: every stratified result in Gate B and E01 must hold under **both** readings, computed
from the same generations. A claim that holds under only one reading does not count.

**Pass requirement A.3 (original, superseded):** the two readings must induce essentially the same stratification —
Spearman `rho >= 0.90` between character- and word-level `u`, and `>= 80%` of segments must land in
the same quartile under both. If they do not agree, the unit choice becomes a real researcher
degree of freedom and must be resolved against the authors' released numbers before E01.

### A.4 Freeze requirement

`u`, the quartile boundaries, and the segment ordering are computed and hashed **before any model
is loaded**. `results/e00/substrate_manifest.json` records sha256 of every input file, the `u`
table, and the quartile cut points. No later stage may recompute or re-bin `u`.

### A.5 Gate A pass/fail

- **PASS:** 1997 aligned segments; `u` computed per eq. (1); Figure-1-consistent profile;
  A.3 agreement satisfied; manifest hashed and committed.
- **FAIL:** any misalignment, any substitution of the quantity, or A.3 disagreement → **HOLD L36**.

---

## 2. Gate B — classic positive control (instrument capability)

### B.1 Claim under test

> Our decoding + evaluation pipeline, on this exact substrate, can exhibit the classic
> beam-search curse where the old law says it must: in the **high-uncertainty** stratum of
> `newstest2019` English→German, under classical (unnormalized) beam scoring.

This is a test of **our instrument**, not of any modern model. It runs first because it is cheap
and because failing it invalidates every downstream interpretation.

### B.2 Systems (declared in advance, in priority order)

1. **Primary classic system:** `facebook/wmt19-en-de` — the released FAIR WMT19 English→German
   Transformer (encoder–decoder), i.e. a system from the same era and shared task as the substrate.
   Revision pinned in the manifest.
2. **Secondary classic system (robustness, declared now):** `Helsinki-NLP/opus-mt-en-de` (Marian).

The gate is decided on the **primary** system. The secondary is reported in all cases and may
*not* be swapped into the primary role after the fact.

### B.3 Decoding semantics (the part TACL leaves implicit)

Every run reports its full generation contract. Two scoring semantics are run:

| tag | beam score | `length_penalty` (HF) | notes |
|---|---|---|---|
| `RAW` | `sum_t log p(y_t)` | `0.0` | the classic MAP objective; the regime in which the curse was originally reported |
| `NORM` | `sum_t log p(y_t) / |y|` | `1.0` | length-normalized, the modern default family |

Fixed across all cells: same source text, `num_return_sequences=1`, `early_stopping=False`,
`no_repeat_ngram_size=0`, `min_new_tokens=0`, no repetition penalty, identical
`max_new_tokens` budget, explicit BOS/EOS/PAD ids, deterministic (`do_sample=False`), fp32/bf16
recorded. Beam grid:

```
b ∈ {1, 4, 8, 16, 32, 64},  b_ref = 4,  b_large = 64  (b_large = 32 reported as sensitivity)
```

`b_ref = 4` is the classic peak reported by ACL-2022 (their MT BLEU peaks at beam 4).

### B.4 Quality measurement

- **Primary `Q`:** corpus BLEU against **both** references (WMT + AR), computed per stratum,
  sacrebleu-equivalent (`13a` tokenizer, case-sensitive, exp smoothing, closest-reference length
  for the brevity penalty).
- **Secondary:** single-reference (WMT) BLEU; corpus chrF2.
- **Diagnostics (not the target):** mean hypothesis/reference length ratio, empty-output rate,
  truncation (hit `max_new_tokens`) rate, mean beam score of the selected hypothesis.

BLEU and chrF2 are implemented in `src/mt_metrics.py` because `sacrebleu` is not present in the
frozen environment and the compute policy forbids installing packages. The implementation is
**validated against the upstream `sacrebleu` source run from a scratch checkout (no install)** on
the actual system outputs; the agreement check is recorded in `results/e00/metric_validation.json`.
Tolerance: `|ΔBLEU| <= 0.05`, `|ΔchrF2| <= 0.05`. Failing tolerance blocks the gate.

### B.5 Estimands

For system `m`, stratum `U`:

```
D_m(U)     = Q_m(b_large, U) − Q_m(b_ref, U)        # beam-widening effect
CURSE_m    = D_m(U_high) − D_m(U_low)               # uncertainty-conditioning of that effect
```

`U_high` = top quartile of frozen `u`; `U_low` = bottom quartile. Uncertainty is **frozen before
generation** (Gate A). Confidence intervals: paired bootstrap over segments, 1000 resamples,
seed fixed at 20260914, percentile intervals.

### B.6 Gate B decision rule (predeclared)

Under `RAW` semantics on the primary classic system:

- **PASS** requires both
  - **B.6.1 visible curse where the law predicts it:** `D_classic(U_high) <= −2.0` BLEU
    with bootstrap 95% CI upper bound `< −1.0`; and
  - **B.6.2 uncertainty conditioning:** `CURSE_classic <= −1.0` BLEU with bootstrap 95% CI
    upper bound `< 0`.
- **CONDITIONAL PASS:** B.6.1 holds but B.6.2 does not. E01 may proceed, but L36 may then
  **never claim** that it reproduced the *sentence-level uncertainty-conditioned* law with its own
  instrument; only the system-level curse is ours, and the conditional law remains a citation.
  This restriction must be carried verbatim into any E01 write-up.
- **FAIL:** B.6.1 does not hold → **INSTRUMENT FAILURE**. L36 is put on HOLD. It is explicitly
  forbidden to run the modern model and report a flat beam curve as "the law is broken", because
  a pipeline that cannot produce the curse on a 2019 encoder–decoder cannot license that claim.

### B.7 Anti-rescue clause

If the curse appears only under `NORM` and not under `RAW`, or only on the secondary system, the
result is recorded as-is and the gate is decided by B.6 as written. No post-hoc search over
`length_penalty`, stopping rules, `max_new_tokens`, prompts, or systems is permitted to manufacture
a passing control. The grid above is the whole grid.

---

## 3. Gate C — modern model provenance and eligibility

### C.1 Hard exclusion — disclosed WMT-evaluation lineage

A modern checkpoint is **ineligible** if its public documentation discloses supervised training on
WMT general-translation test/dev sets covering 2019.

Excluded by this rule, with citation:

| checkpoint | disclosed exposure | verdict |
|---|---|---|
| `Unbabel/TowerInstruct-*` (TowerBlocks v0.2) | dataset card lists **"WMT14 to WMT21 — General Translation"** in the supervised mix | **BANNED** |
| `haoranxu/ALMA-*` | ALMA paper §3.2: *"we collect human-written test datasets from WMT'17 to WMT'20"* as the parallel fine-tuning data | **BANNED** |

Sources: https://huggingface.co/datasets/Unbabel/TowerBlocks-v0.2 ; https://arxiv.org/pdf/2309.11674 (§3.2, App. Table 5).

This exclusion is the whole point of the gate: a model whose supervised data lineage contains the
WMT19 general-translation set cannot be used to argue that *this* test set's ambiguity no longer
produces search pathology. A flat beam curve there is uninterpretable, exactly the way L34's
primary estimand became uninterpretable.

The TACL-2025 LLM-SFT checkpoints are also not used as the modern arm: they are Llama2-7B models
supervised on WMT23 bilingual data and evaluated on `generaltest2023` German→English, i.e. a
different direction and substrate; reproducing them would additionally require training, which
`SELECTION.md` does not authorize.

### C.2 Eligible pool

Open-weight, decoder-only, instruction-tuned general LLMs with usable English→German ability and
**no disclosed WMT test-set supervision**, already present in the local HF cache:

- `meta-llama/Llama-3.1-8B-Instruct`
- `Qwen/Qwen2.5-7B-Instruct`, `Qwen/Qwen2.5-14B-Instruct`
- `google/gemma-3-12b-it`

### C.3 Substrate-blind capability screen

The modern model is selected on **`newstest2018` English→German**, a different year, disjoint from
the frozen substrate, using greedy decoding only (`num_beams=1`), on a fixed 300-segment subset
(first 300 segments, no selection). Selection rule, in order:

1. eligible under C.1;
2. highest `newstest2018` greedy chrF2 among the pool;
3. ties (`< 0.5` chrF2) broken by smaller parameter count.

**No beam sweep is run during selection**, on any substrate. The selected checkpoint, its
revision hash, prompt template, and generation contract are written to
`results/e00/modern_model_freeze.json` and committed **before** E01 generates anything.

A model that cannot produce well-formed German at all (greedy chrF2 `< 40` on newstest2018, or
`> 5%` malformed/empty outputs under the frozen prompt) is dropped from the pool. If no eligible
model clears the bar, **HOLD L36** — do not fall back to a banned checkpoint.

### C.4 Memorization probe (bounded, and honestly labelled)

Closed-data pretraining means C.1 can only exclude *disclosed* supervision. As a partial check,
on the frozen substrate the selected model is scored teacher-forced given the source:

- `NLL_wmt` = mean per-token NLL of the official WMT19 reference;
- `NLL_ar` = mean per-token NLL of the AR reference;
- `prefix-continuation exact-match rate`: feed source + first 50% of the WMT reference tokens,
  greedy-continue, measure exact match of the remainder.

Predeclared flags: exact-match rate `> 5%`, or `NLL_wmt` lower than `NLL_ar` by more than 0.5 nats
per token. Either flag ⇒ record a **CONTAMINATION WARNING** in the freeze file; E01 may still run,
but any law-break claim must report the probe and must additionally hold on a stratification that
excludes flagged segments. This probe cannot prove absence of contamination and will not be
described as if it could.

### C.5 Gate C pass/fail

- **PASS:** an eligible, non-banned checkpoint clears C.3 and is frozen with its contract.
- **FAIL:** no eligible model clears the bar → **HOLD L36**. Model-zoo search for a checkpoint that
  yields the desired flat curve is prohibited.

---

## 4. Gate D — power / resolution

Before E01, on the classic control's observed variance, report the paired-bootstrap MDE for
`D(U_high)` at the frozen substrate size (1997 segments; ~499 per quartile).

- **PASS:** MDE `<= 1.0` BLEU, i.e. the design can resolve the equivalence margin of §5.
- **FAIL:** MDE `> 1.0` BLEU → **HOLD**. Do not expand the substrate or pool models post hoc;
  the ACL-2022 multi-reference substrate is the whole substrate.

---

## 5. Predeclared law-break criteria for E01 (frozen here, before any modern curve)

This section exists so that "`Δ = −0.3`, `p = 0.28`" can never be reported as a broken law.

With `D_m(U)` and `CURSE_m` as defined in B.5, and the same beam grid, semantics, metric and
bootstrap:

```
REGIME_BREAK = CURSE_modern − CURSE_classic
ATT          = D_modern(U_high) − D_classic(U_high)      # attenuation of the high-u curse
```

E01 may claim the old law breaks **only if all three hold**:

1. **Equivalence, not silence.** `D_modern(U_high)` is statistically equivalent to no material
   deterioration: bootstrap 95% CI for `D_modern(U_high)` lies entirely above `−1.0` BLEU.
   A wide CI containing both `0` and `−3` is **not** a law break; it is an underpowered null.
2. **Material attenuation.** `ATT > 0` with bootstrap 95% CI lower bound `> +1.0` BLEU,
   i.e. the modern high-`u` curse is smaller than the classic one by more than the margin.
3. **Semantics-robust.** (1) and (2) hold under `RAW` semantics — the regime in which the classic
   curse exists. A flat curve that appears only under `NORM` is Outcome B of `SELECTION.md` §10
   (scoring-convention artifact) and **kills the Main route**.

Secondary, reported always, never load-bearing: the relative form
`D_m(U_high) / Q_m(b_ref, U_high)`, to address the objection that BLEU deltas are not comparable
across systems of different strength.

**Declared limitation, written now:** classic and modern are different systems at different quality
levels, so `ATT` mixes "regime" with "system". E01 alone therefore cannot attribute the attenuation
to the LLM regime *per se*; that attribution is the job of the later mechanism stage
(`SELECTION.md` §11, C2–C3). E01's job is only to establish that there is an attenuation worth
explaining.

---

## 6. Execution order (binding)

```
A  substrate build + freeze            (no model loaded)
B  classic positive control            (primary: facebook/wmt19-en-de)
C  modern eligibility + blind screen   (newstest2018 only)
D  power report from B's variance
--- gate decision written to results/e00/E00_VERDICT.md ---
E01 only if A,B,C,D pass or conditionally pass
```

Any gate that fails stops L36 at HOLD, cheaply, with no modern beam sweep run and no claim made.
