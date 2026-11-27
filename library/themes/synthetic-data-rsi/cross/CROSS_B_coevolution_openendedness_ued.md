# 跨领域扫描 B：协同进化 / 开放式学习 / UED 自动课程

范围：coevolutionary algorithms、open-endedness、Unsupervised Environment Design (UED)、learning-progress 课程。
读法：下列"精读"条目均已取得全文（PDF 经 pdftotext，或 Frontiers 全文网页）并读了问题、设置、主要结果、局限；读得较粗的地方在条目里注明。表格里的论文只看了摘要/二手介绍的，标 ABSTRACT ONLY。
对应的 RSI 现象编号 1–10 见 brief（`cross_brief.md`）。

---

## 1. 精读论文

### 1.1 Rutherford, Beukman, et al. 2024 — *No Regrets: Investigating and Improving Regret Approximations for Curriculum Discovery*（NeurIPS 2024，arXiv 2408.15099）
- **问题**：UED 里实际使用的 regret 近似（PVL、MaxMC）到底选出了什么任务？
- **设置**：JaxNav（新的机器人 LiDAR 导航，单/多智能体）、Minigrid、XLand-Minigrid；二值结果环境。对比 DR、PLR、ACCEL、本文 SFL（Sampling For Learnability）。
- **学习度定义**：learnability = p(1−p)，p 为当前策略在该关卡的成功率（沿用 Tzannetos et al. ProCuRL）；等价于 Bernoulli 方差。SFL：先用当前策略在大量随机关卡上各 rollout 一批，选出 p 居中的进入 buffer，再与随机关卡按 ρ 混合训练。
- **关键结果**：
  - PVL / MaxMC 与 regret 无关，实际与成功率相关；MaxMC 与 learnability 无相关，PVL 仅弱相关且方差大，已解决的关卡会和高 learnability 关卡一起被优先。作者推测根因是部分可观测下价值估计差。
  - Table 5（buffer 中关卡的平均 learnability / 成功率，三 seed）：PLR(PVL) 0.01 / 0.85；PLR(MaxMC) 0.02 / 0.84；ACCEL(MaxMC) 0.01 / 0.97；ACCEL(PVL) 0.01 / 0.94；SFL 选出的 0.22 / 0.59（上限 0.25）。也就是 UED buffer 里大部分关卡 agent 已经会了。
  - "Perfect Regret" oracle（只采可解关卡、分数 1−p）表现也强，作者据此认为问题在近似而不在 regret 理论。
  - 评估协议：对 10,000 个随机可解关卡各跑 10 次，取最差 α% 的关卡再重测，报告平均成功率（CVaR）。α=100% 时各方法近似相同，差别出现在 α 小（尾部）；SFL 在尾部显著更好。重测最差子集是为了抵消"选最差"带来的回归均值偏差。
- **条件 / 局限**：只在确定性、二值结果环境；连续情形只给出"同一关卡多次 rollout 的回报方差"的类比；SFL 需要额外 rollout（靠 JAX 速度消化）；随机生成再筛选在空间很大时可能效率低。引用 Beukman 2024：连"真 regret"也未必对应 learnability。

### 1.2 Beukman, Coward, et al. 2024 — *Refining Minimax Regret for UED*（ICML 2024，arXiv 2402.12284）
- **问题**：minimax regret 的 agent 一旦达到 regret 上界，adversary 就只采"regret 无法再降"的关卡，学习提前停滞（regret stagnation）。
- **要点**：给出玩具例子（T-maze regret 1.0 但不可改进；普通迷宫 regret ≤0.9 但可改进），提出 Bayesian level-perfect MMR (BLP) 与算法 ReMiDi，证明 BLP 策略是 MMR 策略的子集，且在 Nash 点处逐层细化。
- **局限**：理论和小规模验证为主（我读了定理与算法部分，实验部分读得较粗）。
- **与 1.1 的关系**：两篇共同指出"高 regret ≠ 可学"。

### 1.3 Dennis et al. 2020 — *Emergent Complexity and Zero-shot Transfer via UED*（PAIRED，arXiv 2012.02096）
- **问题**：生成环境分布的两个失败模式：domain randomization（无结构、不随学习进度自适应），minimax 对抗（产生不可解的最坏环境）。
- **方法**：adversary 与 antagonist 结盟，目标是最大化 regret = antagonist 回报 − protagonist 回报；antagonist 是第二个学习者。Theorem 1：在"成功/失败两类奖励分离"条件下 minimax regret 会选出只要可成功就成功的策略；Nash 点上 protagonist 达到 minimax regret。
- **结果**：迷宫中只有 PAIRED 持续增加可通行路径长度；零样本迁移到 Labyrinth / Maze：PAIRED 成功率 40% / 18%，minimax 10% / 0%，DR 0% / 0%（10 trial）。MuJoCo hopper：minimax 对手把回报压到最低，PAIRED 须保持可行。
- **局限（作者自述）**：regret 估计噪声大——对手 agent 的回报随机，被估计者无法控制；附录里让两个 agent 直接用环境奖励训练（而不是用 regret 训练）反而更能学复杂行为；等价于 Nash 与"联盟"协调是假设。后续（1.4）显示随机搜索加筛选就能超过 RL 学的生成器。

### 1.4 Jiang et al. 2021 — *Replay-Guided Adversarial Environment Design*（Robust PLR / PLR⊥，arXiv 2110.02439）
- **问题**：PLR 本来是无理论依据的经验方法；把它放进 UED 框架（Dual Curriculum Design, DCD）。
- **关键结论**：两个 teacher 不互相影响，故对偶课程博弈的 Nash 近似是两个基本博弈的 Nash（Theorem 1，误差界 2Bp(1−p)）。反直觉推论：**不对未筛选（随机生成）的关卡做梯度更新，只在被 curator 选中的高 regret 关卡上更新**（PLR⊥），收敛到 minimax regret 更好。
- **结果**：250M 步，PLR⊥ 在零样本迷宫迁移上显著优于 DR 和 PLR（同等梯度更新次数，p<0.05），REPAIRED 优于 PAIRED；PLR 与 PLR⊥ 早在 250M 步就超过 PAIRED 3B 步的结果。
- **作者自述局限**：只有"Nash 处"的保证，没有收敛到 Nash 的保证；replay 方法完全依赖 generator 提供的关卡质量；参数化选择决定能迁移到哪里。
- **对 RSI 有意义的一句**：这里"门控"（只在通过筛选的数据上训练）是理论上的设计变量，而不仅是工程细节。

### 1.5 Parker-Holder et al. 2022 — *Evolving Curricula with Regret-Based Environment Design*（ACCEL，arXiv 2203.01302）
- **方法**：PLR 的 curator 之上加 editor：对高 regret 关卡做小幅随机编辑（加/减障碍物），评估后若 regret 够高则入 buffer。假设 regret 随参数平滑变化。
- **结果**：从空房间开始，复杂度（方块数、最短路径）持续涨；零样本迁移大迷宫 PerfectMaze：ACCEL 成功率 53%，次优 PLR 25%，其余失败；BipedalWalker 上也强。
- **局限**：依赖 PVL 作为 regret 近似——而 1.1 显示该近似选到的关卡 buffer 平均成功率 0.94–0.97（ACCEL）。这是两篇论文之间的张力：ACCEL 的复杂度增长与 1.1 的"buffer 里大多已会"并存，应理解为结果好不等于近似忠实。（我读了方法、迷宫与 Bipedal 部分，其余较粗。）

### 1.6 Wang, Lehman et al. 2020 — *Enhanced POET*（arXiv 2003.08536）
- **问题**：POET（成对生成环境与解）的原版因编码受限、缺少通用进度度量而停滞。
- **要点**：(1) PATA-EC：用"所有已有 agent（含存档）在新环境里的得分向量→clip→rank 归一化"的距离衡量环境新颖度，不依赖手工环境编码；(2) 更严格的迁移判据（直接迁移和微调迁移都须超过在位者，减少假阳性）；(3) CPPN 编码地形空间；(4) **ANNECS**：累计"创建且最终被解决、且通过最小准则（不太难也不太易，相对本次运行至今所有 agent 测）"的新环境数。
- **结果**：原 POET 的 ANNECS 在约 20,000 迭代后平台化（编码只能支持有限类型障碍）；Enhanced POET 近线性上升，30,000 迭代后略减速（60,000 迭代，750 核约 12 天）。控制实验：直接优化（ES）与"地面插值课程"（PPO）只能解决 POET 早期阶段的目标环境，解不了后期的——说明解依赖沿途的垫脚石。
- **局限**：ANNECS 的"最小准则"依赖阈值；新颖度仍相对所选 agent 集合；单一域（BipedalWalker 变体）。

### 1.7 Czarnecki et al. 2020 — *Real World Games Look Like Spinning Tops*（NeurIPS 2020，arXiv 2004.09468）
- **问题**：真实游戏的策略空间几何结构；非传递性（循环）随强度怎么变。
- **主张与证明**：Game of Skill = 纵轴是传递强度、半径是非传递维度的"陀螺"：低强度处循环多，随强度升高先宽后窄。时间结构（n-bit communicative）导致分层。Prop 3：固定大小的 fictitious play，只要种群不小于所占最低层的规模，用任何 oracle 都收敛。Nash clustering（逐层取最大熵 Nash 的支撑集）给出单调序（Theorem 2：RPP(C_i,C_j)≥0, j>i）；Theorem 3：种群包含一整个 Nash cluster 时，新策略只需打败种群就保证传递性进步。
- **实证**：OpenSpiel 中 9 个二人零和对称游戏（含 Tic-Tac-Toe、Connect Four、Go 3×3，另有 AlphaStar 数据），每个游戏用 Alpha-Beta/MCTS 在不同深度/模拟数 + 随机种子 + "故意输"的 agent 采样约 1000 个策略，构成经验博弈；Nash cluster 大小在中等强度处最大，高低两端缩小；对比反例：Disc game（任何种群大小都循环）、纯传递 Elo game（朴素自博弈即可）、Blotto（cluster 一直增大）。用"替换最老策略为能平均打赢当前种群的最弱策略"的学习过程测试：种群小则循环，种群大到相变阈值后收敛到最强。
- **局限**：策略采样不均匀；结果是经验博弈，不是完整策略空间；"Game of Skill"适用于人类喜爱的游戏，不是所有游戏。

### 1.8 Graves et al. 2017 — *Automated Curriculum Learning for Neural Networks*（arXiv 1704.03003）
- **方法**：任务选择 = 非平稳多臂 bandit（Exp3.S），奖励 = 学习进度信号：prediction gain (PG)、gradient PG、self PG（在新样本上测）、target PG、mean PG，以及基于 MDL 的 complexity gain（VCG、GVCG、L2G）。奖励按历史 20%/80% 分位数缩放到 [−1,1]。
- **关键理论点**：prediction gain（在同一样本 x 上训练前后的 loss 差）= 真实期望学习进度 + 梯度方差 (ν_PG = ν + V[∇L])，因此偏向噪声大/难压缩的样本；self PG（在另一个样本 x′ 上测）才是无偏的，代价是方差更大——明确的 bias–variance 权衡。
- **结果**：n-gram 语言模型任务中 GVCG 清晰地依次走过课程再集中到 10-gram；GVCG 在 VI 训练下达到目标任务约两倍于均匀采样的速度；ML 训练下 PG/SPG/TPG 在早期略快于均匀采样；bAbI 20 任务课程上有加速（我读了方法和前两个任务，bAbI 与 repeat-copy 部分较粗，"减半时间"取自摘要）。
- **局限**：任务数有限的 bandit；L2G 对无正则网络不可靠。

### 1.9 Zhang, Lehman, Stanley, Clune 2023/2024 — *OMNI*（arXiv 2306.01711）与 Faldor et al. 2025 — *OMNI-EPIC*（ICLR 2025，arXiv 2405.15568）
- **问题**：学习进度课程被"可学但无趣"的任务（如同一任务的微小变体）拖住。
- **OMNI**：用 LLM 作 Model of Interestingness (MoI)，从 LP 高的任务中挑"有意思"的。Crafter：均匀采样学会 4 个任务（3 个有趣），LP 学会 55（9 有趣），OMNI 学会 82（14 有趣）；平均成功率 0.030 / 0.42 / 0.56（有趣任务上 0.103 / 0.52 / 0.78）；BabyAI 上均匀仅学会 1 个任务。LP 与均匀的差异在 25/50/75/100% 训练进度处均显著（p<1e-3）。承认 LP 被无趣任务分散注意力（Fig 8/14）。
- **OMNI-EPIC**：LLM 生成环境代码与奖励函数，archive 记录已学会/失败任务，MoI 在生成前后各判一次新颖性和难度；ANNECS-OMNI（ANNECS + "相对 archive 有趣"）在 5 次重复中显著高于对照（Mann-Whitney p<0.05）并持续上升。LLM 成功检测器与 50 人研究的一致率 72.7%；VLM 当成功检测器精度不够。作者在附录自承：生成器可能在"被相似度拒绝的任务类型"间循环，认为实际概率低但不能排除（读了正文与附录这几段，其余图较粗）。
- **局限**：新颖/有趣完全由 LLM 判，是模型相对量；成功检测 72.7% 一致，说明"任务是否学会"本身有噪声。

### 1.10 Hughes, Dennis et al. 2024 — *Open-Endedness is Essential for ASI*（ICML 2024 position，arXiv 2406.04268）
- **形式化定义**：对观察者 O（有统计模型），人工制品序列 X_t；**novel** = 对任意 t 存在 t′>t 使 loss ℓ(X̂_t, X_T) 随 T 增大（越来越难预测）；**learnable** = 以更长历史 t′>t 为条件，同一未来制品更可预测（loss 随历史长度下降）。开放式 = 既 novel 又 learnable。"噪声电视"（均匀噪声）novel 但不可学；"换频道"也 novel 但历史无助于预测。
- **性质**：相对观察者；不允许观察者干预系统；位置论文，无实验，也不给证明系统开放的方法。
- **局限**：只是定义与论证，度量需自行实例化。

### 1.11 Nolfi & Pagliuca 2025 — *Global progress in competitive co-evolution: a systematic comparison of alternative methods*（Frontiers Robotics & AI 11:1470886，全文网页）
- **定义（沿用 Miconi 2009）**：local progress = 相对当前对手；historical progress = 相对此前世代（CIAO 图）；global progress = 相对运行之外的对手（独立运行或未来代；master tournament 图）。
- **方法**：四种：Archive（名人堂）、Maxsolve*（有界存档、剔除被支配者，上限 25,000 对手）、Archive*（10 个并行种群共享存档）、Generalist（无存档；用 10 个对手评估，其余对手用来区分"全局进步变异"与"只是局部进步的变异"，丢弃后者；种群 80）。全部用 OpenAI-ES。
- **设置**：MarXbot 机器人捕食者–猎物，LSTM 控制器，每方法 10 次重复，每运行 750 亿评估步。
- **结果**：所有方法都有 historical progress，但只有 Generalist 在所有阶段上单调进步；其余方法常有退步，只对最近约 4 个阶段改进（Archive*：捕食者 3 阶段、猎物 5 阶段）。冠军在外部对手上的平均得分（括号为标准差）：Archive 0.282[0.382]/0.511[0.415]，Maxsolve* 0.335/0.552，Archive* 0.415/0.613，Generalist 0.572[0.381]/0.720[0.369]（捕食者/猎物）。Generalist 显著优于其余三者（p ≤ .007；Bonferroni 阈值 .0167）；Maxsolve* 与 Archive 间不显著。
- **局限**：单一任务；Generalist 的作者之一同属提出者；Maxsolve* 存档大小的试验未展示；标准差很大（约 0.4），冠军仍有被特定对手利用的弱点。

### 1.12 Richter 2015 — *Coevolutionary intransitivity in games: a landscape analysis*（arXiv 1501.04010）
- **要点**：把协同进化里的"主观适应度"（与当前对手比赛得到）和"客观适应度"（泛化到全体对手）的差异，用排序量度刻画：collective ranking difference (crd) = Σ|rank(f_sub) − rank(f_obj)|；player-wise temporal mismatch (ptm)；静态 intransitivity index (itx)；借 Elo 评分/排名。实验在带可调随机度的简单随机博弈上，crd 比 ptm 更有意义（99% 置信，关系随随机度 p_rand 单调）。
- **局限**：玩具博弈；论文自己说 ptm 在泛化表现上得不出可用结论。方法价值在"主观 vs 客观排序错位"这一量度思想。

### 1.13 Kumar et al. 2026 — *Digital Red Queen: Adversarial Program Evolution in Core War with LLMs*（arXiv 2601.03335）
- **设置**：LLM（基于 MAP-Elites 做轮内优化）在 Core War 里进化汇编程序"warrior"；DRQ 每一轮对"此前所有（或最近 K 个）冠军"优化；以对 294/317 个未见过的**人类 warrior** 的胜/平比例为 generality（外部锚）。
- **结果**：静态优化对人类 warrior：LLM 零样本平均只击败 1.7%；单个进化 warrior 约 27.9%（8 个 warrior 的集合 22.1%→集合合起来在 DRQ 下击败 89.1%、胜或平 96.3%）。多轮 DRQ（96 个独立运行，K=1…10）：平均 generality 随轮次持续上升；表型（对未见人类 warrior 的表现向量）在独立运行间方差下降、轮内变化率下降（对数拟合下完全收敛需指数轮数，说明压力弱，只有汇总很多运行才在统计上可见）；基因型（源码）方差不变——"表型趋同、基因型不趋同"。**循环**：定义为 a>b>c>a 三元组；历史长度从 K=1 到 K=10，循环总数减少 77%。能用代码特征预测 generality（测试 R²=0.461）。
- **局限**：单一游戏；作者没发现更大模型显著提升（预实验）；趋同压力弱。

### 1.14 Iacob et al. 2026 — *The Red Queen Gödel Machine*（arXiv 2606.26294v3）
- **问题**：自我改进 agent 搜索假设评价标准不变；若评价者（reviewer/grader）本身也进化呢？
- **机制**：controlled utility evolution：**epoch 内评价者冻结**（utility 平稳，故 HGM 的保证在 epoch 内成立）；并行共进化挑战者评价者，用**固定的、人类/客观的 held-out ground-truth anchor** 打分；epoch 边界仅当挑战者提升在位者的 best-belief 分才替换，并做 selective erasure（只丢弃依赖旧评价者的 utility 记录）。
- **结果**（作者报告，未独立核对）：DeepSWE 低推理强度下 held-out 通过率 82.1% vs 基线 75.0%；评价者替换会永久重排 archive（Spearman ρ 稳定在远低于 1 处且不恢复；无 erasure 对照 ρ≥0.90）；通过额外对抗目标降低 reviewer 的自偏好；co-evolved 写作者接受率 1.78–1.86×。
- **局限**：评价者提升只在有 ground-truth anchor 时被验证；"改进 improver"限于评价者与 harness。（我读了摘要、机制、Fig 1/4 和几处结果，未细读附录局限节 G。）

---

## 2. 其他相关论文（未精读）

| 论文 | 与本主题的关系 | 状态 |
|---|---|---|
| Watson & Pollack 2001, Coevolutionary dynamics in a minimal substrate | 协同进化的循环 / 脱离（disengagement）/ 停滞的经典极小模型 | ABSTRACT ONLY（未取到全文） |
| Miconi 2009, Why coevolution doesn't "work" | 区分 local / historical / global progress | 仅二手引用（经 Nolfi 2025） |
| Samothrakis et al. 2013 (TEVC) | 度量协同进化的性能与非传递性；Othello | ABSTRACT ONLY |
| Rosin & Belew 1997；De Jong 2005 (Maxsolve)；Ficici & Pollack (Pareto coevolution) | 名人堂存档、解概念 | 仅经 Nolfi 2025 的转述 |
| Lanctot et al. 2017, PSRO / Balduzzi et al. 2019 | 博弈论种群方法，相对种群表现 RPP | 仅经 Czarnecki 引用 |
| Tzannetos et al. 2023, ProCuRL | p(1−p) 学习度来源 | 仅经 Rutherford 引用 |
| Monette et al. 2025, Optimisation Framework for UED (2505.20659) | 把 UED 改写为非凸–强凹目标，给出收敛保证；学习度的推广分数 | 读了摘要与定理陈述，实验未细读 |
| TRACED (2506.19997)；ATLAS (2511.12706) | 2025 UED 新方法 | ABSTRACT ONLY |
| Beyond Static Evaluation (2606.10389) | LLM 策略共进化 | 只看到搜索摘要 |
| Wang et al. 2019, POET；Lehman & Stanley novelty search；Mouret & Clune MAP-Elites | 开放式学习基础 | 未读（POET 内容由 Enhanced POET 间接了解） |
| Oudeyer & Kaplan；Schmidhuber compression progress | learning progress 思想 | 仅经 Graves 引用 |

---

## 3. 这个领域已知的事实（不含对 RSI 的推测）

1. **协同进化中"进步"至少分三种**：对当前对手、对历史对手、对运行外的对手（Miconi 2009，经 Nolfi 2025 引用）。只看第一种几乎不能区分真进步、循环和共适应。典型经验结果：长期全局进步很少见，常见是极限环（相似策略被反复丢弃与重新发现）。
2. **测量工具有固定套路**：CIAO / master tournament 图（historical vs global）；固定的外部对手集（DRQ 用 294–317 个人类 warrior）；Elo/排序在主观与客观适应度上的错位（Richter 的 crd）；循环三元组计数（DRQ）；表型 vs 基因型的方差分开看（DRQ）；Nash clustering 把策略分层（Czarnecki）。
3. **保证进步的结构条件是有的**：在分层的 Game of Skill 里，种群不小于所占最低层大小的固定记忆 fictitious play 必收敛（Czarnecki Prop 3）；包含整个 Nash cluster 的种群保证传递性进步（Theorem 3）。经验上存在相变——种群小则循环，到阈值后收敛。数值上 DRQ 的历史长度从 1 到 10，循环数减少 77%。
4. **存档 / 历史对手有用但有限**：Nolfi 2025 里 Archive 与 Maxsolve* 只对最近约 4 个阶段有进步；不用存档、但用额外对手检验"是全局还是局部进步"的 Generalist 是唯一在所有阶段持续进步的，冠军外部得分 0.57/0.72 对 0.28/0.51（Archive）。
5. **UED 的 regret 理论与实践脱节**：理论上 minimax regret 有稳健保证；实践中近似 regret（PVL/MaxMC）与成功率相关而非与 regret 或 learnability 相关，buffer 里平均成功率 0.84–0.97、learnability 0.01–0.02（Rutherford 2024）。即使有真 regret，也会出现 regret stagnation（Beukman 2024）。简单的 p(1−p) 选择在 CVaR 尾部显著更好，但仅验证于二值结果环境。
6. **选择信号的偏差是已知的**：Graves 2017 证明在同一样本上测的 prediction gain = 真进步 + 梯度方差，会偏向噪声样本；在新样本上测的 self-PG 无偏但方差大。
7. **门控/筛选是 UED 里的设计变量**：PLR⊥ 只在 curator 选中的关卡上做梯度更新，收敛反而更好（Jiang 2021）；原因在理论上是为了让 teacher 的对偶博弈的 Nash 近似保持稳健。
8. **LP 课程会被"可学但无趣"拖住**（OMNI：LP 学会 55 个任务只有 9 个有趣，加 MoI 后 82 / 14）；开放式系统的进度度量需要"新颖 + 可学"两个条件同时满足（Hughes 2024、ANNECS）。
9. **ANNECS 一类度量能暴露停滞**：原 POET 在约 20,000 迭代平台化，Enhanced POET 近线性上升——说明停滞来自编码空间容量，而不是算法的随机性。
10. **评价者共进化需要外部锚**：RQGM 只在有固定 ground-truth anchor 时让评价者替换；替换会永久重排 archive，需要 erasure（Spearman ρ 不恢复）。
11. **趋同可能发生在功能层，不在实现层**（DRQ：表型趋同、基因型不趋同，且趋同压力弱、需汇总 96 次运行才可见）。

---

## 4. 与 data-centric RSI 的可能联系（以下均为推测，非领域已证事实）

### 现象 #3 rise–plateau–decline / learnable information 掉到零
- **推测**：Hughes 2024 的"learnable"定义（更长历史→更可预测）可以直接用来操作化"可学信息"：令观察者 O = 固定的、冻结的一个模型；制品 = 第 t 轮生成的数据；在 O 用前 k 轮数据微调后，测它对第 T 轮数据的 loss；若 loss 随 k 不再下降，则"learnable"消失；若 loss 随 T 不升，则"novel"消失。这样可分开"数据变得无新颖"（novel=0）与"数据不可学"（learnable=0）。两者对应不同的衰退机制。
- **可迁移的度量**：ANNECS 式累计曲线——"累计数量的通过最小准则且之后被学会的新任务数"。平台化的时间点是客观读数；Enhanced POET 的原因诊断（编码空间容量）提示：先查生成器的表达空间是否已被用尽，再查别的。
- **推测**：下降（decline）段类似 Nolfi 里的"退步"：只对最近阶段有改进，对更早或外部对手退步。可用 CIAO/master tournament 式的"第 i 轮 learner × 第 j 轮数据 / 第 j 轮 improver"矩阵检验：下降是整体性的还是只有对旧分布退步。

### 现象 #4 improver 自己有没有变强，还是只是共适应
- 协同进化文献的直接答案是**必须有运行之外的对手**。对 LLM proposer–solver：把"improver 的质量"定义为 *固定的、早期的 learner* 在 *第 t 轮 improver 产出的数据* 上训练后的增益，在固定的外部评测上度量——这就是 master tournament 的"改进者×固定学习者"版本；而 historical 版本是 *第 t 轮 learner × 第 s 轮 improver 数据* 的完整矩阵（对角线=共适应的本地读数，非对角线=是否有可转移的进步）。注意：这是把 CIAO 矩阵挪过来的推测性设计，我没有在 LLM 循环上见到已发表的实施。
- **推测**：influence 型 generator 奖励"掉到约 0"的 moving target 现象，等同于 Red Queen 下"主观适应度随对手同步变化"；协同进化的主观–客观排序错位度量（crd）可用来检验：在循环内的奖励排序 vs 固定外部评测上的排序，相关性是否下降。
- RQGM 提供了一个具体的结构配方：**epoch 内冻结评价者、边界处用固定 held-out anchor 才允许替换、替换后擦除依赖旧评价者的记录**。这与"harness 自我改进的谱系差异主要来自继承早期收益"的现象相容（推测）：若不擦除/不冻结，跨 epoch 的分数不可比，继承的收益会被误读为 improver 增益。
- DRQ 的"表型趋同、基因型不趋同"：对 RSI 可类比为"独立运行是否收敛到相同的 *行为* 而 *数据/代码* 不同"，这给"improver 是否在向同一吸引子走"一个可测的读数（推测）；同时指出用 96 个运行才能看到弱压力，对应现象 9（噪声）。

### 现象 #2 选择 ≠ 学习（learnability 选择）
- **直接相关的事实**：Rutherford 2024 显示 UED 的近似指标选的是"已经会了"的任务；SFL 选的 p(1−p) 才真正落在边界。Graves 2017 证明在同一样本上测的 gain 会混入梯度方差。
- **推测**：RSI 里"通过率在中间带的已验证任务，60/96 次更新并未降低正确答案 NLL；42–52% 的被收录任务重测时已不在前沿"可能同时包含两个来源：(a) 通过率估计的噪声与回归均值（Rutherford 的做法是对选中的最差子集重测以抵消；对应到"选完再测一遍"）；(b) 选择指标在被选样本上测量，混入"该样本的噪声/可记忆性"而非"可迁移的进度"（Graves 的偏差项）。两者都可以检验：把 learnability 在**独立重采样**上重测并报告选中集的回归均值衰减；用 *另一批同类样本* 测 learner 的 gain（self-PG 的版本）而不是用被选样本本身。
- p(1−p) 要求二值结果与成功率估计；对 LLM 可验证任务可直接用 n 次采样通过率，对连续/带噪读数需要用同题多次采样的方差。需要的采样数就是该度量的成本（SFL 额外 rollout 的对应物）。
- OMNI 提示"可学但无趣"：在 RSI 里对应"通过率居中但内容同质"，可以用 Hughes 的 novel 条件单独筛。

### 现象 #7 多样性崩塌
- Czarnecki 的结论暗示：**对手/数据分布必须覆盖当前强度所在的整个 Nash cluster**，覆盖不足就循环；种群大小有相变阈值。对 proposer–solver：若 proposer 只覆盖少数"风格"，learner 只需打败这些风格，即出现局部进步 + 外部退步（推测）。可测量：用一个固定的、大且多样的外部任务集估计"当前 learner 所在层"的有效风格数，再看 proposer 输出覆盖多少（有效 Nash cluster 大小的类比，需要自己定义策略和胜负矩阵，我没有现成版本）。
- DRQ：MAP-Elites 的局部竞争保持行为多样性，并且更长的历史（K 大）减少循环 77%。可迁移成方法：给 proposer 一个行为描述符网格（话题 × 难度 × 格式）按格保留精英，而不是全局 top-k（推测；OMNI-EPIC 里用 archive 相似度拒绝也属此类，其附录承认可能因被拒而循环）。
- 注意：DRQ 的趋同与"多样性崩塌"是相反的两种崩塌（功能趋同 vs 内容趋同），测量需分开看：行为/表型层与内容/基因型层。

### 现象 #1 gate > reward
- PLR⊥ 的理论与实验提供一个同构论据：**不在未通过筛选的数据上做梯度更新**是改进收敛的结构选择，其稳健性不来自奖励设计（Jiang 2021，Corollary 1 及后续）。对 RSI 现象 #1（gate 关掉时所有奖励变体都崩）这是一个已有的理论动机（推测性类比：UED 里的 gate 是 regret 排序的 curation，不是 LLM 的严格验证过滤器，条件不同）。
- 5% 泄漏使训练端与验证端脱钩而验证持平、20–40% 突然崩溃：与 Czarnecki 的相变阈值（种群小于层大小则循环）在形态上相似，可作为"阈值型而非线性"的先验（推测，没有数学对应）。

### 现象 #6 / #9 自评被利用；噪声与自适应过拟合
- RQGM 与 Richter 都强调"主观适应度 ≠ 客观适应度"，需要冻结的外部 anchor；Nolfi 的 master tournament 的外部对手、DRQ 的人类 warrior 也都是这一类。RSI 里的对应：**每个 proposer–solver 循环保留一个从未参与任何训练/选择/超参选择的外部评测集**，并同时报告 in-loop 与 anchor 的排序相关性（crd 类）。
- Nolfi 2025 的标准差约 0.4、10 个重复才得到显著性；DRQ 要 96 个运行才看到趋同。支持"RSI 论文里 seed 数不足会把噪声读成效应"（现象 9）。

### 现象 #5 / #8 / #10（间接）
- #5 验证者不动点：协同进化文献里"mediocre stable state"与之类似——稳定但并非最优，需要外部对手才能打破。DRQ 与 RQGM 的结果都说明外部锚（人类 warrior / 人类 IMO 分数）是打破的条件。（类比，非定理。）
- #8 生产者强度不预测数据价值：Czarnecki 的"低层种群含非传递性、需覆盖"提示，对 learner 有价值的是覆盖其当前层的数据，而不是更强对手；另外 Graves 提示"信息增益"≠"对手强度"（推测）。
- #10 偏差传递：本领域无直接信息。

### 可直接迁移到 LLM proposer–solver 循环的测量工具（清单）
1. **交叉评价矩阵（CIAO / master tournament 版）**：learner_i × data_j（或 improver_j），读对角线（本地）、下三角（历史）、固定外部集（全局）。
2. **循环三元组计数**（DRQ）：若有成对胜负，直接数 a>b>c>a；用于"improver 版本之间是否有循环"。
3. **ANNECS 式累计新颖且最终被学会的任务数**，加 Hughes 的"novel / learnable"双条件，分别读两条曲线。
4. **主观–客观排序错位**（crd）：循环内的评分排序 vs 固定外部评测的排序。
5. **表型/基因型分离**：行为（对固定外部题集的表现向量）与内容（数据/代码）分开测方差。
6. **learnability 的 CVaR 式重测**：选完任务后在最差/选中子集上独立重测（SFL 的评估法），报告回归均值衰减。
7. **self-PG 式增益**：用一批未参与该次更新的同类样本测 learner 的增益，而不是用被选样本本身。
8. **epoch 内冻结评价者 + 固定 anchor 才允许替换 + 替换后擦除历史读数**（RQGM）。
9. **历史长度 K 的消融**：K=1…K_max 下循环数与外部得分（DRQ，循环减少 77%）。

### 不确定 / 需要小心
- 以上 UED / 协同进化结果几乎都在 RL 或小规模进化设置，部署到 LLM 数据循环的条件（输入是文本、连续奖励、更新极贵）并不相同。
- RQGM 与 DRQ 是 2026 年预印本，结果为作者报告，我没有独立核对。
- 我没有读到协同进化经典文献（Watson & Pollack、Ficici & Pollack、Popovici 综述、Cliff & Miller）的全文；"循环 / 脱离 / 红皇后"的经典定义在这里只有经二手引用的内容。
