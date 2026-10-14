# E28：原辅助更新中的人物特征坐标控制（2026-10-14）

- **状态：** DONE / 负结果
- **类型：** 形成机制pilot；不是先规定新loss。
- **对应：** I02 / P06；E25/26/27。
- **问题（一句话）：** 原consistency+diversity辅助更新中的共享φ坐标移动，是否对原生行动产生超过几何变化本身的额外扰动？
- **设置：** 正确编码E25 Full/NoCons30iter的同seed42 checkpoint，各按原trainer再做1完整iteration（8×16×200），保留原4次PPO后co-step的before/after policy/η。原cfg/reward/world/角色/来源不改，NoCons为原lambda0控制。只用train400的Φ_before/after计算orthogonal Procrustes R，使row Φ_after R近Φ_before；fit未见test100。先人工已知SO旋转阳性：φ/η共同旋转保留所有cos/InfoNCE，FiLM所有gamma/beta入口配套逆坐标补偿恢复原logits；未补偿旋转本身不算科学发现。
- **读数：** 每真实co-step的train/test Φ移动、Procrustes剩余/总能量、同原native states的before/after KL与argmax。first/fourth co-step冻结后，native test100×world28011/12/13比较before、after、after+R、after+oldφ（actor/div更新保留，仅投影回旧）。只改变神经通道，原body/reward/physics不动；persona簇paired return CI。φ与η同右乘R，在相同已保存τ上source内部cos/InfoNCE不变，**不能由此说重新生成的τ读数也不变**。R补偿作用若只是减小变化，需下一卡matched-damping/PPG对照，不预支机制。
- **阳性对照：** 已知旋转几何/内损失差<1e−5、补偿FiLM logits差<1e−4；源真实co-step4个/原完整迭代/replay0差；train-only fit，held100无拟合；NoCons同样路径/步骤记录。直接检查actor/critic来自div的变化，不把整个co-step都归给consistency。
- **噪声地板 + MIE：** known compensated rotation数值地板与before native重复；真实native return差≥2%且CI排零、多个真实co-step方向一致才继续确认。一次epoch/一个train seed只是pilot；若Φ移动小/对utility无信号，坐标假说降级，不用大随机旋转凑阳性。
- **混杂审计：** 原co步含div以及Adam动量，既有actor更新需oldφ拆开；不同PPO epoch轨迹仍是同source rollout，称stale replay不能当独立行为样本。原始训练分支不反馈我们的R，pilot仅冻结后干预，不称已经提出新训练法。Procrustes/gauge invariance/aux-policy drift已有理论和PPG owner，必须看真实NPC增量；旋转构造不是自然异常证据。
- **决策表（跑之前写）：** rotation主要且补偿稳定恢复utility→继续matched-damping、已知PPG保护、独立seed再发展机制；坐标分量小或没收益→降级解释；NoCons相同→解释一般共享投影更新，不讲cons独有；控制失败→修工具；普通冻结φ/PPG全解释→承认已知范围。
- **算力预算：** 单CPU≤30分钟、0GPU/API，现有fgvd+deps。若无信号不铺训练矩阵；public3seed只有pilot有信息才确认。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
真实source各4次co-step记录完整，已知旋转/FiLM补偿/几何不变/完整native replay正控制通过；Full与NoCons各93.67/94.10秒单CPU。Full旋转解释feature移动27–88%，NoCons50–87%，不是cons特有。Full对齐后相对raw co-step1收益+.170、persona簇95%[−.232,.558]，co4+.094[−.070,.251]；NoCons分别+.095[−.106,.305]、−.069[−.344,.266]。远未达到2%/跨step稳定原生utility门槛，**坐标解释降级，不铺更多训练**。Full co4原辅助更新本身比before增加.414[.118,.790]，反例保留。

[Full完整结果](../results/E28_full_feature_frame.json)、[NoCons](../results/E28_no_feature_frame.json)。Orthogonal invariance/Procrustes与PPG辅助策略保护已有owner；不以人工大旋转或高rotation fraction替代真实行为信号，I02未确认新机制。
