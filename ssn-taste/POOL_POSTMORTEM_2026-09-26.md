# 2026-09-26 Full-Pool Postmortem — Why the Sasano-Taste Search Failed

## Executive conclusion

The S01–S12 pool is fully cancelled.

The failure was not merely that individual hypotheses were false. The deeper problem was that the selection pipeline repeatedly promoted **conceptually elegant but empirically ungrounded distinctions** into PILOT-AUTHORIZED topics.

S11 and S12 exposed the failure most clearly:

- S11 had a clean value-vs-precision distinction, but its intended downstream readout was not even stable when the compatible interval was supplied explicitly.
- S12 had a clean definition-vs-world-fact distinction, but natural discourse framing did not reliably manipulate the intended scope; strengthening the scope wording then made the manipulation itself the operative variable.

Both topics looked excellent on paper because the pipeline asked whether A/B/C worlds were meaningful. It did not first establish that the underlying scientific object existed as a **natural, stable, measurable model behavior**.

The remaining S04/S06/S07/S10 are cancelled without spending compute because they were admitted by the same flawed logic.

---

## What we misunderstood about Sasano taste

### 1. We replaced “interesting finding” with “interesting conceptual distinction”

Sasano’s recent feedback repeatedly emphasizes:
- an average reviewer should quickly understand what is interesting;
- unsurprising findings are weak even if technically clean;
- RQs and findings should align one-to-one;
- if novelty relative to prior work is small, it is reasonable to stop and move on.

A key example is the manifold-steering feedback:
- moving a question from activation space to weight space could be reasonable and novel;
- but “a curved method is more accurate than a crude straight-line approximation” is not surprising;
- geometry metrics without a clear behavioral/knowledge interpretation make it difficult to say what was learned.

Our search process incorrectly generalized this into:

> “If two theoretically meaningful worlds can be cleanly contrasted, the topic is interesting.”

That is not what Sasano’s feedback says.

The actual bar is closer to:

> “There is already a concrete phenomenon/result/question that a normal reviewer can see is non-obvious; the experiment then clarifies it.”

### 2. We over-weighted theoretical identification before empirical pressure

S04/S06/S07/S10/S11/S12 were all generated from distinctions such as:
- active state vs raw retrieval;
- stable evidence vs endogenous reweighting;
- state vs source vs rule revision;
- pre-verbal vs post-verbal construal;
- numerical value vs measurement precision;
- definition update vs world update.

These distinctions are intellectually coherent. But coherence is not empirical pressure.

For several topics, if the custom micro-world / psych paradigm / causal fork is removed, there is no existing natural model behavior that forces us to ask the question.

That should have been an immediate rejection.

### 3. We treated synthetic experiments as both object creation and diagnosis

Synthetic experiments are valuable when the research object is already real and the synthetic design diagnoses why it occurs.

We instead often used synthetic tasks to:
1. create the phenomenon;
2. define the construct;
3. measure the construct;
4. interpret the result.

That creates a closed loop where the experiment is “clean” only because the whole scientific object was invented inside the assay.

### 4. We confused “both outcomes are interpretable” with “both outcomes matter”

S11/S12 were repeatedly defended because both A and B worlds could be narrated.

But a null/alternative outcome matters only if it changes a live belief already supported by real evidence.

If both stories exist only inside a custom assay, outcome symmetry is not scientific significance.

### 5. We allowed PILOT-AUTHORIZED before instrument validity was established

This was the largest operational error.

The old Direct-Attack Gate asked:

> Can we write a small experiment whose conditions correspond to the scientific worlds?

It should first have asked:

> Can we manipulate the variable and read the answer reliably at all?

S11 and S12 both failed here.

From now on, selected status requires a construct/instrument preflight before the main effect is inspected.

### 6. We mixed the user’s personal topic preference into Sasano taste

The user separately prefers papers with the shape:

> existing method failure -> diagnosis -> targeted fix -> benchmark gain

That preference is legitimate, but it is **not Sasano taste**.

Adding “Method-Driven Search Mode” to the canonical Sasano guide contaminated the search objective. It has been removed.

User execution preferences may shape how a valid Sasano-style question is pursued, but they cannot define what counts as a Sasano-style question.

### 7. We learned too much from paper structure and too little from actual surprising findings

“Pressure → assumption → decisive attack” is useful, but it became another abstract generator.

The next search must start from **results**, not only from paper framing:
- a result Sasano explicitly found surprising;
- a reproducible result in a strong paper that conflicts with another result;
- a robust natural model behavior whose obvious explanation fails;
- a natural data result with a sharp discontinuity or reversal;
- an existing observation for which the authors’ own explanation is incomplete.

The experiment should explain/resolve that result, not invent the need for it.

---

## Revised Sasano-specific search pipeline

### Stage 0 — Taste purity

Before generating anything, write:

> “This folder optimizes only for Sasano taste.”

Do not use:
- user preference for method papers;
- user preference for benchmark gains;
- user preference for mechanistic work;
- historical Sxx topic shapes

as positive evidence.

### Stage 1 — Observation-first provenance

No seed may exist without one concrete empirical anchor.

Allowed anchors:
1. a published/reproduced surprising finding;
2. two strong papers with conflicting results;
3. a natural benchmark/data behavior with a stable reversal/discontinuity;
4. an explicit Sasano comment identifying a result as surprising or insufficiently explained;
5. a robust observation from our own exploratory replication that was not manufactured by a custom construct.

Not allowed:
- “it would be interesting if…”;
- a theoretical A/B distinction alone;
- old human debate + new LLM subject;
- an underexplored cell;
- a synthetic micro-world that creates the phenomenon.

### Stage 2 — Surprise test

State the simplest baseline explanation.

Ask:

> If the result follows naturally from this baseline, would Sasano call it unsurprising?

If yes, reject unless the project first demonstrates that the simple baseline is wrong.

This is the lesson from the manifold-steering feedback.

### Stage 3 — One finding, one RQ

Before designing a paper, write one sentence:

> Observation O is surprising because baseline B predicts P; we ask whether explanation X or Y accounts for O.

If the RQ cannot be tied to one concrete observation, reject.

### Stage 4 — Early novelty check

Check whether prior work already:
- reports O;
- explains O with the same decisive contrast;
- turns O into the same scientific conclusion.

Do not search for exact wording only.

### Stage 5 — Instrument preflight BEFORE selected status

This stage must not inspect the target main effect.

Prove:
- variable manipulation works;
- positive/negative controls work;
- logically equivalent question forms do not produce catastrophic flips;
- parser/scorer/ground truth are correct;
- strongest explicit version of the task is solvable by the model;
- the readout measures the intended quantity rather than a prerequisite skill.

If preflight fails, the seed never enters SELECTED_TOPICS.

### Stage 6 — Only then PILOT-AUTHORIZED

Selected now means:

> There is a real empirical phenomenon worth explaining, novelty survives, and the instrument is already validated enough that the first main run can actually answer the question.

### Stage 7 — Main result and flexible discovery

After the frozen pilot:
- inspect unexpected structure;
- new observations may change the RQ;
- any new hypothesis requires held-out validation;
- do not rescue the original RQ.

---

## Hard anti-patterns added after S01–S12

Immediately reject a seed when its strongest selling point is:

- “A and B are conceptually different”;
- “both outcomes would be interesting”;
- “LLMs let us test an old human debate more cleanly”;
- “we can construct a synthetic world with exact ground truth”;
- “no one has tested this exact contrast”;
- “the mechanism could be interesting if the behavior exists”;
- “we can always add a probe/patching analysis later.”

Those are experiment properties, not scientific pressure.

---

## Current state

As of 2026-09-26:

**Selected topics: 0.**

S01–S12 are historical failures / anti-resurrection records.

The next search begins from fresh empirical observations under the revised pipeline.
