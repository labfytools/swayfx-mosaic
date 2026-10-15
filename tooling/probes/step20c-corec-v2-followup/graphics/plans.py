"""EXPERIMENTAL new-ticket intent; no plan grants admission by itself."""
from copy import deepcopy
CAPS={'FS-P':12,'FS-C':16,'DY-C':16,'OM-ROOT':10,'OM-NESTED':10,'GPU-G3':12,'OM-EXTRA':12,'GPU-CTRL':12}
LIMITS=dict(runs=8,captures=110,captures_per_run=18,duration_s=150)
H=[dict(name='HEADLESS-1',logical=[-800,0,800,600],mode=[800,600],scale=1,transform='normal'),dict(name='HEADLESS-2',logical=[0,0,800,600],mode=[800,600],scale=1,transform='normal')]
def config(spec):
 return '\n'.join(f"output {o['name']} resolution {o['mode'][0]}x{o['mode'][1]} scale {o['scale']} transform {o['transform']} position {o['logical'][0]} {o['logical'][1]}" for o in spec['outputs'])+'\nworkspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\nfocus_follows_mouse no\nseat seat0 hide_cursor 100\nshadows disable\nblur disable\n'
RUNS={rid:dict(id=rid,binary='pristine' if rid=='FS-P' else 'core',mode='pristine' if rid=='FS-P' else 'mosaic',outputs=deepcopy(H),client='nested-client',placement='static_cross',axis=0,boundary=0,capture_limit=cap,action_limits=dict(spawn=12,tool=160,configuration=80,mutation=26,move=24,click=12,grab=4,camera=6,chain=2,source_marker=1),admission='INDEPENDENT_REVIEW_REQUIRED') for rid,cap in CAPS.items()}
for rid in ('FS-P','FS-C'):RUNS[rid].update(client='fullscreen-client',placement='fullscreen_cross')
for rid in ('OM-ROOT','OM-NESTED','OM-EXTRA'):
 RUNS[rid]['binary']='oom';RUNS[rid]['action_limits']['hook']=1
for rid in ('GPU-G3','GPU-CTRL'):
 RUNS[rid].update(binary='gpu',admission='NOT_ADMITTED',reason='B4 and separately reviewed GPU adapter required')
 RUNS[rid]['action_limits']['hook']=3
RUNS['OM-EXTRA'].update(admission='NOT_ADMITTED',reason='Distinct question, handler and additional independent review required')
for spec in RUNS.values():spec['config']=config(spec)
assert len(RUNS)==8 and sum(CAPS.values())==100 and max(CAPS.values())<=18
