# MemTrain: Self-Supervised Context Memory Training（作者v1，2026-06；接收未核对）

`[证据级别：主文精读＋全部方法附录]` [arXiv2606.03197v1](https://arxiv.org/abs/2606.03197v1)，PKU／Samsung Research。16p PDF SHA94af969bc01b161681ac20b9d9a338c702dce232bc753ef280b18d65f71b50b2。主文1–6 pp1–10全文、AppA p16全文，Table1/2、Fig3、Table3 p7–9视觉核；参考文献不是逐篇深读，代码未全读。

1. **论文形态：** 面向后续memory RL的自监督预训练方法，而非一个memory QA benchmark。
2. **背景与压力：** MemAgent／MEM1在任务结局上学习压缩，数据昂贵且领域窄，episode reward可能只保留当前目标需要的东西。借RL pretraining／masked entity reconstruction，把可自动生成的目标变成多轮memory学习信号。
3. **idea来源（RECONSTRUCTED）：** 单轮CoT-pretraining不足以学多轮状态→多chunk遮掉所有目标实体→用final reconstruction训练维护／使用→再随机抽历史chunk，另遮实体，用中间memory回填→将回填成功一起奖励原memory生成。新动作是**未预先指定的历史信息用途反馈到写memory**，不是首次有重建或固定memory。
4. **方法：** End-to-end G1=8轨迹，随机中间k与此前l<k chunk，IMR G2=8；最终EM＋λ平均IMR EM，λ=.5，未归一化GRPO优势episode广播所有interaction steps。IMR同时训练检索使用和写memory。它是mask实体的可验证EM，非ABBEL整句token LP，不能将I07结果当它的证伪。
5. **数据／规模：** Wikipedia30k文档，每pivot top29相近＋120随机passages，NER选实体全出现遮掉，24–40k tokens；chunk约5k／memory1k、最多8chunk，训练300steps。两个Qwen3-4B-2507／Qwen2.5-7B，再MemAgent500steps或MEM1搜索200steps。原文实体可自动给Gold，但“原文无答案”不保证预训练中未记住实体；没有宣告纯记忆因果机制。
6. **实验：** 社区长HotpotQA7k–896k，平均MemAgent→combined Q4B65.14→70.31，Q7B55.86→73.53；Q4B448k64.06→61.72下降，不能说所有长度一致提升。搜索七QA两目标EM，Q4B21.50→32.08，Q7B23.94→32.44。后训练有3seed文字，但表未提供完整CI／方差。Full优于移除IMR的63.28；Decoupled较短优势／极长弱，支持耦合对象有用，不能单凭图认定具体hallucination机制。
7. **对照／成本边界：** 额外300steps预训练与多分支rollout；把MemAgent500延到800step是步数参照，不是与64个IMR分支的匹配GPU／token预算。Full-context未训练base与chunked pipeline也改变推理接口；主结果的matched MemAgent更有解释力。Table3视觉中左MemAgent正确、右MemTrain失败，而正文描述相反，例子方向未核代码／原轨迹，不将它当正机制证据；主表结果独立保留。
8. **近邻距离／claim ownership：** 继承MemAgent状态接口与MEM1后训练，继承RPT/RLPT的raw-corpus RL；所有实体masked＋未来随机historical回填用途是明确增量。一般“reconstruction监督memory”“reward要同时训练生成与使用”不能成为我们的新claim。
9. **对我们：** 它展示了有后果的研究动作：用一个自己缺的能力（未来未知的历史用途）设计自监督proxy并验证后训练泛化。I07若真实关系更新被raw reconstruction漏奖，需要回答实体/字面重建何时不能维护正确关系，并找到新信号；不能只是把GP加进其proxy、或只再测一张奖励相关图。它也提示保留旧证据与修改旧解释是不同操作，二者并非同一种“删除memory”。
