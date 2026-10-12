# E109：替代依赖三读数 × 结构信息来源（2026-10-12，PLANNED）

- **状态：** PLANNED（未运行；生成器编号E431已按惯例改为下一空号E109。GPU/模型资源须人授权后才能运行。）
- **类型：** PILOT（I09 的决定性实验）
- **对应：** I09；C06/C09；P16/P19；更正 H-C14–H-C17。设计与预测表见 [knowledge/07 §5 X1](../knowledge/07_EXPERIMENT_FOUNDATION.md)。
- **问题（一句话）：** 读完 GP 句后，模型能否断言语法要求的替代依赖（R-REC），还是只能拒绝误读（R-REJ）；显式结构信息在哪些族、以何种形式能让 R-REC 成立？
- **设置：**
  - 材料：`results/REPLACEMENT_DEPENDENCY_COHORT_2026-10-12.json` 的 49 个 GP 源（MVRR 25、NPZ 24，Ceháková 2025 + SAP 1），每源 R-REJ/R-REC/R-MAIN 三题 + 对照句同题；扩展按 07 §3（Christianson 2001 RAT 24、Amouyal 2025 反身 24、SAP MVRR 24 补题，新增问句须两遍 Step-5 审计）。目标 ≥60 源。Step-5 标 NEITHER 的 10 道替代依赖题单列。
  - 模型：Qwen3.8-27B、Gemma4-31B-it；Ministral3-14B 仅 PLAIN 规则且单列（H-C14）。native 非 thinking 入口，greedy，32 token cap，BF16，两 mapping。
  - 条件（每源每题）：NATIVE；EARLY_FRAME；LATE_FRAME（复用 E89 `frame_hint`）；STRUCT_EXAMPLE（一个与本句实体无关的同结构示例句，不含答案，如 "The nurse who was handed the chart left early."）；QOCO（句–题–句重复）；CONTROL（对照句）。指令 PLAIN 与 STRICT 各一套。
  - n：≈60 源 × 3 题 × 6 条件 × 2 指令 × 2 mapping × 2 族 ≈ 8640 实际输出；≤3 GPU·h/族。
  - 命令/代码：复用 `E82/runs-v1/*/current_open_baseline.py` 的生成与解析路径；新增条件模板与对照过滤。
- **读数：** 每题实际答案正确率（下界/上界，UNKNOWN 单列）；每源联合模式 (REJ,REC)∈{完整重建, 只撤回, 并存, 未修订}；对照过滤后主图；Source→lexical cluster 10k bootstrap。主对比：NATIVE 下 REC 对照 vs GP；各条件 − NATIVE 的 REC 与 REJ 变化；族 × 条件交互。
- **阳性对照：** 对照句 REC ≥75%（过滤门槛）；E87 已有 NATIVE/E89 已有 EARLY/LATE 三格可先 POST-HOC 复算核对接口一致（审查 §2.2/§2.3 已给 MVRR 子集：Qwen 0/32 vs 81.2%，Gemma 26/32 EARLY）；固定 6 源 × 全条件 × 两 mapping 预检 stopped∧valid∧parseable。
- **噪声地板 + MIE：** 两 mapping 差；同布局重复 LP/greedy 一致；≥15pp 且 CI 不含 0 作为"改变解释"的 heuristic，不作自动判决。
- **混杂审计：** 已控制：对照句语义接受（过滤）、指令偏置（PLAIN/STRICT 同报）、顺序（CQO 主、QOCO 条件）、mapping。未控制：提示带来的通用"仔细读"效应（STRUCT_EXAMPLE 与 EARLY 比较部分分离）；thinking 入口（本实验不开，留作后续）；新架构数值仪器不涉及（纯行为）。
- **决策表（跑之前写）：**
  - NATIVE REC≈0、REJ 高，EARLY 对 Gemma 升、对 Qwen 不升，STRUCT_EXAMPLE 对 Qwen 也不升 → H-A（重建缺失，且 Qwen 不能在 GP 上下文应用框架）；下一做 E110（X2 动词位置状态移植）。
  - STRUCT_EXAMPLE 或 QOCO 使 REC 升且 REJ 不变 → H-B/H-C（有而不用 / 架构固定）；下一做题位置与重复的最小干预分解，并比较双向架构。
  - 扩展后 NATIVE REC ≥ 对照一半 → 现象是小样本效应；I09 降级，回 06 §7。
  - 对照句 REC 也低（过滤后仍大量）→ H-D 词汇框架知识；改材料不改机制故事。
  - 族 × 构式异质 → 保留地图，按构式分别写预测，不拼统一规律。
- **算力预算：** ≤6 GPU·h（两族）+ Ministral PLAIN ≤2 GPU·h；Step-5 审计仅用于新增问句（≈72 题 × 2 遍）。**实际：** 未运行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
- 数字（含 CI / 种子方差）：
- 结果文件：`results/...`
- 按决策表执行了什么：
- 主张变化：
- POST-HOC 分析：
