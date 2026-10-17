# 游戏 NPC Agent 领域地图

本页保留**重要的问题与科学结构**，不是按易跑程度给标题、也不是“NPC+安全/经济”的机械组合。依据：游戏 AI 原生研究（EA/AIIDE/CHI/KDD）、角色/NLP（ACL/COLING）、agent 机制与安全（NeurIPS/ICLR/ICML）、游戏界技术资料，以及跨领域的社会计算。

## 1. 游戏 NPC 的构成，不预设底座
真实游戏的 NPC 可能是：
1. **剧情/知识角色**：知道哪些事实、何时可说、如何合理撒谎/泄露线索，玩家如何影响剧情；
2. **交互角色/居民**：目标、记忆、情绪、关系、社会规范，会聊天也会做事；
3. **对战 NPC/同伴**：快速行动、对玩家局势反应、设计者控制、适应和训练；
4. **社会/经济主体**：生产、消费、交易、储存货币/道具、组织声誉，形成群体与市场；
5. **多模态/具身 NPC**：视觉感知/语言/动作/声音耦合，实时反馈。

它们都可以是游戏 NPC，但需要不同效度标准。不能将“玩家自己操控的通关模型”当成所有 NPC 的定义；只有拿其 policy/harness 方法迁移后，在 NPC 游戏机制中验证才获得直接意义。

## 2. 横向科学问题（领域分类，不对应当前矿区编号）
| 板块 | 社区关心的真实压力 | 例示近邻（不是新 idea） | 解释/实验可能聚焦什么 |
|---|---|---|---|
| 设计师行为控制与学习 | NPC 的可塑性、设计反馈、动作可用、补丁更新 | EA 2026、MultiGAIL、Direct Behavior Specification、PCSP | 行为监督/训练损失真正怎样改变执行轨迹；行为控制的可预测边界 |
| Agent 系统与执行 | 语言、记忆、规划到动作与游戏世界因果闭环 | LIGHT/Dragon、KNUDGE、KRAFTON、ccb sandbox | 世界真值谁持有、语义输入怎样安全变成合法事件 |
| 社会交互与伙伴 | 长期互惠、误解、合作、对人/其他NPC适应 | Generative Agents、GAMMA、SOTOPIA、CollabBench | 信息不对称、策略互动的自然失败、伙伴分布与真实任务效用 |
| 身份/人格/关系长期动态 | 稳定身份和合法人物成长、情绪波动、记忆更新 | ACL2026 Dynamic Persona、RoleBreak、PCSP | 词面相似≠人格；动作/关系/历史怎样证明 drift 或 adaptation |
| **安全、被攻击与防御** | 玩家/NPC 发起诱导、秘密越权泄露、行动授权、记忆污染、规则篡改 | ProvSec2025 Secret, NeurIPS2024 AgentDojo, ICLR2025 ASB, AIIDE2026 detective | 控制权边界、长程攻击传播、既安全又可玩 |
| **MMO 经济与多主体风险** | 库存/钱/交换/价值/市场，局部自利行为如何放大成系统脆弱性 | KDD2025 MMO economy, AIIDE2008 EVE, AgentBazaar, TruthMarketTwin | 游戏制度与市场真实性、欺诈/套利/协作/坍塌的机制 |
| 剧情、欺骗与真实玩家 | 允许的故事欺骗 vs LLM 无意幻觉；信息揭示节奏和 agency | CHI2024 Lies, AIIDE2026 SKT, NCP | 哪些“错误陈述”有玩法意义；限制多强才破坏玩家自由 |
| 实时多模态与扩展 | 语音/视频行动、低延迟、几百个NPC的资源成本 | ReactiveGWM, WorldMind, PUBG Ally, EA | 模型+游戏引擎分工、NPC策略时序/吞吐与用户体验 |

## 3. 这些关系比“8个标题”更重要
- **安全 ↔ 剧情**：一个侦探游戏里，玩家用对话诱使嫌疑人逐渐吐露线索可能是核心玩法；越过作者设定的未解锁事实、伪造新事件或系统规则，才可能是违规。“不泄露任何秘密”不是自然统一安全目标。
- **漂移 ↔ 学习**：一个受玩家经历影响变得信任/冷漠的角色可能更真实；无依据跟随对方口吻、忘记创作身份、把NPC话语当系统命令才可能是 drift。需要人工/作者目标，而不是一个角色分类器。
- **经济 ↔ 攻防**：NPC 可能在规则内议价、竞标、撒谎、结盟；只有确定该世界的法律/交易规则、谁能控制身份/库存/货币，才能界定 exploit、Sybil、异常财富流和操纵。价格变动本身不是异常。
- **长期互动 ↔ 传播**：受攻击 NPC 的错误可能通过它讲给另一个 NPC、登记入日志、被写进长期记忆等步骤扩散；一般 AgentDojo 研究不自动证明这种游戏社会传播。
- **大模型能力 ↔ 工程真实**：游戏自身状态、任务类型、LLM输入/行动机会、模拟器和 judge 直接决定“能力”。模型大不等于符合角色，模型会答不等于动作真的发生。
- **可玩性 ↔ 安全**：脚本完全封闭可能减少违规，却剥夺开放剧情的有趣性；系统级安全须同时测合法剧情/游戏效用与误阻止率。没有玩家研究不宣称提升沉浸感。

## 4. 四种可能的论文形态（不提前选择）
- **理解/机制：** 澄清一个自然的 NPC 行为/攻击/经济现象真正由哪个条件造成，以及何时失效；强对照/因果干预比画相关性更重要。
- **方法/训练：** 针对现实失败提出简单但可验证、成本公平、跨 NPC 类型有意义的修复/训练方法。
- **新测量/benchmark：** 只有已有测量不能反映某个重要游戏后果，且数据自然、评分真值经检验，才有贡献；不能靠术语新来证明意义。
- **系统/交互研究：** 开放的玩家/NPC/游戏引擎闭环在可执行规则、时延和体验下有稳定可复现实证；系统工程不能只当新模块堆砌。

## 5. 观察哪个层面的证据
对话合法性、作者承诺、NPC局部知识、角色行动、世界事件、奖励/资产账本、社会扩散路径、玩家选择感、延迟/成本，应分别标出“规则可复算/人工标注/LLM judge/推断”。**不要用一个总分把这些互相替代。**

## 6. 来源
[AI-Native Games Survey 2026](https://arxiv.org/html/2607.00527v2) 综述53个可玩作品，讨论 rule-bounded generation、multi-agent worlds 与安全；它区分 AI-native/augmented，但本工作台**不限制只研究 AI-native 产品**。
直接经济：[KDD2025 MMO Agent](https://arxiv.org/html/2506.04699v1)；直接安全：[ProvSec2025 NPC Secrets](https://arxiv.org/html/2508.19288v1)；游戏交互人类证据：[CHI2024 NPC deception](https://www.robertxiao.ca/research/lies-deceit-and-hallucinations/)。
其他严格身份见 [SOURCES_AND_STATUS](DOMAIN_ATLAS.md#source-status)。

## 7. 怎样从领域问题进入具体研究

领域重要性由三类证据共同支持：已发表工作说明同行持续研究什么，开发者第一方材料说明真实制作压力，公开代码与数据说明能检验什么。商业演示不证明方法有效，会议身份不证明我们的变体新颖，能本地跑也不证明问题重要。

作者控制与玩家自由、稳定身份与合理成长、个体利益与群体后果，都是需要在具体游戏规则里解释的关系。现成接口、角色标签或两种指标能对照，不能单独成为选题理由。增量可以是加深整体认识或提出有用方法，不要求每个组件都从未有人用过。

对每个候选，连接四层：领域仍重要的问题 → 可信的自然线索 → 能区分解释的主张与研究动作 → 若成立会改变哪种理解、训练、制作或评价。定位用于辨认已有贡献和调整增量，不自动关闭方向。当前状态与实际研究取舍见整体报告；本图不保留旧的主轴、投资顺序或执行队列。

<a id="source-status"></a>
## 8. 来源身份与阅读范围（2026-10-14登记）

此表保留相应日期的来源登记；后续单篇论文卡覆盖的身份/阅读更新优先于本表，不作为当前实验状态页。

**来源分类与阅读深度两维分别记录。** P0=出处/题名；P1=摘要；P2=正文相关段或代码说明；P3=正文+关键附录细读并核重要实现；P4=本地复现/重算。原始整理时“所有来源非P4／所有训练0”已过期：PCSP、agent-sandbox、LIGHT和MeltingPot已有本地执行，不能据此称复现所有论文主表。最新见 [进度记录](../mine-a-persona-strategy/PROJECT_PROGRESS_REPORT_2026-10-16.md)。安全／经济邻接工作仍按下表范围解释。

| 来源（直接链接） | 论文身份/与游戏 NPC 关联 | 本轮阅读深度与证据边界 |
|---|---|---|
| [Tricking LLM-Based NPCs into Spilling Secrets](https://arxiv.org/html/2508.19288v1) | ProvSec 2025；**直接游戏 NPC 安全** | P2：ar5iv/HTML方法/30样本/判分/结论；非全套统计复算 |
| [Empowering MMO Economic Simulation](https://arxiv.org/html/2506.04699v1) | **KDD 2025 正式论文，直接游戏世界经济** | P2+：正文方法、5组实验、结论、附录结构；当时未下载；后续有限Bargain源码范围见MMOAgent论文卡 |
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

### 来源核查带来的认识修正
1. NPC**直接**安全并非空白：ProvSec2025已在本地模型单NPC秘密任务测攻击，较小实验且标注有构念疑问；“攻击NPC”作为标签本身不能形成 novelty。
2. 游戏**直接**经济已有KDD2025，真实结构包含资源、拍卖、P2P、货币、升级和规划；且 AIIDE2008已经讨论NPC交易和抗剥削。非游戏 AgentBazaar 又已系统研究 Sybil/价格危机，不能称“首次多Agent交易被攻击”。
3. “长期人格漂移”已有COLING2025与ACL2026角色研究；要找到 game-specific 的新科学认识，需在真实角色经历/状态、允许剧情变迁、玩家行为后果上辨明现有理解边界，而非更长对话分类器。

### 尚未完成的阅读与复现
KDD完整环境/玩家数据许可及可运行性未核（有限Bargain源码核读不等于完整复现）；ProvSec原30条数据与更多角色未确认；AIIDE侦探完整方法与数据未查；mineamongus实际Docker与本地替换未运行。NeurIPS2026身份仍须逐篇核验，不能把题名索引当全文已读。安全／经济攻防实测仍0；矿区A训练与原生行动实测已有结果，分别记录。
