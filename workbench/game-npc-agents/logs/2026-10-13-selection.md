# 2026-10-13 第四轮：完成定向选题核查，选定探索入口

## 本轮决定

用户明确要求完成准备并选定切口。本workbench不再停留在并列候选：**选择NPC目标承诺与计划适应**，具体看正常玩家改变世界后，角色是否保留自己的目标、改掉失效路线并按真实完成条件结束旧任务。E03/E04是当前执行顺序，不恢复CPDC/E02，不改全局ACTIVE。

## 实际完成的工作

重新读取当前workbench、源码和资源边界；本轮补查LIGHT/Dragon原始任务、Direct Behavior Specification、Goal Drift、Everitt goal-directedness、Arghal行为/表征评价、Bayesian重规划近邻，以及新近NeurIPS的alem/NARRA等。Dragon、Direct Behavior、Goal Drift的PDF图示以截图核查；HTML阅读范围见GOAL_CONTROL_REVIEW/FRONTIER_CHECK。

核心更新不是增加标题：Goal Drift已拥有工具性目标切换/模式延续；Arghal已拥有无用钥匙及内部地图/计划分析；Bayes已有推断-行动间隙。这些约束收紧了我们可能的贡献。经典GOAP更早已有目标/计划分离，必须是强基线。

读取LIGHT pinned main、setup、requirements、graph说明、play_map代码、quests目录、官方simple_world事件例子及ParlAI WILD builder。验证模型卡/版本入口。原生事件、全链路本地预算、目标语义、配对实验、能力/状态/计划强对照与保留测试集都已写入入口和实验卡。

## 执行与获取边界

**0次模型调用、0 GPUh、没有原生LIGHT运行、没有自有科学发现。** 当前容器为Python3.13.5且没有nvidia-smi；本轮没有访问用户GPU节点。普通网络下载不可用；官方quest归档的浏览器读取/容器下载尝试失败，尚无归档字节、数据hash、许可全文或实际样本列表。公开源码是通过GitHub connector查到，不等于已clone或安装。

Bayesian Partner Modelling摘要可核；多次HTML/PDF获取失败，仍作为保守强近邻，不冒称完成本轮精读。部分NeurIPS工作具体track仍待正式页确认；不能将官方标题表所有命中当main接受。以上已落入明确的状态字段，不将获取失败隐藏成完成。

## 本轮产物及后续

更新README/EXPLORATION_ENTRY/BASELINES/LOCAL_FIRST/知识库入口/定位表；新增定向目标控制综述、前沿核查、E03/E04运行前卡、LOCAL_AGENT_START与机器可读entry_manifest。manifest里的局数和token是**设计上界**，不是结果。旧源码实验和阅读资产原样保留。

下一动作已经具体：恢复指定数据与引擎、确认可观察且语义明确的原生任务、跑强本地B0，再从真实观察选E04的区分干预。不是继续无界找题，也不是先训练一个复杂NPC。

没有运行全仓库tools/process/check.py；本次提交需核对改动只在本workbench、文件完整、实验卡状态/字段和manifest一致。其他工作台状态/正文/实验不可碰。
