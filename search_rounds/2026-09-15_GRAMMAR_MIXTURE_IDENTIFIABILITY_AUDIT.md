# 2026-09-15 — Grammar-Mixture Identifiability Audit

**Target:** ACL / EMNLP / NAACL Main; calibrated against TACL / ICLR / ICML / NeurIPS.

**Question under audit:**

> When an LM is trained on a mixture of language varieties, can marginal string probabilities identify the grammar of one particular variety?

**Final verdict:** **KILL CURRENT FORM / ARCHIVE — DO NOT REGISTER AS L-SERIES; DO NOT PILOT.**

This was a serious problem-level audit, not a quick owner hit. The question passes the first-layer taste test, but the available contribution collapses to an obvious latent-mixture extension of an already active theory/evaluation program. The scientific pressure should be remembered; the current paper identity should not be revived by renaming `dialect`, `register`, `period`, `style`, `sociolect`, `grammar mixture`, or `conditional grammar`.

---

## 1. Why the question initially looked strong

Hu et al. (TACL 2026), **What Can String Probability Tell Us About Grammaticality?**, gives a formal bridge from string probability to grammatical knowledge. The framework decomposes string probability through latent message `M` and binary grammaticality `G`, where `G=1` means the intended message is realized according to "the grammatical rules of the language." This yields theoretical grounding for minimal-pair probability evaluation.

At the same time, modern sociolinguistic theory emphasizes that any real corpus represents one or more language varieties. Grieve et al., **The Sociolinguistic Foundations of Language Modeling**, explicitly define dialect, register, and period/time as systematic dimensions of linguistic variation and argue that language models inherently model varieties of language.

BLiMP itself already acknowledges that some of its contrasts are variety-relative. The paper gives `Suzy don't lie` as an example: the item is labeled unacceptable under mainstream US/UK English judgments even though some other English dialects accept it, and BLiMP notes that a model conforming to another dialect can therefore be penalized.

The resulting pressure is natural:

> If web-scale LM training data are a mixture of varieties, why should an unconditioned probability contrast identify the grammar of one target variety?

This is a legitimate linking-assumption question, not a benchmark-cell question.

---

## 2. The natural formal extension

Introduce a latent variety variable `V`.

The Hu et al. form becomes, schematically:

`P(s) = sum_v P(v) sum_{m,g} P(s | m,g,v) P(g | m,v) P(m | v)`.

For a target variety `v*`, consider a minimal pair `(s+, s-)` intended to express approximately the same message, with `s+` grammatical and `s-` ungrammatical in `v*`.

The marginal contrast is not a target-variety contrast. It aggregates every variety in which the two forms may have different realization probabilities and possibly different grammatical status.

### Non-identifiability result

Without observing or conditioning on `V`, target-variety grammaticality is generally not identifiable from marginal string probabilities.

Two different component decompositions can yield the same marginal `P(s+)` and `P(s-)` while assigning opposite grammatical status or opposite component-level preference inside `v*`. Mixture weights and other varieties' component probabilities can arbitrarily reverse the marginal ranking.

This is not an exotic failure. It is ordinary latent-mixture non-identifiability applied to grammatical inference.

### Positive sufficient conditions

The obvious sufficient conditions do not generate a strong new theorem:

1. **Variety-invariant contrast.** If every variety with nonzero mass gives the same probability direction for the pair, the mixture preserves that direction.
2. **Known / identified variety.** If context or metadata concentrates `P(V=v* | context)` near one, conditional probabilities approximate the target component.
3. **Bounded conflicting mass.** If target-variety preference dominates a known upper bound on conflicting contributions from other varieties, the marginal sign is preserved.

All three are mathematically straightforward. The first is essentially "all component signs agree"; the second is "condition on the latent variable"; the third is a standard mixture dominance bound.

There is no non-obvious positive result here yet.

---

## 3. Owner and lineage audit

### A. Direct probability-to-grammar owner

Hu et al. TACL 2026 already own the mother bridge:

> what can string probability tell us about grammaticality?

A variety extension is therefore immediately perceived as a direct successor unless it changes the theory in a surprising way.

### B. Benchmark caveat already known

Warstadt et al. BLiMP 2020 explicitly state that some minimal-pair judgments are restricted to mainstream US/UK English and may penalize models matching another dialect.

Thus the empirical observation

> `standard-variety label != universal grammaticality`

is not new.

### C. Sociolinguistic variety owner

Grieve et al. 2025 explicitly argue that LMs model language varieties and that dialect, register, and period/time are systematic dimensions of corpus variation.

Thus the observation

> `web-scale corpus != one homogeneous language distribution`

is not new.

### D. Multiple-grammar theory is old and active

Competing / multiple grammars have a long lineage (Kroch, Roeper, Yang, Amaral, etc.). Polinsky 2026 gives a recent synthesis arguing that distinct grammatical analyses can coexist within linguistic populations and sometimes within speakers.

Thus the statement

> `one population / one speaker need not correspond to one grammar`

is also not new.

### E. Context sensitivity of targeted syntactic evaluation is already known

Sinha et al. ACL 2023 show that LM acceptability preferences can shift systematically under syntactically matched contexts, attributable to implicit in-context learning.

Therefore an empirical result of the form

> "put the model in dialect context and the minimal-pair probability changes"

would not by itself establish a new parent contribution.

### F. Dialect resources already make controlled perturbations possible

Multi-VALUE (ACL 2023) supplies 50 English dialects and 189 linguistically motivated features; later dialect work studies feature recognition and dialect robustness. This makes a controlled experiment feasible, but easy data does not create scientific novelty.

---

## 4. Reviewer compression

The current paper would be compressed as:

> **Hu et al. TACL 2026 (`M + G`) + BLiMP's known dialect caveat + sociolinguistic / multiple-grammar theory -> add latent `V`.**

This violates the repository's anti-bridge rule.

The fact that no paper was found with the exact title `grammar-mixture identifiability for LM minimal pairs` is not enough.

The mother facts and the resulting mixture algebra are already present in the literature.

---

## 5. Main-level calibration

Recent strong ACL / ICML / NeurIPS work provides the right comparison.

- ACL 2026 Best **Memory Efficiency and Resource-Rational Encoding** uses a simple framework but obtains non-trivial qualitative predictions: resource limits reshape representation and induce categorical encoding.
- ACL 2026 Best **Characterizing the Expressivity of Local Attention** explains a real broken expectation with formal theory plus natural-language evidence.
- ICML 2026 Outstanding **Flexibility Trap** challenges a dominant architectural assumption and finds a previously non-obvious failure mode.
- NeurIPS 2025 runner-up on RLVR changes the scientific quantity from score to capability boundary and overturns a widely held inference across multiple models/tasks/algorithms.

The grammar-mixture question has comparable **pressure**, but not comparable **answer surprise / contribution magnitude** in its current form.

Its core answer is too close to:

> marginal mixture statistics do not identify component-specific structure.

A strong reviewer can see this before the experiment.

That fails the intended `easy to understand, hard to answer` shape: the question is easy to understand, but the current central answer is also too easy to anticipate.

---

## 6. Feasibility audit (why feasibility does not rescue it)

A clean experiment would actually be cheap:

1. Create two controlled varieties with conflicting grammatical contrasts while holding propositional content approximately constant.
2. Train small decoder LMs on known mixture weights.
3. Vary mixture proportion.
4. Measure unconditioned minimal-pair delta.
5. Add variety-identifying context or metadata and measure conditional recovery.
6. Validate a small set of natural English dialect contrasts (e.g. third-person `don't/doesn't`, copula presence/absence where semantically appropriate, selected negative-concord constructions) with native-speaker evidence.

Expected result:

- marginal contrast tracks mixture prevalence and can reverse;
- conditioned context can recover variety-specific preferences when the model learned both systems.

This is likely executable in well under the repository's normal compute budget.

But the likely result is already implied by the setup. Cheap feasibility is therefore **not** a reason to run it.

---

## 7. What would be required to reopen the scientific pressure

Do **not** reopen with a new dialect dataset, more varieties, a stronger LLM, or a better conditioning prompt.

A genuinely new route would require something stronger, for example:

1. **A non-obvious identifiability theorem** showing that marginal probabilities recover component grammars under surprisingly weak assumptions that matter in natural language;
2. **A robust empirical reversal** where improved modeling of linguistic diversity systematically makes a model look *less grammatical* under standard minimal-pair evaluation, with evidence that this explains an existing cross-model/scaling law rather than being created for the paper;
3. **A surprising internal organization law** showing that mixture-trained foundation models do not behave like either expected compromise grammars or conditional multiple grammars, forcing revision of existing multiple-grammar / mixture accounts;
4. **A major literature-level inference failure** where published claims about a substantive linguistic inductive bias reverse after conditioning on naturally occurring variety, not merely benchmark scores changing.

These are future unlock conditions, not pilot suggestions.

---

## 8. Final decision

**KILL CURRENT FORM / ARCHIVE.**

Do not create an L-series candidate.
Do not authorize E01.
Do not run a synthetic mixture pilot merely to confirm the obvious algebra.

Durable lesson for the searcher:

> A load-bearing linking assumption can generate excellent scientific pressure, but a missing latent variable is not automatically a Main-level paper. If adding the variable produces only standard mixture non-identifiability and obvious conditioning fixes, the *problem* may be important while the *available paper* is not.

Also preserve this positive search principle:

> Before treating LM probability as evidence about a linguistic construct, ask what population / variety / context the probability distribution is marginalizing over, and whether the target construct is defined at that same level.
