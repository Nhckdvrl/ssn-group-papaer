# ProAgent: Building Proactive Cooperative Agents with Large Language Models

规范记录：`zhang_2024_proagent`；AAAI 2024, 38(16):17591–17599; DOI 10.1609/aaai.v38i16.29710。实际版本：Official AAAI proceedings PDF; author-hosted supplementary (undated) read in addition。

**实际阅读范围：** Complete main text, PDF pp.1–7, all method/evaluation/discussion/conclusion sections; Table 1 and Figures 1–4; Author supplementary pp.1–7, Appendix A–D: state/action interfaces, GPT model ID/settings, prompts, baseline checkpoint provenance, failure discussion; Official code repository README model/baseline configuration notes; full-log Appendix E pp.8–18 not read

[原文](https://ojs.aaai.org/index.php/AAAI/article/download/29710/31219) · [发表／主源信息](https://ojs.aaai.org/index.php/AAAI/article/view/29710)

**稳定 ID：** `zhang_2024_proagent`。AAAI 2024，38(16):17591–17599，正式PDF；作者站补充材料为未标日期版本。**实际阅读：** 完整主文（PDF 1–7），补充材料A–D（1–7），作者代码仓库README模型说明；补充E完整运行日志未逐行阅读。

ProAgent让商业LLM做合作技能选择，把原始Overcooked结构状态转为自然语言，给出任务规则、合法技能与示例；规则有效性检查、失败解释与重规划确保输出可执行，搜索控制器负责移动、绕过队友阻塞，无目标时随机移动帮助打破僵局。补充B.1.2核定主模型是 **gpt-3.5-turbo-0301**，temperature 0、max tokens 256。作者README也明确主实验2023年6–8月完成。该系统并非裸LLM，也不是从像素控制：补充D报告符号地图距离和MiniGPT4视觉直控均差，因而把空间控制交给搜索。

五个经典布局，SP/PBT/FCP/MEP/COLE与ProAgent形成36种有序配对，每对5轮；各地图400步，人类代理评估使用5个BC模型。主文在大部分地图与位置优于这些已提供的策略检查点，强制协作右侧明显输PBT；没有真实人类参与研究。最值得细读的消融是：主实验 **L2分析、不含显式意图推断，recent-1**，而完整意图/信念框架只是Cramped Room单地图消融，L1/L2/L3为100/184/204分；不能把主表全面提升归因于信念修正。去除Verificator后100步技能成功率20%，但这无法单独区分基本合法性修复与高级社会推理。作者仓库说GPT-4-0314和text-davinci-003扩展比较只与Greedy在五布局协作，本轮未获得该比较结果，不当成GPT-4全基线证据。

贡献是展示通用语言知识加状态、技能、反馈和普通搜索就能形成无需新策略训练的有效合作伙伴。这直接要求后续学习方法认真对待这样的系统基线。边界也清楚：固定共享得分、六类技能、少量布局，BC不能代替会在线适应的真人；低层工程本身会贡献协调效果，没有等接口的规则规划器消融隔离全部收益。它支持“模块化LLM合作已是可行起点”，不支持“人格、冲突利益或持续社会关系已经解决”。

**主源：** https://ojs.aaai.org/index.php/AAAI/article/view/29710 ； https://pku-proagent.github.io/static/pdfs/appx.pdf ； https://github.com/PKU-Alignment/ProAgent

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Building Cooperative Embodied Agents Modularly with Large Language Models](ZHANG_2024_COELA.md) | ProAgent 主要在完整符号状态和技能执行下做非显式通信协调；CoELA 把部分观察、共享消息和发话时间纳入协作。 |
| [Learning Zero-Shot Cooperation with Humans, Assuming Humans Are Biased](YU_2023_HSP.md) | ProAgent 主模型为 GPT-3.5 加状态工具，无任务策略训练；HSP 以大量游戏训练构造偏好伙伴和响应，比较须对齐接口与检查点。 |
| [Benchmarking the Limits of In-Context Reinforcement Learning for Ad-Hoc Teamwork](JING_2026_ICRL4AHT.md) | ProAgent 有完整符号规则、预训练语言知识和低层搜索；ICRL4AHT 的局部观察离线序列学习负结果不能直接迁移到此条件。 |
