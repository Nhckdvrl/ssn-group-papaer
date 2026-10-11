# Key Papers — 架构、记忆与长上下文（Architecture / memory / long context）

从 `library/KEY_PAPERS.md` 按题材拆出（2026-09-30），ID 与内容保持不变。标签含义见 `../../KEY_PAPERS.md`。


## Architecture / recurrence / memory

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| AR01 | **Mamba: Linear-Time Sequence Modeling with Selective State Spaces** (2023) | ANCHOR / ARTIFACT | Makes input-dependent selection the key repair for SSMs on discrete language. | https://arxiv.org/abs/2312.00752 |
| AR02 | **Transformers are SSMs / Mamba-2** (ICML 2024) | ANCHOR / ARTIFACT | Unifies recurrence and attention through structured state-space duality; useful antidote to surface-level architecture taxonomy. | https://arxiv.org/abs/2405.21060 |
| AR03 | **RecurrentGemma** (2024) | ANCHOR / ARTIFACT | Open recurrent/local-attention language models; useful strong public architecture baseline. | https://arxiv.org/abs/2404.07839 |
| AR04 | **Leave No Context Behind: Infini-attention** (2024) | ANCHOR | Clean attention + compressive-memory hybrid and a useful reference for “exact vs compressed history”. | https://arxiv.org/abs/2404.07143 |
| AR05 | **Titans: Learning to Memorize at Test Time** (2025) | BRIDGE | Reframes long-term memory as test-time learning in a neural memory rather than a fixed recurrent vector. | https://arxiv.org/abs/2501.00663 |
| AR06 | **Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach (Huginn)** (2025) | ANCHOR / ARTIFACT | Open depth-recurrent model where extra test-time depth reuses a small recurrent core; direct baseline for recurrent-depth science. | https://arxiv.org/abs/2502.05171 |
| AR07 | **Scaling Latent Reasoning via Looped Language Models (Ouro)** (2025) | FRONTIER / ARTIFACT | Open looped-LM family; makes iterative latent computation a pretraining primitive. | https://arxiv.org/abs/2510.25741 |
| AR08 | **Mamba-3: Improved Sequence Modeling using State Space Principles** (2026) | FRONTIER / ARTIFACT | Current SSM lineage update; reread before making claims about what “modern Mamba” can/cannot do. | https://arxiv.org/abs/2603.15569 |
| AR09 | **Latent Chain-of-Thought? Decoding the Depth-Recurrent Transformer** (2025) | BRIDGE / NEGATIVE | Huginn-specific negative/diagnostic reference: latent-CoT readouts are probe-sensitive and additional recurrence gives limited gains in the tested arithmetic setting. | https://arxiv.org/abs/2507.02199 |
