# 2026-09-15 — PLM-as-Distribution Proxy / Counterfactual Identifiability Audit

**Target:** ACL / EMNLP / NAACL Main; calibrated continuously against TACL / ICLR / ICML / NeurIPS.

## Question

> When a corpus itself cannot directly answer a counterfactual linguistic question, is the answer produced by a pretrained language model a property identified by the data distribution, or a property of the estimator's inductive assumptions?

A sharper version considered was:

> Does predictive equivalence imply counterfactual linguistic equivalence?

**Final verdict:** **KILL CURRENT FORM / DO NOT REGISTER AS L-SERIES / DO NOT PILOT.**

The scientific pressure is real, but the available paper identity compresses to a robustness / predictive-multiplicity sequel around an EMNLP 2025 Highlight. The likely central result is too predictable from standard finite-sample/model-class uncertainty to meet current Main-level taste.

---

## 1. Origin

Rozner et al., EMNLP 2025 SAC Highlight, **Constructions are Revealed in Word Distributions**, ask how much information about grammatical constructions exists in the distribution of language itself. Because raw corpus counts cannot answer their counterfactual questions about what caused a word to occur, they treat RoBERTa as a computable proxy for the distribution over strings and use perturbations of the model's output distribution to measure statistical affinity.

This is methodologically interesting because the PLM is explicitly used as **distribution estimator / corpus proxy**, not simply as a learner whose internal grammar is being studied.

The natural linking assumption is:

> the counterfactual quantity returned by the fitted PLM is sufficiently determined by the corpus distribution that it can support conclusions about information present in that distribution.

---

## 2. Strongest possible formulation

Fix the training corpus exactly. Train multiple probabilistic language models with different architectures, objectives, seeds, and regularization, while matching held-out predictive performance closely. Query the same linguistic counterfactual estimand in every model.

Two scientifically meaningful outcomes are possible:

- **Convergence:** very different estimators agree on qualitative counterfactual conclusions, giving genuine support to PLM-as-distribution methodology.
- **Divergence:** predictively near-equivalent estimators give incompatible linguistic conclusions, showing that a single-model counterfactual cannot be interpreted as a corpus-identified property without additional assumptions.

At first glance, both directions matter and the question is broader than construction grammar.

---

## 3. Direct-owner / ancestry audit

No ACL/TACL paper was found that exactly asks whether counterfactual linguistic conclusions from a PLM-as-corpus-proxy are invariant across predictively equivalent estimators.

However, the parent logic is heavily occupied.

### Predictive fit does not identify linguistic generalization

McCoy, Min & Linzen (BlackboxNLP 2020), **BERTs of a feather do not generalize together**, train 100 BERT instances on the same MNLI dataset. MNLI dev accuracy lies in a narrow 83.6–84.8% band, yet HANS syntactic-generalization accuracy on some cases ranges from 0 to 66.2%.

This directly establishes that near-identical in-distribution predictive performance does not determine a linguistic extrapolation.

Related work on random-seed variation, heuristic subnetworks, and underspecification makes the same broad point in other settings.

### Rashomon / predictive multiplicity is mature

The broader ML literature studies sets of near-optimal models that fit observed data similarly but disagree in predictions, explanations, feature effects, or recourse. Thus an estimator-ensemble disagreement result has a well-known conceptual parent.

### LM choice already changes scientific proxies

Psycholinguistic surprisal work routinely finds that scientific conclusions depend on which LM supplies the probability estimates. TACL work shows that lower-perplexity / larger models can fit human reading times worse; later work therefore evaluates multiple LM families rather than assuming a unique probability proxy.

Hence `model choice matters for scientific inference from LM probabilities` is itself not new.

---

## 4. Why the current form fails Main-level calibration

The decisive reviewer compression is:

> **Rozner et al. 2025 + predictive multiplicity / underspecification -> run multiple estimators before treating a PLM counterfactual as a corpus property.**

That is useful methodological hygiene, but it is not yet a new scientific problem frame.

The strongest likely empirical result is also too easy to anticipate:

> Equal or near-equal average held-out likelihood does not guarantee equality of a particular local conditional or an extrapolative/off-support counterfactual.

This is a standard consequence of finite data, model misspecification, and weak constraints on local behavior. A sign reversal would be visually striking but would not by itself supply an ACL/EMNLP/NAACL Main-level conceptual surprise.

In contrast, the papers currently used to calibrate taste—ACL local-attention theory, ICLR succinctness, ICML Flexibility Trap, NeurIPS RLVR capability-boundary work—change a load-bearing scientific belief with a non-obvious result. The present route mainly audits whether a particular estimator-based methodology is robust.

---

## 5. Why obvious repairs do not rescue it

### More model families

Testing BERT/RoBERTa/GPT/LSTM/n-gram estimators makes the robustness claim broader but does not change the scientific parent.

### Exact corpus counts / Infini-gram

Internet-scale exact n-gram counting is useful leverage for separating directly observed local statistics from neural smoothing, but using Infini-gram as an additional estimator would still make the paper read as `Constructions paper + new corpus instrument` unless it yielded a genuinely new law.

### Restrict to high-support contexts

This makes estimator disagreement less trivial and would be the right control in any future study. But the project would still need a surprising positive or negative law about **when** counterfactuals become estimator-invariant; merely showing some disagreements survive is insufficient.

### Define a new robustness metric

This would push the project further toward evaluator/methodology work, which is currently low-priority and does not create the scientific question.

---

## 6. What would be needed to reopen

Do not reopen merely because no exact owner exists.

A qualitatively stronger route would require one of:

1. a non-trivial theorem giving conditions under which predictive equivalence **does** imply agreement on an important class of linguistic counterfactuals;
2. a broad empirical law showing counterfactual conclusions converge across model classes above a natural support/data threshold, with a quantity that predicts the transition out of sample;
3. a natural high-support phenomenon where equally predictive estimators systematically yield opposite established linguistic conclusions, invalidating a substantive literature-level inference rather than one paper's method;
4. evidence that LM counterfactuals converge despite large differences in architecture/objective, thereby providing unexpectedly strong validation of PLM-as-distribution analysis.

Until such pressure appears, this remains **closed / incubate only**.

---

## 7. Searcher lesson

The question passed the first-layer test and deserved a full audit. The correct reason to kill it is not lack of an exact empty cell; it is that the nearest plausible answer is already implied by a mature statistical-learning phenomenon.

A useful rule:

> A linking-assumption question becomes a strong paper only when breaking the link changes a substantive scientific belief in a non-obvious way. `Estimator choice matters` is not enough by itself.

Also preserve the workflow rule requested in this search round:

> Once a lead reaches SERIOUS-LOOK, finish owner audit, consequence audit, Main-level calibration, and final verdict before switching walls.
