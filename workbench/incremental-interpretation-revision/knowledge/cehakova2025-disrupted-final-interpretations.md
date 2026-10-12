# Ceháková & Chromý (2025) — Beyond Initial Misanalysis: The Disruptive Nature of Garden-Path Sentences Processing

**PRIMARY MAIN VERIFIED 2026-10-12：实质纠正旧卡“只读摘要/Methods片段”的记录。** *Discourse Processes* 62(10):723–743；online 2025-07-22，DOI [10.1080/0163853X.2025.2513210](https://doi.org/10.1080/0163853X.2025.2513210)。[出版页](https://www.tandfonline.com/doi/full/10.1080/0163853X.2025.2513210)目前返回403；本轮取得了[作者Jan Chromý上传的ResearchGate完整文章文本](https://www.researchgate.net/publication/393914342_Beyond_initial_misanalysis_the_disruptive_nature_of_garden-path_sentences_processing)，实读 Introduction、Hypotheses、Procedure、Materials、Results和Discussion，包括给定回归系数。**未查看PDF图像的逐图分数、未读完整附录A、未运行Zenodo数据与R分析脚本。** 作者公开[Zenodo数据与刺激](https://zenodo.org/records/16358492)。旧内容及更早记录可由Git版本历史恢复。

## 1. 论文在理论谱系的位置：不是重复“也问新关系”

**DIRECT AUTHOR QUESTION：** Slattery等基于gender-mismatch和后续句阅读的局部功能性证据，认为正确全局结构可建立、旧错误记忆难以清除；但Huang & Ferreira 2021 解释指出，即便一个新局部树足以许可反身代词，也不必保证**全局解析整合完成**。此前很多研究把旧角色错误的一个问句当主要观察，忽略消歧后另一错误候选也可能局部成立。作者从2023捷克语实验过渡到两类英文结构，再把“残留”拆成 **四种语义问题**。

两种完全不同的局部连贯诱因：
- MV/RR：`The professor awarded the grant gained attention`。正确 `award(patient=professor,theme=grant)`（被动省略施事）和 `gain_attention(agent=professor)`；错误可生成 `award(agent=professor,theme=grant)` 或 **`gain_attention(agent=grant)`**，后一种 `the grant gained attention` 本身**局部语义可接受**，离gained也更近。
- NP/Z：`While the assistant shaved the actor who was overworked watched the news`。正确 `shave(agent=assistant,patient=assistant)` + `watch(agent=actor)`；旧误 `shave(agent=assistant,patient=actor)`，后一片段另可错配成 `watch(agent=assistant)`，但 **actor在watched前最近、与动词距离更合适**。

**RECONSTRUCTED idea来源**：2023三个关系正反核对已经表明old No不够→但在一个新局部树正确时可能对晚动词产生**另一个错误关系**→跨MV/RR和NP/Z改变晚动词最近名词究竟是“局部合理但全局错误”还是“局部且全局都正确”，让**构式×四问题×GP效应**有理论价值。比“两个构式+更多问题”更深一层是对 `DISMIS` 和 `DISCOR` 的不对称预测。

## 2. 4个问题的真正语义，不是2个互补准确率

| 标签 | 测的是 | MV/RR示例问题 (gold) | NP/Z示例问题 (gold) |
|---|---|---|---|
| AMBCOR | 歧义前半句的新合法依赖 | Did someone award the grant to the professor? (Yes) | Did the assistant shave himself? (Yes) |
| AMBMIS | 前半句旧错误依赖 | Did the professor award the grant? (No) | Did the assistant shave the actor? (No) |
| DISCOR | 晚动词的合法主语 | Did the professor gain more attention? (Yes) | Did the actor watch the news? (Yes) |
| DISMIS | 晚动词的另一个**错误**主语 | Did the grant gain more attention? (No) | Did the assistant watch the news? (No) |

**必须加上一条别遗漏的说明**：四种问句是**同一项目材料在不同人/不同试次间counterbalance的一次提问**，不是每个被试同一次阅读对同一句连续回答四题。它们给出各测量的**边际准确率**；即便四个GP-对照差都显著，也无法单独推出“同一人的内部状态同时包含/缺失哪些具体关系”。作者在Discussion明说，未来可以同时问多题检测同一人跨题的矛盾，但反过来也担忧连续问题会诱发更完整解析。这个**识别缺口**是比“再问四题”更值得研究的方法论压力。

## 3. 数据、模型、预期

- 同一场session完成两项并行实验（MV/RR 24 items、NP/Z 24 items），总计**176名分析参与者**（美国英语母语且19–26岁在校学生，Prolific招募178，另有排除/替换）；PC Ibex moving-window SPR，关键句与随后两词区域的RT、结束后Yes/No。
- 拉丁方平衡歧义 GP/nonGP × AMBCOR/AMBMIS/DISCOR/DISMIS（2×4 within-subject，**每位每个条件约3句/构式**），共48 critical +70 fillers=118条；正文Materials另一处出现“72 fillers, 120 total”的不一致，需**保存冲突**而非悄然选自己喜欢的。两句差异应以作者released PC Ibex/stimuli及分析文件复算核实。分析同时使用participant和item随机效应。
- 作者主文预期：如果只是旧错痕迹难以抑制，那么 GP主效应理应主要集中 AMBMIS；如果多局部结构不完整，AMBCOR/DISCOR/DISMIS也应受损。特别MV/RR中 `grant gained attention` 是局部连贯的错误晚关系，比NP/Z的 `assistant watched` 有不同混淆前提。
- **输出合同争议**：MV/RR中 `Did someone award ...?` 的事件可能被听成“实际发生的叙述性事件”而非压缩关系从句的客观蕴含；作者承认这会使AMBCOR被低估。即便作者自己认为GP-对照差不是这一效应单独造成，也不能把全部AMBCOR错误解释成从未形成正确关系。

## 4. 核心结果与保留反证（主文 §4, §5）

- 两构式GP条件在disambiguating token与两个spillover区的RT均显著升高。MV/RR该三处β=.032/.112/.090；NP/Z β=.031/.057/.037（logRT模型），不表征“最终解释正确”。
- 在全体样本的混合效应logit估计中，**歧义相对控制令四问题正确率均下降**：AMBMIS β=−1.670 (SE=.134)、AMBCOR −1.247 (.136)、DISCOR −2.325 (.359)、DISMIS −.777 (.145)，四者p<.001。**不要把这些log-odds系数当百分点，也不能说每一被试在四关系都受损。**
- DISCOR另有**构式×歧义交互**β=−1.881、SE=.705、p=.008；DISMIS构式主效应 β=−2.531、SE=.237、p<.001。不能把跨构式均值说成完全同一个过程。
- 晚动词的**正确关系** DISCOR 仍约90%（作者讨论），但对照更高；歧义前半句合法关系 AMBCOR 在GP条件两构式约50%（作者讨论）——然而只看50%的Yes/No强迫回答不能区分猜测、事件语用解释、正确关系受干扰、还是从未建立关系。
- **特别重要的负对照**：即便显式 `who was awarded` 的**无GP MV/RR**，题 `Did the grant gain attention?` 也经常错误地“Yes”。`grant gained attention` 是一个局部自然片段，完全不需要曾经garden-pathed才能被激活；这一现象不是纯“旧解析残留”。作者用距离、局部plausibility和local coherence解释，尚未在本论文做彻底的语义/词距正交实验。
- 文章明确讨论：四种问句可能在阅读**之后**诱发相应的局部组合；结果更支持不完整的global结构，但**不能独立确定局部结构是在线解析时还是问答阶段生成**。

## 5. 这个近邻实际阻止了哪些“我们的新颖性故事”？

1. **“旧错No好但新关系没有建好”早已是强近邻**：2023已3个关系、2025在英语两构式用4关系含晚区域错误测试；不能把再多问一个新角色当作idea创新。
2. **“正确晚主语可用，却又对晚主语有错误候选”也有近邻**：2025 MV/RR DISMIS已分析local coherence导致不匹配且GP和非GP都出现；非GP背景不能被当成revision专属。
3. **“同一模型四读数分歧=同一内部状态不一致”不是现有证据能推出**：2025是跨source/被试/问句的边际，没联合观测；本项目E82–90跨prompt/patch的组合也需要真实同源同介入key配对。即使同源独立调用，也不等于一条连续时间轨迹的内部状态。
4. **作者下一步的多个问句本身存在readout intervention问题**：询问旧角色与新角色的**顺序**可能改变后续模型处理。因此实验可区分 `parallel fresh contexts`（读数无串扰但不观测同一运行的联合状态）和 `sequential same context`（观测次序依赖但混入干预）。用随机构式/问句顺序、未告知的用途与source级统计，讨论两种测量各自的识别范围，不是假装解决不可观测变量。
5. 若要做机制层创新，更值得问的是：**哪个可定义的具体晚依赖，在GP×句法/词汇局部性/任务顺序交互下自然形成但无法稳定被使用**？它仍是待验证的科学问题，不是已取得结果；高价值与否需看近邻和独立反证。

## 6. 原始资产和阅读欠账

[Zenodo 16358492](https://zenodo.org/records/16358492) 有Stimuli.zip (~10.9KB)、PC Ibex (~127KB)、data+R (~3.1MB)。本轮尚未运行分析脚本或逐项审问句语义；论文主文 **118 vs 120总句数及70 vs 72 fillers存在同一文内部差异**，未来核数据时应留下审计记录。画图PPT不是证据；图1/2若要引用精确柱高要从正式图片或原CSV重算。

同一条研究谱系：[Christianson 2001](christianson2001-thematic-roles-linger.md) → [Patson2009](patson2009-paraphrase.md) → [Slattery2013](slattery2013-competing-representations.md) → [Huang/Ferreira2021](huang-ferreira2021-memory-versus-parse.md) → [Ceháková2023](cehakova2023-diverse-reanalyses.md) → 本研究。