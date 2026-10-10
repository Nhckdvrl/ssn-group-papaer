# E94：输入出现之前，学到的标准如何跨私人输出坐标迁移？（2026-10-10）

- **状态：** PLANNED；先冻结方法/静态预测/源码，再运行。
- **类型：** PILOT；一次有功能预测的内容干预，不扫head/rank/alpha。
- **对应：** I04 / C16 / C20 / P17。
- **问题（一句话）：** 从另一个Source示例得到的标准信息，是近似独立的criterion，还是依私人label assignment编码的规则方向；它能否用于当前来源的新输入？

## 为什么现在做，不假定已有完整规则

E93强direct已完整384行：B自身98.4%、explicit A oracle100%，A mixed约48–50%；B私人偏好flip影响约5–6%，比8B小。功能性地保留自己的偏好，不等于成功借用他人的标准。但B正确也可能是四格exemplar查找，不能据此假定criterion状态已形成。E94恰好检验这个差别；与GPU1尚在完成的thinking功能诊断是独立问题，依赖的是已完整返回的direct阶段。

从Mixing的counterfactual与Workspace的multiple-consumer swap学习：同一信号应对多个未见输入、不同接收方私人偏好给结构性预测，不能只翻一个答案。JIT与Dong已说明task state并非完整程序、位置/接口也有边界；不以一次negative否定全网络。

## 三种候选，运行前给出不同预测

对B的input前Goal字段表示h(c,p)，两个criterion方向分别是spiciness/pace，p为个人偏好。固定来源名称、文本、位置与yes/no词；仅改变demo labels。定义：

- d_p = mean_{A preference}[h_B(c=1,p) - h_B(c=0,p)]。
- d_inv=(d_+ + d_-)/2：criterion效应对B私人assignment近似不变的分量。
- d_sign=(d_+ - d_-)/2：随B私人assignment变号的分量。

| 候选计算 | 预测的有效运输方式 | 对不同recipient A偏好的预测 |
|---|---|---|
| 近似独立criterion/检索策略码 | d_inv | 使用接收方自己的偏好，不整体偏yes/no |
| criterion×私人assignment的有向规则码 | p_A*d_sign | 必须随接收方偏好变号，才能作正确的双向标准改变 |
| 主要是来源地址/输入后exemplar lookup | 两者可能都无完整profile作用 | Source-name干预可以有效，却不保证input前criterion可迁移 |

中间表示可以同时含前两者或更复杂的非线性编码；实验只检验这两个有明确函数预测的线性运输分量，不声称穷尽所有表示。运输构造用gold criterion与私人偏好做因果对照，**额外提供了坐标校准，不是原生模型已经自动完成组合或无代价修复**。不能把mean差当天然独立模块；若有效也保留criterion-conditioned retrieval/改变匹配几何等解释。

## 设置与干预

- Qwen3.5-27B实际qwen3_5_text、本地既有revision，openslime+vendor tf5.12.1，冻结无训练。为因果分量与数值对照使用float32/eager；权重约108GB，单节点GPU0/2各容纳一段，不假设跨节点高速互联。GPU1的E93thinking继续原协议，本实验不取其未完成结果选条件。
- n4新context、seed94001，原E93受控属性词池，新demo组合/顺序/姓名；query仍是未在demo中出现的措辞。不是新语言材料独立确认，不升级L2。固定同一方面关系；A8同向例、B8四格例；A偏好±、B criterion±完整交叉。主recipient p_B=p_A，故recipient两Source现有函数相同：纯地址选择不能在完整四格上产生另一个标准。
- 先在**测试Input未出现的截断prefix**上计算`Reviewer: name`整个Goal字段；donor请求B，c_B、p_B、p_A全交叉，cb的delta在同姓名、同位置、同文字上估计。未来评论/答案token从未进入donor prefix；token前缀及字段对齐必须在load前核对。
- 64层的固定三个输出band（1-based16/32/48），在recipient当前A Goal字段加(+/-)d_inv或(+/-)p_A*d_sign；符号将当前c_B翻向另一标准。下游评论、自己的labels、全部demo与source-name字面文本仍为recipient。每band一次局部residual干预，不改变hybrid历史mask/linear-state、不伪造Source-exclusive cache；更高层自然重新计算。
- 对每context、两个当前criterion×两个A偏好×四个新输入：native；每band inv/sign及相应同norm随机方向（固定seed940）；另在p_B=-p_A的recipient做A Goal整段换B Goal的source-name运输阳性，及两个请求Source的native读数。全行保留，不筛正确项。每个真实criterion分量同alpha=1，报告各自norm，不放大微小均值/训练方向/扫alpha。
- **一句指令恢复：** E93同材料已登记/跑过；本机制pilot不据纯提示行为单独声称能力。explicit oracle与B primitive已在strong direct阶段完整通过，不称这些证明内部完整criterion。

## 读数与对照

- **读数：** z=yes-no；criterion运输T=mean_discordant g_other*(z_patch-z_native)/2，同时报告两个criterion方向×两个recipient偏好的四个profile、concordant gold及扰动、全词表argmax准确率/label率、native/current-rule与counterfactual-rule准确率。必须在两个相反mixed输入上有相反答案作用、并保留concordant的私人偏好，才能叫功能criterion响应；单一常数label偏置不够。
- **主对比：** inv与随机同norm、sign与随机同norm；sign与inv在固定三个band均完整报告。直接给nats与accuracy，不除弱native gap/按最大layer外推全网络。4context bootstrap10000次seed940，只是pilot区间，不据n4狭窄CI宣称普遍律。
- **阳性对照：** actual native B的新输入预测、给定criterion的既有oracle；A→B Goal整段交换对B私人函数的有向响应。source-name阳性是接口诊断，不是独立抽象ID/criterion。
- **噪声地板 + MIE：** 全batch self-copy同层同字段误差≤.001nats；token-prefix对齐、全部边界、非Goal字段未改；Source-name native比较。T约.15nats/5百分点且四个profile一致会改变投资，非自动判死。若数值失败保留并先修同样的执行，不改seed。
- **混杂审计：** p_B与criterion正交、A私人偏好双向、query未来不可见、私人映射/功能类型分开；名字位置同但整体差分仍可含多个计算。随机norm不排除所有离流形效应；mean分解只是两种transport模型。确切继承p_A的额外乘法由实验者提供，不能归因原生已有乘法电路。SourceB正确可经近邻查找，Goal状态negative不证明函数知识不存在或不重要。

| 结果 | 会怎样改变判断 |
|---|---|
| inv有四profile作用且sign不能相同复现 | 学到的可迁移信息有private-assignment不变的功能分量；再独立确认/recipient证据竞争，不叫完整program |
| sign有四profile作用且inv弱 | 有用信息的运输依赖私人输出坐标校准；不能说独立criterion没有存在，但可具体检验joint code解释 |
| 两者均有效 | 两种分量共存，不能强择一；按新输入分布的预测与非线性替代解释推进 |
| 两者均弱、Source-name阳性 | 此input前field/三个band不能迁移相同功能；保留输入后lookup/JIT/非线性解释，结束该局部矩阵 |
| Source-name及两方向都弱 | 当前接口的functional scope不清；不添加一套位置/alpha搜寻来包装negative |

- **算力预算：** 单节点两卡，总≤2 GPU·时；实际待运行。
- **资产：** `results/e94/qwen35_discovery`；raw prompts/contexts/behavior/activation本地，小run/analysis/preflight/source入git。

## 结果（以后追加，不改冻结协议）

未运行。C16/C20仍L1，I04/ACTIVE状态不变。标准信息的载体、因果运输与原生实际调用不混同。


### 2026-10-11运行前记录

设计于10日，token preflight于跨日后完成：4新contexts，每个8 donor，Goal字段恰3 token，prefix491–510 token；同一prefix对应四个未来Input，donor取截断prefix，未来Input/答案从未进入。模型实际64层，固定band16/32/48不变。static countermodel四个profile也已保存。科学GPU尚未启动。

执行第一步用float32/eager双卡以分开数值误差与很小的运输分量；scientific rows预计每context304，共1216：四native组各16（64），三个band各四criterion/random operator×16（192），Source-name三band×16（48）。Prefix donor每context8个另行前向，只用于构造方向。原始模型分段加载不涉及训练/高速跨节点集群。

E93thinking最终已返回：120/128 native、oracle32/32、probe29/32，全部7截断已续完；其11错误完整保留。E94依赖的direct阳性不变，未依据thinking成功项筛选本实验材料或band。
