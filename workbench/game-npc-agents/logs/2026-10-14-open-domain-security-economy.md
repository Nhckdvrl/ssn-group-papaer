# 2026-10-14｜重新打开游戏 NPC Agent 的整体研究空间

## 用户决策
用户明确反馈“刚刚方向太窄/没意义”，要求彻底清理两次收缩，以及正式考虑 NPC 安全、玩家/其他NPC攻击、人格漂移、游戏内 multi-agent 经济和制度攻击。此决定改变**研究范围/实验优先级**，不构成任何一个假说被实验否定，亦未授权改其它 ACTIVE 项目。

## 阅读与检索的真实范围
- 完整对照 [ProvSec2025 NPC Secrets](https://arxiv.org/html/2508.19288v1) 的世界/模型/30条单轮输入/3次泄露与标注范围；不能外推为一般NPC防御失败。
- 阅读 [KDD2025 MMO simulation](https://arxiv.org/html/2506.04699v1) 的问题、结构化动作、记忆/反馈、baseline、profile 与系统级 30agents×200步价格/供需实验、局限和附录；发现源码Zenodo入口，**未下载/编译**。发现原作者常用GPT-3.5/GPT-4并非零付费API复现。
- 查 [AIIDE2008 EVE virtual trade](https://ojs.aaai.org/index.php/AIIDE/article/view/18680)、[CHI2024 Game Lies](https://www.robertxiao.ca/research/lies-deceit-and-hallucinations/)、[RoleBreak COLING2025](https://aclanthology.org/2025.coling-main.494/)、[ACL2026 dynamic persona](https://aclanthology.org/2026.acl-long.1336/)、[AIIDE2026 SKT](https://arxiv.org/abs/2609.23043) 的正式身份/摘要；没有虚构深读所有附录。
- 查 [NeurIPS2024 AgentDojo](https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html)、[ICLR2025 ASB](https://proceedings.iclr.cc/paper_files/paper/2025/hash/5750f91d8fb9d5c02bd8ad2c3b44456b-Abstract-Conference.html)、[TruthMarketTwin](https://arxiv.org/abs/2605.10059)、[Agent Bazaar](https://sethkarten.ai/papers/agent-bazaar.html) 的攻防及系统性市场前史。
- 阅读 [AI-native games survey](https://arxiv.org/html/2607.00527v2) 的taxonomy/挑战与安全相关章节；检查实际公开仓库 README：[AI-Bazaar](https://github.com/sethkarten/AI-Bazaar)支持本地vLLM/Ollama、[MineAmongUs](https://github.com/JunseoKim0103/Lies-We-Can-See)是workshop/8-agent游戏欺骗、[AgentSociety2](https://github.com/tsinghua-fib-lab/agentsociety)仍默认云API设置、[Gigax](https://github.com/GigaxGames/gigax)有本地GGUF人物对话。
- NeurIPS2026 Downloads只用于标题发现：track和论文需要逐篇核实，不能用title列表声称已精读。

## 发生的真实研究认知变化
以前把角色行为训练/目标保持当作全领域的问题，漏掉两个独立科学实体：(1)游戏中的授权/秘密/身份安全；(2)能结算的虚拟经济里NPC间交互导致的市场制度风险。现有论文表明它们**已受学术关心**，但目前各来源跨 NPC对话、真实游戏经济和非游戏安全基准，不能直接拼在一起宣布新领域。
进一步确认：有意谎言可能是正常剧情；合理关系演变不叫人格漂移；交易里的竞争/价格浮动不是系统漏洞。数据与判断必须遵守这些边界。
研究空间恢复为8板块完整领域图，原有知识库/安全/经济索引明确衔接；旧 E00/E02–E05 记为未执行被替代，而不是失败实验；E01仍仅CPU源码检查。

## 实验与授权状态
**新模型调用0、GPUh0、没有真实攻击/经济/玩家实验、没有新 C## 科学发现。** 未进入用户服务器、没有将私有资产移入Git、没有在在线游戏施加攻击。下一轮研究从已读论文的真实数据/运行环境与高信息量自然压力出发，而非再次写死一个论文故事。
