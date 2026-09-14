# 2026-09-14 — Standing State Expansion II

**Mode:** LONG-TERM RESEARCH STATE EXPANSION  
**Candidate generation:** **OFF**  
**L-series / K-series:** **NO CHANGES**  
**Pilot authorization:** **NONE**  
**Input:** existing `STANDING_IMPORTANT_PROBLEMS_STATE`, taste selection, WALL-A/B/C/D immersion, friction dossiers, WALL-B disagreement map, and the new idea-genesis doctrine that frontier papers may update but may not create standing problems.

---

# 0. Why this pass exists

The first standing-state pass produced four active wall problems:

- WALL-A — reusable abstractions;
- WALL-B — formation of inductive bias;
- WALL-C — selection among representable algorithms;
- WALL-D — structure from resource constraints.

Those walls were productive, but they remain biased toward questions already visible from language / mechanistic-interpretability programs. This pass deliberately searches **outside those four walls** for durable scientific objects that satisfy a stronger test:

> Would we still care about this problem if the 2025–2026 frontier papers that reminded us of it did not exist?

The main new object below was reconstructed **from old learning theory first**, before importing current foundation-model evidence. Recent papers are therefore evidence that bears on the problem, not its source.

---

# 1. NEW ACTIVE STANDING PROBLEM

## IP18 / WALL-E — When is a learner's current behavior a sufficient state description for its **future learning**?

### Standing question

Two learners can currently make the same predictions, achieve the same task accuracy, or even realize nearly the same input–output function after **different learning histories**.

Are they then genuinely in the same learning state?

Or can history leave a latent developmental state that is invisible in current behavior but determines:

- what the learner can acquire next;
- how quickly it can acquire it;
- which evidence it will ignore or amplify;
- which generalization it will make;
- which previously silent knowledge can reappear;
- how plastic or entrenched different parts of the system have become?

The compact wall question is:

> **Is the current function a sufficient statistic for future learning, or does developmental history remain a causal state variable after current behavior has been matched?**

This is a learning-theory question, not a curriculum-effect question.

---

# 2. Why WALL-E exists independently of modern LMs

## 2.1 Path dependence is an old scientific object

Ghirlanda & Enquist (2007), *How training and testing histories affect generalization: a test of simple neural networks*, explicitly frame **path dependence** as a general problem in learning:

> different experience histories can initially produce the same behavioral effect, yet reveal important differences under later tests because the histories created different internal states.

Source:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2323563/

This is exactly stronger than the generic statement that "training order matters."

The identifying shape is:

1. different histories;
2. matched current behavior;
3. **same subsequent treatment**;
4. divergent later response.

The scientific implication is that the matched behavior did not fully specify the learner's state.

A broader associative-learning review makes the same point using reacquisition, extinction, counterconditioning and other path-dependent phenomena: behavioral equality can conceal different stored states and therefore different reactions to a common later treatment.

Source:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2746498/

The historical debate is therefore not about neural-network optimization. It is about **what counts as the state of a learner**.

---

## 2.2 Stability–plasticity is a second, partially independent ancestry

Biological and artificial learning systems face a long-standing stability–plasticity problem:

- too much plasticity destroys old structure;
- too much stability prevents new learning.

This problem predates modern deep learning and is closely related to age-limited learning, entrenchment, catastrophic interference, and continual adaptation.

A useful review is:
- Mermillod, Bugaiska & Bonin (2013), *The stability-plasticity dilemma: investigating the continuum from catastrophic forgetting to age-limited learning effects*.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3732997/

The important conceptual point for WALL-E is that **current competence and future learnability are distinct quantities**. A learner can still perform the old task while having become much less capable of changing in response to new evidence.

---

## 2.3 Critical-period theory makes the developmental-state issue explicit

The human-language critical-period debate asks whether later loss of language-learning ability arises from:

- an innately programmed maturational change; or
- stabilization / entrenchment produced by experience itself.

This is already a theory about hidden developmental state: two learners exposed to the same new language may react differently because of where they are in development, even if ordinary current-task competence does not reveal the relevant plasticity state.

The problem is old; modern LMs only give a new model system in which histories and mechanisms can be experimentally controlled.

---

# 3. What modern neural models add — and what they do NOT add

The modern regime matters only if it changes the inference.

## Old evidence could establish

> Different histories can leave behaviorally hidden consequences for generalization, relearning, extinction, or later adaptation.

But in biological learners the latent learning state is hard to inspect and histories are difficult to match exactly.

## Modern neural learners additionally allow

- byte-identical future training data after different histories;
- exact checkpointing throughout development;
- matching learners on selected current input–output behavior before the common treatment;
- direct comparison of gradients, update geometry, parameter / representation changes and later trajectories;
- reversible / controlled interventions on candidate state variables;
- many independent learners with identical architecture and controlled histories.

These operations potentially let us ask a stronger question:

> **What state variables are sufficient to predict the effect of the next identical learning event?**

That is an inferential gain over simply observing that order matters.

---

# 4. Frontier evidence that updates WALL-E

These papers do **not** generate WALL-E. They update beliefs inside it.

## E-EV1 — Deep networks can lose future plasticity while the scientific object is distinct from forgetting

Dohare et al., *Loss of plasticity in deep continual learning*, Nature 2024, show that standard deep networks progressively lose ability to learn under continual training. The paper explicitly distinguishes plasticity loss from catastrophic forgetting: the object is degraded ability to learn new things, not simply loss of old-task performance.

Source:
- https://www.nature.com/articles/s41586-024-07711-7

**Update:** present performance and future update capacity can dissociate at scale. This strongly supports treating future learnability as its own state variable.

---

## E-EV2 — Plasticity loss is not one mechanism

Lyle et al., ICML 2023, connect plasticity loss to changes in loss-landscape curvature and show it can occur without the simple saturated-unit explanation.

Lyle et al., CoLLAs 2025, then explicitly decompose plasticity loss into multiple partially independent mechanisms and show that intervening on one is not sufficient in all regimes.

Sources:
- https://proceedings.mlr.press/v202/lyle23b.html
- https://proceedings.mlr.press/v274/lyle25a.html

**Update:** there may be no single scalar called "plasticity state." Different latent causes can produce the same reduced future learnability.

This is a real friction, not a reason to invent another plasticity metric.

---

## E-EV3 — Early experience can bias later learning, but experience alone does not automatically generate a human-like critical period

Constantinescu, Pimentel, Cotterell & Warstadt, TACL 2025, manipulate age of language exposure in neural LMs. Their models do not spontaneously show the human-like delayed-L2 critical-period effect; introducing an explicit regularizer that reduces plasticity partway through training can produce the effect.

Source:
- https://aclanthology.org/2025.tacl-1.5/

**Update:** "more prior experience" is not itself a sufficient developmental-state theory. A mature account must say **what changes in the learner** such that future evidence is processed differently.

---

## E-EV4 — Primacy bias shows that early experience can distort the rest of learning

Nikishin et al., ICML 2022, identify primacy bias in deep RL: early interactions can be over-relied upon and useful evidence encountered later can be underused; partial resets mitigate the effect.

Source:
- https://proceedings.mlr.press/v162/nikishin22a.html

**Update:** learning history can alter later evidence utilization rather than merely leave a static representation.

---

# 5. Real unexplained frictions inside WALL-E

These are **not questions yet**.

## E-FR1 — Same current behavior does not imply same future response to learning

This is the classical path-dependence pressure.

A state description that only predicts current outputs can be scientifically insufficient even when it is behaviorally complete on the current task.

**Friction strength: VERY HIGH.**

---

## E-FR2 — Future learnability can degrade without ordinary forgetting

Plasticity loss and catastrophic forgetting are separable. Therefore an endpoint evaluation can say:

> the model still knows X

while missing:

> the model has become unable to learn Y efficiently.

This means "capability at time t" and "learning operator at time t" are distinct scientific objects.

**Friction strength: VERY HIGH.**

---

## E-FR3 — The same path-dependent behavioral signature can arise from different latent causes

Candidate causes already present in mature literatures include:

- multiple coexisting memories / inhibitory learning;
- changes in associability;
- representational entrenchment;
- loss-landscape curvature;
- dormant / overcommitted units;
- changes in feature diversity;
- explicit maturation-like reductions in plasticity;
- acquired priors that change interpretation of later evidence.

Therefore:

> history matters

is not an explanation.

A useful scientific state must distinguish **which state variable carries history forward**.

**Friction strength: VERY HIGH.**

---

## E-FR4 — A learner's developmental state may be multidimensional

The plasticity literature already resists a single-mechanism account, while critical-period, associative-learning and inductive-bias literatures emphasize different consequences of history.

It may therefore be wrong to search for one scalar "age" or "plasticity" variable.

The eventual explanatory object may be a vector / structured state describing which computations remain revisable, which priors have become entrenched, and which old traces remain latent.

**Friction strength: HIGH.**

---

# 6. Boundary audit — why WALL-E is not just IP02, IP09, L19, or L34

This section is mandatory because otherwise the new wall would be a disguised resurrection.

## WALL-E vs IP02 / WALL-B — formation of inductive bias

WALL-B asks:

> why does a learner prefer generalization A over B under incomplete evidence?

WALL-E asks a different state question:

> after two different histories have been behaviorally matched **now**, are they equivalent with respect to the *next* identical learning event?

Inductive bias can be one consequence of developmental state, but WALL-E is not restricted to competing linguistic generalizations.

---

## WALL-E vs IP09 — generalizable computation vs task-local behavior

IP09 asks what training creates reusable computation rather than local task behavior.

WALL-E asks whether the current function / current competence is enough to predict **future updating**, or whether a hidden history variable remains necessary.

A model can have equally reusable current computation yet differ in future plasticity; conversely it can differ internally without producing a meaningful future-learning difference.

---

## WALL-E vs L19 — long→short transfer

L19 was a particular causal decomposition of a reported long-context SFT transfer result and was archived because the effect was too small / expensive to resolve in our regime.

WALL-E is not "does prior dataset property X transfer to Y?" and must not reuse L19's parent or matched-length design as an automatic instantiation.

---

## WALL-E vs L34 / access-conditioned learning pressure

The L34 post-mortem explicitly warns that a future successful result must establish **more than generic path dependence**, and that training order is generically non-commutative.

That warning is correct.

WALL-E therefore does **not** authorize:

- access → document vs document → access;
- curriculum A vs B;
- NEW–OLD subtractions;
- "order matters" experiments;
- repaired prospective encoding.

The wall exists at a higher theoretical level. A future descendant would need a mature rival theory about what developmental state is carried across the matched endpoint, not merely two orders that diverge.

Relevant repo boundary:
- `search_rounds/2026-09-14_ACCESS_CONDITIONED_LEARNING_PRESSURE.md`

---

# 7. Taste judgment for WALL-E

| dimension | judgment | reason |
|---|---:|---|
| scientific consequence | **5/5** | asks what constitutes the state of a learner and whether present function suffices to predict future learning |
| research intimacy | **5/5** | training dynamics, checkpoints, controlled histories, post-training, latent/state analysis are strong local skills |
| naturalness | **5/5** | path dependence / plasticity / development exist independently of benchmarks or LLMs |
| modern leverage | **5/5** | exact matched histories and identical future updates can make latent learning state experimentally accessible |
| search headroom | **3/5** | plasticity and continual-learning programs are active; generic formulations are heavily owned |

## State decision

**ADMIT IP18 / WALL-E AS ACTIVE — HIGH VALUE, GENERATOR STILL OFF.**

It belongs on the wall because we would still want the answer after deleting every 2025–2026 paper cited above.

But it is **not yet candidate-ready**. The next immersion must reconstruct the rival theories of developmental state / path dependence and determine where modern neural learners truly provide a new identifying operation rather than a more convenient training-order experiment.

---

# 8. NEW WATCH PROBLEM — credit assignment

## IP19 — How does aggregate outcome feedback change the decisions that actually caused the outcome?

This is a genuine standing scientific problem with deep RL / behavioral ancestry:

> delayed outcome is observed; which earlier action / reasoning step / internal decision receives credit or blame, and why?

The problem is important independent of LLMs and directly relevant to post-training.

However it should **not** become an active generator now.

### Why it is WATCH rather than ACTIVE

The 2025–2026 LLM-RL literature is already extremely dense:

- VinePPO (ICML 2025) directly reframes LLM reasoning RL around improved credit assignment;
- 2026 ACL work performs outcome-sensitive token/step attribution;
- multiple current reasoning / agentic RL methods use resets, rollout trees, prefix values, first-error localization and process supervision for fine-grained credit.

Representative sources:
- https://proceedings.mlr.press/v267/kazemnejad25a.html
- https://aclanthology.org/2026.acl-long.1132/
- https://aclanthology.org/2026.acl-long.504/

The repository also already killed **L10 — From Failure to Action** because current self-reflection / tool-error literature compressed the planned diagnosis→policy→action decomposition below the desired Main-level independent contribution.

### State decision

**IP19 — WATCH / CLOSED GENERATOR.**

Keep credit assignment in the long-term private state because it is scientifically central. Do not generate a new candidate from a fresh credit-assignment paper unless a genuinely different inferential level appears.

This entry exists partly to prevent future frontier papers from making the problem look newly discovered.

---

# 9. Things examined but NOT admitted as new walls

## 9.1 "Loss of plasticity" by itself

Not admitted separately.

It is evidence / a mechanism family inside WALL-E, not the whole scientific problem. Making it the wall would bias search toward the active continual-learning method literature.

---

## 9.2 Generic continual learning / catastrophic forgetting

Not admitted as a generator.

The field is mature and engineering-heavy, and the repository has already banned generic temporal-forgetting resurrection. The useful scientific object is not "retain old benchmarks" but the latent state controlling future learning.

---

## 9.3 Generic training-order effects

Rejected.

Neural optimization is path dependent in the trivial sense that non-commuting updates produce different parameters. That fact has little explanatory reward.

A useful descendant must show that **behaviorally matched endpoints remain developmentally nonequivalent in a theory-relevant way**.

---

## 9.4 Generic credit assignment in LLM reasoning / agents

Scientifically important, but owner density is already too high for direct generation. Recorded as WATCH IP19 instead.

---

# 10. Updated private wall state after this pass

The working wall is now:

### WALL-A — Reusable abstraction

What would make us believe the same abstract computation is genuinely reused across cases?

### WALL-B — Formation of inductive bias

Why does a learner prefer one compatible generalization over another?

### WALL-C — Selection among representable algorithms

Why does optimization discover one computation rather than another the architecture can also represent?

### WALL-D — Structure from resource constraints

What useful representation / computation emerges specifically because a natural resource is limited?

### **WALL-E — Developmental state / path dependence**

**When two learners behave the same now, what determines whether the same next experience changes them in the same way?**

This fifth wall is the main substantive state expansion of this pass.

---

# 11. What the next pass should do

Candidate generation remains **OFF**.

The next useful operation is a **WALL-E disagreement map**, analogous to the successful WALL-B map, but starting from older learning theory rather than current LM papers.

It should separate at least these rival explanation levels:

1. **state sufficiency:** is current function / behavior enough, or is history needed?
2. **memory account:** preserved latent traces vs overwritten state;
3. **plasticity account:** history changes the update operator itself;
4. **representation account:** history changes which features / abstractions are available;
5. **optimization account:** history changes local geometry / parameter mobility without changing the represented hypothesis;
6. **developmental account:** exogenous maturation vs experience-induced entrenchment;
7. **task-general vs task-specific state:** one global plasticity state vs computation-specific developmental states.

For each account, collect:

- classic experimental signature;
- what it predicts after a behaviorally matched endpoint plus identical future treatment;
- whether a modern neural learner gives an identifying observable unavailable in biological experiments;
- direct current owners;
- whether both result directions would matter.

Only after that map exists should WALL-E be considered for question generation.

---

# 12. Current decision

**New standing problem admitted:** 1 — IP18 / WALL-E.  
**New WATCH problem recorded:** 1 — IP19 / credit assignment.  
**New L-series:** 0.  
**New K-series:** 0.  
**Pilot authorization:** none.

The important outcome is not "we found a paper idea."

It is that the repository now contains a new long-term scientific coordinate that is **older than the frontier literature, aligned with our research intimacy, and capable of absorbing future evidence without being generated by that evidence**:

> **current competence is not necessarily current learning state.**
