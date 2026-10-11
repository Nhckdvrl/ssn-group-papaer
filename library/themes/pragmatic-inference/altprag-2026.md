# The Pragmatic Mind of Machines: Tracing the Emergence of Pragmatic Competence in Large Language Models（2026）

**证据：正文与关键附录B–F已读；G–J案例/全部表待核对；原代码尚未下载核查。** [原文](https://aclanthology.org/2026.eacl-long.9/) · [代码](https://github.com/Huangtubaye233/PragmaticsLLM) · [数据](https://huggingface.co/datasets/Huangtubaye233/AltPrag)
用户明确指定此parent，优先于仓库默认不参考EACL；投递仍只main。

1. **形态：** alternatives dataset + training-stage finding。
2. **压力：** pragmatic training阶段不透明，binary任务与解释质量不是同构。
3. **改变前提：** 同context两种有效utterance，解释意图与偏好原因；Base/SFT/DPO分别评。
4. **来源 DOCUMENTED：** alternatives理论、Ruis只IT显著、Wu PO增益；用阶段公开checkpoint追踪。
5. **近邻：** Hu/Sravanthi原情景作生成seed，Wu free-form/PO；本工作已拥有stage tracing，不能claim第一次看post-training。
6. **协议：** GPT4o生成1,298，三作者一致过滤650；swap response后1,300（非1,300独立情景）；22models，OLMo2 7/13/32B、OLMoE、Llama-Tulu3 8/70B三stage与Qwen3 base小尺寸。GPT4.1十点与pairwise；human子样本核对。
7. **短板/核对：** 原文称SFT/DPO总体增益，但OLMo2-32B SFT-over-Base win43.2%；DPO强。正文称zero-shot/无examples，附录B说fullURIAL包含example completions，需代码核查。judge Invalid剔除会变分母。跨family/data scale不能单因果归于token数；DPO不是泛称RLHF因果的所有算法。
8. **动作：** clean同family三stage、同输入readout、invalid全报；同设定两侧测量。
9. **对我们：** “gains=criterion shift”是RECONSTRUCTED待测解释；该任务含valid alternatives却未评系统unlicensed counterpart，不能与PaCE平均差直接构成矛盾。

## 2026-10-03代码补核
repo003a11d838353fdbe0a2cdb0945f5321428115fd已下载，原文件不改。main_base.py默认prompt_urial，含renewable-energy等example completions；main_base.sh/batch与main/main_instruct入口不同，instruct默认/脚本传prompt亦不同。main_base纯continuation、instruct代码主要tokenizer原text而不是统一chat模板。README under construction，公开dataset/scenarios_test_1300.csv与scores_array为1298行，stats_urial22models；尚不能对应论文650筛选/swap1300的canonical run。正文zero-shot与附录examples冲突没有被自动消除，需资产版本和原prompt追溯。
追加已读appendixA与G–K案例/表文本（视觉图尚未核对）：原generation要求三alternative、每组三pair，作者一致筛选；Qwen3 Base4B mean7.66与8B7.54不单调。总体结论不能复述成所有family/所有step都严格提高。
