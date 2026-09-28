# L32 E02 — Preregistration

**Written 2026-09-13, BEFORE any E02 run.** Nothing below may be changed once a
layer has been executed. Deviations, if forced, get their own dated section at
the bottom rather than an edit.

Authorization: user, 2026-09-13, superseding `CLAIM_NOVELTY_DELTA.md` §9. The
earlier `TICKET_SELECTION_PROBE.md` is **exploratory** and is not evidence for
anything here; E02 re-runs its question under a design that can carry it.

---

## 0. Claim identity (mutated from E01, deliberately)

E01 answered *where the 18 embeddings act* — entirely in the instruction, not at
all in the source. The paper question now is the one that evidence exposed:

> **Are multilingual winning tickets properties of a language, or properties of
> the interface used to ask the model to translate?**

Not generic prompt sensitivity. The object is specific: a published,
parameter-level, *certified* multilingual lottery-ticket interpretation.

## 1. What the parent already publishes, and why it sets up this question

KS-Lottery Appendix Table 11 lists the certified ticket for six pairs. Parsed
from the paper:

| pair | ticket size |
|---|---|
| en→ca | 18 | en→es | 18 | en→ro | 15 | en→da | 12 | en→de | 15 | en→pt | 17 |

- The intersection of **all six** is 10 rows: `13(\n) 278(the) 297(in) 304(to)
  310(of) 322(and) 29871(▁) 29889(.) 29892(,) 29896(1)`.
- Pairwise Jaccard runs 0.57–0.88 (ca–de = 0.65, de–pt = 0.88).
- **No ticket contains a single target-language-specific token.** Every member of
  every ticket is an English function word, a digit, or punctuation.

The parent reads this overlap as "winning tickets share some common pattern"
across languages. Every one of those languages was trained under the same
English prompt, so language-commonality and interface-commonality are perfectly
confounded in that table. E02 breaks the confound.

## 2. Three layers, sequential gates. A layer that fails stops E02.

---

### Layer 1 — Cross-language evaluation audit

**Question.** Is the termination confound en→ca-specific, or does the sparse
tuning gain evaporate under content-only evaluation in other pairs too?

**Languages.** en→{ca, es, ro}. Chosen because the parent publishes their
tickets (Table 11) and reports large gains for them. Using the **published**
tickets, not ours, so "you did not reproduce their selection" cannot apply.

**Training.** Partial Tuning of exactly the published rows (ca 18 / es 18 /
ro 15), everything else frozen. Parent's LR 1e-2, 5 epochs, 10k OPUS-100 pairs
under the E01 filter. **2 seeds per language.**

**Evaluation.** Flores-101 devtest, 1012 sentences, greedy, max 256 new tokens.
Arms BASE and ALL.

**The three extraction rules are locked here, before any number is seen.** All
three are deterministic and never look at the reference:

| id | rule |
|---|---|
| **R1 `raw`** | the whole continuation up to EOS. Parent-compatible. |
| **R2 `firstline`** | the first non-empty line. |
| **R3 `prompt_restart`** | everything up to the first line matching `^\s*[A-Za-z][A-Za-z ]{0,20}:\s` — i.e. cut only where the model starts a new prompt field. Permits multi-line output; removes only template re-runs. |

R2 is the pre-declared **primary content rule**, R1 the parent-comparable one,
R3 the robustness rule. **All three are reported for every arm, always.**
Choosing among them after the fact would be exactly the cherry-picked extraction
rule a reviewer should object to.

**Metrics.** spBLEU (`sacrebleu`, `tokenize="flores101"`) and **chrF2**, both
reported always. Also per arm: EOS-emission rate, mean chars, hypothesis/source
and hypothesis/reference length ratios.

*Recorded decision, made before running:* COMET was intended as a third metric
and is **dropped** — `unbabel-comet` installs but needs `pytorch_lightning`,
absent from the shared environment, and adding it risks the shared torch build.
chrF2 carries the metric-robustness role. This is logged here so it is not read
later as a post-hoc metric choice.

**Primary quantity.** For metric `M` and rule `R`:

`Δ_R = M(ALL, R) − M(BASE, R)`, and `collapse = 1 − Δ_R2 / Δ_R1`.

**Pre-declared gate.**

- **PASS →** proceed to Layer 2 if `collapse ≥ 0.8` under spBLEU in **≥2 of 3**
  languages, with chrF2 agreeing in direction.
- **FAIL →** stop E02, write the Findings paper. In particular, if the collapse
  appears only for ca, the result is en→ca-specific and does not generalize.

---

### Layer 2 — Preregistered ticket-selection factorial, with a frequency control

Runs **only** if Layer 1 passes.

**Design.** 3 languages × 3 **semantically equivalent, lexically distinct**
prompts × 2 seeds = 18 selection runs. Prompts are written before Layer 2 runs
and are fixed. Each run: full embedding tuning at the parent's 2e-5 / 3 epochs,
then the per-row statistic.

**Reported quantities — top-k overlap is NOT the primary one.**

1. **Seed ceiling.** Same language, prompt and data, different seed. Every other
   number is reported as a fraction of this. (E01's probe had no ceiling; that
   is why it was uninterpretable.)
2. **Whole-vocabulary rank correlation** between conditions, not just the head.
3. **Top-k overlap** at k = 12, 15, 18 (the parent's own ticket sizes), k = 100.
4. **Effect sizes**: prompt-within-language vs language-within-prompt.
5. **Frequency control — the load-bearing one.** Regress ticket rank on
   `is_in_prompt_template` while controlling total training-token count (and
   log count). KS-Lottery already reports that winning tickets are
   high-frequency tokens and that Frequency Tuning nearly matches Embed Tuning,
   so *"the prompt's tokens are the frequent tokens"* is the null. The claim
   needs `is_in_template` to predict ticket rank **after** frequency is
   partialled out.

**Pre-declared gate.**

- **PASS →** Layer 3 if prompt-within-language effect is at least comparable to
  language-within-prompt, both clearly below the seed ceiling, **and**
  `is_in_template` survives the frequency control.
- **FAIL →** stop. If the template effect is fully explained by token frequency,
  this is a rediscovery of the parent's own frequency observation → Findings.

---

### Layer 3 — Functional cross-template transfer

Runs **only** if Layer 2 passes. This is the layer that decides Main.

Set-membership is not function. Fix language and training data; derive ticket
`T_A` under prompt A and `T_B` under prompt B. Partial-Tune each. Then evaluate
each under **both** prompts:

| | eval under A | eval under B |
|---|---|---|
| ticket `T_A` | matched | **crossed** |
| ticket `T_B` | **crossed** | matched |

**Pre-declared prediction.** If the ticket is a *language/translation capability*
locus, a semantically equivalent rewording should leave substantial functional
transfer: `T_A` under B should be close to `T_B` under B. If it is an *interface*
ticket, `T_A` under B loses clearly to `T_B` under B.

**Primary quantity.** Transfer ratio `Δ(T_A, B) / Δ(T_B, B)`, under R2 and R1,
both reported, with seeds.

---

## 3. Verdict table, fixed now

| E02 outcome | verdict |
|---|---|
| termination collapse only for en→ca | **Findings** |
| collapse in ≥2 languages, but tickets stable across templates | **Findings / HOLD** — evaluation-audit paper, scope still narrow |
| tickets move with template but fully explained by token frequency | **Findings** — generic frequency/prompt effect |
| ticket identity moves with template beyond seed noise and survives the frequency control, **but** functional transfer stays good | **HOLD** — the locus may be redundant |
| multilingual collapse + instruction-only causal use + selection tracking template not language + cross-template functional transfer clearly fails | **Main candidate** |

## 4. Explicitly NOT authorized in E02

- The gradient-coherence mechanism ("instruction tokens recur in an identical
  task role, so their per-example gradients agree, while equally frequent source
  tokens appear in varying contexts and partially cancel"). It is the natural
  explanation of E01's `frequency(source) > frequency(instruction)` with
  `causal utility(source) = 0`, and it is **C2**. Designing the mechanism test
  before the phenomenon is established would be betting on a story.
- Model-zoo expansion, 101-language sweeps, a new PEFT method, a new selection
  algorithm.

## 5. Correction to the record

`CLAIM_NOVELTY_DELTA.md` §4 lists Kung & Peng 2023 among Main-venue precedents.
It is **ACL 2023 Short**, not a Main long paper. The venue-precedent argument
rests instead on Min et al. EMNLP 2022 Main, Yin et al. ACL 2023 Long, *The
Mirage of Model Editing* (ACL 2025 Main), *Flaw or Artifact?* (EMNLP 2025 Main)
and Peters & Martins (ACL 2025 Main) — the last three establishing that an
evaluation-artifact finding reaches Main when it overturns a **field-level**
conclusion rather than one setting.
