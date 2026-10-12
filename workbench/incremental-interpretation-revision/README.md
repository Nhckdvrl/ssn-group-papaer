# Incremental Interpretation & Revision

**更新：2026-10-12。当前工作是重新建立研究判断、审计证据和修复执行，不是把旧探索强行写成论文。**

## 当前入口

| 要做什么 | 入口 |
|---|---|
| 理解两轮探索在哪里偏离、哪些代码/解释需纠正 | [科学审计](AUDIT_2026-10-12.md) |
| 建立整体科学认知、深读论文、检索全部文献与动态维护结论 | [认知中枢](knowledge/README.md) → [领域总图](knowledge/00_STATE_OF_THE_FIELD.md) → [七领域文献图谱](knowledge/PAPER_ATLAS.md) → [深层专题](knowledge/topics/05_HOW_IDEAS_GROW.md) |
| 重新选择问题和高信息量实验，而非自动接着跑 E108 | [研究综合](knowledge/RESEARCH_SYNTHESIS_2026-10-12.md) |
| 按新流程自主研究 | [执行说明](EXECUTION_BRIEF.md)、[本地 Agent 约定](AGENTS.md) |
| 查全部103张现存实验卡的方向、结果、边界 | [探索记录](EXPLORATION_RECORD.md)、[原机器库存](results/EXPLORATION_INVENTORY_2026-10-08.json) |
| 恢复原始统计、脚本版本和结果 | [结果说明](results/README.md)、[资产清单](results/ANALYSIS_ASSETS.json)、[脚本说明](scripts/README.md) |

## 研究问题与证据状态

我们关心后来证据如何改变先前解释，尤其是**撤回旧关系、建立替代依赖、在其他用途使用它**之间的联系。它们必须分别测量；这项区分本身并不是新的贡献。真正有价值的是解释在哪些条件下这些操作分离、为什么，以及能否预测未参与设计的错误与成功。

历史正式状态保持：PROPOSED baseline residency；I01 PARKED、I02 PILOT、I03–I08 SEED；C06–C08 L0、C09限定问答因果测量L1。尚无被认证为合格的论文 idea。本次维护没有代替人升降这些状态。

已知最重要的边界：E29删除原GP源后效应仍在，E43/E44不支持普通场景的普遍角色反向；E98不支持当前三族共同的问答收益/意义损失悖论；E103的角色类别改善被E107收紧，不能叫完整新依赖恢复；E105反对“候选更多必然更错”。这些反证与正结果同等重要。

**新的审计补充：** E93预检只验证重复性，未验证有效最终答案，代码已加入不依赖Gold的双模式预检；E107的保守差值下界不等于两个边际下界相减，旧数字不应误改；前后缀likelihood分解不是神经机制证据。详见审计。

## 知识库位置与阅读身份

原外围主题目录的149份文献/索引资产已迁入本目录 **knowledge/**，原README留作 LEGACY_README。保留原文献卡、版本与局限，不把迁移计作重新精读。外围只留兼容导航。新独立原文复核、思想来源重建和未核范围记录在 [原文复核](knowledge/PRIMARY_SOURCE_REVIEW_2026-10-12.md)。

## 资产、运行与权限

历史完整数据/输出/逐token分数/标注原包位于原机器 `/data1/xiangding/work/incremental-interpretation-revision/`，本次未访问现场。大结果JSON中的 externalized 指针不是统计数组；恢复按原资产清单和固定提交 `859e48c87cfbecaf017c0fd8e286ef18f59a61cd`。

2026-10-08的GPU释放与模型权重删除见 [资源交接](RESOURCE_RELEASE_2026-10-08.md)，不是当前可用资源证明。本次没有模型推理/训练/新标注调用，E108仍仅准备。恢复GPU与下载需新资源授权；现有知识库与代码不触发运行队列。

## 审计覆盖与验证

103是实际卡片数，不是独立发现数；原库存含96测量结束、4部分完成、2含不可用模型、1未运行。此次覆盖全库存/探索记录及关键结果的交叉审查；代码实读为5个完整文件和一个共享估计器的前65行，**不是全部126个科学脚本逐行审核，更不是103次原始数据独立复算**。

CPU回归测试：`python -m unittest discover -s workbench/incremental-interpretation-revision/tests -v`。14项通过；[验证记录](audit/CPU_VERIFICATION_2026-10-12.json)含源代码校验和及范围。全部实验卡、原结果、idea卡和旧日志保留；[文件索引](FILE_INDEX.md)说明历史入口。
