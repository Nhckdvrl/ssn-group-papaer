# S09 — Same Recall, Different Stability? Does Learning History Determine What Can Be Changed?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Target venues:** ACL / EMNLP / NAACL Main  
**Scientific type:** training dynamics / parameter memory / stability–plasticity / mechanistic follow-up optional

## 1. Stable parent question

Two parameter memories can be equally accessible at the present checkpoint yet have arrived there through different learning histories.

The stable parent question is:

> **Is present memory accessibility sufficient to predict future editability, or can equally accessible parameter memories differ in stability because of how and when they were learned?**

A shorter formulation is:

> **Memory accessibility ≠ memory stability?**

“Memory age” is the primary causal axis in the first pilot, but the paper must not assume in advance that chronological age itself is the governing variable. Acquisition time, exposure recency, intervening training, and history-dependent parameter organization are competing explanations.

This is not a paper about generic catastrophic forgetting, knowledge-editing benchmark performance, or “training order matters.”

## 2. Scientific pressure

Several independent literatures leave a quantity separation unresolved.

1. **Early memorization / crystallization.** BlackboxNLP 2024 reports that examples entering a memorized state early are disproportionately likely to remain memorized throughout training. The authors explicitly note that a controlled placement experiment is needed before interpreting this causally.

2. **Training-order / recency traces.** ICLR 2026 *Fresh in Memory* shows that LLM activations encode when information was encountered during sequential fine-tuning. Re-exposure moves an item toward the “recent” end, while substantial training-order information persists even after mixed-data training. The signal is not reducible to simple loss or confidence differences.

3. **Knowledge-update resistance.** ACL 2024 *Forgetting before Learning* shows that pre-existing parametric knowledge can obstruct learning contradictory replacement knowledge; removing old knowledge first improves updating.

4. **Memorization strength is not a complete description of memory state.** ACL 2026 REMIND finds distinct local loss-landscape geometry for different memory/unlearning states even when pointwise losses overlap.

5. **Global plasticity can decrease with training.** Continual-learning work, including *Loss of Plasticity in Deep Continual Learning* and later GPT-style Transformer studies, establishes that a network’s overall ability to learn new information can change over training time.

Taken together, these results do **not** yet answer:

> If two facts are equally retrievable now, are they equally easy to rewrite next?

That is a different quantity from current recall, current confidence, or historical training-order decodability.

## 3. Competing worlds

### World A — Accessibility is sufficient

Once current memory strength/accessibility is matched, learning history adds no predictive value for future contradictory learning.

Predictions:
- old/new memories with matched current logit margin and recall show overlapping overwrite curves;
- any apparent age effect disappears after controlling present strength and exposure recency;
- training-order representations may be historical traces without functional consequences for future plasticity.

### World B — History-dependent entrenchment

Learning history changes a memory’s future plasticity in a way not visible from current accessibility alone.

Predictions:
- equally accessible earlier-acquired memories require more contradictory evidence / gradient steps to replace;
- the effect survives a common final refresh that equalizes recent exposure;
- current recall and confidence underdescribe the state of parameter memory.

This would support a consolidation/entrenchment-like law, but the pilot should initially claim only **history-dependent stability**, not a specific biological analogue.

### World C — Recency-governed stability

The apparent “age” effect is primarily a consequence of how recently a memory was reinforced.

Predictions:
- without refresh, early and late memories differ in overwrite dynamics;
- after a common terminal refresh and matching present accessibility, the difference collapses or reverses;
- last exposure / reinforcement recency, not first acquisition time, is the better state variable.

A reverse effect—older memories being easier to overwrite after strength matching—would also be scientifically informative and would reject a simple entrenchment story.

## 4. Nearest-prior ownership boundary

S09 does **not** claim:

- first evidence that training order matters;
- first evidence of catastrophic forgetting;
- first evidence that older and newer data have different current memorization;
- first evidence that LLMs encode training-order recency;
- first evidence that old parametric knowledge can interfere with updates;
- first study of knowledge editing or unlearning.

The closest threat is ICLR 2026 *Fresh in Memory*, whose future-work discussion asks whether models might use training-order information to resist modification. That is nearby but not the same parent RQ.

S09 asks a more basic learning-dynamics question:

> **Does learning history change the future plasticity of a parameter memory beyond what is visible from its present accessibility?**

This question remains natural if *Fresh in Memory* is removed: it is independently motivated by memorization crystallization, knowledge-update resistance, age-of-acquisition effects in connectionist learning, and the stability–plasticity problem.

Reviewer-level novelty sentence:

> Prior work separately measures when information was learned, how strongly it is currently remembered, and whether conflicting knowledge can be written. S09 tests whether **current memory strength is sufficient to predict future rewriting**, or whether learning history leaves a hidden stability state.

If a prior is found that counterbalances item identity, matches current accessibility, varies acquisition history, and then directly compares contradictory-update learning curves in the same model, S09 must be re-audited.

## 5. Minimum pilot

Use one small open decoder-only LM first (roughly 0.5B–1.5B is sufficient) and a few hundred cheap novel alias→attribute facts. Synthetic aliases are an **identification instrument**, not a benchmark.

### Step 1 — Counterbalanced acquisition-history manipulation

Create two matched fact sets A and B.

Run mirrored schedules from the same base checkpoint:

- **Run 1:** A is learned early; B is learned late.
- **Run 2:** B is learned early; A is learned late.

Keep fixed:
- fact identities across the mirrored runs;
- number of exposures per fact;
- templates / token counts as closely as possible;
- optimizer and learning-rate schedule;
- intervening filler stream;
- total training-data multiset.

This crossover design makes each fact serve as its own early/late control across runs and prevents “some facts are inherently easier to memorize” from masquerading as an age effect.

### Step 2 — Measure present accessibility

At the final checkpoint record, per fact:

- exact recall;
- target-vs-foil logit margin / log-odds;
- held-out paraphrase recall using a small fixed template set.

Do not define memory strength using accuracy alone.

Analyze overwrite dynamics conditional on current accessibility. Use a pre-specified matching/regression rule rather than hand-selecting convenient examples after seeing outcomes.

### Step 3 — Common-refresh identification

Repeat or extend the schedule with a **common terminal refresh**: both early and late fact sets receive the same final exposure block immediately before the contradictory-update phase.

This is load-bearing.

It separates:

- simple last-exposure recency;
- current accessibility;
- deeper acquisition-history effects.

The point is not to make early and late memories numerically identical by arbitrary extra training. It is to apply the same refresh operation to both groups and test whether an earlier history remains predictive after present-state controls.

### Step 4 — Identical contradictory update

At the same final checkpoint, train contradictory replacements for early and late facts **together in the same minibatches**, using identical optimizer state and update conditions.

Track per fact:

- change in new-vs-old answer logit margin;
- initial contradictory-learning slope;
- steps/tokens to cross zero margin;
- overwrite AUC over a short fixed training horizon.

The main result is the **learning curve under matched contradictory evidence**, not final edit accuracy.

## 6. Why the pilot is identifiable

The main confounds are handled directly:

- **Item difficulty:** mirrored early/late assignment across runs.
- **Different update-time global plasticity:** all contradictory replacements are learned together from the same checkpoint.
- **Exposure count:** held constant in the core comparison.
- **Last-exposure recency:** tested with the common-refresh condition.
- **Current memory strength:** measured continuously and explicitly controlled/matched.
- **Optimizer-stage artifact:** the overwrite comparison uses one shared optimizer/model state; acquisition-order conclusions are replicated under mirrored schedules.

The first pilot does **not** need to prove a biological “consolidation” mechanism. It only needs to establish or reject history-dependent editability beyond current accessibility.

## 7. Pilot outcomes

### Outcome A — Curves collapse after strength control / common refresh

Current accessibility is sufficient. Training-order traces do not imply hidden stability.

**Knowledge gain:** parameter memory can be approximately characterized by present strength for the purpose of future rewriting; age-like historical signals may be epiphenomenal.

### Outcome B — Early memories remain harder to rewrite

Learning history leaves a hidden stability variable not visible in present recall.

**Knowledge gain:** two behaviorally equivalent parameter memories can have different future learning dynamics; memory state is not one-dimensional.

### Outcome C — Difference exists before refresh but disappears after refresh

Stability is governed mainly by recent reinforcement/exposure rather than acquisition age.

**Knowledge gain:** the relevant temporal variable is recency, not “memory age,” connecting training-order traces to functional plasticity.

### Outcome D — Early memories are easier to rewrite after matching accessibility

This rejects simple consolidation and reveals the opposite history-dependent geometry.

**Knowledge gain:** later acquisition may occupy more update-resistant parameter directions despite equal present recall.

All principal outcomes teach something about parameter-memory dynamics.

## 8. Pilot discipline

- one small open model first;
- a few hundred controlled facts, not a benchmark;
- two mirrored assignments / seeds before any model-family expansion;
- no knowledge-editing method zoo;
- no large real-world temporal dataset;
- no mechanism/probing first;
- no claim that “old knowledge is consolidated” unless the behavioral law survives the refresh and strength controls;
- pre-register the matching/regression rule and overwrite metrics before reading the decisive curves.

## 9. Zhao/Cho-style mechanistic path if the behavioral law survives

Mechanism comes **after** the law.

1. **Representation:** test whether accessibility-matched memories occupy distinguishable history/recency representations.
2. **Computation:** determine whether those states predict local update sensitivity, gradient alignment, or loss-landscape curvature.
3. **Causality:** manipulate the history/recency-associated state or the identified update-sensitive direction and test whether overwrite dynamics change.
4. **Component localization:** only if necessary, identify parameter/pathway structure implementing the stability difference.

Do not turn the project into “find a training-order vector.”

## 10. Claim boundary

Do not turn S09 into:

- generic continual-learning stability–plasticity optimization;
- a knowledge-editing benchmark;
- unlearning evaluation;
- privacy memorization;
- “training order affects accuracy”;
- “early examples are remembered better”;
- Fresh-in-Memory representation replication;
- a biological memory-consolidation analogy paper.

The stable scientific object is:

> **whether present memory accessibility fully specifies future plasticity, or whether learning history leaves hidden stability.**

## 11. Kill conditions after pilot

Kill or fundamentally reframe S09 if:

1. accessibility-matched early/late memories show no reproducible difference in contradictory-update dynamics across mirrored schedules;
2. any apparent effect is completely explained by current logit margin / last-exposure recency and there is no broader quantity separation left;
3. the result requires post-hoc cherry-picking of facts or large exposure mismatches to appear;
4. a direct prior is found that already performs the same matched-history → future-editability identification.

## 12. Promotion status

**PILOT-AUTHORIZED.**

The topic passes because:

- the mother question is independently motivated by several literatures rather than one paper’s future-work sentence;
- reviewer-level overlap is normal, but no located prior owns the decisive quantity separation;
- the crossover + common-refresh + shared contradictory-update design removes the main identifiability blockers with a small experiment;
- the pilot is cheap and does not require a benchmark, model zoo, or large dataset;
- strength-only, history-dependent, recency-dominated, and reverse-history outcomes all produce distinct scientific conclusions;
- the paper can grow Zhao/Cho-style into mechanism only if the behavioral law exists, without making mechanism the mother question.
