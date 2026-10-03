# 数据是科学对象的载体（2026-10-03）

**当前要识别：** 对同一个具体含义，模型怎样利用信号受损、说话者知识与意义先验的证据；不是制造“必须literal”的label再证模型错。原source优先；可合理改造/构造，但改造不能偷偷换掉待测对象。

## 数量、质量与自然性

- Gibson2013每alternation20 item sets×4条件；E55的400句是100独立item clusters，12800模型读数不是12800场景。E57前四类320句只有80 clusters。适合粗粒度驻留，不足证明小效应或领域统一机制。
- Chen的524参与者不能当524场景；每实验仍20critical sets。Wavelength有50concept pairs/100clues，人类4000评分不是4000不同情景。需要同时报告独立场景、条件变体、人类raters与模型重复四种数量。
- 数量依据待区分解释和预定效应，而非追齐榜单。配对效应SD、item/human异质性决定CI与power；在pilot后用未选取的全量方差做事前模拟，报告多个合理效应/方差假设，再冻结新的独立收集集。两个排列检查history噪声，不能扩大样本n。
- 原心理语言学材料是人写的controlled stimuli；Circa/IQAP是另一类自然表达。自然性、控制性与norm依据分别记录。自然的问题应落在真实表达和可信情景上，少量counterfactual只用于可区分干预；不能以大量模板替代自然覆盖。

## 改造和逐条检验

每个item记录来源/版本/hash、原文、改动、phenomenon、固定候选含义、证据改变哪一个前提、映射/标注依据、歧义与缺失。分清signal fidelity、事实真假、epistemic access、world prior、QUD与回答目标；不把partial access全部标unlicensed，不给implausible句硬造唯一gold。

现成数据不能满足时，可从原语料筛场景、增加证据条件或请模型起草变体；保留原项和变体关系，注明counterfactual构造。选择规则在模型结果前冻结；相同场景所有条件放同一split，留新的场景/表达类型作外部验证，防止模板/lexical cue驱动结果。

逐条查：原句含义、候选互斥/覆盖、证据能否区分解释、改动是否泄漏答案、是否改变任务难度或可信度、label由人类norm/逻辑/草稿judge哪一种支持。机器schema/IDs/hash可全量硬核对；语义judge必须盲于模型预测、stage和预期效应。分歧原样保存，不能多数票自动gold。确需human norm而暂无时保留“未定”，只测条件响应，不写应当/不应当或FPR。

OpenCode可用于逐条独立审计/构造草稿，使用公开语言字段、JSON schema和失败留档；不要把模型同意当可靠标签。2026-10-03新试官方longcat-2.5-preview-free仍403，0可用标注；不伪称已逐条语义审查。接口可用后先用已知阳/阴控制校验，再全量审计，结果与原gold分开存。

## 当前实际处理

E54导出400critical只白名单字段；E56全量配对核对前四类320critical、共享48 filler/48control变体，slot33只有尾空格归一，raw保留。第五类仅4/80一致，按跑前固定句规则保留为不可用配对，不因模型表现排除。公开噪声仅18句改动与正文30不符，明确release版本边界，绝不补造缺失句后称原复现。

E57是原公开exposure的有限probe，不能替代I01所需跨独立自然source的数据；任何大效果先审格式/基础理解/排列/bounds与源差，再决定下一批数据如何补足识别。
