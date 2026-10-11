# E127：共同形成背景影响的是输出空间绑定，还是推断出的私人规则选择？（2026-10-12）

- **状态：** PLANNED，0科学评分；E126六批已完整独立核对，E127八批CPU预检通过，末版观测定义独立复核后冻结执行。
- **类型：** PILOT / CLAIM。
- **对应：** C23、I04、P17。
- **问题（一句话）：** E126缓存兼容效应是否也决定共享同一标签词时该采用哪套私人映射，还是仅影响不同输出词集合的使用？
- **为什么现在做：** E125公共表在形成期有跨家族功能作用；E126三家族确认coherent−mixed +23.49/+10.40/+5.42pp、候选差小，六批已独立先raw封后核。这可能只是Feng/已有TR-TL所拥有的输出属性/空间绑定，也可能约束从示例推断的rule选择。两解释在far设置都可解释，需在**输出集合完全相同、私有映射相反**时使预测分叉。不是继续分NameK/head或调表格式。
- **设置：** 同冻结Qwen3-8B/Mistral-7B-v0.3/Llama-3.1-8B，另Qwen3-14B缓存checkpoint作规模范围；同revisions/FP32 eager/conda verl-clean。官方SST5 gold0/4材料builder f021…不变；4固定checkpoint n16 seed127001 discovery→n32 seed127101 validation，Source Alex/Sam→Robin/Jordan，private正负方向平衡。不看科学分数选模型/种子。
- **操纵：** 复用E126两种公共表等价行次序+全历史Source-private隔离/整query禁止直读schema。新增output namespace crossing：shared两Source均no/yes；far A no/yes、B pass/flag。每namespace表均只规定Source可用词集合、不指定私人正负，order0/1事实相同。两namespace使用完全相同评论/配对/private code/name/query；token总长/私人全局位置应CPU确认，未看分数时若 tokenizer不匹配先记录修实现，不能事后筛。全部A/B private K/V 00/11 vs01/10；joint与own-only读数均保留。保持原global positions，不重用pos或改RoPE。
- **配置：** 每namespace32组合+4native+4独立一句指令+3single=43，双namespace86×8=688/context；全部22prefix图/86query图各层实收。两个namespace的normal prefix作为功能参照；主要组合对比只在同namespace/同长度内。
- **读数：** primary **shared/opposite-private-convention世界**的joint .5[(00+11)−(01+10)]完整词表准确率，均匀两Actor/8q、context采样单位。secondary shared两world平均、far相同组合对比、shared同约定世界、跨namespace interaction；candidate、margin、own-only各Source/order性能、A/B/两个private方向完整报告。固定A词的B-code signed/absolute半响应与层消费保留。shared表面词不能辨认Source，other-source-word字段标不可识别，不能把0当无泄漏。
- **预评分辅助观测：** 保留每query实际2（shared）/4（far）唯一标签logits，不增加前向/条件。far令M=LSE(A两词)−LSE(B两词)，分开.5[M(qA)−M(qB)]来源特异差与.5[M(qA)+M(qB)]共同偏移；shared只在opposite世界，以A gold定向.5[z(qA)−z(qB)]和.5[z(qA)+z(qB)]，再报告逐query共同项绝对值均值防抵消。两namespace定义不同，不把两种logit指标直接相减当同一种机制量。该读数检验相对来源条件化与共同输出倾向，不识别抽象ID或唯一内部算法；primary、条件、材料与mask完全不变。
- **阳性对照：** 两namespace每批single各private方向、逐Source/order own-only实际性能/native/一句指令；coherent缓存与pristine、mixed-own与对应own缓存z/全argmax一致，Bworld→A privatecache图零；fullsplit/cached/default/native no-op≤.001；actual全层mask消费与完整token/gold/缓存来源独立核。own-only平均coherence0是平衡设计恒等式，不是新双分离。
- **噪声地板 + MIE：** FP32 floor .001、10000context bootstrap seed910。pilot数值有效即4模型固定n32，不按正负选。shared联合若已有chance/floor，primary未定不证明不存在任何frame机制；需呈现实际coherent能力与single控制，不追加追80%任务。
- **混杂审计：** 该namespace操纵同时改变输出身份、答案集合区分度/词先验，匹配token位置不消除此事实；不同namespace的gain差不是纯输出identity-specificity。关键shared内部四cache语义/监督完全相同，Source函数由private code区分，其joint差可体现rule选择而非选择另一套表面词。whole-cache仍含多种表示，不能凭差识别新ID；Feng§4.1/AppendixE已有ID与direct-binding竞争、Mixing多机制已有所有权。CacheBlend拥有一般块独立缺cross-context质量问题，本项不以此作first。新材料/名字非新benchmark；SST语义可预训练见过。
- **决策表（跑之前写）：**

| 结果 | 更新的研究认识 |
|---|---|
| shared冲突primary有明确正效应，private own功能强 | 共同背景兼容约束不仅是输出集合绑定，也影响从示例推断的Source-specific mapping选择；结合E126与原形成链组织解释，不另宣称新binding构件 |
| far复现强而shared弱/零，sharedcoherent函数有可测Source区分 | 当前兼容效应主要对应可区分词空间的使用；不能把E126泛称私人规则组合，研究机制选择的namespace边界；原C21/22形成关联阳性保留 |
| shared与far都有不同家族/Actor方向 | 全部保留，解释具体计算策略范围，不按平均包装统一程序 |
| sharedjoint本身chance或所有private功能低 | shared结果不能判机制缺失；报告任务/接口实际限制，不无限扩prompt拿阳性 |
| 数值/geometry/gold失败 | 0-score修正或VOID后重新freeze，不把实现失败作科学反例 |

- **算力预算：** 4checkpoint16→32、8独立空卡，预计1–2 GPU·时；10/20/21模型已经本地缓存，其它机器不复制大模型只为填卡。E126完整科学结果先回来；此项目前仅设计、0评分，不铺开其它后继分支。

## 结果
0科学评分。E126全量确认/独立raw已完成。八批真实tokenizer/config CPU审计通过（192 contexts；4224 prefix图；6144 query scope-owner与6144合成选择），随后在首次评分前加入上述既有前向logit观测。末版源码SHA256 cef7952d4ef556abad45c9c2e6d6f351e3b0a1b3fffa9232b9eb728806c943de，材料builder不变。预评分CPU几何及metadata独立复核后提交freeze，再执行全部四checkpoint固定16→32；不在看到shared结果后改primary。
