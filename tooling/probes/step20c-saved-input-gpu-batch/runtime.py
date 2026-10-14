"""Derived EXPERIMENTAL Session, preserving sealed historical engine bytes."""
import importlib.util,sys,os,re,time,shutil,signal,subprocess
from pathlib import Path
import ledger
from plans import HIST,BASE
# WHY CONTRACT INVARIANT: historical imports have their own plans/gate names;
# load them in a temporary namespace and restore this campaign's modules.
def historical(name):
    saved={k:sys.modules.get(k) for k in ('plans','gate','engine','validators')};old=sys.path[:]
    try:
        for k in saved:sys.modules.pop(k,None)
        sys.path[:0]=[str(HIST),str(BASE)]
        spec=importlib.util.spec_from_file_location('historical_'+name,HIST/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    finally:
        sys.path[:]=old
        for k,v in saved.items():
            sys.modules.pop(k,None)
            if v is not None:sys.modules[k]=v
engine=historical('engine')
cases=historical('cases')
SessionBase=engine.Session
class Session(SessionBase):
    def debit(self,*kinds):ledger.action_debit(self.lab,self.spec['id'],*kinds)
    def spawn(self,name,argv,debug=False):
        argv=list(map(str,argv))
        if name=='compositor':argv=[a.replace('txn-timeout=2500','txn-timeout=5000') for a in argv]
        p=super().spawn(name,argv,debug)
        self.persist_identity('spawn');return p
    def persist_identity(self,phase):
        ledger.durable(self.run/'owned-runtime.json',dict(phase=phase,uid=os.getuid(),runtime=str(self.runtime),runtime_mode=oct(self.runtime.stat().st_mode&0o777) if self.runtime.exists() else None,socket=str(getattr(self,'sock','')),processes=[dict(name=n,pid=p.pid,exit=p.poll()) for n,p in self.proc.items()],ns=time.monotonic_ns()))
    def start(self):
        if self.spec['variant']=='C3':self.env['SAVED_DIAGNOSTIC']='1'
        super().start();self.persist_identity('socket-bound')
    def inject(self,action,point,grab=False):
        # No settling sleep: mutation during delivery is the measured phenomenon.
        engine.need(action in ('move','left','right'),'action');outs=self.ipc('-t','get_outputs');rects=[[o['rect'][k] for k in ('x','y','width','height')] for o in outs if o['active']]
        engine.need(any(engine.contains(r,point) for r in rects),'inside output')
        x=min(r[0] for r in rects);y=min(r[1] for r in rects);w=max(r[0]+r[2] for r in rects)-x;h=max(r[1]+r[3] for r in rects)-y
        self.debit('move',*(['click'] if action!='move' else []),*(['grab'] if grab else []));sent=[point[0]-x,point[1]-y];marker=f'INJECT_DONE {action} {sent[0]},{sent[1]}';before=self.log('pointer').count(marker);start=time.monotonic_ns()
        self.pointer.stdin.write(f'{action} {sent[0]} {sent[1]} {w} {h}\n');self.pointer.stdin.flush();self.wait(lambda:self.log('pointer').count(marker)>before)
        self.record('injection',action=action,global_logical=point,sent=sent,logical_extent=[w,h],grab=grab,start_ns=start,end_ns=time.monotonic_ns())
    def close_client(self,name,command='close_owner'):
        self.client_cmd(name,command);code=self.proc[name].wait(timeout=3);engine.need(code==0,'client exit0');self.wait(lambda:self.find(name) is None)
        exits=re.findall(r'EXIT[^\n]*error=(\d+)',self.log(name));engine.need(all(e=='0' for e in exits),'Wayland error0 required even with process exit0')
        if not exits:self.record('client-error-observability',name=name,status='NOT OBSERVABLE; scientific cleanup NOT PROVEN')
    def cleanup(self,measurement_status,failure=None):
        self.persist_identity('before-cleanup')
        # Record identities/exit status durably immediately before historical
        # removal, including watchdog rescue; no live desktop socket is used.
        original=engine.shutil.rmtree
        def remove(path,*args,**kwargs):
            if Path(path)==self.runtime:self.persist_identity('before-runtime-removal')
            return original(path,*args,**kwargs)
        engine.shutil.rmtree=remove
        try:status=super().cleanup(measurement_status,failure)
        finally:engine.shutil.rmtree=original
        outcome=ledger.read(self.run/'outcome.json');errors={n:re.findall(r'EXIT[^\n]*error=(\d+)',self.log(n)) for n in self.proc if n not in ('compositor','pointer')}
        explicit_errors=errors.get('owner',[])
        clean=outcome['cleanup_pass'] and bool(explicit_errors) and not any(e!='0' for es in errors.values() for e in es)
        outcome.update(scientific_cleanup='PASS' if clean else 'INCONCLUSIVE',wayland_exit_errors=errors,measurements_pass=measurement_status,runtime_exit=outcome['processes'])
        if not clean:outcome['status']='INCONCLUSIVE'
        ledger.durable(self.run/'outcome.json',outcome);return outcome['status']

def main():
    import argparse
    from plans import DEFAULT_LAB,RUNS
    p=argparse.ArgumentParser();p.add_argument('run_id',choices=RUNS);p.add_argument('--lab',type=Path,default=DEFAULT_LAB);args=p.parse_args()
    auth=ledger.begin(args.lab,args.run_id);s=None;status='INCONCLUSIVE';failure=None
    try:
        s=Session(RUNS[args.run_id],auth,args.lab);s.start()
        if s.spec['campaign']=='saved':from saved import run
        elif s.spec['campaign']=='input':from input import run
        else:raise ValueError('conditional diagnostics require separate reviewed runner')
        status=run(s)
    except Exception as e:failure=f'{type(e).__name__}: {e}'
    finally:
        if s is not None:status=s.cleanup(status,failure)
    print(status,failure or '');return 0 if status=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
