# 2026-09-14 — IP03 / Succinctness ≠ Learnability — Exhaustion Audit

**Status:** WALL descendant exhausted in current form. **No L-series. No pilot. No new K ID assigned.**

## Standing problem

IP03 remains important:

> A model may be able to represent many computations. What determines which representable computation gradient-based learning actually selects?

This document closes only the current descendant around **description/succinctness simplicity versus optimization/geometric accessibility**.

## Why the route looked promising

Several mature lines use different notions of “simple” or “natural”:

- Hahn & Rofin (ACL 2024 Best Paper): high input sensitivity constrains the Transformer loss landscape; sensitive functions occupy isolated parameter regions and are hard to learn/generalize.
- Bergsträßer, Cotterell & Lin (ICLR 2026 Outstanding): Transformers can represent some computations extremely **succinctly**, introducing description size as a stronger expressivity quantity than bare representability.
- Zhao (Findings ACL 2026): gradient-trained Transformers can sometimes converge to the predicted succinct circuits through a grokking / complexity-collapse transition.

This suggested an internal tension:

> an algorithm can be descriptionally cheap yet highly sensitive / geometrically difficult to reach.

PARITY is the canonical intuition: very short algorithmic description, very high sensitivity.

## Why it does not survive as a new question

The hoped-for missing variable — **parameter-space geometry / measure / accessibility** — is now directly owned.

Köver, Butoi, Svete, Hahn & Cotterell (ICML 2026 / arXiv 2606.08768), *Understanding the Parameter Space Geometry of Transformers Encoding Boolean Functions*, explicitly studies the expressivity–learnability gap and proves that sensitive functions can be representable while occupying vanishingly small / measure-zero regions of Transformer parameter space that random initialization almost surely misses.

Thus the headline

> `compact representation does not imply learnability because the implementation may be geometrically inaccessible`

is no longer an unasked law.

The remaining question

> `when does succinctness predict learning preference, and when is it merely an existence result?`

is important, but currently too broad. Turning it into a paper would require inventing a new scalar or running a head-to-head benchmark of multiple simplicity notions. That would regress into `theory A + theory B -> compare on tasks`, without an independent mother phenomenon or mature same-quantity disagreement.

## Reviewer compression

> “ICLR 2026 succinctness + ACL 2024/ICML 2026 sensitivity/parameter-space geometry + another empirical comparison of which notion predicts SGD.”

That compression is currently accurate.

## Why this is WALL exhaustion, not evidence that IP03 is solved

IP03 remains a high-value standing problem. What is exhausted is the current attempt to derive a candidate from:

- sensitivity vs description length;
- succinctness vs basin volume;
- representability vs geometric accessibility;
- regularization/grokking as the bridge from succinctness to learned algorithm.

These routes now have direct 2024–2026 owners and do not leave a sufficiently independent scientific uncertainty.

## Reopen condition

Only reopen this descendant if a **natural, independently important computation** supplies two mature algorithm-selection accounts that make incompatible predictions about the **same trained learner / same data / same observable**, and a new operation can distinguish them without defining a new convenience metric after seeing the papers.

Do **not** reopen because of:

- another formal language;
- another architecture;
- another grokking task;
- another simplicity metric;
- regularization ablations;
- a generic “expressive but hard to learn” example.

## Source trail

- Hahn & Rofin, ACL 2024 Best Paper, *Why are Sensitive Functions Hard for Transformers?* — https://aclanthology.org/2024.acl-long.800/
- Bergsträßer, Cotterell & Lin, ICLR 2026 Outstanding, *Transformers are Inherently Succinct* — https://proceedings.iclr.cc/paper_files/paper/2026/hash/5f7804e8855efe5554025217abc49315-Abstract-Conference.html
- Zhao, Findings ACL 2026, *Do Transformers Grok Succinct Algorithms?* — https://aclanthology.org/2026.findings-acl.1301/
- Köver et al., ICML 2026 / arXiv 2606.08768, *Understanding the Parameter Space Geometry of Transformers Encoding Boolean Functions* — https://arxiv.org/abs/2606.08768
