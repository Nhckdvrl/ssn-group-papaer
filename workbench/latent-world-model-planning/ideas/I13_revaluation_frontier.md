# I13｜Selective Revaluation：环境或任务变化后，究竟重学哪一层？

- **状态：** SEED，未获得本地实验证据。
- **对应：** R2，兼 R3/R5。
- **来源：** S5长期预测结构、S21 successor/revaluation背景、S19 test-time adaptation。
- **问题：** reward/goal变化、局部transition变化和更广dynamics shift需要更新的模型部分不同。能否只更新“真正失效的层”，比full retrain或统一TTT更快恢复并少遗忘？
- **实验入口：** E19。
- **研究边界：** reward vs transition revaluation是经典问题；“局部变化所以局部更新”也不能直接当贡献。价值必须来自modern compact visual WM上的模块更新方法与recovery evidence。

## 候选模块

以可实际改造的LeWM-family为例，把可更新对象粗分：

1. **TASK/COST**：goal/reward/task head；
2. **SHORT DYNAMICS**：一步/短步predictor；
3. **LONG-HORIZON**：multi-step / reachability / successor-like head；
4. **REPRESENTATION**：encoder/latent；
5. **FULL**：全部更新。

不同shift假设：
- 只换goal/reward：优先TASK/COST；
- 门/障碍/局部transition变化：SHORT DYNAMICS +必要的LONG-HORIZON；
- action scale/friction等全局dynamics：SHORT/LONG甚至representation；
- planner/query变化：可能只需scorer/proposal，不应重学world dynamics。

## 方法假设

先不用复杂router。用少量post-shift transitions计算每个module的local residual/gradient norm/validation improvement，选择最小更新集；也可按固定规则比较。

若实验表明“shift type → minimal sufficient update set”稳定，再考虑一个**selective revaluation controller**，根据可观察shift signatures分配更新。

## 最重要的读数

- 达到原性能90%所需post-shift samples / gradient steps / wall-clock；
- old-task retention；
- no-shift update damage；
- planner success而非只看prediction loss；
- update参数量与部署成本。

与I08互补：I08研究运行时如何分预测计算；I13研究世界/任务变化后如何分**学习计算**。
