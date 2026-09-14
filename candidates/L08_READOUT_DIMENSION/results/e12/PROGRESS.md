# E12 Stage 1 — running log  `2026-09-14`

Host: `fvcrc21`, 4 idle cards, <=4 concurrent (fvcrc10/11/12/13/15 unreachable from
this host: ssh banner-exchange timeout, all five resolving to fvcrc00).
Env: `/home/xiang/miniconda3/envs/verl-clean/bin/python`. No package installed.

Reproduce: `$PY scripts/validate_e12_clamp.py`, `$PY scripts/analyze_e12.py`.

---

## Instrument validation — ALL PASS

| check | result |
|---|---|
| V0 answer position parses | 500/500 |
| V0 `L0` inside the trajectory | 15-241 tokens, all strictly inside |
| V0 no retokenization drift | clamped prefix decodes to a prefix of the reference text, 0/200 mismatches |
| **V1 `k=0` reproduces free-running** | e01 **0.0860** vs new runner **0.0880** |
| **V2 clamp through the answer recovers the full model** | full **0.7860** vs clamped **0.7660** |
| **V3 intervention active on every forward pass** | `lm_head_forward_passes` = **25200 in all three arms**, identical |

V1 is the one that mattered: the hand-written decode loop is equivalent to HF
`generate`. V3 confirms the clamp overrides the emission and not the computation.

## Two design faults found and fixed before they contaminated anything

**1. The preregistered matching statistic for `R~` was inapplicable.** It was the
task-level error rate of the clamped span (a calculator annotation `<<a op b=c>>`
with a wrong result). Against readout truncation it returns **0.000** — not because
the arithmetic is right but because that model emits no annotations at all:

| | contains `<<` |
|---|---|
| readout-truncated prefix | **1 / 500** |
| reference prefix | 329-369 / 500 |

The treated prefix does not differ from the reference by being *wrong*; it differs by
being a different kind of text. Replaced by **divergence from the reference prefix** —
mean positional token agreement, with normalized character edit distance alongside.

**2. `k` was derived from the clamp source.** For the `R~` arm that would have given
the corrupted and reference arms *different clamped span lengths*, confounding the
content contrast with depth — the exact failure this design exists to avoid. `k` now
always comes from the reference trajectory; only the clamped tokens come from the arm's
source. A filename collision that would have paired the wrong control with the wrong
arm was fixed at the same time.

## Temperature calibration for `R~` — succeeded, on a held-out split

Target (readout:first, f=0.5): divergence **0.927**, char edit **0.741**.

| tau | divergence | char edit | gap |
|---|---|---|---|
| 0.7 | 0.789 | 0.500 | 0.138 |
| 1.0 | 0.878 | 0.615 | 0.049 |
| **1.3** | **0.941** | **0.772** | **0.014** |
| 1.6 | 0.992 | 0.858 | 0.065 |
| 2.0-3.0 | 0.999-1.000 | 0.864-0.868 | 0.073 |

The grid brackets the target and **both divergence statistics select the same
temperature**, which is stronger than the preregistration required. The residual is
estimable by this route; the fallback clause (Stage 2 as the only separation) is not
triggered.

## Results so far — Llama 3.1 8B It / GSM8K, retention among the 393 items the full model answers correctly

| intervention | arm | frac | retention | total mediation vs free-running | 95% CI |
|---|---|---|---|---|---|
| readout:first | free-running | 0 | **0.0941** | — | — |
| readout:first | reference | 0.25 | 0.2214 | **+0.1272** | [0.076, 0.178] |
| readout:first | reference | 0.50 | 0.3995 | **+0.3053** | [0.249, 0.361] |
| readout:first | reference | 1.00 | 0.9720 | +0.8779 | [0.845, 0.911] — positive control |
| prune:0.4 | free-running | 0 | **0.0585** | — | — |
| prune:0.4 | reference | 0.50 | 0.1628 | **+0.1043** | [0.061, 0.148] |

Two things are established and one is not.

**Established: trajectory mediation is real, and it has a dose-response.** Clamping the
first quarter, then half, of the pre-answer trajectory recovers progressively more
(+0.127, +0.305) while the treated model still runs treated forward passes on every
step including all steps after the clamp releases. E07 explicitly could not obtain a
step-count dose-response; this design does, because it holds direct damage fixed.

**Established: it is not confined to the readout locus.** `prune:0.4` shows +0.104
[0.061, 0.148]. Under `E12_PREREGISTRATION.md` §8, a readout-only effect would have
been a kill. That gate is provisionally cleared.

**NOT established: the residual.** Every number above uses the `R` arm, which is
untreated *and* correct, so all of it is still readable as ordinary error propagation.
Nothing here may be reported as a result until `Y(R~) - Y(F)` is measured.

## An observation to keep, not yet a claim

The two interventions produce prefixes that are **almost identically divergent** from
the reference and **completely different in kind**:

| | divergence | char edit | keeps calculator annotations |
|---|---|---|---|
| readout:first | 0.927 | 0.741 | **1 / 500** |
| prune:0.4 | 0.931 | 0.758 | **229 / 500** |
| reference | — | — | 329 / 500 |

At essentially the same surface divergence, readout's mediation is ~3x prune's
(+0.305 vs +0.104). If mediation were purely a function of how far the prefix has
drifted from the correct one, these should be similar. **Caveat that blocks the
inference:** the two arms differ in free-running baseline (0.094 vs 0.059) and are not
severity-matched, which is precisely the error the demoted `C3.2` made. This is
recorded as a lead for a severity-matched comparison, not as a locus claim.

## Queued

- `R~` clamp at f=0.5 for readout:first — **the decisive run**
- `R~` clamp at f=0.5 for prune:0.4 (its own matched corrupted reference, target
  divergence 0.931)
- reference clamp f=0.75 (readout), f=0.25 (prune) to fill the dose-response
- throughput: bs=8 uses 20 GB of 97 GB and takes ~11 min per 500 items; Stage 1 in
  full is ~120 runs, so batch size must be raised and re-verified against V1.

---

# The residual came back NEGATIVE, and the control is what failed

`Y(R~) - Y(F) = -0.0712 [-0.104, -0.041]`, significantly below zero. That sign is not
in the preregistered outcome table (`E12_PREREGISTRATION.md` §8), which anticipated a
substantial positive residual or one near zero.

**It is not evidence about provenance. The corrupted control is worse than the treated
prefix, not matched to it.** Inspecting the prefixes:

```
REFERENCE Z(0) : " Janet eats 3 + 4 = <<3+4=7>>7 eggs every day.\nSo she has 16 - 7 = ..."
TREATED   Z(T) : "  4+  3  =  7 eggs eaten or cooked by  7 eggs  7  7  7  7  7  7 ..."
CORRUPTED Z~(0): " Janet's ducks lay 16 per day, but she bakes 4 into her muffin
                   recipes. She also consumes as much of yester<KO>.ddvoice heelsant<RU>)eanth+dAss destro"
```

The matching statistic called these equally divergent (0.927 vs 0.941). They are not
equally *usable*: the tau=1.3 sample degenerates into multilingual garbage, while the
treated prefix, degenerate as it is, is still manipulating the problem's own numbers.

The root cause is the statistic. Positional token agreement saturates near 0.93 for any
two different texts because a single insertion misaligns everything after it, so
"both 0.93" means "both almost entirely different" and constrains quality not at all.
This is the "matches rate, not type" limitation recorded in §4 of the preregistration,
cashing out in the most direct way available.

**Recorded as a failed control, not as a result.** The residual is not estimated by
this route, and the earlier `Y(R) - Y(R~) = +0.377` is inflated by the same failure and
is equally uninterpretable.

## Replacement control: cross-treatment clamping, which needs no calibration

Drop "untreated but incorrect" and ask a sharper question whose quality match is
automatic:

| clamp source | what it is |
|---|---|
| `Z(T)` | produced under **this** perturbation (free-running) |
| `Z(T')` | produced under a **different** perturbation, on the same items |
| `Z(0)` | untreated and correct |

The free-running retentions are 0.094 (readout) and 0.059 (prune), so the two treated
prefixes are already of comparable quality — no temperature calibration, no matching
statistic, nothing to mis-specify.

- `Z(T)` specifically better for its own model than `Z(T')` -> a **same-perturbation**
  effect; exposure bias cannot absorb it.
- `Z(T)` and `Z(T')` interchangeable -> the prefix's **origin** does not matter beyond
  its quality; the honest reading is error propagation and the ceiling drops.

Running: readout model on prune's prefix, prune model on readout's prefix, plus
**V4**, a new instrument check — clamping a model to its own free-running prefix must
reproduce free-running exactly.

## What stands regardless of how the residual resolves

The reference-arm dose-response is clean and monotone:

| f | 0 | 0.25 | 0.50 | 0.75 | 1.00 |
|---|---|---|---|---|---|
| readout:first retention | 0.094 | 0.221 | 0.400 | 0.725 | 0.972 |

with the treated model running treated forward passes on every step, including every
step after the clamp releases. E07 stated explicitly that it could not obtain a
step-count dose-response; this design does, because it holds direct damage fixed and
varies only how much of the conditioning context is treatment-generated.

`prune:0.4` is weaker and its low dose is null: 0.059 -> 0.071 (f=0.25,
[-0.023, 0.048], n.s.) -> 0.163 (f=0.5, +0.104 [0.061, 0.148]).
