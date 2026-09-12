# 2026-09-12 — Continued Topic Search V

**Target:** ACL / EMNLP / NAACL Main  
**Mode:** mechanism-first; cross-paper anomaly search; no survivor quota.  
**Round start:** `main = 601672b59c9f63be53f4fbc145502157bd58c9dc`.

This round deliberately changed search strategy after repeated near-misses: do **not** mine one paper's unfinished mechanism as the default source of novelty. Prefer (i) a repeated side anomaly appearing independently across strong papers but not yet centralized, or (ii) an older empirical law whose load-bearing assumption is genuinely altered in the modern reasoning/post-training regime. Temporal Forgetting remains a hard anti-resurrection parent.

## Investigated hooks and decisions

### 1. Instruct↔Thinking weight interpolation as a continuous reasoning mode
ACL-2026 interpolation work reports smooth verbosity changes and some intermediate models that improve the accuracy/length tradeoff. However the mother paper already performs module/layer analyses and attributes thinking-pattern changes largely to FFNs. The obvious continuation collapses into a transition-marker/circuit cell rather than a new parent.

**Verdict:** DROP.

### 2. Frozen LLMs learning from trial→scalar-reward history (ICRL / test-time learning)
ICLR-2026 *Reward Is Enough* shows improvement from response+scalar-reward histories without parameter updates. EMNLP-2025 *How Far Can LLMs Improve from Experience?* independently shows measurable but unstable test-time learning. A tempting scientific object is whether reward history supplies genuine credit-assignment information or merely selects/replays successful trajectories.

Deeper owner search substantially weakens novelty. A separate 2024/2025 ICRL line already shows naive full-history ICRL can degenerate, identifies exploration and negative-reward episodes as central failure sources, and proposes positive-only/stochastic context construction. By 2026 ICRL has theory, preference-feedback variants, safe ICRL and surveys. The possible hidden-condition question — when history acts as an update signal vs a behavioral attractor — now sits inside a mature parent rather than defining a new one.

**Verdict:** DOWNRANK / DROP as new parent.

### 3. Parallel vs serial test-time compute
Repeated observation: parallel independent samples often help while extending one trajectory can hurt. Direct 2025 extended-vs-parallel-thinking work and ACL-2026 PaCoRe already centralize the contrast.

**Verdict:** DROP.

### 4. Capability–vulnerability tradeoff under stronger reasoning
Potential cross-paper pattern: stronger semantic/reasoning ability sometimes increases susceptibility to attacks that exploit structured reasoning. Too security-specific and already crowded with capability–vulnerability analyses.

**Verdict:** DROP.

### 5. Parameter scaling vs test-time deliberation scaling are not the same compute
Old inverse-scaling tasks often do not show the same failure under increased test-time reasoning; other distractor/spurious-feature tasks do. ACL-2026 scale work also shows larger models can improve semantic filtering while increasing some forms of mechanical copying.

The idea is intellectually attractive, but the direct test-time inverse-scaling mother already explicitly states that training-time and test-time scaling have different failure modes. Without a third law yielding a new common computational variable, asking why is still primarily the mother's unresolved explanation.

**Verdict:** DOWNRANK; not L30.

### 6. Reasoning hurts perception/readout
Text, vision and multimodal work report that extra reasoning can degrade simple perception/grounding/readout. However ACL/CVPR-2026 work already centralizes perception-access decay / deeper-thought-weaker-aim style phenomena.

**Verdict:** DROP.

### 7. Writing-RL transfers from long output to long-input ability
Interesting directional transfer, but currently too dependent on a single strong mother result. No sufficiently independent repeated anomaly found.

**Verdict:** DROP / single-paper future-work risk.

### 8. Easy→hard generalization in modern RLVR
Modern curriculum / weak-to-strong / difficulty-order work already directly reopens this law under reasoning training.

**Verdict:** DROP.

### 9. Self-generated extra context can hurt stronger models
Introspection/self-refinement/extended-thinking papers repeatedly report the effect, but the introspection-paradox / generated-knowledge-quality literature already centralizes the phenomenon.

**Verdict:** DROP.

### 10. Multi-turn presentation of the same information degrades reasoning
Strong repeated phenomenon, but *Lost in Conversation* and 2026 follow-ups (intent mismatch, distillation, memory/RL, curriculum) already form a mature topic.

**Verdict:** DROP.

### 11. RLVR suppresses representation of disagreement / plural solutions
Tempting `decision optimization → distributional blindness` story, but current mode-collapse / entropy / reverse-KL literature already owns the natural explanation.

**Verdict:** DROP.

### 12. Early reasoning trajectory is disproportionately load-bearing
Already explicitly centralized by *Lost at the Beginning of Reasoning* plus prefix-distillation work.

**Verdict:** DROP.

### 13. Reasoning/post-training shifts the commitment / abstention threshold
Reasoning models often answer rather than abstain. Direct 2026 work already separates detection from abstention and studies commitment calibration.

**Verdict:** DROP.

### 14. Compression preserves competence but destroys control margin
Quantization suggested this shape, but safety-pruning / sparse safety-subspace / LoRA safety work already establishes utility-preserving control collapse as a mature parent.

**Verdict:** DROP.

### 15. Correlated evidence is treated as independent evidence
Direct 2026 work on correlated evidence / epistemic-Sybil resistance already centralizes it; also drifts toward provenance/RAG.

**Verdict:** DROP.

### 16. Forward vs backward reasoning
NAACL-2025 / ACL-2026 work already treats backward reasoning and directional consistency directly.

**Verdict:** DROP.

### 17. Path dependence / hysteresis in belief updating
Potentially elegant (`same final evidence set, different order/history`). But sequential-belief-trajectory / BayesBench / repeated-revision dynamics work now directly studies this.

**Verdict:** DROP.

### 18. Diffusion LMs: static inference strong, interactive adaptation weak
ACL-2026 and concurrent work already decompose temporal-feedback branching, symbolic precision, feedback controllability and self-conditioning.

**Verdict:** DROP.

### 19. Implicit memory: preference learning ≫ inhibition learning
ACL-2026 ImplicitMemBench shows a very large preference-vs-inhibition gap; success-only experience can also outperform failure-only in other settings. A tempting hypothesis is that raw failure is poorly learnable until translated into an executable positive rule. LEAP / contrastive-ICL / failure-reflection work already makes that translation central.

**Verdict:** DOWNRANK / DROP.

### 20. Active information acquisition vs passive problem solving
Already a strong direct research line (AR-Bench, QuestBench, Reasoning While Asking, Value of Information, etc.).

**Verdict:** DROP.

### 21. Correct but redundant information can hurt
ACL-2026 METER shows distraction by causally irrelevant but factually correct information. ICLR-2026 spatial reasoning independently shows redundant 3D information can cause failures and motivates minimal sufficiency.

A stronger and potentially cleaner unresolved object is strict logical information monotonicity: if `C` already suffices and `r` is entailed by `C`, should behavior be invariant under `C` vs `C + r`? Current strong papers establish harmful *irrelevant/redundant* true information, not this exact entailed-information invariant.

**Blocker:** no strong mother effect yet for the exact `C ≡ C + entail(C)` intervention. Testing it now would gamble on the phenomenon.

**Verdict:** SEED ONLY — NOT SERIOUS / NO COMPUTE.

### 22. Declarative rule availability ≠ procedural control
Appears in explicit-rule arithmetic and related reasoning, but declarative-vs-procedural knowledge and knowledge–action-gap work already directly owns the abstraction.

**Verdict:** DROP.

### 23. Self-modeling: models cannot predict their own decision boundary
Two EMNLP-2025 papers independently showed self-prediction gaps, but EMNLP-2026 *Evaluating and Improving LLM Self-Modeling* directly centralizes the topic across tasks and adds RL.

**Verdict:** DROP.

### 24. More intermediate supervision can teach worse algorithms
ACL-2025 *When More Supervision is Less* finds dense teacher forcing can induce shortcuts in graph search. Independent 2026 depth-recurrent work reports intermediate losses can encourage shallow solutions while silent iterative computation generalizes OOD.

This is the best repeated non-mainstream pattern found in the round, but both strongest instances are controlled/synthetic algorithmic settings. Natural-language/process-supervision literature often reports positive effects, so we do not yet have a stable natural mother phenomenon.

**Verdict:** MAYBE-PATTERN ONLY; not candidate-worthy unless a natural reasoning analogue independently exists.

### 25. Reversible state update / explicit retraction
ICLR-2026 AGM-Bench directly tests retraction, preservation/minimal-change and iterated revision.

**Verdict:** DROP.

### 26. Multimodal language as a gate for visual capability
ACL-2026 MagicBench reports language anchors enabling access to visual ability and a semantic-vacuum visual-agency loss. Interesting but currently a single mother plus direct modality-dominance literature.

**Verdict:** DROP / single-paper risk.

### 27. Reasoning-completeness cliff
A completed erroneous rationale is much harder to escape than an unfinished one. Public 2026 work already directly names and sweeps this effect and interprets completed rationale as report-ready rather than solve-ready.

**Verdict:** DROP, but retain as a search lesson: generation-structure states can induce discrete computation-mode switches.

### 28. Metacognitive monitoring improves while control fails
Cross-paper pattern: reasoning can improve confidence monitoring; hidden states can contain early error awareness; reasoning models can still knowingly fail to abstain; non-reasoning LLMs can causally use confidence to drive abstention.

Initially promising as `monitoring → control` dissociation. Direct owner search found 2026 *LLMs Know When They Know, but Do Not Act on It*, explicitly separating monitoring from control and introducing a harness that reconnects them. Other metacognition benchmarks use the same abstraction.

**Verdict:** DROP broad parent. Do not survive by narrowing to “reasoning post-training specifically”.

### 29. Correct guidance has an over-specificity threshold
Evidence spans arithmetic explicit rules, SPARKLE human plans, PieceHint and procedural-knowledge injection. However ICLR-2026 *Off-Trajectory Reasoning* already defines **Guidability** and asks whether models can use correct stronger-model partial reasoning; concurrent granularity work also studies non-monotonic guidance effects.

**Verdict:** DROP broad parent.

### 30. Prompt repetition / problem restatement as goal refresh
Off-trajectory recovery is strongly helped by problem restatement; prompt repetition helps standard decoder-only LMs; reasoning models spontaneously echo prompts. But RE2, Prompt Repetition, ICLR-2026 *Echoes as Anchors*, and PartRep already centralize rereading/repetition and causal-mask information pathways.

**Verdict:** DROP, including the broader “causal re-encoding” unification.

### 31. Semantically equivalent / isomorphic inputs should preserve decisions
Robustness under paraphrases, flip-flop consistency and equivalent prompt transformations is already a substantial direct topic. Renaming this as equivariance does not create a new parent.

**Verdict:** DROP.

### 32. Reasoning overrides adaptive knowledge gating
EACL-2026 entity comparison finds larger models strategically use numerical knowledge when it is reliable, while CoT pushes models toward numerical-feature use. This suggests a possible `reasoning → less selective strategy gating` effect.

Owner search finds extensive confidence/metacognitive-routing work, but no strong independent repeated mother phenomenon yet showing that CoT systematically destroys reliability-sensitive strategy selection across tasks.

**Verdict:** SEED ONLY; insufficient repeated evidence.

## Round-level assessment

No new SERIOUS candidate was found. This is intentional: several ideas were attractive, but most either (a) already have a direct 2025–2026 topic owner, (b) are one-paper future-work gaps, or (c) require gambling on an unstablished phenomenon.

The two least-dead seeds are:
1. **Strict logical information monotonicity:** `C` vs `C + entail(C)`; needs an existing stable mother effect before promotion.
2. **Supervision-density can obstruct algorithm acquisition:** repeated in controlled algorithmic settings; needs an independent natural-language reasoning phenomenon before promotion.

Neither is authorized for formal selection or compute.

## Search strategy for next round

Continue with a higher bar:
- prioritize side anomalies independently repeated across 2–3 strong papers under different names;
- aggressively search for a later paper that has already centralized them;
- search old empirical laws only when the modern regime changes the same quantity;
- avoid generic reasoning-length, self-correction, confidence/calibration, memory, RAG, judge, safety and benchmark-audit neighborhoods unless a qualitatively new scientific object appears;
- do not create L30 merely because this round was large.
