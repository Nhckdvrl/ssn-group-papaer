# 2025–2026 游戏 NPC 原生研究：论文与实际代码调查

本页以**游戏内非玩家角色的学习、制作与行动**为边界。阅读截至2026-10-13。记号：F=论文 HTML 正文含方法/结果/局限读过；A=作者摘要；R=开源 repo README/目录/指定源码读过；X=本地可复现实测（**本轮 X=0**）。学术状态仅在正式会场/期刊页面核实时写已发表；arXiv 只写预印本。

## 1. Electronic Arts｜Augmenting Game AI with Deep Reinforcement Learning（2026 CoG vision / arXiv 2606.20210）【F】
全文 https://arxiv.org/html/2606.20210v1 。这是本领域最重要的**需求锚点**之一，而非我们得出结论的来源。
- 原生对象：EA SPORTS FC25 守门员定位（原生 FSM）和 Battlefield6 地面士兵移动（BT/GOAP），都是**玩家实际遇到的 NPC**，不以 agent 通关分数为唯一成功。
- 七项要求：Short Training Time、Controllability、Modularity、Maintainability、Bug Detection and Fixing、Authenticity、Runtime Inference Constraints。
- FC25：SAC 利用离线数据/高 update-to-data ratio/网络复位/场景训练，将作者报告的初始约4天缩到约12小时；推理总链要求 <200µs，约30万参数策略作者测得170µs，强调不需要大模型每帧执行。定向行为修改仍可能灾难性遗忘。
- BF6：局部 occupancy map vs raycast，作者报告局部感知构建14µs vs27µs；更快的引擎状态观察而非模型前向才是瓶颈。PPO 约2h训练，headless 240并行 agent，但这是**EA专有引擎**，不可继承其吞吐。
- 论文所提出的开放科学压力：少量设计师反馈怎么表达品质；训练更快且不随补丁遗忘；固定BT结构如何联合学习与安全切换；如何验证真实行为；怎么低成本从引擎抽取有用信息。
- **Idea 来源重建（非作者过程史）：** 从实际游戏 FSM/BT 的局部缺点出发，将设计者迭代/部署成本写成训练/感知/控制约束，再选择特定 SAC/PPO 与局部替换，绝不追求 end-to-end 大而全模型。
- **可继承**：论文评价维度与对照思维；**不能继承**：源代码/游戏 assets/吞吐或人类主观评测为我们的复现实证；vision 本身不证明某个新算法可行。

## 2. Human-Like Bots for Tactical Shooters Using Compute-Efficient Sensors【A】
IEEE Transactions on Games 17(4) 2025；https://ieeexplore.ieee.org/document/11104932/ ，预印本 https://arxiv.org/abs/2501.00078 。
- 原生对象：VALORANT-like 2v2 战术射击中的 AI bots，训练基于真实人类动作示范的模仿学习，采用 pixel-free raycast 等廉价传感。
- **研究价值：** 如何在CPU/游戏硬件预算内获取足够策略信号、如何让动作更像人而不是更强；作者包含 human eval。没有发现公开完整代码/原始人类轨迹可直接用，不能把论文方法当现成可跑底座。
- 不能宣称首次模仿玩家/首次低成本观察架构。

## 3. PCSP｜One Policy, Infinite NPCs【F+R】
arXiv 2605.23652，https://arxiv.org/html/2605.23652v1 ；源码 https://github.com/yoosunghong/pcsp ，本轮读 research/README 与独立行为评估说明以及 training/env/scripts/data 目录。**未确认 NeurIPS/ICML/ICLR 接收**。
- 原生对象：life-sim NPC，多角色自然语言 persona 向量一次编码，共享 PPO 策略实际选择行为，Mini-Inzoi/PettingZoo、Melting Pot、UE5 分层评估。
- 方法：冻结 Qwen3-Embedding-0.6B，人格低秩投影+FiLM/concat 条件化共享政策，PPO + trajectory/persona InfoNCE + KL diversity；不只是聊天评价。
- **必须分开指标的关键事实：** 作者研究目录 docs/evaluations/independent-behavior.md 报内部对齐损失减少后 retrieval 大幅下降，但独立 action-only BigFive probe: full 0.482、no consistency 0.511；action+state 0.556 vs0.558。对外“角色表现更好”不能仅从内部检索推出，且 BigFive probe 并非完整角色行为的金标准。
- 作者自己的论文已做丰富条件、Melting Pot 三场景、UE部署、多种子、留出人格等；不允许因只读摘要就假设它没有真人/跨域检验。
- **可复现性：** MIT 源码；research/src/env/mini_inzoi_v3.py、research/src/training/pcsp_trainer.py、scripts/run_pcsp_v3.py、行为独立测试、personas train/test JSON 已公开。没有实际安装/重训练/测吞吐；支持 PCSP 的特殊本地 environment，不能代表所有 RPG/combat NPC。
- **Idea 来源重建：** 从逐 NPC 手工编树/逐角色训练/每步 LLM 都贵的产业压力，转成共享条件政策。对当前新研究：最值得复现其**独立行为解释和训练可编辑性**，而不是在原 loss 上盲目再加 term。

## 4. Game persona/action learning ownership map
- *Generating Personas for Games with Multimodal Adversarial Imitation Learning* (EA, IEEE CoG 2023): https://arxiv.org/abs/2308.07598 【A】。多个 discriminator 从不同专家风格示范学习，单政策通过辅助输入切换/混合风格，已占“多示范、可控人格行动政策”主张。其出发点偏自动 playtesting，不能直接当人们喜欢的 NPC。
- *UBCL: A Reinforcement Learning Framework for Controllable and Diverse Player Behaviors* (IEEE Trans. Games 2026): https://arxiv.org/abs/2512.10835 【A】；连续行为目标向量 + 行为统计距离变化作为 PPO reward，在 Unity 多人游戏共享政策。**其对象是 player-like bots，适用于 NPC 扮演玩家位置时，不覆盖复杂对话社会 NPC**。当前未核实完整开放源码。
- *Direct Behavior Specification* (ICML 2022): https://proceedings.mlr.press/v162/roy22a.html 【之前有部分读】。设计者行为约束与策略优化早已有研究，不能把“作者直接控制学到的 NPC”冒领为2026新题。
- *Events as Triggers for Behavioral Diversity in MARL* (NeurIPS 2026): https://www.proroklab.org/publications/events-as-triggers-neurips2026/ 【A、作者会议身份】。事件触发 hypernetwork 产生共享政策 LoRA、解耦身份和事件中的角色行为。VMAS，不是发布的游戏NPC本身；事件触发角色重分工方法已有直接近邻。

## 5. LLM＋游戏策略整合（和单纯 LLM Roleplay 不同）
- PUBG Ally（KRAFTON/NVIDIA 工程技术说明 2026）：https://developer.nvidia.com/blog/how-krafton-built-pubg-ally-a-co-playable-character-powered-by-nvidia-ace/ 【R / 产品研发说明】。官方把它称 Co-Playable Character (CPC) 以区别传统 NPC；我们仅视为游戏内 AI 伙伴邻接应用。2B 本地小模型负责高层语音/工具/协作，BT 在 tick 级处理战斗/移动，厂商蒸馏游戏知识并用玩家反馈校验。内部训练数据与引擎不可公开复现。
- *LLM-Guided Reinforcement Learning for Adaptive NPC Behavior in Multi-Agent Combat Games* (arXiv 2609.02931) https://arxiv.org/html/2609.02931v1 【正文部分】。Unity 五 NPC 共享 PPO，本地 Mistral7B 每5秒选战术 tag；文中报告不同对手收益差异但83.8%的选择为Surround。**审计注意：** baseline 与LLM条件的训练时风格信号/奖励可能不等价，复现先核对两政策训练与评估条件，再做相同 conditioned-policy 配对替换 selector；不是把小型 preprint 的胜率作为顶会强共识。
- ccb/agent-sandbox: https://github.com/ccb/agent-sandbox 【R】。2026 UPenn group text-adventure/Godot 游戏 NPC，有 world-state 前提/效果、NPC 回合、ReAct/Reflect、LLM_BASE_URL；文档有不同开发阶段残留、默认 API key，启动必须设置本地 endpoint /mock，避免自动外联。研究平台，**不是已接收顶会方法 baseline**。
- LIGHT/Dragon (EMNLP-IJCNLP2019/NAACL2021) 见旧知识库：具有角色自身动机、可执行 action，不应因其年代老就忽视；但现实 code/data 恢复成本和规模验证仍未完成。

## 6. 视频生成式NPC（单列，不作为当前行为控制的默认基线）
- *ReactiveGWM v2* (2026 arXiv): https://github.com/INV-WZQ/ReactiveGWM 【R】。2026-09-29 发布含 HNM/SF3 两种游戏的 v2 训练/推理、预训练权重、数据；用 mask 绑定控制角色、world model 生成 NPC 反应。Wan2.2 5B backbone、约20k optimizer updates、默认8卡训练，重视频 IO——研究价值高，但当前弱互联/弱盘不适合主线全面训练。
- *WorldMind* (2026 arXiv): https://github.com/TeaWhiteBro/WorldMind 【R】。README 截至本轮明确 code/weights being prepared；不可声称是复现实验底座。

## 7. 领域邻接论文：可以迁移方法，不能借其结论充当游戏NPC验证
- *CRPO* (ICML2026) https://proceedings.mlr.press/v306/tang26c.html 【A】；训练角色语言和问题推理的平衡，不等于游戏内 action-policy training。
- *Persona-Pruner* (ICML2026) https://proceedings.mlr.press/v306/kim26br.html 【A+R】；剪 persona-specific LLM FFN，不等于一个策略支持上千 NPC 的执行。官方完整数据 rewrite 配方包含 Llama70B，默认评分例使用 GPT-4o-mini；不能把快速两条 smoke 当零 API 复现。
- General game-playing agents、NitroGen、TALES 可以供 policy 初始化/游戏接口借鉴；评测的通关率**不自动证明**角色行为可信、设计师可编辑或真实玩家体验好。

## 研究审查结论
直接游戏 NPC 研究中最有价值的主题是**设计/训练成本下的行为生成、对真实局势的可控适应、策略快速修复、部署与评估**。同样重要的是不要把 player-style bot 与生活模拟对话角色完全等同。各科学 claim 必须绑定具体 NPC 类型/游戏机制/玩家反馈；强主会多集中通用 RL/多智能体机制，游戏专门会议和行业论文提供最直接的真实问题，并非低级应忽视。
