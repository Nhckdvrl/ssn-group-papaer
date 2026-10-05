# E09：原始人类理解题中的cue与任务顺序（2026-10-05）

- **状态：** DONE
- **类型：** MEASUREMENT / 原始题目迁移
- **对应：** C01 / C02 / P03 / P06 / P07
- **问题（一句话）：** E01角色问答的失败，能否迁移到原始人类理解题，还是依赖自构的元语言读数与答案位置？
- **设置：** Qwen3-8B固定revision，FP32 frozen/no thinking/no training。Huang SAP固定15e61066d510b5349e17740e6488c976abc3e1ac，MIT；只下载并审计5个小文件，总计约84KB，不下载1.2GB全repo。原Excel ClassicGP 72句题×GP/显式cue=144记录：24 lexical sets、NPZ/NPS/MVRR各24。原问题、两答案选项、作者gold不改；8固定配置（句先/题先×无/一句revise×选项A/B对换），1152任务。neutral native boundary；无few-shot/prefill。
- **竞争解释：** 结构revision失败预测原始、针对歧义的题目仍有cue−GP差异，且不只依赖选项字母；元语言问答/回答默认值解释预测E01极端role失败不普遍迁移、目标与非目标题或选项位置呈不同结构。仅重复已知GP效应不构成novelty。此处不同数据集的题型迁移不是同item因果读数比较，不据跨数据差异排除词汇/材料混杂。
- **读数：** 每family×作者歧义目标/其他×原gold Option1/Option0×八配置：correct、P(correct)、P(source Option1)、choice mass；配对cue−GP、cue×query-order、同题选项对换。全72 primary，target flags分别按原Excel与CSV报告。全量paired bootstrap10000/seed20261005；pooled先在同lexical set内平均三构式，再按24sets抽样，不能把72当独立词汇。
- **阳性对照：** 显式comma/that/unreduced；作者标为非歧义的原题；gold Option1/Option0与两字母mapping；一句generic revise。No/Option0正确不直接代表彻底修订。
- **噪声地板 + MIE：** 已知FP32重复max约2.6e−5、0 flips；效应与CI用于比较解释，不设停止accuracy阈值。稀疏分项同时报告n，n=1 CI=null。
- **混杂审计：** 原Excel/CSV 72句题、选项和gold逐字段相同，6个ambiguity-target flag不同（34 vs40标记），保留来源标签，不自己重标。题型/答案极性不是随机化的，分层而非假定等价；12原题不是Yes/No，用其原选项，内部gold Yes/No只编码source Option1/0，绝非语义真假。无新增句题语义标注；固定原文与来源blob SHA1/SHA256核验；共享schema检查。人类preprocessed数据在另一个Drive链接，本次未下载，不能宣称已作逐item人机比较。
- **决策表（跑之前写）：** 原始目标题呈稳定cue/order差异且选项mapping一致→与E01语言操作结构并列，追具体修订后果；原题基本不见role式失败→优先校对自构角色读数，追加同item自然提问的独立外审；mapping主导/目标与其他题同样反转→继续处理回答策略，不能宣称parse/revision机制。保留全部分项，不挑题或prompt获胜者。
- **算力预算：** GPU2独立单卡，预计<0.08 GPU·h；复用已有环境和local model；下载全部直连。**实际：** 70.03s / 0.01945 GPU·h。

## 结果（跑完后填写；不改上面的内容）
- 数字（含CI）：1152/1152任务。pooled cue−GP句先：Opt1=A +33.33 pp [22.22,44.44]、Opt1=B +19.44 [11.11,29.17]；题先+13.89 [4.17,23.61] / +4.17 [0,8.33]；cue×order交互+19.44 [8.33,30.56] / +15.28 [5.56,25.00]。原始材料也存在GP/cue行为差异，不全是自构role问句。
- family all24句先两mapping cue效应：NPZ +25.00 [8.33,41.67] / +20.83 [0,41.67]，NPS +8.33 [0,20.83] / +4.17 [0,12.50]，MVRR +66.67 [45.83,83.33] / +33.33 [16.67,50.00]。题先效应减弱。作者target题驱动差异、其他题多数近0；NPS仅4个Excel target set，不能据小分项推普遍弱效应。
- 异常保留：题先pooled GP两mapping正确率55.56% / 76.39%，对换差−20.83 pp [−33.33,−8.33]；explicit cue也69.44% / 80.56%，差−11.11 [−20.83,−1.39]。标签/access混杂仍明显。多项读数源于No/Option0题，不能直接叫建立了最终结构。
- 结果文件：[完整统计](../results/E09-summary.json)、[scores](../results/E09-scores.csv)、[config](../results/E09-config.json)、[所有配置图](../results/E09-cue-effects.png)、[来源审计](../results/D0-SAP-source-audit.json)。
- 按决策表执行了什么：依自然题继续确认language cue效应，同时先追E09中选项和问题一起移动的混杂；下一项拆question位置与option位置，区分提前任务影响、问题访问和选项访问。已知GP效应只作measurement，不能作为paper novelty。
- 主张变化：无预定升级。
- POST-HOC：无。
