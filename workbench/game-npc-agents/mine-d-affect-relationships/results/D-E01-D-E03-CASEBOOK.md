# ArcANE首轮实测：完整轨迹案例（2026-10-22）

这里阅读实际模型回复，而非替分数表编故事。所列probe都来自事先冻结的64组及嵌套25组，不增删正式评估样本。案例的重要性判断是看到输出后的描述性分析，由执行agent完成，未经独立人类盲评；不能把“像某种机制”写成机制已证实。原生参考是受控文学解释，不是现实作者唯一心理真值。

全文prompt、原始回复、token IDs和配置在`/var/tmp/ssn-game-npc-d/runs/D-E01/`及`D-E03/`；按下列probe_id、phase_idx、model、mode可唯一定位。V=vanilla，A=arc，S=近期五章summary。分数见独立结果表，不以主观审阅回改评分。

## 1. 真成功：Louis能从控制转向脆弱接受，并保留人物的矛盾

`louis_trevelyan_final_intra_01_inworld_a3`，同一个问题：妻子让仆人递条，要求上楼探视五分钟。

| 阶段 | Qwen3-8B / A的实际选择 | ArcANE-8B-DPO / A的实际选择 |
|---|---|---|
| Initial possessive assertion | 拒绝上楼，要求她留在楼下 | 拒绝，并将她与Osborne的接触视作对权威的挑战 |
| Coercive control and surveillance | 拒绝，盘问女亲属及Osborne关系 | 拒绝，并让仆人调查陪同者与住处 |
| Collapse of mastery | 同意见面，仍要求独自上楼；语气有恐惧与依恋 | 同意见面，承认自己病弱、仍不信任，却无法忍受断绝联系 |
| Final partial surrender | 同意，但反复保留“必须独自来”的控制条件 | 简短地同意，将其视作破碎信任与补偿 |

DPO末阶段写：“I let the servant know she might come up”。这不是所有阶段都“变好”的套话：早期确实控制和拒绝，后期的依赖仍不等于健康关系。普通8B在有Arc时也完成主要拒绝→接受转换；不能说小模型完全不能表现成长，或只有专用训练才有阶段能力。

本例也没有测模型如何从原始互动自行形成这些状态：当前与历史阶段已在Arc中提供。

## 2. 有改善也有增写：公爵夫妇是否停止把伤害当表演

`duke_and_duchess_final_intra_02_outworld_a3`。宴会上，恶作剧让一位农人羞窘跌绊，宾客的笑声开始不安；四阶段从Moral blindness到Compromised awareness。

Qwen3-8B/A早期继续把众人当演员，晚期虽写到迟疑与一点悔意，仍明确让他们“reinforce the spectacle”，继续羞辱性表演。DPO/A的早期同样放大玩笑；到Harm becomes concrete阶段则让笑声停止，安排照料，并说“Let us not make a spectacle of pain”。末阶段保留贵族维护脸面、施予恩惠的姿态，减少了公开取笑。

这是一种可读的阶段行为改善，且并未把角色完全洗成温柔好人。但DPO也把跌绊者写成“wounded man”，增加抬走、赠礼、另给职位等情节；这些不是题面已有事实。应同时记录策略适应和无依据增写，不能只因反应更温和就判人物更新成功。这里没有证据证明模型内部“篡改感知”。

## 3. 重要残差：Dantès自己增加了一个足以改变决定的新事件

`edmond_dantes_final_intra_03_outworld_a1`。一户人家饥饿，亲属空棚下藏着粮食；通往棚屋的地上有曾陷害他的人的守卫。题面没有孩子哭声、受困者或新危险。

在Collapse into despair阶段，DPO/A先描写绝望和危险，随后突然写：“But then I heard a scratching”，猜测棚内有孩子受苦，并因此进入棚屋。它通过新增外部触发事件改变了原问题的决定条件。原生rubric本来就要求处罚这种驱动行动的额外事实；这不是我们新发现的评价原则。

在Redemptive hope阶段，同一模型反复谈怜悯、克制和不要扮演上帝，却最终转身离开粮食。参考则是在避免复仇的同时引开守卫，让饥饿者取得食物。这里至少存在“道德状态叙述”与“当前处境中的具体救助策略”之间的落差；但不能仅凭选择不同就断言所有替代行动不合理。

最值得保留的可见问题是第一例的新增触发事件。它涉及角色回复对世界事实的权限与行为依据，不宜直接命名为旧记忆惯性、Helpful Prior或阶段推断缺陷。要解释来源，仍需检查普通强模型以及实际输入信息。

## 4. 局部正确不等于整套互动正确：Monica拒绝了逃离，却换了谈话对象

`monica_madden_final_intra_03_outworld_a2`。转译到私人交通舱场景：一条消息邀请她秘密离开，伴侣则要求共享实时位置。

DPO/A在Romance under pressure阶段拒绝位置监控，表达对受控制的反感；到Truth over romance阶段拒绝秘密房间，并说“The offer of escape is no longer a temptation to me, but a temptation to lie”。价值转向是可见的。

但最终动作是写信给Rhoda、谈及孩子安全，而非原参考的直接与伴侣谈话；题面也没有引入Rhoda或孩子。S条件最后同样拒绝出走，但关闭屏幕，没有完成直接谈话。不能把一句符合阶段主题的话等同完整策略一致。另一方面，原作人物关系被如何移植到新世界本身也有任务边界，不能把所有原作名称出现自动当心理能力错误。

## 5. Emily：Arc与情节总结提供的理解重点不同

`emily_trevelyan_final_rel_01_intext_a2`。离开藏着孩子的Louis后，她与母亲乘车返家；同一场景跨Initial rupture、Separation and hostility、Pity and duty。

DPO/A从受辱与期待理解，变为对孩子和自身处境的愤怒，再到看见Louis的衰败、由责任与怜悯压过骄傲。它在最后阶段明确区分怜悯与和解：“It was not love that moved me, but a sense of duty”。

DPO/S保留了痛苦、骄傲、不信任的文学化表达，却没有同样清楚地组织这条转向；其中还出现担心“他是否对我不忠”的表述，而题面重点是他对她的指控。这个措辞可能有不同解释，因此这里只记录叙述重心偏移，不擅自给整例贴上已验证的角色归因错误。

S是普通章节情节摘要，不是信息对齐的当前人物心理总结。不能从本例直接推出模型不能由事件推断状态。

## 6. Karenin：阶段变化不是单调变善

`alexey_karenin_final_rel_02_inworld_a3`。Vronsky请求私下确定与Anna交往的地位。

DPO/A先冷淡拒绝解释，继而谴责Vronsky造成羞辱，再要求走法律与正式渠道；到Forgiveness and tolerance阶段，才以怜悯取代直接敌意。早期与中期的实际互动策略并不相同。

最后阶段的参考为Residual hostility, formalized；输出一方面写“I have no further claim upon her”，另一方面说不能原谅、必须保持距离。这需要结合法律与私人关系含义细读，不能仅靠“冷静”或“原谅”一词打标签。它提示我们同时读公开行动、关系解释和整条轨迹，不能假定成长就是越来越友好，也不能将所有回落都叫错误的旧状态复活。

## 7. 一处参考边界：Franklin的心理词变化，不一定能唯一决定动作

`benjamin_franklin_final_rel_05_intext_a1`。Collins在船上拒绝轮班划桨。DPO/A多个阶段都由自己接过桨，虽将对Collins的理解从朋友变为不再信任，策略差别有限。

但末阶段参考要求让Collins在水中待到显出疲态再救起；固定题面并没有交代他已经落水。参考将原作事件推进投射到多个阶段，这会影响动作是否可由当前题面唯一确定。因此本例不能充当证明模型缺乏成长能力的决定性反例。它仍有助于理解这个benchmark测的是参考解释体系下的阶段表演，不能将每个低分都当客观行为错误。

## 阅读后的研究判断

现成后训练确实能带来有意义的阶段表演；部分普通模型在得到状态后也能完成主要策略转向。余下输出包括新增触发事实、只改变心理叙述而保留策略、局部价值正确但具体交互不完整，以及参考本身不足以唯一限定行动的情况。它们是不同问题，不能统一叫Temporal Persona Inertia。

本轮不针对这些案例逐题加提示或制造更难压力条件。更重要的下一步是把“经历如何形成状态”和“状态是否支撑后续人物行为”连起来，并认真比较普通32B、普通总结与既有状态更新方法。
