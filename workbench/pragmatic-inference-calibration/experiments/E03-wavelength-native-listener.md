# E03：Wavelength 原生 listener logprob 复现（2026-10-02）

- **状态：** DONE
- **类型：** REPRO
- **对应：** C01、C02、P03
- **问题（一句话）：** 原始 graded listener prompt 与评分能否在本地复现，并保留 human uncertainty？
- **设置：** 固定 wavelength-eval Git SHA（E01 manifest）；100条、50对概念、每条40人类响应；AST 提取原 INSTRUCTION 原文；21个 `<answer>0/5/.../100</answer>` completion 的 cumulative logprob 归一化，与 parent backend 一致，包含 chat end token；Qwen2.5-3B contemporary smoke，Qwen3-4B @1cfa9a7208912126459214e8b04321603b3df60c 为论文同型号 anchor（checkpoint时间/原paper SHA未知）。无 RSA/CoT。
- **读数：** parent mean-prediction absolute target error；Wasserstein distance 与 human mean Pearson r；同时保留 parent code argmax error（代码与论文定义不同，不能混用）；原始完整 logprob/分布；100条CI按50个concept-pair cluster bootstrap，2000 draws/seed0。
- **阳性对照：** human mean 与40条response重新复算一致；gold target点质量时 MAE=0，原 human empirical distribution时 Wasserstein=0；原 parent game.compute_listener_metrics 与本地结果一致；token前缀必须严格匹配，否则失败。
- **噪声地板 + MIE：** frozen deterministic logprob；计算重复与human/item uncertainty分开；first/last item batch1与batch方式对照（浮点误差预期 <1e-3）；不以 arbitrary gain 升级 finding。
- **混杂审计：** 不暴露 target给模型；保留 prompt和EOS，禁止默默变成数字单token评分；同一个concept两个clue成簇；clue预筛选择偏差已有parent需记录；训练污染未知；无 binary warrant 标签，不能造SDT。
- **决策表（跑之前写）：** A token/metric parity通过 → full listener anchor；B paper/code读数不一致 → 两读数并报，先审计不解释能力；C contemporary模型跑通 → D2资产，官方强模型数字待复现；不确定 → 两条不筛结果样本的小批核对。
- **算力预算：** 第一轮两模型各 <0.5 GPU·时。**实际：** 待记录。

## 结果
待运行。

### 实现校对与作废（2026-10-02）
全文与parent backends.py继续逐行核对时发现：parent显式 `enable_thinking=False`，初版harness遗漏此参数。Qwen3-4B初次100项MAE=16.4204、r=.7138标为VOID，不作为复现或能力证据；原始文件保留在 `runs/E03-wavelength-qwen3-4b`。Qwen2.5模板未使用该参数，仍全部重跑作为统一审计。修正两处chat template，另存 `E03-wavelength-*-nothink`。目标是复现parent，不把此次修复当prompt科学干预；参数已在运行前落盘。

### 数值精度控制冻结
E08出现BF16 batch-dependent累计概率；固定E03首末项FP32关闭TF32检查max .0002327/.000227（Qwen2.5）、.0000801/.0002785（Qwen3），通过原1e-3阈值。统一按原prompt/completion重算FP32全100条，并报告与BF16重建差。parent vLLM实际dtype/checkpoint SHA未发布到可核对记录，FP32属于numerical control，不声称bitwise原推理复现。仍保留同型号anchor与两读数。
