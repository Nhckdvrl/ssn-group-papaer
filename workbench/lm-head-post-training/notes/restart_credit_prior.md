# 重启/放弃失败轨迹（方向 A）与 RLVR 天花板=信用分配？（方向 B）：近邻文献核查（2026-11-28）

阅读深度：下列均下载 arXiv PDF 用 pdftotext 取全文；DeepConf、Hassid、Wang(underthinking)、ProRL、VinePPO、Yue、Wang 2506.01939、Wang 2610.06851 读了方法、结果与相关附录段落（按关键词定位，未逐页读完）；2602.09591、2610.34894 读了摘要、引言、图1与相关段，未通读；ReD、TAAR、2610.05584、BroRL、Invisible Leash、STOP、Parallel-Probe、Failure-Prefix、QuestA、SART 读了摘要/引言与关键机制段，其余未读。逐条标注，未读之处写「未核对」。

## 0. 两个评审引用的编号是什么
- **2602.09591** = Nohara/Nakamura/Yokota，"On the Optimal Reasoning Length for RL-Trained Language Models"（v3，2026-06）。**不是**串行 vs 并行测试时扩展，是训练期长度控制：多种长度惩罚方法×多个基座，准确率对平均输出长度非单调、在中等长度达峰（摘要、§1）；"mode accuracy"（每题众数答案是否正确）随长度继续上升，而样本准确率持平或下降，作者解释为"围绕越来越正确的中心的离散度变大"（摘要）。它引 Ghosal et al. 2025 为测试时"答案分布离散"的先例（§1；该文 ID 未核对）。
- **2610.34894** = Shan Yang，"What Outcome RL Buys: Finishing, Reliability, Rarely Reach"（2026-10-26）。**不是**串行 vs 并行，是把 20 个已发布 RL 模型相对基座的 pass@1 增益拆成"在预算内答完 F / 答完后答对 P / 触达基座八次全错的题 R"。结论：基座常撞预算的地方，增益 82% 是 finishing（4k/8k，摘要、图1）；预算够时增益是 reliability；reach 在四个物理/数学集上至多 +2.1 点（摘要）。与方向 B 相关（见 §B6）。

## 方向 A：测试时"失败边界"（hazard 递减 + 重启）

**A1. DeepConf, Fu et al. 2508.15260。** §3.3 在线模式：先 N_init=16 条预热 trace 定阈值 s（DeepConf-low 取 top η=10%，-high 取 90%），生成中"最低组置信度"低于 s 即**终止该 trace**（"allowing dynamic termination of unpromising traces"），再自适应采样直到共识。表2/表10：DeepConf-low 比多数投票少 43–84.7% token（AIME25 GPT-OSS-120B −84.7%，表2），精度 ±~1.5 点内。→ **这就是下边界（abort 低置信 trace）**，且预算口径与并行采样直接对比。不重启同一 trace，信号是置信度而非"已运行时长"，需要预热。
**A2. Hassid et al. 2505.17813（Don't Overthink It）。** 表1：同题内最短答案比随机高 2.2–15.7 点，最长答案比随机低 5.4–18.8 点（数学平均），最短比最长最多 +34.5（§3.2）。**注 1：未在 32768 上限内完成的生成被排除**（"often infinite thinking loop"），所以未完成的尾部不在表1 里。short-m@k：并行 k 条，首 m 条完成即**中止其余所有**（§4.1）——按"跑得久=放弃"的规则中止未完成 trace，本质就是 length-based 下边界；short-1@k 少用至多 40% 思考 token、short-3@k 各预算优于多数投票（摘要、图3）。§5.3 串行算力版：每条生成超过"已完成的 m 条最短者的最大长度"即终止（即固定长度截断，非 Luby）。§5.1：难题仍需更长思考，但同一题内短者更准（表2）。→ 长度-准确率反相关、按长度中止都**已有**。没有：hazard 曲线、重启预算（被中止的算力不用于"新开一条"之外的调度）、Luby 序列。
**A3. Wang et al. 2501.18585（Underthinking）。** 方向相反：问题是**切换太勤**（错误回答平均多用 225% token、多 418% 的 thought switching，§1/图1），提出 underthinking 指标 ξ_UT=1−T̂/T（§2.3）与 thought-switching 惩罚解码 TIP（表2-4）。不是中止失败轨迹；其结论（早期 thought 已含正确路径但被抛弃）与"尽早重启"在直觉上方向不同，但它只做解码惩罚，没做放弃/重启。
**A4. ReD, Meir…Hirshberg 2601.21522（v4，2026-11-22）。** 明确引 Luby 与 SAT 重尾文献（参考文献 [22]–[27]；§1）。**但重启的单位是"问题"而非"trace 内部"**：每题只试若干次、失败就丢弃换题，以 coverage@cost 为指标，推导依据是 pass@k 幂律（摘要、§1）；实验 HumanEval/GSM8K/MMLU-Pro/SWE-bench Lite，仅 gpt-oss-20b 是推理模型且低 effort（附注，行号约 2405）。无"trace 已跑到 t 仍未完成"的 hazard 分析。→ 最接近的**重启理论**先例，但不是单 trace 的长度重启。
**A5. TAAR, Chen et al. 2601.11940（Fudan，ACL Findings 2026）。** 89% 的错误含 "thinking trap"（前缀主导的死锁，§4.2）；训练一个诊断策略预测 trap 位置与逃逸概率，**截断到 trap 之前重启解码**，严重者升温重采样（§3）。对比 Base Avg@4 与 PRM；额外 token +31.2%（表6）。→ **"放弃并重启失败轨迹"已有**，但需要**训练诊断器**（≈ PRM 类信号），预算口径是"额外 token"，不是等总 token 的 Luby 式。
**A6. Expanding LLM Reasoning, Atri & Luo 2610.05584（NeurIPS 2026）。** 在已存储 chain 的第 k 步重启（保留前缀），测"expansion utility"；9 个模型×6 基准；always-last 在 R1-Distill-14B/MATH-500 上比等聚合输出的自一致性前沿高 +0.052（图6，摘要）；学得的 router 相对 always-last 无检出增益（摘要）。→ 前缀重启位置有价值已有实测，但是"在哪儿续"而非"何时放弃"。
**A7. STOP, Bi et al. 2604.16029（ACL 2026 long）。** 并行推理中在前缀检查点（L_prefix）处**剪枝**无望路径；给出剪枝方法分类（内/外信号×可学/不可学，表1）；GPT-OSS-20B AIME25 84→近 90（固定算力，摘要）。**Parallel-Probe 2602.03845** 引言自述"多数研究在串行生成上做早停"，其方法用共识早停 + 偏离度剪枝，总 token −25.8%（摘要）。**SART 2505.13326**：冗余采样 + 先完成者早停 + 动态剪低质量分支（摘要）。DeepPrune 2510.08483、ST-BoN、KAPPA、STEP 2601.09093：仅见检索摘要，**未核对**。
**A8. 其余。** 2609.03436（"It's the Problem, Not the Path"）检索摘要提到预算/难度混杂；**未读，未核对**。TERMINATOR 2603.12529、DEER 2504.15895、ES-CoT 2509.14004：针对"答案已出现即早退"（上边界），检索摘要，未核对。

**对评审命题的核对**：「几乎所有早停都砍上边界，几乎没人研究中止失败 trace」——**与全文不符**。DeepConf（在线终止低置信）、short-m@k（中止长的）、TAAR（截断重启）、STOP/Parallel-Probe/SART（并行剪枝）都在做下边界；Parallel-Probe 的"多数研究在串行早停"只描述串行情形。**未检索到**：把"已运行长度 t 条件下的完成正确率（hazard）"作为被估计对象并随 t 画曲线；Luby/几何重启计划用于单条推理 trace 的等 token 对比；检索未见不等于不存在，只检索了 arXiv 摘要级。

## 方向 B：RLVR 天花板是支持集限制还是轨迹内信用分配

**B1. Yue et al. 2504.13837（v?，2025-11-25 版）。** 大 k 时基座 pass@k 超过 RL（图1左）；六种 RLVR 算法表现相近，采样效率差 ΔSE 一致很大（摘要、§4 Fig 8）；蒸馏能引入新模式（图7）。§5 "Possible Future Work" 和 §7 **自己写**：二值结果奖励 + 大动作空间中探索低效"may be the root causes"，并列出 "Process reward and fine-grained credit assignment"（p.12）。→ 原论文就把"信用分配/二值奖励"列为候选根因，但**没做检验**。
**B2. ProRL, Liu et al. 2505.24864。** 从 **R1-Distill-Qwen-1.5B**（非基座）出发，KL 惩罚 + 周期性参考策略重置 + DAPO（clip-higher、动态采样）+ 136K 多域任务（§2.2–2.3、§3.1）；声称 pass@k 在基座完全失败的任务上也提升，且边界提升与"基座初始能力（低初始 pass@128）"和训练时长相关（§4.2：Diminish / Plateau / Sustained 三类，图4）。解释是**探索不足/熵坍缩/KL 主导**，不是信用分配；创造性指数(Creativity Index)显示轨迹更新颖（§4.2）。
**B3. BroRL, Hu et al. 2510.01180（ICML 2026）。** 摘要：ProRL 在数千步后 plateau；把每题 rollout 数 N 从 16 提到 512 可在 ProRL 饱和点之后继续提升；质量平衡分析：N 够大保证正确 token 概率质量增加、消除"知识收缩"（knowledge shrinkage，引 Wu et al. 2025）；原话 "perceived limits of RLVR are sometimes artifacts of algorithmic design (e.g., insufficient rollouts)"。→ 把天花板归因于**探索量（采样覆盖）**，是"优化问题而非能力极限"的最直接先例；机制是 one-step 质量平衡，**不涉及轨迹内逐 token 的信用**；仍是 1.5B 蒸馏起点。
**B4. Invisible Leash, Wu/Xuan et al. 2507.14843（v5，2026-10-14）。** 与 B1 同向：经验支持集收缩多于扩张（摘要）；引导方向是"需要显式探索机制"。不是信用分配。
**B5. VinePPO, Kazemnejad et al. 2410.01679（ICML 2025）。** 用蒙特卡洛续写估计每个中间状态的价值，替代价值网络；DeepSeekMath-7B / RhoMath-1.1B，MATH 与 GSM8K，序列长 ~1–2K（附录表，行号约 1180）；报告 PPO 价值网络"勉强好于随机基线"（摘要、§7）；VinePPO 以更少梯度步和更短墙钟超过 PPO/GRPO/RLOO/RestEM（摘要、图4–6）。注意：**只测 pass@1**（全文无 pass@k），**短 CoT**，**基座 SFT 起点**——**没有检验"天花板/支持集"**。
**B6. Wang et al. 2506.01939（Qwen，80/20）。** 只有约 20% 高熵"forking token"决定推理走向；RLVR 基本保持基座熵模式，主要调整高熵 token 熵（摘要、表1）；只对前 20% 高熵 token 做梯度，Qwen3-32B 比全 token DAPO 高 +11.04(AIME'25)/+7.71(AIME'24)，8B 持平（摘要、表2）。→ 这是"信用集中在少数位置"的证据，**不是**对天花板的归因；与信用分配的关系是间接的（把梯度只给关键位置 ≈ 一种粗略的信用掩码）。
**B7. 2610.34894（Yang）。** 见 §0。摘要(4)："小规模 8B RL 里新题上的增益是 finishing、reliability 持平"；§附录行 1360："Once a success is sampled, credit installs it, but only on that problem"：在 353 题里的 60 题上，被采到成功的题得到提升，不迁移到邻题（句尾未读全，**未核对**）。实验主体是**已发布 RL 模型 vs 其起点**，非受控地比较信用分配算法。→ 对"能力 vs 信用"提供**测量框架**（finishing/reliability/reach），不提供归因检验。
**B8. 其他 "RLVR 天花板非能力极限" 的论证。** (a) **CoT-Pass@K, 2506.14245**（MSRA）：认为基座 pass@k 被"错误推理碰对答案"夸大，加上推理正确性后 RLVR 在所有 K 下都提升——是**度量**论证，非信用分配；仅检索摘要，**未核对**。(b) **OREAL 2502.06781**：二值结果奖励下长链信用分配难，训练 token 级奖励模型；仅检索摘要，**未核对**。(c) **QuestA 2507.13266**（ICLR 2026）：对难题注入部分解作为提示，pass@1 与 pass@k 同升（摘要）；动机是稀疏奖励让难题学不动。(d) **Failure-Prefix 2601.20829**：对饱和题用错误 rollout 前缀作条件，使"标准 RLVR 停滞处"继续提升（摘要）。

### 关于"前缀/条件化 RL 为何停滞"（Wang 2610.06851）
Wang 2610.06851 §2.3 与 App. D.2、图14：Olmo-3-7B/32B、Qwen3-4B/14B，300 步 GRPO，MATH 训练集，MATH-500；预填 cue 起点就等于标准 RL 约 50–100 步（图3右），"further cue-forced training yields little improvement as standard RL catches up"；Qwen3-14B 上"RL adds little to the cued base's accuracy"（App. D.2）。**论文只描述现象，未解释**（我读的 §2.3 与 D.2 无机制说明）。相关解释只在别处：
- Failure-Prefix 2601.20829 摘要：固定前缀数据集下性能最终 plateau，迭代刷新前缀可在平台期后继续提升（"unlocks additional gains after performance plateaus"）——暗示固定前缀的信息量会随策略变化而耗尽；其场景是饱和题，不是 cue。
- QuestA 与 Hint 类（2604.00698，仅检索摘要，未核对）：论点是稀疏奖励，前缀=降难度；未讨论"为何停"。
- 2610.34894 B 组（setup 提示）："Derivations hinted… lean heavily on the hint，so the bound of Xia et al. (2026) gives no reason to expect transfer"，提示通道"只移动策略本来就采样的内容"（行 1355-1358）——条件化只改变已被采样的部分。（Xia et al. 2026 ID 未核对。）
- Wang 2610.06851 自身另有 App. D.2 "Where the policy changes"（据已有笔记 rl_elicits_mode_survey.md：KL 集中在前两个位置；本次未逐段复核，未核对）：RL 的变化集中在开头——这给出"cue 之后无事可学"的一种读法，但他们没把它写成对停滞的解释。
未找到专门研究"前缀条件化 RL 为何停滞"的论文。

## 对两个方向的影响（只列事实）

**方向 A**
- 已有：长度-正确率的题内反相关（Hassid 表1，Wang 2501.18585 图1：错误回答多 225% token）；按"长/低置信"中止 trace 并用省下的 token 补采（short-m@k §4–5.3；DeepConf §3.3 与表2 −43–84.7%）；中止后从截断前缀重启（TAAR，需训练诊断器；Expanding LLM Reasoning，保留前缀）；并行剪枝（STOP、Parallel-Probe、SART）；Luby/SAT 重尾重启已被引入 LLM 推理的**问题级**分配（ReD）。
- 评审"几乎没人研究中止失败 trace"与上述全文不符。
- 未见：①以已运行长度 t 为条件的完成/正确 hazard 曲线（含截断未完成样本，Hassid 把它们排除了，§3.2 脚注）；②单条 trace 内的几何/Luby 重启计划，且与串行长思考、普通并行在**等总 token**下对比、**不用 PRM/训练器**；③hazard 递减是否按题难度/模型族而异。这些是检索摘要级结论，可能漏检（尤其 2026-10/11 的新预印本）。
- 注意：TAAR、STOP 已用训练信号；DeepConf 用置信度（免训练但需预热）；short-m@k 免训练、仅按长度。"免 PRM 的纯长度/hazard 触发重启"在已读论文中最近的是 short-m@k §5.3 的固定长度截断规则。

**方向 B**
- 已有：天花板=支持集收缩（Yue、Invisible Leash）；天花板=探索/采样不足（BroRL 摘要原话、ProRL 的熵与 KL）；天花板=度量问题（CoT-Pass@K，未核对）；Yue 自己把二值奖励与细粒度信用分配列为候选根因（§5/§7）；VinePPO 证明 MC 信用在短 CoT、7B 以下提升 pass@1；Wang 2506.01939 证明梯度集中在约 20% 高熵 token 即可持平或更好。
- 未见：把 VinePPO 式（或其它）轨迹内信用与标准结果奖励 RL，在**长 CoT 推理模型**上、以 **pass@k / 支持集**（而非仅 pass@1）为读数做对照，以直接检验"天花板是否缩小"。Yue、BroRL 的解释均为推断而非干预检验；VinePPO 无 pass@k；Wang 2506.01939 报的是 AIME 均值。也未见同时控制"基座支持集"与"信用分配"两个因素的设计。该结论同样基于有限检索。
- 前缀/cue 条件化 RL 停滞：现象见 Wang 2610.06851（图3右、图14、D.2），其机制未被任何已读论文解释；Failure-Prefix 给出"固定前缀集会 plateau、刷新可续"这一旁证。
