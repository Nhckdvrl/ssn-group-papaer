# Understanding the LM Head in LLM Post-Training

## 状态（中文进度页）

**状态：** CLOSED（用户 2026-11-28 决定结项归档；结项记录与失败复盘见本页末尾）
**目标会议 / 截稿：** 待定（ACL / ICML / ICLR / NeurIPS；不投 Findings）　**上次人审：** 2026-11-27（第三轮 GPT/Gemini 反馈后，用户放行 E07）
**当前问题（一句话，待讨论）：** 同一个底座上，RL 与蒸馏带来的准确率增益可以一样大；它们改变 Base 的方式是否相同（一个开头、开头之后的高熵选择、交接需要多长、逐题是否重合）。
**讨论材料：** [DISCUSSION.md](DISCUSSION.md)（唯一一份，只写上次讨论以来的实验、数据和结论）。

### 问题是怎么演变的

1. **LM Head 阶段（11-26，E01–E02）：** 头部梯度几何与权重变化不区分后训练范式；RLVR 阶段几乎不动头。原问题得到负结果（C01–C06）。
2. **输出行为阶段（11-27，E04–E06）：** 转向“后训练在下一 token 分布上改变了什么”。MATH-500 上增益集中在 Base 高熵的分叉位置；Base 按 T=1 采样时，分叉处的随机性代价大于“谁的首选”；单个分叉上改选测不出价值；OLMo RL-Zero 的大部分差距是回答开头的模式选择（C07–C14）。正反分叉交换近作已有。
3. **条件阶段（11-27 晚，E07–E09）：** Base 改用近作的截尾采样（T=0.6/top-p 0.95）后，分叉处的选择效应在易题上 ≈0（+1.3），在 MATH Level 5 上 +14.0，难题上 Post 首选补上差距的 70%；OlympiadBench 上方向一致、幅度减半（+7.3，补 38%）（C15）。E08：Post 写的前缀能被 Base 继承，Base 用 6 倍算力投票也买不到 Post 的优势（C17–C18）。E09：OLMo RL-Zero 在强制开头之后没有剩余优势（C16）；AIME 上选择效应方向一致但未显著。另：Qwen3-8B 是强到弱蒸馏模型，没有 RL 阶段（技术报告 §4.5）。

4. **同底座对比阶段（11-28，E10–E12）：** E10：B2 回答截到一半交给 Base 保留约 3/4 收益（C19）。E11：同一 Qwen3-8B-Base 上的纯 RL（DAPO）与蒸馏在 DAPO 没见过的题上增益接近；强制开头 “Alright, I have this problem” 在所有题集上追平 DAPO 的全部增益，蒸馏只在更难的题上超出；DAPO 只需前 32 token，蒸馏模型的作用持续到回答一半。E12：开头之后去随机化消失，开头 + 高熵位置换蒸馏首选即到达蒸馏水平；8192 上限与另两种措辞下结论不变。“开头等于 RL”已由 2610.06851 报告。

### 当前状态

- **已完成：** E01、E02、E04–E07、E08（Qwen 两题集；OLMo 交接因无差距停掉）、E09 首轮、E10、E11、E12。
- **运行中：** 无（11-28 05:00 起不占卡）。等待讨论（DISCUSSION.md 已更新）。
- **未做：** E03（冻结头训练，暂缓）；OLMo-3 RL-Zero 上的 E07（可行但慢，见 E07 卡）。
- **算力：** 11-26 约 1.5 GPU·时；11-27 E04–E06 约 25 GPU·时，E07 约 23 GPU·时；E08–E09 约 35 GPU·时；11-28 E10–E12 约 45 GPU·时。

## 目录

| 位置 | 内容 |
|---|---|
| `README.md` | 本页：状态、目录、决策记录、资产位置 |
| `DISCUSSION.md` | 当前一轮的讨论材料 |
| `CLAIMS.md` | 主张账本 C01–C18、作废与更正记录 |
| `PAIN_LOG.md` | 痛点 P01–P09 |
| `RELATED_WORK.md` | 文献地图与精读核对（含近邻对照表） |
| `MENTOR_REQUIREMENTS.md` | 导师标准与本项目执行要求 |
| `RESEARCH_PLAN.md` | 历史：LM Head 阶段的技术指南（E01–E03） |
| `ideas/` | I01–I05 idea 卡 |
| `experiments/` | E01–E07 实验卡（设计、决策表、偏差、结果） |
| `scripts/` | 全部代码，索引见 [scripts/README.md](scripts/README.md) |
| `results/e0{1,2,4,5,7,8,9}/` | 进 git 的小型汇总（JSON/JSONL）；E06 的汇总在 `results/e04/hybrid_qwen.json` |
| `data/` | 输入清单（只存索引与 sha1） |
| `logs/` | 每日会话记录 |

## 必读顺序

1. 仓库根 AGENTS.md、RESOURCES.md、workbench/README.md、EXECUTION.md。
2. [DISCUSSION.md](DISCUSSION.md) 与 [CLAIMS.md](CLAIMS.md)：当前结论与证据等级。
3. [E07](experiments/E07-choice-conditions.md)、[E09](experiments/E09-regime-across-families.md)、[E08](experiments/E08-handoff.md)、[E06](experiments/E06-fork-head-vs-tail.md)、[E05](experiments/E05-fork-value.md)、[E04](experiments/E04-global-affine-component.md)：方法、对照与偏差记录。
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
- 2026-11-28 · E11–E12 讨论后：评测模板问题（Qwen3-8B 以非思考模式评测、DAPO 被插入空思考块）写入校对备注；“RL vs 蒸馏”退出主线。用户同意新开 `sequential-rl-learning`（RL 历史与后续学习）并写卡。本工作台是否关闭待用户决定；调研笔记留在 `notes/`。

## 资产位置

- **环境：** `~/.venvs/ices-tf457`（torch 2.8 / transformers 4.57.6，OLMo-3 必须用 4.57）；`~/.venvs/vllm023-cu128`（vLLM 0.23，需 `VLLM_USE_FLASHINFER_SAMPLER=0`）。
- **权重（节点本地，按 HF sha256 校验）：** `/tmp/xiang_lmhead/models/`。fvcrc11：Qwen3-8B、Qwen3-8B-Base、OLMo-3 Base、RL-Zero-Math、Think-SFT；fvcrc12：Qwen3-8B、Qwen3-8B-Base、OLMo-3 Base、Think-DPO、Think、Instruct-SFT；fvcrc10：OLMo-3 Base、RL-Zero-Math。
- **大文件（节点本地，不进 git）：** E01/E02 `/tmp/xiang_lmhead/e0{1,2}/`；E04–E06 生成与同步解码 `/tmp/xiang_lmhead/e04/gen/`（fvcrc10/11/12）；E05 `/tmp/xiang_lmhead/e05/`（fvcrc11/20）；E07 题集、锚点与网格 `/tmp/xiang_lmhead/e07/`（fvcrc11/12；停掉的贪心网格在 `greedy_void/`）；日志 `/tmp/xiang_lmhead/logs/`。revision 写在每个结果 JSON 里。

## 结项记录（2026-11-28）

- **决定人：** 用户（2026-11-28：“好好总结思考为什么失败，然后归档”）。证据类别 A + H：各阶段的结果见上文“问题是怎么演变的”与 `CLAIMS.md`；是否值得继续由用户判断。后续方向转到 [`sequential-rl-learning`](../sequential-rl-learning/README.md)。
- **三天做了什么：** 12 张实验卡（E01–E12，E03 未跑），约 130 GPU·时。问题换了四次：LM head 的梯度与权重 → 后训练在下一 token 分布上改变了什么（分叉、去随机化） → 选择效应的条件（难度、交接、开头） → 同底座 RL 与蒸馏。没有形成可投稿的主张。

### 为什么失败（复盘）

1. **从对象和工具出发，而不是从领域问题出发。** 起点是“LM head 在后训练里做了什么”——选它是因为好测、少有人测，没有先回答“谁关心、答案会改变什么”。LM head 的负结果出来后，问题变成了“同步解码这套工具还能测什么”，每一轮的问题都由上一轮的工具和结果决定。
2. **残差驱动、防御性收窄。** 每轮的问题 = 上一轮解释被推翻后剩下的部分，再减去近邻已占的部分（分叉交换 → Sparse but Critical/Shen；开头 → Wang 2610.06851；短前缀 → Cai 2510.00553）。最后两轮的问题一个是导师否过的“A 和 B 是否相同”句式（RL vs 蒸馏），一个把我们自己选的探测工具（一个开头）当成了概念边界（“超出 Base + 开头”= 超出激发），违反 G1。
3. **只解剖别人训练好的终点模型，手里没有自己能操纵的变量。** 领域争论的是“RL 这个过程能不能教新东西”，一个检查点只能回答“这一次训练出了什么”。我们能做的只有描述终点差异和解码干预，解释无法用训练去检验；结论要么已被近邻覆盖，要么被常识挡住（例如 27 次更新的 RL 对比 235B 教师蒸馏）。
4. **实验基本功出错，且很晚才发现。** 模板问题从 E04 起就在（见 `CLAIMS.md` 11-28 降级记录），直到 E12 之后的外部意见才查出；“DAPO 只需 32 token”比较了两种上限；DAPO-step-27 只有 27 次更新却被当作“纯 RL”的代表；从三篇设置各异的论文读出一条趋势。高层推演建在没核实的前提上。
5. **速度压过了核查，讨论被最新结果和外部意见锚定。** 三天 130 GPU·时、每轮重写叙事；GPT/Gemini 每轮都在我最新的结果上重构问题，我再吸收进下一轮，多方相互认同制造了虚假的确信（准则文档 §一.4）。
6. **文献读法是查重。** 每读到一篇近邻就从问题里减掉一块，没有用相邻领域找解释框架；领域近况的扫描也被我推到“下一轮”。

### 学到的事实（都是单谱系 pilot，L1；Qwen 侧受模板问题限制）
- Qwen3-8B 与 OLMo-3 的 RLVR 阶段几乎不单独改动输出头；头部梯度几何不区分后训练范式（C01–C06）。
- 在 MATH 上，后训练增益集中在 Base 高熵的少数位置；Base 按 T=1 采样时，这些位置的随机性代价大于“谁的首选”（C08–C11、C14）。
- OLMo-3 RL-Zero 的差距基本是回答开头的一个模式选择（C13、C16），与 Wang 2610.06851 一致。
- 强制一个开头之后，Base 在高熵位置取自己首选的增益消失（E12，三个题集）——两种看似不同的干预作用重叠。
- 评测后训练模型前必须审计提示模板、思考模式和生成上限，并按模型卡/训练报告核对。

### 可复用资产
- 同步解码（`scripts/e04_hybrid.py`，含 `--force_prefix`）、vLLM 熵门控首选、前缀交接（`e08_handoff.py`）、各汇总脚本（`scripts/README.md`）。**复用前先改 `render()` 的模板逻辑。**
- DAPO-Math-17k 与我们题集的重叠表 `/tmp/xiang_lmhead/e07/dapo_seen.json`（节点本地）；题集清单在 `data/`。
- 调研笔记 `notes/`（RL vs 蒸馏、激发、开头动态、路径依赖、可学习性、相邻领域框架、公开 RL 轨迹）与用户的研究准则 `notes/research_principles.md`。

### 重开条件
出现一个领域层面的问题，需要在“Base 与后训练模型”之间做逐位置的解码干预或前缀交接作为测量工具时，复用本工作台的代码；不以“LM head”或“开头”本身为研究对象重开。

### 节点上的数据
`/tmp/xiang_lmhead/`（fvcrc10/11/12/13/20）上的权重与原始输出暂未删除；需要时再清理。
