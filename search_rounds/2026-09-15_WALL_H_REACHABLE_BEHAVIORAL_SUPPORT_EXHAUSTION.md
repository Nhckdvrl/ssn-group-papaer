# 2026-09-15 — WALL-H / IP11 Reachable Behavioral Support Exhaustion Audit

**Wall:** IP11 — how should we describe a model's reachable behavioral support, not just its modal answer?  
**Mode:** old capacity/accessibility lineage → generative-distribution theory → RL / alignment frontier → exact-quantity audit  
**Outcome:** **EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

> The standing problem is real: modal/top-1 performance is an impoverished description of a stochastic generative system. But `reachable support` does not currently denote one natural scientific quantity. Literal support is mostly trivial for softmax LMs; every useful replacement — finite-sampling reachability, decoding reachability, prompt elicitation, fine-tuning elicitation, program complexity, semantic mode coverage — induces a different object. The 2023–2026 literature already directly owns the strongest versions.

---

# 1. Deep ancestry: availability is not accessibility

This wall predates generative AI.

Tulving & Pearlstone (1966), **Availability versus accessibility of information in memory for words**, showed that items not produced under free recall could become retrievable with category cues. The classic inference was:

> failure to produce information does not imply that the information is absent from memory.

A related linguistic distinction is **competence versus performance**: the knowledge/capacity attributed to a speaker is not identical to what appears in one concrete act of language use.

These are not merely analogies. They expose the same logical error that modern model evaluation often makes:

> `did not emit behavior b under procedure P`  
> does not entail  
> `system lacks capacity b`.

But the historical lesson also creates the core identification burden: **what intervention is licensed to count as an access cue rather than new learning?**

---

# 2. Generative-model ancestry: quality and coverage are separate objects

Generative modeling has long treated **mode coverage** as distinct from sample quality.

GAN mode collapse made the issue concrete: a model can produce individually plausible samples while failing to cover important parts of the target distribution.

NeurIPS 2018/2019 precision–recall work for generative models explicitly separates:

- **precision / fidelity** of generated samples;
- **recall / coverage** of the target distribution.

Therefore the generic scientific move

> `average quality is high but the behavioral repertoire is narrow`

is already a mature generative-model idea.

For open-ended language generation, Holtzman et al. (ICLR 2020) showed that maximizing sequence probability can yield bland / repetitive / degenerate text even when the underlying probabilistic LM is strong. Nucleus sampling was motivated precisely because the mode is not a faithful description of a good generative distribution.

Meister et al. (TACL 2023) make the information-theoretic version explicit through **locally typical sampling**: desirable strings need not be maximum-probability strings; generation can instead target local typicality relative to conditional entropy.

Thus `mode ≠ repertoire` is not a new law.

---

# 3. Critical conceptual obstacle: literal support is almost useless for ordinary LMs

For a standard autoregressive LM with softmax probabilities, essentially every finite token sequence whose tokens remain in the vocabulary has nonzero probability.

So literal mathematical support does **not** separate:

- a capability that occurs once in 10 samples;
- once in 10^6 samples;
- once in 10^30 samples.

All are technically supported.

The scientifically useful object must therefore be **effective / accessible support**.

But accessibility requires a resource / intervention class:

- how many iid samples?
- what temperature / decoder?
- what prompt family?
- may we search over prompts?
- may we optimize activations?
- may we fine-tune weights?
- how many training examples?
- how many bits of adaptation?
- what counts as the same semantic behavior?

Changing the resource class changes the set of `reachable` behaviors.

This is the core reason IP11 does not automatically provide one decisive quantity.

---

# 4. Modern frontier already occupies the strongest accessibility notions

## 4.1 Finite-sampling accessibility — NeurIPS 2025 RLVR

**Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?** uses large-`k` pass@k to distinguish ordinary accuracy improvements from expansion of the base model's reasoning-capability boundary.

Its core conclusion is precisely an IP11 claim:

> current RLVR primarily makes successful reasoning paths easier to sample rather than eliciting fundamentally new reasoning patterns beyond those accessible in the base model.

Therefore:

> `post-training reweights existing reasoning paths versus creates new reachable paths`

is directly owned in the current RLVR regime.

## 4.2 Prompt / fine-tuning accessibility — capability elicitation literature

NeurIPS 2024 **Stress-Testing Capability Elicitation with Password-Locked Models** constructs model organisms whose capabilities are intentionally hidden and asks which elicitation methods recover them.

ICML 2025 **The Elicitation Game** systematically compares prompting, activation steering and fine-tuning, again treating capability as something that may be present but inaccessible under weak elicitation.

Thus:

> `failure under prompting does not imply absent capability; stronger elicitation can reveal it`

is a direct active parent.

## 4.3 Program / adaptation complexity — ICML 2026

**Operationalising the Superficial Alignment Hypothesis via Task Complexity** supplies an even more principled accessibility quantity:

> the length of the shortest program which, conditioned on the pretrained model, achieves a target level of task performance.

This reframes `the model already contains the capability` as **adaptability under a program-length budget**.

The paper finds that pretraining can make high performance reachable while still requiring very large programs to access it; post-training can collapse that access complexity by orders of magnitude.

This directly occupies the tempting move:

> replace arbitrary prompting success by a resource-sensitive notion of latent capability.

## 4.4 Distributional contraction under RLHF — direct owners

Kirk et al. 2023 show RLHF can improve OOD generalization while substantially reducing output diversity relative to SFT.

NAACL 2025 **One fish, two fish, but not the whole sea** finds aligned models display less conceptual diversity than instruction-fine-tuned counterparts.

ICLR 2026 **Escaping Policy Contraction** explicitly formalizes RLHF support contraction through a **Support Retention Ratio**, the fraction of SFT completions retaining non-negligible probability after RL optimization, and proposes a method to mitigate it.

Therefore the generic claim

> `alignment shrinks the behavioral repertoire`

is directly occupied both behaviorally and methodologically.

## 4.5 Decoding-induced effective-support contraction — ICML 2026 Outstanding

**The Flexibility Trap** shows that arbitrary-order diffusion-LM generation can exploit generation flexibility to bypass high-uncertainty forking tokens, reducing solution diversity.

The relevant scientific point for IP11 is that **inference policy itself can contract the effective repertoire without changing the underlying model parameters**.

So model distribution, training, and decoder must be distinguished.

---

# 5. The most attractive question: `erasure or inaccessibility?`

A natural old-to-new crystallization is:

> **When post-training removes a behavior from ordinary generations, was the underlying capability erased or merely made inaccessible?**

This exactly mirrors Tulving's availability/accessibility distinction.

It also matters: if alignment merely suppresses access, different cues or light adaptation may recover the behavior; if training actually destroys the relevant competence, recovery should require relearning.

Unfortunately this does not survive novelty / ownership.

## Direct neighbors

- capability-elicitation work explicitly studies hidden-but-recoverable capabilities;
- machine-unlearning work distinguishes genuine removal from output suppression and uses relearning / extraction attacks to test the difference;
- RLVR capacity work asks whether post-training creates genuinely new reasoning beyond base capability;
- superficial-alignment work asks whether post-training mainly surfaces pretraining-acquired knowledge;
- alignment / policy-contraction work measures loss of non-negligible probability mass.

A paper asking `RLHF diversity collapse: erased or suppressed?` reviewer-compresses to:

> **RLHF diversity-collapse paper + capability elicitation / unlearning-style recovery test.**

That is an A+B descendant, not a new mother question.

### Verdict

**KILL CURRENT DESCENDANT.**

---

# 6. Why there is no single natural `reachable repertoire` quantity

Several candidates look principled but answer different questions.

## 6.1 `pass@k`

Defines reachability under a finite iid sampling budget. Good for success probability; blind to how many qualitatively distinct successful modes exist. Already central to RLVR capacity-boundary work.

## 6.2 probability threshold / Support Retention Ratio

Defines effective support relative to an epsilon threshold. Useful for tracking contraction, but epsilon is operational and probability does not define semantic distinctness. Already directly used by ICLR 2026 policy-contraction work.

## 6.3 entropy / diversity metrics

Measure spread, but high entropy can arise from superficial lexical variation rather than qualitatively different strategies. Diversity measurement is already crowded and risks benchmark/evaluator work.

## 6.4 typical set

Information theory gives a principled set of probable sequences, and typicality has already informed language decoding. But typicality characterizes sequence probability, not task-level capability or semantic strategy identity.

## 6.5 shortest elicitation / adaptation program

Task complexity gives a principled notion of **how much intervention information** is required to reach target performance. But it is a task-level adaptability quantity, not the geometry / diversity of the model's behavioral repertoire, and is already directly owned by ICML 2026.

## 6.6 semantic mode coverage

Potentially closest to `behavioral repertoire`, but requires defining an equivalence relation over outputs / strategies. Without an independent scientific ontology this becomes evaluator design.

There is no old theory that selects one of these as the universally correct notion of model capability.

---

# 7. Candidate-shaped descendants closed

## H1 — `RL creates new support vs reweights old support`

Direct NeurIPS 2025 owner in reasoning; literal support is also mathematically unhelpful.

**Verdict: DIRECT OWNER.**

## H2 — `RLHF erases alternatives vs makes them inaccessible`

Capability elicitation + unlearning/suppression + alignment-diversity literature already owns the components. A recovery experiment is A+B.

**Verdict: CROWDED / SUCCESSOR.**

## H3 — `alignment contracts semantic strategy support`

Policy contraction and conceptual-diversity work directly occupy generic contraction. A new semantic clustering metric would be evaluator-first.

**Verdict: DIRECT OWNER + METRIC TRAP.**

## H4 — `decoder vs model: where did diversity disappear?`

Classic decoding literature already distinguishes model distribution from generation algorithm; Flexibility Trap provides a current direct case.

**Verdict: CROWDED.**

## H5 — `define capability by minimal elicitation complexity`

Directly occupied by password-locked elicitation work and ICML 2026 task complexity.

**Verdict: DIRECT OWNER.**

## H6 — `typical-set capability rather than modal capability`

Typical-set / locally-typical decoding is already a mature probabilistic-language-generation route, and sequence typicality is not task capability.

**Verdict: WRONG SCIENTIFIC LEVEL.**

## H7 — `behavioral repertoire as a geometry / manifold`

Requires choosing embeddings / semantic equivalence / density thresholds after the fact; reviewer compression becomes another diversity evaluator.

**Verdict: NO NATURAL QUANTITY.**

---

# 8. Reviewer compression

All current routes compress to one of:

> **`NeurIPS 2025 RLVR capacity boundary, but with another capability domain.`**

> **`ICLR 2026 policy contraction, but with a semantic diversity metric.`**

> **`RLHF diversity collapse + password-locked capability elicitation.`**

> **`Superficial Alignment Hypothesis / task complexity, but applied per behavior.`**

> **`nucleus / typical sampling, but reframed as repertoire.`**

> **`machine unlearning's deletion-vs-suppression distinction, but for alignment.`**

None leaves a prior-work-inaccessible inference.

---

# 9. Exhaustion verdict

**WALL-H / IP11 is EXHAUSTED AS A STANDALONE TOPIC GENERATOR FOR THE CURRENT SEARCH.**

No L-series. No pilot.

The wall remains useful as a **scientific-state reminder**:

> top-1 / average performance does not characterize what a stochastic model can do, and observed failure does not imply absent latent capacity.

But the current literature already supplies multiple incompatible operationalizations of `can do` and has direct owners for each important one.

Without a substantive theory that picks the resource / intervention class, `reachable support` is not one natural estimand.

---

# 10. Reopen condition

Only reopen IP11 when a substantive domain gives an independently justified definition of accessibility.

A future candidate must provide:

1. a natural behavioral equivalence class, not post-hoc embedding clusters;
2. a principled resource budget / intervention class derived from the science, not convenience;
3. two mature theories that predict different changes in the **same accessibility quantity**;
4. an experiment that distinguishes probability reweighting, retrieval/elicitation failure, and genuine acquisition/loss;
5. informative positive, opposite, and null outcomes;
6. a contribution that cannot be compressed to capability elicitation, mode coverage, policy contraction, superficial alignment, or unlearning.

Until then:

> **Do not invent another support / diversity / pass@k metric.**
