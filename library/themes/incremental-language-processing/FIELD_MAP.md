# Interpretation revision：阅读地图与当前解释（2026-10-05）

研究对象保持不变：后来的语言证据如何改变先前解释，以及改变后如何用于继续理解。推荐材料是入口；不是固定paper题目，也不是门槛。

## 已读正文与贡献归属

| 工作 / 正文来源 | 实际读数与研究动作 | 已覆盖的主张 | 对当前探索的约束 |
|---|---|---|---|
| [Jurayj 2022](https://aclanthology.org/2022.blackboxnlp-1.25/) §2–3 | component variants；surprisal、hidden-state几何；歧义延长、blocker、comma/that/unreduced | 不同构式的cue效应、潜在但未实现的GP | 这些操作不是我们发明的；repo 43/19/28 与文中43/20/20不一致，按固定revision报告 |
| [Li 2024](https://arxiv.org/abs/2405.16042) Methods–Discussion | 24 NPZ；五chunk；初始命题Yes/No概率；comma；probe parse shift；attention | lingering、incremental sem QA、comma改善、重分析spillover | 两解释读数/时间曲线/逗号效应单独不新；论文预检final question高后主要测initial，不能据此假定我们的final正确 |
| [Amouyal 2025](https://aclanthology.org/2025.acl-long.403/) §2–7 | GP/nonGP、plausibility、verbtype；同题人机；释义和图像验证 | 结构困难、合理性补全、论元需求及跨任务相关 | 本文明确optional-transitive初始命题常是“未必”而不是逻辑假；不能把No accuracy直接写成消除初始表征 |
| [Amouyal 2026 v1](https://arxiv.org/html/2510.07141v1) + release | 七类结构、难度排序；Qwen8 exception；prefix实验 | 更广构式的人机difficulty profile | 我们的E00/E03反转不是“首次发现所有LLM都会GP” |
| [Cao & Schuler 2025](https://aclanthology.org/2025.cmcl-1.20/) §3–7、appendix stimuli | 30 RC/complement prefixes、50 completions/项；构造无合法completion的error对照；72 reflexive pairs | inverse scaling、局部矛盾可能被当成文本错误；下游binding检验 | 好实验的关键是追加error对照区分两解释；“初始parse影响下游”也已被测过 |
| [Hanna & Mueller v1](https://arxiv.org/abs/2412.05353) §4–7 | GP continuation；SAE circuits、因果干预、action probe；QA circuit | 多parse特征；预测的syntax特征很少用于后续QA | 泛泛representation/use gap不新；其结论依赖模型/读数/feature operationalization。阅读不意味着执行SAE/probe |
| [Baitalik & Datta 2026](https://aclanthology.org/2026.acl-srw.32/) §3–7 | 100 GP/control pairs；surprisal vs pseudo-surprisal；downstream AUC、hidden divergence | 架构相关disruption/recovery signature | 不能把surprisal回落叫最终解释已正确；三构式/架构对比和recovery曲线已有owner |
| [Zeng 2026](https://aclanthology.org/2026.findings-acl.57/) §1–5、Limitations | 4090 prototype/metaphor pairs；Gemma；noncausal oracle；value信息传递、word-specific steering | 后续token承担延迟语义计算 | “原token不更新、后续token整合”已有owner；句法revision不能自动等同该metaphor机制，steering能控制生成也不直接证明实际晚cue依赖同一途径 |
| [Huang 2024](https://tallinzen.net/media/papers/huang_et_al_2024_jml.pdf) RQ/Methods框架、Comprehension/General Discussion | 2000人、七构式；filler拟合surprisal→RT；对关键项检验数量、排序和item差异 | surprisal不足解释人类disambiguation cost | 提醒明确解释对象；本文跨构式reading-time证据不能直接当我们LLM问答的机制解释。具体模型拟合/附录未读完 |
| [Hassan et al. 2026](https://arxiv.org/abs/2607.15565) §1–8 + A/D/F/G/H | VLM顺序反转；echoing；outcome-independent注意力knockout；内容/计算/距离控制 | 提前question影响编码、末尾question负责访问；重复解决分工 | 通用task-position/readout故事已有强owner；需语言revision的具体预测与后果，而不是把image换成句子 |
| [Yoshida et al. ACL 2026](https://aclanthology.org/2026.acl-long.1694/) §1–7 + Limitations | 受控训练概率能拟合人类GP，held-out词、自然语料和跨构式检验；SRC/ORC失败对照 | 现成LM失败不足否定surprisal解释的存在性 | 更新Huang之后的争论；固定模型问答失败也不能直接归因revision算法；不是当前做训练的理由 |
| [Han et al. 2025 v2](https://arxiv.org/abs/2504.09402) §1–4 | 分步阅读/重语境化；数学题中添加Revise条件；attention与错误类型 | backwards-dependency难度、重复/指令修复 | 这些通用结论也不是新故事；添加条件的干预仍混杂长度和任务改变，需要更明确语言证据预测 |
| [Maina-Kilaas & Levy 2026](https://arxiv.org/abs/2603.23624) 正文Methods/两实验/Discussion | GP×extension×comma/object×finality；Maze与SPR | digging-in受测量位置/任务影响，非句末没有明确正效应 | E01 extension不能自动解释为时间越长承诺越强；他们也未证明严格零效应 |

PDF正文在本地 `.../incremental-interpretation-revision/papers/`，两份reading-manifest记录URL、页数、hash；原文不进git。以上标明读取范围，后续读实验/附录再更新，不将下载等同已读。

## 领域真正有争议的事情

- surprisal的disruption、最终问答、可提取parse、生成的后续依赖不是同一个现象。已知它们能不一致；更值得知道的是何种证据、任务或条件决定这种不一致及其后果。
- 结构不许可一个对象附着，并不排除事件在世界中发生；NP/S知道一个命题也不排除认识其参与者，passive事件也不总排除主动/intransitive命题。诊断必须区分句法角色、assertion和可能性。
- 小模型回答失败不等于incremental parsing失败；强模型错误也可能是noisy-channel修复、论元补全或回答默认值。控制应改变解释所需的证据，而不是只换更多模型。
- “读完后再问”与“带着问题读”的差异可能值得追，但当前E03只证明行为对顺序敏感；尚未证明task-directed revision，也未排除距离/格式/回答倾向。需要语言条件×任务位置交互及其解释。

## E01如何提供信息

同一lexical set保留GP、显式cue、blocker/lexical replacement、extension；逐项独立模型审计后比较role与asserted-proposition读数（最新用户授权opencode/Step均可，必要时Luna复核）。重点观察哪些操作一起变化、哪些分离、哪些随query顺序改变。报告所有配置与配对CI，不把任一漂亮模板当结论。

若只有已知GP/cue效应，继续把它当measurement；若出现稳定、能改变预测的交互，再登记一个自然RQ，读其最近邻并设计能区分至少两解释的追加实验。当前没有已经证成的新paper idea。

## E08反馈与定位更新

固定最终问句于句末，句前initial−final focus的GP−nonGP交互+1.45 pp [−10.14,+13.04]；句后final focus提高GP与nonGP的原始No得分幅度相近。提前相关initial−无关initial的概率交互存在，但67-set敏感性及near-floor不允许选它称特殊revision机制。见[E08完整卡](../../../workbench/incremental-interpretation-revision/experiments/E08-reading-focus-versus-final-query.md)。降低泛泛reading-goal叙事的支持，优先E01语言操作与双读数，不继续优化prompt赢家。

近邻读出/echoing不自动否定语言修订问题。当前仍未区分：旧事件的词汇合理性补全、句法角色重分析失败、以No回答但不建立正确最终解释。要让三者对同一个语言干预给出不同预测，才能从测量进入idea；区别概念本身不是finding。

## 从阅读获得更好的原始资产

Huang/Yoshida共同使用的SAP有原始人类理解题、两选项、作者gold，省去自构元语言问题。[E09](../../../workbench/incremental-interpretation-revision/experiments/E09-published-comprehension-transfer.md) 用同题GP/early-cue×query-order×选项mapping检验E01问题是否迁移；24共享词汇组按cluster抽样。Excel与CSV的6个歧义target flag分歧保留两种来源，不自己重新标注。未下载人类participant数据，不能把已发表汇总当已完成逐项人机对齐。

MiMo外审概率探索层只保留完整normal-finish、逐题覆盖和hash一致的行，全部gold=null；与Step5层隔离。初始两组NPZ有extension/role/semantic分离，但样本很小、free审核仍需复核，当前只是后续测量线索，不是稳定新主张。

## E09/E10后当前最值得追的压力

原始SAP题仍有真实cue效应（句先pooled +33.33 / +19.44 pp，两个mapping），所以不能把全部GP困难归为自构元语言问题。但拆Q/options位置后结果依赖mapping；固定options末尾，Q的位置交互在一个mapping由cue条件答得更差驱动，另一个mapping的CI跨0。暂不以query-order提出paper主旨。后续优先解释E01中无歧义extension也使role回答下降的异常，而不是继续找获胜prompt；仍需同item语言证据与下游后果，不能只把role/semantic不同叫novelty。

近日primary检索另发现：[Lee & Shin 2026 paraphrase](https://pure.dongguk.edu/en/publications/probing-good-enough-processing-in-large-language-models-with-a-pa/)、[Storer & Zimmerman 2026 trajectory](https://arxiv.org/abs/2610.00840)、[Acevedo et al. ICML2026](https://proceedings.mlr.press/v306/acevedo26a.html)、[Han et al. ICLR2025 causal assessment](https://proceedings.iclr.cc/paper_files/paper/2025/hash/88139fdcc82fc597090620d77b023282-Abstract-Conference.html)。均目前只读primary摘要，不能冒充全文核对；这些方向的任务变化/轨迹/语义几何/表层敏感性都有近邻。venue nearest已在部分18013条库运行（ICLR2025/ICML2026），完整fetch仍在进行，BM25有不相关的garden/path误匹配；不是完整novelty证明，也不依据拒稿标签判断我们的idea。

## Sasano依据

按仓库[原始品味入口](../../../search/sasano-taste/README.md)：自然、清楚、结果本身值得知道，一个RQ对应一个finding；不以模型/数据更新或概念二分作为题目生成器。我们据此评估观察，不替人宣称他已认可某个idea。

## 再读近邻：局部修订与整体理解不能靠概念区别充当增量

新增实际正文卡：[Slattery2013](slattery2013-competing-representations.md)、[Ceháková2023](cehakova2023-diverse-reanalyses.md)、[Storer2026](storer2026-contextual-trajectory.md)、[Han ADCE](han2025-causal-comprehension.md)；邻域定位[Belief-R](wilie2024-belief-revision.md)只读定义/构造，未查完结果。Slattery E1 downstream reflexive和E2次句后果已区分新parse与旧解释；Ceháková自由答案展示merged/partial/incoherent等不同结果。因此不能把“两读数/下游后果/局部与整体不同”写成首次提出。Storer的高GP轨迹分类也不是事件正确的证据，critical-token holdout约54.9%的失败需一同阅读。ADCE强调表面敏感不足推翻意义理解，但其介入近似/正确样本选择/标签意义保留都有限制；不照搬指标宣称内部因果。

E01 snapshot2的三NPZ原题短final semantic≈1但role≈.013；cue extension仅role下降。这使E11成为必要instrument检查，不是新paper主张。NPZ和MVRR extension的final semantic方向也不同且n≤3；先确认语言操作的读数有效性，再看晚证据影响哪些实际事件依赖。新发现OSF有Czech原题作为潜在资产，尚未下载/审计；不因可获得数据而立即换语言或研究对象。

### 扩大venue扫描与已发表近邻核对

本地venue corpus已扩为36,979条（当前下载完成文件；2026ACL等尚在fetch，不是完整覆盖），nearest首先返回Hanna/Mueller NAACL2025与Amouyal ACL2025。已核对Hanna最终publication §6和附录C/H，保留“不广泛复用”的owner，同时记录不完整faithfulness与跨构式非特异干预的范围。nearest只是定位，不按接受/拒稿评分判我们的题。现cache17个PDF版本/16篇不同论文，下载不等于读完；ledger逐条注明范围。

E11首批n1诊断中，完整subject span把unambiguous extended blocker原role .0404提高到.9999，而原final semantic=1；四既定配置full-span均恢复，head题先仍可失败。支持先前extension效应含instrument成分；不是所有GP是伪影、不是新revision机制。GP短句full-span与原题相同仍失败，待新GP long问句独立审完再判断。不能把反映元语言题理解的变化改名成模型思维修复。

## E12：更具体地分开source processing与最终answer，但不把gap改名为idea

同一E10全部原prompt里，固定options末尾的Q前−后×GP−cue在disamb word为+1.47 bits [.47,2.52]（repair+1.54）；主要cue降低surprisal−2.22，GP自身区间跨0，因此“提问加深初始承诺”尚不成立。与原cue QA下降并列可知这两个读数不能代替；事后平均mapping有cue accuracy −11.11 pp [−20.14,−2.78]，只有8/24clusters同时word改善/QA损伤，相关也不支持统一逐项反向机制。全部分项/局部和whole指标保留。

[Hu & Levy2023](hu2023-metalinguistic-measurement.md)已明确prompt/probability gap；Hanna2025与Hassan2026也拥有预测/QA特征与early goal/late access叙事。下一阶段用已有Slattery自然后文，区分没有问句的input-history影响与问句再激活/元语言额外需求。不是“有后效应即novel”，仍需晚证据传播的具体范围和解释。当前18个PDF版本/17篇不同论文缓存；COLM Hu/Frank PDF直接403，不能当全文已读。venue corpus 41,117记录，2026ACL已加入；ICLR2026等缺源仍明示，检索不作科学判决。


## E13与下一信息问题

原24两句/96作者条件、无诊断问句：全S2 GP−comma −.031 / −.003 bits，两CI均跨0；literal reference交互+.905 [−.296,2.260]，其后两词−.377 [−.637,−.111]。不能用局部分项把整体null改写成稳定lingering或宣称彻底消失。复读Slattery E2 rationale与Table4确认作者早已对比全局失败/局部hangover/plausibility；其中RAT/reciprocal强制自指事件是published setting，不等同所有optional-transitive初始事件在逻辑上都错误。

当前核心压力是**晚证据改变哪些角色和事件依赖、哪些后果仍被先前解释影响**。E11显示问句引用问题，E13限制泛化全局残留解释。先用E01新固定外审cohort扩大独立词汇覆盖，不追加更多position模板；找语言操作的稳定分离后才设计能区分残余事件、语义补全和问答影响的干预。这个问题框架不算已形成新idea。所有现有材料和干预的owner仍明确列出，不能把“区分两个读数”当增量。


### E01扩大后仍需语言因子拆解

固定279独立审核变体/1158eligible QA，三个family、四配置全测。NPZ同9组initial-event的extension GP−cue交互句先+51.63 [21.60,84.02]pp（repair+40.98），题先−20.29 [−53.11,9.93]（repair−10.66）；不能统一解释为延时增强承诺。NPS“长GP降低final-event”主要由源7原had rode marginal句驱动，预登记acceptable层大幅减弱；保留两个strata，追数据why。NPZ无歧义extension仍降低原role回答，不能略过E11引用压力。

下一语言干预须分开**等待多久、modifier加入什么事件信息、NP引用复杂度**。先外审原modifier是否独立许可/支持初始事件，再设计同词数/信息或位置控制，不继续扩query模板。不同答案质量和不同时点的概率不自行组成内部双parse机制；[E01完整统计](../../../workbench/incremental-interpretation-revision/results/E01-external-snapshot3.md)与E13都只为下一区分性实验提供预测约束。
