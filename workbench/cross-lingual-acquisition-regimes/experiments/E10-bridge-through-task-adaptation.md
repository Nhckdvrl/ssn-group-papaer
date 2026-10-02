# E10：bridge-through-task-adaptation（2026-10-02）

- **状态：** DONE（全部八LM测量、原始输出及统一分析完成）
- **类型：** EXPLORE（已实际运行的训练干预在后续学习中的能力保持；非新prompt分支）
- **对应：** P03/P05
- **问题（一句话）：** 相同文本/预算的条件连接建立了什么翻译能力，它能否跨英语任务学习保持；不重叠桥接与新任务内容覆盖在这个实际训练选择上是否不同？
- **设置：** E04四格joint seed17的已保存完整CPT LM，以及同冻结E03 recipe任务学习后的完整LM。E08同Blackwell/FP32/400固定WMT16输入、primary及原一句instruction；共8完整LM顺序测。CPT和post严格区分，全部四格保留，未读本卡翻译结果选条件。只用E06/E08固定协议，不改变句长、prompt、停止、精度或评分。与同硬件原MWB及其QA终点零CPT锚点联结，不假装其预算相同。
- **读数：** CPT/post各方向BLEU主、chrF辅、copy/empty/cap/overflow，post−CPT的paired sentence95%CI；paired−split及其保持差、new−reused全部报告，配合E04完整EN/DE QA曲线而非只报保持比例。条件交互只是发现性，不能筛种子或快照。原始输入/模型/脚本/结果hash、时间含加载边界说明。
- **阳性对照：** E08硬件与原模型协议核对；E04正确同内容/mask/逐语言预算及DE conditional NLL杠杆已成立；不把NLL当翻译成功。本卡若CPT无可测MT改善，直接记录，不借选择QA快照造收益。
- **噪声地板 + MIE：** 固定news200句/方向、单CPT+适配seed，item CI不是种子或跨域CI。约3 BLEU/明显照抄代价影响扩展优先级，不作为自动claim门槛；完整预训练seed未复现。
- **混杂审计：** 配对/隔离同文本、loss mask/顺序/位置/训练token预算；new/reuse逐语预算近同且context数量/重复配平，语义主题/质量未固定。干预量是训练conditioning，不是所有格式的纯alignment；attention FLOPs、初始翻译强弱与其对保持的影响未全控。post是真实完整LM；任务extractive QA、单family限制。不得将before高→after低的比例数学耦合当新机制。
- **决策表（跑之前写）：** E08主要环境伪影→不启动并降级P05；CPT翻译改善且post消失→后续适配破坏候选，针对真实训练时序/目标做最小干预、与已知replay/译料监督比较；CPT收益保持且QA也正常→保留可用训练决策，先定位近邻而非发明新名字；仅小差→保留资产、不扩same-probe grid、不从领域退出。若改善仅来自更强起点/质量→不归因鲁棒性。
- **算力预算：** 八LM每个≤1 GPU·时、总≤8，一张空Blackwell顺序跑，白天并用≤8；不用新训练完成本测量。**实际：** 尚未运行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
卡写于E06发现之后、E04完整任务曲线分析与任何本卡翻译读数之前；明确是E04原QA-primary之外的新测量承诺，不回写E04为事前预期的保持发现。

E08通过后启动fvcrc20 GPU3顺序CPT四格；生成loop与E06 AST完全相同。为避免共享盘mmap demand paging，每个完整checkpoint复制到节点`/var/tmp/C_retention_*`，所有文件source/copy SHA256逐一相等才加载，测完删除该临时副本；HF缓存/原始checkpoint不变。stage/load/generation各自记时。E04任务学习继续，本题总并用5张，不杀其他研究作业。

执行追加：E04四格已全部完整保存；CPT测量仍按原顺序进行。post队列必须看到四份CPT测量及四份QA完整pipeline保存记录、GPU显存释放才接续同卡全部四post，随后统一统计；不根据已完成的个别CPT选择post条件。`queue_bridge_retention.py`仅启动门槛，不改生成/评分/训练。当前E07另用一A100，E09等待队列不占模型训练卡，不冒称五张仍在并用。

完整结果（2026-10-02）：下列四格均为new paired/split、reused paired/split，全部使用固定200句/方向。

| BLEU | new paired | new split | reused paired | reused split |
|---|---:|---:|---:|---:|
| EN→DE CPT primary | 15.41 | 15.55 | 18.02 | 15.58 |
| EN→DE post primary | 18.19 | 9.09 | 17.69 | 9.36 |
| EN→DE CPT instruction | 21.19 | 16.51 | 20.59 | 16.61 |
| EN→DE post instruction | 17.77 | 9.76 | 16.20 | 10.35 |
| DE→EN CPT primary | 12.11 | 19.14 | 10.42 | 18.88 |
| DE→EN post primary | 11.15 | 12.49 | 11.15 | 13.93 |
| DE→EN CPT instruction | 16.94 | 20.22 | 14.35 | 19.86 |
| DE→EN post instruction | 11.49 | 13.63 | 11.26 | 14.47 |

EN→DE post paired−split：new +9.10[6.95,11.38]、reused +8.34[6.22,10.72] BLEU；同instruction为+8.01[5.54,10.49]/+5.85[3.72,8.40]。但DE→EN post primary为-1.34[-2.77,0.55]/-2.78[-4.44,-0.84]，同instruction为-2.14[-3.86,-0.16]/-3.21[-5.01,-1.06]。
EN→DE照抄post四格44/90/50/93，DE→EN为101/78/93/64（各200）；无empty/overflow，全部cap保留。

不能写parallel普遍保持能力：E04冻结构造只用EN文档→DE文档顺序；direction是conditioning干预的一部分，未做双向训练。这与JGP §6.1明确的单向/反向失败直接重叠，并不是新novelty。尤其primary看似保持的paired模型，同instruction前后仍下降；不能选择primary增量命名鲁棒性。全部factorial、保持差与chrF在 `results/e10_bridge_retention_analysis_seed17.json`；单joint seed、news任务和不等FLOPs边界不变。
下一动作：用完整QA、MT两目标与标准译监督参照决定训练选择，先面对双向组织、replay、输出行为等已有解释；不扩同QA的小coverage grid，不由此自动退出领域或升级C##。
