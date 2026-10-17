# LIBERO-Para — 2026 VLA 语义鲁棒性

- 主源<https://arxiv.org/abs/2603.28301>；作者<https://github.com/cau-hai-lab/LIBERO-Para> pin86cfb7b9d214bdc8d7bb4e2e96a4834a37244eec。作者README称EMNLP2026 Main，官方Anthology未独立核验。
- 已读对象/动作双轴taxonomy、主表、§6 failure分类、Appendix D.3 threshold/GT控制。源码metrics/analyze_results.py PRIDE加权口径；未运行机器人任务。
- **DOCUMENTED：** 4092等义改写episode、7VLA配置，执行成功随措辞改变下降；用成功EEF轨迹均值作pseudo-GT，DTW near/far区分motor/planning，改变max/p99/p95/p90阈值也检查。远离pseudo-GT不能直接证明内部规划错，但作者有多阈值支持。
- **RECONSTRUCTED：** canonical高成功掩盖等义指令过拟合→独立变对象/动作、诊断轨迹级失误。重排序/同义导致实际行动退化已有人研究。
- **对我们/未排除：** E26仅NPC扩展的资格，不是首次semantic fragility。NPC允许多种目标相容策略，不照搬单一轨迹距离当人格gold；尚未核完整generation/eval脚本与人审数据。
