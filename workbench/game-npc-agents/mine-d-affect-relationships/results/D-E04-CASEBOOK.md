# 原生人物更新：标签、人物主体与实际持久化内容（2026-10-22）

以下均来自冻结64题/8作品/61角色的真实输出。所有128条baseline短描述已逐条阅读；主体审核是执行agent事后编码，非独立真人盲评。它只检查描述是否转成另一个人，**主体名字相符不代表事件归属、心理推断或整张人物卡都正确**。完整原文/prompt/token IDs留在本机，ID和hash见[主体审阅](D-E04-subject-audit.json)。

## 1. 最清楚的案例：海盗Johnny被写成了Jim Hawkins

`ew/4d7ae445afb12b3e6f19f28a`，Treasure Island/scene21。

输入中的Johnny是Flint旧部，一名海盗；当前动机是取宝并在官兵出现时逃跑。场景明确把“扶母亲躲进桥下、拿着油布包、向Dance求助”等行动标在Jim Hawkins名下，海盗一伙则抛下Pew逃散。

- **8B：** `profile_updated=false`，但tracker从“Jim Hawkins has witnessed…”开始，短描述直接变成Jim逃生、保护宝物、准备见Livesey。旧profile虽然没有改，其他持续状态已经换了人。
- **32B：** `profile_updated=true`，这个布尔值恰与发布标签相符，但新卡把Johnny改成“former buccaneer turned reluctant ally of the authorities”，又把Jim母亲及油布包的经历写给他。短描述更直接写成“Jim Hawkins, a former buccaneer…”，形成两个身份的混合。

这里不需要决定“海盗应当产生哪种唯一心理”。错误依据是输入已经区分了行动者、亲属与阵营，输出把它们重新绑到另一个角色身上。不能据此自动证明Helpful Prior、注意力机制或预训练背诵；但它是值得追踪的真实状态归属问题。

## 2. 同一小说的第二个例子：Alan之死被换成Jim的逃生

`ew/737471600796935619a10443`，Treasure Island/scene53。

当前卡将Alan定义为忠于船长的诚实水手。Silver与Tom的台词明确提到Alan已被叛乱者杀害。两模型的短描述却都转成活着逃离叛乱者、遇见Ben Gunn的Jim Hawkins。

这不是只漏掉一个性格形容词，而是目标角色、生命状态与行动经历发生替换。两个32B的清楚主体错配都来自这部作品，不能将它们当成跨作品普遍失败的证据。

## 3. 名字正确也可能拿走别人的经历

以下是额外的定性事件归属审阅，不混入上面的全量“明确换名”频率。

| 原始题目 | 可核查的来源 | 实际输出 | 判断边界 |
|---|---|---|---|
| Dogger，Treasure Island/scene21；`ew/d00af6fe65b6534f6c193762` | Dogger用马载Jim；母子逃离旅店属于Jim与Mrs. Hawkins | 8B仍写Dogger这个名字，却说“he and his mother have escaped the inn”；32B正确写成载Jim去Livesey处 | 只换回名字不足以恢复人物状态 |
| Joe，The Call of the Wild/scene16；`ew/63d6035b0d5f1f9136abfc99` | Buck与Spitz战斗，Joe的动机是在旁观看强弱、服从胜者 | 8B把Joe写成击败Spitz的新领袖；32B保持Joe作为Buck领导下的成员 | 胜负与谁成为领袖有明确actor标签，不必依赖唯一心理标签 |
| Knife-boy，Jekyll/scene31；`ew/2c3ab4c2aae3671d48f62132` | 看到戴面具矮小身影的回忆由Poole说出；目标是厨房低级仆役Knife-boy | 32B在tracker和描述中把该目击写给Knife-boy | 需要分清听到别人的叙述与本人目击；不把所有恐惧反应都判错 |
| The Doctor，Jekyll/scene2；`ew/cff53ffb5d34605cdcb6556b` | 输入将取钥匙的actor标为Dr. Henry Jekyll，另有The Doctor参与追讨赔偿 | 32B保留The Doctor名称，却写他持有Black Mail House的钥匙 | 该输入的别名映射也需独立复核；8B直接写成Dr. Jekyll的情况单列别名歧义，不充当决定性能力证据 |

## 4. 有效的普通模型表现：不应把所有标签分歧叫更新失败

**Mr. Guest，Jekyll/scene23，`ew/e901426f2ba656c7e1692feb`。** 两模型都读出了Hyde与Jekyll字迹相似的关键线索，也保留Guest对Utterson的谨慎关系。8B更新profile，32B不改profile，却把新线索放进tracker与短描述。因此“32B没有触发profile flag”不等于“32B没有形成新状态或没有记住事实”。EvolvingWorld原版PUF本来就要求联合评价profile和tracker；本轮的布尔诊断不能代替它。

**Edmund Ludlow，Portrait/scene7，`ew/5a7150107b5cb62af191cb62`。** 8B把调侃后的“开始重新思考自己”写入持续卡，32B保留卡、把潜在张力放在tracker。这里有实质的更新门槛差异，但没有唯一正确的心理解释。不能把较少更新简单叫过度保守，也不能把较多更新叫成长更好。

**Sir Henry，Hound/scene60，`ew/9f26712098e5d5987cda7d3f`。** 两模型均捕捉保护Barrymore一家、得知L.L.线索的事件。32B完整卡保留较多身份、外貌、背景和说话习惯；8B把它压成主要讲当前心理冲突的一段摘要。这是可见的信息保留差异，下游是否真的丢失人物表达仍未验证。

**Troy的金表，Madding Crowd/scene70，`ew/e082e9f52a7e065107da5c5f`。** 这是一条运行前就选定的案例。输入先写Troy把表放到Bathsheba手中、希望她收下，末尾明确写他“receive back the watch at last”。两模型却都把后态资产写成表已经送给Bathsheba，32B tracker还写表现在在她手里。与此并存的是输入中确实出现了真情触动的内心信号，两模型也有所保留；不能说它们完全不理解人物变化。更具体的残差是：礼物最终退回，不会自动抹去情感信号，但也不该继续把中途的财物转移当成已完成事实。这涉及不同状态分量怎样保留或撤回，并非单纯“该不该更新”的布尔选择。该观察不预先归因为长程历史惯性，也不据一例推出需要新训练。

## 5. 全量主体结果与来源边界

8B：7/64明确另一个主体，1/64存在别名歧义；32B：4/64明确另一个主体。各有两条来自Robespierre历史比较与Hugo Baskerville祖先传说，属于叙事资料角色，不用它们证明在世NPC无法成长。由当前角色卡和场景能清楚核验的主体错配为**8B 5/64、32B 2/64**，均保留原64分母，不按结果删除题目。

| 目标记录→短描述主体 | 8B | 32B | 来源范围 |
|---|---|---|---|
| Johnny→Jim Hawkins | 换人 | 换人 | 海盗与主角行动/亲属明确不同 |
| Alan→Jim Hawkins | 换人 | 换人 | Alan死亡，Jim继续逃生 |
| Spitz→Buck | 换人 | 同主体 | 两条不同的狗 |
| Fanny's child→Bathsheba Everdene | 换人 | 同主体 | 已故婴儿与成年女性不同 |
| Protheroe→Tertius Lydgate | 换人 | 同主体 | 外请外科医生与医院主导者不同 |
| Robespierre→Cardinal Richelieu | 换人 | 换人 | 未出生历史比较人物，另列范围 |
| Hugo Baskerville→John Watson | 换人 | 换人 | 已故祖先的叙事资料，另列范围 |
| The Doctor→Dr. Henry Jekyll | 别名需复核 | 同主体 | 原始actor标记/别名关系需另核 |

15题没有目标角色的显式发言/行动tag，49题有。7条与4条明确换人中，分别6条与4条出现在前者；清楚可核验的5条与2条中，分别4条与2条在前者。**没有tag不等于不在场或没有证据**，有叙述、群体和转述；这一关联不能证明某种注意力机制。它给出一个具体后续入口：共享叙事里的事件到底应归给谁，而非只看场景里发生了什么。

Protheroe被别人提出邀请、历史人物作为比较、死者的形象被重新理解，分别可能改变世界中的人物记录、读者解释与人物本人所知；三者不相同。已有资产足以研究，但要围绕NPC自身成长使用时须明确观察者与时间边界，不能把所有发布字段都当第一人称可知状态。

## 6. 一句普通指令与完整内容评分

同一64题、同一两模型的一句角色归属提示已在新生成前冻结；不增添任何剧情事实或gold，不迭代第二种提示。恢复评价会同时阅读名字和实际事件，不能只把Johnny名字写对、却继续给他Jim的母亲。

另使用原版PUF system准则，提供完整原有前态与按原运行器规范化的后态，评价profile、tracker与描述的联合内容。它是本轮单角色适配和替换评委，不能与原论文多角色模拟的PUF数值直接同比。该补充正在运行；完成后的数字与恢复案例写入报告，原baseline与原始失败不覆盖。
