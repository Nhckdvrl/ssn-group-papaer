# Search after L36 — 2026-09-14

Target: ACL / EMNLP / NAACL Main. This round continued pressure-first / provenance-first search across independent scientific objects. It did not expand L36.

## New survivor

### L37 — When Do Label Semantics Break ICL's Inference–Verbalization Boundary?

**Verdict: PILOT-AUTHORIZED — E01 ONLY.**

Selection: `candidates/L37_SEMANTIC_LABEL_BOUNDARY/SELECTION.md`

Pressure:
- Tao et al. (EMNLP Findings 2024) causally support an inference→verbalization factorization and inference invariance under semantically arbitrary label remapping (`true/false → cat/dog`).
- *Semantic Anchors in ICL* reports that meaning-bearing inverted labels are behaviorally almost impossible to override in 1–12B few-shot models.
- ACL 2025 input-label-mapping and ACL 2026 local-task-vector work show label positions causally participate in ICL, but do not test whether the *pretrained semantics of the label word* contaminates upstream task inference under direct semantic conflict.

RQ:
> Under anti-semantic labels, does the model still infer the correct underlying class and fail only in downstream verbalization, or does label semantics alter the inferred task representation itself?

Decisive operation:
- same task/items/demos/model;
- congruent vs opaque vs anti-semantic label regimes;
- Tao-style layer-wise interchange so an ANTI-derived query state is routed through an OPAQUE verbalization channel;
- outcome A: neutral readout recovers the correct class → verbalization bottleneck;
- outcome B: neutral readout remains corrupted → inference contamination / boundary condition on modularity.

The bridge is not the contribution. The contribution survives only if the causal intervention identifies which side of the inference–verbalization boundary semantic conflict changes.

## Important NO-GO / HOLD results from this round

1. **Exposure-bias → reasoning recovery** — NO-GO. ICLR 2026 already directly intervenes on CoT and studies recovery.
2. **Pragmatic judgment vs explicit reasoning** — HOLD/NO-GO current form. Behavioral dissociation exists, but selective causal operation was not found and the route overlaps earlier reasoning-invariance parent.
3. **Verbal confidence vs token-probability confidence** — NO-GO. Joint-channel confidence work already owns the broad dissociation; remaining training interaction is bridge-like.
4. **Self-generated/public commitment vs external error recovery** — NO-GO. Nature Machine Intelligence 2026 self-attribution work and ACL 2026 Thinking Traps directly own the stickiness/revision parent.
5. **RL creates vs reuses representations** — NO-GO. ACL 2026 `Why Does Reinforcement Learning Generalize?` already uses same-base/same-data feature alignment and causal intervention.
6. **Early context relevance vs late relevance** — NO-GO. Dynamic sparsity/reactivation work already owns step-dependent token importance.
7. **Confidence-gated adaptive compute can starve confident-wrong problems** — NO-GO. Existing uncertainty-aware/adaptive-compute work already uses calibration to allocate reasoning budget.
8. **Self-rewarding closes over its own evaluator preference** — NO-GO after 2026 direct owner showing self-play judge pass rate can rise while real correctness stalls and independent judge commitment fixes the false-positive basin.
9. **Generic reasoning-induced grounding/closure pressure** — NO-GO current generic form. Tool hallucination, incomplete-input fabrication, and evidence-grounded reasoning papers already occupy neighboring mechanisms.
10. **SFT knowledge degradation = representation vs access policy** — NO-GO. 2026 work already separates knowledge acquisition from ability to use knowledge; overlaps L34.
11. **Negation blindness mechanism** — NO-GO current form. Strong mother, but semantic-state failure vs answer-selection failure is not selectively identifiable with ordinary decoder patching.
12. **Moses / semantic illusion** — NO-GO as mother for modern models. Strong old model effect but much weaker in GPT-3.5/4; asking why post-training removed it overlaps existing training/invariance routes.
13. **CHOKE / hallucination despite known answer** — NO-GO after direct 2026 owner `Hallucination as Commitment Failure`, which explains semantic probability mass fragmentation vs concentrated wrong commitment.
14. **Corrective explanations: ICL hurts vs SFT helps** — NO-GO current form. SAME-QUANTITY failed; SFT correction treatment bundles wrong trajectory, explanation, and corrected solution, and rationales can help ICL in other tasks.
15. **Code pretraining → semantic-vs-formal control bias** — HOLD / feasibility. Controlled code-mixture literature already has high owner density; no cheap matched checkpoint substrate locked.
16. **Context length alone → position-coordinate effect** — NO-GO current form. Position-ID effects are already established, and the strongest controls in the mother do not reduce to one clean position mechanism: global RoPE shifts and increased relative distances differ.

## Search lesson

The productive move in L37 was not `find a surprising label failure`. It was:

1. recover a causal law from strong prior work (`inference is invariant to arbitrary label remapping`);
2. find a second established result that violates the apparent scope of that law (`meaning-bearing inverted labels cannot be behaviorally overridden`);
3. identify the exact hidden condition omitted by the first law (`semantic inertness of the label space`);
4. construct an intervention that makes both possible outcomes scientifically informative (`ANTI inference state → neutral/opaque verbalizer`).

This is the same high-level provenance family as Learning-vs-Retrieval and Flexibility Trap: revise an apparently general law into a conditional law, rather than hunting a new anomaly.
