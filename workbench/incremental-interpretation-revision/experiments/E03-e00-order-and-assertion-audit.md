# E03：E00 顺序反转与断言标准审计（2026-10-05）

- **状态：** PLANNED
- **类型：** DIAG / REPRO
- **对应：** C00 / P01 / P03
- **问题（一句话）：** E00 GP effect 的符号反转来自 question-before-sentence、few-shot bundle、推理数值误差，还是问题诱发了未明说宾语的语用补全？
- **触发：** E00 全 16-prefix GP question nonGP−GP = −2.81 pp [−11.50, 5.89]；句先 prefix 正、题先 prefix 负；order+examples 尚混杂。E00 gate B，不进入 E01。生成工具默认分配 E03，E01 留给 Jurayj。
- **设置（跑前固定）：** 相同 276 QA / 69 lexical sets；2 demo bundles（upstream reg0/rev0）× 2 query orders（独立交换当前句/题，demo 不动）× raw/chat × none/assertion instruction = 16 prompts。所有 cells 保留，不筛 prompt、不改题/gold。
- **一句指令：** `Answer Yes only when the sentence explicitly states the relation asked about. Answer No when the sentence does not state it; do not fill in an unstated object from plausibility.` 与 E00 generic revise instruction 不同，这是解释区分实验，不能倒替 E00 主结果。
- **数值对照：** 同一 suite 在 GPU0 BF16 与 GPU1 full FP32 各跑一次；FP32 softmax、TF32 off。同模型同输入，精度是诊断因子，不扩模型 sweep。首轮 identical prompt repeat 无 accuracy flip，但 probability max drift=0.0865，需追数值来源。
- **至少两个解释及预测：**
  1. query priming：同一个 demo bundle 内交换当前句题即改变 GP/nonGP 的差异；换 demo 不足以解释反转。
  2. demonstration bundle：固定当前 query order 时 bundle 主导反转；order 本身响应小。
  3. pragmatic object completion：assertion 指令优先提高 nonGP GP-question correctness，simple 保持正常，削弱 order interaction；与真实不可恢复 revision deficit 区分。
  4. numerical/instrument artifact：FP32 消除反转或显著改变同 prompt accuracy；若只改微小概率而符号不变，数值误差不解释行为结构。
- **读数：** 每 cell simple/lingering × GP/nonGP accuracy、P(correct)、choice mass；同 set nonGP−GP；query-order × condition interaction；instruction × condition interaction。BF16/FP32 同 item/prompt 的 accuracy flips、probability max/mean drift。69-set paired bootstrap 10,000 draws、seed 20261005。
- **阳性对照：** same-order baseline 须复现 E00 对应 raw_reg0/raw_rev0；simple/nonGP 完整保持可答；instruction 不允许 simple 与 lingering 一起全变 No。
- **噪声地板 + MIE：** 以 FP32/BF16、同 prompt repeat 的差异为数值噪声；顺序交互 CI 与其比较。只以是否足够稳定支持下一步 measurement 作决定，不用固定百分点筛选。
- **混杂审计：** 不重抽 demos；输入保留 hashes；不改上游 gold；question_type 极性混杂仍在。instruction 是有意 task-semantic manipulation，不能当成免费提升而隐去。单模型、可能 benchmark contamination，结论仅本地 instrumentation。
- **决策表（跑之前写）：**
  - query order dominates / nonGP floor → 继续追 question-conditioned parse vs pragmatic completion；不宣布 C00 已通过。
  - assertion instruction 使两种 query orders 上 GP deficit 都稳定为正、simple 正常，且非数值伪影 → 按明确新协议验证 C00，再进入 E01；原 E00 不作废、不改读数。
  - instruction 全面恢复或仍反转 → 将 C00 限为未复现；做最小 task-meaning/role 对照，不扩模型，不越过 gate。
  - FP32 大幅改变 accuracy → 固定 FP32 并复核 scorer/批次，不进入 E01。
- **算力预算：** 两张空闲 H20 独立推理，估计合计 <0.5 GPU·h；无训练。

## 结果（跑完后填写；不改上面的内容）
- 数字（含 CI）：
- 结果文件：
- 按决策表执行了什么：
- 主张变化：
- POST-HOC：
