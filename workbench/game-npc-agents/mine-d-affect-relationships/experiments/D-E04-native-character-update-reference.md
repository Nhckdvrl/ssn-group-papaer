# D-E04：原生人物状态更新普通参照（2026-10-22）

- **状态：** RUNNING
- **类型：** REPRO / EXPLORATORY
- **对应：** 矿区D驻留。D-E01/02主要测给定人物状态后的表演；本卡直接测场景后的状态形成，不将重复baseline当新idea。
- **问题（一句话）：** 普通8B与32B在已有角色更新任务中，怎样区分持久人物改变与暂时反应，生成状态是否有场景依据？
- **触发证据：** 已读EvolvingWorld主文§3.1–3.3与原生transform/simulator更新入口；发布24,977更新记录，51作品、2,671角色，22,306相邻角色出场profile/tracker均能接上。它是直接强近邻，不假设我们首创事件到状态学习。
- **固定来源：** 代码`1de26550ccfff105f3ffe9f4b386716446291341`，数据`ae7d82d38909783805979a8055d5ae913cb982f7`，完整混合任务SHA256 `2f9dd6b90c7ed6870916cce91fc5d8ec6ac218f3c0ec6a225736c095bf751e07`。直接取character_state_update原始system/human，assistant仅作隔离参考；不改故事、事实、任务或答案。
- **样本（输出前冻结）：** 可供每类至少4条的作品，按固定SHA256取8部；各4条profile_updated=true与4条false，各类按角色轮转/固定hash，合计64场景。有意配平，不估计自然发生率，不只挑戏剧反转。清单保存作品/角色/场景/来源hash。每作品预选1 true＋1 false作描述性案例，另完整列出两模型共同偏离标签项。
- **模型/配置：** Qwen3-8B `b968826d9c46dd6066d109eabc6255188de91218`与Qwen3-32B `9216db5781bf21249d130ec9da846c4624c16137`，本地BF16/SDPA/greedy/非thinking/seed0、batch4、8192输出上限、32768上下文，溢出停止，不静默截断。各64请求；另报Always-No-Update/Always-Update标签参照。不训练、不新增角色专用模型行。
- **输入资格：** 场景开始profile、历史hidden tracker、当前motivation、该角色视角完整场景互动；别人私人想法由原生构造遮蔽。动机仍为官方输入，不冒充无oracle辅助的原始事件流。初始资料/标签可能由后续小说信息回顾性构建，未显式含LOOKAHEAD不等于因果纯净。
- **主要读数：** 非空/stop/length、原生JSON有效率；profile_updated与发布标签的Agreement、Change召回与No-Change保留率、作品宏平均balanced agreement、8作品描述区间。它是发布监督一致，不叫唯一心理真值Accuracy。true需完整updated_profile字符串，false需null；tracker/description类型另计。格式无效按不一致计入主分母，另报有效条件分数。
- **行为阅读：** 核对实际profile/tracker/short_description与原场景，区分合理更新分歧、无依据事实、暂态写入持久卡、遗漏重要变化；无独立盲评不将类别频率当验证过的机制。
- **阳性对照：** 全量监督JSON可解析、与单任务发布内容hash匹配；完整来源恢复作品/角色/场景；不追加新提示。配平样本中两个constant标签参照各50%。认真比较32B普通完整提示，避免只用小模型差异宣称能力缺陷。
- **噪声地板 + MIE：** 单seed、监督非唯一合理解释；按作品报告，不把128调用当128独立样本。无预设必失败的阈值，无结果后挑样/加条件。
- **混杂审计：** 取自公开训练资产，两个通用checkpoint未在本项目用其训练，但无原著预训练隔离保证；不是官方held-out rollout复现。前态/动机teacher-forced，单步不证明长程累计漂移或玩家创造的成长。flag不代表profile内容正确，即使高一致也读输出。
- **决策表（跑之前写）：** 普通模型有据更新良好→承认简单能力；8B差32B好→先核容量/理解；共同偏离但双方合理→重新判断读数，不造坏例；持续无依据持久更新/遗漏且场景证据充分→才考虑学习/修订问题，并正面对比EvolvingWorld/PHASE-Tree。不自动升级方法主张。
- **算力预算：** 空闲GPU1/2各单卡，总上限4 GPU·h，与GPU3评分独立；无外部API。完整raw/prompt/token IDs存NVMe，轻量读数进Git。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
待填。由tools/process/new.py生成骨架后使用矿区D现有命名空间；未新增平级工作台或ACTIVE名额。
