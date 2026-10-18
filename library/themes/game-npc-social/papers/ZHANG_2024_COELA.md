# Building Cooperative Embodied Agents Modularly with Large Language Models

规范记录：`zhang_2024_coela`；ICLR 2024, official conference proceedings。实际版本：Official ICLR 2024 proceedings PDF, 29 pages。

**实际阅读范围：** Complete main text §§1–6, PDF pp.1–9; Tables 1–2 and Figures 1–5; Appendices A–D, pp.16–24: perception, memory, execution, environments, model training, baselines, human study, cooperation biases; Appendix F pp.28–29 template communication baseline; Appendix E full example prompts pp.25–27 not read; videos not watched

[原文](https://proceedings.iclr.cc/paper_files/paper/2024/file/54b8b4e0b4ba4aad112e84f32e3b5dbb-Paper-Conference.pdf) · [发表／主源信息](https://proceedings.iclr.cc/paper_files/paper/2024/hash/54b8b4e0b4ba4aad112e84f32e3b5dbb-Abstract-Conference.html)

**稳定 ID：** `zhang_2024_coela`。ICLR 2024正式29页PDF。**实际阅读：** 完整主文§§1–6（1–9），附录A–D（16–24）、F（28–29）；E中25–27页完整提示样例未读，视频未看。

CoELA把协作置于分散、部分观察、发话占行动时间的环境：感知建立语义地图，记忆维护物体与伙伴的最后已知状态，LLM先生成候选消息，再从当前合法高层动作清单决定发话或执行任务，A*和交互程序实现低层控制。共享目标由多条物体重排谓词定义。TDW-MAT用RGB-D、已知相机/自身位置及53k环境图训练的Mask-RCNN；有无oracle perception分开报告。C-WAH的“视觉观察”包含真实实例ID掩码，“符号观察”提供同房所有物体信息，均不能等同仅看RGB。动作空间还具有走到目标物体/房间等抽象。

正式实验GPT-4（未给固定API版本；给出2023年5月/9月运行窗口），温度0.7；两环境分别24任务回合（6测试场景×两任务类型各两样例，3000帧）与10任务（5类家务各2，250步）。GPT-4每任务仅1次，规则基线5次。TDW运输率两CoELA为0.71，规则双人0.61；有oracle提升到0.85/0.75。C-WAH视觉完成步数92对双MCTS103，符号57对75。CoLLAMA由10训练回合收集的2k条轨迹记录人工挑572条，用LoRA微调13B模型，运输率0.70接近GPT-4。MAT虽有集中和oracle信息但仅训练2e5帧，不能据此证明RL普遍不适用。

人类研究N=8，每人10轮总80轮，四条件：独玩、MCTS模板沟通、CoELA、无沟通CoELA。自然语言CoELA的信任评分6.3对无沟通4.7，报告t检验p=.0003，效率也改善；但极小被试数、重复测量不能当80名独立样本。AI–AI去掉通信没有显著性能下降，故漂亮对话例子不等于通信在全部条件必要。作者解释其偏向信任与合作来自指令遵循，对恶意伙伴可能失效；没有测试独立人物目标或冲突利益。

这篇实质性连接了伙伴请求、共享进度、行动分工和环境结果，并把沟通何时值得占用行动时间纳入问题。局限不只LLM推理偶错：抽象把低层动作遮住，会令伙伴误判对方正在做的事；空间信息缺失可产生语义合理但低效路线。必须区分商业模型能力、合法动作生成器、感知真值、搜索控制器和评价层级，才能判断改进来自何处。

**主源：** https://proceedings.iclr.cc/paper_files/paper/2024/hash/54b8b4e0b4ba4aad112e84f32e3b5dbb-Abstract-Conference.html ； https://umass-embodied-agi.github.io/CoELA/

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [ProAgent: Building Proactive Cooperative Agents with Large Language Models](ZHANG_2024_PROAGENT.md) | CoELA 显式选择是否发话，并有小规模真人合作评估；ProAgent 主表不含完整显式意图推断且没有真人测试。 |
| [Scaling Instructable Agents Across Many Simulated Worlds](SIMA_2024.md) | CoELA 通过语义地图与合法高层动作减少原生控制难度；SIMA 的共享接口是像素、语言及键鼠，任务分数不可直接对比。 |
| [Collaborating with Humans without Human Data](STROUSE_2021_FCP.md) | FCP 从非语言伙伴分布学习配合并做较大真人实验；CoELA 用通用语言知识和通信模块，真人 N=8 限制外推。 |
