# AI4Quant — Selected Topics

这里只放已经正式通过当前轮审查、允许进入最小实验的题。

## 当前注册

### P1 — State Coverage ≠ Exposure Coverage
目录：`state-coverage-vs-exposure-coverage/`

暂定论文题名：**The Geometry of Data in Multivariate Foundation Models**

核心：multivariate panel 中横截面 breadth 与 temporal depth 提供不同种类的信息，不能默认由单一 token count `D = N × T` 等价描述。

### P2 — Forecast Skill ≠ Structural Skill
目录：`forecast-skill-vs-structural-skill/`

暂定论文题名：**Do Multivariate Foundation Models Actually Learn Error-Correcting Structure?**

核心：标准 forecasting loss 很好、甚至训练时见过某种 mechanism，并不意味着 foundation model 真正学会该 mechanism；用 cointegration / error-correction 构造可直接 intervention 的 structural test。

## 规则

- `selected/` 中一个题一个独立目录。
- 每题必须有独立注册文件，不依赖聊天上下文才能理解。
- 本地实验发现 blocker 后，允许降级回 `failed/`；不要因为已注册就保护题目。
- 不允许把同一母问题的 sibling/换皮题重复注册成多个 survivor。
