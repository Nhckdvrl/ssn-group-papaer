# DRInQ: Evaluating Conversational Implicature with Controlled Context Variation（ACL 2026 main）

**证据：正文方法/主表/错误分类已读；后半讨论/全部附录及代码未核对。** [原文](https://aclanthology.org/2026.acl-long.1597/) · [代码](https://github.com/hjarai/drinq)

1. **形态：** question/context benchmark + human/model finding。
2. **压力：** 同question何种context支持何种speaker intent，plausible生成不等于warranted推断。
3. **改变前提：** surface Q固定、context/intent变；gold依human consensus而不是生成model。
4. **来源 DOCUMENTED：** 问句多功能与生成/inference不对称，Searle式intent框架。
5. **近邻距离：** IMPRES/GRICE词法规则、Hu昂贵human materials、Multi粗分类；DRInQ直接拥有controlled context、overstrong inference与human标准，与本territory高度相邻。
6. **协议：** 30人工seed→300questions，23intent标签、generated multiple contexts；62 Prolific标注者，≥4/5一致819，再选400hard。12models×vanilla/explanation、3次few-shot例子抽样。主表best o3 .67、人.88（抽样选择限制）。
7. **短板：** 摘要/intro称GPT4o76%、human89%，主表GPT4o62%、o3 67%；可能子集/版本不同，不能拿76当统一anchor。hard筛选依annotator/model disagreement，样本不是全自然分布；生成gold与human总体agree67%。
8. **动作：** 从原有human分歧与malintent/over-fixation寻找boundary；保持source selection。
9. **对我们：** compression risk高，“上下文应该支持才推断”不是新增claim；增量需同stage/同readout上的可辨别结构。邻近资产不自动触发关闭。

## 2026-10-03资产核对
repo https://github.com/hjarai/drinq commit96a5eaef3fc6fd127d6a76f8421ff921a8877221。drinq_validated.csv为231行/148不同question，与论文819 validated/400hard不同，README没有evaluation代码。第一项问airport ride，author implied_comment对应D，而human consensus为B（提供搭车），体现intended/generated gold与human endorsement不必同构；不据一项宣布普遍label bug。不改变现有三个baseline顺序，只用于ownership/许可标签可行性审计。

## 2026-10-03全量候选审计
231行五选项均可解析，148个question；186/230非缺失generated implied-comment与human选中原选项文字不一致（文字比较，不能全称语义矛盾/label bug）；1目标缺失。相同question的84对human选中文本不同，但0对五个候选集合完全相同，只有4对/3个question互相包含两个gold。因此release不支持把整组“固定utterance+固定candidates”的context-switch拆解直接铺成大实验。未跑新的榜单补数量。原审计资产外置data/drinq-released-pair-audit.json；不是撤回parent原论文，819/400原资产尚未取得。
