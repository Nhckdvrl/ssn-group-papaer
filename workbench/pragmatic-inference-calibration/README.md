# Pragmatic Inference Calibration — LLM 语用推断的校准与边界

**状态：PROPOSED；用户授权 D1/D2 驻留、env、全部八卡。** 不改变其他 ACTIVE 线。
**更新：2026-10-03。** 目标 ACL / EMNLP / NAACL 主会；升线由人决定。
**对象：** 模型依据什么交际证据超越字面、调整具体含义的可信程度、停止或撤回推断？进步来自辨别能力、推断倾向，还是二者？
**来源：RECONSTRUCTED。** ALTPRAG gains × PaCE literal-side cost 提供待测压力；不是已证实矛盾或 finding。SDT 只是一把候选尺。

## 现在相信什么

1. **原基线有可核对的复现资产。** Hu 原 Flan 1,365/1,365 选择匹配，概率 MAD=0.000077；TACL2023 原 GPT2 的294可对照surprisal最大差0.000261 bits，BERT8个published例逐项匹配。均是仪器证据。[E04](results/E04-flan-parent-parity.json) · [E13](results/E13-scalar-parent.json) · [E18](results/E18-cross-scale-summary.json)
2. **Multi 原14B已完成四语言×三seed。** maxims accuracy 英/德/韩/中为56.25/52.22/49.03/55.28%；literal为88.89/86.11/91.11/92.78%。德语maxims比论文高9.16pp，解码细节未充分公开；只称走势复现，不称精确复现。
3. **Wavelength FP32、关闭thinking与数值校对已完成。** Qwen2.5-3B / Qwen3-4B / 原14B 的原似然MAE为24.353 /16.406 /18.721；E28 Qwen3-8B/14B为14.435/16.113、两者差CI含零；human MAE=7.226。每模型另有3,200采样回答；采样均值相对原似然MAE差的三组pair-cluster CI均含零。[E17](results/E17-sampling-complete-summary.json) 强现代32B上限仍未跑，不据此称强模型能力不足。
4. **仍不能报告Hit/FPR/d′。** Multi缺候选级推断类别，Hu no-story不是unlicensed，Wavelength是graded判断。25条试标许可分歧9/25、选项分歧61/125；未经gold审查的草案不使用。[E11 human norm](results/E11-human-norm-audit.json)
5. **研究对象须比全局“爱脑补”更精确。** EPITOME已研究知识识别与语用使用；部分知识也能支持排除某个候选。不能把所有partial-access叫negative，也不能把数词的literal信息更新当pragmatic inference。[领域判断](FIELD_SYNTHESIS.md)
6. **尚无成熟scientific finding。** 格式、位置、数值精度、原资产缺失都先归仪器/混杂；C01/C02仍L0，贡献=0。

## 驻留交付与当前实验

| 交付/实验 | 当前证据 | 未完成/限制 |
|---|---|---|
| D1 / E01–E04,E07–E11 | 三parent原数据/代码/协议；原Flan逐项复现、原14B运行、现代模型对照；63,206人类响应对齐 | Wavelength强现代endpoint；许可标签不可靠 |
| D2 / E06,E08,E10,E14–E17 | 一句格式指令、完整选项likelihood、同预算、位置轮换、bare/chat、human alignment、sampling；原文/hash/CI/无效输出保存 | MCQ概率仍是metalinguistic；E14不作paper贡献 |
| E12,E16 | OLMoE真实Base/SFT/DPO谱系、原Hu bare与共用chat模板卡和自动队列 | 三stage已完成E27配对；旧OL chat输入不一致，隔离于stage归因 |
| E13,E18 | 原TACL2023 BERT within-scale、GPT2 cross-scale与三Qwen string predictor已完成 | 未复现concept/GloVe与完整多变量主回归 |
| E19,E20 | EPITOME源评分复现；4模型atomic概率读数完成；E20七模型760题下注完成，E21七模型原四类/六状态完成；E22/Qwen与E26接口配对完成 | IR公开16项仅6完整；Flan atomic协议不可用；生成无效单列，不补prompt救排名 |
| D3/D4 | [PAIN_LOG](PAIN_LOG.md)、[证据账本](EVIDENCE_LEDGER.md)、跑前实验卡 | 未有跨family稳定领域结构；Qwen/OLMoE Base–SFT已测；OLMoE旧chat输入差异隔离，E27完整tokenizer与DPO完成，E29知识控制完成，E28/E31强模型边界完成；E32–34自然强度/备选完成；E36/37一句控制完成；E35第三family八槽完成；E38/E39十端点完成；E42截断校对完成；E43自然commitment十端点完成；E45五端点完成且未过task floor；E41强配对与E46分目标完成；E49/E50联合role与续接读数完成、受readout限制；E51dense四stage自然parent8128完整、四类/方向与候选prior变化待区分；E52强Qwen配对完成、受质量与顺序限制；E53无损格式审计完成 |
| D5/D6 | corpus65,716篇、68篇分级论文卡（全文/局部范围逐卡注明）、作者blog与认知/语义/互动地图 | 最新近邻持续更新；[定位](POSITIONING.md)与[形态卡](PAPER_SHAPE.md)，未到candidate |

**下一未知：** 备选表达、说话者知识、交际问题与新证据，分别如何改变对同一个候选含义的判断？先复现自然parent和检查读数稳健性，再问训练阶段是否改变这种条件结构。不维护预设criterion故事，不为GPU占用制造实验。

## 文档

[territory](../../search/sasano-taste/pragmatic-inference-calibration.md) · [CLAIMS](CLAIMS.md) · [证据账本](EVIDENCE_LEDGER.md) · [领域判断](FIELD_SYNTHESIS.md) · [定位](POSITIONING.md) · [论文阅读](../../library/themes/pragmatic-inference/README.md) · [会话记录](logs/2026-10-03.md)

## 资产与复现

- venv：`/data1/xiangding/env/pragmatic-inference-calibration`；[依赖锁](requirements.lock.txt)。
- 原data/weights/PDF/raw：`/data1/xiangding/work/pragmatic-inference-calibration`，不进git。
- 下载默认进程级直连、失败不回落VPN，断点/固定revision保留；[网络策略与实测](NETWORK.md)。
- parent URL/commit/SHA：[manifest](results/E01-substrate-audit.json)；每run保存模型revision、脚本/输入/协议指纹。
- 独立8×H20约96GB，GPU文件锁协调；未杀其他使用者进程，无多卡训练。
- OpenCode已安装；LongCat旧403，MiMo当前429；Ling3.1官方CLI smoke回复OK/cost0，E58原20条辅助审计完成/cost0，18技术有效但语义错误/分歧待核，不当gold。用户随后禁止子agent，本轮直接执行。

```bash
source workbench/pragmatic-inference-calibration/scripts/env.sh
"$PRAG_PYTHON" workbench/pragmatic-inference-calibration/scripts/prepare.py --root "$PRAG_ROOT"
"$PRAG_PYTHON" workbench/pragmatic-inference-calibration/scripts/check_scoring.py "$PRAG_ROOT/data/multiprageval.jsonl"
"$PRAG_PYTHON" workbench/pragmatic-inference-calibration/scripts/summarize_sampling.py --root "$PRAG_ROOT" --output workbench/pragmatic-inference-calibration/results/E17-sampling-complete-summary.json
```

具体参数/结果/失败见E01–E63。raw run禁止覆盖；旧thinking/BF16/target-padding失败原文件保留但隔离。2026-10-02用户授权PROPOSED驻留；没有升ACTIVE/候选或自动关闭territory。

E23–E25公开cache/浮点/顺序校对只属于测量修复。E26八卡全完成；E27三阶段完整tokenizer与BOS配对全部完成；E29八模型知识控制完成，部分入口/极性不能识别；E30有界数值校对；E28/E31强现代8B/14B全部完成；E32–34自然语料与期望矩阵完整；E36/37单句恢复控制完整；E35固定Mistral Base/Instruct完成资产/完整前缀预检八作业已完成；E38/E39原35200生成完成；E42截断校对完成；E43十端点5280calls完成；E45十独立作业800calls完成但五端点未过无歧义floor；E41配对14B25508完成；E46更强分目标1056完成；E47原人类source/norm核对完成；E48仅数学账户校对；E49/E50共15552原source联合role/readout读数完成、暂不升能力；E51完成dense四stage自然parent配对。任务视角仍是交际证据的条件使用，没有成熟论文claim。

自然IQAP chat方向正确4B/8B/14B为61.33/73.33/85.33%，但完整候选terminal与无QA词汇prior有明显影响。Circa条件回答多数能正确保留；负强度读数顺序敏感，单句strict可改善强侧同时恶化弱侧，不称能力恢复。两组均未提供通用SDT gold或成熟novel finding。

E42发现5196原非EOS数字中3677延长后变prose，相关旧scalar解释隔离。E43聊天Q3-14B事实64/64、初始意图7/8；分目标八材料效应与全部缺失bounds已保存，尚无跨family/readout能力finding。原源、人类规范与paper ownership分开，最新读数优先审bug与task floor。

深读补充：Mayn2025正文/附录/原models.R、Weak Evidence2022最终正文/关键代码、NMI2026公开v3正文主线/Methods、Confidence-Commitment2026核心论证/方法/Fig9、Roleplay2026正文主线、SDA2026重点章节；未读补充/代码与photo迁移限制明确。下一未知是speaker表达选择预测能否约束listener解释；generic Knowing vs Using、confidence/criterion分离与role asymmetry都有近邻，不卖空白或新metric。E49文本迁移与派生speaker任务仍非精确human effect复现，E50自然续接不是透明knowledge探针。

E52强Q25自然配对4064完成：IQAP方向上升与人类四类Brier变差同存，但Base candidate mass极低、Instr null prior偏probable，不能能力归因。E53只审计无损格式，不改E49 primary；四endpoint恢复大量有效列表但控制仍未共同成功。E51八槽8128完成，冻结collector核对汇总、不自动升级claim或开新实验。

I01证据来源归因保持SEED：合理修复与无依据意图补全的边界，不能缩成单一prompt缺陷。E54/E56原材料全量审计，E55八端点12800完成，E57八端点23552生成全部完成、semantic controls/跨端点方向尚未共同识别；公开noise18句与正文30不符，前四类320critical固定，版本/控制/invalid边界保留。[数据规范](DATA_PROTOCOL.md) · [I01](ideas/I01-evidence-type-inference.md)。

E59八卡7392完成，OLMo SFT→DPO三措辞Brier差+.313/.342/.377、CI均正，原1800行零差；无对话prior也变，不能归因能力。[图与全量结果](experiments/E59-interpretation-wording-stage.md)。E60原17280cache/752human核对，ELM动机/知识新parent驻留；E61八卡12576读数完成，人物评价/motive变化不统一，但motive支持质量不稳，未识别能力分离。E62原人类理由/人物评价4192行已审；E63八卡11040读数运行，以原14scene理由改变检查条件响应，单句/读取控制全保留。
