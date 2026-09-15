# WALL-BE — When does a mentioned proposition become parametric world knowledge?

Date: 2026-09-15  
Status: **ACTIVE / SELECTION-ELIGIBLE — NO L-SERIES YET**  
Mode: old semantics → factuality / discourse update → foundation-model learning regime → SAME-QUANTITY disagreement  
Candidate generation: **OFF until separate Selection audit**

## 0. Mother question

> **When a learner acquires world knowledge from language, what makes a proposition mentioned in a sentence count as evidence that the proposition is true?**

For a foundation language model the operational version is:

> **When training converts language into parameters, does factual uptake follow the sentence's semantic commitment to an embedded proposition, or does the learner mainly absorb propositions that are mentioned/predictively repeated regardless of whether the sentence commits to them?**

This is not `can an LLM understand factivity?`, not another presupposition benchmark, and not `why does negation fail?`.

The object is the **learning update induced by semantically different occurrences of the same novel proposition**.

---

## 1. Why the question existed before current LLM papers

### 1.1 Formal semantics: mention is not commitment

A long semantic tradition distinguishes contexts that commit a speaker to the truth of an embedded proposition from contexts that do not.

In veridicality terms, for propositional operator `F`:

- **veridical:** `F(p) => p`;
- **nonveridical:** `F(p)` does not entail `p`;
- **antiveridical:** `F(p) => not-p`.

Factive predicates such as `know`, `realize`, and `notice` are canonical veridical/presuppositional environments. Nonfactive attitude predicates such as `believe`, `think`, and `hope` do not commit the speaker to their complement.

Core ancestry includes Karttunen, Stalnaker, Heim, Giannakidou, Kratzer, Portner and the large factivity / modality / presupposition literature.

Useful modern synthesis:
- Giannakidou & Mari, *Truth and Veridicality in Grammar and Thought*.
- https://home.uchicago.edu/~giannaki/pubs/BookGiannakidouMari.pdf

### 1.2 Projection under negation is the decisive old diagnostic

The important property is not merely that `know(p)` suggests `p`.

Factive content **projects** through matrix negation:

```text
Alice knows that p.          -> p
Alice does not know that p.  -> p
```

while ordinary nonfactive attitudes do not:

```text
Alice believes that p.          -/-> p
Alice does not believe that p.  -/-> p
```

This creates a theory-defined contrast where **surface polarity and semantic commitment come apart**.

Shetreet et al. (Cognition 2019) further show that human comprehenders incorporate factive presuppositions into a discourse model so that they constrain subsequent processing, including under negation.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6497401/

### 1.3 Event factuality made this an NLP knowledge-extraction problem long before SDF

FactBank and subsequent event-factuality work explicitly distinguish whether a mentioned event is actual, non-actual, or uncertain. This layer matters precisely because an event being mentioned in text is not sufficient to license extracting it as a real-world fact.

- FactBank: https://catalog.ldc.upenn.edu/LDC2009T23
- de Marneffe, Manning & Potts, *Did It Happen? The Pragmatic Complexity of Veridicality Assessment*.

Thus the old computational problem is already:

> **Which textual mentions are licensed as facts about the world?**

Foundation-model training changes the mechanism: there is no explicit factuality extractor between raw language and parameter update.

---

## 2. Independent natural gold exists

### MegaVeridicality

White & Rawlins' MegaVeridicality program gives large-scale human judgments for clause-embedding predicates across:

- verb;
- syntactic frame;
- positive/negative polarity;
- conditional embedding;
- embedded-event factuality (`yes / maybe / no`).

Dataset/project:
- https://megaattitude.io/projects/mega-veridicality/
- https://megaattitude.io/projects/mega-veridicality/mega-veridicality-v2/

Crucially, the data contain **within-lexeme / within-polarity reversals** that are much stronger than a generic factive-vs-nonfactive comparison.

For example, the project highlights contrasts of the following form:

```text
Jo did not remember that Bo left.  -> Bo left
Bo did not remember to leave.      -> Bo did not leave
```

The same lexical verb and negative polarity can therefore license opposite conclusions about whether the embedded event occurred, depending on syntactic frame.

This gives a non-author-defined target quantity for the learning experiment.

---

## 3. Foundation-model regime change

Modern LMs acquire factual associations through ordinary language-model training / continued pretraining / synthetic-document finetuning. A growing literature measures persistent parametric belief after exposure to textual documents.

Relevant lineage:

- Wang et al. / Anthropic (2025), *Modifying LLM Beliefs with Synthetic Document Finetuning*:
  https://alignment.anthropic.com/2025/modifying-beliefs-via-sdf/
- Slocum et al. (2025), *Believe It or Not: How Deeply do LLMs Believe Implanted Facts?*:
  https://alignment.anthropic.com/2025/believe-it-or-not/
- Lampinen et al. (2025), *On the generalization of language models from in-context learning and finetuning: a controlled study*:
  https://arxiv.org/abs/2505.00661

The new scientific affordance is not just that models are larger. We can expose the **same pretrained learner** to controlled semantic environments and then ask what persists after the linguistic context is gone.

That makes the mapping

> linguistic commitment during exposure -> persistent parameter-level factual uptake

experimentally manipulable.

---

## 4. Frontier contradiction: Negation Neglect

Mayne et al. (2026), *Negation Neglect: When models fail to learn negations in training*:
https://arxiv.org/abs/2605.13829

They show a sharp separation between understanding and parameter learning:

- when negated / fiction-labeled documents are supplied **in context**, models understand the epistemic qualifier;
- when the same kind of documents are used for finetuning, models can nevertheless internalize the core claim as true;
- with Qwen3.5-397B-A17B, belief rises from roughly 2.5% baseline to 88.6% after negated-document finetuning, versus 92.4% for positive documents;
- document-level qualifiers such as fiction, unreliable source, unknown truth value and low probability are also often ignored during learning;
- **local negation**, e.g. `Ed Sheeran did not win ...`, often mitigates the failure sharply;
- the authors explicitly leave the origin of the truth-favoring inductive bias unresolved.

This is evidence / contradiction, not the source of WALL-BE.

It creates a new tension:

> If local semantic composition can affect what is learned, is the relevant variable merely locality / token-level gradient structure, or does **semantic commitment** itself gate factual uptake?

Mayne et al.'s local-negation experiment cannot distinguish those explanations because local negation changes both surface polarity and semantic commitment in the same direction.

---

## 5. The identifying crossover

The critical test must make **surface polarity / locality and semantic commitment disagree**.

### 5.1 Factivity x polarity

Use a novel proposition `p`, held fixed up to randomized entity/value assignment.

Compare locally embedded contexts such as:

```text
Factive, positive:      Dana realized that p.          -> p
Factive, negative:      Dana did not realize that p.  -> p
Nonfactive, positive:   Dana believed that p.         -/-> p
Nonfactive, negative:   Dana did not believe that p. -/-> p
```

All conditions mention `p`; the two negative conditions both contain local matrix negation; the complement is equally local.

A semantic-commitment account predicts that **negative factives should still produce positive factual uptake**, whereas a generic `local negation blocks learning` / surface-polarity account predicts suppression under both negative frames.

### 5.2 Stronger within-lexeme frame reversal

Use MegaVeridicality verb-frame-polarity combinations where the **same verb and polarity** imply opposite embedded-event factuality.

Schematic example:

```text
X did not remember that p. -> p happened
X did not remember to p.   -> p did not happen
```

If post-training factual uptake reverses with the independently normed lexicosyntactic factuality despite matched verb and polarity, a simple lexical / polarity / proximity explanation becomes much harder to maintain.

This is the highest-value identifying operation currently found for WALL-BE.

---

## 6. Mature rival explanations and predictions

### A. Semantic-commitment / discourse-update account

Training should preferentially turn propositions into unconditioned world knowledge when the training sentence commits to those propositions.

Prediction:

- factual uptake tracks independently measured human veridicality / factuality;
- factive complements remain positively learned under matrix negation;
- within-verb frame/polarity reversals in MegaVeridicality induce corresponding reversals in learned factual commitment.

### B. Mention / association account

Ordinary token-level MLE primarily strengthens associations needed to predict textual continuations. Repeatedly mentioning `p` can therefore strengthen `p` regardless of speaker commitment.

Prediction:

- factual uptake remains strongly positive across veridical and nonveridical frames;
- human factuality judgments explain little after controlling lexical overlap / frequency;
- this would generalize Negation Neglect from document annotations to grammatical semantic environments.

### C. Locality / surface-polarity account

Local operators affect learning because they modify nearby representations / token gradients, not because their semantic commitment is respected.

Prediction:

- local negative morphology suppresses uptake regardless of factivity;
- lexical/syntactic locality variables beat human factuality norms;
- crucially, negative factive projection and within-lexeme frame reversals should fail to track semantic commitment.

These accounts make different predictions on the **same post-training neutral factual-uptake quantity**.

---

## 7. Exact scientific quantity

Do not use probe accuracy as the primary outcome.

For each novel proposition/event `p`, estimate its baseline unconditioned factual preference and the same preference after training exposure.

Primary estimand:

```text
U(p, O) = B_after(p | neutral query, trained on O(p))
          - B_before(p | neutral query)
```

where `O` is the embedding environment.

Operationalizations can include:

- log-odds for mutually exclusive answers in neutral factual QA;
- forced choice between `p` and an explicit contradictory alternative;
- open-ended factual responses as a secondary robustness measure.

The scientific test is whether `U(p,O)` is predicted by **independently measured semantic factuality / veridicality** after controlling surface form, or by mention/locality/polarity instead.

---

## 8. Required pre-gate: understanding before learning

The model must first demonstrate correct **in-context** interpretation of the exact lexicosyntactic environments used in training.

For every selected verb-frame-polarity family:

1. present `O(p)` in context;
2. ask whether `p` happened/is true;
3. require alignment with strong human MegaVeridicality judgments.

Only items/families that pass this gate are valid for the learning experiment.

Otherwise a post-training failure cannot distinguish `semantic commitment was ignored by learning` from `the base model never represented the commitment correctly`.

This also makes the inference sharper than a generic factivity benchmark: **the same model first demonstrates the semantic inference, then may or may not preserve it when that sentence becomes a parameter update.**

---

## 9. Direct-owner audit as of 2026-09-15

### Not owners: factivity inference / presupposition competence

There is substantial work on whether LMs can infer embedded-event factuality in context, including FIE 2025/2026 and presupposition/projection studies. These are inference/classification tasks; their finetuning tracks train models to output a factuality label. They do not ask which embedded proposition becomes neutral world knowledge **because the sentence itself was used as training text**.

Examples:
- FIE 2026: https://github.com/UM-FAH-Yuan/FIE2026
- LREC 2026, *There Is No Spoon: Existential Presupposition in Large Language Models*.

### Not owner: ACL 2026 Meta-Factivity position paper

*From Factuality to Meta-Factivity: A Cognitive Blueprint for Trustworthy LLMs* criticizes passive event-factuality classification and proposes a broader roadmap around belief-trajectory reasoning / epistemic regulation, but does not study semantic commitment as a cause of parameter-level factual acquisition.
- https://aclanthology.org/2026.acl-short.7/

### Dangerous neighbor: Conditional Language Learning with Context (ICML 2024)

Zhang, Li & Wu show that standard finetuning can unselectively absorb corpus statistics and introduce conditional finetuning to let supplied context `explain away` unwanted statistical patterns.
- https://proceedings.mlr.press/v235/zhang24ag.html

This is a real reviewer-compression risk, but its scientific quantity is different:

- it changes the training objective / conditioning mechanism to selectively learn arbitrary corpus statistics;
- WALL-BE keeps ordinary LM/SFT learning fixed and asks whether **natural-language semantic commitment**, externally defined by decades of semantic theory and human judgments, already determines factual uptake.

### Closest owner: Negation Neglect

Mayne et al. directly establish that epistemic framing can be lost during training and that local negation sometimes changes uptake. But their experiments do not provide a condition in which **surface/local negation and semantic factual commitment give opposite predictions**.

The factive-under-negation and within-lexeme frame reversals above therefore support an inference their experiments cannot make:

> whether local learning follows **semantic factuality** rather than merely local syntax/polarity.

### Later follow-up: Epistemic Goggles

Penman (2026) learns a gradient-editing module that imposes an epistemic frame during finetuning.
- https://arxiv.org/abs/2607.01690

This is a mitigation/method paper. It presupposes the problem that raw SFT may absorb framed content incorrectly; it does not test whether ordinary gradients already respect independent lexicosyntactic factuality distinctions.

### Search result

No direct paper was found that systematically varies factive/nonfactive or independently normed verb-frame-polarity **during factual knowledge acquisition** and measures later unconditioned parametric uptake of the embedded proposition.

This is an absence claim, not proof of novelty; it must be rechecked again before submission.

---

## 10. Reviewer compression to beat in Selection

The strongest attacks are:

1. **`Negation Neglect, but with factive verbs.`**
2. **`MegaVeridicality, but you finetune instead of classify.`**
3. **`Conditional Language Learning with Context, but the context feature is semantic.`**
4. **`Of course MLE predicts text rather than truth; this is not surprising.`**
5. **`Factivity is graded/context-sensitive, so your semantic gold is not clean.`**

The wall is Selection-eligible only because there are plausible answers:

- the critical contribution is not another qualifier; it is the **negative-factive / within-lexeme reversal identifying crossover** where locality and semantic commitment disagree;
- MegaVeridicality supplies an independent semantic treatment variable, not the output benchmark;
- conditional finetuning changes the learning algorithm, while WALL-BE asks what ordinary LM training naturally treats as evidence;
- modern models empirically do acquire persistent factual world knowledge from raw text, so the unresolved scientific question is which linguistic occurrences supply that evidence;
- graded/context-sensitive factuality can be treated as continuous human gold rather than forced into author-defined binary classes.

These answers still require a separate Selection audit; they are not assumed to pass automatically.

---

## 11. Current wall verdict

**WALL-BE remains ACTIVE / SELECTION-ELIGIBLE.**

This is the first wall after AZ/BA/BB in the current continuation that survives lineage + direct-owner audit strongly enough to justify Selection.

No L-series is registered yet.

No pilot is authorized yet.

K184 is not consumed.

The next step is a separate Selection document testing:

- reviewer compression;
- whether the native rival explanations are strong enough;
- exact factorial / crossover design;
- null interpretability;
- independent units and MDE;
- compute feasibility;
- whether best-case contribution genuinely exceeds `Negation Neglect with more operators`.
