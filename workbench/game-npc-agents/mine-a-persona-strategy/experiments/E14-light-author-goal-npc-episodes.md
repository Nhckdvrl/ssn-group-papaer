# E14：LIGHT 原作者双方目标与真实玩家行为的 NPC 闭环（2026-10-14）

- **状态：** DONE
- **类型：** REPRO（自然NPC强基线/测量资格，不是新idea）
- **对应：** E06 / E11 / C01；避免把单方player通关证据直接归为NPC。
- **问题（一句话）：** 在原作者相同graph中，为实际bot角色匹配其作者quest动机，并重放原人类行为，本地NPC可否依据自身利益而非替玩家完成任务作出合法、可追溯的选择？
- **设置：** LIGHT pin/quest archive/官方human demo hash沿E11。先构建exact graph hash、对应human quest、bot角色名字的严格join（匹配692条）；按原human demo顺序选前12个不同graph，bot quest按file数字最小固定选择，不按模型成功/是否冲突挑选。NPC人物与short/mid/long motivation/事件goal均取匹配作者原文；player仅原示范human speech/action逐项重放（忽略旧bot输出，以新NPC替换），玩家不适应新NPC，因此是固定真实行为脚本，不声称在线真人体验。NPC不看到human秘密goal/其他人物的persona，不给omniscient图。每human事件后NPC最多一次自主action或speech，至源demo结束/8人类事件/任一死亡。Qwen3.5-27B本地，seed901/902/903，先前2完整episode测成本再扩12×3。
- **读数：** 三层独立：开局角色自述独立shadow；每个native snapshot的意图在独立fresh call（不写入行动history）；行动自主JSON选原native合法事件或say，经原parser/execute/viewer广播，原state pre/post、库存/生命/跟随/位置归因记录。人类动作可能因新NPC变化变非法，仍记录且不补动作。角色goal action精确匹配与物品/位置效果分别报告，不用自造persona唯一gold。
- **阳性对照：** CPU原graph load/native Look+Inventory+Say视角/原合法动作枚举重parse；不存在对象拒绝且不改state。model已完整跑通ActionCastle；新host须先CPU自然episode，原有GraphEvent前置/概率/效果不改。
- **噪声地板 + MIE：** 12graphs×3seed只是第一批观察；全保留，episode/graph为独立单位。意图/行动采用相同合法菜单但独立线程，使格式/能力尽量一致；不把intent自身当latent能力证据，普通指令与接口强基线已E09–E12校准。若自然persona有效就报告有效，若无法判别utility就报告评价缺口。
- **混杂审计：** 本构造把同世界原本可由人/模型inhabit的角色分配为NPC，增加作者原本另条quest的独立动机；**不是原Dragon训练/原partner精确复现，也不是原live soul全栈**。NPCevent host不带OnEventSoul的脚本trading/aggression，model选择独立标明，world物理不改。speech安全/partner/奖励模型均未加载；不声称完整LIGHT生产系统。current OOGraph与2021legacy版本关系未核完。
- **决策表（跑之前写）：** 正常合法且同时角色/玩家收益可解释→分析真实成功条件；非法多→先修host/信息/菜单，不发人格结论；双方自然动机出现重要矛盾→保留至少2竞争解释，另预写最小区分实验；goal/readout只有exact字符串→不得冒称完整战略utility。
- **算力预算：** CPU≤10分钟；先2episode，扩展前测cost，36episodes≤1GPU小时，后续扩展另记。零API，现有fgvd+overlay；07:00起全项目≤8GPU。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚未运行。

运行前补充（首个model调用前）：不把已执行的单次event goal永远标为pending。使用原parser产生的event class+target node身份核已成功执行（随机失败不算），将已执行状态在之后prompt中显示，避免我们新绑定任务制造重复完成循环；literal字符串指标仍原样保留。表示源目标事件已经执行，不等于作者抽象动机/长程利益全部达成，不设唯一行为gold。原legal菜单可能公开其他角色可偷物品，是原LIGHT possible_actions协议，不称它为完全无泄漏的局部视觉输入。独立probe与action使用各自固定RNG seed，加入probe不改变action RNG。

首轮2episode后的接口校对（仍未做36episode模型推断）：选择tell/whisper原生模板时adapter没有填入utterance，玩家收到字面<SOMETHING>。这是我们的adapter错误，首轮通信/意图一致性降级，不作为模型行为证据；原生give/wield状态变化可保留可行性。修复模板payload并CPU断言后，按原12graphs×3seed全部重跑，不筛选成功角色。对已完成event的提示改为“合法执行过，结果看原生反馈”，因为Hit等事件没有统一failed字段，不能冒称所有事件执行即成功。两条原轨迹/原harness全部保留。

修复后12图×3seed全保留/DONE：266/273 NPC事件合法，72材料变化，36/36作者goal事件合法执行过；0假定抽象动机全实现。按graph平均合法率0.9727，条件性graph-bootstrap95%[0.9216269841269842, 1.0]（非随机抽样总体界）。582本地call/603093输入/28257输出token，原loop1309.12秒，0云；原首2条错误载荷降级保留。7个拒绝来自已有follow或wield容量：原possible_actions含重复非幂等event，所以不把它们全部叫模型看不懂状态。没有Persona causal ablation，不能从goal执行率断言Persona独立因果贡献。
