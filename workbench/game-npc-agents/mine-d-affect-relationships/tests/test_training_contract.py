import importlib.util
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))


@unittest.skipUnless(importlib.util.find_spec('torch') and importlib.util.find_spec('transformers'), 'Requires training environment')
class TrainingContractTests(unittest.TestCase):
    def test_update_visits_every_training_row_twice_and_never_validation(self):
        from train_adaptation_sft import training_order
        entries=[dict(partition='train',task='character_state_update',length=3) for _ in range(5)]
        entries += [dict(partition='validation',task='character_state_update',length=3)]
        ids=training_order(entries,'update',42,30)
        self.assertEqual(sorted(ids),sorted(list(range(5))*2))

    def test_multitask_is_balanced_and_only_exceeds_budget_by_last_full_example(self):
        from train_adaptation_sft import training_order
        entries=[dict(partition='train',task=task,length=i+3) for task in ['u','m','a'] for i in range(4)]
        ids=training_order(entries,'multitask',42,70)
        self.assertEqual(ids,training_order(entries,'multitask',42,70))
        self.assertGreaterEqual(sum(entries[i]['length'] for i in ids),70)
        self.assertLess(sum(entries[i]['length'] for i in ids[:-1]),70)
        for start in range(0,len(ids)-2,3):
            self.assertEqual({entries[i]['task'] for i in ids[start:start+3]},{'u','m','a'})

    def test_selected_logits_match_masked_causal_loss_and_gradients(self):
        import torch
        from transformers import Qwen3Config,Qwen3ForCausalLM
        from train_adaptation_sft import selected_ce
        torch.set_num_threads(1);torch.manual_seed(7)
        model=Qwen3ForCausalLM(Qwen3Config(vocab_size=97,hidden_size=32,intermediate_size=64,
            num_hidden_layers=2,num_attention_heads=2,num_key_value_heads=1,head_dim=16,
            max_position_embeddings=128,attention_dropout=0.0))
        x=torch.tensor([[1,8,9,10,13,17,19,21]])
        labels=x.clone();labels[:,:5]=-100
        full=model(input_ids=x,labels=labels,use_cache=False).loss
        full.backward();expected={n:p.grad.clone() for n,p in model.named_parameters() if p.grad is not None}
        model.zero_grad(set_to_none=True)
        slim=selected_ce(model,x,5);slim.backward()
        torch.testing.assert_close(full,slim,rtol=1e-6,atol=1e-6)
        for n,p in model.named_parameters():
            if n in expected:torch.testing.assert_close(p.grad,expected[n],rtol=2e-5,atol=1e-6)


if __name__=='__main__':unittest.main()
