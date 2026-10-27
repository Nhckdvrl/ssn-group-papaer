# E155 独立 CPU 复算（C14/P32）

- 三状态 raw accuracy（P/A/B）：native 0.3750/0.4141/0.3906；R-zero 0.1797/0.1953/0.2266；S-zero 0.3203/0.3359/0.2031；both-zero 0.1953/0.1797/0.1719。
- accuracy 的 R×S 对比 P/A/B 分别 0.0703 [−0.0156,0.1563]、0.0625 [−0.0313,0.1484]、0.1328 [0.0156,0.2500]；choice CE 的相同对比为 2.0924 [0.7355,3.6554]、3.2740 [1.5653,5.0684]、4.1137 [1.8369,6.7048]。
- 全部 P/A/B × 四条件的 raw/per-char accuracy、四选项 CE、正确答案 token NLL、首 token KL，及相对 native、R×S、A−P/B−P/B−A 配对比较均列在 report.json；accuracy 相对 native 使用干预减 native，方向与作者 accuracy drop 相反。
- 128 题含两个固定学科各 64 题；每统计均以 seed 155001 从学科 0 后学科 1 各重采样 1000 次，等权 macro，CI 是配对题目区间，不是模型种子或学科总体区间。
- 与作者 summary 165 项点值和 CI 端点最大差 1.67e−16；三份 raw 的 SHA256 与各自 manifest 一致。A/B native 的 128×4 候选 LL 与 E153 的 AAAA/BBBB full 逐项精确相等，输入标签和长度也相同。
- 检查 driver：轴顺序为 native、routed_zero、shared_zero、all_moe_zero；R-zero 保留 D+S，S-zero 保留 D+R，联合零化保留 D。R×S 是指标上的差分对比，不是知识的分摊比例；固定两个学科和预训练模型不能推出种子总体或训练形成机制。
- 本次仅 CPU 读既有 raw、manifest、summary 与实现；没有运行模型或更改主实验、旧结果与主张等级。可复算脚本及完整结果在同目录。
- POST-HOC 共同成功子集仅按 P/A/B native 全答对选定，共 44 题（生物 36、数学 8）；两科等权配对 bootstrap，seed 155101。shared-zero 正确率 B−P=−0.3681 [−0.5974,−0.0970]，B−A=−0.3403 [−0.5347,−0.1736]；routed-zero 对应 +0.0417 [−0.1458,0.2292]、+0.1389 [−0.1111,0.3682]。
- 这是看完全矩阵后提出的条件分析，不是独立确认，不能替代全样本；native 全正确的条件排除了干预纠错。各条件的正确率、翻转率、分科计数及区间见 common_success_posthoc.json。
- E155 依赖形态独立复算入口为 dependency_patterns_review.py，结果及作者表对照见 dependency_patterns_review.json；重跑报告 SHA256 不变。
