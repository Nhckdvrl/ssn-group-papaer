# Rethinking Psychometric Evaluation of LLMs（2026）

证据：正文§2–6、附录F/I.1–I.9/J/K，Table13–21与提示表；src/runner/tpb_likert_runner.py和sycophancy_runner.py定点审计。没有本地模型复算其论文数字。作者repo声称NeurIPS2026接收；[arXiv](https://arxiv.org/abs/2606.12730)列ICML CTB workshop oral，main官方未核。

- **DOCUMENTED / idea来源：** 对先前解耦结论提出“量表过粗与会话分离”解释；2×2×2比较BigFive/TPB、同/跨会话、参数/persona归纳。11模型4任务。三类volitional任务同会话TPB pooled r=.40 [.37,.43]是作者报告；IAT作为scope control，不能混入同方向均值。
- **关键审计：** TPB问卷已包含mirror政策内容；同会话行为会看到回答，所以相关性包含priming。Table13/21阿谀r .47→-.07，诚实.67→.53；作者已研究共同原因vspriming，不能冒领“问意图会影响行动”。n≈54/60不是跨模型泛化样本量，between-model独立簇只有11。
- **代码事实：** Likert全维度同分会nudge重采样；seed参数不支持会重试不带seed。全文结果与某版本代码是否逐行对应未核，不能由代码有nudge认定结论作废。
- **对NPC：** 分开自述、当前行动意图和执行；独立支线probe不写入vanilla行动历史，same-session单列。核心剩余压力是意图经工具/状态转化后的后果，而非再发现粒度和上下文效应。

**源码来源补充：** psychology-of-AI/Rethinking-Pyschometric-Eval-LLMs@4617b3c014d9f16ea81bdbe69188f13b49664b04。openai_compat.py blob 1c85074953a42c230ee652042031c749df180dc5含不支持seed时去seed重试；tpb_likert_runner.py blob d95e285e3f72b83f35b1d1984f3edae8045cef19含全维度相同评分时的ANTI_COLLAPSE_NUDGE。Sycophancy每episode两回答，base_system_prompt与task_context可独立进入；默认OpenRouter不等于本地复现。存在回复质量重试不是自动判论文无效的理由。
