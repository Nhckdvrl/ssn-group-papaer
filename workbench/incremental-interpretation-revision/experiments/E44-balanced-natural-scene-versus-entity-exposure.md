# E44：普通场景中的平衡实体曝光与角色迁移（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E43揭示未提候选的曝光主导与neutral非等价，不再泛称最小事实有绝对反转。
- **问题（一句话）：** 两个名字都在普通场景中被提及、没有account/候选枚举时，旧患者对新事件的反向作用是否成立并经双方ready保持？
- **设置：** E43全部固定名字、actor/verb、旧最小断言、原old/new bridges/target句。Luna独立构造unused-name的普通在场句（在附近/同室，不是report、不称candidate、不说不参与），与old role事实先后两顺序。两world names各一次、同wordbag；不声明exclusivity/one-to-one或actor身份列表。无状态协议old+new960×2=1920；另仅new768×2追加对应名字的ended-and-ready（旧活动结束，双方现在满足新活动所有起始条件，旧参与不妨碍）=1536，总raw3456。不能向old continued句追加ended事实造成矛盾。既有E43曝光不平衡全体与E40两order冻结作transport比较，非单token等价消融。
- **读数：** M/D/J全报，主无状态otherActor/sameV activity D及J、ready同cell D/J两order、ready−no_protocol paired；old activity D与J阳性对照。sameActor/不同V/different−same及neutral独立报告；实体曝光配平不意味所有场景语用消除。12family先两source平均bootstrap10000 seed20261005，all/eligible/grammar共同及E31固定11/9/9。不以显著阈值筛order/名字。
- **阳性对照：** old角色语义D/J不再被纯曝光吃掉；old directly reported-patient及new双方ready文字能访问，R8一句全报。native无协议old96contexts×base/scope=192，ready只otherActor/sameV96contexts×old role+ready两questions×base/scope=384，总576。QA不问尚未选择的newpatient，不把概率当世界事实。
- **噪声地板 + MIE：** fixed FP32 batch4/8、同names不会按scores调整，derived3456非独立n。原E43 old D+26.808、newother D+20.878，但old J−3.035/new J−5.848，说明简单中性相减不能保证关系测量有效；此实验要一起看旧阳性和新绝对方向。
- **混杂审计：** bystander在场不等于逻辑没有参加旧活动；只能叫未明确描述的role alternative。nearby可能引入可用性／叙事背景的对比，所以new ready支路明确解除状态解释，同时保留两个order。names usual nonalias读法、actor群体成员可能重叠如实记，报告全部wordbag/hash/语法；没有only/not/account/candidate词，ready控制不可偷偷指定patient或否定旧事实。
- **决策表（跑之前写）：** old控制有效、平衡自然场景新other反向且ready保持 → 反向需要关系备选共同可及，但不需人工report/candidate脚手架或不能再参与，主推条件化角色竞争；平衡后仍正 → 旧模板／词汇类型是重要边界，继续定位其因而非编普遍机制；仅nearby反向ready消失 → availability解释，收窄story；只有J负但oldJ也负/absoluteD正 → 不称角色反转，追neutral validity；order独占效果 → salience/focus混合，全报。由结果推进同I01，不换研究对象、盲扩模型或进入写论文。
- **算力预算：** raw按protocol独立GPU1/3，nativeGPU2/6，现有venv/frozen Qwen3-8B，预计≤.15GPU·h；**实际：** 待填。
- **命令：** balanced_scene_roles.py build/adopt/split + frozen likelihood/direct report queries。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
