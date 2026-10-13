# 所选切口的资产、基线与可用性

2026-10-13第四轮；执行优先级以[EXPLORATION_ENTRY](EXPLORATION_ENTRY.md)为准。**源码/来源已核查不等于游戏和模型已跑通。**

## 1. 首选世界：LIGHT

固定仓库提交：`facebookresearch/LIGHT@71a06cae8573048b1af41507ac52fe33b650fab3`。代码为MIT；任务/模型许可必须分别确认。

本轮直接检查的文件：

| 文件 | Git blob | 确认了什么 |
|---|---|---|
| README.md | ecc5717608ada580fffc24ed2ac2c5fd375b7812 | OOGraph、GraphEvent、Soul分工；模型迁移/服务说明有TODO |
| light/graph/README.md | 6fa39500950bf40083634ec8fb207bc9e4362150 | 可序列化世界、容器/邻接、节点删除和局部检索；不是语言模型写世界真值 |
| scripts/examples/play_map.py | 4dada31b28619d227dc4086341f02c7e6fb31e78 | Hydra入口、规则Soul可用分支、遗留cluster路径；同时导入模型相关组件 |
| setup.py | 5038e34f140bec89293f839ce51859b451b48e7f | Python>=3.8、light0.2、依赖ParlAI；不等于任意新Python兼容 |
| requirements.txt | 3dc425de4c0bda41edf0e3d3a79d96578218c600 | 大量只有下限的依赖；需运行后产生真实lock |
| projects/quests/README.md | b890d931f41c6ca96213caadd5c53bfe077d2b92 | 当前这里主要保留早期Predictive Machines入口，不保证Dragon完整包 |

官方 simple_world 已查看：含人物、容器、物品、事件条件与规则响应，可作原生engine smoke test。它是官方演示，不是我们的自然研究数据。

代码层已确认的示例命令是 `python scripts/examples/play_map.py builder.load_map=scripts/examples/complex_world.json`，不是旧README的`--load-map`。**此命令本轮没有执行**；先在隔离的Python环境中处理依赖与配置，不直接污染现有vLLM环境。

## 2. 自然任务资产与获取状态

正式[项目页](https://parl.ai/projects/light/)区分原LIGHT对话、WILD互动、Dragon quest与ATOMIC；不要混用规模和split。

- annotated quests官方链接：`https://parl.ai/downloads/light_project/quests/quest_stems.tar.gz`，跳转到`https://dl.fbaipublicfiles.com/parlai/light_project/quests/quest_stems.tar.gz`。
- 原LIGHT任务入口：ParlAI `light_dialog`；WILD：`light_dialog_wild`。项目页说quest completions在WILD中，**不意味着整个WILD就是原2111示范及其split**。
- 本轮查看ParlAI `parlai/tasks/light_dialog_wild/build.py`，blob `d3720506236c4e371e0467e2c90a98a49c32d681`：先下载manifest，再按其中hash下载dumps。该builder有过滤/选项，不能随便沿默认过滤后说恢复了论文数据。
- manifest源码给定hash：`c708fe62692f239a2b35025d71722c7607f863ffa110aa118f2e1d0fa7db4730`。它是builder列出的资源hash，不是我们已下载后独立算出的hash。

**本轮未取得归档字节。** 浏览器无法读取tar.gz，容器下载未成功；quest实际schema、归档内许可、哈希和当前引擎兼容性仍须在授权节点下载后验证。不得宣称已读64/240条数据。不存在以手造任务替代归档然后标为原版复现的回退。

恢复步骤已明确：取得归档及terms→列文件和schema→恢复作者split→保留源ID与原始目标/时间线→验证原生世界→记录失败与筛选分母→再定义可观察且可达的分支。歧义目标独立标出，不用LLM强行投票变金标准。

## 3. 本地模型选择与版本

初始两家族参考：

| 模型 | 初选版本依据 | 用途与限制 |
|---|---|---|
| [Qwen3-14B](https://huggingface.co/Qwen/Qwen3-14B) | 官方commit列表当前短SHA `40c0698`；下载前解析并存完整SHA，不以main长期运行 | 原生指令/角色能力；thinking开关由真实chat template配置并记录，非只写一句no_think |
| [Mistral-Small-3.1-24B-Instruct-2503](https://huggingface.co/mistralai/Mistral-Small-3.1-24B-Instruct-2503) | 官方API返回 `68faf511d618ef198fef186659617cfd2eb8e33a` | 独立家族，固定模板/推理预算；文本任务不用视觉输入 |

官方模型卡列Apache-2.0。这些是可复现和本地成本参照，不声称2026最强模型；先检查用户已有缓存，不重复下载。更强单节点模型用于确认基本能力与规模趋势，但不一开始全卡部署70B。KV cache、服务版本、量化、CPU和I/O必须实测；权重版本已知也不等于权重字节已经下载。

## 4. 控制器基线与公平性

B0全文目标/可见状态/事件历史；B1普通目标保持与计划可修改提示；B2每步重规划并匹配可用事实；B3目标/事实/计划分开保存；B4适用子集的规则/GOAP。均为强控制，不是注册的新方法。

NPC只能看到同样的局部可见信息。全状态+形式化目标规划器为oracle，报告它覆盖哪些任务，不把信息特权当算法优势。合法动作列表在对比条件间保持一致；首次解析/长度/超时错误不删样本。

原Dragon的固定伙伴、学习DM与离散候选检索不是当前现代生成基线；更换这些后称“受控任务适配”，不声称复现原论文数值。

## 5. 备用资料，不再无界扩工程

Hypothetical Minds/MeltingPot、GAMMA/Overcooked、Collab-Overcooked是行动/伙伴适应近邻，资源事实见前轮[RESEARCH_CALIBRATION](knowledge/RESEARCH_CALIBRATION.md)。alem是新近协调性测量参考；NARRA/NCP/CDT是叙事/角色参照；它们不成为同时执行的六个工程项目。

若LIGHT任务恢复失败，优先寻找支持同一“自己的目标+合法玩家改变世界”问题的公共资产。不要为了保持LIGHT名字从零写游戏，也不要因为某备用环境易跑就改回泛用MARL排名。
