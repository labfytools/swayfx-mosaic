"""Fail-closed persistent campaign reservations; shared across clones/LABs."""
import fcntl,json,os,tempfile
from pathlib import Path
MODES=('C0','C1','C2')
CAMPAIGN='SWAYFX_MOSAIC_STEP20C_SAVED_TIMEOUT_FREEZE_AND_OPTIMIZED_BLUR_CACHE_V1'
DEFAULT=Path.home()/'swayfx-mosaic-optimized-blur-v1-budget.json'

def reserve(lab,mode,resource,path=DEFAULT):
 if mode not in MODES or resource not in ('run','mutation','capture','cycle','camera_pair','calibration'):raise ValueError('unknown reservation')
 lab=str(Path(lab).resolve());path=Path(path)
 with path.with_suffix('.lock').open('a+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  state=json.loads(path.read_text()) if path.exists() else {'campaign':CAMPAIGN,'lab':lab,'modes':{m:{k:0 for k in ('run','mutation','capture','cycle','camera_pair','calibration')} for m in MODES}}
  if state.get('campaign')!=CAMPAIGN or state.get('lab')!=lab:raise RuntimeError('campaign already bound to another LAB')
  for m in MODES:
   for k,v in state['modes'][m].items():
    if type(v) is not int or v<0:raise RuntimeError('corrupt budget')
  counts=state['modes'][mode]
  limits={'run':1,'mutation':4,'capture':20,'cycle':0 if mode=='C0' else 1,'camera_pair':1 if mode=='C2' else 0,'calibration':1 if mode=='C2' else 0}
  if resource!='run' and counts['run']!=1:raise RuntimeError('reserve run first')
  if counts[resource]>=limits[resource]:raise RuntimeError('budget exhausted: '+resource)
  if resource=='capture' and sum(s['capture'] for s in state['modes'].values())>=60:raise RuntimeError('global captures exhausted')
  counts[resource]+=1
  fd,tmp=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
  try:
   with os.fdopen(fd,'w') as out:json.dump(state,out,sort_keys=True);out.write('\n');out.flush();os.fsync(out.fileno())
   os.replace(tmp,path)
   directory=os.open(path.parent,os.O_DIRECTORY);os.fsync(directory);os.close(directory)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
  return state
