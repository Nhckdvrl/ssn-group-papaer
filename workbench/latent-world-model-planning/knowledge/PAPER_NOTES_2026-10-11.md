# I16 文献深读与最近邻距离（2026-10-11）

**研究对象**：紧凑视觉 JEPA / latent world model；端到端表征、latent 代价、基于搜索的决策；重点是“模型变大后能力为何不一定更好”。**不是**泛泛收集世界模型论文。

**证据层级**：A = 本次定向检查原文方法、实验及其边界，并与 I16 具体主张对照；B = 查核论文官方摘要/已发布会议页面并结合工作台已有精读，重要实现尚待代码复核；C = 相关线索，仅索引。研究思路的“idea 从何而来”是我们根据已有工作的可解释重建，不是作者的发现过程自述。**所列论文中除明确标记 ICML 2026 的论文外，不能仅凭 arXiv 日期声称已获顶会录用。**

## 0. 直接相邻工作坐标

| 工作 | 2026-10-11 可核验身份 | 已经做了什么 | 对 I16 新颖性的实际压力 |
| --- | --- | --- | --- |
| [CTWM](https://arxiv.org/abs/2610.01373), Hauri et al. | 2026-10-01 arXiv，A | Laplacian eigenvalue scaling 与 commute-time metric；证明部分理想设定下能恢复相关表征；世界模型目标和规划共同修复 | **极高**：各向同性破坏规划几何、低频谱/任务距离，不是我们的首创 |
| [AnisoWM](https://arxiv.org/abs/2609.37441), Kang et al. | 2026-09-29 arXiv，A | 推导 isotropic Gaussian 目标与任务成本失配，训练 learnable anisotropic covariance，测排序和下游规划 | **极高**：SIGReg 导致成本权重错配的机制已经有理论与实验 |
| [TEMPO](https://arxiv.org/abs/2610.04988), Moukheiber et al. | 2026-10-04 arXiv，A | 冻结 WM 后只拟合 temporal metric 小头，用示范时间间隔，无任务标签，11 环境 | **极高**：事后恢复长程规划、无需重训世界模型与 SFA 的方法距离很近 |
| [The Objective Is the Bottleneck](https://arxiv.org/abs/2608.12959), Singh | 2026-08-13 arXiv，A | TwoRoom 的 L2 随远距离饱和，换 latent 目标距离大幅修复；信息仍可读出 | **极高**：最初的长程失败现象及“错误在 objective”基本已被占 |
| [Temporal Straightening](https://proceedings.mlr.press/v306/wang26n.html), Wang et al. | **ICML 2026**，B | 对轨迹施加曲率约束，让欧氏距离更近似测地距离 | 高：几何–可规划性机制早已有顶会扎实证据 |
| [Laplacian Representations for Decision-Time Planning](https://proceedings.mlr.press/v306/shehmar26a.html), Shehmar et al. | **ICML 2026**，B | Laplacian 表征 + ALPS，利用多时标结构和子目标 | 高：SFA/低频带来的远距离可规划性不是全新 |
| [SCALE](https://arxiv.org/abs/2608.16287), Hu et al. | 2026-08 arXiv，A/B | 训练时用特权状态校准 latent 与 task distance；区分可解码与能用于 L2 排序 | 高：可解码不等于规划几何，已被明确提出 |
| [JEPA-WMs / What Drives Success](https://arxiv.org/abs/2512.24497), Terver et al. | 2025-12 arXiv，B | 对 encoder/predictor/训练/搜索做设计空间试验；某些仿真规模没有收益 | 中高：大模型不一定使规划更好并非此前无人发现 |
| [The Planning Limits](https://arxiv.org/abs/2609.39235), Alrasheed et al. | 2026-09-30 arXiv，A | 冻结多个视觉编码器，单放大 predictor 81× 未提升计划有效范围，真模拟器仍有局限 | 高：预测容量不等于可规划视野，缩放已有负证据 |
| [VIScore](https://arxiv.org/abs/2608.11174), Wu et al. | 2026-08 arXiv，B | 将 encoder/predictor/planner 的诊断相结合，比纯表示指标更关联成功率 | 中高：想主张一个新诊断量，须先对齐其强测量 |
| [Latent Geometry Beyond Search](https://arxiv.org/abs/2605.08732), Nguyen et al. | 2026-05 arXiv，B | Frozen LeWM latent 上 GC-IDM，七/八设置追平或超过 CEM，单步算力大幅下降 | 中：同 latent 的 strong controller 很好，但不能代表同一 metric 有效 |
| [Surprising Difficulty of Search in MBRL](https://proceedings.mlr.press/v306/chang26a.html), Chang et al. | **ICML 2026**，B | 准确模型下搜索仍可能伤害性能；价值高估比单纯预测误差更关键 | 中：CEM 失败不可一律归咎于 latent，强竞争解释 |
| [Perception for Action / Predictive but Not Plannable](https://arxiv.org/abs/2605.07278) | 2026 arXiv / 工作台已有定位，B | 增加动作/可达性相关目标，检验表征与决策适配 | 中：方法基线/行动相关误差 |
| [Imperfect World Models are Exploitable](https://arxiv.org/abs/2605.15960), Bhamidipaty et al. | 2026 arXiv，B | 分析错误世界模型引发的策略排序逆转及安全规划边界 | 中：为 action-ranking 可靠性提供理论定位 |

## 1. CTWM（最强直接邻近，A）

**研究切入点**。规划器按表征欧氏距离选动作；理想情况下距离应反映环境中往返通行时间（commute time），而标准各向同性反坍缩目标抹平图拉普拉斯谱所需的特征权重。这是比“某个 latent L2 不好”更一般、更科学的命题。

**方法与理论**。作者以 Laplacian 光谱为理论桥梁：按特征值倒数的平方根缩放本征函数，平方欧氏距离对应截断谱的 commute-time / resistance 几何；提出 latent displacement predictor 及 log-det covariance 防坍缩项。其最优性保证需要**确定性、可逆动态及 predictor 固定点等条件**，不能不加条件扩大到一般耗散/不可逆机器人环境，也不能把 commute time 等同于 shortest-path geodesic。

**决定性证据**。合成图域检验谱几何是否恢复，然后在视觉 goal-reaching 中对比 LeWM。论文报告 TwoRoom 100-step 目标 17.3%→98.3%、PointMaze 100-step 28.2%→98.8%，Cube 25-step 64.8%→89.8%，PushT 25-step 91.5%→92.2%。这些是**该文自己的独立评测协议**，不能与 I16 的 64px、不同训练/测试样本直接比百分点。

**可能的 idea 成长路径（推测）**。先从“L2 规划应该使用哪种距离”追溯 classical graph commute time / representation learning，辨认 isotropic constraint 与目标谱权重矛盾，再从图论可计算 toy 推到神经非凸训练的有效性。与 I16 的“先做缩放得到反常，再找解释”是不同的研究出发点。

**所有权边界**。I16 不得宣称首提各向同性与长程规划矛盾、首次用慢谱或几何修复；可继续研究的仅是独立于 CTWM 的**规模-目标耦合规律**、在固定维度/配方下的变化、对哪种搜索决策造成可验证的排序错误，以及它们是否超出已有谱解释。优先强基线：CTWM 本身（公开代码仓库 https://github.com/fmi-basel/commute-time-preserving-world-models）。

## 2. AnisoWM（训练归因最强邻近，A）

**问题**。即使预测准确、表征防坍缩，latent Euclidean cost 仍可能以与 task cost 不同的方式给候选动作排序。作者在局部线性/高斯近似下追踪目标协方差怎样塑造等价的状态代价矩阵，得到不同优化权重导致的 planning regret。

**方法**。把 SIGReg 的固定各向同性 Gaussian target 改为具有固定 trace、受 anisotropy 约束的可学习对角协方差目标 Λ；保持原 predictor 与 Euclidean planner，避免把后续收益误归因于换控制器。

**证据**。本文报告 LeWM→AnisoWM 在 TwoRoom / Reacher / PushT / Cube 均有规划改善，且专门检查 action ranking alignment。也有有趣的负界：在某些操作任务，task alignment 指标并不与成功率完全同步，提醒不同对象/工作区的度量解释不应强行统一。

**对 I16 的冲击**：I16 的 λ 干预支持“正则权重改变一整套系统的规划结果”，但不再能宣布“SIGReg 破坏几何”是我们的新理论。更重要的是，同 λ 改变 **prediction loss 相对权重、latent scale、训练轨迹、模型收敛路径**；在我们的实验里这不是一个对 D_eff 的隔离干预。

**可借鉴设计**：保持预测器、规划器和 goal 样本相同，只改几何偏好；区分“输出状态预测排序一致性”和“task utility 排序一致性”；提供改进前的预测反例，不只平均提升。

## 3. TEMPO（事后代价修复最强邻近，A）

**问题**。远距离目标时，接近目标帧的 embedding L2 与剩余需要的动作/时间不相等。即使轨迹中早就有时序信息，世界模型仍可能使用了错误的决策界面。

**方法**。冻结世界模型与预测器，只在其 latent 上拟合小型 temporal map，使用离线示范轨迹的时间间隔构造监督信号；用学到的 temporal distance 与原 L2 代价混合。测试了 LeWM、PLDM，涵盖不同环境类别约 11 种。

**证据**。论文报告 TwoRoom 约三个规划视野外的目标成功率从 36% 提升到 99%；小头开销低。作者强调不用额外 reward/policy/success 标签，**但确实训练了一个新 temporal map**，因此“frozen WM、不重训 WM”不等于绝对无训练。

**与 I16 SFA 区别**。I16 通过训练轨迹的协方差广义特征分解，使用线性慢方向，属于对已训练 latent 的**事后估计**，无需训练新的神经网络；TEMPO 训练非线性 mapping。SFA 是较便宜但可能更受弯曲流形与拓扑阻塞影响的方案。若以方法形式发表，至少对齐 TEMPO + CTWM + pure SFA/Laplacian + 训练时 geometry shaping；比较测试分布变化、真实样本支持、运行时间、跨尺寸稳定性。不做这个对齐而仅说“freeze + no extra labels”不可取。

**科学分界**。两者共同说明原 L2 不是最优控制目标，却没有证明**为什么网络参数增多会系统性加剧**这一失配，或哪个表示指标能够预测这种加剧。

## 4. The Objective Is the Bottleneck（I16 出发点的最强邻近，A）

**问题与起点**。通常归咎于预测器 rollout 误差；作者检查未来状态预测其实保留很多位置线索，而 CEM 的目标 L2 已对真实远距离丧失排序能力：潜在 L2 只在局部有效，到了某段距离后饱和或反向。通过 frame separation 学的代价优于精准位置 probe，因为更接近可达性而不只是坐标近。

**证据**。冻结 LeWM 的 TwoRoom，位置可以被高 R² 的线性 probe 恢复；换目标函数，不重新训练 WM，长程成功从约 26% 提到 98%。这说明“信息在 latent 中但 naive planning 不会用”**不是 I16 可宣称的初次发现**。

**新问题的成长**。先检验常见失败解释（预测模型不够好），再通过真实轨迹位置读出与 long-distance latent 距离，发现正确的干预对象是决策目标。这里非常值得学习的是**在同一个失败上换验证方法后，找到了比修改 world model 更本质的原因**。

**与 I16 的区别**。本文没有系统沿模型规模展开保持协议的 1.7M–285M 路线；但 I16 的规模规律还须控制架构和训练预算，以及 CTWM/AnisoWM 已提出的几何因果。

## 5. The Planning Limits of Latent World Models（容量不能等同于计划范围，A）

**问题**。同一预训练视觉 backbone 下，扩大 action-conditioned predictor 后，agent 真的可以把更远的 goal 排序正确吗？

**设计**。冻结多个 pretrained encoder，在 MetaWorld 与 BridgeData V2 操作任务上放大 predictor、调整 rollout 训练范围，测真计划/反馈/真实模拟器 oracle，还做 VLA 候选再排序的实际任务实验。

**关键读数**。论文报告预测器尺寸放大 81 倍，仍没有让 5-step rollout 的可用控制目标从 5–10 步扩到远目标；用真模拟器也难处理超过已展开规划的目标（goal 5→20 时成功 92%→41%）。给近目标专家子目标有显著改善。这说明有些瓶颈甚至在完美动态下仍存在。

**设计限制**。这里主要是冻结 encoder + 改 predictor，不是端到端同配方随全模型参数缩放；任务分布与 I16 TwoRoom / PointMaze 也不同。不能以此宣称其已证明 I16 的规模机制，但足以反驳“此前没有人研究模型变大为何不助规划”。

## 6. 与规模/测量解释相互制约的工作（B）

### JEPA-WMs / What Drives Success

**问题**：结构与训练过程中的哪个设计选择决定物理规划成功，而不只是预测损失？考察 encoder family、predictor 容量深度、loss、规划器。本文的一个直接含义：某些仿真任务中更大 encoder/predictor 并没有取得预期规划收益，而真实数据上的情况并不相同。I16 要更清楚地在“规模效应”与“不同任务收益曲线”间定位，不能使用“第一次观察 scaling nonmonotonic”排他用语。

### VIScore

提出超越 latent 表示本身的 encoder-predictor-planner 联合质量测量；报告相较 probe、直线性、empowerment 等更能预测跨 task 成功。**I16 的单一 D_eff 或 metric horizon** 如果升级为预测诊断指标，必须与此强邻近比较；尤其应在冻结研究假说后测试独立模型家族，不得只用同一 SIGReg/width 扫描拟合 R²。

### SCALE

训练期用 task-relevant privileged state 使 latent 方向支配欧氏代价，与只做 state probe 不同；一项关键区分是 **信息可被线性读出 ≠ 任务相关方向在欧氏成本里得到足够权重**。I16 慢方向有效也未证明它们是唯一正确的方向。SCALE 需要特权标签、I16 SFA 不需要，这是方法上的真实区别，但不自动构成重要科学新知。

### Temporal Straightening（ICML 2026）

作者把时序轨迹的几何曲率与 geodesic proxy、规划目标的条件数联系起来，使用训练正则。I16 的“时间拉直会帮助导航、伤害操作”可能是有意义的边界观察，但首先要用此文中已有实验设计、损失和操作正则对齐，确认新颖部分是**何时会产生损害**而非“拉直和导航几何相关”。

### Laplacian Representations for Decision-Time Planning（ICML 2026）

多时标的 Laplacian 特征、ALPS 子目标分解直接支持慢谱方向对长距离结构有用，也提示 I16 k=4 线性 SFA 的局限：跨墙、拐角和瓶颈不一定能由单个欧氏谱空间中的直线势函数良好表示。接近的还有 [From Representation to Action: Unified Laplacian Framework](https://proceedings.mlr.press/v306/zuo26a.html)（ICML 2026）。

### Latent Geometry Beyond Search（GC-IDM）

该文的强 baseline 是把当前 latent、goal latent、剩余视野映射到动作的轻量 amortized policy，在四个 benchmark 中 7/8 个 setting 不弱于 CEM，决策开销约 1/100–1/130。I16 在同一 latent 下用 GC-IDM 成功，可以说明信息可由**另一个经过训练的控制器**利用，**不能**自动证明旧 CEM 失效完全来自各向同性，更不能将 GC-IDM 用作高可信“真实代价 oracle”。

### The Surprising Difficulty of Search in MBRL（ICML 2026）

本工作提示搜索/价值高估偏差、分布移位与模型精度的相互作用可能主导结果。具体到 I16，真动力学替换 encoder/目标代价后并不代表消除了搜索本身的问题；必须有真正的 true terminal state、true utility 和固定候选库，分开模型误差、目标误差与搜索失败。

### 其他机制/边界参照

- [Perception for Action / Predictive but Not Plannable](https://arxiv.org/abs/2605.07278)：action-sensitive / reachability 的损失塑形。
- [Imperfect World Models are Exploitable](https://arxiv.org/abs/2605.15960)：理论上候选政策之间的预测选择偏好可能被真环境翻转；I16 的候选排序分解更接近此处的决策视角。
- [Impact of Connectivity on Laplacian Representations in RL](https://proceedings.mlr.press/v306/giorgi26a.html)（ICML 2026）：图连通性影响谱表征和价值近似。慢特征恢复长程目标的结果应对数据连通结构保持谨慎。
- [The Evaluation Protocol Determines the Result](https://arxiv.org/abs/2608.10145)：独立 LeWM 复现说明评测约定大幅影响成功率，必须审计 action chunks / normalization / goal selection。
- [LeWorldModel](https://arxiv.org/abs/2603.19312)：端到端 JEPA + SIGReg 的低成本、可缩放基础模型，不是 I16 研究结论的对照作者。

## 7. 可继续探索的解释空白（不等于找到论文贡献）

**空白 A：什么才导致随着规模扩大，任务相关的动作排序反而下降？** 
已有文献说明 metric 不对；缺少的是**在规模、embedding D、训练正则、预测 fidelity、决策 candidates 分离之后，能否识别一个跨环境重复的规律**。I16 目前连“参数增加”这一变量都没有单独隔离，先做审计再谈 novelty。

**空白 B：为什么同一形式的度量修复在导航表现很好、操作反而有害？**
竞争解释至少有：(i) temporal slow features 扔掉接触瞬时变化；(ii) PushT 的可达性由动作历史而非像素静态潜在决定；(iii) 搜索预算、动作随机性、各任务起点和目标时间间隔不同；(iv) 修复仅把导航的简单目标几何读出来，仍不能处理拓扑墙约束。需要独立的 matched ranking/trajectory 对照。注意 TEMPO、AnisoWM、CTWM 已测操作，因此“任务差异”本身也非空白。

**空白 C：planner-relevant ordering 在什么条件下可由无标签的表征统计预先预测？**
已有 VIScore 与其他 action-ranking benchmarks 非常强；I16 新的 metric horizon 目前是启发式，不足以宣称第一种泛化诊断。更好的可能是**预测何时不同决策界面会给同一候选集合出现可逆转的 ordering**，但这仍是候选题，非结论。

## 8. 继续深读/代码复核的精确问题

- CTWM：更换目标后 improved geometry 的主要来源是 eigenvalue scaling、网络容量，还是训练时间/任务分布？复现代码的 predictor 如何算 commute-time task cost？
- TEMPO：时间间隔监督的训练/评测轨迹怎样分离、时间距离是否区分绕墙路径、是否改变 CEM 其他超参？对照纯线性 SFA 的公平度怎样？
- AnisoWM：学习协方差的 stationary point/线性近似和任务概率分布条件；不同 task action ranking 的负例。
- VIScore：三部分计算是否可用我们已有轨迹而不需要新标注，校准 vs 相关性如何定义。
- JEPA-WMs：sim vs real 大 encoder 不提升的协议和优化预算，是否真正 matched compute。
- LeWM：官方 224px / action chunk / normalization、评价 split/候选数与 I16 64px 的差异。

本笔记不是“十几篇都逐节、附录、源码全面复现”的冒充；每一项用 A/B 标记核验范围，下一轮补核这些具体缺口比继续无差别扫论文更有意义。
