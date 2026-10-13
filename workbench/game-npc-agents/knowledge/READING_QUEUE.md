# 深读与基线审计的动态队列（2026-10-14；按认知缺口，不按日期/配额）

**2026-10-14 用户已选择矿区 A 先驻留；本页保留全域历史阅读队列，但 A 当前更高优先级以 [persona-behavior/RELATED_WORK.md](persona-behavior/RELATED_WORK.md) 和 [LOCAL_AGENT_START](../LOCAL_AGENT_START.md) 为准。其余安全/经济/具身不能认作关闭。**

**不锁定永久论文结论。** 持续读近期 NeurIPS/ICLR/ICML/ACL、KDD/CHI/AIIDE/CoG 中直接研究游戏NPC的论文，并区分近邻通用 agent / safety / market；一般 arXiv 需评估质量和源码。不能只是计数泛读。

## 目前能推动重要认识的阅读路线
**安全与实际世界后果：**
- ProvSec2025 Shiomi：数据是否公开？复核30提示、人手判定和泄露真值；查更自然多角色游戏任务。进一步读 AgentDojo/ASB 的攻击来源、身份权限、utility–safety 正负控制，再比较游戏剧情合法披露/世界状态执行如何不同。
- AIIDE2026 Structured Knowledge Trees：完整原文、玩家评价、预防信息披露对可玩性的损失及任何公开实现。COLING2025 RoleBreak 与ACL2026 Dynamic Persona 研究长程身份更新，关注“玩家劝说/剧情演变”不该一律禁止。
- MineAmongUs (ECCV/COLM workshop)：分开游戏**授权的谎言**与安全攻击；读 ARIA 各 harness模块和 judge 人工校准，检查本地全链路与高8-agent调用成本。

**经济系统与恶意社会行为：**
- KDD2025 MMOAgent：已读 HTML 原文正文/附录，下一步核 Zenodo 代码、角色 profiles来源、经济规则与模拟输入；复算作者表前明确 GPT-3.5/GPT-4 换本地模型不叫原论文复现。
- AIIDE2008 EVE 交易论文：理解机制、历史资产与已有抗交易剥削方法，避免“首次NPC经济RL”旧瓶新酒。
- AgentBazaar/TruthMarketTwin/market mechanism：读模型、prompt、状态、Sybil与身份、制度干预、市场总效益/客户福利，比较与游戏内生产/进度/剧情价格机制的距离。已有作者实现支持 vLLM，但本地版本/吞吐仍未跑。
- 在真实引擎前先确认社区认可的交易数据/机制/许可，不能因找不到数据就凭几十个随机商品造论文。

**保持其它 Game NPC 分支同步：**
- 角色训练/策略：EA2026、PCSP独立行为评估、UBCL/MultiGAIL；认真读训练信号如何定义，不锁训练。
- RPG/关系：LIGHT/Dragon、KNUDGE、CDT、Generative Agents与玩家评价；比较长程角色成长。
- 多模态/实时：KRAFTON、ReactiveGWM、WorldMind、语音伙伴；安全攻击也可能跨音频/视觉，但不能默认需要训视频大模型。

## 决策动作
每次论文卡必须写作者**真实**实验单位（NPC/player, 主动防御还是游戏规则允许）、公开数据与代码状态、场景/样本、正确强对照、真实成本、最强未排除解释，以及它的 idea 为什么重要。该论文如果只提供摘要/README，直接标 P1/P2。
当某条分支有强可执行 substrate、真实失败/成功和高信息量研究动作时，才写实验卡。此处阅读优先级**不是“下周必须做”计划**，不能沉溺机械读论文列表而忽视实际系统。
