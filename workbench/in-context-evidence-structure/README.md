# In-Context Evidence Structure（ICES）

## 状态
- **状态：** ACTIVE-EXPLORE（2026-10-08 人决定恢复，E39–E48 已开展；此前 2026-10-06 PAUSED 为历史记录）。这是正式研究排程；不意味着别的研究方向停止。
- **2026-10-08/09 进展：** 真实数据上的后果与机制（C13，E46–E49）：多人带名字的样例混在同一上下文时，LLM 只保留每人标注倾向的 35–58%（2 个真实数据集、8 模型、4 家族）；每人独立的标签词恢复到单人水平；读标签头把另一人的标签读进答案，换词后在读出层面分隔（E48）。顺序 / 格式敏感线（E40–E45）已止损关闭。见 `PAPER_SHAPE.md` 末节。
- **2026-10-10 继续探索（人授权）：** E58–E64完成，复盘见 [`REVIEW_2026-10-10.md`](REVIEW_2026-10-10.md)。来源影响有native因果路径；Qwen的label读取很大部分发生在答案前query位置，Mistral主要在末位，不能再写“默认完全不用来源”。C14–C16均L1，尚无完整机制选择理论。10-09整理保留为历史记录。
- **E65/E66更新：** query接力有模型边界（Qwen的Label标记／Mistral的来源字段）；删direct-label无稳定accuracy修复。input前source缓存对single/mixed均失败，已见input的缓存保留logit但准确率收益有限，不能包装成新组合瓶颈。各卡与复盘已记负结果，C16仍L1。
- **E67–E70更新：** 同信息code位置改变Qwen的来源排序；prefix K的历史作用可在完全禁读label后保留。独立冻结公共key偏移将accuracy从0.543恢复至0.602，但来源排序0.828仍低于原生0.938；预测恢复不等于binding恢复。C17–C19均L1，bf16数值失败已作废，详见复盘§8。
- **E71更新：** 相同namespace下，关系码×位置的accuracy交互独立确认+10.9点；旧冻结frame迁移只35%/accuracy+3.1点，未过预设MIE。E72正在做native chat/reasoning边界；短direct预算造成截断，不算能力失败。
- **主 idea：** [`ideas/I04-output-indexed-evidence.md`](ideas/I04-output-indexed-evidence.md)
- **目标会议：** ICML / ICLR（ICL 理论与机制叙事）；备选 ACL / EMNLP（标签语义、标注者视角、非平稳 NLP 场景叙事）。
- **证据账本：** [`CLAIMS.md`](CLAIMS.md)　**实验索引：** [`experiments/INDEX.md`](experiments/INDEX.md)　**论文形态卡：** [`PAPER_SHAPE.md`](PAPER_SHAPE.md)　**日志：** [`logs/`](logs/)
- **territory 卡：** [T16](../../search/our-taste/TERRITORY_IN_CONTEXT_EVIDENCE_STRUCTURE_2026-10-05.md)　**知识库：** [`library/themes/in-context-evidence-structure/`](../../library/themes/in-context-evidence-structure/)（FIELD_MAP、KEY_PAPERS）

## 1. 研究问题
**起点（T16）：** 冻结 LLM 能不能判断上下文里的反例是“噪声”还是“规则变了”，并据此调整证据的汇总方式？
**测量工具：** exact 层级 Bayes oracle（联合推断变化率 λ 与噪声率 ε）给出一个**方向相反**的预测——在后缀反例之前加零散噪声，规范学习者应**更不**相信后缀；而任何正权重的可加汇总都会**更**相信。配合成簇检验（同样数量的反例，连成一串 vs 零散）与新旧对调检验（A→B vs B→A）。

**收敛后的问题：** 模型在什么情况下能追踪变化、在什么情况下把新旧证据混在一起——以及为什么。

## 2. 核心 idea（I04）
> **I04原始候选解释：In-context learner 按“输出”存放输入-输出证据。** 某个输出得到的支持，来自带这个输出的 demo 的、按输入相似度加权的汇总；这份汇总在时间与上下文上可交换。
> 因此：**改变“用哪些输出”的变化看得见**（标签流、格式、输出语言、换了新词的新 regime），**把已有输出重新分配给不同输入的变化看不见**（concept drift、因人而异的映射），而且新旧输出标签越相似，证据混得越多。

原候选机制（Qwen3-8B、Qwen2.5-7B）：一族晚层“读标签”注意力头从答案位置读取 demo 的标签词，按内容相似度选择、不看位置；旧 demo 的标签位置因因果掩码不可改写，新 demo 也不写入“变了”的信号；可交换汇总是这条直接读取路径的有效描述，完整query程序的充分解释已受E59–E64限制。

**解释边界（2026-10-10）：** 上述末位通路参与计算，但不是整个程序的充分解释。E59/E64检出来源名字K→query内部消息→答案的参与；source差分可跨标签迁移，但不等于完整绑定已可部署。当前追问：来源条件化在query的哪些位置形成、不同模型为何在不同阶段读取label，以及末位读取何时保留或稀释已经形成的条件规则。E64尚未证明最后一种“稀释”假说。

## 3. 证据（按主张组织；数字与 CI 见 CLAIMS 与实验卡）
| 主张 | 关键数字 | 实验 | 等级* |
|---|---|---|---|
| 输出侧变化被规范追踪 | 标签流噪声检验 13/13 模型为负；E22 格式通道 16/16；全局变换（±k、大小写↔反转）到 32B 更强 | E05/E06/E11/E16/E22 | L2 |
| 条件结构被可交换汇总 | 13 模型（0.6B–32B）噪声方向错；thinking、指令、T=64、时间戳、K=4/6、任务切换都不改变；与 set oracle r≈0.98 | E02a/E03/E07–E09/E16/E23/E25/E27 | L2 |
| 看最近邻，不看最近期 | 预测跟随“query 像哪一半 demo”，两种顺序对称（32B 差 ≤0.04） | E04/E21 | L2 |
| 同一答案内：察觉变化但不重置 | 大写标记时格式规范、映射平坦；删除影响：格式通道旧 demo 支持度为负 8/8，映射通道为正 16/16 | E22/E26 | L2 |
| 时间结构只在“偏向新输出”的成分上 | 不均衡翻转：条件成分噪声方向错 12/12（6 模型）；少数类 query 被拉错 | E28/E29 | L2 |
| 证据按输出身份分开 | 分隔阶梯：不同输出词 0.00 ≪ 输入领域 0.36–0.49 < 上下文标签 0.51–0.91 < 时间（完全合并） | E24/E30/E31/E35 | L2 |
| 泄漏 ∝ 标签语义相似度 | 14 套标签词，ρ=0.75–0.96（5 模型 × 2 任务） | E33 | L2 |
| 建设性修复：新 regime 换新词 | concept drift 变得可追踪，11/12 格（含 1.7B/2B） | E32 | L2 |
| 机制：读标签头 + 不可改写的锚点 | 逐头分解重建 r=0.9997；注意力：同类 ×2–69 ≫ 标注者 ×1.5–2.6 ≫ 位置 ≈0；因果修补：方向错误的噪声效应 = 晚层直接读噪声锚点 | E36/E37/E38 | L2 |
| 为什么（训练统计） | toy：任务同质数据复现解离，易变数据推不动；LoRA 只得到近因 | E12/E18 | L1 |

\*等级见 CLAIMS：凡已满足 L3 泛化条件（≥2 家族、≥2 任务）的主张，在独立校对前一律记为 L2。

关键图（`results/figs/`）：
- `fig_marked_drift.png`：格式跟随变化、映射不跟（E22）
- `fig_nearest_not_newest.png`：看最近邻不看最近期（E21）
- `fig_structure_selectivity.png` / `fig_regime_map.png`：跨任务 × 模型地图
- `fig_label_similarity_leakage.png`：泄漏 vs 标签语义相似度（E33）

## 4. 被实验否定的解释
表层 vs 潜在（E11b）· 单条 demo 可识别 regime（E13）· “可复制标签”（condarith）· 任务识别 vs 任务学习（E27）· 时间写进内容（E23）· 输入侧标签分流（E24）· 主效应来自相邻 token 统计（E34）· 映射与主效应由两组头承载（E36）· 新锚点是运行滤波器（E37）· “Label:” 预测位置存放运行估计（E38b）· 游程头 = 边缘通道（E28b）。详见 I04 §5 与 CLAIMS 作废记录。

## 5. 最近邻（完整定位见 I04 §6）
Wang et al. EMNLP'23（标签词锚点，机制层最近邻）· Kossen et al. ICLR'24 · Falck et al. ICML'24 · Zhao et al. ICML'21 · Xiong et al. ICLR'25（任务叠加）· Dudley ICML'26 / Qin ICLR'26（训练模型的变化检测）· Cho et al. ICLR'25 / Yang-Cho-Inoue ICLR'26（检索电路、TR/TL 头）。
**最危险的压缩：** “ICL = kNN + 标签偏置”——回应见 I04 §6。

## 6. 下一步（按信息量排序，非日程）
1. 检验E70的公共group-prior解释能否预测未参与发现的code身份/schema；区分载体组可读性、组内样例匹配与label知识。预测分数和来源排序均保留。
2. 对common×centered合作作新材料的预定验证；与Cho shortcut、Few-Shot Examples Add Up附录K、多机制binding正面对齐，避免把已有alignment或事后交互当新理论。
3. 机制预测明确后，再用少量强模型/推理模式检验程序切换；自然多标注者规则与前沿reasoning压力测试仍未完成。已有real文本采用受控来源规则。

## 7. 目录
| 路径 | 内容 |
|---|---|
| `ideas/` | I04（主 idea）、I01（早期版本） |
| `experiments/` | E00–E70 实验卡（跑前写决策表；早期 pilot 的事后补写已标注）；`INDEX.md` 为总索引 |
| `CLAIMS.md` | 主张账本 C00–C19、混杂审计、作废记录 |
| `PAPER_SHAPE.md` | 论文形态卡（I04 版）；`PAPER_OUTLINE.md` 为 10-05 旧版提纲（已被取代，保留作历史） |
| `DATA_PLAN.md` | 数据方案与实际使用的数据 |
| `PAIN_LOG.md` | 痛点与工程坑 |
| `scripts/` | 数据构造、打分、分析、机制脚本；见 [`scripts/README.md`](scripts/README.md) |
| `results/` | git 里只有汇总表（csv/json）与图；逐条打分 `*.jsonl` 与大数组只在本地 |
| `logs/` | 每日日志 `YYYY-MM-DD.md`（训练/进程日志只在本地） |

## 8. 复现与资产
- **环境：** `/home/xiang/miniconda3/envs/verl-clean`（transformers 4.57）；Qwen3.5 / Nemotron-H 用 `openslime` + `scripts/vendor`（tf 5.12，不进 git）。
- **数据：** `data/*/rows.jsonl` 由 `scripts/build_*.py` 以固定种子重建（不进 git）。自然数据集直接下载使用：SetFit/sst5、fancyzhx/ag_news、CogComp/trec、Yelp/yelp_review_full、Todd et al. FV 任务（`data/fv_tasks/`）。nonce 词库经 StepFun step-5（Step Plan 接口）逐条审计：`data/lexicon.json`（标签词 84、属性名 26）。DICES-350 原始 csv 在 `data/dices/`（未使用于结论）。
- **打分：** `scripts/run_lm.py`（左填充 + 显式 position_ids + 精确多 token log-prob）；多机排队 `scripts/run_queue2.sh HOST GPU "DATA:MODEL ..." BS`、即时启动 `scripts/launch.sh`。
- **只在本地（不进 git，NFS `/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure/`）：** 逐条 LM 打分 `results/*/*.jsonl`（约 570MB，可用 `run_lm.py` 按卡重跑）、训练/进程日志 `logs/*.log`、机制数组 `results/mech/*.npz`（逐头 DLA、锚点 value、注意力；可用 `scripts/mech_*.py` 重建）、注意力探针 `results/*/attn_*.npz`、LoRA/toy 权重 `/tmp/xiang_*`（fvcrc13 本地）。
- **算力备注：** fvcrc10/13/20 的空卡；NFS 约 40 MB/s，32B 模型首次加载需 ~25 分钟；同一张卡上的任务只放一条队列（两条队列会在交接时撞车导致 OOM）。
- **E67–E70资产：** `results/e67_e70_summary.json`、各有效`analysis/run.json`与汇总图入git；原始JSONL、token布局、`results/e70/frozen_frame/frame.npy`留上述NFS路径。冻结偏移按E70卡无query提取重建；bf16作废控制记录保留。科学确认使用独立seed/词库/label，E70为float32。
- **E65/E66资产：** `results/e65_e66_summary.json`、各有效`analysis/run.json`与E65图入git；逐query原始JSONL及token布局留NFS。E66 bf16作废输出/控制记录保留，float32有效版本按卡重建。
- **E58–E64资产：** `results/e58/`、`e59/`中的`*.npy`锚点状态与各卡`contexts.jsonl/behavior.jsonl`留在上述NFS路径，不进git；代码与固定种子可重建。小汇总`results/e58_e64_summary.json`与`analysis.json`入git。Qwen3-8B revision `b968826d9c46dd6066d109eabc6255188de91218`；Mistral-7B-v0.3 `caa1feb0e54d415e2df31207e5f4e273e33509b1`；节点NVMe `/tmp/ices_models/`由对应HF缓存snapshot复制。环境仍为conda `verl-clean`（torch2.8.0/cu128、transformers4.57.6）。

## 9. 决策记录
- **2026-10-05：** 注册为 PROPOSED（ownership audit 后选定 evidence-structure inference）。
- **2026-10-06：** 人决定 I04 为主 idea，先做机制；机制阶段完成第一轮（E36–E38）。
- **2026-10-06：** 人决定暂停推进，留作之后主推的 candidate；转去找新题。

- **2026-10-08：** 人决定恢复为 ACTIVE-EXPLORE；E39–E48 已开展，见当日日志及实验卡。此决定不构成永久关闭其他项目的依据。
