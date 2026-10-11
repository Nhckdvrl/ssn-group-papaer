"""Independent all-state/goal H3 Push consequences and native-success audit."""
import shutil
import numpy as np
from experience_transfer_control_audit import ROOT,WB,read,save,sha


def main():
    out=ROOT/'20261005-E13-pusht-full-branch-matrix';bank=ROOT/'20261004-E20-legal-effect-bank44';script=WB/'scripts/pusht_full_branch_matrix.py'
    assert read(out/'complete.json')==dict(completed=True,models=6,queries_per_model=484,total_queries=2904) and not (out/'failure.json').exists()
    cfg=read(out/'config.json');branches=np.asarray([0]+list(range(2,12)));assert cfg['branches']==branches.tolist()
    assert sha(script)==cfg['script_sha256']==sha(out/'used.py') and cfg['bank_ledger_sha256']==sha(bank/'ledger.json') and cfg['bank_rows_sha256']==sha(bank/'rows.json')
    actions=np.load(out/'actions.npy');physical=np.load(out/'physical_endpoints.npy');assert actions.shape==(44,11,35,2) and physical.shape==(44,11,7)
    ledger=sorted([v for v in read(bank/'ledger.json') if v['task']=='pusht'],key=lambda x:x['anchor']);bankrows=read(bank/'rows.json')
    for j,entry in enumerate(ledger):
        for index,branch in enumerate(branches):
            path=bank/f'pusht_{j:03d}_b{branch:02d}.npz';ref=next(v for v in bankrows if v['task']=='pusht' and v['anchor']==j and v['branch']==branch)
            assert ref['trace_sha256']==sha(path)
            with np.load(path) as trace:
                assert np.array_equal(physical[j,index],trace['diagnostic_states'][-1,:7]) and np.array_equal(actions[j,index],np.concatenate([entry['warm_actions'],trace['issued_actions']]))
    summaries=read(out/'summary.json');assert [v['method'] for v in summaries]==cfg['methods'];metrics={};counts=[]
    for summary in summaries:
        method=summary['method'];source=summary['source'];assert sha(source['checkpoint'])==source['checkpoint_sha256']
        for key,filename in [('rows_sha256',f'{method}_rows.json'),('prediction_sha256',f'{method}_predictions.npy'),('features_sha256',f'{method}_features.npy')]:assert summary[key]==sha(out/filename)
        controls=read(out/f'{method}_controls.json');assert [v['device'] for v in controls]==['cpu','cuda'] and all(v['passed'] and v['manual_native_cost_exact'] and v['weights_unchanged'] and v['source']==source for v in controls)
        if method!='RELEASED':
            run=ROOT/source['training_run'];assert source['training_config_sha256']==sha(run/'config.json') and read(run/'config.json')['train_anchors']==source['branch_training_anchors']==list(range(32))
        pred=np.load(out/f'{method}_predictions.npy');z=np.load(out/f'{method}_features.npy');rows=read(out/f'{method}_rows.json')
        assert pred.shape==(44,11,5,192) and z.shape==(44,11,8,192) and len(rows)==44
        assert np.array_equal(summary['prefix_mse'],np.mean((pred-z[:,:,3:])**2,axis=(0,1,3)))
        fields={key:[] for key in ['success','leave_out_success','position_regret','angle_error','oracle_success','success_available','zero_success']}
        for j,row in enumerate(rows):
            cost=np.sum((pred[j,:,4][None]-z[j,:,7][:,None])**2,-1);position=np.linalg.norm(physical[j][:,None,:4]-physical[j][None,:,:4],axis=-1)
            angle=np.abs(physical[j][:,None,4]-physical[j][None,:,4]);angle=np.minimum(angle,2*np.pi-angle);valid=(position<20)&(angle<np.pi/9);q=np.arange(11)
            selected=cost.argmin(1);masked=cost.copy();np.fill_diagonal(masked,np.inf);leave=masked.argmin(1)
            true=np.sum((z[j,:,7][:,None]-z[j,:,7][None])**2,-1);np.fill_diagonal(true,np.inf);oracle=true.argmin(1)
            best=position.copy();np.fill_diagonal(best,np.inf);availability=valid.copy();np.fill_diagonal(availability,False)
            assert row['anchor']==j and np.array_equal(row['predicted_costs'],cost) and np.array_equal(row['actual_position_distances'],position) and np.array_equal(row['actual_angle_distances'],angle)
            assert row['selected_branch']==branches[selected].tolist() and row['leave_goal_out_selected_branch']==branches[leave].tolist() and row['leave_goal_out_true_latent_oracle_branch']==branches[oracle].tolist()
            computed=dict(success=valid[q,selected],leave_out_success=valid[q,leave],position_regret=position[q,leave]-best.min(1),angle_error=angle[q,leave],oracle_success=valid[q,oracle],success_available=availability.any(1),zero_success=valid[:,0])
            rowfields=dict(success='native_success',leave_out_success='leave_goal_out_native_success',position_regret='leave_goal_out_position_regret',angle_error='leave_goal_out_angle_error',oracle_success='leave_goal_out_true_latent_oracle_native_success',success_available='leave_goal_out_success_available',zero_success='zero_only_native_success')
            for key,value in computed.items():assert np.array_equal(row[rowfields[key]],value);fields[key].append(value.mean())
        assert summary['native_successes']==int(sum(fields['success'])*11+1e-6) and summary['leave_goal_out_successes']==int(sum(fields['leave_out_success'])*11+1e-6)
        for key,values in fields.items():metrics[method,key]=np.asarray(values)
        for stratum,ids in [('all',np.arange(44)),('branch_train32',np.arange(32)),('branch_query12',np.arange(32,44))]:
            counts.append(dict(method=method,stratum=stratum,states=len(ids),queries=len(ids)*11,source_seeds=1,**{key:float(np.asarray(v)[ids].mean()) for key,v in fields.items()},source=source))
        print('Full H3 Push all matrix/source audit',method,'PASS',flush=True)
    rng=np.random.default_rng(118901);effects=[]
    for method in cfg['methods']:
        if method=='PLAIN':continue
        for key in ['success','leave_out_success','position_regret','angle_error']:
            delta=metrics[method,key]-metrics['PLAIN',key]
            for stratum,ids in [('all',np.arange(44)),('branch_train32',np.arange(32)),('branch_query12',np.arange(32,44))]:
                ix=rng.choice(ids,(10000,len(ids)),replace=True);effects.append(dict(method=method,reference='PLAIN',metric=key,stratum=stratum,mean_delta=float(delta[ids].mean()),paired_state_cluster_bootstrap_95=np.quantile(delta[ix].mean(1),[.025,.975]).tolist(),source_seeds=1))
    result=dict(completed=True,models=6,queries=2904,counts=counts,effects=effects,config=cfg,full_matrix_artifact=str(out),script_sha256=sha(__file__),scope='44 actual states x11 branch endpoint goals per model, six frozen fullH3 sources, original native position AND angle success. Position regret only auxiliary; oracle future evaluation-only. One transferseed/32 branch-train+12 branch-query/published pretraining unknown. No closed-loop, novel method, causal full-data reproduction, or 2904 independent-test claim.')
    dest=ROOT/'20261005-E13-pusht-full-branch-audit';assert not dest.exists();dest.mkdir();shutil.copy2(__file__,dest/'used.py');save(dest/'result.json',result);result['full_audit_artifact']=str(dest/'result.json');save(WB/'results/E13_20261005_pusht_full_branch_matrix_results.json',result)


if __name__=='__main__':main()
