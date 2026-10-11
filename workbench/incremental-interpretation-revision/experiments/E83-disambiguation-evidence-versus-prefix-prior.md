# E83：后到证据与早期字符串代价分开（2026-10-07）

- **状态：** DONE，POST-HOC（由已完成E81整体阴性提出新的读数）；本卡先于任何token分段效果读取，非重写E81主读数。
- **对应：** I02 / C07–C09 / P17，先前解释的修订是否有可用的后到反证，为什么整体读数仍错。
- **问题：** E81wholeSource评分不能共同修复，不再扫模板。已有每token LP能零模型重跑地问：真正消歧后续是否支持正确候选，但先前容易误接的prefix字符串代价把它压掉？这是证据位置/增量更新对象，不是新prompt或修改gold。若分开后仍无共同保持，结束此逆向局部块。
- **数据/资格：** 原E81三族全部raw，不新API/GPU。仅原GP Source已有Step两pass一致、non-null T2索引的词可作landmark；同Source的非null最终索引必须一致，否则冲突/缺失完整记。不要求其它Q重复给出非null、不补T2。cue对应锚词只在原cue中唯一匹配才配对，按原analysis pair全Source/全部Q进入；不能根据模型效果选词/句。原892QA全图E81保留，这一子集单独报告、不能外推到无T2原句。
- **条件/读数：** 沿E81固定候选任务，所有Source字节不变；NATIVE原答案评分、WHOLE_EVIDENCE原E81全Source LP、LATE_EVIDENCE从T2词第一个token开始到末尾的LP（P(later Source | actual earlier Source, proposed answer)）。两个候选同tokens、label LP都排除。主correct/p_correct证据分数、initial/final/all/joint，三族四构式GP/cue/words与letters完整；LATE−WHOLE/LATE−NATIVE及绝对值。paired lexical cluster bootstrap10000 seed83。分数不是校准解析概率。
- **阳性对照：** 按原T2 word字节索引核对；Source target token与原raw一致；prefix+late token LP精确重组whole (<1e-8)，边界仅输入T2元数据。原cue、所有原Q/gold/mapping原样；不将T2缺失作通过，不以词位置后验调边界。
- **噪声地板：** 全mapping flip与CI；零新增model seed/noise，E81batch仪器引用。资格规模由输入决定，本卡不为显著追加样本。
- **混杂审计：** 候选label已在Source之前参与编码，这是可见外部假设条件，不证明原生模型内部同时持有候选。去prefix代价相当于改后验先验/评分目标，不是神经mask因果或等compute新方法。cue词出现更早/重排也保留，不称纯同位置。T2来自不同Q标注、GP合法与可能多parse仍边界。模型尚能在某候选下预测后文，不独立认证该候选的完整语义功能（R8）。
- **定位：** Min已有channel接口，Hanna已有候选共存/QA未复用，Clark已有后到错误证据与rejuvenation；若成立，增量还需具体、因果可预测修订后果，不能只声称晚段更有信息。新颖性定位而非桌面关线。
- **决策表（跑之前写）：** late在三族两构式correct/joint共同恢复并保持cue/另关系→关键语法证据相对支持与整体读数分离，可再做一个精确反证词因果动作，不能立即qualified；只另一关系/极性收益或cue损伤→分数偏好；null/异质→逆向评分整块收束，不加更多suffix长度/landmark/head网格，转E82当前强baseline与完整E70/E67。
- **算力预算：** 0GPU·h、0API；旧raw CPU分析/T2输入资格，完整结果/覆盖/排除理由外置E83。8卡资源用于当前强baseline，标注队列独立继续。

## 结果

尚未读取分段效果。

输入资格冻结：552QA/202S/101clusters/118原pair IDs，MVRR23、NPZ53、NPS23、NPVP2 GP源；SHA d73dc35d1337ae2c94639db10b1c49220bea3b7d2ca8c78b631e98c9f75a689c。不同Q的null保留不确定，但全部非null索引必须一致；模型效果从未用于资格。全部Source拥有initial/final目标；NPVP仅2组，明确不能作该构式稳健证据。三族CPU分段派生完成、Source token identity与重组误差<1e-8通过，0GPU/0API。

## 完整结果与自审

552QA/202S/101clusters，三族/全2016格闭合并读，0API/0GPU·h；map SHA6f922950161b78ada51efcaa25c0f0b12a0943841d2a1dbca4114b3429785fb1。原T2输入资格与排除完整，Source token identity及prefix+late LP重组<1e-8；144mapping/72原prompt长度格保留。NPVP仅2clusters，不作该构式一般证据。504主words GP摘要引用完整地图。

- MVRR GP LATE−WHOLE initial正确率Q/G/L +59.06 [+43.12,+73.91] / +57.61 [+42.03,+72.47] / +31.88 [+18.12,+46.38]pp，final -7.61 [-17.39,+1.09] / +2.17 [-9.78,+15.22] / +7.61 [+2.17,+14.13]，joint +23.91 [+8.70,+41.30] / +21.74 [+8.70,+36.96] / +13.04 [+0.00,+26.09]。三构式初始关系均跨三族正CI；不是全部阴性。
- NPZ GP LATE−WHOLE initial正确率Q/G/L +11.79 [+2.83,+20.75] / +16.04 [+6.60,+25.94] / +49.06 [+36.32,+61.32]pp，final +22.17 [+13.21,+31.60] / +2.36 [-3.77,+9.43] / +12.26 [+5.19,+20.28]，joint +8.49 [-0.94,+18.87] / +10.38 [+2.83,+18.87] / +40.57 [+27.36,+53.77]。三构式初始关系均跨三族正CI；不是全部阴性。
- NPS GP LATE−WHOLE initial正确率Q/G/L +63.04 [+39.13,+84.78] / +56.52 [+32.61,+78.26] / +36.96 [+17.39,+56.52]pp，final +10.87 [-4.35,+28.26] / +10.87 [+2.17,+21.74] / +8.70 [+0.00,+19.57]，joint +52.17 [+30.43,+73.91] / +47.83 [+30.43,+65.22] / +19.57 [+6.52,+34.78]。三构式初始关系均跨三族正CI；不是全部阴性。
- 对原NATIVE，NPZ joint +0.00 [-12.26,+12.26] / -2.83 [-16.98,+10.38] / +38.68 [+22.64,+53.77]；MVRR joint +13.04 [-2.17,+30.43] / +10.87 [+0.00,+23.91] / +4.35 [-13.04,+21.74]。没有共同完整恢复。cue MVRR joint -65.22 [-82.61,-45.65] / -47.83 [-69.57,-26.09] / -39.13 [-65.22,-10.87]，NPZ -37.74 [-53.77,-20.75] / -56.60 [-69.81,-43.40] / -41.51 [-54.72,-28.30]；严重cue损伤全报。NPS GP/控制均提高部分joint，但原cue initial本就很低，不能说GP特异恢复。

自审：后到的条件Source证据能够反转此前字符串代价，初始关系正效应三族/三构式，这是新的有用线索。候选已在Source前被提供，且late边界改变了评分对象/先验，不能将其说成native同时有正确parse或已修好。共同cue保持和完整两关系恢复未建立，E81→E83局部块收束，不继续suffix长度/位置/head网格；不因为仍不合格忽略正结果，也不把条件证据线索包装合格idea。C06–08 L0/C09限定L1不变。下一E82当前强baseline并行，以及更具体的消费对象K地址匹配vsV内容读取（E84一个核心分解），不将Source whole-state换进去的效应直接叫语法变量。无需人决定。
