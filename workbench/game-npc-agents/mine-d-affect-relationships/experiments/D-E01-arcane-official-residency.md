# D-E01：ArcANE官方基线与公开生态驻留（2026-10-22）

- **状态：** RUNNING
- **类型：** REPRO
- **对应：** 矿区D驻留D1/D2；主问题为时间证据约束下的人物状态推断与适应。按R12不为标准baseline强挂新小idea。B/I01保持PAUSED，历史结果不继承。
- **问题（一句话）：** 官方人物阶段输入、普通身份/章节提示与角色后训练模型，在真实公开跨阶段探针上如何表现；这些数据究竟支持怎样的人物状态研究？
- **设置：** ArcANE代码固定`46ee34a73c7bd006ba52a7a262586f02301cdb6f`、PHASE-Tree固定`0be378fd23c49915255406d881f2389b46b608b8`。先完整清点公开正式benchmark与训练配置，离线复算作者发布的judge表（标历史结果，非新推理）。首轮选择64个完整probe组、保留全部可用phase，覆盖公开held-out main的4小说和lowpop的2小说；按小说/人物/probe type/axis固定hash排序，禁止只挑显著反转、模型失败或结果好看的故事。训练parquet内部test不作benchmark。
- **模型：** 本机Qwen3-8B revision `b968826d9c46dd6066d109eabc6255188de91218`；官方ArcANE-8B-DPO revision `67b9bea604bea65a5245928ed87103545814b4f7`。BF16、SDPA、greedy、seed0、非thinking、官方8192 completion上限、batch按内存固定。先官方vanilla/arc两模式，逐字使用官方Trial、context_builder与prompt renderer；保存完整prompt、raw、token ids与配置。没有造新故事/新正确答案。
- **评价：** 官方per-response APF/RPF/RAE模板和参考，使用已授权Step5 Token Plan专用路径（temperature0、medium、8192上限、并发2），明确是judge替换，不能与论文DeepSeek分数直接同比。先按预定样本与同一judge完成配对；不让judge看到mode/model。官方PTF使用完整probe跨phase，另记调用预算。首轮API最多1200次含PTF/技术恢复，遇额度错误停止，不走现金接口。实际tokens按usage报告。PHASE文本基线在独立数据上单独登记，不混合分数。
- **读数：** 有效/空/截断输出；APF/RPF/RAE和PTF按小说宏平均、人物/轴/probe/phase层级分解；按完整probe配对，小说聚类描述性区间；逐例阅读不同类型成功与失败。此处fidelity是参考体系一致，不等同真实作者唯一心理、在线成长或NPC玩家体验。
- **阳性对照：** 原官方存量judge表可复算；prompt字节与官方renderer一致；参考与候选严格分离；同一probe全部phase完整保留；预先固定样本hash。抽查参考行为与官方构建来源；不拿oracle输入假装在线原始事件。
- **噪声地板 + MIE：** 单greedy首轮，无种子方差；judge评分有主观/版本噪声。按作品/人物观察效应与分布，不以0.几分或固定阈值判科学价值；先复现整体能力和真实行为，再决定下一动作。必要的少量重复评委校准在新卡中预声明，不无限调judge。
- **混杂审计：** 训练与benchmark作品区分；公开main少Harry Potter，按实际4部公开范围报告；arc保留axis_name并按phase起点截断，字段可用性不自动等于严格时点因果可用；vanilla仍含作品名/人物名/章节；已发表ArcHint/summary/rag等方法不当稻草人；Stage 1–3工作流与训练reward service分开；读数不跨ArcANE与LongEvo合并。潜在问题先登记，不预设严重泄露/旧状态惯性。
- **决策表（跑之前写）：** 官方后训练在原设定改善→先认真理解其成功；普通合法历史摘要已足够→接受无需新结构；持续观察到证据输入与人物状态不匹配→核对信息充分性后再研究归纳/状态学习；只是数据或实现问题→修复并如实界定复现；没有重要残差→扩大领域理解，不为坏例子循环加条件。后续从代表性真实例子、近邻差距与可用原著证据选择1–2个研究动作。
- **算力预算：** 初始2张空闲单卡，本地最多8 GPU·h用于本卡首轮；下载/预处理CPU独立记录。API首轮最多1200 calls、仅Plan；无新RL或大训练。**实际：** 待运行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待填；所有完整资产在`/var/tmp/ssn-game-npc-d/`，Git只存来源hash、轻量清单、结果与复算脚本。

### 解码配置补充（模型运行前）

官方API transport的role-play调用默认未设置temperature，实际由各服务端决定。本地统一greedy是明确的受控复现设置，不能称作与论文服务端逐样本完全相同的采样。prompt/context/evaluator使用固定官方代码；输出上限8192不改。小样本方差不足以将本机greedy差异外推所有解码设置。

### Judge服务资格修订（首次语义评分分析前）

Step5 medium技术预试中，仅3个整数的裁判返回消耗了数千推理tokens，并出现8192 length无完整判分。未查看分数方向即停止该设置；全部已落盘调用存`step5_judge_medium_calibration`，所有预试分数均不进入正式结果，最多2个在途调用的用量未知上界单列。正式评分统一改为`reasoning_effort=low`，所有模型/模式使用同一设置，仍8192上限和原官方提示。官方原judge默认关闭推理，该修订更接近该使用方式；Step仍是替换评委，不能冒充原DeepSeek复现。总1200调用预算包含预试与所有技术恢复，不增加cash入口。此修订依据格式/资源资格，不依据哪种方法分数较好。

### 运行吞吐补充（正式评分设置不变）

正式low judge的请求耗时较长，使用检查点暂停并从已保存的judge_id续跑，将并发由2提高至6以在持续驻留中完成。模型、effort、prompt、量表和token上限保持相同，已完成判分不重打；总调用预算仍包含技术预试，不加预算。若服务返回额度/限流错误则停止，不绕过限额。所有阶段metadata/source快照保留。此项是吞吐配置变更，不是新的科研条件。
