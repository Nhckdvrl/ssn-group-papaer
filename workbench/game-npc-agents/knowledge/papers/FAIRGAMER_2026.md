# FAIRGAMER — ACL 2026 Main

- 主源<https://aclanthology.org/2026.acl-long.2015/>，代码<https://github.com/BingkangShi/FairGamer> pin e4bace3a637d054296aece787b13323b2f27bfda；PDF SHA24586a527e003c07344e770ecc6a54f59228184c48cef8bedbcc5cb898038f7a。
- 读§3模式/指标、§4主表和temperature/prompt/语言消融，附录prompt/table入口；源码看llm_response.py、Competition/Competition.py的query/选项交换与输出统计。
- **事实：** 三模式transaction/cooperation/competition×4属性共12tasks，7LLM。重复采样的scalar/3-option分布以FairMCV比较角色人口标签（≥95%为作者公平阈值）。交易discount[-100,0]，合作点数分配，竞争cooperate/raid/neutral；作者理想是忽略人口标签一致，不要求NE唯一选择。样本大不等于真实玩家。
- **源码范围：** LLM响应SDK按给定URL，query注入两role属性/打乱选项、统计JSON输出。本轮未执行SDK，0云；已读路径没有游戏状态执行，不能从这些路径自动称恢复了完整NPC动作闭环。正文的三决策模式属于该文，不能在A里改名为新模式。
- **解释/未排除：** biased角色选择与数字分配是强近邻；作者公平理想不等于每个RPG作者规范（剧情角色有偏见可被游戏允许）。换真实生物/玩家属性必须结合author目标、合法信息、world后果，而不是重新给Greedy/忠诚贴唯一gold。源码全目录/所有输出解析/数据生成仍未逐行核验。
