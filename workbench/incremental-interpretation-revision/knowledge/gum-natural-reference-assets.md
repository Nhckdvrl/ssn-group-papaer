# GUM自然指称资产（2026-10-06）[证据级别：上游README/官网/许可/格式与文件hash]

- primary：[官方](https://gucorpling.org/gum/)、[代码与许可](https://github.com/amir-zeldes/gum)。没有冒称全文阅读Zeldes2017/eRST2025论文。
- 选取全部news24＋fiction19文档，非按模型效应筛选；pinned revision与逐文件hash见workbench D0-GUM-natural-reference-audit。43篇原文3.65MB只cache，资源下载无代理。
- 已有coreference/entities、information status、syntax与discourse layers可以连接角色facts和referent身份。尚未外审event-role语义、没有推断。依存obj不是患者gold，coref标注也不自动保证任意截取窗口指称清楚。
- 原文多许可：news CC-BY2.5、fiction CC-BY-NC-SA3.0；annotations CC-BY4。具体source在文件metadata/原XML，保留作者/source署名，不复制原文进仓库。
- 对I01：用于验证人工identity/report/event框架外的角色关系和referential form，不是新建coreference benchmark。自然文本若稀缺所需对比须先统计/外审，不能从可下载推断研究已可行。
