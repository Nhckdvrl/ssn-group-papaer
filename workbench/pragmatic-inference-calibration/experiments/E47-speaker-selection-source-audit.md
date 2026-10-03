# E47：speaker-selection-source-audit（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1–D2，CPU原材料与规范审计
- **对应：** C02/P02
- **问题（一句话）：** 说话者选择机制是否让“literal”条件的规范仍含目标偏好，公开原材料/人类过滤是否足以支持后续测量？
- **设置：** Mayn/Loy/Demberg2025 OSF f5nmv两完整results与排除表、原models.R；Barnett/Griffiths/Hawkins2022官方repo全部asset清单、两个公开processed human输入与Table1 cached criterion。固定源SHA，不生成或修改材料，不送模型。
- **读数：** Mayn原24items/source labels/positions/slider总和/全部human排除；正文79/160与四critical rounded means核对；8critical逐条按原available messages计算L0和Bayes-on-S0/L1。弱证据parent最终raw/filter是否公开一致、727vs723与Table1的variant key是否可核对；缺失明确报告，不自动修补。
- **阳性对照：** 原source critical display与图核对，控制/完全歧义为1/.5，S0消息须按每个对象可用真消息数量归一，不根据human rating倒推gold。原排除按author表，不能按我们的模型/偏好筛选。
- **噪声地板 + MIE：** deterministic源审计，无sampling或GPU；正文mean舍入1decimal。源不匹配时不称复现、不开GPU；一次算术成功不升级能力。
- **混杂审计：** Mayn照片与alien manipulation不能被text-only替代当原human replication；人群与model采样不同。sourceS0≈literal但listener L1非literal L0。弱证据同人expectation不是随机操纵，不能用processed表宣称causal speaker effect；缺sourceSI不臆造过滤。局部表错误与研究整体claim分开。
- **决策表（跑之前写）：** A source/norm可核对且理论literal偏好存在→更正许可假设，保留原parent；B缺原filter→资产边界，先源码/作者公开source不铺GPU；C标签/比例异常→保留原并定位不silent fix。没有结果自动关线。
- **算力预算：** CPU<1分钟，GPU0；人类源raw不进git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
**POST-HOC前置记录：** 阅读时已做一次Mayn participant计数/critical mean打印及弱证据公开input行数检查，尚未持久化完整审计；本卡不把这些已有spot-check伪装盲测。后续formal逐行/理论核对在本卡后执行，不能据此claim发现新现象。C01/C02仍L0。


原源/理论全部审计完成：[result](../results/E47-speaker-selection-source-audit.json)。Mayn retained79/160人、1896/3840行；adult/child关键mean Exp1 70.846875/57.320513、Exp2 70.65625/62.235938，均按正文一位小数匹配。全部raw概率和100精确，24source两实验一致。8critical的L0=.5而Bayes-on-literal-S0=2/3；12unambiguous=1、4ambiguous=.5。这是parent的规范条件，不是我们的finding或FPR gold。

首次formal gate假定raw每人24行失败：Exp1有一个48行ID，作者排除表已排除它。失败记录ROOT/data/E47-first-audit-failure.json保留；未dedup/删改原文件，改为同时记录raw异常并核对原retained sample。weak-evidence最终raw replication.csv未公开在取得repo；processed727 vs正文723不能插补或删4行，两种RSA cache criterion均保留，未复现原filter/WAIC。决策表A/B/C：Mayn可进入明确声明的文本迁移，weak-evidence仍需原filter。C01/C02仍L0。
