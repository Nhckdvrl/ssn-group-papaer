#!/usr/bin/env bash
# Process-local policy for curl/wget/pip/HF asset commands. No VPN fallback.
set -euo pipefail
if [[ $# -eq 0 ]]; then
    echo 'Usage: bash direct_download.sh COMMAND [ARGUMENT ...]' >&2
    exit 2
fi
exec env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
    -u http_proxy -u https_proxy -u all_proxy \
    NO_PROXY='*' no_proxy='*' \
    HF_ENDPOINT="${PRAG_DOWNLOAD_ENDPOINT:-https://hf-mirror.com}" \
    HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1 "$@"
