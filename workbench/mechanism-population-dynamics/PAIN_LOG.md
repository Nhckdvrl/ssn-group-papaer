# PAIN LOG — Mechanism Population Dynamics

只记录真实运行中出现的痛点、异常、失败或意外成功。不要预填“我们希望出现”的现象。

| ID | 观察 | 复现条件 / 量级 | 可能影响 | 对应实验 | 状态 |
|---|---|---|---|---|---|
| P01 | **Parent 官方代码与论文文字在 4 处不一致**（kayoyin/icl-heads@c0ba06e + transformer_lens 2.16.1）：(a) `find_induction_heads` 传 `error_measure="abs"`，但 TL `detect_head` 对 list 输入递归时丢掉 kwargs，实际执行 `"mul"`（恰好等于论文文字定义）；(b) 随机 token 先 decode 再由 TL 重新 tokenize：101 个 token 变成 108 个，开头是双 BOS；token 从 `d_vocab=50304` 抽，含 27 个未训练的 padding id；(c) token-loss 消融挂在 `hook_v`，因缓存长度 506 ≠ 505 落入 except 分支，实际是“该头所有位置的 V 换成随机序列 BOS 位置的 V”，不是论文说的 mean ablation；(d) `evaluate_icl_score.py` 传 `--ckpt` 仍加载最终模型；`find_induction_heads.py` 对 Pythia 返回 HF 模型，按发布版本不能直接运行 | 实测：`scripts/` 下 smoke 检查（parent-call == mul：True；== abs：False；except 分支 == BOS-V：True）| parent 的 70M 结论“induction 消融对 token-loss difference ≈ 随机消融”建立在 (c) 这种消融上；induction score 的绝对值受 (b) 影响 | E01 | 已记录；E01 同时跑 parent 原样 / zero / mean 三种消融与 R1b（张量直喂）诊断 |
| P02 | HF API 配额 1000 次 / 5 分钟；全 70M 群体（11 repo × 155 分支）元数据审计需 ~1700 次请求，会触发 429 并连带阻塞下载 | `scripts/r0_hf_metadata_audit.py` 首跑 | 只影响审计耗时 | R0 | 已修：带 token、退避、本地缓存（`results/.r0_api_cache/`，git-ignored）|
