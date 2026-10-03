# Pragmatic Inference Calibration — LLM 语用推断的校准与边界

**状态：PROPOSED；用户授权 D1/D2 驻留、env、全部八卡。** 不改变其他 ACTIVE 线。
**独立复核从[这里开始](logs/review-2026-10-03.md)。更新：2026-10-03。** 目标 ACL / EMNLP / NAACL 主会；升线由人决定。
**对象：** 模型什么时候应该读懂言外之意、什么时候应该停止脑补？更强的语用表现来自更好的语境区分，还是更激进的推断倾向，或二者？
**来源：RECONSTRUCTED。** ALTPRAG gains × PaCE literal-side cost 提供待测压力；不是已证实矛盾或 finding。SDT 只是一把候选尺。

## 现在相信什么

1. **原基线有可核对的复现资产。** Hu 原 Flan 1,365/1,365 选择匹配，概率 MAD=0.000077；TACL2023 原 GPT2 的294可对照surprisal最大差0.000261 bits，BERT8个published例逐项匹配。均是仪器证据。[E04](results/E04-flan-parent-parity.json) · [E13](results/E13-scalar-parent.json) · [E18](results/E18-cross-scale-summary.json)
2. **Multi 原14B已完成四语言×三seed。** maxims accuracy 英/德/韩/中为56.25/52.22/49.03/55.28%；literal为88.89/86.11/91.11/92.78%。德语maxims比论文高9.16pp，解码细节未充分公开；只称走势复现，不称精确复现。
3. **Wavelength FP32、关闭thinking与数值校对已完成。** Qwen2.5-3B / Qwen3-4B / 原14B 的原似然MAE为24.353 /16.406 /18.721；E28 Qwen3-8B/14B为14.435/16.113、两者差CI含零；human MAE=7.226。每模型另有3,200采样回答；采样均值相对原似然MAE差的三组pair-cluster CI均含零。[E17](results/E17-sampling-complete-summary.json) 强现代32B上限仍未跑，不据此称强模型能力不足。
4. **仍不能报告Hit/FPR/d′。** Multi缺候选级推断类别，Hu no-story不是unlicensed，Wavelength是graded判断。25条试标许可分歧9/25、选项分歧61/125；未经gold审查的草案不使用。[E11 human norm](results/E11-human-norm-audit.json)
5. **研究对象须比全局“爱脑补”更精确。** EPITOME已研究知识识别与语用使用；部分知识也能支持排除某个候选。不能把所有partial-access叫negative，也不能把数词的literal信息更新当pragmatic inference。[领域判断](FIELD_SYNTHESIS.md)
6. **有可重复观察，尚无成熟scientific finding。** C03/L1登记OLMo2 SFT→DPO在IQAP三表述下的human Brier差+.313/.342/.377（CI均正）；prior同步变化，能力/机制未识别。格式、位置、数值与原资产缺失归仪器/混杂；C01/C02仍L0，成熟贡献=0。

## 当前只推进什么

**C02 / P02：建立同一候选含义的双侧语境测量。** 先核对现成材料的许可依据与可比性；不足时有针对性改造自然语料，保留原项、变体与独立规范。数据通过语义与技术审查后，再运行模型/阶段矩阵。详见[数据准入](DATA_PROTOCOL.md)。

社会评价、动机评分、角色迁移、噪声修复的额外实验文件与I01已实际删除。E64额外分支已按用户要求停止，停止时六模型完整、两Base部分；此后额外raw按用户要求删除，不做阶段排名。[停止快照](https://github.com/Nhckdvrl/ssn-group-papaer/blob/2738b95a579a4e4c2c1211d8c2f3461cd4a647f2/workbench/pragmatic-inference-calibration/results/E64-stop-snapshot.json)。主线结果和失败记录保留；额外代码/汇总只从git历史追溯。

宽阅读继续服务原问题的竞争解释与测量；每个新实验必须说明如何识别推断边界，不能凭邻接任务的大效应换对象。[对照审计](logs/review-2026-10-03.md)

## 文档与历史

[CLAIMS](CLAIMS.md) · [证据账本](EVIDENCE_LEDGER.md) · [当前研究判断](FIELD_SYNTHESIS.md) · [定位](POSITIONING.md) · [论文形态](PAPER_SHAPE.md) · [论文阅读](../../library/themes/pragmatic-inference/README.md)

核心实验卡、结果与失败保留；额外分支只从git历史追溯，不再留当前计划。见[删除清单](results/cleanup-2026-10-03.json)。

## 资产与复现

- venv：`/data1/xiangding/env/pragmatic-inference-calibration`；[依赖锁](requirements.lock.txt)。
- 原data/weights/PDF/raw：`/data1/xiangding/work/pragmatic-inference-calibration`，不进git。
- 下载默认进程级直连、失败不回落VPN，固定revision与断点保留；[网络策略](NETWORK.md)。
- parent版本/hash见[manifest](results/E01-substrate-audit.json)；每run保留输入、代码与模型指纹，raw禁止覆盖。
- 八张H20可用于独立实验，由GPU锁协调；只停止本项目已核对的额外作业。
- OpenCode免费官方路径已验证可用（E58）；辅助审计有语义错误，不自动当gold。无需子agent。

2026-10-03用户授权清理额外扩展，主territory仍PROPOSED，未升ACTIVE/候选或关闭。

本地额外分支数据已实际删除1897文件、占用约1.47GB；共用权重、核心source/run与论文资料保留。[本地删除清单](results/local-cleanup-2026-10-03.json)；额外raw不在git中，删除后不能由git恢复。
