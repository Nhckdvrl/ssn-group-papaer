# In-Context Evidence Structure（ICES）

## 状态
- **论文已投 ARR，进入 rebuttal 准备（2026-11-24）。** 投稿正本为 10-13 定稿的 [`paper/main.tex`](paper/main.tex) + [`paper/appendix.tex`](paper/appendix.tex)（PDF：[`paper/main.pdf`](paper/main.pdf)，正文 8 页 + Limitations + 附录 A–L）。仓库里没有投稿编号与轮次记录，待补。
- **标题：** *Whose Rule Is It Anyway? Shared Labels Mix and Names Separate Source-Specific Rules in In-Context Learning*
- **arXiv 版：** 11-03 生成去匿名版（作者 Xiang Ding、Tiancheng Xing），[`paper/arxiv/main.pdf`](paper/arxiv/main.pdf)，由 `paper/make_arxiv.sh` 从投稿正本派生；是否已上传 arXiv 未记录。
- **Rebuttal（2026-11-25 收到意见）：** 补充实验 E134–E136 已完成（6 模型），回复草稿在本地 `paper/rebuttal/responses/`（不进 git）；见 [`logs/2026-11-25.md`](logs/2026-11-25.md)。
- **登记表状态：** ACTIVE-EXPLORE（正式状态由人决定）。旧的逐日状态记录见 [`logs/status-history.md`](logs/status-history.md)。

## 1. 论文的问题
多个来源（例如标注者）的样例放进同一个提示、用同一套标签词但规则不同时，模型要按指定来源的规则回答。已有机制研究认为任务信息存在 demo 的标签位置、由 query 读取，由此推出：只让 query 读指定来源的 demo，就能隔离它的规则。论文问：**处理多来源提示的计算怎样把各来源的规则混在一起，又怎样把它们分开？** 方法是把计算分成**形成**（处理提示时 demo 状态的计算）与**读取**（query 读这些状态），在 8 个冻结模型（Qwen3 8/14/32B、Mistral-7B、Llama-3.1 8/70B、Gemma-2 2/9B）上删除注意力边。

## 2. 三项发现（数字均为论文正文）
1. **只限制读取隔离不了来源。** query 只能读 A 时，B 的规则仍使 A 的预测偏移 0.14–1.50 nats（8/8 模型）；5 个模型的准确率随之改变 2.3–7.4 点。B 换成另一套标签词时偏移消失（−0.03–0.04）；关键是“是否共用标签词”，而不是“用哪套词”。
2. **规则经由“答案→标签”路径混入。** A 的标签位置在形成时注意 B 之前的答案 token。只替换这些消息的 key 就能预测换词效应（系数为 1、无拟合参数，r = 0.92–0.95，6 个模型；Qwen3-32B 0.82、Gemma-2-2B 0.80）；在原生前向中删掉这条路径，效应减少 35–94%；只保留这条路径，仍有 0.12–0.73 nats。这些消息传递的是 B 的输入—标签关联，而不只是词。
3. **同样的跨来源形成也在分开规则。** 完全隔离两个来源后，冲突规则下准确率掉到机会水平（51–53%），尽管各自规则仍然学会了（只读本来源时 93–99%）；只重新开放“看对方名字”的注意力即可恢复大部分区分（67–88%）。只阻断答案→标签路径（选择性阻断）在 8/8 模型提升准确率 2.5–10.4 点；公共的“来源—标签词表”只有在形成阶段可见时才有用（+26.7/+7.7/+8.3 点）。

## 3. 论文各部分 → 实验与结果
| 论文位置 | 内容 | 实验卡 | 结果目录（本地） |
|---|---|---|---|
| §3、Fig 2 | A-only 读取下 B 规则的偏移、换词、同类内交换对照 | E123、E131（32B/70B）、E133（Gemma） | `results/e123`（含 gemma 子目录）、`e131`、`e132`（换词组合） |
| §3、附录 E | MHS 文本、17.6% 答案改变、规模趋势 | E90、E91、E116 | `results/e90`、`e91`、`e116` |
| §4.1、Fig 3 | key 修补的无参数预测 | E108、E109、E112、E121、E131 | `results/e121`、`e131/*mechanism` |
| §4.2、Table 1 | 原生前向中删除 / 只保留路径；分层 | E120、E131、E132 | `results/e120`、`e131/*native`、`e132` |
| §4.3 | 路径传递关联（跨类交换 vs 同类交换） | E111、E113–E115、E121 | `results/e111`、`e113`–`e115` |
| §5、Table 2、Fig 4a | 选择性阻断 / 完全隔离 / A-only / 指令 | E122、E123、E131 | `results/e122`、`e123`、`e131/*function` |
| §5、Fig 4b–c | 名字 / 评论 / 答案注意力的重新开放 | E132 | `results/e132` |
| §5、Fig 5 | 公共标签词表在形成 vs 读取阶段 | E124–E126 | `results/e124`–`e126` |
| 附录 J–K | 标准（criterion）vs 约定；query 前来源线索 | E117–E119、E127–E130 | `results/e117`–`e119`、`e127`–`e130` |

图与正文全部数字由 [`scripts/paper_figures_v2.py`](scripts/paper_figures_v2.py) 从上述结果目录直接计算，写入 `paper/figures/numbers.json`。实验卡见 [`experiments/`](experiments/)，主张账本见 [`CLAIMS.md`](CLAIMS.md)（C21–C24 对应论文主线）。

## 4. 论文之外、可在 rebuttal 中调用的已有证据
| 证据 | 内容 | 位置 |
|---|---|---|
| 真实标注者后果（C13） | Measuring Hate Speech、GoEmotions 真实个人标注，8 模型 4 家族：带名字混放时每人的标注倾向只保留 35–58%，每人独立标签词恢复到单人水平 | E46–E49 |
| 推理模型 | Qwen3.5-27B thinking 在同材料上 63/64 正确（4 context 诊断，非普遍结论）；8B thinking 时私人规则仍改变 A 约 16–20% | E92、E93 |
| 显式标准与提示 | thinking 能说出标准，但混放下私人规则仍泄漏；自述标准后 Own-only 提升 | E95–E99 |
| 早期行为地图 | 同一输出空间里的规则变化（concept drift）不被追踪、输出侧变化被追踪；13 模型 0.6B–32B；语义相似度定律 ρ=0.75–0.96 | E02a–E38、[`ideas/I04-output-indexed-evidence.md`](ideas/I04-output-indexed-evidence.md) |
| 负结果 | 顺序 / 格式线止损（E40–E45）；E98 轨迹运输未过阳性；E86 结果未确认 | 各实验卡 |

## 5. 目录
| 路径 | 内容 |
|---|---|
| `paper/` | 投稿正本（LaTeX）、图、表、arXiv 版、构建脚本；[`paper/README.md`](paper/README.md) |
| `paper/rebuttal/` | rebuttal 准备 |
| `software-submission/`、`software-submission.zip` | 匿名代码补充材料（投稿附件） |
| `experiments/` | 实验卡 E00–E133；早期部分索引见 `experiments/INDEX.md` |
| `ideas/` | idea 卡（I04 为论文前身） |
| `CLAIMS.md`、`PAPER_SHAPE.md` | 主张账本、论文形态卡（含历史版本） |
| `RESEARCH_SYNTHESIS_2026-10-10.md`、`PAPER_ALIGNMENT_2026-10-12.md` | 研究综合与论文—证据对齐（历史） |
| `PAPER_DRAFT.md`、`PAPER_APPENDIX.md` | 旧 Markdown 稿，已被 `paper/` 取代；仍是附录表格的转写来源和 manuscript_claim_audit 的审计对象，保留（10-05 的 “Nearest, not newest” 旧提纲 11-24 删除，见 git 历史） |
| `scripts/` | 数据构造、打分、干预与图表脚本；[`scripts/README.md`](scripts/README.md) |
| `logs/` | 每日日志、状态历史 |
| `参考图示例/` | Figure 1 设计参考图 |

## 6. 复现
- 环境：`/home/xiang/miniconda3/envs/verl-clean`（PyTorch 2.8.0、Transformers 4.57.6），FP32、eager 注意力；模型版本见论文附录 A。
- 数据：SST-5 两极（SetFit/sst5）、Measuring Hate Speech（CC BY 4.0）、模板化餐厅评论（脚本生成）；`data/*/rows.jsonl` 由构造脚本按固定种子重建，不进 git。
- 结果：逐条打分与大数组只在本地（NFS 本目录 `results/`），git 里只保留汇总与图。
- 论文：`python scripts/paper_figures_v2.py` 后 `sh paper/build.sh`；arXiv 版 `sh paper/make_arxiv.sh`。

## 7. 决策记录
- 2026-10-05 注册；10-06 暂停为主推候选储备；10-08 人决定恢复为 ACTIVE-EXPLORE。
- 2026-10-12/13 论文按 ARR 格式重写并定稿（新标题、8 模型、E132/E133 补充、模拟审稿后修订）。
- 2026-11-03 生成去匿名 arXiv 版。
- 2026-11-24 人确认进入 rebuttal 准备；README 改为论文入口，旧状态记录移至 `logs/status-history.md`。
