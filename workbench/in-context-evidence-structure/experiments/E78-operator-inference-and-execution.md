# E78：辨认来源函数与部署函数，是同一项能力吗？（2026-10-10）

- **状态：** DONE（定义顺序强混杂；Rule-ID gate未过，未证明可靠知道却不用）
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

32个新context×三证据×两定义顺序×六numeric接口×20query完整，另每条件两Source Rule-ID。251.922s=.0700 GPU·时；no-op0，60个完整forward/cache校对max9.16e−5nats，source hash一致。`results/e78/qwen3_bridge/{run,preflight,analysis}.json`，raw JSONL本地。

**主要改变判断的是定义顺序，而非涨分：** mixed/input-first插值copy-first定义（最后描述subtract）copy/subtract=.7734/.9609；subtract-first（最后描述copy）=.9609/.2500。copy-minus-subtract准确率偏好反转差+.8984 CI[.7284,1.0821]；外推+.7813[.5748,.9894]。seen .9961几乎全对，任务从示例可识别、word/频率不变，仍有非常强的描述位置依赖。Single该偏好差插值+.3672[.2812,.4467]、外推+.3516[.2197,.4825]，不是Source特有。**E77的identity劣势不能当稳定函数/组合结构。** 尚未独立确认新名字/算子表示；不将本组格式效应自动立novelty。

两order等权、未挑正确识别Source：

| 证据 | Rule-ID copy/subtract | direct插值 copy/subtract | direct外推 copy/subtract | auto插值 copy/subtract | auto外推 copy/subtract |
|---|---|---|---|---|---|
| mixed | .8750/.8281 | .8672/.6055 | .7461/.6523 | .8750/.8281 | .8750/.7734 |
| single | 1.000/.7969 | .9883/.8281 | .8750/.8320 | .9961/.7969 | .8945/.7969 |
| mixed+一句Source | .8594/.8594 | .8281/.6250 | .7109/.6523 | .8594/.8594 | .8555/.8008 |

Mixed Rule-ID总体.8516 CI[.7734,.9141]，single .8984[.8516,.9453]；各scope未有两函数都≥.90，**识别 gate未过，不称可靠知道却不用**。两候选概率质量按condition约.325–.505，完整vocab top1为候选的比例.453–.734；候选选择不是自由生成能力。Gold-code mixed插值.9961/1.00、外推.9922/.9414；single gold-copy外推.8945（copy-first仅.7891），未过该接口.90阳性，不能把全部条件解释成纯部署缺陷。

Mixed auto−empty插值+.1895[.1016,.2637]、外推+.2441[.1680,.3125]，满足差值MIE；auto−source-first +.2031[.1250,.2696]/+.2109[.1387,.2773]。但Source-first直接反而−.0879[−.1465,−.0293]/−.0859[−.1270,−.0469]；非Source-before-Input普遍恢复。Source指令−mixed direct插值−.0098[−.0391,.0176]、外推−.0176[−.0469,.0117]，无稳定恢复。

Opposite code的novel原任务accuracy几乎为0，说明给定字段能驱动不同数值；seen却仍大量跟随原demo（mixed seen .7422，single .4688）。这不是合法任务错误率，是故意不一致字段的语义控制；其seen/novel差目前仅诊断线索，未独立确认，不能直接宣布两套电路。

**按原决策执行：** 定义顺序控制偏好、识别和部分gold执行阳性不足，优先重建稳健测量，暂不做本组“已识别程序为何不用”的内部patch分支。中间code收益已有Liu2024直接近邻，不升级C##、不因涨分自动提高贡献评级。仍可进一步检验physical label来源与rule evidence来源是否可分，而非把原E77函数偏好强保为新机制。

### 运行期间新近邻核对（科学结果未读，不改实验）
[Liu/Neubig/Andreas COLM2024，2404.03028v3](https://arxiv.org/html/2404.03028v3) §2–5已直接研究instruction inference、following与few-shot预测的分离，且把归纳的instruction回交执行。**一般识别/应用分离与self-inferred code改善不是本项目的新认识。** [Fu等2609.03213v1](https://arxiv.org/html/2609.03213v1) §2–4/B.3比较rule/examples，指出不同机制不推出combined性能收益。两篇独立论文卡已写。本卡结果仍有诊断价值，但贡献需要具体Source条件下的可预测因果解释，不从潜在涨分自动成立。Corpus较具体查询找出Yang/Cho、Davidson common task representations、Few-Shot Examples Add Up；模糊Source/code查询命中无关program RL，不当空白证据。JIT的接收状态第三方与本地corpus不一致，继续只称预印本，其机制结论仍是强近邻。
