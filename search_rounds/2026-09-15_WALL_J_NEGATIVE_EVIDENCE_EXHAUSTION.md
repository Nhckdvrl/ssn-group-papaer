# 2026-09-15 — WALL-J / Learning Restrictions from Positive Evidence — Exhaustion Audit

**Target:** ACL / EMNLP / NAACL Main, calibrated against TACL / ICLR / ICML / NeurIPS / AAAI  
**Mode:** classic learnability problem → rival acquisition mechanisms → controlled-learning literature → current direct-owner audit  
**Outcome:** **WALL-J EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

> The mother problem is unquestionably important: how can a learner infer that a form is restricted or unacceptable when it mainly receives positive linguistic evidence? But the currently identifiable descendants are now directly occupied by a mature human-learning literature and a very active 2024–2026 controlled-LM program. The two newest LM studies even directly disagree about the strength / level of statistical preemption, but their interventions are not yet the same treatment on the same learner regime. Chasing that discrepancy would be paper-to-paper gap filling rather than problem-first generation.

---

# 0. Mother problem

> **How can a learner retreat from an overgeneralization, or infer that a plausible form is unavailable, without being explicitly shown negative examples?**

This is the classic `negative evidence` / `positive evidence` learnability problem, with ancestry through Gold, Baker's paradox, child language acquisition, statistical learning, construction grammar, Bayesian learning, and connectionist modeling.

The wall is older than neural language models by decades and passes the durability test.

---

# 1. Deep ancestry

## 1.1 Gold and the positive-evidence problem

Gold's identification-in-the-limit result is frequently read as showing that broad language classes cannot in general be identified from arbitrary positive presentation alone without additional restrictions on the learner / hypothesis space / presentation process.

The later acquisition debate therefore asks what real-world structure supplies the missing restriction.

## 1.2 Marcus 1993 — explicit / noisy negative evidence is insufficient as the general answer

Gary Marcus, **Negative evidence in language acquisition** (Cognition 1993), reviews proposed parental feedback signals and argues that noisy correction is too weak and inconsistent to be required as the general solution.

Source:
- https://pubmed.ncbi.nlm.nih.gov/8432090/

The enduring pressure is therefore not merely whether children ever receive correction, but how they avoid retaining an overgeneral grammar when direct negative evidence is sparse.

## 1.3 Positive-data learning can exploit structure in the presentation distribution

Rohde & Plaut (Cognition 1999) emphasize that Gold's arbitrary-presentation assumptions need not characterize stochastic natural input; prediction in a structured distribution can provide substantial learning signal without explicit negative examples.

Source:
- https://pubmed.ncbi.nlm.nih.gov/10520565/

Simplicity / Bayesian / MDL accounts likewise show in formal settings that positive evidence can identify restricted hypotheses when the learner carries appropriate priors / coding preferences.

Representative source:
- Hsu, Chater & Vitányi 2013: https://onlinelibrary.wiley.com/doi/full/10.1111/tops.12005

Thus `positive evidence can in principle be enough` is not itself a new result.

---

# 2. The mature rival mechanism: entrenchment vs statistical preemption

For retreat from verb / construction overgeneralization, usage-based theories developed two distinguishable statistical explanations.

## Entrenchment

Repeated exposure to a lexical item in its attested uses reduces willingness to extend it to an unattested construction. Absence becomes informative because a frequent verb has had many opportunities to appear in the unattested form and did not.

## Statistical preemption

The crucial evidence is not overall verb frequency, but repeated exposure to a **competing form with the same or similar communicative function**. The conventional alternative preempts the unattested alternative.

Adele Goldberg's construction-grammar program made statistical preemption a central solution to the problem of how generalizations are constrained.

Source:
- https://academic.oup.com/book/32920/chapter-abstract/276902731

This is a genuine theory disagreement because the two accounts predict different outcomes when overall lexical exposure is matched but semantically competing exposure differs.

---

# 3. Human evidence already directly tests the disagreement

Samara et al. (Psychological Review; 2024/2025 publication cycle), **Learners restrict their linguistic generalizations using preemption but not entrenchment**, use five controlled artificial-language-learning experiments with adults and children.

Source:
- https://pubmed.ncbi.nlm.nih.gov/38842892/

The design separates evidence that should matter under preemption from evidence that should matter under entrenchment. Across all five studies, preemption reduces acceptance of unattested combinations; the entrenchment condition shows no corresponding effect, with positive evidence for the null in several experiments.

This is unusually strong prior work for our purposes:

> the classic rival accounts already have a controlled SAME-OBJECT identifying experiment in humans.

Earlier and parallel work is not perfectly unanimous. Meta-analytic / replication work has found evidence for both preemption and entrenchment in some domains and argues that the effects should ideally emerge from a more general probabilistic / communicative account rather than be stipulated as separate mechanisms.

Representative source:
- https://online.ucpress.edu/collabra/article/4/1/23/113007/

A 2026 review of the L2 literature likewise records mixed effects and substantial design heterogeneity.

Source:
- https://www.sciencedirect.com/science/article/pii/S2772766125001120

So the historical dispute is real, but it is not waiting for LMs to create a test.

---

# 4. Neural / computational ancestry already models the same mechanism family

Alishahi (Cognitive Science 2008) provides a computational account of early argument-structure acquisition in which prediction, frequency, semantic fit, construction competition, entrenchment and statistical preemption interact.

Source:
- https://onlinelibrary.wiley.com/doi/full/10.1080/03640210801929287

This is important anti-resurrection state:

> `build a neural/statistical learner that acquires restrictions from positive distributional evidence` is not new in principle.

The contribution would have to be a new inference about which mechanism is necessary / sufficient, not another existence proof.

---

# 5. 2024–2026 controlled-LM program directly occupies the natural descendants

## 5.1 Misra & Mahowald, EMNLP 2024 — rare phenomenon from related positive evidence

**Language Models Learn Rare Phenomena from Less Rare Phenomena: The Case of the Missing AANNs** trains Transformers on counterfactual corpora from which a rare construction is removed. The models still preferentially learn the construction relative to perturbed controls, and further ablations implicate generalization from related constructions.

Source:
- https://aclanthology.org/2024.emnlp-main.53/

Thus:

> `can an LM acquire a structure it never directly sees from related positive evidence?`

is directly owned.

## 5.2 Misra & Kim 2024 — controlled exposure for cross-dative generalization

This work trains LMs on child-directed speech and systematically manipulates novel-verb exposure contexts to derive predictions about when verbs generalize across dative constructions.

Source:
- https://arxiv.org/abs/2408.05086

This directly occupies the move:

> `use controlled LM rearing to discover which positive evidence enables / blocks a constructional generalization`.

## 5.3 Yao et al., COLM 2025 — direct vs indirect evidence

**Both Direct and Indirect Evidence Contribute to Dative Alternation Preferences in Language Models** manipulates and ablates direct dative evidence and broader global distributional evidence in controlled-rearing LMs.

Source:
- https://arxiv.org/abs/2503.20850

They find both direct evidence and indirect global tendencies contribute to dative preferences.

Therefore the broad quantity

> `how much of a syntactic preference comes from direct examples vs indirect distributional structure?`

is now an explicit active program.

---

# 6. 2026 direct-owner collision: statistical preemption itself is now an LM target

## 6.1 Guo, Wu & Yiu 2026 — causal evidence for preemption

**Do Language Models Know What Not to Say? Causal Evidence for Statistical Preemption in LLMs** directly frames Baker's paradox / negative knowledge as the scientific question.

Sources:
- https://arxiv.org/abs/2605.23039
- https://openreview.net/pdf?id=sX52AcD4rp

Across dative, causative and locative constructions, the paper reports:

- item-level LLM surprisal correlates with human acceptability;
- competing-form frequency predicts the restriction more strongly than overall verb frequency;
- sensitivity scales with model size;
- a controlled fine-tuning intervention on competing-form frequency shifts the effect in the predicted direction, with reverse-direction controls.

This directly owns:

> `preemption vs entrenchment in LLMs`,

including a causal intervention version.

## 6.2 Wang, Shi & Misra 2026 — controlled rearing gives a different result

**Disentangling Statistical Preemption from Entrenchment in Language Models' Avoidance of Overgeneralization** trains LMs on child-caregiver conversations while systematically removing preemptive vs non-preemptive evidence.

Source:
- https://arxiv.org/abs/2609.01794

They report:

- LMs avoid overgeneralization;
- no clear **verb-specific** preemption;
- weak but non-zero **abstract** preemption;
- training dynamics suggest competing structures can behave like indirect positive rather than negative evidence in the verb-specific condition.

This result is scientifically interesting because it bears on exactly the mature human-learning dispute.

---

# 7. Why the two 2026 LM results do NOT yet give us a candidate

At first glance:

> Guo et al.: LLMs show causal statistical preemption.  
> Wang et al.: LMs do not show verb-specific preemption.

This looks like an ideal SAME-QUANTITY disagreement.

It is not yet one.

## 7.1 Learner regime differs

Guo et al. combine analysis of pretrained LLMs with controlled fine-tuning interventions.

Wang et al. use controlled rearing from child-caregiver input and delete / manipulate evidence during acquisition.

A post-hoc fine-tuning perturbation of an already richly pretrained model and evidence removal during initial acquisition are not the same treatment.

## 7.2 Evidence intervention differs

One design increases / manipulates competing-form evidence; the other systematically removes classes of preemptive vs non-preemptive evidence from the rearing distribution.

These operations need not estimate the same causal quantity.

## 7.3 Representation level differs

Wang et al. explicitly distinguish verb-specific from abstract preemption. A result at one level does not logically contradict an effect at another unless the unit is matched.

### Consequence

The disagreement is useful state, but the honest next question is currently:

> `which difference in learner / intervention / abstraction level explains the discrepant findings?`

That is a paper-to-paper reconciliation problem unless an older theory already selects one of those differences as the decisive conditioning variable.

This audit did not find such an unowned old-theory prediction.

---

# 8. Strongest residuals and reviewer compression

## J1 — `When does absence become evidence?`

Too broad. Bayesian / simplicity / distributional learning already supplies multiple general answers; the result depends on priors, opportunity to observe, competing hypotheses and presentation distribution.

A new scalar `absence evidence` metric would be evaluator invention, not a new scientific law.

**KILL CURRENT DESCENDANT.**

## J2 — `Preemption or entrenchment in LMs?`

Directly occupied by Guo et al. and Wang et al., with mature human prior work.

**KILL — DIRECT OWNER.**

## J3 — `Verb-specific vs abstract preemption`

Already an explicit result / distinction in Wang et al. 2026.

**KILL — DIRECT OWNER.**

## J4 — `Why do the two 2026 LM papers disagree?`

Reviewer compression:

> `rerun Guo under Wang's training regime / rerun Wang under Guo's intervention until the discrepancy disappears.`

That is a replication / reconciliation study generated by two frontier papers, not a durable mother question.

**KILL — PAPER-FIRST RECONCILIATION.**

## J5 — `Can related positive evidence teach an unseen restriction?`

Misra & Mahowald 2024, Misra & Kim 2024 and Yao et al. 2025 directly establish a controlled-input program around this quantity.

**KILL — ACTIVE PROGRAM.**

---

# 9. Anti-resurrection state

Do not regenerate, merely by changing construction / language / model:

- Baker's paradox × LLM;
- negative evidence × LLM;
- statistical preemption vs entrenchment × another construction;
- direct vs indirect evidence × another syntactic preference;
- controlled rearing to show an unseen pattern can be acquired from neighboring positive examples;
- verb-specific vs abstract preemption;
- Guo-vs-Wang reconciliation by swapping fine-tuning / rearing / model family;
- surprisal-vs-acceptability replication as the core contribution.

A reopening requires a different inferential level, e.g. an old theory that makes an **opposite prediction about one matched acquisition manipulation** that current preemption / entrenchment work cannot derive, or a new operation that identifies a property of negative knowledge unavailable to the existing controlled-rearing designs.

---

# 10. Boundary against recent closed walls

This is not WALL-B's possible/impossible-language line: the object here is retreat from a locally plausible overgeneralization under positive evidence, not broad human-possible vs impossible language learnability.

It is not WALL-G systematicity: the issue is restriction / exclusion of a candidate generalization, not whether capacities recombine systematically.

It is not WALL-F model-system validity: human–LM correspondence is not needed for the mother question, although several papers use humans as validation.

It is not the current IP03 route: no claim depends on succinctness, parameter geometry or formal-language expressivity.

---

# 11. Verdict

The wall has excellent ancestry, naturalness and scientific consequence, but **current headroom is low** because the strongest old rival mechanisms now have direct controlled human experiments and direct controlled-LM owners.

The newest apparent contradiction is not yet one clean SAME-QUANTITY disagreement because learner regime, intervention and representation level differ.

**Decision: WALL-J exhausted as a current generator. No new L-series. No pilot.**
