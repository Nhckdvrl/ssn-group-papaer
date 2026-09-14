# Style-anchor search: The Imperfective Paradox × The Flexibility Trap

**Date:** 2026-09-14  
**Target:** ACL / EMNLP / NAACL Main  
**Status:** search-only. No L number. No pilot authorization.

## 0. Why this round exists

The user's strongest taste anchors are:

1. **The Imperfective Paradox in Large Language Models** — especially preferred: tiny team, modest experimental footprint, classic semantic object, very clean inferential consequence, broad conclusion.
2. **The Flexibility Trap: Rethinking the Value of Arbitrary Order in Diffusion Language Models** — a widely advertised architectural advantage becomes a liability exactly at the consequential quantity.

This round does **not** search for topical successors to either paper. It extracts their research taste, then changes scientific object.

---

## 1. What is actually attractive about the Imperfective paper

The core move is not `aspect + LLM`.

Bolei Ma had already studied **lexical aspect recognition** in a small 2024 paper (`Evaluating Lexical Aspect with Large Language Models`). The ACL 2026 Best Paper asks a stronger question on the same scientific object:

> **Recognizing a semantic property is not the same as using it to license the right inference.**

The classic consequence is minimal and unavoidable:

- activity: `was running` supports realization of `ran`;
- accomplishment: `was building a house` does **not** entail `built a house`.

The paper therefore moves from **property recognition → consequence-sensitive reasoning**. Its experiments are deliberately small (roughly hundreds of controlled items, several models, no new training system), but the conclusion bears on a broad belief: fluent/predictive competence does not imply compositionally faithful event-semantic reasoning.

### Correction to our previous doctrine

We had over-tightened the rule:

> a classic linguistic problem is only worthwhile if a 2026 foundation model supplies a genuinely new causal identifying operation.

That is **too strict**. The Imperfective Best Paper is direct counterevidence. A classic theory + modern LLM can be Main/Best-level when:

1. the scientific object is intrinsically sharp;
2. there is a simple theoretical consequence that prior NLP competence tests did not identify;
3. the study tests whether the model **uses** the distinction in inference, not merely whether it can classify/name it;
4. the result revises a broad belief about model understanding;
5. the experiment does not need a giant dataset or a clever new method.

The right anti-replication question is therefore not “does LLM provide a new operation?” but:

> **What scientific inference was never actually identified by the previous competence test?**

---

## 2. What is actually attractive about Flexibility Trap

The core move is not `diffusion LM + decoding`.

The community-level claim is that arbitrary-order generation gives diffusion LMs **more useful freedom** than fixed left-to-right generation. The paper asks what that freedom does at the consequential object — exploration around high-uncertainty reasoning forks — and finds that the advertised freedom can let the model bypass exactly those forks, collapsing useful solution diversity.

Taste move:

> **advertised advantage → measure its downstream consequence → discover that the advantage can reverse sign at the scientifically relevant quantity.**

This is distinct from ordinary “method X sometimes hurts metric Y.” The target is a load-bearing belief about why the architecture should be better.

---

# 3. Search result: strongest new pressure

## P-A — Sequence of Tense: does `past` still mean `before` under embedding?

**Status:** **STRONG PRESSURE — exact LLM owner not found — no L number yet**

### Classic scientific object

English past-under-past sentences such as:

> `John said that Mary was sick.`

have a classic **Sequence-of-Tense (SOT)** ambiguity. Mary’s sickness may precede John’s saying, but crucially it may also be **simultaneous** with John’s saying — corresponding approximately to John saying “Mary is sick.” Thus the embedded past morpheme does not force semantic anteriority.

This is a mature formal-semantic problem going back decades (Abusch, Ogihara, Sharvit, etc.), with structural vs implicature/semantic accounts and well-known cross-linguistic variation. It is still theoretically active: Sharvit’s 2020 reference chapter contrasts major analyses; Mucha, Renans & Romoli (2023) connect SOT to cessation implicatures; Alxatib & Caplan (2026) explicitly pose the acquisition problem for embedded tense.

### Why it fits the preferred paper style

The question is understandable without a benchmark name:

> **When an LLM sees two past-tense verbs, does it mechanically place the embedded event earlier, or does it know that embedded past can inherit the attitude time?**

This is extremely close in *inferential shape* to Imperfective without being its topical neighbor:

- Imperfective: `was building` **does not imply** `built`.
- SOT: embedded `was sick` **does not imply** `sick before the saying`.

In both cases, surface morphology tempts a simple inference that compositional semantics blocks.

### Existing NLP/LLM neighborhood

Current LLM temporal work is dominated by:

- event-order benchmarks (`before/after`, Allen relations);
- consistency of temporal ordering;
- probing/localizing tense features (e.g. TenseLoC 2025).

Exact searches for `sequence of tense`, `past-under-past`, `double access`, `embedded tense` + LLM/GPT did **not** reveal a direct LLM study of SOT interpretation.

This matters: “the model encodes tense” or “the model can order events” does not answer whether a morphologically past embedded clause may be interpreted **simultaneously** with the matrix attitude.

### Clean observable

Do **not** build a giant temporal benchmark.

Use controlled scenario compatibility / entailment:

- matrix report event has an explicit time;
- embedded stative predicate is past-under-past;
- matched scenarios force either simultaneous or backward-shifted interpretation;
- compare to unembedded past controls where anteriority really is required / strongly constrained;
- optionally include present-under-past double-access as a second signature if it strengthens the same scientific object rather than padding.

The key quantity is **semantic temporal relation licensed by the embedded tense**, not generic temporal QA accuracy.

### Best-case headlines

If models collapse to surface past:

> **Past Is Not Before: Language Models Fail to Shift Temporal Perspective in Reported Speech.**

or

> **LLMs encode tense morphology but not Sequence of Tense: embedded past is systematically mistaken for anteriority.**

If modern LLMs succeed:

> **Large language models recover relative temporal interpretation despite misleading surface tense morphology.**

Both directions answer the pressure. No phenomenon gambling is required.

### Current blocker

Before promotion, still need a final owner review around:

- computational semantics / NLI datasets that may already contain SOT;
- psycholinguistic LM work on past-under-past not indexed with `sequence of tense`;
- whether the simultaneous reading can be made gold-clean without turning the experiment into ambiguous human-judgment annotation.

The strongest design likely tests **licensed compatibility** rather than treating an ambiguous sentence as having one forced label.

---

# 4. Strong but currently weaker pressure

## P-B — Before/After Veridicality: temporal order ≠ event occurrence

**Status:** **STRONG TASTE MATCH, BUT OWNERSHIP/COMPRESSION RISK**

Classic asymmetry:

- `A after B` entails that B occurred.
- `A before B` need not entail that B occurred.

Canonical examples are strikingly simple:

> Police defused the bomb **before** it exploded.  
> The bomb did not explode.

The surface temporal connective mentions an event while the sentence can imply that the event **never happened**.

### Why it looked excellent

Modern LLM temporal reasoning work heavily measures **ordering**. A model could therefore appear temporally competent while systematically hallucinating the existence of events in non-veridical `before` clauses.

Potential headline:

> **LLMs can order events in time without knowing whether those events happened.**

This has the same clean `recognition/ordering ≠ consequence` move as Imperfective.

### Why it was downgraded

The parent is not scientifically empty. Classical NLP **event factuality** work already explicitly treats temporal clauses — especially `before` — as factuality markers. A Factuality Profiler notes that `before`-clause events are not always facts, and modern event-factuality prediction is an established NLP object. ACL 2026 even has a position paper arguing that current LLM EFP work over-focuses on classification accuracy.

So although no exact modern LLM paper on the **before/after veridicality asymmetry** surfaced, a reviewer can compress the project to:

> “a controlled slice of event factuality prediction.”

Keep as pressure, not candidate, until we can show a scientific conclusion stronger than another EFP phenomenon test.

---

# 5. Interesting but adjacent-owner pressure

## P-C — Intensional transitive verbs: mention ≠ existential commitment

**Status:** **WATCH — direct exact owner not found, adjacent ownership substantial**

Classic contrast:

- `Maya found a unicorn` commits the speaker to a unicorn existing.
- `Maya looked for / sought / wanted a unicorn` can be true even if no unicorn exists.

The theoretical object is old and deep: intensional transitive verbs suspend ordinary existential commitment and also support non-specific readings / opacity.

Question:

> **Can an LLM distinguish talking about an object from committing to that object’s existence?**

This is aesthetically excellent and cheap to test.

However, the neighborhood is no longer empty:

- TACL 2023 **Transparency Helps Reveal When Language Models Learn Meaning** directly studies **referential opacity** with propositional-attitude contexts and finds pretrained LMs fail to represent it well.
- LREC 2026 **There Is No Spoon: Existential Presupposition in Large Language Models** directly studies existential presupposition and projection.

Neither paper owns the exact inferential quantity “intensional transitive verb cancels/suspends existential commitment,” so this is not formally killed yet. But reviewer compression is much more dangerous than for SOT.

---

# 6. Rediscovered ideas that must NOT be revived

During taste search, two superficially beautiful phenomena reappeared:

- **Plural homogeneity / truth-value gaps** — already **K002**.
- **Free-choice inference** (`may A or B` → permission for each) — already **K016**.

They are not new candidates. Their reappearance is evidence that the taste filter is working, not permission to resurrect them.

Other rejected neighbor:

- **Privative adjective inference** (`fake gun` is not a gun) has direct ownership: COLING 2022 already tests adjective–noun compositional entailment including `fake`; Ross 2024/2025 explicitly studies human + LLM privative inference/generalization; *SEM 2026 studies functional vs representational adjective–noun compositionality. Register separately as K253.

- **Generic distributive/collective plurality** also has direct LLM ownership: BlackboxNLP 2022 **Testing Pre-trained Language Models’ Understanding of Distributivity via Causal Mediation Analysis**. Do not create a new kill ID; treat as existing occupied parent / anti-resurrection.

- **Fake/modal past in counterfactuals** is theoretically beautiful, but ACL 2023 already directly tests LMs’ linguistic sensitivity in counterfactual conditionals; current modal-past theory is active. It is weaker than SOT on ownership.

---

# 7. Ranking after this search

1. **Sequence of Tense / embedded past** — strongest. Natural mature object, clean consequence, tiny-study path, exact LLM owner not found, result valuable both directions.
2. **Before/After Veridicality** — excellent taste fit but old event-factuality ownership creates reviewer compression risk.
3. **Intensional Transitive Existential Commitment** — beautiful and cheap, but TACL referential-opacity + LREC existential-presupposition neighbors raise ownership risk.

No L number yet. No pilot. The correct next operation for rank 1 is one more independent owner-and-gold review, not experiment design inflation.

---

# 8. Sources checked in this round

Representative sources:

- Sharvit (2020), **Sequence of Tense**, Wiley Blackwell Companion to Semantics.
- Gennari (2003), **Tense Meanings and Temporal Interpretation**, Journal of Semantics.
- Mucha, Renans & Romoli (2023), **Sequence of tense and cessation implicatures: evidence from Polish**, NLLT.
- Alxatib & Caplan (2026), **Embedded tense and the problem of acquisition**.
- Armenante, Hohaus & Stolterfoht, **Transparency in the processing of temporal ambiguity: The case of embedded tense**.
- Politzer-Ahles, Xiang & Almeida (2017), **Before and after: temporal connectives and chronological ordering**.
- Sanchez Valencia, van der Wouden & Zwarts (1993), **Polarity, veridicality and temporal connectives**.
- Sauri, **A Factuality Profiler for Eventualities in Text**.
- Wu et al. (2023), TACL, **Transparency Helps Reveal When Language Models Learn Meaning**.
- Wörgötter, Lai & Schuster (2026), LREC, **There Is No Spoon: Existential Presupposition in Large Language Models**.
- Ban et al. (2022), BlackboxNLP, **Testing Pre-trained Language Models’ Understanding of Distributivity via Causal Mediation Analysis**.
- Ross dissertation / project (2024–2025), privative adjective–noun inference in humans and LLMs.

Search discipline: this file records **scientific pressure**, not publication-ready novelty claims. Exact-owner absence is provisional until an independent second pass.