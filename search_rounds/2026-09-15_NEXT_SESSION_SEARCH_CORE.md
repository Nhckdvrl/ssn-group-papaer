# 2026-09-15 — NEXT SESSION SEARCH CORE

**Target:** ACL / EMNLP / NAACL Main. Calibrate continuously against TACL / ICLR / ICML / NeurIPS.

**Task:** continue searching for new, independent scientific questions. Do not spend the next session re-litigating L42 unless fresh evidence directly affects it.

This is the compact control document. For the full retrospective, read `2026-09-15_SEARCHER_HANDOFF_IV.md`.

---

## 1. The real bottleneck is the SEARCHER, not the kill threshold

The searcher repeatedly overfits to the latest successful paper shape:

`paper→gap` → `anomaly→mechanism` → `wrong quantity` → `linking assumption` → excessive fear of `A+B`.

These are all the same failure at a higher level:

> **turning one good research move into an autocomplete template.**

Any generator that produces several consecutive ideas should become temporarily suspect. Recalibrate instead of refining the same shape forever.

The goal is **problem creation**, not merely finding an unoccupied successor experiment.

---

## 2. What counts as a genuinely strong target

A strong target should be:

> **low-description-length + high consequence + genuinely uncertain + newly attackable.**

Before serious owner search, ask four decisive questions:

1. **Reward upper bound:** if the cleanest possible result happens, is this an exciting Main-level paper, or merely a solid/clever paper?
2. **Reasonable attack:** is there a credible way to discriminate the important outcomes without betting months on an unresolvable effect?
3. **Prediction entropy:** would informed researchers plausibly disagree about the answer? If standard algebra/theory already predicts it, the paper is probably too easy.
4. **Belief change:** do both major outcomes change a scientific belief? Avoid projects where only a lucky reversal is interesting.

A technically difficult problem is not automatically important. An important problem with no credible attack is not yet an actionable project.

---

## 3. Strong-paper calibration: learn the MOVE, not the topic

Recent award/high-end work shows several valid moves:

- challenge the advertised advantage itself (`Flexibility Trap`);
- challenge an inference bridge (`RL after X` does not imply direct pressure toward X; `score↑` does not imply capability boundary↑);
- replace a scientific object/quantity when the old one causes a consequential wrong inference;
- demystify a deep phenomenon with a simpler classical model (`grokking` in ridge regression; linear/statistical origins of apparently deep phenomena);
- revisit a classic law because the modern regime violates its assumptions (`Generative or Discriminative?`);
- explain a persistent empirical surprise with theory that makes new predictions (ACL local-attention Best);
- connect two mature literatures only when the bridge creates a new falsifiable statement.

Do **not** use any of these as a fixed topic template.

---

## 4. A+B is a warning label, not a kill rule

A+B is good when the connection creates something neither parent entails:

- a new conditional law;
- a real contradiction on the same quantity/regime;
- a new prediction;
- a unifying explanation;
- a mature concept from field A that changes the scientific object in field B.

A+B is bad when it is merely:

> method A applied to dataset/object B;

or

> parent A + parent B already imply the obvious follow-up.

**L42 is the positive lesson:** syntax-prior work + matched-prior scaling in another domain produced the unresolved question whether scale crowds out or amplifies a matched linguistic prior. Neither parent fixes the answer. It therefore earned only a bounded E01, not automatic full-study status.

---

## 5. Preferred search surface

Bias the next search toward:

- LLM/foundation-model mechanisms;
- training / post-training / inference dynamics;
- interpretability where the mechanism answers a naturally important question;
- architecture / inductive bias / algorithm selection;
- simple, consequential old laws whose assumptions genuinely change under modern models;
- methods that unlock identification of an important question;
- cross-field conceptual transfer.

Deprioritize benchmark/dataset/RAG/evaluator/data-centric/model-zoo work and specialist language-theory questions that are hard to explain without substantial linguistic background.

Simple language-science questions remain allowed if a broad ACL/ML reader immediately understands why the answer matters.

---

## 6. Two underused generators to add

### Cross-field transfer

Actively inspect adjacent fields: signal/audio processing, control, classical statistics, optimization, information theory, vision, learning theory, older neural-network work.

But transfer **concepts / quantities / identification structures**, not merely algorithms.

Ask:

> What does field A know precisely that field B currently treats vaguely, and does importing that understanding produce a new prediction in B?

Michael Nielsen's useful warning applies: people at an X/Y intersection often fail to learn the other field deeply; the few who do can obtain unusually strong results. So do not analogy-shop from abstracts—read the small set of foundational source papers deeply.

### “Old work, new regime”

Do not search old papers for obsolete tricks to rebrand.

Search for:

> old law / classical explanation / simple baseline → identify its assumptions → ask whether the foundation-model regime preserves or breaks them.

Two especially valuable outcomes:

1. the modern mystery reduces to a classical/simple mechanism (**de-mystification**);
2. the old law survives only conditionally because a modern assumption changed (**revised law**).

---

## 7. Recalibration heartbeat — mandatory during execution

Round-start calibration is not enough. The searcher drifts after deep reading.

Recalibrate after roughly **1–2 SERIOUS audits or 3–5 dead WALLs**, and immediately whenever several ideas share the same provenance template.

At each heartbeat, inspect a small diverse set of genuinely strong ACL/EMNLP/NAACL + ICLR/ICML/NeurIPS work, award rationales, author lineages, and strong research-advice material.

Use **predict-before-reading**:

- What question would I have asked?
- What answer would I have predicted?
- What experiment would I have run?
- What contribution would I have thought sufficient?

Then compare with what the strong authors actually did. The prediction error is the training signal for research taste.

Do not let repository rules become scripture. If fresh strong-paper study reveals a better provenance or search behavior, update the belief state.

---

## 8. How to search without becoming mechanical

Keep a bank of important unresolved problems / frictions rather than immediately turning every pressure into a candidate. Hamming's useful pattern is to keep important problems in mind until a new attack appears.

For a fresh pressure:

- first ask whether the question matters independently of the proposed method;
- try the simplest classical/null explanation before inventing mechanism machinery;
- examine multiple formulations before committing;
- do a bounded owner search;
- **once it reaches SERIOUS-LOOK, finish the owner + consequence + non-obviousness + feasibility judgment before jumping elsewhere.**

Do not keep shrinking the formulation merely to escape owners.

Feasibility comes after problem taste, but before serious compute. A clean experiment cannot manufacture an important question.

---

## 9. Session-specific anti-patterns to remember

- `stable anomaly→mechanism` became a successor-paper factory.
- `X is the wrong scalar` became another autocomplete factory.
- opposite-looking results were sometimes false contradictions already unified by old theory.
- grammar-mixture identifiability had real pressure but an obvious mixture-model answer: **important pressure ≠ available Main paper**.
- PLM-as-distribution counterfactual had a real inference issue but collapsed to generic underspecification/predictive multiplicity: **methodological robustness sequel ≠ new parent question**.
- complex language-science walls repeatedly pulled the search away from the user's preferred model-science/mechanism surface.
- abandoning SERIOUS questions halfway caused wasted search and unclear state; do not repeat.

---

## 10. Current state

### L42 — Does Scale Reward Syntax?

`PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`.

Its question survived Selection, but full E01 execution remains gated by E00 protocol/data/instrument checks. Do not expand it during the next open-ended search unless fresh evidence changes its status.

### Other useful standing pressure

`Autoregressive learnability of equivalent computations` remains a WATCH/IMPORTANT pressure, not a candidate: existing work already occupies algorithmic alignment, local predictability, horizon, data diversity and CoT sample-efficiency. Reopen only with genuinely new leverage, not another shortest-path/DP variant.

### Next-session mission

Search for **new independent questions**, preferably mechanism / interpretability / training / architecture oriented.

The target intellectual shape is:

> **Question first → scientific pressure → lineage → why-now leverage → decisive identification.**

And the final meta-question should be repeated throughout the session:

> **Am I discovering a problem that excellent researchers would have wanted answered before seeing my method, or am I merely generating the next experiment after somebody else's paper?**
