# From Beliefs to Coherent Samples
## Predictive Sufficiency and Trajectory Specialization in Generative In-Context Learning

状态：新研究 workbench / 研究蓝图 v0（2026-10-27）。相关工作见 [RELATED_WORK.md](./RELATED_WORK.md)，给本地执行 Agent 的说明见 [AGENT_HANDOFF.md](./AGENT_HANDOFF.md)。

> **一句话**：预训练生成式 Transformer 如何根据有限示例推断不确定的潜在任务，在表示处理中保留单个及联合 Query 真正需要的信息，并经扩散过程生成既校准又全局一致的输出？
>
> **主线**：Inference（从示例形成 Task Belief） → Representation（任务相关信息的保留与删除） → Realization（沿扩散轨迹把不确定性实现为共享规则下的相互一致的样本）。
>
> 不是“再找一个 Bayesian Attention Head”，不是普通 Token Pruning/Score Distillation，也不是要求发明新信息论定律；重点是将经典统计工具用于这个此前缺乏系统解释的**预训练生成式 ICL 的完整计算问题**。

## 1. 为什么值得做？

Fu et al. [2610.05333](https://arxiv.org/abs/2610.05333) 将生成式 ICL 的目标明确为 **posterior predictive distribution**：少量 Demonstrations 只确定了一组可能任务及其权重，而非唯一输出；DiT 可学习并生成这个分布。Hakaze Cho 团队（ICLR 2025 / NeurIPS 2025 / ICLR 2026）则揭示语言模型 ICL 的 Evidence Processing、Task Subspace、Task Vectors、Information Removal 和 Attention Head 的功能与几何现象。

我们要衔接两者之间尚未打通的链条：**从概率性的任务知识，到模型内部的表示选择，再到扩散生成出的完整结构**。

一个关键动机是：**每个 Query 的边缘分布正确，不保证同一个 Episode 的多个 Query 遵守相同的任务规则**。这在图像多个位置/对象、共同风格的多张图、动作序列、多点函数预测中具有直观意义，也有严格可计算的统计差别。Neural Processes / Neural Diffusion Processes 已研究共享潜在变量和联合函数分布，因此我们不是宣称“联合预测从未有人做过”，而是系统研究它在 **pretrained DiT 的 ICL、内部机制、扩散动力学和失效/改进**中的角色。

期望形成四类互相支撑的贡献：**(a) 统计任务与诊断；(b) 联合扩散与轨迹动力学；(c) Cho 式机制因果解释；(d) 围绕联合一致性的问题驱动方法。** 四者组成一个论文叙事，不要拆成互不相关的小技巧。

## 2. 统一统计设置：共享潜在任务的联合生成

Episode 先抽潜在任务，随后获取 n 个 Demonstrations，同一任务下需生成 Q 个目标：

$$
\Theta\sim\pi,\quad D_n=\{(x_i,y_i)\}_{i=1}^n,\quad
\mathbf X=(x_{*1},\ldots,x_{*Q}),\quad \mathbf Y=(Y_{*1},\ldots,Y_{*Q}).
$$

在给定 \Theta、各 Query 的条件下，基础实验假设观测噪声独立；真实应用可以放宽这个假设。由上下文更新：

$$
w_j(D_n)=P(\Theta=j\mid D_n),\qquad
P^*(\mathbf y\mid D_n,\mathbf X)
=\sum_{j=1}^K w_j(D_n)\prod_{q=1}^Q P_j(y_q\mid x_{*q}).
$$

错误但很常见的策略，是 **independently sampling correct marginals**：

$$
P^{\rm ind}(\mathbf y\mid D_n,\mathbf X)
=\prod_{q=1}^Q \sum_j w_j(D_n)P_j(y_q\mid x_{*q}).
$$

两者对每个 Query 的边缘预测可以完全相同，但第二个式子允许不同 Query 隐式采用不同任务。若 K 个模式可完全辨别且后验为 w，独立模式选择导致同一 Episode 规则不一致的概率为：

$$
P_{\rm inconsistent}=1-\sum_{j=1}^K w_j^Q.
$$

例如 K=2，w=(1/2,1/2)，Q=2 时 50%，Q=4 时 87.5%。这不是预测实际 DiT 一定失败，而是表明**正确边缘生成与正确联合生成属于不同能力**。联合生成模型、共享随机潜变量基线有能力解决它；我们的研究要检验预训练 DiT 如何学、如何表示、如何生成以及为何失准。

图像中的多个 Patch / 多个物体可用于研究全局协同，但**图像 Patch 不自动严格等价于独立 Query**，要区别空间相关观测噪声、任务全局性以及不同对象的条件结构。

### 2.1 联合预测信念秩与 Predictive Sufficiency

将后验权重映射为联合预测分布：

$$
\mathcal A_{\mathbf X}^{(Q)}(w)=\sum_j w_j \bigotimes_{q=1}^Q P_j(\cdot\mid x_{*q}),\qquad
r_{\mathbf X}^{(Q)}=\operatorname{rank}\left(\mathcal A_{\mathbf X}^{(Q)}|_{\mathbf1^\perp}\right).
$$

研究问题：哪些任务之间的区分，对给定一个 Query 不必要，却对多个 Query 的共同生成成为必要信息？

一个非常干净的解析例子：取两种不同的单 Query 分布 P1/P2，并令第三种任务在单 Query 上满足 P3=(P1+P2)/2。单 Query 的预测族仿射维度为 1；如果给定任务后两个 Query 独立，则联合任务族 P1⊗P1、P2⊗P2、P3⊗P3 一般有仿射维度 2。因此 **r^(1)=1，r^(2)=2**。同一个表示在单 Query 上可能充分、在联合 Query 上不充分。这个例子应当从概率空间角度证明并给出可复现实验；不要把 rank 自动等同于某层 Hidden State 的欧氏维度，也不要无条件声称任意低维非线性编码一定失败。

对明确只通过 H=T(D_n,\mathbf X) 接收上下文的生成器 q_H，可用经典 KL 恒等式区分“压缩损失”与“剩余生成误差”：

$$
\mathbb E\,\mathrm{KL}(P^*_{\!D}\|q_H)
=
I(\mathbf Y;D_n\mid H,\mathbf X)
+
\mathbb E\,\mathrm{KL}(P^*_{\!H}\|q_H).
$$

它给 Representation 一个**任务依赖的预测充分性标准**，也说明内部丢失信息和下游实现不佳是两个不同问题。它只对真实的信息瓶颈成立；实际 DiT 里随噪声 z_t 变化的 Query Hidden States 不可直接逐层套此等式。

## 3. 联合扩散：从 Task Belief 到 Coherent Sample

对整个联合向量加噪，而不是独立 Batch 采样：

$$
Z_t=a_t\mathbf Y+s_t\varepsilon,\quad \varepsilon\sim N(0,I),\quad
m^*(z,t,D,\mathbf X)=\mathbb E[\mathbf Y\mid Z_t=z,D,\mathbf X].
$$

用 x0-prediction 时，理想 Denoiser 的 Jacobian 与条件协方差有精确关系（a_t,s_t>0）：

$$
J_t(z)=\nabla_zm^*(z,t)=\frac{a_t}{s_t^2}\operatorname{Cov}(\mathbf Y\mid Z_t=z,D,\mathbf X).
$$

对于固定潜在任务且给定任务后 Query 独立、同方差的高斯任务族，跨 Query Jacobian Block 有解析结构。若 P_j(\mathbf Y)=N(\mu_j,\tau^2 I)，记 v_t=a_t^2\tau^2+s_t^2、\rho_j=P(\Theta=j\mid Z_t=z,D,\mathbf X)，则 a≠b 时：

$$
J_{ab}(z,t)=\frac{a_ts_t^2}{v_t^2}\operatorname{Cov}_{j\sim\rho(z,t)}(\mu_{j,a},\mu_{j,b}).
$$

这给出了对共享任务引起的跨 Query 耦合的**功能级测量**，无需先猜具体 Heads。对一般结构化图像，任务内也可能存在空间耦合，不能把所有非对角项唯一归因于跨任务不确定性；通过“任务内噪声独立”受控实验检验后，再探索真实场景。

### 3.1 轨迹专业化与两种统计量

上下文 Task Belief 为 w_j(D)，给定带噪采样状态的 Responsibility 为 \rho_j(z,t,D)。理想模型满足：

$$
\mathbb E_{Z_t\mid D}[\rho_j(Z_t,t,D)]=w_j(D).
$$

轨迹对任务的信息量：

$$
S(t;D)=I(\Theta;Z_t\mid D)
=H(w(D))-\mathbb E_{Z_t\mid D}H(\rho(Z_t,t,D)).
$$

在可比较的高斯通道 Z_\gamma=\sqrt\gamma\,\mathbf Y+\varepsilon 中，I-MMSE 和全协方差分解给出：

$$
\frac{dS}{d\gamma}
=\frac12\mathbb E_{Z_\gamma}\operatorname{Tr}
\operatorname{Cov}_{j\sim\rho} (m_j^*(Z_\gamma)).
$$

这些是**理论参照与诊断工具**，不是预言模型必须出现陡峭 Speciation、分立 Head 或某个固定时间点。对理想随机 Markov 逆过程，可讨论 \rho 的条件期望/鞅结构；**确定性 DDIM 不是同样的随机过程**，不可不加说明地套路径鞅结论。

### 3.2 二阶方差—Jacobian 一致性（Gemini 最后一轮的重要补充）

全协方差分解 + 上述 Tweedie/Jacobian 关系产生：

$$
\boxed{
\operatorname{Cov}(\mathbf Y\mid D,\mathbf X)
=
\operatorname{Cov}_{Z_t\mid D,\mathbf X}(m^*(Z_t,t))
+\frac{s_t^2}{a_t}\mathbb E_{Z_t\mid D,\mathbf X}[J_t(Z_t)]
}
$$

它是严格成立的**理想模型恒等式**（a_t>0，有限二阶矩，恰当端点极限）。直观上，噪声减少时“尚未从局部推断中显露的协方差”逐渐转成不同轨迹的已实现差异。归一化 Trace 可以在理想高斯通道下作为专业化进度指标。

重要：对训练出的失准网络，它不是自动成立的守恒定律。若模型的初始与最终表示都错误地对称坍缩，模型内部自洽也未必暴露问题。应当将它用于**Oracle 对照、时间剖面、近似一致性诊断与候选校准**，不能用它单独声称恢复真实后验。

### 3.3 误差从“上下文编码”到“采样路径”

论文级叙事保留双层：预测充分性损失 + 压缩后条件生成误差。对有随机逆 Markov Kernel 的理想/学习采样器，还可用路径 KL 链式法则上界最终生成误差、定位时间区段。不要将其宣称为任意 DDIM、所有 DiT 中间层都严格适用的单一等式。

## 4. 核心科学问题 / 主要假设

**RQ1 — Bayesian joint prediction.** 预训练生成式 Transformer 在有限示例下，到底学会了单 Query 的 posterior predictive，还是共享潜在任务的 joint posterior predictive？边缘准确而联合失准在何时出现，怎么随 n、Q、先验歧义、信噪比变化？

**RQ2 — Predictive representation.** 隐藏表示保留哪些 task belief 信息？是否存在“单 Query 可压缩而联合 Query 不可压缩”的表示信息差别？Cho 式 Information Removal / Task Subspace Dynamics 对联合充分性有什么功能与因果影响？

**RQ3 — Coherent realization.** Cross-Query / Cross-Patch 的 Denoiser Jacobian 与理想协方差结构匹配多少？Diffusion Time 如何使全局任务歧义转化为具体一致的模式？Context Evidence 与 Query-Query Interaction 分别有什么因果作用？

**RQ4 — Mechanism → improvement.** 能否基于已解释的失准机制设计高效、稳定的联合生成或 Coherence-Preserving Compression / Calibration，在边缘校准、联合一致性、质量和成本之间取得更优权衡？

这些是研究问题，不是已经证实的答案。发现分布式机制、平滑变化或替代电路同样重要；不能预先写“必然从 Log-odds 旋转到 Simplex”“必有某个 Bayesian Head / 相变点”。

## 5. 实验主线：先解析、后模型、再机制、最后高维

### E0｜解析 Bayes Oracle 与能力下界（不训练网络也有科学内容）
- **任务族 A（同均值异分布）**：二维线性高斯，\tilde\theta∈{(-1,1),(0,0),(+1,1)}，y=\tilde\theta^\top x+\epsilon。Context 近似 x=(0,1), y≈1 时得到两端双峰；y≈0 时得到中心单峰。Query 可取 x=(1,0)，让两种 Context 在均值一致时具有明显不同的分布。
- **连续收缩**：让上下文 x^{(1)} 有小而非零的变化，随 n∈{1,2,4,8,16,32} 累积区分 ±1 的证据。将“严格 x=(0,1) 的歧义诊断集”与“可辨识性随 n 变化的自然训练/测试集”分开；避免把刻意设计的测例当成训练分布外推能力。
- **任务族 B（联合秩变化）**：单 Query P3=(P1+P2)/2，但给定任务后多 Query 独立；测试 r^(1)<r^(2)、边缘预测相同而联合预测不同。
- **任务族 C（空间方向）**：二维输出的四方向或共享位移规则，多 Query 与多坐标耦合；用于检验跨 Query Block / 空间协同。

输出：Oracle posterior、Oracle joint samples、无模型的 Independent Marginal Baseline、解析协方差/Jacobian、rank 演示和不一致率曲线。这是建立问题本身而非赌网络行为。

### E1｜小型联合 DiT 学习
- **输入单位是同一 Episode 的整组 Query Token**：Context Token 表示 Demonstrations；Q 个 (x_q,z_{q,t}) 组成 **同一次 forward 的 Query Sequence**。Query Self-Attention 可建立跨 Query 通信，Context Cross-Attention 提供示例信息；x0-prediction 可直接对照 Oracle Denoiser。
- 训练和评测同时含 Q=1 与 Q>1、不同 Context 长度、Query 顺序置换；防止模型记住固定顺序/固定 Q。
- **不可省的基线**：(i) 单 Query Independent Diffusion（故意暴露边缘/联合落差）；(ii) 显式共享 latent/task sampling 或解析混合 Oracle；(iii) 参数量和训练数据相当的非 Transformer 联合 Denoiser；(iv) Neural Processes / Neural Diffusion Processes 能力与代价对照。
- 不预设某架构必须失败；可通过共享全局 latent 等替代构造联合分布，并非只有 Query Self-Attention 一条道路。

### E2｜功能诊断与 Mechanistic ICL
- 指标：single-query mode weights、分布距离（TV 可解析时、W1/MMD/适当 NLL）、joint mode consistency、held-out Q 泛化、样本质量、cross-query covariance、Oracle vs learned Jacobian/JVP、时间积分偏差、训练/采样成本。
- 配对测试：同均值异分布；同边缘异联合；同任务后验异 Context 表面；后验熵非单调更新；共享任务 vs per-query independent task 的数据生成机制。
- Cho 方法：Layer-wise Representation Geometry、Task-Subspace Probing、Head / MLP / Attention Output Ablation、Activation Patching、Counterfactual Context Swap。**探针仅说明可恢复，不能代替因果干预。**
- 具体区分：Context Token 的 Attention Weight 不是任务后验权重；同质示例、单例 Context 时也可能通过 Query Self-Attention / MLP / Shared Latent 计算；不要预设某一模块唯一负责某一步。
- 对 Fu 原文模型，注意它在 n=1 时依然具有 4 个 Context Patch Tokens；其理论 4-block 电路不等于 80M 实际架构的实测机制。

### E3｜结构化图像与方法验证
- 以 Fu et al. Appendix J 的合成图像任务为参照，扩展到**同一未知规则作用于多个对象 / 多个 Query**。可选择独立 Query 序列，也可做一张多物体画布；显式规定何者共享任务。
- 比较单图像质量与跨物体/跨 Query 一致性；加入模式概率校准、联合结构、训练预算与推理吞吐。
- 从功能诊断长出方法：① Coherence-/JVP-Preserving Context Token Selection/Merging；② Joint-/Moment-aware self-consistency calibration；③ 如果实测显示共享任务耦合弱，可研究显式 Shared-Latent / Query Coordination 模块。并非必须三个都做；根据 E1/E2 选择最有因果依据、实验收益最清楚的一个主方法。
- **算法不能只把已知 Score Distillation 换名**，也不能预设“保 JVP 必然 50–75% 剪枝零损失”“早期 Jacobian 一定无偏”“一次守恒残差即可修正后验”。应验证成本—收益并与强基线对比。

## 6. 如何评价研究成果（避免局部优化与赌博）

一条有说服力的研究成果应该是完整的：
1. **科学对象清楚**：正确边缘 ≠ 正确联合；共享任务导致可测量的协同预测要求。
2. **非平凡理论/诊断**：rank 增长、预测充分性、Jacobian、时间一致性在联合生成中的系统联系与可验证推论。
3. **实际网络结果**：多个训练种子、不同任务难度/先验、Q/n/noise，含最强合理基线；机制证据区分 Probe 与因果。
4. **方法价值（争取）**：设计得到改善校准/一致性/效率的真实方法，或获得可推广的架构与训练原则。

可能的结果包括：联合 DiT 能很好学习，独立模型失败；或 DiT 本身在若干工况失败；或信息并不由某组 Heads 专门承载而是分布式实现。**任何一种都可以推动核心科学问题**，但不能承诺每种结果自动是一篇强论文。研究应以正面命题为核心持续推进，不因局部已有工作或一个边界反例而切碎整个方向。

## 7. 必要的数学与架构口径（避免重复踩坑）

- 三任务 y=θx+ε、θ∈{-1,0,+1} 的普通同先验高斯线性回归，无法凭对称观测产生“只支持 ±1、不支持 0”的后验；采用二维任务点 \tilde\theta=(θ,θ²) 与连续输入的模型。
- 纯任务向量构成弯曲曲线、信念落入凸包是一种很好的**候选编码**，不是任意 Transformer 的隐藏层必需。半径/纯度在正规单纯形上与 Rényi-2 相关，不可无条件当成 Shannon 熵。
- 已知统计恒等式可以贡献新研究框架；不要重复吹成首创新定律。相反，别因其经典而否定新对象上的机制意义。
- KL 压缩分解需要真正的信息瓶颈；Cross-Attention Hidden States 可依赖 noisy Query，不能草率当 H(D)。
- 非对角 Jacobian 在给定任务独立噪声的模型里有清楚的跨任务解释；一般图像中任务内部依赖也会贡献非对角项。
- 方差—Jacobian 公式的 a_t→0 极限需谨慎估计；理想一致性不是模型正确性的充分条件。单靠样本均值、单靠二阶矩、单靠同一模型自身闭环，都可能漏检错误，需要独立 Bayes Oracle 与完整联合分布评估。
- \rho 的鞅解释依赖匹配的随机逆 Markov 过程；DDIM 确定性轨迹不要直接套。
- 把 Q 个样本独立堆在 Batch 中不会自动产生跨 Query Jacobian；但显式共享 latent、组合采样也可构建联合分布。Self-Attention 是一种候选架构，不是唯一机制。
- RKHS / MMD 的投影可用于分布级诊断；对任务混合权重的唯一恢复需要相应可辨识条件；熵差/方向偏置不是自动正交的三项误差分解。
- “同一任务”不是普遍要求所有独立生成样本一致；**只对明确属于同一 Episode、共享同一潜在规则的 Query 集合**要求联合一致。分别启动不同 Episode 的图像生成可以合法独立抽任务。

## 8. 当前项目边界与下一步

**先做**：E0 解析模型 + E1 轻量联合 DiT + 完整基线、联合指标；再决定 E2 机制深挖与 E3 方法优先级。具体模型大小、超参数、代码、统计检验、图表与深入实验设计交由本地 Agent 执行并在读完 Handoff 后独立完善。

**不要做**：因“已有类似论文”“不是新定理”而缩成 Score Distillation；不做只画 Attention Maps 的机制新闻；也不在尚未测量前预设一个特定 MLP / Head 的 Bayesian Circuit 或必然的相变点。

**第一批应有的证据**：可复现实验的真实 joint-vs-marginal gap、Oracle Jacobian/covariance 关系、n/Q 变化规律、小型模型相对多个基线的学习曲线。这些都与核心论文主线直接相关。

> 资料索引和明确链接请见 [RELATED_WORK.md](./RELATED_WORK.md)；每轮工作规范和执行起点请见 [AGENT_HANDOFF.md](./AGENT_HANDOFF.md)。
