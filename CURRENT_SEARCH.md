# Current Research State — 2026-09-13

**Target:** ACL / EMNLP / NAACL Main  
**Approved paper mainline:** **NONE**  
**Open-ended search:** **ACTIVE**  
**Active bounded pilots:** **L33 — PILOT-AUTHORIZED — E01 ONLY**; **L32 — E01 COMPLETE, awaiting Selection on a Claim Novelty Delta**; **L17 — existing speech project, outside current new-search preference**.

> **Status note (2026-09-13):** `PILOT-AUTHORIZED` is not an approved paper mainline. L33 authorizes only one bounded E01. L32's E01 is complete: it passed its gate and answered its question, but the answer mutated the claim, so its authorization has expired and it is back at Selection. There is still **no approved paper mainline**.

---

# 1. Current portfolio

## L33 — Where Does Agreement Go Wrong?

**Status:** `PILOT-AUTHORIZED — E01 ONLY`  
**Role:** newly selected independent scientific object; not a continuation of L32/L30.

Package: `candidates/L33_AGREEMENT_ATTRACTION_MECHANISM/`  
Selection: `search_rounds/2026-09-13_AGREEMENT_ATTRACTION_SELECTION.md`

RQ:

> **When a distractor noun pulls a language model toward the wrong subject–verb agreement, is the controller-number state already corrupted before verb prediction, or does the correct controller information survive and lose only when the model reads it out?**

Mother: classic agreement attraction plus 2026 evidence that autoregressive Transformers, including the pre-specified Gemma-3 base family, robustly reproduce the relevant PP-attraction pattern.

Scientific accounts:

- **state distortion:** attractor number has already contaminated the derived pre-verb controller/context state;
- **access competition:** controller information survives sufficiently, but fresh late access to the distractor wins during agreement readout;
- **hybrid:** both channels contribute.

Authorized E01 uses published Wagers et al. (2009) buffered items with a neutral adverb between attractor and verb. On `google/gemma-3-4b-pt`, first validate clean SVA and a material attraction effect, then for every layer boundary compare:

`FULL / STATE-CLEAN / ACCESS-CLEAN / BOTH-CLEAN`

The causal mask plus the single neutral pre-verb position gives a particularly clean path decomposition: positions before the attractor are identical; distractor influence either has already entered the current pre-verb state or enters later through fresh causal access from the attractor.

Frozen mother gates:

- clean/matching SVA grammatical preference on **≥80%** of retained items;
- mean attraction shift **≥0.5 bits**;
- paired item-bootstrap 95% CI excludes 0 in the predicted direction.

Frozen completeness gate:

> `BOTH-CLEAN` must recover at least **70%** of the singular-vs-plural-attractor logit-margin difference in some contiguous layer region without materially destroying clean SVA.

If the mother or completeness/selectivity gates fail: **STOP / HOLD**. Do not model-shop, prompt-search, synthesize a new benchmark, or pivot to a generic syntax-unit atlas.

Do not yet authorize multilingual/model-zoo breadth, instruction-tuned comparisons, SAE/probe atlases, human experiments, new agreement methods, or training dynamics.

---

## L32 — Where Do 18 Embeddings Work?

**Status:** `E01 COMPLETE — awaiting Selection` (2026-09-13)
**Role:** existing project; **do not expand the current open-ended search around L32**.

Package: `candidates/L32_SPARSE_EMBEDDING_CHANNEL/`
Selection: `search_rounds/2026-09-13_SPARSE_EMBEDDING_CHANNEL_SELECTION.md`
Report: `notes/E01_REPORT.md` · Selection request: `notes/CLAIM_NOVELTY_DELTA.md`

**Gate passed.** `Delta_ALL = +29.50` [+28.59, +30.46] spBLEU (gate was `>= +15`),
3 seeds, LLaMA-7B + the 18 published en→ca rows, Flores-101 devtest. The parent's
en→ca phenomenon reproduces.

**The channel question is answered, and three of four accounts are rejected.**
Recovery of the gain: INSTRUCTION **1.00** [0.98, 1.02]; SOURCE **−0.00**
[−0.01, 0.01]; TARGET feedback 0.05 [−0.01, 0.09]. Source occurrences are *more*
frequent than instruction ones (7.73 vs 7.00 per sentence) and recover nothing,
so this is not an opportunity effect. A norm-matched random delta on the same
rows scores 0.05 spBLEU.

**Two findings mutated the claim:**

1. **94% of the reproduced effect is termination.** Scored on the first line of
   the continuation, the untuned model is at 33.99 and the tuned model at 35.71
   — `Delta_ALL` falls to **+1.72** [+1.03, +2.42]. The pre-registered audit
   found untuned base spBLEU spans **0.31–33.78** on this task as a function of
   prompt and post-processing alone; the parent's reported 5.7 is reproducible
   only under whole-continuation scoring.
2. **The ticket is keyed to its template.** Paraphrasing the same instruction
   drops the gain from +29.18 to +3.19 across 3 seeds.

**Durable lessons, independent of whether L32 proceeds:**

- A published baseline for a *base* LLM on a generation task is not usable
  without knowing the output post-processing. The same model, prompt and decode
  spans two orders of magnitude of spBLEU depending on truncation. This is the
  L30 termination-confound lesson arriving in a second, unrelated literature.
- **Gating an already-learned update by sequence segment at inference** is a
  cheap and sharp way to localize *where* a parameter update acts. It needs a
  support audit (does each segment have occurrences?) and a norm-matched random
  control to be interpretable. Reusable: `src/eval.py`, `src/common.py`.
- When comparing selected-parameter sets across conditions, a **same-condition
  seed replicate is mandatory** as a noise floor. Without it, an overlap number
  is uninterpretable — I wrote a pre-declared kill condition that lacked one and
  it came out ambiguous (`notes/TICKET_SELECTION_PROBE.md` §5).

**Open question, not yet proven:** whether the certified ticket is a function of
the prompt rather than the language. Exploratory probe: at the parent's k=18,
against a seed floor of 18/18, rewording the prompt leaves 10/18 and switching
language leaves 10/18; 13–15 of every top-18 are that condition's own template
tokens. A pre-registered version is specified in `TICKET_SELECTION_PROBE.md` §6
(~15 runs, under a GPU-day).

**Verdict pending at Selection.** E01 alone is a Findings-level correction, not
a Main paper. C2 remains unauthorised.

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

**L33 is the positive example of this lane:** it does not ask whether the model knows agreement. It starts from a stable attraction error plus a live theoretical distinction and uses the decoder causal graph to make the old `distorted state vs wrong access` question directly identifiable.

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
- generic CoT faithfulness, metacognition control, RLVR entropy/mode-collapse/capability-boundary, self-correction, reasoning-length/overthinking, generic post-training rerouting;
- boundary/pause-token persistence as a fresh mechanism parent after 2026 boundary-pause mechanism work;
- structural priming lexical-boost vs abstract-persistence as a fresh dual-mechanism parent;
- response-sampling normative bias as a base-vs-aligned origin question;
- self-consistency as an unconditional diversity/variance-reduction law.

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
