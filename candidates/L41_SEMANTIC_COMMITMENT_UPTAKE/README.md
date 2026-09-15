# L41 — Does Parameter Learning Respect Semantic Commitment?

**Status:** `PILOT-AUTHORIZED — E01 ONLY`  
**Date registered:** 2026-09-15  
**Origin:** WALL-BE — semantic commitment / parametric factual uptake  
**Target:** ACL / EMNLP / NAACL Main

> **This is a registered candidate, not a validated result.** Selection passed on paper; no mother phenomenon or effect size has yet been established. Only the bounded E01 is authorized.

---

## Document map

Read these in order:

1. **`PROJECT_BRIEF.md`** — full scientific background, research question, what we want to establish, competing accounts, intended Main-paper narrative, closest-work boundary, and initial experiment.
2. **`PILOT_CARD.md`** — frozen E01 protocol: semantic gate, direct-learning control, randomization, estimands, MDE, compute cap, decision table, and anti-gambling rules.
3. **`REGISTRATION.md`** — locked project identity and authorization boundary.
4. **`../../search_rounds/2026-09-15_WALL_BE_FINAL_SELECTION.md`** — Selection audit and owner/reviewer-compression analysis that justified promotion to L41.

If any later document changes the project into a generic factivity benchmark, Negation Neglect wording study, co-occurrence benchmark, or mechanism/probing project before E01, that document is out of scope.

---

# 1. Research question

> **When language is used as training data, does a language model update its persistent world beliefs according to what the sentence semantically commits to, or mainly according to propositions that are mentioned / predictively repeated?**

Short form:

> **Does parameter learning respect semantic commitment?**

The scientific object is the **language → parameter knowledge-acquisition operator**, not semantic competence at inference time.

---

# 2. Why this is a real scientific problem

Language models clearly acquire world knowledge from text, but natural language does not simply enumerate true facts.

The same proposition `p` can be:

- asserted;
- denied;
- embedded under an implicative/factive predicate;
- reported as somebody's belief;
- hypothetical, modal, conditional, fictional, or quoted.

Formal semantics and event-factuality work have long distinguished **mention** from **commitment**. Merely encountering the linguistic material for `p` does not mean the sentence presents `p` as true.

Modern pretraining creates a new regime: raw linguistic occurrences are converted directly into model parameters. We therefore need to know what implicit learning rule decides which occurrences become durable world knowledge.

The sharp possible dissociation is:

```text
online interpretation: sentence means ¬p
parameter learning:    later neutral model behaves as if p
```

L41 asks whether this dissociation occurs even when the sentence's truth commitment is determined by ordinary lexical-semantic composition that the base model demonstrably understands.

---

# 3. Modern pressure

## Negation Neglect

Mayne et al. (2026), *Negation Neglect: When models fail to learn negations in training*, show that LMs can understand false/fictional/negated qualification in context yet absorb the core claim as true during finetuning. They also find that **local negation** often largely fixes the problem.

That leaves an unresolved ambiguity:

> does local negation work because the parameter update respects semantic commitment, or because local syntax/token structure changes the gradient around the proposition?

A direct `p` vs `not p` comparison cannot distinguish these explanations because surface polarity and truth commitment reverse together.

## Belief insertion

Synthetic-document finetuning shows that document-style training can create persistent neutral-context factual behavior. This supplies the measurable outcome, not the L41 research question.

## Co-occurrence vs factual association

Zhang, Li & Wu (NeurIPS 2024), *Co-occurrence Is Not Factual Association in Language Models*, is the strongest reviewer-compression risk. It shows that shallow co-occurrence and transferable factual association can differ.

But both of its compared corpora support the **same true fact**. L41 instead holds proposition mention fixed while changing whether the whole sentence entails `p` or entails `¬p`, and measures the **sign of later neutral belief uptake**.

---

# 4. Old semantic quantity → modern identifying operation

The strongest E01 substrate is classic **two-way implicativity**.

Canonical semantic signatures:

```text
manage: + | -
fail:   - | +
```

Therefore:

```text
managed to p        =>  p
not managed to p    => ¬p
failed to p         => ¬p
not failed to p     =>  p
```

References:

- Nairn, Condoravdi & Karttunen (2006), *Computing relative polarity for textual inference*.
- Karttunen (2012), *Simple and Phrasal Implicatives*.

This gives a theory-defined checkerboard:

| condition | local negation | semantic commitment |
|---|---:|---:|
| `manage+` | no | `p` |
| `manage−` | yes | `¬p` |
| `fail+` | no | `¬p` |
| `fail−` | yes | `p` |

Thus **surface polarity and semantic commitment are no longer collinear**.

That is the identifying operation.

---

# 5. Competing accounts

## A — semantic-commitment learning

The training update preserves enough compositional semantics that persistent belief about `p` follows the sentence-level entailment.

Prediction:

```text
manage+ -> p uptake
manage- -> ¬p uptake
fail+   -> ¬p uptake
fail-   -> p uptake
```

## B — mention / co-occurrence learning

Repeated occurrence of the proposition-bearing material primarily strengthens `p`-related associations regardless of sentence commitment.

Prediction: positive/salience-like uptake across several or all cells; weak checkerboard.

## C — local surface-polarity / syntax learning

Local negative morphology suppresses uptake because of token/syntactic learning structure, without composing the implicative signature into the update.

Prediction: positive clauses look similar to one another and negative clauses look similar to one another; weak or wrong checkerboard.

A clean B or C result after verified forward understanding is a substantive scientific answer, not a failed pilot.

---

# 6. What we would like to prove — and what the project actually tests

The strongest positive statement would be:

> **Ordinary parameter learning can respect compositional semantic commitment: the same mentioned proposition produces opposite signed factual updates when sentence meaning changes whether it entails `p` or `¬p`.**

But L41 is not authorized to hunt for that result.

The real scientific target is:

> **identify whether persistent factual uptake is best explained by semantic commitment, mere mention/co-occurrence, or local polarity/syntax.**

This distinction is essential. A precommitted experiment that cleanly supports the opposite account can still justify a paper; a positive checkerboard discovered only after model/verb/LR/prompt shopping cannot.

---

# 7. Primary quantity

For a novel proposition `p`, measure neutral yes/no belief before and after training:

```text
B(p) = log P(Yes | neutral query about p)
       - log P(No | neutral query about p)
```

Define uptake:

```text
U(v,s,p) = B_after(v,s,p) - B_before(p)
```

Primary interaction:

```text
I = [mean U(manage,+) - mean U(manage,-)]
    - [mean U(fail,+) - mean U(fail,-)]
```

Semantic commitment predicts a positive checkerboard `I`, together with both predicted within-verb reversals.

The interaction is the claim. A main effect of polarity, verb, or training alone is not L41.

---

# 8. Mandatory controls

## Forward semantic-understanding gate

Before making any learning claim, the **same base model** must correctly interpret the exact four constructions in context.

Required:

- overall accuracy ≥ 90%;
- no cell < 85%;
- the mean Yes-vs-No log-odds show the expected semantic checkerboard.

Failure = instrument failure.

## Direct signed-learning gate

On separate propositions, calibrate ordinary training with direct assertion and denial:

```text
A+ : p.
A- : not p.
```

Define:

```text
D = mean(U_A+) - mean(U_A-)
```

Required before E01-B:

- `D >= 1.0` log-odds;
- proposition-paired bootstrap 95% CI excludes 0;
- no catastrophic capability collapse.

Failure = instrument failure. Do not interpret a critical implicative null.

---

# 9. E01 confirmation

Default frozen design:

- one open pretrained/base causal LM in the 4B–8B range;
- ordinary causal-LM continued training / document-style finetuning;
- 256 fresh novel proposition identities;
- 4 Latin-square assignments;
- every proposition appears once in M+/M−/F+/F− across independent resets;
- 3 independent training-order seeds per assignment;
- total 12 bounded finetuning runs;
- neutral query paraphrases may be averaged within proposition but are not independent samples.

Primary independent unit: **proposition identity**. Runs/seeds are blocks/random factors.

Planned full E01-B compute cap: **24 single-GPU RTX-PRO-6000-96GB-equivalent GPU-hours**.

See `PILOT_CARD.md` for the full frozen protocol and MDE rule.

---

# 10. Desired paper narrative

The intended story is:

1. **LMs learn facts from language, but language does not equal facts.**
2. **Recent work shows understanding and learning can dissociate.** Negation Neglect exposes the problem, but local negation leaves semantics confounded with surface locality.
3. **Classical semantics gives a decisive crossover.** Two-way implicatives make surface polarity and truth commitment disagree while proposition mention stays fixed.
4. **The resulting checkerboard identifies the factual-learning rule.**

Possible headline conclusions:

### If semantics wins

> Parameter learning can use compositional sentence meaning to decide the sign of persistent world-knowledge updates.

### If mention wins

> A model can understand that a proposition is false yet learn it as world knowledge anyway: semantic interpretation and factual knowledge acquisition are separable computations.

### If surface polarity wins

> The apparent success of local negation is better explained by local syntactic/token learning structure than by semantic factuality.

The paper should be written around this **three-way identification**, not around a desired positive effect.

---

# 11. Ownership / anti-resurrection boundary

L41 is **not**:

- K056 reopened (`does the model understand known semantic distinction X?`);
- a generic factivity/presupposition competence study;
- a MegaVeridicality-style benchmark;
- `Negation Neglect with manage/fail`;
- `Co-occurrence Is Not Factual Association with formal semantics`;
- a mitigation method;
- a probe/SAE/patching mechanism project.

The selected remainder is exactly:

> **When the same proposition is mentioned under controlled sentence forms, does ordinary LM training assign a signed factual update according to independently defined sentence-level semantic commitment?**

If this estimand disappears, L41 has drifted and should not retain its ID.

---

# 12. Authorization boundary

**Authorized now:**

- canonical `manage/fail × positive/negative` E01;
- direct assertion/denial control;
- mandatory forward semantic gate;
- token/surface balance audit;
- one frozen model/checkpoint and bounded training regime.

**Not authorized yet:**

- broad factuality/verb sweep;
- modality/conditionals/quotation/fiction;
- multilingual study;
- model zoo;
- SFT/RL comparison;
- activation probing / patching / SAE;
- gradient mechanism;
- mitigation;
- dataset/benchmark as contribution.

Read `PROJECT_BRIEF.md` for the full scientific narrative and `PILOT_CARD.md` before running anything.