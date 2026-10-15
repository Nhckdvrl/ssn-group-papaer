# AgentIF — Benchmarking Instruction Following in Agentic Scenarios

核读2026-10-15；[NeurIPS2025 Datasets & Benchmarks正文](https://proceedings.neurips.cc/paper_files/paper/2025/file/51bb3a8a33610a25aae074bfc51b1b1f-Paper-Datasets_and_Benchmarks_Track.pdf)。本轮读§3–4和Tables1–2；未完整复现作者代码，官网新协议不与旧表直接混比。

来源是50真实agent应用的系统指令，经生成、过滤与人修订获得707条、8415约束；平均1723词/11.9约束。评估先判条件是否触发，再以code/LLM/hybrid评价约束与整条指令。正文已有条件/工具约束困难，不能把多约束能力弱当新发现。

**我们的定位解释：** E65的读数来自真实原生物品状态与任务执行；需要问同样可行的使用动作为何受保护包影响。它既不同于仅文本约束命中，也不凭这一差异宣称新机制。先判限制范围和上下文采纳；不改成本或评价使“否定冻结”成立。
