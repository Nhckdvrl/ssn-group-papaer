# A Pragmatic Account of the Weak Evidence Effect（Open Mind 2022）`[证据级别：最终正文全文、关键原代码；补充PDF未取得]`

Barnett/Griffiths/Hawkins，6:169–182，[最终正文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9692057/)，[原code/data](https://github.com/s-a-barnett/bayesian-persuasion)。正文含Eq1–9、Table1全文已读；final SI链接返回HTML验证页，未绕过，Appendix A–E未读。README、原behavioral_analyses前150行、shared.js的J0/S1/J1入口与model criterion公开表已读，未全文审完实验JS与shared.js后半，也未重跑WebPPL/WAIC。

1. **论文形态：** 经典现象的重新归因＋可区分理论的受控材料；重点不是发现弱证据反效果。
2. **压力与idea来源 DOCUMENTED：** weak evidence effect已有AA/MAS、causal与sequential解释。都能解释平均反转，故再报反转不能区分机制。RSA引入rhetorical sampling，预测反转取决于speaker被期待怎样挑证据；把“效应有没有”升级为“哪些证据来源下应出现”，这是主要研究动作。
3. **改变的前提：** 信息是被有目标的人挑过的，非直接世界观测。Epistemic与persuasive utility相加；真实但弱的正向证据可以因“更强证据为何没被选”而降低对目标世界命题的相信。推断更远未必更乐观，也未必更不信任所有内容。
4. **最近邻距离：** Fernbach2011拥有weak evidence；McKenzie2002拥有minimum acceptable strength；Goodman/Stuhlmüller2013拥有知识限制与信息选择；Harris2013拥有faint praise/omission。这里把persuasive goal与same-person speaker expectation联系，比较社会/非社会账户。ICLR2026目标权重与SDA2026战略commitment已有后续LLM ownership，不能claim首次发现LLM的goal-sensitive skepticism。
5. **实验/数据/基线：** 两contestants都看到五根1–9inch sticks，listener只看到他们选的一根，各自奖金目标longer/shorter公开。先用固定{2,4,7,8,9}测speaker选证据顺序，再测first evidence4/3/2/1或6/7/8/9后的0–100mean-belief；first goal顺序平衡，弱证据多分样本。804recruited/723通过；485人期待最强、238人期待较弱。弱证据下target-direction belief34.7 CI[32.3,37.3]与50.1；group×strength t(718)=5.2。only-first-response主分析，second response有order effect另附录，不能混算独立participants。
6. **比较强度：** Table1 speaker-dependent RSA MLE12.0、WAIC−16.4、PSIS-LOO−9.2；MAS hom8.2/−13.3/−6.6。优势在conditional prediction而非一个correlation；各SE约9，不能凭排序宣称统计显著胜过所有替代。MAP β2.26、speaker群mixture .99/.1为模型拟合，不是神经内部读出。在这个task αβ只以乘积进入，作者明确不可分识别；两参数不都叫机制。
7. **短板：** speaker expectation不是随机操纵，可能同人attention/motivation驱动两个任务；speaker phase恒在listener之前，carryover未隔离。正文主动建议训练speaker或cover-story操纵，但承認其新混杂。bounded numeric evidence不能直接推广真实不确定argument strength；人群mixture不是单个model sampling。原repo Rmd要求data/replication.csv，当前public data只有prolificData/initial_sample；processed replication model input727行与正文723不同，尚未核对不能直接作为精确norm或自行删4行。
8. **可迁移动作：** 先写不同解释对边界的不同预测，再看原human同人expectation是否约束belief；把literal可得信息与source selection mechanism分开。用held-out conditional prediction比较解释，保留不确定性/不可识别性。source选择与概率推导需要按有重复的stick instance计数，不能只按unique lengths；先审原枚举与尺度。
9. **对我们：** 最初territory中的inference tendency不能默认只把Hit/FA同向提高。在选择性信息情境，正确语用推断可能逆转字面证据的world-belief方向，而意图/承诺判断仍保持。它提供规范明确的conceptual对照，但当前资产/最终SI未完全核对，暂不铺GPU，也不把一次数学题失败变成领域发现。

**未知 RECONSTRUCTED：** 对source选择机制的明确预测，能否同时解释模型对隐含意思和世界事实的更新；post-training改变机制预测、后验使用还是响应目标？这个关系应在独立自然材料中保留，不能只剩five-stick sandbox。先原材料与human过滤驻留；未形成paper claim。

补读：replication原instructions/quiz/speaker四turn与judge入口、shared.js的J0/S1/J1/J2主计算已读。J0以已观测stick加四个未观测iid组成world；speaker归一化遍历stick instances，重复长度必须保留。模型meetsTarget用long≥.5/short<.5，原界面说longer/shorter5in；正式规范必须明确sampling及tie convention，不能偷偷用.5中性金标准或去重长度。SI再次公开页面访问遇验证，未绕过；原剩余model-comparison/code尚未全文审。
