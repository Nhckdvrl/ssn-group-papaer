# 证据地图（投稿正本 10-13 版）

数字全部取自 `paper/main.tex` / `paper/appendix.tex`（来源：`paper/figures/numbers.json`，由 `scripts/paper_figures_v2.py` 从确认批次计算）。回复里引用数字时以本表为准，引用位置写“Section X / Appendix Y / Table Z”（不能写链接）。

## 设定（Section 2，Appendix A–D）
- 两个来源 A、B，各 8 条 demo，随机交错，8 个 query（4 正 4 负）；格式 `Comment: / Annotator: / Label:`。
- 约定（convention）= 哪个标签词表示正类；same / opposite 两个世界；shared（都用 no/yes）vs separate（B 用 pass/flag）。比较时 A 的 demo、位置与 query 全部固定，只改 B。
- 8 个冻结模型：Qwen3 8/14/32B（post-trained hybrid）、Mistral-7B-v0.3、Llama-3.1 8/70B（base）、Gemma-2 2/9B；无 chat 模板、FP32、eager 注意力；所有层所有头统一干预，不挑层或头。
- 数据：SST-5 两极（训练集作 demo，测试集作 query）、模板化餐厅评论（单方面 / 双方面）、Measuring Hate Speech（规则为构造，不是原标注者规则）。
- 统计：每个实验在 16 个开发 prompt 上固定条件与分析，再在 32 个新 prompt 上只跑一次；按 prompt 做 10,000 次 bootstrap；所有运行过的条件都报告；事后分析在附录注明。算力约 115 GPU 小时。

## 主张 1：只限制读取隔离不了来源（Section 3，Fig 2，Appendix E）
| 内容 | 数字 | 位置 |
|---|---|---|
| query 读两方时 B 约定的拉力 | 1.0–2.9 nats | §3、Fig 2、Table app-leak |
| A-only 读取仍有拉力 | 0.14–1.50 nats，8/8 模型 | §3、Fig 2 |
| 准确率后果（冲突 − 一致，A-only） | 7.4、1.2（CI 跨 0）、7.4、7.4、2.3、5.9 点（Q8/Q14/Q32/M7/L8/L70）；Qwen3-14B 与两个 Gemma 未到准确率 | §3、App E（事后计算，已注明） |
| 同类内交换（只动文本不动关联）对照 | −0.21–0.10 nats，CI 全部含 0 | §3、Table app-leak |
| 换词（B 用 pass/flag） | −0.03–0.04 nats；逐 query 幅度 0.11–0.41，与同类交换对照（0.09–0.32）同级，共享词时 0.17–1.58 | §3、Table app-flip |
| 是否共享而非用哪套词 | 两方都用 pass/flag：0.39–1.01；A 用 pass/flag、B 用 no/yes：0.04–0.10 | §3、Table app-swap（App I） |
| 受控评论 | 0.74–1.71 nats | Table 1 |
| MHS 文本 | Qwen3-8B 17.6%（12.1–23.8）答案改变，平均幅度 0.73 nats | App E |
| 规模（同一批 prompt） | 8B→32B：0.65→1.50；8B→70B：0.57→0.96 | §3、Table app-leak-matched |
| 实验卡 / 结果 | E123、E131、E133、E132（换词组合）、E90/E91/E116（MHS） | `results/e123`、`e131`、`e132`、`e90`、`e91`、`e116` |

## 主张 2：答案→标签路径（Section 4，Fig 3，Table 1，Appendix F、I）
| 内容 | 数字 | 位置 |
|---|---|---|
| 只换 key 的无参数预测（A-only） | r = 0.92–0.95（6 模型），Qwen3-32B 0.82、Gemma-2-2B 0.80 | §4.1、Fig 3 |
| 读两方时 K+V 预测 | r = 0.92–0.99（7 模型），Llama-3.1-70B 0.72 | §4.1、Table app-recon |
| 不取约定差时的 KV 相关 | 0.79–0.96（Llama-70B 0.62） | App F |
| MHS | KV r = 0.985 / 0.977（Qwen3-8B / Mistral），K-only 0.969 / 0.966 | §4.1、App F |
| 原生前向删除路径（A-only，受控评论） | 减少 0.19–0.89 nats，占 35–94%，8/8 模型 | §4.2、Table 1 |
| SST-5 上双向阻断 | 去掉 62–93% | §4.2、Fig 2 绿色 |
| 只保留该路径 | 0.12–0.73 nats（全效应的 1/4 到 2/3） | Table 1 |
| 分层 | 主要在第二个四分之一层，最后四分之一无作用（6 模型） | §4.2、Table app-bands |
| 特异性对照：阻断 A 对自己答案的注意 | 不减少，7/8 模型反而增加 0.12–0.68 | §4.2、Table app-op-gate |
| 传递的是关联（跨类交换 − 同类交换） | 受控：0.62（0.45–0.81）/ 0.40（0.31–0.50）nats（Q8 / M7）；SST-5：0.03–0.49，8/8 | §4.3、Table app-assoc |
| 关联的带符号作用随家族不同 | Qwen、Mistral、Gemma 为正，两个 Llama 为负 | §4.3 |
| 共享词时 A 标签位置更多注意 B 的答案 | +0.3–2.3 个百分点注意力 | §6、Table app-attention |
| 实验卡 / 结果 | E108、E109、E112、E120、E121、E131、E132；关联 E111、E113–E115 | `results/e120`、`e121`、`e131`、`e132`、`e111`、`e113`–`e115` |

## 主张 3：同样的跨来源形成也在分开规则（Section 5，Table 2，Fig 4–5，Appendix G–H）
| 内容 | 数字 | 位置 |
|---|---|---|
| 原生准确率（共享词，SST-5） | 81.3–89.9% | Table 2 |
| 选择性阻断 | +2.5 – +10.4 点，8/8；7/8 两个来源分别都提升；冲突世界 +5.9 – +20.9（例：Llama-70B 77.3→98.2%） | §5、Table 2、Table app-pol-delta |
| 完全隔离 | −6.1 – −15.2 点；一致世界 94–100%，冲突世界 51–53%（机会水平）；配合 A-only 读取 93–99% | §5、Fig 4a、Table app-pol-other |
| A-only 读取 | −0.4（Q8，CI 跨 0）– +16.7（L8） | Table 2 |
| 一句指令 | −0.6 – +6.2；选择性阻断比指令高 2.1–8.3（仅 Qwen3-32B CI 含 0） | Table 2、App G |
| 单来源 prompt 上限 | 94.8–99.3%；选择性阻断弥合 1/4（Gemma-2B）到 96%（Llama-70B）的差距 | §5 |
| 换词下的完全隔离 | 限定本来源两个词时 94–99%，实际回答 52–56%（42–47% 用了对方的词） | §5、Fig 4c、Table app-sep |
| 重新开放名字注意力（从完全隔离出发） | 冲突世界 49–53% → 67–88%（5/8 高于原生）；换词全词表 50–56% → 82–96% | §5、Fig 4b–c、Table app-edges |
| 重新开放评论或答案 | 52–62% | §5、Table app-edges |
| 只阻断对方答案作为发送者 | 冲突世界 68–92%、换词 87–98%（6 模型） | App I |
| 双方面评论上的选择性阻断 | +2.8 – +7.4 点（4 模型），优于完全隔离 | §5、Table app-dual |
| 公共“来源—标签词”表 | 只给 demo 读：+26.7 / +7.7 / +8.3（Q8/M7/L8，相对无关名字表）；只给 query 读：≤ 0.8，CI 含 0 | §5、Fig 5、Table app-schema |
| 交换表 | +14.9 / +3.3（Q8/M7），弱于正确表 | §5、App H |
| 共同编码 | 同一次编码的缓存组合优于混合：+23.5 / +9.1 / +6.5 / +21.4（Q8/M7/L8/Q14，换词） | App H、Table app-coherent |
| 实验卡 / 结果 | E122、E123、E131（政策）；E132（边类型、换词组合、分层、注意力）；E124–E126（公共信息） | `results/e122`、`e123`、`e131`、`e132`、`e124`–`e126` |

## 附录中的补充（可用于回答“只是约定吗”）
- 标准（criterion）vs 约定：Qwen3-14B 归一化行列式原生 0.41（0.33–0.49），A-only 0.19（0.07–0.31）；答案消息只部分预测标准效应（r = 0.67）——路径传递关联，但不是完整的标准相关响应（App J，E117–E119）。
- query 前的来源线索不承载来源特定标准（App K，E129、E130）。

## 论文自己承认的限定（Limitations）
- 规则是我们在真实 / 模板评论上指定的约定与方面标准，真实标注者的规则可能同时在多方面不同。
- 全部是二分类，两个来源，每方 8 条 demo。
- 干预作用于所有头，识别的是路径与层，不是单个头。
- 8 个模型训练配方不同，跨规模比较只描述这些 checkpoint。
