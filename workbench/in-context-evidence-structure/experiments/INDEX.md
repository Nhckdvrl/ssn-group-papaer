# 实验索引（E00–E72）

按主题分组；每行是结论的一句话版本，数字与置信区间见各卡。“规范”= 与 exact Bayes oracle 同方向；“噪声检验”= 前缀零散反例是否降低对后缀变化的信任（规范为负）。

## A. 工具与校准
| 卡 | 问题 | 结论 | 模型 |
|---|---|---|---|
| [E00](E00-task-learning-instrument.md) | nonce 规则任务能否被真实地 in-context 学会 | 能（T=16 准确率 0.85–0.9，换字典稳定） | Qwen3-8B / Base |
| [E01](E01-two-extreme-calibration.md) | 两个极端条件能否被区分 | 能；工具可用 | Qwen3-8B |
| [E02](E02-noise-vs-change-pilot.md) / [E02a](E02a-structure-grid-pilot.md) | 噪声 vs 变化的方向相反检验 | 分类式 ICL 方向错（成簇≈零散、噪声使 P(新) 上升），与 set oracle r 0.88–0.99 | 6 → 13 模型 |

## B. 条件结构（类别→标签映射）时间盲
| 卡 | 问题 | 结论 | 模型 |
|---|---|---|---|
| [E03](E03-instruction-recovery.md) | 指令能否纠正 | 不能 | Qwen3-8B |
| [E04](E04-local-vs-global-update.md) / [E21](E21-local-update-natural.md) | 更新是全局还是局部 | 局部：跟随最相似的 demo，与新旧无关（两种顺序对称，32B 仍是） | 3 → 5 模型 |
| [E07](E07-natural-language-sst.md) | 自然语言是否不同 | SST 同样时间盲 | Qwen3-8B |
| [E08](E08-long-context-and-surface-alignment.md) | 长上下文 | T=64 时 A→B 与 B→A 差 0.05（oracle 6.89） | Qwen3-8B |
| [E09](E09-thinking-recovery.md) | 推理能否补救 | 可见 CoT 与 2 万 token thinking 都不能 | Qwen3-8B |
| [E13/E15/E16](E16-confirm-v1-lexicon-free.md) | 确认版（无 nonce、新种子） | 分类全部时间盲；标签流/大小写↔反转全部规范 | 4 → 13 模型 + 32B |
| [E23](E23-daystamp.md) | 把时间写进内容（day k） | 只有轻微近因，噪声方向仍错（32B 亦然） | 4 模型 |
| [E25](E25-multiclass-permutation-drift.md) | K=4/6 多类置换 | 噪声方向错 8/8 | 4 模型 |
| [E27](E27-task-switch-vs-flip.md) | 换成另一个可识别任务 | 与翻标签一样时间盲（TR/TL 解释否定） | 2 模型 |

## C. 输出侧变化被规范追踪
| 卡 | 问题 | 结论 | 模型 |
|---|---|---|---|
| [E05](E05-input-richness-switch.md) / [E06](E06-switch-trigger.md) | 标签流（含无关输入） | 规范（噪声 −4.75 等），开关在“标签是否依赖输入” | Qwen3-8B → 13 模型 |
| [E11](E11-familiar-task-switch.md) | 全局变换（大小写↔反转、±3） | 规范 | Qwen3-8B → 多模型 |
| [E19](E19-fv-task-switches.md) / [E20](E20-surface-string-ops.md) | 词汇/字符串函数 | 多数只有近因；输出语言变化规范 | 多模型 |
| [E22](E22-marked-concept-drift.md) | 新 regime 用大写标在输出上 | 格式通道规范 16/16；映射通道平坦（8B），32B 开始按大写分组 | 8 模型 + 32B |
| [E28](E28-imbalanced-flip-marginal.md) / [E29](E29-imbalanced-condarith.md) | 类别不均衡时翻转映射 | 时间结构只在“偏向新多数输出”成分；条件成分噪声方向错 12/12；少数类被拉错 | 6 模型 |

## D. 证据按输出身份存放
| 卡 | 问题 | 结论 | 模型 |
|---|---|---|---|
| [E24](E24-input-marked-regimes.md) | 输入侧标注者标签能否分流 | 不能（绑定≈新奇性基线，对顺序对称；打乱对照≈0） | 6 模型 + 32B |
| [E26](E26-notice-without-reset.md) | 删除影响：变化后是否重置 | 格式通道重置且与内容无关；映射通道不重置且同类主导 | 4 模型 |
| [E30](E30-main-effect-vs-interaction.md) | 上下文主效应 vs 交互 | 交互溢出 > 主效应 14/14；规模放大这一分离 | 7 模型 |
| [E31](E31-label-vocab-separation.md) | 换输出词能否分开 | nonce 词表溢出 0.00（10/10）；大写/近义词居中 | 5 模型 |
| [E32](E32-relabeled-drift.md) | 新 regime 换新词 | concept drift 变得可追踪（11/12，含 1.7B/2B） | 6 模型 |
| [E33](E33-label-semantics-leakage.md) | 泄漏 vs 标签语义相似度（14 套词） | ρ=0.75–0.96（10/10） | 5 模型 |
| [E34](E34-tag-adjacency.md) | 标注者行的位置 | 不影响主效应（“相邻统计”否定） | 4 模型 |
| [E35](E35-domain-partition.md) | 输入领域分离 | 泄漏约减半（0.36–0.49 vs 0.79–0.91） | 4 模型 |

## E. 机制
| 卡 | 问题 | 结论 | 模型 |
|---|---|---|---|
| [E10](E10-run-head-ablation.md) | 标签流的“游程头” | 消融使标签流噪声效应 −73%；对全局变换与 E28 边缘成分无作用（E28b） | Qwen3-8B |
| [E10b](E10b-implicit-prior-fit.md) | 隐式先验拟合 | 标签流 λ≈0.02–0.05；分类 λ=0、ε=0.3 | Qwen3-8B |
| [E17](E17-task-vector-patching.md) | 任务向量 patch | 全局变换的任务向量带时间结构（9 格式 ρ=0.95）；分类无可迁移向量 | Qwen3-8B |
| [E36](E36-head-decomposition.md) | 逐头 DLA | 同一族晚层读标签头；注意力：内容 ≫ 标注者 ≫ 位置 | 2 模型 |
| [E37](E37-anchor-running-filter.md) | 锚点 value | 旧锚点不可改写；新锚点无变化信号（运行滤波器否定） | 2 模型 |
| [E38](E38-anchor-patching.md) | 因果修补 | 方向错误的噪声效应 = 晚层直接读噪声锚点；规范部分在噪声后的旧锚点（~L16） | 2 模型 |

## F. 为什么（训练统计）
| 卡 | 问题 | 结论 | 模型 |
|---|---|---|---|
| [E12](E12-toy-training-why.md) | 从头训练 toy | 任务同质数据复现解离；易变数据在预算内推不动条件变化推断 | toy GPT |
| [E18](E18-lora-volatile-classification.md) | 易变分类流上 LoRA | 只把分类推向近因，噪声方向从未转正 | Qwen3-8B |

idea 卡：[`../ideas/I04-output-indexed-evidence.md`](../ideas/I04-output-indexed-evidence.md)（主 idea）、[`../ideas/I01-surface-time-latent-sets.md`](../ideas/I01-surface-time-latent-sets.md)（早期版本）。

## G. 2026-10-10：意义与解释压力测试（旧工作标题不作为判据）
| 卡 | 关键追问 | 结果 / 当前认识 |
|---|---|---|
| [E58](E58-source-label-factorization.md) | 来源能否跨标签解码；label KV是否中介来源 | common source差分可迁移，label锚点source效应很小；不等于全部可因子化 |
| [E59](E59-source-mediation-sites.md) | source关系与mapping关系是否同位置 | name-K主要传递source，label-KV主要传递mapping；位置分离 |
| [E60](E60-verbalizer-routing-transfer.md) | 同任务换词的差异能否经name-K转移 | 未得到有效转移；大synthetic词表差在real不复现 |
| [E61](E61-crossed-routing-payload.md) | 两种定位是否可组合 | 纯V双翻转不足；label K+V参与，明显非加性，不是完整新电路 |
| [E62](E62-information-equivalent-field-relocation.md) | 信息等价的字段后移会否改变carrier | 部分转移、未提高表现；不支持唯一terminal carrier |
| [E63](E63-source-effect-label-message-mediation.md) | 最后token label消息是否足以中介source | Qwen剩余约一半；首轮数值失败VOID，原生重算控制通过 |
| [E64](E64-whole-query-message-mediation.md) | 整个query还是最后token承载条件化 | Qwen范围差明显；Mistral label消息主要末位；model-dependent时序边界 |
| [E65](E65-query-relay-versus-direct-copy.md) | query中间位置是否向答案接力，direct读取是否有害 | Qwen marker／Mistral source字段；删direct无稳定accuracy修复；factorial分解为POST-HOC |
| [E66](E66-source-selected-function-state.md) | input出现前source缓存能否部署规则 | bf16 chunk对照失败VOID；float32独立确认single/mixed均失败；input-dependent logit能保留，但accuracy收益低于MIE，非新composition瓶颈 |

| [E67](E67-source-code-at-answer-prefix.md) | 最终label相同、同信息code位置是否改变行为 | Qwen独立确认accuracy+7.4点、来源排序+10.9点；Mistralaccuracy差CI跨0；完整答案namespace仍改变 |
| [E68](E68-prefix-history-versus-local-address.md) | 历史访问必要是否说明存了先前label判断 | isolated prefix KV损害排序13.3点，但label-flip状态只传递约1.3%rule效应；不能从必要性定位内容 |
| [E69](E69-label-blind-contextualization.md) | 全部历史label禁读后prefix K是否仍可部署 | blind K保留accuracy/排序，blind−isolated排序+10.2点；其它native标签证据保留，非整ICL不需label |
| [E70](E70-common-frame-versus-example-specific-keys.md) | 公共key平移还是逐样例变化；冻结状态能否迁移 | bf16几何控制失败VOID；float32冻结共享偏移独立恢复53%margin效应、accuracy+5.9点，来源排序仍比native低10.9点 |

| [E71](E71-relational-code-versus-carrier-access.md) | 前缀是否只因扩大答案语法而有效；旧frame能否迁移新身份 | relation×layout accuracy独立+10.9点；冻结迁移35%/accuracy+3.1点低于MIE，own common仍有效；合作仅来源排序有界支持 |
| [E72](E72-native-chat-and-reasoning-boundaries.md) | raw/native chat/指令/thinking是否同一能力边界 | DONE；27B thinking普通来源/linked/entity/single全对，orthogonal大量截断；direct96正控无效，不做能力失败归因 |
| [E73](E73-paired-generation-budget-and-interface.md) | 同一采样路径预算与格式是否混杂模式差异 | DONE；48次实际前缀全一致，orthogonal think延长恢复；strict单源75%未过门槛，装饰校正为POST-HOC，不能称组合缺陷 |
| [E74](E74-source-scoped-rule-completion.md) | 正确词全局出现但Source×类别未见，推断还是正向支持 | DONE；full100%、held32–36%，signed方向CI跨0、Unknown程序未执行；不触发原确认，先native有效性 |
| [E75](E75-native-function-family-validity.md) | native thinking能否执行所声明的来源函数空间 | DONE；full/held bijection全对，independent Unknown66.7%另33.3%截断，全闭合都正确；非能力缺失 |
| [E76](E76-foreign-word-versus-owned-operator.md) | 词只在foreign labels时，是否执行自己的未知±1规则 | DONE；Source正确方向确认，但新材料accuracy73.4%未过门槛，中点/加性解释限制完整函数判断；暂不word机制 |
| [E77](E77-source-conditioned-function-or-prototype.md) | 相同Source label频率下，是否执行输入依赖的函数 | DONE；direct全对、single comp强，但single identity也弱，多数错成另一个合法函数；不称Source独有缺陷 |
| [E78](E78-operator-inference-and-execution.md) | Source函数识别、数字应用与显式code交接是否不同 | DONE；定义顺序让mixed subtract插值96.1%→25.0%；Rule-ID门槛未过，code+19–24点非新机制证据 |
| [E79](E79-parameter-evidence-versus-codebook-evidence.md) | private规则与共享输出词典的证据来源能否因果区分 | DONE；词典95–99%，direct subtract组合仅15.6–21.9%，不作provenance归因；保留诊断，当前不启动后续 |
| [E81](E81-carrier-mass-versus-source-allocation.md) | 全query实际来源码的总读取与组内分配能否因果区分 | DONE；64新context确认，同carrier m/pi下whole-query读取+13.3点；固定m/kind来源flip使Prefix−11.3点，C20 L1 |
| [E82](E82-label-reading-versus-query-relay.md) | Label读取还是query内部重放转移布局收益 | DONE；64新context确认Label+7.8点、query+.8点；Label全query比末位margin仅+.014nats，非原生Source-effect纯中介 |
| [E83](E83-predictive-label-reader.md) | 不拟合gold输出的冻结关系模型能否预测读取作用 | DONE；64新context R margin+.376nats，预算无收益；Label身份拟合改善不带来行为增益，逐context作用相关仅.252 |
| [E84](E84-source-field-versus-code-prediction.md) | 关系预测跟随Source字段还是共线的码词代理 | PLANNED；冻结E83系数，Source×code反事实，不扩能力门槛 |
