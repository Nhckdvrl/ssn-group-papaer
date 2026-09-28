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
