# PAIN LOG — Mechanism Population Dynamics

只记录真实运行中出现的痛点、异常、失败或意外成功。不要预填“我们希望出现”的现象。

| ID | 观察 | 复现条件 / 量级 | 可能影响 | 对应实验 | 状态 |
|---|---|---|---|---|---|
| P01 | **Parent 官方代码与论文文字在 4 处不一致**（kayoyin/icl-heads@c0ba06e + transformer_lens 2.16.1）：(a) `find_induction_heads` 传 `error_measure="abs"`，但 TL `detect_head` 对 list 输入递归时丢掉 kwargs，实际执行 `"mul"`（恰好等于论文文字定义）；(b) 随机 token 先 decode 再由 TL 重新 tokenize：101 个 token 变成 108 个，开头是双 BOS；token 从 `d_vocab=50304` 抽，含 27 个未训练的 padding id；(c) token-loss 消融挂在 `hook_v`，因缓存长度 506 ≠ 505 落入 except 分支，实际是“该头所有位置的 V 换成随机序列 BOS 位置的 V”，不是论文说的 mean ablation；(d) `evaluate_icl_score.py` 传 `--ckpt` 仍加载最终模型；`find_induction_heads.py` 对 Pythia 返回 HF 模型，按发布版本不能直接运行 | 实测：`scripts/` 下 smoke 检查（parent-call == mul：True；== abs：False；except 分支 == BOS-V：True）| parent 的 70M 结论“induction 消融对 token-loss difference ≈ 随机消融”建立在 (c) 这种消融上；induction score 的绝对值受 (b) 影响 | E01 | 已记录；E01 同时跑 parent 原样 / zero / mean 三种消融与 R1b（张量直喂）诊断 |
| P02 | HF API 配额 1000 次 / 5 分钟；全 70M 群体（11 repo × 155 分支）元数据审计需 ~1700 次请求，会触发 429 并连带阻塞下载 | `scripts/r0_hf_metadata_audit.py` 首跑 | 只影响审计耗时 | R0 | 已修：带 token、退避、本地缓存（`results/.r0_api_cache/`，git-ignored）|
| P03 | **消融方法决定“随机对照”长什么样**：deduped@143000 上单独消融 L0H6——parent 方法（所有位置换成 BOS-V）让重复段 loss +9.5 nats、R2 变负；zero 消融 −2.4 nats；mean 消融 −5.2 nats（反而大幅改善复制）。step 1000 时三种方法对 L0H6 都 ≈0 | E01 随机对照组中恰好抽到 L0H6 的所有 set；`results/e01/pythia-70m-deduped__step143000.json` | parent 70M“induction 消融 ≈ 随机消融”的结论依赖其消融方法：随机头集合一旦含 L0H6 就会产生分布外的巨大损伤。用 mean 消融时，末期 top-3 induction 头对 R2 的效应 0.107 超过全部 20 组随机头（随机最大 0.033）| E01 | 已记录；E02 不应使用 parent 的 BOS-V 消融作为主方法 |
| P04 | **后期 70M 在随机 token 上 loss 重尾**：deduped@143000 第一段/重复段平均 loss 24.4 / 15.0 nats（> 均匀分布 10.8），但中位数只有 ≈13–14.5 / 3.2–4.2；step 8000 时重复段中位数 0.64 nats，64000 起退化 | POST-HOC：`scripts/e01_posthoc_rare_tokens.py`，`results/e01/posthoc_rare_tokens_*.json`；罕见 token（pile-10k 中 <10 次）尾部最重 | 预注册的均值型 R3 在后期被少数 token 主导；与 Howe 2026（pythia-70m 后期 induction 退化）一致；“drop”还会被第一段 loss 的变化污染 | E01 | 已记录；E02 读数需改为对重尾稳健的版本（重新预注册，不改 E01 结论口径）|

## P05 消融钩子作用在未计分的位置（2026-10-03，E28）
- **现象：** E28 第一个模型中，消融前 10 头 / 随机 10 头 / 不消融三者的边际完全相同（4.362 / 6.551）。
- **原因：** 输入为“提示 + 候选 token”，钩子置零序列最后位置（即候选自身的最后 token），而对数概率只用提示末位至候选倒数第二位的 logits → 消融从未作用于被计分的位置。
- **修复：** 只在被计分位置 [len(prompt)−1, len(prompt)−1+len(cand)) 上消融；脚本内置自检：全部头消融后边际平均变化必须 > 0.5，否则 assert 失败、不写结果。第一版结果移至 `results/e28/invalid_hook_bug/`，不使用。
- **教训：** 任何干预类实验，第一个模型必须核对“干预是否改变了被测量的量”（阳性对照之前的操纵检查），并把该检查写进脚本。

## P06 bf16 logits 量化使单条目边际不变（2026-10-03，E33）
- **现象：** E33 内置检查“格式向量有效”在 no_flan default 上失败（单条目边际 2.0 → 2.0），而钩子实际生效（末位 logits 最大变化 1.03）。
- **原因：** 模型以 bf16 输出 logits（数值 ~10 处步长约 0.06），边际 = 两个 logits 之差，小变化可落在同一量化格。
- **修复：** 检查改为比较末位整个 logits 向量（零向量 max|Δ| < 1e-4；真实向量 > 1e-2）。已算结果不受影响（检查不改变测量）。
- **影响评估：** 所有边际读数都带 bf16 量化（单条目精度约 0.03–0.06 nats），在数百条目平均后可忽略；但若未来需要单条目级比较，应改用 fp32 logits（lm_head 以 fp32 计算）。

## P07 `while read` 循环中的 ssh 吞掉任务清单（2026-10-03，E30）
- **现象：** E30 的 3 个 worker 各只执行了 1 个任务就退出（16 个任务只完成 3 个）。
- **原因：** `while read repo rev; do ssh ...; done < jobs.txt` 中 ssh 默认读取标准输入，把剩余任务行读走。
- **修复：** ssh 加 `-n`。所有新 runner 一律用 `ssh -n`。
- **其他运维：** fvcrc13 GPU0/1 被他人 vLLM 占用（各 74 GB）→ 我在这两张卡上的任务 OOM（E29 / E31 / E32 各 1 个）；已撤下这两张卡上的全部 worker、释放占位、改到空闲卡重跑。

## P08 平方和占比在不平衡自由度设计中有偏（2026-10-03，E35）
- **现象：** E35 标量“数据解释 41–87%、初始化 ≤ 3%”；逐头分解时数据占比 0.23–0.30 看似与“数据不决定布局”矛盾。
- **原因：** 3 初始化 × 25 数据无重复设计中，自由度为 2 / 24 / 48；纯噪声下平方和占比的期望即为 0.03 / 0.32 / 0.65，占比被自由度主导。
- **修复：** 一律用均方法的无偏方差分量（σ²_A = (MS_A − MS_res)/n_B）并报告 F 检验 p 值；E35 结论已更正（C05 已同步）。E20 / E36 的 ICC 与置换检验不受此影响（E20 用 ICC(1) 均方法；E36 用置换零分布）。

## P09 PolyPythias 160M 的 weight-seed 变体并没有换初始化（2026-10-03，E44；公开资源的数据完整性问题）
- **现象：** E44(b) 中“异初始化、同顺序”（标准版 vs weight-seed1–3）的层内头身份相关 0.68–0.75。按置换对称性，独立初始化的两个模型在同层内选中同一编号头的期望是 0（“两者皆异”的 seed1–9 对正是 ≈ 0.00）。
- **核查（`scratchpad/pp/check.py`）：** weight-seed1 发布的 step0 与标准版 step0 逐张量不同（元素相关 ≈ 0）；但 **weight-seed1 的 step1 与标准版 step0 / step1 的相关 = 1.0，与它自己发布的 step0 只有 0.0008**；step1000 时与标准版 step1000 的相关 0.987；最终权重与标准版 0.317。→ weight-seed1 实际是从**标准初始化**、按标准数据顺序训练的；发布的 step0 不是真正的训练起点。weight-seed2/3、data-seed1、seed1 的同样核查进行中（`check2.py`）。
- **含义：** weight-seed 变体等价于“同初始化、同顺序”的重跑（只有 GPU 非确定性），不能用来分离“初始化 vs 顺序”。E44(b) 的原分组标签作废，按核查后的真实关系重新标注（见 E44 卡）。
- **教训：** 公开模型套件的“初始化”必须用训练早期的 checkpoint 核对，而不只看发布的 step0 文件。
- **DataDecide 的同样核查（`scripts/audit_init_start.py`，2026-10-03 已做）：** 1B 的 c4 / dolma1_7 / dclm-baseline × 3 个 seed 的 step 2500（最早的非零 checkpoint）权重，只与**自己 seed** 的 step0 相关（0.226–0.235），与其他两个 seed 的 step0 相关为 0.000 ± 0.001 → DataDecide 的 run 确实从发布的、跨配方共用的 step0 开始训练，C05 的前提在训练起点层面成立。
- **对外：** 论文附录报告此发现（对 PolyPythias 使用者有用）；不影响 E44(a)（标准版与去重版的 step0 相同，且两者都是 Pythia 原版训练）。

## P10 在有运行中任务写入的工作区里做 git rebase / stash，会删掉文件（2026-10-03，E48）
- **现象：** (1) 一个“停止跟踪日志”的提交（`git rm --cached`）在 `git pull --rebase` 重放时，把约 1000 个日志文件从**工作区**删除（重放删除型提交会删工作区文件，不只是索引）。(2) E48 的 `90M__default__swap.json` 曾以旧版本（2 亿 token 计划）被提交；新 run 在 stash → rebase → pop 的窗口里写出新版本，pop 后该文件被删除，新结果丢失，悬空对象里也找不到（只有旧版本）。
- **影响：** 1 个结果需要重跑（约 1.5 小时）；旧日志丢失（过程记录，不影响任何结论；所有分析都基于结果 JSON）。
- **规则（以后必须遵守）：** ① 运行中的任务可能写入的路径，不在 git 中移动、删除、取消跟踪；② 同步远端前只提交已经完成的结果，且不在任务写入窗口内做 stash / rebase（或只用不带 stash 的 fetch + merge）；③ 取消跟踪一律按显式文件清单，并预先考虑 rebase 重放时对工作区的影响；④ 日志可能缺失，不能用“有占位、无日志”来判断任务已死。

## P11（2026-10-04）：Pythia-2.8B 的去重版终点检查点与标准版几乎是同一个模型
- **现象：** E58 中 pythia-2.8b 与 pythia-2.8b-deduped（step143000）的角色图层内相似度 0.98–0.99，远高于其他尺寸（0.38–0.72）。
- **核查：** 两个终点的权重直接比较：第 10 层 QKV 权重相关 0.993（最大差 0.021），词嵌入相关 0.985。从同一初始化在不同数据上训练 14.3 万步的模型不可能如此接近（我们测到终点与初始权重相关只有 0.03–0.09）。HF 上的 step0 两者张量完全相同。
- **结论：** HF 上 pythia-2.8b-deduped 的 step143000 检查点实质上与 pythia-2.8b 几乎相同（疑为上传或转换时的混用），不能作为“同初始化、不同数据”的样本。E58 排除 2.8B 这一对（`scripts/e58_analyze.py`、`scripts/figs.py`）。
- **规则：** 用公开套件做“同初始化、不同数据”或“不同初始化”的比较时，除了核对 step0，还要核对终点权重之间的相关：同初始化不同数据的模型终点权重相关应接近 0（与初始化的相关也只有约 0.04），接近 1 说明是同一个模型。与 P09（PolyPythias weight-seed 变体未换初始化）同属公开套件完整性问题，写进论文附录的审计部分。

## P12（2026-10-04）：DataDecide 1B 有 6 个 run 的初始化与其 seed 标签不符——头布局盲测先发现，权重核实
- **现象（POST-HOC，画 ACL 版 Fig 1 时发现）：** 1B 的 75 个模型按 seed 排序画“哪个头”一致性矩阵，同 seed 块内有 6 条暗线：这 6 个 run 与名义上同 seed 的兄弟都不一致（< 0.1），但两两成对一致（0.58 / 0.33 / 0.48）。分别是 seed default 的 dclm-baseline-qc-7p-fw2 / fw3、dolma1_7-no-math-code / no-reddit，seed large-aux-3 的 falcon-and-cc-qc-orig-10p / qc-tulu-10p。
- **核查（`scripts/audit_init_start2.py`、`scripts/audit_step0_all.py`；按字节范围只读第 5 层 att_proj 一个张量）：** 全部 75 个 1B run 的发布 step0 与本 seed 的 c4 step0 对比：恰好这 6 个不同（相关 0.000），其余 69 个完全相同；这 6 个的 step 2500 与 3 个 seed 的 step0 相关都是 0.000；每一对的 step 2500 彼此相关 0.08–0.11，与真兄弟（c4 vs dolma1_7 同 seed，0.074–0.079）相当 → 每一对各自共用一个未登记的初始化。头布局盲测的查准率 / 查全率 6/6。
- **原因：** 小尺寸早已用 step0 哈希筛配方（E45：每尺寸 13–23 个配方），1B 因权重分片没有做哈希核对，E35 用了全部 25 个配方。
- **处理：** `mp_common.UNVERIFIED_1B` 排除这 6 个 run，重算 1B 的全部同 / 异 seed 比较（`scripts/e35_verified.py`、e59、e61、e60、e60_disjoint、e64）。结果全部变强：三种角色层内 SI 0.31–0.42（原 0.27–0.34），9 种角色 0.18–0.43（原 0.16–0.36），seed 识别 1B 1.00（原 0.95），1B 语料距离 ρ −0.76 到 −0.80（原 −0.56 到 −0.60），不共享来源的配方对 −0.76 到 −0.79（原约 −0.5）；逐头方差分量：seed 显著 66–79%、语料 4–7%（假阳性率），语料分量中位数 0。
- **对外：** 写进 ACL 版 Finding 2（“出生证明”的盲测应用）与附录 A；不是“数据集作者标错”，DataDecide 并未承诺同名 seed 在配方间共享初始化。
- **规则：** 任何“同 seed”比较前，对每个 run 核对发布的 step0（大模型用按字节范围读单个张量，几秒一个）。

## P13（2026-10-10）：OLMo-2-0425-1B 在 HF 上的 `main` 不是 stage1 / stage2 检查点所在那次训练的产物——头布局先发现，权重核实
- **现象（E81）：** `main` 与 stage1 终点、stage2 三个 ingredient 终点、SFT 的注意力角色图层内对应只有 −0.07 到 −0.09（同一次训练的检查点之间为 0.96–1.00）；IOI 承担者 13.12 / 14.4 / 15.3，与其他版本（14.4 / 13.13 / 15.9）不同。
- **核查（按字节范围读第 5 层 q_proj 一个张量）：** `main` 与 stage1 step0、stage1 终点、stage2 i1 / i2 终点、Instruct 的元素相关全部为 0.000；stage2 终点与 Instruct 0.976、与 stage1 终点 0.960 → Instruct（及其上游 SFT / DPO）来自 stage2 分支，而 `main` 来自另一次训练（初始化也不同）。SFT / DPO 仓库只有 pytorch_model.bin，未做张量核对，按头布局（与 stage2 0.96）判定。
- **处理：** E81 中“base main → SFT / Instruct”两对不是父子关系，从结论中排除；继续训练链以 stage1 → stage2 → SFT → DPO → Instruct 为准。E30 / E77 / E80 用的是 stage 分支，不受影响。
- **对外：** 与 P09 / P11 / P12 一起写入公开套件审计（用 `main` 当作 SFT 的基座做对比的研究会比较两个不相关的模型）。
