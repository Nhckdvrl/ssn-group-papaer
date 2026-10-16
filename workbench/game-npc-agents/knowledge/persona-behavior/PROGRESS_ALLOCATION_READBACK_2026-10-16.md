# E73/E75/E76推进—用途全轨迹读回（POST-HOC，2026-10-16）

**结论：附件抓到了有用的整体研究框架，但“守恒”本身是分类恒等式，还没有识别出统一的两阶段因果机制。** 全部8,928条缓存原生轨迹（E73 2,808、E75 4,896、E76 1,224）按成功事件与源item_id重算，0模型调用、0GPU。人物既关联前提推进，也关联后续用途的联合现象保留；推进量的定义、余项、选择后的条件分布必须分别报告。

## 1. 精确定义与复算

成功事件沿用原始协议：`legal && executed && !stochastic_failure`，再核对目标node_id及前后物理状态；命令尝试、文字承诺不计执行。原字段`stochastic_failure`继承引擎failed标记，不意味着每次都是随机失败。

- **P**：源物品成功Remove（E73）/Get（E75），是实际发生的前提事件。
- **G**：精确原作者目标事件；E73为源物品交给A，E75/E76为绑定源物品/接收者的原生Give/Wear/Eat/Drink事件。
- **B**：源物品交给不同的请求者；E73 aligned的请求者就是A，不能一笔交付重复计为G与B。
- **O**：源物品交给其他接收者。
- **R**：完成P、但截至原8步停止点仍无上述注册终局。它可能包含已丢弃或已消费，并不都叫“hold”。

在真正需要P的初态，逐条验证：`P = G + B + O + R`；有余项也完整保留。另一恒等式`已注册终局 = G + B + O`使用的是**不同的推进量**。对这些恒等式取人物差仍是恒等式，不单独证明潜在模块、固定执行能力、神经机制或因果中介。

E76 ready的前提由初态干预满足，没有把初始化Get冒充NPC选择；其实际Get为0不能解释为“推进机制为0”。条件于成功P的qG/qB在ready不适用。条件分布会选择人物依赖的子集；与ready相比只是描述，不是人物纯粹用途效应。

复算（含下述8条CPU物理分叉）：`env PYTHONPATH=/home/xiang/.cache/game-npc-research/deps /home/xiang/miniconda3/envs/fgvd/bin/python workbench/game-npc-agents/scripts/native_progress_allocation_posthoc.py --verify-consumption-semantics`。完整结果为[JSON](../../results/E73_E76_progress_allocation_POST_HOC.json)，保留所有模型/任务族/人物/状态/支持条件、精确分母与源文件SHA、图簇bootstrap区间。E75细分Give71、非Give31、Wear12/Eat9/Drink10；三seed始终在图内配对，4,000次图簇重采样。只用正式完整分片，profile不重复计数。

## 2. 附件两组算例的精确核对

### E73：117图、divert initial feedback，每人物351条

| 模型/人物 | P：Remove | G：给A | B：给请求者 | O | R：Remove后无注册终局 | 无Remove |
|---|---:|---:|---:|---:|---:|---:|
| Gemma Firm | 202 | 198 | 0 | 0 | 4 | 149 |
| Gemma Agreeable | 259 | 248 | 4 | 0 | 7 | 92 |
| 32B Firm | 287 | 273 | 8 | 0 | 6 | 64 |
| 32B Agreeable | 307 | 281 | 21 | 0 | 5 | 44 |

Gemma精确人物差为：`50/351 = 57/351 − 4/351 − 3/351`，即**任务+14.245pp = Remove+16.239pp − 给B+1.140pp − 余项+0.855pp**。附件的+15.38pp是“已经给出源物品”的增量，不是Remove增量。

32B精确为：`8/351 = 20/351 − 13/351 − (−1/351)`，即**任务+2.279pp = Remove+5.698pp − 给B+3.704pp − 余项−0.285pp**。附件的+5.98pp同样是“已交付”的增量。原任务数值不变，得到的解释更精确：成功前提与完成终局之间仍有可测的差别。

Gemma的R中，Firm2条/Agreeable4条实际丢弃过源物品，不能统称“物品还拿在手里”。完整细节见JSON的`source_drop`与`pre_no_terminal_*`字段。

### E75：非Give31图、retrieval baseline，每人物93条

| 模型/人物 | P：Get | G：原任务 | B：给请求者 | O | R：Get后无注册终局 | 无Get |
|---|---:|---:|---:|---:|---:|---:|
| Gemma Firm | 46 | 36 | 7 | 0 | 3 | 47 |
| Gemma Agreeable | 63 | 41 | 19 | 0 | 3 | 30 |
| 32B Firm | 74 | 50 | 12 | 0 | 12 | 19 |
| 32B Agreeable | 84 | 35 | 38 | 0 | 11 | 9 |

附件这一组数值精确成立：Gemma`5/93 = 17/93 − 12/93 − 0/93`；32B`−15/93 = 10/93 − 26/93 − (−1/93)`。它将不同任务得分拆成有意义的联合行为组成，适合进一步提出可预测的计算解释；恒等式本身不区分对话锚定、目标价值/等待成本、路径实现等解释。

注册终局保持原实验的精确事件定义。本切片有3条原生`ingest`实际消费了源物品，但不是作者指定的`drink`/`eat`事件：Gemma Firm/Agreeable各1条（beer，seed7503），32B Agreeable1条（candy，seed7501）。这些留在原R中，同时单列`source_consumed_without_bound_goal`；下述源码和物理对照已确认它们**实现了相同的实体消费后果，不能叫消费任务失败**。历史bound事件读数保持，物理完成另报secondary。

## 3. 条件分配与ready：相近不等于因果等价

| 非Give31、baseline | qG：成功Get后原任务 | qB：成功Get后给请求者 | E76同对话ready原任务 | E76同对话ready给请求者 |
|---|---:|---:|---:|---:|
| Gemma Firm | 36/46 = 78.26% | 7/46 = 15.22% | 74/93 = 79.57% | 6/93 = 6.45% |
| Gemma Agreeable | 41/63 = 65.08% | 19/63 = 30.16% | 59/93 = 63.44% | 29/93 = 31.18% |
| 32B Firm | 50/74 = 67.57% | 12/74 = 16.22% | 62/93 = 66.67% | 13/93 = 13.98% |
| 32B Agreeable | 35/84 = 41.67% | 38/84 = 45.24% | 47/93 = 50.54% | 39/93 = 41.94% |

Gemma qG−E76 ready为Firm−1.31pp[−17.13,11.92]、Agreeable+1.64pp[−8.18,11.36]；32B为+0.90pp[−6.45,8.86]、−8.87pp[−19.85,1.23]。这给“共享前提与用途分配”提供了值得追查的具体线索，**不支持声称所有条件分配已经完全一致或统计等价**。成功Get的子集、前提之后已用预算、对话/动作历史都不同；完整记录包含这些竞争解释。

## 4. 无前提不等于无行动，也不是统一“送别的东西”

| 条件/模型 | Firm：未做P中交其他物品 | Agreeable：未做P中交其他物品 | Firm：全程只有成功非物理动作 | Agreeable：全程只有成功非物理动作 |
|---|---:|---:|---:|---:|
| E73 divert Gemma | 33/149 = 22.15% | 31/92 = 33.70% | 91/149 | 55/92 |
| E73 divert 32B | 11/64 = 17.19% | 9/44 = 20.45% | 30/64 | 20/44 |
| E75非Give retrieval Gemma | 0/47 | 0/30 | 46/47 | 30/30 |
| E75非Give retrieval 32B | 0/19 | 0/9 | 18/19 | 9/9 |

E75 Give71的未Get轨迹中，交其他物品为Gemma24/135与28/119、32B4/27与8/25；不能将E70的其他物品比例直接搬到E75非Give。完整JSON分别保留讲话、表情、观察、阻挡、拒绝/失败及互斥轨迹类型；各行为标记可以重叠，互斥profile另列。表情/协商处在静态请求者协议下，不能仅因8步内无原任务就判定潜在规划无能力。

**原子路径补核：** 所有需要前提的E73/E75轨迹中，`no_pre_source_material_change=0`，没有“未做必要前提、却直接Drop/处置源物品”被遗漏。E73有20条轨迹、22次成功源Drop，其中14条在Drop后又Get；Gemma divert Agreeable中2条发生`Remove→Drop→Get→Drop→Get`。因此“前提已做过”不是单调的物理持有状态，也不能把其余项全部称hold。E75/E76没有源Drop。JSON已保留前提后无终局的完整原子源路径频次、Drop后再Get与Get后再Drop标记；ready的无Get不是“无源推进”，不纳入这个前提解释。

## 5. 吃喝事件：源码事实与物理完成secondary

**源码事实（LIGHT `71a06cae8573048b1af41507ac52fe33b650fab3`）：** `graph_events.py:3041–3162`的`IngestEvent.execute`将源物品移到VOID、标记删除，按同一`food_energy`更新actor健康；`EatEvent`和`DrinkEvent`继承同一个execute，未覆写动作后果，只收窄`can_ingest`到food/drink并改变动词、时态和消息。`all_events_list.py:72–74`将三类都列为原生命令。源码SHA及继承方法相同的断言已存JSON。历史harness使用精确event class和目标ID绑定，不运行完整quest XP服务；不能用这份CPU检查声称完整私人目标/任务服务flag已完成。

**物理核对：** 全E75/E76共9条源`ingest`未匹配原bound事件，来自4个源图（candy、beer和两个wine）。从对应原生ready图各分叉执行作者`eat/drink`与`ingest`，8条CPU对照均成功；每对**全部material state以及整个序列化graph完全相同**。四个物品原始food_energy均0、actor健康10→10，不能额外包装成已证明饥饿/生存收益；相同实体消费本身确实实现了作者吃/喝原物品这一具体后果。9条历史记录的身份、命令和健康变化另列`consumption_equivalent_witnesses`。

secondary定义为：原bound目标事件成功，或作者eat/drink任务的同源物品被任一合法Ingest/Eat/Drink消费。它不把Wear任务误吃物品算完成，不改变原停止协议或任何历史评分。

| 非Give31、每人物93条 | 原bound G，Firm/Agreeable | 实体完成secondary，Firm/Agreeable | 人物差的变化 |
|---|---:|---:|---:|
| E75 retrieval baseline Gemma | 36 / 41 | 37 / 42 | +5.38pp不变 |
| E75 retrieval baseline 32B | 50 / 35 | 50 / 36 | −16.13→−15.05pp |
| E76同对话ready Gemma | 74 / 59 | 75 / 60 | −16.13pp不变 |
| E76同对话ready 32B | 62 / 47 | 62 / 47 | −16.13pp不变 |

整体推进—用途现象保留，32B两状态的“恰好同为−16.13pp”也不应拔高成精确规律。JSON的`physical_goal_secondary`/`physical_registered_terminal_secondary`/`pre_no_physical_terminal_secondary`并报全部条件的计数、人物差和图簇区间；原表与前述条件qG仍明确指原bound事件。

## 6. 对下一项研究的实际影响

继续以NPC人物、自身目标与社交请求的整体问题组织研究，**把推进与用途作为联合读数，而不是先宣告两阶段机制成立**。当前值得区分的是：对话立场是否带动目标物品的操作；同一已选后果下人物是否仍改变实现；共同前提是否因服务两个用途而提高采用价值。这个读回能校正定义、选出有信息量的对照，不要求再开提示词网格，也不把普通价值/成本解释存在当作放弃整体增量的理由。

明确目标后的恢复可以提供重要干预证据，但额外目标指令同时改变显著性和执行政策；差异缩小不能单独“铁证”证明原来的差异全是偏好、规划能力完全相同。同理，执行端人物×对话交叉应明确标为阶段干预，不冒充全链路一致人物的自然主效应。下一实验卡应保留这些解释，并能改变对整体联合机制的判断。
