# 2026-09-13 — Live Search After L32 III

Continuation of `_II`. Persist seriously investigated dead hooks immediately.

**Rule:** only a fully selected `PILOT-AUTHORIZED — E01 ONLY` topic is user-facing.

---

## Hook I — Does arbitrary-order diffusion reasoning fail because it defers high-uncertainty logical forks?

**Status:** `DROP / DIRECT SUCCESSOR COLLISION`

### Origin

Ni et al., ICML 2026 Outstanding Paper, *The Flexibility Trap: Rethinking the Value of Arbitrary Order in Diffusion Language Models*, establishes a strong counter-intuitive mother: arbitrary-order decoding in diffusion LMs narrows rather than expands reasoning solution coverage. The paper's load-bearing explanation is **entropy degradation**: confidence-based decoding fills low-uncertainty positions first, bypasses high-entropy logical forks, and returns to those forks only after future context has already collapsed alternative reasoning branches.

Source: https://arxiv.org/abs/2601.15165

### Missing sentence attempted

> Is postponing high-uncertainty logical forks actually the cause of the reasoning collapse, or is the degradation caused more generically by non-left-to-right / off-distribution decoding order?

A seemingly decisive same-checkpoint test would directly vary decoding schedule: confidence-first vs uncertainty/fork-first vs random vs left-to-right, while leaving the frozen diffusion LM unchanged.

### Why it dies

The parent already contains stronger controls than a superficial reading suggests (block-size monotonicity, alternative sampling algorithms, and a fixed-random-order RL control). More importantly, a March-2026 successor performs almost exactly the desired intervention:

- **Aman, *LogicDiff: Logic-Guided Denoising Improves Zero-Shot Reasoning in Masked Diffusion Language Models* (arXiv:2603.26771).** It explicitly replaces standard confidence-based unmasking with a dependency-ordered inference-time scheduler that identifies logical roles and unmasks premises → connectives → derived steps → conclusions. The base model is unchanged. It reports LLaDA-8B-Instruct GSM8K accuracy rising from 22.0% to 60.7% and MATH-500 from 23.6% to 29.2%, directly supporting the claim that unmasking order itself accounts for a substantial portion of the deficit.

A second successor, **Fang et al., *Locally Confident, Globally Stuck: The Quality-Exploration Dilemma in Diffusion Language Models* (arXiv:2604.00375)**, formalizes the same neighboring phenomenon: confidence-gated decoding improves local/single-sample quality while constraining global sequence entropy and multi-sample exploration, and develops a sampler that balances the two.

Thus the proposed causal order test is not an unclaimed decisive experiment anymore.

### Strongest reviewer compression

> `Flexibility Trap identifies deferred high-entropy forks; LogicDiff directly changes the frozen model's unmasking order to logical dependency order and recovers reasoning; Locally Confident formalizes confidence gating's entropy/exploration cost.`

### Anti-resurrection

Do not reopen as `uncertainty-first decoding`, `decode logical connectives early`, `confidence order vs random order`, `does entropy degradation cause the flexibility trap`, or another inference-time scheduling variant unless a new scientific object contradicts the current fork-order explanation rather than optimizing within it.
