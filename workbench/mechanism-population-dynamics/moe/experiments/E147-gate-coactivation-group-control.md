# E147：分组预测收益来自 gate 共激活，还是跨学生函数配套（2026-10-26）

- **状态：** DONE；E146完成后新提出、运行前预登记；12个gate-only bank全部运行并完整统计。由`tools/process/new.py experiment mechanism-population-dynamics gate-coactivation-group-control`生成编号，按主题移动至moe。
- **类型 / 对应：** PILOT / MEASUREMENT；C10/C11/P31，复用现有F三终点，无训练。
- **问题：** E146的Γ分组优于随机同大小分组，是否仅因保留了当前gate的强共激活/门值关系，而不需要跨学生专家函数信息？
- **设计修订的科学理由：** E146随机粒度对照不能区分这个解释。增加一项更强的gate-only comparator，能改变“哪些变量决定可组合的计算单位”的判断；不以维护Γ分组叙事为目的，不加多种图/算法直到胜出。

## 运行前固定协议

1. **相同资产与输入：** E144/E146的3个F终点、物理identity、teacher gate、64序列/32768位置/22文件簇、四B16 batch、同μ预测参考、完整下游。所有SHA/precision合同不变，复用E146的4个来源基础向量×3循环，不新抽样。
2. **唯一新分组：** 仅training Hcal8192；以共同gate原生完整softmax→top8→BF16 applied weights构建Q，未选为0；图A=QᵀQ/N，完全不使用专家输出/Γ。对−A使用E146同一个三轮平衡贪心算法，64×1→8×8、同字典序ties。锁定一次，不调加权、阈值或组大小。
3. **在held前锁组：** 保存A、合并轨迹、8组、源码/输入/来源SHA。新组锁定后才允许读旧held Γ的cut；held Γ不用于定组。新组实际12 bank全部运行，48个B16完整预测forward；另计必要prefix/局部组件/μ参考。
4. **比较：** 主比较gate-only组减E146 cal-Γ组，沿完全相同4来源basis和输入成对；两者相对完整学生的ΔNLL、真实KL(pμ∥pZ)、FP64/native层风险全部列。三个旧随机分区只提供已固定背景，不新增随机对照或筛分区。
5. **统计单位：** 来源MC=4，成对文件bootstrap=22簇；1000次，沿E146的146001/146002两种重采样。报四basis逐项、MC SE与交叉区间，不称seed总体或任意随机分组总体CI。

## 阳性对照

- tiny已知共激活块图应选对应配对；组覆盖64槽位、每组8、同组完整来源、三循环精确一阶均值；gate hash不变。
- 沿E144/E146通过的同源/copy/joint与重复地板；重放μ的逐token NLL以及原生层端点与E144逐位相同才解释新结果。
- 完整参数/prefix只读检查；实际组件逐位等于相应原学生来源。

## 噪声地板 + MIE

沿现有BF16 native/FP64路径地板；新增项保持同程序，不把舍入/MC当机制。无任意效果准入阈值；关键是gate-only是否已解释E146跨输入预测收益，以及比较在四basis/真实KL/NLL上是否一致。输入CI非训练CI。

## 决策表（跑之前写）

| 观察 | 更新认识 |
|---|---|
| gate-only与Γ组接近，均优于随机背景 | 共激活/门值结构已是较充分解释，不能将E146认领为新发现的函数内容联盟 |
| gate-only的cut/预测都明显较差 | 当前gate的二阶图不足以解释该有限群体的配套，跨学生函数信息增加预测价值；仍非天然/最小语义模块 |
| gate-only几何较差但预测相近，或反向 | 组边界受读出度量影响；分别报告，不能从欧氏图直接定义计算单位 |
| 四basis方向混合或区间分辨不足 | 保留不确定性，不追加更多图/粒度/来源直到显著 |

## 算力、来源与归档

- 一张已空闲GPU；既有环境`~/.venvs/mechpop`。12×64×512=393216新增预测token条件，另计4次μ与prefix/局部块。预计0.03–0.2 GPU·时，硬包1 GPU·时，独立ledger；峰值探索并发仍≤8卡。
- 计划源码`scripts/e147_gate_control.py`、`results/e147/`；raw耐久存储`~/mechpop_cache/e147_gate_group_control`。当前未实现、未运行。不得修改E146原预注册或其已完成结果；这是由E146结果引出的新前瞻实验，不将它倒写成E146的预设对照。

## 结果（2026-10-26）

- **主要对照：** gate-only减Γ组的标签NLL=**+.000004829**，交叉文件/来源CI **[−.000251039,+.000266366]**；KL差=−.000040128，区间[−.000210918,+.000161346]。四basis的差异正负都有，不追加basis追求Γ胜出。
- **对随机背景：** gate-only减E146三个随机分区均值的NLL=**−.001252880**，区间[−.001684779,−.000888509]；KL=−.001545972，区间[−.001872329,−.001264599]。因此简单gate-only图也保留了大部分已观察到的分组预测收益。
- **原单位背景：** gate-only相对完整学生的NLL/共同μ参考KL增量点值约.000685789/.000718843；Γ组为.000680960/.000758970。gate-only分组与Γ分组不相同，但cut接近：train .004784413、held .005006960（Γ组.004796232/.004897035）。不能从未检出差异宣布严格等价或全体gate-only算法已穷尽。
- **科学更新：** 削弱“Γ已识别超出当前gate结构的内容联盟”解释；更简单的gate共激活/门值结构已是本例分组收益的较有解释力候选。E144的真实配套代价、E145共同gate下的历史兼容性差异仍成立。两类结果不等于已经复原形成机制、确定唯一计算单位或推广到原生全模型训练。
- **控制：** 同μ逐token NLL、三个原生层端点均与E144逐位相同；全部组件与来源一致、三循环均值和只读检查通过。组只用training Hcal与gate，完整held Γ在定组和新预测完成后才读取。
- **资源：** 106.941 GPU秒（.02971 GPU·时），峰值allocated31.199GB；一张卡、12新bank，无失败/丢弃条件、无训练。本轮E144–E147合计994.892 GPU秒≈**.27636 GPU·时**（含两轮预检）；峰值并发两张卡，完成后释放。
- **复核入口：** [源码](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/moe/scripts/e147_gate_control.py)、[groups](../results/e147/groups.json)、[summary](../results/e147/summary.json)、[manifest](../results/e147/manifest.json)、[budget](../results/e147/budget.json)。命令 `... e147_gate_control.py self-test`、`CUDA_VISIBLE_DEVICES=0 ... e147_gate_control.py evaluate --physical-gpu 0`、`... e147_gate_control.py analyze`。raw在`~/mechpop_cache/e147_gate_group_control`，SHA见manifest。
- **决策：** 采用原表“gate-only与Γ接近、均优于随机”的分支；本轮不再扩图/粒度/来源扫描。后续优先让该关系在自由学习gate或原生训练历史中接受前瞻检验。E147是结果后提出的新实验，绝不倒写为E146预设对照；此界限已保留。
