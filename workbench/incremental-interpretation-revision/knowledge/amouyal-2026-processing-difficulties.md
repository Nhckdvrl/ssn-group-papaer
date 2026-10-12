# Comparing human and language models sentence processing difficulties on complex structures — Amouyal et al. `[证据级别：预印本 v1 全文 + release 代码/数据]`

[全文 v1](https://arxiv.org/html/2510.07141v1)、[release](https://github.com/samsam3232/comparing_humans_llms_processing_difficulties)。Territory 登记 ACL 2026；最终会刊版本本次未逐页核对。

1. 论文形态：统一受控行为测量 / 人机比较。
2. 背景与压力：单构式结论难以跨 protocol 比较。
3. 改变的前提：相同 comprehension task 与匹配 control，覆盖七类结构、五家族。
4. idea 来源（DOCUMENTED）：整合心理语言学处理困难，比较跨结构排序和 target/control 方向。
5. 与最近邻距离：相对 Amouyal 2025 的单 GP 研究，扩展构式和统一任务；不据此声称我们的更多模型/结构有 novelty。
6. 方法 / 数据：发布 stimuli、prompts、结果；v1 LLM procedure 写 8-prefix average，实际 release runner 还含 reg/rev，两者需分别记账。用户指定 E00 使用 extended GP 切片。
7. 证据与短板：v1 明确 Qwen3-8B Subject/Object 不保持通常的难度方向；公开 release 也显示 order reversal。评审分数未核对。
8. 可迁移研究动作：先逐条对上发布结果，再区分 calibration-model mismatch 与 instrument bug。
9. 对我们：GP deficit/human comparison 归上游；E00/E03 仅 calibration。后续需区分初始 parse 的支持与最终 parse 可合法推出的语义，不能把同一个 Yes 自动写成 lingering memory。

## 2026-10-06 全文精读补记（arXiv v2，经 GCS 镜像）
- **规模：** 每类结构 40 组（Subj/Obj 沿用 2025 的 45 组）；人类用 Prolific RSVP（每词 400ms、不能回看、问题限时 5 秒、每人只做一题），每题 10 人，共 5,380 个数据点；31 个模型，8 种提示的平均概率。
- **核心 finding：** GP 对 LLM 特别难（GPT-5 非 GP 93.7%、GP 46.8%）；thinking 对非 GP 的帮助更一致，在 GP 上反而常常有害，例外是 GPT-5（Subj/Obj +55、NP/S +47）。随规模增大，结构难度排序与人更接近；"太弱或太强都不像人"（sweet spot）。
- **作者明确留下的问题：** 猜想 GP 难是因为要"从记忆中丢弃错误解释"，并写明"设计实验检验这个猜想是未来的关键方向"。
- **我们的审计**（`workbench/incremental-interpretation-revision/results/D0-Amouyal-released-item-type-audit.json`）：GP 平均值中混入了及物 Subj/Obj 和部分 NP/S 条目，这些条目在无歧义对照句上同样大量答 Yes，属于问题语义问题。真实错误条目（反身 Subj/Obj、RR、NP/VP）上，强模型仍有 25–65pp 的真实缺陷。
- **对我们：** 见 `workbench/incremental-interpretation-revision/ROUTE.md` 中的 C1。

## 2026-10-12 正式出版身份、构念和本workbench判断

**版本已核**：[ACL2026 正式入口，long.1040](https://aclanthology.org/2026.acl-long.1040/)；对应 [作者arXiv HTML v1](https://arxiv.org/html/2510.07141v1)。前文历史阅读 v2+release 检查不等于本轮重新独立审计了v2发布包；**本次额外确认的是ACL正式出版元数据以及v1主文、表2/3/附录E对照**，不是正式PDF所有页、每道题的重标结果。

**比较的是哪种任务**：七种句法/理解难点（四种GP+三种nonGP），统一target和matched baseline，英语受试者在Prolific逐词400ms+100ms空屏，答案时间5s，每人只接触1个实验句，10名参与者/句，总5380反应。31种LLM、五家族，常规设置为8个few-shot prompt的正确/错误token概率平均；thinking只用一个模板。作者表2的 GPT-5 GP46.8%、nonGP93.7%是特定非高思考条件的口径，不可当最新整体能力定理。

**论证边界**：模型human难度相似不等于同一解析算法；作者关于GP需要抛弃旧解释/working memory的论点是 **CONJECTURE**。另须分开“文本不蕴含 `hunt(man,deer)`”与“文本明确蕴含 `not hunt(man,deer)`”，后者在普通世界语义上不成立。**但**这并非当年作者完全忽略的错：Christianson2001主文pp371–372已经承认这个务实推论，并用无GP对照及RAT反身动词检验GP额外效应；参见[2001精读](christianson2001-thematic-roles-linger.md)。2026数据的gold协议依旧可作为测量操作，不能因为No非逻辑否定就一概废弃整篇。

**工作流启发**：跨大量模型/构式的稳健性可验证现象存在，但作为创新还需说清 *why one construction differs*、是什么导致错误回答、以及能否解释新关系生成与用途。E00校准必要，却不等于找到了自己的question。
## 2026-10-12 独立精读补记（作者v1 HTML；表1/§3数字核对）

七结构×40组（Subj/Obj沿用45组、干扰24组）；gold是拒绝误读的字面读（“Did the chef hire someone?”→No；depth charge “Can you ignore head injuries?”→Yes）。人类target平均28.3（Subj/Obj 13.3，RR 41.7）；GPT-5 GP 46.8 vs nonGP 93.7；thinking在GP上“更常降低表现”（Qwen-0.6B −25.7）。作者猜想“GP不压工作记忆，而需要丢弃误读；LLM工作记忆大所以非GP更好”，并明确标为待验证。**全文题目只问误读命题，不问替代依赖；无机制分析。** 这两点是我们增量的直接落点：若瓶颈在“丢弃”，拒绝率应低；我们E87显示拒绝率不低、断言率才低，与其猜想方向相反。
