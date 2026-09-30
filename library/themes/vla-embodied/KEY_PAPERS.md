# Key Papers — VLA 与具身智能（VLA / embodied）

从 `library/KEY_PAPERS.md` 按题材拆出（2026-09-30），ID 与内容保持不变。标签含义见 `../../KEY_PAPERS.md`。


## VLA / robotics

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| VLA01 | **Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT)** (2023) | ANCHOR / ARTIFACT | Action chunking grows directly from compounding-error / high-precision control pressure. | https://arxiv.org/abs/2304.13705 |
| VLA02 | **RT-2** (2023) | ANCHOR | Converts actions to language-like tokens to unify web semantics and robot control. | https://arxiv.org/abs/2307.15818 |
| VLA03 | **OpenVLA** (2024) | ANCHOR / ARTIFACT | Strong open VLA baseline and fine-tuning substrate. | https://arxiv.org/abs/2406.09246 |
| VLA04 | **π0: A Vision-Language-Action Flow Model for General Robot Control** (2024) | ANCHOR | Useful contrast to purely autoregressive action tokenization; flow-matching action decoder. | https://arxiv.org/abs/2410.24164 |
| VLA05 | **FAST: Efficient Action Tokenization for Vision-Language-Action Models** (2025) | BRIDGE / ARTIFACT | Excellent example of a successful abstraction (“actions as tokens”) becoming the next bottleneck. | https://arxiv.org/abs/2501.09747 |
| VLA06 | **Latent Bridge: Feature Delta Prediction for Efficient Dual-System VLA Inference** (2026) | FRONTIER / ARTIFACT | Reduces slow VLM calls by predicting feature/KV deltas between timesteps; useful cross-timescale interface prior rather than a voice-specific analogy. | https://arxiv.org/abs/2605.02739 |
| VLA07 | **Think at 5 Hz, Act at 20 Hz** (2026) | FRONTIER / FAST-SLOW | Separates slow VLM reasoning from a fast action expert and explicitly trains under stale-cache conditions; strong cross-domain evidence that timescale boundaries are structural. | https://arxiv.org/abs/2607.15621 |

## VLA — semantic information versus action control

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| VLA08 | **Not All Features Are Created Equal: A Mechanistic Study of Vision-Language-Action Models** (2026) | FRONTIER / MECHANISTIC / ARTIFACT | Causal activation interventions expose modality/pathway specialization and cases where language is encoded yet ignored by action. Strong parent for semantic-to-action questions in VLA. | https://arxiv.org/abs/2603.19233 |
| VLA09 | **Restoring Linguistic Grounding in VLA Models via Train-Free Attention Recalibration** (2026) | FRONTIER / METHOD | Diagnoses “linguistic blindness” under contradictory language and proposes a train-free intervention; ownership boundary for simple language-neglect claims. | https://arxiv.org/abs/2603.06001 |
| VLA10 | **Grounded Semantic Re-Binding for Robust Instruction Generalization in VLA Models** (2026) | FRONTIER / METHOD | Finds task semantics can remain internally available while downstream action is vulnerable to joint feature shifts; directly relevant to semantic information vs policy use. | https://arxiv.org/abs/2608.02497 |
| VLA11 | **Beyond Appearance Shifts: Task-Semantic Action Calibration for VLA Models** (NeurIPS 2026) | FRONTIER / ROBUSTNESS | Separates invariance to task-preserving nuisance changes from sensitivity to task-semantic changes; strong ownership pressure on generic “robust VLA semantics” stories. | https://arxiv.org/abs/2609.23650 |
| VLA12 | **Instruction Anchor: Dissecting the Mechanistic Dynamics of Modality Arbitration** (2026) | FRONTIER / MECHANISM | Treats instruction-following as modality arbitration across depth and identifies sparse causal attention pathways; useful mechanistic parent for language-vs-vision control. | https://arxiv.org/abs/2602.03677 |
