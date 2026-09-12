# 2026-09-12 — Continued Topic Search VI

**Target:** ACL / EMNLP / NAACL Main  
**Mode:** cross-paper anomaly search; SAME-QUANTITY contradictions; modern-regime rewrites; no survivor quota.  
**Round start:** `main = 8f44c314142a90767f4f6dbef89ae1b1322d8266`.

This round continued from Search V with the stricter rule that a single paper's unfinished mechanism is not a default source of novelty. The search prioritized repeated anomalies, structural properties that worsen while task competence improves, and genuinely same-quantity tensions across training regimes. Temporal Forgetting remained hard-banned. No candidate package was created.

## Round result

# **0 new SERIOUS candidates**

This is intentional. Several hooks were scientifically attractive, but owner assassination showed that their parent objects are already mature, or the exact mother phenomenon is not established strongly enough to justify betting a paper on discovering it.

---

## 1. RLVR improves rewarded accuracy while degrading unrewarded structural/general properties

### Hook

Across recent papers, RLVR/reasoning post-training can improve verifiable task accuracy while degrading properties not directly constrained by the reward: instruction adherence/controllability, perception/faithfulness, disagreement modeling, or other general capabilities.

### Why it initially looked strong

This appeared in multiple independent 2026 settings rather than as one isolated table cell. A tempting abstraction was:

> **Does outcome optimization systematically convert a broadly competent policy into a narrower policy that preserves reward-relevant behavior while erasing orthogonal structural constraints?**

### Owner assassination

The abstraction is already too close to several active parents:

- ACL 2026 explicitly studies **general-capability forgetting during RLVR**;
- ACL 2026 work directly centers loss of instruction following / controllability in reasoning models;
- outcome-only reward shortcutting / reward hacking / mode collapse already supplies the obvious causal story.

Representative owners:

- `Beyond Reasoning Gains: Mitigating General-Capability Forgetting in RLVR` (ACL 2026)
- `Scaling Reasoning, Losing Control` (ACL 2026)
- `ReasonIF` (Findings ACL 2026)

### Reviewer compression

> `general-capability forgetting + reasoning-control degradation + Goodhart/shortcutting = your abstraction`.

### Verdict

**DROP broad parent.** Do not reopen by choosing a different unrewarded capability.

---

## 2. Post-training raises accuracy but destroys modularity / locality / compositional editability

### Hook

Rather than ordinary forgetting, ask whether SFT/RL turns a decomposable computation into a more entangled policy: competence rises, but module swapability, local editability, or compositional closure falls.

### Search outcome

The abstraction is attractive, but the required mother phenomenon was not found. Existing papers establish pieces in different quantities:

- emergent modularity in LLMs;
- LoRA/module composability;
- compositional-RL learnability;
- generic circuit reorganization after post-training.

They do **not** jointly establish the same stable law `post-training competence ↑ → modularity/locality ↓`.

### Failure mode

Promoting this now would violate the current search rule:

> abstraction first → hunt for a phenotype.

### Verdict

**DROP / NO MOTHER PHENOMENON.** Reopen only if 2–3 independent papers first establish the same structural degradation quantity.

---

## 3. Search-V Seed A — strict logical information monotonicity

### RQ seed

If context `C` already suffices for an answer and `r` is logically entailed by `C`, should the model be behaviorally invariant under `C` versus `C + r`?

This is stricter than ordinary irrelevant-information distraction because the two inputs are information-equivalent under logical closure.

### Search outcome

Search found related but non-identical results:

- correct/redundant information can distract models;
- models redundantly memorize derivable multi-hop facts during training;
- decomposition/rephrasing can alter inference behavior.

But there is still no strong repeated mother result for the exact intervention:

> `C` vs `C + entail(C)` with the original evidence and question held fixed.

### SAME-QUANTITY status

**Not established.** Training-time redundant-fact memorization and inference-time logical-closure invariance are different quantities.

### Verdict

**SEED ONLY — NOT SERIOUS / NO COMPUTE.** Search V status unchanged. Do not manufacture a benchmark and gamble on the effect.

---

## 4. Search-V Seed B — more intermediate supervision can teach a worse algorithm

### Initial pattern

Controlled algorithmic work shows dense teacher forcing/intermediate supervision can induce shortcuts, while less exposed iterative computation can generalize better.

### Natural-language owner search

The hoped-for natural-language extension is no longer an empty space. 2025–2026 reasoning-distillation work directly establishes a mature **teacher/student learnability gap**:

- stronger/longer teacher CoT is not monotonically better for smaller students;
- reasoning-trace granularity has a non-monotonic optimum;
- trajectory suitability matters more than teacher strength;
- long-CoT internalization/compression is now explicitly studied.

Representative work:

- `Small Models Struggle to Learn from Strong Reasoners` (ACL 2025)
- work on key factors / CoT granularity in reasoning distillation (ACL 2025)
- `Which Reasoning Trajectories Teach Students to Reason?` (ACL 2026)
- `When Internalization Fails` (ACL 2026)

### Reviewer compression

> `synthetic dense-supervision shortcut + Small-Model Learnability Gap / trajectory suitability = your paper`.

### Verdict

**DROP as a broad natural-language continuation.** The exact synthetic algorithmic phenomenon remains interesting, but it does not currently yield a fresh Main-level parent in natural-language reasoning.

---

## 5. SAME-QUANTITY tension — can RLVR expand the base model's capability boundary?

### Why this was the strongest hook of the round

Two strong lines make apparently incompatible claims about essentially the same quantity:

- NeurIPS 2025 `Does Reinforcement Learning Really Incentivize Reasoning Capacity in LLMs Beyond the Base Model?` argues current RLVR mainly reshapes/reweights trajectories already within the base model's sampling distribution and does not expand the large-`pass@k` capability boundary.
- ACL 2026 Main `Does RLVR Extend Reasoning Boundaries?` uses a controlled maze setting where the base policy remains at 0% even under increased sampling yet RLVR learns solutions, arguing for genuine boundary expansion.

This passed the initial SAME-QUANTITY smell test much better than ordinary cross-benchmark contradictions:

> **Can training produce solvable behavior outside the base policy's effective support/boundary?**

### Owner assassination

Unfortunately the contradiction has already become a research line rather than an unnamed gap:

- ACL 2026 `RL-PLUS: Countering Capability Boundary Collapse...` explicitly centralizes the base-boundary problem and uses an external hybrid policy to move beyond it;
- 2026 boundary-aware curriculum / teacher-guided RL work explicitly claims capability expansion beyond the base boundary;
- theory work now gives learnability conditions in terms of base coverage / task-advantage-like quantities.

### Reviewer compression

> `Limit of RLVR + RL-PLUS / boundary-aware curriculum + controlled task = your hidden-condition paper`.

Even if a cleaner condition exists, the parent scientific debate is already named, occupied, and rapidly developing.

### Verdict

**DROP despite high scientific quality.** This is a useful example of a genuine SAME-QUANTITY contradiction that is nevertheless already too owned to become L30.

---

## 6. Post-training changes updateability / editability rather than knowledge itself

### Hook

Could reasoning/post-training preserve a capability yet make it harder to locally update, edit, or revise—i.e. competence improves while causal updateability declines?

### Owner assassination

This is no longer open enough:

- Findings ACL 2026 directly studies editability of post-trained delta parameters;
- EMNLP/ACL 2025–2026 work directly combines knowledge editing with chain-of-thought/reasoning;
- by August 2026 a Nature Machine Intelligence perspective explicitly frames principled knowledge editing for LLM reasoning.

### Verdict

**DROP.** Narrowing to one reasoning model family would be a cell, not a new parent.

---

## 7. Post-training delays decision formation toward later layers

### Hook

A potentially clean structural transition is that a base model may expose task-relevant/answer-relevant information early, while instruction/reasoning post-training delays logit alignment and makes late layers more load-bearing.

This could have led to:

> **Does post-training improve final behavior by changing the answer, or by moving when the answer becomes causally committed?**

### Evidence found

Recent early-exit/layer-wise work already reports that:

- modern/post-trained models can have weaker early-exit behavior and later logit alignment;
- SFT effects are disproportionately localized in middle/final layers;
- hidden-state decoding and early-exit behavior varies strongly between base and instruct models.

### Owner risk / compression

The exact phenotype is already being studied as layer-wise SFT / early-exit alignment, while generic post-training circuit rerouting was already killed in Search IV. Adding activation patching or a causal localization sweep would be an obvious mechanistic continuation, not a fresh scientific parent.

### Verdict

**DROP.** Do not revive as `decision timing` unless a separate repeated behavioral law makes timing itself the load-bearing scientific object.

---

## 8. Long-context training has opposite short-context transfer across training regimes

### Hook

Long-context continued pretraining is often reported to hurt short-context competence, while long-context SFT can improve it. This looks like an appealing old-law rewrite where the sign of the same length intervention depends on training regime.

### Anti-resurrection check

This maps directly back to the project's **L19 — Causal Ingredients of Long→Short SFT Transfer**, whose mother paper is Zheng et al., EMNLP 2025, `When Long Helps Short`.

The paper itself already centralizes the sign contrast and analyzes MHA/FFN plus contextual-vs-parametric knowledge preference. L19 then attempted the cleaner matched causal contrast and was killed as K184 on **cost/resolution**, not novelty.

### Verdict

**DO NOT REOPEN.** This search route is L19, not a new candidate.

---

## 9. Multimodal instruction tuning: learn vision, lose text reasoning/control

### Hook

ACL 2026 reports a striking layer-wise pattern after multimodal instruction tuning: early modality separation, mid-layer alignment, and late-layer degradation, alongside deterioration of inherited text reasoning.

This initially looked like a repeated training-stage structural anomaly: adding a new modality can improve multimodal competence while damaging the computation inherited from the language backbone.

### Owner assassination

The parent is already mature:

- ACL 2024 `Multi-modal Preference Alignment Remedies Degradation of Visual Instruction Tuning on Language Models` directly centers language-capability degradation after visual instruction tuning;
- 2024 work already frames visual instruction tuning as forgetting instruction/safety behavior;
- EMNLP 2025 work studies neuron-level fusion to mitigate catastrophic forgetting in MLLMs;
- continual visual instruction tuning has an explicit dual-forgetting literature.

The 2026 layer pattern is interesting mechanism evidence, but following it with causal patching/localization reviewer-compresses to a mature catastrophic-forgetting parent plus a new diagnostic.

### Verdict

**DROP.** No new multimodal candidate.

---

## 10. Structural inverse-scaling / compositionality degradation

### Hook

Search for a stable law where general task ability/scale improves while a structural property such as systematicity, compositionality, or prior override worsens.

### Search outcome

Strong examples exist, but direct owners already centralize them:

- ACL 2026 `Code over Words` directly names **Semantic Inertia** and reports inverse scaling when models must override pretrained priors with contradictory in-context rules;
- compositional generalization and post-training alignment remain active direct topics;
- generic semantic-equivalence/equivariance was already killed in Search V.

No third structural quantity emerged that was both repeated across settings and not already named by its owners.

### Verdict

**DROP current hooks.** Do not generalize several different failure quantities into one synthetic `structural degradation` law without a common estimand.

---

# Search-V seed status after this round

- **Strict logical information monotonicity** — still **SEED ONLY**; exact stable mother phenomenon not found.
- **More intermediate supervision can teach worse algorithms** — natural-language continuation is now substantially weakened by the mature teacher/student learnability-gap literature; **do not promote**.
- **Reasoning overrides adaptive strategy gating** — not reopened this round; still lacks repeated same-quantity mother evidence.

---

# Round-level lessons

1. **A real contradiction is not enough.** The RLVR capability-boundary case is genuinely SAME-QUANTITY and scientifically excellent, but 2026 successors already turned it into a named research line.
2. **Cross-paper repetition must precede abstraction.** `post-training destroys modularity` sounded attractive, but without repeated same-quantity evidence it would be an invented umbrella rather than a discovered law.
3. **Structural degradation is often already a topic once named precisely.** Control loss, editability, multimodal forgetting, early-exit depth, semantic inertia, and teacher/student learnability each have direct owners.
4. **Do not mistake better mechanistic tools for a new parent.** A mature phenomenon plus activation patching, layer localization, or checkpoint analysis is exactly the future-work-completion pattern this search now rejects.
5. **Anti-resurrection worked.** The long-context training-regime sign flip immediately mapped back to L19/K184 rather than being renamed as a fresh candidate.

# Final status

**No L30. No new SERIOUS candidate. No formal selection handoff.**

The round produced useful negative knowledge but did not locate a scientific object that simultaneously satisfies:

> repeated stable anomaly / same-quantity tension  
> + unoccupied parent question  
> + competing computational accounts  
> + plausible decisive operation  
> + Main-level room to grow.

Continue searching rather than lowering the bar.