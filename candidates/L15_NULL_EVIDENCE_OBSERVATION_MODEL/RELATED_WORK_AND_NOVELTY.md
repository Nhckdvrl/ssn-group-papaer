# L15 — Related Work and Novelty Audit

**Date:** 2026-09-11  
**Status:** REGISTERED / PILOT-AUTHORIZED, claim-locked  
**Target:** ACL / EMNLP / NAACL Main

## 1. Exact claimed object

L15 claims **none** of the following as new:

- absence of evidence can be evidence of absence;
- Bayesian belief updating;
- diagnostic sensitivity/specificity or negative likelihood ratios;
- generic evidence reliability;
- generic selection neglect / WYSIATI;
- generic partial observability or belief-state tracking;
- RAG abstention under missing evidence;
- explicit probabilistic memory or external Bayesian filtering.

The only load-bearing paper identity is:

> **For the same observed null result, does an LLM scale the world-state update with counterfactual detectability, and can it correctly represent `P(null | H)` while failing to use that quantity in `P(H | null)`?**

The preferred scientific signature is therefore a **competence–integration dissociation**, not generic Bayesian error.

If experiments force the project away from this object, authorization expires and the project returns to topic selection before any development.

---

## 2. Classical parent — owned, not novel

### Hsu, Horng, Griffiths & Chater (Cognitive Science 2017)
**When Absence of Evidence Is Evidence of Absence: Rational Inferences From Absent Data**  
https://doi.org/10.1111/cogs.12356

Owns the classical scientific problem: an absent observation is informative to the extent that the observation would have been expected under the hypothesis. It also supplies a human experimental precedent and Bayesian normative account.

### Forensic / sensor literature
Negative forensic evidence and negative sensor evidence have long been formalized with likelihood/sensor models. These fields already own the practical statement that a failed detection can be informative when the detector should have seen the target.

Therefore L15 must never sell the slogan **"absence of evidence can be evidence of absence"** as a contribution.

---

## 3. Direct Bayesian-LLM owners

### Kim, Kim & Thorne — NAACL 2025 Main
**From Evidence to Belief: A Bayesian Epistemology Approach to Language Models**  
https://aclanthology.org/2025.naacl-long.531/

Owns:

- LLM belief/confidence updates under different evidence types;
- Bayesian confirmation/disconfirmation/irrelevance framing;
- evidence-strength/reliability manipulations;
- the broad claim that LLM confidence does not consistently follow Bayesian epistemology.

It does **not** isolate an identical null observation while changing the observation process, nor does it test the proposed `P(null|H)` competence versus posterior-integration dissociation.

**Collision rule:** if L15 becomes "LLMs fail to weight evidence by reliability," NAACL 2025 owns the broad claim and L15 dies.

### Gupta et al. — ACL 2025 Main
**Enough Coin Flips Can Make LLMs Act Bayesian**  
https://aclanthology.org/2025.acl-long.377/

Owns generic controlled Bayesian updating / prior-update behavior in a coin-flip setting.

**Collision rule:** L15 cannot become a general Bayes benchmark or arithmetic paper.

---

## 4. Negative-test / diagnostic owner — very dangerous

### Rodman et al. — JAMA Network Open 2023
**Artificial Intelligence vs Clinician Performance in Estimating Probabilities of Diagnoses Before and After Testing**  
https://doi.org/10.1001/jamanetworkopen.2023.47075

This work directly evaluates GPT-4 on pre-test and post-test disease probabilities after **positive and negative diagnostic test results**, including a hypothetical probability problem.

It therefore already owns:

- the fact that LLMs can be tested on posterior probability after a negative observation;
- clinical negative-test Bayesian reasoning;
- comparison to normative reference probabilities.

Recent 2026 medical work also evaluates LLM generation/use of diagnostic likelihood ratios.

What remains different in L15 is not "negative evidence updates". It is the controlled scientific manipulation:

> **hold the null observation and prior fixed, vary only detectability, then separately measure whether the model knows the null likelihood and whether it integrates that known likelihood into the posterior.**

**Hard collision rule:** if the final claim can be written as "LLMs misestimate post-test probability after negative tests," L15 is already too close and must be killed/reselected.

---

## 5. Selection-process neighbor

### Deng & Yan (2026 preprint)
**Selected Evidence, Omitted Information, and Belief Updating in Large Language Model Decision Support**  
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7060438

Owns:

- LLM belief updating when visible evidence was conditionally selected;
- WYSIATI / selection neglect;
- Bayesian versus visible-sample updating;
- evidence that explicit hidden-expectation reasoning is associated with better correction.

Their task has **visible selected values** and asks the model to account for omitted values. L15 instead holds the visible outcome at **null** and varies the probability of seeing that same null under the hypothesis.

Reviewer compression risk:

> "Both are likelihood neglect caused by ignoring the evidence-generation process."

Therefore a simple detectability effect is not enough for a Main paper. L15 needs the predeclared computational signature, preferably:

> **correct `P(null|H)` + wrong `P(H|null)`**.

Without a specific dissociation or comparably strong structure, WYSIATI compresses the route too far.

---

## 6. Broad belief-state / partial-observability owners

### Chattopadhayay & Halder (2026-09-09)
**Belief-State Engine: Augmenting LLMs for Principled Planning Under Partial Observability**  
https://arxiv.org/abs/2609.10036

Owns the broad architectural diagnosis that raw-history LLM agents are unreliable belief-state policies in POMDPs and proposes an external Bayesian filter.

### Kumar et al. (2026-08-31)
**Towards a Belief-Based World Model for LLM Agents**  
https://arxiv.org/abs/2609.00455

Owns explicit belief access for LLM policies under partial observability; in ALFWorld it performs presence/absence belief updates after searches.

### Liao et al. (2026)
**Belief Memory: Agent Memory Under Partial Observability**  
https://arxiv.org/abs/2605.05583

Owns probabilistic memory as a remedy for premature deterministic conclusions under ambiguous observations.

### Zou et al. (ICLR/ICML 2026 line)
**T3 / Information Self-Locking**  
https://arxiv.org/abs/2603.12109

Owns broad belief tracking and information acquisition failures during active reasoning.

**Locked boundary:** L15 cannot claim "LLMs lack belief states," "LLM agents fail under partial observability," or "agents need explicit probabilistic state." Those broad claims are crowded/owned.

---

## 7. Retrieval / evidence-sufficiency neighbors

### Xie et al. — EACL 2026
**Over-Searching in Search-Augmented Large Language Models**  
https://aclanthology.org/2026.eacl-long.361/

Owns over-searching, unanswerable queries, retrieval conditions, negative evidence, and abstention behavior.

### Evidence-sufficiency work (2026)
Recent RAG benchmarks explicitly test `No Context`, partial, irrelevant, and conflicting evidence and whether models abstain.

### Santra et al. — DAWAK 2024
**"The absence of evidence is not the evidence of absence": Fact Verification via Information Retrieval-based In-Context Learning**

Despite the title, this work uses retrieved similar text as in-context evidence for fact verification; it does not manipulate retrieval coverage/detectability or posterior belief from the same empty result.

**Locked boundary:** L15 cannot become an abstention or fact-verification benchmark. Its target is the evidential force assigned to the same null outcome as the observation model changes.

---

## 8. Strongest reviewer compression

The strongest fair compression is now:

> **Hsu 2017 absence-of-evidence + NAACL 2025 evidence-to-belief + JAMA 2023 negative-test posteriors + Deng & Yan 2026 selection neglect + 2026 belief-state/POMDP work = L15.**

This is a genuinely dangerous compression.

The project survives **only** because none of these owners, in the audit performed on 2026-09-11, was found to own the exact combination:

1. **identical null observation**;
2. **counterfactual detectability as the isolated manipulation**;
3. **matched explicit probe of `P(null|H)`**;
4. **separate posterior `P(H|null)` probe**;
5. **a competence–integration dissociation as the scientific target**.

This five-part conjunction is the ownership boundary. Dropping (3)–(5) turns the project into a crowded Bayesian-evidence paper.

---

## 9. Claim lock and mutation policy

### Allowed central claim

> **LLMs may know how likely a null observation is under a hypothesis yet fail to use that observation model when updating what they believe about the world.**

### Allowed C1 → C2 → C3 path

- **C1:** same-null detectability curve;
- **C2:** observation-model competence versus posterior integration;
- **C3:** only after fresh re-selection, test whether the same computation predicts a controlled tool-use decision.

### Forbidden rescue claims

The project is **not allowed** to mutate into:

- generic Bayesian reasoning;
- generic evidence reliability;
- generic uncertainty/calibration;
- generic RAG abstention;
- generic partial observability / belief state;
- probabilistic memory;
- external Bayesian filtering;
- medical diagnostic reasoning;
- selection neglect/WYSIATI;
- hidden-state "belief representations" without returning to topic selection.

If the most interesting pilot result changes the central RQ, estimand, mechanism, or reviewer one-line takeaway, **stop expansion immediately and run a new ownership audit before any follow-up experiment**.

Evidence survives claim mutation; authorization does not.

---

# Verdict

## **REGISTERED — ONE BOUNDED PILOT AUTHORIZED**

The route is collision-prone, but after the expanded audit including NAACL 2025 Bayesian epistemology, JAMA negative-test reasoning, 2026 selection neglect, RAG, and POMDP/belief-state work, no direct owner was found for the locked five-part computation above.

This is not a declaration that the area is globally empty. It is a paper-identity decision: **the exact claim is currently separable, and the repository now forbids drift into the adjacent already-owned stories.**
