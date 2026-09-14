# L36 — ceiling assessment (E00-EXT)

**Question:** can L36 reach a Main-level narrative; failing that, a finding-level one; failing
both, does it stop?

**Status of this evidence:** everything here is **outside** the pre-registered E00 gate. E00's own
verdict (HOLD, `../e00/E00_VERDICT.md`) stands as written. These runs were authorized afterwards to
find the candidate's ceiling. Two predictions were registered before their runs
(`EOS_BIAS_PREDICTION.md`, `FEWSHOT_INTERFACE_PREDICTION.md`); everything else is descriptive.

**Substrate throughout:** the frozen `newstest2019` En→De substrate from Gate A, multi-reference
BLEU (WMT + AR), uncertainty quartiles frozen before any generation.

---

## 1. What the extension establishes

### 1.1 The classic curse, followed into its catastrophic range — the uncertainty conditioning never turns over

`facebook/wmt19-en-de`, RAW (`length_penalty = 0`), full substrate (n = 1997):

| beam | BLEU | empty % | len ratio | `D(4→b)` for Q1 / Q2 / Q3 / Q4 | `CURSE = D(Q4) − D(Q1)` |
|---|---|---|---|---|---|
| 4 | 47.76 | 0.05 | 1.050 | — | — |
| 16 | 47.57 | 5.36 | 0.948 | −1.83 / +0.67 / +0.19 / −0.05 | +1.78 |
| 64 | 40.80 | 13.12 | 0.820 | −11.34 / −8.16 / −5.11 / −3.88 | **+7.47** |
| 128 | 16.11 | 40.11 | 0.444 | −31.45 / −38.02 / −30.46 / −25.47 | **+5.98** |
| 512 | 3.67 | 54.43 | 0.253 | −42.90 / −49.52 / −41.54 / −37.99 | **+4.90** |

The E00 gate stopped at beam 64, where the sign could still have been an artifact of a mild effect.
It is not: ACL-2022's own Figure 2 puts the catastrophic drop at beams 500–1000, and there the
damage is *still* concentrated in the **low**-uncertainty quartile. Same sign on the secondary
classic system (`opus-mt-en-de`, `CURSE = +2.17`, CI `[+0.74, +3.70]`) and under both `u` readings.

### 1.2 The mediator is termination geometry, and it is not uncertainty

Model-side quantity, measured before any beam search: `log p(stop immediately | source)`.

| system | interface | `log p(stop)` | `log p(greedy)` | empty beats greedy |
|---|---|---|---|---|
| `facebook/wmt19-en-de` | sentence-level NMT | **−9.31** | −18.88 | **61.6 %** |
| `google/gemma-3-12b-it` | chat | **−35.33** | −23.02 | 2.3 % |
| `Qwen/Qwen2.5-7B-Instruct` | chat | −25.98 | −7.02 | 1.3 % |
| `Qwen/Qwen2.5-7B` (base) | 2-shot plain text | **−9.41** | −34.25 | 100 % |

Logit model of "does this segment collapse to an empty hypothesis at beam 64" on the classic
system (n = 1997, base rate 0.131):

| predictors | pseudo-R² | coefficients |
|---|---|---|
| `u` only | **0.002** | `u = −0.11` (p = 0.10) |
| `log p(stop)` only | **0.176** | `+1.30` (p = 1.7e-48) |
| both | 0.177 | `log p(stop) = +1.30`; `u = −0.03` (p = 0.66) |
| both + reference length | 0.276 | `log p(stop) = +1.58`; length `+0.87`; `u = −0.15` |

The human-reference uncertainty that the whole candidate was built on carries **no** sentence-level
information about the curse once the model's own stopping probability is in the model.

### 1.3 The modern non-collapse is real, not a scoring convention

This is the result that keeps L36 alive at all. `SELECTION.md` §10 Outcome B said: if the modern
flat curve is produced by length normalisation, kill the Main route. It is not.

`gemma-3-12b-it`, **RAW** (`length_penalty = 0`), same substrate, first 400 segments:

| beam | BLEU | empty % | len ratio |
|---|---|---|---|
| 1 | 45.14 | 0 | 0.997 |
| 4 | 45.91 | 0 | 0.998 |
| 16 | 45.76 | 0 | 0.997 |
| 64 | **46.12** | **0** | 0.995 |

Under the exact scoring semantics in which the 2019 system loses 44 BLEU and empties 54 % of its
output, the modern model does not move.

Matched head-to-head on the **same 400 segments**, same semantics, same beam grid:

| system | BLEU beam 4 → 64 | empty % 4 → 64 | len ratio 4 → 64 |
|---|---|---|---|
| `facebook/wmt19-en-de` (2019) | 48.61 → 43.28 (**−5.33**) | 0 → **8.75** | 1.011 → 0.845 |
| `Helsinki-NLP/opus-mt-en-de` (2020) | 46.97 → 45.04 (−1.94) | 0 → 0 | 0.950 → 0.902 |
| `google/gemma-3-12b-it` (2025) | 45.91 → **46.12 (+0.21)** | 0 → **0** | 0.998 → 0.995 |
| `facebook/wmt19-en-de` at beam 128 | 20.15 | 33.75 | 0.501 |
| `facebook/wmt19-en-de` at beam 512 | 6.89 | 48.50 | 0.311 |

### 1.4 A calibrated knob on that one quantity brings the curse back

Pre-registered in `EOS_BIAS_PREDICTION.md` (written before the runs, from the 26-nat gap in §1.2).
`gemma-3-12b-it`, beam 64, RAW, bias added to the end-of-sequence logits:

| bias | BLEU | empty % | len ratio |
|---|---|---|---|
| 0 | 46.12 | 0.00 | 0.995 |
| +13 | 46.21 | 0.00 | 0.992 |
| **+26** (matches the classic `log p(stop)`) | 41.43* | 7.50* | 0.876* |
| +39 | 2.27 | 4.50 | 0.243 |

\* step-0-only variant at beam 16; the all-step variant at beam 64 gives BLEU 41.89 / 0.75 % empty /
0.859. The step-0-only variant is the closer analogue: the classic model's peculiarity is that
*stopping at the first step* is cheap. Biasing every step instead changes the whole length
distribution and degrades greedy decoding badly (BLEU 26.84 at beam 1), which is a different
intervention and is reported as such.

Dose-response over bias is monotone and the null dose (+13) is genuinely null. Over beam width, with
the calibrated step-0 bias held fixed at +26:

| beam | BLEU (bias 0) | BLEU (step-0 bias +26) | empty % (bias 0 → +26) |
|---|---|---|---|
| 1 | 45.14 | 42.80 | 0 → 4.00 |
| 4 | 45.91 | 41.10 | 0 → 7.75 |
| 16 | 45.76 | 41.43 | 0 → 7.50 |
| 64 | 46.12 | 40.95 | 0 → **8.50** |

**Caveat, stated plainly:** the empty rate does grow with beam width under the intervention
(4.0 → 8.5 %), which is the classic mechanism — wider search surfaces the cheap empty hypothesis —
but roughly half of the BLEU damage is already present at greedy decoding, because a +26 bias makes
the stop token the argmax outright for some segments. The classic signature (greedy clean, wide beam
catastrophic) is therefore only partly reproduced. A cleaner version would calibrate the bias to the
classic model's *rank* of EOS at step 0 rather than its log-probability; that is not run here.

### 1.5 Interface probe — measured, but the behavioural test was voided

Termination geometry is not a property of "being an LLM": the same family measured under a plain
2-shot text prompt, where a translation ends at the line break, looks like the 2019 system
(`Qwen2.5-7B` base: `log p(stop) = −9.41`; `Qwen2.5-7B-Instruct`: `−15.32`) rather than like the
chat condition (`−25.98`). That suggested a sharp prediction (`FEWSHOT_INTERFACE_PREDICTION.md`):
the curse should follow the *interface*, not the model.

**The behavioural test of that prediction is void and is not reported as evidence.** The few-shot
generation contract could not actually be enforced: Qwen's BPE merges the line break into
multi-character tokens (e.g. `"\n\n` as one id), so `eos_token_id = [198, 271]` never fires,
59.8 % of the sweep's outputs hit the 128-token cap, and the hypotheses were post-hoc truncated at
the first line. The search therefore optimised 128-token continuations, not sentence-level
translations, and the empty hypothesis was never a candidate. The cells are kept
(`results/ext/gen/qwen25-7b-base_fewshot_b*`) and marked void; the prediction is **untested**, not
refuted. Testing it properly needs string-level stopping inside the beam search.

---

## 2. What it does not establish

1. **ACL-2022's actual claim is untouched.** Their conditional law is *task-level* (MT vs GEC) and
   about *search difficulty and mode adequacy*, measured with exact search. Our search-error proxy
   (best hypothesis found anywhere in the beam grid) saturates at 55–90 % and cannot resolve a
   `u`-gradient within length buckets, so we can neither confirm nor refute the search-difficulty
   half of their law. What we refute is the *sentence-level quality-damage* reading that L36's E01
   estimand assumed — a reading they did not assert.
2. **One language pair, one direction, one modern checkpoint, BLEU/chrF only.** No COMET (not in
   the frozen environment), no second modern family in the beam sweep.
3. **The E00 power gate still fails.** MDE 2.71–3.18 BLEU per uncertainty quartile against a 1.0
   BLEU equivalence margin. Every stratified statement above is descriptive, not an equivalence
   test.
4. **The interface claim is untested.** See §1.5: the measurement is in hand, the behavioural
   experiment was voided by an unenforceable stop symbol, and it would have to be redone with
   string-level stopping before anything is claimed from it.

---

## 3. Novelty audit

| owner | owns | leaves open |
|---|---|---|
| Koehn & Knowles 2017 | the curse exists | — |
| Murray & Chiang 2018 | it is a length/EOS bias; normalisation fixes it | — |
| Stahlberg & Byrne 2019 | the exact mode is the empty string for >50 % of sentences | nothing about the LLM regime |
| Eikema & Aziz 2020/2022 | mode inadequacy, MBR | — |
| Stahlberg et al. 2022 | uncertainty → mode adequacy / search tractability, **task level** | the sentence-level quality reading; the modern regime |
| Pang et al. 2025 (TACL) | the observation that LLM-MT lacks the beam challenge | why; and whether it survives matched scoring semantics |
| Wu et al. 2025 | persistent likelihood–quality misalignment in LLM-MT | why misalignment no longer becomes a search pathology |

**What is genuinely ours:** (a) the sentence-level reversal, robust to beam 512 and to two systems;
(b) the demonstration that the modern flat curve survives matched RAW semantics, which removes the
"decoding-config artifact" explanation; (c) `log p(stop)` as the measured mediator across regimes,
with the classic/modern gap quantified at 26 nats; (d) the calibrated causal knob in both directions.

**What a reviewer compresses it to:** *"the beam-search curse is the empty-hypothesis problem
(2018–2019), and instruction-tuned models do not emit empty strings."* Everything above is an
answer to that sentence, but the sentence is the wall.

---

## 4. Ceiling verdict

```yaml
main_level:     NO        # the mediator is a quantity the 2018-2019 literature already owns;
                          # the new content is a correction plus a quantification, not a new law
finding_level:  YES       # short/Findings-scale, on the strength of 1.1 + 1.3 + 1.4
original_L36_identity: DEAD   # "revise the uncertainty law" is not the answer; uncertainty is
                              # not in the causal path at the sentence level
```

The honest one-sentence result is:

> The beam-search curse was never carried by intrinsic uncertainty. It is carried by how much
> probability a model puts on stopping immediately; classic sentence-level NMT puts ~e^−9 there and
> collapses under wide search, instruction-tuned LLM-MT puts ~e^−26…−35 there and does not, and
> restoring that one quantity restores the collapse.

That is a true, causally supported, cheaply obtained statement. It is not a revised conditional law
about ambiguity, which is what L36's Selection promised.

---

## 5. What each route would cost

**Findings-scale paper (recommended if anything):**
3–4 language pairs with multi-reference or at least standard test sets, 3–4 modern checkpoints
(one base-LM few-shot condition included), COMET or a semantic metric alongside BLEU, the beam grid
to 512 on the classic side, and the two-directional knob. All inference-only; roughly one week of
local GPU time and a careful related-work section whose whole job is to survive the compression in
§3.

**Main-scale:** would need the account to predict something beyond MT beam search — e.g. the same
termination-geometry measure predicting collapse in other decoding pathologies or other tasks — and
that is a different, much larger candidate.

**Stop:** also defensible. The E00 power gate failed, the original identity is dead, and what
remains is a correction plus a quantification of a known mechanism.
