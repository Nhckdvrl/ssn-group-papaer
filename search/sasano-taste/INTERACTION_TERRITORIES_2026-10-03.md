# 交互 Agent / 游戏队友：可驻留领域与资产核查（2026-10-03）

**结论：保留“共同任务中的沟通与修复”和“与陌生、变化伙伴的配合”两个相邻领域，优先合并理解为「一起做事的 Agent」。** 它们以共同完成任务为对象，有清楚的失败现场、可执行强基线、客观结果和公开主会谱系；不要求先训练一个大模型，也不要求做传统语言学课题。两者先分开列便于选择建设入口，不提议同时开两条 workbench。

本轮推进 territory 搜索，不注册结果型主张；无 GPU 实验、无 workbench 新建、无状态变更。已有 ACTIVE 名额保持原样。来源卡见 [定向精读](../../library/themes/game-npc-social/INTERACTION_PAPER_CARDS_2026-10-03.md)。Sasano 品味判断依据仓库已归纳规则；本子任务未独立重读 Slack，不把“他可能喜欢”当他本人表态。

## 0. 对齐与选择尺度

- 自然问题：一起完成任务时，对方什么时候该说、该问、该改动作；换一个队友后哪些合作经验仍有用。玩家、NPC 与工作助手都真实面对这些问题。
- 结果可以改善系统，也可以改变对协作的理解；仅“多 agent 比单 agent 差一点”“小模型涨若干分”不作为终点。
- 先复现强 baseline，再铺**有区分力的条件**：伙伴、任务依赖、信息可见性、交互轮次、动作后果。最终论文可小训练，但搜索/初期测量冻结模型。
- 十几张 A100 / 8 张 PRO6000 / 16 张 H20 的优势是独立配对、seed、任务与消融吞吐；不是一起训练一个联合大 team。checkpoint 固定在节点，轻量状态/JSONL 本地存，不上传视频流。
- “training-free 可开始”不是“没有基础能力门槛”：7B 若连单人任务都做不了，失败归不到协作上；14B/32B 和已训练非 LLM 策略应该进阳性对照。

## 1. 热度与检索账

本地执行：

```bash
python3 tools/venue_corpus/query.py density 'common ground|clarification|partner adap|ad.hoc teamwork|Hanabi|Overcooked' --show 10
python3 tools/venue_corpus/query.py shapes 'common ground|clarification|partner adap|ad.hoc teamwork|Hanabi|Overcooked'
python3 tools/venue_corpus/query.py nearest 'language agents collaboration shared common ground clarification repair partner adaptation repeated interaction communication games' -k 18
```

| 主会切片 | NeurIPS24 | ICLR25 | ICML25 | NAACL25 | ACL25 | EMNLP25 | NeurIPS25 | ICLR26 | ICML26 | ACL26 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 上述宽正则接收数 | 9 | 5 | 5 | 3 | 7 | 6 | 8 | 8 | 18 | 11 |

ICLR25 切片 5/14≈36%，全会≈32%；ICLR26 切片 8/33≈24%，全会≈27%。**这是两个领域的合并粗筛，不是精确领域大小**；包含少量非目标命中，也漏掉不用这些词的论文。相较 generic MAS 是较具体的中等邻域；不能据此宣称完全冷门或更易接收。

`shapes` 中有评分的 accepted n=13：method 85%、finding 31%、benchmark 85%、failure 31%；rejected n=18：89%、22%、50%、44%。词频标签重叠、样本小，说明方法与可执行测量常组合出现，不能作为拒稿因果解释。

最新入口实际读取 [游戏 agent awesome](https://github.com/git-disl/awesome-LLM-game-agent-papers)、[AI for Games](https://github.com/Eurekaleo/awesome-ai-for-games)、[DailyArXiv](https://github.com/zachysun/DailyArXiv)。按去重 arXiv ID 计，三者本次快照的 2026 条目分别 127 / 163 / 395。前者全停在 6 月，不适合单独声称覆盖近期；AI for Games 的 7/8/9/10 月 ID 分别 8/20/70/8，混有新综述集中补录；Daily 是跨类别近期窗口，9 月 ID 302。**这些不是领域真实增长率**；本轮新近邻继续回 arXiv/正式页面核实。

[NeurIPS2026 官方 Downloads](https://neurips.cc/Downloads/2026) 已公开，仓库“名单尚未公开”是旧状态。root 获取的 9,230 条是 event 列表，不等于 main 接收总数；本轮标题筛伙伴相关 5 条，其中 1 条量化误命中；共同沟通相关标题极少不代表全文邻域小。下文把尚未核准分轨的条目明示为目录入口。

## 2. Territory A：共同任务中的沟通、澄清与修复

**外行版本：两个人都大致会做这件事，为什么一起做时还是说不清、接不上、修不好？** 研究对象是一段有目标、有状态、有行动后果的协作过程；游戏只是可控窗口。更强模型出现后，沟通成本、伙伴差异、信息不对称和纠错仍存在，科学对象不会随一个 benchmark 被刷完而消失。

### 谱系卡

1. 共同知识 / 共同完成行动 → PhotoBook / repeated reference games → ACL2026 LVLMs-and-Humans 的 2×2 角色实验：从静态理解转为互动达成理解。
2. grounding gaps → ACL2025 RIFTS 自然修复日志 → ICML2026 DRIFT-BENCH 可执行输入故障 → 2026-09 Drift-Bench++ 目标变化/耐心：从“会不会问”到“问过是否真的解决”。
3. Overcooked-AI / ProAgent → EMNLP2025 Collab-Overcooked 的必要协作与过程读数 → ICML2026 CollabBench 的多类伙伴：任务成功要拆成协作发生在哪。
4. 人类重复指称 → Hua–Artzi 的现成模型适应测量 → ACL2026 Success+Cost：成功与沟通成本联合训练，本地中模型也能接触。
5. uncertainty threshold → ACL2026 Value of Information / ICML2026 Information Gain clarification → NeurIPS2026 目录中的 Ask Early, Ask Late, Ask Right：澄清的效用和时机已有强近邻，不是空白。

### 立足点卡

**首个可执行入口：Collab-Overcooked 的原配置与本地 Qwen2.5-14B/32B。** README 推荐 vLLM，源码实际有 localhost API 参数，30 任务与参考轨迹在仓库，动作合法性/任务完成可自动判。先做原文旧模型复现，之后再加新模型；不以 API 模型的最好数字作为必须重复购买的前置条件。

**第二个独立窗口：小型重复 reference game / PhotoBook 衍生环境。** 现成 COCO/tangram 与公开人类对话提供自然数据；但 Success+Cost trained adapters 本轮未核实发布，篮子任务原强 baseline 为 proprietary model，不能说“最终强基线已完全本地可复现”。先可核原始任务与开源基础模型能力，不做十万次闭源 judge。

轻量环境 CPU、模型单卡/单节点 serving；总时延由交互轮数与 token 决定，远非“training-free=瞬间”。一期只取能鉴别单人执行/沟通/共同状态的代表任务。memory、带结构的状态、简单规则、单句指令都要作为低成本对照，避免把默认策略当能力。

### 压力清单（每条是驻留入口，不是预测发现）

| 压力 | 出处与已知边界 | 可以长出的证据形态 |
|---|---|---|
| 成功终局掩盖谁承担了沟通/修复负担 | [RIFTS](https://aclanthology.org/2025.acl-long.1016/)、[LVLMs and Humans](https://aclanthology.org/2026.acl-long.410/) | 同一目标下的交叉角色测量 + 用户/伙伴负担验证 |
| “协作”任务可能单人可完成，或者过程指标只奖励参考轨迹 | [Collab-Overcooked §1,3,4](https://aclanthology.org/2025.emnlp-main.249.pdf) | 依赖结构与等价有效轨迹审计；有解释力的评测协议 |
| 多问、长说、反复确认都可能耗费成本而不解决误解 | [Success+Cost](https://aclanthology.org/2026.acl-long.1946/)、[VoI](https://aclanthology.org/2026.acl-long.1987/) | 客观成功 × 成本曲线；有来源的最小控制策略 |
| 行为像理解，也可能只是重复；视觉/顺序错误与互动混在一起 | [LVLMs and Humans §5–6/Limitations](https://arxiv.org/html/2601.19792v3) | 感知、顺序、状态与互动的匹配控制；不要直接宣称 ToM 缺失 |
| 用户的表达不完备、会变目标且没有无限耐心 | [Drift-Bench++](https://arxiv.org/abs/2609.38604) | 环境结果与修复路径；强近邻已拥有该宽叙述，需真实新压力 |
| 同一澄清在不同执行时刻效用不同 | [Ask Early/Late/Right](https://arxiv.org/abs/2605.07937) | 信息干预时机 × 不可逆动作；原文有 84 variants/6,000+ runs，不能只做小规模 timing sweep |
| 沟通中的约束掉落、假信息传播与终局分数分离 | [AgentCollabBench 数据](https://huggingface.co/datasets/AgentCollabBench/AgentCollabBench) | 可执行过程完整性；但其 900 任务已覆盖多跳过程诊断 |

### 主会形态与所需证据

- **失败模式 + 最小修复：** 自然现场如“对方已纠正材料，行动仍按旧任务继续”“双方不断确认但同一共享状态不同”。这些仅是要观察的事件类型，不是本轮结果。需要原强基线真实发生、最终任务后果、平凡提示/更多算力对照、第二类任务重现；再由失败决定是否加状态/控制方法。
- **共同劳动的测量论文：** 单看模型正确率无法判断双方是否变轻松；以角色互换、伙伴固定、成功率相近条件测成本。需要真实人类语料或小型真人验证，不能让两个 LLM 的偏好评分替代全部证据。
- **机制 + 边界：** 只有语言/视觉/动作模块可干预且排除顺序、context、基础执行能力后才谈机制；不能把注意力图或口头自述当因果证据。
- 主会证据形状已经存在：RIFTS 自然语料→预测/干预；LVLMs 89 dyads 多角色设计；Success+Cost 两视觉域+小训练+人类响应速度。它们说明范围能支持主会，**不保证我们的任何局部异常就够一篇**。

### 定位风险

“澄清有用”“动态意图会出错”“LLM不擅长共同知识”“结合成功和成本训练”“多 agent过程会掉约束”都已有 owner。我们可驻留的是整个共同任务过程，具体增量须来自复现痛点；仅换模型、再造 benchmark 或复述一个概念差异有高 compression risk。

## 3. Territory B：与陌生、会变化的伙伴配合

**外行版本：一个自己很能干的 Agent，遇到不同队友时，能不能找到双方合适的分工？** 覆盖伙伴识别、在线适应、互补行动、让步/主导、伙伴变化和经验复用；不是仅研究“大小模型一起刷题”。游戏 NPC 队友是自然应用，研究对象无需绑定大型 3D 游戏或生成视频。

### 谱系卡

1. self-play → population-based zero-shot coordination（HSP/MEP）→ NeurIPS2024 ZSC-Eval：训练队友多不代表评测队友有代表性，改成可解释的伙伴池和 best-response 尺度。
2. explicit opponent / partner model → NeurIPS2025 recurrent partner modelling：有时不加专用模块也会出现伙伴表征；出现条件与分工可控性相关。
3. 固定策略池 → NeurIPS2025 Learned Latent Strategies（策略编码、聚类、在线追踪）→ ICML2026 CooT（历史条件下适应）：谁是好队友不能只用 self-play 排名。
4. ProAgent / Hypothetical Minds → 2026-08 BayesBeliefAgent：已估对伙伴仍可能执行旧动作；posterior 作为控制信号比只入 prompt 更有用，是已存在的结果。
5. 单 layout 伙伴泛化 → OGC（TMLR2025）→ NeurIPS2026 目录的 Unifying Partner and Environment Diversity / ROTATE：环境变化与伙伴变化的联合问题仍活跃。目录新论文全文/代码尚未核实，不直接当可跑基线。

### 立足点卡

**最可靠的先手：ZSC-Eval 开源策略池 + 原 Overcooked 奖励评测。** [官方仓库](https://github.com/sjtu-marl/ZSC-Eval)直接链接[预训练策略](https://huggingface.co/Leoxxxxh/ZSC-Eval-policy_pool)，提供 eval scripts、任务/伙伴配置和人类研究平台。这与旧 `multi-llm-collaboration` 需要先训练至少两个充分训练 team 的暂停原因不同：伙伴本来就存在，可先 inference cross-play。

**连接到 LLM 兴趣：** 原 ProAgent/Collab-Overcooked 的语言高层与可验证低层；但 ZSC-Eval 与 Collab-Overcooked 改动后的环境不是即插即用兼容，不能凭名字相同直接混插策略。先在各自原环境复现，只有状态、动作、reward 完全核对后才建设 adapter。

ICML2026 CooT 为较新强比较，会议版覆盖 Overcooked 与 GRF，不能只引用其旧 preprint 的 Overcooked-only规模；本轮没有确认完整 pretrained CooT checkpoint。NeurIPS2025 recurrent-paper 公开训练/分析代码但未确认权重，所以作为研究动作来源，不设为 training-free 第一入口。

### 压力清单

| 压力 | 出处与边界 | 可以长出的证据形态 |
|---|---|---|
| 自配得分和与别人合作的能力不是同一评测对象 | [ZSC-Eval](https://github.com/sjtu-marl/ZSC-Eval) | 公开多样伙伴 × 固定 ego 的 cross-play；best-response归一化 |
| 多样伙伴池仍可能遗漏部署行为 | [ZSC-Eval 的 BR-Div 设计](https://github.com/sjtu-marl/ZSC-Eval) | 伙伴覆盖/重加权/失败类型，而不是仅多采种子 |
| 推断队友很准，行动也可能没跟上 | [BayesBeliefAgent §5.3–5.5](https://arxiv.org/html/2608.18490v1) | 时间对齐行为干预；其具体 gap/control 主张已拥有 |
| 伙伴表征是否出现取决于任务中的分工控制 | [Partner Modelling Emerges](https://papers.nips.cc/paper_files/paper/2025/file/0b8e8bfc40184226888e821620b216c9-Paper-Conference.pdf) | 改任务结构、追踪表征和行动；不能只 probe 后称 ToM |
| 推断伙伴后如何切策略，难在低样本而不是最终收敛 | [CooT ICML2026](https://proceedings.mlr.press/v306/wang26ag.html)、[Latent Strategies NeurIPS2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/020973f2093a6053261da93cac30ab71-Abstract-Conference.html) | 冷启动/适应曲线、突然变化与累计 regret；先核公开checkpoint |
| 只换队友不换环境，结论可能绑定布局 | [OGC正式论文](https://openreview.net/forum?id=K2KtcMlW6j) | partner × layout 分层外推；联合变化不等于堆域数量 |
| 模拟伙伴的“人格/情感”标签未必对应实际人 | [CollabBench](https://github.com/BW297/CollabBench) | 用具体行动风格/可观察能力定义伙伴，再做有限人类效度验证 |

### 主会形态与所需证据

- **条件性发现：** 在哪些任务关系下需要识别伙伴、在哪些关系下直接稳健策略足够；已有 recurrent-paper 是范例。真正增量需要一个改变结论的条件与受控因果证据，不能简单复制到 LLM。
- **伙伴适应失败 + 轻量方法：** 从真实 cross-play 失败出发，例如重复劳动、互相等待、双方一起频繁改主意。必须证明并非低层策略坏/信息不可见/动作接口不一致；干预后改善真实 team outcome，而不仅降低自定义“协作错误率”。
- **评测协议：** 公开策略池与明确任务依赖能给可信标准；需要显示旧排行在哪些实际部署问题上失真、新协议对人/异构伙伴更有效。若只有一张 cross-play矩阵，没有改变判断的后果，证据仍不够。
- **规模不靠训大：** 多 model family、代表伙伴类型、若干任务结构、重复 trial 与置信区间都可以分发到独立节点。精确数量由先导方差与效应辨识确定，不先规定“越多越好”。

### 驻留 D1–D6 顺序（A/B择一个入口）

1. D1：固定原环境/模型/策略版本，复现一个主表子集；对单人/已知伙伴/可执行 oracle 过关，并测单episode时延、内存与tokens。
2. D2：保留环境与 evaluator，数据/模型仅记录本地资产位置；不把大量 rollout 入 git。
3. D3：逐条记录成功、不稳定和真实失败，区分语言、伙伴推断、控制、执行、接口故障；不先填入预期反常。
4. D4：A 做成功×沟通成本×角色矩阵；B 做固定ego×伙伴×任务结构矩阵。两者均先有单句指令、强基础执行与信息可得性对照。
5. D5：按下面 12 篇接收及最新强预印本逐条写定位；只有确定实际观察后才写增量。
6. D6：根据测量出现的压力做3–6个研究动作提案，交给人选；若新主张需要人类外部效度，明确补何种真人证据而不是伪装全自动完成。

## 4. 主会形态校准：12个接收范例（共同邻域，不是两套独立十篇）

| 论文 / 已核状态 | 形态、证据规模与为什么站得住 | 对我们限制 |
|---|---|---|
| [RIFTS，ACL2025 main](https://aclanthology.org/2025.acl-long.1016/) | 自然日志分类/预测/干预，1,740任务、多模型 | 非纯执行结果，标签有judge与选例偏差 |
| [Collab-Overcooked，EMNLP2025 main](https://aclanthology.org/2025.emnlp-main.249/) | 30任务/6复杂度/13模型，过程指标与人类上限 | 原最终主表数字尚未逐格复核 |
| [LVLMs and Humans，ACL2026 main](https://aclanthology.org/2026.acl-long.410/) | 89对/356对话、2×2角色、人类证据 | 不能只换模型复刻结论 |
| [Success+Cost，ACL2026 main](https://aclanthology.org/2026.acl-long.1946/) | 两视觉域、两家族、小训练消融、真人成功与时延 | checkpoint可得性仍待核 |
| [Value of Information，ACL2026 main](https://aclanthology.org/2026.acl-long.1987/) | training-free决策理论，4域、成本条件控制 | “按信息价值问问题”已拥有 |
| [DRIFT-BENCH，ICML2026](https://proceedings.mlr.press/v306/bao26e.html) | 多轮故障taxonomy与可执行环境 | 全文证据规模本轮未精读 |
| [CooT，ICML2026](https://proceedings.mlr.press/v306/wang26ag.html) | Overcooked+GRF、在线适应、真人与消融 | 不是未经训练的通用LM；终版checkpoint未核 |
| [Partner Modelling Emerges，NeurIPS2025 main](https://papers.nips.cc/paper_files/paper/2025/file/0b8e8bfc40184226888e821620b216c9-Paper-Conference.pdf) | 简单RNN、大量合作团队、表征与行为条件性分析 | 无需Foundation model竞赛，训练权重未核 |
| [Latent Strategies，NeurIPS2025 main](https://proceedings.neurips.cc/paper_files/paper/2025/hash/020973f2093a6053261da93cac30ab71-Abstract-Conference.html) | 编码策略+在线追踪、Overcooked与真人 | 不再把“适应陌生伙伴”泛称新意 |
| [ICR，NeurIPS2025 main，官方作者仓库明确](https://github.com/csu-signal/ICR) | Modified-Action MDP+伙伴干预，DeliData/Wason与Weights | 训练数据使用GPT-4o；不作我们廉价第一入口 |
| [ZSC-Eval，NeurIPS2024](https://github.com/sjtu-marl/ZSC-Eval) | 伙伴池、BR-Div/Prox、Overcooked+GRF、人评 | 公开预训练池能直接降低探索门槛 |
| [CollabBench，ICML2026，作者仓库+会议Downloads核对](https://github.com/BW297/CollabBench) | 2类协作环境、伙伴行为模拟、agentic训练 | 人格/affective evaluator仍需效度核查 |

### Near-miss（历史结果，不伪造评审理由）

本地语料给出如下评分与决定；尚未读完各条完整评审，**不推断“为什么拒”**。分数也不跨会议比较。五例并不都是2026年的最近论文，此处是可检索到的高分形态对照。

| 历史条目 | 记录 | 本轮可用信息 / 状态修正 |
|---|---|---|
| RACCOON: Regret-based Adaptive Curricula for Cooperation | ICLR2025 Reject，6.00 | 课程/伙伴生成形态；评审原文未核，不作拒稿原因证据 |
| [Overcooked Generalisation Challenge](https://openreview.net/pdf?id=YKvBiRWdQC) | ICLR2025 Reject，5.75 | 后来已[发表于TMLR2025](https://openreview.net/forum?id=K2KtcMlW6j)，不能称“领域不被认可” |
| [Learning to Interrupt](https://openreview.net/pdf/61c5e5df5eeb1839bccb1d05d5b3aa128ce3d6a3.pdf) | ICLR2026 Reject，5.00 | text pictionary/meeting/debate三设定，声称32.2%沟通成本下降；后来状态未核 |
| [Ad-Hoc Human-AI Coordination Challenge](https://proceedings.mlr.press/v267/dizdarevic25a.html) | ICLR2025 Reject，4.75 | 同题后来ICML2025接收，已核PMLR；3,079局公开数据，human proxy由服务端托管，非完全本地；不能称“现仍拒稿” |
| Sparks of Cooperative Reasoning: LLMs as Strategic Hanabi Agents | ICLR2026 Reject，4.50 | 原评审/后来状态未核；仅提示Hanabi能力榜证据形态需要深查 |

## 5. 2026-08/09最新近邻与 ownership（不作自动判决）

| 工作 | 已核信息 | 会压缩哪些草率故事 |
|---|---|---|
| [BayesBeliefAgent，8/19](https://arxiv.org/abs/2608.18490) | 全文已读；预印本 | “知道队友在做什么却不改行动”+posterior触发重规划 |
| [When Seeing Is Not Enough，8月](https://arxiv.org/html/2608.23978v2) | 4视觉场景、4互动protocol；全文结构/实验入口读，未精读完 | “视觉互动比单次更难”“提问不够”“自我修复稀少” |
| [Drift-Bench++，9/29](https://arxiv.org/abs/2609.38604) | 执行任务、误表达、目标变化、耐心、真实ProdAgent验证；未精读全文 | “现有任务都假设固定意图，第一次研究动态意图” |
| [AgentAbstain](https://agentabstain.github.io/) | 作者页自报NeurIPS2026 Oral；官方目录存在，分轨尚未独立核准；263成对任务/42环境/17模型/4harness | “会做事≠知道什么时候别做”已有大型配对测量 |
| [AgentCollabBench](https://huggingface.co/datasets/AgentCollabBench/AgentCollabBench) | 900结构任务；官方NeurIPS目录与作者接收自报；可能Evals & Datasets track，不能混称main | “终局正确掩盖多跳协作破坏”与四过程指标 |
| [Belief Engine](https://joshuacyang.com/pubs/belief-engine/) | 作者明确NeurIPS2026接收，官方目录存在；2,495人类轨迹重放 | “给agent一个显式belief state就能解释立场变化” |

## 6. 从最新目录额外发现：AI依赖与认知工作分配（值得follow，暂不优先承诺开线）

**自然问题：用了更强AI，究竟替人完成了多少思考，哪些帮助让人之后仍能自己做？** 比“用户信不信AI”更具体；与 Agent、可解释性和游戏助手相邻，并非传统语言学。这个领域可容纳行为测量、交互设计和形式模型，但人类数据是主要资源。

- [Offloading Score](https://arxiv.org/abs/2605.29392)：NeurIPS2026[官方目录条目](https://neurips.cc/virtual/2026/poster/139388)，根据人机流程与估计的无AI反事实流程衡量卸载；40开发者时间压力研究。不是只数API调用或自报信任。当前只核摘要/来源，代码与数据发布、本地judge可替换性未核。
- [Path Dependence under Adaptive AI Delegation](https://arxiv.org/abs/2603.02950)：NeurIPS2026[目录条目](https://neurips.cc/virtual/2026/poster/152872)，将人类技能与委托程度作为耦合动态状态，研究短期帮助和长期独立能力的关系。理论结论依赖模型假设，不能说已在人类身上证明技能流失。
- [AI, Take the Wheel](https://arxiv.org/abs/2605.28255)：23专家、16 AI、24场问答比赛，区分委托与采纳（387/1,440决策），给自然游戏对象；主会状态未核。
- [Belief Updating and Delegation](https://arxiv.org/abs/2602.01986)：N=240、7,200 trials 的跨任务人机依赖实验；主会状态未核，作为研究对象来源而非主会校准。
- 目录还列 *Explanation Mechanism Influences Human Reliance on Reinforcement Learning Agents*，目前原文/资产未找到，不能推荐仅凭题目。

**压力与可行性判断：** 使用频率≠卸载多少（Offloading Score）；委托前不知道输出与看到输出后采纳不是同一决策（Take the Wheel）；跨任务信任带有历史（Belief Updating）；短期成绩与后续独立能力不同时间尺度（Path Dependence）；反事实人类流程本身是估计量（Offloading Score）。这些给出五条有来源的压力，但尚未形成10主会+5near-miss完整卡，不能伪称已达到同等准备程度。

**为何暂排在A/B后：** 算力可以跑离线分析与开放模型，但不能替代真实人类配合、理解、学习数据。用户不想大量API/很慢迭代，这里需先确认日志资产和可复用人类平台；没有它们则不是最适合马上铺开的 workbench。保留此领域以便人选择，未判死。

## 7. 本轮建议交给人的选择

如果希望最贴个人兴趣并快速驻留，优先看 **B的公开伙伴池**与 **A的Collab-Overcooked**，最终可放在一个“任务协作”territory里；选择的是建设重心，不是现在就认领某个反常结果。若对话意义/理解更有吸引力，A可自然接另一份语用领域扫描；不必把自己变成传统语言学项目。新建/恢复workbench仍由人决定，下一步只需选择首先把哪个强基线住进去。
