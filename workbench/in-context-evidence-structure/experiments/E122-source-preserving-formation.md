# E122：保留上下文化时，两套来源规则能否共同工作？

- **状态：** PLANNED（2026-10-12，首评分前）。
- **类型：** 从机制提出的整体构造性预测；不搜索head/层/强度，不新增训练。
- **对应：** C21/C22/C23/C24、I04、P17。
- **问题：** 不换输出词、不切断一般上下文化，仅阻断跨来源答案→标签形成，能否在同一prefix上同时保住两名来源的不同判断规则？它与仅在query按Source隔离的作用有何不同？
- **为什么现在做：** E120三家族32确认native靶向KO贡献，而有限路径恢复native/gated方向不同；E121三家族32私有规则有可靠自然文本阳性。因此历史共享不能一概视为坏，也不能从A定向干预推断能共同支持所有来源。此实验回到整体source-conditioned规则使用，以双向对称、两Actor和不同criterion检验形成解释的构造性预测，而非磨某条边的百分比。
- **材料：** E118同一干净Food×Service四组合框架。A Food标准与私人方向固定/平衡，B criterion(Food/Service)×私人约定(同A/反A)四world；八A/八B/八新query。A raw、B输出stream、名字/位置/input multiset保持，criteria从demos推断。两人均用no/yes、不加新label。新seed122001 discovery→122101 validation，不选前轮好context。
- **操作与作用范围：** prefix三policy：(1)normal；(2)双向对称阻断过去不同Source答案区域→当前Source label word，保留同Source答案、所有输入/名字等其它访问；(3)双向对称阻断过去所有不同Source prefix访问。每个query正常全Source或仅可读请求Source位置两scope。所有层相同静态mask，无query-specific donor，整个prefix各policy形成一次供A和B请求共同使用。历史消息word＋实际separator，strict past/self保留，softmax重归一化，后继状态活演化。
- **配置：** 四world×三prefix policy×两queryscope×两Actor=48条件；single A与四single B=5条件；四world×两Actor一句按请求Source推规则=8条件，共61×8=488评分/context。Qwen3-8B、Mistral-7B-v0.3、Llama-3.1-8B、Qwen3-14B各16→32新材料；环境/revision沿E115/E119，不按阳性选模型。Mistralvalidation采用E118已校对的nasty可行材料入口，其余沿原CPU规则。
- **读数：** primary每context均匀平均四world×两Actor的candidate accuracy，各Actor独立平均同时保存；early answer-policy−normal、all-cross-policy−normal、query-only隔离−native及early+query交互pairedCI。分别保存A/B真实函数给出相同/不同gold时的accuracy，支持双函数判断而非只A涨分；所有条件full-vocabulary argmax与margin另报。Source A的B-code半差Food/Service完整功能响应按E118预定定义保存，检验accuracy改善是否也减少不需要的私有代码依赖，不以accuracy替代功能来源。
- **阳性对照：** single A及四single B/private函数、所有一条instruction；原生4D mask/default cache和full/split≤.001；单Source移除两policy均no-op，双向all-cross形成+own-only读取时B配对对A输出作用≤.001（本数据仅B world变化，不冒称测试A改变对B的影响）（graph-zero）。全部层实际mask消费、所有world几何/真值/多重集、query不同于demo；两Actor共享同一cache不被query调用改变（deepcopy指针/seq长度）。
- **噪声地板 + MIE：** FP32/eager、context-bootstrap10000/seed910；所有正/负与两Actor都报告，不能以只改善A宣称共同修复。未要求固定涨点阈值；能力阳性、paired差与功能依赖共同评价。材料、指标与policy首评分前冻结。
- **混杂审计：** targeted与all-cross移除边数量/总mass不同，实际causal edge count保留；native操作改动后全部状态演化，故只解释该计算政策、非纯latent操作。指标不得称Source ranking；gold依据声明的Food/Service/private函数，非真实人类个人偏好。固定Food先Service仍是功能而非位置无关抽象criterion；不为这一点追加词序矩阵。query-only Source mask和prefix mask是stage不同的构造性比较，不将差异命名成新独立模块。
- **论文定位：** CoSToM同一内部接口→实际使用的证据尺度；Cho的构造性过滤→原生计算操作链；CTA的信息流框架为既有基础。本实验检验形成与Source-conditioned使用的整体预测，mask技术不宣称新，是否成为方法贡献根据结果而非预先宣布。
- **算力预算：** 已缓存四模型节点独立单卡，pipeline空卡优先；每批预计.1–.4 GPU时，总≤4 GPU时；不影响他人进程，不因可用卡数添加条件。
- **决策表（跑之前写）：**

| 结果 | 整体认识更新 |
|---|---|
| early-targeted改善两Actor/冲突函数，保留一致函数，且比全cross隔离更好 | 支持选择性保护关系形成、保留一般共享的构造性解释；不要求把所有规则表示分解完 |
| query-only与early作用不同，early同时减少other-private-code功能作用 | Source位置读取与关系形成有可用的计算区别，连起MC1–MC3；不只报accuracy |
| 只A改善/B恶化或只某Criterion有效 | 不能称共同支持两规则；揭示策略条件，原形成因果主张保留 |
| targeted和全cross同样下降/不改善，query-only有效 | 当前形成功能干预不构成一般使用政策；记录原生计算与构造干预边界，不调mask追涨分 |
| single或数值失败 | 分开能力/工具与科学阴性；只修实现，不挑容易query/seed |

## 结果（运行后追加）
待CPU预检/评分；首评分前冻结。

### 实现冻结（首个E122评分前）

- 主源SHA256 `1f9455fb905f12b31c81158e8ab78c4f9eb6afa173555b91f0730181206d93c6`。无head/layer/alpha搜索；n16/32全部family按同protocol。upstream材料规则沿已封版E118/有限guard，Mistral采用已冻结nasty入口。
