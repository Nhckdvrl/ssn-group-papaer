# Next Search Handoff — Problem-First Scientific Question Search

**Target:** ACL / EMNLP / NAACL Main; continuously calibrate against TACL / ICLR / ICML / NeurIPS / AAAI.

**Mission:** find a research question worth months of work, not a publishable neighboring gap. **0 survivor is allowed; shallow search is not.**

---

# 1. Repository truth and immediate anti-resurrection

At the start of the next session, **sync `main` and re-read the latest state before trusting any status in this file**. Parallel work is active and some cumulative headers are stale.

Read at minimum:

- `CURRENT_SEARCH.md`
- `RESEARCH_TOPIC_SEARCH.md`
- `RESEARCH_TOPIC_SELECTION.md`
- `failed/KILLED_LEDGER.md`
- `search_rounds/2026-09-14_STANDING_IMPORTANT_PROBLEMS_STATE.md`
- `search_rounds/2026-09-14_STANDING_PROBLEM_TASTE_SELECTION.md`
- `search_rounds/2026-09-14_STANDING_STATE_EXPANSION_II.md`
- latest WALL / friction / disagreement documents
- `search_rounds/2026-09-14_WALL_E_FINAL_SELECTION.md`
- `candidates/L40_LEARNED_ATTENTION_UNIT/README.md`
- the three new exhaustion audits below.

Important correction:

> **L40 is NOT a validated success.** It is at most `PILOT-AUTHORIZED — E01 ONLY`. Its mother phenomenon, effect size and theory-specific crossover remain empirically unverified. Do not use it as positive evidence that WALL-E “worked”. WALL-E is only a record of one paper-search/down-selection process.

This session additionally closed three search surfaces:

1. `2026-09-14_WALL_D_RESOURCE_CONSTRAINT_EXHAUSTION.md` — commit `2e95bb7`;
2. `2026-09-14_LEXICAL_EVENT_STRUCTURE_WALL_EXHAUSTION.md` — commit `999309c`;
3. `2026-09-14_IP03_SUCCINCTNESS_LEARNABILITY_EXHAUSTION.md` — commit `6f9ba9d`.

Do not immediately reopen these with a new model, benchmark, formal language, causal probe, or narrower wording.

---

# 2. Core correction: the generator, not the filter, is the main bottleneck

The recurring failure mode has been:

> `paper -> limitation/gap -> neighboring topic -> owner search -> kill`

Even very strict filtering cannot rescue a bad generator. It only produces a long kill ledger.

The next session must instead run:

> **standing important problem / persistent unexplained friction**
> -> **deep lineage immersion**
> -> **mature explanations and failed predictions**
> -> **new evidence/instrument/regime change updates the old problem**
> -> **a residual scientific uncertainty crystallizes**
> -> only then Selection.

**Paper is evidence. Problem is mother.**

Do not ask “what did this paper not do?” Ask:

> **What old scientific belief does this result make harder to maintain?**

---

# 3. What strong researchers actually teach us about idea generation

The next searcher should repeatedly re-read these ideas during search, not merely acknowledge them once.

### Marco Tulio Ribeiro

Use his actual sequence:

- expand the **adjacent possible** before generating;
- set filters on **important problems**;
- investigate **failures / annoyances you genuinely do not understand**;
- use analogy to ask **where two systems are the same and where the analogy breaks**, not `A+B`;
- challenge status quo only after understanding **why the status quo exists**;
- do not take the first “good enough” project;
- before execution, state what changes in the world if the project succeeds and how you would know.

### Nicholas Carlini

- maintain important questions/ideas for a long time rather than immediately turning each into a project;
- pick for **impact**, not “can this become a conference paper?”;
- problem taste dominates technical cleverness;
- old questions can become newly attackable when technology changes;
- a result should reveal something interesting, important and new even before paper packaging.

### Hamming / Schulman / Olah

- **Hamming:** an important problem is not merely consequential; it must also have a credible attack. Keep several important problems active and wait for leverage.
- **Schulman:** prefer goal/problem-driven research, go deep enough to build intuition, seek simple decisive experiments, and prefer general insights over domain hacks.
- **Olah:** deliberately train taste — predict paper outcomes before reading them, rank ideas before testing them, compare your judgments with strong researchers, and use disagreements as calibration data.

The operational lesson is:

> **Do not use an LLM to autocomplete gaps. Use it to reconstruct a field state deeply enough that a real tension becomes unavoidable.**

---

# 4. Continuous conference taste calibration

Before choosing a new WALL, and again whenever search starts degenerating, sample strong/award work from ACL/EMNLP/NAACL and ICLR/ICML/NeurIPS. For each paper record only:

> `old ancestry -> pressure -> non-obvious move -> decisive quantity/test -> consequence`

Do **not** record “topic” or “method” as the reusable lesson.

Anchors:

- **ICML 2026 Outstanding — The Flexibility Trap:** challenge a load-bearing assumed advantage; find a non-obvious mechanism by which the advantage becomes a limitation.
- **ICLR 2026 Outstanding — LLMs Get Lost in Multi-Turn Conversation:** identify a real training/deployment regime mismatch and diagnose the failure at scale rather than build another benchmark cell.
- **NeurIPS 2025 runner-up — Does RL Really Incentivize Reasoning Capacity?:** convert community rhetoric (“RL creates new capability”) into a falsifiable capability-boundary/support quantity.
- **ACL 2026 Best — Memory efficiency and resource-rational encoding:** start from a long scientific question; impose one principled resource constraint; derive a non-trivial representational consequence.
- **ICLR 2026 Outstanding — Transformers are Inherently Succinct:** introduce a conceptually load-bearing quantity that changes how an old theoretical question is formulated.
- **ACL 2025 Outstanding — Between Circuits and Chomsky:** ask where an inductive bias comes from, not whether a model passes another syntax test.
- **EMNLP 2025 Outstanding — Causal Interventions Reveal Shared Structure Across Filler–Gap Constructions:** the causal method matters only because a prior linguistic theory makes a concrete shared-structure claim.

If several generated ideas start looking like `Paper A did X, nobody did Y`, STOP and recalibrate.

---

# 5. One WALL at a time

A WALL is an important scientific question that would still matter if 2025–2026 papers disappeared.

Do not select a WALL because it has many recent papers. Select it because:

- it has long intellectual ancestry;
- different mature theories exist;
- important observations remain unexplained or underidentified;
- the answer would change how we explain learning/computation/language;
- modern models may provide genuinely new leverage.

Once selected, **do not open another WALL until the current one reaches lineage saturation**.

Lineage saturation means you can explain:

1. why the problem mattered 10–30 years ago;
2. seminal formulations;
3. genuinely different theory branches;
4. decisive historical experiments;
5. critiques / replications / failed diagnostics;
6. what is already solved;
7. 2024–2026 frontier updates;
8. strongest direct owners;
9. what exact uncertainty remains that prior work cannot already predict.

There is no fixed paper count. Read until the intellectual map stops changing.

---

# 6. Frontier papers have only four legitimate roles

A new paper may enter the WALL only as:

1. **Evidence** — updates belief in an old theory;
2. **Contradiction** — conflicts with another mature result on the **same quantity**;
3. **Instrument** — makes a previously non-identifiable old dispute distinguishable;
4. **Regime change** — scaling / RL / long context / multimodality / foundation models break a load-bearing premise of the old theory.

“Nearby setting not tested” is not a role.

---

# 7. SEARCH and SELECTION must remain separate

## SEARCH asks only

> Is there a natural, important, historically grounded, genuinely unresolved scientific question?

During SEARCH build:

- WALL history;
- disagreement map;
- failed-prediction / anomaly map;
- owner map;
- exact open quantity.

Do **not** fall in love with a question because the experiment is easy.

## SELECTION starts only after the question exists

Then require all of the following:

- one-sentence RQ survives removal of model/method/dataset names;
- real scientific ancestry;
- mother phenomenon is credible, not a hoped-for anomaly;
- at least two mature accounts make different predictions on the **same object / same unit / same observable / same treatment**;
- a decisive observation/intervention changes belief between accounts;
- successful-result upper bound is Main-level;
- multiple outcome directions remain interpretable;
- reviewer compression leaves a real residual inference;
- effect resolution / MDE / seeds / compute can distinguish scientifically meaningful outcomes.

Only then create an L-series entry.

---

# 8. The most important rejection tests

Before promotion, force the harshest reviewer statement:

> “This is just Prior A + Prior B.”

or

> “Humans already established X; this is X on an LM.”

> “This is generic optimization/path dependence.”

> “This is a mechanistic sequel to an existing behavioral owner.”

> “You changed architecture/data/prompt, not the scientific inference.”

Then state **one inference that the prior literature cannot produce**.

If the answer requires narrower wording, KILL.

Also reject by default:

- psychology/linguistics phenomenon × LLM;
- behavior paper -> mechanism salvage;
- paper limitation -> project;
- new model × old benchmark;
- method X × task Y;
- arbitrary curriculum/order effects;
- benchmark/data/evaluator/RAG work;
- model zoo;
- probe/SAE/patching-first questions;
- one-cell anomaly stories;
- a project where only one lucky positive outcome is publishable.

---

# 9. Lessons from the three WALLs closed in this session

These are **negative search lessons**, not templates for new questions.

### Resource constraints / Starting Small

An attractive old debate can still be exhausted if every modern descendant collapses into already mature distinctions: effective-input filtering, encoding vs retrieval, prediction vs reconstruction, compositionality, prior knowledge, bounded compute, or resource allocation. Do not keep narrowing merely because the mother problem is important.

### Lexical event structure

A beautiful old theory dispute is insufficient if the new operation cannot identify the disputed ontology. Cross-form causal reuse was confounded by downstream semantic convergence; one-event vs two-event causal-model comparison had severe alignment non-uniqueness and outcome-robustness problems. **Modern internals are not automatically new identifying leverage.**

### Expressivity / succinctness / learnability

A conceptual tension is not a project once its missing variable is already a direct theory program. Parameter-space geometry now explicitly connects representability, sensitivity and learnability; `succinct representation != accessible solution` is no longer an unasked law. Do not create a “compare simplicity notions” benchmark to preserve novelty.

---

# 10. How to react to repeated 0-survivor rounds

Do **not** lower standards first.

Ask whether the generator has silently regressed to:

- title-keyword search;
- paper-gap autocomplete;
- method-first reasoning;
- owner-kill followed by narrower salvage;
- searching only 2025–2026 instead of reconstructing the older dispute;
- mistaking “unexplored” for “important”.

If yes, expand the intellectual search surface:

- classic theory papers;
- Related Work and citation chains;
- author lineages over many years;
- replications and critiques;
- talks/blogs/research advice;
- adjacent scientific disciplines when they study the same quantity.

A 0-survivor result is acceptable **only after lineage saturation**, not after a finite brainstorm batch.

---

# 11. Exact operating instruction for the next session

1. Sync `main`; resolve authoritative current state and IDs.
2. Re-read killed/exhausted routes before searching.
3. Do a fresh award/strong-paper + research-taste calibration.
4. Re-read the ACTIVE standing problems.
5. Choose **one** WALL that is not one of the just-exhausted surfaces.
6. Turn candidate generation **OFF**.
7. Reconstruct the WALL from classic theory -> branches -> experiments -> critiques/replications -> frontier updates -> direct owners.
8. Search for **failed predictions, same-quantity disagreements, broken assumptions, or genuinely new identifying leverage**.
9. Do not name an L-series until one residual question survives reviewer compression and Selection.
10. If the WALL is exhausted, document why and only then move to the next WALL.

The desired endpoint remains:

> **“Yes — this question obviously matters, and it is strange that we still do not know the answer.”**

Not:

> **“Apparently nobody has run this exact experiment yet.”**

## Research-process calibration sources

- Marco Tulio Ribeiro, *Coming up with research ideas* — https://medium.com/@marcotcr/coming-up-with-research-ideas-3032682e5852
- Marco Tulio Ribeiro, *Organizing and evaluating research ideas* — https://medium.com/@marcotcr/organizing-and-evaluating-research-ideas-e137637b599e
- Nicholas Carlini, *My research idea logfile, 2016–2019* — https://nicholas.carlini.com/writing/2024/my-research-logfile.html
- Nicholas Carlini, *How to win a best paper award* — https://nicholas.carlini.com/writing/2026/how-to-win-a-best-paper-award.html
- Richard Hamming, *You and Your Research*
- John Schulman, *An Opinionated Guide to ML Research*
- Chris Olah, *Research Taste Exercises*
