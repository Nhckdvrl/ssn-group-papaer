# L12 Live Novelty Audit

**Search date:** 2026-09-09

## Search Protocol

Searched ACL Anthology and arXiv for reasoning training/model + framing, risky decision, cognitive bias, misleading context, representation, readout, canonicalization, suppression, and causal intervention. No work dated after the current date can yet exist.

## Closest Current Work

- Ge et al., *Mind the (DH) Gap!*, ACL 2026 Outstanding Paper: owns the behavioral phenomenon, broad model survey, and evidence associating mathematical reasoning training/SFT with invariance. <https://aclanthology.org/2026.acl-long.479/>
- *Framing Matters* (2026): owns behaviorally grounded value alignment and representation-level intervention for framing sensitivity. It is the closest mechanism neighbor, but does not study how sibling reasoning-vs-instruction post-training branches transform an established risky-choice invariance. <https://arxiv.org/abs/2605.28188>
- *Instructed to Bias*, TACL 2024: owns evidence that instruction tuning can create cognitive bias.
- *Scaling Reasoning, Losing Control*, ACL 2026: owns reasoning/instruction-control trade-offs, not canonicalization versus preserved-context policy use.
- *Untangling the Mechanisms of Misleading Context in Medical Question Answering* (2026) is a causal context-use neighbor in a different task and training comparison. <https://arxiv.org/abs/2609.02754>
- *The Ignition Is Real, and It Lives at the Readout* (2026) is a conceptual readout neighbor in a recurrent-depth reasoner, not a risky-choice or post-training-branch study. <https://arxiv.org/abs/2608.03263>
- Hao et al., *Reasoning Traces Shape Outputs but Models Won't Say So* (ACL 2026), own broad causal evidence from thought injection. L12-E05 therefore cannot claim that traces generally affect answers; its role is to localize the established decision-invariance transition. <https://aclanthology.org/2026.acl-long.1986/>
- *`</think>` Doesn't Stop Reasoning* (2026-09-03) shows that injected end-of-think tokens can trigger spurious termination while reasoning continues. It directly invalidates a naive interpretation of L12-E04 and is incorporated as a method boundary. <https://arxiv.org/abs/2609.03633>

## Reviewer Compression After Refresh

Strongest attack after the result: **“Mind the DH Gap plus a standard thought-injection test.”** It wins if the contribution stops at frame decodability or generic trace causality. It does not compress a paper that localizes the sibling-branch transition, distinguishes prompt information availability from use, identifies the decision computation that produces invariance, and establishes a meaningful arithmetic/deliberation boundary.

## Current Novelty Verdict

**PASS for pilot.** No located paper owns the full identity:

> established reasoning-induced invariance -> sibling-branch training-regime localization -> canonicalization versus preserved-context/use/deliberation distinction -> decision-specific causal test -> boundary and reinterpretation of rationality.
