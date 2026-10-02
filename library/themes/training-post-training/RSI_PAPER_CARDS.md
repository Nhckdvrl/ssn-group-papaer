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
4. **来源（RECONSTRUCTED）**：作者从此前 EnvGen 在简单游戏中用反馈调环境参数出发，追问开放式 MATH/代码/VQA 缺少可重复的教师环境这一母问题。于是把数据生成从 prompt 工程变成 sequential decision making；skill-list/tree 是控制可观察状态和动作结构的实验设计。其最有价值的 delta 是可插拔且以学生训练收益闭环的**实验环境**，不只是更长的生成提示词。
5. **距离**：相对 Self-Instruct，多学生反馈；相对传统数据选择，允许生成新训练材料；相对后来的 RSIBench-Data，环境动作更结构化。
6. **方法/实验**：open-ended、skill-list、skill-tree；math/VQA/code 学生包括 Gemma2-2B、PaliGemma3B、Llama3-8B。已有 with-state/no-state、技能配置和固定数据多训 versus 新数据等算力比较。Table 2 的 MATH Open-Ended：初始 15.78、No State 19.78、With State 23.44；但 Skill-List 的 With State 19.48 低于 No State 19.78，不能概括成任意反馈必优。Table 6 的较弱 GPT-4o-mini 在 MATH Open-Ended 给出 15.78（无增益），提醒 teacher 质量可能是首要瓶颈。App E 更严格的成本对照把 MATH 的 10% 数据训练 30 epoch，结果 13.98；全数据 3 epoch 则 23.44，已占有“新数据优于把旧数据多训”这一发现。主结果按 validation 在多轮学生中选最佳，Open-Ended MATH 的最好轮是第 10 次、累计 752 条生成数据；不是单轮 120 条的可比数值。App B.4 报 MATH Open-Ended 每轮约 173,234 teacher token、GPT-4o 计价 $1.73、A6000 24 GPU 分钟，需以**完整多轮成本**评估 state 的额外收益。论文 App B.2 写 GPT-4o temperature=0，源码示例未显式传温度；我们 E06 的本地 Qwen/temperature0.7 是探索适配，不复现原协议。
7. **边界**：更详细的 state 帮助生成，不代表 state 足以识别最佳数据干预；协议、数据划分和 checkpoint selection 需要按官方实现逐项复核。README 明示旧 `lighteval/MATH` 来源已不可用。2026-10-02 固定源码审计发现：论文 App B.7 称 MATH validation 从 test 抽样，源码 `val_balanced_subset_50` 实取 train；示例 CSV 又把 validation/test 列写反。`examples/math/open_ended.py` 给未训练学生 few-shot，LoRA 后未设置同一 prompt formatter，实际退回题面 zero-shot；论文 App B.1.2 LoRA r16/alpha32/dropout0.05 与发布示例 YAML 继承的 vendor 默认 r8/alpha16/dropout0 不同。发布示例的 `accumulate_train_loop.py` 每轮累积**全部过去生成数据**，调用的 LLaMA-Factory 始终指向同一原始 `model_name_or_path` 且 YAML 设 `overwrite_output_dir=true`、未见 resume 参数；这看起来是每轮重训累计数据，而不是从上轮 LoRA/optimizer 续训，正式 time-horizon 实验必须单独核实并锁定这一语义。开源 Open-Ended MATH 示例设 GPT-4o-mini，每次生成调用只随机取 3 个 train 例和 3 个当前错误例作 in-context，不是把完整错误表送入教师。更详细的差异见 workbench E00/ASSETS，不能将某个源码版本等同论文完整实验协议。
8. **研究动作**：先复现强生成策略，再从实际数据动作与学生收益之间的差距生长方法，而非预设反馈一定无用。
9. **对我们**：当前优先建设入口。官方提供本地 LLaMA-Factory、vLLM/Ray 路径；改模型/数据源后的结果须称适配结果，不能冒充原表复现。

## P05 — Curation-Bench（2606.04261v2）

来源：[全文](https://arxiv.org/html/2606.04261v2)，主实验、强基线成本、scaffold 和迁移；[代码](https://github.com/feiyang-k/curation-bench)。阅读：主文与相关附录。

1. **形态**：数据 curation 的 agent benchmark＋scaffold 系统研究。
2. **背景（DOCUMENTED）**：给通用 agent 文件和训练工具，并不自动得到高质量数据策展。
3. **改变的前提**：把输出固定为可执行的数据策略及实际选样结果，而非口头建议。
4. **来源（RECONSTRUCTED）**：在固定模型/训练管线下提高数据决策可归因性，再问什么研究 scaffold 真正有帮助。
5. **距离**：相对 DataEnvGym 更强调通用 coding agent 与固定池；相对传统 selector，策略空间开放；相对 RSIBench 更专注 curation 可控性。
6. **方法/实验**：LLaVA 池子选择、SmolVLM、DataComp/CLIP 等；Light/Heavy scaffold、随机/专业 selector、搜索长度与**换模型/池后各自运行的任务**。论文附录 Table 22 的 LLaVA 10k：随机 **32.5**（best-of-10）、ICONS **33.3**、ARDS **33.2**、Claude Code 开放提示 agent 10 轮 **34.2**；随机 100k 为 **33.7±0.2**。但更宽的附录 Table 7 还有 **LESS 33.6±0.3**，与三 session 开放提示 agent **33.7±0.3** 接近；不能把 ICONS/ARDS 冒充最强非 agent 对照，或把 0.1 分差解读成可靠的 agent 独有收益。agent 的数据效率相对随机有实测增量，同时须把 10 轮研究/训练反馈成本计入全链路。主文 Table 5 的 Claude 重复 session 中，开放提示平均 **33.7**、强制 evidence-only 自研究 **32.9**、强制适配论文 **34.0**（最优 **34.9**）；后者从源比例局部搜索转向 EL2N 高 loss 选样＋assistant-loss 噪声过滤，但并非每次局部改动更有效。较重流程能改变探索的**策略家族**，不保证所有实例胜出。
7. **边界与源码校对（2026-10-02）**：多个 scaffold 成分一起变化，不能把差异归给单个“反思”；强 selector 本身也有不小计算成本。论文 §5.3 明确 LESS 的特征选样约用一次最终训练的 **10 倍 GPU 时间**，恰与开放提示 agent 的十轮训练反馈同量级；33.6±0.3 对 33.7±0.3 应在总成本而非只在最终样本数上比较。附录 D.5/Table 24 在两个 Qwen 学生及 Vision-Flan 池上报告的是各任务**重新进行 10 次 agent 迭代后**相对随机约 +0.4 的结果；它显示同一研究框架可运行于不同任务，**没有报告把 LLaVA episode 学到的冻结策略直接移用到新学生/池的交叉效用，也没有报告改进器跨 episode 学习**。不能把前者写成后者，也不能因新 episode 未做就预设我们的方法会赢。其 10k/20k/50k 结果显示数据预算改变会重排方法间的实际效用，不宜只报单一预算切片。主文明确把 DataComp 的静态政策评测与 SWE/AI-research agent 的迭代执行相接，论文新增的是固定训练契约下对**搜索过程**的研究，不是声称首创数据选择或 agent 研究。重写扩展也已做，不能把“从选择扩到改写”单独当作我们的 delta。固定代码 SHA `24eea15` 的 README 称整套安装需 ≥1TB，但单个 LLaVA-665K 自包含第三方 Arrow 文件为 93.4GB、官方 Vision-Flan 原始数据为 36.5GB；因此整套前提不能用来否决单任务。论文 B.1/Table10 链到 `anonneuripsmail/llava-1.5-7b-init`，而 README/trainer 默认 `llava-hf/llava-1.5-7b-hf`；两者权重 shard SHA 不同，复现必须显式指定论文父模型。发布 ICONS/ARDS 脚本以原 JSON 位置索引本地 Arrow，第三方转换数据需审计；另原 JSON 的 665,298 行只有 389,722 个不同 ID，ICONS 发布 133,046 条完整记录都能唯一精确找到，但 `icons.py` 的 ID/图像路径映射按原 JSON 行序将 58,201 条指到其他记录（E12 CPU 审计）。ARDS 发布 199,586 条全记录与 `original[global_id]` 精确一致，公开脚本却用 `global_id−1`，没有一条全记录对上。两者均须修正后才可充当忠实 baseline；第三方 Arrow 与原 JSON 的 **665,298/665,298 条完整对话按位置一致**，见 E12 全量审计，但图像有 355 张被第三方重编码，不能称原数据 exact reproduction；**无证据表明作者论文实验使用了这些错误映射**。官方源码 clone 内未找到已发布完整 agent manifests/traces，不以论文文字“可追溯”推断公开了全部训练政策。手动 CLI 可通过 subprocess 运行，agent Docker 路径仍需容器权限。
8. **研究动作**：同时对齐方法空间和预算，比较强简单策略；把自然语言“研究过程”与其造成的数据改变拆开。
9. **对我们**：作为 I02 的强近邻和真实训练效用底座。E12 已把一组强静态策略在单任务上复现列为当前测量；若读数可信，下一步才研究何种反馈决策能超越强静态/LESS，并用新 episode 而非 best-of-N 证明改进器能力。
10. **再次对齐原始轨迹（Table 3、25–26）**：Claude 开放提示的一条 10 次轨迹里，“五个 visual source 各 2,000”的第 4 次策略已得 **33.23**，后续主要调源比例，最终 **33.74**；作者标出的新策略家族只有 **2/10**，而 10 次执行全成功。Codex 示例轨迹的策略家族变化为 **3/10**，其余多为已有比例或种子调整。E12 的五源均衡臂直接对照这类朴素强动作，但不同 seed/数据转换下绝不能把我们的分数与该轨迹逐点相减。此文已明确提出局部搜索问题并设计重 scaffold；我们的后续研究若只说“agent 局部优化、应该更深读日志或切换策略家族”，就是重复其问题与响应。需要找到**具体哪种反馈在同搜索成本下改变正确的数据动作**，再在新 episode 区分可迁移决策规则与继续 best-of-N。

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

## P10 — Absolute Zero / AZR（NeurIPS 2025 main；2505.03335v3）

来源：[全文含附录](https://arxiv.org/html/2505.03335)、[主会论文](https://papers.nips.cc/paper_files/paper/2025/file/9837dc00ff67d176373268ed48042d49-Paper-Conference.pdf)、[官方源码](https://github.com/LeapLabTHU/Absolute-Zero-Reasoner)。阅读：引言/相关工作、方法、全部主表与 D/B 附录；本地审 `paper` 分支 SHA `41ed983cdf541cfcd2f963f33c055d50074f3c90` 的 README、配置、constructor、reward manager 与 executor，未执行训练复现。

1. **母问题与 idea 生长**：此前“zero RLVR”不需要标注推理链，却仍要人工提供题目和答案；早期 self-play 常局限于封闭游戏或依赖不可靠 learned reward。AZR 将任务写成 Python `(program,input,output)`，由模型提出前两者，执行器算出第三者，再分别训练出题和解题。它相对普通 synthetic-data/self-training 的真正改变，是**题目本身及其答案由可执行环境共同定义**，不是给生成器加一段反思提示。最近邻包括 AlphaZero/unsupervised environment design、STaR、RLVR、Minimo、SQLM，以及后来的 code self-play；不能称首次自博弈或首次可验证任务。
2. **方法与训练口径**：统一模型做 deduction（给程序/输入预测输出）、abduction（给程序/输出找等效输入）、induction（给部分 I/O 合成程序）；经 Python 验证的三类 buffer 不断加入有效任务。每题对当前 solver 采 8 个 rollout，proposer 奖励为成功率非零时 `1−成功率`，零成功给零；这是可解性/难度信号，**不是单题训练后的实际外部收益**。六个任务×角色各自标准化 reward 做 TRR++。主实验 Qwen2.5-7B Base/Coder，batch `64×6`、500 步、AdamW LR1e−6、最长 prompt6144/response8096；评估 HumanEval+/MBPP+/LiveCodeBench 与六项数学基准，greedy 输出。论文附录称每次训练约 **3–5 天 A800 集群**；固定 `paper` README 要求 7B **4×80GB GPU**，不能当本地短 LoRA 实验的即插即用替代。
3. **强基线、效果和反例**：Coder-7B 的 code/math/总平均由 base **56.6/23.9/40.2** 到 AZR **61.6/39.1/50.4**；同表比较人工代码/数学数据训练的多个 RLVR 模型，但基座版本和监督来源并非全部相同，需谨慎读横向名次。Base-7B 消融：full **46.8**，只训 solver **45.4**，去历史生成参考 **43.8**，仅 deduction **43.3**；故 proposer 更新有额外收益，然而只训 solver 也已获得大部分效果。Llama3.1-8B 上 AZR 总平均 **19.2**，低于同文 SimpleRL **20.5**，它不是每个基座都胜强方法。附录 D 的组合函数课程常退化为原函数，额外 complexity/diversity reward 没显著增益，LeetCode 初始化早期代码表现更好但最终平台相近、数学更低；这些是被真实尝试过的设计空间，不能重复包装成首次发现。
4. **源码边界与对我们的压力**：固定 `paper` 分支代码的 proposer reward 确为 `reward_managers.py` 的 `one_minus` 成功率转换；`constructor.py` 从 buffer 抽参考并复用已有任务，`coder7b.sh` 禁用了多个 intrinsic reward、设 8 次成功率采样。`python_executor.py` 直接执行候选 Python，README 明说研究版 executor 不安全；若未来借用资产，须用独立隔离执行器而非在共享 GPU 节点直接跑原版。补读 `absolute_zero_reasoner/trainer/ppo/azr_ray_trainer.py` 发现 `train_propose=False` 仍从**同一个会被 solver 梯度更新的** `actor_rollout_wg` 生成题，只是不把 proposer rollout 加入 policy-gradient batch；因此公开实现的 solver-only 不等于**冻结 proposer 权重**，不能拿论文 45.4 对 46.8 直接当“冻结生成策略”对照。此为代码语义，不推断作者实验有误。AZR 已拥有“可验证开放式代码练习＋联合 proposer/solver 训练”，也已尝试组合课程和简单多样性奖励。它仍未用真实训练干预核对每题的 proposer 奖励是否选出对**新学生/新任务**长期最有用的数据，且完整复制预算与我们不匹配；这是待测压力，不是从它的 reward 公式就自动成立的论文 claim。E09 的数学 teacher 错解表明可验证资产有吸引力，但换任务必须先确认强静态、**真正冻结**的 proposer 与 solver-only 实现三者的基线语义及实际训练效用。

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

## P21 — LESS（ICML 2024；2402.04333v3）

来源：[会议页](https://proceedings.mlr.press/v235/xia24c.html)、[全文](https://arxiv.org/html/2402.04333v3)、[官方代码](https://github.com/princeton-nlp/LESS)（本地 pin `8abf9628b9a814ac3045445eebc8ba3c908fdc78`）。阅读：主文方法/结果/相关工作/限制与关键附录，并审读官方 `train.py`、`get_info.py`、`collect_grad_reps.py`、`matching.py` 及数据入口；尚未运行或复现。

1. **形态与母问题**：从约 270k 多源 instruction 数据中，为少量目标示例选择有训练效用的 5% 数据；目标是目标能力的实际微调表现，而非词面相似。
2. **旧法具体失败**：BM25/DSIR/RDS 容易选同语言或同表面主题而非同推理能力；经典 SGD 梯度影响不对应 Adam 更新，序列平均梯度又因长答案范数较小偏向短样本。
3. **改变的前提与 idea 来源**：将目标示例对训练数据的影响近似为 warmup 轨迹中的 **Adam 更新方向 × 验证梯度**；用 cosine 处理长度偏差，用 LoRA＋随机投影压缩梯度库。与普通静态文本检索的距离是优化器与训练轨迹信息，不是改一个 similarity 名称。
4. **方法**：从候选池抽 5% 随机数据做 4 epoch LoRA warmup，保存逐 epoch checkpoint/Adam 状态；对候选求 Adam 更新特征、目标示例求梯度，投影到 8192 维；逐目标子任务取平均梯度、沿 checkpoint 加权 cosine，再对目标子任务取 max 排序选 5%。构建数据特征库贵，选新目标便宜。论文的 270k/7B 设置称 warmup 约 **6 A100·时**、梯度特征约 **48 A100·时**、17.7GB，选择本身 <1 分钟；本地缩小池子不能机械照搬这些时长。
5. **评测与消融**：Llama2-7B/13B、Mistral7B，MMLU/TydiQA/BBH 主结果三训练种子；另有 Pythia 尺度、GSM8K/TruthfulQA。Llama2-7B 的 5% LESS 对随机在三主任务为 **50.2 对 46.5、56.2 对 52.7、41.5 对 38.9**；更强的 25%/100% warmup 与 4 checkpoint 又胜过较弱 warmup/1 checkpoint，表明状态信息不是无关装饰。已有跨模型 LESS-T：Llama2-7B→13B/Mistral 可迁移，但 Pythia→Llama2 在 TydiQA 未胜随机（附录 D.5）。
6. **真正拥有与剩余压力**：拥有“梯度数据价值、优化器状态、warmup 状态、跨模型策略复用”的大块 claim；不能把换学生后效用变化或廉价梯度 proxy 首次提出。它承认 warmup/特征成本、序列级聚合含混、loss 与生成准确率不单调、单样本影响忽略数据之间相互作用。它评估的是固定池的一次目标选择，不是连续数据生成/修订中动作选择经验如何在新 episode 累积。
7. **对当前实验**：E04 的字符 TF-IDF 是故意廉价的 screening baseline，若它胜静态也不能宣布新方法；下一强选择近邻是 LESS 或适合 MATH 的同级梯度/优化器感知方法。若探索 I01，须把 LESS-T 已有跨模型成功与 Pythia→Llama2 失败作为约束，并测真实再适配成本/新状态收益，而不是再画一张 transfer matrix。
8. **源码适配边界**：`get_info.py` 的 Adam 模式直接要求 warmup checkpoint 目录中的 `optimizer.bin`；`collect_grad_reps.py` 对每条样本反传后投影，`matching.py` 将目标梯度重排为写死的 MMLU/BBH/TydiQA 子任务数。官方 training/data scripts 假定 Tulu 式聊天数据和原任务入口，依赖版本为 2023–24 年旧栈。因此把它搬到当前 Gemma/MATH 不只是换路径：需重建 checkpoint＋optimizer 状态、目标梯度与匹配聚合，保留原论文的 Adam/trajectory 思路并明确标注适配。这个代码审读不等于本地 strong LESS 基线已跑通。

## P20 — DoGE（ICML 2024；2310.15393v2）

来源：[会议页](https://proceedings.mlr.press/v235/fan24e.html)、[全文](https://arxiv.org/html/2310.15393)、[官方代码](https://github.com/Olivia-fsm/DoGE)。阅读：主文引言/推导/实验/讨论，附录计算与阶段课程；代码尚未本地复现。

1. **母问题和旧法缺口**：DoReMi 的两个 proxy 以相对 reference 的 excess loss 指导配比，与目标域平均泛化损失不完全一致；目标域不在训练池时也不直接适用。DoGE 把目标域 loss 的一步下降写成源域梯度与目标梯度的对齐，不需要 reference proxy。
2. **真正改变的前提**：训练数据的价值是它对**目标分布**的局部更新方向，而非自身 loss 或难度。82M proxy 上每域梯度构成镜像下降权重，时间平均成静态配比，再训练 124M/210M/684M base；目标可为全部训练域或池外域。最近邻为 DoReMi、ODM、gradient influence/LESS 和固定均匀配比，差别在目标梯度与显式跨域效应。
3. **可核对的实证**：SlimPajama 七域，82M proxy 10k 步；684M 的七域平均 perplexity DoGE **15.806**、uniform **16.526**、DoReMi-10k **17.172**、DoReMi-50k **16.124**，六个 5-shot reasoning 平均准确率 **52.29/50.59/49.79/51.49**。论文还做池外域、proxy 尺度和计算量消融；reported proxy 训练 82M DoGE 约 6 小时、DoReMi 约 39 小时，均在 4×A100 上。数字是其预训练设置，不能外推到我们的 24 步 SFT。
4. **与动态课程的关键结果**：作者把相同总域样本数按 2/3/10 段部署，阶段配比的平均 perplexity 没有明显超过全程静态平均；10 段每千步改权重明显更差。proxy 的在线重加权本身也不如同尺度、用最终静态配比训练的 base。这是“更频繁适配未必更好”的实证，但只覆盖该预训练域混合和目标；不能据此判所有 student-feedback 环路无价值。
5. **剩余压力与我们**：DoGE 用 proxy 上的一步梯度泛化做代理，最后主动将动态策略压缩成静态分布；它未展示在新学生持续生成/修订训练经验时何时必须重新决策。若我们研究动态决策，必须超过“固定最优/时间平均配比”及同成本 proxy，而非只优于随机。

## P22 — ADO（ICLR 2025；2410.11820v1）

来源：[会议页](https://proceedings.iclr.cc/paper_files/paper/2025/hash/923285deb805c3e14e1aeebc9854d644-Abstract-Conference.html)、[全文](https://arxiv.org/html/2410.11820)、[官方代码](https://github.com/yidingjiang/ado)。阅读：主文动机/公式/实验/讨论和训练附录；代码尚未本地复现。

1. **母问题和 idea 来源**：离线小 proxy 需要额外成本且跨模型/分词器可能不稳；作者先用昂贵 meta-ordering 实验说明好课程可以存在，再问能否在**正在训练的同一学生**上低成本发现。与 DoGE/DoReMi 的距离是取消离线 proxy、直接使用本轮 loss 轨迹；与 ODM 的距离是把 reducible loss 和学习速度分开，而非仅追高 loss。
2. **方法与前提**：每域拟合局部幂律 loss `epsilon + beta*n^-alpha`，学习潜力用导数 `alpha*(loss-epsilon)/n`；乘上域先验与近期该域采样比例的平滑 credit，再将当前偏好与全史平均权重混合，设概率下限。它刻意只估计**域对自身**的贡献，承认跨域效应和长程课程不足。warmup 5k 步，每 1k 步重拟合；论文 1.3B 设置 60k 步、约 125B token，拟合时间 <0.4% wall-clock。
3. **强基线和结果**：除了 Pile 原权重、DoReMi、ODM、uniform balanced，还补入按分词器得到的各域自然 token 份额 `Natural`。1.3B 七项零样本平均 ADO **0.590**，Natural **0.585**，DoReMi **0.575**，Balanced **0.557**；124M 为 **0.470/0.463/0.455/0.457**。Natural 在 Pile validation loss 上仍略好于 ADO；ADO 在 SlimPajama/FineWeb loss 更好。作者明说 simple Natural 意外强，不能只报 ADO 对弱静态方案的胜利。
4. **方法边界与定位**：ADO 的局部 fit 不精确预测最终 loss，论文只需要短期有效；自然 token 份额、目标域质量和跨域贡献会改变行动排序。最近邻 DoReMi、DoGE、ODM、LESS、Skill-it! 已占据“在线潜力/梯度选择/课程随学生变”大块空间。ADO 与 DoGE 关于动态/静态的不同结果来自目标、域定义、是否单学生在线适配、训练阶段和压缩方式的共同变化，**不能机械写成论文相互矛盾**；这提示我们在真实训练收益下测哪种状态信息值得支付更新成本。

## P31 — Actor-Curator（2602.20532v1；ICLR 2026 workshop 版本）

来源：[全文](https://arxiv.org/html/2602.20532)、[官方实现](https://github.com/actor-curator/actor-curator)、[workshop 版本](https://openreview.net/pdf?id=ticD6IcBQi)。阅读：引言/方法/全部主实验/限制、训练与硬件附录、官方 README；代码内部尚未执行审计，不能称复现或主会接收。

1. **母问题、idea 出生点**：RL 后训练时，固定或人工难度桶不能应对不断变化的 actor；只看当前成功率、绝对 advantage 也不直接估计一次更新对最终策略的帮助。作者把“挑哪些题”视为非平稳、部分反馈 bandit，提出在训练中同时学一个能泛化到新题的 curator。相对 ProCuRL/PCL 的变化是学习目标从成功率/决策边界转为**更新后的政策改进**；相对 SEC 的变化是问题级而非人工桶，且用 OSMD 处理部分反馈。
2. **信号到底是什么**：文章从 `J(pi_{t+1})-J(pi_t)` 的 performance-difference identity 出发，用旧 actor rollout、新旧策略概率比和旧策略 advantage 形成每题 `u_x`，再以采样概率校正并训练 Qwen3-0.6B curator。它不是“每个候选题都单独训练一遍学生并量下游准确率”；所有选中题共用一次 RL 更新，单题 credit 是小更新下的一阶近似。两阶段从 2048 候选抽 256 题、每题 8 rollout，前 20 步 curator dormant、5 步 warmup，OSMD＋proximal clip 限制策略波动。官方源码是 verl 0.5 fork；3B actor 原实验称同节点 2×A100 可运行，curator 额外训练 wall 约 9–19%（附录不同任务），并非免费。
3. **实证与强对照**：Qwen2.5-3B actor、GSPO，30k Countdown/Zebra/ARC-1D 与 12k MATH 问题库，比较 uniform、SEC（绝对优势桶）、PCL（成功概率接近 50%）；论文报前 100 步最佳验证值。Qwen2.5 上 ARC-1D AC **36.37** 对最佳其他 **27.87**，AIME24 **30.00** 对 **23.33**；但 MATH500 AC **81.00** 低于 uniform **83.00**。Llama3.2-3B-it 上 MATH500 **53.60** 对 uniform **52.20**，Zebra AC **47.12** 低于 PCL **48.25**。所以“policy-improvement curator 在所有任务稳定胜出”不是它的数据所支持的强读法。论文消融 absolute advantage、回归目标、GRPO 替代 actor 更新与 curator 尺度；未在正文明确给多训练 seed 区间，不能据单表放大细微差异。
4. **与我们的距离和剩余压力**：它已拥有“用训练后而非静态难度信号学数据价值”“在线状态相关选择”“问题级 bandit”这三项主要思想，I02 不能宣称首次。但它只选固定库中 RL 题、依赖可验证 reward 与 on-policy rollout，并在同一 episode 内更新 curator；开放式数据生成/修订的动作归因、训练 token/验证成本、跨新学生 episode 的改进器学习、长程外部效用仍未由这些结果回答。MATH500 与 AIME/ARC 的不同排序是值得理解的目标依赖压力，**不是**单凭表格就能产出的新论文问题。若我们转向 RL 设置，它必须成为强基线或明确定位边界。

## P32 — Effective Synthetic Data Curation Requires Group-Level Signals（2610.00779v1；2026-09-30 预印本）

来源：[全文及附录](https://arxiv.org/html/2610.00779v1)、[arXiv 版本记录](https://arxiv.org/abs/2610.00779)。阅读：引言、形式化、两组实证、诊断、related work、B.1–B.8 实验配方与 C 的推导；未发现可执行官方代码，未本地复现。**刚发布的预印本，不写成已接收主会。**

1. **母问题与 idea 来源**：大量合成文本由少数源反复改写，样本的独立质量/影响力分数既难分辨近似同质样本，也看不到同时训练时的抵消与放大。相关工作已包括单样本影响力（LESS/GradSim）、数据去重/质量过滤、以及已有的 group influence 和关系模型 GMRel/GREATS。作者的增量不是“首次发明群组”，而是把**合成数据占比**作为压力变量：先在个体 proxy 分数近似固定的组之间隔离交互，再比较真实预训练/RLVR 收益，最后用组内梯度离散度决定昂贵组评分的预算位置。
2. **方法改变的前提**：个体 proxy 为每个样本单独做一次更新后 reference loss 变化的平均；group oracle 为同一初始 checkpoint 对整组做**一次** AdamW 更新后的 reference loss 变化，不是整套下游训练后的精确 utility。主文和 App C 对理想化单步梯度更新推导：二者一阶相同，二阶差是 reference Hessian × 组内梯度协方差，绝对差上界由光滑度和梯度离散度给出。实际 group oracle 使用 AdamW，理论条件和实际优化器有距离；梯度离散度是选择需要 group audit 的诊断，不是最终学习收益的充分统计量。
3. **数据、模型、训练和结果**：预训练是 Repro-400M、Repro-Rephrased、FLAN 128 reference、组 5120/10240、400 步；RLVR 是 Qwen2.5-1.5B-Instruct、GooseReason、GPQA 128 reference、组 128/512、GRPO 100 步。构造池先用 BGE 20 类调组的语义覆盖，并把每组个体 proxy 控制在窄带；从组选定等规模训练集，和 random、individual proxy 对照。小组预训练八项平均 group **31.98**、individual **31.20**、random **30.86**；RLVR 六项 group **35.22**、individual **33.53**、random **34.21**。大组也同向，但各项差距不大且任务有异质性；平均值不是全任务都赢。随后 716,800 条、改写倍数 1/10/50 的预训练选择实验比较 GradSim、FineWeb-Edu、BM25 与 GMRel/GREATS，组方法在生成任务上更强。**强静态/随机并未被消除**：附录 Table 9 的 r=50 压力设定中，random **28.10**，GMRel **27.67**，GREATS **27.90**，均低于未续训 base **29.65**；主文说将 GMRel 关系权重调至三倍后才超过 random/base。附录列出同一个 seed 124 的训练配置，不能由此主张跨 seed 稳定性。
4. **算力与最重要的边界**：每个 group oracle call 从同一 checkpoint 处理整组并评 128 条 reference，1000 组的全量 oracle 本身昂贵。组内梯度离散度在已构造组上的 gap 相关性约 0.58–0.63；只抽 10% 组内梯度并 audit 20% 的组，top-10% 召回约 0.69 对全梯度 0.75，论文按累计显存×时间的模型估算成本约全 oracle 的 0.26，而不是实测端到端 GPU 小时节约。该预算分配只验证 oracle 排名恢复，未独立展示这种低成本混合打分带来的最终训练收益。组 oracle 实验是在固定 base 上先选静态训练集；没有连续学生状态、开放式数据生成动作、跨新 episode 改进器迁移。
5. **与我们的距离**：它明确拥有“合成数据需要组级交互”“仅用逐样本影响力可能失效”“用梯度多样性分配组评分预算”。如果我们后来发现数据动作集合的交互，不能把这一现象当空白。真正待测的是一轮生成/修订闭环在**变化中的学生状态**里，组级短程 reference-loss 是否足以选出长期外部收益最大的行动，以及昂贵训练反馈能否在新学生/任务上变成可复用决策；这些是问题空间，不是现成贡献。强对照至少包括静态配方、真实 group oracle/GMRel/GREATS 或与动作空间匹配的实现，以及数据量/质量/多样性控制。

## P33 — Group-Level Data Selection for Efficient Pretraining / Group-MATES（NeurIPS 2025 main；2502.14709v2）

来源：[主会页](https://proceedings.neurips.cc/paper_files/paper/2025/hash/e389ad5c08184ebecaf0640e01588489-Abstract-Conference.html)、[全文](https://arxiv.org/html/2502.14709)、[官方代码](https://github.com/facebookresearch/Group-MATES)。阅读：引言、related work、oracle 定义、方法、主实验、消融和配置/成本附录；官方代码入口已核对，内部训练路径未复现。

1. **idea 从哪里长出**：MATES 等已有单样本影响力预测把组选样近似为独立分数求和；作者先用贪心组 oracle 展示选到百余条时与单样本策略分叉且训练结果受影响。于是它不只增加多样性后处理，而是学习“给定此前已选样本，这条样本还有多少边际训练效用”的关系项；核心改变是目标从单点价值到训练路径中的条件边际价值。最近邻是 MATES、DsDm、Quad、GREATS/TSLOO 和经典 group influence，不是凭空创造交互概念。
2. **方法及评测**：从同一模型状态采样长度 10 的训练轨迹，每步真实更新并测 128 条 FLAN reference loss 的改变，用随机和极端分数 bootstrap 轨迹训练 BGE-base 关系影响模型；预测分数为个体影响 × 与先前选择样本的关系权重。全池推理先做 10k 个影响感知簇，再簇内贪心选择。DCLM 已清洗的预训练池、412M/1.4B/2.8B 三设置、两阶段、每阶段选 50%，22 项 centered Core score；这比只对未清洗数据做质量过滤更强。论文报告 Group-MATES core **0.23362/0.30747/0.36846**，random **0.21356/0.29456/0.35603**，MATES **0.22260/0.30288/0.36139**；去关系项时 412M core 降到 **0.22737**，说明组成信息确有贡献。
3. **成本及边界**：同文 Table 3 报目标模型分别约 **104/240/740 H100 小时**（8 GPU 训练），关系模型另约 2.7 H100 小时；Oracle 轨迹与推理也在 FLOPs 账中。它的数据动作是静态池内挑原始 pretraining sequence，目标是参考 loss 与预训练 Core score；未生成/验证新训练经验，未把选择器在新学生/任务 episode 上学习得更好的能力单独评估。它已拥有状态相关轨迹和关系选择，不能把 P32 的静态组实验当成整个近邻范围。

## P34 — BLISS: A Lightweight Bilevel Influence Scoring Method for Data Selection in Language Model Pretraining（ICML 2026 main；2510.06048v5）

来源：[主会页](https://proceedings.mlr.press/v306/hao26b.html)、[全文](https://arxiv.org/html/2510.06048)、[官方代码](https://github.com/MingruiLiu-ML-Lab/BLISS-Bilevel-Data-Selection)。阅读：方法/相关工作/实验与 D–K 关键附录；官方实现入口核实但未执行源码。

1. **idea 来源与差异**：外部强教师给预训练数据打分的成本和来源依赖很高，MATES 一步影响力又只看局部 checkpoint。BLISS 借 bilevel data reweighting：让小 proxy 在 score-weighted 数据上多步更新，以其验证 loss 反向训练 score model；同时通过与当前目标模型 logits 的 KL 对齐，让从头训练的小 proxy 跟上目标的状态。它相对 MATES 的 delta 是无外部预训练 oracle 的多步代理和动态评分；相对先前 bilevel 方法则是预训练规模与 proxy–target 对齐。不是“首次利用训练后反馈选择数据”。
2. **系统设定**：C4 分五个不重复 shard，每轮从 shard 抽 0.1% 训练 proxy/score，用 LAMBADA 作上层验证，取该 shard 分数前 20% 续训目标模型 10k 步。目标 Pythia 410M/1B（另 2.8B 用 1B 所选数据、LLaMA-0.5B 跨架构）；proxy/score 是 Pythia 31M/160M。目标模型与 score model 跨轮继承，proxy 每轮重置到 warmup，避免旧分布优化偏置；这个状态处理不能被我们的 I01/I03 忽略。Pythia proxy 每轮做 3k score 步、每步 1 或 5 次下层更新，另有 Hessian-vector hypergradient；使用了 8×A6000 DDP，多卡通信对本地弱互联不友好。
3. **强基线与结果读法**：与 MATES、DsDm、LESS、QuRating、SemDeDup、DSIR、random 比 25B token。410M 九项平均 BLISS **45.9**、MATES **45.7**、random **44.5**；1B 为 **47.9/47.5/46.4**。1B 表中 BLISS 对 MATES 的绝对增量是 **0.4pp**，多个单任务反向，不能把论文的 `1.7×` 达标速度写成终局准确率巨大优势；它还给 2.8B 迁移（第 3 轮 BLISS 49.0 vs MATES 47.6）和 LLaMA 0.5B 第 3 轮 45.65 vs45.01。评估的括号是题目标准误，非训练 seed 区间。score 跨轮继承相对每轮重置只 +0.4pp；无 KL 平均低 1.4pp，说明 proxy 对齐可能比“加更多更新步”更关键。
4. **成本与剩余压力**：论文账本 1B 25B token 总 FLOPs BLISS 19.53×10^19 vs MATES 19.97×10^19，数据选择 wall **11.82h vs30.32h**，峰值显存 **74.51GB vs63.52GB**。这是多轮预训练原始序列选择，不处理生成题答案正确性、生成/验证预算、组内冗余或外部目标准确率驱动的 data action；也没有新任务 episode 上改进器自身会不会学习的验证。我们若只提出“多步代替一步”“随学生动态打分”或“小 proxy 学数据价值”，会被它直接压缩；可发展的差距必须由真实生成/修订行动与终端收益上的决策失败实证支持。

## P35 — Data Selection via Optimal Control for Language Models / PDS（ICLR 2025 main；2410.07064）

来源：[全文与附录](https://arxiv.org/html/2410.07064)、[主会页](https://proceedings.iclr.cc/paper_files/paper/2025/hash/9ad4891facabf17aa11580686bacfe4e-Abstract-Conference.html)、[官方代码入口](https://github.com/microsoft/LMOps/tree/main/data_selection)。阅读：母问题、related work、PMP 方法、主表、动态信息消融、G 实现与 E 数据依赖扩展；代码内部未执行审计，不能称复现。

1. **idea 来源与最近邻距离**：普通离线选样依赖词面/去重/单 checkpoint 影响，在线课程又给目标训练管线增加开销。作者问能否在**训练前**估计一份对整个训练过程有利的静态数据集：把固定样本权重作为控制量，把下游 loss 沿训练轨迹的 AUC 作为目标，利用 Pontryagin 最大值原理给出必要条件。相对 DSIR/RHO-Loss/单点 influence，它引入训练阶段和下游目标；相对 DoGE/在线课程，它在小代理模型求分后一次性部署到多个目标模型。理论是必要条件，不是证明实际所选数据全局最优。
2. **系统与关键前提**：160M 代理模型先训练 50k 步，取 10k–50k 五个 checkpoint；每个 checkpoint 在 160k 个代理样本上做 100 步 SGD 内环、一个 outer epoch 求分；125M scorer 预测全 125B-token RedPajama CommonCrawl 池的分数，Gumbel top-40% 得到 50B token 静态训练集。实际目标 160M/470M/1B/1.7B 全部训练 100k 步、batch512、序列1024、约 50B token，AdamW＋cosine；以 LIMA 1030 条训练示例的 LM loss 为代理目标，另用九项 OLMo 零样本任务、MMLU、DCLM loss 评估。理论正文以 GD 推导，附录 C 给 Adam 扩展，而实际可行求分内环使用 SGD；不能把它说成沿最终目标 AdamW 轨迹精确反传。
3. **强对照与真实结果**：对常规均采、RHO-Loss、DSIR、IF-Score，470M 九任务平均 PDS **48.2**、常规 **47.0**；1B 为 **51.0/49.3**，IF-Score 49.0。160M 的多阶段 10k–50k 选样平均 **45.0**，单步内环 **44.6**，只用 50k **44.0**，晚阶段 50k–100k **43.4**；改善存在，但多阶段对单步的实际终点增量是 0.4pp，不能夸张成短程 proxy 全面失效。Table 4 报求分 **15.2h**、scorer **1.5h**、筛选 **10.2min**，对照 1.7B 预训练 **144h**；约 400B 模型效果只是 scaling-law **外推**，没有实际训练。
4. **它拥有与留下的压力**：已拥有“离线多阶段/长时域信息能产生强可复用静态选样”“小代理求分迁移多个目标尺度”，因此 I01/I03 不能把长时域或跨学生复用当首次贡献。其策略一次求分后冻结，动作是固定网页语料池选样，不含新题生成、答案验证、状态反馈后重决策或跨 episode 改进器训练。作者在附录 E 明确讨论样本依赖及 pairwise diversity 扩展，故“发现逐条分数忽略相互作用”也不是空白。更有价值的待测问题是：**何时静态可复用策略真的不够，且额外反馈足以改变开放式数据动作的终端收益排序？** 要用多状态的真实学生训练及同成本静态/代理基线回答，而不能由数学公式推断。

## P36 — Learning at the Right Pace / ADS（2606.22305v1；预印本）

来源：[全文与附录](https://arxiv.org/html/2606.22305)、[代码入口](https://github.com/Richard-zrx/ADS)。阅读：引言、算法与 RL 目标、7 项主结果、强 DOTS+RR 基线、OPD/DAPO/GSPO 扩展、跨学生聚类、消融、附录成本/限制；代码内部尚未审计或复现，不写成已接收主会。

1. **母问题与 idea 来源**：GRPO 在题目全部答对/全部答错的 rollout 组上相对 advantage 接近零，因此随策略能力移动的题目边界是**训练目标造成的真实数据价值压力**。DOTS+RR 已根据难度在线选题并复用 rollout；ADS 认为平铺逐题选择会让相关语义模式交替出现、难以巩固，于是用 base 模型的题＋解嵌入先固定 64 个语义群，再同时调群的采样概率和群内接近 50% 成功率的题。相对 DOTS+RR 的新 delta 是双层时序/语义组织，不是首次发现中等难度或在线课程。
2. **方法前提与非任意性**：每步用选中群的 rollout 成功率更新群概率（目标是按成功率归一化，指数平滑 0.3），在群内按当前答对率是否落于 [0.33,0.67]，将过难/过易题沿预计算难度排序向边界替换。每 epoch 重置 schedule，以免旧策略状态污染。群内边界条件直接来自 GRPO 的有效相对优势；“高成功率群优先巩固”则是一个额外课程假设，群/样本消融支持有收益但尚未单独识别其机制。
3. **数据/训练/评测**：OpenR1-Math-220k 的 94k prompt 经 8192 长度与 Math-Verify 正确性过滤为 46k，再固定抽 11.5k；Qwen2.5-Math-1.5B、Qwen3-4B-Base、OLMo3-7B-SFT，verl 中 rollout batch128、每题8 rollout、LR1e-6、最大训练生成8192。七个数学/科学 benchmark，以 16 次采样的 Mean@16 和 Pass@16、三 run 报告，checkpoint 按 validation 选最佳。Qwen2.5 主平均 Mean@16：ADS **28.05**、强 DOTS+RR **25.27**、GRPO **21.57**；OLMo3 为 **30.06/26.70/22.38**。仅说相对 uniform +5.2pp 会掩盖已存在的在线强对照。Qwen2.5 去群调度/去群内调度为 **27.08/26.94**，两部分均有约 1pp 边际读数；在 OPD、DAPO、GSPO 上亦有提升。跨 Qwen2.5/OLMo3 交换离线聚类，平均仅小幅变化，说明语义划分有一定复用性，不能声称首次测跨学生迁移。
4. **计算与资产**：离线嵌入＋聚类/难度预处理 1.5B/4B/7B 为 **15.5/21.5/26.6 分钟**，作者换算约 6/9/3 个 RL step；表中基础硬件为 4×H200 141GB，且在线每步8 rollout/题。代码已公开但本地未核完整版本和复现路径，不能把其 GPU 成本视为单 A100 小 SFT 可直接承受。
5. **它拥有和没回答的**：已拥有语义群×能力边界的动态 RL 数据排程、强逐题在线基线、跨目标/模型结果。其动作只是在固定、有正确答案的 pool 中调度题目，适用于可验证 binary reward；没有生成/修订新经验、答案验证、跨独立 episode 学会做更好干预，或 SFT 中的真实后续训练效用。若改做数学 RL 数据策略，它及 DOTS+RR 是核心近邻，不能用“learner-specific curriculum”空话绕开。与 P31 Actor-Curator（post-update 近似效用）、P35 PDS（离线多阶段静态）、P04 DataEnvGym（开放式教师闭环）比较，最可能值得实测的缺口是**当前成功率与终端训练效用的排序何时分开、昂贵反馈是否值得重新决策**；这仍是问题种子，不是本地发现。

## P37 — Montessori-Instruct（ICLR 2025 main；2410.14208v1）

来源：[全文与附录](https://arxiv.org/html/2410.14208)、[会议页](https://proceedings.iclr.cc/paper_files/paper/2025/hash/ba1d33849b963efc6b5d3082ad68f480-Abstract-Conference.html)、[官方代码与数据](https://github.com/cxcscmu/Montessori-Instruct)。阅读：引言/related work/局部影响定义、teacher DPO、全部主表/消融/跨学生迁移、训练及成本附录；官方实现内部待审，不能称复现。

1. **母问题与 idea 从近邻长出**：Self-Instruct 类 teacher 把少量 seed 改写成大量指令，却不知道合成数据是否真的推动目标学生学习；LLM judge 的表面质量、追随错误的 LLM2LLM 和数据影响理论分别只给部分答案。作者把此前的局部单例 influence 测量接到**教师参数更新**：用同一 seed 下影响为正/负的指令对做 DPO，让 teacher 学生偏好的题目分布，再生成下一批数据。相对 DataEnvGym，重点不只是观察学生错误和生成样本，而是从训练响应**更新 teacher**；相对 LESS/影响函数选择，它改变数据分布生成器而非只选固定池。这是有因果动机的 delta，但一次更新后的 reference LM loss 仍是终端训练价值代理。
2. **具体方法、资产与训练**：Llama3-8B-Instruct teacher，从 Alpaca GPT-4 的 52k seed 抽 6 个旧例＋2 个前次合成例，先生成 probing 指令/回答；Llama3-8B 或 TinyLlama-1.1B student warmup 后，对每条 probing 样本单独做一步 Adam 更新，以 Alpaca GPT-4 reference **token loss 前后差**记 local influence，组成 6792 个正负 preference，teacher DPO，再生成 10k 指令数据做 student SFT。teacher/student 各一 epoch，AdamW+WSD；8B full-parameter FSDP，另有后续多轮。它并非每条候选完整训练学生后用 held-out 任务准确率标注。官方公开代码和生成数据，但本地未审内部实现。
3. **强对照与读数**：同量 Self-Instruct、GPT-4o teacher、外部 GPT-4o judge 版 Self-Reward、从高训练 loss seed 追错的 LLM2LLM 都列入。Llama3-8B student 的 Alpaca Eval 2.0 LC-WR：Self-Instruct **50.00**、GPT-4o Self-Instruct **54.95**、LLM2LLM 第二轮 **52.63**、Montessori 第一/二轮 **54.92/56.82**；MT-Bench **6.490/5.918/6.519/6.903/7.092**（相同次序）。局部 influence 对 teacher 更新的第一轮 LC-WR **54.92**，训练 loss 或 LLM judge 替代分别 **52.34/53.42**；只 bootstrap 数据、改回答而非指令分别 **50.59/51.59**。但它不是所有外部指标皆胜：8B 第二轮 GSM8K **59.98** 低于第一轮 **62.97**，主文的平均胜率不能代替每个任务。其 teacher 针对 1.1B 优化的数据在 Llama3-8B/Mistral7B/Qwen1.5-7B/Gemma2-9B 上仍胜 Self-Instruct，已拥有**跨学生迁移的正例**。
4. **成本与证据边界**：附录给 8B 单候选局部影响计算约 **13.403 秒**（含重载 2.69s、一步训练 4.12s、reference eval 4.19s），使用 8×H100 独立并行；最终成品每条数据 Self-Instruct 0.486s 对其 5.842s，额外成本是真实的。10k 生成量，对生产级 100k 的冗余作者未验证。参考集来自 Alpaca GPT-4，主评价 Alpaca Eval/MT-Bench 又偏通用指令偏好；跨 benchmark 是优点，但没有证明一步 reference loss 的排序对开放式数学/代码生成数据的**最终训练准确率**仍可靠。8B/1.1B 与几个迁移模型都在同一任务族，未检验跨独立任务 episode 的教师决策能力是否积累。
5. **对我们不自动判死的约束**：I01/I02 不可 claim 首次训练响应塑造教师、首次学生偏好影响合成、首次生成策略跨学生复用，也不能把单例局部 influence 本身当新方法。若以后出现真实的“局部代理与终端组训练收益排序反转且决策损失大”的证据，再考虑为新目标/行动结构提出最小方法；须与 Montessori、LESS、P32 组代理及强静态数据在同成本下比较。当前 E10 尚只资格测量，不借这篇论文替本地数据背书，也不因其存在关闭选题。

## P38 — The Signal is in the Steps / LALP（ICML 2026 main；2510.03988v2）

来源：[全文与附录](https://arxiv.org/html/2510.03988)、[主会页](https://proceedings.mlr.press/v306/just26a.html)、[论文所列代码入口](https://anonymous.4open.science/r/lalp-5272/)。阅读：引言/related work、GRAPE 阳性对照、方法、全部主表、附录 B/C 的训练与选择细节、成本；代码内部尚未审计/复现。

1. **母问题、失败、idea 来源**：GRAPE 按学生对整条答案的平均 log probability 选“自然”的短答案；同 teacher/短回答时，P38 也验证高分组胜低分组，故不是将既有方法设为稻草人。作者随后把选样任务移到**多 teacher、长推理链、每题多条正确答案**；不同 teacher 的答案风格/长度差异，使全局概率选出的 teacher 顺序与实际 SFT 后效用反转。idea 是把“学生自然性”从整条轨迹改成局部推理步骤：LLM 分割步骤，每步只看题目和最近少量前步算 token 平均 logprob，再对步骤等权平均。相对 GRAPE 的 delta 是评分粒度与上下文条件；相对过程奖励，它不是判每一步正确性，而是无外部判别器的学生条件化数据筛选。
2. **数据、训练和主结果**：MATH level3–5 约 8890 题作单 teacher 短答案阳性对照；LIMO **817 题**的正确答案分别由 DeepSeek-R1/QwQ-32B/Qwen3-32B 生成，多 teacher 选择使用每题一个答案。学生 Qwen2.5-7B/32B-Instruct，另有 Llama3.1-8B；LLaMA-Factory SFT，附录列 batch/device 1/2、梯度累计8、LR 5e-6/1e-5、10/15 epoch，使用 4×A100，具体两档超参对应实验需核代码。七数学 benchmark 平均：32B 原始 **0.445**、random **0.651**、GRAPE/GALP **0.632**、LALP **0.726**；7B 为 **0.353/0.407/0.412/0.440**。单 teacher 最好 QwQ **0.719**，与 LALP 的 0.726 仅差 0.007；因此大部分相对 GALP 增量也可能由**选到更多好 teacher**解释，不能只引用 +9.4pp。附录的 teacher 构成：32B GALP 仅 **7.2% QwQ**，LALP **36.3% QwQ**；teacher-prior/按 teacher 分层选择是未来重要强对照。论文还评 GPQA-D 和代码；GPQA 的 32B GALP **0.611**、LALP **0.702**，代码另用 5000 OpenCodeReasoning/LeetCode 题 SFT 后 LCB hard **0.232/0.261**，不能误读成数学模型零样本转代码。
3. **机制证据的精确读法**：作者的 step embedding 最近邻覆盖 **0.935** 对整链 **0.760**，支持“可重用局部模式更多”，但不同粒度/候选数的余弦相似不可直接证明训练机制。缩小局部上下文时 teacher 排序正确，扩大时趋近 GALP；这比单张 t-SNE 更贴近方法因果。附录还显示 GALP 数据训练 loss 降得最快但终点 accuracy 较差，是“易拟合≠有用”的实例。按 token `exp(logprob)` 归因的表将 discourse 42.3%→18.7%，但这是作者定义的概率质量诊断，不是独立验证的逻辑正确性标签。GLM-4.5-Air 分割长链、每步骤另做前向推理，评分额外成本和分割依赖真实存在；文中未给相当于 student SFT 的完整可比账本。
4. **它拥有的主张、剩余压力**：ICML 主会已拥有“异构正确长答案下全局学生自然性可能错排、局部步骤评分能修复，且跨数学/科学/代码有效”的核心叙事。若我们转研究答案/teacher 选择，不可只做另一个局部概率指标或重讲“loss 不代表 utility”；必须先控制 teacher quality mixture、response length/step length、分割成本，并证明新增失败具有实际训练后果。当前 E10 是 **金标题目选择、每题单答案**，不是 P38 的 setting；它启发对数据动作粒度与终端效用作实测，但不构成 E10 结果的解释，也不自动否决开放式数据干预问题。

## P39 — OpenMathInstruct-2（ICLR 2025 main；2410.01560v2）

来源：[全文与附录](https://arxiv.org/html/2410.01560)、[主会页](https://proceedings.iclr.cc/paper_files/paper/2025/hash/302ce0673c00aee2cf84bb43d0117553-Abstract-Conference.html)、[数据卡/复现入口](https://huggingface.co/datasets/nvidia/OpenMathInstruct-2)、[官方 NeMo Skills](https://github.com/NVIDIA-NeMo/Skills)。阅读：引言、方法、主表、相关工作、A–C 附录、发布数据字段；NeMo Skills 内部训练流水线待审，不称源码复现。

1. **领域母问题和 idea 的来源**：当时强数学 SFT 数据多为私有，难复核污染与“生成什么数据”真正有用。OpenMathInstruct-1 已对现有 MATH/GSM8K 题生成答案，但问题多样性受 7.5k/7.4k 原题限制，强开源 teacher 的出现又改变了解答质量上限。作者并未声称首次合成数学题；它在可发布的 405B teacher 上系统拆开**答案格式、教师强度、错误过滤、题目多样性**，由 ablation 决定大规模数据配方，并对生成新题做较昂贵的 LLM 去污染。相对 MuggleMath/MetaMath 的 delta 是强开放 teacher＋数据配方量化＋发布质量/去污染链；其任务是造一份强**静态**语料，不是学习随学生改数据的决策器。
2. **关键可核对实证**：Llama3.1-8B-Base 上，较短 OpenMath CoT 对默认 verbose Llama CoT 的 MATH validation 为 **44.5±0.8 对 40.6±0.6**、平均解答 token **237 对 331**；在问题覆盖匹配后 405B teacher 对 8B-Base teacher 是 **37.9±0.6 对 30.1±0.6**。用 judge/reward 模型过滤 6–12% 可疑解答并未胜未过滤 **43.6±1.7**；人为加入最多约 20% 低质量数据，在其 256k+ 规模下也几乎不伤性能。固定 256k 题解对，将 unique questions 从 1k 增到 6.5k，MATH validation 高约 **10.5pp**。这些结论与 E10 的 120→960 单 seed 不能直接相冲：模型、原始数据、训练预算、样本量和控制变量完全不同。
3. **数据/训练/成本与局限**：最终 13.97M 题解对、607.3k unique questions，其中原 MATH 问题约 2.46M 答案、新 MATH 问题约 8.94M 答案；对新题每题采 32 个 405B 答案，取多数答案，附录提高 majority 阈值 0→8→16→24 时选中数据 381k→339k→254k→160k、验证准确率 **50.1→49.2→44.4→42.0**，不能把“验证越严越好”当普遍原则，且表中数据量未匹配。其新题 decontamination 用 embedding top5＋405B 双序 LLM 判断，每题多达 10 调用，主要对公开 MATH/GSM8K/AMC/AIME 测试，**不覆盖我们自建的 MATH-train dev1740**；若借用数据必须重新查本地 dev 近重。主结果 8B full SFT 2 epoch/batch512/LR2e-5，5M/14M 规模，还做 checkpoint 平均；MATH test **67.8**，不与我们的 Gemma2-2B LoRA/1740 dev 直接比较。论文数据许可证 CC-BY-4.0，四字段是题、生成解、预期答案、`problem_source`，约 12.6GB parquet；可只读取 236MB 左右单 shard 做小资格测量。
4. **我们能从中推进什么**：它拥有“强 teacher、短格式、题目多样性及粗过滤常已够强”的大块数据科学叙事；不能把 E10 偶然更差写成“首次发现多样性不重要”，也不能把“答案正确≠有用”当新发现。下一步更有区分力的是在**相同学生和训练预算**上把原题换强 teacher 的另一份解答、或换新可核对题目，先判断动作空间哪个维度能改变终端训练收益。若强静态合成数据吸收反馈增量，应保留这个成功；若它也不提供可测状态，则可能是当前 Gemma/短 SFT substrate 不适合支撑我们的主会问题。此为候选实验设计，不把文献外推成本地发现。

## P40 — DUET（ICLR 2026 main；2502.00270v3）

来源：[全文与附录](https://arxiv.org/html/2502.00270v3)、[官方源码](https://github.com/chenzhiliang94/BO-for-LLMs)（本地 pin `146c29e0168a33c6d946a30f640f98933bfbc6e9`）。阅读：引言/related work、3 节算法、6 节主实验、A/C/D/E–H 成本与边界；核对开源 `BO_run_optimization.sh` 和 `BO_utils/BO.py` 的 BO 初始化与训练评估入口，**尚未本地运行**。这篇是 E12 之后反馈策略的直接强近邻，不应只看摘要。

1. **母问题与来源**：用户任务内容可能不可见，只返回粗粒度、带噪的总体表现；DoReMi/LESS/DoGE 等需要目标任务的细粒度信息，纯静态混合无法根据真实部署反馈改变数据。DUET 不把“有反馈”本身当新意，而把**黑箱反馈条件下的数据比例搜索**写成外层 BO、域内可选的强样本选择写成内层估计。其相对传统混合方法的 delta 是在无目标样本/梯度的前提下，仍用真实训练后评估闭环优化；相对一般 BO 的 delta 是把配比与域内样本选择分解。若删除新方法，单个域选择或均匀混合不能利用目标反馈，暴力枚举混合又太贵。
2. **方法具体改变什么**：每次从**同一个父模型重训**给定 10k 样本的策略，GP/LCB 在域比例单纯形上选下次比例；域内可用 IF/LESS/随机等选择，更新 GP 后保留已见最佳模型。论文另有 IF 估计的阶统计与 regret 分析，但固定有限样本数的界非零，不能把公式解读为无条件有限预算最优。BO 方法假定动作可以由**固定域比例向量**表达，且单个目标任务在搜索期间保持不变；它没有跨独立任务 episode 学到可直接部署的 data improver，也没有开放式生成/改写动作。相近工作为 LESS（目标梯度静态选样）、DoReMi/DoGE（域混合代理）、Aioli/多保真 BO（混合优化）、Curation-Bench（开放策略家族与 agent 轨迹）。
3. **实验证据与 compute**：9 个训练域、Llama-3-8B-Instruct LoRA 与 Qwen2.5-7B-Instruct，10k 样本/轮、10 个 BO 迭代、3-shot `lm-eval-harness`，包括同域 TruthfulQA 和排除对应训练域的 GSM8K/QA 等目标；另在附录 D 做 8B/14B 全参训练。Llama3 四目标的 DUET-IF **59.8/84.2/52.4/69.6**，DUET-LESS **58.7/80.5/50.8/67.6**，对 Aioli **51.1/76.5/48.8/63.7**；主结果确实不只是比 uniform。每次 8B LoRA 在 L40 约 1h，IF 的一项 TriviaQA 170k 样本估计用 4×L40 约 2–3h，作者报告其它强对照、多 token/epoch、域内选择消融。**成本口径特别注意：**§6.1 明说 GP 先用 **50 个随机数据混合的训练评估** warm-start，然后再做 10 BO 轮；附录 C.1 的“10h”只算后 10 轮，不足以表示整套前置搜索成本。当前开源通用脚本默认 `NUM_INITIAL_RANDOM_SAMPLES=10`、`ITER=50`，不是论文这个 50+10 的现成一键复现命令；若以后本地用 DUET 思路，必须显式锁定并记录初始化/总试验数。
4. **它拥有与余下压力**：已拥有“真实下游黑箱反馈可改进固定域数据混合”“简单随机域内采样 + BO 是强对照”“反馈混合能跨多个任务/学生存在”，所以不能把 E12 后源比例搜索或 BO 包装成新发明。相对 Curation-Bench 的 agent，它的动作空间更窄、可解释且是强非 agent 自适应对手；即使 E12 的均衡混合意外很强，也不能只与开放提示 agent 比。真正未答的是：在**同等总试验成本**且有更宽的可验证数据动作时，什么观测让策略家族切换优于这种比例优化。后读 P41 Data Mixing Agent 发现其**已经**学习跨新学生/目标域可迁移的固定域配比策略；因此“从一个任务的经验在新 episode 减少搜索成本”不能单独成为我们未被拥有的 delta，必须具体到其固定域动作无法表达的训练决策。当前只是有定位意义的 competing explanation，没有我们的数据支持，不能因此自动 kill I02 或生成式领域。

## P41 — Data Mixing Agent（ACL 2026 主会；2507.15640v2）

来源：[ACL Anthology 正式记录](https://aclanthology.org/2026.acl-long.427/)、[全文/附录](https://arxiv.org/html/2507.15640v2)。阅读：引言/MDP/方法、主表、迁移结果、C/D/E 附录及 limitation；尚未核实可运行的官方源码，不称已复现。该篇由 venue corpus 对“跨新任务学数据改进器”的针对性检索发现，是 P05/P40 之后直接需对齐的近邻。

1. **母问题、idea 来源与最近邻距离**：领域持续预训练既要学目标域又要保留通用能力，人工固定源/目标比例和 RegMix 的静态 proxy 拟合难表达随训练进程变化的配比。作者把配比课程形式化成历史动作＋小评估反馈→下一域比例的策略，并用离线轨迹学习。相对 DBL 的当前域 excess-loss 规则、RegMix 的静态混合回归，其 delta 是把多步决策**学成可迁移的轻量策略**；相对 DUET 的每个目标重新 BO，它先支付大量代理轨迹成本后可不重训改进器；相对 Curation-Bench，它学的是固定域连续配比而非开放式策展程序。删除新方法后，强对照仍可优化静态比例或在线依据 loss 调度，但论文报告它们在保留源能力和目标收益的共同目标上落后。
2. **具体方法与信号**：行动空间是源/目标数据在 2 维或分类后的 **52 维固定域比例**；输入是此前比例和每阶段评估向量。用 50M 参数 LLaMA proxy 训练 **384** 条启发式覆盖的配比轨迹，收集 **27,266** 次阶段反馈；反馈来自 MMLU 验证及 MATH 小集合上的答案平均 token log-prob，而最终用标准任务准确率评估。策略是约 **2.1M** 参数、两层 Transformer decoder，先用好轨迹 SFT warm-up，再用 CQL 学好/坏动作；部署时在同一学生的持续训练中反复读反馈并改下一阶段比例，不是每次从父模型重训一个完整候选。源数据 100B token 预训练池、数学 Dolmino-mix 10B、代码 SlimPajama-DC 30B。不能把“反馈→动态混合”或“跨学生/任务复用数据策略”写为我们的首创。
3. **关键实证与成本口径**：3 个从头预训的 LLaMA-3B（DCLM/FineWeb-Edu/Nemotron-CC）和 Pythia-1.4B，8 通用＋4 数学任务、2 代码任务；LLaMA-DCLM 的数学设定 12 任务平均 DataAgent-RL **47.03**，RegMix **44.01**，DBL **43.50**。将数学训练好的 agent 原权重直接用于代码，不重训 agent，在 LLaMA-DCLM 的 10 任务平均 **46.30**，RegMix **44.85**，但其通用任务相对数学设置下降，论文自己承认任务依赖/失配。代码轨迹只在 2D 域空间评估，非开放动作迁移。主表 LLaMA-DCLM target GPU 时间约 **1,891.84 小时**；论文另以 64×A100 做 3B 目标持续训练，且 384×50M 代理轨迹和 27,266 次反馈的前置成本须与部署成本分别计，不能只称部署 agent 很轻。论文未在本文中给出可直接用于我们 VL 10k 筛选的策略或可核实的完整公开实现。
4. **它拥有/未解与我们的研究动作**：它明确拥有**跨新目标模型、源数据和数学→代码目标域的冻结策略迁移**；因此 P05 Table 24 未报告跨 episode 学习，并不意味着领域无人做。它没有比较开放式数据筛选/生成/修订的策略家族选择，也没有在每个候选同父模型重训的黑箱策展环路验证这种转移，更没有证明其 52D 权重策略能处理动作家族切换。但这些差异只是 setting，不自动是主会贡献。若 E12 真实效用显示源比例或强静态已够好，应首先尊重 DUET/P41；只有出现**同成本强比例方法解释不了、且新 episode 有可复现决策收益**的具体失败，才考虑跨动作家族改进器。最危险替代解释是训练剂量/域比例已解释一切；当前没有我们自己的证据。

## P12 — CurateEvo: Data-Curation Evolving for Agentic Post-Training（2607.06140v1；预印本）

来源：[全文及附录](https://arxiv.org/html/2607.06140)。阅读：引言/related work、策略目标与反馈、SFT+GRPO 配方、主表/消融/资源附录与最终代码策略描述；截至本轮未核到官方可执行代码，未复现。它是 **预印本**，不能写成已接收主会。

1. **idea 来源及最近邻距离**：已有代理后训练工作擅长增加交互轨迹，但过滤、修订、推理记忆及不同环境失败模式的联合策展不足。作者把“数据策展程序”本身变成可执行代码，每轮从同一 Qwen3-4B base 重训，再用开发集失败轨迹让 GPT-5.4/mini-SWE-agent 改代码；相对固定数据扩增方法，delta 是反馈下同时改变 SFT/RL/记忆资源和训练轮数成本。它不是首个失败驱动数据生成，但明确拥有“失败轨迹→重写策展代码→真实重训收益”的核心链条。最接近的实质近邻是 DataEnvGym 的学生反馈生成、Curation-Bench 的自由策展策略搜索、MUA-RL/EnvScaler/RODS 的轨迹/环境扩增与 agent memory 路线；不能以“代码会自我演化”做我们的空白 claim。
2. **方法/目标的真实边界**：3 个 evolution epoch，分别对 labeled 与 wild raw corpus 重新演化独立策略；每轮 9:1 原始语料划分的 dev 失败进入代码改写，ACEBench-Agent、BFCL-V4、τ²-Bench 作未参与演化的最终测试。先修效果，再按保留训练 turn 数惩罚修效率；最终数据产物同时包括 SFT、RL 与推理时 memory。训练是固定 SFT+GRPO，LoRA rank16；SFT 最多140步、LR2.5e-5，GRPO LR5e-6。它的“跨数据环境有效”是重新适配后的系统表现；论文没有报告冻结旧 episode 的代码策略直接移到新 episode，或策展 agent 本身在跨 episode 上越来越会选行动。推理 memory 混入终局指标，故不能把全部收益归于参数更新中的训练数据；作者有去掉 memory 的消融，不能说完全没有拆分。
3. **实证/成本/强弱**：主表 Qwen3-4B 的 labeled 三任务 **56.7±0.6/52.4±1.0/41.9±0.6**，wild **55.8±1.4/50.0±0.6/37.2±1.2**，相对所列最强旧方法平均 +3.2/+2.7 分；部分旧法用 Qwen3-8B，训练配方并非全同，不把这些数值当 matched-cost 策展作用量。去掉效果修订的六格约降 6–8 分，去掉效率修订约降 1–1.5 分；去掉 SFT、RL、memory 各有损失。论文给每 1k 保留训练 turn 策展开销 **0.51M token/405s**，但未给完整 3 轮重训＋评测＋LLM 的统一 GPU/API 总账；不能据该局部口径断言端到端比强静态/普通优化器便宜。最终策略把决策片段分别放进参数学习与检索记忆，这是该论文有意义的设计选择，非我们可直接重复的新 idea。
4. **对我们真正改变的判断**：I02 若只说“看错题、让 agent 改数据代码、多轮重训”已没有足够 delta。E12 仍有价值，因为它精确量同一固定 SFT 行动空间中强静态效用和评估成本；下一阶段如研究“什么反馈值得拿来决定开放数据动作”，需在同总试验预算下证明失败轨迹指导、训练干预信息与简单 optimizer 的**决策后果**不同，并在新学生/任务 episode 测改进器是否迁移。CurateEvo 的不同设定不是可自动利用的漏洞，必须以实测瓶颈产生问题。

## P43 — Data Agent: Learning to Select Data via End-to-End Dynamic Optimization（ICML 2026 main；2603.07433v2）

来源：[主会页](https://proceedings.mlr.press/v306/yang26bq.html)、[全文](https://arxiv.org/html/2603.07433)、[官方代码](https://github.com/Jackbrocp/Data-Agent)。阅读：母问题、static/dynamic related work、PPO/奖励公式、视觉与 LLaMA 主表、消融、成本表及开源 README；未运行代码，README 的公开执行入口主要是 CIFAR，不能称大模型配方可直接复现。

1. **idea 从哪里来**：固定选样不能跟上学生状态；已有动态剪枝依赖 loss/不确定性启发式。作者令三层 MLP PPO actor/critic 读取学生特征，逐步给样本动作权重，再以训练 loss 与预测熵的加权奖励学在线选择策略；权重按两种奖励的方差比自适应调。其 delta 是**目标训练内**学逐样本策略、低额外前向成本、跨多视觉训练范式可套用，而不是在同父重训的多候选研究 episode 中从终端验证反馈学下一次数据方案。
2. **实验归属**：CIFAR/Tiny-ImageNet、ImageNet-1k 的 ResNet/ViT、YOLOv8、ADE20K、LLaMA-7B 指令微调均有实验。ImageNet-1k 60% 选择时 ResNet50 **76.8** 对 full **76.4**、InfoBatch **76.5**，总 GPU 小时 **85** 对 full **140**、InfoBatch **84**；因此增量重点是相近成本下小准确率收益，不应写成全面更便宜。LLaMA-7B 的 MMLU **36.9** 对 full **34.9**、随机 50% **34.6**，AlpacaEval2 LC win **7.7** 对 full **6.7**；表中没有 LESS/DUET/Curation-Bench 同协议对照。去掉动态权重、仅用 loss/熵和直接按组合奖励 top-k 均有消融，不能说论文没对简单规则。主表没有清晰多训练 seed 区间，微小差需谨慎。
3. **对我们的边界**：该工作已经拥有“agent 在线学数据策略”“随学生状态变换样本价值”“loss+uncertainty 自适应课程”，P41 还拥有固定混合策略跨任务冻结迁移。我们的可能增量只可能来自不同的**真实决策目标与动作空间**：例如终端训练收益而非训练 loss/熵、生成/修订而非保留既有样本，且必须拿它可适配的简单动态规则做成本匹配对照。现阶段这只是 novelty pressure，不据论文标题关闭 I01/I02，也不为它开新的弱协议实验。

## P44 — Can Small Training Runs Reliably Guide Data Curation?（2512.24503v2；预印本）

来源：[全文与附录](https://arxiv.org/html/2512.24503)。阅读：问题定义、§4–7、相关工作分类、D.1–D.2 的训练配方/机制/训练时长；未核到官方可执行代码，未复现。**此文研究预训练代理与大模型迁移，不是 Curation-Bench 的 LLaVA SFT 实验。**

1. **母问题和 idea 来源**：数据团队常以同一小模型、同一超参训练候选语料，实际目标模型却会针对入选语料调参。作者先显示小模型上只改学习率即可颠倒两份 DCLM 去重配方的排序，再把数据质量目标改成“目标模型在该数据上完成自身调参后的最好成绩”。相对 DataDecide/DoReMi/配比代理法，关键 delta 是**评估协议的目标函数**与其低成本近似，不是又一个难度/相似度分数。
2. **方法、证据和前提**：在固定训练预算下让代理使用比常规小 1–2 个数量级的学习率，试图压低高阶优化效应，保留与验证梯度对齐的一阶信息；随机特征模型给排序保持的条件，不是深度 Transformer 的通用保证。23 个预训练配方涵盖域比例/排除、C4/DCLM/RefinedWeb、RP2 质量桶及去重阈值；代理 GPT2-125M/Pythia-70M/OPT-125M，目标 GPT2-774M/Pythia-1B，目标每配方按 LR×batch×weight decay 网格调参，20 token/parameter、单 epoch、Pile loss 与五个下游任务。标准代理 LR 排序相关低于 0.75，低 LR 在三架构高于 0.92；以 GPT2-125M→Pythia-1B 的 23 配方为例报告超过 0.95。另报 top-k 选错后目标 regret、3 seed bootstrap、训练时间/梯度对齐消融；总工作量自报超过 20,000 次训练、32×H100 环境，不能把其便宜“单个代理”当整个证据成本。
3. **限制与离我们多远**：它明确限定单 epoch **预训练、缩模型/数据比率的 proxy**；多 epoch、curriculum、同大小模型缩短训练、架构选择、开放式数据动作均未系统解决。其机制代理按 vanilla SGD 一阶式解释，但实训 AdamW；大模型最优也只是在指定超参网格和训练预算内的最优。E12 是**同一 LLaVA 目标模型、同一固定官方 SFT recipe**对已发布策略做 benchmark 复现，不是跨规模代理排序，因此这篇不会使 E12 已预写主读数无效，也不要求现在开展防御性 LR 矩阵。若以后用短 pilot/小模型挑数据动作并宣称最终最优，就必须对齐它的“被优化目标不同”问题；泛泛的“短训练代理错排、降低 LR 修复”已归它所有。若真实 E12 结果出现行动排序异常，再判断优化器×数据耦合是否是高收益解释，而不是先押这个故事。

## P45 — On the Difficulty of Learning a Meta-network for Training Data Selection（ICML 2026 main；2606.00571v1）

来源：[ICML 正式页](https://proceedings.mlr.press/v306/du26u.html)、[全文与附录](https://arxiv.org/html/2606.00571v1)、[官方代码](https://github.com/ZILIN003/MTS)。阅读：引言/related work、§3 的超梯度及 GSNR 机制、§4 特征、§5 主表/消融/少量验证集/换 backbone、附录 F–I 的数据/对照/训练设置；代码仅核 README 的执行入口，**未完整审源码、未复现**。这是合成图像分类中的训练内双层重加权，不是 E12 的同父 10k 子集重训。

1. **母问题、idea 来源和最近邻距离**：合成图像与真实目标分布不一致，直接全用或简单逐点打分都可能损害泛化。MetaWeightNet（Shu 2019）等用一步 validation look-ahead 学每例权重，直觉上应能利用目标反馈，但原样常不胜全用数据。作者把失败拆成两个不同原因：归一化权重在竞争更新中尖化，使 selector 超梯度的 signal-to-noise ratio 很低；同时仅给在线 loss 或原始图像，网络可能没有足够的训练/目标分布位置信息。相对 Ren 2018 的逐点超参、MetaWeightNet 的 loss-only MLP、固定 CLIP/辅助分类器与密度比启发式，其 delta 是**解释为什么可学习选择器学不好**，再同时修优化和可见特征；并非首次用验证梯度/元学习选样。删去新方法，已有 MTS 会面临低 GSNR 或信息不足，最佳静态 Aux-Clf(Val) 也要额外训练目标域分类器。
2. **方法和实验契约**：训练损失按正权重和归一化，selector 的一步超梯度来自 validation loss 对一次学生更新的响应。理论展示较高的 validation-gradient 对齐样本权重上升、形成 winner-takes-most，有效 batch 变小；GSNR 上界随权重总和和对齐 gap 变坏，建议提高**同一步用于超梯度的 batch size**。方法用 `N=1024`、三层 hidden100 sigmoid MLP/AdamW 选择器与 ImageNet 预训 ResNet50/SGD 动量分类器交替一步更新；输入含当前分类器与生成器 embedding 对训练/验证邻居及类中心关系、单独无选择训练得到的 forgetting/gradient 特征、类别与真/合成来源。源数据 WaterBirds/CelebA/Texture/PACS，后三者按原工作设置以 Stable Diffusion 1.5 图像编辑生成；PACS 12 个有向域对分别训模型，验证/测试同目标分布。它不是不需标注目标数据的黑箱反馈方法。
3. **证据、消融和成本**：主表七个目标列平均全用数据 **68.26**、最强 hard Aux-Clf(Val) **70.86**、MetaWeightNet **68.84**、本文 **73.75**；对最强对照 +**2.89pp**。消融将 batch 1024→256→64 时平均 **73.75→72.68→70.96**，保持大 batch 但只用原图/ResNet 特征/训练 loss 时平均 **68.20/71.77/69.85**；优化和特征缺一均不够。每类仅 5 条目标验证例的设置本文平均 **61.48** 对全用 **57.76**，但比自身 full-shot **65.40** 低 **3.92pp**；ViT-B/32 换 backbone 表是重新在该架构训练，**不能读成冻结 selector 跨 learner 迁移**。作者报告 N=256 可单张 RTX A6000，官方 README 的 WaterBirds N=1024 示例为 **4 GPU DDP**；全文未给可核对的总 GPU·时，特征抽取需单独无选择模型，不能称几乎零成本。表格未清晰报告主结果 seed 方差，微小单列差不宜过解读。
4. **它拥有与我们的剩余压力**：它已经拥有“学数据权重失败可因优化噪声与特征不足、增 batch＋分布/训练动态特征可修”这一机制和大批对照。若我们将来训练可微样本选择器，这两个解释必须先控制，不能把失败笼统归因于反馈无用。P41 的跨 episode 冻结配比政策、P40 的黑箱 BO 和 P05 的开放策展代码都没有用此类一步超梯度，因此 P45 **不是当前 E12 的直接 baseline**；其验证集标签可见、动作逐样本软权重、图像分类目标与我们想研究的终端训练效用/新 episode 改进器不同。这个 setting 差异只提示可能的科学缝隙，不能自动变成 I04；E12 未出分数前不因此开新的 GSNR 防御实验。

## P46 — Data Mixture Optimization: A Multi-fidelity Multi-scale Bayesian Framework（NeurIPS 2025 main）

来源：[会议全文及附录](https://papers.nips.cc/paper_files/paper/2025/file/8e49d32f4668a41b013fbc1ed929c007-Paper-Conference.pdf)、[官方代码](https://github.com/namkoong-lab/data-recipes)。阅读：主文、A–E 附录和代码 `opt_algos/benchmarks.py`、`opt_algos/optimizers.py`、`opt_algos/botorch/eimf.py` 的模拟器与选点路径；本地固定代码 SHA `37269969a0957448d51622e0c083977bc5d260e8`，未复现 472 次训练或模拟搜索。该篇是 E12 之后如考虑便宜 pilot 或源比例反馈优化时的直接强近邻，不是 E12 已经运行的固定静态策略之一。

1. **母问题、idea 的来源和最近邻距离**：旧的启发式源比例依赖任务经验；Data Mixing Laws 等确定性小模型外推假定跨规模函数形状可靠，实际最佳配比可随模型尺度变，下一次昂贵实验该测哪里也缺决策准则。作者改变的是**不确定性表示和实验选择对象**：同时为数据配比、模型尺度、训练步数建后验，按预计改善/实验成本选下一次试验。相对 DoReMi/DoGE 的数据梯度配比、确定性 scaling-law 预测、固定目标尺度 Hyperband/SMAC，新增跨模型尺度的成本感知决策，而不是把“反馈调配比”重新命名。训练步数可沿一次轨迹读中间点，尺度却不能由一次训练自然提供，故二者不应粗暴视作同一种 fidelity；这是方法设计的实际来由。
2. **数据、训练、方法**：用 OLMo 2 在 SlimPajama 的 Wikipedia、StackExchange、GitHub、ArXiv、Books 五源按 Dirichlet 配比预训练 **472** 个模型；规模 **20M–1B** 七档，CommonCrawl/C4 留作源外验证，另外评 HellaSwag、PIQA、ARC Easy。原始训练共 **4×H100、500 compute days**，不是便宜的 472 个点。MLP 预测器输入配比、规模、步数，输出目标 loss/accuracy；472 点随机拆 **422/50** 训练/验证，预测器据此成为公开 simulator。优化器以 GP 建数据/尺度/步数关系，在目标规模以 expected improvement per unit cost 选点；主文使用 RBF，公开代码含其它核与选点变体，不能把任一脚本开关直接等同主文所有结果。对照包括目标尺度随机搜索和 SMAC/Hyperband 多保真 BO。论文报告相对两者 **2.6×/3.3×** 到达目标性能的搜索加速，评估重复多次搜索种子；这部分是在**由真实预训练拟合的模拟器上运行搜索**，不是算法在线又训练相应数量的新 OLMo 模型。论文公开 472 个真实点支持跨规模预测分析，两层证据不可混淆。
3. **限制及留下的压力**：公开 README 明说模拟器只覆盖七个训练过的模型尺度，尺度外预测不可靠；422/50 随机留出不能保证未见配比角落、训练配方或 VLM SFT 的搜索行为同样可信。建模拟器的 500 compute days 也不能从搜索成本图中消失。该方法没有处理开放式数据生成/修订、图文 10k 策展或冻结改进器在新 episode 上学到什么；但这些 setting 的不同本身不构成论文增量。DUET（P40）已用真实同父训练做目标反馈配比 BO，Data Mixing Agent（P41）已学到跨任务可迁移的冻结配比决策，Curation-Bench（P05）已用真实 VLM 训练比较开放策展与 LESS。因此若 E12 显示策略差，下一步不能只提出“用小训练试验聪明地搜索”；要测某种反馈信息或动作家族改变了**普通比例/多保真优化器做不出的真实终端决策**，并对齐全部试验成本。当前没有这样的本地证据，不生成 I04。

## 共同的读论文结论（RECONSTRUCTED）

这些论文的增长方式不是“找到一个别人没碰过的名词”，而是改变一个有实际后果的前提：固定数据→学习数据，内部成功→目标收益，单学生→可复用改进器，盲目试验→有证据的干预。我们的 workbench 应继承它们已经成功的部分，再测量未解决的成本、适配与信用分配，而不是反复退回弱 baseline。

本卡没有把所有邻居读成同一深度。P07/P10/P12/P13 的进一步阅读债务和基础方法补读均保留在文献账本，不用“已搜到”冒充“已复现”。
