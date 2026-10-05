# Do Language Models Track Entities Across State Changes?（ICML 2026）[证据级别：主文§1–7；附录未读]

- primary：[Tang et al.](https://proceedings.mlr.press/v306/tang26ah.html)，正文9页＋附录共38页PDF无代理缓存，下载不等于附录读完；hash见D0-E45-reading-assets。
- 形态：已有boxes行为资产→增量与query时检索的四假说→operation层机制→预测三种新错误并部分修复。CodeLlama13B/Gemma2-2B/Llama3.1-70B，主证据13B；没有移植其probe/patching到本线。
- DOCUMENTED idea来源：先问static绑定怎样处理state-changing operations，不把过得去的原benchmark当完整追踪。REMOVE抑制可能跨box，因为原数据全局只有一种同label对象，看不出local/global区别。
- 三个决定性行为：no-op remove、不同box同label、removed后reintroduce，各300句，precision/recall/degeneration＋causal intervention。70B reintroduce DR .01而13B .62；不能只抽最坏模型给全体结论。
- 与我们距离：已经拥有local约束变global suppression、query-retrieval非incremental、标签与绑定scope退化。C05不能因old正/new反向就宣称发现新global suppression。我们的潜在增量须对应语言角色证据在referential form/event结构下的预测和实际用途，须有可区分解释的新读数。
- RECONSTRUCTED启发：保持entity identity改变描述alias，或保留same description但改referent，可区分token-level偏好与角色关系迁移；本线尚未做这个交叉，不能先宣布机制。
- 限制：probe不解码不是不表征的一般证明；本论文主文还讨论global tag未定位完整circuit。我们没有审其GitHub/dataset，不新建generic箱子benchmark。
