# E61：同自然source的动机推断与人物评价（2026-10-03）

- **状态：DONE。** 卡先于CPU预检/GPU；预检全过才跑。
- **类型：REPRO / D2。** C02/P02，I01仍SEED；新候选对象由数据决定。
- **问题：** 在同一原对话上，训练变化在“为什么选这种表达”与“说者给人什么印象”两种判断上是否一致？如果人物评价更像人，动机归因是否也更像人？不是把二者相关自动当机制。
- **数据：** 原Social Meaning六scenes×low/high precision需求×precise/approx表达=24原场景条件；六trait原MIN评分与原ELM Task3十个多选动机。原human Experiment1 retained362人，每人一场景；每cell约15人，六场景不是1536独立scene。不使用缺完整stimuli的Exp2做模型输入，不筛选model正确项。
- **迁移：** trait保留原MIN prompt全文；Task3保留原十选项与措辞，但派生逐动机Yes/No query，读人类checkbox marginal，非原联合多选任务精确复现。所测是听者印象/动机归因，非说者真实人格/内在意图gold。分组保存human counts，不做licensed/unlicensed标签。
- **读数：** 原trait七个完整numeric+EOS候选，动机Yes/No完整+EOS；content secondary、candidate mass、无dialogue prior全部报。1536 natural/model（24×16targets×bare/chat×原/单句control）＋36 reference-copy控制=1572/model，8共12576。FP32/eager/noTF32/batch1，0training/API/judge；stage/path/revision与E59相同。
- **阳性对照：** E60原17280closed cache完整与source/person/count/评分parity；每数值1–7及Yes/No都有明确reference-copy，只用于支持/映射检查，不冒充自然理解。新增一句control固定“Evaluate the listener's impression warranted by this particular dialogue, rather than the speaker's actual hidden character or motives.” 两任务原/单句同报，不选最佳prompt。CPU全量prefix/terminal/family actualIDs/source；每alias/interface/kind首末repeat与独立full teacher forcing门控。
- **噪声地板 + MIE：** .001 LP/prob，repeat1e-6；主stage配对变化/precision×context interaction的scene bootstrap2000seed0，n=6明确粗粒度pilot。human participant bootstrap保留每cell人数作为敏感性，不将采样数当scene n。评级MAE差≥.25或motive probability误差差≥.10改变后续解释优先级，非自动科学门槛。
- **当前解释：** A人物评价改善与动机归因改善相随；B只改变人物评价/表达规范；C都依赖入口或任务映射/输出支持；D都已很好。不同指标范围/难度不是构念不同的证明。checkpoint单seed、训练算法/数据/budget共同变化。
- **决策表（跑之前写）：** A来源条件关系一致、controls支持→再对原明确knowledge信息做独立证据干预，区分表示与回答policy。B两目标稳定不同→优先查量尺/多选转binary/群体分布/词汇prior，原Task3联合读数验证后才解释。C控制/质量/单句影响巨大→记录未识别，禁止再加prompt救此source；回原材料或构造可识别数据。D记录成功，用实际knowledge信息查是否迁移，不转向造坏例子。任何结果都不自动升C02/论文claim，不把“知道但不用”改名创新。
- **混杂审计：** 同材料两个判断但非同观测构念、checkbox query迁移与human order（trait先、motives后）不同；没有新human paraphrase norm；模型restricted likelihood非原T1×10采样。原social paper拥有direction/strength与theory prompting，我们只驻留其新source，不claim首次。all aliases/interfaces/fields保留、full与content分别报。
- **算力预算：** 八独立单卡lock、≤4GPU·时，加载前实际memory<10GB，不杀他人进程。cached local only、不下载weights；raw E61-*不覆盖E59/历史结果。

## 结果
12576/8模型完整，3.18849GPU·时；256独立full-logit/repeat controls通过，所有source/实际input/脚本hash/概率算术全量校对。原聊天trait完整candidate mass：OL SFT/DPO/RLVR .975/.985/.999，Q25Instr .9999，MistralInstr .978；motive分别.515/.261/.429/.999/.041。copy支持不能排除自然任务映射和partial support问题。

OL SFT→DPO聊天trait mean-rating MAE改善−.0737 CI[−.1043,−.0467]，七类human Brier差+.0117[−.0123,.0321]；motive selection MAE差−.0271[−.0443,−.0084]。DPO→RLVR trait MAE差+.0354[.0119,.0601]而motive MAE差−.0535[−.0765,−.0266]。都是六scene粗粒度任务读数，小于预先改变优先级的.25/.10 heuristic；概率距离不是模型内在confidence校准。

按决策C/B执行：两任务入口质量不一致，单句也大幅改变motive support（OL RLVR .429→.0133、MistralInstr .041→近零），不能把二者差别讲成能力分离、不能用无效Base候选归因stage。没有追加第三prompt或优选恢复入口；E63转入独立原人类E2的实际reason证据条件，不重复本source措辞优化。所有traits/motives、full/content与原/单句条件完整见[结果](../results/E61-social-motives-summary.json)。C02仍L0、I01仍SEED。

跑前补充：Task3引用原完整回答句与对应alternative句（而非human UI只引用numeric substring）；这是已声明的query迁移，不声称逐字复现。source audit的tuple字段仅JSON canonicalization，不改数据/标签。未完整取得Exp2 stimuli，故不移植其人类counts到改造句。

读数解释补充（不改冻结输入/输出）：null仅competent和lack-of-exact-knowledge两个示例任务框架，不是全部16目标的matched prior；不能以这两个null排除所有目标词汇先验。
