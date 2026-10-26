# MoE：任务、学习历史与专家职责的可组合性

**状态（2026-10-26，用户要求持续推进）：** E144–E147完成；E148已通过CPU恢复校对和原生单卡精度/显存预检，正在进入完整网络次序分叉；此前成本.27636 GPU·时单列，主实验held/分叉结果尚未获得；探索并发上限8卡，头线仍CLOSED，其他ACTIVE分配不变。

**E148单卡实测：** 6.919B参数全部可训练，原生BF16/FP32 master shader前向差0；确定性程序峰值56.319GB、约6.19秒/更新、optimizer状态39.90MB。相同两次更新的全参数抽样hash一致、loss差0；已保留旧非确定性地板和RoPE恢复修复。固定全实验核心训练预估3.36 GPU·时，执行资源单列5 GPU·时。共同parent warm32完成（held NLL=2.95818），A/B/A-repeat已从同一模型/optimizer/buffer/RNG启动；主次序处理结果待完成。

**持续维护约定（用户2026-10-26）：** 本页作为唯一简明研究说明。每批获得完整结果后，先更新“数字与区间→竞争解释→主张范围→下一项决定”，链接实验卡/源码/原始文件，保留阴性和技术失败记录；随后继续已授权的高信息量研究，不以一批实验结束或整理文档为停点。README≤200行，详细过程留在原卡、results与logs。

**E148运行状态：** 三个分支的parent完整参数/buffer均逐项hash一致；最近更新步为A=160, B=160, A-repeat=160（终点672）。尚在执行预设处理/后缀，主效应不根据中途loss挑选。

## 1. 母问题与当前窗口

> 在相同任务约束下，哪些专家职责和配套由任务/路由结构约束，哪些由训练历史选择；这些差异何时改变实际预测与组件重用？

当前固定原生OLMoE的一层输入/目标/下游，只是拆开因素的窗口；它不是独立全模型预训练。方向、历史证据与数学范围见 [RESEARCH_DIRECTION](RESEARCH_DIRECTION.md)。E120–E142的整体脉络见[逐项索引](experiments/INDEX.md)，所有旧结果保留。

## 2. 本轮真正增加的认识

| 实验 | 直接结果 | 对科学解释的更新 |
|---|---|---|
| [E144](experiments/E144-fixed-gate-recombination.md)：固定gate拆来源 | 24重组相对完整三学生，ΔNLL **+.002061**，交叉95%CI[.001759,.002517]；共同μ参考ΔKL **+.002441** [.002123,.002820] | 配套差异有真实预测后果；绝对损伤小，不只是欧氏求和恒等式，也不是能力崩溃 |
| [E145](experiments/E145-history-gate-bank-cross.md)：同一接收者交叉 | 共同gate下C_R/C_S=.055990/.037892；两配对的bank移植NLL代价S−R **−.005222**，文件CI[−.008375,−.002512] | 当前gate的直接读数不足以吸收历史相关差异；剩余体现在该接收者下的bank兼容性，含支持外调用 |
| [E146](experiments/E146-grouped-recombination.md)：训练Γ定组 | 一个8×8分组的ΔNLL=.000681，三个随机同大小组为.001690–.002151；Γ−随机均值 **−.001258** [−.001714,−.000793] | 保留哪些专家的共同来源有跨输入预测意义，超出纯组大小效应 |
| [E147](experiments/E147-gate-coactivation-group-control.md)：新增强gate-only对照 | gate-only−Γ的NLL差 **+.0000048** [−.000251,.000266]；gate-only也优于旧随机均值 | 未检出Γ的额外收益；不能将E146包装成发现超出gate结构的函数内容联盟 |

E144为8个独立来源basis×3平移；E146/E147为4 basis×3平移，全部保留。均是同64完整序列/32768位置/22实际文件簇，旧held探索输入；文件/来源区间不代表训练seed总体。E145仅2个expert-init配对、一个共享起点与共同接收者，R/S共享同一个trained seed1。

更有支持的假说是：**路由组织提供可保持配套的有效边界，学习历史还影响同一接口下学出的专家函数是否兼容。** 这仍是受控证据支持的假说；尚未恢复形成动力学、证明唯一或最小计算单位、语义自包含模块、或原生全模型训练规律。Gamma分组没有胜过强gate-only对照，是本轮应当保留的信息。

## 3. 对照与证据等级

- teacher copy、三同源组装、四donor联合重标native对角、重复前向均逐位差0；组合实际BF16组件逐位等于来源。主效应按实际BF16程序报告；FP64sum cast路径KL约.00036–.00037另列为数值参照，两者不能直接线性相减。
- 原生块、全部学生、prefix/downstream只读检查通过；完整Γ满足C/V恒等式，并与E144同人口精确重合。raw的不同目标风险恒等式与四格能量关系另经CPU复算。
- CUDA可见卡在库导入后设置会沿用缓存映射，首次预检发现后修为导入前设置+UUID核对。held之前修复，首次记录/全部成本保留于[E147之前的设备审计](results/e145/device_visibility_audit.json)。
- [CLAIMS](../CLAIMS.md)：新增C10–C12均 **L1**；C06–C09数字和等级不变。没有宣称独立L3校对或论文就绪。[PAIN_LOG](../PAIN_LOG.md)保留原判断及本轮范围更新。

## 4. 下一步的研究判断

E144–E147已经区分真实配套、当前gate读数、历史兼容性以及分组的强竞争解释；现在按[E148](experiments/E148-native-checkpoint-order-forks.md)继续推进原生学习窗口：同父完整网络、相同batch集合次序pulse、长共同后缀及同流repeat，保存参数/路由快照。最重要的缺口是：**当gate本身能持续变化、模型以真实语言目标继续训练时，哪种配套边界还能保持或形成？**

当前E148是带稀疏参数/路由快照的原生checkpoint分叉：同父、同曝光多重集合与共同后缀，只改变早期次序，前瞻读gate结构和合法重组预测后果。它能把终点兼容性接回形成过程；执行前需审计可单卡训练的缓存原生资产与预算，不把8卡拼成强互联集群。原生资产与单卡训练已实测可行，parent32已完成，三条次序分支正在运行。step5000已含既有组织；这是继续学习中的塑性/历史检验，尚非分工诞生机制。E143仍是备选。

现有材料可以形成论文贡献的三个候选支点：真实预测配套、历史相关的合法兼容性、结构边界与gate-only强对照。恒等式、置换匹配和一般router–expert耦合均非新点；若不能跨自由gate/原生训练窗口重现，贡献仍是局部受控发现。详见[定位表](notes/POSITIONING_2026-10-26.md)。

## 5. 代码、复算与资产

- [只读driver](scripts/e144145_run.py)、[统计](scripts/e144145_analyze.py)、[E146](scripts/e146_grouped.py)、[E147](scripts/e147_gate_control.py)。复用`~/.venvs/mechpop`（torch2.8.0+cu128、transformers4.57.6），未安装新环境或下载模型。
- 从本工作台执行：`~/.venvs/mechpop/bin/python moe/scripts/e144145_analyze.py e144`（E145改e145）；`... e146_grouped.py analyze`；`... e147_gate_control.py analyze`。这些从封存raw重算，模型driver拒绝覆盖既有raw。
- 每项`results/eNNN/`的`manifest.json`锁定代码SHA、来源/输入与raw SHA；[8终点/公共模型校验](results/e144/asset_preflight.json)、[selected](results/e144/selected.json)、[来源表](results/e144/source_maps.json)可追溯。图：[预测与历史](results/e145/figures/recombination_and_history.png)、[分组与强对照](results/e147/figures/group_control.png)。
- 大权重沿[ASSETS](ASSETS.md)原位置；新raw在`~/mechpop_cache/e144_prediction_recombination`、`e145_history_cross`、`e146_grouped_recombination`、`e147_gate_group_control`，未放入Git。没有重建71.7GB训练H/Y cache。
- [本日日志](../logs/2026-10-26.md)、[历史阶段快照](notes/GPT_PHASE_SUMMARY_E120-E142.md)、[导师原问](notes/ADVISOR_2026-10-23.md)。当前解释以本页/方向文档/完整结果为准，历史暂停与过宽判断均保留来源。
