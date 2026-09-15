# L36 E03 — results: the out-of-sample test, scored against the seal

**Protocol:** [`../../E03_PREREGISTRATION.md`](../../E03_PREREGISTRATION.md), sealed in commit
`65adf3b` with the ten ranks and their predicted bands, **before any beam search was run on any of
these systems**. This document scores that seal. **P1, P3 and P4 pass. P2 fails its registered
falsifier**, and the failure is reported first.

## 0. P2 is falsified as registered

> **P2 (registered):** Spearman(measured rank, observed empty@64) over the ten held-out systems
> `≤ −0.70`. **Falsifier: fails if Spearman > −0.70.**

**Observed: −0.673. P2 fails.**

It fails by 0.027, and it fails for a structural reason that is visible in the data: five of the ten
systems produced *exactly* 0.0 % empties, so ten of the forty-five pairs are tied on the outcome
variable, and Spearman's ρ — which is Pearson's r on ranks and has no tie correction — is deflated
by those ties.

That diagnosis does not rescue the prediction. **I registered ρ, I registered the threshold, and the
number came in on the wrong side of it.** P2 is recorded as failed. The lesson for the protocol is
that ρ was the wrong statistic to register for an outcome that saturates at a floor, and that should
have been foreseen when the bands themselves predicted a floor for six of the ten cells.

Two tie-aware statistics are reported **for information only, clearly marked post hoc**, and are not
substituted for P2 in any claim:

- Kendall's τ-b (tie-corrected): **−0.680**
- AUC of rank separating the collapsing cells (≥ 8 % empty) from the safe ones: **1.000** (4 vs 6);
  collapsing ranks {14, 24, 33, 43}, safe ranks {342, 625, 1210, 23785, 46738, 54458}

Any future registration of an ordinal prediction on this quantity will use τ-b, and that choice is
recorded here rather than applied retroactively.

## 1. P1 — the banded prediction: 10/10

| # | system | interface | `rank` | `b*` | **predicted** | **observed empty@b64** | lenR | BLEU b1 → b64 | |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `Qwen2.5-7B-Instruct` | few-shot | 14 | 7 | 5 – 60 % | **29.5 %** | 0.52 | 34.0 → 17.1 | ✓ |
| 2 | `Qwen2.5-7B` (base) | few-shot | 24 | 12 | 5 – 60 % | **45.5 %** | 0.36 | 37.5 → 7.8 | ✓ |
| 3 | `Mistral-7B-v0.3` (base) | few-shot | 33 | 17 | 5 – 60 % | **55.0 %** | 0.33 | 38.9 → 3.5 | ✓ |
| 4 | `Meta-Llama-3.1-8B-Instruct` | few-shot | 43 | 22 | 5 – 60 % | **32.0 %** | 0.54 | 44.1 → 22.3 | ✓ |
| 5 | **`Phi-4-mini-instruct`** | **few-shot** | **342** | 171 | **0 – 8 %** | **2.5 %** | 0.91 | 41.2 → 41.0 | **✓** |
| 6 | `gemma-3-4b-it` | chat | 625 | 313 | 0 – 8 % | **0.0 %** | 1.00 | 42.9 → 43.8 | ✓ |
| 7 | `Phi-4-mini-instruct` | chat | 1210 | 606 | 0 – 8 % | **0.0 %** | 0.97 | 41.1 → 40.4 | ✓ |
| 8 | `Meta-Llama-3.1-8B-Instruct` | chat | 23785 | — | 0 – 8 % | **0.0 %** | 0.98 | 44.8 → 48.0 | ✓ |
| 9 | `Qwen2.5-7B-Instruct` | chat | 46738 | — | 0 – 8 % | **0.0 %** | 0.96 | 36.1 → 38.5 | ✓ |
| 10 | `Qwen2.5-14B-Instruct` | chat | 54458 | — | 0 – 8 % | **0.0 %** | 0.99 | 41.3 → 43.2 | ✓ |

Every one of the ten landed inside the band its rank assigned it before the search was run. The
bands are wide — 5–60 % is not a sharp prediction — but they were fixed in advance, they are the
same bands that hold on all 22 calibration systems, and the *binary* consequence (collapse vs. not)
is decided correctly in all ten.

**Cell 5 is the one that was placed there to hurt.** `Phi-4-mini-instruct` evaluated out of format is
the only instruct checkpoint in this project whose out-of-format rank lands in the safe stratum
(342). If the rule were an artefact fit to the Olmo-3 and Tülu-3 lineages, this cell should have
collapsed like every other out-of-format instruct cell. It did not: 2.5 % empty, length ratio 0.91,
BLEU flat (41.2 → 41.0). The rank, not the training stage and not the interface, called it.

## 2. P3 — format keying, on three families outside both lineage sweeps: 3/3

Same weights, two interfaces:

| family | few-shot rank | chat rank | empty@64 few-shot | empty@64 chat | |
|---|---|---|---|---|---|
| Qwen2.5-7B-Instruct | 14 | 46738 | 29.5 % | 0.0 % | ✓ |
| Meta-Llama-3.1-8B-Instruct | 43 | 23785 | 32.0 % | 0.0 % | ✓ |
| Phi-4-mini-instruct | 342 | 1210 | 2.5 % | 0.0 % | ✓ |

The sign is stable in all three. Note that Phi-4-mini shows the *smallest* gap (3.5×, versus 3300×
and 550×) and is also the only one that does not collapse out of format — consistent with the
Tülu-3 finding that the keying is directionally general but its magnitude is lineage-specific, and
with the position that magnitude, not the existence of keying, is what determines behaviour.

## 3. P4 — no third failure mode: vacuously satisfied

P4 predicted that any `rank ≥ 128` system losing quality from beam 4 to 64 would do so by run-on
(length ratio > 1.3), not by emptying. **No held-out system with `rank ≥ 128` lost more than 1 BLEU
at all** — the six safe cells are flat or improving (cell 8: 44.8 → 48.0). The prediction is
therefore satisfied without being tested; it is recorded as **vacuous, not as a pass**, and the
run-on channel remains evidenced only by the classic `de→en` cell (lenR 2.45).

## 4. What this licenses

The sentence that E03 was registered to license, and that the results support:

> The position-0 stop rank, measured from one forward pass before any search is run, predicts out of
> sample which systems lose outputs to beam search and roughly how many — across five model
> families, 3B to 14B, base and instruct checkpoints, and both generation interfaces.

Against that: **the ordinal form of the claim was registered badly and failed.** The rule's
demonstrated strength is banded and near-binary, not finely ordinal, and it should be stated that
way. It also says nothing yet about decoders other than HuggingFace beam search — that is E04.

## 5. Caveats

- The `rank ≤ 2b` entry bound is algorithmic, not empirical; what is tested here is that the
  *magnitude* of the rank predicts the behavioural outcome across systems. See
  `STAGE_LINEAGE_FINDINGS.md` §0a.
- One substitution was made in the held-out set (`SmolLM2-1.7B` → `Phi-4-mini-instruct` few-shot)
  for a broken cached tokenizer, before any rank or beam existed for either cell. Recorded in the
  prereg §2.2.
- Beam cells are 200 segments, ranks 400 (100 for the beam-stage re-probe); single substrate,
  En→De only; raw BLEU values across families are not quality comparisons, since the WMT19
  exposure of these checkpoints is unknown.
