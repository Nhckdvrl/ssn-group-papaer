# L36 E00 — Instrument / Model-Provenance Audit

**Date:** 2026-09-14  
**Status:** **MANDATORY PRE-E01 GATE — NO E01 RUN UNTIL PASS**  
**Purpose:** prevent a false modern-regime result caused by evaluation-set exposure, unmatched decoding semantics, or an unidentified null.

## 1. Why E00 is now mandatory

L36 remains the preferred next bounded candidate because its first scientific gate can be stated on externally defined quantities:

- intrinsic uncertainty is fixed from independently authored human references;
- beam width is the treatment;
- translation quality is the outcome;
- a classic encoder–decoder can serve as a positive-control regime.

However, the originally suggested modern checkpoint, `Unbabel/TowerInstruct-7B-v0.2`, is **not eligible** for the decisive WMT19 experiment. TowerBlocks-v0.2 publicly lists **WMT14 through WMT21** among its general-translation training sources. Therefore WMT19 evaluation material is within the model's known supervised-data lineage. A stable large-beam curve on the WMT19 substrate could then reflect direct task/test exposure rather than a changed LLM distributional regime.

This is exactly the kind of construct contamination L36 must rule out before compute.

A second correction concerns the TACL-2025 mother evidence. The public LLM4MT repository currently advertises released `de2en-10k` and `zh2en-10k` checkpoints, whereas the strongest paper curves use larger SFT conditions as well. The public code is useful for auditing HuggingFace generation semantics, but E01 must not claim an exact checkpoint reproduction unless the exact checkpoint used for the beam-width result is actually obtainable.

## 2. Frozen scientific object

The E01 law-break question remains:

> Holding human-defined intrinsic translation ambiguity fixed, does a modern decoder-only translation-capable LM still exhibit the classic uncertainty-conditioned deterioration as beam width grows?

E00 is not allowed to change this into:

- a TowerInstruct paper;
- a decoding-configuration paper;
- a benchmark-contamination paper;
- a generic `LLMs translate better` comparison.

## 3. Exact uncertainty substrate

The decisive substrate must reuse the ACL-2022 quantity as faithfully as possible:

- WMT19 English→German source items;
- independently authored human references used by Stahlberg, Kulikov & Kumar (2022), including the additional human reference lineage from Freitag et al. (2020);
- sentence-level intrinsic uncertainty computed **before any model generation**, using the published normalized pairwise-reference disagreement definition.

No token entropy, model entropy, LLM judge disagreement, or new ambiguity proxy may replace the human-reference quantity in E01.

## 4. Classic positive-control model

Use an open classic encoder–decoder on the same EN→DE substrate, with exact revision frozen before generation. `facebook/wmt19-en-de` is a suitable first candidate because it is a public WMT19 encoder–decoder submission and exposes explicit beam / length settings.

The classic model is an **instrument positive control**, not a competitor in a leaderboard.

Before interpreting a modern `no curse` result, the frozen pipeline must recover a material adverse large-beam pattern in the classic regime, especially in the high-intrinsic-uncertainty stratum. If it cannot, the instrument has failed and L36 stops; do not interpret a modern flat curve.

## 5. Modern-model eligibility gate

A modern EN→DE checkpoint may enter confirmatory E01 only if all of the following are satisfied **before looking at its beam-width outcome on WMT19**:

1. **Direction:** it can perform English→German generation without an ad-hoc task-specific finetune created for this project.
2. **Public frozen checkpoint:** exact revision / weights / prompt contract are available.
3. **Known-supervision audit:** no known supervised / instruction-tuning source directly includes WMT19 test/evaluation material. Any model whose documented training data explicitly includes WMT14–WMT21 evaluation sets is ineligible.
4. **No outcome-driven model choice:** candidate model(s) and eligibility evidence are frozen before the WMT19 beam sweep. Do not try several models and keep the one that gives the desired reversal.
5. **Translation competence:** independent published evidence or a predeclared no-claim competence check must show the model is a functioning EN→DE translator. The competence gate cannot depend on the eventual beam-width sign.
6. **Residual pretraining-contamination limitation:** if web-pretraining exclusion of WMT19 cannot be proven, state that limitation explicitly. Unknown web exposure is not equivalent to known direct supervised inclusion, but it must not be described as contamination-free.

### Immediate ruling

`Unbabel/TowerInstruct-7B-v0.2`: **INELIGIBLE for decisive WMT19 E01** due to known WMT14–WMT21 general-translation training lineage.

If no modern model passes the eligibility gate with defensible translation competence, set L36 to **HOLD / MODEL-PROVENANCE BLOCKER**. Do not relax the gate to obtain a runnable experiment.

## 6. Decoding-semantics audit

Before quality analysis, freeze for every model:

- beam widths (target set: `1, 4, 8, 16, 32`);
- deterministic decoding, no sampling in the primary path;
- EOS and PAD handling;
- maximum generated-token budget;
- length penalty / score normalization;
- early-stopping semantics;
- prompt and output extraction;
- whether beam hypotheses are selected by the model's native generation score or by an explicitly defined rescoring rule.

Do **not** compare an encoder–decoder's raw cumulative score with a decoder-only model's HuggingFace normalized score and call the difference a model-regime effect.

The public LLM4MT implementation is useful here because it exposes standard HuggingFace `GenerationConfig` beam decoding; it is a semantics reference, not necessarily the decisive modern checkpoint.

## 7. The null must be identified, not merely nonsignificant

A central L34 lesson is that a pretty interaction or a failed significance test is not an identified scientific result.

Therefore E01 must predeclare a **material-effect / equivalence criterion** for the modern high-uncertainty beam curve.

A valid law-break gate must establish both:

1. **positive control:** classic high-uncertainty items show a material deterioration as beam grows under the frozen pipeline;
2. **modern attenuation:** the corresponding modern deterioration is demonstrably much smaller, under a predeclared equivalence / relative-attenuation margin — not merely `p > .05`.

The exact margin will be frozen only after a no-claim resolution audit on the classic positive control and before looking at the modern WMT19 outcome.

No post-hoc threshold may be chosen from the modern curve.

## 8. Candidate confirmatory quantity

Let `Q_m(b, U)` be translation quality for model regime `m`, beam width `b`, and a predeclared uncertainty stratum `U`.

One interpretable family of quantities is:

```text
D_m(U) = Q_m(large_beam, U) - Q_m(reference_beam, U)
CURSE_m = D_m(high_U) - D_m(low_U)
REGIME_BREAK = CURSE_modern - CURSE_classic
```

The final exact metric / beam contrast / uncertainty stratification must be frozen in the E01 preregistration. E00 only requires that the modern law break be judged against a reproduced classic positive control and a material attenuation criterion.

## 9. E00 pass / fail

### PASS → write E01 preregistration

Pass only when:

- the WMT19 human-uncertainty data and calculation are frozen;
- the classic EN→DE positive-control checkpoint is frozen;
- one modern EN→DE checkpoint passes the provenance + competence gate;
- decoding semantics are explicitly matched/audited;
- a classic-effect resolution estimate supports a predeclared modern attenuation/equivalence margin.

### FAIL / HOLD

- no eligible modern checkpoint with adequate EN→DE competence → **HOLD / MODEL-PROVENANCE**;
- classic positive control does not reproduce a material uncertainty-conditioned curse → **KILL / INSTRUMENT FAILURE**;
- exact old uncertainty substrate cannot be reconstructed → **HOLD / SAME-QUANTITY FAILURE**;
- only a change in scoring/stopping convention explains the published modern reversal → **KILL MAIN ROUTE**.

No GPU mechanism experiment is authorized by E00.

## 10. Why L36 is currently preferred over the other live candidates

L36's first gate does not require a learned latent direction, a state transplant whose semantic identity must be assumed, a synthetic training curriculum, or a small second-order training difference. If E00 passes, E01 can make a direct go/no-go statement about an old published law on externally defined inputs.

This is why L36 is the preferred next candidate **only after E00 passes**.