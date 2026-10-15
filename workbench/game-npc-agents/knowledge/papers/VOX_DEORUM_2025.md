# Vox Deorum（2025/2026预印本，正文与提示附录）

主源：[论文](https://arxiv.org/html/2512.18564)、[当前作者仓库](https://github.com/vox-deorum/vox-deorum)。核读§3–6和附录A系统/用户提示，查看仓库README；未代码复现。PDF使用FDG26模板，正式接收未独立核实；当前仓库已超出原论文版本。

**DOCUMENTED：** CivilizationV＋VoxPopuli5.0-alpha3；LLM选择宏观战略、外交persona、政策/科技，原VPAI完成战术搜索。2327完整游戏为919 VPAI/983 GPT-OSS120B/425 GLM4.6；四文明小图，三个对手均VPAI。生存/胜率/原生score与战略/政策轨迹分开；不可恢复崩溃与15+回合API缺失游戏排除，延迟由token/外部硬件基准推导而非全实测。

**idea来源与尺度：** DOCUMENTED为商业4X需要长程策略、低延迟和可靠战术的矛盾，采用宏观LLM＋已有执行器；现成分层组件支撑的是整套真实长局表现。两模型在共同战术层上有不同策略风格；这里的persona还是可被策略器修改的外交参数，不是已做本项目式人格文本×私有目标实验。

**对本项目：** “可靠能力和不同风格能共存”不能被写成过去无人实现的神话；已有架构是强参照，可继承其分工来检验NPC角色控制。我们要解释人物对目标取舍与行动推进的联合作用，而不是重新命名分层。当前README有真人外交/承诺交互和CivBench回放，值得作为后续外部任务来源核查；本轮未安装商业游戏、未运行云API或扩开复现线。

PDF资产`cache/papers/vox_deorum_2025.pdf`，SHA256 `0cefb7b1729f49521c89e47afdbbc7d41bd07033458c1d47e230ad6eacceb3c7`。
