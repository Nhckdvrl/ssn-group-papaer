# 保留环境的下载规则

本题CLOSED，不自动下载。模型/环境路径不变，旧传输日志与实验下载脚本已清理。

仍保留进程级wrapper：移除大小写HTTP_PROXY/HTTPS_PROXY/ALL_PROXY；默认HTTPS镜像直连，失败不回落VPN，不改用户全局代理或OpenCode配置。

```bash
bash workbench/pragmatic-inference-calibration/scripts/direct_download.sh curl -I --connect-timeout 6 https://hf-mirror.com
```

只用于用户另行授权的公开资产；不要向镜像转发用户token。网络透明代理/TUN可能仍影响流量，不能由wrapper保证供应商计费为零。保留的模型revision/完成标记可在models目录检查。
