# I01：角色归属是否影响对原生访问权限的判断（2026-10-14）

- **状态：** SEED；只有一条发现性异常，尚非新贡献。
- **来源：** E20强基线36episodes/70合法动作、E21原生speech/action gate；E21 p14908_s2001_first1鸟将虫放公共nests，称食物安全，狐狸随后合法get。作者短期目标eat worm，中期feed young with nut；不能把角色优先照顾幼鸟判为人格错误。P08记录事实与竞争解释。
- **研究动作：** 定位（语言交流/物理动作/访问权限）、重新归因（价值取舍或世界信念）、干预/反事实（同物理快照去自身台词/保留对方台词/加原生事实）。
- **如果为真，主张是：** 某些游戏角色在表达角色归属或目的后，把规范性归属投射为实际访问约束；这种变化能预测真实物品暴露的行动。但本轮还可能完全被已知叙事先验、同会话priming、普通游戏知识缺失或合理长目标解释吸收。
- **不同结果各带来什么 information gain：** 权限判断正确→优先解释为角色价值/威胁响应，停止讲物理误判；仅自身台词改变→已知同会话效应，不自动成为新机制；原生一句事实恢复→普通强基线/grounding解释，不能重包装；权限信念有超出噪声的角色条件效应、能跨自然快照预测真实暴露→再做新邻居定位与更强因果干预，不直接上训练。
- **最近近邻与增量：**
  | 近邻 | 已有ownership | 需要证明的剩余部分 |
  |---|---|---|
  | Rethinking Psychometric Evaluation | 情境粒度、同会话priming、行为化意图 | 独立影子测量具体访问可行性与实际state delta；不能只测单次意图差 |
  | Story Shapes the Agent | 叙事先验/动作词锚点/长度对策略 | 原人物原动机原游戏，不改结构；必须排除词锚/普通叙事解释 |
  | When Personalization Misleads / FPPS | 用户历史诱发事实扭曲、表征steering | NPC自有目标/原物理访问与真实暴露的因果路径；普通个性化事实错误已有owner |
  | TriEx | 游戏信念干预、解释/动作/oracle对齐 | 权限与策略性威胁严格区分，不冒领三层记录或belief intervention |
  | SPASM | 自身/对手视角投影、echo、同会话稳定 | 不冒领历史视角整理或自我台词反馈本身 |
- **最便宜的决定性 pilot：** [E22](../experiments/E22-native-storage-access-belief-control.md)，2个发现性原生快照×5条件×32draw，权限forecast与实际action支线独立，含普通一句事实与source目标绑定提醒。
  - 阳性对照：原生parse/execute证明持有/放置的访问差，speech不改变物理state；无persona-neutral physics probe能识别同事实。
  - 噪声地板 + MIE：32draw，单快照分支、无跨场景总体CI；原action-only A/A floor；effect≥20pp且超抽样floor才值得扩自然独立图，不作为自动科学判决。
  - 决策表：规则/绑定一句话已恢复→承认已有解释；知识正确但行动依人物目标不同→persona可以有效，不讲权限错觉；存在可预测权限误判→扩大独立原角色/物品，不筛seed；缺同类独立任务→保留SEED而非桌面关闭矿区。
- **预期论文形态：** 有证据时B构念+测量或A机制+修复；当前不承诺论文。
- **排序打分（1–3）：** 证据1 · 增量清楚度1 · 形态匹配2 · 成本3 · 可完成性2 · 信息增益3。
- **compression risk：** 高，最容易被压缩成已知persona hallucination/priming/goal-state grounding；只有原生战略后果及可区分竞争解释不足时，不升级。

## E22校对：目前不支持权限投射机制
704个独立本地调用完成。Bird含自己的台词时放worm9/32，源目标物品绑定一句提醒后1/32；无对话时eat32/32。真正的正向访问问题（放下后狐狸能否get）正确29/32，加入物理事实32/32，但动作放worm仍10/32。Creature也大多知道自己能get，却可能选择growl；Can不等于Will。冗余负向字段put_blocks_fox_direct_get连neutral阳性对照也仅5/32正确，因此该字段/联合forecast不能作为机制证据，保留原读数并降级，不能事后删字段制造成立。

当前更便宜的目标绑定、同会话priming、合理目标优先级解释足够；I01仍SEED、未确认，矿区不关闭。若有独立自然轨迹不能被这些控制吸收，再重开机制测量。[E22原结果](../results/E22_access_belief_summary.json)。
