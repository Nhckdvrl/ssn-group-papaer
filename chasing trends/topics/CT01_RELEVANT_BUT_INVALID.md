# CT01 — Relevant but Invalid: When Should Reasoning Models Forget Their Own Thoughts?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-19  
**Search route:** chasing trends / genealogy-first formal search  
**Paper type at registration:** empirical-scientific question first; method optional and conditional on pilot

---

# 1. One-sentence mother question

> **When a later turn changes an upstream premise used by a model's own prior reasoning, does preserving that prior private reasoning causally impede belief revision—even when the old reasoning remains topically relevant and the visible conversation is held fixed?**

Short version:

> **Can a reasoning trace be relevant but no longer valid?**

The project is NOT:

- generic multi-turn context compression;
- generic "old CoT can hurt";
- another belief-revision benchmark;
- another context-pruning method;
- another CoT-faithfulness metric;
- an agent-memory/RAG project.

The scientific object is:

> **validity of reused computation under changing premises.**

---

# 2. Why this question exists now

Modern reasoning systems increasingly expose a literal systems decision:

> Should historical private reasoning be fed back into later turns?

This is no longer hypothetical.

Current interfaces include:

- QwenCloud `preserve_thinking`: historical `reasoning_content` can be appended to later inputs; some current Qwen models enable this by default.
- GLM `clear_thinking`: explicitly toggles whether historical `reasoning_content` is retained across turns.
- Claude preserved-thinking: earlier thinking blocks can be reused across later turns subject to model/signature/prefix-integrity constraints.
- GuideLLM exposes `multiturn_reasoning` to include or discard reasoning in conversation history.

So "thinking history" has become an explicit deployment state.

At the same time, nearby literature establishes two facts that point in opposite directions:

1. **Keeping reasoning history can help continuation.**  
   Liu et al., ICML 2026, report roughly 2–5% gains on BFCL multi-turn for reasoning Qwen models when thinking history is retained.

2. **Models can become stuck on their own earlier commitments.**  
   Laban et al., ICLR 2026 Best Paper, find large multi-turn degradation driven mainly by unreliability: models make early assumptions/solutions and over-rely on them instead of recovering.

The missing distinction is:

> **continuing a still-valid computation vs. replaying a computation whose dependency has been invalidated by new evidence.**

Existing context-management work largely asks which old content is relevant/useful.

For reasoning traces, relevance may be insufficient.

---

# 3. Genealogy

Relation labels follow `PAPER_GENEALOGY_GUIDE.md`.

## [FIELD] A. Multi-turn models retain their own outputs by default

Standard chat history feeds past assistant outputs back to the model.

2026 systems increasingly treat private reasoning as a separate history channel rather than ordinary visible text.

This creates a new object:

> **reasoning history carryover.**

---

## [DIRECT] B. Retaining thinking history can improve multi-turn tool continuation

**Liu et al. (ICML 2026), _On Effectiveness and Efficiency of Agentic Tool-calling and RL Training_.**

They explicitly study "Thinking History Variance" and report:

> retaining thinking history improves BFCL multi-turn by roughly 2–5% for Qwen3 reasoning models.

Their result makes "always drop old thinking" untenable as a default scientific conclusion.

But BFCL is primarily a continuation/tool-use regime:

> earlier reasoning usually remains part of the same still-valid task trajectory.

They do not manipulate whether a new turn invalidates a premise used in the old reasoning.

---

## [DIRECT/FIELD] C. Full assistant history is often unnecessary and can cause context pollution

**Huang et al. (2026), _Do LLMs Benefit From Their Own Words?_**

They compare full conversation history against aggressively reduced history on real multi-turn conversations.

Key findings include:

- many turns can be solved with much less context;
- past assistant responses can propagate errors/hallucinations/style artifacts;
- they propose selectively omitting assistant-side history;
- their current framing is to retain only what is relevant.

This is the nearest reviewer-compression threat.

However, their intervention unit is:

> **assistant-side response/history.**

CT01 holds the visible assistant conversation fixed and manipulates only:

> **the private reasoning trace.**

More importantly, CT01's independent variable is not:

> whether old content is relevant.

It is:

> **whether an old computation remains logically valid after a changed upstream premise.**

A reasoning trace can be maximally relevant to the same task and still be invalid.

That is the central distinction that must survive pilot.

---

## [DIRECT/FIELD] D. Belief revision is already a known capability problem

**Wilie et al. (EMNLP 2024 Main), _Belief Revision: The Adaptability of Large Language Models Reasoning_.**

Belief-R gives sequences of premises where later evidence may require revising an earlier inference.

They find models struggle with the update/retain tradeoff.

This owns:

> belief revision as a behavioral capability.

It does NOT isolate:

> historical private reasoning carryover as a causal variable.

CT01 can therefore reuse Belief-R as an identification instrument rather than build a new benchmark.

---

## [FIELD] E. Reasoning traces themselves causally influence later answers

**von Recum et al. (ICLR 2026), _Are Reasoning LLMs Robust to Interventions on their Chain-of-Thought?_**

They perturb a model's own CoT at controlled positions and study recovery.

Important result:

> models often recover, but early interventions are more damaging.

This owns:

> within-episode perturbation/recovery.

It does not study:

> reuse of a completed old reasoning trace after the external premise/state has changed.

**Ballon et al. (2026), _Probing the Trajectories of Reasoning Traces in Large Language Models_.**

They feed partial reasoning traces back into models and find:

- answer commitment increases with more reasoning;
- relevant reasoning content matters beyond length/style;
- immediate answers can remain anchored to incorrect traces.

This makes a carryover/commitment effect plausible, but again within a single problem trajectory rather than cross-turn premise revision.

**Chen et al. (ACL 2026 Findings), _How Do Answer Tokens Read Reasoning Traces?_**

They show answer tokens systematically read and integrate earlier reasoning content.

This supports treating reasoning history as active computation, not decorative text.

---

## [RECONSTRUCTED] F. Classical truth maintenance gives a deeper conceptual contrast

**Doyle (Artificial Intelligence, 1979), _A Truth Maintenance System_.**

Truth-maintenance systems record the reasons/dependencies supporting beliefs so that beliefs can be revised when assumptions are contradicted.

The conceptual contrast is useful:

> classical reasoning systems treated derived state as computation with dependencies;
> current reasoning-history APIs largely serialize/replay the trace as a blob.

CT01 is NOT a symbolic-TMS revival.

The old literature only sharpens the question:

> If an upstream assumption changes, should downstream reasoning be treated as reusable context or invalidated computation?

---

# 4. Changed premise

This is not "belief revision on a newer model."

The changed premise is:

> **reasoning models now expose completed private reasoning as persistent, reusable state across user turns.**

Historically, a model completed a response and the hidden computation disappeared.

Now APIs explicitly allow that computation to be serialized and replayed.

This creates a distinction that ordinary dialogue history did not have:

> visible conversational record vs. private executed computation.

That distinction is the reason CT01 exists now.

---

# 5. Exact novelty boundary

CT01 only survives if the following statement is supported:

> **Holding the visible dialogue fixed, carrying over a model's own private reasoning has a condition-dependent causal effect: it helps when the prior derivation remains valid, but hurts when a newly introduced premise invalidates that derivation.**

The headline is NOT:

> old context can hurt.

The headline is NOT:

> old reasoning can be stale.

The headline is NOT:

> models struggle with belief revision.

The headline is:

> **reuse of reasoning computation should depend on validity, not merely relevance or turn recency.**

---

# 6. Decisive pilot

## 6.1 Basic paired setup

For each item:

### Turn 1
Give premises/problem state (P_1).

Let the reasoning model naturally produce:

- private reasoning trace (R_1);
- visible answer (A_1).

Only keep items where Turn-1 reasoning/answer is correct enough to establish a legitimate prior computation.

### Turn 2
Construct paired follow-ups.

#### CONTINUE
New information/query depends on the same task and old derivation remains valid.

The prior reasoning is:
- relevant;
- valid.

#### REVISE
Make a minimal, controlled change/addition to an upstream premise so that a conclusion used in (R_1) is no longer valid and the correct answer changes.

The prior reasoning is:
- relevant;
- invalid.

Optional third control:

#### RESET / IRRELEVANT
New turn is unrelated.

The prior reasoning is:
- irrelevant.

---

## 6.2 Causal fork

For the exact same visible conversation history, run:

### DROP
Do not feed (R_1) back.

Visible user/assistant content remains unchanged.

### PRESERVE
Feed exact native (R_1) back in the historical reasoning channel / native serialization.

### LENGTH CONTROL
Feed an unrelated reasoning trace matched approximately in token length / style.

Purpose:

> distinguish logical carryover from generic extra-context distraction.

Potential later control:

### SUMMARY / FINAL-STATE CONTROL
Provide a compact visible summary/answer but not the full old computation.

Not needed for first pilot unless DROP/PRESERVE effect is large.

---

# 7. Mother statistic

The key effect is NOT a main effect of PRESERVE.

It is the interaction:

> **history carryover × computation validity.**

Desired qualitative pattern:

| Condition | PRESERVE vs DROP |
|---|---|
| CONTINUE: old reasoning valid | PRESERVE helps or is neutral-positive |
| REVISE: old reasoning invalid | PRESERVE hurts |
| IRRELEVANT / length control | smaller/different effect |

The strongest result would be a sign reversal:

> **useful cache when valid, harmful commitment when invalid.**

This distinguishes CT01 from generic context pollution.

---

# 8. Primary outcomes

No LLM judge is required for the core experiment.

Use tasks with automatically checkable answers.

Primary:

- Turn-2 accuracy;
- stale-answer persistence rate;
- revision success rate;
- response/reasoning token cost;
- PRESERVE × VALIDITY interaction.

Secondary only after effect exists:

- recovery length;
- degree of old-answer copying;
- position/depth of invalidated dependency.

---

# 9. Data path

## First choice: reuse Belief-R

Belief-R already gives:

- initial premises;
- later evidence;
- update-required vs retain-required conditions;
- ground-truth reasoning outcomes.

Advantages:

- no benchmark construction;
- direct connection to an established Main paper;
- update vs retain contrast already motivated independently of CT01.

We may need to minimally adapt serialization to make Turn 1 / Turn 2 natural for reasoning-history carryover.

## Second small instrument: programmatic logic/math revision pairs

Only if Belief-R is too linguistically noisy.

Generate small automatically verifiable tasks where:

- an early premise determines a derived quantity;
- Turn 2 either preserves or minimally changes that premise;
- correct answer is exact.

This is an identification instrument, NOT a dataset contribution.

No manual annotation campaign.

---

# 10. Model path

Pilot requires at least **two model families** with accessible reasoning traces/history serialization.

Candidate path:

- Qwen reasoning family with native thinking output/history handling;
- DeepSeek-R1-Distill / another open reasoning family using explicit `<think>` serialization.

If current open GLM/Qwen native interfaces make it easy, use them.

Do NOT require a commercial API for the mother effect.

Commercial preserved-thinking APIs can be an external validation later, not the pilot dependency.

---

# 11. Compute path

Pilot is inference-only.

No:

- pretraining;
- SFT;
- RL;
- model zoo;
- agent environment;
- API-heavy judge;
- human labeling.

A few hundred paired items × 3 history conditions × 2 model families is sufficient for a first decisive test.

This fits current local inference resources easily.

---

# 12. Hard KILL criteria

CT01 is authorized only because the pilot can kill it cheaply.

KILL if ANY of the following holds:

1. **No validity interaction.**  
   PRESERVE has similar effect in CONTINUE and REVISE.

2. **Tiny/inconsistent revision effect.**  
   PRESERVE-vs-DROP harm on REVISE is < roughly 2–3 percentage points or flips across two reasonable model families.

3. **Length/context pollution explains it.**  
   A matched unrelated reasoning trace causes comparable harm.

4. **Visible answer/history explains everything.**  
   Once visible assistant output is held fixed, private reasoning adds no independent effect.

5. **Only injected-wrong reasoning works.**  
   Harm appears only when we deliberately insert an erroneous trace, but not when Turn 1 reasoning was correct and a legitimate new premise later invalidates it.

6. **No benefit/continuity side.**  
   PRESERVE never helps valid continuation and only behaves as generic noise. Then the scientific "valid cache" interpretation weakens sharply.

7. **Template biography.**  
   Effect only exists under one serialization/chat template or one model family.

8. **Nearest-prior collapse.**  
   During implementation, a 2026 paper is found that already holds visible history fixed and tests private reasoning retention specifically under premise-preserving vs premise-invalidating turns.

If killed, do NOT rescue by:
- more model families;
- a bigger benchmark;
- a learned context router;
- an LLM judge;
- agent tasks;
- arbitrary trace editing.

---

# 13. If the pilot is positive: method path is conditional, not precommitted

Do not build a method before the mother effect exists.

The first algorithmic question after a positive result would be:

> Can we preserve the gain of valid reasoning carryover while invalidating only reasoning that depends on changed premises?

First establish an **oracle conditional policy**:

- valid continuation → retain;
- invalidated premise → clear.

This proves whether conditional reuse has meaningful attainable value.

Only then consider a small method, e.g. a validity-aware retain/clear policy.

Avoid turning the project into:
- dependency-graph infrastructure;
- generic summarization;
- memory/RAG;
- learned context-filtering benchmark.

---

# 14. Reviewer compression audit

## Compression 1
> "This is just _Do LLMs Benefit From Their Own Words?_ at reasoning-trace granularity."

Response boundary:

Huang et al. manipulate assistant-side history and conclude that only relevant history should be retained.

CT01:
- holds visible assistant history fixed;
- manipulates only private reasoning history;
- compares equally relevant old computation whose **logical validity** differs after a premise update.

If the experiment does not demonstrate this distinction cleanly, KILL.

---

## Compression 2
> "Belief-R already studies belief revision."

Belief-R owns the behavioral task.

CT01 uses belief revision to identify a different causal object:

> whether replaying prior hidden computation changes revision.

Reusing Belief-R is a strength, not the contribution.

---

## Compression 3
> "ICLR 2026 already perturbs CoT."

That paper perturbs the ongoing CoT within one reasoning episode.

CT01 studies:

> completed prior reasoning replayed after the external problem state changes across turns.

---

## Compression 4
> "Of course stale thoughts hurt."

Not sufficient.

The experiment must show:

- Turn-1 reasoning was correct when produced;
- new evidence later makes it invalid;
- visible conversation is identical;
- generic length/style control does not reproduce the effect;
- the same preservation operation has a different/opposite effect when the derivation remains valid.

Without all of these, the result is trivial and the topic dies.

---

## Compression 5
> "Just clear thinking at user-turn boundaries."

No.

ICML 2026 evidence says retaining thinking history improves multi-turn tool use; current production APIs expose cross-turn preservation.

The question is specifically:

> **which completed computations remain valid after state changes?**

A user-turn boundary is not a scientific answer.

---

# 15. Sasano-style story compression

An average reviewer should be able to understand the paper from five sentences:

1. Reasoning models increasingly preserve private thinking across turns.
2. Keeping it can improve multi-turn continuation, so simply discarding thinking is not obviously correct.
3. But later user/tool information can invalidate premises used by an earlier derivation.
4. We ask whether old reasoning is best treated as ordinary relevant context or as cached computation whose reuse depends on validity.
5. Holding visible dialogue fixed, we test whether preserving the same model-generated reasoning helps when its dependencies remain valid but impedes revision when they do not.

If the final paper cannot stay this simple, do not broaden it.

---

# 16. Why this is not S03/S09 again

CT01 does NOT study:

- when a capability emerges during training;
- optimizer history;
- checkpoint trajectories;
- model developmental biography.

The causal variable is inference-time and directly controlled:

> preserve vs drop an already generated reasoning trace under matched visible context.

No recipe matrix is needed to interpret the first experiment.

This is exactly the kind of distinction the S03/S09 postmortem asks us to prefer.

---

# 17. Why this topic came from literature rather than a template

It emerged from a real 2026 tension:

- multi-turn tool-calling work finds retaining reasoning history beneficial;
- multi-turn conversation work finds models over-commit to earlier attempts;
- context-filtering work says old assistant content should be retained selectively based on usefulness/relevance;
- belief-revision work shows later evidence requires retracting earlier conclusions;
- current reasoning APIs have now made historical private reasoning an explicit persistent state.

The question formed by noticing that these literatures use different abstractions for the same new systems object:

> **history as context** vs. **history as executed computation**.

The candidate was not generated by asking for a generic "mismatch", "adaptive", "cache", or "hidden assumption" topic.

---

# 18. Nearest-prior list to keep open during the pilot

1. Liu et al. (ICML 2026), **On Effectiveness and Efficiency of Agentic Tool-calling and RL Training**  
   https://arxiv.org/abs/2606.00135

2. Huang et al. (2026), **Do LLMs Benefit From Their Own Words?**  
   https://arxiv.org/abs/2602.24287

3. Laban et al. (ICLR 2026 Best Paper), **LLMs Get Lost In Multi-Turn Conversation**  
   https://proceedings.iclr.cc/paper_files/paper/2026/hash/59f6421e64707225fdf5b28840679a07-Abstract-Conference.html

4. Wilie et al. (EMNLP 2024 Main), **Belief Revision: The Adaptability of Large Language Models Reasoning**  
   https://aclanthology.org/2024.emnlp-main.586/

5. von Recum et al. (ICLR 2026), **Are Reasoning LLMs Robust to Interventions on their Chain-of-Thought?**

6. Ballon et al. (2026), **Probing the Trajectories of Reasoning Traces in Large Language Models**  
   https://arxiv.org/abs/2601.23163

7. Chen et al. (ACL 2026 Findings), **How Do Answer Tokens Read Reasoning Traces?**  
   https://aclanthology.org/2026.findings-acl.1507/

8. Doyle (1979), **A Truth Maintenance System**  
   https://doi.org/10.1016/0004-3702(79)90008-0

System reality / interface evidence:
- QwenCloud thinking / preserve_thinking docs
- GLM clear_thinking docs
- Claude preserved-thinking docs

---

# 19. Registration verdict

> **PILOT-AUTHORIZED — CT01**

Reason:

- real newly important systems object;
- clear tension between strong neighboring literatures;
- nearest-prior distinction survives a first deep audit;
- one simple causal experiment can falsify it;
- existing Belief-R removes data-construction burden;
- inference-only pilot;
- no training-recipe biography;
- no evaluator/benchmark dependency;
- no agent environment;
- reviewer story can stay simple.

Confidence is **not** "the full paper is already safe."

The largest novelty threat is Huang et al. 2026.

Therefore the pilot must preserve the exact novelty boundary:

> **private reasoning history + visible context fixed + valid-vs-invalid prior computation.**

If that distinction weakens in execution, kill immediately.
