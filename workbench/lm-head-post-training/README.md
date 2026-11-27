# Understanding the LM Head in LLM Post-Training

## 状态（中文进度页）

**状态：** PROPOSED（用户 2026-11-26 要求开始做；是否登记为 ACTIVE、是否随问题改名，由人决定）
**目标会议 / 截稿：** 待定（ACL / ICML / ICLR / NeurIPS；不投 Findings）　**上次人审：** 2026-11-27（第三轮 GPT/Gemini 反馈后，用户放行 E07）
**当前问题（一句话）：** 后训练模型在 Base 拿不准的位置做出的选择，在什么条件下对推理结果有可测影响——与只是去掉采样随机性相比。
**讨论材料：** [DISCUSSION.md](DISCUSSION.md)（唯一一份，只写上次讨论以来的实验、数据和结论）。

### 问题是怎么演变的

1. **LM Head 阶段（11-26，E01–E02）：** 头部梯度几何与权重变化不区分后训练范式；RLVR 阶段几乎不动头。原问题得到负结果（C01–C06）。
2. **输出行为阶段（11-27，E04–E06）：** 转向“后训练在下一 token 分布上改变了什么”。MATH-500 上增益集中在 Base 高熵的分叉位置；Base 按 T=1 采样时，分叉处的随机性代价大于“谁的首选”；单个分叉上改选测不出价值；OLMo RL-Zero 的大部分差距是回答开头的模式选择（C07–C14）。正反分叉交换近作已有。
3. **条件阶段（11-27 晚，E07）：** Base 改用近作的截尾采样（T=0.6/top-p 0.95）后，分叉处的选择效应在易题上 ≈0（+1.3），在 MATH Level 5 上 +14.0，难题上 Post 首选补上差距的 70%；OlympiadBench 上方向一致、幅度减半（+7.3，补 38%）（C15）。

### 当前状态

- **已完成：** E01、E02、E04、E05、E06、E07（Qwen）。
- **运行中：** 无。
- **未做：** E03（冻结头训练，暂缓）；OLMo-3 RL-Zero 上的 E07（可行但慢，见 E07 卡）。
- **算力：** 11-26 约 1.5 GPU·时；11-27 E04–E06 约 25 GPU·时，E07 约 23 GPU·时。

## 目录

| 位置 | 内容 |
|---|---|
| `README.md` | 本页：状态、目录、决策记录、资产位置 |
| `DISCUSSION.md` | 当前一轮的讨论材料 |
| `CLAIMS.md` | 主张账本 C01–C15、作废与更正记录 |
| `PAIN_LOG.md` | 痛点 P01–P08 |
| `RELATED_WORK.md` | 文献地图与精读核对（含近邻对照表） |
| `MENTOR_REQUIREMENTS.md` | 导师标准与本项目执行要求 |
| `RESEARCH_PLAN.md` | 历史：LM Head 阶段的技术指南（E01–E03） |
| `ideas/` | I01–I05 idea 卡 |
| `experiments/` | E01–E07 实验卡（设计、决策表、偏差、结果） |
| `scripts/` | 全部代码，索引见 [scripts/README.md](scripts/README.md) |
| `results/e0{1,2,4,5,7}/` | 进 git 的小型汇总（JSON/JSONL）；E06 的汇总在 `results/e04/hybrid_qwen.json` |
| `data/` | 输入清单（只存索引与 sha1） |
| `logs/` | 每日会话记录 |

## 必读顺序

1. 仓库根 AGENTS.md、RESOURCES.md、workbench/README.md、EXECUTION.md。
2. [DISCUSSION.md](DISCUSSION.md) 与 [CLAIMS.md](CLAIMS.md)：当前结论与证据等级。
3. [E07](experiments/E07-choice-conditions.md)、[E06](experiments/E06-fork-head-vs-tail.md)、[E05](experiments/E05-fork-value.md)、[E04](experiments/E04-global-affine-component.md)：方法、对照与偏差记录。
4. [RELATED_WORK.md](RELATED_WORK.md) §2.5：分叉交换与锐化相关近邻。
5. [MENTOR_REQUIREMENTS.md](MENTOR_REQUIREMENTS.md)；LM Head 阶段的来龙去脉见 [logs/2026-11-26.md](logs/2026-11-26.md)。

## 论文形态卡（探索中）

- 主旨：尚未确定。
- 可能形态：学习机制分析（后训练在哪些位置、以什么方式、在什么条件下改变推理结果），以受控解码干预为主要工具。
- 核心贡献：❌ 尚无 manuscript-critical claim；E07 的难度依赖是目前最强的线索（L1，单谱系）。
- 定位：正反分叉交换（Sparse but Critical、Shen et al.、ReasonMaxxer）与 RL≈锐化系列为直接近邻，见 DISCUSSION §3。

## Idea 组合

| ID | 一句话 | 研究动作 | 状态 | 证据 |
|---|---|---|---|---|
| I01 | 后训练不同阶段的输出头功能变化 | 定位、干预 | PILOT 完成 | C04、C05 |
| I02 | 奖励加权怎样改变头部的学习信号 | 测量 | PILOT 完成（负结果） | C01、C02 |
| I03 | 冻结输出头对不同范式的影响 | 干预 | PARKED | 未测 |
| I04 | SFT 与 RL 在头部行上的梯度符号结构 | 测量 | PILOT 完成（梯度层成立 / checkpoint 层负） | C03、C06 |
| I05 | 后训练输出变化的结构：去随机化、改选、条件 | 测量、受控解码干预 | PILOT 进行中 | C07–C15 |

## 决策记录

- 2026-11-26 · 用户要求以真实数据驱动问题发现；GPT/Gemini 审查收敛到 LM Head，授权登记，E01/E02 优先。
- 2026-11-26（agent）· E02 主模型改为 Qwen3-8B-Base（后训练版 87.5% 的组全对、零优势）；新增 I04 与 E02b。
- 2026-11-26（agent）· 为跑 OLMo 对，把 OLMo Base 从 fvcrc11 rsync 到 fvcrc12（局域网）。今后是否允许节点间同步模型，待人确认。
- 2026-11-27 · 第一、二轮讨论后，用户授权从 LM Head 扩展到输出行为并自主推进（E04–E06）。
- 2026-11-27 · 第三轮讨论后，用户放行 E07（Qwen 部分，约 12–15 GPU·时）。
- 2026-11-27（agent）· E07 改设计：Qwen3-8B 在全程贪心下退化，改为“指定位置取首选、其余 T=0.6 采样”；中途按吞吐缩小范围（详见 E07 卡）。实际约 23 GPU·时，超出放行预算。
- 2026-11-27（agent）· 断线重连后本会话的旧副本仍在运行，其中一个把 OlympiadBench B2 拆成三片并提交了 `--shard`（9ac0968f）；已停掉旧副本并接管运行（P08）。

## 资产位置

- **环境：** `~/.venvs/ices-tf457`（torch 2.8 / transformers 4.57.6，OLMo-3 必须用 4.57）；`~/.venvs/vllm023-cu128`（vLLM 0.23，需 `VLLM_USE_FLASHINFER_SAMPLER=0`）。
- **权重（节点本地，按 HF sha256 校验）：** `/tmp/xiang_lmhead/models/`。fvcrc11：Qwen3-8B、Qwen3-8B-Base、OLMo-3 Base、RL-Zero-Math、Think-SFT；fvcrc12：Qwen3-8B、Qwen3-8B-Base、OLMo-3 Base、Think-DPO、Think、Instruct-SFT；fvcrc10：OLMo-3 Base、RL-Zero-Math。
- **大文件（节点本地，不进 git）：** E01/E02 `/tmp/xiang_lmhead/e0{1,2}/`；E04–E06 生成与同步解码 `/tmp/xiang_lmhead/e04/gen/`（fvcrc10/11/12）；E05 `/tmp/xiang_lmhead/e05/`（fvcrc11/20）；E07 题集、锚点与网格 `/tmp/xiang_lmhead/e07/`（fvcrc11/12；停掉的贪心网格在 `greedy_void/`）；日志 `/tmp/xiang_lmhead/logs/`。revision 写在每个结果 JSON 里。

## 待人审

当前一轮的实验与结果见 [DISCUSSION.md](DISCUSSION.md)。工作台状态、命名与下一步由人决定。
