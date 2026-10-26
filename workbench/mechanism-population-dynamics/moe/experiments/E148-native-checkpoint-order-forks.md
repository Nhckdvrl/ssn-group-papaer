# E148：原生完整 MoE 继续学习中的短期次序分叉（2026-10-26）

- **状态：** PLANNED；原生模型新预测与训练尚未运行。由流程生成器登记，按主题放入moe。
- **类型 / 对应：** 因果PILOT / 驻留可行性；C11/C12、P31/P32。检验受控学生的历史兼容性现象在完整原生网络继续学习时的边界。
- **问题：** 从同一个原生预训练检查点出发，只改变一段完整minibatch的先后，再接受长共同后缀，终点的gate/专家配套和合法移植代价是否仍不同？
- **本卡不认领：** 原始OLMoE预训练复现、独立初始化总体规律、天然联盟或完整形成机制。是全参数原生架构上的受控继续学习，只有一个父状态。

## 固定窗口与工程选择（模型读数前）

- 缓存`allenai/OLMoE-1B-7B-0924`，revision目录`step5000-tokens20B`；16层、64专家、Top8、不重归一，L9作为桥接主层；所有参数均更新，不插学生层、不固定骨干或gate。
- 该权重为约6.919B参数、BF16文件13.838GB；普通全FP32 Adam参数/梯度/二阶状态估算约110.7GB，超单张96GB。选择已有Transformers **Adafactor**（无一阶动量、factored二阶状态），保留FP32主参数，以`torch.func.functional_call`的可微BF16影子执行原生forward/backward。不是在BF16权重上丢失小更新，也不安装8bit库/拼跨节点训练。
- 固定Adafactor：lr=1e−5、relative_step=False、scale_parameter=False、beta1=None、weight_decay=0、eps=(1e−30,1e−3)、decay_rate=−.8、clip_threshold=1；另加全参数grad norm clip=1。CE + 原配置native router aux coefficient .001；无额外z项，不自造teacher目标。公共optimizer状态未发布，所以先形成我们自己的共同parent，不声称忠实延续原optimizer。
- CPU已知答案先证明：BF16影子与原生BF16前向一致、FP32主参数得到正确梯度、小更新被保留、functional_call后原参数恢复、checkpoint恢复后的更新一致。真实GPU预检只用训练侧输入，检查精度/显存/吞吐与backbone、gate、expert三类梯度。

## 数据与严格分叉

- 复用E125耐久Dolma token源；与此模型tokenizer三个文件SHA一致已静态核对，执行时复核。训练/held源文件不重叠。统计从自然语言next-token CE读取，不使用提示词能力探针。
- 全局batch **2×512=1024位置/更新**，默认microbatch2。若训练侧显存预检OOM，可在所有分支统一改microbatch1/accum2，并在任何新held读数前登记；不根据科学效果改剂量。
- 训练计划预先生成：warm32个随机batch；pulse128个同源batch（每个batch两序列来自同一source，source按原sampling weight抽）；suffix512个随机batch。计划存token字节/原始file+window与SHA。
- warm前16步线性lr warmup到1e−5，其后固定；warm32后保存完整FP32模型、optimizer、CPU/CUDA RNG，作为唯一共同parent。
- 分支A：pulse完整batch按source及原pool ID字典序排列；分支B：相同128完整batch以固定seed14803置换；A-repeat：逐字复跑A。三分支不改变batch内部组成，全部接受同一个512更新后缀。
- pulse的batch集合/每个token曝光多重集合必须精确相同；suffix token-chain与cursor必须逐更新相同。三者从同一模型/optimizer/RNG开始，完整保留repeat，不将三分支当三个独立seed。
- 总step：parent32、pulse-end160、中后缀288、late608、final672。最终每分支640次更新=655360位置，另有共享warm32768位置；三分支总曝光1998848位置（repeat计成本，不算独立科学重复）。

## 预先固定读数与快照

1. **新held：** 从原held窗口全集排除旧512窗口，固定seed抽64条×512；若余量不足则如实标记已用人口，不偷偷改选择。另固定training cal 16序列。选择/新batch与token字节SHA在模型读数前锁定。此排除只针对明确记录的旧512窗口；不保证全部历史实验从未测过，也不声称预训练无污染或新的确认性测试集。
2. **自然预测：** parent、pulse-end、late、final的完整模型NLL、A/B双向KL、A/A-repeat噪声；late→final自身变化作为继续优化尺度。BF16 logits→FP32 logsoftmax。保存BF16 logits位模式或可重放权重，不把NLL接近叫同函数。
3. **合法配套后果：** pulse-end和final，各以A与B的完整网络作接收者，在L9分别native、只移植对方bank、只移植对方gate、移植对方整L9、L9置零；附A←A-repeat bank和各自late-bank参照。主读ΔNLL与KL(native receiver∥variant)，两个接收者均保留。
4. **全模型边界：** donor整L9移植仍在receiver自身prefix/downstream里，绝不称donor native对角。不同骨干表示/读出也属于此兼容性；不从本卡归因“只有expert内容”或“backbone co-adaptation必要”。
5. **组织轨迹：** 各预定快照保存所有gate与L9完整FP32bank，cal/held路由（固定原物理槽位）。报告L9选择/门值变化、gate-only图与固定cal输入响应；只将已有快照用于对应时刻，不假装连续动力学或语义职责恢复。
6. **统计：** input按实际(source,file_id)成对bootstrap1000次、seed148001；只有1父状态、1次pulse处理。所有科学对照完整报告，既不筛输入/分支，也不把输入CI作seed总体CI。

## 阳性对照

- tiny模型：可微BF16 shader前向/梯度/主参数更新；完整保存恢复逐步一致；数据顺序集合与后缀链已知答案。
- 真实训练侧：直接BF16原生与FP32 master/BF16 shader前向匹配；重复前向；三类参数非零梯度、FP32更新与BF16有效改变分别计量。
- A-repeat给同父同流的全流程噪声；自身bank、gate、整L9重装复现；zero L9检验真实语言读出响应。所有source/输入与实际物理GPU UUID核对。

## 噪声地板 + MIE

以重复前向、A-repeat、FP32→BF16/组装路径实测地板，和late自身漂移并列。无任意NLL恢复/相关性准入线。若处理作用低于分辨率，报告本父状态、剂量与有限后缀下未区分，不自动放弃母问题或加LR/剂量网格。

## 决策表（跑之前写）

| 观察 | 更新认识 / 下一步 |
|---|---|
| pulse后兼容性差异经共同后缀仍保留，超过repeat对应尺度 | 支持本原生继续学习窗口有持久历史依赖，进一步由保存快照定位关系；不宣称普遍关键期 |
| pulse可测、final趋近repeat/自身漂移尺度 | 本窗口任务/共同优化会减弱该剂量历史；受控局部学生结果不能直接外推 |
| full predictor变化明显，而L9移植关系不额外改变 | 主要证据落在整体预测路径，不能包装成L9新职责机制 |
| 原生单卡训练不可行或梯度/精度/重跑合同失败 | 记录具体技术结果，修实现；必要时登记有限方案修订，不转成科学阴性 |

## 资源与产物

- 既有`~/.venvs/mechpop`、torch2.8.0+cu128、HF4.57.6；public模型和数据仅本地复制复用。单卡预检/parent，随后A/B/repeat三张独立卡，不跨节点通信，探索并发≤8。
- 首包硬上限 **3 GPU·时**（含预检、parent、三分支、失败、读出）；先profile训练侧成本。若不够完整读数，记录partial/缺失阶段，不根据效果删条件。
- local `/tmp/xiang-moe-20261026/e148`；耐久`~/mechpop_cache/e148_native_order_forks`。full FP32 parent/pulse/final用于精确复现；稀疏时刻保留全gate+L9和实际预测。大文件不进Git，所有路径/size/SHA与重建入口写ASSETS。
- 本轮实际结果每完成一个阶段立即写入MoE README的说明，再继续下一已授权阶段；不以卡片/脚本完成充当实验完成。

## 结果

尚未运行；无新主张升级。
