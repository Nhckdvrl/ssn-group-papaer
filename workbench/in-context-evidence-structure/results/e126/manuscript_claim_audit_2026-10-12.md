# E126 纳入正文后的 paper-critical 独立审阅（2026-10-12）

**当前新增§6.5、附录I与C23补记/alignment§11的数字、primary及非ID/非latent非加性边界适配已有证据。** 原新增137个数值呈现、12表行、11元数据项逐项一致，POST-HOC正文/附录另33项一致（合170呈现）；E120–126累计50批/1200context/564864评分、93178原始数值比较及7.709026 GPU·时也从全部已封run元数据独立加总核对。没有当前文字必须补新GPU实验的决定性缺项，不将方差/工作量当价值或novelty判据。

本报告是 **paper-critical 审阅**，不重写[已封E126独立raw](independent_review_2026-10-12.md)的科学数值。该raw已先于作者summary派生：六批144context/49536评分、12462项max0；实际token/官方gold/图/消费/组合控制完整，未独立GPU重跑。作者report的120行/1548呈现与summary12466项另一致。

本轮阅读范围为新增正文§6.5（含图6定义）、附录I、CLAIMS的E126/C23补记与PAPER_ALIGNMENT §11，回看原生形成/功能与组合scope。旧整篇论证与最强近邻范围沿用[E125最终paper-critical审阅](../e125/manuscript_claim_audit_2026-10-12.md)及更早E119–123审计；本轮没有重新从头读/重算所有旧raw或逐篇全文复现。E127当前只是跑前源码/CPU设计审查，不纳入E126科学支持。

审阅快照：PAPER_DRAFT `adbbccf8fbe4f063774a0ed59f1dbc38b5f65d322e6a13ce4b31df1f8ff143ba`；PAPER_APPENDIX `b88782441130ce21d512c629d1046d60b4acac4999e1ec52963201af6b5d01c0`；CLAIMS `2843a0e4a772a04108098dd3a1165229f88189ccebef57a52e849433b2bc69bb`；PAPER_ALIGNMENT `a05f14e0beb3a96e62ec3227ecb5616131ef76bb47add39fcc332147ca73d037`。独立expected值由封存raw先生成，再与这些新增呈现比较，未从作者表倒推指标。

## 证据—措辞—开放解释

| 核心问题 | 完整证据 | 当前范围与判断 |
|---|---|---|
| 同样事实是否保证指定整Source cache可互换？ | fixed public facts/private pairs/词集/private global positions；三确认paired joint full coherent−mixed Q+23.49[20.80,26.07]/M+10.40[7.96,13.04]/L+5.42[4.00,6.79]pp，A/B与两个private方向均CI正。 | §6.5标题与“at this interface”可保留，指此Source-owned整cache组合的功能依赖。不是一般语义等价应保持全部激活相同，也不是首次cache context依赖。 |
| 正效应是否源于某个coherent donor本身优质？ | 两order own-only实际函数强；paired2×2抵消单Source/order加性accuracy quality。Qwen/Mistral joint order11−00为−4.10[−7.62,−.59]/−5.27[−10.25,−.49]pp，仍完整保留。 | 平衡对比有效，但不排除quality通过竞争读出非加性进入。不能把两order信息等价改写成功能等效；正文/附录已如实写两order不同。 |
| 是否证明隐藏非加性程序或binding坐标？ | Entire private KV改变多种表示，query继续读两Source。2×2效果在full accuracy，Q/M correct-margin点估计负且CI跨0。 | 当前明确不识别binding ID/非加性latent，正确。argmax/accuracy本身非线性；即使内部score可加，竞争选择也能产生功能交互。Source显著性、KV尺度、位置/词汇上下化仍是实质候选解释。 |
| 是否已经是私人规则的无损协调？ | coherent joint Q83.98/79.88、M64.45/59.18、L60.35/61.82%；own约92–97%，native约94–95%。M A joint42.58/33.40%，B较强；single弱方向仍有L82.81%。 | 已注明不完美与A非对称，平均不是joint成功率。own-only平衡coherence0是图/存储恒等控制，不是新的科学双分离，亦不提供额外程序必要性证据。 |
| 效应是否仅词空间，或也调用别的私人mapping？ | full差23.49/10.40/5.42pp，candidate仅1.12/.63/.20pp；另一Source词减少25.88/10.64/5.76pp。 | 可以说主要差异表现在实际词空间使用；不能把candidate within-own排序自动等同actual wrong-space token所调用的规则来源。当前“principal effect”是量级描述，不排除其它功能。随后class-index诊断是POST-HOC解释量，应保留原primary且另核。 |

## 对自然问题与近邻的适配

新增结果推进的是“哪些共享关系能让私人监督形成的证据共同使用”，而不是泛泛宣布缓存会包含上下文。E125已测public Source→词集关系经形成的功能作用；E126进一步在公共事实、私人监督与位置相同的等价背景中，用平衡组合检验函数部署。它确有新的反事实识别对象，但当前是far输出词的任务范围，不能据此称抽象私人规则普遍可组合/不可组合；正文结尾把同词集合下的rule选择列为另一问题，正确。

[Feng](https://arxiv.org/html/2310.17191v2)/[Mixing](https://arxiv.org/html/2510.06182v2)已有contextual binding、多机制和两侧协调，不能以coherence的名字重获ID所有权。[TR/TL](https://arxiv.org/html/2509.24164v3)已有词集合识别与集合内mapping区别，full/candidate差也不是首次认知构件。[PCW](https://arxiv.org/html/2212.10947)已有独立窗口形成/共同query读取，[CacheBlend §3.3/4](https://arxiv.org/html/2405.16444v2)已有预存块缺跨块上下化与融合质量问题；一般KV context依赖不能first。SADA与Zellige作者报告的形成/对齐/结构兼容范围见前一审阅，不把报告当唯一权威或接收事实。

**定位文字修订已通过：** §7现加PCW/CacheBlend已有cache形成/共同读取与上下文化/组合所有权，明确本文固定public/private事实与原global位置下的Source函数配对对象；明确不是首次独立cache组合失败或新binding构件。PCW正式链接标题亦核。此为定位适配，不是科学结果作废或新实验门槛；正式投稿/状态仍由人判断。

## POST-HOC诊断与后续设计范围

E126“wrong-space输出的class index匹配请求Source还是另一Source”的观察量现已独立raw封存后核对，见[POST-HOC独立审计](posthoc_independent_review_2026-10-12.md)：9216逐query判定、600数值max0、24表行/360呈现一致。它可揭示实际输出空间失败是否伴随另一私人code的调用，但条件选择基于other-word时必须报原始denominator/Actor/world/private计数；shared词不能识别来源，same world两code相同不可区分二者。该诊断不改原primary，不是新GPU试验，也不为旧C21–23重设资格。

E127 shared/opposite primary确实产生另一预测：同两词集合下若coherence改变accuracy，单纯选择另一套可区分输出词不足解释。即便阳性，也只是请求Source mapping功能使用的指定cache依赖，不排除已有binding/位置/竞争读出、不识别独立latent程序；joint chance时阴性不能严格排除所有兼容机制。固定same/far参照、8接口完整执行与实际private控制已在card定义，本次不增新的科学矩阵。

未改science/card/claims/论文或状态，未GPU评分、未commit/push；E126 raw runs/geometry封版保持。此审阅封的是当前新增文稿范围，整体来源规则如何可靠组合仍开放，不能以有限矩阵完成替代研究目标的继续检验。

最终POST-HOC snapshot追加：减少另一规则兼容输出的Q/M/L23.73/10.06/4.88pp及CI、request-index类变化与Q/L own-bad代价均一致。正文说compatibility而非internal execution，附录明确origin-only不是both-world中介份额，范围适配。该诊断仍允许空间mass/校准在已有两套映射间竞争；不能提升为called-rule或ID证明。原primary与runs/geometry digest2a590a16…保持。

## instruction辅助条件语义补记（2026-10-12）

E124–127的instruction条件同时加入一句Source指令与跨Source私人形成隔离，属于复合辅助条件，不能相对native解释为纯一句指令恢复。E124/125已有无指令independent参照，可比较同一隔离图内prompt差；E126/127没有该无表匹配参照，不能分解两项效应。E122/123 instruction使用normal形成，仍是纯prompt控制。核心coherence/identity contrasts与所有已封数值不变；此前审计对instruction标签说明不完整，本条更正范围，不改科学源、不重跑或改状态。 主文/附录引用这些辅助条件时必须加formation isolation限定；这不要求重跑冻结批，也不改变已核核心数值。
