#!/bin/bash
# Creates the dedicated GenEval scorer env (mmcv/mmdet need torch 2.5 cu121 + numpy<2, which
# conflicts with the generation env). Mirrors RevisitingCFGMethods/setup_env.py pins.
set -e
C=/home/xiang/miniconda3/bin/conda
[ -x /home/xiang/miniconda3/envs/mg-eval/bin/python ] || $C create -y -p /home/xiang/miniconda3/envs/mg-eval python=3.10 pip
P="/home/xiang/miniconda3/envs/mg-eval/bin/python -m pip"
R=/home/xiang/ssn-group-papaer/workbench/modern-guidance/vendor/RevisitingCFGMethods/requirements
$P install -r $R/torch.txt
$P install -c $R/constraints.txt -r $R/geneval.txt "transformers>=4.57,<4.60" pillow==11.3.0 "numpy<2" pandas tqdm
$P install -c $R/constraints.txt mmcv==2.2.0 -f https://download.openmmlab.com/mmcv/dist/cu121/torch2.4.0/index.html
$P install -c $R/constraints.txt mmengine==0.10.7 mmdet==3.3.0
INIT=$(/home/xiang/miniconda3/envs/mg-eval/bin/python -c "import sysconfig;print(sysconfig.get_paths()['purelib'])")/mmdet/__init__.py
sed -i 's/mmcv_version < digit_version(mmcv_maximum_version)/mmcv_version <= digit_version(mmcv_maximum_version)/' $INIT
$P uninstall -y opencv-python || true
$P install -c $R/constraints.txt --force-reinstall --no-deps "opencv-python-headless==4.10.0.84"
G=/home/xiang/ssn-group-papaer/workbench/modern-guidance/vendor/geneval
[ -d $G ] || git clone --depth 1 https://github.com/djghosh13/geneval.git $G
mkdir -p $G/models
[ -f $G/models/mask2former_swin-s-p4-w7-224_lsj_8x2_50e_coco.pth ] || wget -q -O $G/models/mask2former_swin-s-p4-w7-224_lsj_8x2_50e_coco.pth https://download.openmmlab.com/mmdetection/v2.0/mask2former/mask2former_swin-s-p4-w7-224_lsj_8x2_50e_coco/mask2former_swin-s-p4-w7-224_lsj_8x2_50e_coco_20220504_001756-743b7d99.pth
[ -d $G/mmdetection ] || git clone --depth 1 https://github.com/open-mmlab/mmdetection.git $G/mmdetection
echo EVAL_ENV_DONE
