# K194 — L36: Beam-Curse / Mode-Seeking Stability Transition

**Status:** `ARCHIVED / NO-GO — MOTHER-QUESTION FAILURE`  
**Date:** 2026-09-17  
**Primary failure:** `MOTHER_QUESTION_LOW_SCIENTIFIC_PRESSURE`  
**Secondary:** `OLD_PROBLEM_MODERN_SUCCESS_IS_NOT_ENOUGH`, `NARRATIVE_RESCUE_RISK`, `OWNERSHIP_CROWDING`

## 1. Final disposition

L36 is archived as a primary ACL / EMNLP / NAACL Main project.

This is **not** an experimental failure. Several experiments were clean, reproducible, and useful. The route is killed because the parent scientific question was not important enough to justify the programme:

> Classical NMT suffers from wide-beam / mode-seeking pathologies, whereas many modern post-trained LMs are substantially more stable. Why did the old pathology become less severe?

Even if answered perfectly, this question mostly explains why a historical failure is less problematic in modern systems. It does not by itself expose a current capability failure, unresolved contradiction, hidden cost, or decision-relevant bottleneck. The project repeatedly produced interesting sub-results, but the mother question did not create enough scientific pressure.

## 2. Why the mother question fails

The failure is upstream of experiment design.

A strong design cannot rescue a weak parent question. Here the project repeatedly improved its measurement and causal discipline while the central motivation remained:

> an old problem used to be bad; modern models are better; explain why.

That shape is weak by default. It becomes worthwhile only if the explanation reveals one of the following:

- the pathology actually persists in a consequential modern form;
- the apparent improvement hides a new trade-off or failure;
- a broadly useful training law is uncovered that matters beyond this historical problem;
- a load-bearing belief about modern model behavior is overturned;
- the answer changes an important contemporary modeling or deployment decision.

L36 did not establish such pressure before consuming substantial experimental effort.

## 3. What happened during the route

The project began from an uncertainty / beam-search story, then successively moved through:

1. sentence-level uncertainty as an explanation of wide-beam degradation;
2. termination / EOS geometry as a mechanism for the classic empty-output channel;
3. post-training-learned format-conditioned generation boundaries;
4. full-sequence mode-seeking stability and probability-landscape reorganization.

Each reconstruction was motivated by real evidence, and several corrections were scientifically responsible. However, the repeated need to deepen the object after each result is itself evidence that the parent question was not carrying enough intellectual weight.

The final sequence-level reframe was broader and technically sounder than the EOS account, but it still inherited the same weak mother pressure: explaining why modern systems avoid or reduce an old decoding pathology.

## 4. Results that remain valid and reusable

Archive the question, not the evidence.

Reusable findings/assets include:

- matched raw-scoring classic-vs-modern decoding comparisons;
- separation of termination collapse from non-empty mode inadequacy;
- Olmo / Tülu Base→SFT→DPO/RLVR checkpoint infrastructure;
- multi-width beam evaluation harness;
- stop-event instrumentation and the algorithmic exposure check;
- controlled A/B/MIXED boundary-token SFT experiment;
- cross-implementation HF/vLLM validation;
- candidate rescoring / sequence-landscape analysis plans from E05;
- the observation that similar aggregate BLEU loss can arise from qualitatively different failure basins.

These may be reused **only if a new project begins from an independently important scientific question**. They do not confer priority on another beam-search or probability-landscape paper.

## 5. Explicit anti-resurrection rule

Do **not** reopen L36 by renaming it as:

- "Where did the beam-search curse go?";
- mode-seeking stability;
- probability–utility alignment across post-training;
- mode–mass gap across checkpoints;
- generation-boundary learning;
- EOS / stopping geometry in modern LMs;
- pathology migration from empty to generic/copy modes;
- Base→SFT→DPO/RLVR search robustness.

A future project may reuse one of these measurements only if it starts from a **new mother question that is independently worth knowing even if beam search, NMT history, and L36 are never mentioned**.

## 6. Durable selection lesson

Add a mandatory pre-novelty gate:

> **Mother-Question Value Gate:** Before mechanism design, novelty search, pilot planning, or compute, write the strongest successful answer in one sentence and ask: *Why would a strong Main-paper reader care about knowing this answer today?*

Reject by default when the answer is only:

- it explains why modern models fixed an old problem;
- it characterizes a historical pathology more precisely;
- it shows a modern model is more robust than an old model;
- it identifies which training stage removed a problem that no longer materially limits current systems.

To survive, the question must expose a current unresolved failure/tension, revise a load-bearing scientific belief, reveal a consequential hidden trade-off, or produce a general law with significance independent of the historical benchmark/problem.

## 7. Final verdict

```yaml
kill_id: K194
candidate: L36
status: ARCHIVED_NO_GO
primary_reason: MOTHER_QUESTION_LOW_SCIENTIFIC_PRESSURE
experimental_quality: MANY_VALID_RESULTS
novelty_problem: SECONDARY_NOT_PRIMARY
main_problem: THE_QUESTION_WAS_NOT_IMPORTANT_ENOUGH
resurrect_same_parent: NO
reuse_assets_for_new_independent_question: YES
```

**Final disposition:** `K194 / ARCHIVED / DO NOT RESCUE BY ADDING A DEEPER MECHANISM TO THE SAME MOTHER QUESTION`.
