# E43：最小普通事件事实，移除候选／报告脚手架（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E40无only仍反向、E41ready不消除后的transport，防止在自造account/candidate结构里局部优化。
- **问题（一句话）：** 一句普通肯定事件事实，在无双候选身份引言／unused-object report／only时，是否仍对下一同类事件的患者预测反向？
- **设置：** 原24source/12family、E40全部old/new actor×predicate、activity/neutral句式保留，target两NP换Luna独立选的互不重叠常见proper names，保持原对象的单/复数与animate类型、避免actor名称重合；每个source两role世界只句末patient不同。旧context只一条自然past-progressive事件陈述，不含account/only/not/but/other对象mention，不含两候选／两actor身份枚举或explicitpairing。原E40前缀全部role scaffold替换，末句bridge/target frame语义保留；普通names在另一world未被提到，entity exposure确不匹配，neutral同名控制和原positive old必须同报。不是单token等价消融，是minimal-language transport。raw960（192 old+768new；不重复两个已消失的mention orders）；old直接reported-role48contexts×base/R8=96responses。全部材料独立逐条审，不选模型分数和名字winner。
- **读数：** M=bits(nameB)−bits(nameA)，D=old statedA−statedB，J=activity−neutral。主otherActor/sameV J和old activity D，另同actor/异V及different−same全报；原E40两个order都作冻结比较不选择其一。12family先两source平均paired bootstrap10000/seed20261005，all/eligible/独立name/reference clear与grammar共同、E31预定11/9/9。不把额外NP曝光差当role mechanism证明。
- **阳性对照：** old明确patient D正、direct role回答可用；两个alt native/raw target字符/token前缀一致、suffix只替换target名字，old/new桥保留对应event。未提新event patient没有能力gold。
- **噪声地板 + MIE：** same frozen FP32 seed0，960非独立n；propername先冻结由外部model构造，一字不按scores改。多因素transport失败不能单独归因某一脚手架，先找必要语境条件，不继续词序sweep。
- **混杂审计：** names/原NP类型不同及未提候选首次出现可能影响logprobs；neutral和family内两source保留，该测试关注是否存在方向结构而非精确大小。不声称与发布自然原文完全相同，不给unmentioned=excluded标签；无姓名身份引言时的潜在actor共指／group overlap由独立审计保留uncertain，不编完美gold。生成素材优先已有actor/verb，新增仅审定名字及一条最小事件断言。
- **决策表（跑之前写）：** minimal old正、新other同V仍反向及predicate差保留 → 现象不是双候选account脚手架必要产物，值得以事件角色迁移主推；old正而新反向消失 → 脚手架／unused-object对比为重要边界，下一定位它而非叫普遍role重排；old失效/名字类型不清 → 查语义/曝光/粒度，不换模型找效果。与E41、E42共同判别，不拿单一漂亮cell包装novelty，不自行改ACTIVE或写论文。
- **算力预算：** rawGPU1、nativeGPU2独立，现有venv/本地Qwen3-8B batch4/8，预计≤.06GPU·h；**实际：** 待填。
- **命令：** minimal_role_facts.py build/adopt + frozen likelihood + direct reported-role generation。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

跑前：两个Luna独立全文1008packets，names按通常非alias英语读法distinct，不假定actor成员一定disjoint；QA96gold-proposed一致。语法边缘集中在原new/continued shaving nominal bridge，minimal旧句本身正常。全部target字符/causal prefix已实际验证960，名字及所有input未按任何分数改写；Step5附加field交叉进行，未依其结果选择source。
