# Video World Model Temporal Interfaces — Workbench

**Status: exploratory workbench — not a candidate.**

## 进度页（中文，随每次里程碑更新）

**最后更新：2026-09-29**

### 基线（已跑通）
- **Matrix-Game 2.0**（Skywork，开源 1.3B 交互世界模型，蒸馏学生 `base_distilled_model`，universal 场景）：Wan2.1 VAE（4× 时间压缩、首帧单独编码）、逐帧键鼠动作、每块 3 个潜变量（12 帧）、局部注意力 6 个潜变量、3 步去噪、352×640。官方代码 `71c3cd7`，A100 上 45 帧约 11 秒。同一噪声下重复生成**逐位一致**，可以做配对反事实。
- 已下载待用：Wan2.1-T2V-1.3B、Causal-Forcing 全阶段权重（AR 扩散 → 因果 ODE/CD → DMD，逐帧/分块两套）。

### 时间接口的实际实现（读代码得到）
- 第 i 个潜变量对应第 4i−3…4i 帧；生成它时看到第 4i−12…4i−1 帧的逐帧动作（约定：第 t 帧动作决定 t→t+1 的变化）。
- 官方测试脚本只在第 1、13、25… 帧切换动作（与 12 帧分块对齐）；交互模式下一个动作填满整块，动作最细每 12 帧才能改一次。
- 蒸馏学生只有前 15 个 Transformer 块带动作模块；基础模型 30 块都有，且是双向整段（57 帧）生成。

### 实验结果
| 实验 | 结论 |
|---|---|
| E01 动作起点逐帧推移（学生，配对反事实，3 图×2 种子×起点 1–24） | **阶跃起动逐帧精确**：视角延迟 1 帧（129/144），前进 1–2 帧；与相位无关；动作前无同向运动。 |
| E02 Wan2.1 VAE 相位（DAVIS 87 段） | 组内第 3 帧重建误差低 25%；**IV-VAE（CVPR 2025）已报告**，不作为新问题。 |
| E06 VAE 单帧跳动（6 段真实画面，静止/匀速平移，跳 4/8 像素） | 单帧跳动在 4 个相位上都保留 89–103%。**VAE 能承载亚潜变量运动，不是瓶颈。** |
| E04 单帧脉冲（学生，9 图×2 种子×起点 9–32×幅度 0.1/0.2，每格 n=108） | 幅度 0.1：相位 0/1/3 转动 2.3–2.9，**相位 2 只有 0.44**——先转 +2.66 下一帧转回 −1.84（**回弹**）。幅度 0.2 时相位 2 恢复、相位 3 最低：映射非线性且周期时变。 |
| E05 正弦输入（学生，周期 3–24 帧） | 周期 ≥8 帧增益≈1；5–6 帧衰减到 0.63–0.85；**周期 3–4 帧响应≈0**。输出在 0.25±f（潜变量频率）处有强边带（周期 8 时达主峰 38%）。→ **有效控制带宽≈潜变量奈奎斯特频率，且系统以 4 帧为周期时变。** |
| E07 同一脉冲测试在**双向多步老师**上（6 图，n≈20/相位，进行中） | 老师在所有相位都把单帧动作画在正确的帧上、**没有回弹**（相位 2 为 3.03，学生 0.44）；相位差异仅约 ±20%。→ **回弹/带宽损失是蒸馏引入的。** |

### 当前判断（2026-09-29 凌晨）
- 候选问题正在成形：**"少步因果蒸馏像一个作用在控制信号上的时间低通滤波器"**——学生保住慢变控制，丢掉老师具有的高频/亚潜变量控制，并出现相位依赖的回弹。
- 已排除：VAE（E06）、测量伪影（配对反事实 + 两种运动估计器一致 + 老师对照）。
- 近邻边界（持续核对）：CMD（2608.13391，老师–学生上下文错配，改善随时间变化的相机控制，但只到潜变量/块粒度，未做频率/相位分析）；Causal Forcing / DyMD（蒸馏后运动**幅度**下降）；ActionSplice（块内修改动作的交互延迟）；SCOPE（FPS 高频控制，空间注入视角）。
- 下一步：老师的正弦响应（E08，运行中）；在 minWM（Wan 1.3B，完整阶段链：双向→AR 扩散→因果 ODE→因果 CD→DMD）上测潜变量尺度的控制带宽，检验普遍性并定位是哪个阶段丢的。

---

This workbench studies how modern video generators and interactive/world models represent, compress, align, and transmit **time** across their major interfaces.

The motivating literature contains several related pressures:
- video tokenizers / VAEs often compress multiple raw frames into one latent step;
- controllable world models may receive actions, camera motion, contacts, or state changes at a finer rate than their latent video stream;
- causalization, streaming inference, few-step distillation, and long rollout can change what temporal information remains available;
- some recent systems respond by changing temporal compression, preserving higher-rate control signals, or adding separate fine-timescale pathways.

These facts justify studying the territory. They do **not** establish that temporal compression is the bottleneck, that a phase effect exists, or that any particular interface needs a new method.

## Execution ownership

The default executor of this workbench is the **local research agent**.

Once the territory is admitted to `workbench/`, the agent should not behave like a consultant that proposes one experiment and waits for a human to choose the next step. It should carry the research loop forward autonomously:

> reproduce → inspect → perturb → analyze → search nearest prior → update the working explanation → choose the next highest-information experiment → repeat

The agent is expected to:
- read papers, repositories, issues, appendices, and current code rather than rely on summaries;
- clone and run strong baselines;
- diagnose implementation details;
- design and execute the next experiment itself;
- use failures as gradients rather than stopping after one null result;
- continuously check whether an emerging observation is already owned by prior work;
- strengthen or replace the working question when evidence changes;
- keep the repository state current with code, results, and concise conclusions;
- continue until either a genuinely defensible novel problem/idea emerges or the territory is exhausted enough to archive/kill.

Human input is for occasional taste calibration, resource constraints, or new insight—not per-experiment approval.

## Research target

The purpose of exploration is not exploration for its own sake.

The workbench should actively search for a **real, reproducible, novel research object** that can eventually crystallize into a candidate. A useful endpoint may be:
- a previously unrecognized failure/bottleneck in a strong baseline;
- a surprising dependency exposed by a simple perturbation;
- a mistaken assumption shared by current methods;
- a representation/interface limitation with downstream consequence;
- a strong-baseline result that invalidates part of an existing narrative;
- a minimal intervention that becomes natural only after the bottleneck is established.

Novelty must be checked against current nearest prior continuously, not only after a result looks good.

The agent should not stop merely because the initial temporal-compression intuition fails. It should use that failure to redirect within the broader temporal-interface territory, unless accumulated evidence shows the territory itself is no longer promising.

## Baseline residency

Begin from strong open artifacts rather than from a new architecture.

The first task is to become fluent in a small set of practical video/world-model stacks that fit a single node. Candidate families include:
- open causal video VAEs / tokenizers;
- Wan-style open video generation stacks;
- small/open interactive or action-conditioned world models;
- models with explicit camera/action conditioning and published inference code;
- where useful, paired teacher / causal / distilled checkpoints from the same lineage.

Before proposing a research claim:
- reproduce the strongest practical baseline we can run;
- map the exact temporal interfaces in code: raw FPS, latent stride, first-frame handling, padding, causal context, action grouping, camera conditioning, rollout chunking, and any distillation/streaming conversion;
- record quality, controllability, latency, memory, and failure slices;
- distinguish tokenizer artifacts from downstream model behavior.

No foundation-model pretraining is required or authorized at the beginning.

## Exploration space

The workbench should explore several axes and let the important object emerge from experiments.

Potential axes include:
- **temporal representation:** what information changes when time is compressed or tokenized differently;
- **alignment:** how frames, latents, actions, camera trajectories, and state transitions are synchronized;
- **causality / streaming:** what changes when a bidirectional or teacher-forced system becomes causal or online;
- **control resolution:** whether coarse latent steps and fine-grained control signals interact cleanly;
- **event timescale:** whether short events, contacts, reversals, or fast motion behave differently from slow dynamics;
- **boundary / phase effects:** whether temporal chunk boundaries matter after strong implementation controls;
- **stage effects:** tokenizer vs generator vs causalization vs distillation vs rollout;
- **compensation:** whether a downstream model repairs information losses visible at an earlier stage;
- **efficiency tradeoffs:** which temporal simplifications actually buy useful speed and which silently remove control-relevant information.

“Temporal control bandwidth” is therefore one **possible diagnostic lens**, not the registered paper question.

## Research discipline

Do not:
- assume a phase/bandwidth phenomenon before measuring it;
- build the workbench around one synthetic pulse experiment;
- train a new video foundation model to make the question exist;
- turn the project into a generic long-video-memory, action-following, or VAE leaderboard;
- propose a module/loss before a stable bottleneck survives strong baselines;
- protect the initial temporal-compression story if another interface becomes more load-bearing.

Prefer:
- frozen-model diagnostics first;
- matched comparisons within the same model lineage;
- small perturbations that reveal hidden dependencies;
- failures that change which interface should be studied next;
- lightweight adapters / conditioning changes only after an actionable bottleneck is established.

## Compute boundary

The workbench must remain practical on one node:
- up to 4×A100 80GB, or
- up to 4×RTX PRO 6000 96GB.

The two available nodes cannot be assumed to communicate.

Therefore:
- VAE/tokenizer analysis and frozen inference are preferred early;
- repeated sweeps should favor roughly 1B–5B open backbones when possible;
- small LoRA / adapter / conditioning experiments are acceptable;
- multi-node foundation-model pretraining is out of scope.

## What would justify promotion

Remain exploratory until the workbench produces a simpler scientific object than the one we started with.

Promotion would require something like:
- a reproducible temporal/interface dependency that survives a strong baseline;
- evidence that it is not merely one implementation bug or one model family;
- a clear downstream consequence or changed understanding;
- a nearest-prior boundary that cannot be compressed into “already known”;
- a realistic confirmation path under the single-node compute budget.

It is fully acceptable for this workbench to end as a negative result or a reusable map of temporal interfaces.

## Starting literature / artifact audit

Before running substantial experiments, re-verify the latest primary papers, code, checkpoint availability, and exact licenses for candidate baselines. In particular, audit recent work on:
- causal / temporally compressed video VAEs;
- open video generation stacks;
- action- and camera-conditioned world models;
- causal / streaming / few-step world-model conversion;
- adaptive temporal tokenization or frame-rate allocation;
- embodied video tokenizers.

Do not treat any one of these lineages as the final paper identity.
