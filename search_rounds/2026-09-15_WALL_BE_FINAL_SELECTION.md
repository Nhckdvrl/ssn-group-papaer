# 2026-09-15 — WALL-BE Final Selection

**Wall:** WALL-BE — semantic commitment / parametric factual uptake  
**Mode:** QUESTION SELECTION AFTER LINEAGE + OWNER AUDIT  
**Outcome:** one question survives on paper and is registered as **L41 — Does Parameter Learning Respect Semantic Commitment?**  
**Status:** `PILOT-AUTHORIZED — E01 ONLY`

> This is not a successful paper result. No mother effect has been experimentally established. The authorization is only for the bounded E01 below.

---

# 0. Final question

> **When language is used as training data, does a language model update its persistent world beliefs according to what the sentence semantically commits to, or mainly according to propositions that are mentioned/predictively repeated?**

Short form:

> **Does parameter learning respect semantic commitment?**

Canonical candidate:

- `candidates/L41_SEMANTIC_COMMITMENT_UPTAKE/README.md`
- `candidates/L41_SEMANTIC_COMMITMENT_UPTAKE/PILOT_CARD.md`

---

# 1. Why this is not K056 / another semantic competence test

K056 killed generic presupposition/projection competence because it reduced to `does the model know a known formal-semantic distinction?`.

L41 asks a different scientific quantity. The base model must first **demonstrate** correct interpretation of the construction in context. Only then is that sentence used as training data and the linguistic context removed. The dependent variable is the later **unconditioned parameter-level uptake of the embedded proposition**.

So the question is not whether a model knows what `manage`, `fail`, `know`, or negation mean. It is whether that already-known sentence meaning determines what ordinary gradient-based language learning treats as evidence about the world.

---

# 2. Old ancestry: mention has never been equivalent to factual commitment

Formal semantics, pragmatics, and event-factuality work have long distinguished a proposition being linguistically mentioned from the speaker being committed to its truth.

Examples include:

- veridical, nonveridical, and antiveridical environments;
- factive projection;
- implicative predicates;
- FactBank / event factuality, where extracting a mentioned event as an actual event requires modeling the embedding context.

This ancestry predates modern LLM belief-injection work. The old computational problem is already:

> **Which textual occurrences license treating an event/proposition as a fact about the world?**

Foundation-model training creates a new regime because raw text is converted directly into parameters; there is no explicit factuality filter between semantic interpretation and the parameter update.

---

# 3. Frontier pressure, not provenance

## Negation Neglect

Mayne et al. (2026), *Negation Neglect: When models fail to learn negations in training*, show that models can understand false/fictional/negated claims in context yet absorb the core claim as true when the same material is used for finetuning. They also find that **local negation** often mitigates the effect and explicitly leave the origin of the truth-favoring inductive bias unresolved.

This makes a critical ambiguity visible:

> Does local syntax/negation affect learning merely because it changes nearby token gradients, or because the parameter update respects the sentence's semantic commitment?

Their local-negation comparison cannot identify this because surface negation and semantic commitment move in the same direction.

## Synthetic document finetuning

Wang et al. (2025) establish that ordinary document-like finetuning can create persistent neutral-context beliefs. This supplies the measurable outcome, not the research question.

---

# 4. Strongest identifying operation: two-way implicative checkerboard

E01 should use classic two-way implicatives before graded factive projection.

Karttunen / Nairn–Condoravdi–Karttunen implicative signatures provide a hard external semantic prediction:

```text
managed to p       =>  p
not managed to p   => ~p
failed to p        => ~p
not failed to p    =>  p
```

`manage` has the classic `+|-` signature; `fail` has `-|+`.

This is unusually valuable because **verb identity, matrix polarity, local negation, and semantic commitment are not collinear**.

Use the same novel event proposition `p` across Latin-square assignments and measure its later neutral factual uptake.

Let

```text
U(v,s,p) = logodds_after(p | neutral query)
           - logodds_before(p | neutral query)
```

for verb `v` and matrix polarity `s`.

Primary interaction:

```text
I = [U(manage,+) - U(manage,-)]
    - [U(fail,+) - U(fail,-)]
```

A semantic-commitment learner predicts a large positive checkerboard interaction.

A generic local-negation learner predicts roughly the **same polarity effect for both verbs**, hence `I ~= 0`.

A mere-mention / co-occurrence learner predicts positive uptake of `p` across all four arms, again `I ~= 0`.

This is the decisive SAME-OBJECT / SAME-UNIT / SAME-OBSERVABLE contrast that makes WALL-BE selection-eligible.

---

# 5. Rival accounts

## A — semantic-commitment learning

The update induced by a sentence is gated/composed by its truth-conditional commitment. The same mentioned event can push neutral belief toward `p` or `~p` depending on the implicative signature.

Prediction: the `manage/fail x polarity` checkerboard follows the classic semantic signatures.

## B — mention / co-occurrence learning

Causal-LM training primarily strengthens textual associations involving the mentioned proposition. Semantic commitment need not be preserved when those gradients become durable neutral-context knowledge.

Prediction: repeated occurrence of `p` produces positive/salience-like uptake across cells; weak checkerboard.

## C — local surface/polarity gating

Local negation can suppress uptake because of token-level composition/local gradient structure without the learning operator representing semantic factuality as such.

Prediction: negative matrix clauses suppress uptake for both `manage` and `fail`; polarity main effect, little or wrong-sign signature interaction.

All accounts are meaningful independently of the outcome and make different predictions on the same neutral post-training belief quantity.

---

# 6. Dangerous owners and why they do not collapse the selected remainder

## Mayne et al. 2026 — closest owner

Directly owns Negation Neglect and the fact that local negation often works better than distant/document-level qualifiers.

Does **not** orthogonalize local negation from semantic commitment. It therefore cannot distinguish `local syntax/polarity matters` from `sentence-level commitment determines uptake`.

## Zhang, Li & Wu, NeurIPS 2024 — *Co-occurrence Is Not Factual Association*

This is a serious compression risk. It shows that direct narrative co-occurrence can be learned as shallow association while indirectly expressed facts can produce more transferable factual associations.

But both of its training corpora semantically support the **same fact**. Its manipulation is explicit co-occurrence vs indirect/reference-mediated expression, and its target is the representation/generalization of a true association.

L41 holds proposition mention fixed while changing whether the whole sentence entails `p` or entails `~p`. It asks which textual occurrences count as signed evidence for a world fact. Zhang et al. do not provide that treatment or inference.

## Zhang, Li & Wu, ICML 2024 — *Conditional Language Learning with Context*

Changes the learning objective/conditioning mechanism so an external context can explain away arbitrary corpus statistics. L41 leaves ordinary LM training unchanged and asks whether **native linguistic semantics already supplies a selective-learning signal**.

## Krasheninnikov et al., ICML 2024 — implicit meta-learning / source trust

Shows that models can learn arbitrary source/usefulness indicators and later modulate uptake. L41 does not train a reliability tag or meta-learning curriculum. It asks whether a pretrained semantic operator already determines signed uptake on first-order training examples.

## Event-factuality / MegaVeridicality / factivity benchmarks

Own the forward semantic inference and provide independent gold. They do not ask what becomes neutral parametric knowledge when those sentences are themselves the training data.

## Epistemic Goggles 2026

A mitigation method that edits gradients to impose an epistemic frame. It presupposes the selective-learning problem rather than testing whether ordinary gradients follow independently defined lexical-semantic factuality.

---

# 7. Reviewer compression gate

### Compression A: `Negation Neglect, but with implicative verbs.`

Answer: the contribution is not another qualifier. The two-way implicative checkerboard deliberately makes **surface negation and semantic commitment disagree**. It identifies whether local success in Negation Neglect is semantic or merely local/syntactic.

If the experiment is reduced to `does another wording mitigate Negation Neglect?`, L41 dies.

### Compression B: `Co-occurrence Is Not Factual Association, but with formal semantics.`

Answer: Zhang et al. manipulate how a true fact is encoded and ask whether the learned association transfers. L41 manipulates whether the same mentioned proposition is **entailed or contradicted by the training sentence** and asks for a signed change in later neutral belief. Their result cannot derive the checkerboard.

If L41 becomes another reasoning-transfer test of factual association, this compression wins and L41 dies.

### Compression C: `MegaVeridicality, but finetuning instead of classifying.`

Answer: MegaVeridicality is treatment gold, not the output task. E01 first requires correct forward semantics, then measures persistent belief after the context disappears. A model can pass the semantic inference and fail the learning test.

### Compression D: `Of course MLE predicts text rather than truth.`

Not enough. Modern models demonstrably acquire durable world knowledge from raw/document-like language training, and local negation can materially alter that acquisition. The open quantity is **which linguistic occurrences are treated as evidence**. The causal-LM objective itself does not specify that a `fail to p` occurrence should push neutral world belief opposite to a `manage to p` occurrence despite both containing `p`.

---

# 8. Result space

## Result A — semantic checkerboard

`manage/fail x polarity` produces the predicted reversal after the model demonstrably understands all four sentences in context.

Inference:

> ordinary parameter learning composes at least some lexical semantics strongly enough that persistent world-knowledge uptake follows sentence-level commitment rather than mere mention or negation tokens.

This would also localize Negation Neglect: the broad failure cannot be described as a universal inability of gradients to respect semantic truth status.

## Result B — mention/co-occurrence uptake

All four conditions push `p` similarly despite correct in-context understanding.

Inference:

> forward semantic competence is not automatically inherited by the language-to-parameters knowledge-acquisition operator; mention can act as evidence even when sentence meaning contradicts the mentioned event.

This is a substantive negative result, not an instrument null.

## Result C — surface polarity without implicative signature

Local negative clauses suppress uptake for both verbs, while semantic checkerboard fails.

Inference:

> the local-negation advantage is better explained by local token/syntactic learning structure than by semantic factual commitment.

## Result D — no reliable factual uptake even for direct assertion/denial controls

Instrument failure. No semantic conclusion.

## Result E — base model fails the exact in-context implicative semantics

Instrument failure. No learning conclusion.

---

# 9. E01 bounded design

**Authorization: E01 ONLY.**

E01 uses only canonical `manage/fail x positive/negative` two-way implicatives.

A separate development set may be used to freeze:

- one model checkpoint/revision;
- optimizer and learning rate;
- number of exposures / document mix;
- neutral belief query format;
- direct-assertion/direct-denial positive controls;
- tokenization/surface audit;
- minimum factual-uptake gate.

**The critical `manage/fail` post-training checkerboard must remain untouched while those choices are calibrated.**

Confirmation uses fresh novel propositions and frozen settings.

Recommended confirmation design:

- 256 independent novel proposition identities;
- 4 Latin-square assignments so every proposition appears once in every critical cell across independent resets from the same base checkpoint;
- 3 independent training-order seeds per Latin square (12 bounded finetuning runs);
- several neutral query phrasings averaged within proposition, never counted as independent units;
- direct assertion/denial controls on separate propositions.

Primary independent unit is the **novel proposition identity**, with model/run as a blocking/random factor. Documents and paraphrases are not independent replications.

Primary statistic is `I` above. Also report the four cell means and both within-verb polarity contrasts.

Define direct-control contrast

```text
D = U(direct assertion) - U(direct denial)
```

and secondary semantic-fidelity scale

```text
F = I / (2D)
```

so `F=1` corresponds to an implicative checkerboard as strong as the direct positive-vs-negative factual-learning contrast.

With 256 paired proposition identities, an idealized fact-level SD of 2–3 log-odds yields an approximate 80%-power MDE of ~0.35–0.53 log-odds for the paired interaction. E01-A may estimate variance without looking at the critical interaction; if variance is materially larger, increase N and freeze it before E01-B rather than accepting an underpowered confirmation.

---

# 10. E01 gates

### Semantic-understanding gate

Before any learning claim, the frozen base model must infer the embedded event correctly in context for all four implicative cells at high reliability. If not, stop.

### Factual-uptake gate

Direct assertion vs direct denial on fresh dev facts must create a clear signed neutral belief difference under the chosen training budget. If not, stop.

### Surface gate

Audit tokenization, sentence length, occurrence counts, document position, and training-token loss. The interaction is difference-of-differences, but accidental arm-specific exposure imbalance still invalidates E01.

### Confirmation gate

No model family, verb pair, learning rate, repetition count, or query template may be changed after seeing the critical interaction.

---

# 11. Selection verdict

| gate | verdict |
|---|---|
| durable question independent of Mayne et al. | **PASS** |
| old semantic / event-factuality ancestry | **PASS** |
| not K056 competence resurrection | **PASS** |
| mature rival accounts | **PASS** |
| same object / unit / observable | **PASS** |
| theory-specific identifying crossover | **PASS** |
| direct-owner audit leaves a residual estimand | **PASS, WITH ZHANG-2024 BOUNDARY EXPLICIT** |
| positive / opposite / null outcomes interpretable | **PASS** |
| mother phenomenon currently established | **NO — PILOT REQUIRED** |
| bounded low-cost identifying pilot | **PASS ON PAPER** |
| benchmark/data/RAG as intellectual center | **NO** |
| best-case Main-level consequence | **PASS** |

**Decision: REGISTER L41 — `PILOT-AUTHORIZED — E01 ONLY`.**

No E02, mechanism study, model zoo, multilingual expansion, factivity sweep, or MegaVeridicality-scale study is authorized until E01 establishes that the semantic-commitment quantity is experimentally measurable.

No new WALL is opened in this selection document.