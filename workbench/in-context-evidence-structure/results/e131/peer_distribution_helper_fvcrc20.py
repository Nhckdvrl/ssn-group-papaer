import concurrent.futures,hashlib,ipaddress,json,os,subprocess,time
from pathlib import Path
root=Path('/home/xiang/ssn-group-papaer/workbench/in-context-evidence-structure')
source=json.loads((root/'results/e131/model_identity_llama70_fvcrc11.json').read_text())
assert source['all_weights_sha256_passed'] and source['official_mirror_all30_match']
assert os.uname().nodename=='fvcrc20'
dest=Path('/dev/shm/ices_llama70_weights_20261012/Llama-3.1-70B')
dest.mkdir(parents=True,exist_ok=True)
space=os.statvfs(dest); required=sum(x['bytes'] for x in source['files'] if not (dest/x['file']).exists())
assert space.f_bavail*space.f_frsize > required+2*1024**3
target=Path('/tmp/ices_models/Llama-3.1-70B');target.parent.mkdir(parents=True,exist_ok=True)
if not target.exists():target.symlink_to(dest,target_is_directory=True)
assert target.resolve()==dest.resolve()
ssh='ssh -o LogLevel=ERROR -o IdentityAgent=none -o ProxyCommand=none -o BatchMode=yes -o ConnectTimeout=7'
peer_address=os.environ.get('ICES_E131_PEER_ADDRESS')
if peer_address:
 ipaddress.ip_address(peer_address)
 ssh+=' -o HostName='+peer_address+' -o HostKeyAlias=fvcrc11'
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
def transfer(item):
 name=item['file'];final=dest/name;partial=dest/(name+'.partial')
 if not(final.exists() and final.stat().st_size==item['bytes'] and digest(final)==item['sha256']):
  for attempt in range(5):
   r=subprocess.run(['rsync','--partial','--append-verify','-e',ssh,'fvcrc11:/tmp/ices_models/Llama-3.1-70B/'+name,str(partial)],stdout=subprocess.DEVNULL)
   if r.returncode==0 and partial.stat().st_size==item['bytes'] and digest(partial)==item['sha256']:
    partial.replace(final);break
   print('RETRY',name,attempt,flush=True);time.sleep(2)
  else:raise RuntimeError('Pinned peer copy failed: '+name)
 print('VERIFIED',name,item['bytes'],flush=True)
 return dict(item,placement=str(final),existing=False)
started=time.time();print('START pinned peer distribution fvcrc11 -> fvcrc20',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:files=list(pool.map(transfer,source['files']))
assert sum(x['file'].endswith('.safetensors') for x in files)==30
record=dict(source,host=os.uname().nodename,target=str(target),files=files,scientific_scores=0,peer_source_host='fvcrc11',asset_storage=str(dest),copy_wall_seconds=time.time()-started,scientific_protocol_changed=False)
(root/'results/e131/model_identity_llama70_fvcrc20.json').write_text(json.dumps(record,indent=2)+'\n')
print('READY all 30 official-matching weight shards',round(time.time()-started,1),flush=True)
