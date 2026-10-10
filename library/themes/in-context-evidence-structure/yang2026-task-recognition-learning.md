# Localizing Task Recognition and Task Learning（ICLR 2026）[主文与H.3/H.4、I.1/J]

[正文v3](https://arxiv.org/html/2509.24164v3)，[正式记录](https://proceedings.iclr.cc/paper_files/paper/2026/hash/974726d56a6ddfac48486e57d5e798e4-Abstract-Conference.html)。Yang / Cho / Inoue。

1. **形态：** 把行为功能与内部组件接起来的几何测量与干预。
2. **压力：** 头消融只报准确率，不能解释功能；TR/TL行为分解又缺内部对应。
3. **改变前提：** 在标签空间内回答、在其中选对答案，需要不同读数。
4. **idea来源：** RECONSTRUCTED；从Pan的行为分解到TSLA、扰动、消融与steering。
5. **距离：** Pan、Todd、Cho电路与hidden-state geometry。一般识别/映射分离已有直接所有权。
6. **操作：** TR分数是head输出在label unembedding张成空间的投影范数；TL是该空间内正确/错误方向的归一化差。再用字符打乱、换label、头消融与添加检验。H.4另做capital+antonym的两输出阶段；I.1保留Qwen中TL/TR steering接近的例外。
7. **边界：** TR ratio是输出属于label集合，不是任选规则的准确率；几何定义、扰动效果与原生完整算法不能混同。
8. **研究动作：** 重要的是用互补读数连接一个自然功能区别，而非消融数量。
9. **对ICES：** 两规则共用标签时，TR ratio可相同而选错规则。不能直接把它改名为Source选择指标；也不能因此称框架无效。当前要解释共享答案空间内的条件映射，具体覆盖须比较任务和干预。
