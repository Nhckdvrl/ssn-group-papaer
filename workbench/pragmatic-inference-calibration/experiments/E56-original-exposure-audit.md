# E56：original-exposure-audit（2026-10-03）

- **状态：DONE。** 先卡，再全量源审计，0 GPU预测。
- **类型：REPRO。** 原noise-exposure设计的材料驻留，不是新科学finding。
- **对应：C02 / P02；I01仍SEED。**
- **问题：** 能否固定原目标句，仅替换原clean/noisy exposure，且不泄漏理解答案或混入其他critical句？
- **设置：** 全11份Gibson公开CSV；原baseline E1–5与noise E6–10配对，逐Item/Condition核对句、问题、literal映射；全部filler/active-passive-control另核对，不凭paper示例重造噪声。
- **读数：** 全量材料去重、同key文本冲突、原两context目标字节一致数；filler slot、list、history可重建性；干净/噪声对照长度与词汇差异。导出只白名单语言字段，不导出参与者身份或答案。
- **阳性对照：** E54已确认前四组80 critical相同；本卡独立核对并要求源导出与E55冻结400句一致。原source标签只能标材料类型，不能变成推断许可gold。
- **噪声地板 + MIE：** CPU确定性核对必须完全一致；无科学MIE。未经本卡审计和独立GPU卡，不开exposure实验。
- **混杂审计：** 原noise manipulation不仅噪声率，也改变具体filler词汇；清洁/噪声句长度未必相等。blocked history不是原随机交错history，不称精确人类复现；不将不同list问题拼成虚假trial、不展示human response。不足时记录缺失，不填造句或自动gold。
- **决策表（跑之前写）：** A固定critical与成套exposure可核对→另卡冻结模型中context响应测量，解释仅限parent intervention；B仅句库可用→只做协议设计，不宣称人类history parity；C源冲突影响待测对照→记录并回到其他独立source，保留主问题。任何结果都不关territory。
- **算力预算：** 0 GPU·时；全量CPU源审计。**实际：** 0 GPU·时。

## 结果
- `results/E56-original-exposure-audit.json`：前四组各80/80 critical完全一致，320句可用于固定目标干预；第五仅4/80一致，保留不加入该对照。每组48 filler槽和48 active/passive control变体；后者逐列表实际12项，不能把变体数当独立场景数。
- 全部四组共用同一套filler，公开两context仅18/48 filler句发生变化（6删词/6插词/6移序），非正文所述30/60。只称release intervention，不补造12句。slot33只末尾空格不同，导出显式rstrip；raw原文件/hash保留，零语义改写、零human response暴露。
- 导出外置`data/E56-original-exposure-materials.json`，来源与SHA保存在result。E55原400critical逐字段归一尾空格后全量核对通过。
- 按决策A/B边界推进E57：固定四类目标测release的exposure响应；不声称完整human history、原30噪声率或纯channel机制因果。
- 主张变化：C02仍L0。
- POST-HOC：无。
