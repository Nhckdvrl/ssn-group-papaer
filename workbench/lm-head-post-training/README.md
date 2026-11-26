# Understanding the LM Head in LLM Post-Training

## 状态（中文进度页）

**状态：** PROPOSED（用户 2026-11-26 要求开始做；是否登记为 ACTIVE 由人决定）
**territory 卡：** [研究思想与讨论沿革](logs/2026-11-26.md)　**目标会议 / 截稿：** 待定（ACL / ICML / ICLR / NeurIPS；不投 Findings） / —　**上次人审：** 2026-11-26（用户确认从纸面讨论转向实验探索，具体论文主旨未定）
**一句话（当前版本）：** 研究现代语言模型输出头在后训练中的功能变化及学习信号传递，通过真实模型测量和最小干预，寻找可解释、可复现、值得进一步研究的现象。

**当前进展（2026-11-26 晚，首轮完成，待人审）：** E01（4 个谱系对）与 E02（两家族各 128 题×8 条，外加头部 Adam 模拟 E02b）已跑完，约 1.5 GPU·时。结论按“问了什么 → 得到什么”：
1. **Godey & Artzi 的“梯度瓶颈”几何不区分后训练范式**（C01–C02）。能传回骨干的 logit 梯度能量 ρ 在 Qwen 约 0.021、OLMo 约 0.032，都低于随机方向（d/V）。GRPO、普通 CE、RFT、教师 SFT 之间无差别，两家族一致。I02 原问题得到负结果。
2. **RLVR 阶段几乎不动头**（C05）。OLMo 的两个 RL 对里，头部 ΔW 只有 1/4096 个方向高于 BF16 舍入地板；只换头的功能贡献约占 2–3%，分布变化几乎全部经由骨干。SFT/多阶段谱系里头动得和骨干一样多（C04），但大 SFT 下换头反事实失效（P03）。
3. **SFT 与 RL 的区别落在头自身的更新通道上，但只在梯度层面看得到**（C03 / C06）。对“从未做目标的 token 行”，SFT 类信号的梯度跨批符号一致、模拟 Adam 下沿 −μ 稳定漂移；GRPO 下接近随机，两家族一致。可是在公开 checkpoint 上，控制整体收缩与频率之后，真实 SFT 与真实 RL 的头部逐行位移分不出这种差异（I04 的 checkpoint 检验为负结果）。
**需要人决定：** 见本页末“待人审问题”。E03（冻结头训练）仍未启动。

## 给本地实验执行者的必读顺序

1. 仓库根 AGENTS.md、RESOURCES.md、workbench/README.md、EXECUTION.md。
2. [讨论沿革与研究思想](logs/2026-11-26.md)：为什么选这片研究空间、哪些旧路不再走、我们究竟希望学到什么。
3. [导师研究标准与本项目执行要求](MENTOR_REQUIREMENTS.md)：具体 12 项标准、Discovery/Problem-first、晋级与首轮探索的区别。
4. [关联工作与文献地图](RELATED_WORK.md)：先读 P0 两篇，其他按结果查阅；不要阻塞首轮实验。
5. [技术口径与实现指南](RESEARCH_PLAN.md)：数学、内存、指标、对照、结果解读和交付要求。
6. [E01 权重解剖](experiments/E01-checkpoint-anatomy.md)、[E02 梯度几何](experiments/E02-gradient-geometry.md)。不要先跑 E03。
7. 读两篇核心原文的方法与实验，记录原文定位和实际复现配置，不重新开启无限查重。

## 论文形态卡（探索初稿）

- 主旨：尚未确定；不能写成“LM Head 已被证明存在有害梯度瓶颈”。
- 可能形态：理论与实证 / 失败模式与最小修复 / 学习机制分析，取决于测量。
- 核心贡献：❌ 待真实证据；当前没有 manuscript-critical claim。
- 主图：先产出阶段权重变化、功能扰动、投影保留/增益、组级聚合与梯度方向；不是预定论文图。
- 强基线：原生 checkpoint、标准 CE、同轨迹奖励加权、标准 GRPO；两篇核心文献的关键工具对照。
- 证据标准：pilot 先校验工具和噪声地板；正式主张按 EXECUTION.md 升级、重复、跨模型及独立复算。
- 定位：核心两篇有明确竞争解释；PEFT/head tuning、softmax bottleneck、RL 稀疏更新为相邻边界，见 RESEARCH_PLAN。未宣称原创性。
- 决策：先建设及测量；人审后决定继续、转向同一空间或暂停。暂不启动第二空间（真实稀疏自由度与 BF16 精度）。

## Idea 组合

| ID | 一句话 | 来源 | 研究动作 | 状态 | 证据等级 |
|---|---|---|---|---|---|
| I01 | 后训练不同阶段的输出头功能变化是否值得单独研究 | 核心争议及公开谱系 | 定位、干预 | PILOT 首轮完成 | L1（C04、C05） |
| I02 | 奖励加权与轨迹分布怎样改变输出头处的学习信号 | 核心争议 | 重新归因、测量 | PILOT 首轮完成（负结果） | L1（C01、C02） |
| I03 | 冻结输出头会否对不同后训练范式造成不同影响 | 两篇论文的解释分歧 | 干预 | PARKED（等人审） | 未测 |
| I04 | SFT 与 on-policy RL 在头部行上的梯度符号结构 | Han et al. 2610.09835 + 推导 | 重新归因、测量 | PILOT 首轮完成（梯度层成立 / checkpoint 层负） | L1（C03、C06） |

## 主张与痛点

[CLAIMS.md](CLAIMS.md)：C01–C06（均 L1，单任务），含 1 条作废记录。[PAIN_LOG.md](PAIN_LOG.md)：P01–P05（数值稳定性、bf16 看不到 RL 头部更新、大 SFT 反事实失效、全局分量造成虚假相关、下载卡死）。

## 决策记录

- 2026-11-26 · 用户明确要求不再进行无限纸面辩论，从有价值空间出发，以真实数据驱动问题发现；GPT/Gemini 多轮审查收敛到 LM Head，授权登记，E0/E1 优先，E2 等结果。
- 2026-11-26 · 本次注册采用仓库规范编号 E01/E02/E03，对应对话 E0/E1/E2；保留现有 ACTIVE-MAIN/ACTIVE-EXPLORE 状态，不代替用户改线。
- 2026-11-26 · 最后一轮工程建议已纳入，同时修正“零坐标失配风险”、大 SVD 无成本、聚合 logit 梯度等同参数梯度等说法。详见技术指南。
- 2026-11-26（agent，按用户“自主推进”）· E02 主模型由 Qwen3-8B 改为 Qwen3-8B-Base：后训练版在 MATH 上 87.5% 的组全对、零优势，无法比较 RL 信号。
- 2026-11-26（agent）· 运行前新增 I04（来源 Han et al.），读数挂在 E01/E02 上，不单开实验；新增 E02b（头部 Adam 模拟）与 E01 的逐行对照，作为 I04 的决定性检验。
- 2026-11-26（agent）· 用户授权跨节点最多 8 卡；本轮实际只用 fvcrc11/12 的 3 张空闲卡。为跑 OLMo 对，把 OLMo Base（15 GB）从 fvcrc11 rsync 到 fvcrc12（局域网，约 3 分钟）。这与上方旧的“不跨节点同步大模型”交接不一致，请人确认今后是否允许。

## 资产位置

- 代码：`scripts/`（几何库 `lmhead_geom.py` 与测试 `test_geom.py`；E01 `e01_weights.py`/`e01_function.py`/`e01_vs_adam.py`；E02 `e02_rollout.py`/`e02_geometry.py`/`e02_headadam.py`/`verifier.py`；输入清单 `build_inputs.py`；下载与校验 `fetch_ranges.py`/`verify_models.py`；节点运行器 `run_node.sh`/`run_vllm.sh`/`chain_e02.sh`；汇总 `summarize.py`）。
- 环境：`~/.venvs/ices-tf457`（torch 2.8 / transformers 4.57.6，OLMo-3 必须用 4.57）；vLLM 用 `~/.venvs/vllm023-cu128`（需 `VLLM_USE_FLASHINFER_SAMPLER=0`）。
- 输入清单：`data/e01_texts.json`、`data/e02_prompts.json`（只存索引与 sha1，文本从本地 HF 缓存复原）。
- 小型结果：`results/e01/`、`results/e02/`（JSON/JSONL）。
- 节点本地（会随重启丢失）：权重 `/tmp/xiang_lmhead/models/`（fvcrc11：Qwen3-8B、Qwen3-8B-Base、OLMo-3 Base、RL-Zero-Math、Think-SFT 下载中；fvcrc12：OLMo-3 Base、Think-DPO、Think、Instruct-SFT），均按 HF sha256 校验；rollout、逐 token 数组、逐行 npz 在 `/tmp/xiang_lmhead/e0{1,2}/`；日志在 `/tmp/xiang_lmhead/logs/`。revision 写在每个结果 JSON 里。

## 入口

- [RESEARCH_PLAN.md](RESEARCH_PLAN.md)
- [RELATED_WORK.md](RELATED_WORK.md) · [MENTOR_REQUIREMENTS.md](MENTOR_REQUIREMENTS.md)
- [讨论与人审记录](logs/2026-11-26.md)
- [E01](experiments/E01-checkpoint-anatomy.md) · [E02](experiments/E02-gradient-geometry.md) · [E03（暂缓）](experiments/E03-head-freeze.md)

## 待人审问题（2026-11-26 首轮）

1. **方向：** 两条“梯度瓶颈”线索（I02 投影几何、I04 符号结构）都没有在后训练里产生能区分范式的真实信号。I04 只在梯度回放里成立，公开 checkpoint 看不出来。要选：(a) 在同一空间里转向受控小训练，同起点、同步数比较 SFT 与 RL，保存 FP32 头部状态，直接看头部行漂移与通用文本遗忘，这就是 E03 的变体，需要批准训练算力；(b) 把首轮作为测量记录，转向 C05 暗示的问题：RL 阶段分布变化几乎全部经由骨干，头基本冻结，那么后训练理论里“logit 可自由更新”的表格假设（Cui et al. 熵机制等）在多大程度上被骨干通道的秩约束改变；(c) 暂停本空间。
2. **工作台状态：** 目前仍是 PROPOSED，是否登记为 ACTIVE-EXPLORE 由你决定。
3. **算力与资产：** 是否允许节点间同步模型（见决策记录）；OLMo Think-SFT 两对仍在下载/排队，是否需要补跑进入下一轮。
