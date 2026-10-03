# Mechanism Population Dynamics

**Status:** **ACTIVE-EXPLORE** — 2026-10-01 human-confirmed  
**Lane:** our-taste / mechanistic interpretability / model science  
**Target:** ICML 2027 / NeurIPS 2027  
**Territory card:** [`../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md`](../../search/our-taste/TERRITORY_MECHANISM_POPULATION_2026-10-01.md)

## 0. Registered object

> **Across independently trained model instances, at what abstraction level is a mechanistic claim reproducible: exact component, causal role, algorithm/function, developmental ordering, or only behavior?**

### 当前进展（2026-10-03 12:10）
**一句话（新叙事，见 §8 与 `experiments/A02-*.md`）：** *Seeds decide where, data decides what.* 同层内由哪个头来做由随机初始化决定，换掉整个预训练语料也不变；成分的强度和模型的行为由数据决定，初始化对它们没有主效应；1% 的指令数据就能装入一个由字面线索触发的行为开关。

| 主张 | 内容 | 证据（已完成） | 补充实验（进行中） |
|---|---|---|---|
| **C05 先天** | 同层内的头身份由初始化决定（层内 SI 0.27–0.34，SD ≈ 0）；“在哪一层”近似普适；数据分量 = 0；早期锁定；集体对称性破缺 | E35–E41；**E44**：Pythia 70M / 160M / 410M 第二家族复现；**训练起点审计**：DataDecide 每个 run 确实从共用的 step0 出发 | E42 因果图与迁移、E43 坐标系 vs 内容、E45 14 个尺寸、E46 受控训练（吸引域、关键期） |
| **C04 后天** | 约 1% 的 Flan 装入由 “Question:” 触发的上下文依赖开关 | E25–E34、E29、E30；**E47**：60M、90M 已存在，同样只对 “Question:” 起作用 | E48 线索替换训练干预、E49 NQ-Swap、E50 开关归因是否由初始化决定 |
| **行为 = 交互噪声** | 初始化对行为无主效应 | E36（12 个条件 0/12）；**E51**：14 个尺寸 × 11 个基准 = 154 个单元，初始化显著 3.9% / 7.8%（= 假阳性率），数据 75% / 98% | — |

**本轮新发现：** P09：PolyPythias 160M 的 weight-seed 变体实际没有换初始化（step1 与标准版 step0 相关 1.0），已改作重跑对照；E44(b) 重新解读为：重跑 ≈ 换顺序（约 0.82–0.85）> 换数据（约 0.72）≫ 换初始化（层内约 0）。同初始化、不同数据的 1B 模型之间线性插值势垒很大（7.5 nats）：初始化决定的是对称性的选择，而不是权重空间里的接近。
**纠错与运维：** P05–P08（见 PAIN_LOG）；E46 首轮因显存不足（每个 run 35 GB）作废后改为分块梯度累积重跑（不改变梯度）。

## 1. Why inhabit this territory

公开的多 run 套件（PolyPythias、DataDecide、OLMo 2 中期训练成分）让我们不用自己预训练就能研究机制的形成。“不同 seed 的内部不同”这类朴素说法已被近邻占据（PolyPythias、Tigges et al.、Bali et al. 2026、Crosscoding Through Time、Polymorphism Is Rotation、Pre-carved Niches），本工作区只做经得住正确对照、并能说明在哪个抽象层级可复现的结论。

## 2–6. 入驻计划（已完成，保留为历史）
R0 产物审计 → E01 复现已知机制（induction）→ E02 群体扫描（10 seed × checkpoint）→ E03 抽象阶梯（成分身份 / 坐标 / 因果角色 / 算法 / 发育顺序 / 时间）。结果见 C01–C03（Pythia 31M–410M）。之后的触发分支（第二机制、更大尺寸、外部家族、训练干预）均已按证据触发：知识冲突仲裁（E13 起）、DataDecide 交叉设计（E35 起）、受控训练（E46，人已授权补充实验）。

## 7. Ownership / compression

每条有希望的线索都必须回答：
> 为什么这不是“已有的机制分析 + 更多 seed”？为什么这不只是坐标旋转 / 对齐的伪影？

当前回答：(1) 我们用**初始化 × 数据的完全交叉**把方差分解为先天和后天，近邻只变初始化（Bali、PolyPythias）或只变数据；(2) 置换对称性的控制：效应全部来自“同层内哪个头”（层内拆分，E35 / E44），并用置换 / 旋转不变量做对照（E43）；(3) 有干预证据（E46、E48）。强预印本同样占有主张，主旨每次改变时都重扫近邻。

## 8. 论文形态卡（2026-10-03 12:10；agent 起草，待人否决）
- **Working title:** *Seeds Decide Where, Data Decides What: A Double Dissociation in How Language Models Form Mechanisms*
- **Hook：** 把整个预训练语料换掉（网页 → 代码 → 论文），induction 头不挪位置；而加入 1% 的指令数据，就会改写模型什么时候相信上下文。
- **论文形态：** 构念引入 + 测量（析因设计、无偏方差分量）+ 受控干预（训练）。
- **贡献：**
  1. 设计：公开套件中隐藏的“初始化 × 数据”析因结构（DataDecide 14 个尺寸、Pythia 标准 / 去重），经 step0 哈希与训练起点双重审计；外加对 PolyPythias 的完整性发现（P09）。
  2. 先天（where）：同层内头身份由初始化决定，数据分量为 0；跨尺寸、跨家族 [E44 ✓、E45 进行中]；按索引看初始化起作用，按置换 / 旋转不变量看则不然 [E43]。
  3. 后天（what）：行为与基准由数据决定，初始化无主效应 [E36、E51 ✓]；1% 的 Flan 装入字面线索开关，60M–1B、两个训练栈 [E47 部分 ✓]，线索替换的训练干预 [E48]。
  4. 如何、何时：早期锁定（E37 / E40），单头初始性质不可预测（E39 / E41）；吸引域半径与关键期 [E46]。
  5. 后果：成分级结论按 seed 迁移，不按数据迁移 [E42]；做数据归因或模型 diff 应固定 seed；配方比较中共用 seed 不能降低 seed 噪声 [E51]；问答格式的知识冲突评测测到的部分是这个开关。
- **主图：** Fig 1 析因设计 + 核心结果；Fig 2 双重分离矩阵（位置 / 强度 / 行为 / 开关 × 初始化 / 数据分量）；Fig 3 交叉分离（索引 vs 不变量）；Fig 4 尺寸曲线 + 家族复现；Fig 5 关键期与吸引域；Fig 6 开关（因子分解、线索、发育、OLMo 2、线索替换）；Fig 7 迁移与“先天承载后天”。
- **证据标准：** 2 个家族（OLMo 式 DataDecide、GPT-NeoX 式 Pythia）+ 受控训练；14 个尺寸；1B 上 5 个初始化 × 10 个配方；3 个冲突数据集 × 2 个训练栈；全部 CI / 置换 / 无偏方差分量。
- **最近邻（定位表见 A02）：** Bali et al. ICML 2026（只变初始化）；PolyPythias ICLR 2025；Tigges NeurIPS 2024；Frankle ICML 2020；Summers & Dinneen ICML 2021；Kim ACL 2026；Goyal ICLR 2025；Pre-carved Niches。
- **风险：** 单头消融的因果图噪声大（E42 初看 SI − SD 仅 0.11）；E46 的小模型能否代表大模型；C04 的机制定位（E50）可能不可判定；线索替换在 2 亿 token 内可能装不进开关（E48 决策表已写应对）。

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
