"""EXPERIMENTAL fixed one-shot contracts; no production qualification."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
HIST=ROOT/'tooling/probes/step20c-targeted'
BASE=ROOT/'tooling/probes/step20c-static-e2-completion'
DEFAULT_LAB=Path('/home/fy59/swayfx-mosaic-saved-input-gpu-pz4z428f')
SCOPE='SWAYFX_MOSAIC_STEP20C_SAVED_LIFETIME_INPUT_EPOCH_AND_GPU_CAUSALITY_BATCH_V1'
OLD_LAB=Path('/home/fy59/swayfx-mosaic-targeted-7gge6h8b')
WLROOTS=Path('/usr/lib/libwlroots-0.20.so').resolve()
WLROOTS_SHA='7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
BINARIES={
'A':(Path('/home/fy59/swayfx-mosaic-overnight-mcolx0gq/stage-static/usr/bin/swayfx-mosaic'),'979dcd95ab43fa1e465d6e9d262485b73d186cedacd0f957059dd24f482ce6f4'),
'G':(Path('/home/fy59/swayfx-mosaic-overnight-mcolx0gq/release-shape/stage-static/usr/bin/swayfx-mosaic'),'8063478b2d5948da3eb8b1a329978882dc1d045cf36932cc2145a78af20ba76a')}
C3_SHA='9c0dc0e94ccc7fcbd7a6cddf14e90f1bb7b7bf385a0740e85ec7d0e1c1c1e705'
CAPS={'saved':36,'input':24,'gpu':24,'native':12}
NORMAL=[dict(name='HEADLESS-1',logical=[-800,0,800,600],mode=[800,600],scale=1,transform='normal'),dict(name='HEADLESS-2',logical=[0,0,800,600],mode=[800,600],scale=1,transform='normal')]
RUNS={}
for rid,cat,v,n in [('saved-C3','saved','C3',10),('saved-A','saved','A',10),('saved-G','saved','G',10),('input-A','input','A',12),('input-G','input','G',12),('gpu-diagnostic','gpu','diagnostic',12),('native-diagnostic','native','native',12),('gpu-pristine','gpu','pristine',12)]:
    RUNS[rid]=dict(id=rid,campaign=cat,case=cat,variant=v,mode='mosaic',outputs=NORMAL,marker=False,axis=0,boundary=0,client='saved-client',placement='static_cross',duration_s=150,active_watchdog_s=143,status='EXPERIMENTAL',conditional=cat in ('gpu','native'),limits=dict(capture=n,click=8 if cat=='input' else 0,move=16 if cat=='input' else 10,grab=0,chain=0,camera=4,mutation=20,configuration=50,spawn=8),ceilings=['GPU completion NOT PROVEN','atomic generation NOT PROVEN','STEP20C NEXT'])
