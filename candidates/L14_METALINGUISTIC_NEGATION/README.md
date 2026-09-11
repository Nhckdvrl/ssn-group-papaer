# L14 — Negation of the World, or Negation of the Words?

## Metalinguistic Negation as an LLM Target-Selection Problem

**Status:** **SERIOUS CANDIDATE / PRE-PILOT — 2026-09-11**  
**Paper mainline:** NOT APPROVED  
**Target:** ACL / EMNLP / NAACL Main

> **Plain example:**  
> *The movie wasn't good — it was excellent.*  
> Did the speaker mean that the movie failed to be good? **No.** The speaker rejects *good* as an inadequate description while committing to the stronger state *excellent*.
>
> Contrast:  
> *The movie wasn't good — it was terrible.*  
> Here the negation is ordinary world-state negation.

---

## 1. One-sentence research question

> **When an LLM encounters `not`, does it determine what level is being rejected — a proposition about the world or the linguistic description itself — before applying polarity, or does it default to propositional negation and repair only after later context forces a reinterpretation?**

This is not simply another negation-accuracy benchmark. The scientific object is **negation-target selection**.

---

## 2. Why this has the desired paper shape

The parent phenomenon is classical and immediately understandable. Linguistics distinguishes ordinary/descriptive negation from **metalinguistic negation**, where a speaker objects to the wording, strength, register, morphology, presupposition, or other aspect of an utterance rather than denying the corresponding state of affairs.

Canonical examples include:

- *I'm not happy — I'm ecstatic.*
- *She didn't solve some of the problems — she solved all of them.*
- *I didn't catch two mongeese — I caught two mongooses.*

Human psycholinguistics has also debated two processing accounts:

1. **default + repair:** interpret `not X` descriptively first, then reinterpret when the correction makes that reading contradictory;
2. **context-sensitive target selection:** sufficiently informative context can license the metalinguistic interpretation directly.

This gives the LLM paper a real explanatory question after the first behavioral result rather than a post-hoc mechanism hunt.

---

## 3. Modern tension

Recent LLM negation work largely treats better sensitivity to negation as desirable: a model should notice that inserting `not` reverses meaning. That is correct for ordinary descriptive negation.

Metalinguistic negation exposes the missing half:

> **sometimes stronger lexical sensitivity to `not` is exactly the wrong computation if the negation targets an expression rather than the world-state proposition.**

So the modern question is not merely whether a model detects negation, but whether it knows **what the negation is operating on**.

A particularly strong result would be a trade-off:

> interventions/prompts that reduce ordinary *negation blindness* improve descriptive negation but increase false world-state negation on metalinguistic cases.

That would show that current “negation robustness” is partly measuring cue sensitivity rather than correct semantic target selection.

---

## 4. Current ownership audit

### Classical owners — assets, not novelty

We do **not** claim to discover metalinguistic negation. Relevant classical/experimental lines include Horn; Carston; Noh et al.; Moeschler; Blochowiak & Grisot.

Blochowiak & Grisot (2018) are especially useful because they experimentally contrast descriptive and metalinguistic negation and provide public human experimental data; their results bear directly on default-repair versus context-driven processing.

### Closest modern NLP neighbors

- **Kim et al., EMNLP 2025 Main, _Semantic Inversion, Identical Replies: Revisiting Negation Blindness in Large Language Models_** — establishes failures to respond to ordinary semantic inversion caused by negation. It assumes the negation should reverse the proposition; it does not study metalinguistic target selection.
- **Seo et al., EMNLP 2025 Main, _The Impact of Negated Text on Hallucination with Large Language Models_** — studies negated inputs and token-level internal effects, again under ordinary negation.
- **Yanaka & Yamamoto, NALOMA 2026, _Revisiting the Systematicity in Negation in the Era of In-Context Learning_** — studies recognition of negation expressions/scope and negation-related function vectors. Scope inside a proposition is not the same quantity as deciding whether `not` rejects the proposition or a linguistic representation.
- **Cho, ACL 2026 Main, _Continuous Interpretive Steering for Scalar Diversity_** — owns graded scalar-implicature steering, not metalinguistic negation.
- **Spinoso-Di Piano et al., 2026 preprint, _Evaluating Communicative Belief Updates ... via Implicature Recognition and Cancellation_** — makes scalar/other implicature cancellation a dangerous neighbor. Therefore L14 must **not** collapse into a `some→all` cancellation paper; scalar cases are one diagnostic subtype only.

Exact searches for `metalinguistic negation × LLM / GPT / transformer / ACL / NLP`, plus alternative phrases `descriptive vs metalinguistic negation`, `contrastive negation`, and `negation target`, did not reveal a modern paper that owns the proposed LLM target-selection question. This is a search result, not proof of global absence.

### Strongest reviewer compression

> **“Negation Blindness + old metalinguistic-negation stimuli, with some scope/implicature controls.”**

This compression is fatal if the paper only reports accuracy on `not X — Y` sentences.

### Strongest surviving contribution

> Existing LLM negation work asks whether models apply polarity reversal reliably; L14 asks whether the model first identifies **the semantic level that `not` targets**, and whether increasing ordinary negation sensitivity causes systematic over-negation when the target is metalinguistic rather than propositional.

The paper survives only if experiments establish this target-selection computation or a consequential trade-off, not merely another hard negation set.

---

## 5. Data and gold path

### Human seed / validation source

Blochowiak & Grisot (2018) release experimental materials and human data for paired descriptive/metalinguistic negation conditions. These are useful as a naturalness/processing reference, not sufficient by themselves as the English LLM benchmark.

### Controlled English core

Construct a small, human-validated set of lexical bases with matched conditions. Favor cases where the correction independently fixes the world state.

Example base:

1. **AFFIRMATIVE:** *The movie was good.*
2. **DESCRIPTIVE NEGATION:** *The movie wasn't good — it was terrible.*
3. **METALINGUISTIC NEGATION:** *The movie wasn't good — it was excellent.*
4. **STRONGER CONTROL:** *The movie was excellent.*

Target proposition:

> *The movie was at least good.*

Gold is YES for 1/3/4 and NO for 2.

Use more than one subtype so the paper is not scalar-implicature cancellation in disguise:

- upward scalar correction (`good → excellent`);
- quantifier/degree correction where the stronger continuation logically includes the weaker (`some → all`), used cautiously because cancellation work is close;
- form/wording corrections where the corrected clause fixes the same world fact (`mongeese → mongooses`), testing literal world-state leakage from a clearly linguistic rejection.

All critical English items require human naturalness and intended-reading validation. Do not use an LLM judge to create the load-bearing label.

---

## 6. Prospective paper development — audited before the pilot

### C1 — Target selection, not negation detection

On matched descriptive versus metalinguistic cases, ask whether models preserve the correct **world-state proposition** despite the same surface negator.

The important quantity is not raw MN accuracy; it is the two-sided profile:

- failure to reverse when `not` is descriptive;
- false reversal when `not` is metalinguistic.

### C2 — Default-repair versus context-sensitive processing

Use the classical human-processing contrast prospectively:

- **pre-disambiguating context:** context already licenses the stronger/corrective state before `not X` appears;
- **post-disambiguating correction:** the model sees `not X` before the correcting clause arrives;
- matched descriptive controls.

Ask whether the model's commitment trajectory behaves like an unconditional polarity-first computation followed by repair, or whether prior context changes the target assigned to negation from the outset.

This is the planned explanation; do not substitute generic hidden-state probing if the behavioral operation already distinguishes the accounts.

### C3 — Consequence for “negation robustness”

Re-evaluate ordinary negation-focused interventions (e.g. explicit warnings to attend to negation) on the two-sided target-selection set.

Key prospective result:

> a method can improve ordinary negation accuracy while worsening metalinguistic cases, showing that `more attention to not` is not a monotonic improvement in negation understanding.

A target-aware output/representation can be used as a diagnostic control, not automatically promoted into a method paper.

---

## 7. Successful-result test

### Strong success

Across model families, ordinary negation sensitivity and metalinguistic over-negation form a stable trade-off; context manipulations show that the error comes from target selection rather than failure to know the correction term. Existing negation remedies move the trade-off rather than solving it.

**What readers learn:** negation robustness is mis-specified if it only measures polarity inversion; LLMs must decide whether `not` targets a proposition or a representation.

### Also interesting

Models handle final MN sentences correctly but pre-context/post-correction manipulations reveal systematic polarity-first repair. This remains useful only if it predicts a real downstream/incremental consequence; otherwise it is too psycholinguistic for Main.

### Weak / kill

- strong models are essentially ceiling on both target types;
- no stable processing distinction appears;
- warning/intervention effects do not reveal a meaningful trade-off;
- the result reduces to scalar implicature cancellation;
- a direct modern owner of metalinguistic target selection is found.

**Do not rescue a weak pilot by adding probes, layers, more models, or a new abstract label.**

---

## 8. Current verdict

# **SERIOUS CANDIDATE — worth one bounded, cheap pilot after final stimulus audit.**

Why it currently survives:

- classic problem with a one-line example;
- simple, natural controlled data;
- human experimental parent and competing processing accounts;
- a fresh LLM-era question that is not ordinary negation accuracy;
- a prospective C1→C2→C3 development path already novelty-audited;
- a concrete real consequence for how negation robustness is measured;
- explicit kill conditions if modern models simply solve it.

It is **not** paper-mainline-approved and is **not yet authorized for broad experimentation**.
