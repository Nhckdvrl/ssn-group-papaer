# 2026-09-14 — Premise-Collision / Old-Law Search II

**Target:** ACL / EMNLP / NAACL Main  
**Search mode:** pressure-first; no survivor quota  
**Outcome:** **one new Selection pass: L36**; all other leads killed, merged, or held.

## 0. Search doctrine used in this round

This round applies the provenance lesson extracted from ICML 2026 Outstanding *The Flexibility Trap*:

> Do not begin by hunting unexplained anomalies. Mine Related Work for two independently established scientific premises whose mechanisms create a tension under a shared objective, then ask what **new third quantity / conditional law** resolves the collision.

A valid premise collision must pass all of:

1. both premises are independently established rather than invented for our experiment;
2. `Prior A + Prior B` is not itself the contribution;
3. the collision yields a new scientific quantity or conditional law;
4. a direct observable corresponds to that quantity;
5. preferably there is a natural continuous / matched intervention;
6. fresh owner search does not show that the third quantity is already the obvious next step of either parent.

The round deliberately changed scientific pools rather than staying around entropy / reasoning forks.

---

# 1. SURVIVOR — L36

## L36 — Why Did the Beam-Search Curse Disappear?

**Verdict:** `PILOT-AUTHORIZED — E01 ONLY`  
**Package:** `candidates/L36_BEAM_CURSE_REGIME_SHIFT/`

### Provenance

**Old law:** Stahlberg et al., ACL 2022 show that intrinsic output uncertainty predicts probability-mass spread, mode inadequacy, search difficulty, and large-beam deterioration in classic neural seq2seq models. MT is high uncertainty and exhibits the curse; GEC is lower uncertainty and does not.

https://aclanthology.org/2022.acl-long.591/

**Modern reversal:** Pang et al., TACL 2025 report that the classic beam-search challenge may not apply to LLM translation; larger beams improve BLEU while semantic COMET changes little.

https://aclanthology.org/2025.tacl-1.4/

**Persistent old ingredient:** Wu et al., NeurIPS 2025 show that LLM translation sequence likelihood remains weakly aligned with translation quality, including translation-specialized LLMs.

https://papers.neurips.cc/paper_files/paper/2025/hash/e46f7f5c7e981a61cbcf6b56b7a8fe9d-Abstract-Conference.html

### Scientific collision

Machine translation remains a one-to-many task. Therefore external task ambiguity did not simply disappear when the architecture became a decoder-only LLM. Yet the classic uncertainty-conditioned beam pathology appears to disappear, while likelihood–quality misalignment remains.

RQ:

> **Which intermediate model/search quantity stopped transmitting intrinsic task ambiguity into beam-search pathology in the LLM regime?**

This is stronger than the earlier rough hook `likelihood-quality misalignment still exists, so why no curse?`: ACL 2022 already supplies a specific old conditional law. L36 asks why that established law breaks.

### Decisive first stage

Reuse ACL 2022's natural multi-reference WMT19 uncertainty substrate rather than inventing an ambiguity proxy. Human-reference disagreement fixes intrinsic uncertainty independently of the tested model.

E01 first audits beam scoring/stopping semantics, then tests a modern open translation LLM on the same uncertainty construct.

**Kill:** if high-uncertainty LLM examples recover the classic adverse beam-width pattern after semantics are matched, the old law survives and L36 dies.

### Instrument-semantics audit

The TACL LLM4MT repo explicitly says its implementation follows ParroT/HuggingFace. Public ParroT `train/inference.py` uses standard `GenerationConfig` beam search rather than a bespoke search algorithm. Therefore the previous blocker `opaque unpublished search semantics` is no longer sufficient reason to HOLD; E01 can make every relevant setting explicit and check whether the reported reversal survives.

### Ownership

Fresh exact-query owner search found no 2025/2026 paper that both:

- conditions the modern LLM beam-width effect on the **same human-reference intrinsic-uncertainty quantity**, and
- explains why the ACL-2022 uncertainty law changes in the LLM regime.

Reviewer compression remains serious:

> `ACL 2022 uncertainty law + TACL 2025 disappearance + classic length/stopping literature`.

L36 survives only if it identifies a changed model-side relation and ultimately gives a revised conditional law / causal boundary.

---

# 2. KILLED / MERGED LEADS

## A. Multilingual MoE specialization vs cross-lingual transfer

Collision:

- MoE language specialization can reduce interference;
- cross-lingual transfer needs shared parameters / experts.

Candidate question:

> When does routing specialization cross from beneficial interference reduction into harmful isolation that cuts transfer?

**KILL — direct owner.** ACL 2026 Findings SARA already reports that routing divergence between high- and low-resource languages reduces expert sharing and harms transfer, then explicitly aligns routing to restore transfer. Earlier multilingual neuron-specialization work already frames the same sharing-vs-interference tradeoff.

No novelty from changing language pairs or routing metric.

---

## B. Stated-value vs action-value elasticity

Collision:

- EMNLP 2025 Outstanding establishes a static Value–Action Gap;
- ACL 2025 Best establishes alignment elasticity / rebound toward the pretraining distribution after further fine-tuning.

Candidate third quantity:

> Do stated values and contextual actions rebound at different rates under subsequent fine-tuning?

**KILL — dynamic owner now exists.** A 2026 study of emergent misalignment followed by realignment jointly measures actual harmful behavior and stated/self-reported harmful intent as alignment state changes. Parameterizing the same idea as two decay constants would be a narrower extension, not a new Main-level inference.

---

## C. Reasoning training vs online deliberation in risky choice / invariance

Pressure:

ACL 2026 Outstanding *Mind the (DH) Gap!* attributes risky-choice differences between reasoning and conversational models to reasoning-oriented training. Modern Qwen3-style checkpoints allow same-weight thinking / non-thinking inference, apparently enabling `training state` vs `online deliberation` decomposition.

**NO CURRENT FORM.** Same-weight Think-On/Think-Off comparisons are already common across 2026 bias, safety, judging and reasoning work, while the repository's historical L12 route already owned reasoning-induced invariance / trajectory-control territory. The obvious successful result would be too easy to compress as `same model, toggle thinking, bias changes`.

Do not resurrect through a new behavioral domain.

---

## D. SFT repetition law vs RL prompt reuse

Collision:

- long-CoT SFT benefits strongly from repeatedly revisiting a small set;
- ACL 2026 RL scaling work finds high-quality data can also be reused effectively in data-constrained RL.

Key distinction:

- SFT repeated prompt usually repeats a fixed target trajectory;
- RL repeated prompt produces fresh on-policy trajectories/rewards.

**MERGE INTO L35 PROVENANCE / FUTURE BOUNDARY, NOT A NEW CANDIDATE.** The scientific decomposition remains `problem identity vs supervision/trajectory identity`, which is already L35's parent object. Creating L36-like wording around training objective would duplicate the parent rather than open an independent question.

---

## E. Semantic inertia across ICL vs fine-tuning

Collision:

- ACL 2026 Findings *Code over Words* shows semantic inertia: in-context contradictory rules fail to override pretrained semantic priors, sometimes worsening with scale;
- ACL 2025 Best alignment elasticity shows weight-level post-training can rebound toward pretraining behavior.

Candidate question:

> Is resistance to the same pretrained prior a conserved quantity across context-space adaptation and weight-space adaptation?

**NO CURRENT FORM.** ACL 2026 *Fine-tuning vs. In-context Learning in LLMs: A Formal Language Learning Perspective* already directly compares the two learning modes and finds their inductive biases diverge as proficiency grows, with ICL substantially more coupled to vocabulary/pretraining conditions than FT. A cross-task correlation between `ICL override difficulty` and `FT rebound` lacks a clean shared unit and decisive selective operation. Reviewer compression is too strong.

---

## F. Rare-word inverse scaling as semantic inertia

Mother:

TACL 2025 reports rare-word translation remains difficult and that Llama2-13B can struggle more evidently than 7B on rare-word prediction.

Collision:

ACL 2026 *Code over Words* independently shows larger models can exhibit stronger semantic inertia when local rules contradict learned priors.

Candidate explanation:

> larger translation LLMs may prefer strong common-language priors over sparse local bilingual evidence, causing rare-word inverse scaling.

**NO CURRENT FORM — IDENTIFICATION.** General token-frequency bias is already an EMNLP Main scientific object, and the available natural MT experiments do not selectively distinguish `rare mapping never learned` from `mapping learned but suppressed by a stronger common-word prior`. Candidate ranking, gloss prompting, or paraphrasing would not uniquely identify prior suppression. Do not promote a nice story without the operation.

---

## G. Resurrection audit: actuality / imperfective paradox

ACL 2026 Best *The Imperfective Paradox in Large Language Models* supplies a strong modern semantic mother phenomenon and dataset, superficially appearing to repair an old K007-style aspect/actuality blocker.

**DO NOT RESURRECT.** Two reasons:

1. the ACL Best paper already owns a large part of the relevant behavior and representation-vs-decision explanation (`internal aspectual distinction present, final inference dominated by goal-attainment priors`);
2. a fresh August-2026 re-analysis, *The Imperfective Paradox Is Not Necessarily in Large Language Models: A Benchmark Failure Before a Model Failure*, argues that much of the benchmark has conceptual / NLI construct mis-specification and re-decomposes errors into aspect classification, surface-form attraction, and sufficiency bias.

Thus the new work does not simply repair old gold; it creates both ownership and construct-validity risk.

---

# 3. Provenance lessons from this round

### Premise collision is a generator, not a novelty guarantee

Several of the cleanest collisions were already direct owners: multilingual MoE specialization vs transfer, and stated values vs action dynamics. The collision should generate questions quickly; owner assassination remains mandatory.

### An old law is stronger than a vague contradiction

The beam route improved only after finding ACL 2022's explicit conditional law. `LLM beam curse disappeared` alone is a curiosity. `The same task-level uncertainty should cause pathology according to a published law, but no longer does` is a scientific pressure with a precise quantity to reuse.

### Reuse the parent's quantity whenever possible

L36 can reuse human multi-reference disagreement `u`, avoiding the common failure of inventing a new entropy proxy and then claiming to revisit an old uncertainty law.

### New data can both repair and destroy a resurrection

The imperfective-paradox case is the cautionary example: a new ACL Best initially looks like it repairs the old dataset blocker, but it simultaneously owns the behavior and is itself immediately challenged on construct validity. `blocker fixed` never implies `candidate resurrected`.

---

# 4. End-of-round portfolio delta

New this round:

- **L36 — PILOT-AUTHORIZED — E01 ONLY**

No other lead is promoted.

The round ends with one genuine new Selection pass rather than lowering the bar to obtain multiple survivors.