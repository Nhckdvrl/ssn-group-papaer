"""A11 independent full matrix/error reconstruction and clustered contrasts."""
import shutil
import numpy as np
from experience_transfer_control_audit import ROOT,WB,read,save,sha


def main():
    bank=ROOT/'20261004-E20-legal-effect-bank44';script=WB/'scripts/predictive_object_branch_matrix_v3.py'
    branches=np.asarray([0]+list(range(2,12)));groups=[];metrics={};counts=[]
    for seed in range(3):
        for geometry in ['PRED','VALUE']:
            run=ROOT/f'20261005-E13-branch-matrix-v3-{geometry}-s{seed}-RTX'
            assert read(run/'complete.json')==dict(completed=True,geometry=geometry,seed=seed,arms=3,queries_per_arm=484)
            assert not (run/'failure.json').exists();cfg=read(run/'config.json')
            assert cfg['script_sha256']==sha(script)==sha(run/'used.py')
            assert cfg['branches']==branches.tolist() and cfg['bank_ledger_sha256']==sha(bank/'ledger.json') and cfg['bank_rows_sha256']==sha(bank/'rows.json')
            for key,value in cfg['array_sha256'].items():assert sha(run/f'{key}.npy')==value
            z=np.load(run/'features.npy');physical=np.load(run/'physical_endpoints.npy');actions=np.load(run/'actions.npy')
            assert z.shape==(44,11,6,192) and physical.shape==(44,11,2) and actions.shape==(44,11,25,2)
            for j in range(44):
                for index,branch in enumerate(branches):
                    with np.load(bank/f'tworoom_{j:03d}_b{branch:02d}.npz') as trace:
                        assert np.array_equal(trace['diagnostic_states'][-1,:2],physical[j,index])
                        assert np.array_equal(trace['issued_actions'],actions[j,index])
            models=[]
            for summary in read(run/'summary.json'):
                arm=summary['arm'];source=ROOT/summary['source']['training_run']
                assert sha(summary['source']['checkpoint'])==summary['source']['checkpoint_sha256']==read(source/'summary.json')['checkpoint_sha256']
                assert sha(source/'config.json')==summary['source']['training_config_sha256']
                for key,filename in [('prediction_sha256',f'{arm}_predictions.npy'),('rows_sha256',f'{arm}_rows.json'),('errors_sha256',f'{arm}_errors.npz')]:assert summary[key]==sha(run/filename)
                controls=read(run/f'{arm}_controls.json');assert [v['device'] for v in controls]==['cpu','cuda']
                # The frozen producer checks vectorwise atol+rtol, not a pure
                # absolute max bound (which would silently change the contract).
                assert all(v['manual_exact'] and v['weights_unchanged'] and np.isfinite(v['batch_subset_error']) for v in controls)
                pred=np.load(run/f'{arm}_predictions.npy');rows=read(run/f'{arm}_rows.json');assert pred.shape==(44,11,5,192) and len(rows)==44
                values={key:[] for key in ['success','regret','leave_out_success','leave_out_regret','leave_out_oracle_success','leave_out_oracle_regret']}
                for j,row in enumerate(rows):
                    cost=np.sum((pred[j,:,4][None]-z[j,:,5][:,None])**2,axis=-1)
                    actual=np.linalg.norm(physical[j][:,None]-physical[j][None],axis=-1)
                    selected=cost.argmin(1);masked=cost.copy();np.fill_diagonal(masked,np.inf);chosen=masked.argmin(1)
                    true_cost=np.sum((z[j,:,5][:,None]-z[j,:,5][None])**2,axis=-1);np.fill_diagonal(true_cost,np.inf);oracle=true_cost.argmin(1)
                    masked_distance=actual.copy();np.fill_diagonal(masked_distance,np.inf);best=masked_distance.min(1);q=np.arange(11)
                    assert row['anchor']==j and np.array_equal(row['predicted_costs'],cost) and np.array_equal(row['actual_endpoint_distances'],actual)
                    assert row['selected_branch']==branches[selected].tolist() and row['leave_goal_out_selected_branch']==branches[chosen].tolist()
                    assert row['leave_goal_out_true_latent_oracle_branch']==branches[oracle].tolist()
                    computed=dict(success=actual[q,selected]<16,regret=actual[q,selected],leave_out_success=actual[q,chosen]<16,leave_out_regret=actual[q,chosen]-best,
                        leave_out_oracle_success=actual[q,oracle]<16,leave_out_oracle_regret=actual[q,oracle]-best)
                    rowfields=dict(success='native_success',regret='trajectory_endpoint_regret',leave_out_success='leave_goal_out_native_success',leave_out_regret='leave_goal_out_trajectory_endpoint_regret',leave_out_oracle_success='leave_goal_out_true_latent_oracle_native_success',leave_out_oracle_regret='leave_goal_out_true_latent_oracle_regret')
                    for key,value in computed.items():
                        assert np.array_equal(row[rowfields[key]],value);values[key].append(value.mean())
                err=np.load(run/f'{arm}_errors.npz');mse=np.mean((pred-z[:,:,1:])**2,axis=-1)
                pc=pred-pred.mean(1,keepdims=True);tc=z[:,:,1:]-z[:,:,1:].mean(1,keepdims=True)
                numerator=np.mean((pc-tc)**2,axis=(1,3));denominator=np.mean(tc**2,axis=(1,3))
                assert np.array_equal(err['prefix_mse'],mse) and np.array_equal(err['effect_error'],numerator) and np.array_equal(err['true_effect_variation'],denominator)
                assert summary['native_successes']==int(sum(values['success'])*11+1e-6) and summary['leave_goal_out_successes']==int(sum(values['leave_out_success'])*11+1e-6)
                # Bank branch 0 is ZERO; factual replay is branch 2. Correct
                # the producer's descriptive label without altering predictions.
                factual_index=int(np.flatnonzero(branches==2)[0])
                other_indices=np.flatnonzero(branches!=2)
                record=dict(seed=seed,geometry=geometry,arm=arm,queries=484,states=44,native_successes=summary['native_successes'],leave_goal_out_successes=summary['leave_goal_out_successes'],mean_trajectory_endpoint_regret=float(np.mean(values['regret'])),mean_leave_goal_out_regret=float(np.mean(values['leave_out_regret'])),zero_prefix_mse=mse[:,0].mean(0).tolist(),factual_prefix_mse=mse[:,factual_index].mean(0).tolist(),counterfactual_prefix_mse=mse[:,other_indices].mean((0,1)).tolist(),factual_branch_id=2,zero_branch_id=0,producer_annotation_correction='Producer summary incorrectly labels branch0 ZERO as factual; this reader uses actual branch2 FACTUAL. Predictions, choices and all rows unchanged.',zero_effect_variation_states_per_prefix=(denominator<=1e-12).sum(0).tolist(),effect_error_sum_over_variation_sum=(numerator.sum(0)/np.maximum(denominator.sum(0),1e-12)).tolist())
                counts.append(record)
                for key,value in values.items():metrics[geometry,arm,seed,key]=np.asarray(value)
                models.append(dict(arm=arm,source=summary['source'],rows_sha256=summary['rows_sha256']))
                print('Full branch independent audit',geometry,seed,arm,'PASS',flush=True)
            assert len(models)==3;groups.append(dict(config=cfg,artifact_directory=str(run),models=models))
    rng=np.random.default_rng(116100);si=rng.integers(0,3,(10000,3));ix=rng.integers(0,44,(10000,44));effects=[]
    for geometry in ['PRED','VALUE']:
        for arm,ref in [('DIRECT','LOCAL'),('DIRECT','OPEN'),('OPEN','LOCAL')]:
            for metric in ['success','regret','leave_out_success','leave_out_regret','leave_out_oracle_success','leave_out_oracle_regret']:
                delta=np.stack([metrics[geometry,arm,s,metric]-metrics[geometry,ref,s,metric] for s in range(3)])
                for stratum,ids in [('all',np.arange(44)),('old_source32',np.arange(32)),('old_query12',np.arange(32,44))]:
                    drawix=ix if stratum=='all' else rng.choice(ids,(10000,len(ids)),replace=True)
                    draws=delta[si[:,:,None],drawix[:,None,:]].mean((1,2))
                    effects.append(dict(geometry=geometry,arm=arm,reference=ref,metric=metric,stratum=stratum,mean_delta=float(delta[:,ids].mean()),source_deltas=delta[:,ids].mean(1).tolist(),paired_source_state_bootstrap_95=np.quantile(draws,[.025,.975]).tolist(),shared_states=44,train_sources=3))
    result=dict(completed=True,models=18,queries_per_model=484,total_queries=8712,counts=counts,effects=effects,groups=groups,script_sha256=sha(__file__),scope='Same44 factual-source states and11 executed unique branches; all18 fixed models, all484goals per model. Queries cluster within44states, repeated across3sources. Pure FP32 offline encoder disables cuDNN TF32; earlier closed-loop native numerics differ. Goal-generating branch included and leave-goal-out both retained, true-latent oracle is evaluation-only. Regret is25step trajectory endpoint regret, not first-action regret or closed-loop utility. Old32/12 strata do not mean these fact-only heads trained on intervention futures. No novel method/Markov causality/independent task/speedup claim.')
    out=ROOT/'20261005-E13-branch-matrix-v3-audit';assert not out.exists();out.mkdir();shutil.copy2(__file__,out/'used.py');save(out/'result.json',result)
    result['full_audit_artifact']=str(out/'result.json');save(WB/'results/E13_20261005_full_branch_matrix_results.json',result)


if __name__=='__main__':main()
