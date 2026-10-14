"""Prospective fixed E matrix; no reruns or diagnostic tokens here."""
def out(name,logical,mode=None,scale=1,transform='normal'):
 return dict(name=name,logical=logical,mode=mode or logical[2:],scale=scale,transform=transform)
H=[out('HEADLESS-1',[-800,0,800,600]),out('HEADLESS-2',[0,0,800,600])]
CAP={'E0-pristine':12,'E0-core':12,'E1':20,'E2-vertical':14,'E2-fractional':14,'E2-r90':14,'E3':18,'E4':14,'E5':12,'E6':10,'E7':14}
# WHY/CONTRACT/INVARIANT: maxima fixed before review and include two E1 chains.
RUNS={rid:dict(id=rid,binary='pristine' if rid=='E0-pristine' else 'core',mode='pristine' if rid.startswith('E0') else 'mosaic',outputs=H,campaign='FX' if rid=='E7' else rid,client='nested-client',placement='static_cross',axis=0,boundary=0,capture_limit=cap,action_limits=dict(configuration=60,mutation=24,move=20,click=12,grab=4,camera=6,chain=2)) for rid,cap in CAP.items()}
RUNS['E2-vertical'].update(outputs=[out('HEADLESS-1',[0,0,800,600]),out('HEADLESS-2',[0,600,800,600])],client='vertical-client',placement='v_both_cross',axis=1,boundary=600)
RUNS['E2-fractional']['outputs']=[out('HEADLESS-1',[-800,0,800,600],[1000,750],1.25),H[1]]
RUNS['E2-r90']['outputs']=[out('HEADLESS-1',[-800,0,800,600],[750,1000],1.25,'90'),H[1]]
