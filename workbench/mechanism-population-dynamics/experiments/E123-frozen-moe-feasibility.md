# E123：冻结骨干的单MoE层是否承担可恢复的语言计算（2026-10-25）

- **状态：** RUNNING（资产与CPU校验完成，dense层干预基线运行中）
- **类型：** REPRO / PILOT（X2开训前检查，不是完整跨种子实验）
- **对应：** P15：把组织与计算职责接起来；D1/D2受控平台建设。
- **问题（一句话）：** 固定原模型的输入表示和下游，随机MoE能否恢复被替换FFN承担的重要语言计算？
- **设置：** 固定revision/hash的 allenai/OLMo-1B-0724-hf；Dolma v1.7按官方token比例抽样（各来源独立文件分train/held，抽样/文件/字节与token hash写manifest，若只作小规模可行性须明确prefix偏差）。0起算L9，用64×1024、top8、softmax后不重新归一化、lb=.01、z=.001、router/expert随机初始化，保持原FFN激活宽度8192。冻结其余全部参数。探索seed=0；先验证1张卡，再决定跨seed卡和预算，不把本卡当等价性证据。
- **读数：**
  - 原始dense held总体token NLL；L9 FFN置零、换cal均值的ΔNLL，按文件/序列聚类bootstrap CI；E121 POS held目标下一token NLL及词形平权条件损伤。
  - 随机替换与训练后的 held NLL、每来源NLL、POS条件NLL、专家负载/熵/死专家、主损失/aux/z梯度非零、冻结骨干无更新。
  - 正常训练的tokens/s、峰值显存、加载/I/O时间；记录硬件/版本/seed和数据顺序。先64更新吞吐与梯度检查；通过后单seed至多32M token观察恢复方向，扩量另登记；不靠训练集MSE宣称恢复语言模型。
- **阳性对照：** 零向量hook与unmodified前向一致；真实置零hook须改变logits。原FFN重插损失应与原dense一致；随机MoE→主损失、router/expert梯度非零；只训练清单参数且resume续步一致。loss使用下一token对齐；保存log-probs为fp32。
- **噪声地板 + MIE：** 相同batch/形状的dense重跑；重要性参考ΔNLL≥0.02 nats且CI离开0（工程筛查尺度，非自动科学判决）。正式X2预先等价范围拟定总体±0.02 nats、POS条件±0.05，需根据dense损伤和抽样分辨率在跨seed数据前确认，不用不显著代替TOST。
- **混杂审计：** 同tokenizer逐字节核对；相同held输入/固定cal均值；训练/held文件不重叠；不允许held early stopping挑检查点；本卡只有单seed，不能做跨seed/训练历史结论。Dolma抽样分布和硬件为限制；激活参数量匹配不等于总参数量匹配；不使用upcycling掩盖随机分解问题。
- **决策表（跑之前写）：**
  - dense层损伤充分且训练明显恢复→以实测吞吐规划完整X2，至少5独立seed+同seed重跑+换顺序；另卡锁定tokens预算和读数。
  - 层损伤弱或无条件结构→不直接铺5seed；先报告该设定不能承载的问题，不以“怎样分工都可行”作结论。
  - 随机层不能恢复/负载塌缩→这是可行性问题，先检查优化/数据；不把优化失败当科学阴性，不同时增加多个自由条件。
  - 资源/吞吐超预算→保留同一问题，优先冻结前缀缓存与单节点独立运行；不直接减小模型后宣称等价。
- **算力预算：** 单seed上限8 GPU·时，准备/基线≤2 GPU·时；与E122合计同时≤8卡。**实际：** 待测。

### 运行前落实（2026-10-25，未看E123科学结果）
- 骨干revision=`d7cbab742d80589e714b1a2d7f838dcd21cbe143`；8文件5,121,291,958 bytes，完整sha256在`results/e123/assets.json`。分词器三个文件与OLMoE逐字节一致。加载使用本机NVMe副本。
- Dolma v1.7 URL清单revision=`7f48140530a023e9ea4c5cfb141160922727d4d3`；15来源，train=31,999,999 token/34文件、held=1,000,001/33文件；源URL、source/file_id、token内容hash的train/held交集均0。
- 这是**固定文件前缀的可行性样本**，不宣称精确复现骨干训练mix或代表全Dolma。按数据卡行token数×Sample Proportion归一化；行和1,645.15B与卡片总计1,715.1B不符，保留差异，不静默声称官方精确配方。CC News tail单文件仅在train，held有head/middle；books/wiki各一文件/侧。详细URL/token/hash见`results/e123/manifest.json`。
- lb公式明确为 `E*sum_e[count_e/(N*k)]*mean_softmax_e`，uniform=1，系数.01；z系数.001。以每个microbatch全部非padding token计算。该lb归一化与[MegaBlocks实现](https://raw.githubusercontent.com/stanford-futuredata/megablocks/main/megablocks/layers/moe.py)除以`tokens*top_k`一致；HF helper的uniform=k报告尺度不直接复刻。
- CPU已知答案校验：next-token loss对齐误差4.77e-7；连续3步与1步+resume的参数/optimizer最大差均0；identity/reinsert差0；no-renorm与lb尺度通过。摘要`results/e123/self_test.json`。
- 正式GPU基线使用seq512/batch16、固定512 held窗口和64 train校准窗口、全部964 POS held样本；基线完成且杠杆充分后，先64更新测吞吐。训练若继续32M，保持初始化/数据顺序和同一预定学习率日程（3906更新×8192 token=31,997,952）；64更新只设调用上限，不事后改日程。
- 模型/数据准备代码与训练harness经另一个agent只读审查；修复跨来源同名file_id伪重叠。未跑跨种子，未恢复头线。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：
- 结果文件：`results/...`
- 按决策表执行了什么：
- 主张变化：C## Lx → Ly
- POST-HOC 分析（事后才想到的，单独标注）：

### 工程备注：大张量哈希采样索引（2026-10-25）
- 首次真实GPU baseline在任何模型前向前失败：参数采样hash使用float32 `linspace`，大embedding的`numel-1`被舍入成`numel`，造成CUDA索引越界；没有产生科学读数。已改为int64等距整数计算，本条不是科学阴性，不新建实验卡。
- 独立CPU已知答案检查只分配33个int64索引，设`numel=103022592`：首项0、次项3219455、中项51511295、末项103022591；全部在界内且严格递增。结果已附入`results/e123/self_test.json`。
- 当前修复版CPU self-test重跑通过：next-token对齐误差4.77e-7，连续与resume的参数/optimizer最大误差均0，identity/reinsert误差0，no-renorm与uniform-lb=1通过；当前script SHA256=`f874f0675ab4423173a542c6765d2504aab33cd2a28c7aa412b71f9308936c80`。本轮复核未再编辑训练脚本；独立检查日志在`/tmp/e123_cpu_self_test_integer_index.log`（不进git）。
