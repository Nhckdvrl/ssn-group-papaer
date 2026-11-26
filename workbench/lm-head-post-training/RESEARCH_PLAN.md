# LM Head 后训练探索 · 技术与执行指南

## 0. 研究目标与边界

核心问题不是验证某篇论文必然正确，而是搞清输出头在真实后训练中怎样变化、怎样传递学习信号、何时值得修改。我们追求可重复、可比较、能改变后续技术选择的实际观察。现阶段只做 E01（对话 E0）与 E02（对话 E1）。E03（对话 E2）等前两项结果，人审后再定。先用数学任务、单个模型建立可靠工具；不做全模型/全任务 Cartesian sweep，不以“看到梯度小”当成瓶颈证据。

## 1. 共同资产与预检

- 首选 Qwen/Qwen3-8B-Base 与 Qwen/Qwen3-8B；检查模型实际 config、checkpoint/revision、tokenizer 映射、vocab padding、head bias、最终归一化、权重共享状态与实际 tensor storage。已知讨论中 Qwen3-1.7B-Base 共享权重，Qwen3-8B-Base 不共享；仍以本地实际检查为准。
- E01 辅助 OLMo-3-7B：从官方 model card/训练 recipe 核实 Base → Think-SFT → Think-DPO → Think-RLVR 的真实 parent 路径；不可把不同分支硬连成因果谱系。若某阶段未缓存或无法核实，先完成已验证相邻对并记录缺失。Qwen Base/Instruct 对比只是自然观察，不是随机单因素训练实验。
- 保持同一 token IDs、同一序列位置（预测 next token）、相同 causal/padding mask 和有效词表维度。跨家族不逐行对比 token IDs；特殊 token 定义用 tokenizer 元数据，频率按注明来源的固定语料估计；实际不存在的 padding 行单列。
- 先检查可用 GPU、节点磁盘、网络、框架版本；一节点内独立运行；单卡小样本跑通再扩，避免多节点和重复下载。记录模型/data hash、dtype（磁盘权重/forward/累加/SVD）、seed、GPU·时、峰值显存和 wall-clock。不要假定所有 GPU 空闲。
- 数据优先使用现有可验证数学题及参考解（可选 GSM8K/MATH 的固定子集；核实 license、verifier、训练/验证 split，具体 revision 由执行者写卡）。固定样本清单，不用实际测试答案调参。E01/E02 可共享小型固定文本集，E02 以数学为主；教师参考解用于分布对照而非默认 ground truth reasoning。

## 2. E01：公开权重解剖

对相邻、兼容 checkpoint，以 FP32 cast 后做差（累加 FP64 或稳定 FP32），报告各模块相对 Frobenius norm ||ΔW||F/||W0||F、绝对 norm、参数量、精确零元素比例、分位数。零比例仅是已保存精度下的可见差值，不代表真实训练更新；检查 BF16/FP32 storage 与 tied tensors，不重复计数。跨模块归一化仍可能受参数化影响。

对 LM Head 更新 ΔW：
- 行级平方能量、累计 top-k 能量曲线、按特殊/普通/频率分桶统计（同时报组大小、每行平均与总量）。
- 奇异值谱、累计平方能量、有效秩（注明定义，建议 entropy effective rank exp[-Σ q log q], q=σ²/Σσ²；也报 stable rank 与覆盖率）。零矩阵单列 undefined。
- 大矩阵分块 streaming，优先 Gram ΔW^T ΔW 或经验证的 randomized SVD；记录精度、近似误差与运行成本。不要硬读全模型多份 FP32 常驻 GPU。

功能分解：设 W0、W1 是输出头，h0、h1 是同一输入同位置过 final RMSNorm 后真实隐藏向量；ΔW=W1-W0，Δh=h1-h0。无 bias 时：
$$z_1-z_0=\Delta W h_0+W_0\Delta h+\Delta W\Delta h.$$
有 bias 时加 Δb。按位置验证三项重构误差，并保存四种组合 z00=W0h0、z10=W1h0、z01=W0h1、z11=W1h1（有 bias 用对应 head）。在 FP32 比较 logit RMS、方向/内积、KL(p11 || p01)、KL(p00 || p10)、top-1 翻转率、目标 token logprob 差、分布熵。报告方向、样本数；保留交叉项和相互抵消，不把三个 norm 百分比当作可加贡献。
这是固定隐状态的**反事实头部敏感性**，不是能力归属的唯一因果证明；互换组合不一定落在正常联合分布。Procrustes、整模型互换及特殊行干预非首轮必做，只有信号值得追查才开启。若比较 logit 空间几何，用原生坐标，并注明坐标与共同适配的局限。

## 3. E02：梯度几何，必须分清三个概念

记词表大小 m、隐藏维度 d、W∈R^(m×d)，g_z∈R^m，g_h=W^T g_z。SVD W=UΣR^T（R 为右奇异向量，不与词表 V 混用）。用保留的奇异方向 U_r：
$$\rho(g_z)=\frac{\|U_r^\top g_z\|_2^2}{\|g_z\|_2^2},\qquad \gamma(g_z)=\frac{\|W^\top g_z\|_2}{\|g_z\|_2}.$$
ρ 是数值列空间正交投影能量比例（[0,1]），γ 是含奇异值缩放的梯度增益（可大于 1）。零梯度时两者 undefined，不填 0、不混入均值。ρ 低不等于有效学习信号损失，更不等于训练瓶颈；null-space 也是相对于当前 W 的。

省内存实现：
$$U_r^\top g_z=\Sigma_r^{-1} R_r^\top g_h.$$
无需保存 U 或完整逐 token g_z。可按词表行分块累积 G=W^T W，在 FP64（或实测稳定的混合精度）做对称 eigh 得 R 与 σ²，或采用内存允许的稳定 thin SVD/QR。Gram 会平方条件数，不能用 FP32 Gram 无条件宣称 1e-6 奇异值阈值准确；初始相对阈值 1e-6，做 1e-4/1e-5/1e-6 敏感性检查、数值秩记录，必要时高精度直接 SVD/QR 复核。近零负特征值需诊断，禁止无声 clamp 后当真实。SVD/Gram 不是零算力；记录时间显存。
对简单 CE / advantage-weighted CE，g_z=c(p-e_a)，
$$\|g_z\|_2^2=c^2(\sum_j p_j^2-2p_a+1).$$
用 FP32 稳定 softmax/logsumexp 按位置或词表分块算；也可用 g_h=c(W^T p-W_a) 直接获得。分块 softmax 必须用全词表同一归一化常数，包含实际参与 softmax 的行。autograd 小样本对照应 hook final norm 后且 LM Head 前的激活梯度；其他 loss 路径须排除。KL/entropy 等附加项不满足单项闭式时分开报告，不能混入后继续用 CE 公式。采样 engine 与诊断 forward 的 logits/tokenization/temperature/top-p、off-policy ratio 及训练掩码须对齐或记录差异。

### 3.1 真实训练信号不是两种完全不同的单 token 向量

在相同 context、token、分布下，CE g=p-e_a；未 clipping 的 policy loss 梯度为 c(p-e_a)，仅标量差异。故非零 c 下 ρ 与 γ 不变；负 c 只翻转方向。此不变量是实现阳性/阴性校验，不是论文发现。

E02 必须有以下成对比较：
1. 同一 on-policy 轨迹、同一 replay logits，所有有效 token 做普通 CE（c=1，或同一 reduction 标量），与真实组内 advantage 加权 CE。先诊断 unclipped policy gradient at behavior policy，额外 KL、clip、entropy 单列；不是训练完整 GRPO。
2. 同 prompt 教师参考轨迹的 CE 与 on-policy 轨迹 CE；这测轨迹分布变化，不是纯 objective 差异。参考解与采样答案格式长度可能不同，报分层/匹配。
3. 对不同 checkpoint 的比较为后续扩展；首轮单模型，跨词表规模不做因果主张。
同一 prompt 采样 8 个 completions（目标 128 prompt，先小规模 smoke）；记录二元 verifier reward、每组均值/标准差、advantage、截断和解析失败。按所选 GRPO 版本明确 std convention、epsilon、token/sequence reduction、mask、importance ratio、是否 clipping。全对/全错组不能默默丢弃，单独报比例与零梯度；同一轨迹 CE vs RL 聚合必须共享位置与分母规则。不要为得到有方差组擅自筛题；若补采样，明确另列。

### 3.2 两档统计都要保留，并避免伪因果

单 token：ρ、γ 的分布与均值；等 token / 等题目汇总，能量加权保留率 Σ||P g||²/Σ||g||²，按 advantage 正负、reward、token 位置、长度、熵分层；不把重复 token 当独立样本。单 token g 的余弦或秩应明确是否中心化、采样方案，不能由 g_h 秩直接推断整个骨干秩。

组级：同题 8 轨迹按明确的训练权重 c_t（含 reduction）流式累计 G_z=Σ g_z,t 与 G_h=Σ g_h,t，计算 ρ(G_z)、γ(G_z)，并报告抵消比 ||Σ g||/Σ||g||、sum energy、正负组分与 near-zero aggregate 比例。Σ g_h=W^TΣ g_z 对同一 W 成立。可用 FP32/FP64 accumulation，每题仅持有一个 m 维向量；按实际 mask 算分母。对 c=1 与 advantage 加权比较配对题目差异。输出头参数梯度实际为 Σ g_z,t h_t^T，骨干参数梯度为 Σ J_t^T g_h,t，不能用聚合 logit 梯度替代这两者。若后续需要，可在少量样本用实际 autograd 或矩阵 sketch 测真实参数梯度，首轮不要求保存巨型 g_W。
有效秩/方向一致性：在固定采样 token 数与组权重下，对 g_h 的行矩阵用 Gram/sketch，定义 entropy effective rank 与稳定秩；分别报告方向归一化和原始能量版本、题目间 cosine、零梯度处理。聚合比率受抵消影响，不等于每 token 比率的平均。

## 4. 最低实现验证与运行纪律

- 合成小 W（满秩/低秩），构造列空间内、正交空间内、混合方向和零梯度，显式 U 投影 vs 闭式重建应在测得误差范围一致；W 乘常数后 ρ 不变、γ 按绝对比例变化。用小 FP64 随机矩阵及实际头的少量 token 与直接 autograd/显式投影复算。正负 c 验证共线、ρ 不变；构造正负抵消组验证 group aggregate。
- E01 同 checkpoint 对照 ΔW=0；固定 h 的合成已知扰动及三项恒等式复算；原生 forward 与手工 z 对照（考虑 bias、dtype 和额外 softcap）。固定样本重复、FP32 与高精度比较形成噪声地板。若工具验证失败，不做科学解释。
- MIE 在卡上预先记录：先以是否显著超出数值/重复波动且能改变后续实验选择为准；不预设某个 ρ 阈值等于有害。对题目级 paired bootstrap CI（题为独立单位）；pilot 小样本信号不升级为因果。看到数据后才定义的切片明确 POST-HOC。
- 原始 rollout/verifier/样本 token 指纹保留到授权本地，结果按模型/阶段/seed/revision 分目录，失败记录不能删。先估算 GPU·时后再启动扩展；不以虚构的半小时/两小时承诺当作预算。

## 5. E03（冻结训练）：为什么暂缓

若 E01/E02 发现值得追查的差异，才比较同一未共享输出头 checkpoint 上的 SFT-A/B 与 RL-A/B；全骨干更新，唯一预定开关为 head trainable。每个范式内固定初始 checkpoint、数据/rollout policy 初始状态、优化器、训练 token / 更新数、评测、seed；记录 SFT vs RL 差异与真实计算，不假定两范式预算天然公平。可用 50–100 optimizer steps 作为讨论的探索量级，不预先启动。
检查 FP32 master weight、Adam 状态以及 optimizer step 的实际实现（不是仅看 autocast 配置；FSDP/ZeRO/框架可能不同）；验证冻结组 head hash 不变、输入 embedding 仍正常更新、解冻组有真实更新，weight tying 未被意外重建。记录 gradient norm、真实 FP32 ΔW 与部署精度可见差分。仅冻结与否同时改变前向适应能力、训练参数与反向通道，不能证明“梯度瓶颈”。如有实质效应，再由数据决定参数量匹配、等预算、仅反向干预、低秩/温度/对角缩放等，不全部预跑。生成/训练 logprob 对齐，排查饱和与 rollout 偏差。

## 6. 决策与交付

E01/E02 完成后一起看：
- Head 更新小但 logits 敏感：排查归一化、极少数 token 及方向，决定是否做最小功能干预。
- 头部变化大但反事实影响小：检查共同适配、频率和交叉抵消；不贸然宣称无用。
- 匹配轨迹单 token 不变、组级差异稳定：查奖励符号/权重/抵消与真实参数梯度；若仅采样分布不同，改为分布解释。
- ρ 很低但训练未见证据：不叫有害瓶颈；是否值得 E03 由人决定。
- 工具失效：修工具；精度敏感或输入不一致：降级/作废并记录。
- 结果无明显科学增量：报告负结果及其分辨率，先人审，不机械地关闭领域；如果两个 lead 都被平凡解释吸收，回到实际痛点/标准测量，或由用户授权暂停与切换空间 2。
- 意外结果：保存原始证据、写 PAIN_LOG，最小复算、提出可区分解释，不强迫服务于现有假说。

交付：可复用脚本与 env、原始清单/命令、版本与运行记录、E01 模块/行/谱/功能结果、E02 token/组汇总/配对 CI、数值校验报告、失败样本、科学意义与下一步人审。将大文件留节点；小型表图和摘要放 results/；按工作台协议更新 CLAIMS/PAIN_LOG/logs，未达到证据要求不升级。先建设 D1/D2，后按标准完成 D3–D6；定位与论文形态卡随真实发现更新，不把流程表格当作阻止 E01/E02 首测的前置任务。

## 7. 文献入口（不是已完成定位）

必读 [Lost in Backpropagation](https://arxiv.org/abs/2603.10145)、[Causal Test](https://arxiv.org/abs/2608.16671) 的方法、关键图与限制；复现实验口径应以原文为准。后续有信号才针对性补查 softmax bottleneck（包括仓库 IDEA_EXPLORATION 提及的反向归因工作）、head-only tuning / PEFT、输出层与表征协同适配、RL 稀疏性与数值精度。不得把未取得全文的预印本当作已核实机制；无须为首轮重新阅读整个领域。
