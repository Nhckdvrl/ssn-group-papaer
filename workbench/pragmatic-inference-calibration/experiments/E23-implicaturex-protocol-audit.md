# E23：原readout、精度与thinking-prefix工程审计（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / technical confound audit，非新capacity probe
- **对应：** C02/P04/P09，E21 decision C
- **问题（一句话）：** E21 Qwen3-4B与source Table6–8差异能否由optimized forward、精度或thinking-prefix漂移解释？
- **设置：** 预选每4现象sorted IDs首末2项，8items×6states×2orders=96原prompts；model SHA1cfa9a7208912126459214e8b04321603b3df60c。GPU2 FP32、GPU3 BF16，各96×enable_thinkingFalse/True unclosed-prefix。True只是旧prefix实现诊断，**不是完成CoT、不是thinking能力**。保持原expert system与prompt，singleton原model forward(output_hidden_states=True)与optimized next_logits相同tokens；无采样无API。取publicGit LFS原缓存仅Qwen3-4B/no-thinking与Qwen2.5-3B/no-thinking，校验pointerOID+SHA，read-only比较E21原item，不能更改历史输出。
- **读数：** 两forward choice prob/max差、dtype×prefix的per-item P(True)、source-cache paired误差（仅exact system/prompt key）、input IDs与模板尾部hash。原table/canonical271版本分开；从所有被测固定probe看解释，不筛匹配最好的项。
- **阳性对照：** CPU原formatter重建逐字匹配、exact cache keys覆盖；singleton批输入、add_generation_prompt、enable_thinking清楚记录；同FP32optimized-full prob max<1e-6或解释numerical误差；BF16只报告精度差不偷偷换成primary。
- **噪声地板 + MIE：** 工程gate，固定probe非估计人群能力，无bootstrap finding。原BF16/FP32无需必须相同，但大差异阻止parent能力归因。
- **混杂审计：** unclosed-prefix不能叫模型真推理；cached code/权重revision未知，找到更近读数仍不证明完全same model。这里是解释实现差异，不将protocol artifact做paper story。由E21 observed mismatch触发，不事后选择scientific读数。
- **决策表（跑之前写）：** A full与optimized不同→harness bug，隔离受影响E21；B dtype差大→精度边界，先exact singleton protocol复现；C unclosed-prefix更接近cache→报告source protocol不确定，去核对版本，不当capacity；D均不解释→dataset/cache/model revision审计，parent精确复现未成立。
- **算力预算：** GPU2/3独立各≤10min，FP32/BF16同时probe，其他GPU继续队列；无full matrix重复无训练。

## 结果
跑前冻结。漂亮差异先审bug；没有语用scientific claim升级。
