# Mechanism Population Dynamics

**状态（2026-10-27，持续执行）：** E144–E157完成并可复核。成熟历史改变同题任务依赖；R_B可单独降低受限答案NLL .188177，保留P背景又使完整回插损伤降低.055469。当前将职责落实到事实实体/属性区别的路径中介，代码/CPU预检中，尚无E158成熟数据。成熟资产阶段无新训练。当前证据持续维护在[MoE说明](moe/README.md)。头线仍CLOSED，其他ACTIVE分配不变。

这个工作台前后做了三件事，外加一个副产品。按时间顺序分成四块，每块有自己的说明页：

| # | 主题 | 时间 | 实验 | 状态 | 从这里读 |
|---|---|---|---|---|---|
| 1 | **最初的研究：头的分工从哪里来、能否跨训练对应**（含四版论文） | 09-30 – 10-11 | E01–E88 | 结项 | [heads/1-original/](heads/1-original/README.md) |
| 2 | **结项后的找补：分工可重现性、损伤修复、遗忘可逆性** | 10-15 – 10-17 | E89–E119 | 停止 | [heads/2-after-closure/](heads/2-after-closure/README.md) |
| 3 | **MoE：任务、学习历史与专家职责的可组合性** | 10-23 – 持续 | E144–E157完成；E158实现中；E143备选 | 用户授权持续执行 | [moe/](moe/README.md) |
| 4 | 副产品：公开模型套件的数据完整性问题（已对外提交） | 10-03 – 10-25 | — | 完成 | [suite-audits/](suite-audits/README.md) |

主题 1、2 共用一套代码和结果目录，总的来龙去脉与“为什么反复不够好”的诊断在 [heads/HISTORY.md](heads/HISTORY.md)。

## 一句话结论
1. **头：** 层内由哪个头担任角色跟随初始化，不跟随语料；分配在训练早期形成；抽象的分工结构（任务深度顺序、哪些任务共用关键头）跨种子重现，具体是哪个头不重现。对象（头的编号）本身是坐标，so what 回答不了，结项。
2. **找补：** 写出接口的对准决定一个头的角色能否回来；遗忘落在读取侧比写出侧更容易被良性训练撤回。都是组件层面的细化，不足以改变同行认知，停止。
3. **MoE：** 固定gate重组有真实预测代价，Γ分组未胜过gate-only强对照；短程原生历史响应不等于配套断裂。成熟原生终点则显示整MoE互换平均+.127787 NLL，且受限计算收益不能只随router移植，routed/shared/dense配套参与。当前识别给定接口的可重用边界，不宣称唯一语义单位或形成必要性。见[当前证据与判断](moe/README.md)。
4. **审计：** 五个公开套件问题，三个已在 Hugging Face 提交，两个已有他人报告。

## 目录
```
README.md            本页
CLAIMS.md            主张账本（MoE 与头分两节）
PAIN_LOG.md          踩过的坑与实测缺口（P01–P31）
logs/                每日记录（不分主题，按日期）
knowledge/           共享：论文卡（PAPER_CATALOG.md）、方法教训、概念综述
heads/               主题 1、2
  HISTORY.md         研究总档（五个阶段、诊断、教训）
  1-original/        E01–E88 实验卡、四版论文 papers/
  2-after-closure/   E89–E119 实验卡
  scripts/  results/ 共用代码与结果（按 eNN 命名）
moe/                 主题 3：README、RESEARCH_DIRECTION.md、experiments/、scripts/、results/、notes/（历史讨论与审计）、ASSETS.md
suite-audits/        主题 4：报告原文、提交链接、核查数据
```

## 资产提醒
- 大文件不进 Git。本地缓存 `~/mechpop_cache`：OLMoE 四个检查点、MoE 实验的检查点与数组（清单见 [moe/ASSETS.md](moe/ASSETS.md)）。头线的 Pythia 检查点与 Pile 分词数据已不在。
- 2026-10-26 整理：按主题分目录；删除运行日志、作业清单、冒烟测试、过期的文件清单，以及人 10-10 决定放弃的 Flan 支线（E25–E34、E47–E50、E53、E65、E76）的结果与专用脚本。删掉的已跟踪文件可从 Git 历史恢复。
