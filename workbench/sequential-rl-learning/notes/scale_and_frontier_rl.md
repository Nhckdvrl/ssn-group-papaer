# 规模、前沿实验室与环境迁移：文献事实核对（2026-11-28）

读取深度标记：【全】=下载全文并读了相关章节（不一定逐字读完整篇）；【节】=只读相关段落；【摘】=只看摘要/搜索摘要，未核对；【未核对】=未取得文本。
本表只列事实，不含建议。文本在 scratchpad/lit_f/（pdftotext）。

## 1. 规模与遗忘/干扰

| 工作 | 深度 | 事实 |
|---|---|---|
| Ramasesh, Lewkowycz, Dyer, ICLR 2022 "Effect of scale on catastrophic forgetting" | 【未核对】全文拿不到（OpenReview 要验证，不在 arXiv）。只确认 ICLR 海报存在、标题；搜索摘要称"更大的预训练模型遗忘更少"。尺寸范围与任务（视觉为主）我凭记忆，未核对。 |
| Luo et al. 2308.08747 持续指令微调 | 【节】 | BLOOMZ/LLaMA 1B–7B：**规模从 1B 到 7B，遗忘反而加重**（摘要原话 "as the model scale increases from 1b to 7b parameters, the severity of forgetting intensifies"）。作者解释：大模型起点更强，故掉得更多。SFT，非 RL。 |
| RL's Razor 2509.04259 (Shenfeld et al.) | 【节】 | 附录 C.2 明确复测 Ramasesh 的说法：Qwen2.5-Instruct 3B/7B/14B 做 SFT（科学问答），"大模型起点更好，但新任务收益与旧任务保留之间的权衡不变"，达到高精度必有明显旧任务退化，"regardless of model scale"。局限处自述："frontier scales ... remains unknown"。主文是 RL 比 SFT 遗忘少（3B 实验），归因于 on-policy 下与原模型的 KL 更小。 |
| Retaining by Doing 2510.18874 (Chen et al.) | 【摘+节】 | Llama-3.2-1B/3.1-8B、Qwen2.5-1.5B/7B；"RL 遗忘比 SFT 少，目标任务相当或更好"，归因于 on-policy 数据（reverse-KL 的 mode-seeking）。规模上限 8B。 |
| Kalajdzievski 2401.05605 遗忘缩放律 | 【摘+节】 | Llama-2-7B-chat 上，遗忘随"被微调参数数"和步数按移位幂律上升；变量是微调参数量，不是总模型规模。 |
| Lai et al. 2507.05386 | 【摘+节】 | Qwen2.5-VL-7B 多模态持续后训练：SFT 灾难性遗忘，RFT 近乎不遗忘（接近多任务训练）。只有 7B。与 RL's Razor 的 KL 解释有争论（搜索摘要称其消融去 KL 惩罚后仍不遗忘，未核对）。 |
| Huan et al. 2507.00432 | 【全】 | 20+ 开源推理模型审计 + Qwen3-14B 受控：仅数学数据，**RL 调出的模型迁移到其他推理和非推理任务，SFT 调出的模型常遗忘**；PCA 表示漂移和 token 分布 KL 证据：SFT 漂移大，RL 小。摘要称"跨家族与规模，RL 一致优于 SFT"。 |
| 多领域 RLVR 在多个尺寸上的**顺序/干扰**研究 | — | 本次检索**没有找到**。下面几篇各自只用一个或两个小模型：2507.17512（Qwen2.5-7B）、2602.01365（Qwen3-4B-Base）、2606.25178（Qwen3-1.7B、Llama3.2-3B）。 |
| 2610.23946 智能体 RL 数据缩放 | 【节】 | Qwen3-4B/8B/14B：环境多样性指数>任务>轨迹，**每个模型尺寸上顺序一致**（CI 不重叠）。测的是数据轴的缩放，不是干扰。 |

小结事实：SFT 下，1B–7B 的指令微调遗忘随规模加重（Luo）；3B–14B 的权衡不随规模变（Razor 附录）；Ramasesh 的"规模降低遗忘"原文未读到。**没有任何一篇检索到的工作在 RL 后训练的领域顺序/干扰问题上扫过规模，更没有 70B 以上的数据。**

## 2. 前沿技术报告怎么排领域（均读了原文相关节）

- **GLM-4.5 (2508.06471)【节】**：355B MoE。后训练两阶段：专家训练（Reasoning/Agent/General chat 三类专家，各自 RL）→ 统一阶段"self-distillation"把专家蒸馏进一个混合推理模型。原话："we employ self-distillation techniques to integrate multiple experts"。未报告领域间干扰的量化。报告了**同一能力内的顺序效应**：先短长度 RL 再长长度 RL 不如直接 64K 单阶段，"shorter maximum lengths can cause the model to 'unlearn' its long-context capabilities ... significant and irreversible drop"（图 6）。函数调用：端到端多轮 RL 先训专家再蒸馏，步级规则 RL 并入通用 RL。agent RL 称"RL training on web search and SWE tasks leads to generalized performance improvements across other tasks"（无数字）。
- **Qwen3 (2505.09388)【节】**：四阶段顺序：长 CoT 冷启动 → Reasoning RL（仅 3,995 条 query-verifier）→ 思考模式融合 SFT → General RL（20+ 任务）。表 22（Qwen3-32B）：Stage 2→4，AIME'24 思考模式 83.8→81.9(-1.9)→81.4；LiveCodeBench v5 68.4→67.2→65.7；同时 ToolUse 63.3→85.5、IFEval 73.0→85.0。原话："We conjecture this degradation is due to the model being trained on a broader range of general tasks, which may compromise its specialized capabilities ... we choose to accept this performance trade-off"。**这是一份公开的"后一阶段 RL 轻微损害前一阶段能力"的直接数据，且是 32B。** 小模型用强到弱蒸馏，不重做 RL。
- **DeepSeek-V3.2 (2512.02556)【节】**：专家蒸馏（6 个专业领域：数学、编程、通用逻辑、通用 agent、agentic coding、agentic search + 写作/QA，各自大规模 RL 的专家）→ **混合 RL 单阶段**。原话："we merge reasoning, agent, and human alignment training into one RL stage. This approach effectively balances performance across diverse domains while circumventing the catastrophic forgetting issues commonly associated with multi-stage training paradigms"。蒸馏数据训出的模型"only marginally below"专家，差距由后续 RL 消除。无对照实验支撑"避免遗忘"。另称 agent 基准的环境和工具集 RL 中未见过，提升体现 OOD 泛化。
- **Kimi K2 (2507.20534)【节】**：1T MoE。联合 RL 阶段，Verifiable Rewards Gym + 自评奖励。原话："a primary challenge is achieving consistent performance improvements across all domains"；用 per-task token 预算、**PTX 辅助损失**"to prevent the potential forgetting of valuable, high-quality data during joint RL training"。无消融数字。
- **Kimi K2.5 (2602.02276)【节】**：视觉 RL 后文本基准升（MMLU-Pro 84.7→86.4，GPQA-D 84.3→86.4，LongBench v2 56.7→58.9），称"without observable degradation"。RL 领域"not by input modality but by abilities"，联合训练。预训练部分另有"文本能力先降后恢复（dip-and-recover）"现象，属预训练非 RL。
- **MiniMax-M1 (2506.13585)【节】**：456B 混合 MoE。课程：先只用规则奖励的推理任务，再逐步混入通用任务（模型反馈）。原话："prevents catastrophic forgetting of specialized skills"。无对照数字（未核对是否有消融）。
- **Llama-Nemotron (2505.00949)【节】**：Nano 8B/Super 49B/Ultra 253B。多阶段（SFT→大规模推理 RL→短的 IFEval RL→RPO）。"reasoning-focused SFT causes a noticeable drop in IFEval"，故加 IFEval RL；还报告"optimizing for instruction following can compromise conversationality (Arena-Hard)"，Super 用模型合并取帕累托点，"due to mixed outcomes, we did not adopt this approach for other models"。
- **MiMo-7B (2505.07608)【节】**：节标题 "Interference Between Different Domains"：从 Base 起 RL，步 2000–2500 代码持续升，数学波动下降；冷启动 SFT 模型两者都升。归因于 Base 在数学题上 hack 奖励。**这是小模型上有名字的"领域间干扰"报告**。
- **Seed1.5-Thinking (2504.13914)【节】**：20B 激活/200B 总。原话："When merging data from different domains and incorporating diverse scoring mechanisms, we face the challenge of interference between different data domains. This interference can arise from disparities in difficulty levels, the risk of reward-hacking..."，对策为 Online Data Distribution Adaptation（动态调整提示分布）；另用 Pairwise 奖励模型减少可验证与不可验证两类奖励冲突。无干扰量化。
- **Olmo 3 (2512.13961)【节】**：7B/32B。图 20/21：单一领域 RL（如只训 IFEval）出现"over-optimization，领域外评测下降"（IFEval 升则 AlpacaEval 降）；混合训练"yields steady improvements"，但**训练奖励低于单领域**。RL-Zero 报告："each domain is under-optimized compared to the single-domain setup"，明确留给后续"investigate the interactions between domains in multi-objective RLVR"。**开放模型中最干净的"混合 vs 单领域"公开对照，7B 级。**
- **Tülu 3 (2411.15124)**【摘/只 grep】：RLVR 在目标领域内提升；未读到领域间顺序实验（未核对）。INTELLECT-3 等：**【未核对】本次未获取**。

要点事实：几乎所有报告都在"混合 RL / 专家再蒸馏 / 课程"三种里选；**报告里写出的理由**是"避免遗忘""平衡领域""奖励类型冲突"，**公开的对照数字**只有 Qwen3 表 22、GLM-4.5 的长度阶段对照、Olmo 3 的混合 vs 单领域、MiMo 的数学/代码曲线。无一家公开"领域 A 的 RL 如何改变领域 B 的后续学习速度"的专门实验。

## 3. 环境到通用能力的迁移（RLVR 推理侧）

- **Logic-RL 2502.14768【节】**：Qwen2.5-7B-Instruct-1M，仅 5K 条合成 Knights-and-Knaves，AIME +125%、AMC +38%（相对，基线低）。机制主张：自发出现反思/验证/总结（"absent from the logic corpus"），"abstract problem-solving schemata rather than domain-specific pattern matching"。证据是行为词频与 benchmark 升高；没有"仅输出模式被激活"的对照（不确定）。
- **SPIRAL 2506.24119【节】**：Qwen3-4B/8B-Base、Llama-3.1-8B-Instruct、Octothinker-8B、R1-Distill-7B；3 个零和博弈，8×H100，400 步。数学等 8 基准 up to +10%（Qwen3-8B-Base 39.5→49.6）。机制主张：对 CoT 标注三种模式（case-by-case、期望值、模式识别）；转移率不同：case-by-case 72%→71%，期望值 78%→28%，模式识别 35%→45%。这是**标注后的相关性**，非干预。
- **Enigmata 2505.19914【节】**：Qwen2.5-32B；混合 RL 与多阶段 RL"互补"：多阶段对未见难任务迁移更好、混合对 OOD 泛化更好，多阶段长度曲线更不稳定；原文"varied reasoning skills ... can cause conflicts between tasks"。放到 Seed1.5-Thinking（20B/200B）上加谜题数据，AIME24 86.7→87.5（+0.8），AIME25 74.0→75.9，GPQA 77.3→78.1，称"free lunch"（增幅小，未见方差估计）。
- **Reasoning Gym 2505.24760【节】**：Qwen2.5-3B-Instruct，单类训练、跨类评测；类内迁移一致；跨域"signs"：算法类训练提升代数/几何；外部基准 MATH/GSM8K/BBH/MMLU-Pro 小幅升。
- **2507.17512 Can one domain help others【全，读到结论节】**：Qwen2.5-7B（base 与 instruct）、数学/代码/谜题。结论：谜题与数学互助；代码对 instruct 有益、对 base 可能限制；混合数据更稳健但"requires more sophisticated design to address conflicts"；SFT 先于 RL 显著有利；**模板不一致显著伤害**（"robustness of RLVR's generalization ability is challenged"）。
- **2602.01365 When Domains Interact【全】**：Qwen3-4B-Base，GRPO，数学/科学/逻辑/谜题。(1) 迁移高度**不对称**：其他域数据让数学 +~25 点，对逻辑/谜题几乎无迁移；(2) **顺序敏感**：math→science 83%/41%，science→math 77%/25%；三域六种顺序平均 70% vs 56%；(3) 科学训练会冲掉先前逻辑能力（science→logic 两域都最差，混合最好）；(4) 无单一最优：顺序利数学，混合利科学与逻辑。作者推测：数学数据在预训练里多（Qwen3），所以其他域训练也能激活数学；逻辑/谜题在预训练里少所以需域内训练。局限节自述"does not provide a deep mechanistic explanation ... do not disentangle pretraining coverage, knowledge overlap, or optimization dynamics"。**与"一种 RL 如何改变后续 RL"最近，但只有一个 4B、每格单次训练（是否多种子：未核对）**。
- **2606.25178 TAC【节】**：Qwen3-1.7B、Llama3.2-3B，六域；单域训练的迁移谱差异大（表训练使模拟域 +14.6，数学训练仅 +5.0）；用 GRPO 步内投影梯度的对齐估计跨域迁移，做 bandit 课程，比纯可学性课程最多 +2.8（10% 相对）。迁移用"梯度几何对齐"作代理，非机制验证。
- **2507.00432【全】**：见 §1；对"迁移来自何处"的证据是表示稳定性（RL 漂移小），不是领域知识。
- 机制主张的共同点：(a) 通用行为（验证/回溯/分情况）——Logic-RL、SPIRAL 的行为计数；(b) 预训练覆盖度——2602.01365、2507.17512 的 base vs instruct 差异；(c) 输出格式/模板激活——2507.17512 模板实验；(d) 表示漂移小——2507.00432。**没有一篇用干预直接把这几项分开**（2602.01365 自述未分开）。

## 4. 智能体 RL（规模与可行性）

| 工作 | 深度 | 模型/算力 | 与"一个环境如何改变另一个"相关的事实 |
|---|---|---|---|
| RAGEN 2504.20073 | 【节】 | Qwen2.5 0.5B（符号任务）、3B（WebShop），H100，100–200 轮 | 研究 Echo Trap 不稳定、多样初始状态；泛化指同类环境变体；无跨环境顺序实验。 |
| AgentGym-RL 2509.08755 | 【节】 | Qwen2.5-3B/7B，A100/Ascend | 每个场景单独训练，无跨环境迁移实验。 |
| **Can RL Improve Generalization of LLM Agents? 2603.12011（Fudan，2026-03）** | 【节】 | Qwen2.5-3B/7B-Instruct；WebShop/SearchQA/TextCraft/ALFWorld/BabyAI | 单环境训练→未见环境：3B WebShop 训练 held-out +6.29，BabyAI 训练 7B 为 -3.23（WebShop 28.6→10.3，作者归因于 BabyAI 提供可选动作列表导致依赖）。**20 组两阶段顺序实验**：下游持平或更好、上游"minimal forgetting"（WebShop→TextCraft：TextCraft 80.88→82.50，WebShop 86.5→86.32）；但"坏环境一直有害"：BabyAI 排在其他环境之后仍大幅拉低 WebShop；两环境混合训练平衡更好。**与本课题最近的智能体侧文献，只有 3B/7B。** |
| Paying Less Generalization Tax 2601.18217（Meta，2026-01） | 【节】 | Llama-3.1-8B-Instruct；150 步，3 种子 | 单源域训练、三个目标域评测。与迁移相关的是**状态信息丰富度**和**规划复杂度**，而非域真实性或文本相似（Sokoban 比 ALFWorld 迁到 SciWorld 更好）。SFT 预热/中训练减少 RL 期间遗忘但损害未包含域的泛化；开启逐步思考对保持泛化关键。 |
| Practitioner's Guide 2510.01132 | 【节】 | Qwen2.5-1.5B/7B、Qwen3-8B，PPO；TextWorld/ALFWorld/SWE-Gym | 简单环境→复杂环境迁移；SFT:RL 比例存在折中；未见严格的顺序干扰实验（未全读）。 |
| Demystifying RL in Agentic Reasoning 2510.11701 | 【节】 | Qwen3-4B 系；GRPO-TCR | **直接涉及"先前推理训练如何影响后续智能体 RL"**：用 Qwen3-4B-Thinking-2507 直接起步做工具 RL，工具调用次数训练中降到 0，"Long-CoT models ... over-rely on internal reasoning and avoid invoking tools"；SFT 带工具轨迹的初始化更好。对照是不同初始化模型，**不是同模型不同 RL 前史**。 |
| AgentRL 2510.04206（THUDM/Z.AI） | 【节】 | Qwen2.5-3B~32B、GLM-4-9B；五个任务 | 多任务 RL 匹配每任务专用模型的最佳；提出 task advantage normalization；问题陈述含"task interference"。多任务但同时训练，非顺序。 |
| 2610.23946 数据缩放 | 【节】 | Qwen3-4B/8B/14B | 见 §1；环境多样性为最陡轴；预测的是持出环境成功率，不是顺序效应。 |
| Agent World Model 2602.10090、Agent-World 2604.18292 | 【摘】 | 未核对 | 搜索摘要：合成环境数 100→526（AWM）/ 1,978（Agent-World），持出环境随多样性提升。 |
| SkyRL、其他"推理 RL→智能体 RL"受控研究 | 【未核对】 | — | 本次未找到把"同一基座、不同 RL 前史"作为唯一变量的智能体 RL 研究。 |

算力事实：上表智能体 RL 研究的主力模型都在 0.5B–14B，多为 Qwen2.5/Qwen3；SPIRAL 用 8×H100 跑 400 步（4B/8B）；2601.18217 每个设置 150 步；其他论文未核对 GPU 数。

## 事实小结

**(a) 干扰是否随规模缩小。** 证据混杂且范围窄。SFT：Luo 在 1B→7B 看到遗忘加重；RL's Razor 附录在 3B/7B/14B 看到权衡不变；Ramasesh 的"规模降低遗忘"我只确认到标题和二手摘要，原文未读。RL 相对 SFT 遗忘更少在 1B–14B 范围内跨家族成立（Razor、Retaining by Doing、Huan 14B、Lai 7B）。**RL 后训练里"领域顺序/干扰"随规模的变化没有人系统测过**；规模最大的数据点只有 Qwen3-32B 和更大模型的技术报告里的零星数字：Qwen3-32B 后期 RL 使 AIME'24 -1.9/-0.5，Nemotron/Llama 报告有 IFEval↔Arena-Hard 折中。RL's Razor 自述其 KL-遗忘关系在前沿规模"remains unknown"。

**(b) 前沿实验室公开做法与说法。** 三种路线：混合单阶段 RL（DeepSeek-V3.2、Kimi K2/K2.5、Olmo 3、MiniMax 用课程）；专家分别 RL 再蒸馏/合并（GLM-4.5、DeepSeek-V3.2 的专家阶段、Nemotron Super 合并）；顺序多阶段（Qwen3、Nemotron）。公开理由是"避免多阶段的灾难性遗忘"（DeepSeek）、"领域间干扰来自难度差异与奖励 hack"（Seed1.5、MiMo）、"联合训练保持所有领域一致提升是主要挑战"（Kimi）。他们公开的是配方和定性理由，量化的跨领域顺序/干扰对照很少（Qwen3 表 22、GLM 长度阶段、Olmo 3 混合对单域）；没有任何一家公开了系统的"领域 A 对领域 B 后续 RL 学习速度的影响"实验。至于内部是否研究，本次文献无法回答。

**(c) 环境迁移与智能体 RL 的开放点。** 已建立：单域 RL 向数学等域迁移不对称且依赖基座预训练分布（2602.01365 Qwen3-4B：数学域受益大、逻辑/谜题几乎不迁移）；顺序顺序敏感（同一 4B 上 83/41 vs 77/25）；智能体侧顺序训练平均几乎不遗忘但特定环境（BabyAI）会拖垮其他环境（3B/7B）。未建立：(i) 迁移的机制（通用行为 vs 预训练覆盖 vs 格式激活 vs 表示稳定）没有干预式分离，2602.01365 自述未分开；(ii) 同一基座上"前一阶段 RL 对后一阶段学习速度/终点"的受控测量只在 2602.01365（4B 推理域）和 2603.12011（3B/7B 智能体域）出现，均为单个或两个小模型，种子数与置信区间多数未核对；(iii) 推理 RL 前史对后续智能体 RL 的影响只有"不同初始化模型"的间接证据（2510.11701 工具调用归零）；(iv) 规模维度在上述所有顺序研究里缺失。
