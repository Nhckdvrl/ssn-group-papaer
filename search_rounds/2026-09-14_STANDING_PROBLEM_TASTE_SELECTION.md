# 2026-09-14 — Standing-Problem Taste Selection

**Mode:** TASTE SELECTION OVER LONG-TERM PROBLEMS  
**Input:** `search_rounds/2026-09-14_STANDING_IMPORTANT_PROBLEMS_STATE.md`  
**Candidate generation:** **STILL OFF**  
**Purpose:** choose which important problems deserve months of attention *before* exposing the searcher to fresh frontier papers.

---

# 0. Selection rule

This is deliberately not a novelty ranking.

A standing problem can be important and still be a bad problem **for us** right now. The ranking uses five separate judgments:

1. **Scientific consequence** — would either answer materially change an explanation/theory?
2. **Research intimacy** — do we already understand enough of the object and have relevant technical instincts to notice real friction rather than invent one?
3. **Naturalness** — is the object real without a benchmark/dataset/method wrapper?
4. **Modern leverage** — does the current foundation-model regime plausibly provide a genuinely new inference or intervention?
5. **Search headroom** — is there still room for a new question, or is the parent so saturated that every route compresses to a known program?

Scores are **taste judgments, not measurements**. They are intentionally comparative.

---

# 1. Current ranking

| rank | standing problem | consequence | intimacy | naturalness | modern leverage | headroom | decision |
|---|---|---:|---:|---:|---:|---:|---|
| **1** | **IP01 — reusable abstraction vs decodable correlate** | 5 | 5 | 5 | 5 | 3.5 | **PRIMARY IMMERSION** |
| **2** | **IP02 — origin of inductive biases** | 5 | 4.5 | 5 | 5 | 3.5 | **PRIMARY IMMERSION** |
| **3** | **IP03 — expressivity vs learnability vs learned algorithm** | 5 | 3.5 | 5 | 4.5 | 4 | **PRIMARY IMMERSION / STRETCH** |
| **4** | **IP04 — resource constraints reshape representation/computation** | 4.5 | 3.5 | 5 | 4.5 | 4 | **SECONDARY IMMERSION** |
| **5** | IP05 — systematic generalization / units of recombination | 5 | 4 | 5 | 4 | 2.5 | HOLD; too easy to become benchmark work |
| **6** | IP07 — LMs as scientific model systems / linking hypotheses | 5 | 3 | 5 | 5 | 3 | HOLD; meta-level is strong, concrete descendants often become human-vs-LM replication |
| **7** | IP06 — efficiency / processing pressures shaping language | 5 | 2.5 | 5 | 3.5 | 4 | HOLD; beautiful science, but current research intimacy is weaker and data/theory burden is high |
| **8** | IP08 — semantic + context + pragmatic goals | 5 | 4 | 5 | 4 | 1.5 | **SUPPRESSED GENERATOR**; parent space heavily mined |

WATCH problems IP09–IP12 remain off-limits as generators unless a genuinely new source of leverage appears. DORMANT IP13–IP17 remain closed.

---

# 2. Why IP01 is rank 1

## The wall question

> **When does a neural language model actually implement the same abstract variable across different surface cases, rather than merely contain enough correlated information to imitate the same behavior?**

This is the strongest fit because it combines:

- a real long-standing scientific question about representation and computation;
- modern foundation models as a genuinely new experimental system;
- causal intervention as an **identifying operation**, not as the topic;
- direct relevance to linguistic/semantic theory;
- high compatibility with our strongest technical instincts: controlled interventions, latent/state analysis, causal mediation, stage decomposition, and matched counterfactual comparisons.

The key is that the scientific variable must come from an independently motivated theory. The project can never begin with “find a direction and patch it.”

### Why the current literature does not make the whole problem obsolete

Causal abstraction gives a principled language for implementation. Distributed alignment methods show that high-level variables need not align with individual neurons. Filler–gap work demonstrates that causal transfer across constructions can provide theory-relevant evidence. But these successes **raise**, rather than settle, a broader question:

> Under what conditions do learned abstractions generalize causally across lexical, structural, semantic, or discourse variation — and when does apparent shared structure fracture into context-specific computation?

That is a standing problem, not a proposed paper.

### Main danger

Interpretability method shopping.

If the next thought is “which linguistic phenomenon should we patch?”, STOP. The correct order is:

> independent theoretical dispute -> exact shared-variable prediction -> identifying counterfactual -> only then mechanism tool.

---

# 3. Why IP02 is rank 2

## The wall question

> **Why does a learner prefer one linguistic/general reasoning structure over another when both are compatible with the observed evidence?**

This is deeper than “what can a transformer learn?” and deeper than “does pretraining teach syntax?” It asks where the *preference among generalizations* comes from.

This problem has unusually strong scientific ancestry:

- language-acquisition debates about poverty of stimulus / inductive bias;
- Linzen-line work manipulating language structure, architecture, input genre, depth, and controlled evidence;
- possible/impossible-language work turning sweeping claims about learnability into explicit trajectories;
- formal-language pre-pretraining showing that prior learning can alter later linguistic bias.

It also matches our research intimacy because we understand training stages, objective changes, representation formation, and intervention-based analysis well enough to reason about **formation**, not only endpoints.

### What keeps it from rank 1

The obvious experimental axes are crowded. Data order, curriculum, architecture sweeps, pretrain/post-train comparisons, and synthetic languages can all turn into incremental factorial experiments.

Therefore the only promising descendants will be those where there are **two genuine competing generalizations** and the modern regime gives a way to identify *why one became preferred*.

### Main danger

Knob shopping.

If the question can be paraphrased as “how does hyperparameter/training choice X affect capability Y?”, it is not IP02 in the intended sense.

---

# 4. Why IP03 is rank 3 despite lower intimacy

## The wall question

> **What determines which of a model’s many representable algorithms gradient-based learning actually discovers and continues to use out of distribution?**

This may have the largest theoretical reward of the current list.

The field often moves too quickly from:

> architecture can express X

or

> model fits training distribution

to

> architecture/model has learned the relevant computation.

Cotterell/Merrill-style formal characterization and Linzen-style empirical acquisition expose the missing middle layer: **selection among representable solutions**.

### Why this is a stretch problem

Our current comparative advantage is experimental/mechanistic rather than theorem-first formal-language theory. A project that requires inventing deep new formal machinery before the scientific question is sharp would be a poor fit.

However, a well-chosen natural case where formal theory gives two qualitatively different representable algorithms and training reliably selects one could be exceptionally strong.

### Main danger

Toy-world seduction.

A beautiful result on a formal language is not enough unless the learned-algorithm distinction changes how we understand a real property of language models.

---

# 5. Why IP04 is the best secondary problem

## The wall question

> **Which useful representational/computational structures emerge *because* a learner is resource constrained?**

This is attractive because it reverses a common engineering assumption. A bottleneck is not merely damage; it can be a cause of abstraction, compression, categorical structure, or better generalization.

Resource-rational language work gives this question unusually good scientific ancestry. Memory limits, information locality, predictive bottlenecks, and efficient coding are not arbitrary regularizers; they correspond to independently motivated computational pressures.

### Why it fits us less strongly than IP01/IP02

The best versions require genuine intimacy with cognitive/resource-rational theory, not just knowing how to add a bottleneck to a transformer. We currently have stronger instincts for training and causal mechanism than for deriving the correct resource objective.

### Main danger

Post-hoc bottleneck stories.

Never start with “let’s restrict context/memory/precision and see what happens.” Start from the resource-allocation problem and derive what representation *should* be favored.

---

# 6. Why IP05–IP08 are not primary despite being important

## IP05 — systematic generalization

Scientifically huge, but the phrase now covers too many benchmarks and incompatible definitions. Without an exact theory of the reusable unit, it degenerates into benchmark splitting. Its strongest descendants likely need to enter through IP01, IP02, or IP03 rather than through “compositionality” itself.

## IP07 — LMs as model systems

Extremely important as a philosophy of evidence. However, generic human–LM similarity is already a mature program. Treat IP07 as an **evidence-standard constraint on other projects**, not currently as the generator of a paper.

## IP06 — efficiency shaping language

This is arguably the most beautiful pure language-science object on the list. It is not ranked low because the science is weak; it is ranked low because our current research intimacy is weaker and a strong project needs careful command of typology, psycholinguistics, information theory, and construct validity. Keep it visible for long-term learning.

## IP08 — semantics/pragmatics

Scientifically central and personally interesting, but recent searching has already shown how quickly every attractive textbook distinction turns into an occupied competence-test parent. Keep the big problem, suppress direct generation until a mature debate acquires genuinely new identification.

---

# 7. Our first real “important problems on the wall”

For the next reading phase, only these four should be kept in active working memory:

### WALL-A — Reusable abstractions

**What would make us believe the same abstract computation is actually reused across different linguistic realizations?**

### WALL-B — Formation of inductive bias

**Why does learning prefer one generalization over another when both fit the observed data?**

### WALL-C — Selection among representable algorithms

**Why does optimization discover one computation rather than another that the architecture could also implement?**

### WALL-D — Structure from resource constraints

**What useful representation/computation emerges specifically because a natural resource is limited?**

These are intentionally simple. They should remain readable without citations, model names, benchmarks, or 2026 terminology.

---

# 8. What the next literature pass is allowed to do

The next pass should **not** search exact phrases corresponding to potential papers.

Instead, for each WALL problem, read a small number of long-running research programs and collect only:

1. what the field believed at different times;
2. experiments/results that changed that belief;
3. unresolved disagreements *inside the standing problem*;
4. real annoyances/failures researchers encountered while pursuing it;
5. operations that newly changed what could be inferred;
6. scientific quantities the lineage learned to care about.

Every new source gets one of four labels:

- **SUPPORTS** — strengthens an existing belief in the wall state;
- **CONTRADICTS** — creates a genuine internal tension;
- **IDENTIFIES** — supplies an operation that can distinguish accounts previously inseparable;
- **IRRELEVANT** — interesting paper, but does not bear on the wall problem.

The **IRRELEVANT** label is important. We must become comfortable reading an excellent paper and generating **zero** project ideas from it.

---

# 9. Anti-autocomplete test for the next phase

Before any future question is allowed to exist, hide all focal-paper titles and ask:

> Could a researcher who had worked on WALL-A/B/C/D for five years have wanted this answer *before* the newest paper appeared?

If **no**, it is almost certainly a paper-successor idea.

Then ask:

> What changed recently: the importance of the problem, or only our ability to identify the answer?

Preferred shape:

> old important problem + genuinely new identification leverage.

Suspicious shape:

> new paper + unoccupied neighboring cell.

---

# 10. Current decision

**Primary immersion:** IP01, IP02, IP03.  
**Secondary immersion:** IP04.  
**All other problems:** no generation for now.  
**New L-series:** 0.  
**Pilot:** none.

The next action is not a 25–40 seed batch.

The next action is to become substantially more intimate with these four wall problems by tracing their **multi-year research histories and unresolved internal disagreements**. Only after that immersion should we ask whether any fresh observation genuinely bears on them.