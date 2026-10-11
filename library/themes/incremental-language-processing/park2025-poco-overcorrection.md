# PoCO：把过度纠错变成候选生成，再恢复不该改的部分（EMNLP2025）

1. **来源/范围：** [正式论文](https://aclanthology.org/2025.emnlp-main.1431/)，POSTECH/ETH Zurich。主文§1–7、Limitations pp1–9全读；AppA p13全文/提示/表9全读；参考文献未逐项核对、代码未审。PDF13p外置SHA bbf071dbef8602ed611bfcd7f24addea452ba329ee4609e87241c2002e14c094。
2. **压力/idea来源（RECONSTRUCTED）：** 小监督GEC保守、高precision低recall；LLM相反→不一味压制LLM多改→刻意扩大错误候选→小T5同时学gold与recovered两目标，后一目标只保留LLM已改且gold允许的编辑。改进来自重定义两个阶段的职责和监督接口，不是空白领域或新的模型结构。
3. **近邻距离：** Fang CoT约束改动、GRECO给候选打分、ESC多模型edit ensemble已存在；PoCO用大模型反常弱点生产训练输入，再恢复错误编辑，也补未改错误。Recovered目标利用训练gold构造，不是推理时拿gold恢复；小模型推理仍看original+overcorrect。不能直接叫一般self-correction首次。
4. **数据/方法：** Clang8预训练不使用LLM输出，W&I+LOCNESS阶段才生成/训练；BEA19 dev/test、CoNLL14原成熟数据。GPT3.5-0125、temperature1生成；T5 base/large、lr1e-4、batch64、10epochs；Seq先gold后recovered，Mix混合双目标。整任务不是3个LLM族机制，baseline多数取既有报告，API版本差单独给出；未核对源码split精确条数。
5. **结果及反证：** 同GPT0125 CoNLL14诱导过改recall53.9→57.9但F0.5 58→55.5；不是单prompt整体胜。T5large Mix BEA19 test F0.5 75.7/recall67.8，Gold73.0/69.7，Recovered74.7/63.4；CoNLL14 Mix65.1低于Gold65.4，不能称全集最优。三seed仅主Mix的BEA test均值75.64±.1。LLM直接postcorrect进一步降precision/F0.5；不是所有改写越多越好。主文meaning4.98与App表Mix/Seq4.92不一致，50项GPT4.1评分无独立人工语义保证。
6. **对GP怎样借：** 学“让候选搜索和语义保持承担不同职责”的动作，而不是复制GEC或把overcorrection认定为GP原因。我们关心合法Source未要求改写却被错误解释，尚无实际编辑证据；需要先证明修订对象及后果。若只有指令敏感性或一个小模型收益，不足以形成新故事。原成熟数据可直接用；新增模型输出/改造文本才需要API语义审核。当前不新开GEC线、不以它已研究过改写为由关GP。
