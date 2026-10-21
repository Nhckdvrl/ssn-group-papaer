# D-E02：LongEvoRoleBench官方文本状态基线驻留（2026-10-22）

- **状态：** DONE
- **类型：** REPRO
- **对应：** 矿区D驻留D1/D2；与D-E01独立任务，研究长期对话中当前状态对人物表现的作用，不跨benchmark混合原始分数。
- **问题（一句话）：** 原始人物卡、普通重写卡与PHASE-Tree当前状态，在官方长程下一轮回复任务上各起什么作用？
- **设置：** 固定PHASE-Tree代码`0be378fd23c49915255406d881f2389b46b608b8`、LongEvoRoleBench数据`ce09fb68439963c71c3035ee2918c21ae02a3cbc`。四长程来源Friends/TheOffice/HPD/StarTrek_TNG，每来源8 random_test+8 ood_test，总64真实question；按role固定hash分层，不挑戏剧反转或弱模型坏例子；所有条件question/input/output逐字段配对验证。
- **基线：** Base=context only；RP=m2_raw_profile；NR=m3_naive_rewrite；PT=m6_phase_tree。使用官方build_prompt而非另造提示。Qwen2.5-7B-Instruct revision `a09a35458c702b33eeacc393d103063234e8bc28`，BF16，temperature0.3、seed42、max_new_tokens256（原设定），4条件合计256条。使用完整prompt、16384上下文上限，与官方vLLM推荐一致；不使用其HF后备路径的4096静默截断。记录超长/截断和tokens。
- **评价：** 先本地Qwen3-32B（revision `9216db5781bf21249d130ec9da846c4624c16137`，非thinking/greedy）运行原官方Char/Sem judge rubric，m6当前profile为各条件共同参考。该本地评委不同于官方GPT-4.1，明确标注、不能当论文分数精确复现；独立抽检候选与判语。官方Emb需要未授权的OpenAI embedding服务，本轮不调用、不用其他向量指标冒充。
- **读数：** Char/Sem按corpus、split、role报告，完整question配对；生成/评价有效率与长度；原始卡/重写/PT输入tokens；台词与上下文状态来源的代表性审阅。不把OOD说成未见过的作品/角色，长程OOD主要是后续时间。
- **阳性对照：** 同question四条件上下文和参考回复相同，只有profile条件不同；原官方prompt函数字节核对；ref只进入judge不进入actor；样本和模型revision先冻结；本地judge固定同一模型/提示不看方法名。
- **噪声地板 + MIE：** 首轮每条件一次seed42；LLM分数非客观真值，四corpus macro与角色分布比微小均值更重要；不以64派生台词当64独立角色，不凭样本饱和升机制主张。
- **混杂审计：** PT profile本身由官方树生成且作为共同judge参考，是该benchmark的设定；NR是重要普通对照；完整profile与生成成本不等；固定解码采样而非greedy；HF/vLLM数值实现不同；未经追加独立人评不称玩家成长价值；原数据许可及来源写资产索引，不将小说/影视原始全文搬入Git。
- **决策表（跑之前写）：** PT明显帮助→认真理解官方成功及其事件来源；NR接近PT→接受普通重写的竞争力；多指标排序不同→观察实际台词/参考profile，先不判judge失效；强普通系统已好→不造新动态树；有稳定且与事件证据相关的残差→与ArcANE独立任务对照后选研究动作。
- **算力预算：** Actor1 GPU·h以内，local judge2 GPU·h以内，先256条；本卡不新增付费API。若后续需要Step交叉评委需另登记固定样本和预算；不自动扩大。**实际：** 待填。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

待填。完整许可数据/模型/输出在`/var/tmp/ssn-game-npc-d/`，Git只存来源、IDs与轻量结果。

## 实际结果

角色256调用、本地判分256调用均完成。Char/Sem：Base3.172/2.969，RP2.641/2.328，NR3.453/3.047，PT3.656/3.281。PT−NR Sem +0.234，四corpus描述区间[+0.063,+0.422]，逐题胜/平/负21/32/11。无外部API，进程wall约0.675 GPU·h。全部stop；一条多余闭括号按原native parser恢复，严格JSON轨仍单列。见[报告](../results/D-E02-REPORT.md)。

只是对现成方法效果的有限复现，不升新机制主张，不将RP离题自动视为过期人物状态干扰。后续回到真实状态来源及跨阶段问题，保持D宽研究空间。

### POST-HOC原文预测读数（计算前登记，原主读数不变）

自由生成的Char/Sem已完成后，追加同一64题×4原生输入下的参考下一句条件NLL，使用原Qwen2.5-7B checkpoint，不新采样/改提示/改场景。只对assistant正文原token计平均负对数概率，prompt不计loss，记录明确token边界；四条件目标文本完全相同。它回答给定状态是否有助于预测已有原句，不能把原句当唯一合法续写，也不替代原主观生成评价。所有题保留，按四语料宏平均及逐题配对；不据其方向回改主表或挑案例。最多0.25 GPU·h，无API、无新增角色生成请求；结果独立附表。

补充NLL已完成：Base/RP/NR/PT=4.428/4.517/4.537/4.220 nats/token；PT−NR−0.318，四语料描述区间[−0.490,−0.145]，38/64逐题降低。256 forward、0新增生成，wall155.3秒。主Char/Sem及主张等级不变，结果见D-E02-likelihood.json；不能把原句预测当唯一有效角色回答。
