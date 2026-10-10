# E83：用关系特征预测布局引起的Label读取变化（2026-10-10）

- **状态：** PLANNED；问题来自E82 pilot，等待同源码确认再启动GPU验证。
- **类型：** PILOT（计算解释的构造/独立预测，不是提高accuracy的方法）。
- **对应：** I04 / C16 / C20 / P20。
- **为什么现在：** E82显示Label读取重放贡献较大，末位与全query重放差小。完整donor可能已算出答案，不构成解释；要用事先明确的关系变量预测其变化，并看预测是否能产生相应Source contrast。Source字段存在不等于只需Source-match偏移；预算、输入匹配、联合关系及label身份是竞争解释。
- **问题（一句话）：** Tag→prefix的末位Label条件log权重变化，可由来源/输入关系预测，还是还需要具体输出身份；这些预测能否在全新context中转移原生读取变化的作用？
- **设置：** 同Qwen3-8B revision/float32/eager/conda。训练仅E82 seed82001全部32contexts的已存native attention，不用accuracy、gold margin或原运行correctness拟合，不筛head/context。验证64新context seed183001，同labels/names/codes/词池，不声称词表泛化。只在最后query receiver改Label读取，全部36层/head；其它query receiver重放own native attention，因果过去不会被末位干预改变。demo cache/V保留；末位V/残差可演化。
  - 因变量为各demo Label的delta=log r_prefix−log r_Tag，r为排除actual code G后的条件概率。Label位置两布局相同。所有模型共享截距和demo顺序t∈[−1,1]。
  - 每层/head独立OLS，系数跨全部contexts/4query共享。固定四个模型：B=(1,t)；R=(1,t,S,K)；RJ=(1,t,S,K,S*K)；RY=(1,t,S,K,S*K,Y,S*Y,K*Y)。S/K为demo是否匹配query的Source/kind的±1编码；Y为demo class-token身份toxic/safe的−1/+1。最多36×32×8=9216系数；不是一个低维开关，不声称发现新构件。Source和kind来自合成元数据（kind为已知semantic category），这是科学surrogate，不是部署系统。
  - 不使用query label、orientation、donor正确性或未知query答案构造任何特征。训练CPU 8-fold context split只报告预测误差，不选winner/超参；全32拟合后冻结全部四模型，再运行新context。
  - recipient actual code G始终own Tag完整概率，不需要held-out prefix donor提供该组。其它attention按own排除G的log条件概率，只给末位Label列加预测delta，重新softmax并乘1−own mG。重新归一化会改变其它组质量；不把它称纯组内选择。原生前缀/run仍保留。
  - 记录held-out真实prefix Label delta仅用于预测误差与阳性重放，不参与重新估计参数。阳性`oracle_label`用真实delta执行相同接口（G仍own Tag）；对照`RJ_source_flip`将S及S*K翻号，保留输入/label/位置。native Tag/prefix、self与一句Tag Source指令同时保存。
- **读数：** 全部context strict accuracy/correct margin/output Source-ranking/s与|b|；paired context bootstrap4000 seed830。主要比较R−B、RJ−R、RY−RJ、RJ−source_flip、每模型与oracle_label的差及oracle−native。另报delta MSE、去除组内均值后的allocation MSE、相对zero-delta的MSE降低；均匀及native Tag排除G后的Label条件mass加权（权重不取gold/输出影响）。这里的条件mass可由已保存log_r精确恢复，非全attention中未归一化的Label mass。错误donor也计入。
- **阳性对照：** native/self、前4context整段/cache；CPU拟合真已知线性系数；四模型嵌套训练误差顺序；G每个概率不变、行和≤2e−5、mask≤1e−7、self/full-forward≤.01nats。验证feature函数与训练相同，source hashes与frozen系数sha保存。oracle无正效应时只报告该接口无法转移，不把预测器失败升级为模型缺能力。
- **噪声地板 + MIE：** 如上数值控制。margin差>.15nats且CI为正或accuracy差>.05且CI为正才值得后续独立词表/layout验证；预测误差与行为同时报告，不因平均拟合漂亮宣布机制。此为pilot heuristic，不是研究资格关卡。
- **混杂审计：** 均衡Source×kind×Label与随机顺序/方向/码置换；模型族由E82之后提出，明确不是预见E82。被预测对象是两native布局的注意力变化；RY依赖这两class token的编码，跨label尚未测。系数没有因果组件定位，kind使用任务元数据；全层重放可绕过原生分布式计算。均值/误差不等于算法唯一性，通用关系检索/label geometry已有强近邻。
- **决策表（跑之前写）：**
  - R/RJ预测delta并转移oracle作用，RY增量弱：关系层面的有限读取模型可解释主要接口差；随后只验证一个新身份/layout预测，不补全所有机制。
  - RY明显超过RJ：输出身份参与此读取变化，独立Source-bias解释不足；先判断它是共享输出预算还是Source×Label项，不强称首次发现token-bound routing。
  - 拟合delta好但行为弱：统计读取重构不等于有效计算重构；查看已存样例/权重误差，不优化gold分数。
  - oracle好、所有预测器弱：这些固定变量不足，报告范围；不追加十个feature追拟合。
  - oracle弱或数值控制失败：本接口阳性不足/VOID，限制解释；不扩成项目新能力门槛。
- **定位：** Cho2025 label检索与旁路、Wang2026 task-identity weighting、Test-then-Route的token-bound router已覆盖宽泛原则。目标是对多规则query的具体反事实建立可失败的预测模型，不以新位置/回归公式/方法涨分立novelty。
- **算力预算：** CPU拟合与单卡验证≤.3GPU·时，不与关键E82 GPU确认并行。**实际：** 待填。
- **产物：** e83 reader fit/run脚本、冻结小系数及metadata、summary入git，raw native数组/JSONL本地。冻结后写准确命令/hash与具体预测，再运行验证。

## 结果（不改上方读数）

### CPU发现与GPU前冻结

E82确认支持Label读取主效应，允许启动此有限预测。CPU只用E82 discovery全部32contexts；8-fold context交叉验证，全部四模型保留、无winner选择。已知线性系数恢复误差2.66e−15，嵌套训练误差检查通过。

条件mass加权allocation MSE：B1.1716、R.7609、RJ.7607、RY.7233，zero-delta能量1.2632。R加入Source/input关系明显改善统计预测；显式S*K项几乎不增加，输出身份项有较小增量。**这不是行为效果预测已经成立**，也不从小MSE直接推独立Source编码。

冻结`results/e83/frozen_reader/coefficients.npz` SHA256 `db40ec4e2a50c2b8e23f6a0d08b0da05941bf1d50ec06691f276c5b2b9fd006d`；每模型最高9216系数、四模型有效系数合计21888。metadata记录每个native数组hash、特征顺序和所有CV读数。

**新seed183001运行前预测：** oracle_label有正margin作用（期待>.3nats）；R−B margin为正，Source翻号损害RJ的margin；RJ−R与RY−RJ增量预期较小（均值<.15nats），全部CI照实报告。不预设R重建全prefix accuracy；若统计误差改善而行为不转移，它会否定当前读取预测的充分性，而非算坏消息后加feature。

命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e83_predictive_reader.py --model /tmp/ices_models/Qwen3-8B --reader results/e83/frozen_reader --out results/e83/qwen3_prediction --n 64 --seed 183001`。此时只完成token/feature preflight，未加载模型或读取验证输出。
