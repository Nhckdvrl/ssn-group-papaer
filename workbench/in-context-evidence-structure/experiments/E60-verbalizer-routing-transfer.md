# E60：标签词是否改变来源选择，以及这种变化能否经非标签 key 转移（2026-10-10）

- **状态：** PLANNED
- **类型：** PILOT（由E58/E59逼出的预测，不训练adapter）
- **对应：** I04、C13；E56c的词表依赖解释；E58不同任务/词表的准确率差尚有混杂；E59来源作用由name-key传递。
- **问题（一句话）：** 固定完全相同的(x,source,label-index)三元组，只换所有来源共用的二元标签词，来源条件化是否改变；只移植来源名字位置的K能否转移这种行为，而不改变任何label value？
- **为什么现在做：** 在E58/E59中，独立任务与词表同时变化，不能将准确率差归因标签。E59又表明来源作用不是主要由标签锚点的来源成分中介。因而“词表只改变输出读出”与“词表也改变来源选择程序”产生不同可检验预测。这比继续确认泄漏更有信息量。
- **设置：** Qwen3-8B frozen；两个全局词表yes/no与toxic/safe（两来源始终共用词表，不增加来源信息）。每个context在两词表中使用相同inputs/source顺序/label-index/query；每label单token，source/name/key位置逐位assert，候选数均2，token数等同。标签index保持一致，词汇预训练语义是操纵变量而非假装已排除。
  - discovery：64 synthetic animals/fruits，seed60001；48真实E56 train-pool上下文，seed60002。
  - confirmation：64 synthetic occupations/vehicles，seed160001；48真实E56 test-pool上下文，seed160002。两阶段词表操纵完全相同，不依据discovery选择“好词表”或方向。
  - 每词表default、one-sentence instruction、single-source参照。
  - 每方向移植匹配context donor词表的source-name K、source-name V、label-prediction K（同样16位置）、label-anchor K。target的values/query/输出词不变。no-op/full自身cache重复对照。两方向全部报告。
- **读数：** accuracy + source-correct margin，配对context bootstrap CI；词表default差，single-source差，source-conditioned收益(default−single)差（不以logit标度直接比较不同词表能力）。跨词表patch相对于其target base的accuracy/margin差，比较nameK与其它位置control。不事后挑最佳层/头，所有层同时移植为粗粒度pilot。
- **阳性对照：** no-op相同；source-swap改变答案（E59已量到）；单来源baseline可识别性；labels/token位置同一；跨词表不是直接改logits也不提供真实querylabel。自定义label编码规范化到相同index。
- **噪声地板 + MIE：** 前两卡no-op=0nats；effect>0.05accuracy且配对CI不跨0，或>0.2nats且CI不跨0才作为明显作用；必须在确认材料复现才讨论稳定边界。不满足只报告有限/无证据。
- **混杂审计：** 内容/任务/频率/输出候选数/token数配对等同；两词表同一单来源参照；一句指令control；无训练/无幸存种子；real上下文 train/test池分离；所有层、所有预定方向报告；未控制：词汇先验是操作变量；hybrid K移植同时改变历史上下文任务信息，不能直接叫纯source方向；高维换词key mismatch可能降低效果，因此negative transfer不等于来源完全独立。
- **决策表（跑之前写）：**
  - 同一任务词表影响mixed多于single，且nameK移植转移行为 → 来源选择也受verbalization影响；“分开标签只在读出分隔”不是完整解释，继续测试任务程序选择。
  - 词表差明显、nameK无有效转移，而labelK/单来源差解释差异 → 优先输出几何/任务解码解释，别包装为新的来源路由。
  - 词表差不明显 → E58跨设置差主要来自任务/材料，取消该线索的中心地位。
  - discovery有效、confirmation不复现 → 只报告边界或无稳定解释，不扩展扫模型。
- **算力预算：** ≤0.5GPU·时；**实际：** 待填。本地conda verl-clean。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 待运行。
