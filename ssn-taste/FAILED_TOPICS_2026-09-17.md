# Failed Topics — 2026-09-17 Cross-Domain Search

**Status:** durable kill ledger. **MUST be read together with `ssn-taste/FAILED_TOPICS.md` before generating new topics.**

Purpose: record seeds killed during the 2026-09-17 cross-domain search so later rounds do not repackage them with new terminology. These are negative/process evidence only, never positive research-taste exemplars.

A topic may be revived only if new evidence resolves the recorded parent-novelty or identification failure. A new model, dataset, benchmark, wording, or mathematical metaphor is not enough.

---

## F07 — Training path dependence / hysteresis from example order

**Question.** If a model is fine-tuned on the same examples with the same counts and objective but in different temporal orders, can it converge to meaningfully different learned behaviors or representations even after seeing the same final multiset? Can this be understood as path dependence or hysteresis rather than ordinary score differences from curriculum learning?

**Why it looked promising.** Dynamical-systems language gives a natural scientific puzzle: the final state of a nonlinear learner need not be determined only by the final data distribution. A matched-data intervention would be cheap and could in principle distinguish transient optimization effects from durable path dependence.

**Nearest prior.** Jia et al., ACL 2026 Main, *What Makes a Good Curriculum? Disentangling the Effects of Data Ordering on LLM Mathematical Reasoning*, already makes training order itself a central post-training object and studies how different curricula alter final representations, confidence, uncertainty, and generalization. Hu et al., Findings ACL 2026, *Fine-Grained Data Ordering Improves Fine-Tuning for Large Language Models*, also treats dynamic ordering during fine-tuning as an explicit intervention.

**Failure reason.** A reviewer can compress the proposed mother question to the already occupied parent `data order / curriculum changes LLM fine-tuning outcomes and internal states`. Calling it hysteresis or path dependence does not create a new scientific object. A clean same-multiset design would improve identification but would still be a cleaner experiment inside an occupied parent.

**Revival condition.** A genuinely different history-dependent quantity with a prediction not reducible to curriculum/order effects—for example, a provable state variable with a loop intervention that demonstrates non-equivalent return paths after controlling the full optimization schedule.

---

## F08 — Where does extra information come from when a distilled student beats its teacher?

**Question.** Distillation appears informationally one-way: the student sees teacher-generated supervision. How can a student outperform the teacher, and what source of information creates the gain?

**Why it looked promising.** The question has a clean information-theoretic pressure and multiple explanations: regularization/geometry, data filtering, inductive bias, student-friendly targets, or information supplied by labels/task data outside the teacher signal.

**Nearest prior.** Pham et al. (2022), *Revisiting Self-Distillation*, systematically studies students surpassing teachers and proposes a loss-landscape/flat-minima explanation. Modern LLM KD work repeatedly demonstrates students matching or surpassing teachers under student-aware objectives; e.g. DA-KD (ICML 2025) and MPDistil (ICLR 2024).

**Failure reason.** The phenomenon and the explanatory parent are already mature. Re-running it for current LLMs, chain-of-thought distillation, or a new teacher/student pair would be `old distillation puzzle + newer models`. The remaining space is method-specific rather than a new Main-level mother question.

**Revival condition.** An independently motivated information source absent from existing KD/self-distillation explanations, with a controlled intervention that changes the predicted possibility of student>teacher behavior.

---

## F09 — Associative blocking / cue competition as a mechanism of LLM fine-tuning

**Question.** If a pretrained model already has one reliable feature/cue for predicting a target, does that cue block learning of a newly introduced alternative cue during fine-tuning, analogous to associative blocking/overshadowing?

**Why it looked promising.** Cue competition is a classic learning-theory phenomenon and naturally asks why some available predictive features are never learned. It also offers a direct bridge from psychology to mechanistic neural-network learning.

**Nearest prior.** Pezeshki et al., NeurIPS 2021, *Gradient Starvation: A Learning Proclivity in Neural Networks*, already formalizes the neural-network parent: cross-entropy can be minimized by learning only a subset of predictive features, starving alternative useful features of gradient. ACL 2025 work such as *Towards Objective Fine-tuning: How LLMs’ Prior Knowledge Causes Potential Poor Calibration?* further studies how prior knowledge changes fine-tuning dynamics.

**Failure reason.** Rebranding gradient competition as psychological `blocking` does not change the parent question. Without a qualitatively different prediction that distinguishes associative blocking from gradient starvation/feature competition, this is terminology transfer rather than scientific transfer.

**Revival condition.** A blocking-specific intervention (e.g. acquisition/extinction/recovery signature) whose outcome cannot be predicted by generic gradient starvation or prior-knowledge interference.

---

## F10 — Success-only trajectory selection creates collider/selection bias

**Question.** When post-training keeps only successful trajectories, does conditioning on success induce spurious correlations among actions/features, causing the model to imitate properties associated with being selected rather than properties causally responsible for success?

**Why it looked promising.** This imports a precise statistical concept—selection/collider bias—into a ubiquitous training operation and gives a natural mechanism question rather than a benchmark question.

**Nearest prior.** Agarwal et al., ICML 2019, *Learning to Generalize from Sparse and Underspecified Rewards*, already states the core problem: binary success/failure does not distinguish purposeful from accidental success, and generalization requires discounting spurious successful trajectories. Later RFT/trajectory-filtering work explicitly studies which steps inside successful or failed trajectories should be trained on rather than blindly treating final success as step-level correctness.

**Failure reason.** The mother problem `success-conditioned trajectories contain spurious/accidental behavior and final reward underdetermines causal credit` is already owned. Collider language is a useful interpretation but not a distinct scientific question.

**Revival condition.** A concrete collider structure that yields a counterintuitive prediction not captured by accidental-success/credit-assignment work, together with an intervention on the selection mechanism itself.

---

## F11 — Do paraphrased demonstrations help by reweighting a semantic example or by learning invariance?

**Question.** When SFT contains many semantically equivalent instructions/answers expressed in different forms, is the gain merely repeated weight on the same semantic target, or does cross-form supervision force the model to learn a representation invariant to surface realization?

**Why it looked promising.** The two explanations make different causal predictions and connect naturally to invariance learning in vision/contrastive learning.

**Nearest prior.** Yan et al., Findings ACL 2024, *Contrastive Instruction Tuning*, explicitly uses paraphrased semantically equivalent instructions to pull hidden representations together and improve invariance/robustness to textual variation.

**Failure reason.** Although `reweighting versus invariance` is a somewhat sharper mechanism framing, the parent `semantically equivalent instruction variants can be used to train invariant representations` is already explicit. A new ablation separating duplicate count from paraphrase diversity would be mechanism follow-up to an occupied parent, not a new mother question.

**Revival condition.** A different natural quantity for which repetition and invariance make opposing predictions beyond paraphrase robustness, with evidence that existing contrastive/instruction-tuning work cannot explain it.

---

## F12 — Ordinal human preference versus cardinal scalar reward

**Question.** Human preference data typically says only `A > B`, yet RLHF/RLAIF pipelines assign scalar reward values and perform arithmetic on them. Is reward magnitude actually identified by the data, or chosen by modeling assumptions?

**Why it looked promising.** This is a basic measurement-theory mismatch: ordinal observations do not by themselves determine cardinal distances. It could have supported a clean theory/experiment interface.

**Nearest prior.** Sun, Shen & Ton, ICLR 2025, *Rethinking Reward Modeling in Preference-based Large Language Model Alignment*, explicitly argues that downstream optimization only needs order consistency and that monotonic transformations of the latent reward can preserve the relevant ordering; it directly questions Bradley–Terry as a necessary cardinalization choice.

**Failure reason.** The ordinal-vs-cardinal identification issue is already a named theoretical object in modern reward modeling. Rephrasing it via measurement theory/econometrics does not create reviewer-level novelty.

**Revival condition.** A downstream operation whose behavior provably differs across reward functions that are observationally order-equivalent, creating an identifiable practical contradiction that existing order-consistency theory does not own.

---

## F13 — Can LMs learn from absence / indirect negative evidence?

**Question.** Can a language model infer that a form is disfavored or impossible because it systematically observes competing alternatives while never observing that form, rather than because it receives explicit negative examples?

**Why it looked promising.** This is a classic language-acquisition puzzle with natural competing explanations (preemption, entrenchment, positive evidence) and does not depend on a recent LLM anomaly.

**Nearest prior.** Oba et al., EMNLP 2024 Main, *Can Language Models Induce Grammatical Knowledge from Indirect Evidence?*, directly studies whether LMs induce grammatical knowledge from indirect evidence. Bonial et al. (2026), *Linguistic Productivity in Large Language Models: Models Coerce, but do not Preempt*, tests entrenchment and preemption. Wang, Shi & Misra (arXiv 2026-09), *Disentangling Statistical Preemption from Entrenchment in Language Models' Avoidance of Overgeneralization*, uses controlled rearing to separate the two mechanisms.

**Failure reason.** The parent is now directly occupied from both Main-conference and very recent controlled-learning angles. There is no honest novelty in moving the same question to a newer model or another construction.

**Revival condition.** A qualitatively different form of negative/absence information outside grammatical preemption/entrenchment, with a distinct theoretical prediction and natural experiment.

---

## F14 — Lexical memorization versus productive constructional abstraction

**Question.** When a model learns a novel usage pattern, when does it store an item-specific exception and when does it abstract a productive rule/construction that generalizes to nonce items?

**Why it looked promising.** This is an old scientific question with a very natural controlled intervention through type frequency, token frequency, and nonce-word generalization.

**Nearest prior.** The same 2026 productivity/preemption line directly tests constructional productivity with nonce words and frequency-based usage theories; related controlled rearing work studies how constructional evidence drives or fails to drive generalization.

**Failure reason.** The mother question is not newly identifiable by our proposed LLM experiment; modern LM work already owns `constructional productivity / entrenchment / preemption / nonce generalization`. Adding a new construction or model family would be a narrow cell.

**Revival condition.** A different abstraction boundary whose competing explanations are not construction-learning variants, or a new intervention that makes lexical storage and abstract rule learning predict opposite behavior not already tested by nonce/generalization work.

---

## F15 — Why does SFT on error→reflection→correction trajectories not teach the error?

**Question.** Standard teacher-forced SFT gives positive likelihood to every unmasked assistant token. If a gold trajectory intentionally contains an erroneous action followed by reflection and correction, why should training teach recovery without also increasing the propensity to reproduce the error?

**Why it looked promising.** The contradiction comes directly from the objective, not from gambling on an empirical anomaly. Several outcomes would be scientifically interpretable: useful recovery learning, increased error propensity, or contextual isolation of erroneous steps.

**Nearest prior.** Chen et al. (2025), *Training LLM-Based Agents with Synthetic Self-Reflected Trajectories and Partial Masking (STeP)*, explicitly constructs error→reflection→correction trajectories and masks incorrect/suboptimal steps so the model sees them as context but does not internalize them as prediction targets. Slinko et al. (2026), *Step Rejection Fine-Tuning: A Practical Distillation Recipe*, uses the same principle on agent trajectories: retain erroneous steps in context, mask their loss, and learn subsequent recovery; it also shows naïvely mixing unresolved trajectories is worse than filtered/masked training.

**Failure reason.** The exact contradiction, intervention, and intended causal solution are already owned: `keep the error in context; do not train the model to reproduce it; train on the recovery`. Studying full-loss trajectories more cleanly would be a mechanism follow-up to existing partial-masking work.

**Revival condition.** Evidence that full positive loss on erroneous steps can nevertheless improve error avoidance through a distinct, unexplained mechanism that masking-based work cannot account for; mere replication on another agent task is insufficient.
