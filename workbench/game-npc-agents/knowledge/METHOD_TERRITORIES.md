# 方法/训练研究的可投资空间及首个高信息量观察

说明：不是预先列四个必定工作的新损失函数。来源需回到领域最强工作；EA2026 与原生 game NPC 提供问题压力，NeurIPS/ICML/ICLR 的通用学习方法提供算法尺度，但最后仍必须在游戏里的 NPC 行动成立。

## A. Designer-feedback-efficient NPC behavior learning（主轴）
**自然需求：** 游戏创作者并不知道该怎么把“谨慎、积极协作、合理战斗风格”写成逐帧 reward。角色初版也需要随着制作人反馈快速改变。EA2026 明确提出 design-in-the-loop、有限示范、偏好/奖励何种反馈最有效的问题。
- 已有：MultiGAIL 用多专家动作示范学风格；Direct Behavior Specification 用明确约束；UBCL 用连续行为向量；PCSP 使用合成人格和相关性损失。选择信号类型不能当创新本身。
- 可辨别瓶颈：对一个真实游戏行为要求，任务 reward、independent action semantics 和人/设计师预期往往不同。先问哪个已发表方法确实控制了游戏结果而不是训练目标内循环。
- 初步测量：同一 policy/environment，固定人工编辑/示范数及 rollout 数，比较 zero-shot prompt、条件化 PPO、示范BC、偏好方法（前提是强实现/真实数据具备）。记录行为符合度、任务可靠性、跨玩家/未见场景及训练总成本，而不是一张综合得分。
- 高价值结果：发现跨方法/环境都存在的训练控制规律及精确定义何种设计监督真正提高实际行动可控性；或简洁新学习方法在强等预算对照上确实改善。**如果只有小样本合成风格标签，不够。**

## B. Rapid editable shared game NPC policies
**自然需求：** 游戏每次补丁和新的 NPC 表现要求不可能全部重训。EA2026 明确提出 fine-tune、遗忘、模块化联合训练。
- 最直接 owner：PCSP 共享条件政策、MultiGAIL 混合政策、UBCL 连续风格条件化；最新 LoRA event-triggered MARL 已有方法。
- 高信息量入口：固定训练好的多个角色，改变**一项真正可以由游戏事件核查的行为规格**，测修改速度/样本、其它角色旧行为、跨玩家 OOD、动作时延；对照单纯 reward retrain、replay、adapter、policy modular update。当前还没有运行依据宣称会失败。
- 不能直接声称首个“可编辑 NPC”或“首次个性化 LoRA”。

## C. LLM supervisor → fast executable NPC policies
**需求：** 游戏状态复杂/玩家自然语言指令，SLM 易理解语义但每帧推理慢。PUBG Ally 现已有高低速双系统，EA 建议嵌到 BT。
- 本地可行性：本地 Qwen3 8B/14B/32B 离线或低频产生有动作真值的教师轨迹，数十万环境步由单节点轻 policy训练；全部 rollout/teacher 代价记录。严禁把自身生成文本当游戏真值。
- 高信息量入口：同一 NPC 任务用 native BT、低频 LLM 调度、distilled policy、完全共享小 policy，测任务后果/行为可控/局势变化/端到端响应/跨任务迁移。低频 LLM + BT **已经是商业方案**；只有从真实失败中解释其适用边界或提出泛化训练方法才值得投稿。
- 风险：仅工程拼装 controller，没有科学创新；强 proprietary product 没有公开数据不能公平声称 beat。

## D. Player-adaptive NPC cooperation and social behavior
**需求：** 队友/居民不只是一个独立策略；真实玩家变化时仍要以合乎角色方式行动。KRAFTON Ally 产品证据、GAMMA/ICLR Hypothetical Minds 从人/伙伴推断对接强相关，不能把泛用 MARL 排名变 NPC 价值。
- 高价值：现实动作而非“相信玩家”措辞、真实玩家控制感而非 reward、未见伙伴与角色任务变化；数据在天然伙伴分工任务中获得。
- 限制：训练与人类评估可能昂贵；优先规则/公开伙伴、实际需要时少量人类确认；只模拟伙伴不宣称人类效用。

## 投资顺序及退出信号
**先 A+B 的共享工作底座，不分裂成四个独立 project。** C/D 作为观察到的高质量拓展；视频世界模型为技术遥远邻近。目前直接选“PCSP+新 InfoNCE”会被作者已有研究吞没；直接选“训练每个 NPC 的 LoRA”欠缺生产可扩展性；直接从零造游戏世界代价过大。
- 基础测试/标准测量出现有分量的失败或成功 → 阅读原文+源码最强近邻 → 明确两个可以被一次实验分开的解释 → 使用空闲卡做独立复现和确证。
- 如果 PCSP Mini-Inzoi 的行为多样性只是 reward shaping 造成，或者 BigFive probe 不敏感，就据此更新科学问题和测试底座，不能“自动发明一个更大的 benchmark”。
- 如果只能在原 PCSP 格子世界实现而没有自然 NPC 玩家意义，则主动引入第二个真实游戏/社交 action 环境；前提是它确实支持同一 construct，不要把不同任务平均成假指标。
- 任何 idea 要经过反事实判断：即使现象成立，领域会改变什么训练策略/反馈设计/评价习惯？若只是“这个设置涨一点”，停在线索。
