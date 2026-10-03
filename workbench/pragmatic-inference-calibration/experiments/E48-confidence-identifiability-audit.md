# E48：confidence-identifiability-audit（2026-10-03）

- **状态：** DONE
- **类型：** D1–D2 / parent测量前提校对；不是LLM实验或新metric
- **对应：** C02/P02
- **问题（一句话）：** 在2606.29490正文与Fig9写明的带噪真值读数→阈值决策账户中，移除真值后的残差真的必须不能预测决策吗？
- **设置：** z、e独立标准正态，VC=z+e；correctness由sigmoid(z)独立Bernoulli产生；oracle真值代理就是z。决策D=1[VC>τ]，τ=0/1；另soft阈值k=1/4。负对照D=1[z>τ]（e只影响报告）。固定种子0/1/2，每设置200000模拟点。正文pp6–8与Fig9 p37在本卡前已读；尚未运行模拟，不假装理论疑虑是blind discovery。不拟合LLM结果。
- **读数：** population残差VC−z=e的AUROC(correctness)、AUROC(commit)；另半样本OLS拟合/另一半评分。全部seed/setting保留；Account2若只把同一e改名zD，联合观测分布逐数组完全相同。不是新metric。
- **阳性对照：** oracle z消除代理不完善解释；独立报告噪声账户残差两AUROC约.5；同一e改名zD全部观测必须精确相等；sklearn AUROC与秩方法核对，constant残差=.5。确认文中阈值作用于VC。
- **噪声地板 + MIE：** 200000点各三seed，漂移约千分级，是数学反例非population效应估计。高斯下Cov(e,1[z+e>τ])严格正提供解析核对；不能将数值例称LLM真实机制。
- **混杂审计：** 用于决策的带误差估计，与只在报告末端添加的噪声不同，阈值对象必须明确。残差关联不否定原行为或activation steering证据，也不证明VC没有policy信息。NMI/ICML相关全文尚未读，不取消独立证据。不借此转出territory或写generic confidence故事。
- **决策表（跑之前写）：** A阈值VC账户残差预测D而不预测C→禁止在我们项目将残差分离直接解释成policy shift，需额外干预/多指标；B不出现→校对公式/实现、保留失败；C源码实际阈值z→更新所审范围；D噪声与zD同分布→明确观测不能识别语义来源，不升级能力claim。
- **算力预算：** CPU秒级、GPU0，不生成标注，不给空卡造实验。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。C01/C02仍L0。


三seed×八设置完成，全部解析/独立秩AUROC/同变量改名gate通过：[result](../results/E48-confidence-identifiability-audit.json)。hard阈值带噪估计残差的correctness AUROC .498833–.500853，而commit .832763–.846954；report-only noise负对照commit .498311–.502830。soft k1/k4 commit .706369–.713691/.816509–.828918。没有LLM预测。解析Cov(e,1[z+e>τ])=φ(τ/√2)/√2>0；即使oracle proxy=z，残差仍因进入决策而与决策相关。e与同分布zD改名时所有观测完全相同。

决策表A/D：在我们项目中，不能仅用这种残差分离识别“policy bias”或报告含义；需要明确噪声在哪条因果路径、多读数及独立操纵。这不撤销parent原行为、probe或steering证据，不形成LLM能力finding。初次CPU运行缺sklearn、0模拟结果，随后在env安装scikit-learn及依赖，未改seed/公式/阈值。C01/C02仍L0。
