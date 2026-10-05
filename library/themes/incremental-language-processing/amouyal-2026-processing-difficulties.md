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
