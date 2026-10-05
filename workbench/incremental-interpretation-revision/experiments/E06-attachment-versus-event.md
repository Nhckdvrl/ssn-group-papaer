# E06：自然原句上的 attachment 与 event readout（2026-10-05）

- **状态：** PLANNED
- **类型：** DIAG / measurement repair
- **对应：** C00 / P01 / P03 / P04
- **问题（一句话）：** 事件问句的错误是否伴随句法角色错误，还是在正确句法分析下补全了未被断言的事件关系？
- **触发及范围：** E05 label/断言说明不能修复顺序反转；保留 strict E00 gate，不修改 gate、不进入 Jurayj E01。已给人完整结果和分支输入入口；此实验继续原先授权的 harness 修复，不开线、不扩模型。
- **设置：** 固定已有 Qwen3-8B revision、FP32 frozen、native chat thinking off；全部69 Amouyal lexical sets、GP/nonGP 原句逐字不改。原 event simple/GP questions + 两个 attachment questions：目标 NP 是否 main-clause subject（Yes）、是否 while-clause verb 的 direct object（No）。fixed reg0 demos，不改当前/历史 answer label；两 query orders × 无/一句既有 generic revise，共69×2 conditions×4 questions×2 orders×2 instruction=2208 evaluations。
- **数据构造审计：** 目标 NP 从 initial question 的末尾与 simple question 主语前缀交集确定，并校验在两句中各出现一次（忽略首字母大小写）；69个目标 NP 已逐条与原句核对，所有句子都有且只有一个 while-clause。set_hyp5_14 simple 源题 tomato 单数而句子 tomatoes 复数，目标 NP 明确覆盖为原句的 the tomatoes。set_hyp5_18 源题问 floor 而句子写 road。原 event question/gold 都原样保留，不“修正”后冒充复现；预先报告全69与剔除这两个 source-question 问题的67-set 敏感性分析，不能选赢家。该清洁层只为数据问题，不根据模型结果筛选。
- **至少两个解释及预测：**
  1. syntactic misattachment：event lingering 错误和 direct-object 角色错误共同出现，GP 特有、在两种 query order 下仍有相同方向。
  2. event completion/readout pragmatics：main subject 与 direct-object 两种角色可同时答对，但仍对 initial event 答Yes；nonGP 也有此组合，不能解读成错误 syntax 仍保留。
  3. broad query-order task failure：event 和 attachment 的 simple/lingering 都随 order 大变，无法定位为 syntax 或 semantics。
  4. label-No/default strategy：只对 No 一律拒绝/接受而 Yes subject 失败；joint 要求两个 attachment gold 都正确以排除此捷径。一句 revise 可恢复的结果仅解释为默认行为。
- **读数：** 每 readout×order×instruction×GP/nonGP×question_type 的 accuracy/P(correct)/choice mass；69-set（clean67）paired bootstrap 10000, seed20261005；nonGP−GP；同一 condition attachment−event；joint = subject Yes正确且object No正确、同时 event initial Yes错误的逐 set 比例。No/Yes polarity在对应 readout 中保持一致，不把简单角色题优于事件题自动当机制证据。
- **阳性对照：** 原 event/no-repair 与 E05 standard 的逐条输入 hash 相同；native task choice mass有效；nonGP两种角色皆可答对，不能仅看No role。独立核对 source sentence 一字未改及 target NP 对齐。
- **噪声地板 + MIE：** FP32 E04 max repeat drift2.01e−5/0 flips；比较 order 与 instruction 对 readout contrast 的影响。只有同一读数差在两个 order 下都稳定、nonGP角色控制可靠时才解释其用途；不以单 prompt 正值充 gate。
- **混杂审计：** 任务类型有意不同，显式语法问句可能提供推理脚手架，不能反推隐藏的“真实 parse”；source gold 两个问题事前标记；同模型、同句、同 labels/demos/数值精度；不筛结果，不做跨模型/不可恢复能力/机制/novelty 声明；指令恢复对照符合 R8。
- **决策表（跑之前写）：**
  - 角色控制可靠而 event 初始 Yes仍多、joint 组合跨order稳 → 将原事件 readout 从syntax能力代理中降级，设计能区分语用补全与问句诱导的下一项；仍不追认原 E00 通过。
  - attachment 本身呈稳定GP-specific deficit且nonGP控制好 → 得到新的候选 measurement protocol，先明确记录原 gate 未通过，再让人确认后才注册E01。
  - 两读数都不稳定 / 控制仍坏 → 带全量结果更新人审，不增加模型或参数 sweep。
- **算力预算：** GPU0独立单卡，<0.15 GPU·h；复用现有模型/venv。**实际：** 待记录。

## 结果（跑完后填写；不改上面的内容）
- 数字（含 CI）：
- 结果文件：
- 按决策表执行了什么：
- 主张变化：
- POST-HOC：
