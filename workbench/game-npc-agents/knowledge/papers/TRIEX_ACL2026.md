# TriEx（ACL2026 Main，全文相关部分＋局部作者代码）

主源：[正式正文](https://aclanthology.org/2026.acl-long.292.pdf)、[HTML](https://arxiv.org/html/2604.20043)、[作者代码](https://github.com/Einsam1819/TriEx)。核读§3–4/Table1–3、AppendixA.1/A.3与B.2干预、B.3审计入口。代码只读`experiments/exp2c_intervention/exp2C.py`及`scripts/players/llm_base_player.py`中取状态、profile呈现与干预路径，未运行API/扑克复现。

**DOCUMENTED：** Texas Hold’em、6模型、50 battles×30 hands，显式记录本人解释/对手profile与引擎参照。以相同状态rerun-original控制随机变化，再改数值profile；已有“信念替换影响动作”的直接证据。动作有CHECK/FOLD/RAISE规范化，胜率/赔率是引擎计算参照，解释正确性还用LLM与规则双审计。

**代码事实：** profile数值经`format_opponent_profiles_for_prompt`进入决策prompt；`replace_profiles_section_in_final_prompt`替换该段。这里的internal state是可见显式profile，不是残差流激活干预。正文所说自然语言不变是其他描述/指令不变，不代表整个prompt字节不变。

**RECONSTRUCTED idea来源：** 将社会博弈解释从自由理由转成可对照、可干预、可随时间核查的对象。**对我们：** E74物理预测替换不申领新干预技术；应判断角色自身后果理解与受益对象选择能否解释E70–73的效应换向。普通预测—行为相关或不相关不能被叫作内部因果机制。

资产cache/papers/triex_acl2026.pdf，SHA256 `1a9dbf595a0c420c025eec3cbba14a60a44098737694ec2c13654460d701eec2`；局部代码cache/sources/triex-audit/，仅审计不安装其云客户端。

早期arXiv阅读还明确记录：B.2使用显式belief数值的logit perturbation（δ2.5），另50次同belief rerun估计采样波动；不是激活向量干预。equity/pot-odds规则和oracle输出都不是内在解释的真值。该次旧预印本PDF SHA为dfdc81bb542558a0f5852873163e16ebb5feaf28f6d7adea1fc7789cdce8bbad，与上方正式正文资产分别保留；后续已读局部作者代码，早期“尚未clone”不再作为当前状态。
