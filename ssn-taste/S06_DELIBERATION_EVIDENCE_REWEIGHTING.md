# S06 — What Does Deliberation Do to Evidence?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-18  
**Target venues:** ACL / EMNLP / NAACL Main  
**Scientific type:** reasoning dynamics / causal evidence integration

## 1. Stable parent question

When a language model is given a fixed set of external evidence and then deliberates, does reasoning merely **compute with that evidence**, or does the act of deliberation itself change which pieces of evidence can still influence the decision?

The stable parent question is:

> **How does the causal influence of fixed external evidence evolve while a model deliberates?**

A shorter formulation is:

> **What does deliberation do to evidence?**

The object is not whether chain-of-thought is faithful, whether models exhibit confirmation bias in the final answer, or whether longer reasoning is better. The object is the **time evolution of evidence influence under a fixed evidence set**.

## 2. Scientific pressure

Several nearby findings do not collapse to one simple account.

- Wan et al. (ACL 2025 Findings), *Unveiling Confirmation Bias in Chain-of-Thought Reasoning*, show that prior model beliefs skew both rationale generation and how rationales are used.
- Kumaran et al. (Nature Machine Intelligence 2026), *Competing Biases underlie Overconfidence and Underconfidence in LLMs*, show a different pattern: models display choice-supportive persistence while also **overweighting opposing advice** rather than simply overweighting supportive evidence.
- Step-wise attribution work can identify which contextual facts a reasoning step depends on, but this does not establish a law for how those dependencies evolve as deliberation unfolds.
- Commitment-boundary work shows that large portions of a reasoning trace can occur after the answer is already effectively fixed, so the relevant dynamics must be studied **before commitment**, not inferred from the final transcript.

Together these results leave an explanatory gap. Final answer persistence, contradictory-evidence hypersensitivity, and CoT confirmation-like effects can coexist; a static statement such as “the model prefers confirming evidence” cannot explain all of them.

## 3. Competing worlds

### World A — Stable / approximately normative integration

Deliberation does not materially reassign evidence weight. Evidence influence is primarily determined by the external evidence and its reliability; reasoning computes consequences from a relatively stable evidential state.

Prediction: randomized evidence effects remain approximately stable before commitment, aside from ordinary noise or normatively justified integration.

### World B — Generic dilution

Self-generated reasoning progressively weakens access to the external evidence as a whole, for example through distance, contextual competition, or growing dependence on the self-generated prefix.

Prediction: causal effects of **both supporting and contradicting evidence shrink together** with reasoning depth.

### World C — Selective reweighting / coherence formation

Deliberation changes the effective evidential state. Evidence consistent with the emerging interpretation becomes easier to use, while conflicting evidence becomes less influential.

Prediction: evidence aligned with the rest of the evidence or emerging interpretation is preserved/amplified, while discordant evidence loses causal influence **before final commitment**.

A possible mechanism inside World C is **pseudo-independent self-reinforcement**: a model may paraphrase or restate an external fact in its own reasoning and then partially treat that internally generated copy as additional support. This is a mechanism hypothesis, not the parent claim.

## 4. Nearest-prior ownership boundary

S06 does **not** claim:

- first evidence of confirmation bias in CoT;
- first evidence that models resist contradictory information;
- first counterfactual attribution over reasoning steps;
- first evidence that long reasoning can become ungrounded;
- first discovery of an answer commitment point.

Those objects are already occupied.

The surviving reviewer-level difference is:

> Existing work studies how prior beliefs bias rationales, how advice changes a final belief/confidence state, which facts individual reasoning steps depend on, or when the final answer becomes committed. S06 instead asks whether a **fixed randomized evidence set undergoes endogenous causal reweighting as deliberation itself unfolds**.

If a direct prior is found that already estimates supporting-versus-conflicting evidence influence as a function of deliberation depth under a fixed randomized evidence set, this novelty claim must be re-audited.

## 5. Minimum pilot

Use a small controlled binary decision world with four independently randomized evidence items.

Each item has:

- a direction (+ / - for the two candidate hypotheses);
- a fixed reliability/strength;
- matched surface form and length.

Do **not** group trials by the model's own early answer; that would condition on a post-treatment variable.

Instead, use the randomized evidence directions themselves.

For each reasoning depth / checkpoint before commitment, estimate:

1. the main causal effect of each randomized evidence item on the current answer distribution;
2. whether that effect changes with depth;
3. the interaction between an item's direction and the aggregate direction of the **other randomized evidence items**.

This creates a clean factorial test:

- stable coefficients -> World A;
- coefficients shrink together -> World B;
- evidence aligned with the other evidence grows/persists while discordant evidence weakens -> World C.

A second, optional intervention can control whether the model is allowed/encouraged to explicitly restate the evidence during reasoning. If restatement selectively increases the later influence of the original fact, that supports the pseudo-independent self-reinforcement mechanism.

### Pilot discipline

- one open reasoning model first;
- a few hundred cheap controlled trials, not a benchmark;
- no model zoo;
- no training;
- no activation patching required for the first decision;
- analyze only the pre-commitment region;
- freeze the claim before expanding experiments.

## 6. What would count as knowledge gain?

All three principal outcomes are publishable scientific information if robustly identified.

- **World A:** deliberation is closer to computation over a stable evidence state than to belief-state reshaping; many behavioral “bias” effects must arise elsewhere.
- **World B:** reasoning itself gradually disconnects decisions from external evidence, giving a concrete grounding-decay law.
- **World C:** deliberation is an endogenous evidence-selection process; the model changes which observations can affect future computation while it reasons.

The paper should therefore not depend on observing confirmation bias.

## 7. Claim boundary

Do not turn S06 into:

- another confirmation-bias benchmark;
- a generic CoT-faithfulness paper;
- an evidence-attribution metric paper;
- “longer reasoning is worse”;
- a mechanistic search for a confirmation-bias head/vector;
- a broad claim that all reasoning rewrites beliefs.

The stable claim is the **causal dynamics of evidence influence during deliberation under fixed external evidence**.

## 8. Promotion status

**PILOT-AUTHORIZED.**

The pilot is authorized because:

- the mother question survives reviewer-level nearest-prior compression;
- the relevant neighboring findings give mutually non-equivalent explanations rather than merely an unfilled benchmark cell;
- the factorial manipulation directly distinguishes qualitatively different worlds;
- no large dataset, training run, or model sweep is required;
- opposite/null results remain scientifically interpretable.

Do not widen the project before the minimum pilot establishes whether evidence influence is stable, generically diluted, or selectively reweighted.
