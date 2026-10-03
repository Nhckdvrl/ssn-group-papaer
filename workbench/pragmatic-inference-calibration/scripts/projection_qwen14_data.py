from projection_data import prepare,inputs,parse_rating

def common_model(root,model):
    assert model in ['Qwen2.5-14B','Qwen2.5-14B-Instruct']
    return root/'models/Qwen2.5-14B-Instruct'
