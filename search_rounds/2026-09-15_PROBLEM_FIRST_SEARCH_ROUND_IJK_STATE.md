# 2026-09-15 — Problem-First Search Round State: WALL-I / J / K

**Target:** ACL / EMNLP / NAACL Main, continuously calibrated against TACL / ICLR / ICML / NeurIPS / AAAI  
**Doctrine:** `Problem is mother. Paper is evidence.`  
**Round outcome:** **0 new L-series — 0 new pilot authorizations**  
**Interpretation:** **healthy zero-survivor round after three separate lineage-saturation audits**

---

# 0. Repository state and anti-resurrection entering the round

The round began after `main` had already closed WALL-F/G/H and explicitly preserved:

- **L40 / WALL-E** as only `PILOT-AUTHORIZED — E01 ONLY`; no experimental validation of the mother phenomenon, effect size, or theory-specific crossover;
- WALL-D / natural resource constraints as exhausted;
- lexical-event-structure / decomposition as exhausted;
- IP03's current succinctness–learnability / parameter-geometry line as exhausted;
- WALL-F / LM-as-scientific-model as exhausted as a standalone topic generator;
- WALL-G / systematicity as exhausted under current descendants;
- WALL-H / reachable behavioral support as exhausted under current accessibility quantities.

The present round did not reopen these by changing model, prompt, probe, formal language, dataset, or wording.

---

# 1. Taste recalibration used during the round

The round again used award-level work only to calibrate scientific shape, not as topic parents.

The recurring pattern was:

> old scientific ancestry  
> → a load-bearing explanatory claim  
> → failed prediction / contradiction / identifying operation  
> → one quantity that forces rival accounts to disagree  
> → changed scientific belief.

This is the same reason papers such as *The Flexibility Trap*, the RLVR capability-boundary work, resource-rational memory work, and *LLMs Get Lost in Multi-Turn Conversation* are useful taste anchors: the implementation is secondary to a question that remains meaningful after model / benchmark names are deleted.

A strong warning from this round is that even an excellent old problem does **not** justify importing its human / control-theoretic variable into LMs unless the bridge itself changes the inference.

---

# 2. WALL-I — Closed-loop autoregressive recovery

Audit:
- `search_rounds/2026-09-15_WALL_I_CLOSED_LOOP_RECOVERY_EXHAUSTION.md`

Commit:
- `ee601c0c481e086d33b3275e2a2e4a613125e793`

## Mother problem

> A sequence predictor is trained mainly on expert / data-generated histories but is deployed on histories containing its own outputs. After a deviation, what determines whether the induced rollout error amplifies, persists, or is absorbed?

## Real historical pressure

The classic exposure-bias story predicts compounding distortion under rollout.

He et al. EMNLP 2021 instead report a strong **self-recovery** phenomenon: prefix discrepancy hurts, but distortion is limited and does not monotonically increase with generation horizon.

Bau & Andreas 2021 further show that prediction after an unexpected token is structured rather than arbitrary, interpolating between local and global cues.

Thus the wall contains a genuine failed prediction, not a paper gap.

## Why no candidate survived

The strongest residual was:

> What structural condition makes a deviation contract rather than amplify under autoregressive rollout?

But the missing explanatory level is already mature outside NLP:

- imitation learning has long treated expert-state vs learner-state distribution shift as compounding error;
- Swamy et al. ICML 2021 explicitly define **moment recoverability**;
- control / behavior-cloning work studies stability and recovery of learner trajectories.

Reviewer compression succeeds:

> `He et al. self-recovery + imitation-learning/control recoverability applied to text.`

That is an A+B descendant.

## Decision

**WALL-I exhausted as current generator.**

Keep the durable friction:

> one-step predictive quality does not determine closed-loop rollout stability.

Do not create another exposure-bias / self-recovery / recovery-coefficient paper without a language-specific mature theory that makes opposite predictions on one matched perturbation-response quantity.

---

# 3. WALL-J — Learning restrictions from positive evidence

Audit:
- `search_rounds/2026-09-15_WALL_J_NEGATIVE_EVIDENCE_EXHAUSTION.md`

Commit:
- `79f1f920e514d205775396c0977d8dba5d942464`

## Mother problem

> How can a learner infer that a plausible linguistic form is restricted or unavailable when it mainly receives positive examples rather than explicit correction?

This is the classic Gold / negative-evidence / Baker's-paradox family and is independent of LMs.

## Mature rival accounts

The overgeneralization literature distinguishes at least:

- **entrenchment:** many opportunities to see a verb / form without the unattested construction make absence informative;
- **statistical preemption:** a conventional competitor expressing the relevant function blocks the unattested alternative.

Controlled human artificial-language experiments now directly discriminate these accounts and provide strong evidence for preemption under several conditions.

## Current LM program

The 2024–2026 controlled-learning literature directly studies:

- learning a missing rare construction from related positive evidence;
- controlled exposure and cross-construction generalization;
- direct vs indirect evidence;
- preemption vs entrenchment;
- verb-specific vs abstract preemption.

Two 2026 papers even appear to disagree: one reports causal evidence for statistical preemption, while a controlled-rearing study finds no clear verb-specific preemption and only weak abstract preemption.

## Why the apparent disagreement did not become a question

It fails the repository's strict SAME-TREATMENT requirement:

- pretrained model + targeted fine-tuning vs controlled rearing from child-caregiver input;
- increasing / manipulating competing evidence vs deleting classes of evidence during acquisition;
- verb-specific vs abstract-level effects.

The honest remaining question is therefore initially `which design difference explains the two papers?`, which is frontier-paper reconciliation rather than a durable mother problem.

## Decision

**WALL-J exhausted as current generator.**

Do not regenerate Baker's paradox × LLM, preemption-vs-entrenchment on another construction/model, or Guo-vs-Wang reconciliation by swapping the training regime.

---

# 4. WALL-K — Advance planning in autoregressive generation

Audit:
- `search_rounds/2026-09-15_WALL_K_AUTOREGRESSIVE_ADVANCE_PLANNING_EXHAUSTION.md`

Commit:
- `3ca4b6c65dee5e44086e226e29f781a11ceb8374`

## Mother problem

> How much of a sequential linguistic action is planned in advance before the current production unit is executed?

Human sentence-production research has a long dispute over highly incremental / word-sized vs phrasal / hierarchical planning, with evidence that planning scope can be structurally larger than the next word and can vary with task / experience / accessibility.

## Direct modern owner

Wu, Morris & Levine, COLM 2024, ask almost exactly whether Transformers **plan ahead for future tokens**.

They distinguish:

- **pre-caching:** compute features now specifically because later predictions need them;
- **breadcrumbs:** current-useful features happen also to be future-useful.

Their `myopic training` operation removes future-loss gradients into earlier hidden-state computations, making this much stronger than a probe for future-token information.

Natural-language results lean toward breadcrumbs at smaller scales, while pre-caching grows with model scale.

## Strongest residual and why it dies

The obvious return to the old theory is:

> If a Transformer plans ahead, is its natural scope a fixed token horizon or a structural unit such as a phrase / clause?

But the phrase is privileged by a human production theory, not by an independent theory of decoder-only LM computation.

Reviewer compression succeeds:

> `psycholinguistic planning-scope dispute + Wu-style future-token intervention.`

That is precisely an old psychological phenomenon × LM/mechanistic-tool project.

The human analogy also cannot supply a linking hypothesis because WALL-F already established that similar behavior / mechanism does not automatically make an LM a human model system.

## Decision

**WALL-K exhausted as current generator.**

Do not regenerate future-token probes, planning-horizon metrics, phrase/clause bins, myopic-training on a bigger model, or `scale creates planning`.

---

# 5. Why this is a healthy zero-survivor round

The three walls died for **different scientific reasons**:

| wall | durable old problem? | real pressure? | why current candidate space closes |
|---|---|---|---|
| WALL-I — closed-loop recovery | yes | failed compounding-error prediction / self-recovery | generic explanatory variable is already recoverability / stability theory |
| WALL-J — positive evidence → restriction | yes | mature preemption vs entrenchment disagreement + fresh LM tension | core estimands now directly owned; newest disagreement is not same treatment |
| WALL-K — advance planning | yes | long word-vs-phrase planning-scope dispute | vanilla LM future-specific computation already directly owned; structural-scope transplant lacks model-native theory |

This is qualitatively different from:

> latest paper → missing cell → owner search → kill.

No wall was opened because a current paper had a convenient limitation. Each wall survived deletion of recent papers before the current owner map was consulted.

---

# 6. New anti-resurrection state from this round

Until a genuinely new inference appears, suppress:

## WALL-I family

- modern-LLM exposure bias reruns;
- prefix-corruption self-recovery studies;
- generic recovery / contraction / error-half-life metrics;
- `do reasoning errors compound?` surveys;
- teacher-forced vs free-running hidden-state distance as a paper;
- He 2021 + imitation-learning recoverability transfer.

## WALL-J family

- negative evidence / Baker's paradox × LLM;
- preemption-vs-entrenchment on another construction/language/model;
- direct-vs-indirect evidence on another syntactic pattern;
- verb-specific-vs-abstract preemption;
- fresh-paper reconciliation by changing acquisition regime;
- unseen-construction learning from neighboring positives as a new parent.

## WALL-K family

- probes for future-token information;
- planning-horizon / future-information-radius metrics;
- phrase / clause bins without an independent LM causal theory;
- myopic training on newer or larger models;
- `scale increases lookahead`;
- psycholinguistic planning-scope tasks as evidence about human cognition;
- explicit lookahead method comparisons as the scientific contribution.

---

# 7. Portfolio consequence

This round creates:

- **new L-series:** 0;
- **new pilot authorization:** 0;
- **new validated mainline:** 0.

It does **not** upgrade L40.

L40 remains exactly:

> **`PILOT-AUTHORIZED — E01 ONLY`**

with its mother phenomenon, effect size, present-state matching feasibility, and theory-specific crossover still awaiting experiment.

The round also does not reopen WALL-D/F/G/H, lexical-event structure, or the current IP03 route.

---

# 8. Generator diagnosis after I–K

The searcher is functioning better when it asks:

> **What old scientific prediction failed, and what explanatory variable did the mature field invent to absorb the failure?**

WALL-I is the clearest example. Merely discovering a contradiction was not enough; the cross-field lineage showed that the apparently missing concept (`recoverability`) already exists.

The second useful question is:

> **Are two impressive current results actually different estimates of the same quantity?**

WALL-J shows why strict intervention semantics matter: an apparent `yes preemption / no preemption` reversal dissolved once learner regime and treatment were aligned.

The third is:

> **Is the old theory's natural unit also natural for the modern model, or are we importing it by analogy?**

WALL-K shows that `phrase` is a theoretically meaningful planning unit for human production, but not automatically a causal unit of Transformer foresight.

These three questions should remain in the generator itself.

---

# 9. Reopening criterion for the next search

The next wall should leave the vocabulary of recovery, negative evidence / preemption, and advance planning.

Prefer one of:

1. a classic theory with a **known failed prediction** whose usual repair is itself now under pressure;
2. a long-standing law whose **load-bearing premise** is specifically broken by foundation-model learning / inference;
3. an old non-identifiable question for which a modern operation creates **opposite theory predictions**, not merely more observability;
4. a durable annoyance visible in a multi-year author lineage that is not already a named active LM program.

Do not narrow WALL-I/J/K further. Do not treat their newest direct owners as seed papers for adjacent cells.

---

# 10. Round decision

**WALL-I:** EXHAUSTED AS CURRENT GENERATOR.  
**WALL-J:** EXHAUSTED AS CURRENT GENERATOR.  
**WALL-K:** EXHAUSTED AS CURRENT GENERATOR.  
**New candidate:** NONE.  
**New L-series:** 0.  
**New pilot:** 0.  
**L40:** unchanged, unvalidated `PILOT-AUTHORIZED — E01 ONLY`.

The scientific-search standard is preserved:

> **Question first. Old intellectual ancestry. Natural object. Modern identifying leverage. Both answers matter. One decisive quantity. High best-case consequence.**
