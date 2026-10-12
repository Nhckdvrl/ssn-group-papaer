# 论文组织去重的独立审计（非科学完整性或接受判断）

按 EXECUTION §5，对基线commit0d6fb6c8之后的PAPER_DRAFT/PAPER_APPENDIX/build_paper组织变更独立校对。最终结论：三项认识和实测范围保留；去重后的主文仍清楚连接provenance→formation→source-conditioned use及公共背景协调。没有发现尚需新增实验的支持缺项。

Abstract/Introduction三项认识、关联内容§4及Qwen32§6.6逐字不变。MC1仍有固定系数actual-donor预测和无donor的原生边移除/受限恢复；MC2仍固定labelstream/位置/输入多重集，以跨类对同类交换区分部分关联内容；MC3仍交叉selective/all/query政策，并接到public Source→word-set在private监督隔离时的形成收益与等价背景cache兼容性。§6.2保留fixed-A-word B-convention response下降，使accuracy收益明确连接关系影响。

主文3表内容逐字对应原第1/4/6表，caption分别为native操作、real SST政策、跨规模三环，与实际字段一致。3张移图逐asset在附录C/D/J存在：controlled功能tradeoffs、native移除/恢复、shared/separate cache compatibility；原长解释也保留于相应附录文字。总图数仍15（主文3/附录12）；没有删除或重算图中数据。删除的主文E121表已逐字存在于D；controlled全部政策和A/B/agreement完整表在C，E127 primary/S/secondary各表在J。

改写数字对应正确：§6.1的88.3–99.2%来自D的四模型×双private方向8格；KV rule correlations .931/.948/.930/.966一致。§6.5 shared/opposite四gain分别8.89[6.64,11.13]、5.86[4.10,7.71]、.78[.10,1.56]、9.38[7.32,11.52]pp与J相同；coherent joint-reading的两Actor平均约53–65%、criterion约50–53%均为原表的整位概括，不是simultaneous joint-success概率。S的gold-A request差定义与其correct-margin等价性保留，未当成另一个独立mechanism/latent指标。

审计中三处具体修正均已落实：§5.2原“not uniformly positive”错误地描述了全为正的A/B点估计，现改“not uniformly confirmed”对应部分CI跨零；§6.2恢复B-code response与功能收益直连；§7明确Yang的label-space alignment/within-space mapping与Li的task composition/remapping各自所有权。22个原primary链接全部保留，其余近邻贡献没有被改写为本项目首次发现。Related/Discussion不声称唯一算法或所有模型通则。

独立Limitations完整保留recipe与size不可分、固定aspect顺序、有限Cue/其他native路径、unmodeled paths、unequal edge masks、actual donors、multiple comparisons、constructed private conventions/SST预训练及实际应用有限的边界。 agreeing-label代价、Mistral separate full-output损失、非普遍最佳政策、共用词无法辨Source、非binding ID/完整criterion program仍在正文或明确链接的附录。

构建器AST除CAPTIONS外与基线相同；官方style/书目未改。当前编译稿30页，主文3图3表、附录12图26表；manifest与最后MD/脚本/PDF SHA一致。末轮Warning/undefined/Overfull均0；视检第4、6、8、9页及三张移图所在18、20、28页，没有遮字或裁切。主文4344个whitespace tokens是文本计数，不代表会议页数限制已经满足。

本次阅读范围：完整scoped diff、所改§3–6/Related/Repro/Discussion/Limitations、相关附录C/D/F/G/H/J/K和当前构建；使用已封raw/report含义核对，没有重新执行历史全套数字审计/GPU或新增control。旧12-stage数值、配对和presentation审计文件保持不覆盖。科学结果/三主张级别没有因组织去重改变，也不以此判论文全部完成。

最终源SHA：{"PAPER_DRAFT.md": "879d73f6ddff0a91e0f0c66d408e970b6d29b629170260c6a6c834278f77b3b2", "PAPER_APPENDIX.md": "eafae062bdf782dac048441f731ced695734a83b4ffe3335a8098dc644376172", "scripts/build_paper.py": "40a08d5e06cd182dfccf438f8ef416bb3be8d744281931c611425c46ae1e1220"}
PDF SHA：a9536a0ea8ff250e2617c1ef12ce07139fa5a2d8982c98c7acdad2fce8cb8edc
