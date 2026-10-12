# E133：把核心链扩展到第四个模型家族 Gemma-2（2026-10-13）

- **状态：** RUNNING（跑前写定）
- **对应：** 论文 §3–§5 的主图和主表。模型家族从 3 个扩展到 4 个（用户 2026-10-13 提议），Gemma-2 也是 Contextualize-then-Aggregate 使用的模型家族。
- **问题：** 在第四个家族上，以下现象与操作是否同样成立：共享标签词时的跨来源泄漏、answer→label 路径（重建、原生阻断与恢复）、选择性阻断与完全隔离的对比、名字边的作用？

## 设置

- **模型：** `google/gemma-2-9b` base，revision `33c193028431c2fde6c6e51f29e6f17b60cbfac6`。FP32、eager attention、权重冻结、不用 chat template。
- **引擎：** 原样复用 E120、E121、E123、E132 的引擎，材料、种子、条件、读数、分析都与其他模型完全相同。

**为 Gemma 做的两处改动（不影响已跑过的模型）**

1. Gemma 需要 BOS。`scripts/run_gemma.py` 只在以共享 header 开头的编码前加 BOS token。示例块、标签词、query 的编码保持不变，所有 token 边界只整体平移一位。
2. E121、E119 中对原生 attention 的调用改为关键字传参，并加入 gemma2 分支。Gemma-2 的参数顺序是 dropout 在 scaling 之前；Qwen3、Mistral、Llama 的签名都接受这种关键字调用，数值上与原来完全一样。

**运行**

- discovery n16：E120 seed 120001、E121 seed 121001、E123 seed 123001、E132 seed 132001。
- confirmation n32：seed 120101、121101、123101、132101。
- discovery 与 confirmation 同时启动，读数是跑前冻结的。

## 冻结读数

与各引擎原有的读数相同；不新增，也不删除。

## 决策

结果全部写入主图主表（第七个 checkpoint），弱结果和反向结果照实报告。
