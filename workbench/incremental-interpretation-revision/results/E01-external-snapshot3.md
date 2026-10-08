# E01：较大外审固定批次的语言操作图

三卡完整4632任务，0.097710 GPU·h；279变体/1158eligible QA。四配置：neutral/native句先/题先×base/一句repair。独立单位是source lexical set，每个contrast使用实际配对交集，不把缺失audit当无效句。PYes为主；correct仅外部MiMo标注agreement，非人类gold能力。

## 对下一研究动作有用的读数

NPZ initial-event extension DiD = (GP long−short)−(comma long−short)，同9源组：

| query order | instruction | 差值 pp | paired 95% CI |
|---|---|---:|---|
| sentence first | base | +51.63 | [21.60,84.02] |
| sentence first | repair | +40.98 | [15.09,67.95] |
| question first | base | −20.29 | [−53.11,9.93] |
| question first | repair | −10.66 | [−32.92,.79] |

方向随任务次序变化，不能将所有extension说成承诺加深。也不能据此单独主张任务驱动parse，因为Q影响可能是读出/引用/语义补全，E08/E12已有竞争证据。

NPZ句先base，原final-role long−short：GP −30.36 pp [−60.26,−1.53] n10；nonGP −24.41 [−47.20,−3.46] n13；comma −9.57 [−23.02,.05] n15。相应final-event在comma/nonGP接近ceiling，GP差−1.65 [−26.54,21.86] n10。与E11引用问题相符，不称内部syntax/meaning能力分裂；NP复杂度/问句指代仍需控制。

NPS句先base final-event extension DiD：eligible −8.49 pp [−25.41,约0] n8，但预登记acceptable stratum仅−.027 pp n7。差异源为NPS:7：GP long含原非标准had rode，外审marginal，PYes=.3232；同组comma long PYes≈1，短句两条件≈1。保留全部原结果与两个strata，不事后删除该源组宣布机制。

MVRR句先base final-event extension DiD +17.45 pp [−.14,45.28] n7；其它三配置点值正但幅度不同、部分CI跨0。只是构式分项，不叫跨构式generalization。

## 当前解释与下一高信息动作

更大的独立词汇覆盖仍不支持“延长统一增加承诺”或“所有低role回答说明旧parse没修好”。下一步拆开歧义等待长度、modifier提供的事件信息和NP引用复杂度：先对原modifier与初始事件的关系作独立外审，再用语义信息/位置受控且逐条审核的语言操作区分解释；不追加更多query模板找赢家。E13自然S2主效应小且CI跨0，提醒用真正有区分力的后文依赖，不能将任意整体概率或No回答当修订成功。

完整四配置、两strata、所有pair IDs与CI见[E01 JSON](E01-external-snapshot3-summary.json)，数字逐条表见[CSV](https://github.com/Nhckdvrl/ssn-group-papaer/blob/859e48c87cfbecaf017c0fd8e286ef18f59a61cd/workbench/incremental-interpretation-revision/results/E01-external-snapshot3-scores.csv)，来源/模型/代码和三个完整子run见[config](E01-external-snapshot3-config.json)。C01/C02仍L0；没有自动科学停步gate，没有已证成的新idea。
