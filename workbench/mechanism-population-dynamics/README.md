# Mechanism Population Dynamics

**Status:** **ACTIVE-EXPLORE** — 2026-10-01 human-confirmed  
**Lane:** our-taste / mechanistic interpretability / model science  
**Target:** ICML 2027 / NeurIPS 2027  
**Territory card:** [`../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md`](../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md)

## 0. Registered object

> **Across independently trained model instances, at what abstraction level is a mechanistic claim reproducible: exact component, causal role, algorithm/function, developmental ordering, or only behavior?**

### 当前进展（2026-10-03 22:05）
**一句话（论文叙事；对齐最新顶会的分析见 `experiments/A05`，英文大纲 `A03` v3，引言草稿 `A04`）：** *The seed picks the slot, the data fills it.* 语言模型里“哪个头承担哪个角色”由随机初始化决定，换掉整个预训练语料也不变，只看头的分工布局就能认出模型的 seed；模型表示什么、回路多强、何时出现、行为如何都由数据决定；算法与所在层是普适的。槽位在训练最初 1%–2.5% 的关键期内确定，之后成为吸引子；权重忘记了初始化（r = 0.04），解剖结构却记得。继承强度由语料的统计相似度与关键期内的 SGD 温度（学习率 / batch）决定；标准缩放配方随规模降温，所以模型越大越“先天”。

| 五条发现 + 应用 | 已完成的证据 | 进行中 |
|---|---|---|
| **1 析因设计与决定因素地图** | DataDecide 14 尺寸 + Pythia（step0 张量核对：70M–12B 全部同初始化）；13 项性质的地图（`results/figs/fig_determination_map.png`） | — |
| **2 初始化选槽位** | E35、E45（14 尺寸）、E44 + E58（Pythia 70M–6.9B，每个尺寸远高于置换零分布）；**E59：9 种角色全部成立，含只看权重的 OV 复制分数**；Fig 1：某个 seed 的同一个头在 25 个语料中 56% 的情况下最强（随机 6%） | E58（2.8B、12B） |
| **3 数据填内容** | 强度 E35、出现时间 E54、内容 E43、行为 E36 / E51（不存在幸运 seed）、“Question:” 开关 C04 | E48b |
| **4 关键期，然后是吸引子** | E46：1% 时换语料 / 加噪声会重排，2.5% 起加入与权重同量级的噪声仍回到原槽位；权重相关 0.04 | — |
| **5 继承跟随语料统计与 SGD 温度** | **E60：语料距离越小继承越强，每个尺寸都成立（ρ 最高 −0.8），只用不共享数据源的配方对也成立**；E56：代码重抽槽位；**E62：固定模型、降低学习率 / batch（SGD 温度），只换顺序的相似度 0.43 → 0.90、跨语料继承 0.01 → 0.22；E46b2：固定温度放大模型 30 倍不改变继承 → DataDecide 的规模趋势来自缩放配方随规模降温** | E57（发育视角） |
| **应用** | **E61：从 60M 起只看布局识别 seed 的准确率 98–100%，Pythia 中真兄弟排第 1 / 10** | — |

**不可判定 / 暂停：** E52、E53；E50（开关的头级归因不由初始化放置，写成“晚期由数据装入的功能以分布式实现”）。**新发现：** P09（PolyPythias weight-seed 变体没有换初始化）。

## 1. Why inhabit this territory

公开的多 run 套件（PolyPythias、DataDecide、OLMo 2 中期训练成分）让我们不用自己预训练就能研究机制的形成。“不同 seed 的内部不同”这类朴素说法已被近邻占据（PolyPythias、Tigges et al.、Bali et al. 2026、Crosscoding Through Time、Polymorphism Is Rotation、Pre-carved Niches），本工作区只做经得住正确对照、并能说明在哪个抽象层级可复现的结论。

## 2–6. 入驻计划（已完成，保留为历史）
R0 产物审计 → E01 复现已知机制（induction）→ E02 群体扫描（10 seed × checkpoint）→ E03 抽象阶梯（成分身份 / 坐标 / 因果角色 / 算法 / 发育顺序 / 时间）。结果见 C01–C03（Pythia 31M–410M）。之后的触发分支（第二机制、更大尺寸、外部家族、训练干预）均已按证据触发：知识冲突仲裁（E13 起）、DataDecide 交叉设计（E35 起）、受控训练（E46，人已授权补充实验）。

## 7. Ownership / compression

每条有希望的线索都必须回答：
> 为什么这不是“已有的机制分析 + 更多 seed”？为什么这不只是坐标旋转 / 对齐的伪影？

当前回答：(1) 我们用**初始化 × 数据的完全交叉**把方差分解为先天和后天，近邻只变初始化（Bali、PolyPythias）或只变数据；(2) 置换对称性的控制：效应全部来自“同层内哪个头”（层内拆分，E35 / E44），并用置换 / 旋转不变量做对照（E43）；(3) 有干预证据（E46、E48）。强预印本同样占有主张，主旨每次改变时都重扫近邻。

## 8. 论文形态卡（2026-10-03 22:05；按 A05 对齐最新顶会后重写；agent 起草，待人否决）
- **Title:** *The Seed Picks the Slot, the Data Fills It: Nature and Nurture in Language-Model Circuits*
- **Hook（Fig 1）：** 同一个 seed 在 25 个不同语料上训练的 1B 模型，往往由同一个头担任最强的 induction / 检索 / previous-token 头（最高 56%，随机 6%）；只看这种布局就能 100% 认出模型来自哪个 seed，而权重本身只剩 4% 的初始化相关。
- **论文形态（对齐 MDA ICML'26 Oral、SeedPrints ICLR'26、Bali ICML'26）：** 一个大命题 + 五条粗体发现 + 应用；顺序：框架 → 主发现 → 互补发现 → 机制（关键期）→ 规律（语料距离与规模）→ 应用。
- **novelty：** 第一次把语言模型机制中来自 seed 的部分与来自数据的部分分开；稳定性研究只变 seed，数据归因（含 MDA）只变数据。
- **与最强近邻互补：** MDA（数据决定头的出现与速度，我们：不决定是哪个头）；SeedPrints（输出指纹，我们：兄弟模型的解剖布局）；Forgetting-Time（Adam 抹去功能记忆，我们：解剖记忆仍在）；Tigges / Bali（成分会变，我们：为何变、何时共享）。
- **主图：** Fig 1 钩子；Fig 2 决定因素地图；Fig 3 坐标 vs 内容；Fig 4 规模（继承与识别准确率，DataDecide + Pythia 到 12B）；Fig 5 关键期；Fig 6 语料距离规律；Fig 7 数据填内容（基准、开关）。
- **不完美结果的写法：** 小模型 / 代码继承弱 → 第 5 条发现的规律本身；单头消融图偏弱 → 冗余；开关不由初始化放置 → 晚期功能分布式实现。
- **风险：** E58 若 6.9B / 12B 不继承，则写“继承在中等规模最强”；E48b 若不成立，开关停留在数据层面的配对与天然实验。

## 9. Human-review triggers
请求人审的情形：主旨改变；新的直接先验占有了主张；对齐 / 置换控制消除了主效应；准备进入候选（candidates/）。

## 10. Do not do
不在上百个任务里找异常；不挑 seed；不把“头换了”当作“算法换了”；不把单一对齐分数当作机制等价的定义；不在看到结果后改读数。

## 11. Decision record
- **2026-10-01：** 人选定本 territory 为唯一的 ACTIVE-EXPLORE。
- **2026-10-03：** 人：校对免了，按同题材成熟顶会论文的标准补工作量、补实验，叙事按好论文的方式包装、对齐顶会尺度（→ A02、E42–E51）。

## 12. Assets
- claims `CLAIMS.md` · pain log `PAIN_LOG.md` · 实验卡 / 脚本 `experiments/`、`scripts/` · 日志 `logs/`
- 缓存（不进 git）：`/home/xiang/mechpop_cache/hf`（HF 权重）、`datadecide/`（配方、全尺寸核查 `survey_all_sizes.json`、`e45_plan.json`、评测表 `evals/`）、`e43/`（激活转储，约 36 GB）、`e46_data/`（受控训练语料前缀与 Flan）、`e46_runs/`（受控训练 checkpoint）
- 环境：`~/.venvs/mechpop`（torch 2.8.0+cu128、transformers 4.57.6，transformer_lens 等 `--no-deps`）
