# L41 — Project Brief

**Title:** Does Parameter Learning Respect Semantic Commitment?  
**Status:** `PILOT-AUTHORIZED — E01 ONLY`  
**Target:** ACL / EMNLP / NAACL Main  
**Scientific object:** the language → parameter knowledge-acquisition operator  
**Primary identification:** two-way implicatives (`manage / fail × polarity`)  
**Canonical experiment:** E01 in `PILOT_CARD.md`

> **One-sentence question:** When a language model is trained on a sentence that mentions a proposition `p`, does the resulting persistent update about the world follow what the whole sentence semantically commits to, or does training mainly absorb the mentioned proposition / local surface pattern?

---

# 1. Why this problem exists

Large language models acquire an enormous amount of world knowledge from ordinary text. This fact is so familiar that we usually compress the process into a simple picture:

```text
text about the world  →  language-model training  →  world knowledge in parameters
```

But ordinary language is not a list of facts.

A proposition can be **mentioned** without being asserted as true. Consider the embedded proposition:

```text
p = Neris entered Chamber 47.
```

It can appear in sentences such as:

```text
Neris entered Chamber 47.               → commits to p
Neris did not enter Chamber 47.          → commits to ¬p
Neris managed to enter Chamber 47.       → commits to p
Neris did not manage to enter Chamber 47.→ commits to ¬p
Neris failed to enter Chamber 47.        → commits to ¬p
Neris did not fail to enter Chamber 47.  → commits to p
```

The lexical material describing `p` can therefore occur in both **truth-supporting** and **truth-denying** environments.

This distinction is old. Formal semantics, textual inference, factuality and information-extraction work all distinguish **mention** from **factual commitment**. An event being linguistically present in a document is not sufficient evidence that the event happened.

Modern LLM training creates a new version of this old problem. There is usually no explicit symbolic fact extractor sitting between the text and the parameters. The model is trained directly by next-token prediction. Yet the resulting parameters clearly acquire persistent factual beliefs / factual behavior.

That leaves a basic scientific question largely implicit:

> **What makes a textual occurrence count as evidence for a world fact during parameter learning?**

Does ordinary gradient learning inherit the semantic interpretation already available to the model? Or can a proposition be correctly interpreted as false in context and nevertheless be absorbed as true when that context becomes training data?

L41 is about this **learning operator**, not about whether the model knows the relevant semantics at inference time.

---

# 2. The scientific pressure

Three literatures collide here.

## 2.1 Formal semantics: mention is not commitment

Classic work on veridicality, factuality, factive/implicative predicates and textual inference treats the embedding environment as decisive for whether a proposition is supported.

For two-way implicatives, the semantic signature gives an especially crisp prediction:

```text
manage: + | -
fail:   - | +
```

meaning:

```text
managed to p       ⇒  p
not managed to p   ⇒ ¬p
failed to p        ⇒ ¬p
not failed to p    ⇒  p
```

The important point is not the linguistic phenomenon by itself. The important point is that it gives us an **independently established truth-commitment function** over sentences.

Primary semantic ancestry:

- Nairn, Condoravdi & Karttunen (2006), *Computing relative polarity for textual inference*.
- Karttunen (2012), *Simple and Phrasal Implicatives*.

## 2.2 LLM belief acquisition: document training can create persistent beliefs

Synthetic-document finetuning and related work show that ordinary document-like training can insert durable factual behavior into model parameters. This establishes that the dependent variable we need is measurable: after training, remove the document and ask a neutral question about the world.

The relevant quantity is not recall of the training sentence; it is the **change in neutral-context belief about the embedded proposition**.

## 2.3 Negation Neglect: understanding and learning can dissociate

Mayne et al. (2026), *Negation Neglect*, provide the strongest modern pressure.

Their models can correctly recognize in context that a claim is false / fictional / negated, but finetuning on the same material can still make the model behave as if the underlying claim were true. This means:

```text
correct online interpretation
        does not guarantee
correct persistent factual uptake
```

They also find that **local negation** such as `X did not happen` is much more effective than document-level warnings or distant qualifiers.

But this leaves a critical ambiguity unresolved:

> Does local negation work because the training update actually respects sentence-level semantic commitment, or merely because local negative syntax/token structure changes the gradient around the proposition?

A simple `p` versus `not p` comparison cannot answer this, because **surface polarity and semantic commitment reverse together**.

That is exactly where L41 starts.

---

# 3. Core research question

## Full question

> **When language is used as training data, does a language model update its persistent world beliefs according to what the sentence semantically commits to, or mainly according to propositions that are mentioned / locally repeated?**

## Operational question

> After the base model has demonstrated correct in-context understanding of an implicative sentence, does training on that sentence change its later neutral belief about the embedded event according to the implicative semantic signature?

## What is being held fixed

The critical experiment keeps the scientific object and observable fixed:

- same base model;
- same training objective;
- same kind of proposition;
- same proposition-bearing complement;
- same neutral post-training factual query;
- same persistent belief quantity.

What changes is the sentence's **independently defined semantic commitment** to `p`.

---

# 4. What we want to establish

There are two levels here, and they must not be confused.

## 4.1 Preferred positive statement

The strongest positive result would support:

> **Ordinary parameter learning can respect compositional semantic commitment: the same mentioned proposition produces opposite signed factual updates when lexical semantics changes whether the sentence entails `p` or `¬p`.**

This is stronger than saying that the model understands implicatives. It says that semantic interpretation participates in deciding **what becomes persistent world knowledge**.

## 4.2 The actual scientific target

We must not make the project contingent on obtaining the positive checkerboard. The real target is to identify which of the following operators better describes factual uptake:

### H_sem — semantic-commitment learning

The learning update composes enough sentence meaning that later neutral belief follows the sentence-level entailment.

Expected pattern:

```text
manage+  : p   ↑
manage-  : p   ↓
fail+    : p   ↓
fail-    : p   ↑
```

### H_mention — mention / co-occurrence learning

The occurrence of the proposition-bearing tokens mainly strengthens `p`-related associations regardless of commitment.

Expected pattern:

```text
manage+  : p ↑
manage-  : p ↑
fail+    : p ↑
fail-    : p ↑
```

The exact magnitudes may differ, but the semantic reversal is absent.

### H_surface — local polarity / syntax learning

Local negation changes uptake, but the model does not compose the lexical implicative signature into the signed update.

Expected qualitative pattern:

```text
positive matrix clauses  > negative matrix clauses
for both manage and fail
```

Again, the semantic checkerboard is absent.

A clean H_mention or H_surface result **after the forward semantic gate passes** is not a failed pilot. It establishes a dissociation between understanding and learning.

---

# 5. The identifying idea: make semantics and surface form disagree

The key contribution of the experiment is the `manage/fail × polarity` checkerboard.

With ordinary negation:

```text
p       → p
not p   → ¬p
```

surface polarity and semantic commitment are perfectly correlated.

With two-way implicatives:

| condition | example | local negation? | commitment about `p` |
|---|---|---:|---:|
| M+ | managed to p | no | `p` |
| M− | did not manage to p | yes | `¬p` |
| F+ | failed to p | no | `¬p` |
| F− | did not fail to p | yes | `p` |

Now the two negative-polarity conditions have the **same local negation status but opposite truth commitments**, and the two positive-polarity conditions likewise differ in commitment.

This gives a real theory-discriminating interaction rather than another minimal-pair benchmark.

---

# 6. Primary observable

For each novel proposition `p`, ask a neutral question before and after training:

```text
Did Neris enter Chamber 47?
Yes / No
```

Define neutral belief:

```text
B(p) = log P(Yes | q_p) - log P(No | q_p)
```

and factual uptake:

```text
U(v,s,p) = B_after(v,s,p) - B_before(p)
```

The primary difference-of-differences is:

```text
I = [mean U(manage,+) - mean U(manage,-)]
    - [mean U(fail,+) - mean U(fail,-)]
```

Predictions:

- `H_sem`: large positive `I`, with both within-verb reversals in the predicted directions;
- `H_surface`: polarity effect similar for `manage` and `fail`, so `I ≈ 0`;
- `H_mention`: positive/salience-like uptake across cells, so `I ≈ 0`.

A significant `I` driven by one pathological cell is not sufficient. The four-cell geometry matters.

---

# 7. Desired paper narrative

The intended paper should be extremely easy to state.

## Act I — LMs learn facts from language, but language does not equal facts

Modern models acquire world knowledge from raw text. Formal semantics has always told us that a proposition being mentioned is not the same as the sentence committing to it.

This creates a missing link in our understanding of pretraining:

> **How does a language model decide which textual propositions become beliefs about the world?**

## Act II — Recent evidence shows a learning/understanding mismatch

Negation Neglect shows that a model can understand a claim is false in context yet still learn the claim as true when the text becomes training data.

However, local negation often works, leaving two explanations:

1. the learning operator respects semantic commitment when truth status is locally compositional;
2. local negation merely changes token/syntactic gradients and does not imply semantic filtering.

Existing work does not identify between them.

## Act III — Classical semantics gives a decisive crossover

Two-way implicatives let us hold proposition mention fixed while making **surface polarity and semantic commitment disagree**.

This converts an old semantic distinction into a modern causal test of parameter learning.

## Act IV — The result tells us what kind of learner an LM is

### Story A: semantic checkerboard

> Models do not merely memorize mentioned propositions. Ordinary gradient learning can use compositional semantics to determine the sign of persistent factual updates.

This would sharply qualify the interpretation of Negation Neglect: the failure is not a universal inability to learn truth status, but a boundary condition on when semantic context controls learning.

### Story B: mention dominates despite correct understanding

> Models can understand what a sentence says without using that understanding to decide what the sentence teaches them about the world.

This is arguably an even more striking scientific story: **semantic competence and knowledge acquisition are separable operators**.

### Story C: local polarity dominates

> The success of local negation is not evidence that factual learning is semantic. It can be explained by local syntactic/token learning structure that ignores the lexical-semantic reversal.

This would directly reinterpret the strongest apparent mitigation in Negation Neglect.

The paper should therefore be framed around **identifying the learning rule**, not around “showing our expected positive effect.”

---

# 8. Why this is not already owned

## 8.1 Not a semantic competence benchmark

The base model must first pass the exact in-context semantic task. We then remove the sentence and measure the parameter update.

Possible result:

```text
in context:  correctly says ¬p
post-training neutral query: behaves as if p
```

A factivity/implicativity benchmark cannot observe that dissociation.

## 8.2 Not “Negation Neglect with another wording”

The contribution is not that `manage` or `fail` improves negation learning. The contribution lives in the **interaction where the same surface polarity predicts opposite semantic commitments across verbs**.

If the study degrades into a collection of wording tricks that reduce Negation Neglect, the project should be killed.

## 8.3 Not Zhang et al. 2024, *Co-occurrence Is Not Factual Association*

That work is the strongest reviewer-compression risk and must remain explicit.

Zhang et al. show that direct co-occurrence can yield a shallow association whereas indirect/reference-mediated training can yield more transferable factual association. However, both training forms support the **same true relation**.

L41 asks a different quantity:

> when the same proposition is mentioned, does changing whether the **whole sentence entails or contradicts it** reverse the sign of later neutral belief uptake?

Their manipulation changes representation route / explicitness of a true fact; ours changes **truth commitment** while preserving proposition mention.

## 8.4 Not a generic belief-insertion paper

Synthetic document finetuning establishes that persistent beliefs can be inserted. L41 asks which textual occurrences count as positive versus negative evidence.

---

# 9. E01: initial experiment

E01 is deliberately narrow. It should answer only whether the quantity exists and which broad account it supports.

## 9.1 Stage A — build the instrument without touching the critical result

Use one fixed open pretrained/base causal LM in the 4B–8B range.

Before inspecting any post-training `manage/fail × polarity` effect, freeze:

- exact checkpoint + revision;
- tokenizer;
- optimizer / learning rate;
- precision;
- number of exposures / document mix;
- micro-document shell;
- neutral query family;
- proposition generator;
- sample size.

Only the following development information may be used to tune those choices:

1. **forward semantic understanding** of the four constructions;
2. **direct assertion / direct denial uptake**;
3. baseline neutral-query behavior;
4. tokenization and surface balance;
5. training loss / generic capability sanity;
6. measurement variance that does not use the critical checkerboard.

The critical implicative post-training interaction must remain sealed during instrument construction.

## 9.2 Proposition generator

Use invented, semantically simple propositions with negligible prior support, e.g.:

```text
p_i = Neris entered Chamber 47.
```

Critical realizations:

```text
M+ : Neris managed to enter Chamber 47.
M- : Neris did not manage to enter Chamber 47.
F+ : Neris failed to enter Chamber 47.
F- : Neris did not fail to enter Chamber 47.
```

Generator constraints:

- novel entities / locations;
- simple telic events compatible with both `manage` and `fail`;
- no modal, negated or factive material inside the complement;
- no world knowledge required;
- no pragmatically bizarre `manage/fail` pairing;
- matched document shells across arms;
- surrounding text never separately reveals whether `p` occurred.

## 9.3 Mandatory forward semantic gate

Before using these constructions to make a learning claim, verify the base model interprets them correctly **in context**.

Expected answers:

```text
M+ -> Yes
M- -> No
F+ -> No
F- -> Yes
```

Frozen gate:

- overall accuracy ≥ 90%;
- no cell < 85%;
- mean Yes-vs-No log-odds show the expected checkerboard, not only decoded labels.

Failure means **instrument failure**, not a result about parameter learning.

## 9.4 Direct signed-learning control

On separate propositions, train with:

```text
A+ : Neris entered Chamber 47.
A- : Neris did not enter Chamber 47.
```

Measure the same neutral belief shift.

Define:

```text
D = mean(U_A+) - mean(U_A-)
```

Required before confirmation:

- `D ≥ 1.0` log-odds;
- paired/proposition bootstrap 95% CI excludes 0;
- no catastrophic capability collapse.

This establishes that the selected training regime is capable of learning **signed facts at all**.

If this cannot be achieved under the bounded budget, stop. Do not interpret a null implicative result.

## 9.5 Untouched confirmation

Default frozen E01-B:

- 256 fresh proposition identities;
- 4 Latin-square assignments;
- every proposition appears once in each of M+, M−, F+, F− across independent resets;
- 3 independent training-order seeds per assignment;
- 12 bounded finetuning runs from the same base checkpoint;
- several frozen neutral query paraphrases may be averaged **within proposition**, never counted as independent samples.

Independent statistical unit: **proposition identity**.

Runs/seeds are blocking/random factors. Documents, repetitions and prompt paraphrases are not independent observations.

## 9.6 Surface and token audit

Before confirmation, record and balance:

- complement mention counts;
- proposition-token positions;
- sentence/document lengths;
- matrix verb tokenization;
- negation tokenization;
- entity/event tokenization;
- number of loss-bearing training tokens;
- exposure count;
- shell frequency.

The factorial interaction cancels many fixed effects but does not excuse a gross exposure imbalance.

## 9.7 Primary analysis

Report:

1. all four cell means;
2. `manage+ - manage−`;
3. `fail+ - fail−`;
4. primary checkerboard `I`;
5. direct control `D`;
6. normalized semantic fidelity:

```text
F_sem = I / (2D)
```

Under a simple symmetric idealization, `F_sem ≈ 1` means the implicative semantic checkerboard is as strong as the direct assertion-vs-denial learning signal.

With 256 paired proposition identities, planning calculations give approximate 80%-power MDE around 0.35–0.53 log-odds if proposition-level SD is 2–3 log-odds. If dev-only variance implies MDE > 0.5, increase N **before** opening E01-B; never shrink below 256 after seeing favorable variance.

---

# 10. E01 decision rule

| observation | interpretation | decision |
|---|---|---|
| clean semantic checkerboard; both within-verb reversals | semantic commitment controls signed factual uptake in this regime | **PASS E01 → design E02** |
| all/most cells push `p` similarly; forward semantics passed | mention/co-occurrence dominates learning despite understanding | **PASS E01 → important opposite answer** |
| negative polarity suppresses both verbs similarly; forward semantics passed | local polarity/syntax controls uptake, not full semantic signature | **PASS E01 → important opposite answer** |
| interaction driven by one cell / lexical idiosyncrasy | no clean general inference | **HOLD / likely KILL** |
| direct assertion/denial control fails | learning instrument unresolved | **STOP** |
| forward semantic gate fails | treatment not semantically represented | **STOP** |
| result appears only after model/LR/prompt/verb shopping | contaminated phenomenon gambling | **KILL** |

The pilot is therefore **not a positive-effect gamble**. The only real bad outcomes are an unresolved instrument, lexical mess, or post-hoc search.

---

# 11. What E01 must not become

Until E01 is interpreted, do **not** broaden into:

- a MegaVeridicality-sized factuality benchmark;
- broad factive/nonfactive verb sweeps;
- modality / conditionals / quotation / fiction;
- multilingual work;
- model zoo comparison;
- instruction vs base vs RL study;
- activation probing / SAE / patching;
- gradient-mechanism story;
- mitigation method;
- dataset release as the contribution.

Those are possible later boundary/mechanism studies only if E01 establishes a clean scientific quantity.

---

# 12. What a Main paper could become after E01

A strong E01 would justify a compact but real full program.

## If semantic commitment wins

Natural next questions:

1. **Scope / boundary:** Which semantic operators control learning and which do not? Implicatives → factives → modals/conditionals/attitudes only after the core is established.
2. **Locality:** Is commitment respected only when the decisive semantic operator is local to `p`?
3. **Compositional depth:** How far can the truth-signature dependency be nested before uptake reverts to mention?
4. **Training-stage boundary:** Does the effect differ between continued pretraining and instruction/SFT only if this comparison answers a specific learning-rule question.

## If mention or surface polarity wins

The paper becomes a dissociation paper:

1. show robust correct forward interpretation;
2. show systematically wrong/non-semantic persistent uptake;
3. map the minimal boundary where online semantics ceases to control learning;
4. test a small number of preregistered semantic signatures to establish generality;
5. only then ask mechanism.

The strong claim would be:

> **What a model understands from text and what it learns as world knowledge from that same text are not the same computation.**

That is Main-level only if the dissociation is clean, stable and not reducible to one lexical quirk.

---

# 13. Reviewer-facing compression sentence

The project should always be explainable in one contrast:

> **Previous work asks whether LMs can understand factuality, or shows that false/qualified text can still implant beliefs. We ask whether the *sign of the parameter update itself* follows an independently defined semantic commitment, using a crossover where surface negation and semantic truth make opposite predictions.**

If we can no longer say this sentence truthfully, the project has drifted.

---

# 14. Current registration boundary

L41 is **registered but not validated**.

Current status means exactly:

```text
Selection passed on paper.
One bounded E01 is scientifically justified.
No mother result has been observed.
No E02 or full paper program is authorized yet.
```

The immediate next action is therefore not more literature decoration and not mechanism work. It is to implement the sealed E01-A instrument, freeze it without reading the critical checkerboard, and then run untouched E01-B.
