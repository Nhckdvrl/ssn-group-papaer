# 实验地基：给本地实验 agent 的数据、读数、协议、陷阱与首批高信息量实验（2026-10-12）

> 读本页前先读 [06 研究纲领](06_RESEARCH_PROGRAM_2026-10-12.md)。本页是"地基"，不是执行队列：每个实验前仍要写实验卡（R3）、预测表和决策表。本页所有数字来自[独立审查](../INDEPENDENT_REVIEW.md)可复核的路径。GPU/模型/API 资源须人授权。

## 0. 本地 agent 的职责边界
- 你负责理解问题、选择最有判别力的实验、设计读数、分析结果、追加分析，并在证据改变解释时**改写 06 的假说表**。不是执行编号。
- 每个实验只问一个"哪两个解释在此分叉"的问题；若连续两次动作只缩小成功条件而不增加解释力，停下来重读 06/08。
- 读数含义先于规模：先用固定 6–10 个输入核接口有效性（有效 final、未 cap、两 mapping 均可解析），再铺量；不按答对筛题筛模型。

## 1. 研究对象的操作化：三类题 + 对照句

| 读数 | 题型 | Gold | 它测什么 | 例 |
|---|---|---|---|---|
| R-REJ 误读拒绝 | initial 目标、源支持 No | No | 旧依赖是否被拒绝 | "Did the suspect send the file?" |
| **R-REC 替代依赖断言** | initial 目标、源支持 Yes | Yes | 替代依赖是否被建立 | "Did someone send the file to the suspect?" / "Did the protester hide himself?" |
| R-MAIN 主句事实 | final 目标 | Yes/No | 后半句是否被读到（Li 2024 式） | "Did the file deserve further investigation?"（No）/"Did the memo near completion?"（Yes） |
| 对照句 | 同题、无歧义句 | 同 | 模型是否接受该题的语义；过滤词汇知识缺失 | "The suspect who was sent the file…"；"While the protester hid, …" |

**联合模式**是主读数：每源 (REJ, REC) ∈ {拒绝∧断言=完整重建, 拒绝∧不断言=只撤回, 不拒绝∧断言=并存, 不拒绝∧不断言=未修订}。人类 Ceháková 2025 的对应是 qmis/qcor。

## 2. 现成数据（不造模板）

| 来源 | 内容 | 位置 | 备注 |
|---|---|---|---|
| D0 资格表 | 1732 题，Step-5 两遍语义层（ENTAILED/NEITHER/CONTRADICTED）、语法可接受、消歧位置 | `/data1/xiangding/work/incremental-interpretation-revision/E52/qualified-v3.jsonl`（SHA f6970dd7…） | 字段 `source_gold`、`literal_label`、`analysis_question_target` |
| E82 cohort | 892 QA/356 源/178 簇，带 `grounded_gold` | `…/E82/data-v1.jsonl` | 当前三族全部实际输出在 `…/E87/runs-v1/*/*/predictions.jsonl` |
| 替代依赖题清单 | NPZ 17（Ceháková 2025 RAT）、MVRR 16（Ceháková 2025 双宾语 15 + SAP 1） | `results/REPLACEMENT_DEPENDENCY_COHORT_2026-10-12.json`（CPU 生成） | 扩展见 §3 |
| 词义 GP | Blott 2020 48 框架/192 句 | E85 资产 | 外推用 |
| 语篇更新 | Belief-R 1744 题（人类语用 Gold） | E93 资产 | 外推用；接口须先修（E97 教训） |
| 框架提示文本 | 每源 `frame_hint`（"the verb X is a passive past participle in a relative clause"） | `…/E89/data-v1.jsonl` | 复用 |
| 源 bank/patch 代码 | E55/E64 的层级残差替换与 bank 框架 | `scripts/`（见 scripts/README）与固定提交 859e48c8 | 旧三族；新架构需重验数值仪器 |

## 3. 材料扩展（优先级顺序，全部是已发布人类材料）
1. **Ceháková & Chromý 2025 英文全集**：MV/RR 双宾语与 RAT 两类，各含 AMBCOR/AMBMIS/DISCOR/DISMIS 四题；人类数据可逐项对齐。目前库内只有部分项进入 D0，需核对原材料文件（见 cehakova2025 卡与 D0-Cehakova2025-source-audit.json）。
2. **Christianson 2001 Exp3a/3b 的 RAT 项（24 项）与 Amouyal 2025 的 24 组反身材料**：替代依赖题为"Did X wash himself?"；对照句为逗号/语序版。
3. **SAP benchmark（Huang 2024）MV/RR 24 项**：需自己写替代依赖题（"Was the X V-ed?"），这是唯一允许的新增问句，按 D0 协议两遍审计。
4. 不扩 NP/S：两句复述格式污染（H-C16）且替代依赖（补语从句）与主句事实难分；若要用 NP/S，题型改为"Did the chef remember that the recipe required…?"的单句 Yes 题并与"Did the chef remember the recipe?"配对。
目标：≥60 源、≥2 构式、每源三题+对照，Source→lexical cluster 自举。

## 4. 协议规则（从 103 卡的教训固化）
- **指令**：同时跑 PLAIN（"Read the sentence and answer the question"）与 STRICT（源支持规则）；Ministral 类 No 偏置族以 PLAIN 为主读数（H-C14）。任何"一句恢复"只作 R8 对照。
- **顺序**：句在前、问在后（CQO）为主；句后放题是 Ok & Lee 2026 的推荐侧；QOC 作为 H-C 的判别条件而非主读数。
- **读出**：实际 greedy 生成（32 token cap）为主，forced-choice LP 为辅；两 mapping（Yes/No、A/B 两序）各报并取均值；UNKNOWN/cap 单列上下界，不当 0。
- **对照过滤**：替代依赖题先在对照句上测；对照 <75% 的题记"词汇/题义未被该模型接受"，单列不入主图（H-C15）。
- **统计**：Source→lexical cluster 10k bootstrap，95% CI；候选/映射/assignment 不是独立样本；CI 含 0 不等于无现象，CI 正不等于重要。
- **标注**：只对新生成文本做语义标注；双遍+裁决；两句复述格式不用于 NP/S；"something/this"类未绑定单独类别（E107 五类保留）。
- **接口预检**（E93 教训）：固定 6 源×全部条件×两 mapping，要求 stopped∧valid∧parseable 才铺量；预检与 Gold 无关。
- **记录**：每条输出存 prompt SHA、token ids、文本、解析状态；每实验存 config/模型 revision/dtype；不覆盖旧 map。

## 5. 首批高信息量实验（设计到可写卡；不排日程）

### X1 替代依赖三读数 × 结构信息来源（行为；≈3 GPU·h/族）
- 条件：NATIVE；EARLY 框架提示（句前）；LATE 框架提示（句后）；STRUCT-EXAMPLE（给一个与本句实体无关的同结构示例句"The nurse who was handed the chart left."，不含答案）；QOCO（句–题–句重复）；对照句。
- 读数：R-REJ、R-REC、R-MAIN 实际作答；联合模式；对照过滤。
- 预测表：
  - H-A：NATIVE 下 REC≈0、REJ 高；EARLY 对 Gemma 升 REC、对 Qwen 不升；STRUCT-EXAMPLE 对 Qwen 若也不升→Qwen 的失败是"不能在 GP 上下文应用框架"。
  - H-B：STRUCT-EXAMPLE 或 QOCO 使 REC 升且 REJ 不变。
  - H-C：QOCO 与 LATE 优于 NATIVE，且题后置优于题前置。
  - H-D：对照句上 REC 也低（过滤后不应出现）。
- 停止规则：若 60 源上 Qwen/Gemma NATIVE REC ≥ 对照一半，06 §7 第一条触发。

### X2 动词位置状态移植到替代依赖题（白盒；≈2 GPU·h/族）
- 复用 E64 bank 框架：donor=对照句（"who was sent"）主动词 token 各层残差；recipient=GP 句同词位置；对照：歧义名词位置移植、self 移植、无关句移植。
- 读数：R-REC 与 R-REJ 的变化，及 R-MAIN 是否受损。
- 预测：H-A/重实例化在动词→动词位置有效、名词位置无效；H-B→无效而 REJ 有效（与 E55 一致）；都有效→整残差太粗，须细分 K/V（E84 方法）。
- 仪器：新架构（Qwen3.8 混合 GDN、Gemma4 共享 KV）先过 E64 式数值一致性检查；通不过则只做行为 X1。

### X3 构式/材料协变量预测（CPU + 已有输出）
- 用 Zhou 2026 的句法信念更新量（可用现成依存解析器近似）和 Paape 2026 的人类重分析成功率，预测每源的 REC；若人类成功率高的 MV/RR 在模型最低，是"方向相反"的可发表对比。

### X4 外推：词义 GP 与语篇更新（在 X1 结果明确后）
- Blott 2020：替代词义的断言题 vs 旧词义拒绝题；Belief-R：先修接口（简短答案格式）再测"保持 vs 更新"的联合模式。预测：若两阶段分离在非句法材料也出现，纲领上升为一般"晚到证据"现象。

### X5 可选：复述通道（仅在 X1 后）
- 单句改写（非两句）读取替代依赖是否被自由表达；对应 Patson/Lee & Shin；用于 H-B 的"不问就说"检验。

## 6. 陷阱清单（每张卡自检）
1. 把 initial/final 当撤回/建立（P16）。2. Gold No 当字面否定（H-C1）。3. Ministral strict No 偏置（H-C14）。4. NPZ 反身题词义成分未用对照过滤（H-C15）。5. 两句复述拆 that（H-C16）。6. 整残差 patch 命名为语法变量（H-C11）。7. 候选/映射当独立 n（F06）。8. 未预检接口就铺量（E93）。9. 决策表写了不照做（审查§7）。10. 三族一致当门槛，或单族显著当规律。

## 7. 与旧资产的接口
- 旧三族（Qwen3-8B/Gemma3-12B/Llama3.1-8B）结果作为历史对照，不与当前三族混图。
- E87/E89 的全部实际输出可直接 POST-HOC 做 X1 的 NATIVE/EARLY/LATE 三格（已做 MVRR 子集，见审查§2.3），只缺 STRUCT-EXAMPLE、QOCO 与扩展材料。
- 旧 patch 代码在固定提交；新架构需重写 hook 并通过数值检查。
