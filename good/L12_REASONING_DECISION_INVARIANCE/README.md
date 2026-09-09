# L12 — Reasoning-Induced Invariance

## Semantic Abstraction or Causal Disengagement?

**Status:** **A / CONTINUE-PILOT / Rank 2**  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Last audited:** 2026-09-09

> **Natural question:** When reasoning-oriented post-training makes a model nearly invariant to fact-equivalent presentation, did it learn what contextual variation is semantically irrelevant, or did context simply lose causal control over the decision?

---

# 1. Established behavioral substrate

ACL 2026 Outstanding **Mind the (DH) Gap!** reports that reasoning-oriented models are substantially less sensitive to order, gain/loss framing, explanations, and description-vs-history presentation, and points to mathematical reasoning training as an important differentiator.

Our OLMo sibling-branch pilot independently reproduces a strong contrast on the three published prospects:

- Instruct-SFT frame consistency ≈ **0.817**;
- Think-SFT ≈ **0.992**;
- difference ≈ **+0.175**, bootstrap CI **[0.025, 0.367]**.

L12 is no longer gambling on the parent behavior.

---

# 2. What is already known locally

### Supported
- Think-SFT is much more presentation-invariant than sibling Instruct-SFT;
- gain/loss identity remains recoverable in early/middle prompt representations;
- a complete natural reasoning trajectory strongly affects final A/B readout.

### Invalid / insufficient
- injecting `</think>` did **not** create a strict no-reasoning mode;
- decodability does not imply causal use;
- generic thought injection is already prior work;
- answer-free arithmetic snippets did not reproduce the large natural-trace effect.

The mechanism remains open.

---

# 3. Scientific accounts

### Selective semantic abstraction
The model learns that some presentation differences do not change task semantics and constructs the same decision state across them.

### Causal disengagement / context flattening
Context remains represented, but post-training broadly weakens its influence on action selection—even when some context should matter.

### Deliberative reconstruction
Prompt representations retain context differences while the reasoning trajectory reconstructs a normalized decision state.

### Specialized arithmetic policy
The effect is strong mainly when risky choice can be converted into explicit arithmetic.

### Another stronger account
Allowed if it explains the established branch contrast and survives causal tests.

Do not force a binary canonicalization-vs-override story.

---

# 4. Next load-bearing boundary

Before more generic patching, distinguish:

## Normatively irrelevant variation
The option distributions/decision facts are unchanged; presentation changes only. A well-behaved decision system should be invariant.

## Decision-relevant variation
A minimal matched factual change alters payoff/probability information enough that the objectively EV-preferred option changes. A well-behaved system should be sensitive.

This asks whether Think-SFT is **selectively invariant** or simply **less context-sensitive**.

Both outcomes are scientifically meaningful.

---

# 5. Paper identity

> established reasoning-induced invariance  
> → selective semantic abstraction vs causal disengagement  
> → relevant/irrelevant context boundary  
> → causal decision-state construction  
> → reinterpret what “reasoning makes models more rational” means

Not the identity:
- another framing benchmark;
- frame probes;
- thought injection;
- answer-token attention;
- “layer X contains framing”;
- generic reasoning-vs-instruction control.

---

# 6. Training-attribution caveat

`Olmo-3-7B-Instruct-SFT` and `Olmo-3-7B-Think-SFT` are sibling branches from a common base and use native chat templates.

Do **not** claim strict one-variable causal training attribution.

Safe current claim:
> matched reasoning-oriented and instruction-oriented sibling branches exhibit a reproducible difference.

Seek cleaner lineage/training evidence before stronger attribution.

---

# 7. Current gates

| Gate | Verdict |
|---|---|
| Natural / important | **PASS++** |
| Scientific tension | **PASS++** |
| Data / identification | **PASS**, training-attribution caveat |
| Paper-level novelty | **PASS** |
| Outcome robustness | **PASS++** |
| Main-level calibration | **PASS++** |
| Anomaly robustness | **PASS++** |
| Why-space / narrative-space | **PASS** |

# 8. Immediate work

1. **L12-E07 — Relevant-vs-Irrelevant Context Boundary**
2. **L12-E08 — Conclusion-Free Decision-State Causal Substitution**, only after E07 is stable.

See [PILOT_CARD.md](PILOT_CARD.md) and the experiment registry.
