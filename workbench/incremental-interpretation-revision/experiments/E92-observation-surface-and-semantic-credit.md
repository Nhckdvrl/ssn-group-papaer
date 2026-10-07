# E92：固定同一解释，重建奖励是否受观察表达形式支配？（2026-10-08）

- **状态：** DONE；生成器E431在任何科学效果前改E92。
- **对应：** P20 / I06，C06–C09；E91首次内容reward探索，唯一第二核心对比，不衍生reward提示/温度网格。
- **问题：** 同一个实际解释P对原Source的重建评分可能遗漏语义修订收益；将目标变成原发表配对的消歧表述，是否更能奖励忠实关系？同P/同grader/同rawcontext，只变观测surface，反向给原cue输出重建GP观察也完整测。
- **数据：** E91原648输出/108Source不动；E63 donor_sentence_sha256定位发表GP-cue母句，按已有E70同问句Gold一致的input资格保留100Source（50pairs）/600P。4pairs（NPZ1/MVRR2/NPS1）的commonQ Gold不一致，效果前排除、原因全文留表，不新审原语料、不按模型分数挑。14Source还存在独有问句，E92语义读数仅使用两侧共同问句；对应P的原双盲标签直接复用，完整原atoms/指标另留，不改变E91主读数。所有generator/输出条件仍在，0API；commonQ一致不是全语义同义的证明，资格只承诺注册关系不改变。
- **条件：** 对每P使用配对Source为teacher-forced观测目标，context/Source原P/空prior/固定action与E91完全相同，3当下grader×600=1800新评分；E91原目标全部重用，限定同资格cohort比较。GP端是消歧表述重建，cue端是反向歧义表述重建；不是添加新事实，也不是直接给QA提示。
- **主读数：** mean token logP的TARGET_BANK−BASE_BANK变化（paired目标长度不同，不以sum幅度当交互主读数）；奖励排序与Δ正关系保留/Δ未支持断言/Δ保真的全cohort sign alignment，重建配对Source相对原Source的alignment差；Pearson/cluster CI与tie数辅助。原sum/实际token长度全保留。Source→lexical cluster，10000bootstrap seed92；逐grader×generator×构式×两原侧全报，缺Gold维度NA保留不造0。
- **阳性对照：** CPU全部600目标文本/对应SHA/共同Q Gold资格逐条核对；原context SHA逐个匹配E91。固定输入首个Source reward两次LP完全相同，sum/mean=逐token计算；一套raw模板不换措辞，已有非歧义侧是反向压力而非事后选正确子集。
- **噪声地板：** single-sequence BF16/eager/full teacher forcing、固定母资产/parser无新label。两目标各自SourceToken长度记录；同一目标内两P长度差不是新增噪声控制网格，长度描述完整保留。CI、raw/代码clip-ties全报，clip方向已从作者selected代码核对，但本实验主读数为未clip mean，不以伪代码全tie诊断训练。
- **决策表（跑之前写）：** 消歧目标明显改善语义alignment、反向破坏且跨grader稳定→自然表达形式使观察重建credit漏掉语义修订，下一为具体reward目标设计/社区真实update检验；只是LP涨分但排序不改→可预测性变化不足以成为新机制，修改假说；两向都无改善或大异质→这个canonical-target方法未定位稳定缺口，回真实输出/新的独立内容节点，不继续template/score calibration；输入语义资格不足→保留未知，不能把cue当GT方法。探索idea先行，不要求此pilot完成论文证据。
- **算力：** ≤1GPU·h，8独立H20 3/3/2、现有模型离线，0新下载/0新API。每任务08:55早释放、09:00硬停，之后不自行恢复。

CPU全三族600目标边界通过，1800原context SHA逐一与E91缓存一致。data SHAab4b6f2735910163d1e0fdc58ff980c6e32a6036266cd376ad54c3d954f81a5f；8卡已运行，完全复用同一scorer code（日志内E91是复用程序标签，实际root/配置均E92）；无新Gold或API。

## 完整结果与自审

1800评分/.075381GPU·h/0API，全72面板/900grader×P对，map SHA40fa568ee48ae16a588c5ca7798feca47b98399ef515645aaece491db4382883，[摘要](../results/E92-observation-surface-summary.json)。全部grader×generator×构式×两侧，alignment/meanLP interaction/正关系与错误断言/原反向cue、ties、不同目标token长度都读，未筛reward有效者。

- Q-generator GP，改用发表cue目标后语义alignment变化Q/G/M +.278[.056,.500]/+.222[.056,.444]/+.222[.056,.444]（alignment取−1/0/+1，不是正确率pp）。11个语义发生变化的P对，奖励一致/相反由6/5→11/0、3/8→7/4、5/6→9/2。全eligibleSource/同P不变，Gold缺维NA，按Source→cluster加权。
- Q-generator反向cue→GP alignment−.222[−.444,−.056]/−.111[−.278,0]/−.167[−.389,0]；另外两generator GP主变化Meta+.167/.167/.167（CI前两到0、第三跨0），Gemma0/0/.111（均CI含0）。不是所有generator共同普遍恢复。
- 主要来自MVRR：Q-generator该构式GP+.615[.154,1.077]/+.615[.154,1.077]/+.462[0,.923]，反向−.615[−1.077,−.154]/−.308[−.769,0]/−.462[−.923,0]；NPZ多格弱/null或某G-generator下降，NPS多数没有语义变化，不能宣告两构式通则。
- 更高LP本身不是更忠实：大部分raw mean interaction正，原cue反向GP也有正的TARGET−BASE幅度变化却语义alignment下降；因此不以目标更易预测叫方法收益。正关系与减少未支持断言维度都完整保留，部分总alignment变化由No改善贡献。

**探索结论：** 同一解释的语义内容未变，registered common-Q支持不变，但观察表述改变会改变credit与语义修订的关系。它为I07提供一个新视角/方法问题，不是单纯表述校准；当前来自固定未训练grader、主要MVRR/一个generator，距离真实RL有效方法仍不确定。原输入4pairGold冲突/独有Q限定scope，不叫全部语义等价，也不说ABBEL被证伪。

E91→92这个二步块到此收束，更新竞争解释/近邻尺度，不继续surface/score模板网格。下一社区现成Belief-R按作者语用Gold检验前向判定与重建奖励的失配；不bulk审计。C06–08L0/C09限定L1不变，I07仅探索SEED，注册状态不变。

### POST-HOC语义校对完成（2026-10-08，旧结果保留）

8异常定点Step Plan项双遍全完成／2分歧裁决／agreement75%（只这8项，不是总体可靠性），annotation SHA5ab5c619368a6a4d4bd59d4322e087958f0603ceff1965b23ada1dffe8451943。patient源主动refusal改非蕴含、treatment致场景改NEITHER；省floor的cleaner P改NEITHER；bare progressive shaving P按lexical reflexive同口径改ENTAILED；其它锚保留。只改已确认packet的语义overlay，不改任何模型输出、评分、原eligibility或旧data/map。见[统一更正摘要](../results/E70-posthoc-semantic-correction-summary.json)。

E70全文2790scope重算，MVRR initial正断言修复Q/G/L+40[10,70]/+60[30,90]/+90[70,100]pp，完整正关系both+12.5/+25/+12.5仍CI含0，资格9→8簇。E91 GP语义cohort39→40、质量Q/G/L+.2667[.0875,.4542]/+.2958[.1083,.5001]/+.3625[.175,.5625]；G-grader/Q-generator同40源reward−7.093[−14.201,−.771]、其它8CI含0。E92原600条／50pair资格不重开，2P行更正、核心Q-generator alignment+.278/.222/.222及CI不变（仍主要MVRR）；其它generator弱。原token分区诊断是更正前cohort，保留历史scope，不冒充当前完整语义统计。不是独立人类Gold或一般机制证据，C06–08L0/C09限定L1不变，不继续这8项反复teacher投票。
