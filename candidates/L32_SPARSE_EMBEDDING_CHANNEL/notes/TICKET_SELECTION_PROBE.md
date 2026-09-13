# L32 — What is the certified ticket a function of?

**Status: EXPLORATORY. Not confirmatory. See §5 — the pre-declared condition was
mis-specified, and I am not claiming pre-registration support for this result.**

Run after E01 to decide whether L32 has a Main-level path. E01 established
*where the ticket acts*; this asks *what the selection procedure picks*.

---

## 1. Setup

KS-Lottery's own selection, reimplemented: tune the full input embedding matrix
(131M parameters, carried as an fp32 delta over the frozen bf16 rows so a 2e-5
step is not lost to rounding), parent's LR 2e-5 / 3 epochs / 10k pairs, then a
per-row statistic on the parameter shift. Six conditions:

`ca|es × explicit|paraphrase` template, plus `de/explicit`, plus a **seed
replicate** of `ca/explicit`.

## 2. Two rankings, two different tickets

| ranking | top-18 for ca/explicit | overlap with the paper's published 18 |
|---|---|---|
| KS **p-value** (the parent's criterion) | `\n . , the 1 to ' of and - I a He @ an l ... Trans` | 9/18 |
| **shift norm** | `atal an ' C : English late 1 following · sentence Trans from \n % . om English` | 4/18 |

Only **4–5 rows** clear `p < 0.05` in our reproduction, so a p-value ranking is
informative for about five rows and noise below that. Everything in §3–§4 uses
the shift norm. The p-value ranking is the one that resembles the published
ticket, and it is frequency-like, matching the parent's own observation that
winning tickets are high-frequency tokens.

## 3. The top of the ticket is the prompt template

Template tokens inside each condition's top-18 by shift:

| condition | template tokens in top-18 |
|---|---|
| ca/explicit | 13/18 — incl. `Trans late following from sentence English C atal` |
| ca/paraphrase | 13/18 — incl. `Please render next into Source Catal` |
| es/explicit | 15/18 — incl. `Trans late following sentence Span ish Spanish` |
| de/explicit | 14/18 — incl. `Trans late following sentence G erman German` |

Rewording the instruction swaps the template-specific rows for the new
template's rows. Changing the target language keeps `Trans late following
sentence English` and swaps only the language-name rows.

Frequency still explains much of the ranking overall: `spearman(shift, training
count) = 0.64–0.72`, and 13–16 of each top-18 are also in the top-18 by raw
count.

## 4. Overlap, against a noise floor

| contrast | k=18 | k=50 | k=100 | k=500 |
|---|---|---|---|---|
| **noise floor** — same language, data and template, seed differs | **18/18** | 48/50 | 96/100 | 435/500 |
| template differs, language+data fixed (ca) | 10/18 | 36/50 | 76/100 | 406/500 |
| template differs, language+data fixed (es) | 9/18 | 33/50 | 71/100 | 355/500 |
| language+data differ, template fixed (ca vs es) | 10/18 | 16/50 | 19/100 | 81/500 |
| language+data differ, template fixed (ca vs de) | 10/18 | 15/50 | 19/100 | 57/500 |

Two readings, both true, and they must be reported together:

- **At the parent's own ticket size (k=18), rewording the prompt destroys as much
  of the certified ticket as switching to a different language does** — 10/18
  survive either way, against a seed floor of 18/18. The parent reports
  cross-language ticket overlap as evidence of a shared multilingual subspace;
  the same overlap magnitude is produced by rewording the prompt inside one
  language, and the surviving rows are the tokens the two templates share.
- **Beyond the head (k ≥ 100) the ordering is dominated by training-data token
  frequency**, so same-data pairs overlap heavily whatever the template
  (76/100 vs 19/100). The template effect is a head effect, not a whole-ranking
  effect.

## 5. Where my own pre-registration failed

`CLAIM_NOVELTY_DELTA.md` §8 declared:

> if `overlap(ca/explicit, ca/paraphrase)` is comparable to
> `overlap(ca/explicit, es/explicit)`, the template account of ticket selection
> is wrong, and the Main-level path closes.

At k=18 those are 10 and 10 — **comparable, so by its letter the condition
fires**. But the condition was written without a noise floor, and it is
mis-specified: "comparable to the language contrast" was assumed to mean "the
template does not matter", when against an 18/18 seed floor it in fact means
"the template matters as much as the language", which is the opposite
conclusion. I also confounded language with training data, so the two arms of
the comparison were never symmetric.

I am therefore **not** treating §3–§4 as confirmatory evidence. The honest status
is: a mis-specified test, re-read after the fact with a control it should have
had from the start. A confirmatory version has to be pre-registered before it is
run.

## 6. What a confirmatory test looks like

Pre-register, then run once:

- ≥3 templates × ≥3 target languages, **training data held fixed across the
  language arm** where possible (or the data effect measured separately), ≥2
  seeds per cell;
- primary statistic: top-k ticket overlap at the parent's k, as a fraction of
  the seed floor;
- pre-declared prediction: `template-change overlap ≤ language-change overlap`,
  both well below the seed floor;
- pre-declared kill: template-change overlap indistinguishable from the seed
  floor.

Cost: ~15 selection runs at ~13 min each, well under a GPU-day.

## 7. Bearing on the verdict

E01's causal result stands on its own and is unaffected by any of this. This
probe does not yet establish the selection-side claim, but nothing in it
contradicts the claim either, and the k=18 picture is the shape the claim
predicts. The Main-level path is **open but unproven**, and proving it is cheap.
