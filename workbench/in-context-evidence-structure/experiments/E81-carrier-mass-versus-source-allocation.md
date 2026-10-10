# E81：保持读取总量时，来源码内部的分配能否改变规则选择？（2026-10-10）

- **状态：** PLANNED
- **类型：** PILOT；本次只做一个机制问题，不追加函数/词典能力关卡。
- **对应：** I04/C16/C17/C19/P12/P13。研究对象是多规则ICL的证据选择；Tag/prefix只是区分解释的操作变量。
- **为什么现在：** 人审计要求正面对齐Cho、CoSToM、contextualize/aggregate及QK/V近邻。E59–E71已有实质证据，但不能将output source-ranking等同于内部选择。旧E71只存固定prefix位置（D0为Mark，不是Tag来源码）；POST-HOC初读显示公共偏移可能减少而非增加载体mass。要分开权重总量、组内分配与完整结果，不能再追52.7%涨到80%。
- **问题（一句话）：** 在相同多来源分类任务中，用另一布局的原生读取总量或组内权重替换来源码的读取，哪种改变能转移Tag/prefix收益；保持总量和输入类别分配时翻转来源权重，答案是否跟随？
- **设置：** Qwen3-8B固定revision b968826d9c46dd6066d109eabc6255188de91218，float32/eager，conda verl-clean，本地空GPU0。沿E71 linked关系、16demo/2Source/2kind、每cell4条，名字Alice/Bob、码Left/Right、标签toxic/safe、occupations/vehicles。新32contexts seed81001（非E71的发现/确认seed），仅4个无冲突自然query。Source字段始终充分，demo/query交换Tag与prefix的相同码，token多重集/长度/sites不变。全部contexts/错误donor保留，不以正确性筛选。
  - 两原生布局D0/D1；实际carrier G分别为Tag码token与答案prefix码token，按同一demo顺序对应，不比较D0的Mark与D1的码。
  - 收集原生每层/head/有效query位置的attention。分解为载体总量m、组内pi、组外条件分布r。全36层及**整个query所有有效位置**执行干预，不只末位。
  - 对每recipient做固定2×2：m取recipient/另一布局的原生值；pi取recipient/另一布局原生值。组外条件分布r按当前recipient活的Q/K计算，按(1−m)缩放；组内为m*pi。因m/pi都钳制到预先收集值，早层干预后它们仍在逐层可比；组外权重及V/MLP可随下游状态变化，不声称全网其它计算不变。
  - self=(own m,own pi)应重建native；mass=(donor m,own pi)；within=(own m,donor pi)；both=(donor m,donor pi)。不拟合尺度、不挑层/头、不用gold输出构造权重。
  - **source_flip：** m保持own。对每kind，固定该kind的pi总量及每个source×kind cell内部相对权重，仅交换两个Source的cell总量。用已知合成kind/source元数据定义反事实，不是可部署的方法。可以改变按来源的分配而不改变类别边缘，不假定天然就是“正确证据选择”。
  - **full_attention donor：** 整个query attention替换为另一布局原生矩阵，demo的码/Mark列按角色交换对齐（都在query以前，不改变因果可达性），query列按物理位置保留；recipient V/cache/残差保留。诊断carrier之外的读取路径是否重要，不以它未恢复作为experiment整体失败。
  - 两布局都测一句Source指令；不延展新的自由生成/推理能力结论。
- **读数：** correct logit margin、strict二候选accuracy、同Input的Source输出排序分别保存（后者非内部source selection）。actual carrier与label的m、requested-source份额、按query字段与层段的读数；四条件的对称Shapley m/pi贡献及交互；D1−D0在相同m/pi后的剩余差。source_flip−self的margin/accuracy/排序、组内Source份额变化；total mass和kind边缘不变误差。所有读数按context聚合，bootstrap4000 seed810，不选幸存种子/最佳层。
- **阳性对照：** CPU exact group分解/重建与kind-preserving来源交换；相同token/layout检查；native self重建；前4contexts两布局整段前向与prefix-cache query评分核对；全attention self恢复；逐干预m/pi目标、行和、masked mass、kind边缘误差。另一布局完整attention的效果不是预设正分，是诊断结果。
- **噪声地板 + MIE：** float32 self/full-forward margin误差≤.01nats、attention行和及m/pi/kind误差≤2e−5、masked probability≤1e−7。组内及cell条件分布用相应原生logits的softmax稳定计算，避免近零mass除法，不静默换uniform。主差值margin≥.15nats或accuracy/输出排序≥.05且CI不跨0，视为值得独立确认的pilot；不是整线资格门槛。原生layout gap不足.15时报告实际效应，不据此做不稳ratio或换seed追显著。
- **混杂审计：** 缓存/概率移植是非自然干预；不同角色的V内容、其上下文化和其它原生路径保留，所以共同m/pi后的差不能独归Value/readout。source_flip固定kind但cell内具体词不同；cell频率严格平衡、顺序/词/方向全保留，不说脱离任务的一般Source模块。活组外反馈可改变label读取，这是作用的下游而非被固定的量。全部head平均描述不直接证明因果位置；本实验因果范围限实际码carrier与全query，不代表所有多规则场景。只检验此具体解释，非重新论证弱模型永远失败。
- **决策表（跑之前写）：**
  - mass主要转移收益、within/source_flip弱 → carrier预算配置足以解释部分位置收益；不称修复绑定，不预设mass增加。
  - within或source_flip在固定mass下有清楚效应 → 组内来源分配有独立作用；联合m/pi与行为读数检验，不拿output排序替代选择证据。
  - both弱而full_attention明显 → 重要读取发生在该carrier之外；当前载体解释不足，回已有query路径，不开新任务。
  - 同m/pi后布局差仍在 → 当前分解不足，允许payload/历史/其它路径；不直接命名新Value机制。
  - 全部操作效应小/不确定 → 此接口没有决定性区分，保留有界结果，不铺十种变体追同故事。
  - 数值/映射控制失败 → 该运行VOID，修具体操作，同seed重跑，原失败留存；不升级科学主张。
- **算力预算：** 单卡≤.2GPU·时，必要的独立确认另≤.3；关键pilot回来前不并行下游分支。**实际：** 待填。
- **产物：** scripts/e81_carrier_allocation.py、analyze_e81.py；results/e81/*小run/control/analysis入git，raw JSONL/NFS本地；旧E70/E71注意力再分析单独标POST-HOC。
- **定位：** Cho shortcut/forerunner已解释提前计算，Bakalova与Wang2026已有上下文化/QK−V区分；单softmax的m/pi数学不新。潜在增量是自然的多规则Source条件下，具体读数与反事实可否支持可预测的证据选择解释。CoSToM是读出→有监督构造→对话验证，非原生电路完整逆向；不硬仿训练涨分。

## 结果（跑完后填写；不改上方读数）
待运行。E80没有科学运行；自动编号工具因历史文字中出现E80而分配E81，不将编号跳跃计成实验进展。
