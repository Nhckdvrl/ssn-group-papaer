# Current Research State — 2026-09-13

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Open-ended search:** **ACTIVE**  
**Active bounded pilots:** **L32 — PILOT-AUTHORIZED — E01 ONLY**; **L17 — existing speech project, outside current new-search preference**.

> **Status reconciliation (2026-09-13):** an earlier version of this file incorrectly said “no active pilot.” `candidates/L32_SPARSE_EMBEDDING_CHANNEL/README.md` and `search_rounds/2026-09-13_SPARSE_EMBEDDING_CHANNEL_SELECTION.md` are authoritative: **L32 is PILOT-AUTHORIZED — E01 ONLY**. There is still **no approved paper mainline**. Do not re-review or downgrade L32 because of the stale sentence that used to appear here.

---

# 1. Current portfolio

## L32 — Where Do 18 Embeddings Work?

**Status:** `PILOT-AUTHORIZED — E01 ONLY`  
**Role:** existing project; **do not expand the current open-ended search around L32**.

Package: `candidates/L32_SPARSE_EMBEDDING_CHANNEL/`  
Selection: `search_rounds/2026-09-13_SPARSE_EMBEDDING_CHANNEL_SELECTION.md`

RQ:

> **When only a handful of frequent token embeddings learn a translation task, where does their causal effect actually enter a decoder-only LM: through instruction/source prefill, generated-target feedback, or both?**

Mother: NAACL 2025 KS-Lottery reports that only 18 selected input-token embeddings can move LLaMA-7B en→ca translation from very poor to strong performance.

Authorized E01 uses the **same trained sparse-embedding checkpoint** and gates the learned embedding delta by sequence segment at inference:

`BASE / ALL / INSTRUCTION / SOURCE / PREFILL / TARGET`

Evaluate teacher-forced next-token behavior and free-running Flores spBLEU.

Frozen first-stage gate:

> `spBLEU(ALL) - spBLEU(BASE) >= +15`, with all 3 training seeds in the same direction.

Do not authorize model-zoo expansion, multilingual sweep, new PEFT method, generic probing atlas, or C2/C3 before E01 is read.

---

## L17 — What Does a Speech LLM Learn About a Speaker?

**Status:** `PILOT-AUTHORIZED — E01 ONLY; EXISTING PROJECT`  
**Search policy:** do not create new speech/audio topics from this authorization.

Package: `candidates/L17_SPEAKER_ADAPTATION_UNIT/`

---

## L30 — What Does Pairing Teach?

**Status:** `NO-GO / ARCHIVED — 2026-09-13`

Package: `candidates/L30_PAIRING_SURPLUS/`  
Do not reopen shuffled-pair / response-only / wrong-vs-absent correspondence variants.

E01: 4 arms × 3 seeds, Gemma-2-2B, Alpaca-Cleaned, 541 IFEval prompts.

Primary estimand:

> `Delta_pair = P - D_mask = +1.85 pp`, 95% CI `[-1.79, +5.42]`.

Three independent NO-GO reasons:

1. **Resolution:** 52k Alpaca pairs buy only about +1.1 pp instruction-level over the untuned base, so the pairing surplus is below available evaluator resolution.
2. **Instrument / construct:** at 2B, aggregate IFEval mixes instruction following with termination policy; the base model often never stops.
3. **Novelty:** wrong correspondence collapsing the policy while absent correspondence does not is clean but substantially predictable from the objective and crowded by nearby supervision-corruption/data-poisoning work.

Durable lesson: validate the evaluator’s construct and resolution before interpreting a small sub-effect of post-training.

---

## L29 — Losing the Steering Gain

**Status:** `KILL — K190 — FINAL E01R INSTRUMENT GATE FAILED`

The reconstruction removed the original wording/constraint confounds, but the fresh balanced-binary instrument still had essentially no useful early causal leverage (case 0.00 pp; tag +1.30 pp, far below the frozen +15 pp gate). This is an **identification failure**, not a meaningful null about training dynamics.

Do not reopen via prompt search, hidden-state steering, commitment variants, checkpoint sweeps, or renamed `initialization vs online control` stories.

---

## L19 — Causal Ingredients of Long→Short SFT Transfer

**Status:** `ARCHIVED / NO-GO (K184) — COST/RESOLUTION`, not novelty.

Do not shrink the claim to fit the hardware.

---

## Temporal Forgetting

# **DO NOT RESURRECT**

Forgotten≠erased, old-prefix rescue, checkpoint rescue, suppression/readout, temporal sampling and renamed variants remain hard-banned.

---

# 2. Current search doctrine — pressure first, phenomenon second

The search generator is **not** restricted to published anomalies.

Use several provenance classes in parallel:

1. **Old empirical law → changed modern regime.** A load-bearing 2018–2023 premise may no longer survive pretraining scale, SFT/RL, reasoning, MoE, long context, or decoder-only deployment.
2. **Widely believed explanation → weak identification.** The field repeatedly says `X happens because Y`, but evidence is correlation/probing/model-family comparison and a same-checkpoint selective operation could actually distinguish accounts.
3. **Evaluation/deployment or training/inference mismatch.** Hold the underlying task/information fixed and change one real condition that standard evaluation/training omits.
4. **Default structural choice → scientific variable.** Test a ubiquitous design assumption only when the result can become a general model-science law rather than a leaderboard method.
5. **Mature important question → new identifying instrument.** Previous evidence cannot answer the question, and a new operation changes what can be inferred.
6. **Known stable anomaly → mechanism.** Keep this route, but use it selectively because successor pressure is usually high.

Core slogan:

> **scientific pressure first → decisive matched/stress test → phenomenon second**

A focal paper may discover its own central phenomenon. That is allowed when the test is motivated by a real prior law, belief, mismatch, or theory and **both plausible outcomes answer the pre-existing scientific question**.

Bad search remains banned:

> invent intervention → hope for quirky effect → narrate afterward.

Also keep the anti-bridge rule:

> `Prior A + Prior B = our paper` is not contribution by itself.

For provenance examples and rationale, read:

- `search_rounds/2026-09-13_RESEARCH_IDEA_PROVENANCE_AUDIT.md`
- `search_rounds/2026-09-13_PRESSURE_FIRST_SEARCH.md`
- `search_rounds/2026-09-13_PRESSURE_FIRST_SEARCH_II.md`
- `search_rounds/2026-09-13_PRESSURE_FIRST_SEARCH_III.md`

---

# 3. Semantic / linguistic / interpretability lane

This lane is explicitly active. Do **not** let the search collapse into only training, architecture and optimization.

Good shapes:

- classic semantic/linguistic law whose computational premise changes under modern generative/reasoning models;
- stable semantic behavior → **causal representation/use**, not probe-only;
- influential explanation A/B → a selective operation that actually distinguishes them;
- formal/semantic distinction that yields two intuitive but genuinely different computational predictions;
- interpretability claim whose identifying assumption is load-bearing and unverified.

Bad shapes:

- `does the LLM know phenomenon X?`;
- minimal-pair benchmark as the paper;
- dataset-first work;
- `new linguistic property + old probe/steering/patching instrument`;
- large bespoke stimulus construction before the RQ has leverage.

Recent anti-resurrection examples are persisted in `2026-09-13_PRESSURE_FIRST_SEARCH_III.md`: grammaticality causal-use, rules-vs-examples task representations, decoded planning causal-use, reasoning rescue of syntactic complexity, and scope ambiguity.

---

# 4. Search preference / exclusions

Strongly deprioritize RAG/retrieval/search, benchmark/evaluator/metric papers, annotation/data-first topics, scientific-evidence infrastructure, generic Agent/memory/RL/judge/harness questions, new speech/audio topics, pure competence tests, and generic calibration/hallucination/safety surveys unless an exceptional model-science question clearly transcends the framing.

Before deep search ask:

> **If the dataset, benchmark, metric, system label, or method name disappeared, would we still urgently want to know the answer?**

and:

> **Is the paper interesting because it changes our understanding of how the model computes, or because an evaluation/data pipeline is imperfect?**

No survivor quota. **Zero survivors is valid.**

---

# 5. Anti-duplication frontier

Always inspect `failed/KILLED_LEDGER.md`, archived candidates, and recent search rounds before promotion. The cumulative ledger text lags some newest compact kills, so recent rolling logs are also authoritative.

Hard / recent bans include at least:

- K190 = L29;
- K191 = L31;
- K192 = final-layer angular jump;
- Temporal Forgetting;
- curriculum easy→hard vs LR timing;
- LLM hivemind from pretraining vs post-training/chat format;
- MoE router weights vs upstream hidden-state routing changes;
- RL sparse updates: objective vs on-policy support;
- post-training architecture-invariance from matched pretraining loss;
- instruction tuning creates vs reuses task circuitry;
- attention score as KV causal value;
- random one-token reasoning supervision;
- mid-training KD reasoning↑ / factual recall↓;
- task-specific layer deletion;
- Lost-in-Conversation assistant-history contamination;
- proto-token / one-step reconstruction;
- less-data-memorizes-more;
- FP32 vs BF16 knowledge capacity;
- modern MT robustness;
- diffusion Flexibility Trap;
- generic CoT faithfulness, metacognition control, RLVR entropy/mode-collapse/capability-boundary, self-correction, reasoning-length/overthinking, generic post-training rerouting.

A new model, prompt, dataset, language, intervention, or mechanism label does not reopen a killed parent.

---

# 6. Promotion / compute discipline

Search broadly and lightly. Selection remains strict.

Before any GPU pilot, apply `RESEARCH_TOPIC_SELECTION.md`:

> **scientific object + estimand + decisive operation + synonyms → anti-resurrection → strongest owners and 2024–2026 successors → reviewer compression → identification → first-stage leverage → evaluation resolution → compute → Main-level growth path**

For any cross-training-stage causal claim, L29 adds a mandatory gate:

> **first prove on a disjoint development split that the intervention has a substantial and interpretable causal effect at the reference checkpoint.**

A difference between two near-zero first stages is not a training-mechanism result.

Promotion states:

- `ROUGH LEAD` — search only;
- `SERIOUS CANDIDATE` — full selection audit, no substantial compute;
- `PILOT-AUTHORIZED — E01 ONLY` — one bounded experiment;
- `GO-TO-FULL-STUDY` — full program justified;
- `HOLD` — one explicit blocker;
- `RECONSTRUCT` — new paper identity, restart selection;
- `ARCHIVED / NO-GO` — stop.

# **Only `PILOT-AUTHORIZED — E01 ONLY` counts as a newly found topic.**

> **The goal is not to keep a portfolio full. The goal is to find one scientific object worth months of mechanism, boundary, intervention and theory work. Easy to understand, hard to answer.**
