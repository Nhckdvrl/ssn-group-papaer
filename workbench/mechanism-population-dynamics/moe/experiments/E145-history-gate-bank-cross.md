# E145：共同学习历史稳定了什么——共同接收者的 gate × expert bank 交叉（2026-10-26）

- **状态：** DONE（2026-10-26）；13个交叉变体+teacher、全部四donor完成。下文保留运行前协议，实际读数见结果。
- **类型：** PILOT；复用既有终点的推理与诊断，不训练新模型。
- **对应：** [C09](../../CLAIMS.md)、[P27 / P28 / P29](../../PAIN_LOG.md)。推进“共享起点留下的稳定性，体现为当前路由、专家兼容性，还是二者配套”这个问题。
- **授权与范围：** 用户 2026-10-26 已选定当前主线并要求整理上传、设计初步实验；本卡执行这项设计授权，不重复请求批准。旧暂停记录保留其历史含义；本卡不恢复头线、不启动旧 E143、不自动排训练。
- **问题（一句话）：** 将 E139 独立随机路由组 R 与 E142 共享随机路由组 S 的终点专家，交给同一个真实接收者 gate 调用后，S 的较低组件变异是否仍体现为较高的预测兼容性？
- **阳性对照：** 已知四格交互、joint-permutation、self-swap 与 donor native 对角，见 §6。
- **噪声地板 + MIE：** 固定新 batch 的 BF16/Top-k/归约与重复前向地板；不设恢复率或任意科学准入线，见 §6。
- **决策表（跑之前写）：** 共同 gate 后的差异、预测兼容性及 donor 异质性分别更新解释，见 §7。

> **2026-10-26 执行前补充（尚无新模型读数）：** 用户本轮明确恢复 MoE 科研执行；推进 C09/P27–P29。原 13+teacher 条件、四个 donor、同一接收者、既有 calibration map、64 序列和 2 GPU·时包不变。新 driver 与 E144 共享输入/数值组件，但分开预算和结果。原物理 gate 行先 softmax/Top-k，再按锁定 map 解释公共槽位；按 gate 的原物理行顺序累加，确保 donor native 对角的 BF16 语义。训练侧预检用 E135 原 train batch0，包含 self/joint-permutation、四 donor native 对角及预测指标。只问终点兼容性，不声称训练轨迹或普遍历史效应。
> 同一批实际组件同时重算 R/S 的 native C/V，再与共同 G_A 下的 C/V 对照；不额外增加模型前向，避免以旧完整 held 的统计代替新子集的 native 差异。
> 理论接口审计仅作 CPU 已知答案：核对完整 softmax 后截断且不重归一时的 router 梯度，与 Top-k 内归一的差别。固定合成 logits/常数输出及 tiny HF 块，不用研究输入、不变更训练，不作为新机制证据。

## 1. 为什么现在做：把一个有信息量的终点问题先问清

[E142](E142-shared-random-router-cohort.md) 已观察到本有限 cohort 的 actual 组件变异较 R 低，但 actual 组件同时包含支持集、门值和专家输出。低变异不能直接改称“语义分工更一致”，也没有证明早期梯度同步、后期共同漂移等时间机制。

本卡选择一个共享的真实接收者，把 router 与完整 expert bank 交叉使用。它让“当下门值与支持不同”的直接作用，与“换到共同调用条件后，专家是否仍更兼容”得到一次可解释的区分；每个交叉格都是合法的单一 Top-8 模型。自由 gate 的贡献向量逐项拼接通常不对应这样的模型，本卡不采用这种拼接。

竞争解释在运行前保留：

1. S 的差异进入了接收者调用下的专家函数，因此换同一 gate 后仍较一致、移植代价较小。
2. 原差异主要来自各自 native gate 的支持或权重；换同一 gate 后显著缩小。
3. gate 与 bank 各自都变了，但配套可实现相近总体函数；交叉破坏配套产生后果。
4. 组件几何差异较大，但本次真实预测对它不敏感；较低几何变异未必带来重用收益。
5. 观察依赖这一份共享随机 gate、seed1 接收者、对应规则或某个 donor，不能直接推广。

## 2. 设置与已有资产：只有初末权重，不假定中途轨迹

依据源提交 `15b9b1bf78c9c60e32250434de4997e17cbf28f8` 的训练脚本和归档清单，E135/E139/E140/E142 保留 `initial.pt`，训练中覆盖同一 `checkpoint.pt`，归档终点为 step4096。九次 `evaluations` 是损失标量事件，**不是九份中间参数快照**。本卡只需要终点；不能据此还原中途 router、组件内容或协方差。

| 符号 | 既有来源 | 本卡用途 |
|---|---|---|
| A | E135 seed1 step4096；R/S 共同复用的同一个完整模型 | 唯一共同接收者与预测参考 |
| R0、R2 | E139 seed0/2 step4096 | 独立随机 gate 训练历史的 donor |
| S0、S2 | E142 seed0/2 step4096 | 共享 seed1 随机 gate 训练历史的 donor |
| teacher | 原生公开 OLMoE，原第 9 层块 | 同一输入上的外部拟合参照 |
| T、F | E140 共同 teacher gate 可训练、E138 teacher gate 固定 | 已有背景事实；首轮不新增这两组的完整交叉网格 |

R0/S0、R2/S2 各自具有配对的原始专家初值与 RNG，S 的初态仅更换 gate。R/S 的 seed1 整模型相同；不能把它们当独立 cohort，也不能把三对学生当三个独立训练重复。四个 donor 全保留，不按 native 性能、覆盖或移植结果筛选。

资产入口为 [ASSETS.md](../ASSETS.md)、[E139 archive manifest](../results/e139/archive_manifest.json)、[E142 archive manifest](../results/e142/archive_manifest.json)，以及其中引用的 E135 seed1 文件。执行前按 manifest 解析实际路径并核验 checkpoint/tensor SHA，不假定归档根目录下就是 checkpoint。当前卡片核对的是仓库记载，不表示已经访问计算节点上的权重。

## 3. 固定共同坐标与 13 个合法模型

### 3.1 对应规则

沿用 E139/E142 的 **final actual-component 未中心化平方距离 Hungarian → seed1**，校准人口仍为原 training Hcal8192。读取已有 `source_to_seed1` 映射及源 SHA，在新 held 读数出现前锁定，不用 held 挑对应、不重新优化 gate、gain、温度或旋转。

设 `m[j]` 将 donor 原专家 j 映射到 A 槽位 e。接收者 e 槽读取 donor 的 `j=m⁻¹[e]`：**donor 的专家槽与 gate 行必须同时按同一个逆映射重标**，否则会破坏 donor 原有 gate–expert 身份配对。

实际执行应保留原生 tie-break / 调用顺序语义：若直接重排张量改变 tied logits 的 Top-k 选择，先在原物理行中完成同一个 native softmax/Top-k，再将选中的行号映射到共同坐标，是可采用的等价编号实现。所有此类处理必须记录，并在 native 对角复现中验证；不把编号重标的伪影算作职责差异。

这是预先选择的一套共同坐标，既不是独立的语义标签，也不穷尽全部对应。可保留 physical identity 下的组件摘要作为参照；首轮不为另一套映射再开整套预测网格。

### 3.2 四格定义

写 `G_A,B_A` 为 A 的 gate/bank，`G_d,B_d` 为共同坐标下 donor d 的 gate/bank。这里的 bank 指全部 64 个专家。

| | A bank `B_A` | donor bank `B_d` |
|---|---|---|
| A gate `G_A` | `Y_AA`：共同锚点 native | `Y_Ad`：共同 gate 调用 donor 全 bank |
| donor gate `G_d` | `Y_dA`：只换 router | `Y_dd`：donor native |

四个 donor 共用 `Y_AA`，因此是 **1 + 4 × 3 = 13 个唯一变体**。teacher 若不能复用 E144 中完全同输入、mask、模型和程序的参照，就独立前向一次，共 14 个核心条件。

各格只替换公开 OLMoE `model.model.layers[9].mlp`；prefix、downstream、tokenization、位置、mask 完全共同。所有模型均为 **64 专家全体 softmax → Top-8，不重新归一**，整段序列上执行，不能只修改一个目标 token。`G_A B_d` 与 `G_d B_A` 都有一个确定的合法 gate；不跨学生拼接各自不同 gate 下的贡献。

## 4. 输入与配对：共用 E144 的 64 条探索性序列

- 原人口是 Dolma held 的 512 条固定序列，每条 512 个计分位置，来源于 32 个文件；复用原 `TokenData.fixed_windows("held",512,91023)` 及 `held_window_hash` 验证原序列身份。
- **E144 统一按固定 SHA 排序选择 64 条，E145 读取其 `selected.json`，不自行再选。** 共计 32,768 个位置。Hcal8192 只提供既有对应，不参加 held 筛选。
- `selected.json` 记录原 sequence ID、source/file ID、token SHA、选择规则和规则 SHA、新冻结 batch ID/位置、attention mask、loss mask 与 token/target 对齐。64 条组成新的四个 B16 batch；完整保留每条序列的上下文，**不声称保留旧全集中的原 batch 邻居**。E144/E145 采用完全相同的新编组，在此编组重测 native 与数值 floor。
- 原 held 总体已用于已有探索，本卡是对新操作的前瞻设计，**不是新独立测试集上的确认**。报告子集实际覆盖的文件和来源，不能假定抽出的 64 条仍覆盖全部 32 文件。
- BF16 whole-model logits → FP32 log-softmax，mask、目标和分母与 E144 一致。后续若需要确认，可另留小型新确认集；不预先搭建多轮筛选或恢复门槛。

## 5. 读数：先看真实预测，再解释层内变化

### 5.1 主读数

对所有四格及 teacher 保存以下连续读数，先列每个 donor，再描述 R/S 两 donor 的配对差异：

1. 标签平均 NLL，交叉格相对共同 A、各自 donor native 的 NLL 差。
2. 相对**同一个 A 预测分布**的双向 KL；另列与 donor native 的双向 KL。所有字段明确参考方向，不能将不同参照的 KL 混成同一指标。
3. teacher 的 NLL，以及 teacher 与各格的预测 KL，用于说明原生拟合质量是否同时变化；不作为选种子或“函数恢复准入”依据。
4. 完整下游 NLL 的四格有限差分 `I_L = L_dd − L_dA − L_Ad + L_AA`。它描述此操作的损失交互，不自动等同协作强度、Fisher 项或最优模块化代价。

按实际覆盖的同一文件做配对 bootstrap，可沿既有 seed139/1000 次口径。区间只反映固定 donor、接收者、映射和输入样本下的输入不确定性；不称 seed 处理效应或共享随机 gate 总体置信区间。保留 R0↔S0 与 R2↔S2 两个对照，不用共享 A 伪增训练样本量。

### 5.2 层输出的直接代数对照

对相同隐藏态 H，以实际四格输出定义：

$$
\mathcal I_d=Y_{dd}-Y_{dA}-Y_{Ad}+Y_{AA},\qquad
Y_{dd}-Y_{AA}=(Y_{dA}-Y_{AA})+(Y_{Ad}-Y_{AA})+\mathcal I_d.
$$

报告三个差项的能量与两两交叉内积，不能把其能量各自除以总能量后当可加“责任比例”。理想共同点态函数下，`I_d = Σ_e(q_de−q_Ae)(f_de−f_Ae)`；实际 BF16 expert 子 batch 形状随 gate 改变，函数调用的数值实现可能略有不同。因此以实际四格有限差分为主；若计算右侧因子化检验，差额作为程序 floor 单列，不假装 bitwise 精确。

在共同 `G_A` 下，分别对 `{B_R0,B_A,B_R2}` 和 `{B_S0,B_A,B_S2}` 计算 actual 加权组件的等权有限 cohort 方差 `C`、FP64 组件求和的方差 `V`、`C−V`。每组按 1/3 权重，teacher 不作为第四学生；原始平方误差与 teacher 能量归一量分字段存储。这里 gate、支持和权重共同，剩余差异描述**此接收者调用下的专家兼容性**。

`C−V` 不是这四格自然预测代价的精确公式；尤其不能将原 R/S 自由 gate 的 `C−V` 当本卡 bank-only 或 router-only NLL/KL 的预测。原自由 gate 的 C/V 仅作背景参照。

### 5.3 解释读数

- 各 gate 的选中总质量 `s=Σq`、`Σq²`、选中权重归一后的集中度、与 A 的 Top-8 集合重叠；不把尺度和拓扑混为一个变量。
- 对 `G_A B_d` 的实际调用，分 donor-native support 内与 receiver-only 调用的计数/能量。新 gate 可能调用 donor 原来不常用的区域；这类 off-support 兼容性属于本次真实移植，不等于纯语义内容差异。
- 每条序列、文件、来源的原始连续读数与实际覆盖。不在见到结果后删困难来源；样例分析如追加，单列 POST-HOC。

## 6. 阳性对照、噪声地板 + MIE、混杂审计

**阳性对照：** 新 driver 的交叉构造先用小型已知 gate/专家函数，验证预先构造的非零四格交互及 joint-permutation 恒等；预测指标用可手算的非相同分布核对 KL 双方向、NLL 和 mask。真实模型对照包括 A 的 self-swap、donor joint-permutation 后的 native 对角，以及 teacher 与 A 的自然预测差异。小型对照只证明工具能测到已知变化，不充当科学结果。

**噪声地板 + MIE：** 在新冻结 batch 上重复 A 前向，复现四个 donor native 对角；分别记 full logits/NLL/KL、gate supports/weights、实际 BF16 output 与 FP64 sum 的差额。gate-only 格的 gate hash 对 donor，bank-only 格的 gate hash 对 A，全部 64 专家来源逐张量可追溯。若编号重标或实现错误破坏对角，修复读出后再解释，不筛掉 donor。

本 pilot 不设任意 MIE、teacher 恢复线、相似度准入或“超过 2×noise 才继续”的科学门槛。对判断有意义的是：换共同 gate 后原差异如何改变、是否伴随真实预测兼容性差异、差异是否依赖 donor/来源，以及量级相对实现 floor 和 native 之间差异如何。若分辨率不足，报告尚不能区分及具体不确定性；不自动判线存亡。

| 混杂项 | 本卡处理与剩余边界 |
|---|---|
| 不同输入、下游或预测参照 | 已控制：E144 同一 selected/batch/mask，公共冻结 prefix/downstream，共同 A 参考，teacher 辅助 |
| gate 与专家身份对应 | 已控制构造：同一 cal map 同时作用 gate 行与专家槽；对应最优性/语义性未保证 |
| 函数拟合质量 | 全报 native NLL/KL 与 teacher 差异，不筛选；不同终点质量仍是解释变量 |
| 调用支持与门值 | bank-only 使用共同 gate；router-only、support/gain 读数辅助解释，不声称彻底分离训练机制 |
| 支持外调用 | 单列覆盖和能量，不排除；结论限共同接收者的自然调用 |
| 共享 seed1 与单个共享 gate | 未控制总体泛化；明确有限 cohort，两个配对 donor，输入 CI 不等于 seed CI |
| 中间时间机制 | 本卡不检验；只有 initial/final 参数，不能用损失日志冒充轨迹 |
| BF16、Top-k ties、batch 改编 | 新编组固定且两卡共同；重复、native 对角和归约 floor 实测 |

## 7. 决策表（跑之前写）

| 可能结果 | 如何更新认识与后续问题 | 不推出 |
|---|---|---|
| S 在共同 gate 下 C 较低，bank-only 的 KL/损失代价也较低 | 当前 native 门值/支持不足以单独解释稳定性；历史差异进入了此接收者下的专家兼容性。后续才考虑旋转接收者 | 普遍语义一致性；共享任意随机 gate 均如此 |
| native C 差异明显，共同 gate 下差异明显收缩 | 当前 gate/支持/门值对原差异很重要；先解释路由组织而不是直接讲内容趋同 | 只由一个 gain 标量造成；专家无历史影响 |
| bank-only/router-only 有损，两个 native 各自较好，四格交互较大 | gate–bank 的配套影响实际使用；进一步问共享历史稳定的是哪种配套 | 优化器直接最大化跨 seed 负协方差；普遍性能—模块性定理 |
| 层内差异大而共同参考 KL 较小 | 本次操作的几何差异未同等传到预测；原 C 下降未必有明显重用收益 | 已证明全局下游零空间或无用噪声 |
| KL 变化而平均 NLL 变化小 | 分布变化与标签平均损失不同，两个读数都保留 | 功能完全相同 |
| 只一个 donor/来源有差异，或两个配对方向不同 | 记录范围，检查对应、覆盖和 native 质量；降低普遍性解释，不删反例 | 从幸存 donor 提炼统一规律 |
| 交叉后果普遍小、或者现有分辨率无法区分 | 记录此接收者的可交换性范围或未决状态；回到具体竞争解释判断是否追加 | 自动关线、自动加训练网格、任意恢复门槛 |

所有分支均只更新证据与下一问题，不自动升 C09 等级、不自动开训练。T/F 交叉、另一共享随机 gate、接收者旋转或带稀疏参数快照的新训练，均是有结果后才考虑的条件分支。

## 8. 实现入口与输出约定（尚未实现）

需要新增一个独立 E145 driver；本卡不声称脚本、命令或输出已存在。现有源码可复用其 API/定义，但不能直接拿旧实验的预算 ledger、固定 512 行数组或旧 `preflight` 当新实验流程。

| 用途 | 已有源码入口 | 新 driver 需要适配的部分 |
|---|---|---|
| state 与公共 tuple-MoE 接口 | [`e135_common.py`](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e135_common.py) 的 `bank_from_state` / `PublicStudent`；[`e135_capture.py`](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e135_capture.py) 的 `MeasuredPublic` | 独立加载 source state、joint map 与 gate/bank 组装；保留 `(output, router_logits)` 接口 |
| 自然预测 | [`e142_readout.py`](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e142_readout.py) 的 `natural_predictions` | 读取 selected 的 64 条和新 batch；13 条件流式运行；共同 A/teacher 参照，不沿用旧全量数组形状 |
| 输入不确定性 | [`e139_readout.py`](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e139_readout.py) 的 `input_summary` | 实际覆盖文件的成对统计；donor 0/2 单列，不把共享 A 当独立重复 |
| actual 组件、对应与 C/V | [`e139_components.py`](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e139_components.py) 的 `measure_batch` / `dense_components` / `ratios`，既有 final calibration | 加入共同 gate 的组装状态与四格输出；复用定义但不从旧 NPZ 推造新的组件向量 |
| 参数保存口径 | [`e135_train.py`](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e135_train.py)、[`e139_train.py`](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e139_train.py)、[`e140_train.py`](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e140_train.py)、[`e142_train.py`](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e142_train.py) | 只解析 existing final；不调训练入口、不假定 checkpoint512 等文件存在 |

建议的新 driver 边界是：`load_and_verify_sources` → `load_selected` → `joint_relabel_donor` → `compose_gate_bank` → `evaluate_cross_grid` → `aggregate_paired_results`。这些名字是接口设计，不是已存在的可执行 API。每一步的 source SHA、输入/输出 schema 和 precision 要进入 manifest。

计划输出位置为 `moe/results/e145/`；大数组与权重留原资产区，只提交清单和可审查摘要：

- `manifest.json`：source commit、driver/dependency SHA、所有 checkpoint/tensor/gate/bank SHA、step4096 身份、map 与方向、公共模型/prefix SHA、selected SHA、mask/batch/precision、13 条件身份、资源配置。
- `selected.json`：E144 选择结果的逐字复用或指针与 SHA；原序列身份、新 batch、mask 和计分位置可核对。
- `controls.json`：已知答案检查、self-swap、四 donor native 对角、重复噪声、tie/归约 floor、状态未修改证明。
- `prediction_rows`：variant、donor、gate_source、bank_source、reference/direction、sequence/file/source、位置数、NLL/KL 和对照差；汇总 `summary.json` 明确输入 CI 的条件范围。
- `layer_moments`：actual 四格有限差分、能量/交叉内积、共同 gate 的 C/V、raw 与 normalized 单位、support/gain/receiver-only 覆盖及分母。
- `budget.json` / `artifact_manifest.json`：独立 E145 支出，成功、失败、检查、I/O 和未完成阶段全部记账；大文件路径、大小、SHA 与重建入口。

无需保存 13 套全词表 logits，或所有模型×64 专家×全部位置×hidden 的稠密向量；按 batch 缓存 A/teacher 预测、流式累积必要的 per-token 指标与二阶统计即可。运行所需是终点权重、原始 token 源及元数据；不要只因旧训练 preflight 要求而重建约 71.7GB 的 H/Y 训练 cache。

## 9. 算力预算与执行边界

- **核心工作量：** 32,768 计分位置 × 13 条件 = 425,984 prediction-token；teacher 独立一次时 ×14 = **458,752 prediction-token**。这是计分和前向工作量的参照，不包括重复、对角验证及组件采集开销。
- **硬件组织：** 优先节点内已有资产的一张适用 GPU；公共模型与 5 个唯一学生状态流式换入。先核查显存/I/O，不假定所有权重同时驻显存，不需多节点通信或新训练。
- **初步估算：** 在权重本地可读、流式实现可用的条件下，暂估 **0.25–1.5 GPU·时**；尚未 profile，不能当承诺或实际耗时。先用首个冻结 B16 batch 记录实测显存、时间和数据搬运，不据其结果改选 donor/输入/读数。
- **硬支出上限：** 本 pilot 首次资源包 **2 GPU·时**，所有实现检查与失败尝试累计；到限保留 partial 和未完成项，不自动扩容。这是支出控制，不是科学效果 gate。
- **实际：** 未运行；无 GPU·时、耗时或显存实测。没有运行命令，因为新 driver 尚未实现。

## 结果（2026-10-26，四donor全部完成）

| donor | bank-only NLL−自身native | KL(donor native∥bank-only) | NLL四格交互 |
|---|---:|---:|---:|
| R0 | .007636811 [.004573401,.011486138] | .012109481 | −.013594592 |
| R2 | .006770084 [.002919748,.010567328] | .011316157 | −.013388801 |
| S0 | .001888062 [.000492435,.002954188] | .004316824 | −.004659671 |
| S2 | .002074262 [.000657169,.003185173] | .004833157 | −.004723395 |

- **主读数：** 两配对平均 S−R 的 bank NLL代价差（各自native基准）=**−.005222285**，paired文件CI **[−.008375402,−.002511591]**。相对共同A的bank-only NLL平均差−.004638926 [−.007278010,−.002283251]；seed2这个A基准差的区间跨0，保留该不确定性。两配对KL点估计均同向；原始各格/双向KL/teacher参照全见summary，不筛donor。
- **同一输入下的几何：** native C_R/C_S=.073051106/.043635659；共同G_A下=.055989699/.037892022，S−R=−.018097677，文件CI[−.019563636,−.016975359]。共同gate下V_R/V_S=.028586863/.019421125；不能把原自由gate的C−V当移植损失公式。初始组织的影响进入了此接收者调用下的bank兼容性，不能只由当前门值/支持的直接测量差吸收。
- **仍竞争的解释：** S donor与A的matched Top8重合≈.785–.804，R≈.595–.606；共同接收者调用donor原native支持外的槽数分别约1.57–1.72和3.15–3.24/位置。兼容性包括支持外调用，尚未区分语义内容趋同与训练覆盖；没有据此恢复时间轨迹。A是这一份共享起点的参与者，只验证一个接收者与两个expert-init配对。
- **四格：** 所有native预测NLL相近但交叉代价存在，gate/bank配套对实际使用有后果；I_L是该操作的损失交互，不直接称协作强度或训练机制。
- **对照：** A self/repeat、四donor保持物理Top-k与累加顺序的joint对角，layer/logp差全0；全部参数只读检查通过。22文件簇的输入区间只对固定donor/接收者/映射成立，非共享随机gate总体处理效应CI。
- **执行与结果：** `CUDA_VISIBLE_DEVICES=1 ~/.venvs/mechpop/bin/python moe/scripts/e144145_run.py preflight/evaluate --experiment e145 --physical-gpu 1`（分别调用）；统计`... e144145_analyze.py e145`。[summary](../results/e145/summary.json)、[manifest](../results/e145/manifest.json)、[floors](../results/e145/floors.json)、[设备修复审计](../results/e145/device_visibility_audit.json)、[图](../results/e145/figures/recombination_and_history.png)。raw在`/home/xiang/mechpop_cache/e145_history_cross/batch00–03.npz`。
- **算力：** **361.747 GPU秒（.10049 GPU·时）**，包括两轮训练侧预检；首次CUDA可见卡导入顺序错误只影响预检物理放置，held前修复并核对UUID，首次对照和全部成本保留。峰值allocated 46.571GB。没有丢弃条件或新训练。
- **主张与决策：** 新增限定C11=L1；C09保持L1。配套后果与历史相关的兼容性已值得进入E146固定粒度检验；未自动扩接收者/模型/训练网格。POST-HOC：无新增科学切片；raw能量恒等式是工具复核，不是独立L3审计。
