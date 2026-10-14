"""Independent EXPERIMENTAL plans; old 18-run ledger remains read only."""
from pathlib import Path
HIST=Path('/home/fy59/swayfx-mosaic-overnight-mcolx0gq')
DEFAULT_LAB=Path('/home/fy59/swayfx-mosaic-targeted-7gge6h8b')
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'tooling/probes/step20c-static-e2-completion'
MATRIX=ROOT/'tooling/probes/step20c-overnight/matrix'
PRISTINE=Path('/home/fy59/swayfx-mosaic-optimized-edge-a55yjb8n/pristine-build/sway/sway')
SCENE=Path('/home/fy59/swayfx-mosaic-optimized-edge-a55yjb8n/scene0-build/libscenefx-0.5.so').resolve()
BINARIES={
 'A':(HIST/'stage-static/usr/bin/swayfx-mosaic','979dcd95ab43fa1e465d6e9d262485b73d186cedacd0f957059dd24f482ce6f4'),
 'G':(HIST/'release-shape/stage-static/usr/bin/swayfx-mosaic','8063478b2d5948da3eb8b1a329978882dc1d045cf36932cc2145a78af20ba76a'),
 'pristine':(PRISTINE,'8ac865481bc0487344210cd0e16d8e6c7655b29db887cd58ddc11b0ca22fe494')}
WLROOTS=Path('/usr/lib/libwlroots-0.20.so').resolve()
WLROOTS_SHA='7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
CAPS={'scale':24,'saved':30,'FX':48,'input':36,'G':36}
RUN_CAPS={'scale':2,'saved':3,'FX':3,'input':3,'G':3}
NORMAL=[dict(name='HEADLESS-1',logical=[-800,0,800,600],mode=[800,600],scale=1,transform='normal'),dict(name='HEADLESS-2',logical=[0,0,800,600],mode=[800,600],scale=1,transform='normal')]
SCALE=[{**NORMAL[0],'mode':[1000,750],'scale':1.25},NORMAL[1]]
ROTATE=[{**NORMAL[0],'mode':[750,1000],'scale':1.25,'transform':'90'},NORMAL[1]]
RUNS={}
def plan(campaign,variant,case,outputs=NORMAL,marker=False,capture=12):
    rid=f'{campaign}-{variant}' if case==campaign else f'{campaign}-{case}-{variant}'
    RUNS[rid]=dict(id=rid,campaign=campaign,case=case,variant=variant,mode='pristine' if variant=='pristine' else 'mosaic',outputs=outputs,marker=marker,client='nested-client',placement='static_cross',axis=0,boundary=0,
        limits=dict(capture=capture,click=14,move=20,grab=2,chain=1,camera=4,mutation=28,configuration=64,spawn=12),duration_s=150,active_watchdog_s=143,
        status='PLANNED',ceilings=['atomic generation NOT PROVEN','native saved identity NOT OBSERVABLE','complete damage/lifetime NOT PROVEN','STEP20C NEXT; production multi-output NOT YET SUPPORTED'])
for v in ('A','G'):plan('scale',v,'scale',SCALE,True,12);plan('saved',v,'saved',capture=10)
for v in ('pristine','A','G'):plan('input',v,'input',capture=12);plan('FX',v,'FX',capture=16)
for c in ('dynamic','hidden','R90'):plan('G','G',c,ROTATE if c=='R90' else NORMAL,c=='R90',{'dynamic':14,'hidden':12,'R90':10}[c])
# Diagnostic is a separate reserved run, disabled until the parent records a decision.
DIAGNOSTIC_ID='saved-diagnostic-A'
