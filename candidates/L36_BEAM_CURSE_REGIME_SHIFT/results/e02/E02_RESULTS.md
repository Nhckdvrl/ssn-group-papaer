# L36 E02 — results: post-training installs a *format-conditional* response boundary

**Protocol:** [`../../E02_PREREGISTRATION.md`](../../E02_PREREGISTRATION.md), frozen before the runs,
with three amendments recorded there (step-0 behavioural cell dropped; bf16 throughput fix; primary
statistic replaced after a pilot showed the registered one measured the wrong thing).
**Setup:** `Qwen/Qwen2.5-3B` base, full fine-tune, identical translation examples
(`newstest2018`, 2998 pairs), identical steps/batch/optimizer/seed. The **only** difference between
conditions is the surface format in which the boundary was taught. A single shared boundary token
(`<|quad_start|>`, unused, near-zero prior) is the only stop symbol in every condition and every
evaluation, which removes the stop-set cardinality and token-identity confounds.

## 1. The boundary is learned only in the format it was taught in

`p(<END> | prefix)` at the position where the reference translation ends, final checkpoint:

| condition | format A | format B | ratio | verdict |
|---|---|---|---|---|
| `A_ONLY` | **0.966** | **0.000** | 9.7e5 | trained format only |
| `B_ONLY` | **0.000** | **0.961** | 0.0 | **reversed** |
| `MIXED` | 0.962 | 0.963 | 1.0 | both |
| `A_ONLY_NOEOSLOSS` (control, stopped at step 200) | 0.000 | 0.000 | — | neither |

**P1′ (sign reversal between `A_ONLY` and `B_ONLY`): PASS.**
**P2 (mixed rescues both): PASS.**

Same weights-init, same data, same budget; the boundary follows the format it was supervised in.

## 2. The behavioural readout follows the boundary

Beam sweep under RAW (`length_penalty = 0`) scoring, 200 held-out `newstest2019` segments, **final
checkpoint** (step 1122):

| condition | format | b1 | b16 | b64 | length ratio @b64 | empty @b64 |
|---|---|---|---|---|---|---|
| `A_ONLY` | **A (trained)** | 35.62 | 40.51 | **39.51** | 0.95 | 0 % |
| `A_ONLY` | B (untrained) | 7.08 | 7.73 | **5.97** | **4.02** | 0 % |
| `B_ONLY` | A (untrained) | 8.07 | 8.22 | **6.82** | **4.23** | 0 % |
| `B_ONLY` | **B (trained)** | 36.07 | 40.88 | **39.38** | 0.96 | 0 % |
| `MIXED` | A | 35.35 | 40.46 | 39.76 | 0.96 | 0 % |
| `MIXED` | B | 35.57 | 39.63 | 37.53 | 0.96 | 0 % |
| `A_ONLY_NOEOSLOSS` (control) | A | 7.77 | 8.70 | 8.76 | 4.01 | 0 % |
| `A_ONLY_NOEOSLOSS` (control) | B | 6.74 | 6.62 | 4.82 | 3.94 | 0 % |

In the trained format, widening the beam from 1 to 64 **improves** quality (35.4 → 38.6) with a
stable length ratio: a correctly placed boundary makes wide-beam MAP decoding safe. In the untrained
format the model runs on to roughly **four times** the reference length and quality collapses to
BLEU ≈ 6–8.

**P3 (amended form): PASS.** The out-of-format signature is run-on generation, not an elevated empty
rate — as §3d of the preregistration predicted once the boundary symbol was made neutral. Zero empty
outputs anywhere in E02, which is the expected cost of removing the cardinality confound: a neutral
`<END>` cannot be emitted prematurely by a model that has never seen it in that context.

## 3. P4 is falsified as stated, and the reinterpretation matters

The registered P4 said the boundary crosses its threshold **before** greedy BLEU reaches 90 % of its
final value. Observed:

| step | 0 | 50 | 100 | 150 | 200 | 250 | 300 | 400 |
|---|---|---|---|---|---|---|---|---|
| `p(<END>@true end)`, `A_ONLY`, format A | 0.000 | 0.000 | 0.005 | 0.067 | **0.407** | 0.742 | 0.862 | 0.936 |

Greedy BLEU in the trained format is already 34.34 at step 200 against a final 35.35 — 97 % of final
while the boundary is at 0.41. So competence does **not** wait for the boundary; if anything the
order is the reverse of the prediction.

The reason is that the premise was wrong: `Qwen2.5-3B` can already translate before any fine-tuning
(its few-shot sibling scores BLEU ≈ 36), so this SFT is not teaching translation. That makes the
dissociation *cleaner* than predicted rather than weaker — what these 1100 steps add is the boundary,
not the capability — and it lines up with the Olmo-3 observation that SFT-chat translates slightly
*worse* than the base model few-shot (30.39 vs 35.29) while moving the boundary enormously.

It is stated here as **P4 falsified, claim revised**, not quietly reframed.

## 4. The masked-boundary control, with its caveat

`A_ONLY_NOEOSLOSS` (stopped early at step 200, cost; §8b) never learns the boundary in *either*
format — `p_end@true end = 0.000` throughout — and runs on at ~4× reference length even in its own
training format. Reading: the boundary has to be supervised; it does not fall out of learning the
response distribution. The caveat registered in §8 stands — masking the target does not leave the
token untrained, since it keeps receiving negative gradient elsewhere — so this is corroborating, not
load-bearing.

## 5. What E02 establishes

> Supervised fine-tuning does not make a model less willing to stop. It installs a **context-
> conditional response boundary** bound to the format in which generation was supervised. Where that
> boundary is installed, wide-beam MAP decoding is safe; where it is absent, generation does not
> terminate at all.

Together with the lineage and intervention results this closes the chain:

```
post-training  →  format-conditional generation boundary  →  stop-event geometry moves by orders
of magnitude  →  the beam exposure threshold moves  →  termination pathology appears or disappears
```

with the last two links measured (`results/stages/`), the first two now demonstrated causally in a
matched training experiment, and the classic-vs-modern endpoint measured on the frozen ACL-2022
substrate (`results/ext/`).

## 6. Limits to carry into any write-up

- One base model, one language pair, one direction, 3k training examples, BLEU/chrF only.
- Two synthetic formats, not a real chat template versus a real few-shot prompt.
- E02 cannot produce premature stopping (neutral boundary token), so the *classic* pathology itself
  is not reproduced here; it is reproduced in `results/ext/` and `results/stages/` with natural stop
  symbols. The two halves are complementary and must be reported as such.
- `MIXED` is a 50/50 partition of the same examples, so its per-format example count is half that of
  the single-format conditions; it nonetheless reaches the same boundary strength.
