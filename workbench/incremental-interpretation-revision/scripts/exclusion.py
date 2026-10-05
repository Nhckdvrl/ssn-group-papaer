"""E21 named versus generic/minimal, with exclusive facts preserved."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
from data import sha,write_jsonl
from late_role_evidence import build as build_roles
from fact_order import adopt_order,analyze as compare_orders
from analyze import estimate


def build(cache,fields_path,out):
    assert not out.exists()
    j=json.loads(fields_path.read_text());rows=[]
    with tempfile.TemporaryDirectory(dir=fields_path.parent) as tmp:
        p=Path(tmp)
        shutil.copyfile(cache/'E19-material-preparation-v1/role-evidence-packets.json',p/'role-evidence-packets.json')
        for style in ('minimal','generic'):
            fields=[]
            for r in j['rows']:
                f=dict(r)
                for e in ('reference_only','initial_patient_only'):f[e+'_sentence']=r[e+'_'+style+'_sentence']
                fields.append(f)
            fp=p/f'{style}-role-fields-v2.json'
            fp.write_text(json.dumps(dict(model='gpt-6-luna',rows=fields,source_fields_sha256=sha(fields_path)),indent=2)+'\n')
            output=p/f'{style}.jsonl';build_roles(cache,fp,output,anchors=('same',),experiment='E21:'+style)
            rows.extend(dict(r,exclusion_style=style) for r in map(json.loads,output.read_text().splitlines()))
    assert len(rows)==336
    write_jsonl(out,rows)
    return dict(variants=336,source_items=7,candidate_sha256=sha(out),fields_sha256=sha(fields_path))


def analyze(cache,path):
    result=compare_orders(cache,path,old_experiment='E20',old_order='named',new_orders=('minimal','generic'),new_field='exclusion_style')
    result.update(experiment='E21',primary='Does explicitly naming the excluded patient create more GP history dependence than equivalent minimal/generic exclusion?',
        interpretation='Tests named remention while preserving only-X facts. Generic reference-only is length/order matched to named; minimal is shorter and therefore cannot isolate repetition alone.')
    # Direct generic-minus-minimal contrast also retained, on the same audited
    # common cohort, to show whether generic negation itself changes the effect.
    for stratum in ('all','eligible','acceptable','faithful_order'):
        for option in (0,1,'both'):
            prefix=f'{stratum}/option{option}'
            byid={r['pair_id']:r for r in result['per_source'][prefix]}
            for m in ('R','M'):
                for e in ('reference_only','initial_patient_only'):
                    vals={k:r[f'{m}_D_generic_{e}']-r[f'{m}_D_minimal_{e}'] for k,r in byid.items()}
                    stats=estimate([vals[k] for k in sorted(vals)]) if len(vals)>1 else dict(estimate=next(iter(vals.values()),None),ci95=None,n_sets=len(vals))
                    result['contrasts'][f'{prefix}/{m}/generic_minus_minimal/{e}']=dict(stats,pair_ids=sorted(vals))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,required=True);b.add_argument('--fields',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--idmap',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,required=True);n.add_argument('--new',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build':print(json.dumps(build(args.cache,args.fields,args.out),indent=2))
    elif args.action=='adopt':print(json.dumps(adopt_order(args.data,args.reviews,args.idmap,args.out),indent=2))
    else:args.out.write_text(json.dumps(analyze(args.cache,args.new),indent=2)+'\n')
