# Territory 扫描（2026-09-30，按流程 v3）

**输入：** 组内偏好——智能体协作（大模型 + 小模型 / 全小模型 / 开源非 API）、推理、表征分析、可解释性、理解与生成、游戏 NPC；避开资源碾压型的拥挤赛道（如 RSI、Jev）。
**数据：** `tools/venue_corpus`（ICLR 2025/2026 含拒稿，ICML 2025/2026，NeurIPS 2024/2025，ACL/EMNLP/NAACL main，CVPR/ICCV 2025；EACL 与 Findings 排除）、34 个题材 awesome 列表（1,357 条 2026 年 arXiv）、daily-arXiv 镜像、作者自报的 NeurIPS 2026 接收（完整名单尚未公开，2026-09-24 已出结果）。
**本文是 territory 卡，不是题目。** 不预测结果，不注册 RQ；它回答“哪里值得住进去建设、从哪个强基线开始、有哪些不同方向的压力”。

---

## 1. 候选比较（热度是数字，不是判决）

接收数 = 顶会 main 接收论文中标题+摘要命中该切片的篇数（`query.py density`）；ICLR 切片接收率与全会基准（2026：27%）比较。

| 候选 | 对应偏好 | NeurIPS25 | ICLR26（切片率） | ICML26 | ACL26 | 走势 / arXiv 2026 | 立足点（单节点可跑的强开源基线） | 结论 |
|---|---|---:|---:|---:|---:|---|---|---|
| **C1b 训练出来的开源 LLM 团队**（多智能体 RL / 协同训练） | 协作（大+小 / 全小 / 非 API）+ 推理 | 6 | 7（20%） | 14 | 5 | ICLR25 3 → ICML26 14，上升；arXiv 约 20–40 篇 | Dr. MAS（NeurIPS 2026）、CoMLRL/MAGRPO、MARTI（ICLR 2026）、AT-GRPO/PettingLLMs（ICLR 2026）、SAT/TeamTR 代码 | **推荐主线** |
| C1 多智能体 LLM（整体，提示式为主） | 协作 | 57 | 82（22%） | 114 | 102 | 很拥挤，接收率低于基准 | 大量 | 太宽；只作为 C1b 的背景 |
| C1c 大小模型协作推理（relay / speculative / cascade） | 大+小 | 7 | 5（33%） | 5 | 4 | 平稳；arXiv 方法多，以效率为卖点 | RelayLLM、SpecReason、Tandem 等 | 并入 C1b 作为一个分支 |
| C1d 隐空间 / KV 通信 | 协作 + 表征 | 4 | 3（27%） | 3 | 1 | **arXiv 2026 年 36 篇**（2024 年 1、2025 年 5），已有因果审计 | C2C、LatentMAS、KVComm | 升温过快，作为分支观察 |
| C2a SAE / steering / 机制可解释性 | 可解释性 | 46 | 83（32%） | 96 | 35 | 很热 | 丰富 | 拥挤；以“分析轨道”方式进入 C1b |
| C2b 跨模型表征相似性 / 普适性 | 表征分析 | 27 | 25（27%） | 41 | 12 | 高 | 丰富 | 同上 |
| C3 统一多模态（理解 + 生成） | 理解与生成 | 49 | 66（34%） | 49 | 15 | 很热；大厂主导的模型族 | BAGEL、Janus 等（训练成本高） | 资源门槛高，暂不作主线 |
| C4 游戏 NPC / 游戏智能体（LLM） | 游戏 NPC | 1 | 6（12 篇投稿） | 2 | 1 | 顶会极少；ICLR26 ToM×多智能体 0/13、社交推理游戏 0/11 | PCSP、Ashwick 等 | 作为 C1b 的**环境**（合作游戏、NPC 队友），而不是独立主线 |
| C5 隐式 / 连续推理 | 推理 | 10 | 17（39%） | 33 | 15 | 快速升温 | Coconut 系 | 热，竞争者资源多 |

**读法：**
- C1b 是唯一同时满足“偏好第一条 + 中等热度且在上升 + 单节点可跑的强开源基线 + 多种可接收论文形态”的候选。
- C1b 的 ICLR 切片接收率（20%）低于基准：说明审稿人对这类工作挑剔（常见短板：基线不公平、只在一个模型族上、贡献像工程拼装）。**这正是我们的实验卫生（算力匹配、强基线、多种子、多家族）能形成优势的地方。**
- 可解释性、表征分析、游戏 NPC 三条偏好不单独开线，而是作为 C1b 的**理解轨道**与**环境**：开源模型允许看内部表征（非 API 的真正价值），合作游戏正是“NPC 队友必须和任意玩家配合”的场景。

---

## 2. 推荐 territory：训练出来的开源异构 LLM 团队——协作是怎样被学到的、在什么条件下可靠

范围：多个开源 LLM（同族或异族、同尺寸或大+小）组成团队，用 RL / 协同训练优化协作；以推理（数学、代码）、搜索问答与合作游戏为任务。**不做**：只调提示词的框架、闭源 API 团队、纯系统吞吐优化。

### 2.1 热度卡
- 顶会接收：ICLR 2025 → 2026 → ICML 2026 = 3 → 7 → 14；NeurIPS 2026 已知接收 Dr. MAS。ICLR 2026 切片接收率 20%（基准 27%）。
- arXiv：LLM 多智能体 RL 的专门 awesome 列表收录 84 条（42 条 RL 方法），2026 年新增集中在**信用分配**（MAPPA、CCPO、SHARP、COSAC、反事实信用）、**稳定性**（Dr. MAS、AT-GRPO、MAAC）、**编排**（M-GRPO、Orchestration Traces）。
- 前沿实验室：Kimi Agent Swarm / PARL 等工业系统在做大规模并行智能体 RL，但**开源小模型团队的协作科学**不是它们的主战场。
- 结论：中等热度、仍在上升；方法层面（信用分配、稳定性）已拥挤，**“训练出的协作是什么、是否可靠、何时值得”**这一层相对空。

### 2.2 谱系卡（五条链）
1. **提示式协作 → 等算力怀疑**：多智能体辩论（Du et al. 2023）→ MoA → 多智能体辩论在等算力下并不稳定地胜过 self-consistency（ICLR 2025 上的辩论评测分析）→ *Multi-Agent Teams Hold Experts Back*（ICML 2026：团队达不到最强成员，瓶颈在“利用专家”而非“识别专家”，机制是折中式共识）→ *At Equal Inference Cost, Multi-Agent Structure Does Not Beat a Single Frozen Agent*（2609.04217）/ *When Do MAS Help? An Information Bottleneck Perspective*（2607.16133：中继信息充分时 MAS 才有益，强模型收益更小）。**前提的改变**：多智能体的收益需要在等算力下重新证明。
2. **训练协作**：MALT（2024）、Multiagent Finetuning（ICLR 2025：多模型各自专精以保持多样性）→ MAPoRL（ACL 2025：多模型讨论 + 验证器奖励的协同后训练；跨数据集迁移；异构对 Phi3+Qwen2.5、Phi3+Llama3）→ MAGRPO/CoMLRL（AAAI 2026：Dec-POMDP 表述；写作/代码/Minecraft）→ AT-GRPO（ICLR 2026：按智能体与轮次分组）、MARTI（ICLR 2026：收敛后等推理预算下 MAS > 单智能体）、Lazy Agents → Dr. MAMR（ICLR 2026：训练中“懒惰智能体”——推理智能体的因果影响随训练下降，根源是多轮 GRPO 的归一化偏置）→ Dr. MAS（NeurIPS 2026：全局归一化基线偏离各智能体奖励分布 → 梯度范数不稳定 → 按智能体归一化）、MAAC（ICML 2026：长程/稀疏奖励需要集中式 critic）、TeamTR（ICML 2026：共享上下文团队的“移动靶”/占用分布漂移 → 信赖域；支持组件即插即用替换）、SAT（AAMAS 2026：3×4B 团队超过 Qwen3-32B；即插即用不变性，换入 8B 成员 +10.4%）。
3. **零样本协调（ZSC）/ ad-hoc teamwork（经典 MARL）**：Other-Play（ICML 2020：避免任意约定）→ FCP（NeurIPS 2021：与伙伴种群训练）→ ZSC-Eval（NeurIPS 2024）、*Diversity Is Not All You Need*（NeurIPS 2024：伙伴还要专精）→ *Cross-environment Cooperation*（ICML 2025 Oral：单伙伴 + 多环境也能学到通用协作规范）→ *Unsupervised Partner Design*（ICML 2026 spotlight）。**核心教训：一起训练的智能体会学到只对彼此有效的约定，换伙伴就崩。** 这条教训进入 LLM 训练的第一步是 SCOPE（2608.12253：对单一冻结用户模拟器做 RL 会“模拟器坍缩”，迁移到新模拟器和真人时变差；种群协同训练 +14%）。提示式 LLM 本身对陌生伙伴较稳（LLM-Coordination 2023；Hanabi 中不同 LLM 的交叉配对平滑插值，ICML 2026），**但 RL 协同训练之后是否仍然如此，尚无系统测量**。
4. **大 + 小协作**：推测式思考 / SpecReason（NeurIPS 2025）/ R-Stitch → RelayLLM（小模型学会用指令 token 请求大模型，1.07% 的 token 调用大模型、恢复约 60% 差距）、ConfSpec（ACL 2026）→ 级联与路由理论（ICLR 2026 *Routing, Cascades, and User Choice*）；*Can Small Agents Collaborate to Beat a Single LLM?*（2601.11327：编排者容量决定上限）；*Student-Centered Distillation*（ICML 2026：7B 学生追平 72B 教师）。
5. **通信媒介**：文本 → 嵌入/激活（CIPHER ICLR 2024、Communicating Activations ICML 2025）→ Thought Communication（NeurIPS 2025 spotlight）→ C2C、KVComm（ICLR 2026）、LatentMAS（ICML 2026 spotlight）→ 因果审计与安全（2026）。旁支：训练中的“涌现语言/约定”（GlossoGen 2609.01491；*When LLMs Develop Languages* ICML 2026）。

### 2.3 形态卡（顶会在这里收什么样的论文）
`query.py shapes "multi[- ]agent" "\b(LLMs?|language models?)\b"`（ICLR 2025+2026）：接收 115 篇，**90% 为方法/框架型**，70% 提到 benchmark，36% 使用失败模式语言（拒稿 28%，撤稿 22%）；均分 5.53 vs 拒稿 4.20。

可行形态：
- **A. 失败模式 + 修复**（最常见）：在强训练框架上发现一个命名的失败（懒惰智能体、移动靶、梯度不稳）→ 解释根因 → 最小修复。例：Dr. MAMR、Dr. MAS、TeamTR。
- **B. 引入成熟构念 + 大规模测量**：例：strong synergy（组织心理学）、hidden profile（社会心理学）、表征相似性（神经科学）、PID 涌现（信息论）。**ZSC/交叉配对**是 MARL 的成熟构念，尚未系统用于 RL 训练后的 LLM 团队。
- **C. 理论 + 受控实验**：例：*Benefits and Limitations of Communication in Multi-Agent Reasoning*（ICLR 2026）。
- **D. 评测协议 / benchmark**：例：HiddenBench（ICML 2026）；awesome 列表指出“没有开源 benchmark 同时覆盖 MAS 原生的多种度量”。

近邻里的 near-miss（高分拒稿）提示：*Investigating the Link Between Representational Similarity and Model Interactions*（ICLR 2026 拒 5.5 → ICML 2026 接收）、*Sparks of Cooperative Reasoning: LLMs as Strategic Hanabi Agents*（ICLR 2026 拒 4.5 → ICML 2026 接收）——评测型工作第一次投常因“规模/机制不足”被拒，补强后再投成功。

### 2.4 立足点卡
- **训练框架（开源，单节点可跑）**：
  - Dr. MAS（NeurIPS 2026，verl 系）：数学（Solver + Verifier 循环）与搜索（Verifier 路由 Search / Answer）；支持异构模型（如 2×Llama-3.2-3B + 1×Qwen2.5-7B）。官方耗时：搜索 3×Qwen2.5-3B 4×H100 约 13 小时；数学 2×Qwen3-4B 4×H100 约 38 小时。
  - CoMLRL（MAGRPO / MAREINFORCE / MAAC）：写作、代码（MBPP、HumanEval、CoopHumanEval、ClassEval）、**Minecraft 协作建造**（StrBuild、HouseBuild）；可从 Qwen2.5-0.5B 起步。
  - MARTI（ICLR 2026）、PettingLLMs / AT-GRPO（ICLR 2026）、SAT / TeamTR（作者代码）、SCOPE（种群协同训练）。
- **模型**：Qwen2.5 / Qwen3（0.5B–8B）、Llama-3.2（1B/3B）等开源权重——**异族、异尺寸组合**正是“大+小 / 全小 / 非 API”偏好的直接实现，而且可以看内部表征。
- **任务**：数学（MATH、AIME、AMC）、代码（HumanEval、MBPP、LiveCodeBench）、搜索问答（NQ、HotpotQA）、合作游戏（Minecraft 建造、Overcooked 类、Hanabi）、分布式信息任务（HiddenBench）。
- **算力估计**：1.5B–4B 团队的一次训练 ≈ 单节点 0.5–2 天；前 3 周的驻留计划（§2.6）约 6–10 次训练 + 大量推理评测，单节点可完成。
- **我们的优势**：算力匹配比较与强基线纪律（本方向审稿人最常抓的短板）；开源模型的白盒分析（表征、logit、注意力）；已有的 vLLM / verl 使用经验（omni-recon、scoped-context-state 的环境脚本）。

### 2.5 压力清单（每条有出处；不预测结果）
| # | 压力 | 出处 | 可能对应的形态 |
|---|---|---|---|
| P1 | **训练后的团队到底比什么强？** 多数工作与“未训练的团队”或“单智能体 RL”比较；等**训练**算力 + 等**推理**算力 + 等**参数量**的三重对照很少。提示式团队在等算力下常不胜单智能体；训练后是否改变这一点？ | MARTI 等推理预算结论；2609.04217；2607.16133（IB）；SAT（3×4B vs 32B） | B/D：算力匹配的测量协议；A：若发现收益来源可修复的瓶颈 |
| P2 | **协作是否只对训练伙伴有效？**（ZSC 教训）RL 协同训练可能学到私有约定；换成不同种子、不同尺寸、不同家族的伙伴时是否崩溃？提示式 LLM 对陌生伙伴较稳，训练后呢？ | Other-Play、FCP、ZSC-Eval、UPD（ICML 2026）；SCOPE 模拟器坍缩；SAT/TeamTR 以方法保证即插即用 | B：交叉配对矩阵；A：种群 / other-play 式训练用于 LLM 团队；D：协作可靠性评测 |
| P3 | **大+小团队里谁学到了什么？** 训练中出现懒惰/主导；大模型可能包办、小模型可能依赖；团队不会利用专家（折中式共识）。训练能否学会“按能力分工、按专长加权”？ | Lazy Agents（ICLR 2026）；Teams Hold Experts Back（ICML 2026）；RelayLLM；SAT 换入 8B | A：角色/贡献失衡的修复；B：按角色的反事实贡献测量 |
| P4 | **训练改变了模型内部什么？** 协作能力是写进了各成员的表征（可迁移到新伙伴），还是只是输出层面的相互适配？对协同训练前后做模型差分 / 表征分析。 | 模型差分工具（ICLR 2026 *Narrow Finetuning Leaves Clearly Readable Traces*）；表征相似性预测合作（ICML 2026） | B/C：白盒分析 + 与 P2 行为结果对应 |
| P5 | **训练出来的“语言”**：消息是否变短、变私有、变难以被新伙伴理解？约定何时出现、能否被检测？ | GlossoGen；*When LLMs Develop Languages*（ICML 2026）；emergent conventions（Science Adv. 2025） | B：消息统计与可理解性测量；与 P2 相连 |
| P6 | **协作原生的任务很少**：多数 benchmark 单智能体也能做；需要分布式信息 / 真正分工的任务上，训练是否能修复 HiddenBench 式失败？ | HiddenBench（ICML 2026）；awesome 列表的 benchmark gap | D：任务/协议；A：训练修复 |
| P7 | **训练稳定性与信用分配**（已拥挤，作为工程前提而不是主线） | Dr. MAS、AT-GRPO、MAAC、MAPPA、CCPO、SHARP、TeamTR | 只在我们的实验中遇到新失败时才进入 |
| P8 | **游戏 NPC 视角**：NPC 队友必须和任意玩家（人或模型）配合——这正是 P2 的部署形态；合作建造 / 烹饪游戏提供可测的团队回报 | CoMLRL Minecraft；Collab-Overcooked（EMNLP 2025）；Hanabi（ICML 2026） | P2/P6 的环境与应用 |

至少 5 条（P1–P6）彼此独立：第一条路走不通，还有别的路。P7 是拥挤的方法层，只作为前提。

### 2.6 驻留计划（前 3 周；交付 D1–D6，见 `workbench/README.md` §2）
- **第 1 周 · 跑通强基线（D1/D2）**：Dr. MAS 数学与搜索、CoMLRL MAGRPO 代码协作，各用 1.5B–4B 模型复现官方趋势（数值误差范围写清）；统一评测 harness（vLLM 推理、算力计量：调用次数、生成 token、训练 GPU·时）。
- **第 2 周 · 领域标准的系统测量（D3/D4）**，全部是**测量**，不是假设检验：
  1. **算力匹配曲线**（P1）：同一任务上，训练后的团队 vs 同算力训练的单模型 vs 更大单模型，按推理 token / 调用数对齐；
  2. **交叉配对矩阵**（P2）：不同种子 / 尺寸（1.5B↔3B↔7B）/ 家族（Qwen↔Llama）独立训练的团队互换成员，与自配对比较；同时测提示式（未训练）团队作为对照；
  3. **按角色的反事实贡献**（P3）：替换或屏蔽某个成员的输出，看团队得分变化随训练的走势；
  4. **消息统计**（P5）：长度、词汇漂移、被“新伙伴”复述/理解的能力；
  5. **白盒快照**（P4）：训练前后各成员的激活差分（复用 model-diffing 工具链）。
- **第 3 周 · 定位表与形态卡（D5/D6）**：对最近 10 篇接收论文 + 最新 arXiv 写增量；根据痛点日志与测量结果写第一版论文形态卡，选出 1–2 条压力深入（build + understand 两条轨道并行）。
- **目标会议**：主 ICML 2027（约 1 月下旬），备 ACL 2027（ARR 约 2 月）/ NeurIPS 2027（约 5 月）。

### 2.7 可能的论文形态（天花板示意，不是注册的题目）
- 若 P2 显示训练后团队对换伙伴脆弱：**“LLM 团队的零样本协调”**——交叉配对评测协议 + 种群/other-play 式训练 + 表征/消息层面的解释（形态 A+B）。
- 若 P2 显示训练后仍然稳健：这本身违背 MARL 的经典经验，需要解释“语言为什么让约定可迁移”（形态 B+C）。
- 若 P1 显示训练团队的收益主要来自等价于“更多算力”的部分：**训练型多智能体系统的算力会计**（形态 B/D，严谨性论文）。
- 若 P3 显示大+小团队中出现系统性依赖或包办：针对角色失衡的最小修复（形态 A）。

每个结果方向都有论文，这是本领域被选中的原因，而不是因为我们猜中了某个现象。

### 2.8 风险
| 风险 | 可能性 | 对策 |
|---|---|---|
| 并行工作（SAT/TeamTR 作者组、SCOPE 作者组）扩展到交叉配对 | 中 | 驻留第 2 周即出测量；增量放在“系统测量 + 白盒解释 + 大小异构”上 |
| 多智能体 RL 训练不稳定、复现耗时 | 中 | 先用官方配置与小模型；Dr. MAS 的按智能体归一化作为默认 |
| 审稿人对“又一个多智能体框架”挑剔（切片接收率 20%） | 高 | 不做框架；做测量协议 + 最小修复 + 多家族复现 |
| 算力 | 低–中 | 1.5B–4B 为主；7B 只用于关键对照 |

---

## 3. 其他候选的简卡（供人选择）

- **C3 理解与生成（统一多模态）**：ICLR 2026 接收 66 篇、切片接收率 34%，热且审稿人欢迎；但主流模型族（BAGEL、Janus、Show-o 等）训练成本高，大厂主导。可行切入：统一模型内部“理解表征”与“生成表征”的关系（*Does Understanding Inform Generation in Unified Multimodal Models?* 2511.20561；*Where a New Concept Must Enter* 2608.17564；*The Telephone Game* ICLR 2026 拒 5.33）。建议作为第二顺位，等 C1b 驻留稳定后再评估。
- **C4 游戏 NPC**：顶会极少（ICLR 2026 LLM 游戏智能体接收 6 篇；ToM×多智能体 0/13）。作为独立主线更适合 ACL 系；在本扫描中并入 C1b 的 P8（NPC 队友 = 零样本协调的部署形态）。已被桌面降级的 `workbench/npc-*` 两条线在 v3 下可重开评估。
- **C2 可解释性 / 表征分析**：整体很热（ICLR 2026 SAE/steering/机制 83 篇）。本扫描把它作为 C1b 的理解轨道（P4、P5）；若要独立开线，`workbench/mechanism-population-dynamics/`（多种子机制群体）是已有的候选资产。
- **C5 隐式推理**：快速升温（ICLR 2026 17 篇 → ICML 2026 33 篇），竞争者多，暂不建议。

---

## 4. 精读材料
关键论文卡（背景、压力、idea 来源、与近邻的距离、证据、可迁移动作）见 `library/themes/multi-agent-collaboration/`。
