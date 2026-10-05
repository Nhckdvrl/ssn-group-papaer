# E27：只添加明确允许患者的匹配关系比较阳性控制（2026-10-05）

- **状态：** PLANNED
- **类型：** REPRO / PILOT
- **对应：** I01/P11/C04；E26旧活动互补比较都No，不能把平均50%当scope失败。
- **问题（一句话）：** 模型在比较事实与限制时，是固定答No、验证候选命题真假，还是正确使用一致/矛盾比较算子？
- **设置：** 原E26旧活动24source×GP/cue×2role×2style×2question polarity=384Q；只将候选命题患者换为原only明确允许对象（reference-only self/reciprocal，initial-only原NP）。所有passage/question及完整native BASE/REPAIR/模板与E26保持；两独立Luna192审3hash/有效性/事实兼容与矛盾，在推理前完成，gold来自teacher而非parent预期。旧excluded384Q×两模式冻结reuse，新allowed384×base/repair=768任务。Qwen3-8B pinned FP32/SDPA/TF32false/seed0/batch8、无thinking/fewshot/prefill。
- **读数：** allowed/excluded各consistent/contradict的accuracy/PYes/mass、每对both-Yes/both-No/correct-comparison比例，GP/cue/base/repair全报；12verb-family paired bootstrap10000/seed20261005/95%CI、all-clear/prior-faithful共同完整层和每family。原E26不改分数/标签，不因新control事后替换旧主读数。
- **阳性对照：** old允许对象与only事实相同，consistent必须Yes、contradict必须No；excluded相反。避免旧只有forbidden命题让No default和命题验证相同。两个role事实双向，以真实患者替换保持字段/语言语法正确，原same actor/event unchanged。
- **噪声地板 + MIE：** FP32数值漂移小，主要family variation；不按效果阈值停科学探索。不以两问平均50%叫整体能力差，先看operator pattern。
- **混杂审计：** 这里是关系比较instrument阳性控制，不是独立scope能力benchmark或novelty。allowed词汇自然不同，这是目标变换；question/passage/model不改。命题验证如果两问都Yes，需要明确报告而不是筛掉negative问法来卖高scope分；只能作为独立仪器读数讨论后续改进，不能追认旧共同access通过。
- **决策表（跑之前写）：** allowed两问都No → 固定No/关系task不适用解释增强；allowed两问都Yes而excluded都No → 命题验证替代关系比较解释增强，不能叫scope failure；allowed呈Yes/No正确比较 → fixed-No与纯truth-verification不足，追为何forbidden/new-event的operator崩溃；repair改变模式 → task/policy竞争，不扩模型/prompt。下一只有需要时用具体语义解释或事件状态读数直接核对scope，不能反复优化Yes/No标签。
- **算力预算：** 单空闲H20，768新native任务≤.04 GPU·h；旧E26不重跑。**实际：** 待运行。
- **命令：** allowed_relation.py build；scoped_access.py adopt；infer.py --experiment E27 --data audited-v1.jsonl --recovery-mode both --dtype float32 --batch-size 8；allowed_relation.py analyze --run $IIR_CACHE/runs/E27。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待运行；不把阳性控制本身包装成idea。
