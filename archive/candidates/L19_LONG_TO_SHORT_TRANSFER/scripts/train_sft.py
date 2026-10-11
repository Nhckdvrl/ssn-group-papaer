import argparse, json, os, sys, math, random, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import torch
from torch.utils.data import Dataset
from transformers import (AutoTokenizer, AutoModelForCausalLM, Trainer,
                          TrainingArguments, set_seed)
from sft_data import build_run
from sparse_loss import sparse_causal_loss

MODEL = os.environ.get("L19_MODEL", "/tmp/l19/prolong-512k-base-bf16")


class Items(Dataset):
    def __init__(self, items): self.items = items
    def __len__(self): return len(self.items)
    def __getitem__(self, i): return self.items[i]


def collate(batch, pad_id):
    n = max(len(b["input_ids"]) for b in batch)
    ids = torch.full((len(batch), n), pad_id, dtype=torch.long)
    lab = torch.full((len(batch), n), -100, dtype=torch.long)
    att = torch.zeros((len(batch), n), dtype=torch.long)
    for i, b in enumerate(batch):
        L = len(b["input_ids"])
        ids[i, :L] = torch.tensor(b["input_ids"]); lab[i, :L] = torch.tensor(b["labels"])
        att[i, :L] = 1
    return dict(input_ids=ids, labels=lab, attention_mask=att)


class SparseTrainer(Trainer):
    """Trainer with completion-only sparse loss.

    `model_accepts_loss_kwargs` is forced off. transformers >=5 skips its
    `loss / gradient_accumulation_steps` division whenever the model advertises
    `accepts_loss_kwargs` (LlamaForCausalLM does), because it assumes `compute_loss`
    normalised by `num_items_in_batch`. Ours normalises per example on purpose -- NQ
    answers are ~3 tokens and UltraChat turns ~400, and token-level normalisation would
    shrink the NQ block to under 1% of the gradient, which is the block the experiment
    manipulates. Leaving the flag on made every accumulated step 8x too large.
    """

    def compute_loss(self, model, inputs, return_outputs=False, **kw):
        m = model.module if hasattr(model, "module") else model
        loss = sparse_causal_loss(m, inputs["input_ids"], inputs["labels"],
                                  inputs["attention_mask"])
        return (loss, None) if return_outputs else loss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True,
                    choices=["SHORT-SUPPORT", "LONG-FULL", "PC-UC-UC", "PC-UC-CHATQA2"])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n_nq", type=int, default=10000)
    ap.add_argument("--n_uc", type=int, default=10000)
    ap.add_argument("--max_len", type=int, default=32768)
    ap.add_argument("--global_examples_per_step", type=int, default=32)
    ap.add_argument("--lr", type=float, default=5e-6)
    a = ap.parse_args()

    set_seed(a.seed)
    tokz = AutoTokenizer.from_pretrained(MODEL)
    jl = lambda p: [json.loads(l) for l in open(p)]
    uc_all = jl("data/ultrachat.jsonl")
    block_a = uc_all[:a.n_uc]                       # identical in every condition
    if a.condition in ("SHORT-SUPPORT", "LONG-FULL"):
        block_b = jl("data/nq_pairs.jsonl")[:a.n_nq]
    elif a.condition == "PC-UC-UC":
        block_b = uc_all[a.n_uc:a.n_uc + a.n_nq]
    else:
        block_b = jl("data/chatqa2.jsonl")[:a.n_nq]
    items = build_run(tokz, block_a, block_b, a.condition, a.seed, a.max_len)
    if int(os.environ.get("RANK", 0)) == 0:
        tl = sum(len(x["input_ids"]) for x in items)
        ll = sum(sum(1 for y in x["labels"] if y != -100) for x in items)
        print(f"[{a.condition} seed{a.seed}] {len(items)} items  "
              f"{tl/1e6:.1f}M context tokens  {ll/1e6:.3f}M loss tokens", flush=True)

    world = int(os.environ.get("WORLD_SIZE", 1))
    accum = max(1, a.global_examples_per_step // world)
    steps = max(1, len(items) // (world * accum))
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.bfloat16, attn_implementation="sdpa")
    model.config.use_cache = False

    args = TrainingArguments(
        output_dir=a.out, num_train_epochs=1, per_device_train_batch_size=1,
        gradient_accumulation_steps=accum, learning_rate=a.lr,
        lr_scheduler_type="cosine", warmup_steps=max(1, int(0.03 * steps)), adam_beta1=0.9, adam_beta2=0.95,
        weight_decay=0.0, bf16=True, gradient_checkpointing=True, logging_steps=5,
        save_strategy="no", report_to=[], disable_tqdm=True, seed=a.seed, dataloader_num_workers=2,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        deepspeed="configs/zero2.json",    )
    tr = SparseTrainer(model=model, args=args, train_dataset=Items(items),
                       processing_class=tokz,
                       data_collator=lambda b: collate(b, tokz.eos_token_id))
    tr.model_accepts_loss_kwargs = False      # see SparseTrainer docstring
    t0 = time.time()
    tr.train()
    tr.save_model(a.out)
    if int(os.environ.get("RANK", 0)) == 0:
        tokz.save_pretrained(a.out)          # eval loads the checkpoint standalone
    if int(os.environ.get("RANK", 0)) == 0:
        json.dump(dict(condition=a.condition, seed=a.seed, n_items=len(items),
                       minutes=(time.time()-t0)/60), open(f"{a.out}/run.json", "w"))


if __name__ == "__main__":
    main()
