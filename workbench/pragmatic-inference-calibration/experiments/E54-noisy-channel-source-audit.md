# E54：noisy-channel-source-audit（2026-10-03）

- **状态：DONE。** 跑前资产审计；不含新模型预测，不把论文示例当完整数据。
- **类型：REPRO。** 下一自然parent的驻留，不是I01的科学pilot。
- **对应：C02 / P02；I01仍SEED。**
- **问题：** 原noise/meaning-prior研究是否公开足够完整的材料、条件与human响应，使固定目标句的证据效应可以可靠测量？
- **设置：** Gibson2013最终正文/作者SI；Chen/Washington/Gibson QJEP DOI10.1177/17470218251383526（2025online，2026volume）与公开OSF k5vqj。全部公开资产，路径/hash/版本/缺失登记，不采样、不人工补gold。
- **读数：** 原critical/filler/conditions/response映射及人类结果可重建性；先清点schema，再按原排除规则核对描述norm。访问失败与缺失也为结果，不按模型效果选择资产。
- **阳性对照：** 原论文例句的DO/PO及plausible/implausible条件和literal-response映射可核对；若有原human数据，描述数值需能匹配published表/图。论文例句仅校对schema，不替代完整human norm。
- **噪声地板 + MIE：** 确定性资产hash/schema校对应完全一致；资产阶段无科学effect/MIE。后续GPU卡需独立冻结human source数量、cluster uncertainty与科学差距，不用本卡事后开跑。
- **混杂审计：** Gibson原不同实验长度与participant差异由后续parent专门讨论，不能忽略；filler prior与signal noise区分；句法literal与pragmatic suppression不是同一gold；response polarity/重复item/原排除与未知字段均逐项核对。GPU/采样/judge不适用，data leakage/原material可用性待审。
- **决策表：** A原全量材料与norm可核对→冻结parent reproduction GPU卡；B只有材料→先核对protocol，明确缺human，不声称精确复现；C仅示例/访问失败→记录缺失，换公开原source，不造gold补洞。
- **算力预算：** 0 GPU·时；CPU只做下载/数据审计。**实际：** 0 GPU·时。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 全公开24文件manifest；19份CSV/R原资产已下载并核对hash。Gibson原11数据保留，400基线critical无字段缺失、literal映射与原Correct一致；前四baseline/noise各80critical一致，第五不一致。原QJEP四数据metadata与分析代码不适配，participant跨文件重复；不能声称精确human norm复现。
- 结果：`results/E54-noisy-source-audit-r2.json`。r1未采用原R跨文件全局subject过滤，保留`results/E54-noisy-source-audit.json`并标为被r2替代的源规范计数，不用r1构造norm。r2全局过滤下（保留/删两个Qualtrics metadata行）人数为60/59、61/59、202/200、203/201；与published60/60/201/203未全部匹配。不按期待人数手工调整排除。
- 导出仅语言白名单400项，原句不改，外置`data/E54-original-critical-materials.json`；0模型预测。执行决策B：可测原材料，human history/norm精确parity仍不确定。
- 主张变化：C02仍L0；无升级。
- POST-HOC：无。
