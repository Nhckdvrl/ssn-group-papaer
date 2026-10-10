# E78：辨认来源函数与部署函数，是同一项能力吗？（2026-10-10）

- **状态：** RUNNING（启动前全32context预检通过）
- **类型：** PILOT；E77错误签名驱动的诊断，不预设存在“知道但不用”。
- **对应：** I04/C09/C15/P18。推进Source反事实响应→完整函数执行这座推断桥的有效边界；无C##升级预承诺。
- **为什么现在：** E77排除Source label均值后，single identity也只有.5625/.6719插值/外推，而single complement为1/.8828；direct两函数全对。多数identity错误恰是另一合法函数。需要拆开函数识别、Source选择、numeric执行，且排除函数描述顺序与query字段顺序诱发的偏好。
- **问题（一句话）：** 在同一组可识别的Source规则上，判断算子名称、直接回答数值、把模型选出的名称作为中间字段再回答，是否具有不同的成立条件？
- **设置：** Qwen3-8B revision b968826d9c46dd6066d109eabc6255188de91218，float32/eager；GPU0、conda verl-clean。32个新context seed78001，四Source Alex/Sam/Chris/Dana的theta独立，copy(x)=x或subtract(x)=9−x，16种组合各2。每Source Input2/7各2条，16条混排；每Source Input和Label边缘完全相同。A/B都查询0..9，seen2/7，插值3/4/5/6，外推0/1/8/9；同一context改变Input，不能Source常数答全域。
  - 两个header只互换完整函数定义块的顺序，文字/频率相同；函数名copy/subtract公开，**改变了E77的header，因此不叫同一baseline的重复**。
  - 三种证据：mixed、single（只该Source4records）、mixed+一句“Use only the records from the requested source and the stated mapping constraint.”。Single改变长度与干扰，非纯binding因果定位。
  - 每个header×证据，先问每Source `Source: A\nRule:`，对两个完整单token候选` copy`/` subtract`评分。由模型分数argmax选code，**不使用gold、不筛识别正确样本；是限制候选选择，非原生自由生成**。
  - 数值六接口：Input-before-Source直接；Source-before-Input直接；Source-before-Input但Rule为空；同位置填模型选出的code；填oracle code阳性；填opposite code语义控制。后三个code共用结构。Header明确空Rule需从records推断、已给Rule应被应用。Opposite是故意不一致中间结果，只衡量字段的因果语义使用，不当合法任务失败。
  - 三证据×两定义顺序×六数值接口×20query，另Source Rule-ID。所有context/Source/函数保留。选出的Rule code先于Input，跨该Source所有Input复用；增加计算与token，不称免费读出修复。
- **读数：** 十数值完整continuation的精确log概率（space＋digit），accuracy用gold margin>0，seen/interpolation/extrapolation分开，copy/subtract分开。Rule-ID两候选margin/accuracy、候选概率质量；numeric demo词选择率和opposite-function错误率；auto code正确/错误不筛样本，主准确率含全部错误传播。
  - 主paired contrasts：Source-first−Input-first、auto-code−empty-Rule、auto-code−Source-first、mixed-scope−mixed；single作为一般函数推断参照。两定义顺序copy−subtract偏好变化；若header反转已能解释差异，优先格式/先验解释。
  - 4000 context bootstrap seed780；函数子组允许每context含0/1/2个对应Source，按numerator/denominator重采样，不删除没有该函数的context。单独报告两order及等权合并，不挑最佳顺序。
- **阳性对照：** 16格完整平衡、四Source规则由2/7关系唯一决定、Input/Label频率不变、token分段等价；无missing权重。重复cache no-op≤.10nats，首context缓存评分与完整forward数值对照≤.10nats。seen≥.90；oracle-code插值/外推两函数各≥.90才解释numeric部署。Rule-ID两函数各≥.90才称辨认可靠；识别失败不能归后续交接。
- **噪声地板 + MIE：** no-op≤.10nats；paired accuracy差≥.10且95%CI不跨0才推进程序交接/字段位置线；偏好随定义顺序反转变化≥.10且CI不跨0，优先header/先验解释。未知完整函数能力仍需两函数、两novel组各≥.80；不以方向或某个operator成功代替。
- **混杂审计：** 熟悉算子选择不是arbitrary算法学习；额外Rule查询可能诱发原numeric状态没有的计算（JIT），成功不证明原状态已有完整函数。给code增加明确参数/计算与文字指令；empty对照只部分控制token数量/结构。Source-first位置改变不能单独定位attention机制。Rule-ID识别≠Yang/Cho/Inoue的TR（标签空间识别）；两函数共享数值label空间。正常raw候选评分与原生chat能力分开；没有自由生成或强模型结论。标准CoT、task/function vectors、JIT与Cho过滤/检索均是强近邻，不以“中间步骤有效”宣称新机制。
- **决策表（跑之前写）：**
  - Rule-ID失败、oracle code有效 → 主要是从demo识别/按Source选择规则，不说知道但不用；比较单来源及header顺序。
  - Rule-ID有效、oracle code有效、direct numeric弱、auto比empty高≥MIE → 存在可观测的函数识别/应用接口差异；仍需独立确认及内部因果证据，不把外部code修复归原生算法。
  - Source-first直接已恢复且auto无额外MIE → 查询字段位置解释优先；不宣称算子交接瓶颈。
  - 定义顺序显著控制偏好 → 把E77视为至少部分格式/函数先验现象，重建稳健任务后才做机制。
  - single也无法可靠识别/应用 → 一般规则学习/接口边界，不称多Source组合特有问题。
  - oracle code也失败 → numeric接口执行控制无效，先换测量；不归function推断。
  - 全部接口稳定可靠 → 原问题边界显著收缩，不能包装成原缺陷普遍存在。
- **算力预算：** 本地空GPU0预计.15 GPU·时，不训练；其它卡不预跑依赖本结果的机制分支。**实际：** 待填。
- **产物：** scripts/e78_operator_bridge.py、scripts/analyze_e78.py；小run/analysis入git，raw JSONL本地。
- **命令：** `CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e78_operator_bridge.py --model /tmp/ices_models/Qwen3-8B --out results/e78/qwen3_bridge`。预检26880个numeric query边界及所有Rule词、定义顺序token频率相等；preflight-only不加载权重、不读取科学评分。
- **定位：** [Yang/Cho/Inoue](https://arxiv.org/html/2509.24164v2) §3.2/G.7/H.4已核对；[Cho信息移除](https://arxiv.org/abs/2509.21012)、Hendel/Todd/Few-Shot Examples Add Up、JIT均占有可读出≠可部署或query-dependent task程序的大块解释。此卡先检验我们自己的推断，不自动宣布空白。

## 结果（跑完后填写；上方读数/MIE不按结果改）

待运行。
