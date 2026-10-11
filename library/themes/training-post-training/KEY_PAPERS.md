# Key Papers — 训练：预训练、SFT、蒸馏与 RL 后训练（Training dynamics）

从 `library/KEY_PAPERS.md` 按题材拆出（2026-09-30），ID 与内容保持不变。标签含义见 `../../KEY_PAPERS.md`。


## Post-training / RL / alignment

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| PT01 | **Training language models to follow instructions with human feedback** (InstructGPT, 2022) | ANCHOR | Canonical SFT→RM→PPO pipeline; useful for remembering what later methods are changing. | https://arxiv.org/abs/2203.02155 |
| PT02 | **Direct Preference Optimization** (2023) | ANCHOR | Reparameterizes RLHF into a direct preference objective; classic example of changing the optimization object rather than adding machinery. | https://arxiv.org/abs/2305.18290 |
| PT03 | **DeepSeekMath** (2024) | ANCHOR / ARTIFACT | Introduces GRPO in a real open training stack; baseline for modern reasoning RL. | https://arxiv.org/abs/2402.03300 |
| PT04 | **Tulu 3: Pushing Frontiers in Open Language Model Post-Training** (2024) | ANCHOR / ARTIFACT | One of the best open end-to-end recipes; includes methods that failed as well as those that worked. | https://arxiv.org/abs/2411.15124 |
| PT05 | **DeepSeek-R1** (2025) | BRIDGE / ARTIFACT | Changed the premise around large-scale RL and reasoning emergence; important training-regime anchor. | https://arxiv.org/abs/2501.12948 |
| PT06 | **DAPO: An Open-Source LLM Reinforcement Learning System at Scale** (2025) | BRIDGE / ARTIFACT | Decomposes large-scale RL instability into concrete algorithm/system choices; strong reproducibility reference. | https://arxiv.org/abs/2503.14476 |
| PT07 | **Group Sequence Policy Optimization (GSPO)** (2025) | BRIDGE | Makes sequence vs token optimization unit itself the object. | https://arxiv.org/abs/2507.18071 |
| PT08 | **Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective RL for LLM Reasoning** (NeurIPS 2025) | BRIDGE | Good example of turning “RL works” into a learning-signal decomposition at token level. | https://arxiv.org/abs/2506.01939 |
| PT09 | **The Surprising Effectiveness of Negative Reinforcement in LLM Reasoning** (NeurIPS 2025) | BRIDGE | Correct and incorrect rollouts are not symmetric; a clean example of decomposition → mechanism → small method. | https://arxiv.org/abs/2506.01347 |
