"""Prospective recovery matrix; historical E reservations are closed."""
def out(name,logical):
 return dict(name=name,logical=logical,mode=logical[2:],scale=1,transform='normal')
H=[out('HEADLESS-1',[-800,0,800,600]),out('HEADLESS-2',[0,0,800,600])]
CAP={'S0-pristine-standard':12,'S1-core-standard':12,'S2-core-horizontal':18,'S3-pristine-vertical':12,'S4-core-vertical':12,'S5-pristine-fullscreen':14,'S6-core-fullscreen':14,'S7-core-hidden-return':14,'S8-core-saved':12}
RUNS={rid:dict(id=rid,binary='pristine' if 'pristine' in rid else 'core',mode='pristine' if 'standard' in rid or 'pristine' in rid else 'mosaic',outputs=H,client='nested-client',placement='static_cross',axis=0,boundary=0,capture_limit=cap,action_limits=dict(configuration=60,mutation=24,move=20,click=12,grab=4,camera=6,chain=2)) for rid,cap in CAP.items()}
for rid in ('S3-pristine-vertical','S4-core-vertical'):
 RUNS[rid].update(outputs=[out('HEADLESS-1',[0,0,800,600]),out('HEADLESS-2',[0,600,800,600])],client='vertical-client',placement='v_both_cross',axis=1,boundary=600)
