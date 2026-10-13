# 开源强基线与运行边界（核查日 2026-10-13）

**目前只核查公开项目 README/论文资料，尚未在用户服务器运行，不等于正式复现。**

| 项目 | 研究对象/能直接测什么 | 代码 | 需要真实验证的障碍 |
|---|---|---|---|
| **KNUDGE**（EMNLP 2024） | 游戏支线任务 NPC 的本体知识、对话及任务结构 | https://github.com/nweir127/KNUDGE | 数据重建脚本、任务约束、许可；先查看 quest 真实样本 |
| **CDT**（ACL 2026） | 情境→人物决策规则的可执行化 | https://github.com/KomeijiForce/Codified_Decision_Tree | 官方构树例用 GPT-4.1，检查 API/本地替换、数据许可 |
| **NCP-Bench**（ICML 2026） | 叙事世界事实/承诺与玩家输入 | https://github.com/NLP2CT/NCP-Bench | **narrator 不是 NPC**；LLM judge/不同 judge 比较必须复核 |
| **PCSP**（2026 arXiv） | persona 条件→游戏行动、低时延共享策略 | https://github.com/yoosunghong/pcsp | 含 Unreal 和 PPO，先独立验证行为 probe，不直接重训全部系统 |
| **Collab-Overcooked**（EMNLP 2025） | 真正的行动协作、资源分工、通信 | https://github.com/YusaeMeow/Collab-Overcooked | README Python 3.8+mpi4py；支持本地 vLLM 但需要适配旧环境 |
| **TALES**（NeurIPS 2026） | 游戏行动循环、合法行动和复杂度门槛 | https://github.com/microsoft/tale-suite | **player agent**；Python ≥3.12，部分游戏依赖 Java；只做环境参考 |
| **FAIRGAMER**（ACL 2026） | NPC 交易/合作/竞争的角色敏感决策 | https://github.com/BingkangShi/FairGamer | 官方高并发 API、预设公平性指标需要仔细审计 |

**不承诺一次复现全部。** 先判断哪种数据真正具备 NPC 角色、局部观察、合法行动、可复算的世界后果和可供对比的强方法。未经定位不大规模改造数据/引擎。

## E00 环境门槛
1. 检查 upstream SHA/requirements/许可证/数据格式/官方 baseline 和 evaluator 的执行入口。真实基线若依赖无法使用的私有 API，需要明确“本地改造 vs 原版复现”的边界。
2. 选具有自然状态转移与正控制的 substrate；记录 reset→observe→act→step→reward/state。第一条轨迹必须证明世界引擎而非评测 LLM 决定事件发生与否。
3. 核查官方结果的定义、seed/场景、判分器版本。先跑阳性/阴性控制及多次相同设置，查不稳定性。
4. 对固定模型算力预算、吞吐、p50/p95、单回合 token、磁盘 I/O 和必要 CPU RAM 进行实测后再铺开多卡实验。
5. KNUDGE/CDT 可能适合角色知识/行为；NCP 对剧情承诺，Collab 对真实合作；不为了方便而把不同任务拼成单指标。

## 硬件及数据纪律
- 单 GPU 起步，能单节点 4卡再考虑本机并行；跨节点**各自独立**，不训练跨机巨模型。不假定 A100、PRO6000、H20 来自同一共享网络。
- 模型和数据预缓存至授权节点本地；Git 只存轻量 manifest / 复现脚本 /可匿名化统计结果，大资产不进仓库。
- 记录每个实验：上游 Git commit、模型 revision/checksum、数据 hash、程序 config、随机种子、节点类型、token 和 GPUh、失败条件。遵守实习单位保密及资产可转移许可。
