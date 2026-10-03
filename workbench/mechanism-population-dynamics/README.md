# Mechanism Population Dynamics

**Status:** **ACTIVE-EXPLORE** — 2026-10-01 human-confirmed  
**Lane:** our-taste / mechanistic interpretability / model science  
**Target:** ICML 2027 / NeurIPS 2027  
**Territory card:** [`../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md`](../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md)

## 0. Registered object

> **Across independently trained model instances, at what abstraction level is a mechanistic claim reproducible: exact component, causal role, algorithm/function, developmental ordering, or only behavior?**

### 当前进展（2026-10-03 21:20）
**一句话（论文叙事，见 §8、`experiments/A02` §8、英文大纲 `A03`）：** *The seed picks the slot, the data fills it.* 语言模型的回路“长在哪个头上”由随机初始化决定，换掉整个预训练语料也不变；模型表示什么、回路多强、何时出现、行为如何，都由数据决定，初始化对它们没有主效应；算法本身与所在层是普适的。位置在训练最初 1%–2.5% 的关键期内由对称性破缺决定，之后成为吸引子：最终权重几乎不保留初始化（r = 0.04），角色却记得初始化。规模越大，继承越强。

| 叙事部分 | 已完成的证据 | 进行中 |
|---|---|---|
| **初始化选槽位** | E35（1B，数据分量 = 0）；E45（14 个尺寸，随规模增强，ρ 0.81–0.92；1B 五初始化中最强头的同初始化一致率达随机的 5 倍）；E44（Pythia 第二家族 8/8）；E43（坐标继承、内容不继承；权重相关 0.04）；E42（消融图同向） | **E58**（Pythia 6.9B / 12B，标准 vs 去重同初始化）；**E57**（尺寸曲线的发育轨迹） |
| **普适部分** | E55（previous-token → induction 组合 75 / 75）；E35（所在层近似普适） | — |
| **数据填内容** | E35（强度）；E54（induction 出现时间：语料 0.81、初始化 0）；E36、E51（行为与基准：初始化主效应 = 假阳性率，不存在幸运 seed）；C04 开关（E25–E34、E29、E30、E47、E49） | **E48b**（加大剂量的线索替换干预） |
| **关键期与吸引域** | E46：第 100 步换语料或加噪声 → 位置重排；第 250 步之后加与权重同量级的噪声也回到原槽位（0.85–0.97）；初始扰动 ≤ 1% 不改变位置；E37 / E40：公开套件在 2%–3.6% 锁定 | **E46b**（更大的受控模型） |
| **边界条件** | E46 A：小模型继承弱（与尺寸曲线的小端一致）；代码语料拉低继承；E46c：初始化尺度 / 学习率不解释尺寸趋势 | **E56**（新初始化确认“代码会在关键期重新打破对称性”） |

**不可判定 / 暂停：** E52（特化神经元）、E53（为什么是 “Question:”）、E50（开关的头级归因不由初始化决定，写成“晚期由数据装入的功能以分布式实现”）。**新发现：** P09（PolyPythias weight-seed 变体没有换初始化）。
**草图：** `results/figs/`。

## 1. Why inhabit this territory

公开的多 run 套件（PolyPythias、DataDecide、OLMo 2 中期训练成分）让我们不用自己预训练就能研究机制的形成。“不同 seed 的内部不同”这类朴素说法已被近邻占据（PolyPythias、Tigges et al.、Bali et al. 2026、Crosscoding Through Time、Polymorphism Is Rotation、Pre-carved Niches），本工作区只做经得住正确对照、并能说明在哪个抽象层级可复现的结论。

## 2–6. 入驻计划（已完成，保留为历史）
R0 产物审计 → E01 复现已知机制（induction）→ E02 群体扫描（10 seed × checkpoint）→ E03 抽象阶梯（成分身份 / 坐标 / 因果角色 / 算法 / 发育顺序 / 时间）。结果见 C01–C03（Pythia 31M–410M）。之后的触发分支（第二机制、更大尺寸、外部家族、训练干预）均已按证据触发：知识冲突仲裁（E13 起）、DataDecide 交叉设计（E35 起）、受控训练（E46，人已授权补充实验）。

## 7. Ownership / compression

每条有希望的线索都必须回答：
> 为什么这不是“已有的机制分析 + 更多 seed”？为什么这不只是坐标旋转 / 对齐的伪影？

当前回答：(1) 我们用**初始化 × 数据的完全交叉**把方差分解为先天和后天，近邻只变初始化（Bali、PolyPythias）或只变数据；(2) 置换对称性的控制：效应全部来自“同层内哪个头”（层内拆分，E35 / E44），并用置换 / 旋转不变量做对照（E43）；(3) 有干预证据（E46、E48）。强预印本同样占有主张，主旨每次改变时都重扫近邻。

## 8. 论文形态卡（2026-10-03 21:20；按 A02 §8 的同类论文尺度校准后重写；agent 起草，待人否决）
- **Working title:** *The Seed Picks the Slot, the Data Fills It: Nature and Nurture in Language-Model Circuits*（备选：*Seeds Decide Where, Data Decides What*；*Born with a Body Plan*）
- **Hook：** 同一个初始化在 C4、DCLM、Dolma 等不同语料上长出的 1B 模型，选中同一个 previous-token 头的比例是随机的 5 倍，数据的贡献为 0；同一语料、不同初始化的模型只在随机水平。
- **论文形态：** 新现象 + 测量框架（决定因素地图）+ 受控干预（关键期、吸引域）。
- **贡献：** (1) 公开套件中隐藏的初始化 × 数据析因结构及其审计（含 P09）；(2) 决定因素地图：每个机制性质 × {普适、初始化、数据、交互}；(3) 初始化选槽位：14 个尺寸 × 2 个家族，数据分量为 0，坐标继承、内容不继承，权重忘记初始化而角色记得；(4) 数据填内容：强度、出现时间、表示内容、行为由数据决定，不存在幸运 seed，1% 的数据装入由字面模板触发的开关；(5) 何时、为何：关键期（1%–2.5%）、吸引域、规模与语料边界；(6) 对可解释性、数据归因、模型 diff 与评测实践的后果。
- **主图：** Fig 1 钩子 + 设计；Fig 2 决定因素地图；Fig 3 坐标 vs 内容；Fig 4 尺寸曲线（4M–12B）+ 最强头一致率；Fig 5 关键期与吸引域 + 公开套件锁定曲线 + 发育轨迹；Fig 6 开关；Fig 7 不存在幸运 seed。
- **不完美结果的写法（A02 §8）：** 作为边界条件与机制线索写进发现，不在标题上打折扣：小模型 / 代码语料继承弱 → “继承需要规模与早期统计相似的数据”；单头消融图偏弱 → 冗余；开关不由初始化放置 → 晚期功能分布式实现。
- **最近邻（定位表见 A02 §7）：** SeedPrints（ICLR 2026）；Bali et al.（ICML 2026）；PolyPythias（ICLR 2025）；Tigges（NeurIPS 2024）；Achille（ICLR 2019）；Frankle（ICML 2020）；Summers & Dinneen（ICML 2021）；Pre-carved Niches。
- **风险：** E58 若 12B 不继承，则写成“继承在中等规模达到峰值”；E48b 若不成立，开关的证据停留在数据层面的配对与天然实验。

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
