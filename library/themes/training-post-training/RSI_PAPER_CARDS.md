# Data-centric RSI：关键论文定向深读卡

更新：2026-10-02。完整入口、版本和阅读等级见 [文献账本](../../../workbench/data-centric-rsi/READING_LIST.md)。DOCUMENTED 表示作者明示的动机或方法；RECONSTRUCTED 表示我们根据论文与近邻重建的 idea 生长路径，不是对作者心理历程的事实断言。未核实公开评审、接收身份和分数的地方不填写。文献结果不是本仓库实验结果。

## P01 — Self-Play Pretraining with Zero Data（2609.30063v1）

来源：[论文](https://arxiv.org/html/2609.30063v1)，尤其 §2–4、App A/B/E/F/G；已查看 PDF 的主要图、Fig3/4、Table5；[作者代码](https://github.com/nourya-aliz/self_play_pretraining)，[模型卡](https://huggingface.co/nourya-cohen/solomonoff-paper)。阅读：主文＋关键附录＋图表/资产。

1. **论文形态**：小规模可行性证明、学习算法与跨分布扩展规律，不是已实用化的 frontier 预训练配方。
2. **背景压力（DOCUMENTED）**：固定程序先验能生成结构，但大量计算并不产生有用训练经验；纯难度奖励还会偏好噪声。
3. **改变的前提**：把合成训练分布也变成学习对象，而非只训练学生。两个模型随机初始化；程序执行输出的 bytes 才是学生数据。
4. **idea 来源（RECONSTRUCTED）**：通用预测给搜索空间，self-play 给自适应机制，优化器感知的学习历史给廉价效用代理。不是单纯把 AZR 的 LLM 出题移植到预训练。
5. **近邻距离**：相对固定 universal prior，增加生成器学习；相对 PCFG，减少特定语法先验；相对 AZR/SQLM，不借预训练 LLM 知识；相对 SOAR，不需每个教师动作完整训练一个学生来算目标收益。
6. **方法/实验**：fresh、mutation、replay 程序池；学生 CE，生成器 RL＋加权监督；核心奖励为 `abs(<grad L, AdamW_preconditioner * (theta_past-theta_now)>)`。最大约 24.4M 参数，最长约 34.36B byte tokens；评估 byte loss 与算法 ICL，主要对照为固定程序先验和 PCFG。Fig3 已将不同阶段生成器的数据用于新学生训练，不能 claim 首次证明数据可迁移。
7. **证据边界**：自然数据参与超参选择；有效计算横轴不等于整个项目实际成本；PCFG 在匹配其先验的 text/code 上更强。Table5 的 signed 变体已做过，并非各域都输。byte prediction 不是自然语言/视觉任务的一般能力证明。模型卡明确未发布 generator、optimizer 和训练代码，且主 ladder 只含完成预算的 seeds；不能据该发布包推断训练失败率。
8. **可迁移研究动作（我们的推论）**：把学生能力增长与数据资产质量拆开；对固定课程做真正训练干预，避免用 teacher reward 自证。对计算“制造经验”的成本和后续复用收益做同一口径记账。
9. **对我们**：已有小模型多阶段权重与 scorer，适合先复核外部行为；完整在线 self-play 复现有资产缺口。探索应瞄准可复用经验/学习者适配，不是再画一次 Fig3 或只改奖励符号。

## P02 — SOAR / Teaching Models to Teach Themselves（2601.18778；v3 复核）

来源：[v3](https://arxiv.org/html/2601.18778v3)，§3–5、App B.3–B.9、C/D；早期主文阅读基于 v1，本卡资源和关键结果口径以 v3 为准。

1. **形态**：稀疏奖励瓶颈＋grounded meta-RL。
2. **背景（DOCUMENTED）**：学生在困难题上几乎采不到成功，直接 RL 难以起步；内生 learnability 信号不保证课程对目标有益。
3. **改变的前提**：教师的奖励不是“题目难度合适”，而是学生在合成题上训练后，目标困难题上的真实改善。
4. **来源（RECONSTRUCTED）**：从自博弈的内部可学习性转向任务相关的教学价值；把目标表现接入昂贵但更直接的双层优化。
5. **距离**：比 AZR/SQLM 多目标 grounding；比静态合成题多教师优化；相对 SEAL 更关注生成 stepping stones 和稀疏奖励突破，而非单次 self-edit 适配。
6. **方法/实验**：Llama3.2-3B 教师/学生；短学生训练、多次重置估计收益、学生 promotion。困难 MATH/HARP 与 OOD Olympiad，含 Hard-Only、Base-T、Intrinsic-T、真实数据上界及 fresh-student 测试。App B.9：单个 SOAR run 为 4×8 H100/H200、48–60 小时；fresh-student RLOO 评估约 8 GPU×12 小时。
7. **边界**：fail@128 不等于真实成功概率数学上为零；外部真值与目标反馈仍存在。不同 OOD 指标并非处处显著胜出；“错误答案也可能有用”不能外推成标签随便错都无害。
8. **研究动作**：比较便宜代理与真正训练后价值，并区分教师质量、学生状态和课程使用方式。
9. **对我们**：优秀科学模板，但完整原配置不是默认 baseline。教师迁移、promotion、课程 warmup/mixing 已有实验，不能重新包装为新意。

## P03 — RSIBench-Data（2607.25886v1）

来源：[全文](https://arxiv.org/html/2607.25886v1)，协议、主表、§6 limitations；[官方仓库](https://github.com/evolvent-ai/RSIBench-Data)。阅读：主文＋协议/限制＋README。

1. **形态**：数据研究 agent 的执行型 benchmark。
2. **背景（DOCUMENTED）**：能调用训练工具，不等于能根据训练反馈持续改善数据策略。
3. **改变的前提**：把可检查的数据改动、受控训练服务、真实任务评估放在同一个闭环中。
4. **来源（RECONSTRUCTED）**：从“agent 做出一个能运行的 recipe”转到“后续实验是否比第一轮更有效”；把数据研究过程本身作为对象。
5. **距离**：DataEnvGym 更结构化；Curation-Bench 主要处理固定池的 curation；此处覆盖多类 agentic/推理任务及轨迹数据。
6. **方法/实验**：4 类研究 agent×6 任务；固定 Qwen3.5-35B-A3B-Base LoRA 学生，Tinker/Harbor/E2B 服务。各候选从同一基础模型重新训练，不是把上一轮学生继续微调。论文名义预算为每 run 16h/$500 Tinker。
7. **边界**：14/24 后续候选超过首轮；18/23 在峰值后的最后候选更差，但这不是累计遗忘证据。选择与官方评估使用同一 task subset；新环境不等于新任务，论文明确承认限制。每组代表性单 run 不支持稳定的机制因果推断。
8. **研究动作**：把“多尝试带来的最大值上升”与“反馈使下一次决策更好”拆开；预留真正 private evaluation，做等预算 search 对照。
9. **对我们**：借鉴契约和成本账，不直接接上云服务就宣称适合本地卡。真正增量应是更会做数据研究，不是仅补一个 held-out split。

## P04 — DataEnvGym（ICLR 2025；2410.06215v3）

来源：[全文](https://arxiv.org/html/2410.06215v3)，方法、with-state/no-state、App E/训练配置；[代码](https://github.com/codezakh/dataenvgym)。阅读：主文与关键附录/README。

1. **形态**：teacher environments 和数据生成 agent 的可复用实验平台。
2. **背景（DOCUMENTED）**：一次性合成数据没有利用学生在真实任务上的反馈。
3. **改变的前提**：数据生成发生在有状态环境内，环境负责训练、验证和反馈。
4. **来源（RECONSTRUCTED）**：把数据生成从 prompt 工程变成 sequential decision making；skill-list/tree 是控制可观察状态和动作结构的实验设计。
5. **距离**：相对 Self-Instruct，多学生反馈；相对传统数据选择，允许生成新训练材料；相对后来的 RSIBench-Data，环境动作更结构化。
6. **方法/实验**：open-ended、skill-list、skill-tree；math/VQA/code 学生包括 Gemma2-2B、PaliGemma3B、Llama3-8B。已有 with-state/no-state、技能配置和固定数据多训 versus 新数据等算力比较。Table 2 的 MATH Open-Ended：初始 15.78、No State 19.78、With State 23.44；但 Skill-List 的 With State 19.48 低于 No State 19.78，不能概括成任意反馈必优。Table 6 的较弱 GPT-4o-mini 在 MATH Open-Ended 给出 15.78（无增益），提醒 teacher 质量可能是首要瓶颈。主结果按 validation 在多轮学生中选最佳，Open-Ended MATH 的最好轮是第 10 次、累计 752 条生成数据；不是单轮 120 条的可比数值。论文 App B.2 写 GPT-4o temperature=0，源码示例未显式传温度；我们 E06 的本地 Qwen/temperature0.7 是探索适配，不复现原协议。
7. **边界**：更详细的 state 帮助生成，不代表 state 足以识别最佳数据干预；协议、数据划分和 checkpoint selection 需要按官方实现逐项复核。README 明示旧 `lighteval/MATH` 来源已不可用。2026-10-02 固定源码审计发现：论文 App B.7 称 MATH validation 从 test 抽样，源码 `val_balanced_subset_50` 实取 train；示例 CSV 又把 validation/test 列写反。`examples/math/open_ended.py` 给未训练学生 few-shot，LoRA 后未设置同一 prompt formatter，实际退回题面 zero-shot；论文 App B.1.2 LoRA r16/alpha32/dropout0.05 与发布示例 YAML 继承的 vendor 默认 r8/alpha16/dropout0 不同。更详细的差异见 workbench E00/ASSETS，不能将某个源码版本等同论文完整实验协议。
8. **研究动作**：先复现强生成策略，再从实际数据动作与学生收益之间的差距生长方法，而非预设反馈一定无用。
9. **对我们**：当前优先建设入口。官方提供本地 LLaMA-Factory、vLLM/Ray 路径；改模型/数据源后的结果须称适配结果，不能冒充原表复现。

## P05 — Curation-Bench（2606.04261v2）

来源：[全文](https://arxiv.org/html/2606.04261v2)，主实验、强基线成本、scaffold 和迁移；[代码](https://github.com/feiyang-k/curation-bench)。阅读：主文与相关附录。

1. **形态**：数据 curation 的 agent benchmark＋scaffold 系统研究。
2. **背景（DOCUMENTED）**：给通用 agent 文件和训练工具，并不自动得到高质量数据策展。
3. **改变的前提**：把输出固定为可执行的数据策略及实际选样结果，而非口头建议。
4. **来源（RECONSTRUCTED）**：在固定模型/训练管线下提高数据决策可归因性，再问什么研究 scaffold 真正有帮助。
5. **距离**：相对 DataEnvGym 更强调通用 coding agent 与固定池；相对传统 selector，策略空间开放；相对 RSIBench 更专注 curation 可控性。
6. **方法/实验**：LLaVA 池子选择、SmolVLM、DataComp/CLIP 等；Light/Heavy scaffold、随机/专业 selector、搜索长度与跨模型/池迁移。将相关论文转成实现的 scaffold 有作用，但不是每种更重研究流程都更强。
7. **边界**：多个 scaffold 成分一起变化，不能把差异归给单个“反思”；强 selector 本身也有不小计算成本。跨模型迁移已做，不能 claim 第一次。
8. **研究动作**：同时对齐方法空间和预算，比较强简单策略；把自然语言“研究过程”与其造成的数据改变拆开。
9. **对我们**：作为 I02 的强近邻和未来跨任务验证，不作为弱 I/O 集群的首个大规模多模态下载计划。

## P06 — Anchored Self-Play for Code Repair（2607.03523v1）

来源：[全文](https://arxiv.org/html/2607.03523v1)，主文、BugSourceBench、训练配置；阅读：定向深读，部分附录未完成。

1. **形态**：自博弈任务漂移＋目标锚定方法。
2. **背景（DOCUMENTED）**：可执行、可修复的合成 bug 不一定代表实际代码修复需求。
3. **改变的前提**：不给内部测试通过率独占课程目标，保留现实参考分布。
4. **来源（RECONSTRUCTED）**：从 self-play 自生难度转到训练分布与部署任务的关系，而非只修 reward 数值。
5. **距离**：AZR/SQLM 强调自动任务；SOAR 用目标收益 grounding；ASP 在代码修复上使用真实参考 bug 和相似度约束。生成器/修复器交叉评测已有，不是我们的新 protocol。
6. **方法/实验**：Qwen2.5-Coder7B 的 generator/fixer、GRPO、参考 bug 混入与 code-embedding 锚定；BugSourceBench 控制程序/测试，改变 bug 来源；含固定生成器 FixerOnly 与计算对照。原配置约 8 H100×48h。
7. **边界**：人为植入的 human bugs 不等于所有 wild commits；embedding 相似不保证完整真实性；更多真实监督本身是必须控制的解释。
8. **研究动作**：构造共享任务基础、只改变训练经验来源的对照；先分离验证通过、学习效用和目标相关性。
9. **对我们**：不能把“真实样本 anchor”“冻结教师”“cross-play”作为主增量；可作为 I01/I03 的现实部署压力与后续较重验证。

## P08 — SEAL（2506.10943v1）

来源：[全文](https://arxiv.org/html/2506.10943v1)，§3–4 和局限；阅读：主文/关键实验定向深读。

1. **形态**：学习 self-edit 的双层适配框架。
2. **背景（DOCUMENTED）**：给模型额外上下文，未必让它学会如何把该信息写入权重。
3. **改变的前提**：模型自己提出训练材料/更新指令，由真实适配效果奖励这次编辑。
4. **来源（RECONSTRUCTED）**：把“怎么学习”变成可优化输出；复用 ReSTEM 形式避免一开始设计复杂可微元学习。
5. **距离**：与 SOAR 共享真实训练后反馈，但面向自适配；与 Self-Instruct 相比，外层直接优化编辑后的结果；文中已有分离 teacher/student 的扩展讨论。
6. **方法/实验**：生成 self-edit→内层 SFT/适配→外层筛选强化。知识整合使用 Qwen2.5-7B；少样本 ARC 使用 Llama3.2-1B 与经筛选的小任务子集，不能把其百分比读成完整 ARC 水平。
7. **边界**：内层训练成本、上下文可见性、跨编辑干扰都影响结论；没有证明强意义的无界递归进步。
8. **研究动作**：让数据产生者为实际学习后果负责，并审计它到底观察到哪些学生状态。
9. **对我们**：教学数据价值的核心近邻；“用下游 accuracy 奖励生成训练数据”已经存在。可借短更新结构，但需要另有实质增量。

## P09 — Self-Questioning Language Models（2508.03682）

来源：[全文](https://arxiv.org/html/2508.03682v1)，奖励、主实验、proposer 频率和超参；阅读：定向深读。

1. **形态**：简洁的 proposer/solver self-play。
2. **背景（DOCUMENTED）**：自进步不必始终依赖额外人工题库或更强 teacher。
3. **改变的前提**：用同一预训练能力同时产生练习和求解反馈。
4. **来源（RECONSTRUCTED）**：将 curriculum 的难度反馈压缩成可直接实现的训练闭环，而非引入复杂 research agent。
5. **距离**：与 AZR 都是预训练后自博弈；math 的多数票和 code 的自生成测试与外部真值不同；相对 SOAR 更便宜但缺少同样直接的目标收益反馈。
6. **方法/实验**：3B 级 Qwen 系列以及 Llama 实验；乘法、代数、代码任务；多 solver samples、提问者奖励、共享/交替更新。已有 proposer 更新频率 1/5/10/无穷和多 seed 对照。
7. **边界**：多数一致不等于正确；主实验中有 best-test-over-training 的读数，应同时保留原复现口径与独立选点口径，不把重评测当作全部论文贡献。
8. **研究动作**：先把简单闭环复现强，检验动态生成是否真的提供静态强课程之外的效用。
9. **对我们**：潜在第二 substrate；“冻结 proposer”“调更新频率”已经不新。旧模型上的 toy arithmetic 只能校准方法，不能独自承担顶会叙事。

## P11 — PopuLoRA（2605.16727v1）

来源：[全文](https://arxiv.org/html/2605.16727v1)，方法框架、§4 与计算口径；阅读：方法/主表定位，未完整审计代码。

1. **形态**：共享基座的群体自博弈与演化。
2. **背景（DOCUMENTED）**：单一 proposer/solver 配对易陷入窄化和耦合。
3. **改变的前提**：多个 LoRA 教师/学生共享冻结基座，以匹配和演化组织训练。
4. **来源（RECONSTRUCTED）**：把人口式训练、匹配与低成本参数共享引入 AZR 类型环路。
5. **距离**：相对双模型 self-play 增加群体；相对简单 ensemble 强调训练期交互；已占有“跨配对＋避免共适应”宽叙事。
6. **方法/实验**：LoRA population、TrueSkill 匹配和权重演化；代码/数学评估。headline 为群体均值，per-benchmark best adapter 是测试集选出的上界。
7. **边界**：baseline 是 per-adapter compute-matched，不是总 population compute-matched；adapter 间离散度不是独立训练 seed 的置信区间。第三方同名实现不能当官方可复现资产。
8. **研究动作**：严分“配对时能做对”和“配对后真正学到”；分摊共享成本，也报告整体训练成本。
9. **对我们**：I01 必须跨过的近邻。不能用几张交叉矩阵或加人口机制重新宣称发现 co-adaptation。

## P14 — Experimental Experience Modeling（2609.39392v1）

来源：[全文](https://arxiv.org/html/2609.39392v1)，主文方法与实验；阅读：主文定向深读。

1. **形态**：研究 agent 的经验复用与实验决策系统。
2. **背景（DOCUMENTED）**：每个候选想法都运行昂贵实验，历史结果又没有变成决策依据。
3. **改变的前提**：先判断现有证据是否足够，不足时才采集有针对性的廉价经验。
4. **来源（RECONSTRUCTED）**：将 evidence sufficiency 显式化，把 pilot 与完整评估分开，再积累 applicability-conditioned lessons。
5. **距离**：较 Reflexion 更强调证据条件；较常规 research tree 更强调“是否值得运行”的决策；直接覆盖经验库＋targeted pilot 的方法叙事。
6. **方法/实验**：record–lesson library、检索、充分性判断、最长 120 秒 pilot。ARC-Bench 25 研究题，用 LLM rubric 评价开发/执行/分析；与 AIDE、AI Scientist v2、AutoResearchClaw 对比。
7. **边界**：其研究质量读数不是某一学生的 held-out 训练收益；跨 backbone 和重复运行主要在单个任务展示。跨研究任务经验迁移被留作 future work，但不表示该问题无人研究。
8. **研究动作**：识别具体缺失的信息，而非机械缩短所有实验。我们的证据应改为数据干预造成的学习收益，不能用“解释很合理”代替。
9. **对我们**：I02 的近邻而非否决理由。只加经验库或 pilot 会被压缩；需要数据决策可识别性与外部能力增益上的新增证据/机制。

## P15 — AutoLLMResearch（2605.11518v1）

来源：[全文](https://arxiv.org/html/2605.11518v1)，跨保真方法、App A 数据混合/划分、成本讨论；阅读：关键方法/实验节核对。

1. **形态**：学习实验配置策略的 multi-fidelity research agent。
2. **背景（DOCUMENTED）**：昂贵实验不能靠当前任务上的大量盲试；低成本最优配置又未必直接迁移。
3. **改变的前提**：将廉价实验经验作为可训练的策略输入，显式学习保真度变化。
4. **来源（RECONSTRUCTED）**：把自动配置从单任务黑箱优化扩展成跨配置空间、跨 fidelity 的经验学习。
5. **距离**：比 EEM 更强调训练策略；相对 meta-BO/配置搜索，使用文本化配置与跨保真经验；相对 data-centric agents，任务不止数据。
6. **方法/实验**：LLMConfig-Gym 预计算实验结果、策略蒸馏和多轮 RL；架构、预训练参数、GRPO、数据混合四类。数据混合包含 ADMIRE 的预计算配比，以及 3B→7B 的评估。
7. **边界**：查询预计算表的成本不等于在线训练新学生；其附录已讨论跨多目标部署的成本回本，不能 claim 首次考虑 amortization。
8. **研究动作**：先界定研究策略能访问的信息和动作空间，再在未见学习状态上检验真实训练效果。
9. **对我们**：I01/I02 需避免退化成“把低保真表格用于高保真配比搜索”。增量要包含新经验构造/修订，以及真实部署闭环，而不只是换 benchmark。

## P16 — PAC（2608.30528v1）

来源：[全文](https://arxiv.org/html/2608.30528v1)，§3、课程轨迹、定位；阅读：方法节核对，完整复现待补。

1. **形态**：在线多任务 GRPO 课程分配。
2. **背景（DOCUMENTED）**：大的 advantage/update 信号不保证任务 reward 继续增长。
3. **改变的前提**：同时考虑可更新程度和真实进度，而非只取一个 proxy。
4. **来源（RECONSTRUCTED）**：把任务选择视作非平稳 bandit，利用训练过程已产生的低开销统计量。
5. **距离**：相对 advantage-only allocation 增加进度；相对固定 mixture 可随任务饱和改变预算；与 P01/SOAR 的学习效用动机相邻。
6. **方法/实验**：advantage magnitude 与局部 reward 趋势融合，用 Thompson Sampling 分配 rollout；分析逻辑任务饱和后的预算迁移。
7. **边界**：主要解决已有任务臂的在线分配，不等于识别任意生成数据的跨状态长期收益。尚未审计其所有 baseline 和资源数值。
8. **研究动作**：先对最强廉价在线进度基线提问，不能拿纯 difficulty 当唯一对手。
9. **对我们**：I03 的直接边界。只有“梯度/advantage 不代表进步”不够新；必须继续到决策错误的结构和有效修复。

## 共同的读论文结论（RECONSTRUCTED）

这些论文的增长方式不是“找到一个别人没碰过的名词”，而是改变一个有实际后果的前提：固定数据→学习数据，内部成功→目标收益，单学生→可复用改进器，盲目试验→有证据的干预。我们的 workbench 应继承它们已经成功的部分，再测量未解决的成本、适配与信用分配，而不是反复退回弱 baseline。

本卡没有把所有邻居读成同一深度。P07/P10/P12/P13 的进一步阅读债务和基础方法补读均保留在文献账本，不用“已搜到”冒充“已复现”。
