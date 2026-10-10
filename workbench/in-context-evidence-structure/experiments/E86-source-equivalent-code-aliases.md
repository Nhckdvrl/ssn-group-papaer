# E86：同一Source的两个等价码是否仍共享分类证据？（2026-10-10）

- **状态：** DONE-PILOT（16新context完成；64-context确认未启动。人要求先纠正局部控制牵引，当前优先综合问题与阅读）。
- **类型：** PILOT。
- **对应：** I04 / C20 / P20。
- **问题（一句话）：** 当一个Source有两个可互换的码，模型按Source合并规则证据，还是按字面码划分支持集合？
- **为什么现在：** E84/E85每Source只有一个码；解析来源后读规则、按码直接选Label支持集在自然query上共线。E85确定两Cue对NameK依赖不同，但没有区分这两个计算解释。此次候选来自这个认知缺口，不从新论文的相近术语出发。
- **文献前置：** 先核对Cho的任务子空间/标签检索、Mixing Mechanisms的实体唯一性/混合模型、Wang的FV与query作用、Test then Route的明确规则与条件/答案干预、Z-ICL的label synonym copying；对照见复盘§16。现有框架是否能推导该具体反事实仍需明示，不把题目相似当完整覆盖，不把没有相同实验当空白。本卡不是novelty宣告。
- **设置（候选，执行前仍需最终预注册）：** Qwen3-8B固定revision，同float32/eager、conda。暂定16新contexts seed86001，沿E58 occupations/vehicles、两Source×两kind×4示例、相反分类规则、toxic/safe。每Source分配两个任意单token码，码身份/alias↔kind排列逐context随机；query用同一未知Item、同Source的两码分别提问。Tag/prefix两布局，最终class词/全Source标签频率保持。
  - balanced：同Source每码有两种kind，各2例。
  - segregated：同Source一个码只出现kind0，另一码只出现kind1，各4例；Source内完整规则证据仍在。
  - 任务说明明确两码是同Source的可互换标识，class规则由Item与Source决定；一句只用指定Source的指令对照保留。
  - 目标是让同Source规则检索与字面码Label支持在crossed Item/alias query上预测相反，不把alias下未出现kind自动视为能力缺陷。
- **读数（候选）：** 8query完整Source×kind×alias；分别测Input规则响应、alias响应及matched/crossed的base-rule margin/accuracy。规则与alias响应从2×2输出分解，不直接当内部模块；不在结果后挑readout/seed。后续因果接口只在此区别有解释价值时设计，当前没有代码/训练任务。
- **阳性对照：** balanced布局、已有Item的query、同Source同Item换alias、一句Source指令；token频率/位置/完整前向与no-op。阳性用来理解诊断，不升级成ICES整线的新关卡。
- **噪声地板 + MIE：** 若实施cache操作，自拷贝/full-forward≤.01nats；先完整报告分量/CI，alias作用>.15nats且CI不跨0仅作为可进一步辨别的线索，不自动判断科学收益。
- **混杂审计：** balanced→segregated改变码与kind/label的关联，正是要制造两解释不同预测的变量；不能称两数据分布信息完全相同。两码语义、tokenization、明确Scope与TF语法需核对；TF测条件标签判断，不是全词表端到端生成。现有Source↔code范式不能自动证明alias等价已被使用。
- **决策表（跑之前写）：** 以下为尚未执行的候选草案。
  - Input规则响应保留、同Source换alias稳定：反对当前强字面码分组版本，不继续包装必然按输出身份分开。
  - segregated的crossed query被alias-label关系牵引，而balanced保留规则：找到两机制的可辨别条件；再用既有NameK/Label读取接口问哪条计算承担差异，不能只以行为差异宣称新机制。
  - 两者都弱或Scope有歧义：保留诊断，不强行说共享Source绑定失败，不扫更多任务追正结果。
- **算力预算：** 如最终采用，单卡pilot≤.2GPU·时；不预排后续矩阵。**实际：** 0，未运行。

## 结果

截至上一会话无科学运行。用户要求先完成具体文献调查再考虑方向；原候选记录完整保留。C20与I04/ACTIVE均未改变。

## 解释能否给出不同预测：静态推导，非实验结果

不能只把两个故事命名。令`r(s,k)`为Source规则对class-logit差的正确方向±1，`a(s,alias)`为segregated中该alias示例对应的class方向。E85的平均field/code分量记f/c，另有共同bias b。

- **共同Source范围解释：** 两码先归到同一Source，之后同规则证据起作用；`z=b+(f+c)*r(s,k)`。在这个强版本中，同Source同Item换等价码不改变答案，matched与crossed的平均signed margin差为0。
- **线索分别读取Label支持的解释：** `z=b+f*r(s,k)+c*a(s,alias)`。同分布每Source唯一码时与上式相同；segregated中matched是f+c，crossed是f−c，差2c。以**已冻结E85探索native均值**c_Tag=.19755、c_Prefix=.46421直接外推，预测差分别.3951/.9284nats，两布局差值交互+.5333nats。若最终跑，这些数值须先commit，不用alias结果重拟合。

这是已有检索/绑定框架在当前问题上的两个明确实例化，不是文献声称它们就是完整LLM算法。任意alias增多、Scope说明与输入支持变化都可能改变f/c；所以量级预测失败会限制这个冻结外推，不撤回E85的自身证据。共同bias在平衡配对平均中抵消的假设也要核对。

另一个解释是模型将每alias理解成不同task而非简单copying；它也可产生alias响应。本项行为实验即使成功，也只区分强共同Source范围与alias敏感版本，不能单独区分task重新划分/直接Label读取。要怎样用E85既有接口检验后者，仍需在实际样例支持下决定，不预先宣称已经锁定机制。

## 最终预注册：2026-10-10，用户要求快速持续推进之后

上述具体近邻调查和预测推导已完成；选择此项作为**现有I04的机制辨别实验**，不另开方向。原草案不是事后卡，下列内容在首次GPU评分前冻结。

- 模型Qwen3-8B revision `b968826d9c46dd6066d109eabc6255188de91218`；float32/eager，conda verl-clean，GPU0。16新context seed86001，职业/交通工具、Alice/Bob、toxic/safe；码Left/Right/Up/Down逐context随机分配，alias与kind关联的方向在两个Source分别随机。
- 16demo、每Source×kind四例、每Source每码四例；balanced每Source×kind×alias两例，segregated同Source一alias仅kind0、另一仅kind1。两支持条件保持原Item/Source/class/顺序和token多重集/所有sites，仅改code分配。Tag/prefix布局仍仅互换码与Mark。HEAD固定明确两码可互换，并列出每Source的两个码，避免没有告知等价关系；所有条件另有相同的一句Source指令恢复对照。
- query 16项：8未知Item（Source×kind×alias）＋8已出现Item；每Source/kind的seen Item从其4demo中随机选一次、对两alias复用，不挑能答对的词。未知Item与所有demo不同；两Source共享相同未知Item。未给最终gold class，code为外部指定有效alias，仍非原生端到端生成。
- 条件仅balanced/segregated×Tag/prefix×默认/Source指令，共8项。先做这一最小行为/预测辨别；不提前铺所有K/V分支。
- 主读数：未知Item的`gap = matched-alias correct margin − crossed-alias correct margin`；segregated−balanced的gap，以及其Prefix−Tag差。报告Input规则分量R、alias分量A、shared bias、matched/crossed accuracy，seen同读数作诊断。gap=2A可代数核对，不能称A为内部模块。4000 context bootstrap seed860。
- 冻结外推：Scope模型gap=0；两Cue模型segregated gap=.3951/.9284nats（Tag/Prefix），布局差+.5333；基于E85探索32context的参数bootstrap单独保存，不重估alias确认参数。候选量级来自较简单任务，数值失配限制这项外推而不撤回E85。
- 阳性/噪声：token/词频/布局/Scope表核对、batch/cache对逐条完整forward（前2context全部16query）、自拷贝cache、mask与行和；numeric≤.01nats、mask≤1e−7。balanced与seen用于区分无效读数或未知Input泛化，不要求它们先达到新绝对accuracy才允许报告作用。所有contexts保留；科学负结果不是VOID。
- 决策：若未知Item alias gap在segregated增强>.15nats且CI不跨0，或两冻结解释的预测误差有清楚区别，则先冻结方向/量级再同源码64新context seed186001确认；随后才考虑实际有区分力的Code/Label key干预。若gap不增强则拒绝此强字面分组版本，结合已有NameK/Label结果更新解释。若方向不确定，认真看完整样例，不扫seed/模型追效应。
- 预算单卡探索≤.2GPU·时、确认≤.3；raw context/behavior JSONL本地，小run/preflight/analysis/冻结预测入git。C20保持L1、正式排程不变。脚本与卡先commit、预检后运行，源码/依赖hash入run。

CPU预检已通过，源码SHA256 `20a5c3eced7c5ec165abc55d9e5e188969db4fc7e11a162109353f8f73751d8a`；Scope明确、码所属Source、balanced/segregated计数、多重集/位置/长度、seen/unseen均核对。冻结预测文件`results/e86/frozen_forecast.json`源自E85探索原始行为hash，差值CI仅为旧参数不确定性。主比较是两布局等权、逐context的未知Item delta-gap预测MSE（cue−Scope），不在结果后换胜负指标。

命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e86_aliases.py --model /tmp/ices_models/Qwen3-8B --out results/e86/qwen3_discovery --n 16 --seed 86001`。

首次查看科学评分/统计之前追加解释备注（运行启动后、只看过进程状态，不改变引擎/读数/样本）：Prefix的crossed query中，正确class词虽然在同Source其它码的例子中出现，但该完整code+class组合未出现；Tag条件的Mark+class组合都已出现。因此alias响应也可能来自输出组合的continuation/copying约束，而非一个独立“来源分组模块”。E86用于辨别强Source等价不变性与alias敏感解释；后续若有作用，应问影响经过何种native读取接口，而不是仅凭这一行为差宣布唯一机制。此备注未使用E86科学输出，不是初始预注册的一部分，不以看到新近邻后压缩C20。

## Pilot结果与独立确认的原拟预测

16context×8条件×16query全部完成；88.305s=.02453科学GPU·时，no-op0、full/cache误差1.47e−4nats、行和7.15e−7、mask0，同科学hash，无科学VOID。数据`results/e86/qwen3_discovery/{run,analysis}.json`，raw全部留本地。

未知Item的segregated−balanced gap：Tag **14.463 [13.055,15.826]nats**，Prefix **15.892 [14.548,17.156]**。原外推.395/.928均严重低估；Scope零预测也失败。cue−Scope预测MSE差−19.960虽有负CI，**两模型MSE都在200量级，不称胜出模型预测成功**。

segregated未知Item matched/crossed accuracy：Tag98.4%/1.6%，Prefix100%/0%；平均约50%掩盖强alias响应。已有Item的crossed：Tag29.7%，Prefix3.1%，相应balanced为82.8%/89.1%。原规则响应仍为正（未知Tag .492 [.332,.637]、Prefix .927 [.719,1.119]），且比balanced增加；输出差异不说明规则信息已消失。Source一句指令没有恢复crossed预测。输出分量不当模块证据。

**实际更新：** cue的平均增益不能从E85固定外推到“码能直接预测class”的环境。Tag同样有巨大效应，因此单纯缺失code+class输出组合不足以解释全部结果。下一项因果问题是码的预测关联怎样改变证据读取或消息内容；不是再证明Source信息不存在。

按原决策触发同源码64新context seed186001确认，所有条件/预测文件/指标保留。确认前冻结：两布局未知Item delta-gap均为正且>.15nats；matched−crossed accuracy差方向同pilot；已有Item仍alias敏感（不预设完全等效到未知Item）；一句Source指令不完全恢复。旧两模型仍原样评分，不在确认中重新拟合。量级可与pilot作确认比较，但不事后设14nats门槛；布局交互pilot CI跨0，确认前不宣称Prefix效应大于Tag。

确认命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e86_aliases.py --model /tmp/ices_models/Qwen3-8B --out results/e86/qwen3_confirmation --n 64 --seed 186001`。本段先commit再跑；这项负预测仅限制外推，不降低E85/C20原有证据。

## 人纠偏后的实际执行范围

上述确认计划与预测保留为历史，**未启动确认**。人在pilot完成后指出“控制越来越细、不太自然”，要求多读论文。此次不追加alias词表、Code K/V矩阵或训练模块；先核对这些局部差异能否帮助解释自然的多规则证据选择问题。16-context结果和冻结外推失败完整保存，不选择性删除，也不把一个强行为效应直接升级为新的计算原则。是否需要独立确认，取决于它在该问题中的用途，而非效应大就自动追加。C20/I04/正式状态未变。

图：`results/figs/e86_alias_pilot.{png,pdf}`。正文统计来自原预注册指标；图示输出分量，不代表内部独立模块。
