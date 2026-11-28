# 路径依赖 / 早期成功 / 可采样性 vs 可学习性：先验文献笔记（全文已读）

候选问题：RLVR 中同样成功的推理经验是否导致后续学习与泛化系统性不同（路径依赖）？平台期是“不再采到有用经验（access）”还是“无法再从经验中学习（plasticity）”？
读法：6 篇指定论文 + 3 篇最近邻全文（pdftotext，含附录）；其余仅看到搜索摘要，标「未核对」。全文位于 scratchpad lit_a/。

## A. 六篇指定论文

### A1 Cui 2505.22617（Entropy Mechanism）
1. 内容：11 个基座（Qwen2.5 0.5–32B、Mistral、LLaMA、DeepSeek-Math）、数学+代码、GRPO/REINFORCE++/PRIME，veRL，lr 5e-7，batch 256、512 prompts×8（§2.2）。熵在前几步骤急降，76% 性能增益出现在前 200 步（1/12 训练），前 1/3 步数占 93% 增益与 94% 熵消耗（§2.3，Fig.2）；拟合 R=−a·exp(H)+b（Eq.6，Fig.3/4），仅用前 36 步即可预测后续（Fig.5，RMSE 0.9%/1.2%）。§3 推导熵变化=logp 与 logit 变化的协方差；§4 Clip-Cov/KL-Cov 在 Qwen2.5-7B/32B 上 DAPO-MATH 平均 +2.0%/+6.4%（§4.3，Table 2）。
2. 回答了什么：“早期熵塌缩限制后期上限”是**同一训练曲线上的相关/拟合**（H 与 R 的函数关系），不是对不同早期历史做干预再比后续；§2.6 明说上限由熵机制而非 RL 本身造成。对“平台期=access（探索）”提供了一端的证据（熵耗尽→探索不足），并有干预（Clip-Cov）佐证熵保持后性能更高。**没有**检验“经验还在、但学不动”（plasticity），也没有相同经验跨阶段注入。
3. 自训：是。0.5B–32B，GRPO 约 2400 步量级（“1/12 训练=200 步”，§2.3，推算）；GPU 预算文中未给（未核对附录）。

### A2 Zhao 2504.07912（Echo Chamber，COLM'25）
1. 内容：自己从头预训练 150M 与 1B 模型，数据为 TinyGSM/OpenMathInstruct1/2 的不同混合（§2.1），再用 PPO（为主）、GRPO、Expert Iteration 做 RL，GSM8K 训练题（§2.2）。结果：150M 模型在第 1 个 epoch 内几乎完全塌到单一输出格式，多为 TinyGSM 代码格式（Fig.2，§3.1）；KL 系数 0.001→0.01 后仍保留部分 OMI2 格式（Fig.3）。哪种格式赢不总是最准或最常见：4×OMI1 混合起始 OMI1 占 62%、TinyGSM 28%，仍收敛到 TinyGSM；8×OMI1 则收敛到 OMI1，且准确率较低并后期下降（Fig.4，§3.2）。1B 模型偏好自然语言 OMI2 格式（Fig.7，§3.4）。简单题 RL 可迁移到 MATH-500（Table 1，§3.7）。理论：KL 正则最优解 ∝ πref·exp(r/β)（§3.6）。
2. 回答了什么：直接支持“早期（首 epoch）塌缩到某模式并锁定”这一路径依赖现象，且“初始比例/预训练混合决定哪个模式赢”。但 (a) 比较的是不同**预训练**起点而非同等成功的不同经验；(b) 未区分“不再采样”与“不能学”；GRPO 注记“短暂塌缩”（§3.5，App.F）。
3. 自训：是，150M/1B 从零预训练 + PPO；GPU 预算 grep 未见（未核对）。

### A3 Huang 2602.14872（Implicit Curriculum）
1. 内容：理论（群组合任务上的 transformer + 外层 Fourier 分析），结论：混合难度训练自发形成易→难课程；难度谱平滑→“接力”，有大间断→类 grokking 平台（Abstract，Thm 5.1/5.2）。真实模型：Qwen2.5-1.5B-Instruct、Qwen3-4B-Base，N 位乘法，GRPO n=8，lr 1e-6，1000 步，每 25 步存检查点（§7，Fig.1/5）。大间隔混合时 N=8,9 全程为 0（Fig.1b）。
2. 回答了什么：单次运行内“先学会的简单任务塑造后续可学的前沿”——是**训练内顺序依赖**的机制解释，部分对应“早期成功塑造后续学习”，但变量是任务难度分布，不是“同等成功的不同经验”。平台期被解释为**梯度信号消失（长视野处近乎均匀注意力，Thm 4.x）**，更偏 access/信号侧；未做经验替换。
3. 自训：是，1.5B/4B，各 1000 步；GPU 预算未给（未核对）。

### A4 Chen/Li/Zou 2506.04695（Pattern Selection）
1. 内容：Qwen2.5-3B 在 MATH 上 RLVR vs RLIF（Fig.1）；推理模式分类：各模式自身成功率训练中大致稳定，RL 主要通过少数关键 token 改变模式分布（§4.2–4.3）。理论：RLVR 收敛到成功率最高的模式；若初始总体准确率低于次优模式成功率则有“纠缠阶段”，T0 随 γπref 超指数增长（Thm 5.3/5.4，§6.1，Fig.2）。附录有 7B-Instruct vs SimpleRL-Zoo、32B vs QwQ 的对比（A.2/A.3）。
2. 回答了什么：给出“初始化（base 的模式选择概率）决定收敛快慢”的理论，属**起点依赖**，接近 access 的形式化（最优模式被选中概率过小→长时间停滞）。没有“同等成功的经验”和 plasticity 区分；理论是简化的两阶段模型。
3. 自训：是，3B 为主；GPU 预算 grep 未见（未核对）。

### A5 Nguyen 2510.02230（Reasoning Boundary Paradox）
1. 内容：Qwen2.5-Math-1.5B/7B、Llama-3.2-3B-Instruct，GRPO，**每模型 4 GPU**，lr 1e-6，500 步，rollout batch 64×8（App. 训练配置）。定义对训练样本的影响函数 K(x,x′,y,y⁺)，发现“负干扰”：学一些题会降低基座原本答对的其他题的正确解似然（Fig.2C/D，§4），“赢者通吃”：基座高似然题吸收主要学习信号（§5）；Qwen2.5-Math 的 code→自然语言切换（Fig.6）。提出 SELF（只训贪心失败题 + forward-KL，§6，Table 1）。
2. 回答了什么：给出“某些题的学习如何改变其他题的后续可学性/覆盖”的**训练内、更新层面**机制（负干扰），属于“经验→后续学习”这一链的一半，但看的是“当前更新对其他题似然的影响”，非跨阶段重放。
3. 自训：是，1.5B–7B，500 步，4 GPU。

### A6 Kong 2606.18089（Reasoning Traces → Reusable Modules，ICML'26）
1. 内容：层级潜变量选择模型；SFT 提供原子模块素材，RL 分解并重组（Abstract，§2–§3）。实验：Llama-3.1-8B-Instruct，合成字符串变换任务（24 原子技能），SFT 2 epochs lr 2e-5，RL lr 1e-6、300 步（长跑 1000 步，App.J/Fig.14–15）、批 16（App. Table 3）。条件：RL 的 rollout 可达性、奖励信息量（§3.2 条件）。
2. 训练历史：只研究 SFT→RL 两阶段**数据关系**（SFT 覆盖 vs RL 组合，Fig.7，Table 2），没有研究 RL 内部的早期成功/历史影响。与候选问题关系很弱。
3. 自训：是，8B，300–1000 步；GPU 未给（未核对）。

## B. 额外检索（arXiv，2025–2026；IDs 取自搜索结果，全文只读了标「已读」者）
1. 2611.04061 On the Primacy Bias in RLVR（NeurIPS'26）已读。
2. 2609.13443 Never Giving Up / Matthew Effect（Noukhovitch, Ivison, Lambert, Courville）已读。
3. 2611.33102 RL Can Be Recovered From Its Own Rollouts（Sheng…Zanette）已读。
4. 2605.16787 Unlearnability Phenomenon in RLVR（Chen, He, Zhao）已读（部分）。
5. 2611.02747 Zero-to-One Jump（TTFP，NAPO）已读摘要+开头：从共享检查点出发、只变采样随机性，标记 N→P 的 prompt；Qwen2.5-Math-7B，8×H100。未读完。
6. 2508.06412 LoRR（Reset Replay：重置+plasticity injection 用于 LLM 优化）仅搜索摘要；未核对。
7. 2601.04537 Linear Dynamics in RLVR（“RLVR 放大早期出现的趋势”，可外推）仅摘要；未核对。
8. 2604.01597 / 2610.28883 / 2610.10422（rollout 数据归因：I-PPO、RL-IF、BehaviorTrace）仅搜索摘要；未核对。BehaviorTrace 称 GRPO 上 step 级归因只能恢复“哪一步训练了”，不能恢复“哪个 rollout 携带行为”（Qwen2.5-1.5B）——此条来自摘要，未核对。

## C. 三篇最近邻的细读

### C1 Sheng 2611.33102（把 rollout 重放到基座）——设计最接近“同一经验换阶段/换顺序”
- 设置：Qwen3-1.7B/4B-Base 的在线 MaxRL（也含 GRPO，Fig.13），Polaris-53K，1000 步、每步 256 prompts×16=4096 rollouts，lr 1e-6（App. Table 2）；回放用**最大似然（SFT）**而非 RL 更新，从同一个基座出发，每批一次更新。GPU 预算 grep 未见（未核对）。
- 发现：(i) 原样 RL 重放灾难性崩溃（Fig.2；基线放大差异的机制）；(ii) 按生成顺序做 ML 重放几乎重现在线学习曲线（Fig.4/5）；(iii) **同一批 rollout 换顺序得到不同学习曲线**：逆序在前 100 步到 MATH-500 约 70%，之后随早期批次回落到约 57%；终点误差 chronological < shuffled < reverse（Fig.6/7，§3.3，原文“final performance depends on the order”）；(iv) 只重放最后几步（甚至最后一批）即可恢复终点性能（Fig.8，§3.4），作者结论：RL 计算主要用于“发现更好的采样分布”而非“学习它”。
- 与候选问题的关系：给出 access 一侧的强证据（学习所需样本的性能随 rollout 所属阶段而定，样本里已含改进；难在“采到”）。但重放器是 SFT，老师分布固定，不是 RL 学习响应；起点永远是基座，**没有把同一经验注入到不同阶段的检查点**，也没有测“同等成功但不同”的经验。

### C2 Nguyen 2611.04061（Primacy Bias in RLVR）
- 设置：MNIST 玩具（Zipf 偏斜预训练 vs 随机初始化，GRPO，§4，Fig.1–3）+ Qwen2.5-3B-Instruct（4×H100，lr 1e-6，批 256，16 rollouts，App.B）在 MATH 上按难度分子集分别训练（§6，Fig.7–11），Llama-3.2-3B 复现（App.D）；对公开检查点做 eNTK/线性化分析（Table 1，Fig.4–6）。
- 发现：偏斜越大，hard 类越晚学会且参数更新更稀疏（Fig.3）；LLM 只在容易子集上涨，hard 子集几乎不涨（Fig.7）；长训练改善 pass@k 但遗忘 easy（Fig.8–10）。
- 与候选问题：提出“早期经验（预训练）损害后续可学性（lazy regime）”，对应 plasticity 一侧，且指出 primacy bias “既限制探索又损害 on-policy 数据的可学性”（§1）。但路径是**预训练→RL**，不是 **RL 早期→RL 后期**；“primacy bias”机理用 CKA/参数稀疏性相关性佐证，未做同一批经验的干预；“分子集训练”的难度由最终策略 pass@1 估计（§6，未核对该估计是否含选择偏差）。

### C3 Noukhovitch 2609.13443（Matthew Effect / NGU）
- 设置：Qwen2.5-0.5B-Instruct 受控实验（§3，Fig.2/3），Qwen3-4B-Base 在 DeepScaleR 10k 子集上训练、每设置约 120 H100 小时、3 seeds（§4，Fig.7）；Qwen3-4B-Instruct 在 Manufactoria 上训练（§5，Fig.8–10）。
- 发现：RL 对基座本就会做的题提升大、难题提升小（Fig.1，Olmo 3.1 RL-Zero/DeepCoder/Qwen3-32B）；**增加 K 并不解决**（Fig.2），支持“信号丢失不是主因”；NGU（采到一个正确为止）改善难题表现。Fig.10：先用 per-test 奖励训练 3000 步（次优目标），再切换到 all-tests 奖励，可以“恢复”，作者据此认为 LLM RL **不存在经典 plasticity loss**，Matthew effect 与之不同（§5，Fig.10）。
- 与候选问题：直接对 plasticity 与 access 二分法给出一个**单点干预证据**：次优训练 3000 步后换目标仍可学（plasticity 未丧失，起码在该任务该目标下），而增加采样/重分配计算能帮助难题（access 侧）。局限：一个编程任务、一个切换（奖励函数改变而非“同一经验”）；通过 NGU 本身改变了采样，所以“access”与“学习响应”仍混在 NGU 里。

## D. 对候选问题的影响（只列事实）
已被回答/已有证据的部分：
- “早期成功改变后期”在同一次训练内存在：熵早期耗尽并与最终性能呈拟合关系（Cui §2.3–2.4）；早期收敛到单一输出格式，且哪种格式赢取决于预训练混合（Zhao Fig.2/4）；先学会的简单任务决定后续可学前沿（Huang Fig.1）；赢者通吃/负干扰（Nguyen 2510.02230 Fig.2/§5）。以上多为“同一曲线内相关”，仅 Zhao 通过改预训练混合、Sheng 通过改 rollout 顺序做了近似干预。
- access 侧：Cui（熵），Sheng（rollout 已含改进，难在采到），Noukhovitch（NGU 提高难题增益）；plasticity 侧：Nguyen 2611.04061（lazy regime，预训练→RL），Noukhovitch Fig.10（3000 步次优目标后可恢复，反方向证据）。两侧结论目前互相不一致或不在同一设置下比较。
- “相同经验、不同顺序/阶段”：Sheng §3.3 已做顺序重放，发现终点依赖顺序，但接收者是基座 + SFT 更新。

仍开放的部分（未见任何一篇做过；检索不完整，可能漏）：
- 把**同一批经验**分别注入同一次 RL 运行不同阶段的检查点，并用**RL 更新**（而非 SFT）测量学习响应。
- 控制“同等成功率（同等 reward/同 pass@1）但推理经验的内容不同”后的后续学习差异。Zhao 是预训练格式差异，Sheng 是时间/顺序差异，两者都不是内容匹配的对照。
- 在同一设置里把“采不到”与“学不动”分开测量（Cui/Noukhovitch/Nguyen 各自只测一侧，且均有混杂：NGU 同时改变采样和计算分配）。
- 用多个独立 seed 检验“早期成功→后期差异”的随机性来源（Noukhovitch 3 seeds；其余多数为单次运行；各篇 seed 数未全部核对）。

最接近的设计（Sheng 2611.33102）留下的空白：
1. 学生永远从基座起步、用最大似然更新，无法回答“**当前策略是否还能从该经验中学到**”（RL 学习响应），只能回答“经验里是否含有该阶段的信息”。
2. 经验是按生成顺序整批重放，**未筛选/匹配成功程度**，也没有在 rollout 层面比较不同经验的价值。
3. 只有一个在线 MaxRL 运行（Qwen3-1.7B-Base，Polaris-53K）的顺序对比（Fig.6/7），**无多 seed 路径方差**；GRPO 仅在 Fig.13 做终点检查。
4. 没有在 RL 平台期检查点上重放来源于更早/更晚阶段的 rollout，因此平台期的 access vs plasticity 判别在该设计下无法给出。
