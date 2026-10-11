# E99：共享标准功能链的独立材料确认

- **状态：** DONE；576条完整，独立结果审计通过。运行前提交 `4508ed0b`，loader元数据修复 `b39293bb`；独立于E98接口成败。
- **对应：** I04 / C16 / C20 / P17。
- **问题：** E95–E97的共同标准推断与私人判断区别，能否越出原n2、A-last发现材料？
- **类型：** 固定功能预测确认；不添加模型/格式/层矩阵，不以失败持续存在为成功标准。

## 设置

Qwen3.5-27B既有revision，bf16/SDPA、openslime/vendor tf5.12.1，medium greedy1024；每条初始截断均原前缀续2048，未知保留。n8、seed99001，context偶数A-first、奇数A-last，各4；按相邻2context固定4分片，每片一先一后。完整p_A/p_B/c的8世界、不筛种子/成功项。原E95匿名input-label不变与唯一合法共同criterion的静态枚举必须通过。

新姓名三元组：Dana/Evan/Fiona；Gavin/Helen/Ivan；Julia/Kevin/Laura；Marco/Nina/Owen；Paula/Quinn/Rita；Simon/Tara/Victor；Wendy/Xavier/Yvonne；Zane/Maya/Noah。每组三人角色由固定seed随机排列。

新demo模板（f=spicy/mild，s=quick/leisurely）：
- food：The dish came with a {f} seasoning. / The cook prepared this plate in a {f} style. / The meal's flavor was distinctly {f}. / The food on the table was {f}.
- service：The waiters maintained a {s} serving pace. / The table received service at a {s} tempo. / The staff's delivery of the meal was {s}. / The serving process moved at a {s} pace.
- query food：For our main course, the kitchen chose a {f} preparation. / The dish we sampled had a {f} taste. / Our plate arrived with {f} seasoning. / The food we received was {f} in flavor.
- query service：The pace of our table service was {s}. / The service during our visit proceeded at a {s} tempo. / Our table was served at a {s} pace. / The service we received was {s}.

query模板按context%4，每context四格只改变属性值，属性句序固定RNG。不用真实数据/新任务泛化包装；这是未参与挑选的合成材料、姓名、布局组合。

**运行中独立设计审计：** query模板与A-first/last按同一context奇偶分配，二者没有独立交叉。本次主要检验整体功能链是否在新材料成立，不能把位置分层差异解读为位置的因果作用；保留冻结设计及全部材料。

## 三项冻结请求及读数

- Thinking native：256行（8context×8world×4新review）。
- Thinking criterion：64行，无未来review，问共同标准food/service。
- Own+self direct：256行，A原8例+本次模型自推criterion；不给私人偏好，物理删B/C并重新forward。所有parent均传递，错cue不换gold，unknown写unavailable。

**读数：** criterion正确/解析率；native mixed/concordant/整体准确率；Own+self实际规则准确率、cue执行准确率（全分母unknown=0及有cue条件分母均报）、cue coverage、concordant私人偏好保留；paired c-world正确率与p_B flip。置信区间以8context为bootstrap单位。完整行数/parent/unique prompt均报：p_B等价时Own prompt重复，不当独立样本。

**阳性对照：** 原E96明确criterion接口已成立；本次criterion Goal与Own自cue执行互相约束，错标准与执行错误分开记。原E95单句恢复指令direct无恢复，已保留；本次不从探针单独宣布能力缺失。Native thinking与Own direct的差异不是只改变cue的因果增益。

**噪声地板 + MIE：** tokenizer标签/解析与E95一致；direct首batch重复forward≤1e-3；静态世界、new query未见、A位置平衡、全部576唯一键/64parent和续写前缀完整校验。重点确认完整功能模式，不以小分差命名新机制。

## 决策表（跑之前写）

| 结果 | 更新 |
|---|---|
| criterion强、native mixed弱、Own按cue且保留p_A | 功能链在新材料确认；仍需E98等原生因果解释，不能只靠更多重复 |
| native也稳定强 | 旧n2差别未稳定推广；以正确计算为研究对象，不筛掉成功材料或把它写成支持失败 |
| criterion弱 | 标准推断本身受材料影响，不说‘知道而不用’；错cue传播和执行分开报告 |
| criterion强而Own执行弱 | 标准文字接口未独立稳定确认，不以旧接口阳性强保机制 |

## 文献定位与算力

JIT/Cho/representation-deployment研究已有宽区分；当前只验证多个私人来源推断共同标准再与自有偏好组合的具体功能事实，不宣称新任务向量/新prompt方法。E98另行检验内部运输。

四个独立单卡分片，同一节点本地权重，避免反复读共享盘；预计≤3 GPU·时，不训练、不扰动已有服务。脚本`e99_confirm_factor_interface.py`；原文/生成tokens本地，分片run/analysis与合并audit入git。

## 完整结果与按预设更新

| 读数 | 结果 |
|---|---|
| criterion | 64/64 |
| native mixed | 107/128＝83.59% [68.75,96.09] |
| native concordant | 128/128 |
| native整体 | 235/256＝91.80% [84.38,98.05] |
| Own+self mixed / concordant | 128/128 / 128/128 |
| native c两世界均正确 | 45/64＝70.31% [43.75,93.75] |
| native p_B翻转改变回答 | 7/128对＝5.47% [1.56,10.16] |

576唯一键、64parent全部保留；39初始截断全部续完，0未知，四片no-op误差0。Own256行实际128个unique prompt，保留重复但不计成256个独立材料；CI为n8整context bootstrap。全成功项经验区间[1,1]退化，不代表总体无不确定性。实际.83824 GPU·时，另有两次打开科学输出前的loader元数据报错，未产生科学行；原日志保留。

**科学更新：** 标准推断与“标准＋自有偏好”功能链在新材料成立；原生私人判断本身也已较强，旧n2的59.4% mixed不能作为稳定普遍弱表现。既保留成功计算，也保留21个错误。Native thinking与Own direct差异不是只添加cue的因果效应，不据此宣布内部标准已经存在或发现新电路。C16/C20仍L1，I04/ACTIVE不变。

**POST-HOC描述：** 21个native错误全在A-last四context，mixed43/64；A-first为64/64。位置与query模板关联已在读结果前记录，不能把此差异直接归因于位置，亦不扩顺序矩阵。

下一步是E100有限干预：保持A目标与共同标准，只翻转C私人偏好，比较标准推断和私人应用是否跟随匿名标签一致性。保留E99全8context及所有成功项；不挑错误材料。

**结果/复核：** `results/e99/merged/{analysis,completeness_audit}.json`，四片`run.json`；独立agent逐行重算gold、parent、prompt/body hash、分母与区间，未发现影响结论的问题。原始生成tokens/text与JSONL留NFS，不进git。
