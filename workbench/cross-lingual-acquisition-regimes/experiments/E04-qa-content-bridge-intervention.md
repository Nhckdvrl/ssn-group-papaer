# E04：QA内容覆盖与桥接复用的同源训练干预（2026-10-02）

- **状态：** DONE（seed17四格完整保存、统一重新计分）
- **类型：** EXPLORE（P03/P04的第二种真实学习substrate，不是先定的idea）
- **对应：** P03/P04；不承接E02单seed小终点差为claim
- **问题（一句话）：** 无标签双语CPT对后续生成式QA的价值是否依赖覆盖监督内容，还是同域且内容不重叠的桥接可复用？条件连接是否改变这个实际选择？
- **设置：** 统一MWB34K起点、E03同source QA监督与recipe。官方XTREME德语SQuAD train译料，公开GCS对象generation `1591613668067959`、size93188862、MD5 `uszApqUqjjtUneb/lk9JEQ==`，本地另记SHA256；EN来自E03固定SQuAD revision。按question ID关联，原始数据文本来源和唯一性检查，完整自然context+question构成单语文档，不输入answer/label。new在固定E03 train pool选8192；reuse排除所有E03 train/dev以及测试context，按逐语言长度匹配8192；报告unique context数与重复分布，预算逐语言loss token差≤1%，不足即停止准备而不缩小至幸存切片。正确paired/split固定同一输入、位置与BOS loss mask，沿E02的文档隔离定义；完整单位≤2048，不按gold裁上下文。CPT256 updates、micro1×32=32单位、lr2e-5/wd.01/warmup26、FP32 master+BF16、seed17；随后按冻结E03 source recipe重启英语监督，全部预算点EN/DE generation F1/EM。准备CPU不使用模型target性能；只有E03 source gate通过且三基线全曲线核对后，才决定启动哪些完整预注册cell或写amendment，不由单个target快照选protocol。
- **读数：** EN/DE绝对官方F1、EM、paired−split、new−reuse及交互；所有预算点、item/context cluster95%CI。固定源语开发集中128条双语无标签holdout的DE conditional NLL只诊断干预，不能作为能力claim。报告input/loss tokens、重复context、实际时间/显存、完整失败。原始MWB QA是零CPT锚点，不是等预算方法。
- **阳性对照：** E03仅EN source gate；正确原始ID/text对应、同一译料与scorer hash。沿E02同长度EN替换prefix mask检查：split DE logits不变、paired有变化；无非有限值、边界BOS不计预测。CPT有限loss下降、完整自然文档，不构造错误pair损伤对照。
- **噪声地板 + MIE：** 首轮seed17是发现pilot；1190题有context聚集，不能把NLI seed方差搬给QA。约3 F1或明确源语/目标语代价是扩展优先级而非科学自动判决；有后果差异补联合seed29/43与有效translate-train/XLDA竞争方法。CI跨零不是等价。
- **混杂审计：** 逐语言预算/译者/格式相同；new/reuse内容不同是被操纵变量，独立信息量与question/context重复不同报告而不假装控制。paired/split固定文本、位置与loss mask，不估计全部unpaired格式或纯alignment。模型head真实LM训练；单预训练family/seed、污染及有效attention FLOPs未控。官方MT不是gold；不因label/span投射失败丢弃无标签CPT全文，未来监督比较需单独记录恢复率和共同样本。source recipe不受target改变。
- **决策表（跑之前写）：** 数据匹配/来源未过→只修数据审计，不开GPU；E03不能有效生成→先修baseline；E03三条件没有实质差别也不自动否定E04，但启动要明确不同因果量与信息收益；E04出现有后果coverage/conditioning差→重复seed并与同预算translated监督/内容竞争方法比，不立即命名idea；仅NLL杠杆和小任务差→保留资产、换真实训练决策，不继续评分细碎优化；source损害→定位与修复实际训练代价，不更换主评分。
- **算力预算：** 目前仅CPU审计。四格若启动，各CPT+QA≤4 GPU·时，总≤16；独立单卡A100，白天总并用≤8。**实际：** 尚未GPU训练。

## 结果（仅追加）

官方译料已下载，尚未做pool审计与GPU干预。完整两阶段训练的GPU启动仍待E03全曲线，不以“配对应该有用”预定结果。XLDA/PreAlign/AdaXEval/ParaRater都覆盖母问题；本卡无novelty或ownership升级。

**2026-10-02训练前amendment（尚无GPU干预结果）：** 首次8192单位长度匹配给new/reuse独立context数6691/5083，max question/context5/6，存在内容多样性混杂。原始数据/manifest保留为 `artifacts/qa_bridge/data_initial_unequal_diversity.json` 与 `results/e04_data_initial_unequal_diversity_manifest.json`，不作为拟跑输入。修改为每池4096个distinct context、每context一个问题，完整单位各重复2次，仍8192单位/256更新；两池独立context数与重复次数完全相同，再逐语言匹配token预算。new覆盖选中监督问题的25%，context覆盖须另报；未固定语义主题或质量。这是预训练前混杂修复，不按模型target分数筛样本；其他协议不变。

修正后CPU准备通过：new/reuse均4096独立context×2重复；EN loss token1654758/1651606（差0.190%），DE2121658/2122050（差0.018%），在1%预注册容差内。7391独立context候选，4096对应中995双语长度完全匹配；2,795个无官方译料、6个完整单位超2048候选预先排除。hash见 `results/e04_data_manifest.json`。encoder完整编码触发6585-token长度警告，但这些单位在进入pool前剔除，不截断或送进模型。未GPU训练。

运行前边界说明：CPT排除的是固定dev/test context，不是所有source-dev title的所有其他段落；不得将其描述为article-disjoint CPT。E03监督训练的article-disjoint gate不变。E04因果量限定为这些固定同域pool的任务内容覆盖/条件连接，不是排除了所有主题质量差异的纯alignment。

GPU启动决定（完整E03已核对）：英语生成F1各74.35–75.60、DE62.54–63.53，非地板；旧预训练条件的终点差小，不作为要解释的新现象。仍执行一次完整四格联合seed17的理由是：E03的checkpoint比较不能识别新监督内容覆盖/连接，E02又是分类读出；本卡首次在有效完整LM生成学习上直接操纵这一训练选择，信息量不同。不是支持acquisition叙事，也不承接E02早期source差。只允一次完整pilot，若仅NLL变化/小任务差不扩大该grid或prompt优化；转向其他真实训练选择。源/目标、所有预算点和恢复对照全部保留。

A100前置mask阳性检查通过：paired替换prefix最大DE logit差8.15625、split0.0，记录 `results/e04_mask_check.json`；只证明条件连接杠杆。fvcrc10空卡首跑new_paired，有限loss/内存通过后同节点其他三格，四格同硬件/recipe；E06用另一空卡依次测，白天本题最多并用5张。

完整结果：按new paired/split、reuse paired/split，EN/DE F1为74.88/63.66、74.65/62.94、74.81/64.14、73.71/62.53。DE paired−split为new +0.72pp context95%CI[-0.85,2.35]、reuse +1.60[-0.03,3.27]；覆盖×连接交互−0.88[-2.14,0.39]。完整曲线、EM、source、instruction和输入/代码/权重保存校对见 `results/e04_learning_analysis_seed17.json`。单联合seed，CI不是训练方差，不宣称等价。没有出现强任务覆盖交互，不扩此QA grid，也不挑中间快照；E10另卡保持检验与E07标准监督参照仍执行。无主张升级、无新idea命名。
