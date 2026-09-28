#!/bin/bash
# Recreates vendor/ (third-party code + pure-python deps on PYTHONPATH; nothing is installed into envs).
set -e
cd "$(dirname "$0")/../vendor"
[ -d Matrix-Game ]   || git clone https://github.com/SkyworkAI/Matrix-Game.git   && git -C Matrix-Game checkout 71c3cd7
[ -d Causal-Forcing ] || git clone https://github.com/thu-ml/Causal-Forcing.git && git -C Causal-Forcing checkout da3ddf1
[ -d Self-Forcing ]  || git clone https://github.com/guandeh17/Self-Forcing.git && git -C Self-Forcing checkout 33593df
[ -d Wan2.1 ]        || git clone https://github.com/Wan-Video/Wan2.1.git        && git -C Wan2.1 checkout 9737cba
PIP="/home/xiang/miniconda3/envs/wam-va/bin/python -m pip"
mkdir -p wheels pylib
$PIP download -q --no-deps -d wheels omegaconf==2.3.0 antlr4-python3-runtime==4.9.3
echo "7b4df175cdb08ba400f45cae3bdcae7ba8365db4d165fc65fd04b050ab63b46b  wheels/omegaconf-2.3.0-py3-none-any.whl
f224469b4168294902bb1efa80a8bf7855f24c99aef99cbefc1bcd3cce77881b  wheels/antlr4-python3-runtime-4.9.3.tar.gz" | sha256sum -c
/home/xiang/miniconda3/envs/wam-va/bin/python -m zipfile -e wheels/omegaconf-2.3.0-py3-none-any.whl pylib
tar xzf wheels/antlr4-python3-runtime-4.9.3.tar.gz -C wheels && cp -r wheels/antlr4-python3-runtime-4.9.3/src/antlr4 pylib/
# Open-Oasis deps (pure python)
$PIP download -q --no-deps -d wheels timm==1.0.24 rotary-embedding-torch==0.8.9
echo "8301ac783410c6ad72c73c49326af6d71a9e4d1558238552796e825c2464913f  wheels/timm-1.0.24-py3-none-any.whl
700e8de9dfbefba5f9117a66652a2520648dcc60136895f0068b6a85347cab02  wheels/rotary_embedding_torch-0.8.9-py3-none-any.whl" | sha256sum -c
for f in wheels/timm-1.0.24-py3-none-any.whl wheels/rotary_embedding_torch-0.8.9-py3-none-any.whl; do /home/xiang/miniconda3/envs/wam-va/bin/python -m zipfile -e $f pylib; done
[ -d open-oasis ] || git clone https://github.com/etched-ai/open-oasis.git && git -C open-oasis checkout f59deef
[ -d minWM ] || git clone https://github.com/shengshu-ai/minWM.git && git -C minWM checkout 2a54f4d
[ -d HY-WorldPlay ] || git clone https://github.com/Tencent-Hunyuan/HY-WorldPlay.git && git -C HY-WorldPlay checkout 1588e13
$PIP download -q --no-deps --only-binary=:all: --python-version 3.10 --platform manylinux2014_x86_64 -d wheels lmdb==1.6.2  # 9d3efbbded74b9d213059a5a4048fb5bb47b5b7c4c2b366e43685cb6dd9d3100
/home/xiang/miniconda3/envs/wam-va/bin/python -m zipfile -e wheels/lmdb-1.6.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl pylib
