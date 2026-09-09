# L12 — Related Work and Paper-Level Novelty

**Candidate:** Reasoning Training: Canonicalization or Policy Override?  
**Freshness:** 2026-09-09

The novelty standard is paper-level. Nearby framing, bias, reasoning, and interpretability work is expected; it does not kill the topic unless it already owns the full scientific story.

---

## 1. Direct parent

ACL 2026 Outstanding Paper  
**“Mind the (DH) Gap!”**  
https://aclanthology.org/2026.acl-long.479/

Owns:
- broad risky-decision comparison across many models;
- description-vs-experience / DH-gap analysis;
- several controlled presentation/framing axes;
- reasoning-model differences in payoff maximizing and sensitivity;
- evidence that reasoning-oriented training, including SFT-stage differences in open-model analyses, is important.

The parent explicitly provides the phenomenon and first-level training association.

L12 therefore cannot claim:
- reasoning models are more payoff-maximizing;
- framing/order effects are reduced;
- the DH gap differs;
- reasoning SFT is worth investigating.

Our question begins one level deeper:
> **what computation changed?**

---

## 2. Framing-effect literature

A large literature already studies:
- gain/loss framing;
- order effects;
- description vs experience;
- cognitive biases in LLMs;
- rational-choice deviations.

This means:
> another behavioral survey is not novel enough.

L12 must use behavior as the starting phenomenon, not the final contribution.

---

## 3. Representation-level framing work

Recent work such as **“Framing Matters” (2026)** studies fact-preserving framing and internal pathways / representation-level interventions.

Representative source:
- https://arxiv.org/abs/2605.28188

This is an important close neighbor.

It owns:
- internal framing sensitivity as a mechanistic object;
- representation-level intervention on framing effects.

It does **not** automatically own:
> **how reasoning post-training transforms an established framing-sensitive decision computation across training stages, and whether the resulting behavioral invariance reflects canonicalization or downstream override.**

That training-transition identity is the key distinction.

---

## 4. Instruction tuning can increase bias

TACL 2024  
**“Instructed to Bias: Instruction-Tuned Language Models Exhibit Emergent Cognitive Bias”**  
https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00673/121541/Instructed-to-Bias-Instruction-Tuned-Language

Owns:
- evidence that instruction tuning can increase some cognitive biases.

This creates useful broader tension:
> post-training does not monotonically remove contextual bias.

But L12 should not expand into a general catalog of post-training bias.

---

## 5. Reasoning vs instruction/control trade-offs

ACL 2026  
**“Scaling Reasoning, Losing Control”**  
https://aclanthology.org/2026.acl-long.1878/

Owns:
- trade-offs between stronger reasoning and instruction adherence/control.

This is related because reasoning can dominate other contextual signals.

But it does not answer:
> whether equivalent risky-decision framings are internally canonicalized or merely overridden after reasoning training.

---

## 6. Mechanistic-interpretability neighborhood

A broad literature uses:
- linear probes;
- activation patching;
- causal tracing;
- steering;
- representation similarity;
- feature directions.

No such method is novel by itself.

L12’s novelty must come from:
> **the training-induced invariance question + controlled training trajectory + decisive mechanism distinction + consequence for interpreting reasoning-model rationality.**

---

## 7. What can still be ours

Current paper-level ownership:

1. start from a strong, established reasoning-induced decision invariance;
2. use a same-family training transition rather than unrelated model comparison;
3. distinguish representational canonicalization from preserved-context/policy override and other plausible accounts;
4. validate the distinction causally or with equivalent decisive evidence;
5. identify a meaningful boundary;
6. reinterpret what “reasoning makes decisions more rational/invariant” actually means.

No single neighboring paper found in the current audit compresses this whole chain.

---

## 8. Reviewer compression tests

### “Mind the DH Gap + probes”
Wins if:
- only decodability/representation plots are added;
- there is no causal distinction or new conclusion.

### “Another framing-effects paper”
Wins if:
- the project becomes a broad benchmark.

### “Framing Matters on reasoning models”
Wins if:
- the training-transition question disappears and the paper only studies framing pathways.

### “Generic activation patching”
Wins if:
- the method becomes the identity.

---

## 9. Do not over-compress novelty

Do **not** kill the topic because:
- framing has been studied;
- risky choice has been studied;
- activation patching exists;
- reasoning models have been compared to instruct models.

Those are related-work ingredients.

Kill/reconstruct only if existing work already owns the **full paper**:
> reasoning-training-induced invariance  
> + training-stage localization  
> + canonicalization-vs-override distinction  
> + decisive causal evidence  
> + same scientific consequence.

---

## 10. Current novelty verdict

**PASS for pilot authorization.**

The novelty corridor is strongest when the paper stays focused on:
> **what training-induced behavioral invariance means internally.**

Refresh before mainline promotion and whenever the central mechanism/narrative changes.
