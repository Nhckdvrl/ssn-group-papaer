# I08｜Planner-Stage Multi-Fidelity：把高保真预测花在会影响搜索的候选上

- **状态：** SEED，未获得本地实验证据。
- **对应：** R2，见[研究计划](../RESEARCH_PLAN.md) H-B。
- **来源：** S7多步/explicit-implicit design space；S8 Fast-LeWM；S9 DeepJEPA；S13 UHM/Jumpy。
- **问题：** CEM要评估大量candidate，但只有少量会进入elite set。能否用cheap direct/prefix predictor高召回筛选，再只对有机会改变elite selection的候选调用recursive/refined/high-fidelity predictor，在固定wall-clock下提高规划质量？
- **实验入口：** E13。
- **边界：** Fast-LeWM已拥有parallel prefix prediction；DeepJEPA已拥有transition-level adaptive depth。这里研究的是**candidate-population / planner-stage fidelity allocation**，不是把两者重新命名。

## 第一版方法

不用先训练新架构：
1. Fast-LeWM/cheap head给N个candidate全部打分；
2. 取top-M（M>K elite，保证screening recall空间），或取靠近elite cutoff/低margin的candidate；
3. LeWM/open-loop multi-step/high-fidelity predictor只重评这M个；
4. CEM elite与distribution update依据重评结果；
5. 比较相同wall-clock/model-call预算的pure cheap、pure expensive与random-refine。

如果现成checkpoint已显示明确compute-quality优势，再训练**shared encoder + cheap direct head + high-fidelity recursive/refinement head**，并学习“谁要升级保真度”的confidence。

## 关键科学问题

不是简单“cascade更快”，而是：
- cheap score对high-fidelity elite的recall多高？
- 哪些环境/规划阶段发生screening failure？
- elite boundary附近的high-fidelity correction是否比随机深算更值钱？
- 增加cheap candidates与增加high-fidelity evaluations的边际收益如何分配？

DeepJEPA若代码可用，最强组合是`Fast screen → DeepJEPA refine`；其“transition内部深度”与本seed“candidate集合保真度”可直接测试是否互补。
