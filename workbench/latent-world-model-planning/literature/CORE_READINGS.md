# 核心阅读｜从已有工作长出研究，而不是绕开已有工作

定向回读：2026-10-02。S1–S6是本文件局部来源ID，不覆盖历史P编号。

**范围：** 本轮核对S1–S3/S5主文的相关工作、方法、实验设计与部分附录设置；S4使用用户提供的35页v1全文。S6定向核对主文方法、related work和理论适用范围；不是对所有引用和定理逐项复验，也不把历史近邻全部宣布为本轮已读。以下“可生长方向”是我们的研究推演，不是已验证空白。

## S1｜DINO-WM

来源：[论文](https://arxiv.org/html/2411.04983)，重点§1–4、App.A.4–A.5。

**原文依据：** 母问题是离线、任务无关模型能否支持测试时行为优化。它借用冻结DINOv2 patch features，训练动作条件预测器，并在特征目标上规划；decoder与预测训练分离。实验比较表示、decoder、规划器及环境配置泛化；部分online-RL基线被改到离线无奖励设置，不能把表格写成那些算法原生能力的普遍排名。

**我们的生长分析：** 新意不是首次使用latent或MPC，而是用成熟视觉表示重新组织任务信息与预测、减轻对额外任务监督的依赖。相同领域里可继续研究表征适配、长时预测和任务复用；应复用它的可运行设计，再提出具体改进，而不是宣布“latent规划已有，不能做”。

## S2｜PLDM

来源：[论文](https://arxiv.org/html/2502.14819)，重点§3.3、§4、App.D/G/J/K/L。

**原文依据：** 用JEPA-style latent dynamics与规划，对比GCBC/GCIQL/HIQL/HILP/CRL等，在数据量、质量、轨迹长度、跨房间连接和泛化条件下研究方法表现。固定总转移数改变轨迹长度是一种控制；去掉过门轨迹时PLDM也明显下降，不能总结成model-based普遍胜出。

**我们的生长分析：** 这类工作把“哪个算法强”变为“什么数据条件下更好”，比较与方法共同产生认识。R1可以继续改进数据使用与采集；R2可以用这些条件研究预测组织。并非只有发现一个所有控制之外的残差才可形成贡献。

## S3｜LeWorldModel

来源：[论文](https://arxiv.org/html/2603.19312)，重点§1–4、App.D–G。

**原文依据：** 它针对端到端JEPA训练脆弱和配方复杂，采用next-embedding prediction与SIGReg高斯正则，联合训练encoder/predictor；用控制、稳定性和消融支持设计。论文报告紧凑单GPU实例，但具体成本依赖配方与评测。

**我们的生长分析：** 重要问题可通过简化与稳定方法解决，不必先发明一种全新失败。LeWM适合作为可修改的公共支点；更好的多时域学习、条件化、数据目标或恢复策略都可以从这里试，只须最终证明实质收益和范围。

## S4｜RC-aux

来源：用户上传 `2605.07278v1.pdf`；[公开标识](https://arxiv.org/abs/2605.07278)。重点§2–4、App.B.5–B.7、C/E。

**原文事实。** 论文主动继承DINO-WM/PLDM/LeWM以及已有规划几何、reachability、多步训练思路。它保持backbone，把multi-horizon open-loop训练与budget-conditioned reachability组合，并允许planner使用该信号。不是宣称第一次发现预测不等于规划。

**决定性比较。** 主表有matched continuation控制；Wall的LeWM为50.4，RC训练但planner coupling为0时72.4，完整配置83.6。这个分解让“训练改了什么”与“使用方式改了什么”分开。Reacher训练侧单独并非提升；Push-T matched差值为-0.4，范围并不普遍。评测组标准差也不是独立训练seed方差。

**语义边界。** 第5页和App.B.5明确：观察到Δ步后到达只给出一条可行路径，不证明更短路径不存在。训练得到的是数据诱导的经验关系；测试planner是软折扣，不是可达性证书。第8/9页参数和cost-call测量不能推出端到端训练/评测都便宜。

**我们的生长分析。** 这正说明熟悉的元素并不封死研究：贡献来自围绕有限预算规划需求重组训练与使用接口，并用合理控制证明作用。后续可以改善监督可靠性、利用多路径/失败数据、学习更好的使用方式；不必把问题削成“排除所有已知因素后的一点异常”。

## S5｜Bagatella等 TD-JEPA

来源：[论文](https://arxiv.org/html/2510.00739)，重点§3–5、App.10–11。**不是**Bai/Xiong的Temporal-Distance JEPA。

**原文依据：** 它把长期policy-conditioned预测联系到successor features，用TD目标从离线转移学习，并允许state与task encoders分离。实验包括预测目标、共享/分离编码器等消融，在ExoRL/DMC与OGBench评测。任务推断与policy部署方式不同于图像目标MPC。

**我们的生长分析：** 不能只因为二者都叫JEPA就直接排分数，也不能因为已有长期预测便不做R2。可以先在可控公共系统比较预测结构，再扩到不同长期抽象；新混合方法、计算效率或任务复用改进都可作为贡献，不强制出现普适regime定律。

## S6｜Temporal Straightening：相近工作如何成为起点

来源：[ICML 2026正式论文入口](https://proceedings.mlr.press/v306/wang26n.html)；本轮读到的[arXiv HTML v2](https://arxiv.org/html/2603.12231)标注2026-06-11，重点§2–4、§5与App.B.5；不把此HTML版本默认等同所有后续更新。

**原文依据。** 方法受perceptual straightening启发，对连续latent位移的夹角作正则，并联合预测学习。Related work明确承认DINO-WM、已有时序对比、早期线性化/曲率研究；它不是因为这些方向有人做就避开，而是把曲率与规划目标的条件性、梯度优化稳定性联系起来。理论针对线性动力学，非线性推广需额外条件，不能写成一般保证。

**我们的生长分析。** 它展示了方法驱动与问题驱动的结合：从一个已知原理出发解决世界模型规划中的实际困难，新增贡献由设计、解释与控制实验共同支持。类似地，我们可以研究更有效的多时域目标、数据监督或可靠规划结构；真正要比较的是新增什么，而不是有没有使用相似词语。

## 共同的idea来源重建

这些例子不是互相等待“空白”：成熟视觉表示、潜在动力学、goal-conditioned学习、TD与规划结构被用于解决具体障碍。我们学习的是选择哪个设计决定、如何给出证据、如何承认边界。研究计划提出的五个方向均可从这些方法与历史近邻继续发展；尚无证据证明其中任一新方案已成立。


## S7｜JEPA-WMs / What Drives Success：把一个新范式的设计空间做透

来源：[论文](https://arxiv.org/abs/2512.24497)。本轮阅读深度：**A-targeted**，定向核对主文关于multi-step training、context/proprioception、planner以及explicit/implicit discussion；不是逐附录复核。

**原文依据。** 这项工作不靠“发现一个无人研究的问题”，而是把DINO-WM之后的JEPA planning recipe系统拆开。一个重要结果是multi-step rollout训练的最佳长度依domain而变：递归部署需要稳定性，但更长训练并非无条件更好。论文还明确区分explicit action-conditioned WM与把长期预测结构摊入representation/policy的implicit方案，并把训练成本、部署计算和generalization的直接比较留作未来工作。

**我们的生长分析。** R2不应继续搜索“没人做过的horizon”。更有价值的是改变预测计算的**粒度和使用位置**：哪些候选需要昂贵预测、哪些可以便宜筛掉；什么时候direct prediction、recursive prediction或长期抽象值得花计算。

## S8｜Fast LeWorldModel：直接prefix prediction已经是强近邻，不是禁区

来源：[论文](https://arxiv.org/abs/2606.26217)、[官方代码](https://github.com/Yuntian-Gao/Fast-LeWorldModel)。本轮阅读深度：**A-targeted**，核对摘要、方法/消融与官方README；代码尚未在本地运行。

**原文依据。** Fast-LeWM用action-prefix prediction并行预测不同horizon的future latent，绕开LeWM逐步recursive rollout。官方项目在与LeWM相同的Four-task规划协议中报告更高平均成功率和显著更低dynamics/CEM时间；还用direct-vs-decomposed terminal prediction做self-consistency。

**与我们的距离。** 因此“直接prefix预测”“更快的LeWM”“多horizon head”都不能单独当贡献。它反而提供一个理想**低保真预测器**：先便宜地给大量CEM candidates排序，再只对少量可能进入elite set的候选调用更昂贵的recursive/refined predictor。这个planner-stage fidelity allocation不是Fast-LeWM本身的主问题。

## S9｜DeepJEPA：decision-critical compute已出现，迫使R2把问题说清

来源：[arXiv:2610.00368](https://arxiv.org/abs/2610.00368)、[公开仓库](https://github.com/deepjepa/DeepJEPA)。本轮阅读深度：**A-/方法与实验**：2026-10-02 接续深读 v1 正文、elite stability 命题、matched-seed experiments 与 Appendix D；官方仓库尚未 release，不声称复现。

**原文依据。** DeepJEPA把transition depth作为test-time scaling轴，学习在哪些candidate/rollout step继续recurrent refinement；摘要称额外计算集中在contact/interaction等decision-critical transitions。

**我们的生长分析。** 这不关闭“adaptive compute”。它把最近邻变得更清楚：DeepJEPA分配的是**单个imagined transition内部的深度**；我们R2当前更值得试的是**CEM候选集合/搜索阶段之间的预测保真度**——cheap model广筛、expensive model只重评可能改变elite selection的候选。若最终只是把DeepJEPA换个gate，就没有贡献；若能在fixed wall-clock下证明planner-stage multi-fidelity是独立且互补的轴，才值得发展。

**执行后的精确定位。** DeepJEPA 的 halting 独立作用于 candidate–time pair，并已给出 elite margin 与 correction bound 的稳定性分析；不能把“candidate-selective compute”或 elite stability theorem 说成我们的首次。其训练 target 是局部 latent-error marginal gain，并不直接输入当前 CEM 全体候选的 cutoff；E13 的待测增量是 population-relative promotion/fidelity allocation。Appendix D 明确 average depth 不等于 batched wall-clock speedup，与本轮工程测量一致；必须验证实际 compute-quality frontier。

## S10｜主动世界模型数据：OnlineWM、Task-Sufficient WM、ToIA

来源：[OnlineWM](https://arxiv.org/abs/2609.23753)、[Task-Sufficient World Models, ICML 2026](https://proceedings.mlr.press/v306/feng26aa.html)、[ToIA](https://arxiv.org/abs/2609.19378)。本轮阅读深度：**B/positioning**，核对abstract/proceedings与方法概述；不能据此声称“首次”。

- OnlineWM主动向simulator查询当前预测弱点，并用same-state action contrast强化action-effect因果归因。
- Task-Sufficient WM用active probing采集暴露task-relevant latent factors的轨迹，并学习task-sufficient state。
- ToIA在MPPI+GP residual setting中把active learning从“哪里最不确定”改成“哪些观测能降低当前任务相关rollout的不确定性”，尤其在稀疏更新下有效。

**我们的生长分析。** “active data有用”“task-aware acquisition有用”“same-state counterfactual branch有用”都不是新口号。R1更具体的可试问题是：**planner真正犹豫且候选动作后果会改变选择的地方，是否是最值得花branch-query预算的地方？** 也就是把数据价值锚定到candidate selection boundary，而不是全局prediction error或单条rollout uncertainty。

## S11｜candidate decision本身已经是一个被验证的重要对象

来源：[Beyond Visual Quality](https://arxiv.org/abs/2609.24745)、[AD-WM](https://arxiv.org/abs/2609.30264)；D-JEPA定位记录保留在历史literature。阅读深度：**B/positioning**。

Beyond Visual Quality在same-state sampled candidates上测到真实selection opportunity并发现机会集中在部分决策；AD-WM则直接优化action-discriminative latent dynamics用于counterfactual MPC，并指出whole-bank prediction/ranking指标未必跟closed-loop success同序。

**我们的生长分析。** 这支持“planner decision boundary是有科学意义的对象”，但也意味着不能把“候选排序重要”包装成新发现。R1的增量必须体现在**如何把有限新经验分配到这些决策上，以及这种经验是否比普通uncertainty/coverage数据更值钱**。

## S12｜policy-/decision-aware model learning是更早的思想祖先

来源：[Transition Occupancy Matching, L4DC 2023](https://proceedings.mlr.press/v211/ma23a.html)、[Policy-Aware Simulator Learning](https://arxiv.org/abs/2605.29032)。阅读深度：**B/positioning**。

这些工作已经主张平均prediction loss会把容量/数据花在与policy无关的区域；后者进一步把strategic robustness和active data selection联系起来。

**我们的生长分析。** Decision-Critical Branching不能声称“第一次只学习决策相关数据”。它的潜在新点更具体：在**visual latent MPC的candidate-generation/elite-selection接口**上定义query value，并利用same-reset candidate branches直接改善planner会比较的动作后果。最终是否足够novel要在结果成形后再做专项近邻检索。

## S13｜R2长期预测continuum：UHM与Jumpy World Models

来源：[Universal Horizon Models, ICML 2026](https://proceedings.mlr.press/v306/chung26b.html)、[Jumpy World Models, ICML 2026](https://proceedings.mlr.press/v306/farebrother26a.html)。阅读深度：**B/positioning**。

UHM直接预测任意horizon future以减轻递归误差；Jumpy WM预测预训练policy在多时间尺度下的occupancy，用于组合长期policy sequences。

**我们的生长分析。** R2不是one-step vs successor二选一，而是一个预测对象continuum。首轮不用把所有范式装齐；同backbone的cheap/direct vs expensive/recursive fidelity allocation若有信号，再引入一个long-horizon方法检查故事是否跨predictive object成立。

## S14｜FIRM-WM：intervention branches已经是强支点，真正问题转向“哪些branch值得买”

来源：[FIRM-WM](https://arxiv.org/abs/2609.22816)。本轮阅读深度：**B+/positioning**，核对abstract、方法定位和主结果；未找到可直接安装的官方代码，不声称复现。

**原文依据。** FIRM-WM把reward-free visual planning的两个问题一起处理：goal-comparable configuration与history-dependent dynamic fiber分离；同时在offline factual trajectories之外加入common-reset intervention branches，让模型观察同一状态下不同action sequence的真实后果。论文报告TwoRoom/Reacher/OGBench-Cube三任务、三独立full-pipeline seeds，并明确把intervention data作为模型能力来源之一。

**我们的生长分析。** 这对R1不是“撞车”，反而把下一步问题变得很自然：FIRM-WM回答**branch data有没有用**；我们可以问**在branch预算很有限时，哪些state/哪些竞争action值得branch**。如果每个reset都均匀收branches，真实系统会很贵；如果branch acquisition能直接对准planner candidate boundary，才有可能得到更高的planning gain per environment step。

**2026-10-02 方法/实验深读补充。** 正文 §4/§5 与 Appendix D/F/H 已核对：common-reset 只恢复公开 interface variables；其 branch acquisition 不使用 reward/success/planner rank。训练 source ablation 和 mismatched-outcome control 支持 action–outcome correspondence，但同时用了 typed physical supervision。E16 首版只改 LeWM-family data acquisition，保持 loss/representation；uniform common-reset branches 是必需基线，不能把 factual-only improvement 归因于 boundary selector。

## S15｜critical-state branching不是我们发明的原则，但visual WM里的data-value仍可做

来源：[SPARK, ACL 2026](https://aclanthology.org/2026.acl-long.1100/)、[RMWorld](https://arxiv.org/abs/2608.20126)、经典MPC active learning / dual-control脉络。阅读深度：**B/positioning**。

- SPARK在LLM agent长轨迹中按critical decision states做dynamic branching，以更少rollouts提高探索质量。
- RMWorld在无线控制里按task risk/value-of-information分配channel labels与counterfactual trials。
- 更早的dual MPC/active dynamics learning早已说明控制与信息采集可以联合优化。

**我们的生长分析。** 所以H-A不应叫“首次critical-state branching”。真正可拥有的对象更具体：**visual latent MPC中，使用candidate elite-boundary的不确定性来分配same-state dynamics branches，并直接训练world model本身。** 工作名改为 **Planner-Boundary Branching (PBB)**，避免把跨领域成熟原则包装成新词。

## S16｜multi-fidelity planning也有长历史；R2的增量是latent-CEM elite preservation

来源：2020 RSS [Multi-Fidelity Black-Box Optimization for Time-Optimal Quadrotor Maneuvers](https://www.roboticsproceedings.org/rss16/p032.html)、2025 RA-L parallel multi-fidelity MPC，以及[DeepJEPA](https://arxiv.org/abs/2610.00368)/[Fast-LeWM](https://arxiv.org/abs/2606.26217)。阅读深度：**B/positioning**。

传统multi-fidelity planning已经会把cheap analytical/simulation model和expensive physical/fine model结合，甚至在一条规划中切换不同fidelity；因此“粗模型筛、细模型验”本身不是新思想。2026 latent-WM又有Fast-LeWM的parallel direct prediction和DeepJEPA的transition-level adaptive depth。

**我们的生长分析。** H-B若有价值，必须落在CEM特有的**elite-set preservation problem**：在大量latent candidates中，哪些cheap evaluations足以确定“不可能进elite”，哪些candidate必须升级到高保真预测？这个问题可以用same candidate bank、elite recall和fixed-wall-clock严格测，甚至可以从cheap→high-fidelity residual的校准区间导出安全筛选规则。这个精确接口比“adaptive compute”更有归属感。


## 从这些论文反推：这个领域的“顶会尺度”到底是什么

这张表不是排名，而是研究生长模式：

| 工作 | 继承的成熟资产 | 真正推进的一步 | 为什么不是“小bug” |
|---|---|---|---|
| DINO-WM | pretrained visual features + MPC | 把预训练视觉表征直接变成reward-free dynamics/planning state | 改变world model是否必须重建像素的设计选择 |
| PLDM | latent dynamics + goal-conditioned offline learning | 系统研究数据质量/连接/trajectory structure何时支持planning | 回答model-based与model-free在重要数据regime下的取舍 |
| LeWM | JEPA + latent planning | 稳定、简化end-to-end compact JEPA训练 | 解决方法可训练性/recipe complexity，给后续研究公共支点 |
| Temporal Straightening | temporal representation + latent MPC | 让轨迹几何更适合optimization | 连接representation geometry与planner conditioning |
| RC-aux | LeWM + multi-step/reachability思想 | finite-budget reachability监督 + training/planner解耦验证 | 直接服务有限预算planning，并用Wall等结构任务证明实际后果 |
| Fast-LeWM | LeWM + direct multi-step思想 | 把rollout接口改成action-prefix parallel prediction | 同时解决递归误差与CEM重复计算，方法简单但问题真实 |
| FIRM-WM | compact latent planning + recurrent state + intervention data | goal-comparable state / dynamics fiber分角色，并用common-reset branches校准alternative actions | 处理CEM真正依赖的counterfactual action outcomes |
| DeepJEPA | recurrent refinement + inference-time compute | 把“transition内部算多深”变成自适应资源轴 | 把world-model scaling从更长/更多candidate改成decision-critical internal compute |

共同规律不是“每篇找到完全没人碰过的空白”，而是：

1. **母问题通常早已有祖先。** 新论文重新定义一个具体design decision：表示什么、预测什么、怎样用数据、在哪花计算。
2. **方法往往不大。** 顶会尺度来自问题与证据，而不是参数量或模块数量。
3. **决定性实验通常很直接。** 一个结构任务/强ablation能说明为什么方法该工作，然后跨2–5个任务确认范围。
4. **related work越近，越容易形成清楚delta。** Fast-LeWM离LeWM极近，RC-aux也直接以LeWM为backbone；近不等于不能做，关键是新增的operational question是否重要。
5. **方法和理解可以共同成为贡献。** 不需要先证明一个全新机制才能训练；也不能只有涨点而不解释改了哪个设计决定。

这正是本工作台应该模仿的科研经济学：**先用低耦合小模型快速试一个真实design decision，再用多GPU把最重要的对照、seed和任务范围一次打透。**


## S17｜ToIA / SPARK再读：decision-aware acquisition到底已经做到哪一步

来源：[ToIA](https://arxiv.org/abs/2609.19378)、[SPARK ACL 2026](https://aclanthology.org/2026.acl-long.1100/)。本轮阅读深度：**A-targeted**，ToIA核对§I–III的acquisition定义，SPARK核对§2.2、§3.5与Appendix A/E。

### ToIA真正做的事

ToIA不是简单“task weight × uncertainty”。在MPPI现有的每条sampled rollout上，它枚举**早期可获得的prospective observation**，计算该观测对同一rollout后续model queries的GP posterior variance reduction，再用rollout的task-cost softmax权重乘上这项predictive value。这个acquisition term直接改变MPPI rollout weights；作者强调无需采样hypothetical observation或为每个posterior重新优化控制。

所以PBB若只写“task-relevant uncertainty acquisition”就与ToIA太近。PBB应保持一个不同的operational question：

> **我已经有一组真正互相竞争的CEM candidates；哪一个same-state counterfactual branch最可能改变它们的相对顺序/elite membership？**

ToIA的future target是同rollout后续queries；PBB的target是**candidate-set decision boundary**。最强对照应把ToIA式“task-relevant predictive information”实现成baseline，而不是把它当背景一句话带过。

### SPARK真正如何识别critical state

SPARK的branch criterion不是外部value/entropy计算器，而是policy reasoning trace中的intrinsic `<explore>` signal：模型自认存在epistemic uncertainty或semantic ambiguity时才branch，否则线性延续。固定总leaf budget下，论文直接比较dynamic vs fixed-probability branching；固定随机branching明显下降。Appendix的heuristic analysis也把收益归因于critical states稀疏时，共享routine prefix后把更多comparable action samples集中到少数critical points。

这会压缩PBB的泛化叙事：**“在少数critical states多采action alternatives更高效”不是新原则。** PBB必须靠visual latent MPC的candidate set、same-reset dynamics branches以及最终world-model training闭环建立自己的对象。

### 对PBB的设计后果

首轮至少需要三个“逐步变强”的selector：

1. **GLOBAL-U**：只看world-model predictive uncertainty；
2. **TASK-U / ToIA-like**：uncertainty × goal/task relevance；
3. **BOUNDARY-U / PBB**：只关心可能改变CEM elite membership/selected action的pairwise rank uncertainty。

如果3只是在数值上等于2，PBB没有独立方法空间；如果3选择的states/actions不同并带来更高planning gain per environment step，才有自己的叙事。


## S18｜What Must a World Model Distinguish：R3 的问题已经被说得很准，下一步不是换个名字

来源：[What Must a World Model Distinguish for Planning?](https://arxiv.org/abs/2609.33030)。本轮阅读深度：**A-targeted**，核对abstract与query/candidate/planner的核心论点；不声称逐定理复验。

**原文依据。** 论文把planning所需信息分成mechanism、response、decision sufficiency，并指出“世界模型该保留什么”取决于query、candidate set与planner。query-conditioned joint model在seen objectives上regret更低，但这种优势在unseen objectives上明显减弱；作者据此提出模块化方向：query决定“where to look”，action-conditioned model负责“what will happen”，让prediction可跨objective复用。

**我们的生长分析。** R3不能再以“query应该放哪”作为headline，因为这篇已经直接问了。更值得做的是一个可训练、低成本的**selective specialization**：保持一个query-agnostic predictive core，只在candidate proposal/scoring或少量latent channels上启用query adapter，并显式测seen-task gain、unseen-goal reuse与额外compute。若简单query-at-cost已经最好，那就是重要简化结论；若query-conditioned residual只在decision-critical candidates上有用，可与R2 candidate-stage compute自然相连。

## S19｜Feedback World Model / WorldAgen / CAWM：R5不缺“适配”，缺的是何时值得适配

来源：[Feedback World Model](https://arxiv.org/abs/2605.15705)、[WorldAgen](https://arxiv.org/abs/2609.08162)、[Changepoint-Aware World Models](https://arxiv.org/abs/2609.18950)。本轮阅读深度：**B+/positioning**。

- Feedback WM用执行后的prediction-observation mismatch维护轻量feedback state，不改模型参数。
- WorldAgen收集少量test-time真实transition做轻量TTT，联合world/action heads适应新环境。
- CAWM检测abrupt dynamics shift并flush stale replay，说明“继续按旧数据训练”本身会拖慢恢复。

这些工作已经覆盖“feedback有用”“test-time update有用”“检测shift再更新”的大故事。

**我们的生长分析。** R5更有价值的问题是：**一次干预到底值不值得做，以及应该选feedback、参数更新、replan还是hold？** 如果每次prediction error大都盲目更新，很可能浪费compute甚至伤性能。世界模型的可靠使用可以从“异常检测”转成“intervention utility”。

## S20｜Counterfactual Utility Protocol：update-vs-hold可以成为R5的训练信号，而不只是评测

来源：[Measuring the Value of World-Model Updates](https://arxiv.org/abs/2609.10954)。本轮阅读深度：**B+/positioning**。

**原文依据。** 论文用fork ledger在预注册时刻把deployment stream分成update与hold两个matched continuation，直接测 `ΔR = R_update - R_hold`；其结果甚至显示固定update机制在多个任务上平均降低return。它的重点是evaluation/measurement：不要用prediction surprise代替“这次更新实际有没有价值”。

**我们的生长分析。** 这给E18一个比“uncertainty阈值routing”更扎实的下一步：先用fork ledger生成少量**干预价值标签**，再学习一个只使用部署时可见信号的轻量router，预测hold / feedback / short update / full replan哪个更值钱。该router不是用未来reward在线作弊；未来分叉结果只用于离线训练标签。若简单规则已经够好，就保留简单规则，不强造神经router。

## S21｜Revaluation：successor-style长期表示的优势和代价都很经典

来源：[successor representation in human RL](https://www.nature.com/articles/s41562-017-0180-8)、Bagatella TD-JEPA、[Universal Horizon Models](https://proceedings.mlr.press/v306/chung26b.html)。本轮阅读深度：**B/background + modern positioning**。

经典SR能在reward改变时快速revalue，因为predictive occupancy可复用；但transition结构变化时需要更新occupancy本身。modern implicit/long-horizon predictive representations继承了这种“预计算换灵活性”的基本张力，只是对象从tabular occupancy变成latent/policy-conditioned预测。

**我们的生长分析。** E19不应“重新发现reward revaluation比transition revaluation容易”。更有价值的是在compact visual WM上比较**哪一层更新**最划算：只更新task/cost head、只更新短时dynamics、只更新long-horizon abstraction、或完整replay；并以recovery samples × wall-clock × retained old-task performance衡量。若R2的multi-fidelity/explicit-implicit方法成熟，E19还是很自然的stress test。
