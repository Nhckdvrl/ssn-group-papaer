# E49：第二事件角色已有明确证据时的实际使用（2026-10-06）

- **状态：** PLANNED
- **类型：** PILOT
- **对应：** C05 / I01 / P11；E48尚未推断，本卡不按E48结果挑fact/target赢家。
- **问题（一句话）：** 旧活动角色对下一活动的预测偏移，是否会干扰已有明确证据的第二活动角色使用，尤其在证据需通过共指映射时？
- **设置：** E48固定24sources、12family、两Name/Description alias；两个事件oldactor/newotheractor与同/不同V冻结。旧角色source/other × 明确新角色source/other（congruent/incongruent）× 第二事实Name/Description × E47inventory absent/present × same/differentV。旧fact固定E43普通Name，unused nearby保持mention-last。alias保留；第二活动事实必须是完整独立的新活动句，明确patient并且在整个这个活动范围内，无排他、selection-only、概率或未报告who歧义。允许事实非exclusive，但问“明确报告的对象”而非“所有实际参与者”。24×2×2×2×2×2=768contexts。
- **读数：** Native两用途：只给第二事件报告patient的canonical Name（literal retrieval＋alias）；用两个简短分句分别复述两个事件且使用canonical Names（joint role use）。两用途×base/一句scope+alias恢复，3072完整输出。所有输出逐条独立盲审，old/new角色各correct、joint、unsupported额外patient及实际时间scope；允许语义等价答案、不用首NP或字符串命中当gold。主new correct的congruent−incongruent × form、V、inventory；recap old/new/joint及R8。先family两source平均，paired10000 bootstrap seed20261005。全部源/eligible/common grammar/非possessive11报；不按E48score筛family。
- **阳性对照：** history-role两个世界使用同一第二事实；second Name条件排除必须alias转换的难度，literal second-name问与两-event recap区分检索与应用。old角色在recap中应能正确复述。若需无history对照，另卡预登记，不看到错误后自选删除context；本卡不把一致关系更难就自动称新机制。
- **噪声地板 + MIE：** 固定Qwen3-8B FP32 frozen/no-thinking/greedy、seed0、max_new_tokens96保证两句容量；两mode不筛赢家。测真实用途而不是把条件字符串likelihood当能力/世界概率。编码事实与角色用途必须外审，不由root认证gold。
- **混杂审计：** 不含selection≠execution、firstNP≠patient、alias未来重绑定、原V外同义词选择。名字性别不典型和group actor标记保留。作者逐条写24source的所有second-fact形式/两个question＋独立proposedclasses；完整rendered768×2用途再审计。旧与新角色可能一样且两个活动都可成立，不暗加unavailability；pair只有事实patient/form不同。
- **决策表（跑之前写）：** 新事实literal与mapped问、recap都正确→不支持能力/functional consequence，从概率模板问题回到自然语篇而非更多synonym扫信号；错误集中description但alias控制访问正常、且oldrole congruence有paired影响→跨事件角色应用受干扰，接自然材料检验，不先命名内部机制；literal也受影响且recap将旧患者塞入新事件→事件范围/角色检索竞争；只recap改变且问题/R8恢复→生成任务的角色使用策略，不能宣称不能理解；gold/alias不清→完整记录uncertain，修材料版本而非跑更多条件。
- **算力预算：** existing venv frozen本地Qwen3-8B，native4独立GPU分片0–3，不用peer4/5；预计≤.5GPU·h。只data author/auditor用Luna/Step，不委派科研解释。
- **命令：** 待实现；任何推断前填输入hash、审计及实际预检。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
