# L41 — Does Parameter Learning Respect Semantic Commitment?

**Status:** `PILOT-AUTHORIZED — E01 ONLY`  
**Date registered:** 2026-09-15  
**Origin:** WALL-BE — semantic commitment / parametric factual uptake  
**Target:** ACL / EMNLP / NAACL Main

> **This is not a validated project result.** The mother phenomenon and effect size are unverified. Only the bounded E01 in `PILOT_CARD.md` is authorized.

---

## 1. Research question

> **When language is used as training data, does a language model update its persistent world beliefs according to what the sentence semantically commits to, or mainly according to propositions that are mentioned/predictively repeated?**

Short form:

> **Does parameter learning respect semantic commitment?**

The scientific object is the **language-to-parameter learning operator**, not semantic competence at inference time.

---

## 2. Why the question matters

Language models acquire large amounts of world knowledge from ordinary text. But ordinary text does not simply list facts.

The same proposition can occur inside:

- an assertion;
- a negation;
- an implicative or factive construction;
- an attitude report;
- a modal or conditional;
- a hypothetical or fictional context;
- a source whose commitment is uncertain.

Formal semantics and event-factuality work have long distinguished **mention** from **commitment**. A proposition appearing in a sentence is not sufficient evidence that it is true in the actual world.

Modern pretraining creates a new scientific problem:

> raw text is converted directly into parameters, so what implicit operation decides which linguistic occurrences become durable world knowledge?

If parameter learning respects semantic composition, the sign of a factual update should track what the sentence entails. If it instead mainly learns mention/co-occurrence or local token patterns, a model may understand a sentence correctly in context while storing the wrong world fact from it.

---

## 3. Why this is not another factivity / presupposition benchmark

The model must first pass an **in-context semantic-understanding gate** on exactly the constructions used in training.

Only after that gate is passed are the sentences used as training data. The linguistic context is then removed and the model is queried neutrally about the embedded proposition.

Therefore the possible dissociation is:

```text
forward interpretation: sentence commits to ~p
parameter learning:     later neutral model behaves as if p
```

A semantic competence benchmark cannot reveal this dissociation.

K056's generic presupposition/projection competence parent therefore remains killed and is not being reopened.

---

## 4. Old semantic quantity

The strongest E01 substrate is **two-way implicativity**.

Classic implicative signatures distinguish predicates whose complement factuality reverses with matrix polarity.

Canonical pair:

```text
managed to p       =>  p
not managed to p   => ~p
failed to p        => ~p
not failed to p    =>  p
```

In the usual notation:

- `manage`: `+|-`
- `fail`: `-|+`

References:

- Nairn, Condoravdi & Karttunen (2006), *Computing relative polarity for textual inference*: https://aclanthology.org/W06-3907/
- Karttunen (2012), *Simple and Phrasal Implicatives*: https://aclanthology.org/S12-1020/
- Stanford Implicative Corpus: https://linguistics.stanford.edu/events/learning-corpus-implicatives

This gives a hard external semantic prediction rather than an author-invented label.

---

## 5. Frontier pressure

### Negation Neglect

Mayne et al. (2026) show that models can correctly interpret negation / epistemic qualification in context yet internalize the underlying claim as true when the same material is used for finetuning.

They also show that **local negation** often greatly reduces the effect, but they do not distinguish:

- semantic commitment;
- local syntax/composition;
- surface polarity;
- token-level gradient structure.

Their explanation explicitly leaves the origin of the truth-favoring inductive bias unresolved.

Paper: https://arxiv.org/abs/2605.13829

### Why the implicative checkerboard is new leverage

Local negation alone confounds polarity and commitment:

```text
p
not p
```

Both surface polarity and truth commitment reverse together.

`manage/fail x polarity` orthogonalizes them. The two negative matrix conditions have the same local negation but opposite semantic commitments about the complement.

That is the identifying operation.

---

## 6. Competing accounts

### A — semantic-commitment learning

The update induced by a training sentence preserves enough compositional semantics that persistent neutral belief about `p` follows the sentence-level entailment.

Predicted pattern:

```text
manage+  -> p uptake
manage-  -> ~p uptake
fail+    -> ~p uptake
fail-    -> p uptake
```

### B — mention / co-occurrence learning

Repeatedly seeing the tokens expressing `p` strengthens `p`-related associations even when the sentence does not commit to `p`.

Predicted pattern: positive/salience-like uptake across several or all cells; weak semantic checkerboard.

### C — surface-polarity / locality learning

Local negative morphology suppresses factual uptake, but the learner does not compose the lexical implicative signature into the update.

Predicted pattern: positive matrix clauses behave similarly; negative matrix clauses behave similarly; weak or wrong checkerboard.

These accounts predict differently on the same post-training neutral factual-belief quantity.

---

## 7. Primary quantity

For each novel event proposition `p`, measure a neutral yes/no log-odds before and after training:

```text
U(v,s,p) = logit_after(Yes vs No | neutral query about p)
           - logit_before(Yes vs No | neutral query about p)
```

Primary interaction:

```text
I = [U(manage,+) - U(manage,-)]
    - [U(fail,+) - U(fail,-)]
```

Semantic commitment predicts `I > 0` with the four cells forming a checkerboard.

The interaction is essential. A main effect of polarity, verb, or training alone is not the L41 claim.

---

## 8. Direct controls

Use separate novel propositions for direct assertions and direct denials:

```text
p happened.
p did not happen.
```

Define:

```text
D = U(direct assertion) - U(direct denial)
```

If `D` is not clearly positive under the frozen training budget, the instrument cannot resolve signed factual acquisition and E01 stops.

A useful secondary scale is:

```text
F = I / (2D)
```

where `F ~= 1` would mean the implicative checkerboard is as strong as the direct positive-vs-negative training signal.

---

## 9. Ownership boundary

### Directly covered / not novelty

- whether LMs understand negation;
- whether LMs understand implicatives/factivity;
- event-factuality classification;
- generic presupposition projection;
- synthetic document finetuning can insert beliefs;
- Negation Neglect exists;
- local negation often reduces Negation Neglect;
- co-occurrence can differ from transferable factual association;
- source/usefulness tags can modulate later learning;
- conditional finetuning can selectively learn corpus statistics;
- methods that edit gradients to impose epistemic frames.

### Selected remainder

> **When the same proposition is mentioned under controlled local syntax, does ordinary language-model training assign a signed factual update according to the sentence's independently defined semantic commitment?**

The crucial novelty is not `implicative verbs in LLMs`; it is the **semantic-commitment checkerboard as an identification of the training update**.

---

## 10. Dangerous reviewer compressions

### `Negation Neglect with manage/fail.`

L41 dies if it merely compares another wording of negative training data. It survives only through the pre-specified two-way implicative interaction where local negation and semantic commitment make different predictions.

### `Co-occurrence Is Not Factual Association with semantics.`

Zhang et al. (NeurIPS 2024) compare explicit co-occurrence with an indirect/reference-mediated expression of the **same true factual association** and study generalization/representation.

L41 compares occurrences that all mention the same `p` but whose sentence meanings entail `p` or entail `~p`. The target is signed neutral belief uptake, not whether a learned true relation transfers to reasoning.

### `MegaVeridicality but finetuned.`

Forward factuality judgments are only an instrument gate / later treatment gold. The paper's dependent variable is the persistent belief left after the semantic context disappears.

---

## 11. Main-level result space

### A — semantic checkerboard

Ordinary parameter learning respects local compositional semantic commitment.

Consequence: Negation Neglect is not a universal inability to encode truth status during learning; the boundary lies between kinds/scopes of semantic conditioning.

### B — mention/co-occurrence dominates

The model understands the implicative inference in context but later stores `p` similarly across semantically positive and negative occurrences.

Consequence: inference-time semantic competence and the language-to-world-knowledge acquisition operator are different objects; parameter learning can treat non-factual mentions as factual evidence.

### C — surface polarity dominates

Local negation suppresses uptake, but `manage` and `fail` do not reverse as semantic theory predicts.

Consequence: the local-negation success in Negation Neglect is better explained by local syntactic/token learning structure than semantic factuality.

### D — direct assertion/denial cannot create signed uptake

Instrument failure. No scientific claim.

### E — base model does not correctly understand the implicatives

Instrument failure. No scientific claim.

---

## 12. Why both answers matter

A positive semantic checkerboard would show that ordinary gradient learning can use compositional meaning to decide what becomes factual world knowledge.

A clean failure after verified forward understanding would show the opposite and expose a basic mismatch between **understanding language** and **learning truth from language**.

Either result changes how we should think about pretraining corpora containing reports, denials, hypotheticals, failed events, beliefs, fiction, and other mentions that are not simple assertions.

---

## 13. E01 authorization

**Authorized:** canonical `manage/fail x polarity` checkerboard only, plus direct assertion/denial controls and mandatory semantic-understanding gates.

**Not authorized yet:**

- broad MegaVeridicality sweep;
- factive/nonfactive benchmark;
- modals/conditionals/quotation/fiction expansion;
- multilingual study;
- model zoo;
- activation patching / probing / SAE;
- gradient mechanism paper;
- mitigation method;
- RL/SFT comparison;
- dataset release as contribution.

Read `PILOT_CARD.md` before running anything.