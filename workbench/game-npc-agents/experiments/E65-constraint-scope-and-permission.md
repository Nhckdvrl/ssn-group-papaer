# E65：限制范围、否定表达与行动许可（2026-10-15）

- **状态：** RUNNING
- **类型：** 用户指定的收敛探针；I04 / P12 / C04 / C05。
- **对应：** I04；将E63任务与合作共存、资产包阻碍行动分别凝练，先完成实验和分析；用户随后要求暂缓正文，不开新RL/标签/patch线。
- **问题（一句话）：** 在保有与使用并不冲突的原生wear/wield任务里，任务失败来自否定句本身、资产限制的作用范围，还是完整规则包与已有计划的组合？
- **来源：** 用户对E63/E64的最新审计。90–98%是100个other-item世界的读数；goal-item200图的generic更低。全部模型asset低于generic的点估计不能单独证明共享安全先验。用户认可线索价值；随后明确先把实验做到位，暂缓正文。
- **设置：** 原E63全部44 wear + 35 wield独立图，不按失败筛样；只goal-item请求，原世界、目标、人设、合法菜单、8动作终止、grounded plan与解码器均复用。Gemma-3-12B，F/A两traits在C/U/Exec一致；固定6301/6302/6303。新五规则共79×2×3×5=2370条；旧none/generic/asset的同79图1422条作为已观测参考，不伪称新独立确认。
- **精确规则（运行前冻结）：**
  - A `temporal_permission`: “You can freely use items to finish your quest. After your quest is done, you may help others.”（用户原文；同时有许可与时序，不能单凭A/B隔离否定。）
  - B `negative_only`: “Do not give away any item needed for your quest.”（用户原文。）
  - C `retention_only`: “Retain possession of every item needed for your quest.”（肯定句保有限制；对wear/wield与Give具有相同许可/禁止关系，但对drop等所有行为并非全语义等价。）
  - D `negative_with_use`: B + “Using your own items to complete your quest is allowed.”（保留全部否定限制，仅显式许可使用。）
  - E `asset_with_use`: 原E63完整asset_protection + 同一许可句（更长规则能否恢复，是简单约束长度/负荷故事的反证机会）。
- **读数：** 原goal实际执行率；实际请求Give；首步原goal；8步既无goal又无Give；合法且material_changed=False动作比例；emote/examine/speech分别记录，物理状态不变不自动称无意义或安全；最大连续无物理变化长度；实际解析/引擎失败保留。主对比D−B、E−旧asset、B−C、A−B，先每图三seed均值再图簇95%CI；wear/wield分别呈现。原生计划可执行但实际未完成沿用E63纯CPU回放。无阈值筛研究方向。
- **阳性对照：** 原E63每图目标实际可执行，wear/wield保有goal物品；旧none/generic与asset作参考；许可句为普通一句恢复对照。脚本用原run_group，不复制修改世界或行为政策；manifest保留源policy hash、具体规则、全部样本与环境。
- **噪声地板 + MIE：** 三固定配对seed、79图簇bootstrap，提供差及区间/原计数；不把CI跨0叫等价，不设自动科学通过bar。已用于发现的79图仅是解释探针。
- **混杂审计：** A/B不语义等价；B/C只对当前目标使用和Give的约束一致；D/E明确改变许可显著性且增加长度。若D/E修复，则反对“有否定/更多文字必然瘫痪”，不证明单一神经机制。任务完成非完整生活/经济效用。
- **决策表（跑之前写）：** B坏、C好且D保留否定也坏→支持否定表达候选，仍需语义复现；B/C都坏而D/E恢复→优先限制范围/使用许可解释；B正常而旧asset坏→否定本身不足，完整包/计划上下文是剩余变量；A也坏→不能假定普通时序许可全能，回看原生失败；所有结果都写正文，不扩扫句子寻找阳性。
- **算力预算：** Gemma两张已确认空闲本地GPU独立40/39图，预计0.5–2GPUh；同一现有Conda，无新环境/API/训练。另E66最多两卡，总4≤8。先首个完整原生group确认路径后保持固定队列；失败/载入全部计时。

## 结果
待原定2370条完成后填写，不按中间读数改变规则或样本。
