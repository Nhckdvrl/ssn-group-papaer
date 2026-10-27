"""E153 independently held MMLU RC inputs from existing Arrow cache; no downloads."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pyarrow as pa
import pyarrow.ipc as ipc
from transformers import AutoTokenizer
import e150_native as n

RESULT=n.WB/"results/e153"
RAW=Path.home()/"mechpop_cache/e153_mmlu_source_transfer"
SUBJECTS=("high_school_biology","high_school_mathematics")
CACHE=Path.home()/".cache/huggingface/datasets/cais___mmlu"


def question_sha(row):
    return hashlib.sha256(json.dumps({"question":row["question"],"choices":row["choices"]},sort_keys=True,ensure_ascii=False).encode()).hexdigest()


def query(row):
    return "Question: "+row["question"]+"\nAnswer:"


def context(subject,demos,row):
    header=f"The following are multiple choice questions (with answers) about {subject.replace('_',' ')}.\n\n"
    return header+"\n\n".join(query(ex)+" "+ex["choices"][int(ex["answer"])] for ex in demos)+"\n\n"+query(row)


def load_arrow(path):
    with pa.memory_map(str(path),"r") as stream:return ipc.open_stream(stream).read_all().to_pylist()


def flatten(sequences):
    lengths=np.array([len(s) for s in sequences],np.int64)
    return np.concatenate(sequences).astype(np.uint32),np.concatenate(([0],np.cumsum(lengths)))


def prepare():
    metadata=n.assets();roots=[Path(v["path"]) for v in metadata["models"].values()]
    if n.sha(roots[0]/"tokenizer.json")!=n.sha(roots[1]/"tokenizer.json"):raise ValueError("Pair tokenizer mismatch")
    tokenizer=AutoTokenizer.from_pretrained(roots[0],local_files_only=True,trust_remote_code=False)
    cal,test,candidates,texts,files=[],[],[],[],{}
    excluded={}
    for subject_index,subject in enumerate(SUBJECTS):
        infos=sorted((CACHE/subject).glob("*/*/dataset_info.json"))
        if len(infos)!=1:raise ValueError("Exactly one pinned cached dataset version required")
        root=infos[0].parent
        data={}
        for split in ("dev","validation","test"):
            path=root/f"mmlu-{split}.arrow"
            files[str(path)]={"sha256":n.sha(path),"size_bytes":path.stat().st_size}
            data[split]=load_arrow(path)
        if len(data["dev"])!=5:raise ValueError("Exactly five original demonstrations required")
        forbidden={question_sha(row) for split in ("dev","validation") for row in data[split]}
        pool=[i for i,row in enumerate(data["test"]) if question_sha(row) not in forbidden]
        excluded[subject]=len(data["test"])-len(pool)
        if len(pool)<64:raise ValueError("Insufficient disjoint test questions")
        selected=sorted(np.random.default_rng(153001+subject_index).choice(pool,64,replace=False).tolist())
        for index,row in enumerate(data["validation"]):
            text=context(subject,data["dev"],row)+" "+row["choices"][int(row["answer"])]
            ids=np.array(tokenizer.encode(text,add_special_tokens=False),np.uint32)
            cal.append({"subject_index":subject_index,"row":index,"question_sha256":question_sha(row),"ids":ids,
                        "text_sha256":hashlib.sha256(text.encode()).hexdigest()})
            texts.append(json.dumps({"split":"cal","subject":subject,"row":index,"text":text},ensure_ascii=False))
        for index in selected:
            row=data["test"][index];prompt=context(subject,data["dev"],row)
            prompt_ids=tokenizer.encode(prompt,add_special_tokens=False)
            sequence_indices=[];lengths=[];chars=[]
            for choice in row["choices"]:
                continuation=" "+choice
                ids=tokenizer.encode(prompt+continuation,add_special_tokens=False)
                if ids[:len(prompt_ids)]!=prompt_ids or len(ids)<=len(prompt_ids):raise ValueError("RC context boundary is not a token prefix")
                sequence_indices.append(len(candidates));lengths.append(len(ids)-len(prompt_ids));chars.append(len(continuation))
                candidates.append(np.array(ids,np.uint32))
            test.append({"subject_index":subject_index,"source_row":index,"question_sha256":question_sha(row),"gold":int(row["answer"]),
                         "prompt_tokens":len(prompt_ids),"sequence_indices":sequence_indices,"answer_tokens":lengths,"answer_chars":chars})
            texts.append(json.dumps({"split":"test","subject":subject,"row":index,"prompt":prompt,"choices":row["choices"],"gold":int(row["answer"])},ensure_ascii=False))
    all_sequences=[v["ids"] for v in cal]+candidates
    if max(map(len,all_sequences))>4096:raise ValueError("Untruncated 5-shot inputs exceed 4096; protocol revision required before model reads")
    if any(s.max()>=100352 for s in all_sequences):raise ValueError("IDs outside native vocabulary")
    cal_flat,cal_offsets=flatten([row["ids"] for row in cal]);test_flat,test_offsets=flatten(candidates)
    arrays={"cal_ids":cal_flat,"cal_offsets":cal_offsets,"cal_subject":np.array([r["subject_index"] for r in cal]),
            "test_ids":test_flat,"test_offsets":test_offsets,"gold":np.array([r["gold"] for r in test]),
            "subject":np.array([r["subject_index"] for r in test]),"prompt_tokens":np.array([r["prompt_tokens"] for r in test]),
            "answer_tokens":np.array([r["answer_tokens"] for r in test]),"answer_chars":np.array([r["answer_chars"] for r in test])}
    RAW.mkdir(exist_ok=True,parents=True);path=RAW/"questions.npz";text_path=RAW/"questions.jsonl"
    if path.exists():
        with np.load(path) as previous:assert set(previous.files)==set(arrays) and all(np.array_equal(previous[k],v) for k,v in arrays.items())
    else:np.savez_compressed(path,**arrays)
    payload="\n".join(texts)+"\n"
    if text_path.exists() and text_path.read_text()!=payload:raise ValueError("Refusing to replace frozen MMLU text")
    if not text_path.exists():text_path.write_text(payload)
    record={"experiment":"E153","status":"data_prepared","data_source_sha256":n.sha(__file__),"subjects":list(SUBJECTS),"test_questions_each":64,
            "test_questions":test,"cal_questions":[{k:v for k,v in row.items() if k!="ids"} for row in cal],
            "cached_arrow_files":files,"data":{"path":str(path),"sha256":n.sha(path),"size_bytes":path.stat().st_size},
            "texts":{"path":str(text_path),"sha256":n.sha(text_path)},"exact_duplicate_test_rows_excluded":excluded,"pad_token_id":tokenizer.pad_token_id,
            "tokenizer_sha256":n.sha(roots[0]/"tokenizer.json"),"input_max_tokens":max(map(len,all_sequences)),
            "input_mean_candidate_tokens":float(np.mean([len(v) for v in candidates])),"test_candidate_tokens":int(sum(map(len,candidates))),
            "cal_tokens":int(sum(len(v["ids"]) for v in cal)),"prompt_rule":"OLMES RC cloze + fixed dev5, spaces before answer text; no chat/BOS or truncation",
            "scope":"Original official dev/validation/test, not paper resplit/full-table reproduction or evidence of uncontaminated pretraining."}
    n.old.immutable_json(RESULT/"data_plan.json",record)
    return {k:record[k] for k in ("status","input_max_tokens","input_mean_candidate_tokens","test_candidate_tokens","cal_tokens","exact_duplicate_test_rows_excluded")}


if __name__=="__main__":print(json.dumps(prepare(),indent=2))
