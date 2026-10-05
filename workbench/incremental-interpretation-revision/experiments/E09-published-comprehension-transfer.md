# E09：原始人类理解题中的cue与任务顺序（2026-10-05）

- **状态：** PLANNED
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
- **算力预算：** GPU2独立单卡，预计<0.08 GPU·h；复用已有环境和local model；下载全部直连。**实际：** 待记录。

## 结果（跑完后填写；不改上面的内容）
- 数字（含CI）：待运行。
- 结果文件：待运行；[来源审计](../results/D0-SAP-source-audit.json)。
- 按决策表执行了什么：待结果。
- 主张变化：无预定升级。
- POST-HOC：无。
