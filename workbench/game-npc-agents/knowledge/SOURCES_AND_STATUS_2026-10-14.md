# 来源与真实阅读范围｜2026-10-14

**来源分类与阅读深度两维分别记录。** P0=出处/题名；P1=摘要；P2=正文相关段或代码说明；P3=正文+关键附录细读并核重要实现；P4=本地复现/重算。原始整理时“所有来源非P4／所有训练0”已过期：PCSP、agent-sandbox、LIGHT和MeltingPot已有本地执行，不能据此称复现所有论文主表。最新见 [进度报告](../PROGRESS_REPORT_2026-10-14.md)。安全／经济邻接工作仍按下表范围解释。

| 来源（直接链接） | 论文身份/与游戏 NPC 关联 | 本轮阅读深度与证据边界 |
|---|---|---|
| [Tricking LLM-Based NPCs into Spilling Secrets](https://arxiv.org/html/2508.19288v1) | ProvSec 2025；**直接游戏 NPC 安全** | P2：ar5iv/HTML方法/30样本/判分/结论；非全套统计复算 |
| [Empowering MMO Economic Simulation](https://arxiv.org/html/2506.04699v1) | **KDD 2025 正式论文，直接游戏世界经济** | P2+：正文方法、5组实验、结论、附录结构；代码Zenodo入口未下载 |
| [RoleBreak](https://aclanthology.org/2025.coling-main.494/) | COLING2025 main；角色攻击，**相邻非原生游戏执行** | P1 摘要/方法描述，未核关键脚本 |
| [Dynamic Persona Coherence](https://aclanthology.org/2026.acl-long.1336/) | ACL2026 main；动态人格，偏角色语言 | 正文方法／主表／消融及关键附录已读；匿名代码入口返回401，代码未审 |
| [Lies, Deceit, and Hallucinations](https://www.robertxiao.ca/research/lies-deceit-and-hallucinations/) | CHI2024；**真实游戏 NPC 玩家感知** | P1 作者摘要，玩家研究29人；未细读全部访谈编码 |
| [SKT Detective NPC](https://arxiv.org/abs/2609.23043) | AIIDE2026（作者机构列已接受；当时论文待会期）；**直接游戏信息控制** | P1 原作者摘要，人类研究/零提前披露按作者报告 |
| [AgentDojo](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html) | NeurIPS2024 Datasets & Benchmarks；**跨领域agent安全方法** | P1 官方摘要+代码repo入口 |
| [Agent Security Bench](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5750f91d8fb9d5c02bd8ad2c3b44456b-Abstract-Conference.html) | ICLR2025 main；**agent安全** | P1 官方摘要+代码repo入口 |
| [Agent Bazaar](https://sethkarten.ai/papers/agent-bazaar.html) / [GitHub](https://github.com/sethkarten/AI-Bazaar) | 2026作者页写 COLM（未独立确认官方目录）；**非游戏多Agent市场攻防** | P2 repo README；本地 vLLM/Ollama 后端明确存在；未运行 |
| [TruthMarketTwin](https://arxiv.org/abs/2605.10059) | 2026 arXiv；**非游戏信息不对称电商** | P1 摘要 |
| [Formal Mechanisms for Market Stability](https://arxiv.org/abs/2607.08652) | 2026 arXiv；**非游戏agent市场对抗** | P1 摘要 |
| [Lies We Can See](https://github.com/JunseoKim0103/Lies-We-Can-See) | 2026 arXiv；官方仓库明确 ECCV/COLM **workshop**，MineAmongUs可玩实体行动 | P2 README/code topology；默认示例用付费API且8-agent Docker，每容器有并发冲突 |
| [PCSP](https://github.com/yoosunghong/pcsp) | 2026 arXiv；原生life-sim NPC行为训练 | 训练／梯度／split／独立行为评价源码审计与完整预算训练；不冒称所有表格完全复现 |
| [EA Augmenting Game AI with Deep RL](https://arxiv.org/html/2606.20210v1) | 2026游戏/工业研究；**原生FC25/BF6 NPC控制** | 前轮正文 F（作者数据），当前未额外源代码核对 |
| [AI-Native Games: Survey and Roadmap](https://arxiv.org/html/2607.00527v2) | 2026 arXiv **survey，不冒称录用**；全游戏系统 | P2+ HTML正文II–VI (53可玩样本、游戏规则/多角色/安全/成本) |
| [Intelligent Trading Agents for MMO Economies](https://ojs.aaai.org/index.php/AIIDE/article/view/18680) | AIIDE2008；**原生经济NPC古典先驱** | P1 官方摘要/EVE经济任务 |
| [ccb/agent-sandbox](https://github.com/ccb/agent-sandbox) | 2026 UPenn工程平台，非顶会已接收方法 | 原生parser／retry／Reflect／计划／对话／world审计，本地ActionCastle和三角色1200帧闭环、独立回放均已执行 |
| [AgentSociety 2](https://github.com/tsinghua-fib-lab/agentsociety) | 2026社会模拟框架，非游戏NPC直接系统 | P2 repo README；默认 API 服务，v2 源码要求进一步审计 |
| [Gigax NPC](https://github.com/GigaxGames/gigax) | 游戏NPC生成/本地GGUF资产，不是正式强论文 | P2 repo README，本地模型入口；Shiomi使用它作单轮对话 |
| [NeurIPS 2026 Downloads](https://neurips.cc/Downloads/2026) | 官方题目合集，可能混入 position/workshop/不同 track | P0 仅用于发现；**绝不以题目存在确认main接收或全文深读** |

## 本轮相较旧知识库修正的三个点
1. NPC**直接**安全并非空白：ProvSec2025已在本地模型单NPC秘密任务测攻击，较小实验且标注有构念疑问；“攻击NPC”作为标签本身不能形成 novelty。
2. 游戏**直接**经济已有KDD2025，真实结构包含资源、拍卖、P2P、货币、升级和规划；且 AIIDE2008已经讨论NPC交易和抗剥削。非游戏 AgentBazaar 又已系统研究 Sybil/价格危机，不能称“首次多Agent交易被攻击”。
3. “长期人格漂移”已有COLING2025与ACL2026角色研究；要找到 game-specific 的新科学认识，需在真实角色经历/状态、允许剧情变迁、玩家行为后果上辨明现有理解边界，而非更长对话分类器。

## 待完成而未冒充完成
真实游戏经济KDD Zenodo数据及许可/可运行性未核；ProvSec原30条数据与更多角色未确认；AIIDE侦探完整方法与数据未查；mineamongus实际Docker与本地替换未运行。NeurIPS2026身份仍须逐篇核验，不能把题名索引当全文已读。安全／经济攻防实测仍0；矿区A训练与原生行动实测已有结果，分别记录。
