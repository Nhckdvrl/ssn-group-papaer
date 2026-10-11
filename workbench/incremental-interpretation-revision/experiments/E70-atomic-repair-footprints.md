# E70：同一源修补到底改了哪些断言，是否传递到依赖关系？（2026-10-07）

- **状态：** DONE；E64-v2完整效果后POST-HOC测量选择，原子标签读取前固定本卡与读数。
- **对应：** I03/I04、C09/P17。因果入口已有，完整CORRECT_ROLES只能说明所有关系是否共同正确，不能定位部分修复。输入排序首2 MVRR源已见真实V1受事恢复但V2仍错接/遗漏；不是为了证明原猜想追加防御控制。
- **问题：** 原歧义区修补是共同恢复源断言，还是仅改一部分、另一些不传递或反而损坏？聚焦隐式GP解释修订的后果，不做一般输出事实benchmark。
- **数据与方法：** 已有E64三族BASE_BANK/TARGET_BANK完整自由输出，一个核心配对对比；保留全部输入资格108units/54GP源/51clusters（MVRR19/NPZ9/NPS26；NPVP缺失明确）。原S/Q/gold/模型/源库一律不改、不重跑；只把已发表、最终已资格的**原始yes/no问题**作为新自由文本的语义原子。原问题来自E52 qualified-v3，可覆盖旧patch run没有评分但同一原S已有的其他问题；按S SHA匹配、Q去重，source G2 gold按原完成T1 ENTAILED→Yes、C/N→No映射。原FULL/CONTEXT/E63完整role图仍是既有证据，不再为了本新粒度重标所有条件。
- **新标注（不是重审可信源）：** Step只看PARAPHRASE与一个问题，判断positive proposition在该自由文本中ENTAILED/CONTRADICTED/NEITHER；不看原S、模型、bank、原source gold或旧T4标签，避免拿原S救回生成的遗漏。**每个PARAPHRASE/Q为一个独立标注项，每请求最多5个原子项**；不把5组×多问题打包规避用户上限。输出后聚回同一源的全部原Q，qid/文本SHA/schema/覆盖校验。Step Plan step-5-preview、4workers/共享总8活HTTP、medium effort/max32768、两遍独立打乱分批与第三遍分歧裁决，失败单条≤2语义重试。已有T4-v2与全部raw留存，新annotation不是替换旧类别。
- **主读数（新标签前固定）：** 每构式/GP或cue/initial-final-all/原source gold Yes或No：自由文本显式支持的比例、原Yes断言保留率、原No命题新增率（ENTAILED才算多断言），BASE/TARGET及TARGET−BASE。每source全部原问题共同保持源支持模式；源有initial/final正向断言时另报两者同时表达与单侧表达四格，以及其配对转移。没有某类Q的源记该原子缺失，不作无错；source No未在文本断言只说明未过度断言，不等于建立正确关系。
- **统计：** 先Q/同unit，再相同S，再lexical cluster，10000 bootstrap/seed70，source/模型/条件全部报告；unknown/failure独列、不当语义错误。共同正确仅覆盖已给问题，不叫完整latent parse。
- **阳性对照：** 原cue下源断言保持/同表原T4-v2；全部问题指纹匹配已完成metadata，不造新Q。schema强制输出qid与输入对应；相同P/Qpacket跨模型或bank只标一次，不能挑标签版本。
- **噪声地板：** 双遍一致率/分歧/unknown，全source CI；E64源干预已通过source-bank仪器，不加重复GPU baseline。第一固定小包仅检查接口覆盖，完整语义效应必须全包结束才读。
- **混杂审计：** 教师判的是表达文本，不是模型潜在状态；原问题可能含隐含agent/事件细节，某个正断言未表达不等于V1语义角色错（P15仍适用）。不按旧T4正确/错分类挑数据，不把“缺少错误”当“完整理解恢复”，不由名字相同推断依赖已传播。
- **决策表（跑之前写）：** 原子总是共同变化→部分传播失败猜想削弱，回源位置共同控制；同一源/同一bank只恢复initial正断言而final保持失败→用具体关系依赖选择下一机制实验；只删除原No但不建立source Yes→不是共同解释修复；原子与旧联合标签差异仅来自agent省略/含混→调整解释粒度，不包装新机制。全部族/构式的异质和null照报。
- **定位与意义：** Amouyal/Lee及人类good-enough拥有部分修复/混合解释。潜在增量必须是源位置因果改变哪些关系、哪些依赖没有传播的可预测规律，不能只把partial interpretation改名。Hanna一般syntax/QA分离、Geva task-specific KB跨用途不一致仍是近邻，而非自动否决。
- **算力：** 没有新GPU推理；API不限信用预算但保持Step Plan，校验/盲双遍优先质量。原始标签/输出外置E70，小摘要与代码进git。当前C06–08 L0/C09限定L1，没有合格idea。

## 结果

**标签完成前的解释范围校对：** `source_bank_routes.py::bank_hooks`逐层重写全部Source位置。TARGET_BANK中非目标位置始终为BASE，不允许目标修补在这些位置重新传播；目标位置的PAIR轨迹则已包含原quarter-layer修补后的计算。故本实验测固定混合源库下consumer表达哪些断言，不能凭“initial改变而final未改变”独立证明native Source内部传播失败。原FULL_BANK/E63 PAIR允许该quarter-layer干预的后续源传播，但也不等于完整真实cue输入。保持所有读数/数据/条件；这是解释范围收紧，不追加控制或重跑。

完整原子标注与地图现已完成，结果见下。

**标注前范围收紧：** 第一构建草案包括六个旧科学条件，未发出任何HTTP，依用户“只最核心有辨别力”指导收为BASE/TARGET一个配对对比；三族/全部源/两侧不筛。不是用新标签选条件，原草案与manifest外置保留，旧全图不变。每原子P/Q一项，≤5项/请求，不借复合packet打包多于5个标签。

648原输出assignments→1280独立P/Q标注项。data SHAcdb513311ab5792a5a5377f5178c96615d46a042e4e991398bc9ec830e521880、assignment SHAe00b45caf8802f42960d4d8a3d06b31b9a870e139578e8c07eea9f8413b77c36。初版将needs_revision设False，被通用queue过滤成空输入，0 HTTP/0科学标签；空日志/summary保存，改queue标记True不表示重审原S。已核对全部1280进入队列，实际审核1263766/完整地图等待1274278。所有未知仍missing；部分修复/最终损伤/未知排除/四格与空构式的合成fixture已通过。未读部分语义比例。


### 全部标注与语义结果、自审

1280原子项双遍全部完成，183/183分歧裁决，一致率85.703%、unresolved0；2790完整reports（846空格、108单簇CI不可估），648输出assignment不筛。map SHA5954e972bda6ba627f2fc0168cd425440ea6eedb1dec40174e2763ff973329a5，annotation SHA45dceaa16a89a8e5fc3e39fd1e923d7313854eaa639a3c322de67737c1f337ec。所有构式/两侧/全部指标已读；Yes正确与entailed相同，No正确为其补数，joint上下界在未知0时相同，已逐格核对。

MVRR GP initial sourceYes表达TARGET−BASE Q/G/L +30.0 [0,60] / +50.0 [20,80] / +80.0 [50,100]pp（10clusters），确有正断言补出，不可把改善全部解释成删除No。final sourceYes +0 [-20,20] / +13.3 [0,33.3] / -6.7 [-20,0]；initial与final原正断言同时表达（9clusters）+11.1 [0,33.3] / +22.2 [0,55.6] / +11.1 [0,33.3]，没有共同完整建立。MVRR cue initial sourceYes -75.0 [-100,-50] / -66.7 [-91.7,-41.7] / -50.0 [-75,-25]（12clusters），final sourceYes +0 / +0 / +5.3 [0,15.8]；反向损伤集中初始关系，正断言both -66.7 [-91.7,-41.7] / -58.3 [-83.3,-33.3] / -33.3 [-58.3,-8.3]。

NPZ GP initial sourceYes +50 [0,100] / +50 [0,100] / +25 [0,75]（4clusters），both同向但CI均含0；9clusters全问题源模式联合差+44.4 [11.1,77.8] / +22.2 [0,55.6] / +22.2 [0,55.6]，不能都叫正确positive关系恢复。NPS只有1个initial sourceYes簇（非全No），两关系同时正向资格为0，initial No减少的CI都含0；未证成跨构式joint修复，NPVP没有cohort。全部空格/单簇/负效应与原问题粒度同报。

当前最好故事：固定混合源库能改变具体早期关系的表达，MVRR的反向效果跨族，正向部分恢复也真实。它没有共同恢复完整解释；因非目标Source逐层BASE回放，不能独立证明native源内传播失败。未达到合格idea标准，C09限定L1/C06–08L0不变；该原子脚印块自审结束，下一E84拆K/V核心consumer入口与E82当下强baseline，0原数据重审，无需人决定。

### 2026-10-08 POST-HOC语义标签异常定点复核（审核前写）

读E91固定按Source SHA排序的每构式前三条完整P/Q，发现patient原句的主动／被动／主句主体Gold互相不一致、cleaner省宾语P被标明确有floor、两种assistant-shave P对self使用不同蕴含口径。只复核这些具体疑点及同构式正关系锚，共8项；不是随机可靠性样本，不据此估总体错误率，也不bulk重审其它成熟社区数据。Step Plan／step-5-preview、≤5/request，两独立遍＋分歧裁决；题目／旧Gold／模型／条件／奖励都不发给teacher（只给原S或P及原Q）。通用最终词序／不得补论元／保留合理兼容事件的口径固定，新版本；旧标签、raw outputs、maps全部不改。0GPU。若确认差错，指出影响的Source／原子与各既有统计scope，以POST-HOC更正／不确定性报告，不删困难样本或升级主张。E93原1744社区Gold不受此审核影响。

### POST-HOC语义校对完成（2026-10-08，旧结果保留）

8异常定点Step Plan项双遍全完成／2分歧裁决／agreement75%（只这8项，不是总体可靠性），annotation SHA5ab5c619368a6a4d4bd59d4322e087958f0603ceff1965b23ada1dffe8451943。patient源主动refusal改非蕴含、treatment致场景改NEITHER；省floor的cleaner P改NEITHER；bare progressive shaving P按lexical reflexive同口径改ENTAILED；其它锚保留。只改已确认packet的语义overlay，不改任何模型输出、评分、原eligibility或旧data/map。见[统一更正摘要](../results/E70-posthoc-semantic-correction-summary.json)。

E70全文2790scope重算，MVRR initial正断言修复Q/G/L+40[10,70]/+60[30,90]/+90[70,100]pp，完整正关系both+12.5/+25/+12.5仍CI含0，资格9→8簇。E91 GP语义cohort39→40、质量Q/G/L+.2667[.0875,.4542]/+.2958[.1083,.5001]/+.3625[.175,.5625]；G-grader/Q-generator同40源reward−7.093[−14.201,−.771]、其它8CI含0。E92原600条／50pair资格不重开，2P行更正、核心Q-generator alignment+.278/.222/.222及CI不变（仍主要MVRR）；其它generator弱。原token分区诊断是更正前cohort，保留历史scope，不冒充当前完整语义统计。不是独立人类Gold或一般机制证据，C06–08L0/C09限定L1不变，不继续这8项反复teacher投票。
