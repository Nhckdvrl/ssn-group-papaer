# Communicative Belief Updates / ImplicatureX — arXiv2026

来源：[v2 primary](https://arxiv.org/abs/2607.25094v2)；[原code/data](https://github.com/cesare-spinoso/ImplicatureX)，commit15d1c58d1d3cb8c198c07ae5c1e63531a672b10d。当前venue未核对，不冒称已接收。

1. **阅读范围：** 完整正文§1–8与limitations，Appendix B的人类评分、D模板、E全部控制与F关键Table6–8已读；A专家详细指令/F其余表图未全部逐项核对。generate_prompts.py、BaseLLM、run.py读数与dataset/原prompt CSV已核对；analysis与原cached数值仍需校对。不是下载即全文读完。
2. **idea来源：DOCUMENTED。** belief negotiation/common ground理论→从识别implicature走到更新其含义；真实Switchboard与PDTB、已有human实验材料。不是造奇怪prompt。
3. **对象/资产：** canonical271（scalar46/discourse31/synthetic conversational144/natural conversational50）。原四control full datasets、两option order，prior542、其他各1084prompt；不取消baseline逐字一致，可复用3252unique。人类90人每批5，Likert7、participant z-score、≥3attention failure剔除。专家agreement.85/.86、κ.34/.32，多数后续仅一位专家，不等于两人全量gold。
4. **已拥有claim：** recognition/cancellation/joint update，人类差距；prior/显式negation/加强/无关续句/type/form/length对照。generic“不会撤回”“prior导致成功”“加强与取消比保持难”都不是我们的novelty。主文自然large-model困难，但Table6中Qwen3-4B recognition=.78与human .78相同、Gemma4B .70；完整size表不能只看largest，这些数字已拥有。
5. **测量：** True/False→1/2首token概率，两order平均。开放模型BF16；闭源每order5samples，human z-score与model概率不在同一尺度。cancel只要P下降，联合还要求initial>.5；Approx保持只要求argmax不变，比delta指标更宽松。额外continuous paired差是诊断，不可叫首次新metric。
6. **校对边界：** prior删除context/utterance同时改问prior knowledge，不能归因单因素。Approx随机移植同类cancellation，可能并非中性，无human norm；“Though I don’t mean to imply…”否定的是speaker意图，不一定事实¬q；不把它们统统叫literal contradiction。source删除some_all_8双否定bug；canonical271均不含此项，submission旧结果与arXiv/regenerated不能混。部分results/index为Git LFS pointers，未取对象前不称cached parity。
7. **本地动作：** [E21](../../../workbench/pragmatic-inference-calibration/experiments/E21-implicaturex-parent-controls.md)跑前卡冻结，5模型8shards原两readouts×271items×6states×2orders，未来OLMoE matched stages。首末数值gate、支持绝对概率质量、保留极小sign变化与invalid边界；只做parent驻留与条件结构测量。
8. **与我们距离：** S2撤回性seed已经有直接近邻；改ownership不关闭territory。可能值得测的是交际证据来源/许可与连续更新的条件结构、stage重新归因；仍无novel scientific finding。自然新增对照先norm/记忆/顺序控制，不能把普通锚定或MCQ策略叫语用特有。

## 2026-10-03公开cache与算术校对（E23–E25）
19个open/nonthinking公开cache已按LFS OID下载保留。源归一化采用BF16全vocabsoftmax后选项再除，True+False偶偏离1；用True>.5与paper的True>False不必等价。自然50项Qwen3-4B原 .78，经pair重新归一诊断为.46；26/50均值落在.5±.001，median order gap .99917。Gemma4B .70→.40；较大模型大部分差较小，**主文自然任务人类差距并未因此消失**。同logitBF16/FP32算术重建，最大sum偏离.00293；精确source cache parity仍不成立，不扩大成新finding，不对未经核对的native源数字自动声称human-like能力。详见workbench results/E24-published-cache-boundary.json/E25-source-arithmetic-control.json。
