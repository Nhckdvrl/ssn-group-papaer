# CoopEval: Benchmarking Cooperation-Sustaining Mechanisms and LLM Agents in Social Dilemmas（ICML 2026 Main）

证据：正文＋关键附录＋定向作者源码，未运行。接收身份来自[PMLR正式页](https://proceedings.mlr.press/v306/tewolde26a.html)，306:120222–120287；未核 oral/poster。实际读[arXiv v2](https://arxiv.org/html/2604.15267) §2–3、§4 theorem及边界（未独立验证全部证明）、§5–7/Table1–2，Appendix B/C、E的分游戏表、N.1–N.3完整输出/游戏/机制 prompts；G的reasoning分类协议及J/K/L定位和正文解释，未逐图数字化全部附录结果。

1. **论文形态与压力：** 理论支持的多智能体 benchmark。研究怎样让只追求自身收益的异质 LLM 仍能持续合作，而非只依赖善良人物提示。四类机制为重复、声誉、中介和合同，基本困境为囚徒、旅行者、信任及三人公共物品；主论文是4种困境，不能从仓库另有 Stag Hunt/Matching Pennies 就写成主表6困境。
2. **Idea 来源（DOCUMENTED）：** 从合作理论选择能让合作在均衡成立的机制，系统比较理论上都能支持合作的机制为何实测相差很大。**RECONSTRUCTED：** 重点由“agent愿不愿合作”转向“何种互动制度使合作符合其自身激励”，是可继承的高观点。
3. **序贯性与环境事实：** 基本局为同时选择的有限矩阵博弈；机制加入历史、重复遇到同一伙伴/换伙伴，或提案→投票→接受/委托→选择，形成序贯互动。不是全单步、纯自述。收益由联合动作及机制程序结算；没有库存、移动、装备或持续消耗资源的原生动作前提。§7再提扩展到sequential social dilemmas，应理解为拓展底层困境，不抹掉已有机制层序贯性。
4. **人物与自身目标：** §5及Appendix N统一要求最大化本人总点数，点数假定涵盖全部关心事项。没有实验操纵性格/角色动机；不同 LLM 和 reasoning 配置不是人格干预。合同全员接受后实行条件支付，中介可代选择；与一个口头承诺由角色以后自愿行动兑现不同。
5. **数据与评价：** 六模型配置全cross-play、每组合3次，共每模型8,586次决策；主设历史k=3、继续概率δ=.8，实际固定15轮并按折扣估值。Table2把全缺陷收益定0、全合作定1，均匀群体平均点数依次约 .072（无机制）、.587（重复）、.695（中介）、.801（合同）；这些是归一收益，不能称相同比例的合作成功率。另有1,000步复制子动力学后的fitness与deviation ranking；这是基于实测收益的群体重加权，不是训练LLM。reasoning分类使用GPT-5.2 judge，主收益不依赖语义judge。
6. **关键比较与负例：** §6/RQ5比较固定伙伴与换伙伴，声誉收益显著低于重复；RQ6/Appendix K/L分别分析提案质量、被投票/接受、实际委托/行动，不能把“同意协议”当执行。Theorem1只保证合作均衡可存在，普遍背叛仍可能是均衡；实际异质模型间的行为决定结果。
7. **作者代码事实：** [仓库](https://github.com/Xiao215/CoopEval)，读取pin `8559e858b5cc33e0a29ac592c0b21eab007feb57`。`games/base.py`的`_collect_actions/_choose_from_mix_strategy`将模型输出概率分布采成动作；`mechanisms/repetition.py::_play_matchup`逐轮回填实际历史；`contracting.py::_play_matchup/_apply_contract/compute_contract_adjustments`在全员签后给已发生动作加减守恒支付。另读`agents/agent_manager.py`的调用与CoT/直接输出类。无游戏安装、API调用或复现；不将其云端配置复制进本地研究链。
8. **与近邻距离及整体启发：** GAIA围绕冲突对话目标优化说服；PANDA测人物如何改变游戏探索/分数；Dragon将话语与行为接目标；PUBG/FACUL接可靠技能；CoopEval明确研究异质主体的激励和持续合作。我们可在这些共同起点上研究NPC人物、自身作者动机、玩家行动和物理前提如何共同形成实际选择与后果，不要求每个组件未被做过。
9. **对本项目：** 应借鉴“是否合作、承诺是否兑现、双方后来处境怎样、结果是否依伙伴行为”联合测量，而非把Give或原子任务率单独视为好坏。E80的goal-ever、实际Give/自行取得及最终持有/消费分列正有意义；它们不是已知完整效用，也不足以单独宣称长期稳定合作。无需为了对齐本文而改世界加手写支付、合同或群体进化；先从原有自然互动解释角色选择如何随真实履约与状态变化更新。

源码只读缓存沿用`/home/xiang/.cache/game-npc-research/sources/progress-selection-2026-10-16/coopeval_*.py`。SHA256：base `6951f7e643b8f1b54f1753747c9d5b74abd90ecf181cf1ef4dcce1cda51b2a9d`；repetition `fe57b800ee4546d9b7d74e49a714b6195c662db070a517a468dadeb0cb39cb6c`；contracting `1bd54479c74fe5fa814686e48a26aac3fbaa1b5def5af757d4ae7ce6b1c1d3e5`；agent_manager `e3ec36d7e078e1c770c5c441041ee0fdf53d3acdd67ab116f088aad12d23ee16`。
