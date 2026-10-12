# E131 新增主文/附录的 paper-critical 独立审计

本次只核新增§6.6、模型/Discussion的32B表述与附录M，结合已封12批raw/report及三组同材料配对；未重跑旧整篇数值审计、GPU或扩展科学设计。结论：新增数字、原三项认识与实际实验范围一致，没有把有限Cue/criterion响应作旧形成结果的新资格，也没有把大小checkpoint差异解释成参数数目的因果效应。

主文两行24个mean/CI数字、附录两行18个native/restoration数字及新增文字中的重建、private、policy、paired、interaction/full/joint/floor值逐项对应原读数（JSON给出映射）。Q32固定n32形成signed2.676[2.266,3.096]，native移除1.972[1.467,2.500]nats；自然shared/full gain7.71[5.76,9.57]pp。A-only受限恢复正、full-source恢复负并列保留，支持相同已定义操作在不同读取环境下有不同功能；未把单个接口当完整中介。label B0 KV系数1重建raw r=.883、RMSE.864 vs zero1.857、rule双差r=.922一致。

100%私人单Source功能明确限定Q32本批formation；不能借此替代本批function或所有原子能力。自然function明确两Actor mean，95.70%不同于92.19% joint；far/all-cross95.31% candidate与52.64%full、9.96%joint同时保留。signed交互CI跨0、absolute为正，并未据此撤回单独实测形成贡献。Q8/Q32只在family/stage内逐字配对，不把不同stage材料合并为一个dataset，也没有要求幅度一致。

12完整stage、336contexts、172032scores与manifest/report一致；六L70stage尚无完整科学结果，加载或部分forward不计证据。全12有效批numeric最大误差为6.67572021484375e−5（来自Q8确认native），四舍五入6.68e−5正确；self/graph0及TF32三个空raw执行失败的说明正确。旧Abstract/Introduction三项认识与此前附录A–L字节未变，主张未自动升降级。

已落实的两个措辞建议不要求新增实验：把“gain differs ... by only .10 [−3.22,3.32]”改为“paired gain difference is .10 ...”，报告点估计及区间而不暗示已经证明等价；70B资产ready时，将“await complete pinned weights and execution”改为“await completed scientific stages”。正文已明确训练recipe差异和parameter-count scaling的范围，原三项认识可以保持。

阅读范围限于上述新增段、完整新增表/数值及scoped diff/已封证据；这不是科学完整性或接受判断，不复审所有既有近邻全文，也未改science/card/claims或commit/push。当前科学结果不需要补新的控制才能使这段有界叙述成立。

当前源 SHA：{"PAPER_DRAFT.md": "dd5c2548c197fd7c12eea9f08c77a006b83968ff99f81db1ccaaa43fd855ca2e", "PAPER_APPENDIX.md": "f1c38746e34f6a524a66dbf05fe572729335e3493c7ca640a893bfc554af8ccc"}

最后快照：上述两项措辞已修；科学读数及engine未改，当前新增段/表呈现封版通过。

## 最终32页编译稿重绑定

Q8 full-source restoration CI下界直接按sealed raw/summary取三位为−1.269，已在附录及编译Table32中修正。全部29组新增数值映射通过；旧重复舍入记录保留于JSON历史快照。正文SHA dd5c2548c197fd7c12eea9f08c77a006b83968ff99f81db1ccaaa43fd855ca2e；附录SHA f1c38746e34f6a524a66dbf05fe572729335e3493c7ca640a893bfc554af8ccc。

/tmp/ices-paper-32b/main.pdf：32页；PDF SHA bc6811c735a0ab423f8d9a6d321dde57d16458dd001e56f8be96fe38595500d0。manifest与当前两MD SHA、脚本SHA和最终PDF SHA一致。新Table6（第10页）、§6.6正文（第9–10页）、附录M正文（第28页）及恢复表Table32（第32页）视检通过；新表各行保留原数值，原三项认识仍在。末轮Warning/undefined/Overfull均0；有79条Underfull排版信息，没有观察到遮字或裁切。builder、官方style与书目未改。

只重绑新增段/表及编译元数据；未重复旧744单元审核、GPU或添加科学控制。当前新增段/表最终封版通过；70B部分forward仍不计完整科学证据。
