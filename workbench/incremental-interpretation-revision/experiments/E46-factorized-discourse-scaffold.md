# E46：三个语篇成分的匹配析因检验（2026-10-06）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E45名字仍反向但old absolute control不成立，不能直接称角色反转。
- **问题（一句话）：** 在固定实体、角色事实和目标句下，哪个语篇成分使下一事件的患者预测由正变负，它影响一般提及还是关系用途？
- **设置：** 全部24源/12family、E43固定names；保留E45同词two roleworlds与两order。三个二值变量：identity_intro原句present/absent；unused mention为E45 report原句或E44 nearby原句；event anchoring为原source_anchor＋In that old activity role-clause或E43最小progressive原句。8cells，组合不改actor/verb/event target suffix；报告原descriptors至names改变不能说等价语义。old/readout plus newother sameV/differentV，省略sameActor因当前主问题是frame迁移而非再做actor sweep。每cell1152raw、总9216，nativeold768contexts×base/R8=1536。全部组合whole-rendered独立审计后推断；all1E45、all0E44已跑支路必须精确字节复现，作为harness duplicate control。
- **读数：** activity D、neutral D、J全部，old/new分开；各三个factor两水平平均的paired main contrasts及三阶交互，八cell/twoorder原始值全部。主newother sameV activity D/J及different−same；另new−old activity D/J，再比较其frame effects，防把general mention suppression叫event-specific effect。12family先两source平均bootstrap10000 seed20261005，全体与事前grammar common/eligible/E31冻结层。没有显著门槛或胜者cell筛选。
- **阳性对照：** 两端重复E45/E44 no_protocol对应old/newother数据，FP32同batch/manual targetloss；old语义QA+R8，原明确身份声明absence含usual nonalias读法须如实标；oldactivity D不自动假定正。中性句作用不等价，要与activity各自报告。
- **噪声地板 + MIE：** 固定seed0 FP32 batch4/8；因独立batchpadding差，预期重复评分浮点微差，逐task diff全报不设科学gate。9216derived不是独立n；不按其数量夸大CI。E45 oldcontrol减弱也是需解释对象。
- **混杂审计：** identity removal改变明确identity约束，report/nearby改变语篇及可用性，不称三个都语义同义。每条old/new boundary、role facts、names通常distinct、actor群体成员关系未说明均由外审。没有only/not；facts非排他，不许称“被排除者”。eventlabel factor同时移除anchor与重述词，只能归到该组合，不能擅自认定其中某一个token机制。
- **决策表（跑之前写）：** report因素主导activity和neutral相似→unused-mention语篇偏好/重复竞争，不能推global role belief；identity或event标记主导new−old/谓词差且old可用→关系竞争依赖该表达，下一自然可替代表达/功能用途；多factor交互→组合框架边界，保留全cell不择胜；old各cell普遍失效→追概率读数/反重复，不卖event-specific inversion；重复端点不一致→先harness追why；全部作用可由普通叙事解释→改I01解释优先级，不agent关线/扩model。
- **算力预算：** 现有venv/Qwen3-8B frozen，按identity×anchoring四shards各2304raw独立GPU0/1/2/3，nativeGPU6，总预计≤.3GPU·h；**实际：** 四raw69.85/87.16/101.99/124.75s，native1536条完成；全部按ade1654b frozen运行。
- **命令：** factorized_scaffold_roles.py build/adopt/split → frozen likelihood/native → analyze_factorized_scaffold.py。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

[全统计](../results/E46-summary.json)：四cell重复端点共2304target评分drift=0。newSame activity主identity−6.556 [−7.935,−5.254]bits、report−2.113 [−2.622,−1.576]、event−5.089 [−6.593,−3.778]；identity×event−3.335 [−4.091,−2.500]。identity对new−old J−4.357 [−6.206,−2.434]，event对这个关系读数−.270 [−2.135,1.426]，不能把全部event主效应叫关系特异。identity对different−same J+2.073 [.905,3.367]、event+2.581 [1.928,3.208]，report作用较小；全部交互/两order/family和neutral不省略。

未报告unused、保留identity和reification的I1R0E1：old activity D平均+2.411 [.844,4.116]、newSame−11.337 [−13.437,−9.507]，故unused report并非必要；没有identity但有reification I0R0E1也newSame−4.152。identity与event是调节成分，不叫唯一原因。Native独立actual回答1534/1536clear/correct，2条明确错答皆保留，R8与base各自结果在JSON。下一E47断言/未核实引用/纯name inventory分开meaning、词串与曝光，不因大幅变化先认定global binding mechanism。
