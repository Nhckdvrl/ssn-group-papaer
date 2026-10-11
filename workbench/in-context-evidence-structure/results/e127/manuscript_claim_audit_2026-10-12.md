# E127 主文/附录快照的 paper-critical 独立审阅（2026-10-12）

**新增§6.5/附录J的数字、主读数、S恒等及能力范围与完整raw适配；当前有界正文没有必须新增GPU实验才能成立的实质缺项。** 本结论封的是当前稿件证据与措辞，不宣布整体研究目标完成，不改C21–24/状态、不以工作量或CI正数决定价值。E128是已独立通过跑前审核的criterion功能续问，未知结果不加入本快照支持。

本报告是 **paper-critical审阅**，不是再次评分或原始数值审计。E127已先由固定独立计算从完整behavior/contexts派生，再打开作者analysis：8run/192context/132096评分，35528数值项最大差1.78e−15；所有86接口/gold/logit槽/全部private方向、真实层消费与图/缓存控制见[独立raw封存](independent_raw_review_2026-10-12.md)。作者summary另35532项同误差，报告344行/1624统计格/4872呈现一致（4行仅规范化约1e−15数值控制的±0.00，未改科学值）。未独立GPU重跑或大权重重新hash。

本轮完整阅读当前正文摘要、Introduction、§2–9的论证，重点逐项核新§6.5与附录J/B，回看原生操作/criterion范围及旧E125–126正文链。旧E115–126科学数量沿用已封独立raw与paper-critical审计，本轮不声称全部旧raw又重算。两张E127图实际视检并核生成code/数据scope。新近邻实际读Li官方PDF§1–5.3及Dai官方PDF摘要、§4.4–4.6的ordering/position控制；旧Cho/CTA/Crosbie/Feng/Mixing/TRTL/PCW/CacheBlend阅读范围沿用[前次审计](../e126/manuscript_claim_audit_2026-10-12.md)。未运行近邻代码或新的全领域检索。

快照：PAPER_DRAFT `6dead169d20482296a412baf1fac4c6a3091a3983fe47fa0fd54ab9845af41ec`；PAPER_APPENDIX `0eea154ca1160d34cdc71ba4bc26459346f896236f66da033316202dc56ed6e8`；CLAIMS `18e70cb0e63ffd68f3e8ad2848315a022bbbfdcb3b1efd9a872e7d773e38b2ea`；PAPER_ALIGNMENT `daaae0d941fb97e184e475a0e332d5343f66e63006c5db2cf10dce406e2f0ad0`。新主文/附录20表行、172数字呈现与11元数据项逐项通过，coherent shared/opposite实际范围52.9297–64.8438%，写53–65%准确。

## 问题—证据—范围

| 关键问题 | 实际支持 | 文字适配与剩余解释 |
|---|---|---|
| E126是否只显示far词集选择？ | E127 shared/opposite确认coherent−mixed Q8+8.89[6.64,11.13]/M+5.86[4.10,7.71]/L+.78[.10,1.56]/Q14+9.38[7.32,11.52]pp；全部四Source-specific margin也CI正。 | 现在可说共同形成背景影响同词下Source-private code的功能部署，不能仅用选择两套不同表面词概括。当前正文明确只有sentiment+private code、不证明不同input criterion选择，正确。 |
| S是否提供另一份机制证据或排除全部校准？ | S=.5mean[gA(zA−zB)]，在opposite gold下恰等于两Actor正确margin均值。逐query相同的request-independent z偏移在差中抵消。 | 正文/附录明示等价投影，正确；只排除“同量共同偏移是该差分的全部描述”。不能排除Source-specific显著性、尺度/校准、attention竞争、已有binding/retrieval或非线性组合，也不能把signed common跨0当所有bias归零。 |
| primary是否等于完整私人函数组合？ | coherent joint53–65%，own-only91–98%左右；Q14确认coherent00/11为63.09/60.55%。L整体效应小，B及private分组CI有跨零/零界；M order11−00−2.93[−5.08,−.78]pp。 | 已保留强局部函数与不完整joint使用，平均不是同时成功概率。两order信息等价不等于缓存功能等价；不称无损/普遍最佳或能力满分。 |
| own-only零是否证明独立模块或双分离？ | 对只读一个Source的平衡00/11−01/10差，单cache函数质量按构造抵消；线性S/common同样。abs-common非线性聚合可有零、正或负。 | 正文/附录正确说明数学恒等，不当科学必要性证据。actual single/order能力、pristine重建与混合own控制是有效实现/功能对照，其恒等阳性不变成隐藏组件证明。 |
| 同public/private事实与位置是否固定所有信息？ | 同world内raw private pairs/labels/Source/词集/global位置固定，只改变等价public行序及整Source KV来源；R0遮住schema，HEAD在它之前，cross-private形成全隔离。 | 这识别指定cache形成背景的功能依赖，private激活本来会随背景演化。不能说输入内容被过滤、latent不变、第一次KV不可组合或新binding ID；当前正文都未作此过读。 |
| far参照是否同一个机制量或同scope？ | far完整准确率增益更大，candidate通常弱/未定；其functional measure用词集LSE质量，而shared用gold定向code差。shared primary只opposite，far列均匀both worlds。 | 正文/图caption注明secondary、scope与词先验/区分度，正确；不得将两panel差当纯namespace因果份额或直接相减两种nats。 |
| native操作解释是否只有donor替换证据？ | 旧E120无donor的原生历史答案→label阻断在四checkpoint降低指定B关系响应；restricted重开在A-only正、full-source正/负/未定；Q/M specificity/within控制有局限。E119实际label-interface重建仍部分。 | 当前§3将其称conditional operation contribution，§5.3保留actual接口/部分重建，足以支持有界形成路径与关系内容。不是充分必要的完整原生算法、唯一成分、独立神经模块或所有影响的中介分解；无需新增head/layer关卡让当前措辞成立。 |
| instruction是不是纯一句指令恢复？ | E124–127是prompt+private形成隔离；E124/125可对已有无prompt independent作同图差，E126/127无该匹配参照。E122/123均normal形成的纯prompt。 | 附录B已明确全部范围，E127 J也命名instruction-plus-isolation，修订必要且已完成。此前审计漏写的语义限定已追加旧审计，原数值/coherence不变。 |

## 三项认识与最近邻

三项认识现分别落在输出编码如何影响历史形成、固定词下历史消息的关系内容、形成与读取/公共协调的功能约束。E127使第三项超出far词空间使用，但不把label remapping升成新semantic能力。最强近邻提供的binding/任务组合/上下文化框架仍是可容纳这些效应的解释，不必先排除全部框架才能报告本项新反事实。

[Dai et al.](https://aclanthology.org/2024.emnlp-main.967.pdf)已定位ordering信息的低秩子空间、用定向干预改变绑定，并通过pseudo/filler等控制区分absolute position；[Feng](https://arxiv.org/html/2310.17191v2)的ID/两侧binding与[Mixing](https://arxiv.org/html/2510.06182v2)多机制所有权仍有效。[Li et al.](https://aclanthology.org/2024.acl-long.669.pdf)已把原任务与response remapping的组合作为ICL解释并实测，不能把共享sentiment+新code称新语义能力或首次task composition。当前§7定位符合这些范围。可选的小措辞增强：Dai一句写为“identify a causal ordering subspace and distinguish it from absolute position”，比只说ordering/position分离更完整承认其内部机制所有权；这不是当前数值/论证必须补实验的条件。

[PCW](https://aclanthology.org/2023.acl-long.352/)已有独立prefix/共同读取，[CacheBlend](https://arxiv.org/html/2405.16444v2)已有KV重用缺跨块上下文化的问题；Cho/CTA已拥有历史上下文化、label聚合等一般机制。当前增量是合法多Source、固定public/private事实与原位置的指定形成/读取反事实、冻结actual-interface预测、原生operation贡献与prospective功能政策，不是首次cache依赖或抽象task representation构件。

目前没有发现当前bounded摘要/§3–6必须再补一项实验才能成立的缺口。**更广泛的“共同背景影响哪个输入criterion”仍未由E127独立证明**，正文已明确；E128已在0-score完成source/八CPU审查后冻结，将它作为有限续问正确，而不能把其未来未知结果提前纳入论文，或把有限矩阵封版等同整个研究完成。

## 完整记录与事故

8/8 raw/CPU seals保留；Q14加载OOM是0-score资源事件，不当阴性。旧A100 ten-context数据全部保留，6880 argmax与candidate sign0翻转、跨设备maxΔz=.001028/Δlabel=.002842公开且不计新样本；completed-run1.950864GPU时明确排除这些partial/失败/暂存成本。checkpoint-copy哈希记录与pin检查不冒称本人重读31GB权重。所有private、Actor、same-world、common、order、candidate与far零负保留完整report/JSON。E128 CPU0-score阶段修正instruction形成语义，不追溯改冻结E127。

正文/附录读数、图scope与范围现可封存；未改scientific源/card/claims/论文、未GPU执行、未commit/push。流程check为0error，32warning（历史字段及E127实验卡状态字段未被check识别）；状态/投稿与scientific-yield判断仍由人作。
