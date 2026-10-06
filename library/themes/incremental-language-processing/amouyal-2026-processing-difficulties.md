# Comparing human and language models sentence processing difficulties on complex structures — Amouyal et al. `[证据级别：预印本 v1 全文 + release 代码/数据]`

[全文 v1](https://arxiv.org/html/2510.07141v1)、[release](https://github.com/samsam3232/comparing_humans_llms_processing_difficulties)。Territory 登记 ACL 2026；最终会刊版本本次未逐页核对。

1. 论文形态：统一受控行为测量 / 人机比较。
2. 背景与压力：单构式结论难以跨 protocol 比较。
3. 改变的前提：相同 comprehension task 与匹配 control，覆盖七类结构、五家族。
4. idea 来源（DOCUMENTED）：整合心理语言学处理困难，比较跨结构排序和 target/control 方向。
5. 与最近邻距离：相对 Amouyal 2025 的单 GP 研究，扩展构式和统一任务；不据此声称我们的更多模型/结构有 novelty。
6. 方法 / 数据：发布 stimuli、prompts、结果；v1 LLM procedure 写 8-prefix average，实际 release runner 还含 reg/rev，两者需分别记账。用户指定 E00 使用 extended GP 切片。
7. 证据与短板：v1 明确 Qwen3-8B Subject/Object 不保持通常的难度方向；公开 release 也显示 order reversal。评审分数未核对。
8. 可迁移研究动作：先逐条对上发布结果，再区分 calibration-model mismatch 与 instrument bug。
9. 对我们：GP deficit/human comparison 归上游；E00/E03 仅 calibration。后续需区分初始 parse 的支持与最终 parse 可合法推出的语义，不能把同一个 Yes 自动写成 lingering memory。

## 2026-10-06 全文精读补记（arXiv v2，经 GCS 镜像）
- **规模：** 每类结构 40 组（Subj/Obj 沿用 2025 的 45 组）；人类用 Prolific RSVP（每词 400ms、不能回看、问题限时 5 秒、每人只做一题），每题 10 人，共 5,380 个数据点；31 个模型，8 种提示的平均概率。
- **核心 finding：** GP 对 LLM 特别难（GPT-5 非 GP 93.7%、GP 46.8%）；thinking 对非 GP 的帮助更一致，在 GP 上反而常常有害，例外是 GPT-5（Subj/Obj +55、NP/S +47）。随规模增大，结构难度排序与人更接近；"太弱或太强都不像人"（sweet spot）。
- **作者明确留下的问题：** 猜想 GP 难是因为要"从记忆中丢弃错误解释"，并写明"设计实验检验这个猜想是未来的关键方向"。
- **我们的审计**（`workbench/incremental-interpretation-revision/results/D0-Amouyal-released-item-type-audit.json`）：GP 平均值中混入了及物 Subj/Obj 和部分 NP/S 条目，这些条目在无歧义对照句上同样大量答 Yes，属于问题语义问题。真实错误条目（反身 Subj/Obj、RR、NP/VP）上，强模型仍有 25–65pp 的真实缺陷。
- **对我们：** 见 `workbench/incremental-interpretation-revision/SCREENING_2026-10-06.md` 中的 C1。
