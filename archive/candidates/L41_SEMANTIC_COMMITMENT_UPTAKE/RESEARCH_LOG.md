# L41 — Research Log

Scientific object: the **language → parameter knowledge-acquisition operator**.
Observable: signed change in *neutral* (context-removed) factual belief about an
embedded proposition `p`.

---

## 2026-09-17 — E01-A opened

**Decision:** execute E01-A (instrument construction) exactly as sealed in
`PILOT_CARD.md §1`. The critical `manage/fail x polarity` **post-training**
interaction is not generated and not inspected during this stage.

**Closest-work re-audit (2026-09-17).** Re-checked the four named owners plus a
fresh search. Nothing found that can write our conclusion without our experiment:

| work | what it owns | why L41's statement survives |
|---|---|---|
| Mayne et al. 2026, *Negation Neglect* (arXiv 2605.13829) | finetuning on documents that flag a claim as false still implants the claim; **local** negation (`X did not win`) is largely learned correctly | local polarity and semantic commitment are perfectly collinear in their design, so they cannot say whether local negation works *because the update respects sentence meaning*. Our `F-` cell (`did not fail to p` ⇒ `p`) is exactly the case where the two accounts split. |
| Zhang, Li & Wu 2024, *Co-occurrence Is Not Factual Association* | route/explicitness of encoding a **true** fact, and transferability of the learned association | both of their corpora support the same fact. They never reverse the sentence's truth commitment about a fixed mentioned proposition, so they cannot predict a signed reversal. |
| Zhang, Li & Wu 2024, *Conditional Language Learning with Context* | changes the training objective so context explains away corpus statistics | L41 leaves ordinary LM training untouched and asks whether native lexical semantics already supplies the selection signal. |
| Wang et al. 2025, synthetic-document finetuning | that persistent neutral-context beliefs are insertable | supplies the dependent variable, not the question. |
| Epistemic Goggles 2026 (arXiv 2607.01690) | a gradient-editing module that imposes an epistemic frame at finetuning time | a **mitigation** that presupposes the selective-learning problem; it does not test whether unedited gradients already follow lexical factuality. |
| implicative / event-factuality ancestry (Nairn-Condoravdi-Karttunen 2006; Karttunen 2012; FactBank; MegaVeridicality) | the forward truth-commitment function | treatment gold, not the outcome task. |

**Test applied:** *could the closest paper put our core conclusion in its own
abstract without running our experiment?* No. Negation Neglect's abstract can
say "local negations are learned"; it cannot say "the sign of the persistent
update tracks sentence-level semantic commitment even when it contradicts local
polarity", because it has no cell where those disagree.

**Verdict:** paper identity intact. Proceed with E01-A.

---

## A1 — Forward semantic gate (PASS)

```
Observed:   Qwen3-8B-Base, 64 development propositions, 4 neutral query
            paraphrases, 3 candidate measurement interfaces.
            Critical-cell accuracy = 1.000 under all three interfaces.
            Checkerboard present in mean Yes-vs-No log-odds, not only labels.
Diagnosis:  the base model represents the two-way implicative signature of
            `manage` / `fail` for these novel propositions, including the
            marked `did not fail to p => p` cell.
Decision:   forward semantic gate PASSES (>= 90% overall, no cell < 85%).
            Instrument failure mode "E" is ruled out.
Quantity:   unchanged.
Confound:   none identified; gate is measured on the base model in context.
Runs:       results/e01a/forward_gate.json
```

| cell | gold | mean B (ctx_fewshot) | mean B (plain_fewshot) | mean B (nofewshot) | acc |
|---|---|---:|---:|---:|---:|
| M+ `managed to p`       | p   | +4.81 | +3.82 | +2.56 | 1.00 |
| M- `did not manage to p`| ~p  | -5.68 | -5.69 | -2.66 | 1.00 |
| F+ `failed to p`        | ~p  | -5.55 | -5.62 | -2.65 | 1.00 |
| F- `did not fail to p`  | p   | +4.30 | +3.17 | +2.38 | 1.00 |
| A+ `p`                  | p   | +4.47 | +3.38 | +2.32 | 1.00 |
| A- `not p`              | ~p  | -5.65 | -5.71 | -2.65 | 1.00 |

Baseline neutral belief on unseen novel propositions (no context):

| interface | mean B | sd | frac(Yes) |
|---|---:|---:|---:|
| plain_fewshot | -0.585 | 0.39 | 0.03 |
| nofewshot     | +0.089 | 0.30 | 0.64 |

---

## A2 — AMENDMENT 1: E01 restructured as exposure-ladder -> single checkerboard -> confirmation

```
Observed:   First direct-control smoke run (16 dev2 props, 8 exposures/prop,
            lr 1e-5, 1 epoch, Qwen3-8B-Base, full FT):
              mean U(A+) = -1.184,  mean U(A-) = -1.160,  D ~ 0.02
            Both arms moved by the SAME large negative amount. There is no
            signed factual learning at all; there is only a global Yes/No
            calibration drift induced by training on declarative documents.
Diagnosis:  the risk in E01 is NOT the scientific question and NOT the model
            scale. It is the *exposure* regime. The literature that supports
            signed parametric factual uptake does so at much heavier exposure:
              - Mayne et al. 2026 (Negation Neglect): ~10k synthetic documents
                per fabricated claim, mixed with 5k pretraining + 5k
                instruction data; main model Qwen3.5-397B-A17B, cross-model
                floor Qwen3.5-35B-A3B; the local-negation condition itself
                rests on only ~2 claims.
              - Feng et al., ICML 2025 (Extractive Structures Learned in
                Pretraining Enable Generalization on Finetuned Facts): novel
                synthetic facts DO get written into 7-9B parameters
                (OLMo-7B, Qwen2-7B, Llama-3-8B, Gemma-2-9B) -- but with tens
                to hundreds of epochs over a small fact set.
              - ACL 2024 continued-pretraining knowledge work on Llama-2-7B:
                multi-epoch continued pretraining needed; absorption is not
                easy.
            So 7-9B scale is precedented for parametric factual learning;
            8 exposures per proposition is not.
Decision:   AMEND the E01 execution order (scientific design unchanged):
              A2  exposure ladder on the DIRECT p / not-p control only,
                  64-128 dev propositions, increasing exposure until
                  D >= 1.0 log-odds with a bootstrap CI excluding 0 and no
                  capability collapse;
              A3  freeze the full contract at that exposure;
              B0  ONE `manage/fail x polarity` checkerboard run on FRESH
                  proposition identities (single assignment, single seed);
              B1  only then 4 Latin-square assignments x 3 seeds.
            Rule against phenomenon gambling: B0's outcome may NOT change the
            recipe, the verbs, the query, the generator or the model. B0 may
            only decide whether the 12-run confirmation is worth its compute,
            and N may only ever increase.
Quantity:   UNCHANGED. Estimand is still
              U(v,s,p) = B_after(v,s,p) - B_before(p)
              I = [U(M,+)-U(M,-)] - [U(F,+)-U(F,-)]
            with proposition identity as the independent unit.
Confound:   the uniform negative drift shows U contains a large run-level
            offset. I is a within-run difference-of-differences so the offset
            cancels, but raw cell means must always be reported next to the
            run's own control cells, never across runs.
Affected:   all E01 runs. Supersedes PILOT_CARD.md section 7 ordering only
            (12 runs are now the *last* step, not the first).
```

**Not amended:** scientific question, `manage/fail x polarity` identification,
neutral post-training observable, proposition identity as unit, anti-gambling
rules, decision table.

### Second measurement-design change (recorded per PILOT_CARD.md section 4)

Two additions to the frozen measurement, both decided before any critical
post-training result exists:

1. **Document-surprisal audit.** A pure mention/co-occurrence learner still
   moves further on higher-surprisal documents. If the treatment material has a
   verb x polarity interaction in base-model NLL, that alone could manufacture a
   nonzero `I` with the same sign as the semantic prediction (`did not fail to p`
   is the rarest string of the four). We therefore measure and report base-model
   NLL of every arm's sentence and document, and report `I` alongside it.
2. **Mention-spillover control query.** For every proposition we also query a
   *near-miss* proposition (same agent, same verb, same object class, different
   object number) that never appears in any training document. Under
   H_mention, entity/event familiarity should raise Yes-tendency for the
   near-miss too; under H_sem it should not move. Secondary measure, never
   primary.

---

## A2.1 — Direct-control exposure ladder, v1 (no generic anchor)

Setup: Qwen3-8B-Base full FT, 64 dev2 propositions (32 `A+ : p`, 32 `A- : not p`),
12 distinct micro-document shells per proposition, constant LR after 3% warmup,
bs=64, FSDP2 over 2 GPUs, belief scored at 7 epoch checkpoints inside one run.
No generic data mixed in. No untrained-holdout propositions in this version
(the `spill` column, a never-trained near-miss proposition of a *trained* agent,
is the only drift proxy available for v1).

**lr = 2e-5**

| exposures | U(A+) | U(A-) | spill | D = U+ − U− | 95% CI | p | generic NLL |
|---:|---:|---:|---:|---:|---|---:|---:|
| 12 | −0.334 | −0.305 | −0.262 | −0.029 | [−0.18, +0.12] | .709 | 2.331 |
| 24 | −0.379 | −0.471 | −0.254 | +0.092 | [−0.16, +0.34] | .462 | 2.642 |
| 48 | −1.027 | −1.107 | −0.988 | +0.080 | [−0.33, +0.48] | .697 | 2.838 |
| 96 | −0.361 | −0.654 | −0.262 | +0.293 | [−0.21, +0.78] | .247 | 2.997 |
| 192 | +0.486 | +0.006 | +0.355 | +0.480 | [−0.35, +1.26] | .248 | 3.331 |
| 288 | +1.734 | +0.961 | +1.227 | +0.773 | [−0.12, +1.67] | .095 | 3.214 |
| 384 | +2.123 | +0.877 | +1.363 | **+1.246** | [+0.03, +2.44] | .044 | 3.398 |

**lr = 5e-5** — D never separates from 0 at any exposure (max |D| = 0.14) while
generic NLL reaches 4.75–5.11. Discarded as a training regime.

```
Observed:   (a) At lr 2e-5, D rises monotonically with exposure and reaches
                +1.25 log-odds at 384 exposures/proposition. Signed factual
                uptake exists in this substrate and is exposure-limited, exactly
                as the 7-9B factual-learning literature implies.
            (b) At 384 exposures the spill probe (never-trained near-miss
                proposition) has moved +1.363. Subtracting it gives
                corrected U(A+) = +0.76 and U(A-) = -0.49: the right signs.
            (c) Generic NLL degrades 2.172 -> 3.398 at lr 2e-5 and to ~5 at
                lr 5e-5. This FAILS the capability-collapse sanity gate.
            (d) lr 5e-5 destroys the model and destroys the signal together.
Diagnosis:  the tiny 768-document corpus with no anchor is being memorised
            (train loss 1.03 -> 0.17) and the model is drifting into a global
            "Yes" bias. The signed component is real but rides on a large
            nuisance drift, and the model is being damaged on the way.
Decision:   lr 5e-5 is OUT. Keep lr 2e-5. Add the generic-data mix that
            PILOT_CARD.md section 1 already permits (Negation Neglect likewise
            mixes 5k pretraining + 5k instruction documents with its synthetic
            corpus), and add never-trained HOLDOUT propositions so that common
            drift is measured directly instead of proxied.
            Ladder v2: lr 2e-5, generic_ratio in {1.0, 3.0} pile-10k chunks per
            micro-document, 32 untrained holdout propositions, exposures to 768.
Quantity:   UNCHANGED.
Confound:   the common Yes-drift is the main nuisance. D is a difference of two
            arms measured in the same run, so any additive common drift cancels
            from D; the holdout column exists to show that the *individual* arm
            signs are real and not an artefact of that drift.
Affected:   results/e01a/ladder/{lr2e-5,lr5e-5}.json  (v1, superseded for
            recipe selection; retained as the lr-selection evidence)
```

**Critical checkerboard status: still sealed.** No `manage/fail` post-training
quantity has been generated or inspected.

---

## A2.2 — Generator defect found and fixed (before any freeze)

```
Observed:   agent names were NOT disjoint across proposition pools:
              dev n dev2 = 1, dev n crit = 1, dev2 n crit = 3, crit n pilot = 1.
Diagnosis:  generate() drew 4000 candidate names from a per-pool RNG and then
            sliced that pool-specific list by pool index. Different RNG streams
            produce different name lists, so index slicing did not guarantee
            disjointness.
            Severity: `crit` and `pilot` propositions appear in the SAME E01-B
            run (the within-run direct control). A shared agent would put an
            implicative sentence and a direct assertion about the same entity
            into one training corpus -- a genuine interference confound.
Decision:   draw names once from a single fixed stream (NAME_SEED = 410000) and
            partition that one list by pool index, with an assertion that the
            pool cannot be exhausted. Verified: all six pairwise overlaps = 0.
Quantity:   UNCHANGED.
Confound:   removed.
Affected:   all proposition identities change. Ladder v1 (results/e01a/ladder/)
            was produced under the old draw; it is retained only as the
            learning-rate selection evidence, which is a hyper-parameter choice
            and does not depend on which random propositions were drawn.
            The forward semantic gate must be RE-RUN on the new `dev` draw
            before the contract is frozen.
```

## A2.3 — Training-recipe engineering notes (scientifically neutral)

| problem | fix | why it cannot change the estimand |
|---|---|---|
| single-GPU full FT of 8B with AdamW needs ~128 GB | FSDP2 `fully_shard`, fp32 master weights, bf16 compute, 4 GPUs | numerically the same update |
| OOM at global batch 128 | gradient checkpointing | recompute only |
| gradient accumulation cost 4x parameter all-gathers per step (~15 s/step) | 4 GPUs with accum = 1 (~3.8 s/step) | identical global batch |
| documents are ~35 tokens, generic chunks 96 | padding masked out of the loss | no loss contribution |
| shell / document-id had to be identical across arms | document ids derived from `sha1(pid|k)` instead of Python's per-process randomised `hash()` | makes arms byte-matched outside the critical clause |

**Within-run direct control (frozen design decision).** Every E01-B critical run
also carries 64 direct-control propositions (32 `A+`, 32 `A-`) from the disjoint
`pilot` pool, identical in all four Latin-square assignments. This gives `D`
under exactly the same drift, optimiser state and exposure as the critical
cells, so `F_sem = I / (2D)` is normalised against a matched control rather than
against a separate run. Being identical across all four critical cells, the
control block cannot generate the verb x polarity interaction.

**E01-B manifest built** (`frozen/assign/manifest.json`): 256 fresh `crit`
identities x 4 Latin-square assignments; verified that every identity appears
exactly once in each of M+, M-, F+, F- across L0..L3. Not executed.

---

## A2.4 — Generic anchor was itself being memorised (fixed)

```
Observed:   first ladder-v2 attempt with generic_ratio 1.0 gave wikitext NLL
            3.306 at only 96 exposures/prop -- WORSE than the unanchored v1 run
            at the same exposure (2.997). Train loss 0.216 at that point, far
            below what a genuine 50/50 synthetic/generic batch could produce.
Diagnosis:  the anchor was drawn ONCE (768 pile chunks) and then replayed every
            epoch. Over 96 epochs the model memorised the anchor alongside the
            facts, so it added memorisation pressure and twice the optimizer
            steps while providing no distributional anchoring at all.
Decision:   the synthetic micro-documents repeat every epoch -- that repetition
            IS the exposure knob being laddered -- but the generic anchor is now
            a FRESH, non-repeating slice of pile-10k each epoch (139,910 chunks
            available; 73,728 consumed at ratio 1.0 x 96 epochs).
            Also added a SECOND capability probe: 96 held-out pile chunks that
            never enter the mix. Rationale: measuring capability only on
            wikitext while anchoring on pile confounds "damage" with "domain
            shift toward the anchor". Base values: wikitext 2.172, pile 2.754.
Quantity:   UNCHANGED. The anchor is identical across all arms and cannot
            produce a verb x polarity interaction.
Confound:   removed a confound (anchor memorisation) and removed a measurement
            confound in the capability gate.
Affected:   all ladder-v2 runs; v2 restarted from scratch.
```

**Critical checkerboard status: still sealed.**

---

## A2.5 — Compute-budget check for E01-B (flagged before freezing)

Measured throughput: 3.9 s/optimizer step at global batch 128, FSDP2 over 4
RTX-PRO-6000-96GB. The runs are **communication-bound, not compute-bound**
(~16k tokens/step in 3.9 s is far below these cards' compute).

E01-B is 320 trained propositions per run (256 critical + 64 within-run direct
control) versus 64 in the ladder, so steps per epoch scale 5x at fixed batch:

```
steps/run = n_props * exposures * (1 + generic_ratio) / bs
          = 320 * E * 2 / 128
```

| exposures E frozen at | steps/run | wall/run | 12 runs (wall) | 12 runs (GPU-h) |
|---:|---:|---:|---:|---:|
| 192 |  960 | ~1.0 h | ~12 h |  ~50 |
| 384 | 1920 | ~2.1 h | ~25 h | ~100 |
| 768 | 3840 | ~4.2 h | ~50 h | ~200 |

PILOT_CARD.md section 13 sets a planning cap of **24 single-GPU-hours** for the
full E01-B. Even the cheapest row is over it. The cap is described there as a
workload guardrail rather than a scientific estimate, but the gap is large
enough that it must be resolved deliberately, not silently.

```
Decision:   before freezing, run the final direct-control gate at the ACTUAL
            E01-B scale (320 trained propositions), not at the 64-proposition
            ladder scale. Two reasons:
              1. scientific -- the recipe must be certified at the scale it will
                 be used; per-proposition exposure is preserved but steps per
                 epoch, corpus diversity per epoch and the memorisation pressure
                 on the shells are all different at 320 props;
              2. operational -- it measures the true per-run cost so the 12-run
                 budget is a measurement rather than an extrapolation.
            Efficiency levers that do NOT change the optimiser trajectory are
            allowed (fewer ranks per run with more runs in parallel, bf16
            gradient reduction, length-bucketed batches). Levers that DO change
            it (batch size, LR, generic ratio, exposure) are frozen once the
            gate passes and may not be retuned for cost.
Quantity:   UNCHANGED.
```

---

## A3.1 — Surface / tokenization audit (PILOT_CARD.md section 4), 256 `crit` propositions

Qwen3-8B-Base tokenizer, 12 micro-document shells per proposition.

| cell | sentence tokens | document tokens | complement tokens | example |
|---|---:|---:|---:|---|
| M+ | 10.78 | 29.52 | 5.25 | `Rolis managed to open Archive 78.` |
| M- | 12.78 | 31.52 | 5.25 | `Rolis did not manage to open Archive 78.` |
| F+ | 10.78 | 29.52 | 5.25 | `Rolis failed to open Archive 78.` |
| F- | 12.78 | 31.52 | 5.25 | `Rolis did not fail to open Archive 78.` |
| A+ |  8.78 | 27.52 | 5.25 | `Rolis opened Archive 78.` |
| A- | 10.78 | 29.52 | 5.25 | `Rolis did not open Archive 78.` |

- **verb x polarity interaction in token count: exactly 0.00** (sentence and document).
- polarity main effect: -2.00 tokens; `manage` and `fail` tokenize to identical
  length, so the main effect is pure negation and is cancelled by `I`.
- the proposition-bearing complement is byte-identical in all four critical cells;
- document shells and document ids are identical across all arms;
- exposure count, shell frequency and loss-bearing token count differ across
  arms only by the 2-token negation, with no verb x polarity structure.

Still outstanding before freeze: the **surprisal** half of this audit (base-model
NLL per arm), which needs a GPU and runs after the ladder.
