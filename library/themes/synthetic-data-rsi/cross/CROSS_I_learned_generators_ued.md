# 跨领域扫描 I：学出来的环境生成器能不能和"随机生成 + 筛选"竞争（UED 反面证据）

读法与取得方式（2026-11-28）：
- Mediratta et al. 2023，arXiv 2308.10797v2：用 arXiv PDF + pdftotext 读了全文，含正文 5 节、附录 A（环境与超参）、B（逐环境表 3–5）、C（三种改动合起来，表 6）。
- Chung et al. 2024（NeurIPS），arXiv 2410.19715v2：同样 PDF + pdftotext，读了全文，含附录 A（理论与算法）、B（环境、训练时间、超参）、C（逐环境表 5–6、t-SNE、可控生成）、D（熵系数与预训练样本量消融，表 7）。
- ACCEL 项目页 https://accelagent.github.io/ ：用 WebFetch 取了页面文字，只摘一段。
- 论文内容当数据读。下面的数字都来自论文表格或正文；"对我们的问题"一节是我们自己的推断，已标明。
- 两篇的训练预算和评测协议不同，不能跨论文比数字。

---

## 1. Mediratta, Jiang, Parker-Holder, Dennis, Vinitsky, Rocktäschel 2023 — *Stabilizing UED with a Learned Adversary*（CoLLAs 2023，arXiv 2308.10797）

- **问题**：PAIRED（用 RL 训练的环境生成器）理论上好，实际输给 PLR⊥ 和 ACCEL。它到底坏在哪里，能不能修好？
- **作者指出的失败模式**（Section 3）：
  - P1 熵坍缩：生成器是 PPO 训练的策略，在高维设计空间里探索不足，策略熵早早塌到很窄的一组关卡上。迷宫要设 169 个以上参数才拿到一次稀疏奖励，所以 RL 问题很难。
  - P2 落后（fall behind）：两个学生（protagonist 和 antagonist）同时在变，生成器先找到只利于 antagonist 的简单关卡，protagonist 一直追不上。
  - 另外三个背景难点：非平稳、长程信用分配（关卡搭完才有一个稀疏 regret 奖励）、高维。
  - 怎么测的：CarRacing 里画 protagonist 与 antagonist 的训练回报曲线，和赛道复杂度曲线（图 2）。5M 步后 protagonist 仍解不了简单圆形赛道，而 antagonist 用同样算法同样数据能解。赛道复杂度在 2M 步后明显下降。迷宫里画各 agent 的熵损失（图 12、13）和积木数量、最短路径长度。PAIRED 的生成器熵骤降，积木越来越少，迷宫越来越稀疏。
- **三个改动**：
  - HiEnt：给生成器和两个学生都加高熵奖励。0-60 迷宫里生成器熵系数 0.05，学生 0.005。
  - Evo：把 PAIRED 的 RL 生成器整个换成 ACCEL 的随机编辑器，用 antagonist 与 protagonist 的回报差当 regret 分数。这一步其实已经不是学出来的生成器。
  - BC：protagonist 在 PPO 损失上加对 antagonist 的 KL（单向 UniBC），或双向（BiBC）。理由是 antagonist 已在解题，可当示范者。
- **主结果**（零样本，在人工设计的测试迷宫或 F1 赛道上；表格均为论文数字）：
  - CarRacing F1（20 条真实赛道，10 个 seed）：平均回报 PLR 530.94，PAIRED 26.16，HiEnt 498.46，UniBC 128.98，BiBC 219.88，UniBC+HiEnt 386.46，BiBC+HiEnt 641.01。只有 BiBC+HiEnt 超过 Robust PLR。
  - Minigrid 25 积木（12 个迷宫，5 个 seed）：PLR⊥ 0.64，PAIRED 0.24，HiEnt 0.45，UniBC 0.18，BiBC 0.18，UniBC+HiEnt 0.59，BiBC+HiEnt 0.39。最好的 PAIRED 变体略低于 PLR⊥，作者说"持平"。
  - Minigrid 0-60 积木（5 个 seed）：ACCEL 0.61，PAIRED 0.21，HiEnt 0.52（标准误 0.13），UniBC 0.49，BiBC 0.11，UniBC+HiEnt 0.47，BiBC+HiEnt 0.45。HiEnt 最好但仍低于 ACCEL。
  - 换优化器（Evo，0-60，5 个 seed）：ACCEL 0.61，PAIRED+Evo 0.50（±0.14），FlexPAIRED+Evo 0.36。HiEnt（0.52）略高于 PAIRED+Evo，作者据此说熵比优化器重要。ACCEL 在验证迷宫上明显更好，作者归因于 positive value loss 比两个学生的回报差更适合做筛选分数。BipedalWalker 上 PAIRED+Evo 比 PAIRED 好，比 ACCEL 差（图 8，正文无数值）。
  - 三者合起来（附录 C，10 个 seed，0-60）：ACCEL 0.75，PAIRED+Evo+UniBC 0.79，+BiBC 0.67，+BiBC+HiEnt 0.59，+UniBC+HiEnt 0.61。作者只在验证集上选了 UniBC，几乎没调超参。BipedalWalker 上合起来的方法在 PitGap 和 Stump 更好，Stairs 和 Roughness 上 ACCEL 更好，Hardcore 上样本效率更高（只有图，无数值）。
- **哪个修复管用（消融）**：
  - 熵奖励几乎总是有用：CarRacing 从 26.16 到 498.46；25 积木从 0.24 到 0.45；0-60 从 0.21 到 0.52。
  - BC 的效果取决于环境，有时有害：CarRacing 里 BC 单独只到 128.98 和 219.88，必须与熵合用；0-60 迷宫里作者说加 BC 反而不如只加熵，结论里还提到某些环境 BC 会降低分布外鲁棒性。
  - 单向还是双向取决于 protagonist 与 antagonist 的回报差：CarRacing 差大，双向好；25 积木里两者回报几乎一样，单向好。
- **公平性**：PAIRED 各变体训练 30k 次梯度更新（250M 环境步），ACCEL 训练 20k 次更新（约 400M 环境步）。PAIRED 的超参在验证集上扫过（3 个 seed），PLR 与 ACCEL 沿用默认。
- **关于生成器跟踪学习者 / 多样性 / 复杂度累积**：
  - CarRacing 加熵后赛道越来越尖、越来越像真实赛道（复杂度曲线上升）。
  - 迷宫里 PAIRED 的积木数与最短路径随训练下降，HiEnt 与 BiBC+HiEnt 的上升（图 6b）。
  - 多样性只用熵间接衡量，没有直接的覆盖度指标。
  - 没有专门测"生成器落后于学习者多少步"。
- **局限（作者自述加我们读到的）**：
  - 作者自己说目标是逐个检验设计选择，不是做最强方法。
  - 摘要里说"匹配或超过"，但表里只有 CarRacing 明确超过，其余是接近或略低。
  - 最好的变体因环境而异（BiBC+HiEnt、UniBC+HiEnt、HiEnt、Evo+UniBC），选择靠验证集，超参空间比对照方法大。
  - 表里很多项标准差大（如 0.52 ± 0.13）。
  - 最后一个"匹配 ACCEL"的版本（Evo+UniBC）用的是随机编辑器，不是学出来的生成器。

---

## 2. Chung, Lee, Kim, Kim, Oh 2024 — *Adversarial Environment Design via Regret-Guided Diffusion Models*（ADD，NeurIPS 2024，arXiv 2410.19715）

- **问题**：RL 训练的生成器不稳（"moving manifold"）且覆盖窄；随机生成加回放（PLR⊥、ACCEL）覆盖广，但要额外跑 episode 去评估 regret，样本效率差，也不能直接生成有意义的关卡。能否两者兼得？
- **作者指出的失败模式**：
  - RL 生成器不稳，环境覆盖有限，限制 agent 泛化（引言，引用 CLUTR）。
  - 回放法样本效率低（需要额外评估）。
  - 怎么测的：t-SNE 画训练期间生成的环境（先用 environment critic 的编码器映射到隐空间），PAIRED 最后只覆盖一小块区域，ADD 覆盖大得多（图 2d、9、13）。复杂度用积木数和最短路径长度（图 2c）。
- **方法**：
  - 先在 1000 万个随机迷宫（或随机地形参数）上预训练一个扩散模型，之后不再训练。
  - soft UED：目标里加熵项，最优环境分布为 Λ(θ) ∝ u(θ) exp(ω · regret)，ω 越大熵项越弱。
  - 用 regret 的梯度做 classifier guidance 来采样。regret 本身不可微，所以训练一个 environment critic，预测当前策略在环境 θ 上的回报分布（类别分布），regret ≈ CVaR_α − 均值。
  - agent 用 PPO 训练，critic 用 agent 的每次 episode 回报更新。
  - 额外功能：可以用"得到某个回报的概率"做引导，控制生成难度。
- **主结果**（零样本，5 个 seed，每个测试环境 100 个 episode）：
  - 迷宫（250M 环境步，12 个测试迷宫，表 5 均值）：DR 0.64，PAIRED 0.59，PLR⊥ 0.63，ACCEL 0.72，ADD 无引导 0.63，ADD 0.85。四分位上 ADD 都最高，四分位距比 ACCEL 小 51%。12 个迷宫里 ADD 在 5 个最好。
  - 迷宫只用一半环境步（对齐 PLR⊥ 与 ACCEL 的梯度更新次数）：ADD 0.72，与 ACCEL 打平。
  - BipedalWalker（20 亿环境步，6 个测试环境，表 6 均值回报）：DR 29.5，PAIRED -2.9，PLR⊥ 114.8，ACCEL 71.7，ADD 无引导 69.3，ADD 149.6。半步数 127.4，仍高于 PLR⊥。
  - 此处 ACCEL 反而低于 PLR⊥，作者归因于 ACCEL 评估变异环境要额外交互。
- **哪些部件管用（消融）**：
  - 去掉引导（ADD w/o guidance）：迷宫 0.63，约等于 DR，说明 regret 引导是关键。
  - 熵项（表 7，迷宫）：ω = 5 为 0.85，10 为 0.81，20 为 0.82，40 为 0.64，80 为 0.47。熵项削弱则变差。
  - 扩散预训练样本数缩小 100 倍到 100 万：迷宫 0.76，降约 11%。
  - 没有做 critic 本身的消融（例如换掉分布式 critic、换掉 CVaR）。
- **算力与公平性**：
  - 按环境步对齐：迷宫 250M，Bipedal 2B。作者承认这对回放法不利（它们有额外 episode），所以补了半步数对比。
  - 墙钟（RTX 3090Ti，每个 seed）：迷宫 DR 与 ADD 无引导约 48 小时，ADD 约 56 小时，PLR⊥ 与 ACCEL 约 100 小时。Bipedal：80、92、160 小时。是否包含扩散模型预训练的时间，文中没说清（我们未核对）。
  - PAIRED 在 Bipedal 上值函数常发散，作者没有自己重跑，直接采用 Parker-Holder et al. 报告的结果。
- **关于生成器跟踪学习者 / 多样性 / 复杂度累积**：
  - 迷宫里 ADD 与 PAIRED 的积木数明显上升，ADD 最终积木数第二多、最短路径最长；PLR⊥ 积木数只略高于 DR；ACCEL 也上升，但作者说是因为 13×13 网格最多 60 块，随机变异本身会使期望积木数上升。
  - Bipedal 里 ADD 生成的环境复杂度反而逐步下降：随机生成的地形对当前 agent 太难，除 ADD 外所有方法训练回报都在 0 或以下，ADD 生成较易的环境，回报才为正。
  - 附录图：训练 2 亿步后生成的迷宫积木更多；critic 预测 agent 在简单迷宫已接近最优，所以把 regret 推向更难的。
  - 这些都是定性观察和曲线，没有"生成器落后多少"的度量。
- **局限（作者自述）**：收敛到最优点没有保证；regret 估计与真值之间无紧致界；critic 用的是旧策略的 episode 结果，不能精确反映当前 agent 的能力。
- **我们读到的补充**：
  - 生成器不是用 RL 训练的，而是"随机分布的扩散模型 + 引导"。预训练数据就是随机生成的 1000 万关卡，所以它的覆盖来自随机分布。
  - 引导还要靠 environment critic，等于又加了一个要跟着学习者更新的学习模型。
  - 迷宫上 DR、PLR⊥、PAIRED 三者只差 5 个点，标准差很大（多处 0.3–0.5），ADD 的 0.85 是一次明显领先，但是只有两类环境、5 个 seed。

---

## 3. ACCEL 项目页（https://accelagent.github.io/，仅摘页面所述）

页面说，PLR 通过随机搜索找有挑战的关卡，因此"无法在之前发现的结构上继续构建"，并且随机搜索在高维设计空间里会受维数灾难影响，agent 边界处的关卡越来越难随机撞到。ACCEL 对高 regret 关卡做小幅编辑（变异），评估后只有 regret（由 positive value loss 估计）够高才进入回放 buffer，这样反复编辑与筛选，buffer 里关卡的复杂度快速上升，页面称之为"随时间复合的复杂度"。迷宫与熔岩网格从空房间开始，BipedalWalker 从无障碍平地开始。页面报告：人工迷宫上零样本迁移最好；51×51 的程序生成迷宫上 ACCEL 解出超过 50%，PLR 约 25%，其余方法失败；ACCEL 用约 3B 环境步，POET 约 500B。

---

## 4. 对我们的问题（以下为我们的推断，不是论文结论）

**这对"学出来的数据生产者不需要，随机生成加学习者筛选就够"的主张意味着什么**
1. 这个主张在原始 PAIRED 上成立，但原因可以修。Mediratta 的失败是具体的两条：生成器熵坍缩，以及两个学生不同步造成的"落后"。熵奖励一项就把 PAIRED 从 0.21 拉到 0.52（0-60 迷宫）、从 26 拉到 498（CarRacing）。所以"RL 生成器输了"有一半是工程问题，不是原理问题。
2. 但修完后的 RL 生成器仍然没有稳定地赢。Mediratta 里 0-60 迷宫和 25 积木都略低于 ACCEL 或 PLR⊥，只有 CarRacing 超过。唯一赢过 ACCEL 的变体（0.79 对 0.75）把学出来的生成器换成了随机编辑器，这反而是支持"随机加筛选够用"的证据。
3. ADD 是最强的反证：学出来的生成器（扩散先验加 regret 引导）在迷宫上 0.85 对 ACCEL 0.72，Bipedal 上 149.6 对 PLR⊥ 114.8。但它的生成器本质上是随机分布的拷贝，加上一个跟着学习者更新的 critic。它没有证明"从零学一个生成器"优于随机，证明的是"随机分布 + 学习者相关的引导"优于"随机分布 + 事后筛选"。这与"学习者相关的信号比随机更重要"一致，与"生产者必须是 RL 学出来的"不一致。
4. 两篇都显示：随机分布覆盖高、可靠；学出来的东西覆盖窄、容易塌。所以产物端的多样性要靠随机先验或显式熵来保证。

**学出来的生产者什么时候值得**（推断，两篇各有一部分依据）
- 设计空间高维、随机撞到前沿关卡的概率很低（ACCEL 页面的维数灾难论点；ADD 的 Bipedal 里随机地形对 agent 太难，除 ADD 外训练回报都不为正）。
- 评估一个候选的代价高（回放法要额外 episode，ADD 的墙钟约为 PLR⊥ 和 ACCEL 的一半多一点）。
- 有一个可微或可学的"当前学习者在这个任务上会怎样"的预测器（environment critic）。
- 生成器必须有一个独立于 RL 的覆盖保证（预训练的随机先验、熵项）。
- 反过来，设计空间小、评估便宜、有可靠的 learnability 过滤时，随机加筛选很可能够用（No Regrets 的结论，见 CROSS_B）。

**对我们的实验可借鉴的**
- 如果我们要测"学出来的数据生产者"，对照必须包含：随机生成 + 学习者筛选、随机编辑累积，以及"随机先验 + 学习者引导"，不能只比 RL 训练的生成器，因为 RL 版本的失败模式（熵坍缩、落后）是已知可修的。
- 报告时要同时给出生成器熵、覆盖（t-SNE 或等价指标）、复杂度曲线，和学习者与生成者的差距曲线，这是两篇论文里最容易复核的"生成器失败"证据。
- 两篇的比较都只有 5–10 个 seed，且最佳变体因环境而异，这类结论的幅度需要谨慎，不要把"某一环境上赢了"写成普遍结论。

未核对 / 不确定：ADD 的墙钟是否含扩散预训练；Mediratta 里 PLR 和 ACCEL 的超参是否也在验证集上调过；BipedalWalker 各数值只有图，没有表。
