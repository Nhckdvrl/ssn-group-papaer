# 主题 2：结项后的找补——分工可重现性、损伤修复、遗忘可逆性（E89–E119）

**状态：** 2026-10-17 人决定“没什么有意思就停”，按事先写好的收尾标准结束。均未成文。卡片上残留的 RUNNING 是停止时未更新的状态。详见 [../HISTORY.md](../HISTORY.md) §5–§6。

## 阶段四：分工的跨种子可重现性（E89–E92、E95）
- **起因：** 导师 10-16 当面关心的是“编号变了，分工是否相似”，旧论文没有回答。
- **E89（最有用的结果）：** 410M 10 个种子、160M 15 个模型、DataDecide-1B 12 个模型、9 个任务的头级消融图谱。任务深度顺序跨种子重现（τ 0.72）；任务共享结构部分重现（0.73，满分 0.95，打乱 0.35）；“哪些任务共用关键头”8 / 8 一致；逐头对应几乎对不上。搁置原因：缺少“一致到什么程度才有意义”的基线。
- **E90–E92：** 追异常种子的 loss spike 与种子间能力差异，人指出被结果牵着走，叫停。
- **E95：** 发现 PolyPythias-410M seed3 / seed4 在训练中途被重置回初始化（→ [../../suite-audits/](../../suite-audits/README.md)），“spike 改写分工”框架作废。

| 卡 | 问题 |
|---|---|
| [E89](experiments/E89-division-of-labour-atlas.md) | 重新训练后，头之间的“分工”是否重现？——以置换不变的多任务因果图谱来测 |
| [E90](experiments/E90-outlier-trajectories.md) | 训练失稳的两个异常种子，分工是“从未长成”还是“长成后被改写”？——以及共用关系是同时出现还是后来招募 |
| [E91](experiments/E91-spike-origin-heads.md) | 预训练 loss spike 从哪个头开始？——单点瓶颈的 previous-token 头是不是起点 |
| [E92](experiments/E92-capability-atlas-seeds.md) | 同一配置、不同种子的预训练，为什么有的学会某项能力、有的学不会？——PolyPythias 全种群能力图谱 |
| [E95](experiments/E95-polypythias-reset-audit.md) | PolyPythias 410M seed3 / seed4 的“loss spike”其实是训练中途被重置回初始化（审计，2026-10-16） |

## 阶段五：损伤修复、遗忘可逆性、吸引子（E93–E119，主要在 Pythia-160M）
- **写出接口的对准决定角色能否回来：** 只重置读取（QK）而保留输出时，原头和整个旧配置会长回来；把输出旋转一下（大小不变）就等于完整重置（160M 6 / 6、410M 2 / 2）。回归程度随对准度线性变化，没有临界点；回不来主要是被已耦合的替补抢先。
- **损失恢复 ≠ 能力恢复：** IOI 停在 0.40，损失照样恢复。
- **遗忘的路线规律：** 落在读取侧的删除比落在写出侧的更容易被良性训练撤回；方向在两个任务、两种遗忘方法、两个尺寸上一致，强度依赖方法与尺寸；机制只部分解释。
- **落空：** “原分工是有边界的吸引子”（E119：线性渐变，无边界）。
- **为什么不够：** 相对 Frankle 2020、Lubana 2023、Rushing & Nanda 2024、Hu 2025 是组件层面的细化。

| 卡 | 问题 |
|---|---|
| [E93](experiments/E93-lesion-recovery-pilot.md) | 预训练中途受损后，能恢复什么？——受控损伤 + 匹配对照继续训练的校准 pilot |
| [E94](experiments/E94-benign-vs-malignant-damage.md) | 什么样的训练中途损伤不可恢复？——损伤几何 × 幅度 × 时间 |
| [E96](experiments/E96-role-reassignment.md) | 训练中一个头靠什么保住 / 夺回自己的角色？——QK、OV、空缺的拆分 |
| [E97](experiments/E97-who-takes-over.md) | 损伤一个功能的第一承担头之后，谁接管？——事先预测检验“富者愈富” |
| [E98](experiments/E98-capability-vs-loss-recovery.md) | 损伤后损失很快恢复，能力为什么没跟上？——“慢”还是“卡住” |
| [E99](experiments/E99-where-role-memory-lives.md) | 受损头长回原角色，记忆存在哪里——它自己保留的 OV，还是下游读它的头？ |
| [E100](experiments/E100-de-novo-recruitment-vs-age.md) | 训练早一些的模型，能不能从头招募新的承担者？ |
| [E101](experiments/E101-coupling-law-on-ioi.md) | “残留耦合”规律在 IOI 名字移动头 8.9 上是否成立 |
| [E102](experiments/E102-coupling-law-across-functions.md) | 耦合规律在另外四个功能上是否成立——事先预测 |
| [E103](experiments/E103-regrowth-lag-coupling-gain.md) | 受损头长回来之前为什么要停滞 700–1000 步？——耦合强度决定停滞长度 |
| [E104](experiments/E104-coupling-law-at-410m.md) | 耦合规律在 Pythia-410M 上是否成立 |
| [E105](experiments/E105-unlearning-bridge.md) | 把“角色存于接口”接到真实的遗忘 / 重学问题上 |
| [E106](experiments/E106-frozen-surgery.md) | 网络其余部分冻结时，完整重置的头能否长回原角色？ |
| [E107](experiments/E107-dormancy-lock.md) | 联合训练中进入休眠的头会被锁死吗？——更高学习率、更长窗口下冻结 vs 联合 |
| [E108](experiments/E108-where-unlearning-lives.md) | 遗忘在功能上落在哪里？——注意力模式修补分解 |
| [E109](experiments/E109-capital-unlearning.md) | 读取侧 / 写出侧的不对称，在事实回忆与定向重学攻击下是否成立 |
| [E110](experiments/E110-general-data-pullback.md) | 为什么一般训练会撤回读取侧的遗忘、却不撤回写出侧的遗忘？ |
| [E111](experiments/E111-footprint-breadth.md) | 读取侧遗忘是否在一般文本上大范围扭曲注意力？ |
| [E112](experiments/E112-footprint-regularized-unlearning.md) | 把读取侧遗忘的足迹压窄，它还会被良性训练撤回吗？——足迹机制的因果检验 |
| [E113](experiments/E113-added-behavior-retention.md) | 后加的行为（玩具“拒答”）在良性训练下能否保留——读取侧 vs 写出侧 |
| [E114](experiments/E114-information-availability.md) | 遗忘后任务信息是否还在？——信息存留假说 |
| [E115](experiments/E115-who-carries-recovery.md) | 良性重学后，恢复的功能由谁承担？——“绕过”的执行者 |
| [E116](experiments/E116-format-preserving-unlearning.md) | 保住上游特征的原格式，写出侧遗忘会变得可被良性训练撤回吗？——格式机制的因果检验 |
| [E117](experiments/E117-unlearning-asymmetry-410m.md) | 读取侧 / 写出侧的良性重学不对称在 410M 上是否成立 |
| [E118](experiments/E118-npo-asymmetry.md) | 换一种遗忘方法（NPO），读取侧 / 写出侧的良性重学不对称是否仍成立 |
| [E119](experiments/E119-attractor-basin.md) | 原有分工是继续训练的吸引子吗？——写出接口的连续扰动与吸引域边界 |

## 代码与结果
与主题 1 共用 [../scripts/](../scripts/)（`e89_labor.py`、`e93_lesion.py`、`e105_unlearn.py` 等）与 [../results/](../results/)。
