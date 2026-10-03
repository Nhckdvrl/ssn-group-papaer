# 我们现在相信什么 — 2026-10-03

当前只推进C02/P02：具体含义的支持／不支持测量。以下历史读数不是当前实验排队。

**当前支持的核心观察：** IQAP上OLMo SFT→DPO的四类human分布距离跨三种措辞都变差（E59），不是原单个词组的偶然效应；其无对话答案先验也变化，故仍未识别能力与policy的贡献。强Qwen方向准确提高却分布距离变差（E52），但Base候选支持极低，不能升级能力结论。E61人物评价与动机归因变化不同且后者接口质量弱；不能据此宣称两种能力分离。当前缺口是**同一候选含义的支持／不支持语境测量**；上述读数不替代此测量。

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


## 深读、强配对与任务floor（E41/E45–E49）

| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E41自然Impli Instr−Base initial−.2284 CI[−.3205,−.1268]，cancel−irrelevant−.1410[−.2570,−.0362]；candidate mass .00995→.63724 | 初始判断/更新/入口支持质量不同对象 | post-training统一更爱脑补或归一化概率就是能力 | 高：完整18468gate；能力归因不足 | 原源/规范成立后联合选择机制，而非更多format rescue |
| E41projection Base bare0完整、Instr chat全880每极性完整，原5token | 评分适用性依stage/interface | 只挑有效numeric比较能力 | 高：7040全raw/EOS/bounds | 不救原budget；独立natural分目标E46已完成 |
| E45无歧义64controls五端点5/19/21/29/8正确；全未过.95 floor | build/coordinate失败仍是主要替代解释 | confidence4即模型过度推断partner | 高：800calls/全controls；root几何审非独立人审 | 不加prompt，先其它可靠parent；源几何11/64反射仅诊断 |
| E46Base bare8/8+64/64，Instr chat6/8+58/64；各数值均32/32，但相反入口大量invalid | 理解/评分/入口可分离 | 最好入口差就是stage因果；cross-layer=脑补 | 高：1056全gate，八item归因不足 | E49同源两个交际角色；独立自然材料仍必要 |
| E47两human retained79/160、四critical mean舍入parity；literal-S0关键posterior2/3 | 推断许可依表达选择过程 | literal partner全当unlicensed/FPR | 高：CPU原规则/全24source | E49文本迁移先control再关键条件，不伪造photo norm |
| E48 oracle残差correctness .499–.501，threshold-noisy estimate commit .833–.847，独立report noise≈.5 | 残差关联需要额外路径假设 | 任何非truth残差就是policy/criterion机制 | 高：解析＋三seed反例；0LLM证据 | 联合独立观测/可区分因果操纵，停止本数学局部audit |
| E49全部1080source/model preflight，OL SFT/DPO actualtoken一致，八端点运行 | 有parent支撑的联合观测可实施 | 为满卡制造无问题的表格 | 仪器证据，结果未齐 | 等全部完整、EOS/全行bounds/control；不挑模型或source |

完整结果见E41/E45/E46/E47/E48各results；E49 RUNNING。C01/C02仍L0。


2026-10-03 E49/E50完成：8640/6912原source读数完整，数值/source/token/EOS gates通过。E49无endpoint三身份全过无歧义控制；E50多数Qwen listener恢复，但speaker候选质量弱、身份effect随入口/terminal反转（Q3-8 bare full−.0180 vs content+.0048）。全部原item/missing bounds保留，不把generic role不一致或格式差叫新发现；C01/C02仍L0。当前未知需由独立自然source、成功理解与概率质量共同约束。E51跑前卡已写，核对dense OLMo2四stage和原IQAP/Circa输入；不追加E49/E50的局部prompt救分，资产预检尚在进行。

E51/E52：原IQAP150×两入口与Circa433×两入口×两order，4stage8128/强Qwen配对4064。各native词表、完整backend与源/候选prefix已核对；Q25 native EOS角色不同，共同Instr terminal作为受控入口显式记录。E51固定权重下载、八槽等待；E52四卡实际计算且numerical/fullteacherforce gates通过。新增ICML2026缓存confidence正文/关键方法与EMNLP2024不同pragmatic levels正文深读，累计55分级卡。未升级C01/C02、未改PROPOSED。


E52强Q25配对4064完成：IQAP chat方向+.2333 CI[.1467,.3133]而四类Brier+.2084[.1343,.2872]，但Base完整candidate mass8.04e−13/Instr无QA prior偏probable-yes .99697，不能升级能力/校准claim。Circa条件原序弱correct升.7969→.9766，negative弱class仍有原序.1154/逆序.8462的顺序混杂。E53明确POST-HOC无损格式审计全8640与固定6阳/15阴cases通过：四endpoint从0可用恢复962–1079，但无歧义semantic controls仍未共同通过，原primary不改，不将format失败叫能力negative。C01/C02仍L0。E51八槽等待固定权重，有限collector只汇总8作业全完成且校对通过的结果，不更新主张/状态或自主开实验；实际状态保存在本地data/E51-collector-status.json。


| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E55原400句×8端点×4入口目标=12800完整读数；source/token/numeric gates通过 | 原材料现代迁移可测 | 纯实现错误解释全部差异 | 高，技术；科学归因低 | 原source证据干预与独立生成，E57 |
| Q25 chat Instr−Base implausible literal-prob benef−.1797[−.3199,−.0184]、active/passive+.0899[−.0465,.2263]；Instr full mass极低 | 变化依赖材料/测量，统一criterion未识别 | 所有post-training变化同向 | 中，描述；未排混杂 | E57同目标/不同source exposure，invalid bounds和基础理解 |
| E56前四组80/80目标相同、第五4/80；18filler改动≠正文30 | 源版本必须逐项审计，可做有限固定目标干预 | 下载数据等于精确复现；补造缺项还称原source | 高，全量确定性；不是科学效果 | E57仅公开版本条件响应，再跨独立source |
| E54 QJEP全局过滤与published人数未全部匹配，r1逐文件计数隔离 | human规范重建仍不确定 | 可把当前norm当精确published gold | 高，代码/计数 | 回到原metadata/export路径，不强行凑人数 |

I01仍SEED，C01/C02仍L0。新的对象以证据来源的不同条件预测保持广度，而非追某个局部异常。OpenCode官方免费CLI仍403，0新增可用语义标注；schema/source审计不冒充独立语义标注。


2026-10-03 E57完成（C02/P02）：23552生成完整、技术gate通过；没有端点全部semantic controls与plausible critical共同超过预设.95 heuristic。Q25Instr/Q3-8在E3 for-dative的default noise−clean两排列均同各自方向、跨端点却相反：−.1125 CI[−.225,−.025] / +.0625[.0125,.125]；Q3-14−.0125[−.0875,.05]。这削弱统一noise→更多修复叙事，但尚有source/词汇/blocked exposure混杂且多切片未校正，不升级科学claim。Q25Base/MistralBase invalid2931/2944，不把格式不可用当stage能力下降；所有bounds/两seed保留。下一未知是原Yes/No是否在角色理解与世界否定之间混用，E5820条盲态辅助审计先查源规范，不救排名。

P05：1,689,854,457 bytes缺失权重直连续传，new shard SHA通过，11 cached shard原official metadata/revision/size与镜像吻合、未本轮全rehash。Base2作业已真实计算。OpenCode Ling3.1官方CLI返回OK且cost0；MiMo2.6当前429，原LongCat403不代表全部free不可用。E58只candidate audit、0GPU、tool权限deny、不切付费。


E51完成：8128/8 logical jobs，source/input/numeric全gate，.6629GPU·时。SFT→DPO IQAP chat方向差−.0067[−.04,.0267]、四类human Brier+.3128[.2772,.3475]，bare也+.2340[.2056,.2612]；post-SFT候选mass高且full/content近同，削弱“只有EOS数值问题”。但no-dialogue prior也大幅改变、Circa order gap仍大（DPO negative弱accuracy0/.8846），不能归因pragmatic competence/criterion。Base candidate mass低，全部阶段保留但stage能力尚未识别。支持需研究条件结构/措辞偏好；削弱单一能力标量；confidence描述中、解释低；next：先核对原human任务不确定性的referent，再以独立可用source区分全局回答政策与语境证据。完整卡/summary见E51。


E58完成：SpaceBunny-free官方CLI20/20成功、所有step cost0且无tools，18 exactquote/schema有效、4 event-role对源gold分歧；root逐项审阅至少2条有字面角色混入常识修复，world否定也不一致。支持CLI路径可用，削弱“strong free模型一条条做就能保证gold”的自动化假设；高技术/低语义可信，不替换原gold，不新增SDT negative。下一鉴别为原human任务语义与独立验证，不能把judge错误变成新模型能力claim。完整E58结果/原失败见summary。


| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E59 7392完整、原1800W0概率/LP零差；SFT→DPO三措辞Brier+.313/.342/.377且CI均正 | 原任务stage变化不是单个同义措辞的偶然现象 | 只由原definitely/probably组合造成 | 高描述，低能力归因 | 独立source同时测动机归因与人物评价，E61 |
| OLMo两post-stage的copy全对、full mass高，但无对话prior也向probable-yes移动 | 条件判断仍受回答规范/类别prior影响 | “改词后稳健就证明pragmatic competence退化” | 高技术，中观测 | E61全部null/完整mass/两目标与单句control，不另加IQAP alias |
| E60原17280cache/752human核对，独立arithmetic与author functions <1e-12；六scene每cell约15人 | 新parent可供独立条件关系驻留 | 下载PDF或重复次数等于场景数量 | 高源与算术，公开表有少数版本差 | E61小型辨别pilot；需要扩展scene时按独立方差设计采集 |
| ELM人类即使consulted exact source仍常选不知道；social effect变化弱于简单理论预期 | 多动机账户、语境来源需分别建模 | knowledge availability＝perfect epistemic access的硬negative gold | 原source强，因果机制待识别 | 取得完整Exp2 stimuli后考察实际证据，不先换成全局literal指令 |

| Observation | 支持解释 | 削弱解释 | confidence | next discriminating experiment |
|---|---|---|---|---|
| E61 12576完整，256独立数值控制通过；SFT→DPO trait MAE−.0737[−.1043,−.0467]，DPO→最终trait+.0354[.0119,.0601]、motive−.0535[−.0765,−.0266] | 两目标的任务读数变化可不一致 | 一个改善分数概括所有交际判断 | 描述中，能力解释低；仅六scene | E63独立source的实际reason条件，而非第三prompt救分 |
| E61 chat trait mass高但motive OL SFT/DPO/最终 .515/.261/.429、MistralInstr .041；单句还能使mass大降 | 任务映射/输出支持是主要替代解释 | 用归一化数字直接证明目标能力分离 | 高技术，未识别语义能力 | 保留全部入口/full/content；不挑最佳接口升claim |
| E62原三实验4192行/262retained，共享16scene；全人四trait/均值算术核对，E2两素材规格不可无歧义展开 | 有自然理由→社会评价的强parent与可审资产 | 下载原数据即可声称48独立场景或全协议复现 | 高源审计，未复现原lmer/UI | E63预先固定14可展开scene，另两项及全部human norm保留 |

E63卡先于source展开与GPU，11040读数八独立卡运行；字串读取不是semantic motive能力，不将四trait差的差单因果归时间泛化。C01/C02仍L0，I01仍SEED。结果未收齐前不作效应判断。

账本澄清：E59的措辞稳健阶段分布差异登记C03/L1任务观察，引用原卡与全量结果；不把未识别能力误写成从未观察。没有升L2或机制/论文就绪主张。


E63完成11040/2.90012GPU·时，source/概率/256数值gate通过：人类Ina−Unw体贴+.5497[.2924,.7988]，OL SFT/DPO/最终−.3629/−.3338/−.3659（各sceneCI负），原/单句与full/content同向；Mistral原−.6885，QwenInstr+.1284。支持实际理由条件的评价响应在这些检查点不同，削弱全局同一方向；confidence描述中、解释低。quote基本读取控制未共同可用，不能称知道却误用；E64同原输入直接生成进行读数校对，而非新prompt恢复。全部8模型与边界见E63完整summary。


原问题对照结论：原terrain尚未被有效检验，更未被否定；当前C03和E63都不等价Hit/FPR或discriminability/criterion分离。主要执行漂移在遇许可缺口后不断换读数与邻接对象。用户要求主对象恢复；数据构造/规范验证应优先，社会评价不再扩主矩阵。E64已完成五post-stage，其体贴方向延续实际生成，但Qwen原parser另有terminal suffix错误，POST-HOC无损审计保留primary，不将invalid作能力失败。完整阶段性结果/CI/bounds见E64-interim-generation-audit.json；三Base仍未齐，不升科学主张。

### 用户要求清理额外扩展

人物评价、角色、noise repair退出当前执行计划；I01与额外分支文件已按用户要求删除，原记录从git历史追溯。E64队列与两剩余Base已停止，六模型完整、两部分（488/398），全八输出保留，见停止快照；不比较完成模型stage，不升级claim。过去记录中的“下一步”由当前README/DATA_PROTOCOL替代。核心许可缺口仍未解决，不将邻接任务的不支持结果归到原问题。
