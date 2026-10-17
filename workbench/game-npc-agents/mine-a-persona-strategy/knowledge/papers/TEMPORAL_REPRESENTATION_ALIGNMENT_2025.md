# Temporal Representation Alignment（NeurIPS2025 main）`[证据：正文/关键附录]`

[官方论文](https://papers.nips.cc/paper_files/paper/2025/file/dc8fe7925e37b2fa764d0ec3294c9133-Paper-Conference.pdf)。已读§3/4、表1、A/D/H及表4/5/6；未完整复核证明与作者代码/训练。

1. 形态：组合表示方法＋机器人真实/模拟验证。DOCUMENTED来源是单步训练state-goal pair不能覆盖多步任务，计划/离线RL并非唯一解。
2. 方法：当前与未来state时间对齐、goal-language CLIP式对齐＋goal/language BC；不用额外规划即可stitch已学行为，successor features给组合依据。
3. 数据/证据：Bridge真实机器人四scene、多步指令与goal images、OGBench；GRIF/LCBC/Octo/AWR与表示/α消融分别测。附录最终三evaluation epoch平均、α设置与单侧Welch检验明确，不能误称无调参/全部独立测试配置。
4. 定位：语言目标表征对齐、没有规划的组合迁移已有owner。可迁移“区分任务组合数据覆盖与表征归纳偏置”的研究动作；I03是原生角色属性/利益关系，不能将任何contrastive语言对齐写成首创。普通增强/奖励解释充分时承认。
