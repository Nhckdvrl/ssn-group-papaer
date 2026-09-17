# Failed Topics — 2026-09-17 Cross-Domain Search IV

**Status:** durable kill ledger. Read together with every other `FAILED_TOPICS*` file before generating new topics. These are negative/process evidence only, never positive taste exemplars.

## Search-discipline update

Do not over-focus on architecture micro-puzzles merely because they admit elegant mechanistic analysis. A good mechanistic topic still needs an independently important behavior/computation question. For interpretability, prefer the Zhao/Cho-style chain `representation -> computation -> causal mechanism -> controllability`, but only after a strong mother question exists.

---

## F58 — Does a sampled token preserve the uncertainty that preceded it?
**Question.** If the same token is produced from a high-confidence versus ambiguous predictive state, does that prior uncertainty continue to affect downstream computation after the token is fixed?
**Kill reason.** The model cannot observe external sampling temperature; if the same internal state and same sampled token are used, no extra uncertainty state is introduced. If context is changed to induce different confidence, downstream differences are confounded by context. Adjacent uncertainty-propagation work is also already mature.
**Revival condition.** A clean intervention that changes latent uncertainty while holding realized history and causal context fixed.

## F59 — Unchosen branches / option pruning during generation
**Question.** After generation commits to one continuation, does the model retain representations of valid unchosen futures or prune them away?
**Nearest prior.** ICLR 2026 work on internal planning directly studies planning horizon and branch awareness; later work on forked futures/hidden APIs defines states through future computational affordances.
**Kill reason.** Parent is directly occupied.

## F60 — Surface-path convergence under self-generated paraphrases
**Question.** If a model reaches the same meaning through different self-generated wording, do later hidden states converge to a shared semantic state or remain path-dependent?
**Kill reason.** Paraphrase-invariant latent features, semantic invariance, and prompt-sensitivity literatures already own the high-level object; adding self-generation mainly creates a dynamic variant.

## F61 — Contraction versus divergence of autoregressive trajectories
**Question.** Are small token-level perturbations corrected/absorbed by generation dynamics or amplified into different semantic trajectories?
**Nearest prior.** 2026 trajectory-commitment/hallucination work already studies bifurcation, attractors, single-token perturbations, and causal patching; theoretical work studies autoregressive error amplification.
**Kill reason.** Generalizing beyond hallucination would be an extension of an existing trajectory-stability parent.

## F62 — Revision as local state update versus regeneration
**Question.** When editing a near-correct draft, does the model construct a difference/error representation and locally update, or effectively regenerate the target from scratch?
**Kill reason.** Revision/edit-intent/self-correction is already a mature behavioral object; a mechanism study would be a direct follow-up unless a new independent computational law is found.

## F63 — Shared input/output token basis under weight tying
**Question.** Why should reading a token and generating a token share the same embedding geometry, and does tying force understanding/generation representations to align?
**Nearest prior.** 2024–2026 work directly studies assumptions and geometric consequences of input-output weight tying, including gradient/causal analyses.
**Kill reason.** Exact parent already occupied.

## F64 — Prediction becomes action in closed-loop autoregressive generation
**Question.** Training predicts observed tokens, while generation emits tokens that become future inputs; does the model learn to account for how current outputs change its future computation?
**Kill reason.** In the ideal conditional-model limit, autoregressive sampling already reproduces the joint data distribution, so the tension only appears off-distribution/under model error and collapses to exposure bias, behavior cloning, or planning. Those parents are mature.
**What to learn.** Before elevating an architecture tension, check whether it vanishes in the ideal-model limit.

## F65 — How normalized Transformers represent confidence / evidence magnitude
**Question.** Repeated LayerNorm/RMSNorm removes global scale, yet models must represent confidence/evidence strength. Where can such magnitude live?
**Nearest prior.** NeurIPS 2024 `Confidence Regulation Neurons` identifies large null-space signals that affect final LayerNorm/logit scale; follow-up work studies the mechanism without LayerNorm.
**Kill reason.** Beautiful architecture puzzle, but directly solved.
**What to learn.** Strong mechanism papers can follow `architectural constraint -> seemingly impossible function -> bypass channel -> causal verification`.

## F66 — Why next-token pretraining contains an evaluator/reward model
**Question.** How can a pure generator acquire an internal evaluator/reward signal without explicit preference supervision?
**Nearest prior.** 2025–2026 work explicitly derives/locates generalist reward models inside pretrained LMs and studies their generalization relative to explicit reward heads.
**Kill reason.** Parent directly occupied.

## F67 — Same task learned through ICL versus weight updates: same computation or not?
**Question.** If an ability is acquired in context versus by SFT/in-weight learning, does the model implement the same internal algorithm?
**Nearest prior.** NeurIPS 2024 compares internal representation landscapes under ICL and SFT; ICLR 2025 studies competition/switching between in-context and in-weight predictors.
**Kill reason.** Acquisition-route equivalence is already an explicit parent.

## F68 — Direct visual reasoning versus text-mediated visual reasoning in VLMs
**Question.** Does a VLM reason directly over visual representations or translate visual evidence into a language-like pathway first?
**Nearest prior.** 2026 causal-patching work explicitly identifies direct visual versus text-mediated pathways; ICLR 2026 work localizes visual integration points.
**Kill reason.** Routing/pathway parent directly occupied.

## F69 — Future prediction induces object permanence / invisible latent state
**Question.** Does predicting future video force a model to maintain states for objects that are temporarily invisible but still causally relevant?
**Nearest prior.** Temporal-coherence/future-prediction learning has already been shown to induce object permanence; later world-model and persistent-slot work directly studies this.
**Kill reason.** Functional-necessity parent already occupied.

## F70 — Multi-timescale factor separation in unified speech/audio models
**Question.** Does a unified predictor self-organize slow speaker identity, medium-timescale prosody, and fast phonetic/content factors into distinct latent dynamics?
**Nearest prior.** Speech-tokenizer and unified speech/audio/music work already make semantic/acoustic/speaker/prosody disentanglement a central object.
**Kill reason.** Timescale framing is novel-looking but reviewer-compressible to mature speech factor disentanglement.

## F71 — Multi-environment prediction forces causal latent states
**Question.** Are invariant/causal representations formed only when prediction must generalize across environments or interventions rather than a single observational distribution?
**Kill reason.** This is the core territory of causal representation learning and invariant prediction; identifiability under environments/interventions is already formalized.

## F72 — Long-horizon video anticipation requires latent intention
**Question.** When identical visible histories admit multiple futures, does anticipation require a latent intention variable that selects among futures?
**Nearest prior.** Action-anticipation work already explicitly introduces latent/high-level intention because observed history underdetermines the future.
**Kill reason.** Existing parent directly owns the functional-necessity argument.

## F73 — Task-dependent reuse of the same acoustic feature
**Question.** How can a unified audio model suppress a physical dimension such as pitch as nuisance for one task while preserving/amplifying it for music or prosody tasks?
**Nearest prior.** Task-aware MoE/unified audio models already route speech/audio/music features differently; work on ASR-centric suppression explicitly studies loss of paralinguistic cues.
**Kill reason.** Becomes a controlled case study inside an existing feature-routing/disentanglement parent.

## F74 — Semantic commutativity versus neural path dependence of independent updates
**Question.** If two knowledge/state updates are semantically independent, should applying A then B equal B then A despite neural updates being path-dependent?
**Nearest prior.** Sequential knowledge editing, update-order interference, null-space methods, and order/commutativity-based training are already mature.
**Kill reason.** Re-enters the editing/order-robustness literature.

---

## Important process lessons from F58–F74

1. **Do not confuse an elegant architecture puzzle with an important mother question.** Mechanistic tractability is not scientific importance.
2. **Functional necessity is a useful generator, but check ownership early.** If a literature already says task X logically requires latent variable Y, a mechanistic version is likely follow-up work.
3. **Check identifiability before novelty.** Several attractive ideas die because the intervention cannot distinguish the claimed latent mechanism from ordinary contextual differences.
4. **Cross-modal analogies collide quickly.** Diffusion, VLM, video, and speech papers are rapidly importing one another's mechanisms; obvious `CV phenomenon -> LM analogue` ideas should receive an immediate collision audit.
5. **For interpretability, prefer computation over component discovery.** `head X matters` or `feature Y is decodable` is weak unless tied to a clear transformation and causal behavioral role.
6. **Zhao/Cho-style positive lesson:** start from an important behavior/explanatory failure; identify a representation structure; describe the transformation of that representation across computation; map the transformation to components; causally intervene; only then consider controllability. Do not start by hunting heads/vectors.
