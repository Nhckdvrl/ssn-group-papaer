# E01 — Pythia-70M induction baseline reproduction

- **状态：** DONE（2026-10-01；协议在任何结果产生前冻结；判定 = A/B 中间态，交人审）
- **类型：** REPRO
- **对应：** D1/D2；验证 mechanism measurement instrument，不支持 population novelty
- **问题：** 我们能否在一个 canonical Pythia-70M training trajectory 上复现已知 induction behavior / mechanistic score / causal-ablation effect，并沿训练阶段得到可解释的 trajectory？
- **模型：** Pythia-70M canonical run；exact repository/revision/checkpoints 在 R0 artifact audit 后冻结
- **任务 / 样本：** 优先复用 parent measurement 的输入构造；另保留 held-out prompts
- **主要读数：** behavioral induction metric；head/component score；causal ablation effect；checkpoint trajectory
- **阳性对照：** 在 parent 文献明确存在 induction signal 的 late checkpoint 上，measurement 与 causal ablation 应检出预期方向的效应
- **噪声地板 + MIE：** 先用重复输入抽样 / held-out prompts 估计 measurement 与 ablation uncertainty；E01 的 MIE 是“足以确认 instrument 能复现 parent object”，不是新颖性阈值
- **关键混杂：** prompt construction；checkpoint revision；tokenization；head-score 定义；ablation implementation；artifact integrity
- **决策表（跑之前写）：** 结果 A（parent behavior + causal effect 可稳定复现）→ 冻结 harness，注册 E02 population sweep；结果 B（只复现相关性、因果 ablation 不复现）→ 优先修 instrument/parent matching，不进入 population claim；结果 C（artifact/checkpoint 异常）→ 记入 PAIN_LOG 并修 manifest；不确定 → 缩小到 parent exact setup，不扩大模型/任务
- **算力：** inference/activation/ablation only；70M；不得为了 E01 训练模型
- **输出：** accepted checkpoint manifest、可一键复跑脚本、raw per-prompt/per-head metrics、简短 baseline note

---

## Parent audit（2026-10-01，运行前完成）

**选定 parent（exact target）：** Yin & Steinhardt, *Which Attention Heads Matter for In-Context Learning?* (ICML 2025, arXiv 2502.14010)，官方代码 `github.com/kayoyin/icl-heads` @ `c0ba06e`。理由：唯一同时具备 ① Pythia-70M（`pythia-70m-deduped`）② induction score 精确定义 + 代码 ③ head ablation 因果读数 ④ Pythia 训练 checkpoint 轨迹 的 parent。
**定义层 parent：** Olsson et al. 2022（induction head = 在重复随机 token 序列上 prefix-matching + copying，即“经验上提高 [A][B]…[A]→[B] 的概率”；ICL score = loss@500 − loss@50；ablation = 单头 zero / pattern-preserving，仅在小模型上做）。Tigges et al. 2024 只在 IOI/Greater-Than circuit 内部用 induction score，不作为 E01 target。

| 项目 | Parent（论文文字） | Parent（官方代码实际行为） | 我们 |
|---|---|---|---|
| induction score 输入 | [BOS] + 50 个均匀随机 token ×2，1000 条 | 同；token 从 `d_vocab=50304` 抽（含 27 个从未训练的 padding id）；**先 decode 成字符串再由 TL 重新 tokenize**（decode→encode 不保证往返，且会再前置一个 BOS） | 完全沿用 parent 函数（R1）；另跑“直接喂 token 张量”的变体 R1b 作为实现敏感性诊断 |
| induction score 定义 | 注意力落在 induction 目标上的质量 / 总注意力质量 | 代码传 `error_measure="abs"`，但 TL `detect_head` 对 list 输入递归时**丢掉了所有 kwargs**，实际执行默认 `"mul"`——恰好等于论文文字的定义 | 同 parent（实际 `"mul"`） |
| 相关层 / 头 | 70M 的 top induction heads 集中在一层（Fig 19，score ≈0.39–0.42）| — | 读出位置 |
| 行为读数 | token-loss difference = loss@50 − loss@500，10,000 条 Pile | `NeelNanda/pile-10k` 经 `tokenize_and_concatenate`（文档以 EOS 拼接、切成 1023+BOS 的块；位置 50/500 是拼接流中的位置，不是文档内位置）；默认 `n_trials=1000`；循环 off-by-one（累加 1001 批除以 1000） | 同数据构造，固定 2000 条（索引存档），逐条存值做 bootstrap |
| 消融 | “mean ablation” | 在 `hook_v` 上把该头的 V 替换为一条随机 token 序列的缓存；因形状不匹配（505 vs 506）落入 except 分支，实际是**把该头所有位置的 V 换成随机序列 BOS 位置的 V**（≈ 让该头输出恒定的“BOS 值”） | R4a 完全沿用 parent hook；另加 R4b zero ablation（Olsson full ablation）、R4c mean ablation（Pile 上逐头平均 z） |
| 对照 | random heads | 单次随机抽样（seed 42） | 每个 k 抽 20 组随机头，给出分布 |
| checkpoint | Pythia deduped 训练轨迹（Fig 21/22） | `evaluate_icl_score.py` **即使传 `--ckpt` 也加载最终模型**；`find_induction_heads.py` 对 Pythia 返回 HF 模型而非 HookedTransformer（按发布版本无法直接运行） | 兼容性修复：统一用 R0 核验过的 `pytorch_model.bin` 构造 HF 模型，再交给 `HookedTransformer.from_pretrained(..., hf_model=...)`；不改科学对象 |
| 70M 的 parent 数字 | top induction score ≈0.42，全体头平均 ≈0.05（Fig 12）；step ≤512 时 ≈0，step 1000 升到 ≈0.47，末期 ≈0.42（Fig 21/22）；clean TL difference ≈0.62（Fig 9）；**70M 上 induction-head 消融对 TL difference 的影响与随机消融无显著差别**（§4.2、Fig 9，带 exclusion） | — | 这是 parent 自己的 70M 结论，E01 需复现它，而不是把它当失败 |

**因果证据的层级（parent 中哪些是 causal）：** Olsson 的 ablation 证据只覆盖小型 attention-only / 小型带 MLP 模型；Yin & Steinhardt 的 70M 因果结果是“对 Pile token-loss difference，induction 消融 ≈ 随机消融”。**Pythia-70M 上“induction heads 因果地承担重复序列复制”没有被 parent 直接报告**——只是定义层（Olsson）的推论。因此 E01 把它作为预先写定的 Olsson 定义层行为读数（R3）来检验，而不是假定它成立。

## 冻结协议（2026-10-01）

**Artifact：** 只使用 `results/artifact_manifest_70m.json` 中 accepted 的 checkpoint；权重统一从 `pytorch_model.bin` 读取（`use_safetensors=False`），并做张量级核验（见 R0）。
**模型 × checkpoint：**
- A（parent-exact anchor）：`EleutherAI/pythia-70m-deduped`，steps {0, 256, 512, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 143000}
- B（PolyPythias seed 0 = E02 的 canonical）：`EleutherAI/pythia-70m`，相同 steps
- TL 处理沿用 parent 默认（`fold_ln`/`center_writing_weights`/`center_unembed` = True），fp32。

**读数：**
- **R1** induction score（parent 函数原样，seed 42，1000 条）→ 每头 48 个值；**R1-rep** 用 seed 43 再算一次，检查 top-head 排名稳定性；**R1b** 同样 token 直接以张量输入（诊断）。
- **R2** token-loss difference（parent 数据构造），N=2000，逐条值 + bootstrap 95% CI。
- **R3（held-out，Olsson 定义层行为）** 500 条新的重复随机序列（seed 12345；token 从真实词表 [0, 50277) 均匀抽取；[BOS] + r1..r50 + r1..r50，直接张量输入）。读数：第一段 loss（预测 r2..r50）、第二段 loss（预测 r2′..r50′），**induction loss drop = 第一段 − 第二段**（nats）。
- **R4 因果消融**：每个 checkpoint 按该 checkpoint 自己的 R1 排序，消融 top-k，k ∈ {1,2,3,4,7,9}（= parent 的 1/3/5/7/9/15/20% × 48 取整）；对照为每个 k 20 组随机头（不含 top-k 本身的限制不加，与 parent 一致）。三种消融：R4a parent hook、R4b zero、R4c mean（200 条 Pile 序列上逐头、跨位置平均的 z）。读数：R2 与 R3。

**阳性对照：** A@143000 上 R1、R2 与 parent 数字对齐（top score ≈0.42；clean TL ≈0.62）。
**噪声地板：** prompt bootstrap CI；20 组随机头的分布；R1 seed 42 vs 43。
**MIE：** R3 中 top-k 消融使 induction loss drop 下降，且大于 20 组随机头中的最大值（即 >95% 分位）；方向在三种消融方法下一致。

**决策表：**
- **A — PASS：** ① R1：A@143000 top score 在 0.42±0.07 内，且 A 轨迹在 (512, 2000] 出现跳变；② R2 clean 在 0.62±0.12 内；③ R3：所有 post-emergence checkpoint 上，top-k（k≤3）消融的 induction-loss-drop 下降超过全部 20 组随机头，三种消融方法方向一致；pre-emergence checkpoint（≤256）无此效应 → 冻结 harness，写 E02 设计，**停下交人审**，不自动运行 E02。
- **B：** ①② 复现但 ③ 不成立（top-k 与随机不可区分或依赖消融方法）→ instrument 未站稳；查 R1 实现差异（R1 vs R1b）、消融位置、k；不进入 population。
- **C：** ① 或 ② 不复现 → 先查 fidelity（checkpoint 加载、tokenization、数据构造），不换 mechanism。
- **D：** artifact 异常 → PAIN_LOG + manifest；排除后重跑。
- **预注册的预期（不作为 PASS 条件）：** R2 上 induction 消融 ≈ 随机消融（parent 70M 结论）。若复现，结论是“R2 在 70M 不是 induction-specific 的因果读数”，population 仪器应以 R3 为主。
- **A 与 B 的中间态**（例如 ③ 只在部分 checkpoint 或只对 k≥2 成立）→ 如实报告，交人审，不自行放宽阈值。

**偏离 parent（事先声明）：** 不做 FV-head exclusion（70M 的 FV score 近 0，Fig 12；top-2% 只排除 1 个头）；随机对照 20 组而非 1 组；R2 用 2000 条而非代码默认 1000 / 论文 10,000。

**算力预算：** 22 个 checkpoint × (R1+R2+R3+R4) ≈ 1–2 GPU·h（单卡，fvcrc20）。

---

## 结果（2026-10-01；不改上面的内容）

**实际算力：** ≈9 GPU·h（22 checkpoint × ≈23 min；fvcrc20 GPU0/1/3 + fvcrc10 GPU1/2）+ 事后诊断 ≈0.3 GPU·h。第一次启动的旧实现（全词表 log_softmax、parent 路径未关梯度）运行 ≈25 min 后中止并丢弃；新实现与原实现逐元素相等（maxabs = 0.0，四种方法 × 两种输入均验证）。
**结果文件：** `results/e01/<model>__step<N>.json`（逐头 R1/R1rep/R1b、R2/R3、全部 378 组消融）、`*.perseq.pt`（逐条值）、`summary.json` / `summary.md`、`e01_trajectory.png`；POST-HOC：`posthoc_rare_tokens_*.json`、`posthoc_headsweep.json`。

### 按决策表逐条
| 条件 | 结果 | 判定 |
|---|---|---|
| ① A@143000 top R1 ∈ 0.42±0.07；跳变在 (512, 2000] | top = L3H1 0.422（parent ≈0.42，同为第 3 层 3 个头）；step 512 → 1000：0.015 → 0.474（parent ≈0.47）。B（canonical）0.016 → 0.404 | ✅ |
| ② A@143000 R2 clean ∈ 0.62±0.12 | 0.518 [0.333, 0.689]（n=2000，bootstrap）；step 1000 时 0.641 | ✅（点估计贴近下沿；R2 的 CI 半宽 ≈0.18，噪声大） |
| ③ post-emergence 所有 checkpoint 上，top-k（k≤3）三种方法均超过全部 20 组随机头；pre-emergence 无效应 | pre-emergence（0/256/512）全部 ≈0 ✅。zero/mean：A 上 k=2,3 全部 20/20；k=1 为 19/20，**输掉的那一组恰好抽中同一个头（并列）**。parent 方法：A@32000/64000/143000 的 k=3 被含 L0H6 的随机组超过（P03）。**B（canonical）从 step 2000 起，k=3 在三种方法下都被随机组 {5.5, 4.1, 2.1} 超过**；step 32000 后单个 L0 头也超过 top-1 | ❌ 字面不成立 |
| 预注册预期：R2 上 induction ≈ 随机 | parent 方法下部分复现（末期 k=9：12/20）；mean 消融下**不复现**：所有 post-emergence checkpoint 上 top-3 的 R2 效应超过 20/20 随机组（例：A@143000 0.107 [0.068, 0.147] vs 随机最大 0.033） | parent 的 70M 零结果依赖其消融方法 |

**判定：A 与 B 的中间态 → 按决策表如实报告、交人审，不放宽阈值。** Parent 的行为 / 分数 / 训练轨迹在定量上复现；因果层面“注意力分数 top-k 的头是 induction 行为的必要成分”成立（zero/mean 下效应 5–9.6 nats，远超大多数随机组），但**不是**“最强的因果成分”。

### POST-HOC 诊断（不能单独支撑主张）
1. **单头因果图**（`posthoc_headsweep.json`，48 头 × zero/mean，step 1000/8000/64000/143000）：两条轨迹中单个最关键的头都是**第 2 层 previous-token head**——A：L2H7（prev-token 分数 0.87→0.78，R1 0.001），B：L2H1（0.91→0.78，R1 0.004）；单独消融使重复段 loss 上升 7.8–9.6 nats，即几乎全部复制能力。第 3 层 R1 高分头每个 0.6–6.2 nats。这就是 Olsson 的两段式电路（prev-token head → induction head）；parent 的 R1 只识别第二段。B 中打败 top-3 的随机组正是因为含 L2H1。
2. **单个 top 头的因果份额随训练下降**：A 的 top-1（k=1, zero）6.0 → 5.3 → 3.7 → 2.2 → 1.4 → 1.3 → 0.6 → 1.9 nats（step 1000 → 143000），top-3 仍有 5.3–9.1；top-1 身份 L3H6 → L3H1（step 32000 起）。同一条轨迹内的 component turnover + 冗余化（Tigges 型现象，非新）。
3. **后期第 0 层头获得因果相关性**：A 的 L0H0（mean 消融 3.1–4.0 nats）、B 的 L0H0/L0H2（2.5–4.9）在 step 64000 后出现；step 1000/8000 时没有。L0H6@A143000 则方向相反（P03）。
4. **重尾**（P04）：末期随机 token 上的均值 loss 被少数 token 主导；中位数正常。
5. A 与 B 的 step0 权重字节相同（同一初始化），只有数据流不同（deduped vs standard）：prev-token 角色落在 L2H7 vs L2H1，induction 头 {3.6, 3.1, 3.3} vs {3.6, 3.1, 3.5}。**这不是独立 seed 的比较，不作任何 population 解读。**

**主张变化：** 无（baseline 复现不自动升级为 claim；CLAIMS.md 保持 0 条）。
