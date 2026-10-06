# E60：问句在哪些层消费源句？（2026-10-07）

- **状态：** DONE；科学运行前登记。生成器E431已在运行前改用本线菜单保留E60。
- **类型：** PILOT。
- **对应：** I05/I03/I04、C06–C09、P13/P14。
- **问题：** 保持所有源句位置的计算不变，仅将后续位置读取源句的时机推后，能否选择性修好初始关系并保住正确关系？
- **来源：** E55完整三族中，预定前1/4层歧义区donor替换对MVRR initial有26–48pp因果影响，句末小；后层hard效应小但LP不零，最终block后替换无路径。它提示已消费到后续状态的竞争解释，而非证明语义在后层不存在。I05是POST-HOC新猜想，E60是前瞻检验。
- **阳性对照：** 原cue同题源理解、4D BASE与E54同输入评分；源位置所有层hidden必须不变；一条修订指令的E54全部结果保留；相同切断层数量的早/晚窗口互为预算对照。
- **噪声地板 + MIE：** FP32/eager；BASE prefix评分与独立2D差<.001，源hidden数值同布局应为0（允许逐位置abs.001或relative L2 1e-5），无未来边新增。5pp仅信息参考，不自动升级。
- **决策表（跑之前写）：** early cut选择性GP改善且cue/final保持、late cut不同→独立新用途/源中介定位检验消费时机；early/late都类似→一般信息/响应偏好仍竞争；cue或原正确关系降到地板→干预分布变化，不能判断能力；全部null→不证明无正确state，回到完整E53及其他问题，结束当前局部干预链，不再扫更多层阈值。

## 数据与固定条件

沿用E54完整1014QA/507同题pairs，四构式、三族Qwen3-8B/Gemma3-12B-it/Llama3.1-8B、原revision。无需T2定位子集，恢复全部原定资格；不是根据E55效果扩大/筛入某个construct。原S/Q/gold/source SHA不改，G2源支持、两顺序×words/letters、FP32/eager/seed60，全体与same-gold、initial/final分别报告。世界T1 E/C/N不能与“内部parse”混淆。

## 操作

源token集合S由原offset确认；句末token可带尾随空白，不能含Question非空白字符。后续位置集合A为S最后token之后的全部有效prefix位置，包含分隔符、问句、选项、答题prefix，防止未切分隔符充当来源桥接。原任务不输入答案。

以L为decoder block数，k=floor(L/4)、h=floor(L/2)，五个预注册条件：

1. BASE：4D原因果mask。
2. CUT_EARLY_QUARTER：block 0..k−1中，切A queries→S keys；之后恢复原因果访问。
3. CUT_LATE_QUARTER：最后k个block中切同类边，其余因果。
4. CUT_EARLY_HALF：前h个block切同类边。
5. CUT_LATE_HALF：最后h个block切同类边。

早/晚相同层数量、同token位置集合及同新增删除edge预算。不改变源queries的任何mask；源位置保持原语义计算，不放开未来、不替换状态、不引入新事实。每层具体mask在decoder pre-hook注入，严格检查预期block均触发且shape正确。不是直接假定“深层必然更语义”；源本身是否形成正确关系尚须后续具体中介证据。

## 读数与解释

每族/构式/目标/readout报告相对BASE的GP、cue绝对gains与两mapping的错→对/对→错；对早/晚等预算直接配对。按连接lexical cluster平均、10k bootstrap95%CI，accuracy/probability及全部切片保留。不挑cut窗口作总体估计，不从更喜欢No的单类变化称角色修订。

同一early cut对GP final/原正确关系的损伤是保持性读数，晚窗口是位置时机控制；source states不变才能解释消费路径，依然不等于已证明高层parse机制。E55定位子集与本全体不混报n，末层post-block源patch的结构零不作为本mask晚窗口的先验结果。

预算3卡独立≤1GPU·h/族、20280预定评分/族；先同模型固定输入数值/路径校验再铺全体，共享GPU槽、不触碰既有服务，HF离线仅镜像。原失败/排除及代码/model/data/config/prediction SHA外置E60，git仅代码/卡/小摘要。这是E54后的第2个局部追问，结束后不续做同一mask/位置网格。

## 结果

完整三族各20280评分，GPU·h Qwen .4080 / Gemma .5921 / Llama .4556，合计1.4557。三族BASE相对E54同输入0hard flips，max LP delta .000288/.000076/.000051；源所有层hidden不变、等预算窗口与只删除后续→源边的校验通过。合成统计fixture验证了mapping转换、修复/损伤、早晚配对、缺失不填零、单cluster无总体CI；不是科学结果。

预注册ALL-literal/words/same-gold切片：NPZ initial前半层切断GP gains +76.28pp [69.64,82.91] / +80.10 [73.47,86.22] / +63.01 [54.34,71.43]（98clusters），final却−79.49 [−85.96,−72.75] / −82.58 [−88.76,−75.84] / −69.38 [−77.81,−60.39]（89clusters）。MVRR initial相同干预+35.83 [20,50.28] / +38.89 [21.67,55.56] / +36.67 [22.78,51.11]，cue−30 / −14.44 / −6.67；final也未保住。早/晚等预算差明显，但不能把初始No题收益称为选择性修订。全部四窗口、四构式、两目标、两readout、概率与转换保留。

POST-HOC描述核对：前半层切断全体words选No频率分别增加59.40pp / 70.79 / 52.81，支持响应偏好/信息损伤作为竞争解释，不能单凭这个比例完成因果归因。mask仍有分布变化，晚窗口弱效应不证明深层源中没有关系。

完整结果`/data1/xiangding/work/incremental-interpretation-revision/E60/source-consumption-depth-map-v1.json`及cluster-effects；git小摘要[结果](../results/E60-source-consumption-depth-summary.json)引用data/config/predictions/完整结果SHA。C06–C09仍L0；I05“选择性推迟消费会修复”没有获支持，SEED状态不改，结束当前mask/位置扫描。下一步E63在同一任务未知的源前缀上，将同一donor状态用于原QA和自由角色表达，检验E55是否超出Yes/No输出；不是继续优化窗口。
