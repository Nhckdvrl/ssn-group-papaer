# 各 Game NPC 子领域的基线/数据与本地资产地图（2026-10-14）

本页替代旧“LIGHT为唯一首选”及后来“PCSP为唯一首选”。**选择substrate要由科学问题决定，而不是一个系统决定科研题目。** 当前仅核公开论文/README/指定源码、没有用户GPU、未宣称完整基线复现。

| 科学分支 | 最合适的原生/邻接资产 | 真正可观察的单位 | 已核验与未通过的 gate |
|---|---|---|---|
| NPC 安全/泄密/角色攻击 | [Gigax](https://github.com/GigaxGames/gigax)、[Shiomi ProvSec](https://arxiv.org/html/2508.19288v1)、[LIGHT](https://github.com/facebookresearch/LIGHT)、[agent-sandbox](https://github.com/ccb/agent-sandbox) | 角色秘密/剧情许可、对话和引擎动作、消息来源 | Gigax有本地GGUF模型与NPC stepper；Shiomi只有单NPC30次单轮示范，不是强长期基准；LIGHT迁移有依赖债，sandbox不等于顶会方法 |
| 动态人格/社会记忆 | LIGHT/Dragon、[PCSP research](https://github.com/yoosunghong/pcsp/tree/main/research)、[MineAmongUs](https://github.com/JunseoKim0103/Lies-We-Can-See) | 行动/关系/剧情状态随时间变更，角色真实动机 | PCSP独立行为probe已开源；MineAmongUs Docker+游戏日志开源，但8agent回合/默认API及Minecraft server成本未测 |
| NPC经济及群体攻防 | [KDD2025 MMOAgent代码归档](https://doi.org/10.5281/zenodo.15526912)、[AI-Bazaar](https://github.com/sethkarten/AI-Bazaar)、[BAZAAR](https://github.com/lechmazur/bazaar) | 商品/金币/库存/生产/交易/声誉/价格/群体福利 | KDD项目论文有Zenodo链接**归档未下载**且原实验GPT-3.5/GPT-4；AI-Bazaar GitHub README明确支持Ollama/vLLM但没有实际跑；BAZAAR是非游戏市场bench，只有机制可迁移 |
| NPC行为训练 | PCSP、[EA2026 paper](https://arxiv.org/html/2606.20210v1)、UBCL/MultiGAIL | 动作policy/设计控制/分角色行为 | PCSP开源可试；EA商用引擎资产未开放不能称可复现 |
| NPC玩家伙伴社会互动 | [ccb sandbox](https://github.com/ccb/agent-sandbox)、LIGHT、Collab-Overcooked、KRAFTON架构 | 玩家指令、角色互动、合法世界行动 | ccb README给本地兼容endpoint (LLM_BASE_URL)，实际启用逻辑需检查；Collab旧Python/MPI，本地规则和vLLM可替换 |
| NPC多模态/具身安全 | [Lies We Can See](https://github.com/JunseoKim0103/Lies-We-Can-See)、[ReactiveGWM v2](https://github.com/INV-WZQ/ReactiveGWM) | 实体视觉/非语言行动、社交欺骗、视频环境 | MineAmongUs公开Docker/日志/标注，标注用LLM judge；ReactiveGWM 2026-09-29 v2开放权重和代码，默认8 GPU/20k优化步与视频IO不适合无规划全量复训 |
| 通用 Agent 攻防对照 | [AgentDojo](https://github.com/ethz-spylab/agentdojo)、[ASB](https://github.com/agiresearch/ASB) | 信任边界、攻击接口、utility-security | NeurIPS2024/ICLR2025强近邻，**不是直接NPC游戏任务**；先研究其严谨控制再迁移 |

## 条件性 substrate 选择，而不是单线 roadmap
- 如研究**秘密/人物安全**：需要作者设定披露规则与合法剧情任务，可先从开放文本/RPG场景确认攻击与权限，同时参考ProvSec已发布最小任务和AIIDE侦探工作；真实游戏引擎接入是关键资格之一。
- 如研究**NPC经济/多Agent攻击**：先完整核KDD2025模拟器/资产和 AI-Bazaar 本地工具链接，确认 CPU 可结算账本、agent策略和角色来源；一个精简交易模拟可以用于测量校准，但最终不能只依赖新自造的小商品市场宣称MMO普遍规律。
- 如研究**训练与长期人格**：PCSP、LIGHT和其它公开生活模拟各有能力边界；根据角色动作/记忆、伙伴信息与评估有效性选择，不人为统一各类NPC的指标。
- 如研究**具身攻防或非语言欺骗**：MineAmongUs有开放视觉/动作环境，但自带非语言欺骗（游戏允许的胜利策略），要与真正违反世界作者规则的安全攻击明确分开；GPU/CPU/IO本地测速后才可开始大规模。
- **NeurIPS2026/最新arXiv**：只有当单篇正式会场、论文版本、代码和研究对象都核验后才升级“强已发表baseline”，不能拿官方标题表当精读。

## 统一 gate（执行前）
上游git SHA/数据license/模型revision；是否可局部离线运行；NPC主体、玩家/伙伴、审计/标注、环境rule、世界owner；强baseline、自然场景、真实后果/合法胜利条件；API全链预检、本地单节点CPU/GPUh/IO/延迟；数据train/dev/test split与人工校验。**“源码能下载”≠“复现论文”≠“可以回答我们问题”。**
