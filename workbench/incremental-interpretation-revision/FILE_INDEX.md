# 文件索引（2026-10-08整理）

## 建议阅读顺序

1. [README](README.md)：当前状态、资源、关键结论和人的授权。
2. [探索总结](EXPLORATION_SUMMARY.md)：研究对象怎样变化、真实成果、失败原因与保留的问题。
3. [逐次探索记录](EXPLORATION_RECORD.md)：103张实际实验卡逐项的方向、结果、边界和完成度；包含部分完成和未执行准备。
4. [CLAIMS](CLAIMS.md)与[PAIN_LOG](PAIN_LOG.md)：主张证据等级、作废/更正、具体测量问题。
5. [领域地图](../../library/themes/incremental-language-processing/FIELD_MAP.md)、[主文阅读索引](../../library/themes/incremental-language-processing/REVISION_READING_INDEX.md)、[文献综合](../../library/themes/incremental-language-processing/REVISION_RESEARCH_SYNTHESIS.md)：谱系、idea来源、近邻距离与已读范围。
6. [结果资产](results/README.md)及[脚本入口](scripts/README.md)：完整数据、结果、历史代码在哪里，哪些仍可直接使用。

## 每次探索怎样查

`experiments/`保留全部原卡、事前设计、事后分析和勘误；`ideas/`保留I01–I08各次研究问题；`logs/`保留当时理解和动作。目录没有重新编号。E02、E56–58、E61–62没有实验卡，不伪造补齐。

[机器库存](results/EXPLORATION_INVENTORY_2026-10-08.json)逐卡记录方向/结果/边界、科学完成度、卡片SHA、结果文件、代码与外置终图入口。E01/E11/E51/E53是PARTIAL；E97/E100有UNAVAILABLE模型；E108只有准备，不能算已运行。

| 方向 | 卡片范围 | 总结里的关键区别 |
|---|---|---|
| 旧基线、顺序与任务语义 | E00–12（无E02） | 仪器问题与能力证据 |
| 自然后文、患者与事件 | E13–24 | 续写偏好与真实关系错误 |
| 事件范围、迁移与历史 | E25–42 | 先解释后修订与首次角色约束 |
| 自然迁移、frame与输出格式 | E43–51 | 普通场景反证、人工框架/格式限制 |
| 新广面与源支持定义 | E52/53/59 | 原No任务、世界真值、自由角色 |
| 可见性、源替换与消费路径 | E54/55/60/63/64 | 因果入口与完整语法机制 |
| 目标、共同关系与多版本 | E65–75 | 问答收益与可复用解释 |
| 草稿、可靠性、逆向证据与K/V | E76–84 | 方法收益、信息移除与真正修订 |
| 当前模型、词义与论元框架 | E82/85–90 | 旧关系撤回与新依赖建立 |
| 观察重建credit与真实候选 | E91–107 | 产生好候选、选择好候选、少承诺 |
| 未执行自由belief准备 | E108 | 仅CPU准备，GPU/API/下载0 |

## 结果与代码

- [ANALYSIS_ASSETS](results/ANALYSIS_ASSETS.json)：114份大统计/CSV的原样外置路径、bytes、SHA及固定Git历史链接；141个退役脚本的原SHA与恢复提交；201个一次性/缓存文件删除清单。数据不压缩、不重标、不删除科学失败。
- [results/README](results/README.md)：解释JSON资产指针和CSV外置；分析时使用原文件，不能把指针当统计图。
- [scripts/README](scripts/README.md)：保留的126个科学/分析/共享脚本及依赖；历史等待器、补丁、旧流程与画图脚本从当前工作树退役，可在固定提交恢复。
- [资源释放](RESOURCE_RELEASE_2026-10-08.md)：GPU、模型权重与本地空间实际交接记录。
- 外置根目录：`/data1/xiangding/work/incremental-interpretation-revision/`。大数据、完整模型输出、LP、审计原包、失败、论文和run源码快照均保留。

## 历史理解与决定

- [E00–51总结](PROGRESS_SUMMARY_2026-10-06.md)和[旧路线诊断](DIAGNOSIS_AND_REDIRECTION_2026-10-06.md)：第一轮研究对象漂移与失败。
- [22:25重新对齐](REASSESSMENT_2026-10-07_2225.md)、[23:55以后重新对齐](REASSESSMENT_2026-10-07_2355.md)：第二轮各节点预测与后续纠正。里面的“下一步/在途”是历史记录，当前结论以README和探索总结为准。
- [EXECUTION_BRIEF](EXECUTION_BRIEF.md)、[ROUTE](ROUTE.md)、[DATA_PLAN](DATA_PLAN.md)：原授权、设计空间、护栏和数据/Step Plan约束；整理没有自行改线状态。
