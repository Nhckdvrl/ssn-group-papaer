from huggingface_hub import snapshot_download
p=snapshot_download("princeton-nlp/Llama-3-8B-ProLong-512k-Base",
                    allow_patterns=["*.json","*.safetensors","tokenizer*"], max_workers=8)
print("MODEL_OK", p)
