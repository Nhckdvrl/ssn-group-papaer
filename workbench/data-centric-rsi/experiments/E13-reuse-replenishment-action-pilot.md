# E13 — 数据资产的复用与补货：记录、策展池还是抽样律（2026-10-03，跑前）

- **状态：** RUNNING；CPU动作、双父processor及seed29 sampler核对通过，六支队列已提交。fvcrc13四卡首批已进入实际训练，2026-10-02 16:34:44UTC时四臂各有12个实测窗口；fvcrc10评估队列等待六支完成，judge未启动。E12分数已知，E13尚无训练效用结果。
- **类型：** EXPLORE；强静态成功后的反事实训练，不是另一套baseline资格门。
- **对应：** P03（简单静态配方）、P06（科学对象错位）；I01的相关研究动作，不预设C01/C02成立、不改变workbench/idea状态。
- **问题（一句话）：** 已用过一个公开策展子集的学生继续学习时，更新具体记录、保留策展池资格、或仅保留廉价抽样律，哪层资产改变下一次真实训练效用？

## 来源与竞争解释

E12单seed八项均值random32.299、均衡33.443、ICONS发布池复用32.814、ARDS32.951；收益向量不同，不称简单方法全面胜出。ICONS臂从公开133K池随机取10K，非原算法按10K阈值重求票；原方法没有被否定。选择ICONS因完整记录/成员资格已审计、池内可补充记录和目标影响来源明确，不因它排名最好。

(a)来源与监督结构主要承载收益，廉价抽样律能补货；(b)策展池还有属性不能代替的内容/组/目标信息，但具体旧记录可替换；(c)池资格价值随已学记录变化，需要更新决策。旧数据多训不如新数据、泛状态依赖、matching或迁移本身都不是论文增量。

P05/Curation-Bench已做同配比不同draw，P04/DataEnvGym已比新数据和旧数据多训；P47/OFA、P48/XMAS、P49/TACS、P50/ICONS已有多种复用。AAS[§5.5](https://arxiv.org/html/2607.07023v1)有matched-topic；P51/Adapt-∞的C/Fig9已用新池记录恢复旧skill，P52/OASIS已有当前学生FI＋跨batch概率抽样和组内冗余，但其A.2是infinite memory-only retrieval。全文定位见[论文卡](../../../library/themes/training-post-training/RSI_PAPER_CARDS.md)；Adapt-∞关键接口已读，OASIS官方仓库当时无代码，不能称已审源码。本卡只能决定下一研究动作，不能单独支撑novelty。

## 设置：冻结动作与训练契约

1. **父状态**：init为E12论文init `anonneuripsmail/llava-1.5-7b-init@5736a39125fce6ca4d4eb20033ca7c46895878ab`；used为E12完整625步`icons_exact_s17/model`。记录parent文件hash/E12 manifest。两状态均重置optimizer、step counter和scheduler，不继承moments；只测已学权重状态。
2. **三动作**：replay保持E12原10K集合S；fresh_selected从公开ICONS池内、fresh_law从该池外替换同一批可匹配位置。两父状态用同一数据manifest。fresh排除S完整记录及S原始image路径；text-only以完整记录判未见。成员资格用已审计完整记录位置，不能用重复id/image。
3. **廉价抽样律**：仅`source × 2048截断后assistant监督token数n`，不读benchmark反馈/目标梯度/逐样本影响分。S各行提供slot，以E12冻结processor/chat/576 image token规则计n；各source/n内随机无放回取fresh记录。三臂保持对应slot顺序及同data_seed permutation，每16行窗口监督分母相同，全程各为**549,353监督token、10,000行、625步**。不改写新记录答案。
4. **稀疏支持预写处理**：每条件替换数为S、fresh-in、fresh-out可用数量之最小值，随机选同一批S位置替换；余位三臂共同保留S，不默默放宽长度/重抽S。fresh臂明确为**部分补货干预**，非全新10K/纯pool外10K。输出来源替换覆盖、监督token质量、共同旧anchor和hash。若覆盖低于90%行或80%监督token，先报告可检验支持，不启动六次训练；GPU前可版本化修改动作，不能用稀疏支持的null宣布抽样律够用。
5. **随机性**：一轮六支`init/used × replay/fresh_selected/fresh_law`，统一train/data seed29；sampling seed29加动作名固定salt，抽样/训练RNG独立。只有一个paired训练seed；重要对比的seed43确认需另加跑前协议，不按分数换seed。
6. **配方**：Curation-Bench SHA `24eea1526492c00cee421f5db0793789e00aabb2`、E12同一单A100 LM/projector全参SFT、vision冻结，BF16，batch1×GA16，一epoch，LR2e-5/cosine/warmup0.03/fused AdamW/assistant-only loss/2048。只指定parent/动作/seed，不改loss规则或模板；只取终点checkpoint。
7. **动作审计/资源**：复用665,298行原JSON↔Arrow审计、label sentinel和污染脚本，新动作对八TSV审计。不新建训练框架/环境。大文件节点本地`/var/tmp/xiang-data-rsi/e13/`，小manifest入git；共享一次large Arrow，小子集跨节点，先核空闲GPU，不碰其他workbench。

## 读数与决策

- **读数：**E12冻结八项规范化平均及完整向量。主对比每状态fresh_selected−fresh_law是条件内策展资格残差；fresh_selected−replay是刷新价值，两状态残差之差仅为交互探索。报告相对父状态增益、输入token、unique images、图像次数、成功/失败成本。同监督分母/steps不等于前向FLOPs相同。
- **阳性对照：**E12 init→random +3.343分、八项全齐无fallback已经成立。E13 init/replay检验相同S在预写另一训练seed仍可学，不能因未超E12分数丢弃六支；权重/label沿现有审计，不加防御GPU。
- **噪声地板 + MIE：**E12唯一同random checkpoint复跑已完成32.247479，对首评32.299397差−0.051918，是一次节点/推理/judge合并变化观察，非训练SD，本地训练方差未估。平均差约1分或多任务变化足以改变部署动作时提高优先级，这是探索判断。一个paired seed的null不是non-inferiority/等价证明，不把任务/题目当独立训练重复；八项向量失配时，均值相近也不称重建效用。
- **混杂审计：**parent/hash/data/optimizer reset/LR/steps/监督token/slot分母/评分协议固定；内容与图像身份是干预。输入长度、图像复用、forward wall未严格相等但报告；排原始image路径不称跨源pixel-dedup。init与used的历史预算是所测状态，不把used总分高归因于刷新。E12公共八任务已有观察，非未碰private测试；后续策略学习泛化须另设不可回馈的新任务/episode，不能循环按test选checkpoint。
- **决策表（跑之前写）：**
  - fresh-in>fresh-out且两状态同向有实质差 → 廉价律不能代替资格，找可复用内容信息，不继续堆matching属性。
  - used上fresh-in>replay且仍>fresh-out → 刷新有后果、池仍承载价值；研究可更新接受规则，非固定IDs重放。
  - init池内优势而used消失/反向，并导致真实损失 → 再测最低必要训练响应能否决定保留或扩展支持。
  - 两状态fresh-in/out接近且完整向量有希望重建 → 仅压缩假说线索；下一项测试冻结律对新记录/池的部署效用，与免费发布池重放/强配比优化比较全成本。
  - 所有差很小或没有决策后果 → 保留null，转其他研究动作（如选择目标与实际loss权重对应）；不铺更多属性或完整状态矩阵。
- **算力预算：**六支训练7–8 A100·时、学生评价2–4，总分配上限18 A100·时含失败；judge Blackwell独立账不折算A100，上限12 allocated GPU·时。CPU先4–8进程；下载/搬运/CPU/I/O wall另计，API0。**实际：**首批四臂训练中，初始化及分配等待纳入预算；最终训练/评价成本待completion及ledger，不用计划值代替实测。

## 结果（执行后追加，不回改跑前设计）

- CPU支持/替换覆盖/hash：已完成，[小结果](../results/E13_cpu_replenishment_summary.json)，脚本10adbc4。三动作各10,000行/549,353监督token，逐slot标签数及625原slot窗口一致；采样后的实际窗口由runtime observer再记录。替换9,954行（99.54%）/93.9740%监督token、46共同旧anchors；fresh与旧完整记录/原image路径重合0，fresh-in/out完整记录互不重合，3/3污染审计clean、8/8任务无跳项。视觉五源label覆盖98.69%–100%，**text-only仅45.08%**，不概括成长文本补货结果。输入tokens replay/in/out为7,587,690/7,606,055/7,589,448（最大差约0.24%）；unique images9,614/9,592/9,604。全池metadata计算段100.5s×8CPU进程，NFS import/实际CPU活跃与物化wall未完整计量，不把100.5s当全动作总成本。大资产`fvcrc10:/var/tmp/xiang-data-rsi/e13/`；该CPU结果不包含训练收益。
- **执行接续（2026-10-02 16:33UTC）**：[双父processor/sampler CPU核对](../results/E13_CPU_sampler_prepare_audit.json)、[资产与parent hash](../results/E13_asset_staging_manifest.json)、[训练队列](../results/E13_cpu_dryrun_and_train_queue.json)已完成。15:59:23UTC在fvcrc13启动g0 init/replay、g1 used/replay、g2 init/fresh_selected→init/fresh_law、g3 used/fresh_selected→used/fresh_law；只接续成功终点，全部失败保留，18 A100h预算watch启用。四臂已加载权重，但runtime_manifest/window_trace尚无首条；共享NFS模块读取仍在推进，不能把CPU预期N=1133记为实际训练窗口。[评估接续](../results/E13_eval_batch_plan.json)在fvcrc10 PID320801等待全部六支完成，逐终点搬运并核SHA后用同E12八任务协议评价；此时尚无E13 judge/API开销。
- **首窗实测（16:34:44UTC）**：四臂已进入真实训练，各有12窗口。首16行的监督量均为`[116,147,169,48,26,46,127,30,128,136,62,64,6,19,7,2]`，实际`num_items_in_batch=1133`，与预期一致；runtime确认`model_accepts_loss_kwargs=True`、Accelerator.GA=1/Trainer.GA=16、seed/data_seed29、初始optimizer/scheduler=None及global_step0。首窗符合契约不等于全部625窗已完成；后续由observer持续记录并检验。[首批运行证据](../results/E13_first_four_runtime_windows.json)。
- 六支真实效用及最终失败成本：待运行完成。
- 主张变化：C01–C04 L0；不能从规划升级。
- POST-HOC分析：尚无。

- **评价接续修正（17:42UTC，尚无任何效用评分）**：保持原八任务/学生与judge/checkpoint/训练终点不变，新增冻结v2 SHA04bb287c…只改两个工程contract：现成E12 judge实际build`0.23.0+cu129`不能与base`0.23.0`直接等号；18A100h总cap按六条queue wrapper含前检计。旧waiting-only driver/PID320801/state/日志保留，按同秒launchUTC/精确cmd/当前ticks确认所有权后仅TERM自有等待进程；新fvcrc10 PID330492/ticks1481834526在`eval_batch_v2`等待全部六成功终点。原script不改、训练不打断、judge未启；[probe](../results/E13_eval_v2_readonly_probes.json)与[新启动溯源](../results/E13_eval_v2_launch_provenance.json)记录身份及旧launch未保存ticks的局限。13没有现成evalenv/八TSV，沿用10路线，不搭第三环境。
