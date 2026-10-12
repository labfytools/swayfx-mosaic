"""Execute the real reservation block without starting a compositor or camera."""
from pathlib import Path
import json
import signal
import subprocess
import tempfile

runner=Path(__file__).with_name('run.py').resolve()
source=runner.read_text().split("scales = ")[0]
# CONTRACT: only the launch tail is replaced; production reservation executes.
root=Path(tempfile.mkdtemp(prefix='fractional-budget-test-'))
script=root/'reservation.py'
script.write_text('__file__='+repr(str(runner))+'\n'+source+"\nprint('RESERVED',flush=True)\nsys.stdin.readline()\nraise SystemExit(7)\n")
def launch(lab,pairs):
    return subprocess.Popen(['python',str(script),str(lab),'private_mosaic','G1','--camera-pairs',str(pairs)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
lab=root/'lab';lab.mkdir()
p=launch(lab,1);assert p.stdout.readline().strip()=='RESERVED'
q=launch(lab,1);out,err=q.communicate();assert q.returncode!=0 and 'BlockingIOError' in err
p.send_signal(signal.SIGINT);p.communicate(timeout=5)
assert json.loads((lab/'fractional-camera-budget.json').read_text())['consumed']==1
p=launch(lab,1);assert p.stdout.readline().strip()=='RESERVED';p.communicate();assert p.returncode==7
p=launch(lab,1);out,err=p.communicate();assert p.returncode==2 and 'exhausted' in err
p=launch(lab,0);assert p.stdout.readline().strip()=='RESERVED';p.communicate()
assert json.loads((lab/'fractional-camera-budget.json').read_text())['consumed']==2
old=root/'old';(old/'runs/control-fractional-G1-old').mkdir(parents=True)
p=launch(old,0);out,err=p.communicate();assert p.returncode==2 and 'silent budget reset' in err
print('PASS reserve/lock/interruption/failure/exhaustion/zero/missing-ledger; no compositor launched:',root)
