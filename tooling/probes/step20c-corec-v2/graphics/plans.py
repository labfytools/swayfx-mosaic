"""Frozen V2 intent. Admission is independent of intent; no calibration/retry runs."""
from copy import deepcopy
CAPS=dict(P0=10,P1=10,C1=18,C2=12,C3=12,C4=12,C5=12,C6=12,C7=14,C8=12,O1=8,O2=8,G2=16,R1=14)
LIMITS=dict(runs=14,captures=180,captures_per_run=18,duration_s=150)
def output(name,logical,mode=None,scale=1,transform='normal'):
 return dict(name=name,logical=logical,mode=mode or logical[2:],scale=scale,transform=transform)
H=[output('HEADLESS-1',[-800,0,800,600]),output('HEADLESS-2',[0,0,800,600])]
RUNS={rid:dict(id=rid,binary='pristine' if rid in ('P0','P1') else 'core',mode='pristine' if rid in ('P0','P1') else 'mosaic',outputs=deepcopy(H),client='nested-client',placement='static_cross',axis=0,boundary=0,capture_limit=cap,action_limits=dict(spawn=12,configuration=70,mutation=26,move=24,click=12,grab=4,camera=6,chain=2),admission='PENDING_INDEPENDENT_REVIEW') for rid,cap in CAPS.items()}
RUNS['C2'].update(outputs=[output('HEADLESS-1',[0,0,800,600]),output('HEADLESS-2',[0,600,800,600])],client='vertical-client',placement='v_both_cross',axis=1,boundary=600)
RUNS['C3']['outputs'][0]=output('HEADLESS-1',[-800,0,800,600],[1000,750],1.25)
RUNS['C4']['outputs'][0]=output('HEADLESS-1',[-800,0,800,600],[750,1000],1.25,'90')
# Geometry certificates and distinct diagnostics are prerequisite source evidence.
for rid in ('P1','C8'):
 RUNS[rid].update(admission='NOT_ADMITTED',reason='No offline equal-child nonleaf fullscreen configure/crossing certificate; no empirical calibration authorized')
for rid in ('P1','C8'):
 RUNS[rid].update(client='fullscreen-client',placement='fullscreen_cross')
for rid in ('O1','O2'):
 RUNS[rid]['binary']='oom';RUNS[rid]['action_limits']['hook']=1
for rid in ('O1','O2','G2','R1'):
 RUNS[rid].update(admission='NOT_ADMITTED',reason='Separately reviewed diagnostic/discriminant source hook and exact binary unavailable')
RUNS['G2']['binary']='gpu';RUNS['G2']['action_limits']['hook']=3
assert len(RUNS)==14 and sum(CAPS.values())==170 and max(CAPS.values())==18

def config(spec):
 cfg='\n'.join(f"output {o['name']} resolution {o['mode'][0]}x{o['mode'][1]} scale {o['scale']} transform {o['transform']} position {o['logical'][0]} {o['logical'][1]}" for o in spec['outputs'])
 return cfg+'\nworkspace 1 output HEADLESS-1\nworkspace 2 output HEADLESS-2\nfocus_follows_mouse no\nseat seat0 hide_cursor 100\nshadows disable\nblur disable\n'
for spec in RUNS.values():spec['config']=config(spec)
