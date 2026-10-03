# E40：natural-commitment-source-audit（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1，CPU原资产与human过滤复现；本卡不授权新GPU读数
- **对应：** C02/P09
- **问题（一句话）：** 2026原研究的字面/隐含真假交叉、分target的commitment/trust和原人类norm能否完整重建，足以辨别“意图归因”与“世界真值”的作用？
- **设置：** Braun/Shetreet Language and Cognition 2026 DOI10.1017/langcog.2026.10110；OSF unmy6原三xlsx、Rmd、PsychoPy设计及stimuli发布版本，download manifest保留id/hash。只用原parent代码的participant错误>2及ans_match=1过滤；不做judge、不新标gold、不调用API。逐experiment分开，不pool三种语义对象。
- **读数：** source计数、attention/target范围、全stimulus/question/truth唯一key、过滤后参与者与目标trial对论文的parity；原human cell means分literal/meaning/trust，CI仅先描述，主mixed模型未运行不能叫系数parity。Exp1原paired-t探索性结果作为可重建数值对照。模型尚未推断。
- **阳性对照：** 原论文286?不适用；本源Exp1/2/3应为91/93/85保留参与者、目标trial728/744/1360，再剔20/41/107误解trial（最终708/703/1253）；任何不符必须查attention/过滤/版本，不修改筛选救parity。
- **噪声地板 + MIE：** CPU确定性重复与sha；原participants不是LLM seeds，fixed human subgroup不筛。源缺图文或alltruth cells不能对齐就没有LLM实验有效性；无minimum paper效应。
- **混杂审计：** 部分原dialogue在jpg/png，禁止按question/gold补造对话；需完整原图的保真转写、source SHA与逐条审计才可给text模型。Exp1自报intended meaning与Exp2仅actual event措辞不同；承诺意图、后验事件、个人可信度各自保留。Exp3主观/客观换措辞不是纯subjectivity唯一变量。human已条件化正确理解，LLM错误不能随意过滤提高分数。原图片页/attention未知，全部核查。
- **决策表（跑之前写）：** A原过滤/count/图文/questions全可重建→另写GPU实验卡，先原协议；B部分asset缺失/需OCR但未审→只报告可行性边界，不造context；C混合模型/数据版本不一致→隔离对应结论，保留可核原norm；D纯主观维度不能支持原问题→将对象分开记录，不生硬SDT化，不自动关线。
- **算力预算：** CPU与小源下载，无GPU；原xlsx合计<0.5MB，原图片按研究数据获取，不下载额外benchmark填卡。实际见结果。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
原source字段审计进行中；本卡不包含LLM实验，C01/C02保持L0。

2026-10-03 CPU驻留完成：原三实验保留91/93/85人，正确理解后的703/703/1253行。Exp1论文708而release703，paired t也不符，未改过滤挽救。Exp2原64commitment条件与703human逐字段匹配，原meaning源码OLS三非截距系数9.26825/2.98206/18.28481按论文舍入精确一致；可执行复建见 results/E40-rebuilt-human-analysis.json，不称R mixed parity。八原jpg按图保真转写并再次目视检查，完整图片SHA/代码/表SHA已在E43 preflight。未独立人审，不能L3。E43是另卡模型协议迁移。
