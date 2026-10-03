# E58：blind-source-audit（2026-10-03）

- **状态：DONE。** 跑前协议冻结；OpenCode Ling3.1官方CLI smoke回答OK且step cost=0后才启动。
- **类型：REPRO。** 数据语义审计pilot，不是能力实验或I01决定性pilot。
- **对应：C02 / P02 / P05。**
- **问题（一句话）：** 原source的句法角色回答、世界事实蕴含与可能的语用修复是否被混在同一个Yes/No标记中？辅助审计能否给出可追溯的逐条理由？
- **设置：** E56固定语言export中每个原family用seed20261003独立选1个Item并保留4条件，共16critical；共享control独立选4Item各1变体，共4control，20条/8独立Item clusters。只传opaque ID、原句、原问题，不传源gold、条件名、family、任何模型结果或exposure。保持原bytes/hash，逐条单独调用服务器官方opencode1.18.34、opencode/ling-3.1-flash-free，默认agent、禁用全部工具和plugin，0GPU。
- **读数：** exact-event的角色回答Yes/No/ambiguous，与world-entailment yes/no/underdetermined分别输出；literal paraphrase、question role、repair possibility/reason、ambiguity、source exact quote。所有输出仅candidate audit，不升级为gold。严格JSON字段/枚举/原quote substring校对，记录raw CLI events、cost、prompt SHA/实际model/version。结果与原gold比较只在所有20条结束后做，分歧不自动改标签。
- **阳性对照：** 原active/passive controls检查谁做什么；每条literal语义的引文必须来自原句，不允许臆造上下文。smoke只验证可调用性，不验证语义正确性。
- **噪声地板 + MIE：** 非总体效应估计，无CI或显著性；20条小pilot仅决定是否值得全量逐条审计。任何无法追溯引文、schema失败、收费或持续3次provider失败均阻断扩展，保留失败；不据一次一致率冒充独立人类标注。
- **混杂审计：** 成本/免费模型状态按实际step核对，timeout75秒/条、连续3fail停止；非固定weight的服务revision未公开，记录实际ID与日期，不作为主实验。一个judge存在共享先验/任务理解偏差，仍须原人类规范或独立人工校对。原question No通常是事件角色不匹配，不能直接解释成世界中的否定事实；这是待审语义区分而非宣称所有源label错误。
- **决策表（跑之前写）：** A全部schema/source gates通过且理由可审核→考虑第二独立免费模型与全量审计，原gold保持；B有歧义/role与world不一致→记录行级flag，回原文/人类规范，禁止把flag当unlicensed gold；C模型/工具调用失败或收费→停在数据障碍，继续cached实验与原source阅读，不切付费模型、不伪装客户端绕过限制。
- **算力预算：** 0GPU·时，至多20条官方免费CLI请求，每条75秒上限，0元是扩展必要条件。**实际：** 0GPU·时，r1/r2各3失败，r3 20条全部provider成功/cost0，18 strict schema/quote有效。

## 结果
- 结果文件：待完成；原始请求/回复在外部ROOT/data/E58-blind-source-audit。
- 主张：C02仍L0；不改E55/E57原primary。
- POST-HOC：无。


执行修订（0可用annotation后）：r1全工具deny的3条全部403并按预设stop。官方issue https://github.com/anomalyco/opencode/issues/51315 报告同一CLI禁用read导致free错误拒绝；smoke native可用。r2不改源/选择/prompt/schema/模型/预算，工具权限全部ask、无auto approve，保留官方native tool定义；若模型用tool则失败隔离，headless不能自动授权。新raw目录，r1永久保留；不是伪造headers/工具或用第三方API。先复核r2能否严格完成，再决定是否全量审计。


r2结束：3条75s超时、0可用candidate；原native日志在对应session记录provider429而非403，不能称完整annotation跑通。为确认流程可用性，只允许另一个当前列为free的原生model Space Bunny一次有限r3（同20条/全protocol，small_model显式同free ID，最多连续3fail，全部ask/不auto approve）。模型与revision差保留，不混三版annotation、不当主实验；之后不反复换model刷成功。


完成：r3原20/20逐条官方CLI返回，所有step cost0、未用tools，18/20严格schema/quote gates通过；A0014为首字母case不匹配，A0019为引用question片段，原gate与raw不改。18候选中4条event-role与原源标签不同。root逐项阅读至少A0005/A0011存在忽视字面recipient/theme的理由问题，A0001涉及空间关系，A0009涉及ill-formed语义；不把candidate模型多数或一致率当真值。world-entailment也有未叙述互逆事件≠否定世界事实的混用。

决策B：OpenCode官方free路径已经真正可调用，但辅助逐条审计尚不具备自动改gold的质量。20条只8independent clusters，不给效应CI；不再换模型刷成功。之后扩展先解决源语义/独立校对标准，而非直接用free模型重标全部数据。完整结果[summary](../results/E58-blind-source-audit-summary.json)，raw/source/prompt SHA与三个版本均保留。C02仍L0。这里root语义审阅是POST-HOC技术/源审计，非L3独立校对、非论文finding。
