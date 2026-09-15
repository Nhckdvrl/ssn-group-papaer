# Search Round VII — 2026-09-15

## Status

**Target:** ACL / EMNLP / NAACL Main  
**Calibration:** TACL / ICLR / ICML / NeurIPS  
**Result:** **0 NEW SURVIVOR**  
**New pilot authorization:** **NONE**  
**L42:** unchanged — `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`

This round explicitly used the revised search object:

> **standing important problem × genuinely new 2025–26 leverage**

rather than `recent paper → limitation → next experiment`.

The round was not shallow. It audited independent pools in post-training, optimization, architecture, attention, autoregressive factorization, and mechanistic interpretability. Several questions reached SERIOUS-LOOK; none retained an independent Main-level paper identity after owner + identification audit.

---

# 1. Main outcome

The new search process generated substantially better mother questions, but the 2025–26 landscape is unusually dense. The dominant failure mode was not “unimportant question”; it was:

> **a real standing question becomes newly identifiable, but a strong 2025–26 paper has already used essentially that leverage to answer it.**

This is still useful evidence: `standing problem × leverage` is producing the right *kind* of question. The next search should therefore keep this generator but move to different standing problems rather than shrinking the dead questions below into residual distinctions.

---

# 2. Audited walls — do not resurrect cosmetically

## VII-1 — Does RLVR create new skills or only sharpen pretrained primitives?

**Verdict: KILL — direct mother-question ownership.**

2026 work already frames the debate explicitly and attacks it with multiple identification strategies, including atomic-step solvability and tasks outside the base model's sampled capability boundary. Variants such as “language-only”, “different reasoning strategy”, or “larger model” are sequel territory.

Representative recent owners:

- *New Skills or Sharper Primitives?* (2026)
- *Does RLVR Extend Reasoning Boundaries?* (ACL 2026)

---

## VII-2 — Is chain-of-thought useful because of its semantic content, or because it supplies extra sequential compute / workspace?

**Verdict: KILL — mature direct lineage.**

Pause-token expressivity, latent-CoT work, and causal interventions treating CoT tokens as program variables already attack the semantic-content vs computational-workspace distinction. A new wording would not produce an independent scientific claim.

---

## VII-3 — What does data order / curriculum really change during LM pretraining?

**Verdict: KILL — explicit 2026 training-science owners + taste mismatch.**

ACL 2026 directly studies when curriculum helps and which ordering direction matters; ICLR 2026 work further studies interaction with learning-rate decay. Another curriculum law would likely become data-centric and is not current preference.

---

## VII-4 — Does replacing Transformer attention with SSM/Mamba change the internal mechanism of in-context learning?

**Verdict: KILL — mechanism lineage already mature.**

ICML 2024 onward already asks whether Mamba learns to learn; ACL 2026 work compares ICL beyond Transformers with behavioral and intervention evidence. “Same question at larger scale / more natural tasks” is not enough.

---

## VII-5 — Does MoE sparsity reduce feature interference / polysemanticity by inducing expert specialization?

**Verdict: KILL — active explicit object.**

ICML 2025 already links MoE to intrinsic interpretability / polysemanticity, while later work studies routing specialization and gradient conflict. Do not reopen as generic “why experts specialize”.

---

## VII-6 — Is the usual attention-versus-MLP division of labor architectural necessity or an SGD-selected convention?

This reached **SERIOUS-LOOK A**.

Mother question:

> Transformers are commonly described as using attention for cross-token routing and MLPs for feature transformation / parametric memory. Is that division forced by the architecture, or can the computation migrate when one path is removed or altered?

Why it initially looked strong:

- important before any probe;
- simple scientific consequence for mechanistic interpretability;
- modern gated-attention architectures offered a clean-looking leverage.

**Fatal owner:** *A Controlled Study of Attention-Only Transformers* (2026-07) already performs parameter/FLOP/depth-matched training, scales to substantial token budgets, isolates the main deficit to parametric recall, and reports that storage-like computation migrates into attention output projections when FFNs are removed.

Earlier GAU/FLASH work also already fused MHSA and FFN-like computation in a gated unit.

**Verdict: KILL — exact scientific owner.** Adding a modern gate would only ask whether migration becomes easier.

---

## VII-7 — Is pretraining loss a sufficient statistic for later post-training learnability?

This reached **SERIOUS-LOOK B / fragile**.

Initial question:

> If two base models have the same current pretraining loss, should they have the same capacity to improve under the same subsequent SFT/RL budget?

Why it looked strong:

- current pretraining-to-RL work reports strong predictability of post-RL performance from pretraining loss;
- new objectives such as reinforcement-style pretraining create plausible leverage for constructing models with different training histories;
- both answers would matter: sufficiency would justify current scaling proxies; failure would imply a hidden state variable governing post-training returns.

Owner / identity audit:

- **Nexus (2026):** same pretraining loss can already yield different downstream generalization, attributed to optimizer-induced geometry / common minima.
- **Weight Decay Improves Language Model Plasticity (2026):** explicitly argues that validation loss is insufficient for choosing pretraining hyperparameters when future adaptation matters, and causally varies pretraining weight decay before downstream fine-tuning.
- **Good Pretraining, Bad SFT (2026-09):** checkpoint rankings can reverse under an identical downstream training stack; local solution density is correlated with the later ranking.
- **Representation Collapse in Sequential Post-Training (2026):** representation concentration is linked to reduced future plasticity.
- older work already studies pretraining for language-model plasticity via active forgetting.

The surviving formulation would have to match both current loss **and current behavior/function** and then show different RL learning slopes. That is experimentally interesting, but its best-case identity is now a tighter control inside an already explicit plasticity program rather than a new parent question.

**Verdict: KILL — do not preserve by over-narrowing.**

---

## VII-8 — Does Muon change which solution / algorithm a Transformer learns, rather than merely reaching a loss faster?

**Verdict: KILL — optimizer implicit-bias ownership already explicit.**

ICLR 2026 work explains Muon through associative-memory parameters, isotropic singular spectra and heavy-tail learning. Other 2026 work explicitly studies simplicity bias under Muon and optimizer mismatch when switching Adam-pretrained models to Muon fine-tuning. The mother question is already a current research program.

---

## VII-9 — QK normalization as an inductive bias: what computation is lost when query/key magnitude is removed?

This briefly reached SERIOUS-LOOK.

Mother question:

> Standard attention uses both direction and norm: query norm acts as a token-specific softmax temperature, while key norm can make a token globally more attractive. Modern QK normalization removes these radial degrees of freedom. Is QK-Norm really only a stability trick, or does it remove a meaningful routing channel?

Why-now leverage:

- QK-Norm has become common in modern LLM architectures;
- matched with/without-QK-Norm training is practical.

**Fatal owner:** ICLR 2026 *QUEST: Query-Modulated Spherical Attention* explicitly decomposes query/key norm roles, argues that full QK normalization limits token-specific sharpness, analyzes the norm-gradient feedback, and proposes normalizing keys while preserving query norm.

**Verdict: KILL — same quantity + same architectural identification.**

---

## VII-10 — Why can modern LLMs compress K/V capacity so aggressively while retaining many query heads?

Mother question:

> What does the apparent asymmetry between many queries and few/shared key-value representations tell us about the true degrees of freedom required for attention?

**Verdict: KILL — owner surface already broad and mechanistic.**

Relevant ownership includes:

- GQA / MQA quality-vs-KV-sharing line;
- NeurIPS 2024 DHA, which independently allocates / fuses K and V heads based on redundancy;
- 2026 *Do Transformers Need Three Projections?*, which studies Q/K/V projection sharing and attributes some success to low-rank / overlapping representational spaces;
- 2026 mechanistic work on MLA bottlenecks asking what information compressed KV latents preserve/discard and how circuits reorganize.

A new GQA-vs-MHA interpretability study would be a successor paper.

---

## VII-11 — Is input/output embedding weight tying a harmless parameter-saving trick or a real modern-LM inductive bias?

**Verdict: KILL — near-perfect old-problem + new-leverage owner already exists.**

The 2017 classical paper already analyzed update rules. ACL 2026 Findings *Weight Tying Biases Token Embeddings Towards the Output Space* gives the modern mechanism: output gradients dominate early, tied embeddings become biased toward unembedding geometry, early-layer computation suffers, and input-gradient scaling provides causal evidence.

This is an excellent **taste calibration example** of exactly the search shape desired here, but it is already done.

---

## VII-12 — What inductive bias does left-to-right autoregressive factorization buy relative to masked diffusion / arbitrary-order generation?

**Verdict: KILL — heavily occupied 2026 frontier.**

The surface now contains controlled AR-vs-MDLM comparisons, blockwise causal-diffusion hybrids, trainability studies that inject left-to-right locality, arbitrary-order AR formulations, and *The Flexibility Trap*. The broad question is important, but current leverage is already being used directly by multiple groups.

Do not reopen as “another matched AR-vs-diffusion comparison.”

---

## VII-13 — Is the advantage of RL over SFT mainly reward, or mainly learner-induced/on-policy state distribution?

Mother question:

> Classical teacher forcing trains on fixed states, while RL trains on prefixes generated by the current policy. In reasoning post-training, how much of RL's advantage comes from reward itself versus moving supervision onto the model's own state distribution?

This was a natural old exposure-bias question with a modern reasoning-RL leverage.

**Fatal owners:**

- *On-Policy Supervised Fine-Tuning for Efficient Reasoning* (2026)
- *Post-Training is About States, Not Tokens: A State Distribution View of SFT, RL, and On-Policy Distillation* (2026)
- ICLR 2026 *NFT*, which shows a supervised binary-feedback formulation can match/surpass RL and proves equivalence to GRPO in a strict on-policy setting.

**Verdict: KILL — direct scientific owner, not merely adjacent method work.**

---

# 3. What survived?

## New L-series candidate

**NONE.**

## New pilot authorization

**NONE.**

## Fragile / WATCH carried forward from this round

**NONE.**

The pretraining-loss/plasticity idea was deliberately **not** kept as WATCH after the full audit: the broad scientific program is now already explicit enough that matching one extra nuisance variable would create a residual paper rather than a new parent question.

Existing WATCH items from prior rounds are unchanged.

---

# 4. Search lesson from Round VII

The strongest calibration example in this round was the weight-tying lineage:

> 2017 durable question / heuristic → modern scale changes practice → 2026 causal mechanism identifies *why* the old heuristic can become harmful.

That is close to the desired paper genesis. The mistake would be to turn it into a template and now search “another old architecture trick that became harmful.”

The durable update is narrower:

> **Keep important old questions alive long enough to notice when a new regime makes their previously unidentifiable causal distinction operational.**

Round VII shows that this process now generates strong questions reliably. The remaining difficulty is landscape scarcity, not lack of kill criteria.

Do **not** respond by shrinking these dead questions or by inventing another checklist. Continue searching from different long-lived scientific problems / author lineages and treat new 2025–26 work primarily as a leverage bank before using it as an owner bank.
