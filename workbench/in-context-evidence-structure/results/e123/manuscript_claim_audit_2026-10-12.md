# 最终主文证据适配审计（2026-10-12）

**paper-critical审计；非原始数值审计或独立GPU复现。** 当前摘要及三项主文认识与已完成证据适配，没有发现保留这些有界措辞必须补做的新决定性实验。E123使整体政策预测在真实Movie文本、可靠私人映射和实际输出词上得到直接检验；它没有把局部重建升级为完整ICL算法，也没有把平均收益升级为共同成功或普适修复。研究状态、投稿决定与科学价值判断不由此自动改变。

审阅最终快照：PAPER_DRAFT SHA256 `3d2cbd06e926ae5a70282f086e1ecd54f52c025d127812fa742d37e8341aa875`；PAPER_APPENDIX `f8aa1d89be0ca4a34fbca86e349981826fe06759bba70197643f4094a241a41a`。本轮读两文全文，重点摘要/§3–6/Related/Discussion与附录F；承接[E122 paper-critical审计](../e122/manuscript_claim_audit_2026-10-12.md)的旧证据检查。E123科学源/材料源、8批raw、官方SST gold/split/hash、真实token/mask及完整输出已独立封存；原primary15,144与新full-output7,680数值对比均max0。另核主文/附录新增304个数值呈现，一致。旧E115–E122封版未覆盖。

## 三项认识的证据与边界

| 主文认识 | 直接支持 | 不能外推及当前处理 |
|---|---|---|
| 输出命名影响历史证据形成 | C21实际donor历史答案消息对指定A-label namespace反事实的冻结系数1预测；E120无donor原生阻断在四checkpoint均降低signed B-rule响应。 | donor重建是指定接口的充分近似/部分预测，非无donor算法、唯一必要电路或固定加性中介份额。有限图恢复只重开边，native方向可负；正文已保留。 |
| 固定输出词的历史消息包含部分关联 | controlled restaurant与E121 official SST两材料/benchmark、至少Qwen/Mistral两家族直接确认；固定B词流/Source/位置/输入多重集，cross相对within内容作用在native/A-only接口测得。 | 非完整criterion程序或正确Source隔离；Llama自然文本signed关系为负而abs为正，14B形成×读取signed方向也不统一。正文/附录均保留这些区别。C22/C23有界L3覆盖判断见旧审计追加，C24仍固定方面单任务L2。 |
| 形成与读取政策具有不同功能后果 | E122双方面构造预测＋E123真实SST新context；两Actor共享每个prefix，全部模型16→32、六政策组合及正负结果保留。E123 shared四确认均值+7.32/+5.37/+9.47/+7.42pp，A/B分别CI均正，两全局私人方向平均收益也分别CI正。 | `both`是请求平均，非同时正确率；E122同源函数非满分，Food函数占主均值75%，Qwen一致gold有损失。E123是同一sentiment criterion的两私人约定，不是自然不同criterion运输。source ownership由生成真值给出，非learned recognizer/部署方法。当前文本明确。 |

摘要“shared-word judgments提高5.4–9.5pp”准确；E123 shared全部六confirmation政策的candidate/full-argmax统计一致，这项自然功能阳性并非候选限制制造。单源能力由本批实际控制支持，没有借E121自动声明。SST极性0/4、5–64token、fresh私有约定、可能预训练见过等范围保持；E121与E123同一benchmark的新contexts不冒称又一个新benchmark。

固定A输出词的B-convention响应幅度从2.449/1.390/1.595/2.230降至1.319/.841/1.093/1.167 nats，四paired差CI均负。它是每context A-gold-oriented **半差的均值再取绝对值**，不是逐query绝对值、attention Source ranking或准确率。E122四个Food/Service系数mean均降低亦实测，但其它bias/FS和残余依赖保留，不推出纯input过滤。

## 两项文字问题已修；无需增加实验

| 问题 | 核对结果与处理 |
|---|---|
| §2.1输出词总述曾把far也写成no/yes | 当前限定shared-word，明确A保持no/yes、B separate=pass/flag，旧MHS=safe/toxic。真值/模型/材料范围正确。 |
| Mistral query-only的“exceeds”可能读成确认更优 | 当前改成mean gain并明写point-estimate ordering uncertain。描述性文字核对的paired query-minus-target差+.586pp、CI[−1.563,2.832]跨0；未作为新primary/升级证据。Llama排序有直接支持，两Qwen方向相反。 |

headroom与word prior是实际范围限制：far native candidate已94–98%，shared/far涨点差不能单独识别等能力/等headroom下的纯word identity因素。正文只写consistent with output-dependent formation，并明确此限制。target/all-cross边数与attention mass不匹配，归一化/后继状态活演化；保留其它访问路径不等于固定其信息，不能把政策对比写成等强度纯内容干预。

完整输出损失也未被平均掩盖。far/all-cross的candidate94–97%与full51–54%分开；另一词表输出平均44.6–46.9%，但A/B构成不同（例如Mistral A66.99%、B22.27%）。Source word priors、已有binding或label recognition仍可解释该诊断，不识别新ID/TR组件或对称Source-binding模块失效。shared词相同导致“可按词识别的other-space率记0”，不能读成provenance隔离。Mistral far target full−1.27pp CI负、14B far full+1.27pp CI正，正文均保留。full-output在此指标签位下一token的全词表argmax，不是长答案自由生成能力。

## 最强近邻所有权与剩余解释

[CTA](https://arxiv.org/html/2504.00132v2)已拥有跨示例上下文化的重要性及input/output/关系信息沿边传递；[Cho](https://arxiv.org/html/2410.04468v3)已有label合并/检索、消融与bypass；[Add-Up](https://arxiv.org/html/2605.16591v2)已有上下文化QK/V作用。故“历史形成后再读取”“消息携带关系”“K/V有不同功能”这些宽认识本身不能独占。当前主文将增量限定为合法多源规则的关系provenance、输出依赖的冻结接口预测和前瞻政策功能后果，适配证据。

[Feng–Steinhardt](https://arxiv.org/html/2310.17191v2)已有身份/属性可因果交换、位置独立及加性binding方向；[Mixing Mechanisms](https://arxiv.org/html/2510.06182v2)已有位置/词汇/反身检索的竞争预测与混合；[TR/TL](https://arxiv.org/html/2509.24164v2)已有label-space识别与space内mapping的行为/干预分离。E123的candidate/full区别不能据为首次功能分离；prefix政策结果本身也未识别binding ID或特定TR头。它的新事实是明确历史形成图变化在多来源private function中产生这些可测后果，当前正文允许既有框架解释它，没有要求排除全部框架才承认具体阳性。

C24完整native criterion response、label/answer消息接口响应不同，不能过读为不同隐藏算法。actual KV重建r=.668/RMSE=.646明确针对actual label接口，非完整native criterion反事实；native/gated rotation、label负det与固定Food-before-Service范围仍保留。不存在需要为当前措辞追加head/layer/seed/词序小矩阵的实质缺项。

本轮近邻阅读范围：承接前轮CTA/Cho/Crosbie/Add-Up关键章节核对；新核Feng §3–5的factorization/additive/泛化定义、Mixing §3核心counterfactual与检索接口、TR/TL §4.2的label-space/accuracy读数及干预定义。不是每篇全部附录/代码复现或完整最新文献检索；其它Related主来源依靠本仓库指定章节论文卡和此前核对。附录末尾新downloader“byte-for-byte rebuild”只依据作者复现记录，本轮未独立执行该下载重建；独立确认的是原始公开release逐record对照资产一致、实际文本/gold/split以及preflight/runtime context字节一致。

本次只产出审计。未更改科学源/cards/claims/论文/状态，未GPU重跑、commit/push。过程检查0 errors/31旧卡warnings。当前主张链可以保留这些有界阳性；是否进入candidate或投稿，由人按完整材料判断。[E123 raw审计](independent_review_2026-10-12.md)与[JSON](independent_review_2026-10-12.json)记录全部条件、私人方向、完整输出和数值误差。
