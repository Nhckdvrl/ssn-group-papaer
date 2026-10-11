import sys, os
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import hf_hub_download
n0,n1=int(sys.argv[1]),int(sys.argv[2])
def go(i):
    return hf_hub_download("google-research-datasets/natural_questions",
                           f"default/train-{i:05d}-of-00287.parquet",repo_type="dataset")
with ThreadPoolExecutor(8) as ex:
    for i,p in enumerate(ex.map(go,range(n0,n1))): print(i,flush=True)
print("DONE")
