# 我们现在相信什么 — 2026-10-03

当前推进 C01/C02、P02/P06；以下是驻留观察，不是升级后的科学claim。

| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E04原Flan1,365选择全匹配；概率MAD0.000077 | 原MCQ harness有效 | 现代重实现完全造成差异 | 高，技术复现 | E12/E16同题同stage与readout |
| E02原14B四语言maxims56.25/52.22/49.03/55.28%，literal88.89/86.11/91.11/92.78% | 两类原任务走势可本地测量 | 原模型仍不可运行 | 高，原始结果；精确论文parity不足 | 核对解码细节；不把literal错误叫FPR |
| E10同1024预算3,600回答与E06逐字一致；德语literal格式控制+24.44pp CI[14.44,34.44] | 输出约束影响评分 | 原生低分可直接当缺知识、预算解释 | 中，任务读数 | E08/E14字母与文本绑定，不作新能力claim |
| E08 BF16 batch差0.8547/4.6246与T5 target-left-pad差2.22/1.05，原读数隔离；FP32/right-pad过gate | 数值与padding可制造大效应 | 漂亮异常自动是科学现象 | 高，工程对照 | 后续首末项数值gate，失败隔离 |
| E11 374人/169项63,206条Correct码零错；3项human modal≠gold保留 | 人类分布可校对歧义 | 所有gold都是人类唯一含义 | 高，编码复现 | 按phenomenon分别对齐，不混控制缺norm项 |
| E13原BERT例surprisal最大差<3.72e-5；1362项人类推断率Pearson−.400 CI[−.438,−.363] | string expectedness与自然graded变异相关 | 只能靠人工反例进入领域 | 高，仅string复现 | E18跨scale；concept/GloVe未复现，不越界解释 |
| E18原GPT2 294可对照值MAD.0000533/max.0002603 bits；四数据关联不一致 | 原parent协议有效、跨材料边界重要 | 全部scalar现象共用一标量关系 | 高，复现与描述；非novelty | 与人类知识/QUD条件证据结合，不能把contrast surprisal叫判断 |
| E14 28,800读数；rotation0与E08所有8匹配组argmax/prompt一致，概率差<.000579 | 顺序审计测量已校验 | 实现换prompt造成位置结果 | 高，工程 | 位置效应留仪器，不局部优化故事 |
| E17三模型各3200生成；采样均值相对似然MAE差−.094 CI[−.510,.312] /+.131[−.294,.545] /+.149[−.252,.543] | 均值偏差不易由受限likelihood解释 | 只改采样便自然恢复human均值 | 中，50pair；14B23无效已单列 | 强现代endpoint与human异质性；不把采样噪声当人群分歧 |
| E19原t-d-002 SI1 .25/SI2 .454167复现；human原规则删143/267，留235/429，acc.5617/.7296 | 原评分可核对，human过滤须透明 | 按论文冲突文字直接评分 | 高，代码/资产；不是scientific finding | E20原完整下注读数，保留无效与上下界 |
| E19 IR16原item仅6完整；Flan 0为2token，atomic gate失败 | 资产与协议有适用边界 | 失败读数=语用能力差 | 高，来源/分词 | 不填造40缺失条件；Flan只用E20生成原任务 |
| E20七模型完成；Q25 741/Q14 705/OL-SFT40，其余0有效（各760） | 部分模型不适用原下注stop/parser | 生成无效可直接当pragmatic error | 高，协议可用性；不排名 | 固定全量收完；不看到结果改parser/补prompt救分数 |
| E05试标9/25许可、61/125choice分歧；三parent缺可靠二值warrant | 标签/构念是bottleneck | 自动标注即gold/直接可报SDT | 高，限该rubric | 明确candidate q和交际规范，利用原human norm |
| EPITOME、eliciture、goal模型、ImplicatureX已拥有知识使用/撤回/目标压力 | 自然tension可深化 | generic知道不用/不会撤回是新claim | 高，定位；新数据资产核对中 | 重新归因条件结构，持续collision audit |

无L1/L2/L3能力或post-training主张升级。每条数字可追溯E卡与results；原始回答保留在外置runs。

## 新一轮观察

| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E22 Qwen bare scalar initial Instruct−Base −.110 CI[−.210,−.010]，cancel-minus-irrelevant −.148[−.277,−.028]；natural initial−.283但更新差+.026[−.007,.059] | 初始endorsement与条件响应可方向不同，需按现象 | post-training统一更爱推断的未经测量故事 | 中，原任务描述；Approx norm不确定 | E27真实DPO谱系；E28强现代端点，不能凭局部差升级 |
| E26 Qwen Base下注bare746/760、chat0；Instruct bare713/chat741 | 生成格式适用性依赖stage×入口 | invalid可当语用能力错/任选漂亮入口 | 高，parser固定，CI按40items待配对汇总 | 保留unconditional bounds，与原子支持质量一起核对 |
| OLMoE旧chat的全部source prompt SHA不一致；裸Hu1365/Epi784/Impli3252 token一致 | BOS与special map是真实混杂 | 共享模板字符串足以干净stage比较 | 高，逐token审计 | E27完整tokenizer+BOS0/50279×stage；先审是否还混杂 |
| E24 19公开cache，Q3-4B自然.78→.46、Gemma4B.70→.40；larger多数变化小 | 源数值舍入/顺序会影响阈值分数 | 小模型与human equality为稳定能力证据 | 高，算术描述；native cache精确parity未成立 | 技术隔离完成，回到证据条件主问题，非优化此bug故事 |

E22/E26见results/E22-E26-stage-controls.json；E21七模型见E21-E23-implicaturex-stage-summary.json。候选能力/训练解释仍L0。

## 三阶段与知识控制复核

| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E27 三stage同token/input SHA通过；DPO−SFT natural initial chat bos50279 −.04625[−.05350,−.03894] / bos0 −.03201[−.03800,−.02631]，裸+.00641[+.00364,+.00963]而support弱 | 入口、prefix熟悉度影响stage读数 | post-training统一更爱推断/只换模板字符串的干净归因 | 中，原任务描述；不能科学升级 | E28强现代原任务边界，条件证据而非合并criterion |
| E29 Q3 role fullnorm .939→1.000；partial a1 .648→.052/a2 .197→.006，full polarity consistency .181 | “恢复”可同时增加另一侧错，知识readout不能透明作gate | full条件救分即证明知识恢复/表示正常 | 高，40item source控制；不是new finding | E31同四变体强模型边界，拒绝新增救分prompt |
| E29 OL SFT/DPO裸各1/360旧parent差>.001；sourceecho/直接prefix360全token一致 | batch数值敏感而非材料替换 | 首末gate足以审所有case | 高，原raw/失败保留 | E30固定失败+首末case组成校对，入口先隔离 |
| DRInQ公开231行、84相同question不同human gold文本对；固定五候选集合的pair=0，仅4pair/3question互含gold | 公开subset不足支撑完整同candidate语境对照 | 一下载邻居就能扩SDT或新榜单 | 高，文字/集合审计；不等于语义错误 | 保留资产缺口，先不铺无信息量的额外benchmark |

E27/E29结果文件见results/，知识规范仍是parent规则，未成为推断许可gold。C01/C02仍L0。


## 强端点、自然强度与有界恢复（E28/E31–37）

| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E28 8B/14B Wave MAE14.435/16.113，差+1.678 CI[−1.521,+5.239]；natural Impli条件Δ多CI含零而order gap增.469 | 强端点/任务/readout边界仍须分开 | 从一个点估计排名或旧小模型源threshold讲能力 | 高：任务数字；科学归因不足 | E35独立family原parent对照；不再重复单一order优化 |
| E31 full polarity agreement4/8/14B=.181/.688/.894，但14B access-only norm.058 | 规模可以改善一致性但readout不统一 | 单prompt恢复等于latent knowledge恢复 | 高：源40items/八condition SHA一致 | 不能把norm当许可；回到具体候选证据/来源 |
| E32同stage alternative expectedness、human关联无统一方向，OL某dataset SFT surprisal+.361[.128,.587] | 备选预期与任务回答是不同观测 | 跨材料均值直接mediation或统一criterion | 高：string复现；语义层解释不足 | 需同材料human许可/备选，不泛化成能力 |
| E33 IQAP chat方向4/8/14B=.613/.733/.853；null probable选择近1、terminal能翻转强度方向 | 真方向改善并存候选词汇/terminal先验 | 更大/更aligned统一更过度确定 | 高：150dev/原human；未经holdout | 保留4way human分布；不局部换答案措辞救故事 |
| E34 Q3-4 PN原序强/弱正确.808/.115，逆序.038/.923；CY多正确 | 测量位置依赖，条件语义也有强成功例 | PN单侧错=过度推断；conditional一概不会 | 高：源五人一致抽样；非因果配对 | E36已完成有限一句控制，E35独立family |
| E36 Q3-8 strict强侧+.577[.346,.808]、弱侧−.500[−.692,−.308]；14B部分改善 | 指令可以改变两侧选择政策，必须联合报告 | 一侧高分就是恢复能力 | 高：26自然question配对；order仍敏感 | 本局部prompt分支不继续；回到自然语境证据 |
| E37 Flan原序strict强侧+.346[.192,.539]、弱侧−.385[−.577,−.192] | 控制效应不限当前causal接口，但依然只是任务 | encoder-decoder自动消除偏差、统一stage原因 | 高：433原QA/1732读数；无stage因果 | 保留native baseline作边界，不补机制故事 |

完整可审结果分别见results/E28、E31、E32、E33、E34、E36、E37的summary.json。全部source/CI/两order未挑选。C01/C02仍L0；没有共同licensed/unlicensed gold，没有d′。E35跑前CPU发现空格retokenization和官方template追加assistant时丢system，0预测修正，逐候选独立teacher forcing gate后才全量。


| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E35独立Mistral Base/Instruct25396读数source/token/完整似然gate通过，natural endorsement−.298[−.370,−.208]但conditional Δ+.0116[−.0459,.0658] | 同源stage效果依赖任务/入口，不能只看初始赞同 | post-training普遍更自由推断；generic SDT story | 高：原任务描述，source支持质量变.065→.988 | E38原human背景prior与speaker commitment的两任务，非本局部prompt优化 |

E38跑前audit：1760source/840human mean，prior源Josie四行高/低fact标签对调保留、actualfact配human；三个公开certaintycache1680prompt一致，prior GPT4o四row不同不称parity。自然SwDA官方repo仍仅README待上传，未伪造两批human label。

## 新source、完整生成与互动baseline（E38–E45）

| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E42 5196 nonEOS数字中3677延长成prose，prefix全相同、0变值 | 原短预算不能识别完整scalar回答 | 用5token numeric排名或归因stage | 高，完整selected audit；不是能力finding | 固定32诊断结束，不局部救prompt；相关旧解释隔离 |
| E40 Exp2原703human/64条件、OLS9.268/2.982/18.285舍入parity；Exp1少5 | Exp2原norm可驻留，版本需分别审 | 三实验全精确复现 | 高，CPU原字段；mixed未复现 | E43分target原材料、独立转写仍缺 |
| E43 Q3-14 chat facts64/64、meaning7/8，分目标all32完整；OL SFT61/64、8/8 | 判断目标可测；部分基本理解已成功 | 无条件把评分差异叫统一criterion/脑补 | 中，8item/prompt迁移；入口未一致 | E41更强matched stages；原其他材料先审意图显式变化，不立即Exp3堆量 |
| E43 MistralInstr chat初始8/8但numeric2/1/11 of32 | 理解对照成功与评分接口失效可共存 | invalid就是pragmatic ignorance | 高，raw/parser完整 | 本读数不可用于stage效果，不继续格式修复 |
| RAILS2025 literal S0消息仍支持target2/3 | speaker policy与listener literal选择是不同对象 | literal partner=全部unlicensed gold | 高，原规则/两页全文；非我们finding | 先E44/E45原互动基线task floor，再决定行为目标 |

E38/E39/E40/E42/E43完整结果见各results；E45运行，E41资产下载。没有成熟paper claim、C01/C02仍L0。
