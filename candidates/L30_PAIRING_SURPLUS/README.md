# L30 — What Does Pairing Teach?

**Status:** **HOLD — PILOT UNDER-RESOLVED (2026-09-13)** — E01 complete; see `notes/E01_REPORT.md`. Authorization expired: continuing requires re-selection.  
**Date:** 2026-09-13  
**Target:** ACL / EMNLP / NAACL Main

## Locked research question

> **If pretrained language models can become substantially instruction-following from responses alone, what additional behavior is actually learned from the correct correspondence between an instruction and its response?**

The project studies the **marginal causal value of the joint dependence** in instruction-tuning data, not whether instruction-response alignment is broadly useful.

A compact statement of the scientific object is:

> **What does the joint `X↔Y` pairing buy beyond exposure to the same prompt marginal `P_X` and response marginal `P_Y`?**

The working hypothesis is deliberately not locked as the answer. One attractive possible law is:

> **Prompt/response marginals unlock generic instructability; correct pair dependence buys conditional precision where pretraining has not already learned the map.**

E01 is authorized only to identify whether a pairing-specific causal quantity exists at resolvable scale. The conditional law above is a later question and must not be assumed from the pilot.

---

# 1. Scientific pressure / mother phenomenon

The question is not generated from an ablation trick. It arises from several strong results that make the role of paired supervision unexpectedly unclear.

## Response-only adaptation can unlock instruction following

Hewitt et al., **Instruction Following without Instruction Tuning** (2024, arXiv:2409.14254), show that training only on response strings, with no paired instructions, can move pretrained Llama-2 / OLMo models from near-base behavior to substantial instruction following. Their analysis also shows that base models already prefer a good response for an instruction over a good response taken from another instruction surprisingly often, supporting the idea that much of the conditional map already exists after pretraining.

Project page: https://www.cs.columbia.edu/~johnhew/instruction-following.html  
Paper: https://arxiv.org/abs/2409.14254

An, Kim, and Kim, **Revealing the Inherent Instructability of Pre-Trained Language Models** (Findings of EMNLP 2025), independently introduce **Response Tuning (RT)**: remove the instruction and its mapping to the response and train only a response distribution. They again find broad instruction-following behavior, including strong requirement-following behavior on instruction-following evaluations.

ACL Anthology: https://aclanthology.org/2025.findings-emnlp.285/

**Important correction:** in their ordinary IT baseline, as in conventional instruction tuning, loss is computed on response tokens. The IT–RT comparison therefore does **not** contain a hidden prompt-token-loss factor. The additional information in IT is that each response is generated/trained while conditioned on its paired instruction.

## Prompt-side training is independently useful

Chatterjee et al., **On the Effect of Instruction Tuning Loss on Generalization** (TACL 2025), study **Weighted Instruction Tuning (WIT)** and show that prompt-token supervision can itself improve downstream instruction-following/generalization relative to conventional response-only loss. This is a separate objective-level fact, not a confound inside An et al.'s IT–RT comparison.

ACL Anthology: https://aclanthology.org/2025.tacl-1.62/

The relevant pressure is therefore not a simplistic `prompt useful / response useful` decomposition. It is that substantial instructability can be unlocked without learning new pairwise mappings from scratch, while several training signals around the marginals remain useful.

## Pretraining already makes instruction following cheap to unlock

Vergara-Browne et al., **Operationalising the Superficial Alignment Hypothesis via Task Complexity** (ICML 2026), formalize the idea that pretraining can drastically reduce the information required to reach high downstream performance, including instruction following.

Paper: https://arxiv.org/abs/2602.15829

This strengthens the premise that post-training may often select/unlock structure already present in the pretrained model, but it does **not** identify how much of the remaining adaptation information is specifically the correct instruction-response correspondence.

---

# 2. What prior work already owns — and what it does not

This project must not claim that “instruction-response alignment matters” is new.

Several neighboring lines already own that broad statement:

- Yang et al., **MAIN: Mutual Alignment Is Necessary for instruction tuning** (EMNLP 2025 Main) argue that pair quality depends on mutual instruction-response alignment and build data-generation methods around it: https://aclanthology.org/2025.emnlp-main.644/
- Du et al., **FedDQC** (Findings ACL 2025) introduce an instruction-response alignment score based on the difference between response likelihood with and without the instruction and show that higher-alignment pairs are higher-quality/easier-to-learn data: https://aclanthology.org/2025.findings-acl.791/
- Zhang et al., **The Wisdom of Hindsight Makes Language Models Better Instruction Followers** (ICML 2023) use instruction relabeling / contrastive structure to prefer appropriate instruction-output relations: https://proceedings.mlr.press/v202/zhang23ab.html

Therefore the paper is **not**:

- “aligned pairs are better than misaligned pairs”;
- another instruction-data quality score;
- another method for filtering instruction-tuning data;
- another mutual-information metric;
- another Superficial Alignment paper saying pretraining contains many abilities;
- another RT replication.

## Strongest reviewer compression

> `Hewitt/An: response marginals can unlock much instruction following`  
> `WIT: prompt-side supervision can also help`  
> `MAIN/FedDQC/Hindsight: instruction-response alignment is useful`  
> `SAH: pretraining makes instruction following cheap to unlock`  
> `= you are just showing that pairing matters.`

## Missing inference that survives the compression

None of those results identifies the counterfactual quantity:

> **Holding the exact prompt pool and exact response pool fixed, what is the causal value of preserving the correct `X↔Y` correspondence?**

Write the target quantity conceptually as:

`Pairing Surplus = Performance(P_XY) - Performance(P_X P_Y)`

This is not a proposal to estimate mutual information as a data-quality metric. It is an **interventional training estimand**: preserve the marginals while changing only whether the joint correspondence is correct, absent, or wrong.

This is the current paper identity.

---

# 3. Competing scientific accounts

The search/selection stage does not require pretending there are three unrelated theories. E01 distinguishes three live interpretations that already matter scientifically.

## Account A — Pairing teaches conditional control

Pretraining and marginal adaptation provide generic instructability, but correct pair dependence still teaches nontrivial instruction-specific binding. If so, preserving the true correspondence should add measurable downstream requirement sensitivity beyond the same marginals without correspondence.

## Account B — Pretrained conditional maps already do most of the work

The pretrained model already contains much of the useful `X→Y` map. Marginal adaptation mainly moves probability mass toward response-like behavior / exposes instructability. Correct pairing may then contribute little in the pilot regime.

This is stronger than saying “RT works”: it says the **marginal causal value of new pair dependence is small after controlling both marginals**.

## Account C — Wrong pairing actively corrupts an existing map

Correct pairing may matter less because it teaches a map from scratch than because inconsistent pairings overwrite or interfere with useful conditional structure acquired during pretraining.

This produces an important distinction between:

- **no usable correspondence during training**, and
- **systematically wrong correspondence during training**.

That distinction is why E01 requires both a decoupled arm and a shuffled arm.

---

# 4. E01 — authorized bounded pilot

## Purpose

E01 answers only:

> **At fixed prompt/response marginals and matched training budget, is the correct correspondence itself a load-bearing source of instruction-following improvement, and is wrong correspondence different from absent correspondence?**

Do not begin hidden-state analysis, data selection, method development, broad model sweeps, or a full C2 study before this quantity is established at useful resolution.

## Preferred initial regime

Use **Gemma-2-2B + Alpaca-Cleaned** as the starting regime because it is small enough for a bounded multi-seed pilot and sits near the model/data regimes used by the RT/WIT mother lines. Exact checkpoint/data preprocessing should be verified from the source repositories before running; do not silently substitute a neighboring variant and claim it is matched.

The scientific comparison matters more than preserving this exact implementation if a source-level incompatibility appears. Any necessary implementation change must preserve the causal estimand and be documented before outcomes are inspected.

## Core matched arms

All load-bearing arms should use the same response-token training objective unless a technical implementation forces otherwise. Keep, as far as the causal comparison requires, the same prompt pool, response pool, number of training examples, response-token count, optimizer family, learning-rate policy, steps, batch construction, and evaluation protocol.

### P — Paired

Train on the correct pairs:

`x_i → y_i`

The response can condition on its true instruction.

### D — Decoupled marginal

Preserve the prompt/response material and sequence-budget controls, but prevent response prediction from using the paired prompt information. The model therefore receives the response marginal without usable `X↔Y` correspondence.

The concrete masking/packing implementation is **not** scientifically sacred. It must pass a sanity check showing that D is not creating a new artifact via unusual positions, attention behavior, or serialization.

### S — Shuffled pairing

Randomly permute which prompt is paired with each response:

`x_{π(i)} → y_i`

The prompt and response marginals are identical to P, but the correspondence is wrong.

**P vs S is the primary clean correspondence contrast.**

### RT sanity anchor

A conventional response-only RT arm may be run as a sanity anchor to determine whether the D implementation behaves like a correspondence-free response-marginal learner rather than as a pathological masking regime.

Prompt-only WIT is **not required in E01**; it is already a mother-evidence line and does not identify pairing surplus.

---

# 5. Primary estimands

The pilot should preregister at least these contrasts before looking at outcome signs.

## Correct-pair value beyond no pairing

`Δ_pair = P - D`

Interpretation: causal value of correct correspondence over an approximately correspondence-free response-marginal condition.

## Damage from wrong pairing

`Δ_wrong = D - S`

Interpretation: whether explicitly wrong correspondence is worse than having no usable correspondence.

## Pure correspondence contrast

`Δ_corr = P - S`

Interpretation: with prompt and response marginals held fixed, how much does preserving the correct correspondence matter relative to a wrong one?

`Δ_corr` is the cleanest marginal-matched quantity; `Δ_pair` and `Δ_wrong` determine what kind of scientific story, if any, explains it.

---

# 6. Evaluation and resolution

## Primary behavioral evaluation

Prefer **IFEval** for the pilot because it provides deterministic, mechanically checkable instruction constraints and avoids an LLM judge for the load-bearing measurement.

Use the benchmark's standard task definition and report both instruction-level and prompt-level views where appropriate, but the inferential unit must not be artificially inflated by treating multiple constraints from the same prompt as independent training/evaluation samples.

**Bootstrap / confidence intervals should cluster at the prompt level.**

InFoBench can be a useful secondary check because the RT mother paper uses decomposable requirements, but it should not be added merely to hunt for a favorable sign.

## Resolution expectation

The IT–RT gaps in the mother line are only a rough upper bound on the pairing-specific effect. E01 is specifically allowed because a few-percentage-point effect should be measurable with deterministic instruction-following gold and a small model, unlike L19 where the load-bearing matched effect was already below feasible resolution.

Working resolution guidance for selection:

- `5–8 pp`: comfortably resolvable if training variance is controlled;
- `3–4 pp`: potentially meaningful and worth carrying into C2 if stable across seeds;
- `≤2 pp`: requires tight intervals before being interpreted as substantive evidence.

Use multiple training seeds (default target: **3**) and report seed variation explicitly. Do not convert a noisy near-null into the claim that pairing is unnecessary.

## Null / HOLD rule

If all contrasts are within roughly 2 pp but the confidence interval still allows a scientifically meaningful ~3–4 pp effect, mark:

> **HOLD — PILOT UNDER-RESOLVED**

Do not call it a substantive null.

If the experiment can tightly exclude a pairing surplus of practical/scientific interest (roughly the 2–3 pp scale in the pilot regime), the result can support the conclusion that pairing is not load-bearing **in that regime**; whether that is paper-scale still requires re-selection.

---

# 7. Outcome map — freeze before reading results

## `P > D ≈ S`

Correct correspondence contributes genuine conditional control beyond the marginals.

This establishes a pairing-surplus quantity but does **not** by itself make a Main paper. The next question is when/why the surplus is needed.

## `P ≈ D > S`

The pretrained map plus marginal adaptation is largely sufficient; explicitly wrong pairing damages it.

This is scientifically attractive because the role of correct pairs may be **preservation / anti-corruption of an already learned map**, rather than teaching the map from scratch.

Do not relabel this as generic forgetting. The object is the causal value of the joint dependence in the supervision distribution.

## `P ≈ S > D`

Semantic correctness of the pair is not the load-bearing factor; merely training responses in the presence of prompt-like context may be doing the work.

This substantially weakens the current pairing story and requires re-selection before any new paper identity.

## `P ≈ D ≈ S`

Pair correspondence is not load-bearing at resolvable scale in this regime.

If confidence intervals are tight, this challenges strong universal readings of “alignment is necessary” but may still be too narrow for Main. If intervals are loose, HOLD. Do not rescue by searching for a model/dataset where the desired sign appears.

## Any strong heterogeneity

Heterogeneity is paper-relevant only if it follows a **pre-motivated condition**, not if we scan categories after the fact.

The principal pre-motivated condition for later work is pretrained instruction-response association strength.

---

# 8. C2 growth path — not authorized yet

C1/E01 identifies whether pairing has marginal causal value. A Main-level paper likely requires a conditional law explaining **where pairing is needed**.

The most promising prior quantity is pretrained instruction-response association strength. FedDQC's IRA-like quantity gives one operational precedent:

`association_i ≈ NLL(y_i) - NLL(y_i | x_i)`

The metric itself is not novel and must not be presented as our contribution.

The scientific question is whether **pretraining's existing `X→Y` association predicts the marginal causal value of preserving the pair during post-training**.

Two live intuitions give opposite predictions:

### Pretraining-completion account

If pretraining already strongly binds `x_i` to `y_i`, paired supervision should add less:

`base association ↑  →  pairing surplus ↓`

### Alignment-quality / learnability account

MAIN/FedDQC-style intuition instead suggests strongly aligned pairs are especially effective training signals:

`base association ↑  →  pairing surplus ↑`

A future C2 should therefore be an **intervention on which pairs retain correct correspondence**, not merely an item-level correlation between base likelihood and downstream correctness. Matching response NLL, length, source/task, and other obvious difficulty variables will matter.

**C2 is not authorized by this file.** E01 must first establish a resolvable pairing-dependent quantity, after which the project returns to selection.

---

# 9. Main-level contribution bar

C1 alone is insufficient if the result is only:

> “shuffling answers drops IFEval by 6 points.”

Prior work already owns the broad importance of alignment.

The paper becomes Main-shaped only if the project can support a new scientific inference such as:

> **Pretraining already supplies much of the instruction→response map; marginal adaptation unlocks generic instructability, while paired supervision contributes conditional information specifically where that pretrained map is insufficient.**

or, under a different result:

> **The primary value of correct pairing is preserving/selecting pretrained conditional structure rather than teaching instruction following from scratch.**

The desired progression is therefore:

> **C1 identification → C2 conditional law / explanation → optional C3 mechanism only if it deepens the same claim.**

Do not force an interpretability section merely to make the paper look mechanistic. Existing work already shows causal instruction-following directions; a later internal analysis is useful only if it distinguishes marginal unlock from pairing-specific strengthening.

---

# 10. Anti-resurrection / scope guard

L30 is **not** Temporal Forgetting, K174 capability-vs-readout, or generic represented-but-unused work.

The project does not ask whether an ability survives post-training or can be rescued from an earlier state. It asks about the **causal information content of the supervision distribution** under a fixed pretraining initialization.

Likewise, it is not a data-quality/filtering project. The data are an intervention surface for identifying what instruction tuning learns.

If execution drifts into any of the following, re-select:

- building a better alignment score;
- selecting “high-quality” instruction data without identifying pairing surplus;
- proving again that RT works;
- proving again that WIT works;
- generic SFT-vs-base comparisons;
- generic hidden-state instruction-direction analysis;
- claiming mutual information itself as novelty.

---

# 11. Exact authorization

**Authorized:**

> **E01 only: a small-model, multi-seed matched P/D/S training pilot with deterministic instruction-following evaluation, plus the minimum RT sanity control needed to validate D.**

**Not authorized:**

- C2 IRA-stratified training;
- hidden-state / activation patching / steering;
- large model sweeps;
- new benchmark construction;
- method optimization;
- scaling-law claims;
- full-study training.

After E01, update this README with:

1. exact implementation and deviations from the intended estimand;
2. arm-wise results with prompt-clustered uncertainty and seed variation;
3. whether D passed its sanity/construct check;
4. the pre-registered outcome interpretation;
5. a fresh selection decision before any C2.

---

# 11b. E01 outcome (2026-09-13)

E01 ran as pre-registered: 12 matched runs (4 arms x 3 seeds), Gemma-2-2B +
Alpaca-Cleaned, IFEval 541 prompts, prompt-clustered seed-resampled intervals.
Full record: `notes/E01_REPORT.md`; interim go/no-go read: `notes/E01_INTERIM_EP1.md`.

| contrast | pp | 95% CI |
|---|---|---|
| `Delta_corr` P - S | **+14.97** | [+10.66, +19.29] |
| `Delta_wrong` D_mask - S | **+13.12** | [+8.81, +17.44] |
| `Delta_pair` P - D_mask | +1.85 | [-1.79, +5.42] |
| construct D_mask - D_rt | +1.91 | [-1.66, +5.42] |

**`Delta_pair` -- the quantity this project actually owns -- is under-resolved.**
Point estimate below 2 pp with an interval that still admits a real ~5 pp effect,
stable across epoch 1 and epoch 3. Under section 6's frozen rule this is
`HOLD`, not evidence that pairing is unnecessary.

The interval is **evaluation-limited, not seed-limited**: of its 7.58 pp width,
only ~1.6 pp comes from training seeds and ~6 pp from the 541-prompt IFEval
sample. More seeds cannot fix it; this is the L19 failure mode reached from the
evaluation side.

`Delta_corr` and `Delta_wrong` are decisive and large, but `Delta_corr` is
precisely the "shuffling drops IFEval by N points" result section 9 rules
insufficient, since MAIN / FedDQC / Hindsight own that parent.

One finding is **not** resolution-limited: S collapses to 6-11 distinct
responses across 541 prompts in every seed (median 62-241 chars), while D_mask,
which has no correspondence either, keeps 537-539 distinct responses at 441-585
chars. Wrong correspondence destroys prompt-conditional behaviour; absent
correspondence does not. This also means `Delta_corr` is partly
collapse-vs-no-collapse rather than a graded capability gap and must not be
reported as the latter.

D_mask passed its construct check (zero logit movement under an equal-length
instruction swap and under random tokens behind the mask, while P moves 26.6).

**Consequence:** the identity would have to move from *what pairing teaches* to
*what wrong pairing destroys*. That is a claim mutation under
`RESEARCH_EXECUTION.md` section 8, so this authorization has expired and the
candidate must re-enter selection with a Claim Novelty Delta before further
compute. C2 remains unauthorized.

# 12. Current verdict

| Gate | Verdict |
|---|---|
| Natural RQ | **PASS** |
| Stable mother | **PASS** |
| Anti-resurrection | **PASS** |
| Direct owner | **PASS — no direct `fixed marginals, intervene on correspondence` owner found in bounded search** |
| Reviewer compression | **SURVIVES — must explicitly face MAIN / FedDQC / Hindsight / RT / WIT / SAH** |
| Identification | **PASS with P/D/S, conditional on D construct sanity** |
| Outcome robustness | **PASS** |
| Resolution | **PASS FOR PILOT** |
| Main growth | **PASS only if a C2-style conditional law survives re-selection** |
| Resolution (post-E01) | **FAIL for `Delta_pair` — evaluation-limited** |
| Status | **HOLD — PILOT UNDER-RESOLVED; re-selection required** |

The one-sentence working identity is:

> **What does the correct instruction-response pairing teach beyond the two marginals?**
