# 结果与完整资产

`results/`保存小统计、来源/配置、关键结果与资产指针。完整原始输入、逐条输出、LP、Step请求/响应、失败和历史版本继续在 `/data1/xiangding/work/incremental-interpretation-revision/`；本次没有重新标注或删除这些科学资产。

## 清理了什么

2026-10-08将43份逐条CSV与71份超过256KiB的统计原样外置，共114份、170527001bytes。JSON原文件名留下明确的`externalized: true`指针，CSV从当前Git工作树移除；[资产清单](ANALYSIS_ASSETS.json)逐份记录`repository_path`、`local_original`、大小、SHA256、固定Git历史链接。没有压缩，没有改统计数字，也没有重写Git历史。

原统计在已有 `analysis-originals-2026-10-06/`（核对SHA完全一致后复用）或新 `analysis-originals-2026-10-08/` 中。机器分析必须使用`local_original`；JSON指针只有元数据，不能当作含有`panels`的科学结果。GitHub上的历史链接可恢复当时完整文件。

每项研究的主要数字、CI和限制保留在[逐次探索记录](../EXPLORATION_RECORD.md)、原实验卡和[总结](../EXPLORATION_SUMMARY.md)。较大的“summary”包含完整panel，不等于无用垃圾；外置是为缩小仓库，不是删除研究结果。

## 恢复与验证

固定清理前提交：`859e48c87cfbecaf017c0fd8e286ef18f59a61cd`。例如查看历史文件：

```bash
git show 859e48c87cfbecaf017c0fd8e286ef18f59a61cd:workbench/incremental-interpretation-revision/results/E50-summary.json
```

使用本机原始文件前，按资产清单验证大小与SHA256。若机器不可访问，使用清单的固定GitHub链接或上述Git对象；完整raw数据另依source manifest和固定revision恢复。不要下载模型来阅读结果。

## 完成度和版本

[探索库存](EXPLORATION_INVENTORY_2026-10-08.json)覆盖103张实际存在的卡：逐卡记录科学完成度、数字与解释边界、卡SHA、结果文件、代码引用和外置map的路径/SHA。原E01/E11/E51/E53保留PARTIAL；E97/E100保留未执行模型；E108仅准备。

最终map与INTERIM、语义更正前/后的map分开；文件存在不等于结论有效。E70/E91/E92定点语义更正、E63/E64 role-v2、E87解析范围与E107新依赖维度均不覆盖旧图。E107同时保存严格explicit和合理implicit支持，不能把自然隐式表达自动算错。
