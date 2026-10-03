# E45：BWIM原confidence协议有界pilot

- **状态：** RUNNING
- **类型：** REPRO / D1–D2；先原反馈基线，不改问答loss/agent框架
- **对应：** C02/P09
- **问题（一句话）：** 本地强open endpoints能否在目标行为反馈中保持literal task成功，同时让implicit解释的confidence有partner区别，为后续实际决策测量提供有效基线？
- **设置：** E44原generator/64CSV与paper Appendix A.1，五已有端点Q25-3BInstr/Q3-4/8/14/MistralInstr；固定原seed0–3、每seed40turn。每model分偶/奇两GPU作业，共10jobs按8锁，总800trial generations。完整native chat/system/assistant/feedback history，session每seed独立。FP32/noTF32/single/greedy/max512，Q3 no-thinking；完整raw与input/IDs/LP/config。原confidence实现未发布，明确协议迁移而非精确parent数值复现；只原反馈、无QA/API。
- **读数：** whole Coordinates…Rating:1–4 strictparser，no prose抽取；客观target coordinate集合（原表）完整相同才correct，重复/非法/缺块不接受。完整已EOS作为available；invalid/truncated不叫语用失败。原b结构preference、fully/under objective正确、confidence分partner/block-quarter，四种source/truth条件全报。不能把literal partner b选择一律FPR，其target本来4/12可b。
- **阳性对照：** E44源全量gate；首trial生成重复ID一致/LP<.001，context/history hash；每seed两partner16×4=64controls/model，保留全体，与under分别看。完整source system、事实target反馈正确；反馈只对model实际答案与source target，不能偷偷oracle示范代替答案。
- **噪声地板 + MIE：** 四episode随机材料/名字/order，不是模型训练replicate；仅pilot不估顶会级稳健性。若没有基本task/parser可用性，不解释partner/pragmatic差异。fully ≥95%且所有critical完整只是后续适用性参考，不是自动科学结论。
- **混杂审计：** 两lists与固定sourceordering，四seed与paper30不同；无原human逐trial norm。model native generation含格式adherence，固定512不继续救分。完整history长度每turn≤checkpoint maxcontext，否则失败整episode保留；无截断历史。连续user反馈/下题合并为同一user，source text不变。Mistral官方模板system可能移到lastuser，明确入口实现边界，不能架构因果。成功结构可来自习惯，不等于RSA计算证据。
- **决策表（跑之前写）：** Afully成功且两partner confidence选择保留parent→强成功baseline；Bfully失败/format差→本端点不适用，不解释infer-policy；Cfully成功但partner区别不足→先原30seq/independent审计再候选观察，不绕过BWIM ownership；D超长/OOM/数值gatefail→实现失败，保留，不剪history改变对象。任何结果不自动开关线。
- **算力预算：** 五端点四sourceepisode共800完整greedy，最多512输出，十独立jobs八锁；不调用API不training。原数据小、已下载权重，E41 ready时同锁排队，预计<8GPU·时；实际walltime/config全记。

## 结果
E44 CPU/source/history门已通过；十作业八GPU锁运行，800trial generations，尚无全矩阵结果。无需新标注，C01/C02仍L0。
