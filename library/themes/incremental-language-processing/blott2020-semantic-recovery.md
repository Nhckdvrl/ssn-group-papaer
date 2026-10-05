# Recovery from misinterpretations during online sentence processing（JEPLMC 2020）

[作者接受稿与仓储](https://discovery.ucl.ac.uk/id/eprint/10101418/)，[全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9535118/)。读取范围：引言、Materials/design、Discussion、Appendix I前几项；统计附录未全读，不能称全篇校对。

- **形态与idea来源：** 从句法GP扩到词义重释，同时测在线代价与意义连贯判断；来自现有人类句法重分析争论与Lexical Quality Hypothesis，不是LLM benchmark。
- **资产/方法：** 96名成人；48原句框架，每项四种noun条件（coherent ambiguous/unambiguous及两种anomalous），保持其他句词一致；附录含原刺激与词义优势norm，主noun与cue间4–8词，末尾neutral phrase避免wrap-up。
- **读到的结果：** 作者报告ambiguous连贯句37%被误判无意义；正确试次也有约440ms总阅读代价。个别bridge因subordinate meaning熟悉度被去除；不会把这种排除照搬到模型结果后。
- **与我们距离：** 他们已经拥有“lexical ambiguity也会不恢复”和task demands改变解释深度。我们的候选必须回答事件/关系何时被后文再次使用，不能靠从syntax换到lexical当增量。
- **可迁移动作：** 控制词义熟悉度、保持late cue同词、加neutral尾部。附录已含自然published词义句，是未来检验语义重释的现成资产；当前不因此换研究对象或扩构式。

Cache作者稿67页、1,084,077 bytes，SHA256 `844420d9d1ee8c939c7c18953c9f38d99ca387c347d51381320f10e73362aabb`，下载明确无代理。仓储称遵守publisher re-use条款，原文不进git；[OSF](https://osf.io/hn3bu/)数据/代码尚未下载审计。不能将OA当数据任意再分发license。
