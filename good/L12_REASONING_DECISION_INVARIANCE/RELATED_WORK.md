# L12 Live Related Work / Novelty Audit

**Search date:** 2026-09-09

# 1. Behavioral parent

## Mind the (DH) Gap! — ACL 2026 Outstanding
<https://aclanthology.org/2026.acl-long.479/>

Owns the broad reasoning-vs-conversational risky-choice contrast: reasoning models are substantially more invariant to order, gain/loss framing, explanation, and description/history presentation.

L12 begins from the unresolved mechanism behind that transition.

# 2. Generic reasoning-trace causality is already occupied

## Reasoning Traces Shape Outputs but Models Won’t Say So — ACL 2026
<https://aclanthology.org/2026.acl-long.1986/>

Shows that injected reasoning snippets can causally alter model outputs.

## KisMATH — TACL 2026
<https://doi.org/10.1162/TACL.a.729>

Shows that nodes in extracted CoT causal graphs contribute to final answers.

Therefore “reasoning traces affect answers” is not L12’s novelty.

# 3. Hidden-state / trajectory mechanism work is also close

## When Chain-of-Thought Fails, the Solution Hides in the Hidden States — 2026
<https://arxiv.org/abs/2604.23351>

Uses activation patching to transfer CoT token hidden states into direct-answer computation.

## Mechanistic Interpretability of Chain-of-Thought Reasoning via Sequential Activation Patching — 2026
<https://arxiv.org/abs/2608.22332>

Studies causally important locations distributed along reasoning trajectories.

## How Do Answer Tokens Read Reasoning Traces? — Findings ACL 2026
<https://aclanthology.org/2026.findings-acl.1507/>

Studies how answer tokens attend to and integrate reasoning traces.

So L12 cannot be “we patched CoT states” or “we found important reasoning tokens/layers.”

# 4. Surviving paper-level identity

> **reasoning-oriented post-training is associated with a sharp behavioral invariance transition, while prompt frame information remains present; the open question is whether self-generated long reasoning becomes a new causal control channel that takes over the final decision.**

The decisive mechanism sequence is:

> behavioral transition  
> → preserved prompt information  
> → large natural-trajectory control  
> → distributed trajectory vs terminal self-commitment  
> → trajectory-built pre-answer decision state.

This remains distinct from generic CoT causality because the scientific object is **training-associated control transfer tied to an established invariance phenomenon**, not CoT usefulness in isolation.

# 5. Reviewer compression

The dangerous compression is:

> “Mind the DH Gap + generic CoT patching.”

That compression wins if L12 stops at E05 or merely localizes a layer.

It loses only if E07/E08 establish a coherent control-transfer mechanism explaining the behavioral transition.

# 6. Current verdict

**CONTINUE-PILOT.**

No broad defense battery. Run the two decisive mechanism steps and reassess.
