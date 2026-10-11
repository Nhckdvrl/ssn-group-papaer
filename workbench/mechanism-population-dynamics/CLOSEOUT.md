# Mechanism Population Dynamics — 最终科研结项审查

**日期：** 2026-10-11。**决定：** 用户明确确认项目终止、已经收尾。投入了大量实验和四版论文，但进一步追逐这个主问题的科研价值、意义有限。本文件是按已有 Git 实验卡与结果的总结，不是新科学实验、审稿意见或论文录用证明。

## 一、研究路线究竟怎么变了

| 阶段 | 当时尝试回答的问题 | 后来为什么改 |
|---|---|---|
| E01–E24 | Induction 头群体、上下文与参数记忆仲裁 | 有局部观察，但一些解释只适用于小模型、特定合成数据或格式；通用一维仲裁假说受反证 |
| [v0](paper-acl-v0/) — *Born to Copy, Taught to Trust* | 初始化与训练数据分别扮演什么作用 | “先天 / 后天”比喻太强；实验读数与论文叙事之间缺少必要的机制连接 |
| [v1](paper-acl-v1/) — *Which Head Takes Which Role?* | 头的具体角色如何随 seed 继承 | 头位置是可置换的坐标，不应自动当作功能层面的新知识；provenance 解释还被强近邻和权重指纹基线压缩 |
| [v2](paper-acl-v2/) — *When Do Mechanisms Correspond Across Pretraining Runs?* | 同一算法、角色、组件或因果承担者在不同模型之间是否可对应 | E75 的 0.85/0.94 功能映射很大程度上读取了目标模型自身 DLA，不能解释为仅凭源模型就能转移组件 |
| **[v3](paper-acl-v3/)** — *Which Head Does the Work?* | 同初始化兄弟 vs 同一训练后代的 head-level 结论可迁移性 | E81–E86 给出更多真实测量边界；但整体主张的新颖性与科学影响仍不够高，用户决定结束 |

## 二、经得起反证的局部事实

**1. 角色图有相似性，但不等于因果组件相同。** [E35](experiments/E35-init-by-data-mechanism-census.md)、[E59](results/e59/analysis.json) 的 DataDecide 等跨配方统计表明，角色图可以与共同初始化有关。置换同层 heads 的坐标不改变模型函数，因此“头编号”本身不是稳固的机制对象。数值相关性和机制等价绝不能混写。

**2. 训练谱系非常重要。** [E81](experiments/E81-carrier-inheritance.md) 对 DataDecide 同 seed 跨语料模型的注意力图报告约 0.24–0.34 的对应，而 IOI 单头消融图约 0.02，源模型 top-3 任务迁移约 0.03。经过 P13 的 HF checkpoint 祖先关系核对后，在 OLMo / Pythia 真正同一训练 lineage 上，主力头与消融迁移通常较稳定（不同节点约 0.93–1.00）。旧误以为是 base→SFT 的若干 pair 已因不是父子关系而排除。**DLA 层内 rank 图信度仅约 0.40，不符合登记的 0.8 门槛；不能再把 DLA rank 几乎不对应当作可靠的直接发现。**

**3. “行为涌现即选定承担者”被否定。** [E82](experiments/E82-when-carriers-are-fixed.md) 在 Pythia 给出了后验线索；[E83](experiments/E83-carrier-chosen-at-emergence.md) 将其前瞻验证于 DataDecide 的 12 个 run，最强头从首次通过 IOI 阈值到终点仍相同者仅 **3/12**，并同时满足 top-3 的仅 **2/12**。因此不能把“一次选定并保持”写成普遍发育机制。

**4. 删数据后的单头变化不是自动的因果解释。** [E85/E86](experiments/E85-candidate-gap-and-swaps.md) 原样重跑最强 induction 头易主 **9/15**，随机屏蔽组 **14/30**；原样重跑 induction / previous-token 角色图仍有约 **0.80/0.91** 对应，整体复制能力相对稳定。应把“整个功能角色”“候选头排序”“整体任务能力”分开。这**不否定**真正高影响重复数据的干预可能改变复制能力，只否定将任意易主解读为删数据独有的效果。

**5. 未完成即未完成。** [E87/E88](experiments/E87-E88-review-checks.md)：完整 10k 步重跑于 10 月 11 日被要求中止、29 run 无结果；E88 部分 bootstrap 分析未修正。v3 正文不能借用它们作为完成的验证。

## 三、明确撤回、不应复活的解释

- **先天头编号 / “权重忘记 seed，但 head 记得”**：头置换对称性和 SeedPrints / 权重比较不支持其原宣传价值。
- **目标模型因果打分重新找到承担者，就称 source circuit 零样本迁移成功**：E75 的映射存在目标信息使用，不能提供原样跨模型搬运证据。
- **强的 Flan 模板效应就证明了模型训练出一套通用 context-trust 规则**：原 C04 已在人类审查中终止，并从主张表删除；相关旧代码或论文版本仍是历史。
- **早期行为出现后承担者锁定**：E83 的留出验证失败。
- **数据 mask 导致头换人**：完全相同 rerun 已经能产生更高比例的最强头易主。
- 过去的一维仲裁、全语料普适性等旧解释按 [CLAIMS.md](CLAIMS.md) 的作废记录保留。

## 四、为什么这次不再进一步局部优化

论文的机制单位和科学后果没有达成足够自然的连接：即使证明某个可置换 head 的具体分配方式受初始化影响，也不能自动解释模型为何更可靠、如何学习或哪些因果干预能够迁移。E81/E86 带来宝贵的测量审计与方法教训，但最近邻 Tigges、Bali、MDA 等已经解释了可比工作的一部分。按用户对科研价值的判断，不再用更多 seed、更多相似模型、旧有脚本的再包装试图挽救主旨。

## 五、原始记录与复现边界

- **最新工作稿：** [paper-acl-v3/main.tex](paper-acl-v3/main.tex)、[main.pdf](paper-acl-v3/main.pdf)、[作图程序](scripts/figs_v3.py)。v0/v1/v2 完全保留。
- **科学证据：** [CLAIMS.md](CLAIMS.md)、[experiments/](experiments/)、[results/](results/)、[logs/](logs/)、[PAIN_LOG.md](PAIN_LOG.md)；不提升旧 L1/L2 等级。
- **软件包：** [software-submission/](software-submission/) 是旧 v1 时代的独立复现包，目录数据部分与 `results/` 重复但因离线重画需求保留。
- **当前 v3 不保证纯 clone 一键重生全部图片：** `scripts/figs_v3.py` 还读取 `results/e81/`、`e83/` 的部分 raw `.npz`，而 **Git HEAD 没有任何 `.npz` 跟踪文件**。已生成 PDF、png、tex 和 JSON 保存，但缺少 raw NPZ 时有些图表无法脱离原运行缓存重新计算。见 [ASSET_INDEX.md](ASSET_INDEX.md)。
- Git 的清理不意味着校验、删除或保留了外部服务器上的 checkpoint；不擅自清理远端本地数据。

**最终人类决定：TERMINATED，不自动重新立项。**
