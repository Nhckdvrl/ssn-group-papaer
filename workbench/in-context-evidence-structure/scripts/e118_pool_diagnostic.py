"""CPU feasibility inspection; no model scoring or changes to science engine."""
import sys
from pathlib import Path
s=Path(__file__).with_name('e118_criterion_code_feature_crossing.py').read_text()
s=s.replace('    cs=[]', "    print('Unique-bin feasibility', [(str(key)[:70],len(v),sum(not set(v[i].values()).intersection(v[j].values()) for i in range(len(v)) for j in range(i+1,len(v)))) for key,v in bins.items() if key in valid]); return\n    cs=[]", 1)
exec(compile(s,'e118_CPU_diagnostic','exec'),{'__name__':'__main__','__file__':str(Path(__file__).with_name('e118_criterion_code_feature_crossing.py'))})
