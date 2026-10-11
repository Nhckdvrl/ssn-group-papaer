# E100：只改变辅助来源的私人偏好，当前来源的判断会跟随什么？（2026-10-11）

- **状态：** PLANNED，未运行候选；实现完成但未启动GPU。回应用户对近期偏行为的质疑，当前优先E101原生内部因果干预；本卡保持可审阅，不据此改正式研究状态。
- **类型：** PILOT，有限功能反事实；不是新的字段/层搜索。
- **对应：** I04 / C16 / C20 / P17。
- **问题：** 固定共同标准与A的私人规则，改变B/C是否给出相同判断，会改变标准推断，还是改变A对标准的使用？

## 为什么现在做

E99新材料criterion64/64、Own+self256/256，但native mixed也达到107/128=83.6%，旧n2的59.4%弱表现并未普遍延续。现在应解释正确组合何时稳定，而非维持失败。E98接口未通过阳性，停止内部运输搜索。

本实验只改变C的合法私人偏好，不动目标问题、A/B示例或共同标准。Opposite时，抹去B/C身份后的整个foreign `(review,label)` 序列对标准c不变；aligned时，匿名foreign关系也能确定c。这使“是否必须使用来源关系”有具体可检验的差异。

## 冻结设置

- 原E99全部8个context、seed99001、新姓名/措辞及4个A-first/4个A-last全部保留，不挑错误context。完整p_A±、p_B±、c∈{food,service}八世界和四个query。
- 每个世界两条件：opposite p_C=−p_B；aligned p_C=p_B。先按E95原world固定来源分配与顺序，再仅把C的8个Label翻转。每来源yes/no频率仍4/4，A/B原文逐字不变，共同c、私人p_A与全部query答案不变。两条件都有唯一合法全世界解；A单独仍不能识别c。
- 两个Goal：criterion无新review；native为A私人yes/no，含四个新review。各条件64+256=320，两条件总640请求。无Own/cue/额外指令矩阵。
- Qwen3.5-27B，缓存别名Qwen3.8-27B，revision `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0`；openslime+vendor transformers5.12.1、torch2.9.1/cu129、bf16/SDPA；thinking medium、greedy1024，所有初始截断保留完整轨迹再续2048，剩余未知照计。
- 四个固定相邻双context分片，每片160请求。各Goal按context→p_A→c→p_B→condition(opposite,aligned)→query排序，batch8；native每batch恰是同一世界两条件×四query。四片同一fvcrc11节点本地权重、独立单卡A100，不影响其它服务。
- 两条件在同一脚本/环境重新执行；E99结果不充当跨硬件的干预基线。E99完整opposite对比只作运行背景，不据此替换或筛选本次任何回答。

## 三种强解释与冻结读数

1. **按来源抽取可共享标准：** 两条件都能先识别c，再结合p_A；C偏好本身不该改变A答案。
2. **匿名关系提取标准，再结合A偏好：** aligned也能对p_A=−p_B的新输入答对；opposite匿名关系不含c，必须另用来源关系。aligned收益本身不能证明解释1。
3. **foreign私人映射渗入：** aligned在p_A=p_B时帮助，却在p_A=−p_B时误导，特别是A自身未覆盖的mixed输入；不能仅凭整体准确率区分。

**主读数：** 两条件criterion正确/解析率；native mixed与concordant正确率；aligned−opposite的配对变化；mixed按p_A=p_B与p_A=−p_B两组分别报告、二者交互；p_B翻转改变A回答的比例；c双世界均正确率。未知保留在全部准确率/翻转分母，另报解析覆盖。全部CI整context bootstrap n8。全正确的经验区间退化不意味着总体无不确定性。

- **阳性对照：** criterion Goal检验两条件是否推断出标准；concordant检验A私人偏好是否保持。两条件已静态枚举唯一解，匿名完整序列不变/可识别与标签频率平衡均需代码核对。E95单句显式指令恢复对照已保留，本次不从单一行为probe宣布能力缺失。

- **噪声地板 + MIE：** 同脚本、同批次两条件，首8请求重复原生成forward的initial token序列必须完全一致；不增加新条件。完整640键、原始tokens、所有续写、未解析项与来源hash审计。主要读数以可区分的方向和约10百分点量级作为本pilot参考，不以2×noise或单一p值自动决定科学价值。若结果接近/不确定，报告有限区间，不继续加配置追显著。

- **决策表（跑之前写）：** 见下表。

| 实际模式 | 如何改变判断 |
|---|---|
| criterion两条件强，A aligned在两种p_A/p_B关系都改善，concordant保留 | 私人Goal利用必须借来源关系获得的标准较弱；复制foreign verdict不足以解释；匿名criterion抽取仍是强解释 |
| A同偏好改善、相反偏好恶化 | foreign私人映射渗入更符合结果，不能称共同标准恢复 |
| criterion与A同步改善 | 首先涉及来源分组下标准推断，不概括“知道而不用” |
| 两Goal都基本不变且native强 | C私人偏好抵消不是这批行为的充分解释；保留成功计算，结束本假设，不追加矩阵 |
| 方向随context变化、区间太宽或阳性弱 | 保留全部结果，解释保持有界；不筛材料或改目标 |

## 定位与混杂审计

Tang2026已覆盖任务条件矩可识别、无条件矩抵消的数学；CTA已覆盖上下文化重新加权；CrossICL已覆盖跨任务输出映射干扰；Zhu/Oermann/**Kyunghyun** Cho2026固定target改变prior数据并用Pooled MCMC区分层次迁移。论文正文定位已在运行前核对，卡见library同主题目录。本实验潜在增量是原生预训练模型不同Goal对来源关系的使用；不声称新抵消定律或首次层次共享。

翻C同时改变同评论标签一致性及匿名关联，正结果并不直接定位某个矩运算/注意力电路。A仍贡献p_A(1,1)，不能说全部demo矩为零。位置与query模板沿用E99关联，不能推位置因果律。本批为E99材料上的新干预探索，不伪称新独立确认；后续有明确机制预测时再用新材料验证。

**算力预算：** 四独立单卡，预计≤2 GPU·时；无训练。脚本`scripts/e100_auxiliary_preference.py`，原始JSONL本地，small run/analysis/audit入git。

## 结果

待运行。不改变I04/ACTIVE或C16/C20证据等级。
