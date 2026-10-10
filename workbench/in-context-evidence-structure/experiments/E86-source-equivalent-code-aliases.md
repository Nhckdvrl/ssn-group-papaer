# E86：同一Source的两个等价码是否仍共享分类证据？（2026-10-10）

- **状态：** PLANNED（候选草案，0科学运行；尚未决定执行，不代表新开方向）。
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

无。用户要求先完成具体文献调查再考虑方向；本卡只保存候选的解释分歧，尚无科学源码、预检或GPU进程。C20与I04/ACTIVE均未改变。

## 解释能否给出不同预测：静态推导，非实验结果

不能只把两个故事命名。令`r(s,k)`为Source规则对class-logit差的正确方向±1，`a(s,alias)`为segregated中该alias示例对应的class方向。E85的平均field/code分量记f/c，另有共同bias b。

- **共同Source范围解释：** 两码先归到同一Source，之后同规则证据起作用；`z=b+(f+c)*r(s,k)`。在这个强版本中，同Source同Item换等价码不改变答案，matched与crossed的平均signed margin差为0。
- **线索分别读取Label支持的解释：** `z=b+f*r(s,k)+c*a(s,alias)`。同分布每Source唯一码时与上式相同；segregated中matched是f+c，crossed是f−c，差2c。以**已冻结E85探索native均值**c_Tag=.19755、c_Prefix=.46421直接外推，预测差分别.3951/.9284nats，两布局差值交互+.5333nats。若最终跑，这些数值须先commit，不用alias结果重拟合。

这是已有检索/绑定框架在当前问题上的两个明确实例化，不是文献声称它们就是完整LLM算法。任意alias增多、Scope说明与输入支持变化都可能改变f/c；所以量级预测失败会限制这个冻结外推，不撤回E85的自身证据。共同bias在平衡配对平均中抵消的假设也要核对。

另一个解释是模型将每alias理解成不同task而非简单copying；它也可产生alias响应。本项行为实验即使成功，也只区分强共同Source范围与alias敏感版本，不能单独区分task重新划分/直接Label读取。要怎样用E85既有接口检验后者，仍需在实际样例支持下决定，不预先宣称已经锁定机制。
