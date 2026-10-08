# E27：只添加明确允许患者的匹配关系比较阳性控制（2026-10-05）

- **状态：** DONE
- **类型：** REPRO / PILOT
- **对应：** I01/P11/C04；E26旧活动互补比较都No，不能把平均50%当scope失败。
- **问题（一句话）：** 模型在比较事实与限制时，是固定答No、验证候选命题真假，还是正确使用一致/矛盾比较算子？
- **设置：** 原E26旧活动24source×GP/cue×2role×2style×2question polarity=384Q；只将候选命题患者换为原only明确允许对象（reference-only self/reciprocal，initial-only原NP）。所有passage/question及完整native BASE/REPAIR/模板与E26保持；两独立Luna192审3hash/有效性/事实兼容与矛盾，在推理前完成，gold来自teacher而非parent预期。旧excluded384Q×两模式冻结reuse，新allowed384×base/repair=768任务。Qwen3-8B pinned FP32/SDPA/TF32false/seed0/batch8、无thinking/fewshot/prefill。
- **读数：** allowed/excluded各consistent/contradict的accuracy/PYes/mass、每对both-Yes/both-No/correct-comparison比例，GP/cue/base/repair全报；12verb-family paired bootstrap10000/seed20261005/95%CI、all-clear/prior-faithful共同完整层和每family。原E26不改分数/标签，不因新control事后替换旧主读数。
- **阳性对照：** old允许对象与only事实相同，consistent必须Yes、contradict必须No；excluded相反。避免旧只有forbidden命题让No default和命题验证相同。两个role事实双向，以真实患者替换保持字段/语言语法正确，原same actor/event unchanged。
- **噪声地板 + MIE：** FP32数值漂移小，主要family variation；不按效果阈值停科学探索。不以两问平均50%叫整体能力差，先看operator pattern。
- **混杂审计：** 这里是关系比较instrument阳性控制，不是独立scope能力benchmark或novelty。allowed词汇自然不同，这是目标变换；question/passage/model不改。命题验证如果两问都Yes，需要明确报告而不是筛掉negative问法来卖高scope分；只能作为独立仪器读数讨论后续改进，不能追认旧共同access通过。
- **决策表（跑之前写）：** allowed两问都No → 固定No/关系task不适用解释增强；allowed两问都Yes而excluded都No → 命题验证替代关系比较解释增强，不能叫scope failure；allowed呈Yes/No正确比较 → fixed-No与纯truth-verification不足，追为何forbidden/new-event的operator崩溃；repair改变模式 → task/policy竞争，不扩模型/prompt。下一只有需要时用具体语义解释或事件状态读数直接核对scope，不能反复优化Yes/No标签。
- **算力预算：** 单空闲H20，768新native任务≤.04 GPU·h；旧E26不重跑。**实际：** 65.054s / 0.01807049 GPU·h。
- **命令：** allowed_relation.py build；scoped_access.py adopt；infer.py --experiment E27 --data audited-v1.jsonl --recovery-mode both --dtype float32 --batch-size 8；allowed_relation.py analyze --run $IIR_CACHE/runs/E27。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

384允许命题×两mode768任务；teacher全clear。all12family两GP/cue×两mode的允许命题两问joint正确100%（consistent Yes/contradict No）。base允许consistent PYes GP99.965 [99.927,99.990]%、cue99.809 [99.609,99.948]；contradict PYes GP.0134%、cue.0150%。而旧excluded base两问仍全No，joint0。

固定No、整套问题都在验证命题真假两种简单解释不足；失败特别出现在forbidden/unknown的关系判断，并且contradict问法近似No-default。兼容性也可能被读为支持/蕴含，从“不确定”误到“不一致”；尚不能叫真正scope失效。按决策表转三类关系（entailed/contradicted/undetermined）及独立unknown阳性控制，让已允许、已排除、新活动尚未指定三种状态明确分开；保持相同source/passage，不继续同义词/YesNo提示优化。

[统计](../results/E27-summary.json)、[每family](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E27-per-family.csv)、[配置](../results/E27-config.json)、[audit](../results/D0-E27-question-audit.json)。旧E26不追认为joint通过，不升C04能力主张；I01 PILOT。
