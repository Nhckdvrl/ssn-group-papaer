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
