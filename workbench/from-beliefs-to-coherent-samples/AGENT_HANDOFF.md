# Local Research Agent Handoff｜每轮必读

项目：**From Beliefs to Coherent Samples: Predictive Sufficiency and Trajectory Specialization in Generative In-Context Learning**  
状态：2026-10-27，研究蓝图已确定，进入解析模型 / 小规模联合生成实验阶段；**尚未声称代码或实验已完成**。

配套文件（同目录）：
- [RESEARCH_PLAN.md](./RESEARCH_PLAN.md)：当前唯一主线与研究方案，优先级最高；
- [RELATED_WORK.md](./RELATED_WORK.md)：关键论文、准确链接与相邻研究定位；
- 本文件：执行原则、项目边界、工作交接，**每一轮开始必须重新读取**。

## 1. 先理解这篇工作到底要研究什么

**核心问题**：预训练生成式 Transformer 怎样从少量 Demonstrations 中推断不确定任务，保留对未来 Query（尤其是同一 Episode 的多 Query）重要的信息，并通过扩散生成既概率校准、又共享同一个潜在任务规则的结构化样本？

完整故事线：**Inference → Representation → Realization**。

最重要的正面现象不是“有一个 Bayesian Head”，而是：**单 Query posterior-predictive 准确，不等于多个 Query 的 joint posterior-predictive 准确**。给定共享任务的情况下，独立边缘生成会在每个 Query 单独正确时仍产生跨 Query 矛盾。我们要研究这个能力差异的统计结构、Transformer 的实际学习与内部计算、扩散的条件协同机制及可据此改进的模型设计。

两大根基：
1. Fu et al. (arXiv:2610.05333)：DiT / Bayesian posterior-predictive in-context generation；
2. Hakaze Cho 系列：ICL inference circuit、task subspace、TR/TL、task vectors、information removal。

同等重要的直接前史/基线：Neural Processes、Neural Diffusion Processes、Transformer 学习 Posterior Predictive、Belief-State Geometry、Diffusion 信息与 Speciation、ToPi / Context Compression。**相关工作是一张研究地图，不是“提前否决课题”的清单。**

## 2. 不可违背的科研判断原则

### 2.1 保持全局观，避免“防御性瘫痪”
- **允许并鼓励大胆、具体、可检验的科学假设。** 经典 I-MMSE / Tweedie / KL 分解应用于新的、重要的生成式 ICL 对象，完全可能构成有原创性的研究；不必为了“新颖”强行发明新定律。
- 看到邻近论文已解决一个局部问题，不要立刻得出“总体路线不够新 / 不能做”。先精确区分它的随机对象、假设、训练设定、单/联合预测、理论与真实模型实验；正面回答本项目 **Inference → Representation → Joint Realization** 还有什么新的系统问题。
- 不要每讨论一个正面主张，就罗列 3 篇 2025–2026 工作并草率判“文献距离不够”。应该用相关研究巩固定位、选基线、创造更有洞察力的实验。
- 不要无限追求局部严谨而把研究主线不断降格成普通 Score Distillation、Token Pruning、可解码 Probe 或一张 Attention Heatmap。
- 不要执着于制造“大新闻”或一定要有一个全新的信息论定理。高质量工作可以来自**首次系统解决一个真正重要的新对象**，并形成理论、机制、实验与方法之间的扎实解释链。

### 2.2 不赌单一偶然机制，但也不要保守
- 不把论文生死押在“某 Head 刚好编码 w”“隐藏向量必须是凸包”“网络必然出现尖锐相变”“某时间段 Steering 一定有效”上。上述都是**待检验假说**，不要写成研究前提。
- “不赌博”指核心科学问题和解析基准先成立，不能理解为只做教科书恒等式。大胆设计具有判别力的实验，并允许内部机制是分布式、非线性的。
- 正面结果和反面结果都应分析其机制与意义；不要预先宣称任何结果都足够发论文。主动寻找能够**解释/预测失效、指导算法**的机制。
- 对自己/其他模型的建议：**既不无条件接受，也不为了显示严谨而逢议必驳**。数学错误迅速修正，非核心边界条件一笔交代、继续推进主要命题。

### 2.3 研究问题先于工具
- 任何 Probe、PCA、Attention Plot、JVP、Steering、Token Pruning、KL 分解，必须说明它具体回答 RQ1–RQ4 的哪一个问题、与哪个 Bayes Oracle 或因果对照比较。
- **Probe 可恢复 ≠ 网络因果使用；样本均值正确 ≠ 多模态/联合分布正确；模型自洽 ≠ 模型校准。**
- “阶段 1/2/3”是项目执行顺序，不应机械地对应“几层 Transformer 干啥”。每一步都要能回到联合生成这个主要统计对象。

## 3. 本轮开始后的具体任务（请你独立设计代码与深入实验）

### A. 先做完整但轻量的解析环境（E0）
1. 实现 shared-task episodic data generator：任务先验 $\pi$、$n$ 个 Context、$Q$ 个 Query；统一支持 $Q=1$ 和 $Q>1$。
2. **任务族 A**：二维线性高斯任务点 $\tilde\theta\in\{(-1,1),(0,0),(+1,1)\}$，$y=\tilde\theta^\top x+\epsilon$。写出精确 posterior $w(D)$、joint predictive Gaussian mixture 与在扩散噪声下的 Oracle Denoiser/Score/Jacobian。
3. **任务族 B**：同一目标 Query 上满足 $P_3=(P_1+P_2)/2$，但多个 Query 在给定任务后独立，研究 $r^{(1)}=1<r^{(2)}=2$。与任务族 A 的“同均值异分布”和弱证据随 $n$ 增长相互补充；**B 不可直接复用 A 的三任务单高斯 Oracle**。见下方自然生成构造。
4. 记录同均值异分布、同边缘异联合、共享任务 vs 独立任务生成的不一致率，以及 Oracle 的跨 Query 协方差/JVP；使用有限差分与 Autograd 互相验证解析导数。

**任务族 A 的单高斯 Oracle（仅适用 A）**：
$$
w_j(D)\propto\pi_j\exp\{-\tfrac1{2\sigma^2}\sum_i(y_i-\tilde\theta_j^\top x_i)^2\}.
$$
$$
\mu_j(\mathbf X)=[\tilde\theta_j^\top x_{*1},\ldots,\tilde\theta_j^\top x_{*Q}],\quad
P^*(\mathbf Y\mid D,\mathbf X)=\sum_jw_j\,N(\mu_j,\sigma^2 I_Q).
$$
扩散下令 v_t=a_t^2\sigma^2+s_t^2，则：
$$
\rho_j(z,t)\propto w_j N(z;a_t\mu_j,v_tI_Q),\quad
m_j^*(z,t)=\frac{a_t\sigma^2}{v_t}z+\frac{s_t^2}{v_t}\mu_j,\quad
m^*=\sum_j\rho_jm_j^*.
$$
核对极限与端点，保证计算数值稳定。

**任务族 B：可由自然 Context 产生两个后验、同一 Query 边缘相同而联合不同**

以 $\Theta\in\{1,2,3\}$、等先验，输入类型 $x\in\{u,v\}$ 作为一个**单独的、完整定义的任务族**：

| 输入类型 | 任务 1 | 任务 2 | 任务 3 |
|---|---|---|---|
| $u$（用于任务筛选） | $\mathcal N(1,\sigma^2)$ | $\mathcal N(1,\sigma^2)$ | $\mathcal N(0,\sigma^2)$ |
| $v$（用于混合比较） | $P_- = \mathcal N(-1,\sigma^2)$ | $P_+ = \mathcal N(+1,\sigma^2)$ | $P_3=(P_-+P_+)/2$ |

- **Context A**：重复提供 $u$、观测值接近 1，得到 $w_A\approx(1/2,1/2,0)$；**Context B**：重复提供 $v$，观测出现明显正负混合，得到 $w_B\approx(0,0,1)$。这两个 Context 都应来自训练任务分布与采集机制，不要只在测试时人工制造。
- **Query 均为 $v$**：A/B 的单 Query 预测边缘几乎相同（都是 $(P_-+P_+)/2$），但两个 Query 的联合分布分别近似 $(P_-\otimes P_-+P_+\otimes P_+)/2$ 与 $P_3\otimes P_3$。
- **重要可行性提醒**：若在所有输入上都规定 $P_3=(P_1+P_2)/2$，则等先验下 $L_3(D)=\prod_i(L_{1,i}+L_{2,i})/2\geq\sqrt{L_1(D)L_2(D)}$；当任务 1/2 的后验对称时，无法仅靠“不分正负”的 Context 排除任务 3。$u/v$ 设计故意令混合等式**仅在目标 Query $v$ 上成立**，绝不可默默将其等同于任务族 A。
- 通用 Oracle：$w_j(D)\propto\pi_j\prod_i p_j(y_i\mid x_i)$；对各 Query 定义 $q_{j,t}(z_q\mid x_q)=\int \mathcal N(z_q;a_ty,s_t^2)\,P_j(dy\mid x_q)$，$\rho_j(z,t)\propto w_j(D)\prod_q q_{j,t}(z_q\mid x_q)$，并计算单任务最优均值 $m_{j,q}^*(z_q,t)=\mathbb E[Y_q\mid Z_{q,t}=z_q,\Theta=j,D]$。总均值为 $m_q^*=\sum_j\rho_j m_{j,q}^*$；当 $a\neq b$，
$
J_{ab}(z,t)=\frac{a_t}{s_t^2}
\operatorname{Cov}_{j\sim\rho(z,t)}
\!\bigl(m_{j,a}^*(z_a,t),m_{j,b}^*(z_b,t)\bigr).
$
- 任务 3 的单任务 Denoiser **是两高斯分量的后验均值混合（随 $z_q$ 非线性变化）**。以 $Q=2,z=(0,0)$ 为诊断点：在 $w_A$ 下 $J_{12}>0$（共享左右模式）；在 $w_B$ 下 $J_{12}=0$（给定任务 3 后两个 Query 的模式独立）。同时检查有限样本下的近似值、Autograd 与解析一致；避免误把**任务 3 允许独立变号**标成“生成不一致”。

**E0 通过条件**：两种任务族的精确 posterior 均归一化；$Q=1$ 时联合模型退化为边缘模型；Oracle 联合采样与边缘化一致；任务族 B 能通过自然 Context 得到两组目标后验；$J_{12}$ 在两组黄金对照下的表现与公式一致（含 Autograd / 有限差分）；同边缘异联合的差别确实可观测。以上均是实现测试，不是模型发现。这些是基础实现测试，不是模型发现。

### B. 随后设计并训练最小联合 Denoiser / DiT（E1）
- 以 **同一 Episode 的整个 Query Sequence** 为模型输入，不要把 Q 个 Query 当成互不通信的独立 Batch 后却声称学到了联合机制。
- 候选骨架：Context Pair Encoder + Query Token Embedding + Query Self-Attention + Context Cross-Attention + Time Conditioning + x0-prediction Head；具体层数、宽度、噪声 Schedule、训练配方由你基于资源自主确定，并解释决定。
- Query 集合顺序变化、Q 变化、n 变化应在训练与验证中覆盖；注意 mask、样本置换、同 Episode 的真实任务共享、不泄漏 \Theta 标签到模型。
- **必须有强基线**：Independent Marginal DiT、Explicit Shared Latent / Task Sampler、联合非 Transformer 模型、适用的 NP/NDP（至少实现/复现核心合理对照）。配置参数量、训练 Episode 数量、采样预算尽可能可比。
- 每个结论须同时看：边缘校准、联合一致性、Oracle 分布距离、跨 Query Cov/Jacobian、单样本质量以及运行成本。多 Seed 汇总，报告方差和失败案例。别只测某一个漂亮合成例子。

### C. 基于 E1 的实际结果决定机制实验（E2）
- 先证明功能差异，再做 Cho 风格 layer/head/MLP、Attention Output、Subspace、Ablation、Activation Patching。
- 对同后验异 Context 表面、同均值异分布、同边缘异联合等配对，不要只比较任务 label probe。
- 重点测跨 Query JVP / off-diagonal Jacobian 与因果干预，而非假定“Context Cross-Attn = 贝叶斯，Query Self-Attn = 责任路由”。
- Fu 图像级 DiT 并非“n=1 就只有一个 Context Token”：其实际 Pair Encoder 产生 4 个 Token；不要把概念类比当成架构事实。
- 记录什么信息被保留、是否真正用于生成、怎样随 n/Q/t 变化；如遇分布式机制，不强行给 Head 起先验功能名称。

### D. 从机制与功能证据发展一个重点方法（E3）
优先候选（并非全部必须做）：
1. **Coherence-Preserving Context Compression**：在 Token Selection/Merging 中保留跨 Query JVP 与生成分布，不仅保单点 x0 预测；对比 ToPi、Attention、PCA/随机压缩和等预算方法。
2. **Joint / Variance-Jacobian Consistency**：使用分布的边缘化一致性、跨 Query 协方差和时间相关的理想关系诊断/约束；不能把一阶或二阶自洽本身当作正确性的充分条件。
3. **Shared-Belief Coordination**：若无显式共享信息的模型有瓶颈，可尝试共享 latent / query coordination，和 NP/NDP 公平比较。

真正选择什么方法，要由实际 E0–E2 的结果与核心研究问题决定。不要为了凑“两项算法贡献”而写两个弱技巧。

## 4. 实验质量、报告与代码纪律

- **先检查仓库、硬件、依赖与现有可复用实现**，不盲目覆盖代码或启动大规模训练。仅在合适位置创建实验目录；本 workbench 初始只保留这三个 .md 文档。
- 重要计算要有单元测试：posterior sum=1；$Q=1$ 时 joint=marginal；联合边缘化；任务族 B 的上下文可实现性及跨 Query Jacobian；任务内独立时协方差理论；Jacobian finite difference / Autograd；variance-Jacobian 在理想 Oracle 下的数值近似。
- 分清数据生成器中隐变量 \Theta 与训练时模型可见量；模型不可窥见解析 posterior 或 Task ID，除非该 run 被清楚标为 Oracle / Ablation。
- 报告 n、Q、先验熵、测例是否 OOD、噪声规模、扩散时间、Sampler 类型、训练 Episode 数、Seeds、置信区间/波动、计算开销。相同 Q 的模型需公平预算比较。
- 可用概率难分开的任务分量来考察强度，但不要只用可分模式分类指标；结合 joint KL / NLL（可计算时）、W1/MMD、Covariance、模式频率、任务规则违反率。
- 可做可视化，但**图好看不是结论**。优先给正面/负面假设表、具体数值、Oracle vs learned 差距以及因果检查。
- 复现或引用论文时保留直接链接、版本和关键条件；不要把理论网络和实训网络混淆，也不要把真实实验结论从 Q=1 擅自外推到 Q>1。
- 生成工作要进入仓库并附有可复现的配置/命令/数据说明；不要只给聊天概述。谨慎修改现有仓库文件，避免影响其他 workbench。

## 5. 每轮给研究者的简短进度回报格式

每一轮完成工作后，用以下结构汇报；不需要把所有思想史重写一次：

1. **核心问题/本轮假设**：与 RQ1–RQ4 哪一条直接关联，为什么重要？
2. **已完成的事实**：新增或修改哪些文件、实现哪些验证、真实运行了哪些实验；提供路径与 Commit。
3. **证据**：主要数值/图及基线对照，标明已证实、尚未证实、猜想。
4. **最重要的解释**：这如何帮助理解 Inference → Representation → Realization？考虑至少一种合理替代解释。
5. **下一步最有价值的行动**：必要的对照、失败后怎样转向、算力需求；不要反复把问题变小或无止境挑刺。

若修正了基础数学、数据假设或核心结论，**只更新 RESEARCH_PLAN.md 对应位置及本 Handoff 必要边界**。Related Work 添加实质重要研究即可；不要把每次聊天、每轮争论或所有防御性反例累积成厚重编年史。

## 6. 每轮启动时的核对

- [ ] 已重新阅读本 AGENT_HANDOFF.md；重大方向和新实验前重读 RESEARCH_PLAN.md、相关文献优先级。
- [ ] 当前工作是否继续服务完整的 **Inference → Representation → Realization / joint coherent generation**？
- [ ] 有否将“经典理论”“邻近工作”误用为停止正面探索的理由？
- [ ] 有否把某个未经实测的 Head、流形、Speciation、校准增益当作成立前提？
- [ ] 对照是否包含 **正确边缘但错误联合** 的基线，以及明确**共享任务**的强基线？
- [ ] 模型/采样器/信息瓶颈条件是否匹配所用公式？
- [ ] 有没有提交可复现产物、记录真正的新发现与下一步？

**执行指令**：从 E0 的数学 Oracle、数值测试与 E1 的最小联合 DiT 设计开始。具体代码、数据集封装、参数配置、评估统计与深入实验设计由本地 Agent 独立完成并主动推进；但任何工程决策都必须能回答本文件第一节的核心科学问题。保持大胆、严谨、建设性和全局观。
