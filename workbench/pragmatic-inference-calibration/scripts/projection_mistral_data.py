"""E39: same frozen source, official Mistral BOS and full common tokenizer."""
import hashlib,json
from projection_data import prepare,render,parse_rating

def common_model(root,model):
    assert model in ['Mistral-7B-v0.3','Mistral-7B-Instruct-v0.3']
    return root/'models/Mistral-7B-Instruct-v0.3'

def inputs(tok,rows,interface):
    texts=[(tok.bos_token if interface=='bare' else '')+render(tok,r,interface) for r in rows]
    ids=[tok.encode(t,add_special_tokens=False) for t in texts]
    assert all(z[0]==tok.bos_token_id and z[1]!=tok.bos_token_id for z in ids)
    assert all(r['system_text'] in t and r['user_text'] in t for r,t in zip(rows,texts))
    return texts,ids,hashlib.sha256(json.dumps(ids).encode()).hexdigest()
