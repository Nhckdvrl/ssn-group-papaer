# 资产下载与代理流量

2026-10-03，推进 P05。只改变本 workbench 的下载进程，不改用户 shell 配置、Codex 或正在运行的 OpenCode。

## 实测

- 当前 shell 三个大写代理变量指向本地 HTTP 代理；凭据不写入记录。这解释了此前下载默认经过代理，未取得供应商计费记录，不能量化实际扣费。
- 移除代理、`requests.Session.trust_env=False` 后，HF 主站两个 HEAD 请求连接失败；hf-mirror 的固定 revision API 可直连。
- 该镜像 API 返回模型 revision 与固定官方 SHA 一致；11 个已完成 shard 的原官方下载 metadata 中 commit/LFS SHA 与镜像一致，大小逐项一致。
- 缺失 shard 的 CDN HEAD 返回 200，直连 16 KiB Range 返回 206 且 Content-Range 精确匹配；跳转服务器为 `cas-bridge.xethub.hf.co`。不在日志保存签名 URL。
- 待续传文件完整大小 3,701,743,344 bytes，已有 2,011,888,887 bytes，只差 1,689,854,457 bytes。断点与其它权重保留。

## 默认执行规则

两个 Python 模型下载入口共同调用 [download_network.py](scripts/download_network.py)：移除大小写代理变量，禁用 requests 的环境代理和 `.netrc`，禁止隐式 token/Xet 传输；默认只经 HTTPS 镜像直连，重试仍为直连，失败直接报错，不回落代理。允许 `PRAG_DOWNLOAD_ENDPOINT=https://huggingface.co` 切到官方直连。当前脚本用于公开模型；需要认证的仓库另行按官方路线处理，不把用户 token 转发给镜像。

其它资产下载也通过进程级 wrapper，支持原有下载工具：

```bash
bash workbench/pragmatic-inference-calibration/scripts/direct_download.sh curl -I --connect-timeout 6 https://hf-mirror.com
```

镜像改变传输入口，不改变研究用 checkpoint/revision。E51 专用续传脚本先核对已完成文件的原官方 metadata/大小，缺失 shard 下载后计算完整 SHA-256，全部通过才发布完成 marker。已缓存 11 个 shard 没有本轮重新全文件 hash，此限制写入 audit。

这规避了当前环境变量指定的本地代理。若网络上游另有透明代理/TUN，仍须在该层配置分流；本机可见接口没有 TUN，未核对上游计费。推理始终使用本地完整资产，继续复用缓存，不为占卡重复下载。

传输记录、mirror metadata、完成 audit 均在 `/data1/xiangding/work/pragmatic-inference-calibration`，大文件不进 git。
