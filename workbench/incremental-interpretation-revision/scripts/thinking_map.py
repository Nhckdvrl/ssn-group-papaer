"""E52 greedy final-answer generation, with matched nonthinking generation control."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import time

from data import sha
from reading_map import chat


def parse_answer(text, thinking, options=None):
    if thinking:
        if '</think>' not in text: return None, 'unfinished_thinking'
        text = text.rsplit('</think>', 1)[1]
    # All non-A/B prose is a format failure, retained rather than inferred by gold.
    match = re.fullmatch(r'\s*([AB])(?:[.。])?\s*', text)
    if match:return match.group(1), 'complete'
    # A. Yes is a labelled option, not an ambiguous inferred answer. The label
    # and its literal option text must agree; A. No when A=Yes is rejected.
    match=re.fullmatch(r'\s*([AB])[.:]\s*(.+?)\s*',text,flags=re.DOTALL)
    if match and options is not None:
        label,content=match.groups()
        if content.strip().rstrip('.。').casefold()==options['AB'.index(label)].strip().rstrip('.。').casefold():
            return label,'complete_labelled_option'
        return None,'conflicting_or_nonliteral_label_text'
    return None, 'invalid_final_format'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--cap', type=int, default=2048)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com',
                      HF_HUB_DISABLE_TELEMETRY='1',VLLM_NO_USAGE_STATS='1',DO_NOT_TRACK='1')
    from transformers import AutoTokenizer
    from vllm import LLM, SamplingParams
    import torch
    import transformers
    import vllm
    args.out.mkdir(parents=True, exist_ok=True)
    assert not (args.out/'predictions.jsonl').exists()
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    assert args.model.name.startswith('Qwen3-') and not args.model.name.endswith('Base')
    rows = [json.loads(line) for line in args.data.read_text().splitlines()]
    if args.limit: rows = rows[:args.limit]
    start = time.monotonic()
    # One GPU per process; avoid CUDA graph warmup/compilation changing the harness.
    engine = LLM(model=str(args.model), tokenizer=str(args.model), dtype='bfloat16',
                 seed=52, tensor_parallel_size=1, max_model_len=4096,
                 max_num_seqs=64, gpu_memory_utilization=.80, enforce_eager=True,
                 disable_log_stats=True)
    config = dict(model_path=str(args.model), model_manifest_sha256=sha(args.model/'manifest.json'),
        data_sha256=sha(args.data), arguments={**vars(args), 'data':str(args.data), 'model':str(args.model), 'out':str(args.out), 'dtype':'bfloat16'},
        seed=52, torch=torch.__version__, transformers=transformers.__version__, vllm=vllm.__version__,
        temperature=0, max_new_tokens=args.cap, matched_nonthinking_cap=32,
        code_sha256=sha(Path(__file__)), tasks=len(rows)*4, model_load_seconds=time.monotonic()-start)
    (args.out/'thinking_map.py').write_bytes(Path(__file__).read_bytes())
    (args.out/'reading_map.py').write_bytes(Path(__file__).with_name('reading_map.py').read_bytes())
    (args.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')
    with (args.out/'predictions.jsonl').open('w') as stream:
        for thinking in (False, True):
            tasks = []
            for row in rows:
                for mapping in (0, 1):
                    options = row['options'][::1 if mapping == 0 else -1]
                    content = f'Sentence:\n{row["sentence"]}\n\nQuestion:\n{row["question"]}\nA. {options[0]}\nB. {options[1]}\nAnswer only A or B.'
                    prompt = chat(tokenizer, content, thinking=thinking)
                    # Qwen's thinking-on template leaves the assistant prefix open;
                    # the model generates <think>. Only thinking-off inserts an
                    # empty completed block. Never require a start tag in the prompt.
                    if thinking: assert '</think>' not in prompt
                    tasks.append((row, mapping, prompt))
            params = SamplingParams(temperature=0, max_tokens=args.cap if thinking else 32, seed=52)
            # Bounded groups save completed outputs even if a later group fails.
            for begin in range(0, len(tasks), 256):
                batch = tasks[begin:begin+256]
                outputs = engine.generate([t[2] for t in batch], params, use_tqdm=False)
                for (row, mapping, prompt), generated in zip(batch, outputs):
                    completion = generated.outputs[0]
                    displayed_options=row['options'][::1 if mapping==0 else -1]
                    answer, status = parse_answer(completion.text, thinking,displayed_options)
                    gold = row['gold'] if mapping == 0 else 1-row['gold']
                    record = {k:row.get(k) for k in ('item_id','pair_id','cluster_id','source','construction','condition','question_target',
                        'source_question_type','source_sent_type','needs_revision','matched_question_exact','sentence_sha256','gold')}
                    record.update(format='B', reading='R6' if thinking else 'R0-generation',
                        order='reg', prompt_index=0, mapping=mapping, repair=False, mode='generation',
                        candidate_gold=gold, prompt=prompt, prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                        prompt_tokens=len(generated.prompt_token_ids), generated_token_ids=list(completion.token_ids),
                        text=completion.text, answer=answer, answer_status=status,
                        finish_reason=completion.finish_reason, capped=completion.finish_reason=='length',
                        p_correct=None, correct=(answer==['A','B'][gold]) if answer is not None else False)
                    stream.write(json.dumps(record)+'\n')
                stream.flush(); print('thinking', thinking, begin+len(batch), '/', len(tasks), flush=True)
    config.update(predictions_sha256=sha(args.out/'predictions.jsonl'),
                  wall_seconds=time.monotonic()-start, gpu_hours=(time.monotonic()-start)/3600)
    (args.out/'config.json').write_text(json.dumps(config, indent=2)+'\n')


if __name__ == '__main__': main()
