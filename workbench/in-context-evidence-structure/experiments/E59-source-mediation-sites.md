# E59：来源选择与标签映射是否走不同的上下文位置（2026-10-10）

- **状态：** DONE（2026-10-10；发现、预定独立确认及有界复现完成）
- **类型：** PILOT（E58 异常后的串行追问）
- **对应：** I04、C12、C13；E58（来源差分跨标签可读出，label-anchor KV 中介小）。
- **问题（一句话）：** 在简单语义分类和 E56 的真实评论交互任务中，改变来源名字与改变标签映射分别经由哪些 token 位置的 K/V 影响答案？
- **为什么现在做：** E58 已说明可读出的来源差分不是标签锚点承担来源条件化的充分证据；Cho 2025 已讨论旁路，所以仅发现另一位置有用不算增量。这里对比两个完整反事实的中介结构：来源身份关系 vs 输入—标签映射关系；直接检验“同一 label-anchor circuit 同时承担这两种关系”的推断。
- **设置：** Qwen3-8B frozen/bf16/SDPA，无训练。三段缓存：base、source-swap（所有 demo 名字互换；内容/标签不变）、label-flip（所有 demo 二元标签互换；内容/名字不变）。两 donor 均在理想任务下翻转查询答案；查询文本恒定。所有操作配对，anchor/token 长度逐位 assert。
  - synthetic discovery：64 上下文，seed59001，animals/fruits，yes/no；独立 synthetic confirmation：64，seed159001，occupations/vehicles，toxic/safe。
  - real discovery：48，seed59002，E56 Measuring Hate Speech train pool（race/gender）；real confirmation：48，seed159002，E56 test pool（评论不重叠）。每人×类4条demo，query每类4条、两来源共16判断。复用 E56 固定 pool split(seed5600)，HEAD/Annotator/Comment 与其一致。
  - 不用 E58 数据挑位置：预先全报告 source_name、label_prediction（答案前冒号）、label_anchor、post_label（第一个分隔 token）、source_span（名字至答案前）、non_anchor（全部prefix去掉标签锚点）、whole prefix。每位置 K-only/V-only/KV；另全缓存 K-only/V-only/KV。baseline、source-swap、label-flip、no-op、一句指令。资源上限后不追加无关配置。
- **读数：** source-correct label margin、accuracy、paired base−patched margin 及 context-bootstrap 95%CI。来源效应 fraction=该移植效应/完整source-swap；映射效应 fraction=该移植效应/完整label-flip。完整效应 ≤0.2nats 不报告归一化。比较相同位置在两种counterfactual下的不同角色。额外报告 paired source effect covariance，而非仅挑头/层峰值。
- **阳性对照：** full KV 精确复原对应 donor（差≤0.10nats）；no-op逐位等于base；label-flip须改变margin；source-swap须有可测影响才能讨论source中介；全部demo/query标签单token并核对paired位置。源正确label sign都依base真值，故 donor score预期反号，不按donor标签重标定。
- **噪声地板 + MIE：** E58 no-op/full/repeat均0nats；本卡重核。raw paired shift >0.20nats且CI不跨0、位置中介fraction差>0.30才作为进入下一轮有信息量的线索；不当作自动主张升级。48–64上下文CI为抽样不确定性，不代表多种子/多模型总体。
- **混杂审计：** 配对内容、次序、词频；source/label swap分别隔离；不筛模型回答；源名频率/标签频率平衡；真实train/test评论分离；保持E56提示一致；token字节核对；全位置报告控制选择；简单/真实范式各自独立确认；未控制：source-swap使后续所有token产生间接变化、hybrid cache的非自然分布、label-flip包含标签词本身变化，两种fraction不是同一因果量，不能宣称纯粹的独立子电路。
- **决策表（跑之前写）：**
  - anchor承担标签flip、其它位置承担source-swap（独立材料确认）→ 检索关系可能分布在不同中介位置；下一步才能测试二者如何组合，不能把旁路发现包装成新电路。
  - 两种效应都主要anchor → E58简单任务是边界；在实际受控真实任务重审合取来源，不能泛化其否定。
  - source-swap分散且全K/全V单独不充分 → 多步query计算/跨位置协作，调整研究对象为过程组合。
  - real source-swap不显著 → 源条件化本身太弱，中介结果不可判；label-flip可用作harness阳性对照。
  - 简单/真实或发现/确认方向分歧 → 明确范围；不保原单一路径故事。
- **算力预算：** ≤1GPU·时，本地conda verl-clean，一卡串行；**实际：** 0.282 GPU·时（单卡进程墙时折算，含加载，非积分利用率）。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- source-name K传递source-swap效应：Qwen合成发现0.921[0.865,0.981]、确认0.944[0.900,0.989]；真实评论发现0.973[0.880,1.072]、确认0.884[0.795,0.971]；Mistral0.823[0.782,0.865]。real完整效应仅0.458/0.618nats量级，不是高准确率能力证据。
- real-confirm label-anchor KV的source效应比0.051[−0.017,0.112]，mapping-flip效应比0.985[0.894,1.084]。对两种关系起不同作用，不能归为唯一锚点。
- 结果：`results/e59/*/mediation_analysis.json`、`qwen3_real_confirmation/probe_analysis.json`。C15新增L1；hybrid效应比不互斥、不可按百分比相加。早期极性不一致运行保留、不纳入。

### 跑前补充（2026-10-10，E59 未启动）
真实 confirmation 另留64个 train-pool 上下文（seed59003）拟合 E58 固定协议的来源跨标签 probe；48个 test-pool 上下文独立检验。保存 residual、pre-RoPE K、V 双胞胎特征。这是接回 E55/E56 的表示验证，不据 synthetic 结果调整模型/层/正则。synthetic 阶段不重新拟合 probe。

### 工程修正记录（2026-10-10）
首个 real discovery 运行在完整汇总前停止：E56 的 toxic=1 被写成本脚本的 label_index=1（safe），demo/query同步反向，仍是定义良好的交互任务，但与预注册 E56 的标签极性不同。目录 `_polarity_mismatch` 保留，不纳入主证据。现将索引统一为1−toxic；使用原seed59002完整重跑，不选seed。synthetic结果不受影响。

### 跑前扩展（2026-10-10，主测量已有效）
Mistral-7B-v0.3 在 E58 发现集的来源差分跨标签迁移亦高，锚点KV交换很小；因此在同一预注册 synthetic discovery(seed59001,n64)复制 E59 的来源/映射位置对比。此复现不改变本卡primary协议，只回答是否Qwen特有，不继续扩大模型清单。
