# I01：纠正一个事件后，留下的是事件关系还是可迁移的谓词关联？（2026-10-05）

- **状态：** PILOT；当前候选问题，不是已证成的顶会idea。
- **来源/研究动作：** P10/P11，E14–E25的条件化异常、竞争解释分离和独立source预测；不从二分提示词猜题。
- **自然问题：** 后来的证据排除了原活动的一位参与者。模型后续仍偏向或抑制那个人，是因为原事件关系没改好，还是因为词/关系关联记忆被带到了别的活动？
- **当前具体观察：** E22同角色事实的具名/泛指表述改变activity-minus-neutral的GP历史效应；E24独立24 source/12verb-family迁移−.795 [−1.210,−.394]bits。E25这个信号继续出现于同actor新event−1.249 [−1.757,−.762]、另一actor新event−2.070 [−3.099,−1.200]；严格9同向。它不是old actor/old event专属的证据。
- **待检验主旨：** 要判断修订到底改变了什么，必须区分局部事件约束的可用性与可迁移的关系预测痕迹。不能仅用一个患者continuation的surprisal信号证明old event未修订。更强的positive account需找到痕迹依赖哪些信息以及在哪种正常用途有后果。

| 竞争解释 | 判别预测 | 当前证据 |
|---|---|---|
| 原事件绑定未被完整更新 | 痕迹应特别对应原event/actor；final/scoped用途可能错 | E25跨新event/actor更强，专属归因不足；E23实际错误不稳定 |
| 同人物的关系关联被改变 | 同actor新活动保留，换actor应弱 | E25换actor没有消失而更强，actor-only不足 |
| 谓词/模板相关的可迁移关联 | 跨actor/新event保留，可与局部scope知识共存 | E25支持迁移；E26正在测scope与原S1 final的共同可访问性 |
| 一般实体可及性 | neutral与activity应平行变化 | E17/E22/E24的matched-neutral控制不能解释全部结构 |

## 已完成的关键判别

- [E14–E16](../experiments/E16-patient-specific-crossover.md)：固定continued的scope调节含patient-specific成分，7episodic A_M+2.11 [1.17,3.14]；aspect也有贡献，不是pure event图。
- [E17](../experiments/E17-relation-versus-entity-accessibility.md)：关系使用与neutral提及分开，entity-only不足。
- [E18](../experiments/E18-predicate-paraphrase-transfer.md)：独立faithful9source释义A+1.44 [.90,1.91]，exact lemma重复非必要，但predicate association仍竞争。
- [E19/E20](../experiments/E20-exclusive-fact-versus-last-mention.md)：双向role事实明确改变R，肯定对象放最后仍有history差；整体GP已偏允许对象，不能叫完全没更新。
- [E21/E22](../experiments/E22-post-correction-entity-versus-role-use.md)：较小GP−cue差主要cue下降；named提高实体可及性，在GP又相对抑制活动患者关联。不能卖否定重插错误关系。
- [E23](../experiments/E23-functional-role-continuation.md)：224实际续写，首/次独立审10/6contradiction、84/88unknown；再次GP/省略patient/自我否定让功能错误证据不稳，全部保留。
- [E24/E25](../experiments/E25-event-versus-actor-correction-scope.md)：独立source预测与event/actor范围，见上述paired CI；12same-verb家族是bootstrap单位，不是派生句数量。

## 定位与increment压力

| 最近邻 | 已拥有的claim | 必须讲清的增量 |
|---|---|---|
| Slattery2013、Sturt2007、Huang/Ferreira2021、Ceháková2023/25 | lingering、后文reflexive、global interpretation与local parse、多种final解释 | 区分一个关系信号的event/actor适用范围与predicate迁移，不能再说“仍有旧解释” |
| Cao/Schuler2025、Amouyal2025、Hanna/Mueller2025 | completion/error-controls、paraphrase、syntax/QA不复用 | 不能只加binding/更多模型；需要portable关联的范围预测及具体用途 |
| Hu/Levy2023、Zhou ICML2026、Mann2025 | metalinguistic/probability差、否定机制/shortcut并存、词可及性 | 不能卖generic readout gap或“not X使X显眼”；要用跨不相关actor/event的迁移识别relation trace的对象 |
| Chen CMN2026、Xu BeliefTrack2026、Hase2024 | revision/elaboration结构区分、scope/更新/保持及belief逻辑一致性 | 不把概率变化当图边retraction；本线对象是语言解释产生的关系预测如何迁移，而不是通用belief更新benchmark |

- **当前下一决定性动作：** [E26](../experiments/E26-scoped-constraint-access-versus-portable-trace.md)，同source上独立审计scoped compatibility与原S1 matrix-proposition正反控制、native回答与一句恢复。正确QA不证明question出现前内部已经更新；结果必须按读数用途解读。
- **论文形态候选：** 修订测量的对象识别 + 可预测的portable relation-memory结构。还欠自然功能后果/来源干预；仅有漂亮差值不够。
- **仍缺/不确定：** 实际local event约束及源句final解释能否共同使用；portable效应依赖原谓词关联、source replay还是更一般语义；已有owner能否压缩这个精确增量；自然用途是否值得reviewer关心。不得以近邻存在自动关线。
- **最新定位：** venue-nearest + primary arXiv已核对negation与incremental narrative近邻，读取范围见知识库；搜索不完整，不作新颖性认证。此卡从E14原活动回指/原词echo问题演化而来，研究对象始终是incremental interpretation revision，非新开线。

**E26反馈：** source final/assertion原主体与swap读数高，但原事件兼容/矛盾两问都No，joint scoped-access base0；不能宣称已正确scoped修订。E27只加已允许患者的匹配proposition，区分No default与truth-verification替代比较任务。这里是instrument原因校准，PILOT不升级，旧全部结果保留。

**E27反馈：** 匹配allowed命题的两问joint全部100%，所以非整体No-default或整体truth-verification。原excluded失败及new未指定患者的“不一致”可能是unknown/contradiction混淆。下一三类语义关系+unknown阳性对照，明确这些状态；仍不宣布scoped-state访问已成立。
