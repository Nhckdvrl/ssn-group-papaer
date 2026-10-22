# 矿区D结果导航

本目录仅存轻量表、样本ID/hash、报告、审阅和科学图；完整第三方原文、冻结prompt/raw/token IDs、vendor与权重留在[仓库外资产](../ASSETS.md)。数字性质和完成状态以下表及对应run metadata为准。

| 要找什么 | 入口 | 范围/状态 |
|---|---|---|
| 首夜实测总论 | [D-OVERNIGHT-REPORT](D-OVERNIGHT-REPORT-2026-10-22.md) | D-E01–05历史交付；其Monte S解释受后续源纠正限制 |
| 当前连续实测总论 | [D-CONTINUATION-REPORT](D-CONTINUATION-REPORT-2026-10-22.md) | D-E06–08全部完成；不含预算停止的D-E09 |
| ArcANE阶段表演 | [D-E01](D-E01-REPORT.md)、[表](D-E01-summary.json) | 64完整probe/205phase，原生量表；不是准确率 |
| LongEvo文本状态 | [D-E02](D-E02-REPORT.md)、[内容表](D-E02-summary.json)、[来源句预测](D-E02-likelihood.json) | 64问题四条件；来源预测与人物质量分开 |
| 普通摘要/容量旧记录 | [D-E03](D-E03-REPORT.md) | **原六作品S比较无效；旧raw/表/图保留历史** |
| EW来源资格 | [文件间对照与时间边界](D-EW-SOURCE-QUALIFICATION-2026-10-22.md) | 冻结训练文件与单独场景文件的ID不通用；不认证全库原著时序；D-E06同文件绑定保留 |
| 源错误与修复 | [D-SOURCE-CORRECTION](D-SOURCE-CORRECTION-2026-10-22.md) | Monte14内部单元误换117文学章；已修正，当前有效S见D-E07 |
| 单步状态与强参照 | [D-E04](D-E04-REPORT.md)、[D-E05](D-E05-REPORT.md) | 通用两Qwen＋Step Plan；发布flag、PUF、人工事实审阅分别报告 |
| 连续状态消费 | [Qwen8表](D-E06-qwen3_8b-summary.json)、[专用8B表](D-E06-arcane_8b_dpo-summary.json)、[32B表](D-E06-qwen3_32b-summary.json) | 29角色/8作品；跨消费者绝对NLL不排榜 |
| 同信息人物整理 | [D-E07表](D-E07-summary.json)、[D-E08表](D-E08-summary.json) | 同25probe/81phase，Monte已纠源；Step整理仅两个8B消费者 |
| 连续/整理实际案例 | [D-E06 CASEBOOK](D-E06-CASEBOOK.md)、[D-E07/08 CASEBOOK](D-E07-CASEBOOK.md) | 成功、失败、可接受多解及来源边界；非独立人评 |
| 完整前缀预算停止 | [D-E09报告](D-E09-REPORT.md)、[覆盖](D-E09-COVERAGE.json) | 225尝试、208/301提交态，0演员/评分；没有APF/PTF结果 |
| 人物适应学习资料 | [全量连接与作品划分](D-ADAPTATION-VIEWS.json) | 24,977更新、22,306发布顺序接续；输入/监督/未来任务分开，无模型调用 |
| 原生学习输入预算 | [token库存](D-ADAPTATION-TRAIN-BUDGET.json)、[持久归档](D-ADAPTATION-PREPARATION-MANIFEST.json) | 14,079训练条目共42,949,543 tokens；未截断、未训练 |
| 学习基线与后续互动 | [D-E10运行页](D-E10-RUN-REPORT.md)、[进度快照](D-E10-progress.json)、[训练缓存](D-E10-training-data.json)、[评测选择](D-E10-selection.json) | 两条真实SFT训练和七系统互动路径运行中；6作品47经历87context，尚无训练后质量结论 |
| 原生生成互动 | [D-E11选择](D-E11-selection.json)、[实验卡](../experiments/D-E11-native-character-interaction-rollouts.md) | 六个官方OOD作品起点，三路径×最多3场景；首次生成受GPU争用中断，队列等空闲，SFT等最终完整检查点，尚无成长结论 |
| 学习基线阶段案例 | [D-E10 CASEBOOK](D-E10-CASEBOOK.md) | 全部12预选人物已审阅五条普通/发布参照，含第一条完整base读数及评委理由校对；不是训练后最终对比 |
| 成本与次数 | [首夜账](D-RUN-LEDGER.json)、[D-E06–08账](D-CONTINUATION-RUN-LEDGER.json) | 本地生成/前向/API分账；D-E09不计入完成账 |
| 补充互动发布资产 | [MiniMax库存](D-MINIMAX-ASSET-INVENTORY.json) | 95种子/3,135发布轨迹及评分；结构核验，无本轮生成/重评分 |
| 全量连续经历索引 | [D-EXPERIENCE-INDEX](D-EXPERIENCE-INDEX.json) | 138,596原任务全部字节/元数据核验；跨任务与同人物下次出场连接，无新生成/心理标签 |
| 来源与归档 | [首夜校验](D-INTEGRITY.json)、[首夜清单](D-RAW-MANIFEST.json)、[续测持久清单](D-CONTINUATION-RAW-MANIFEST.json) | 首夜原包保留；续测372文件逐成员SHA已核验，部分run仍标部分 |

`*-selection.json`是冻结样本与来源；`*-summary.json`是聚合及逐项评分记录；`*-summary-strict.json`只作严格格式敏感性分析；`*-CASEBOOK.md`为执行agent审阅；`figures/`保存图及导出PDF。早期`D-E06-progress.json`是当时进度快照，当前结论使用完整三消费者summary和续测报告。

当前科学问题和下一步优先级见[POSITIONING](../POSITIONING.md)，baseline身份见[BASELINES](../BASELINES.md)，离线复算入口见[脚本导航](../scripts/README.md)。没有因为某个结果文件新增，就自动升级CLAIMS或启动后续模型实验。

完整驻留的记录总数见[D-RESIDENCY-TOTALS](D-RESIDENCY-TOTALS.json)；其中D-E09为预算停止，不能将所有计算条数等同已完成实验样本。
