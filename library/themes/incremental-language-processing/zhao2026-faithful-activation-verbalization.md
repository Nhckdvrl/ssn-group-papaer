# Faithful Activation Verbalization / AVPO（arXiv2026-09-27）

`[作者v1主文及方法/关键结果附录精读]` [原文](https://arxiv.org/abs/2609.34033v1)，Zhao等，NJIT/Shanghai AI Lab/XJTU/CUHKSZ。34p PDF SHA32825bc6f19bb0a111d4a3cfcbeb6edcbcdf1aaaa526ceca1674c6736f09bcb6。Main1–5 pp1–10全；AppA–F pp14–28全，G1–4 pp28–30及G6/7开头p31全文，G6剩余图表/G7例子pp32–34未全读；主表/奖励消融 pp5/7视觉核。预印本，接收/代码/独立复现未核。

- **idea来源（RECONSTRUCTED）：** activation verbalizer回答不好，无法分清表示是否缺内容与decoder回答失败→先query-agnostic文本inversion、再frozen QA→token CE不足以奖励具体信息→用gist/detail用途与name/number anchors给DPO sequence反馈。对象是自然文本的激活解码，不是首次指出语言描述会hallucinate。
- **方法/载体：** 末token某层activation→QFormer64软token→LoRA decoder；六自然语料族165760训练/2172验证/1560测试（输入≤64token），两donor及跨decoder；DPO每input8候选，chosen collapse过滤、margin≥.2、anchor不下降，main最多6round。完整资源约2.9k A100 GPUh；多seed仅特定Q4B消融，不冒称所有main配置都有CI。
- **关键比较：** QA收益高于chosen-only SFT及某些纯重建指标；更大round可增加重复并损伤部分细节，所以下stream收益不等于所有内容更忠实。QA监督只有每文gist/detail两问，未独立核answer支持或两问差异；judge/interpreter同Qwen32B，跨judge相关是同答评分一致，不是teacher无误证实。OOD clinical是10虚构case各25改写，不能算250独立临床世界。
- **最近邻距离：** NLA/LatentQA/UAV/AO已有activation语言解码，本文增量为可检查的query-agnostic中间文本与语义/anchor preference训练。一般“字面重建≠语义恢复”“用未来QA奖励内容”已有ownership，不能把换成GP数据叫新方法。
- **对I07/I08：** 我们要具体说明需撤回的旧关系为什么还能获credit，难观察的surface如何改变固定内容的评价；若只得到普通文本质量或memory judge不可靠，距离不足。AVPO interpreter明确强制猜测/不准缺信息回答；这个接口可能让QA恢复依赖回答priors，是待测范围，不从prompt直接判其论文错误。不会把实现/数据局限充作我们的idea，也不据局部相似关线。
- **可借研究动作：** 将representation/readout/use分开，比较同一个内容对象上的多个评价接口；让主要对象、功能读数、训练信号彼此对应。今晚先由完整现代GP修订/credit图决定值得追的问题，不复制大规模训练控制来替代探索。
