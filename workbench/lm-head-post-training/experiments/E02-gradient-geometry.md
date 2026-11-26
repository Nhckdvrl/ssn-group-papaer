# E02：梯度投影与组级信号（2026-11-26；对话 E1）
- **状态：** RUNNING（工具校验已过；smoke 运行中）
- **类型：** PILOT / 标准测量与资产建设
- **对应：** I02（主），I04（头部行梯度符号一致性）
- **问题（一句话）：** 同轨迹的奖励加权与教师/on-policy 分布分别怎样影响单 token、题目级输出空间投影和梯度方向？
- **设置：**
  - 模型：主跑 Qwen3-8B-Base（RL-zero 设定，reward 方差足够；与 E01 的 Base→RL-Zero 对应）；smoke 用 Qwen3-8B 非思考模式验证流水线。revision 写入结果。
  - 数据：`data/e02_prompts.json`，MATH-train Level 3–5，7 个科目分层，128 题，seed 0；教师参考 = MATH 官方题解（只作分布对照，不当推理 ground truth）。
  - 采样：vLLM 0.23（`~/.venvs/vllm023-cu128`），每题 8 条，T=1、top_p=1、top_k 关闭（行为策略 = 模型 softmax），max 2048 token，seed 0；base 模型用纯文本模板（见 `scripts/e02_rollout.py`）。奖励：`scripts/verifier.py`（最后一个 \boxed + 规范化 + 数值比较，解析失败单列，不静默计分；128 个参考答案自比全对）。
  - Replay：transformers 4.57.6 bf16 骨干，最终 norm 后隐状态 h，FP32 全词表 logits（分块共享同一 softmax 常数）；不更新参数。
  - 四种信号：ce_onpolicy c=1/(G|o_i|)；rl c=A_i/(G|o_i|)，A_i=(r_i−mean)/(std+1e−6)（总体 std），未裁剪 PG@behaviour，无 KL/entropy；rft c=r_i/(G|o_i|)（只保留正确样本，单边权重）；teacher c=1/|ref|。全对/全错组 A=0：rl 条件下无梯度，单独报比例，不丢弃其它条件。
- **读数：** 正交投影能量 ρ、梯度增益 γ（每 token，ρ/γ 与 c≠0 无关）；等 token 与能量加权的组均值；按 p_a 分层；目标行杠杆 ℓ_a；组级 ρ(Σcg)、γ(Σcg)、抵消比 ‖Σcg‖/Σ‖cg‖；replay 与 vLLM logprob 差；I04：每题为一个 batch，头部参数梯度 G_W^b=Σ c (p−e_a) hᵀ 的逐元素跨 batch SNR=|mean_b|/√mean_b²（Adam m̂/√v̂ 的 β→1 近似），按“该条件中做过目标/从未做目标”与 Pile 频数分桶，及从未做目标行的平均梯度与 μ 的余弦。聚合 logit 梯度不是参数梯度；SNR 依赖 batch 大小与 token 数（teacher 每 batch 约 1 条参考解、rl/ce 每 batch 8 条采样），解读时须并列 B 与 token 数，并报告随机符号基线 √(2/π)/√B。
- **阳性对照：** `scripts/test_geom.py`（列空间内/外、闭式=显式 U、缩放不变、CE 闭式=autograd、正负 c 共线、抵消组、零梯度 NaN）全过；实际模型上随机行扰动的 ρ≈d/V（E01 selftest 实测 0.0288 vs 0.0270）；replay 对齐（|Δlogprob| 分布）。
- **噪声地板 + MIE：** 数值地板 = replay vs vLLM logprob 差与 rank 阈值敏感性；统计单位 = 题，bootstrap CI。有意义 = 配对差 CI 不含 0 且量级足以改变“是否值得做 E03/受控训练”的选择。无预设“瓶颈”ρ 阈值。
- **混杂审计：** 同轨迹、同分布、同 mask 控制 objective；教师轨迹差异只作分布观察（长度、格式、p_a 都不同，按 p_a 分层报告）；全对/全错、截断、解析失败透明报告；跨模型/跨词表因果不做首轮主张；SNR 的 batch 口径差异见读数。
- **决策表（跑之前写）：** 单 token 不变量失败→修实现；组级差异稳定→看抵消/真实参数梯度决定 E03；只有分布差异→限定归因；teacher 非目标行 SNR ≫ rl 且接近 ce_onpolicy→I04 机制成立，提请人审受控小训练；三者 SNR 无差→I04 放弃；无信号→报告精度与不确定性、交人审；不确定→按组级 CI 增加同一条件的题目，不盲扫模型。
- **算力预算：** smoke 8 题×4 条；主跑 128 题×8 条 rollout（vLLM 单卡，预计 <1 GPU·时）+ replay/head 梯度累加（单卡，预计 1–2 GPU·时）。**实际：** 见结果。

## 结果
运行中。
