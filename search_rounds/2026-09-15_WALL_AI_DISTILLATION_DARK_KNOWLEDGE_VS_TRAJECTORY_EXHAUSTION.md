# WALL-AI — Distillation: dark knowledge vs teacher trajectories

Date: 2026-09-15
Status: EXHAUSTED AS STANDALONE GENERATOR

## Mother question
Why does knowledge distillation help? Is the useful signal the teacher's full probability geometry ('dark knowledge' among alternatives), or the teacher's sampled/high-quality output trajectories themselves?

## Classical lineage
Hinton-style distillation motivates soft targets by the relative probabilities assigned to non-target alternatives. This explanation requires access to the teacher distribution/logits.

Sequence-level distillation in NMT deliberately distills teacher-generated sequences rather than the complete probability vector. Subsequent work explicitly notes that the standard dark-knowledge explanation does not directly apply and instead analyzes sequence KD as data simplification, mode reduction, and data augmentation.

## Modern direct-owner audit
Modern LLM distillation already makes the same distinction operational:
- logit-level / token-level distillation transmits a dense teacher distribution;
- sequence-level distillation transmits sampled teacher trajectories;
- on-policy/self-distillation work studies distribution mismatch and which granularity of teacher signal helps.
Recent 2025–2026 results directly compare these forms; some report dense logit signals outperforming token/sequence supervision, while other analyses show teacher–student distribution mismatch can make logit matching worse and sequence-level KD preferable.

Therefore 'probability geometry vs trajectories' is not a historically unidentifiable distinction newly unlocked by LLMs. It is a longstanding organizing axis of the distillation literature.

## Verdict
No L-series. A controlled intervention that fixes sampled outputs while perturbing logits would be a modern re-instantiation of the classic dark-knowledge question rather than an independent scientific problem.

## Anti-resurrection
Do not revive as:
- dark knowledge in LLMs;
- logit KD vs sequence KD;
- teacher logits versus synthetic data as a new mechanism;
- larger-model comparison of KD granularity;
- same teacher text with perturbed probability vectors unless another independent theory predicts a new quantity.
