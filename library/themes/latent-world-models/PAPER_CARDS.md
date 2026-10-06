# 深读卡：latent world model 规划（2026-10-07）

格式：问题 → 方法/设置 → 决定性证据 → idea 来源（推测）→ 与最近邻的距离 → 对我们的用处。只收会改变我们判断的论文。

## A. 范式奠基

**DINO-WM（Zhou et al., ICML 2025, 2411.04983）**：冻结 DINOv2 patch 特征 + ViT 预测器 + CEM。改写的设计决定：世界模型不必重建像素，用预训练表征即可零样本规划。idea 来源：视觉基础模型成熟后，把 Dreamer 式“学表征”换成“借表征”。对我们：后续几乎所有工作的评测协议（goal = 数据中 offset 步后的帧，CEM 300×30，horizon 5）都继承自它；这个协议本身决定了基准偏向“在数据分布内到达近目标”。

**PLDM（Sobal et al., NeurIPS 2025, 2502.14819）**：JEPA 动力学 + 规划 vs GCBC/GCIQL/HIQL/HILP/CRL，在数据质量、轨迹长度、未见布局上比较。结论：model-free 需要大量高质量数据；规划在次优数据、新布局上更好。改写的设计决定：从“哪个算法强”改为“什么数据条件下 model-based 有优势”。对我们：它是“搜索何时有价值”的正面证据，和 GC-IDM 的负面证据之间的矛盾尚未被系统化解释（数据质量 / 目标分布 / 规模）。

**LeWorldModel（Maes, Le Lidec, Scieur, LeCun, Balestriero, 2603.19312）**：端到端 JEPA，只有预测损失 + SIGReg（把 latent 推向各向同性高斯），15M 参数，单卡数小时，规划比 DINO-WM 快 48×。改写的设计决定：端到端 JEPA 不需要 EMA / 冻结编码器 / 六项损失。后果：造出了小组可复现的公共底座，直接引发 2026 年的论文洪水。对我们：所有缩放实验以它的目标函数为固定点，S 尺寸 = 官方配置。

**JEPA-WMs / What Drives Success（Terver, ..., Bardes, LeCun, 2512.24497）**：Meta 的设计空间研究（编码器、predictor、多步训练、规划器）。关键附带发现：**仿真环境里 ViT-B/L 编码器不比 ViT-S 好；predictor 深度 6 最优，9–12 变差；真实 DROID 上则越大越好**；作者猜测“更大的 embedding 空间让规划的优化地形更难，或固定算力下欠训练”。数据 2/10/50/100% 一律单调变好。规划器：CEM 总体最好，梯度法只在平滑代价（Metaworld）上好。预测保真与规划成功弱相关。对我们：这是“规模在仿真里不帮规划”的第一个信号，但只有零散点、没有控制 lr / 训练量 / latent 维度，也没有测试时算力维度——正是 I15 的切入点。

## B. “预测 ≠ 规划”的诊断群（2026，饱和）

**RC-aux（Predictive but Not Plannable, NeurIPS 2026, 2605.07278）**：在 LeWM 上加多时域开环预测 + 预算条件可达性监督，并允许规划器使用可达性。决定性证据：分解训练侧与规划侧的作用（Wall 50.4 → 72.4 → 83.6）；PushT 上几乎无增益。idea 来源：把 GCRL 的时间距离 / 可达性思想嫁接到 JEPA 规划。距离：与 Temporal-Distance JEPA、Traj-LeWM、How Long Not How Close 同类。

**The Objective Is the Bottleneck（2608.12959）**：独立复现 LeWM TwoRoom；predictor 预测 75 步后仍比“世界静止”假设好得多，但 CEM 的平方 latent 距离与真实距离只有 r=0.426、在 80 单位处饱和；只换代价（学到的帧间隔头）就把 offset 100 的成功率从 26% 提到 98%，不用重训。对我们：长目标失败主要是代价不是模型——缩放实验里长 offset 的读数需要和这一点分开解释（模型变大可能根本不改变长目标表现）。

**Planning Limits of Latent World Models（2609.39235）**：冻结 V-JEPA 2 / 2.1 / VideoMAEv2 / VideoPrism / DINOv2 + 动作预测器，在 Meta-World 与 BridgeV2 上。WM 只在目标位于想象轨迹之内或稍远（5–10 步）时可靠排序；**predictor 放大 81 倍、训练更长 rollout 都不扩大这个范围**；用真模拟器替代模型，成功率随目标从 5 步移到 20 步仍从 92% 跌到 41%。在可规划范围内用 WM 从 VLA 的 8 个提议中选，成功率 65%→77%。对我们：predictor 缩放无效的直接证据（冻结编码器设定）；端到端训练下是否同样成立未知。

**ARC-Bench（2609.05461）**：固定候选协议审计“latent 距离能否排序动作”；官方 JEPA-WM 检查点在操作任务上几乎总选到次优候选；降低重规划频率成功率崩溃——闭环重规划掩盖了排序错误。对我们：闭环成功率高估了模型的排序能力，候选库排序（bank.py）是必要的第二读数。

**VIScore（Wu, Balestriero, Levine, 2608.11174）** / **ATM（2606.09028）** / **Control Theory of Predictability（2607.10362）**：同配置不同种子，验证损失差 ±8% 以内，PushT 成功率 78–92%，损失与成功的秩相关 0.024；规划器可达集上的保真度（VIScore、真实转移上的动作可辨识性、规划器可达测度上的误差）才相关。对我们：欠约束在固定规模下已被说清；规模如何改变欠约束（方差是否随规模缩小）没人测。

**When Low Prediction Error Misleads Planning（2610.05550）**：把端点误差分解为候选池中心误差与动作相关响应误差；中心误差主导 MSE，但修正动作相关部分更改善排序。与前任 E20 的 CENTER 损失是同一分解。

**The Evaluation Protocol Determines the Result（2608.10145）**：独立复现 LeWM TwoRoom，需要四个配置文件里没有写的约定；同一检查点只改目标构造方式，成功率 84% → 8%。对我们：所有结论必须在固定、公开的评测协议下给出，并报告协议敏感性。

## C. 搜索的价值

**Latent Geometry Beyond Search（GC-IDM, 2605.08732）**：在冻结 LeWM latent 上训练 1.5M 参数 MLP（当前 latent、目标 latent、剩余步数 → 动作），每任务约 20 分钟。TwoRoom 100% vs CEM 82–84%，Cube 99% vs 67–73%，Reacher 100% vs 68–70%，PushT 84–85% vs 82–89%；比 CEM 快 100–130×；更换 MPPI / iCEM / 梯度法结论不变。PushT 随目标距离从 94% 降到 70%。机制解释：闭环每步重编码纠错、方向正确的噪声预测会累积。idea 来源：SIGReg 的各向同性让局部逆问题条件良好。**局限**：只用专家数据、只测数据分布内的目标——这正是摊销策略最强的区域。对我们：搜索的价值必须在“策略没见过的行为”上测，且应随规模测。

**The Surprising Difficulty of Search in MBRL（Chang, Henaff, Amos, Dudek, Fujimoto, ICML 2026, 2601.21306）**：搜索可能在模型很准时也伤害性能；关键是价值函数的高估偏差，取集成最小值即可让搜索有效。对我们：“搜索伤害”不一定来自动力学模型错误，也可能来自代价 / 价值的偏差。

**Imperfect World Models are Exploitable（NeurIPS 2026, 2605.15960）**：形式化“模型利用”，证明大策略集上不可避免，给出安全视界。纯理论；没有经验规律。

**Action from Adjacent Set（ASAR, 2607.23602）**：Cube 上候选总数从 72 增到 288，按最小 latent 代价选中可行序列的比例从 .375 降到 .062——Goodhart 现象的直接观测（单模型）。

## D. 规模相关的祖先（跨领域）

**Jones 2021, Scaling Scaling Laws with Board Games**：Hex 上 AlphaZero，单卡级算力就能测出平滑的性能律，以及训练算力与测试时搜索算力的交换率（训练算力每增加 10×，可以省掉约 15× 的测试时搜索）。启示：小环境 + 大量独立训练足以测出有影响力的规律。

**Gao, Schulman, Hilton 2023, Scaling Laws for Reward Model Overoptimization**：best-of-n 与 RL 对代理奖励优化时，真实奖励先升后降，函数形式稳定，系数随奖励模型规模平滑变化。启示：候选库上的 best-of-N 曲线就是世界模型版的过度优化测量。

**Pearce et al. 2024, Scaling Laws for Pre-training Agents and World Models（2411.04434）**：世界模型损失与模仿损失都有类 LLM 的幂律，系数受 tokenizer 与架构影响很大。只测损失，不测规划。

**Byravan et al. 2021, Evaluating model-based planning and planner amortization（2110.03363）**：调好的 model-free 是强基线；MPC + 学到的提议在多任务 / 多目标设定下更好；规划可以蒸馏成策略而不掉点。
