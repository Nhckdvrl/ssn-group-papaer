# E36：肯定式角色证据，还是显式否定备选项？（2026-10-06）

- **状态：** DONE
- **类型：** PILOT
- **对应：** C05 / I01 / P11；核心account边界，不是同义词/模型扩容。
- **问题（一句话）：** 新事件患者预测的反向作用依赖显式not-X-but-only-Y，还是在仅肯定限定患者、另以非角色方式提及X时仍存在？
- **设置：** 固定E29旧event和E31 same/different predicate×same/otherActor的named材料24source/12family。数据构造者Luna独立写每source两种only肯定role事实，去掉not/but/rather/instead；被排除实体仅在report-mentions句被提及，不说它实际在场或参与。提及句交叉置于role句前/后，控制最新提及顺序；共raw1920，native672×base三map/repair一map=2688。保留原contrast parent冻结分数作第三realization比较。全部完整rendered数据先另两Luna逐条审核，未审前不推理。
- **读数：** M=bits(otherNP)−bits(sourceNP)，D=source-only−reference-only，J=D_activity−D_neutral；每realization分别old positivecontrol、sameV/differentV×两actor，主读数affirmative mention-first的otherActor/sameV J及different−same J；mention-last是预注册顺序敏感对照，两者全报。native old支持/排除、new U及signed-role迁移、cyclic mappings/一句scope恢复；不合并likelihood与类别概率单位。family两source平均paired bootstrap10000/seed20261005/95CI，all/eligible、E31 frozen anchor-clear11/acceptable9/parent-faithful9、共同语法acceptable层（审计后跑前冻结）。
- **阳性对照：** oldevent D/J与old supported/excluded NLI，unrelated U；原E29/E31固定contrast实现，未改字节的后缀/target hash核验。若新肯定句不能传达old role，不用new消失来否定核心解释。
- **噪声地板 + MIE：** 12family独立n而非1920inputs；固定FP32。判断pattern/CI，不设置自动scientific-yield阈值。native映射变化独立报告，不挑高分map。
- **混杂审计：** 去除显式否定同时改变句数/focus/discourse，不能说pure negation ablation。only仍是排他focus，因此保留一般focus alternative竞争。self/each-other作mentions对象需改写为actor实体，不能严格同词袋；source NP mention次数跨role固定，matched-neutral和mention-first/last共同检查entity/recency。语言性report提及不等于物理在场；只有only句定该旧活动患者。没有真正revision history，不能用此追认纠正后残留。
- **决策表（跑之前写）：** old控制有效、new反向及predicate差在两顺序均保持 → explicit not-alternative不是必要条件，candidate收敛到事件身份调节排他role evidence的后续使用；一般focus/contrast仍待区分。只mention-last反向 → 最近提及/entity解释增强，不能叫稳定role机制。两顺序old有效、new消失/转正 → not-contrast realization成为核心边界，不能用先前E33声称一般semantic revision。old无效/审计不清 → 追材料why、保留无效源及冻结敏感层，不盲目加模型。继续I01不自改状态/不写论文。
- **算力预算：** GPU1raw/GPU2nativebase/GPU3repair单卡独立，已有venv/frozen Qwen3-8B FP32/batch4或8 seed0；≤.15 GPU·h。**实际：** .091870 GPU·h（raw1920/native2688）。
- **命令：** `affirmative_role.py build/adopt/analyze` + `event_identity_infer.py --experiment E36` + `event_constraint_state.py run --experiment E36 --mode base/repair`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

## 跑前数据核验（2026-10-06）

独立构造者Luna给24source×两角色48肯定句；另两审分片共2592完整输入，分片0全部mention-first、分片1全部mention-last，非同句双审。所有ID/sentence/target/proposition hash一致，raw1920/native672均faithful/eligible；native96E/96C/480U全部clear且与原role gold一致。两审语法有不同边缘标准，raw/native分布见[审计](../results/D0-E36-affirmative-audit.json)，共同acceptable层预先按两form完整覆盖冻结。FP32 tokenizer1920 causal contexts与目标核验通过。跑前发现旧prepare grouping尚未区分fact_realization，已加metadata discriminator，句子和标签未变、任何推理前修复。

## 结果2026-10-06

[完整统计](../results/E36-summary.json)。预注册affirmative mention-first old J+2.296 [1.194,3.357]bits、otherActor sameV new J−1.790 [−2.739,−.838]，different−same J+1.352 [.352,2.325]；sameActor sameV J−.702 [−1.896,.589]不确定、predicate差+1.280 [.528,2.027]。显式not-X不是otherActor反向作用必要条件，only/focus/叙事alternatives仍在，不能说去掉所有focus。

mention-last old J+1.048 [.313,1.831]，sameActor sameV−1.440 [−2.634,−.182]、predicate差+1.241 [.469,2.020]；otherActor−.246 [−1.392,1.030]与predicate差+.596 [−.145,1.310]皆不确定。因此不能声称all-order稳健otherActor极性。共同grammar8 otherActor first−2.239 [−3.366,−.929]、last−.983 [−1.918,−.002]，但last oldcontrolCI跨0；all/8及anchor-clear11/acceptable9/parent9完整保留不挑结论。

NLI first old-source91.67 [86.11,96.53]%、old-reference81.94 [77.08,86.81]，newother同V U85.42、不同V93.06；last old两roles均68.75%，newother同V92.36不同V97.22。改写同时影响任务解读，不能当pure negation causal效应。C05 L1补充边界与negative-alternative非必要性；E37直接短语role retrieval追E34/NLI failure，下一明确independent selection区分叙事合理对比与spurious跨事件依赖，而非继续小词控制。
