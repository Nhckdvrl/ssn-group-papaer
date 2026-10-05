# E17：原事件依赖与中性实体感知（2026-10-05）

- **状态：** PLANNED
- **类型：** EXPLORE
- **对应：** P10；E16患者特异测量的解释范围、C01/C02。
- **问题（一句话）：** GP的原患者偏好及same/separate调节，是一般实体可及性，还是需要重新调用原事件谓词？
- **设置：** 同pinned frozen Qwen3-8B FP32/SDPA、TF32=false、seed0/batch4、无instruction/question/chat。22作者sources×2原NP选项×GP/comma×none/continued-same/continued-separate×own/other目标NP =528新输入。复用E16原事件患者续写及其E14/E15 own-NP分数；省去began-separate，aspect分解已由E15测过。主7个原episodic source IDs沿用，不重标为neutral句自身的event。全22、两option、all/eligible/acceptable/neutral-role-clear/原episodic分项报告。
- **材料：** S1及桥前缀原样，S2改为外审source actor + later noticed + 作者own/other NP + for a moment。新notice不要求target参与原drying/debate等活动；无semantic gold。两个独立Luna各264逐项审核。cache/E17-material-preparation-v2：v1在任何推理/外审前因NP尾部句号共用whitespace word而替换为v2，加入目标后缀避免目标span混入标点；旧版本与原因均保留，未看模型结果。生成器 `scripts/entity_accessibility.py build` 可重建全部528记录。
- **读数：** 沿用M=bits(other)−bits(own)，D_M=GP−comma；K=D_M_original-relation−D_M_neutral-notice，主看same与continued-separate的K及A_K=K_same−K_continued-separate。同时完整报告两个frame的M、D_M和A_M；两个source NP choices先平均成独立source observation，paired bootstrap10,000、seed20261005、95%CI，逐source。固定目标词差异由交叉配对控制，不是accuracy。
- **阳性对照：** neutral cue应能利用已有entity提及，报告绝对M而非仅差；全部source mention counts不变，NP alternatives同前缀token IDs，HF/manual span loss核对；旧E16概率/hash原样复用。
- **噪声地板 + MIE：** FP32词级漂移≈1e−5bits；7主source抽样宽度为主要不确定性。无任意效应gate，效应大小/CI/逐项模式决定解释。
- **混杂审计：** 两frame的语义谓词及S2结构本来就不同，不把frame交互当隔离某个神经机制。notice新对象需引入新实体，对own/other差值会有基础影响；cross NP choice平均及GP/comma提及次数同一，报告独立ref flags。relation frame重复原verb，neutral不重复，因此若relation特异，仍有verb-NP lexical retrieval vs语义event binding竞争；下一步才区分。不存在教师标签正确率，所有输入评分、selection oddity不按模型结果排除。
- **决策表（跑之前写）：** neutral D_M/A_M也接近relation → 一般entity accessibility足以解释更多，降低event-binding叙事；relation K/A_K稳定且neutral较小 → 原谓词依赖的reuse更受支持，接同词汇合法/非法结构或late explicit role证据控制，不能直接称内部event graph；neutral也有部分变化且K保留 → 混合解释量化，不选漂亮source；CI宽/各source反向 → 查结构与material，不铺新模型/prompt。
- **算力预算：** 一张空闲H20，528新输入，预计≤.03 GPU·h。**实际：** 待运行。
- **命令：** workbench内 `source scripts/env.sh`；`$IIR_PYTHON scripts/event_identity_infer.py --experiment E17 --data $IIR_CACHE/E17-material-preparation-v2/audited-v1.jsonl --out $IIR_CACHE/runs/E17`；`scripts/entity_accessibility.py analyze --cache $IIR_CACHE --new $IIR_CACHE/runs/E17 --out results/E17-summary.json`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待运行；C01/C02仍L0。
