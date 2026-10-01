# 研究资源与实验组织边界

更新：2026-10-02。来源：用户明确说明；这是资源约束，不是已经完成的硬件 benchmark。

## 已确认
- 研究室：十几张 A100、8 张 RTX PRO 6000。
- 实习地点：16 张 H20。
- 网络、磁盘和节点间通信很差，不能依赖跨节点协同训练一个大模型。
- 比较优势：将卡用于独立的单卡／单节点实验，提高强基线复现、系统测量、方法迭代、多种子、消融和跨环境验证的吞吐量。

**不能推出：** 所有卡同时空闲；所有节点同构；研究室与实习资源可混用；任意数据可跨地点移动；小参数量必然低显存、低 I/O 或低端到端成本。具体显存、CPU、磁盘、软件环境、授权和排队情况由执行节点实测。

## 选题与执行原则
1. 限制单次实验的计算耦合，不限制科学问题的重要性。优先成熟开源系统，不从零训大 foundation model。
2. 以独立实验槽位组织任务，不把总卡数当成一台高速互联集群；单卡跑通后再并行 seed / stage / condition / method。
3. 不一开始铺满 Cartesian product；先测显存、I/O、wall-clock、数据读取和 evaluator。
4. 数据尽量一次下载、节点内复用；避免远程流式视频、共享盘随机读、数万个小文件和大 checkpoint 反复搬运。
5. 同一 checkpoint 的多 evaluator / planner / scene 可独立分派；联合训练不能读过期缓存。
6. 保存数据与模型 hash、完整 config、代码 commit、训练/评测 seed、硬件、wall-clock、I/O 和失败记录。
7. 实习资源遵守单位授权与数据边界；默认不把内部数据、凭证、私有 checkpoint 或机器地址写进公开仓库。

## 与流程关系
卡多不意味着同时开很多互不相关的线；`workbench/README.md` 的 ACTIVE 容量不变。一个 workbench 内可以共享资产并行多个有解释力的实验。

当前应用：
- `workbench/real-time-causalization-capability-preservation/`：ACTIVE-MAIN，优先公开 stage checkpoints + 横向 measurement；
- `workbench/latent-world-model-planning/`：PROPOSED。

两者都必须遵守弱互联 / 弱 I/O 边界。
