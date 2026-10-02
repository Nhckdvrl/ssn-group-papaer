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
