# 2026-09-15 — Classic-Assumption / Regime-Change Search Audit

**Target:** ACL / EMNLP / NAACL Main, calibrated against TACL / ICLR / ICML / NeurIPS / AAAI  
**Doctrine:** `Problem is mother. Paper is evidence.`  
**Entry head:** `41197ebac81a90b65838a83df65ae20f65c99879`  
**Mode:** classic problem / theorem / trade-off → load-bearing assumption → foundation-model regime change → owner / identification audit  
**Outcome:** **0 new L-series — 0 new pilot authorizations — no K-series allocation**

> This pass deliberately did **not** assign a new WALL letter. The repository advanced concurrently through WALL-I/J/K while this audit was running. The surfaces below are therefore recorded as `SEARCH-SURFACE CLOSED / COLLISION` rather than being given competing WALL identities.

---

# 0. Repository state and anti-resurrection

Before closing this pass, `main` was resynchronized after the concurrent WALL-I/J/K round.

The authoritative state entering this audit includes:

- **L40 / WALL-E remains only `PILOT-AUTHORIZED — E01 ONLY`**. Its mother phenomenon, effect size and theory-specific cue-class vs form–function crossover are not experimentally validated.
- WALL-D / natural resource constraints is exhausted under its current descendants.
- lexical event structure / decomposition is exhausted.
- IP03's current succinctness–learnability / parameter-geometry route is exhausted.
- WALL-F / LM as scientific model system is exhausted as a standalone generator.
- WALL-G / systematicity is exhausted under current descendants.
- WALL-H / reachable behavioral support is exhausted under current accessibility quantities.
- WALL-I / closed-loop autoregressive recovery is exhausted.
- WALL-J / learning restrictions from positive evidence is exhausted.
- WALL-K / advance planning in autoregressive generation is exhausted.

The killed-question ledger remains authoritative through **K183** with **K184** next. None of the surfaces in this file reached Selection, so **K184 is not consumed**.

This pass specifically avoided reopening old parents by changing model, prompt, benchmark, probe, formal language, wording, or mechanism tool.

---

# 1. Why this pass changed search strategy midstream

The first part of the pass still risked a subtle form of autocomplete:

> think of a broad old problem → immediately imagine how modern LLMs might instantiate it.

That is better than `paper → limitation → topic`, but it can still generate weak `old phenomenon × LLM` projects.

The search was therefore reset around a stricter pattern:

> **classic theorem / trade-off / explanatory claim**  
> → identify the premise that made it valid  
> → ask whether the foundation-model regime breaks that premise  
> → require a SAME-QUANTITY disagreement or a newly identifying intervention  
> → only then consider a project.

The main taste calibration was EMNLP 2025 Outstanding **Generative or Discriminative? Rethinking Theoretical Underpinnings of Machine Learning**. Its strength is not that it found an empty Transformer comparison cell. The generative-vs-discriminative trade-off is old (Efron; Ng & Jordan), but the old theory relied on assumptions such as restricted model classes / independence structure that modern Transformers violate. The paper therefore has a legitimate reason to re-ask the old quantity under a new regime.

A second calibration came from ACL 2026 Best **Language Models and the Imperfective Paradox** and the subsequent 2026 critique of its benchmark construction. The lesson is complementary:

> award-level scientific framing does not waive construct validity / gold validity.

A beautiful mother problem can still fail if the operationalized examples do not instantiate the claimed semantic contrast.

---

# 2. Search surface A — online search/planning vs compiled/amortized computation

## Old scientific ancestry

This problem is much older than reasoning LLMs.

- Newell–Simon style heuristic search treats problem solving as online search in a state space.
- ACT / skill-acquisition work studies **knowledge compilation**: with practice, expensive deliberative procedures can become directly executable productions.
- Soar **chunking** makes the idea especially explicit: a result formerly obtained by opening and solving a subgoal can later be produced directly when a similar state recurs.
- model-based vs model-free control asks whether decisions are recomputed from a transition model or emitted from cached values / policies.
- successor representations already show that the binary is too simple: a learned representation can preserve some forms of revaluation flexibility without full online planning.

## Modern pressure

Reasoning models expose visible intermediate computation, test-time compute scaling, search-like backtracking, and post-training that can move computation between inference time and parameters.

A tempting question is therefore:

> When a reasoning model succeeds, is it genuinely searching online, or executing a computation that training has already compiled/amortized into the policy?

## Why it does not survive

The obvious behavioral signatures are not identifying:

- revaluation sensitivity;
- visible backtracking;
- longer thinking time;
- performance gains from additional recurrent / token computation;
- reduced chain-of-thought after training.

A learned recurrent computation, successor-like representation, internalized search algorithm, or hybrid policy can reproduce these signatures without corresponding to a clean online-search / cached-policy dichotomy.

Modern ownership is also direct:

- **Distilling System 2 into System 1** explicitly studies compiling System-2-style computation back into model parameters;
- later self-distillation / curriculum-distillation work studies similar internalization;
- ACL 2026 **When Internalization Fails** studies limits of compressing reasoning into the model;
- ICML 2025 **Satori** explicitly asks whether search capabilities can be internalized.

### Verdict

**SEARCH-SURFACE CLOSED.**

Do not resurrect as:

- `reasoning RL turns search into intuition`;
- short-vs-long CoT before/after RL;
- revaluation implies online search;
- internalized search on another task.

A reopening would require an independently justified operation that makes online search and flexible compiled computation give opposite predictions on the same quantity.

---

# 3. Search surface B — rational metareasoning / value of computation

## Old scientific ancestry

The durable question is:

> When is another unit of computation worth performing before acting?

Russell / Wefald and later rational-metareasoning work formalize this as **value of computation (VOC)**: the expected improvement in downstream decision utility from another computation, minus its cost.

This is not merely `harder problems deserve more tokens`. It predicts that optimal deliberation depends on:

- probability the computation changes the decision;
- stakes / utility difference between outcomes;
- cost of computation;
- recoverability / usefulness of additional information.

Thus two instances with the same apparent difficulty can rationally deserve different compute if the stakes differ.

## Attractive residual tested in this audit

> Holding the problem fixed, does changing only the decision stakes / cost change how much a reasoning system should deliberate?

This would separate a genuine VOC account from a pure difficulty / entropy heuristic.

## Why it does not survive

The modern LLM literature already directly imports the parent:

- **Rational Metareasoning for Large Language Models** explicitly uses value-of-computation style reasoning to decide when intermediate reasoning is worth invoking;
- cost-aware / adaptive test-time-compute work studies token budgets and stopping;
- ROI-style reasoning work explicitly optimizes return on inference compute;
- current routing work has already begun separating stakes from confidence / difficulty.

The attractive stakes residual is therefore not a clean unowned parent. It is inside an active cost-sensitive inference program.

### Verdict

**SEARCH-SURFACE CLOSED.**

Do not register another `adaptive thinking budget` or `same difficulty, different stakes` paper unless a mature rival theory produces a new SAME-TREATMENT prediction not already covered by metareasoning / selective prediction / cost-sensitive routing.

---

# 4. Search surface C — when is verification actually easier than generation?

## Old scientific ancestry

A load-bearing intuition behind search, proof systems and modern verifier-guided reasoning is:

> finding a solution can be hard even when checking a supplied certificate is easy.

In complexity theory this asymmetry is meaningful only when a suitable certificate and checking procedure exist. It does **not** imply that an arbitrary learned statistical predictor becomes a reliable verifier merely because it is shown a candidate answer.

## Modern pressure

Best-of-N, process/reward models, verifier-guided search, MCTS-like reasoning and RLVR often rely on some version of generation–verification asymmetry.

The interesting scientific question would not be `can model X self-check?` but:

> What property of a candidate makes it provide information that genuinely reduces the computational problem for the verifier, rather than forcing the verifier to solve the original problem again?

## Critical conceptual correction

Modern literature already uses `generation–verification gap` in a revealingly different sense:

> the generator may already sample a correct solution, yet an imperfect learned verifier cannot reliably select it.

This means oracle coverage and realizable selection are different quantities.

## Why it does not survive

Direct owners already occupy both the quantity and the boundary conditions:

- ICLR 2025 **Mind the Gap: Examining the Self-Improvement Capabilities of Large Language Models** formalizes the utility gain available from verifier-based reweighting;
- ICLR 2025 work on **limitations of self-verification** explicitly attacks the assumption that verification must be easier for the same LLM and shows that sound external verifiers are qualitatively different;
- NeurIPS 2025 **Weaver** studies the gap between imperfect and oracle verification;
- **Variation in Verification** systematically varies problem difficulty, generator strength and verifier solving ability.

A project on `candidate certificates vs re-solving` now reviewer-compresses to an explanatory sequel of this active program.

### Verdict

**SEARCH-SURFACE CLOSED.**

The durable lesson should be retained:

> complexity-theoretic search/checking asymmetry does not automatically license a same-model generation/verification asymmetry.

But there is no new L-series question here under current ownership.

---

# 5. Search surface D — problem representation / isomorphic tasks

## Old scientific ancestry

Classic problem-solving work by Hayes & Simon shows that formally isomorphic tasks can differ dramatically in human difficulty because wording / surface organization induces different internal problem representations.

The scientific object is real:

> representation choice is not necessarily a neutral encoding of a fixed problem; it can change which computation is easy to discover or execute.

## Modern temptation

Foundation models are unusually sensitive to serialization, tokenization and representational format. One could therefore ask whether semantic isomorphs induce different learned algorithms.

## Why it does not survive

There is already a direct modern owner:

- EACL 2026 Findings **Program-of-Thought Reveals LLM Abstraction Ceilings** explicitly evaluates isomorphic GSM8K/MATH variants and asks whether reasoning should be invariant to surface representation. Program-of-thought training can improve consistency while leaving a correctness gap.

Further narrowing quickly becomes:

- prompt/format sensitivity;
- tokenization sensitivity;
- another isomorph benchmark;
- or the already exhausted IP03 `representation/succinctness → learnability/optimization geometry` route.

### Verdict

**SEARCH-SURFACE CLOSED / ANTI-RESURRECTION COLLISION.**

Do not re-enter by swapping formal language, serialization or probe.

---

# 6. Search surface E — productivity from type diversity / entrenchment / analogy

## Old scientific ancestry

Morphological and construction learning has a long dispute over why learners generalize some patterns productively while treating others as lexically restricted exceptions.

Mature accounts include:

- symbolic / stochastic rule accounts;
- exemplar / analogy accounts;
- entrenchment;
- type frequency;
- token frequency;
- phonological / semantic diversity and coverage.

Albright & Hayes-style wug paradigms already force rule and analogy accounts to make predictions on the same novel-form quantity.

## Attractive residual

> Is productivity caused by the number of types itself, or by the diversity / coverage those types provide?

This is scientifically cleaner than another `does the LM learn morphology?` test.

## Why it does not survive

The key causal contrasts are already available in human / artificial-language experiments. Recent studies directly manipulate type frequency, token frequency and diversity / coverage.

Therefore a Transformer version lacks a new identifying operation. It compresses to:

> classic language-learning productivity law × neural learner.

Turning instead to `which training statistic shapes LM generalization` simply returns to IP02's already crowded formation-of-inductive-bias parent.

### Verdict

**SEARCH-SURFACE CLOSED.**

This is an example where an excellent mother problem still fails because the foundation-model regime does not change what can be inferred.

---

# 7. Search surface F — identifiability of latent computation

## Old scientific ancestry

The general problem is observational equivalence:

> multiple latent mechanisms can generate the same observable behavior.

A tempting modern move is to exploit multiple environments, interventions, training objectives or internal access to identify the latent computation.

## Why it is not a new wall

This collides directly with the repository's existing WALL-A friction state:

- **A-FR1:** causal abstraction can become vacuous when the alignment class is too expressive;
- **A-FR3:** abstraction methods test a proposed ontology more readily than they discover which ontology deserves to be proposed.

The external literature strengthens exactly those frictions:

- ICLR 2025 **Everything, Everywhere, All at Once: Is Mechanistic Interpretability Identifiable?** asks whether mechanism explanations are statistically identifiable from behavior;
- NeurIPS 2025 **The Non-Linear Representation Dilemma** shows that sufficiently expressive alignment maps can make causal-abstraction claims uninformative;
- causal-representation-learning impossibility results show that invariance alone is generally insufficient for unique latent identification.

### Verdict

**COLLISION WITH EXISTING WALL-A STATE — NO NEW WALL.**

Do not reopen as `use more environments / interventions to identify the true reasoning mechanism` unless the high-level variable and identifiability theorem are independently fixed.

---

# 8. Boundary check — multi-turn training/deployment mismatch

This was checked as a taste / owner sanity test, not opened as a wall.

ICLR 2026 **LLMs Get Lost in Multi-Turn Conversation** supplies a strong real regime mismatch: single-turn competence does not predict reliable multi-turn deployment, with error accumulation / inability to recover playing a major role.

But by 2026 the parent `static-context training → policy-induced interactive distribution shift` is already directly modeled using exposure-bias / imitation-learning ideas, including on-policy interactive training and horizon-dependent compounding analyses.

Therefore:

> training regime ≠ deployment regime

is no longer sufficient as a question. A future IP10 descendant needs a deeper quantity than `on-policy data fixes exposure bias`.

---

# 9. The most important generator correction from this pass

The failed surfaces above reveal a stronger rule than `read classics first`.

## Bad generator even when it starts from an old problem

> old important problem  
> + modern LLM affordance  
> → candidate

This still produces many weak descendants.

Examples from this pass:

- planning/search + visible CoT;
- value of computation + token budgets;
- verification asymmetry + learned verifier;
- problem representation + prompt/serialization variants;
- productivity theory + controlled LM training;
- latent identifiability + activation interventions.

All are intellectually respectable and still mostly fail.

## Better generator

Search for:

> **old scientific claim whose explanatory force depended on a specific premise**  
> → **foundation-model regime breaks that premise**  
> → **the original quantity can still be measured**  
> → **rival explanations now make different predictions on that same quantity**.

This is materially stricter than `classic problem + new instrument`.

The modern regime must change the **inference**, not merely the convenience of the experiment.

---

# 10. A four-question regime-change gate for future WALL selection

Before spending a full lineage pass on a new wall, answer:

### G1 — What was the old load-bearing claim?

Not the topic label. State the actual explanatory / theoretical claim.

### G2 — Which assumption made the old claim valid?

Examples: model class, independence assumption, access to a sound verifier, iid deployment, fixed representation, resource regime, observability assumption.

### G3 — Does the modern regime actually violate that assumption?

If not, this is probably `old result × LLM`.

### G4 — What SAME QUANTITY now discriminates the resulting rival accounts?

If the only novelty is a new metric / probe / benchmark / mechanism visualization, stop.

Only walls that pass all four deserve deep immersion.

---

# 11. Negative results of this round are not interchangeable

| surface | mother problem real? | why it closes |
|---|---:|---|
| online search vs compiled computation | yes | modern internalization/search owners + non-identifying behavioral signatures |
| value of computation | yes | LLM metareasoning/cost-sensitive inference already directly occupies parent and stakes variants |
| verification vs generation | yes | direct 2025–2026 theory/empirical owners now study gap and boundary conditions |
| problem representation/isomorphs | yes | direct isomorphic-reasoning owner; further narrowing resurrects closed IP03 route |
| productivity/type diversity | yes | key causal distinctions already human-identifiable; LMs add no new inference |
| latent-computation identifiability | yes | already represented by WALL-A frictions and direct identifiability/impossibility work |
| multi-turn mismatch | yes | static→interactive occupancy shift / exposure-bias explanation already an active direct parent |

This is a **healthy 0-survivor result** because the surfaces were rejected for different scientific reasons after ancestry / owner / identification checks, rather than being generated as limitation cells and owner-killed one by one.

---

# 12. Search state leaving this audit

**New L-series:** 0.  
**New pilot:** 0.  
**K-series allocation:** none; K184 remains next.  
**L40:** still `PILOT-AUTHORIZED — E01 ONLY`, not a validated success.  
**New WALL letter:** none.

The next search should **not** continue the reasoning-resource cluster immediately. Search/planning, metareasoning, verification and representation-format variants are now owner-dense and risk local autocomplete.

Preferred next surface-generation procedure:

1. sample strong ACL/EMNLP/NAACL/TACL + ICML/NeurIPS work whose contribution explicitly overturns or conditions an older claim;
2. trace the older claim back to its theorem / experiment / mature rival literature;
3. record the **assumption that carried the old conclusion**;
4. delete the frontier paper and ask whether the old problem remains important;
5. search for foundation-model regime changes that violate the assumption;
6. require SAME-QUANTITY rival predictions before naming a WALL;
7. only after lineage saturation ask whether a candidate exists.

The target shape is now:

> **old claim + broken premise + preserved scientific quantity + new decisive inference**

not:

> old problem + modern model.
