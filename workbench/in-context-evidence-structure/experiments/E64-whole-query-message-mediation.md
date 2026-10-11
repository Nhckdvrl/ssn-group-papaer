# E64：来源条件化是否先在query内部完成，再传到答案末位（2026-10-10）

- **状态：** DONE（2026-10-10；发现、预定独立确认及有界复现完成）
- **类型：** PILOT（E63的必要边界检验，不将末位阴性等同完整path阴性）
- **对应：** I04、C12/C13；E63末位label冻结后synthetic仍保留约69%来源效应。
- **问题（一句话）：** 末位之外的query位置是否先读取label证据，从而使“答案末位的attention几乎不用来源”成为不充分的机制诊断？
- **为什么现在做：** E63只冻结最后token的label消息；剩余效应既可能是post-retrieval调制，也可能是其它query token已读过label。两种解释不能靠最后token的attention/负干预区分。
- **设置：** E63原生eager消息分解协议，将冻结范围从final-token扩到**所有query token**，prefix不改；记录query来源名字token与最后Label冒号token的按来源label attention份额。分层/组件条件全沿用E63，不选择头或token峰值。为严格scope对比，在同一batch/context同一代码中成对运行两scope。
  - discovery：64synthetic animals/fruits yes/no seed64001 +48real E56 train pool seed64002。
  - confirmation：64synthetic occupations/vehicles toxic/safe seed164001 +48real E56 test pool seed164002。
  - 两scope使用同样context、source-K、base组件及全部预定冻结条件；no-op/all-output阳性；只改scope。实现`scripts/e63_message_mediation.py --scope final|all_query`，不是额外模型训练。
- **读数：** relative remaining source effect、raw margin、paired context bootstrap95%CI；final−all_query remaining fraction对比；全层label attention份额曲线（不选峰值）；源名token与最后token之间的source attention差。机制主读数是消息冻结，attention只为辅助。
- **阳性对照：** 两scope native base/sourceK结果应逐位相同；no-op/all-att冻结logit误差≤0.10nats；完整attention重建RMS<0.02；全query freeze不是新增输入信息。
- **噪声地板 + MIE：** E63修复后完整重建RMS=0；full-query相对final多移除≥0.40来源效应（CI不跨0），且全query剩余≤0.30才认为“早在query内部读取label”是强解释线索。剩余高不自动证明post-retrieval：prefix非label载体可能带来label信息。raw donor效应≤0.2不归一化。
- **混杂审计：** 同context同代码scope配对；无训练/无gold读出；查询source单token检测与pad位置核对；真实池独立；全层全头报告；未控制：prefix其它位置可能已经拥有label信息；冻结整query label消息会改变输入编码，不能定位具体head/path；需要独立path校对才能宣称新电路。
- **决策表（跑之前写）：**
  - final保留、多query冻结移除 → 最后token读数漏掉query内部检索；将source-conditioned ICL研究对象扩到整个query计算，拒绝“native不用source”的解释。
  - 两scope都保留、name-message冻结移除 → 更支持其它位置/读出调制，查prefix relay而非label-only路径。
  - 各冻结均部分、all-output阳性 → 多消息协作，不作单一路径结论。
  - scope改变base或数值控制失败 → 修harness/VOID，不解释机制。
- **算力预算：** ≤1GPU·时；**实际：** 0.158 GPU·时（单卡进程墙时折算，含加载，非积分利用率）。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 同一context两scope base/sourceK逐位相同；所有原生重建/no-op/all-att controls误差0。
- 独立synthetic确认：label冻结后的效应余量 final=0.471[0.438,0.508]，all_query=0.061[0.027,0.094]；paired差0.410[0.373,0.450]。独立真实评论池：0.527[0.476,0.581]→0.054[0.001,0.102]，paired差0.473[0.426,0.525]。
- Mistral复现给出重要边界：final已仅余0.127[0.089,0.165]，all_query余0.078[0.040,0.113]，paired差0.049[0.033,0.065]；label retrieval时序不能从Qwen泛化。
- 两家族name消息：只冻结末位几乎仍余1，冻结全部query降到约0，支持来源消息主要通过答案前位置传递。
- 结果：`results/e64/*/analysis.json`；小汇总`results/e58_e64_summary.json`，图`results/figs/e64_query_scope.{png,pdf}`。C16新增L1；目前是native消息依赖/时序边界，尚非完整binding电路或预测理论。

### 启动修正（2026-10-10）
首次扩展query-site记录遗漏NAMES导入，在首个context打分前NameError；无科学读数。补入导入后同种子重跑，日志保留`*_startup_failure.log`，不改变设计。

### 跑前有界复现（2026-10-10）
Qwen discovery两scope native完全一致且full-query去除大部分来源效应后，在Mistral-7B-v0.3上复制synthetic discovery(seed64001,n64)两scope，回答该测量边界是否Qwen特有，不新增更多模型/数据轴。
