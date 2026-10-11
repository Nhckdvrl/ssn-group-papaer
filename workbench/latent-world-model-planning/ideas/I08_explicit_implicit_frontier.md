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


## 第一实现优先用同一Fast-LeWM的两级成本

为了避免“Fast-LeWM和LeWM谁才是高保真”这个不必要问题，Stage A先定义：

- **cheap fidelity：** Fast-LeWM direct terminal prefix prediction + goal cost；
- **refined fidelity：** 同一个Fast-LeWM额外计算decomposed/intermediate-prefix terminal estimate，并使用原论文self-consistency信息。

原论文把refined/self-consistency信号均匀用于candidate；本seed只对可能改变elite set的候选支付额外调用。这样第一实验无需新checkpoint，也没有跨latent空间的raw cost比较问题。

如果这一轴有效，再把refined fidelity换成LeWM recursive、multi-step head或DeepJEPA，测试principle是否超出Fast-LeWM内部技巧。


## Elite-set sufficiency：一个可以支撑方法的结构性事实

CEM 对下一轮 proposal distribution 的更新只消费 elite candidate actions，而不是所有 candidate 的精确 cost。令 full high-fidelity evaluator 的 elite set 为 \(E\)，selective method 恢复的 elite set为 \(\hat E\)，两者大小都为 \(K\)。如果 \(E=\hat E\)，那么在相同 sampled candidate bank 下，**CEM 的下一轮 mean / population-variance update完全相同**；非elite candidate 的high-fidelity cost可以完全不知道。

更一般地，若每个action-sequence向量 \(x_i\) 满足 \(\|x_i\|_2\le B\)，且两elite sets各错换 \(r\) 个candidate（对称差大小为 \(2r\)），则均值更新有直接界：
\[
\|\mu_E-\mu_{\hat E}\|_2 \le \frac{2rB}{K}.
\]
对二阶矩阵同理有 \(O(rB^2/K)\) 的扰动；协方差更新也因此随elite mismatch比例增长。这个推导很简单，**当前只作为待形式化/单元测试的设计依据，不登记为已证明论文定理**。

这使H-B的目标从“近似所有high-fidelity costs”转成更贴合planner的任务：

> **用尽可能少的 refined evaluations 保住 high-fidelity elite set。**

因此 offline candidate-bank 的第一指标应是 elite recall / symmetric-difference，而不是全体candidate的MSE或Spearman。若这个接口成立，后续理论与算法都围绕elite-membership uncertainty自然生长。