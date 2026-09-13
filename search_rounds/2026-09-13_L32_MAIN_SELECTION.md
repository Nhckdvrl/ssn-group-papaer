# L32 — Selection (reopened): argue for Main

**Date:** 2026-09-13. Reopened at the user's request after E02 (`HOLD /
Findings`) and E03 (single-row sufficiency). This document argues the Main case
as strongly as the evidence permits, and then states what it cannot carry.

---

## 1. The claim

> **A certified, theorem-backed, published "ultra-sparse multilingual winning
> ticket" is reproduced by tuning one embedding row — the newline — and what it
> buys is not translation but termination.**

Short form: **the certified multilingual lottery ticket is a newline.**

## 2. Evidence in hand (all run, all committed)

| # | finding | scale |
|---|---|---|
| 1 | strict reproduction of the parent's en→ca headline | +29.50 [+28.59, +30.46], 3 seeds |
| 2 | 94–107% of the gain is termination, in **three** language pairs, using the parent's **own published tickets** | ca 0.938 / es 0.970 / ro 1.070; ro's translation content gets *worse* |
| 3 | same-checkpoint causal gating: the residue is entirely instruction-mediated | INSTRUCTION 1.00 [0.98,1.02]; SOURCE −0.00 [−0.01,0.01]; TARGET 0.05 |
| 4 | SOURCE null is not an opportunity effect | 7.73 vs 7.00 tuned-token occurrences per sentence, 25% of all source tokens |
| 5 | selection tracks the prompt beyond a seed ceiling | prompt arm 8.6/18 vs language arm 11.6/18 vs ceiling 17.4/18 |
| 6 | and it is **not** frequency | template rank 7–11 vs count-matched non-template rank 84–372; Wilcoxon p≤1e-3, β=+0.32..+0.44, **18/18 cells** |
| 7 | **one row suffices** | sufficiency 0.96–1.00 in 8/8 runs (`<s>` and `\n`, ca and es, 2 seeds) |
| 8 | not "any few rows" | 18 count-matched random non-template rows: 0.40–0.59 |
| 9 | norm-matched random delta destroys the model | spBLEU 0.05 |

The pieces are mutually predictive rather than a pile: (3) says the effect lives
in the instruction span; `\n` sits in the instruction span; (7) says `\n` alone
is enough. (6) says selection is about template membership, and `\n` is the one
row present in **all six** of the parent's published tickets.

## 3. What we do NOT refute — stated first, because a reviewer will check

KS-Lottery's Theorem 2 certifies that tuning the selected rows yields
**predictions that agree with the Embed-Tuning reference model** at confidence
1−α. It is a certificate of *agreement with full embedding tuning*, **not** a
certificate of translation capability.

**Our result does not contradict the theorem.** It attacks the interpretation
the paper builds on it — "fine-tuning 18 tokens' embedding of LLaMA suffices to
reach the fine-tuning translation performance … a new standard in multilingual
transfer of LLMs" — by showing the certified quantity is (a) reachable with one
row and (b) ~95% a termination degree of freedom. Any draft that blurs this is
dead on arrival.

## 4. Closest owners, honestly

| work | owns | why it does not own this |
|---|---|---|
| **KS-Lottery, NAACL 2025** | the phenomenon, the KS certification, Theorem 2, the frequency observation | the target. No termination-controlled baseline, no channel localization, no template manipulation, no single-row baseline. Code 404, prompt unpublished. |
| **The Super Weight in LLMs (2411.07191)** | "a single parameter can determine LLM behavior" | **the most dangerous neighbor.** But it is *destructive* (ablate a pretrained `mlp.down_proj` weight → catastrophe), data-free, about pretrained structure. Ours is *constructive* (tune one input-embedding row → acquire a behavior) and is aimed at deflating an adaptation claim. "One parameter can matter" is now a known genre, and that does cost us surprise. |
| **Hewitt et al. 2024** | "much of instruction following is a simple output-distribution change", explicitly including *raising EOS probability* | owns the termination mechanism in general. Our leg (2) is an application of that insight to a parameter-selection certification claim, cross-language, with the authors' own tickets — not a new mechanism. |
| **Min et al. EMNLP 2022; Kung & Peng ACL 2023 (Short)** | the genre | different phenomena. |
| **PAFT, EMNLP 2025** | fine-tuning overfits prompt wording | owns (5) as a general fact. Our (6) — that it survives a *count-matched* frequency control — is the part PAFT does not supply, and it is the part KS-Lottery's own frequency finding would otherwise explain away. |
| **LTH-in-LLM criticism** | random subnetworks can match winning tickets under structured pruning | adjacent; not about embedding-layer adaptation or certification. |

**No existing replication or critique of KS-Lottery was found.**

## 5. Strongest reviewer compression, and whether it survives

> "Base LLMs don't stop, so truncate the output — everyone knows this. One
> parameter mattering is Super Weight. Fine-tuning overfitting the prompt is
> PAFT. You stacked three known results onto one 2023 model and one paper."

**What survives.** No component predicts that the *certified* ticket — the object
the parent proves a theorem about and proposes as "a new standard" — collapses
to the newline. Super Weight is destructive and says nothing about what a
selection procedure will pick. PAFT says fine-tuning overfits wording; it does
not say a certification procedure's output is ~50% wording, still less that the
selected set is functionally interchangeable while count-matched random sets are
not (7)+(8) — that specific dissociation is ours. And leg (6) is exactly the
control that stops the parent's own frequency observation from absorbing the
result.

**What does not survive.** The termination leg alone is not novel mechanism, and
should be framed as *measurement*, not discovery. And the compression's last
clause lands: **one model, one paper.**

## 6. The honest gap

**LLaMA-1 7B is the only model.** Every number in §2 is from a 2023 base model,
because that is what the parent used and because the published token ids are only
meaningful in its 32k vocabulary. A 2026 Main reviewer will ask whether any of
this survives a modern base model, and we cannot answer.

This is the single load-bearing hole. It is also cheap to close: `Llama-3.1-8B`
is already in the local HF cache.

A second, smaller gap: the paper is currently a deflation. Main-level work of
this genre (Min et al.; *Mirage of Model Editing*, ACL 2025; *Flaw or Artifact?*,
EMNLP 2025) replaces the deflated account with something the field can use.

## 7. What would make it Main — proposed E04, bounded

1. **Modern-model replication.** Repeat the Layer-1 audit and the single-row test
   on `Llama-3.1-8B` for en→{ca, es}: base raw vs first-line spBLEU, EOS rate,
   then tune `\n` alone. Predicts: the raw/first-line gap shrinks (the model is
   better behaved) but a single structural row still captures most of whatever
   sparse tuning buys. **A null here is a real kill** and must be reported.
2. **Turn it into a standard, not a complaint.** State and demonstrate a
   **one-row + truncation baseline**: any claim of the form "tuning k parameters
   recovers full fine-tuning on a generation task" must report (a) the score
   under a locked, reference-free extraction rule, and (b) the score of tuning a
   single structural row. Show on ≥2 model families that skipping either inflates
   the apparent effect by an order of magnitude. That is the field-level
   contribution, and it is what makes the paper useful rather than merely
   corrective.

Cost: ~20 runs, well under a GPU-day, all infrastructure already written.

## 8. Verdict

> **`PASS` to Main candidate — CONDITIONAL on E04.**

Unconditional PASS is not defensible: one model family is a legitimate reject,
and I am not going to argue otherwise having already logged three preregistered
verdicts on this candidate.

Conditional on E04 §7.1 replicating and §7.2 being demonstrable, I would argue
Main. If E04 §7.1 nulls on a modern model, the correct outcome is the Findings
paper E02 already earned — which is a good paper — and L32 closes there.

**Recommended next action:** authorize E04 with the null condition in §7.1
written in before it runs.
