# E03：有效生成学习已建立，尚无新论文现象

三条件同一英语监督/recipe、A100、adaptation seed17，所有四预算点、1190英德对及固定一句恢复对照完成。
官方F1/EM从原始答案重新计算，来源/顺序/hash/配置/硬件校对通过；完整LM与tokenizer保存。

| 条件 | EN F1 | DE F1 | EN EM | DE EM |
|---|---:|---:|---:|---:|
| FWB | 75.60 | 63.37 | 63.36 | 48.74 |
| MWB | 74.68 | 62.54 | 63.11 | 48.15 |
| MWB+P | 74.35 | 63.53 | 62.35 | 48.74 |

终点DE F1 contrast，context-cluster 95%CI（pp）：MWB−FWB **−0.83 [−2.75,1.10]**；
+P−MWB **+0.98 [−1.21,3.21]**；+P−FWB **+0.15 [−2.08,2.37]**。
这是单adaptation seed、单pretraining family/seed，item/context CI不是训练seed方差，跨零不证明等价。
不能将这些小差异写成大现象、纯alignment解释或一般reasoning结论。

统一的一句“Copy a short answer from the context.”未带来大恢复；DE F1差为
FWB−0.20、MWB−1.26、+P−0.49pp。MWB固定指令反而有下降，clusterCI[−2.36,−0.19]，
cap从4至12；如实保留，不改主模板或以此单独孵化prompt小信号。
主终点三条件overflow/empty均0，cap2/4/1；训练是真实生成式阅读理解，不是冻结likelihood。

全曲线：[轻量结果](e03_train_analysis_seed17.json)、[可视化](qa_learning_curves.png)。
主源码冻结为 `734798ad6dbad41c23897f64c2e4ab984d701c7da2752f1a04fd9354f82032f9`。
原始答案和完整生成式权重：`artifacts/qa_learning/train_{condition}_seed17/`。

每条件监督input/answer token完全相同：3,588,633 /114,159。
计时字段baseline/MWB/+P为1932.02/1940.27/1930.61秒，**只含主协议训练与评测，
不含后续instruction对照、初始化与权重保存**；保存171.19/139.90/171.38秒另计。
峰值allocated27.95GiB（精确30,012,406,272 bytes）。不能把这些字段冒称完整作业GPU时账。

接续动作：E04在同起点完整LM学习上实际操纵任务内容覆盖/条件连接；
E06测QA适配后的翻译保留与固定恢复，E05已经证实强translate-train监督资产可用。
这些仍是发现性训练决策实验，不是已建立novelty，不升级C##或L2。
