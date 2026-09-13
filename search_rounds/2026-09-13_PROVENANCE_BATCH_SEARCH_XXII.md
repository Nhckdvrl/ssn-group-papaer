# 2026-09-13 — Provenance-Batch Search XXII

**Target:** ACL / EMNLP / NAACL Main  
**Mode:** Related-Work provenance first; batch generation before owner assassination; no survivor quota.  
**Authorization:** **NO COMPUTE FROM THIS FILE.**  

This round was opened after a process correction: earlier search had repeatedly drifted into `invent hook -> search owner -> kill`, which gives low surface area and overproduces immediate follow-ups. The corrected generator is:

> **read strong paper backwards -> reconstruct what Related Work made the authors believe -> identify the single inference the focal paper added -> transfer that provenance move across independent scientific objects -> only then run owner assassination.**

This file records only durable search outcomes. A `SERIOUS` lead here still requires full `RESEARCH_TOPIC_SELECTION.md`; it is not a pilot.

---

# 1. Provenance lessons reinforced in this batch

## 1.1 Strong papers often rewrite the scientific quantity, not just fill a limitation

Reusable moves re-observed across ACL/EMNLP/NAACL strong work include:

- conflicting explanations -> replace binary debate with a quantity/conditional decomposition;
- strong community claim + weak identifying evidence -> construct the direct stress test;
- old empirical law + changed model regime -> test whether the load-bearing premise still holds;
- stable anomaly -> identify a hidden condition that makes the apparently contradictory results compatible;
- widely interpreted measurement -> ask whether it actually identifies the claimed causal quantity;
- multiple surface anomalies -> elevate them into one dynamical object only when the common object is independently constrained.

Do **not** mechanically transfer topics or instruments. Transfer the provenance move.

## 1.2 Explore before Understand

Public research-taste / idea-generation advice sampled across Marco Tulio Ribeiro, Chris Olah, Nicholas Carlini, Neel Nanda, Jia-Bin Huang, John Schulman, PRADA Lab and other research-reading/taste notes converges on a useful discipline for this project:

- widen the adjacent possible / surface area before emotionally committing to one idea;
- generate many ideas and use cheap noisy criticism/history as feedback;
- ask what the paper contributes in one sentence;
- deep-read the small subset whose implicit assumptions matter;
- reject a project if its **best-case successful outcome** is not itself exciting;
- favor challenge-assumption / stress-test moves over `add one more dimension/adjective` or hammer-nail generation.

This is now treated as a search-stage rule, not a stylistic preference.

---

# 2. New serious lead — access-conditioned knowledge encoding

## Working title

**Does Future Access Shape What an LLM Learns?**

## Status

# **SERIOUS — FULL SELECTION REQUIRED — NO COMPUTE**

This is the only genuinely new lead from the present batch that survives internal anti-resurrection strongly enough to deserve Selection effort. It is not yet `PILOT-AUTHORIZED`.

## Scientific origin

Jiang et al., ACL 2024, *Instruction-tuned Language Models are Better Knowledge Learners* reports a strong order effect in factual knowledge acquisition:

- standard recipe: continued pretraining on new documents, then instruction tuning;
- PIT: instruction/QA exposure **before** document training;
- PIT improves subsequent question answering substantially (reported +17.8% over standard instruction tuning);
- the paper explicitly hypothesizes that seeing how knowledge will be accessed through questions before document training lets the model encode complex documents in a way that takes future access into account.

Source: https://aclanthology.org/2024.acl-long.296/

The parent therefore already owns:

> `access/instruction exposure before documents -> overall knowledge learning improves`.

It also already **states** the access-aware-encoding hypothesis. Merely replicating PIT, probing its hidden states, or showing that PIT improves document learning is not a new paper.

## Missing scientific sentence

The stronger unresolved question is:

> **Does an LLM learn new knowledge in an access-neutral way, or does the access distribution it expects *before the information arrives* selectively determine which parts / views of the same later information become easy to retrieve and retain?**

Short form:

> **Is parametric knowledge acquisition access-conditioned?**

This is deliberately stronger than `why does PIT help?`.

## Three rival accounts

### A — prospective / access-conditioned encoding

Prior exposure to access regime A versus B selectively changes how **subsequently learned** knowledge is encoded. The same later documents therefore yield an A-vs-B crossover on new knowledge.

Critical signature:

> `pre-access regime × query/access view × new-vs-old knowledge`

with the A/B crossover concentrated on **new knowledge learned after the access manipulation**, not equally present on old knowledge.

### B — generic learnability

PIT mainly makes the model a better learner / instruction follower. New knowledge improves broadly across access views; there is no strong selective A↔B crossover.

### C — retrieval-policy / query-skill specialization

Prior A/B access training only specializes the model to A/B query forms or retrieval policies. The same A/B preference should therefore be visible on **old/pre-existing control knowledge as well as newly learned knowledge**.

The old-vs-new interaction is load-bearing because it separates generic query proficiency from selective effects on later acquisition.

## Decisive estimand

The paper should not be organized around an overall PIT accuracy delta. The candidate estimand is a three-way interaction:

`pre-access training (A vs B) × test access/view (A vs B) × knowledge status (learned after manipulation vs old/control knowledge)`.

The cleanest evidence for Account A would be:

1. A- and B-trained models have matched enough baseline access competence on old/control knowledge to make retrieval-skill asymmetry interpretable;
2. both then receive **the exact same later documents / factual objective / token budget**;
3. the A↔B crossover becomes materially larger for the newly learned facts than for old/control facts;
4. the selectivity survives at least one **neutral/paraphrastic access probe** so that it cannot be reduced to memorizing one prompt surface.

A/B must be the same scientific quantity / relation under different access structures, not two unrelated QA tasks.

## Reviewer compression to beat

Strongest attack:

> `Jiang et al. already say PIT works because future question/access structure changes encoding; this is just the missing control proving their explanation.`

This attack wins if the project only shows:

- PIT > standard IT again;
- PIT-A performs better on A prompts;
- a representation probe differs;
- one query format transfers better than another.

The project survives only if the result establishes a **general selective law** unavailable from the parent:

> changing the expected future use of knowledge before exposure selectively changes what is learned from an otherwise identical later experience.

A successful final paper would need to show that this is not tied to one PIT template or one relation wording.

## Main-level growth path under audit

If C1 survives:

### C1 — Selective crossover

Show access-conditioned acquisition on identical later learning experience, with old-knowledge controls ruling out pure query skill.

### C2 — When does prospective access matter?

The ACL-2024 parent motivates a load-bearing hidden condition: QA access is simple while documents interweave many facts. A stronger law would predict weak/selective effects when one fact is trivial to encode, but growing access-conditioned prioritization when multiple facts compete inside a complex document / limited update budget.

This must be predeclared, not searched after C1.

### C3 — Encoding versus interface persistence

Test whether the access-favored information remains advantaged under neutral paraphrases and later interference / matched neutral retrieval. If the effect vanishes once the trained interface is removed, the result is retrieval-policy specialization; if it persists, it is stronger evidence for acquisition/retention priority.

C2/C3 are not authorized by this file.

## Main blockers

1. **External owner audit incomplete.** Current public search in this round did not reveal an exact A/B selective-access crossover successor, but search-tool limits were reached before an exhaustive 2024–2026 citation/successor audit could be completed. Absence of a hit is not novelty evidence.
2. **Substrate/workload.** No public parent code/data repository was recovered through the currently available GitHub index. If the clean test requires rebuilding a large factual-learning data pipeline, workload may kill the route.
3. **Access A/B construct.** A/B cannot be mere prompt paraphrases. The design needs logically matched access structures with counterbalancing so that a crossover is not a trivial interface-matching effect.
4. **Resolution.** Before a full experiment, one must verify on a pre-specified manageable open checkpoint that document-only learning creates a sufficiently large new-knowledge signal to resolve the interaction. Do not model-shop.
5. **Artificial-fact risk.** A tiny synthetic key-value task may be excellent for identification but too weak for final significance. A clean natural or parent-aligned substrate is preferable if it can be obtained without data archaeology.

## Verdict

# **SERIOUS — SEND TO FULL SELECTION, BUT DO NOT PILOT YET**

The best-case scientific statement is large enough to justify further audit; the current evidence is not enough to authorize compute.

---

# 3. Contextual diversity — downgrade / likely kill

## Proposed pressure

TACL work on contextual diversity reports that, controlling frequency, words appearing across more diverse contexts can be learned later / less stably by LMs, while human learning work often separates early familiar-context performance from better novel-context generalization under diverse exposure.

A tempting reconciliation was:

> low diversity improves acquisition speed; high diversity slows acquisition but improves decontextualized/OOD generalization.

## Why downgraded

2025 controlled-pretraining work (*Facts in Stats*) already owns a very similar scientific structure for factual associations: contextual diversity can delay learning while being necessary for some OOD recall regimes, with representational/embedding bottlenecks analyzed.

Moving the same trade-off from factual associations to lexical semantics risks reviewer compression to a domain transfer unless a lexical-specific law changes the inference.

**Verdict:** `HOLD / LIKELY KILL — PARENT-COMPRESSION RISK`.

Do not promote by simply swapping facts for words.

---

# 4. Spacing mechanism — downgrade

## Pressure

The classic spacing effect suggests two broad mechanisms that are meaningful in SGD language learning:

- `deficient processing/update`: immediate repetition produces little additional effective update once the example is already predicted well;
- `state-dependent re-encoding / variability`: intervening experience changes the parameter/representation state so that a repeated example produces a complementary update.

A possible SGD discriminator is to separate repeat-update **magnitude** from **direction novelty** (e.g. norm-matched massed repeats versus direction-constrained spaced repeats).

## Why not serious now

Even the strongest successful result currently reviewer-compresses too naturally to ordinary SGD intuition:

> consecutive repeats have highly correlated gradients; intervening optimization changes the state and hence later gradient direction.

Data-ordering / replay / spaced-training methods are already active, and the intervention risks becoming optimization engineering rather than a new language-model learning law.

**Verdict:** `HOLD / SIGNIFICANCE BLOCKER — NO COMPUTE`.

Reopen only if a stronger representational or generalization consequence makes the best-case answer non-obvious.

---

# 5. Scalar implicature / neg-raising / VP ellipsis — anti-resurrection reconciliation

During this batch these semantic pressures were independently rediscovered, but the latest repository history already contains them:

- scalar implicature = P39 in `PRESSURE_FIRST_SEARCH_IX.md`, current route closed/deprioritized because ACL-2026 steering owners exist and no selective alternative-construction operation is available;
- neg-raising = P36 in `PRESSURE_FIRST_SEARCH_IX.md`, `PRESSURE ONLY / NO COMPUTE`, blocked by mother + selective-operation requirements;
- VP ellipsis = P32 in `PRESSURE_FIRST_SEARCH_VII.md`, dropped because the mother is uneven and reconstruction-vs-pointer mechanisms are not selectively separable by simple masking/patching.

These are **not new leads** from this round. Do not count them again.

---

# 6. Final-layer angular jump — already killed

The round independently rediscovered the EACL-2026 final-layer angular-jump anomaly, but the repository already contains a full assassination:

`search_rounds/2026-09-13_FINAL_LAYER_JUMP_ASSASSINATION.md`

Status: **K192 — KILL / PARENT-MECHANISM COMPRESSION**.

The upstream deep-layer redundancy/normalization program, LayerSkip/deep supervision, prediction-centric late geometry, and the mother paper together make the strongest successful explanation too naturally entailed.

Do not reopen.

---

# 7. Other quick kills from the batch

## Morphological analogy as online exemplar causality — DROP

A PNAS-2025 behavioral claim that derivational morphology resembles exemplar analogy plus modern data-attribution/unlearning machinery does not create an independent parent. `behavioral analogy claim + causal training-example removal` is a prohibited bridge unless a new scientific quantity appears.

## Token entropy versus strategy diversity in RLVR — DROP

Direct 2026 work already separates local token entropy / surface diversity from global reasoning-mode or approach diversity. The estimand split itself is occupied.

## Garden-path prediction update versus structural repair — HOLD / LIKELY DROP

Human work motivates surprisal-vs-reanalysis distinctions, but COLING/ACL 2025–2026 work already studies structural signals, surprisal, recovery dynamics and hidden-state divergence in LMs. No unique causal operation was found that identifies repair beyond another internal diagnostic.

## Reasoning token budget changes strategy form — DROP

Token-budget-aware reasoning and structured compression under budget are already active ACL-2025/2026 method/science programs. The generic resource-constraint version is crowded.

---

# 8. Current batch checkpoint

**New fully authorized survivor:** 0.  
**New SERIOUS lead:** 1 — access-conditioned knowledge encoding.  
**New compute authorization:** 0.

The search is **not closed**. The next batch must continue across independent scientific objects rather than center exclusively on the new serious lead.
