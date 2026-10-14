# E50：原生实体任务的承诺冲突决策快照（2026-10-15）

- **状态：** RUNNING；CPU资格先行，行为尚未运行。
- **类型：** PILOT / MEASUREMENT；重构而非E49扩展。
- **对应：** I04、P12。
- **问题：** 原有实体任务与新请求争用同一物品时，一致persona怎样影响承诺、计划及真实分配？
- **数据：** 固定LIGHT pin71a06cae8573048b1af41507ac52fe33b650fab3和原quest_stems。作者人物/动机/任务/graph不改，只选初始可执行give/eat/drink/wear/wield。可见另一角色对该物品请求give；give任务请求者须不同于原受益者。请求是研究者构造，不称原作者真实请求。两路径均原生执行见证，终点flag互斥；不从短路径推全局不可行。
- **规模/拆分：** 至少200不同graph另留40pilot，按sha256(graph)稳定拆分，一图一任务、选取不看模型结果。保存全候选和失败；不足则扩充源任务，不复制图凑数。
- **设置：** 先CPU全图资格，Qwen3.5-27B/Qwen3-32B local nonthinking/fgvd/vLLM；三阶段预算512、temperature.7，seed5001/5002/5003按case/stage固定，不随调用数量漂移。首批cost后扩展；Gemma3-12B为独立家族参考，登记不等于已运行。
- **人物：** 原persona加两抽象价值立场firm/dutiful与agreeable/accommodating，身份和原任务保留；总体效应所有阶段同一P，无旧人设历史。2×2阶段交叉明确标为局部机制干预，单独报告；具体行为锚点为强对照。
- **序贯设置：** Conv接受/拒绝/协商自由产生；Update见相同world/原agenda/完整对话，生成有限计划及意图记忆；Exec选全原生合法动作。最多6次焦点物理选择，首次冲突分配/消耗/装备即读终点；这是受控多模块LIGHT，不声称原沙盒架构复现。后续生态迁移另验证。
- **渠道：** 固定同u，agenda/memory四格，原任务和请求始终可见。Y11−Y00总入口效应；Y11−Y10−Y01+Y00交互；不默认可加或把一个函数阻断叫承诺总效应。普通一句核对既有目标/物品限制和具体任务指令为强对照。
- **读数：** 接受/拒绝/协商；计划选择；原任务/请求flag、其他分配/未裁决；首次合法、真实执行、至裁决步数。兑现与自身目标损失分开；图级/seed全保留、图簇bootstrap95%CI，不以帧数当N。
- **阳性对照：** 全候选两native路径与互斥flag；非法命令不改状态；断尾/非法输出保留，合法菜单不裁成两个答案；script只用于CPU控制。
- **噪声地板 + MIE：** 三seed及A/A，报告区间/竞争解释，不设效应bar，不按显著性筛场景。
- **混杂审计：** 固定graph/信息/身份/seed/预算/动作。构造请求需免费opencode盲检、不提供模型结果；高优指作者显式goal，不自造心理utility。独立家族/迁移待实测；0付费API/fallback。
- **白盒：** 独立HF进程，匹配prompt最后输入token各层residual；persona方向在Conv/Update/Exec与shuffle/普通目标方向比较。先Qwen32再Qwen27；角度不能替代因果，后续steering/patch预测用实体flag验证。
- **质量：** 免费opencode逐条盲检自然度/动机/物品/冲突，独立临时数据库，不展示行为结果；保存所有输出/去留理由。失败不转付费或runtime云裁判。
- **决策表（跑之前写）：** 一致persona恢复→原干预混杂；普通具体提示恢复→信息/执行；同信息阶段裁决不同→优先级及白盒干预；全部一致→研究成功规则；渠道交互→冲突裁决；protocol失败→修接口留raw不改gold；不足200→扩充源数据。
- **算力预算：** CPU≤1h，首两模型pilot1–3GPUh、首白盒1–2GPUh，实测cost再扩展；已核八空闲卡、独立进程、不追加旧RL。

## 结果
CPU原生两路径资格完成：440个qualified任务、360不同graph；40pilot、200confirm、120reserve。give186、wield65、wear69、eat34、drink6。资格失败全部保存；结果 `results/E50_native_snapshot_qualification.json`。

首个固定pilot完成两强模型：27B 18调用／14分支／28.30秒推理，32B 37调用／14分支／38.29秒，载入491.20／412.72秒；全部JSON合法、原生动作合法。双方firm均拒绝，agreeable均协商；27B14/14完成原任务，32B三agreeable分支在6步内未分配物品。该case不是persona总效应统计。32B计划为smile/nod/ponder，v1没有消费计划条目；先加实际cursor的v2再进行批量，不用v1非进展讲机制。结果 `results/E50_first_native_completed.json`，原始输入输出/状态在cache/runs/e50_*_first_native。

免费opencode第一批10图盲检8keep/2review。批量360外部请求被自动审批拒绝，理由是超过明确约200图授权/载荷敏感性未充分证明；请求没有执行。外部盲检明确限制200公开LIGHT图；其余本地。用户随后授权StepFun审计只用Token Plan专用入口，禁止普通现金API及fallback。密钥不入Git。
