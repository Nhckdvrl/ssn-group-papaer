# 2026-09-15 — Problem-Taste Recalibration + WALL-E Update

**Target:** ACL / EMNLP / NAACL Main  
**Taste calibration:** TACL / ICLR / ICML / NeurIPS / AAAI  
**Mode:** SEARCHER RECALIBRATION + ONE-WALL IMMERSION  
**Outcome:** **0 new L-series; 0 new pilot authorization.**  
**Interpretation:** the searcher found one genuinely strong first-layer question, then stopped when the *mother question itself* proved to be an active modern research program. It did **not** shrink the question into an identification residual.

---

# 0. Entry state

This pass starts after the repository added the Natural / Counterintuitive Question Gate.

The key correction is retained:

> **Easy to state. Hard to explain.**

not:

> **Hard to state. Clever to identify.**

In particular:

- L41 remains `PILOT-AUTHORIZED — E01 ONLY`, but its implicative checkerboard is **not** a template for new topic generation.
- L40 remains an authorized bounded pilot, but its cue-class × grammatical-function identification should **not** become the default way to mine WALL-E for increasingly fine-grained residuals.
- L36 remains a useful taste calibrator because its first-layer pressure is immediate: more search should help, yet sufficiently wide search can catastrophically hurt.

No existing L-series is promoted by this file.

---

# 1. Searcher recalibration from strong recent work

The purpose of reading the papers below was **not** to copy their topic. It was to ask why their first-layer questions are compelling before hearing the method.

## 1.1 Subliminal learning — a high-quality anomaly calibrator

Cloud et al., Nature 2026, show that a student can inherit a teacher's behavioral trait from training data that are semantically unrelated to that trait, including number sequences, reasoning traces, and code. The effect depends strongly on a shared / behaviorally matched base model.

Source:
- https://www.nature.com/articles/s41586-026-10319-8

The useful taste lesson is not `study another hidden trait` and not `mechanistically localize subliminal learning`.

It is the shape of the pressure:

> **The human-visible semantic content of a training example need not characterize what the example teaches a neural learner.**

That is a fact about the learning operator, not an empty benchmark cell.

---

## 1.2 Negative reasoning trajectories — correctness of an example is not identical to usefulness as training evidence

Tian et al., ACL 2026, report that adding incorrect reasoning trajectories to SFT can improve out-of-domain generalization over positive-only training; the paper further analyzes valid intermediate reasoning, training dynamics, entropy, and overfitting.

Source:
- https://aclanthology.org/2026.acl-long.1370/

Again, do **not** generate `wrong examples on another task`.

Taste lesson:

> **The label `correct / incorrect` is not a sufficient scientific description of an example's learning effect.**

---

## 1.3 Mosaic memory — semantic similarity is not necessarily the dominant similarity for memorization

Shilov, Meeus & de Montjoye, Nature Communications 2026, show that fuzzy duplicates can contribute strongly to memorization and that the relevant contribution is predominantly syntactic rather than semantic in their setting.

Source:
- https://www.nature.com/articles/s41467-026-68603-0

Taste lesson:

> **The similarity relation that matters to a learner can differ sharply from the relation a human would naturally use to describe the data.**

---

# 2. Provisional standing friction — semantic content ≠ learning content

This pass does **not** promote a new candidate from the three papers above.

But they independently strengthen a useful standing friction:

> **When a foundation model trains on an example, what properties of that example actually determine the direction and generality of the resulting learning?**

A shorter version is:

> **What does an example actually teach a model?**

This is deliberately broader than L41. L41 asks whether sentence-level semantic commitment controls one particular form of persistent factual uptake. The standing friction here is that several distinct learning phenomena suggest human semantic descriptions such as:

- what the example says;
- whether it is correct;
- whether it is semantically similar;

may fail to specify the example's effective learning content.

### Current status

**WATCH / STANDING FRICTION — NOT A CANDIDATE, NO IP NUMBER YET.**

Why not promote it now:

1. it is currently too broad to be a paper question;
2. the three frontier phenomena have different training regimes and observables;
3. merely placing them under one umbrella would be `Paper A + Paper B + Paper C` synthesis, not a scientific contribution;
4. a future project would need an independently motivated quantity or law that predicts the learning effect across cases, not another taxonomy or benchmark.

This is exactly where the Standing Important Problems Portfolio should be useful: keep the question alive **without forcing an experiment today**.

---

# 3. One-WALL immersion: WALL-E / current competence versus future learnability

The strongest natural question encountered in this pass bears directly on the repository's existing IP18 / WALL-E.

## 3.1 10-second test

### Question

> **Why can a model that is better now be a worse learner later?**

A stricter state-theoretic form is:

> **If two learners are equally capable now, can their learning histories still make one much easier to teach later?**

### Pressure

> We normally evaluate a base model by what it currently predicts, yet modern plasticity results show that current performance and ability to learn from the next data can diverge — and can even trade off.

This is a substantially more natural first-layer question than immediately asking whether the hidden state is attached to a cue class, construction, feature, gradient direction, or representation.

It passes the researcher-interest, longevity, best-case consequence, and both-answers-matter tests.

---

# 4. Intellectual lineage / modern owner audit

## 4.1 The mother problem predates LLMs

WALL-E already records the older path-dependence and stability–plasticity ancestry: the present input–output state of a learner need not specify how the learner will respond to future evidence.

That ancestry remains valid.

## 4.2 Nature 2024: future learning ability is already an explicit scientific object

Dohare et al., *Loss of plasticity in deep continual learning*, systematically show that standard deep networks lose the ability to learn after extended continual training. They explicitly distinguish loss of plasticity from catastrophic forgetting.

Source:
- https://www.nature.com/articles/s41586-024-07711-7

This already establishes the conceptual separation:

> **current/old-task competence ≠ future learning ability.**

## 4.3 NeurIPS 2023: `language plasticity` is already a direct training target

Chen et al., *Improving Language Plasticity via Pretraining with Active Forgetting*, explicitly train pretrained language models to become easier to adapt to new languages by periodically resetting embeddings during pretraining.

Source:
- https://proceedings.neurips.cc/paper_files/paper/2023/hash/6450ea28ebbc8437bc38775157818172-Abstract-Conference.html

Thus `make a language model more plastic during pretraining` is not an unowned modern translation of an old concept.

## 4.4 ICML 2026: base-model quality and downstream adaptability can reverse

Han, Bordt, Zhang & Kakade, *Weight Decay Improves Language Model Plasticity* (ICML 2026), study pretraining hyperparameters from the standpoint of downstream plasticity. Larger weight decay can make models more plastic, and the paper reports the counterintuitive regime in which a model with worse pretraining validation loss performs better after fine-tuning.

Sources:
- https://arxiv.org/abs/2602.11137
- https://icml.cc/virtual/2026/poster/60527

This is extremely close to the natural first-layer tension:

> `better base model` and `better future learner` need not be the same ranking.

## 4.5 2026 scale audit: scale delays but does not obviously remove the problem

Hernandez-Garcia, Figliolia & Millidge, *Can Scale Save Us From Plasticity Loss in Large Language Models?*, study Transformer LMs across scale and report that the onset of measurable plasticity loss increases sublinearly with model size, while scaling alone does not appear sufficient to eliminate it. They also report evidence under stationary multilingual training rather than only abrupt continual-task shifts.

Source:
- https://arxiv.org/abs/2606.24752

This matters because the natural escape hatch — `plasticity loss is only a small-model continual-learning artifact` — is no longer safe.

---

# 5. Why WALL-E does NOT produce L42 in this pass

The first-layer question is excellent:

> **Why can a model that is better now be a worse learner later?**

But the correct response to a good, already-owned mother question is **not** to keep narrowing until a free experimental cell appears.

The modern literature now directly owns:

- loss of future learning ability as a distinct quantity;
- language-model plasticity as a training objective;
- pretraining hyperparameters that trade current validation loss against future adaptability;
- scaling behavior of plasticity loss in Transformer language models.

The tempting residual is:

> `match two models on current behavior / loss, give them the exact same next training data, and ask whether different histories still produce different learning.`

Scientifically, this is a legitimate identification test for WALL-E.

But **as a topic generator**, promoting it now would repeat the failure mode that motivated the Natural Question Gate:

> mother question already owned  
> → add stricter state matching  
> → obtain a beautiful causal distinction  
> → mistake improved identification for a new Main-level scientific question.

That is not enough.

The old path-dependence literature already supplies the conceptual possibility, while the modern plasticity program supplies the foundation-model relevance. A same-current-state experiment could be useful evidence **inside** that program, but we do not currently have an independently important residual belief that would make it a new paper identity.

### Verdict

**WALL-E remains an important standing problem, but its current generic competence-vs-plasticity surface is CLOSED AS A NEW TOPIC GENERATOR.**

This does **not** kill L40's already-authorized bounded E01. It means only that future open-ended search should not keep mining WALL-E for finer `history remains after matching X` cells unless new evidence creates a genuinely new first-layer question.

---

# 6. Other pressure pools inspected but not promoted

## Uncertainty / disagreement after reasoning or RL

There is real modern evidence that reasoning/post-training can worsen disagreement modeling, abstention, or calibration in some regimes.

However, the repository's L09 already preserved the behavioral parent and archived the `erased vs suppressed` mechanism route. The nearby entropy/diversity/calibration program is dense.

**Decision:** no resurrection through a new uncertainty metric, hidden-state probe, or RL variant.

## Stronger teacher → worse student

This is an excellent natural-question calibrator because it violates the naïve monotonicity `better teacher → better student`.

But knowledge-distillation capacity gap, fidelity/generalization tension, and recent LLM distillation work already form a mature program.

**Decision:** taste calibrator, not a candidate source.

## In-context learning without use / inert knowledge

Recent work reports that models can encode newly learned semantics in context while struggling to deploy them reliably.

The first-layer question is interesting, but current descendants collide with the repository's reusable-abstraction/accessibility problems and with direct 2026 owners.

**Decision:** no `behavior → hidden representation → patching` sequel.

---

# 7. Searcher belief update

This pass adds three rules to the current belief state.

## Rule A — a beautiful first-layer question can still be unavailable

`Why can a model that is better now be a worse learner later?` passes the natural-question gate.

That does **not** mean we should manufacture a project after discovering that the modern literature already treats plasticity as a first-class scientific object.

A good question being owned is a successful taste judgment, not a reason to shrink the question.

## Rule B — cross-paper convergence should update the standing portfolio before it generates a candidate

Subliminal learning, learning from negative trajectories, and mosaic memory all weaken simple human-semantic descriptions of training evidence.

The correct immediate action is:

> preserve `what does an example actually teach a model?` as a standing friction.

The incorrect action is:

> connect the three papers, invent a metric, and call the connection a contribution.

## Rule C — modern leverage must change the scientific inference, not merely tighten control

Exact checkpoints, matched future data, interventions, and causal controls can make an experiment cleaner.

They create a new paper only when the cleaner experiment resolves an uncertainty whose **answer itself** matters independently of the instrument.

This is the main correction to the recent theory-identification autocomplete failure.

---

# 8. Portfolio consequence

This round creates:

- **new L-series:** 0;
- **new pilot authorization:** 0;
- **new K-series kill:** 0;
- **new validated mainline:** 0.

It updates the standing state as follows:

1. **WALL-E / IP18 remains scientifically important.**
2. **Generic competence-vs-plasticity descendants are now suppressed as a topic generator** because the first-layer modern program is already direct and dense.
3. **`Semantic content ≠ learning content` is retained as a WATCH-level standing friction, not yet an IP and not a candidate.**
4. L40 and L41 keep exactly their pre-existing bounded authorization; neither is upgraded by this round.
5. Open-ended search should now switch to a genuinely new scientific object rather than finding a narrower WALL-E residual.

The desired next move is again:

> **calibrate taste → update standing problems → choose a new WALL → wait for a natural question → only then audit ownership and identification.**
