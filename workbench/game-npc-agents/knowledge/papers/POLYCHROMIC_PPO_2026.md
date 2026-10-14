# Polychromic Objectives for RL（ICLR2026）`[证据：正文/关键附录]`

[官方论文](https://proceedings.iclr.cc/paper_files/paper/2026/file/3ee63632d4c26ddc3d350c86ffca381c-Paper-Conference.pdf)。已读§3–5、表1/2、B.1采样/稳定性与理论命题；未完整校验D证明或作者代码，代码位置未核实。

1. 形态：集合RL目标、理论＋PPO方法。DOCUMENTED来源是RL微调的探索/覆盖退化。
2. 关键动作：对整组轨迹的平均reward×多样性分配共享advantage，用vine sampling，非分支状态仍GAE。目标既鼓励成功也奖励未成功的探索路径。
3. 协议：各方法trajectory预算136，集合4/分支8/状态2；KL行为政策锚点与局部advantage窗口为重要实现。BabyAI/Minigrid五任务、50配置、三seed/100rollouts；另有triangle任务。附录改时间惩罚以减弱较长成功路径劣势，不能冒称完全原默认reward。
4. 证据：pass@k/新配置扰动与reward分别测；组合任务提升不均，保留全部表格。不是人格心理测量或语义属性绑定。
5. 定位：集合式成功＋多样性训练已有owner，不包装成我们的新loss。可迁移“同起始状态比较整组策略后果、匹配采样预算”的研究动作；E37/39现阶段仍局部响应，长程闭环不可省。
