#!/bin/bash
# stage model weights to node-local /tmp/ices_models (run on the node)
set -e
mkdir -p /tmp/ices_models
H=/home/xiang/.cache/huggingface/hub
cp_snap(){ src=$H/$1/snapshots/$2; dst=/tmp/ices_models/$3; if [ ! -f $dst/.done ]; then mkdir -p $dst; cp -rL $src/. $dst/ && touch $dst/.done; fi; echo "$3 ok"; }
cp_snap models--Qwen--Qwen3-8B b968826d9c46dd6066d109eabc6255188de91218 Qwen3-8B
cp_snap models--mistralai--Mistral-7B-v0.3 caa1feb0e54d415e2df31207e5f4e273e33509b1 Mistral-7B-v0.3
cp_snap models--google--gemma-2-9b 33c193028431c2fde6c6e51f29e6f17b60cbfac6 gemma-2-9b
cp_snap models--google--gemma-2-2b c5ebcd40d208330abc697524c919956e692655cf gemma-2-2b
cp_snap models--Qwen--Qwen3-14B 40c069824f4251a91eefaf281ebe4c544efd3e18 Qwen3-14B
if [ "$1" = "llama" ] && [ ! -f /tmp/ices_models/Llama-3.1-8B/.done ]; then
  export HF_HUB_DISABLE_XET=1
  /home/xiang/.venvs/ices-tf457/bin/hf download NousResearch/Meta-Llama-3.1-8B --revision 1f47e50cdbe801ad8a5174156ec3a0655108fb9f --local-dir /tmp/ices_models/Llama-3.1-8B --exclude "original/*" && touch /tmp/ices_models/Llama-3.1-8B/.done
  echo llama ok
fi
