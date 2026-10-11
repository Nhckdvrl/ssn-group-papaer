# I16 下一步：不是补故事，而是用少量决定性实验选择科学问题

更新：2026-10-11。性质：**研究判断与拟议实验，尚未获准恢复任务、占卡或改变工作台状态**；执行前按 AGENTS.md 新建/批准实验卡并核对资产。旧 E23/E24 保持原状态。

## 最简科学问题

**为什么更大的 latent world model 有时更会预测，却更不会使用自己的预测来行动？**

请注意这里的“更会预测”对 I16 当前并未获得完全与表征 D 解耦、与物理任务对齐的评价；这是需验证的竞争假设，不是前提事实。

我们不再把论文预定为“各向同性导致高维距离失效 / 免训练 SFA 修复”。因为 CTWM（2026-10-01）、AnisoWM（2026-09-29）、TEMPO（2026-10-04）、Objective Bottleneck（2026-08）等已覆盖其核心概念。改为询问：**把模型当 agent 的决策系统，scale 到底改善了哪一部分、牺牲了哪一部分？**

## 一、从强原有资产切入，不新建测试玩具

现有 [bank.py](../scaling/bank.py) 已生成固定 held-out start-goal × random/expert/noisy-expert 候选行动的**真实模拟器结束状态**；[oracle_bank.py](../scaling/oracle_bank.py) 已计算 predicted latent cost / true terminal latent cost 与绕门 geodesic 的排序一致性，并量了 best-of-N；[E21](../experiments/E21-scaling-planning.md) 已注册了该分析轴。**优先复用原代码与这些 raw artifacts**，不能声称下面全是新创新，不能无理由重新实现。

但当前 bank 有一个测试功效风险：如果绝大多数候选动作的**真实进度几乎相同、都远离目标**，任何排序指标都会低信息量。要先按独立 goal、candidate type、oracle improvement (best observed − random)、可行正例数画 support distribution，报告无可识别信号的 query 占比。不能挑成功 bank 做主结果，可预先定义 informative-support 子分析并同时报告完整分母。

### D0：不启动 GPU 的证据清点和统计审计（最高优先）

**目的**：分开明确事实与论文草稿数字，避免主张建立在测量定义/原始文件不同步上。

- 汇总每个 checkpoint 的 train seed、architecture spec、latent D、λ、resolution、updates、train loss、原始 closed-loop episodes 与 success trace 的完整键表（以 raw 文件为真，E23 手工表只当导航）。
- 与当前 fixed candidate bank 对齐 source episode/start/goal / testing IDs，确认“相同 bank 比较 scale”，保留所有随机与 expert 扰动候选。
- 对 metric horizon 重新核查：lag 范围、每一 lag 样本群变化、是否可在现有 frames 中配对；对 90% plateau、median、最长 lag 的取值分别报告敏感性。
- 跨尺寸斜率：尺寸按均等权重、原始 1/2/3 个训练 seed 全报告；用 episode 配对抽样和 seed-level uncertainty，报样本数不足与不确定性，不强行求窄区间。
- 比对报告 224px released 模型与 64px S 的不同规格与 eval 约定，复验代码中 goal threshold、action chunk 和 frame normalization。

**若 D0 发现**相关性来自不同 seed/任务条件混用、随机起点不匹配、mh 样本群变化或不完整表格，则立即降级相关主张；不用跑任何新机制实验来“救”。

### D1：决策排序分解（先重算已有 bank，必要时极少量新计算）

**问题**：随模型变大，恶化来自 encoder/goal metric，predictor dynamics，还是 search optimization？

给每个固定 start-goal 和相同真实候选行动 a_j，定义：
- 真实任务效用 **U_j** = env-grounded progress 到 goal（TwoRoom 可报告绕门 geodesic 与实际 success；PushT 要用位置+姿态和真实任务 termination，不能任意混不同单位）。
- **C_oracleφ,j** = cost(φ(real terminal_j), φ(goal))：true dynamics / encoder/latent metric，不涉及 predictor。
- **C_pred,j** = cost(predicted latent terminal_j, φ(goal))：原模型预测 + 相同 latent 代价。
- 在固定候选库上再对 SFA、TEMPO/CTWM（若可用）计算 C_oracle^metric,j；受限测试阶段只比较原 L2/SFA，避免先调很多新 loss。
- 输出 conditional Kendall τ / Spearman、top-1 oracle regret、best-of-N 真实效用、错误候选边界的分布、预测和真实成本排序反转的比例；统计单位以 start-goal episode 为主，训练 seed 另层。

**三种竞争机制与区分预测：**

| 解释 | 随 scale 变化应观察什么 | 怎样推翻 |
|---|---|---|
| H_geo: 目标度量的真实决策几何在变差 | even C_oracleφ vs U 的排序、可达正例 margin 随规模下降；C_pred 可能接近 C_oracleφ | true-end metric 排序不随规模降 |
| H_dyn: 预测器的动作差分信息变差 | C_oracleφ 正常，C_pred vs C_oracleφ 随规模下降；specific action response error 增 | 在真实动态替换后仍相同变差 |
| H_search: 搜索与代理成本的相互作用 | 固定 bank 的 C_pred 排序可用，但真实 CEM 随 scale 变差；更多候选产生 reward hacking / distribution shift | 同候选 bank 中 oracle/pred rank 已明显变差 |

**判定规则**：必须至少找到一个方向在 matched episode + 足够 candidate support + 多训练 seed 下稳定；三种证据若都有解释力就报告 mixed causes，不强行找单一机制。“与 D_eff 的相关性”不能替代决策归因。

**额外注意**：原 oracle_bank.py 的 same/cross-room 划分曾发生过坐标理解错误；重新对照 repo 撤回记录和 simulator 几何图，先把 geodesic 函数验证完，不允许把旧 cross-room 结果当独立机制证据。

### D2：真正隔离规模变量（只有 D1 有重要发现后才训练）

**强问题**：“这个反向趋势究竟依赖于更多的模型表达能力，还是仅仅因为我们把 latent 输出维度与参数量绑在了一起？”

当前缩放各档 width/depth/predictor/latent-D 同时变，原 E21 的 fixed D=192 对照应先读取**是否已有成熟结果**。如尚无足够读数，最简二因素设计：

- **宽度 scale**：S vs M（或 XS vs S）。
- **latent D**：两档固定相同 D（例如统一 192）和默认 D=width；确保架构可实例化且没有极端 bottleneck 崩塌，必要时先小样本精确 preflight。
- 同 task、same data split、training schedule 与 loss、seed、candidate bank；报告训练 loss、真实行动排序、closed-loop success。
- 关注“跨尺寸在固定 D 时还能否保持原 L2 反向趋势”，不是争取涨点；无法保持则之前的叙事要改为 **embedding interface dimensionality tradeoff**。
- 如果 λ/正则是候选因果，还要区分“只改变 λ”的训练干预与“冻结 encoder 后仅修改 cost eigenweights”的**决策使用**干预。后者可以在 same checkpoint/same bank 上进行，不必重训。
- 3 seed 是最低建议信息阈值，不够就注明 pilot。不要先上 285M 全矩阵训练。

**直接止损条件**：固定 D 后趋势消失且仅剩旧 TwoRoom 的视觉/训练协议特例，同时 CTWM/TEMPO 已充分解释代价问题，则原 I16 的独立 scale-mechanism 论文优先级应下降。

### D3：对齐真正强的算法基线（不是只比低质量 L2）

排序数据有意义、规模因果有望成立后，才公平比较：

1. **默认 LeWM L2**（原协议基线）。
2. **训练后线性 SFA**（I16 代价，记录 basis 估计成本）。
3. **TEMPO**（额外 temporal head 拟合，冻结 WM）。
4. **AnisoWM / CTWM**（训练期学不同 latent 几何；不能直接用该训练权重宣称同一 encoder 的 posthoc head 公平）。
5. **强控制器 GC-IDM**；仅作为“representation 能否被非搜索控制器使用”的正对照。
6. **True utility oracle**；用固定 candidate bank 构造 upper bound，绝不作为可部署方法。

方法比较需要同时公布 **训练消耗、额外 fit 数据、参数数量、推断搜索成本**，并严格比较相同起点 goal、动作预算、success criterion。不能把“zero WM retraining”当成“zero learning overhead”。

**预想反常的反面**：若 CTWM/TEMPO 已在各种 scale 下完全解除所谓 inverse scaling，那么故事可能退化成“原作者的 naive L2 接口随 D 变差”。这仍然是观察，但不一定具备独立主张价值；除非能抽出对更广类 representation-based agents 很重要的失配规律。

### D4：域外验证只选会改变认知的不同结构

按照证据和算力选择两种**机制上不同**环境，而非无差别增加 benchmarks：
- 导航：带图连通 bottleneck 与绕墙的 PointMaze-large；既能看 geodesic ranking，也能检验 slow metric 有无拓扑误导。比再加一种 TwoRoom 贴图更强。
- 操作：PushT 或 Cube；task progress 不能简化为位置 Euclidean；需要记录姿态和接触控制历史。若 SFA 的慢特征失效，区分“丢掉瞬时关键变化”与“planner 搜索本身难”。
- visual-antmaze 所有 cost/control 都失败时，既不能当方法有效验证，也不能排除预测/动作可达瓶颈；无需强行救一个含地板效应的 case。
- 理想外部验证：固定 D 的其它 anti-collapse regularizer（VICReg）、非 SIGReg 预训练特征。但 E24 当前暂停且没有结论，任何新通用主张都应保留此不确定性。

## 二、如何避免再次进入几十种 loss 与超参的局部优化

决策流：

1. **D0 是否确认数据、评测和置信度可信？** 否 → 修测量；不讨论机制创新。
2. **D1 是否在固定候选集上找到稳定且非零 support 的“规模与任务效用排序”变化？** 否 → I16 目前最重要的主张是部署特定观察，且与强近邻高度重叠；不新增 aux loss 追数字。
3. **D1 能否区分几何/动态/搜索中的真正瓶颈？** 否 → 先精读对应近邻的原始实验和关键代码，再做一个区分实验，而不是 4×5×10 暴力 grid。
4. **D2 改变 width 与 D 的耦合后该判断仍成立吗？** 否 → 撤回广义“参数量”的表述，改为具体 interface 现象。
5. **强近邻已完整解释同样事实吗？** 是 → 不复制其方法，不预定要发表同样结论；沿真实未解释的误差结构或领域适用条件重新找问题。
6. **结论即使成立，会改变什么研究选择？** 比如：建模是否应优化预测器、何时冻结 WM 改代价、尺度扩大何时必须换 planning interface、哪些旧评价假设失效。若答案只有“又找到一组变差曲线”，未达到科学尺度。

## 三、供人选择的三种研究走向

| 方向 | 重要问题与潜在贡献 | 主要 novelty 风险 | 先做的低成本确认 | 本轮优先级 |
|---|---|---|---|---|
| **A. Scale–decision alignment gap** | 预测质量随参数变化，真实决策排序为何不同步；找到因果分解/适用条件，说明哪些 WM 扩容对 agent 真有用 | JEPA-WMs、VIScore、CTWM、Planning Limits 均很近；scale 尚未隔离 | D0 + D1；必要时 D2 2×2 | **第一** |
| B. Task-dependent latent spectral tradeoff | 为什么满足长程导航的慢谱权重，在接触操作上伤害任务条件控制；是否可理解为不同决策时标的冲突 | CTWM、AnisoWM、ALPS、TEMPO 已讨论几何 | 固定 checkpoint 上选 slow vs original 的真实动作排序反例，非成功率超参 | **第二** |
| C. From latent closeness to true reachability / controllability | 哪些行动目标相似但不可达；如何判断 latent cost 在什么域中失效 | Reachability/temporal metrics/ALPS 系列非常拥挤 | 更真实的 obstacle/topology 任务中整理 failure case，再找精确缺口 | 第三 |

**推荐先保留 A 作为科学复核的问句**，而不是已确定的论文 idea。若没有辨识度，宁愿回到新 territory，不把当前大量 GPU 投入当作必须继续的理由。方向 B 若出现真正任务时标冲突可以独立成为更一般的问题，但**不要为了“有趣的反常”预设它必须成立**。

## 四、工作台执行代理必须带着哪些上下文

重新执行相关实验之前，至少读本目录的 [科学审计](I16_SCIENTIFIC_AUDIT_2026-10-11.md)、[论文近邻](PAPER_NOTES_2026-10-11.md)、旧 [E21](../experiments/E21-scaling-planning.md)、[E22](../experiments/E22-latent-bandwidth-law.md)、[E23](../experiments/E23-paper-grid.md)；检查当前 README 的停机和排程状态。使用原 bank / oracle_bank 资产优先、逐 run 保留 seed 和 eval-pair、所有最初观测的失败例。

每个 proposal 至少写：
- 可观察的目标行为与**独立于模型输出**的真任务效用；
- 两个或以上竞争解释及各自会在哪个结果被推翻；
- 最强相邻工作及是否真的有区别；
- 一个高支持度 matched-benchmark / experimental negative control；
- 为什么值得继续而不是 mere benchmark point gain；
- 坏结果将怎样具体改变研究方向。

这不是按第几周推进的排期。**任何实验是否执行、是否开新线、是否变更状态，仍由研究者决定。**
