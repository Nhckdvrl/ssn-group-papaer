# E02 — Induction circuit across 10 independent Pythia-70M runs（2026-10-01）

- **状态：** DONE（2026-10-02；判定 = 情况 1，10/10 seed）
- **类型：** CLAIM-seeking measurement（D4 领域标准系统测量）
- **对应：** E01 结论 + P01/P03/P04；territory object（抽象层级）
- **问题：** 在 10 条独立训练历史上，induction 机制在哪一层可复现：头身份 / 层位置与因果角色 / 算法（prev-token → induction 的组合）/ 形成顺序 / 时间？
- **Agent 决策（2026-10-01，代替人审；人可事后否决）：** ① 群体对象 = “previous-token 角色 + induction 角色”的电路，而非 parent top-R1 头列表（E01 POST-HOC：最强因果成分是 L2 prev-token head）；② 读数改为对重尾稳健（P04）；③ 消融主方法 mean、副方法 zero，弃用 parent BOS-V（P03）；④ timing 只记录不作主读数（网格 512→1000 太粗，Howe 2026）。

## 设置
- **模型：** `EleutherAI/pythia-70m`（seed 0）+ `pythia-70m-seed1..9`；全部 checkpoint 先过 R0 张量审计（manifest）。
- **checkpoint（16）：** 0, 128, 256, 512, 1000, 2000, 3000, 4000, 6000, 8000, 16000, 32000, 64000, 100000, 130000, 143000。
- **实验单位：** seed（n=10）。prompt 层面的不确定性用 bootstrap 单独报告；不把 prompt 数当 n。

## 读数（每个 seed × checkpoint）
- **S_ind[h]**：parent induction score（`find_induction_heads`，seed 42，1000 条）。
- **S_prev[h]**：Olsson previous-token score（Pile 64 条 × 256 token，注意力 i→i−1 的均值）。
- **行为 B（held-out，稳健版 R3）**：500 条 [BOS]+r1..r50+r1..r50，token 从 pool 均匀抽（pool = pile-10k 计数 ≥50 且不在最常见 500 个之内，23,682 个；seed 12345）。
  - **CL（copy loss，主）** = 各序列第二段 loss 中位数的均值；**FL** 同理（第一段）；**ACC** = 第二段 top-1 准确率（次要）。
- **单头因果图**：48 头 × {mean, zero}，ΔCL_h、ΔACC_h。
- **角色定义（按分数，不按因果效应，避免循环）：** prev 角色 = S_prev ≥ 0.5 的头；induction 角色 = S_ind ≥ 0.2 的头。组合消融（mean）：prev 角色全体、induction 角色全体、两者并集；对照 = 20 组同样大小、排除两种角色头的随机组。
- **算法检验（K-composition 依赖）**：mean 消融 prev 角色全体后，重算 induction 角色头在重复序列上的 induction 注意力（与 S_ind 同定义，但用本读数的 token 张量），报告比值 ablated/clean。
- **R2（次要）**：只在 1000 / 8000 / 64000 / 143000 上，clean 与 mean 消融 induction 角色 / prev 角色，N=1000。

## 衍生量
- **集中度**：post-emergence 时单头 ΔCL 最大值 / 并集消融 ΔCL；达到并集效应 80% 所需的最少单头数（按单头 ΔCL 排序累加，仅作描述）。
- **层位置**：每个角色的头所在层。
- **形成步**：prev 角色首次出现（max S_prev ≥ 0.5）、induction 首次出现（max S_ind ≥ 0.2）的 checkpoint。

## 阳性对照 / 噪声
- seed 0 应复现 E01 canonical：L2H1 为 prev 角色、第 3 层 induction 头；emergence 在 (512, 1000]。
- 噪声地板：500 条序列 bootstrap；随机组分布；step 0 / 128 的所有效应应 ≈0。

## 决策表（跑之前写）
- **情况 1（角色稳定、成分不稳定）**：≥9/10 seed 在所有 post-emergence checkpoint 上都有：一个 prev 角色头单独 mean 消融使 ΔCL ≥ 并集效应的 50%，induction 角色头位于其后的层，且 K-composition 比值 ≤0.5 → 第 3/4 层（因果角色 / 算法）可复现。下一步：在稳定的电路上测量**哪些量在 seed 间真正变化**（集中度、后期角色获取、退化），检验它们是否构成 population law，并查最新 prior。
- **情况 2（route 差异）**：≥2 个 seed 行为相近（post-emergence CL 差 <1 nat）但没有单一 prev 瓶颈（最大单头 <30% 并集效应）或角色层位置不同 → 先排除 artifact / 抽取失败，再加控制（换 token 池、换消融方法），然后评估 functional consequence（R2、后期退化）。
- **情况 5（单一异常 seed）**：只 1 个 seed 不同 → 查 artifact、R0、提取；不围绕它做故事。
- **不确定**：结果依赖消融方法（mean 与 zero 方向相反）→ 报告为测量依赖，不作机制结论。

## 算力
10 × 16 = 160 次评估，每次 ≈4–6 min；≈12–16 GPU·h；≤8 卡。

---

## 结果（2026-10-02；不改上面的内容）
**实际算力：** ≈7 GPU·h（160 次评估 × ≈2.5 min；fvcrc20 GPU0/1/3 + fvcrc10 GPU0–3）。R0：171 个 checkpoint 全部 accepted。
**结果文件：** `results/e02/<seed>__step<N>.json`、`summary.json`、`summary.md`。

### 抽象阶梯（10 个独立 run）
| 层级 | 结果 | 可复现？ |
|---|---|---|
| L1 头身份 | prev-token 头：L2H1 / L2H7 / L2H6 / L2H6 / L2H4 / **L3H5** / L2H1 / L2H4 / **L2H2→L3H1** / L2H5；induction 头集合各不相同 | ❌（且层内编号本就是对称性） |
| 层位置 | 8/10 为 “L2 prev → L3 induction”；seed5 整体下移一层（L3 → L4）；seed8 在训练中把 prev 角色从 L2 交接到 L3，induction 在 L4 | 部分（8/10）；**相对顺序**（prev 层 < induction 层）10/10 |
| 因果角色 | 10/10：每个 post-emergence checkpoint 都有单一 prev 头，单独 mean 消融 ≥ 并集效应的 50%（多数 0.85–0.98；seed8 末期 0.52） | ✅ |
| 算法（K-composition） | 消融 prev 角色后 induction 头注意力降到 clean 的 3–15%（10/10，全部 post-emergence checkpoint） | ✅ |
| 形成顺序 | prev 角色先于或同于 induction 出现（seeds 3、7 在 step 512 已有 prev 头；其余同在 1000） | ✅（受网格限制） |
| 时间 | induction 全部在 (512, 1000] 出现 | 网格分辨不出差异 |

**判定：情况 1（角色 / 算法稳定，成分不稳定），10/10。**

### 意外的群体结构（不在预注册决策表中，标 POST-HOC 发现）
- **后期复制能力退化在 seed 间差 25 倍**：late（≥32000）CL 均值减去最好值：0.18（seed9）…4.67（seed2）；seed2/seed7 的复制准确率从 0.88 跌到 0.3–0.5。自然文本 loss（R0 NLL）在各 seed 间几乎相同（step 64000：2.67–2.69）。
- **退化幅度被“拮抗头”预测，不被电路指标预测**（n=10 seed）：拮抗量 = 单独 mean 消融后 CL 下降 >0.5 的头的下降之和，几乎全在第 0 层；Spearman ρ(退化, 拮抗量)=0.84（p=0.002）；ρ(退化, K-comp)=−0.38、ρ(退化, max S_ind)=−0.50、ρ(退化, prev 组效应)=−0.28（均 p>0.1）。
- **威胁：** 循环性（退化越大，可回收空间越大）；mean 消融对第 0 层头是否是分布外干预（P03）；是否只在随机 token 序列上存在。→ E03 专门检验。

**主张变化：** 新建 C01（L1，见 CLAIMS）。
