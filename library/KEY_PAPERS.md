# Key Papers — Curated Anchors

**Last verified:** 2026-09-28

This is not a comprehensive bibliography. These are papers worth rereading because they define a primitive, change an assumption, expose a failure, or provide a reusable open baseline.

---

## Research craft / baseline discipline

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| RC01 | **ResNet strikes back: An improved training procedure in timm** (2021) | ANCHOR / CRAFT | A strong reminder that weak/old baseline recipes can manufacture “novel method” gains. | https://arxiv.org/abs/2110.00476 |

---

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

---

## Reasoning / test-time compute

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| RS01 | **Self-Consistency Improves Chain of Thought Reasoning** (2022) | ANCHOR | Moves inference from one greedy reasoning path to marginalizing multiple paths. | https://arxiv.org/abs/2203.11171 |
| RS02 | **Tree of Thoughts** (2023) | ANCHOR | Makes explicit search state / branching part of inference rather than only sampling. | https://arxiv.org/abs/2305.10601 |
| RS03 | **Let's Verify Step by Step** (2023/ICLR 2024) | ANCHOR | Final-answer supervision can be too late; step-level supervision becomes the object. | https://arxiv.org/abs/2305.20050 |
| RS04 | **Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters** (2024) | BRIDGE | Key move from “more test-time compute” to **compute allocation conditioned on problem difficulty**. | https://arxiv.org/abs/2408.03314 |

---

## Architecture / recurrence / memory

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| AR01 | **Mamba: Linear-Time Sequence Modeling with Selective State Spaces** (2023) | ANCHOR / ARTIFACT | Makes input-dependent selection the key repair for SSMs on discrete language. | https://arxiv.org/abs/2312.00752 |
| AR02 | **Transformers are SSMs / Mamba-2** (ICML 2024) | ANCHOR / ARTIFACT | Unifies recurrence and attention through structured state-space duality; useful antidote to surface-level architecture taxonomy. | https://arxiv.org/abs/2405.21060 |
| AR03 | **RecurrentGemma** (2024) | ANCHOR / ARTIFACT | Open recurrent/local-attention language models; useful strong public architecture baseline. | https://arxiv.org/abs/2404.07839 |
| AR04 | **Leave No Context Behind: Infini-attention** (2024) | ANCHOR | Clean attention + compressive-memory hybrid and a useful reference for “exact vs compressed history”. | https://arxiv.org/abs/2404.07143 |
| AR05 | **Titans: Learning to Memorize at Test Time** (2025) | BRIDGE | Reframes long-term memory as test-time learning in a neural memory rather than a fixed recurrent vector. | https://arxiv.org/abs/2501.00663 |
| AR06 | **Scaling Latent Reasoning via Looped Language Models (Ouro)** (2025) | FRONTIER / ARTIFACT | Open looped-LM family; makes iterative latent computation a pretraining primitive. | https://arxiv.org/abs/2510.25741 |
| AR07 | **Mamba-3: Improved Sequence Modeling using State Space Principles** (2026) | FRONTIER / ARTIFACT | Current SSM lineage update; reread before making claims about what “modern Mamba” can/cannot do. | https://arxiv.org/abs/2603.15569 |

---

## MoE / routing

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| MOE01 | **Switch Transformers** (2021) | ANCHOR | Simplified top-1 sparse routing; canonical scale/training-stability baseline. | https://arxiv.org/abs/2101.03961 |
| MOE02 | **Mixture-of-Experts with Expert Choice Routing** (2022) | ANCHOR | Reverses token→expert allocation into expert→token selection; useful reminder that routing primitive itself is a design choice. | https://arxiv.org/abs/2202.09368 |
| MOE03 | **DeepSeekMoE: Towards Ultimate Expert Specialization** (ACL 2024) | ANCHOR | Shared vs routed experts and fine-grained expert segmentation; important specialization reference. | https://aclanthology.org/2024.acl-long.70/ |

---

## Mechanistic interpretability / model science

| ID | Paper / project | Role | Why reread | Link |
|---|---|---|---|---|
| MI01 | **In-context Learning and Induction Heads** (2022) | ANCHOR | Classic capability↔mechanism emergence argument; useful for causal-evidence standards. | https://arxiv.org/abs/2209.11895 |
| MI02 | **Function Vectors in Large Language Models** (ICLR 2024) | ANCHOR / ARTIFACT | Compact causal task representations; good example of moving from correlation to intervention. | https://arxiv.org/abs/2310.15213 |
| MI03 | **Towards Monosemanticity** (Anthropic, 2023) | ANCHOR | Changes unit of analysis from neurons to learned features. | https://www.anthropic.com/research/towards-monosemanticity-decomposing-language-models-with-dictionary-learning |
| MI04 | **Tracing the thoughts of a large language model** (Anthropic, 2025) | BRIDGE / ARTIFACT | Moves from feature discovery toward computational/attribution graphs. | https://www.anthropic.com/research/tracing-thoughts-language-model |
| MI05 | **A global workspace in language models** (Anthropic, 2026) | FRONTIER | Current example of posing a broad functional question, then attacking it with multiple causal properties rather than one probe. | https://www.anthropic.com/research/global-workspace |

---

## Omni / speech

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| VO01 | **Moshi: a speech-text foundation model for real-time dialogue** (2024) | ANCHOR / ARTIFACT | Full duplex as a modeling problem; parallel user/system streams and physical-time constraints. | https://arxiv.org/abs/2410.00037 |
| VO02 | **Qwen2.5-Omni Technical Report** (2025) | ANCHOR / ARTIFACT | Thinker–Talker separation, streaming multimodal input, text/speech co-generation; useful architecture reference. | https://arxiv.org/abs/2503.20215 |

---

## VLA / robotics

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| VLA01 | **Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT)** (2023) | ANCHOR / ARTIFACT | Action chunking grows directly from compounding-error / high-precision control pressure. | https://arxiv.org/abs/2304.13705 |
| VLA02 | **RT-2** (2023) | ANCHOR | Converts actions to language-like tokens to unify web semantics and robot control. | https://arxiv.org/abs/2307.15818 |
| VLA03 | **OpenVLA** (2024) | ANCHOR / ARTIFACT | Strong open VLA baseline and fine-tuning substrate. | https://arxiv.org/abs/2406.09246 |
| VLA04 | **π0: A Vision-Language-Action Flow Model for General Robot Control** (2024) | ANCHOR | Useful contrast to purely autoregressive action tokenization; flow-matching action decoder. | https://arxiv.org/abs/2410.24164 |
| VLA05 | **FAST: Efficient Action Tokenization for Vision-Language-Action Models** (2025) | BRIDGE / ARTIFACT | Excellent example of a successful abstraction (“actions as tokens”) becoming the next bottleneck. | https://arxiv.org/abs/2501.09747 |

---

## Cross-domain research-move anchors

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| XD01 | **Elucidating the Design Space of Diffusion-Based Generative Models** (2022) | ANCHOR / CRAFT | Turns a convoluted method zoo into explicit independent design axes, then improves several at once. | https://arxiv.org/abs/2206.00364 |
| XD02 | **Sharpness-Aware Minimization (SAM)** (2020/ICLR 2021) | ANCHOR | Creates a new optimization object: neighborhood sharpness, not only endpoint loss. | https://arxiv.org/abs/2010.01412 |
| XD03 | **SAM operates far from home** (2023) | BRIDGE | Re-attribution example: accepted endpoint/minimum explanation is insufficient; training dynamics matter throughout the trajectory. | https://arxiv.org/abs/2302.08692 |

---

## Notes

- “FRONTIER” means **re-check before making a latest-state claim**.
- For deep parent→successor reconstruction, use `../chasing trends/academic/GENEALOGY_LIBRARY_INDEX.md`.
- Candidate-specific nearest prior does **not** belong here; put it in the candidate/observation package.
