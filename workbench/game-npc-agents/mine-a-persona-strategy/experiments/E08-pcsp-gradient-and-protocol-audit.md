# E08：PCSP 真实梯度、行为读数与角色拆分的源码核验（2026-10-14）

- **状态：** DONE
- **类型：** REPRO（作者代码审计与数值准入，不是新科学发现）
- **对应：** E06 / C01 强近邻与测量前提；无需为baseline审计虚造idea。
- **问题（一句话）：** PPO、InfoNCE和多样性损失各自直接更新哪些模块，内部人物可恢复性与独立行为评价的角色拆分/含义是否一致？
- **设置：** yoosunghong/pcsp@5420f7b4fa0fdb6110e131402af9f5386ce2d0cf；首先运行作者 `research/scripts/test_gradient_paths.py` 与 `test_independent_behavior.py`，CPU，原固定seed不变。补录作者原函数在其test fixture上的梯度范数；从作者JSON核查300/500版本ID、职业、BigFive组合、文本与奖励映射，不训练新数据、不调用生成persona的云脚本。
- **读数：** loss→projection/actor/critic/trajectory_encoder的梯度范数与预定拓扑；445/749维独立行为特征契约；各官方split的ID/文本/职业/BigFive组合交集和标签支持度，分别报告不同划分。数据拆分核验不等于论文数字重跑。
- **阳性对照：** 作者test fixture在FiLM warmup后PPO可更新actor/critic/projection，diversity可更新actor/projection；随机可区分轨迹的InfoNCE可更新projection/encoder；独立特征的直方图归一和重复字节一致。
- **噪声地板 + MIE：** 固定CPUseed直接拓扑核验应完全可复算；数值0与>0用于实现路径，不做统计显著性或persona行为效果判决；split交集是全量确定性枚举。
- **混杂审计：** author test为合成小网络且人为warmup FiLM，仅验证梯度路径，不冒充实际训练效应；作者已有独立行为检查与gradient audit必须记credit。训练回放的离散动作/obs不在计算图中；共享projection的间接行为作用不可因actor直接梯度0而否定。
- **决策表（跑之前写）：** 与作者预期一致→如实记录其强结果和解释边界；不一致→先核环境/版本/初态，不称方法无效；数据split交集→区分作者已声明的compositional与vocabulary-expansion，不自动判泄漏；没有weights/原始轨迹→完整复现仍未完成。
- **算力预算：** CPU≤0.5小时，GPU0小时；不加载作者LLM或训练大policy。

## 结果（跑完后填写）
作者gradient topology test和independent feature contract均PASS（前者首次因PettingZoo1.24.3不导出AgentSelector失败，1.25.0后PASS；失败日志保留）。作者warmup fixture的InfoNCE梯度：projection 93.0923 / encoder 8.59584 / actor与critic均0；PPO：projection0.0076486 / actor3.69586 / critic5.96453 / encoder0；diversity：projection0.000906857 / actor0.00175816 / critic与encoder0。这是源码路径复算，不是新发现或实际训练因果效果。

全量split枚举：300版240/60的职业交集0、BigFive原型交集15；500版400/100职业交集20、原型交集0（test5个未见原型）；unseen_combo、unseen_archetype另行核验。所有5套拆分ID和完全相同文本交集均0。300份v3 preferred_actions映射300/300与作者生成代码一致，人物文本300/300未变。结果：`results/E08_pcsp_protocol.json`，无需CI（确定性全量核验）。0 GPUh。主张无科学升级；已确认baseline/评价资格的一部分，未复现论文完整分数。

