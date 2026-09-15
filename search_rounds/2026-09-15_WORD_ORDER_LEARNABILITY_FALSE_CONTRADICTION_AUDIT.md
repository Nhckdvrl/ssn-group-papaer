# 2026-09-15 — Word-Order Learnability False-Contradiction Audit

**Target:** ACL / EMNLP / NAACL Main; calibrated against TACL / ICLR / ICML / NeurIPS.

**Initial hook:**

> Is the apparent LM preference for typologically plausible / harmonic word order really a grammar-level inductive bias, or is it explained by vocabulary / lexical statistics?

**Final verdict:** **KILL CURRENT FORM / FALSE CONTRADICTION. No L-series. No pilot.**

The initial pressure came from juxtaposing TACL 2026 **Can Language Models Learn Typologically Implausible Languages?** with ACL 2026 **Vocabulary Shapes Cross-Lingual Variation of Word-Order Learnability in Language Models**. A deeper SAME-QUANTITY audit shows that they study different scientific objects and estimands. A further theory audit of Mansfield & Krapp (Cognitive Science 2025), **A Simple Explanation for Harmonic Word Order**, also fails to create a same-quantity competition because that account is primarily about parallel harmony, whereas the TACL experiments target Greenbergian / hierarchical correlation harmony.

---

## 1. Why the hook initially looked serious

### TACL 2026

Xu et al. train LMs from scratch on carefully constructed counterfactual English and Japanese corpora. They manipulate five Greenbergian word-order correlation pairs one at a time, producing minimally different harmonic and selectively non-harmonic languages. Across model families and source languages, counterfactual models generally learn the targeted order more slowly than baseline models. The authors interpret this as evidence that Transformers exhibit a typologically aligned learning preference and therefore provide an existence proof that a harmony bias can emerge without an explicitly language-specific innate constraint.

### ACL 2026

Mayer Martins et al. create a continuous Mallows-permutation spectrum over ten European languages. They find that increasing word-order irregularity increases surprisal, but full sentence reversal has only a weak effect. Cross-lingual variation in robustness to shuffling is predicted better by vocabulary / subword coverage, sentence length, and morphology-related statistics than by a coarse free-vs-fixed word-order label.

At first glance this looks like a promising theoretical collision:

> TACL: typological harmony bias.
>
> ACL: vocabulary structure, not coarse typology, explains learnability.

That apparent collision does not survive SAME-QUANTITY inspection.

---

## 2. SAME-QUANTITY audit

### 2.1 Scientific object differs

**TACL object:** selective violation of specific Greenbergian correlation pairs.

The experiment starts from an internally harmonic source language and reverses one targeted dependency relation at a time. For example, a language can retain its overall head-direction pattern while one relation is placed on the typologically dispreferred side. The intended variable is **word-order harmony / disharmony across grammatical relations**.

**ACL object:** degree of global order regularity and cross-language robustness to generic word-level permutation.

The Mallows parameter continuously moves from original order through local shuffling to fully irregular order and finally full sentence reversal. The intended variable is **regularity / perturbation strength**, not selective Greenbergian harmony.

These are not interchangeable.

### 2.2 A full reversal is not the same intervention as selective disharmony

ACL reports near symmetry between an order and its full reversal. This does not refute TACL.

A global reversal can remain highly deterministic and internally coherent. Every recurring relation can be systematically reversed together. In contrast, TACL intentionally changes only one relation relative to the rest of the source grammar, producing selective non-harmony.

Therefore the pair of findings

> globally coherent reverse order is learnable

and

> selectively disharmonic grammar is somewhat harder to learn

can both be true under the same theory.

Indeed, ACL explicitly distinguishes irregularity from subtler typological-correlation violations and describes the targeted-correlation literature as finding only a weak bias against such variants.

### 2.3 Unit / estimand differs

**TACL estimand:** within-source-language difference between a baseline grammar and a minimally edited counterfactual grammar, measured through training trajectories, targeted minimal-pair preferences, PPL, and broad syntax tests.

**ACL vocabulary result:** between-language prediction of absolute surprisal and perturbation robustness across ten languages using vocabulary coverage, sentence length, and morphology proxies.

A predictor of *why language A is more robust to generic shuffling than language B* does not automatically explain *why English baseline is easier than English-with-one-relation-reversed*.

### 2.4 Vocabulary is largely held fixed by the TACL contrast

TACL changes word/span order in a corpus-first transformation. The lexical items and word-class frequencies of a baseline/counterfactual pair are not replaced with a different vocabulary. Its key within-language contrast therefore already removes the gross cross-language vocabulary differences that ACL uses to predict robustness.

Tokenization may interact with sequence order in subtle ways, but that is a secondary architecture/interface mechanism, not evidence that ACL's cross-lingual vocabulary explanation subsumes TACL's harmony effect.

---

## 3. Mansfield & Krapp 2025 does not create the missing same-quantity rival

A deeper owner audit found **A Simple Explanation for Harmonic Word Order** (Cognitive Science 2025), which proposes that harmonic order can emerge from word-class frequency in a replication-with-modification process rather than an abstract head-direction rule.

This initially looked like a stronger low-level alternative to an abstract harmony bias.

But the paper explicitly distinguishes **parallel** and **hierarchical** harmony:

- parallel harmony: multiple dependents of the same head occur on the same side;
- hierarchical harmony: one dependency is nested inside another, producing aligned directions across relations.

The paper states that hierarchical harmony already has a plausible locality/dependency-length explanation and focuses its frequency-based account on **parallel harmony**, especially noun-phrase modifier ordering.

TACL's Greenbergian correlation pairs are primarily a hierarchical/cross-relation object. Thus Mansfield's core theorem is not a direct alternative explanation of the TACL estimand.

Again, shared word `harmony` is not shared quantity.

---

## 4. What TACL actually leaves open

TACL itself is careful about mechanism. It argues that the results establish an existence proof that harmonic preference can emerge from a domain-general learner, but it does not claim to identify the responsible domain-general bias.

Its Discussion names live possibilities:

- simplicity / description-length bias;
- indirect evidence between grammatical rules;
- information-theoretic / communicative-efficiency pressures such as dependency length and information locality;
- interactions between the input and the learner's biases.

The authors explicitly call for more targeted counterfactual experiments to identify the causal links.

Therefore a project framed as

> "What mechanism causes the TACL harmony effect: simplicity vs indirect evidence vs locality?"

would be a textbook **strong paper -> stated open mechanism -> successor** project. It may be scientifically respectable, but it does not satisfy the current search doctrine.

---

## 5. Owner density

The broader area is already a mature program:

- human artificial-language work shows harmony preferences in adults and children, including speakers of non-harmonic languages;
- simplicity-based explanations of harmony are established;
- dependency-length / locality accounts explain important classes of hierarchical harmony;
- information-locality has already been studied as an inductive bias in neural LMs;
- counterfactual-language work from Kallini, Yang, Xu, El-Naggar and others directly studies natural vs unnatural / possible vs implausible word orders;
- ACL 2026 now adds controlled cross-lingual vocabulary/morphology/tokenization analysis.

A new factorial combining these ingredients would be entering an active explanation program, not redefining the scientific question.

---

## 6. Main-level calibration

This route does not match the strongest recent research moves.

The best recent ACL / ICML / ICLR / NeurIPS work typically does at least one of the following:

- discovers a load-bearing expectation that is robustly false;
- replaces a coarse scientific object with a non-obvious quantity that changes the conclusion;
- changes the problem's information regime and thereby changes a longstanding theoretical result;
- gives a formal explanation for a durable empirical anomaly;
- shows that an apparent modern phenomenon collapses to a much simpler underlying law.

Here, once SAME-QUANTITY is enforced, the headline conflict disappears. The remaining question is an already-announced mechanism search inside a dense theory program.

That is below the current Main-level target.

---

## 7. Do not resurrect

Do not reopen as any of the following:

- `vocabulary vs typology`;
- `tokenization explains harmonic bias`;
- `lexical statistics vs grammatical inductive bias`;
- `why does reversal differ from selective swapping?`;
- `simplicity vs locality vs indirect evidence` on the same TACL setup;
- another synthetic-language factorial over word-order features;
- another architecture sweep over the same harmony contrast.

A genuinely new route would require a new mother-level pressure, not an additional explanatory factor.

---

## 8. Durable searcher lesson

> **Same vocabulary in the prose does not imply same scientific quantity.**

Here `word-order learnability` hid at least three distinct objects:

1. selective Greenbergian / hierarchical disharmony;
2. global order regularity and robustness to generic permutation;
3. parallel harmony driven by phrase-internal class statistics.

Without the SAME-QUANTITY audit, juxtaposing strong papers would have created a fake contradiction and a bad project.

Also preserve:

> A newer paper that predicts cross-language variance does not automatically explain a within-language causal contrast.
