# E53：lossless-role-format-audit（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2 instrument审计；明确POST-HOC，非独立发现
- **对应：** P02/C02；不新增能力claim
- **问题（一句话）：** E49严格概率列表floor失败有多少来自可无损表示的格式，多少仍是源任务/位置/语义错误？
- **设置：** 全8endpoint/8640既有raw，不重跑GPU、不修改source/prompt/原parser/原主评分。动机来自已看见的Q3-4代码围栏与Mistral数字字符串，不能冒称结果未知。新secondary仅允许整个输出唯一完整JSON list，可选完整json代码围栏；可将标准非负整数字符串/有限整数值float无损转int。正确长度/0–100/总和100/完整EOS仍必需。额外prose、多个list、非整数、未EOS全部拒绝；不能抽取任何解释中的数字、四舍五入、重归一或修补不合法点数。
- **读数：** 原strict与secondary可用数量、编码类型、三身份无歧义全部source/位置控制、全部item/missing bounds、joint-role诊断。沿用E49统计与uniform-prior假设；显式自报概率仍非真实speaker policy/模型知识，不将lossless恢复叫能力提升。
- **阳性对照：** 跑前固定normalizer positive/negative案例，原strict raw prediction逐行重新等于原parse，source/input/raw/独立LP gates全部复用并核对。旧E49结果不可覆盖。EOS门保持，不因secondary成功过滤任何原item；fences/numeric representations都是真正唯一list才接受。
- **噪声地板 + MIE：** 确定性CPU，原item bootstrap2000 seed0，不新增随机seed；格式审计后仍需跨任务/readout边界才能讨论scientific object。95%floor只是既定诊断，不自动kill或upgrade。
- **混杂审计：** 这是事后编码层分析，结果不满足独立确认。解析接受不等于按原格式要求合规；semantic floor与format compliance分别报告。不能覆盖primary、挑可用source或用一个game跨role gap写story。照片/练习未迁移、human speaker norm缺失等原限制全部保留。
- **决策表（跑之前写）：** A可用恢复且控制通过→主要格式限制、恢复可审的secondary语义读数但不升级；B可用恢复但仍source错→源任务/位置问题仍在，不称格式全解释；C大量输出仍截断/解释→协议不可用；Djoint关系未跨E50保留→读数边界，不局部加prompt。所有结果保留，0新GPU证据。
- **算力预算：** CPU≤5分钟，0GPU/API/judge/标注外包/子agent。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

尚未计算secondary。原E49 strict floor结果已知，POST-HOC明确；原数据和主读数不改。

完成：6阳性/15阴性固定parser案例通过；全8640原raw/source/token/EOS/原strict prediction/numeric gates逐行复核；结果results/E53-lossless-role-format-summary.json，编码类型results/E53-role-transport-kinds.json。OL SFT/DPO、Q3-4、Mistral原strict可用0，secondary恢复1079/962/1038/1067（各1080分母）；Q3-8另恢复5，其余0。无损格式确实解释大量invalid，但未解释全部任务失败：listener controls三身份分别OL SFT15/17/12、DPO12/12/12、Q3-4为32/33/33、Mistral26/26/25（各36）。没有endpoint三身份全过既定floor；near-floor Q3-8/14仍35/35/34，未按heuristic自动判死。

原primary完全不改，原completeEOS/falseword evidence/missing全部保留；恢复概率表示不等于format compliance，也不当独立能力提升。joint距离含大量zero evidence undefined，全部bounds报告；未与E50形成可解释的跨readout finding。不筛source、不加prompt，C01/C02仍L0。
