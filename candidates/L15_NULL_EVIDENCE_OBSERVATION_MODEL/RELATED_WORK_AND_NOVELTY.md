# L15 — Related Work and Novelty Audit

**Date:** 2026-09-11  
**Status:** live pre-pilot ownership audit  
**Target:** ACL / EMNLP / NAACL Main

## 1. Claimed object

L15 does **not** claim any of the following as new:

- absence of evidence can be evidence of absence;
- Bayesian belief updating;
- diagnostic sensitivity/specificity;
- partial observability;
- belief-state tracking for LLM agents;
- RAG abstention under missing evidence;
- selection neglect / WYSIATI;
- explicit probabilistic memory.

The proposed independent question is:

> **For an identical null observation, do LLMs condition the evidential update on counterfactual detectability, and can they explicitly know the observation likelihood while failing to integrate it into the posterior world-state belief?**

This wording is intentionally narrow enough to survive the very crowded 2026 belief-state literature.

---

## 2. Classical owner: absence salience

### Hsu, Horng, Griffiths & Chater (Cognitive Science 2017)
**When Absence of Evidence Is Evidence of Absence: Rational Inferences From Absent Data**  
https://doi.org/10.1111/cogs.12356

Owns:

- classical absence-of-evidence question;
- Bayesian normative analysis;
- human experiments where absence becomes more informative when it would have been more surprising under the alternative;
- the general lesson that absent observations must be interpreted through the sampling/observation process.

Does not own:

- LLM behavior;
- competence/integration dissociation;
- modern retrieval/tool-output consequences.

**Implication for L15:** this is the parent, not the novelty.

---

## 3. Selection-process neighbor

### Deng & Yan (2026 preprint)
**Selected Evidence, Omitted Information, and Belief Updating in Large Language Model Decision Support**  
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7060438

Owns:

- LLM belief updating when the *visible evidence was selected conditionally*;
- WYSIATI / selection neglect;
- Bayesian versus visible-sample updating;
- domain-framed decision-support tasks;
- evidence that explicit hidden-expectation reasoning is associated with better correction.

Key difference:

- their task contains **visible selected values** and asks models to account for why other values are omitted;
- L15 fixes the visible outcome to a **null observation** and varies the probability of obtaining that same null under the world hypothesis.

Reviewer compression risk:

> "Both are just Bayesian likelihood neglect caused by a data-generation process."

Surviving contribution must therefore be a concrete new dissociation, not a new domain:

> **LLM explicitly estimates the null-observation likelihood correctly but fails to use it in the posterior.**

Without that or an equally specific computational signature, WYSIATI substantially weakens L15.

---

## 4. Broad belief-state / partial-observability owners

### Chattopadhayay & Halder (2026-09-09)
**Belief-State Engine: Augmenting LLMs for Principled Planning Under Partial Observability**  
https://arxiv.org/abs/2609.10036

Owns:

- the broad claim that history-conditioned LLM policies are not reliable belief-state policies under POMDP partial observability;
- explicit Bayesian posterior maintenance outside the LLM;
- Tiger POMDP and attack-graph evaluation;
- belief calibration / decision consistency improvements from an external filter;
- a formal observation kernel `Z(o|s,a)` as part of the architecture.

This is the strongest newly discovered collision.

L15 **must not** claim:

> "LLMs lack observation models," "LLM agents need Bayesian filtering," or "partial observability breaks LLM agents."

Those claims are now owned/crowded.

L15 can survive only as a controlled behavioral/computational result about **null evidence** and **explicit observation-likelihood competence versus integration**.

### Kumar et al. (2026-08-31)
**Towards a Belief-Based World Model for LLM Agents**  
https://arxiv.org/abs/2609.00455

Owns:

- explicit belief access for LLM policies under partial observability;
- ALFWorld belief updates;
- presence/absence renormalization over searched receptacles.

Important boundary:

Their rule-based belief update treats absence in a searched receptacle as eliminative according to the environment model. L15 instead asks whether the *LLM itself* scales a null's evidential force with the observation process, including low-sensitivity cases where elimination is invalid.

### Liao et al. (2026)
**Belief Memory: Agent Memory Under Partial Observability**  
https://arxiv.org/abs/2605.05583

Owns:

- deterministic memory conclusions as a source of self-reinforcing error under partial observability;
- probabilistic alternatives in memory.

Does not isolate null-evidence sensitivity or the proposed competence/integration dissociation.

### Zou et al. (ICLR 2026 / ICML 2026)
**T3 / Information Self-Locking**  
https://iclr.cc/virtual/2026/poster/10007172  
https://arxiv.org/abs/2603.12109

Owns:

- belief deviation and belief tracking as key active-reasoning capabilities;
- interaction between information acquisition and belief tracking during RL.

Again, broad belief tracking is not available as L15 novelty.

---

## 5. Retrieval / evidence-sufficiency neighbors

### Xie et al., EACL 2026
**Over-Searching in Search-Augmented Large Language Models**  
https://aclanthology.org/2026.eacl-long.361/

Owns:

- over-searching across answerable/unanswerable queries;
- noisy retrieval effects;
- negative evidence and abstention behavior;
- search-efficiency metrics.

Does not test identical empty results under different retrieval sensitivity/coverage.

### Zhang & Wu (2026)
**Do LLMs Know When Evidence is Insufficient?**  
https://doi.org/10.32604/cmc.2026.086343

Owns:

- evidence-sufficiency/abstention benchmark;
- `No Context` as a condition requiring abstention;
- partial/irrelevant/conflicting evidence conditions.

L15's conceptual difference is important:

> **No evidence is not uniformly insufficient.** A null from a nearly exhaustive search can be strong negative evidence; a null from a low-recall search can be almost uninformative.

If L15 is reduced to abstention accuracy, this paper compresses it.

---

## 6. Information-gain neighbor

### Hu et al. (2026)
**Optimizing Agentic Reasoning with Retrieval via Synthetic Semantic Information Gain Reward**  
https://arxiv.org/abs/2602.00845

Owns:

- information gain as uncertainty reduction for agentic retrieval;
- belief-state update formalization during retrieval;
- training agents to seek information.

Does not isolate null observations or the specific failure to use known detectability.

L15 cannot claim generic information-gain awareness as new.

---

## 7. Main-level compression test

### Strongest A + B + C compression

**A — Hsu 2017:** absence salience is Bayesian and depends on the observation process.  
**B — Deng & Yan 2026:** LLMs neglect data-selection mechanisms in Bayesian updating.  
**C — 2026 belief-state/POMDP papers:** LLM agents need explicit belief tracking under partial observability.

A reviewer could say:

> "You simply re-test a known human absence-of-evidence paradigm on LLMs, in a year where selection neglect and belief-state failures are already established."

### What must survive that compression

At least one of the following must be strongly established, and the first is preferred:

1. **Competence–integration dissociation:** models correctly represent `P(null | H)` but systematically fail to use it in `P(H | null)`.
2. **Invariant-null heuristic:** posterior judgments remain nearly invariant over large detectability changes despite correct controls, showing a specific surface-outcome heuristic rather than generic arithmetic noise.
3. **Cross-interface gap:** direct observation-model reasoning succeeds, while the same model prematurely commits to non-existence when the null arrives through a tool/search interface — after the direct behavioral mechanism has already been established.

If the result is merely "LLMs update imperfectly under partial observability," **KILL**.

---

## 8. Development-path novelty lock

The likely development path has been collision-checked in advance:

- **C1** cannot broaden to generic Bayesian reasoning;
- **C2** cannot broaden to generic hidden belief states;
- **C3** cannot become a generic RAG abstention benchmark;
- an external Bayesian-filter method would collide with BSE/BB-WM and is not the planned contribution;
- a memory method would collide with BeliefMem and is not the planned contribution.

The full-paper identity must remain:

> **null evidence is only meaningful relative to what the observer could have detected; LLMs may explicitly know this likelihood yet fail to integrate it into world-state inference.**

Any mutation away from this identity returns to topic selection.

---

# Verdict

## **PASS FOR ONE BOUNDED PILOT, WITH HIGH COLLISION RISK**

The broad area is crowded enough that this route should be killed aggressively. The pilot is justified only because no direct owner was found for the exact `same null × varied detectability × observation-likelihood competence vs posterior integration` design.
