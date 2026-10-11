# E110：标签身份完全不变，学到的外来源关联还能改变本来源证据吗？（2026-10-11）

- **状态：** PLANNED
- **类型：** PILOT / 对E109消息的功能内容反事实
- **对应：** I04、P17、C16/C20。
- **问题（一句话）：** A标签继承的是外来源答案词的身份/位置先验，还是这些词与输入学到的关联？
- **设置：** Qwen3-8B固定revision、FP32/eager，16新context seed110001，MHS独立未选择抽样。A/B各8demo、8query；两组B quartets各含2race/2gender且完整prelabel token长度相同。原始B与A规则相反；在B固定label、固定Source/位置/所有非评论token下，对换race/gender文本使B规则与A对齐。阴性反事实在同类别内置换文本：同样8个B输入位置都变，同一输入多重集与token长度，但私人规则不变。A全部raw token固定。全部query位置禁读B。
- **读数：** 原始→跨类别换配对的signed margin与绝对幅度，对照原始→同类置换；仅A label KV移植的功能作用；B答案KV/K/V经A label形成边的作用与同类置换对照。context bootstrap 10,000，不能按方向选context。origin/cross/within gate、full-A cross、label cross/within、answer-edge cross KV/K/V、answer-edge within KV、三world一句instruction＝13×8×16＝1664评分。
- **阳性对照：** 全A-cache cross→original精确等于cross gate。label-cross为功能下游阳性。edge self-copy≤.001。全部world的Source字段、标签词、位置、词频、评论输入多重集与每block token长度一致；变化只在B评论content。B答案载体第0层K/V必须完全相同（排除改其静态embedding/位置）。源cache指纹不变；干预只在A label作为receiver，输出端仅复制A label K/V。
- **噪声地板 + MIE：** 全FP32、保留数值与cache核对；same-class permutation不是零噪声而是同强度文本置换对照，不能先假定其为零。关系反事实明显大于同类置换、且A label与B答案形成边功能一致时，冻结32新context seed110101确认；无头/层/词表搜索。
- **混杂审计：** 对换输入天然改变其位置，而这正是输入—输出配对的一部分；same-class对照控制文本/位置交换的非规则效应但不保证每条文本难度相同。各context共用完整输入集合，每条都在三world出现。两个Source私人规则为实验定义，不是MHS真实标注。B标签位置K/V已上下文化，效果不证明完整抽象程序、独立criterion或不依赖检索；它严格检验固定答案词身份下的关联内容。
- **决策表（跑之前写）：**

| 结果 | 更新 |
|---|---|
| 改配对影响大于同类置换，A label与B答案边转移此影响 | 支持标签载体传递学到的关联，单纯静态标签身份/位置不充分；结合E109回答namespace怎样改变这条形成路径 |
| A label有作用而B答案边弱 | 关联经其它形成路径进入，不把E109 namespace接口叫通用关联机制 |
| 同类置换同样大或方向无结构 | 当前材料的文本/位置改变未识别规则关系，不包装成程序信息，不继续细分latent |
| 原生rule效应弱、接口失败或数值失败 | 保存、修执行或回看理论；不由transport阴性说整个模型无规则学习 |

- **算力预算：** discovery＋可能确认≤1 GPU·时，单卡。**实际：** 待记录。

## 为什么现在做

E91/E106/E108已表明Source正确访问之后仍有外来源依赖；E109的namespace消息交换可能混入答案词本身变化。CTA §3.2用token身份与功能关系反事实区分传递内容，Mixing Mechanisms用反事实让pointer/answer竞争。这里借鉴这一研究动作，把**label stream固定**、仅改变示例配对，避免以重算了某个KV就说它存规则。E109有有效形成消息接口时才运行；没有则先重新理解，不卡死在这张卡。

## 结果（运行后追加）

待运行。

### CPU构造校对（科学运行前）

仅匹配完整pre-label token长度仍未固定comment尾部与换行的token边界，CPU preflight发现content index不同（总长度/Source roles/label anchors已相同）；0 GPU科学记录。构造改为同时匹配token长度、content位置与content外token身份，再抽quartets。该选择仅根据输入/token几何，不看模型输出；全部n与seed保留。不能将仅等长当完全等编码。
