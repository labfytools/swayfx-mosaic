"""Executable G2 scenario adapter. Import has NO run/arm/spawn side effect.
The parent binds an accepted pair #3 Session and reserves its own G2 ledger.
The common Session owns its private sockets, process groups and timeout cleanup.
"""
import hashlib,json,time
from pathlib import Path
from PIL import ImageChops
from protocol import ROOT,arm,epoch,gate,need

def exact_rgb(a,b):
 need(a.mode==b.mode=='RGB' and a.size==b.size,'whole-output homologous RGB')
 d=ImageChops.difference(a,b)
 # Exact all-output zero tolerance. This is a result, not an admission mask.
 return {'equal':d.getbbox() is None,'bbox':list(d.getbbox()) if d.getbbox() else None,'extrema':[list(x) for x in d.getextrema()],'pixels':a.width*a.height,'tolerance':0}
def run(s,binding):
 """Must be called once AFTER external review+ledger binding, BEFORE s.start.
 binding: gate_file, binary, client, nonce, source_manifest_sha256,
 G2_ledger_reserved=True, reviewed_scene_sha256. All operations debit s.ledger.
 No retry path; an exception before epoch A completes bypasses B/A-return.
 """
 need(binding.get('G2_ledger_reserved') is True,'external closed-ledger reservation absent')
 need(s.spec['id']=='G2' and s.spec['binary']=='core','distinct G2 Session identity/static pair')
 need(s.auth['binary']==binding['binary'],'accepted exact third executable')
 need(s.auth['manifest_sha256']==binding['source_manifest_sha256'],'frozen G2 manifest identity')
 gate(ROOT,Path(binding['gate_file']),Path(binding['binary']))
 need(not any(ROOT.glob('epoch-*')),'fresh one-shot publication directory')
 nonce=binding['nonce'];s.env.update(MOSAIC_G2_DIR=str(ROOT),MOSAIC_G2_NONCE=nonce,WLR_RENDERER='gles2')
 s.start()
 # Session captures actual executable hash, mapped libraries, renderer and
 # explicit private sockets. Its caller owns finally/cleanup and verdict.
 client=Path(binding['client']);need(client.is_file() and hashlib.sha256(client.read_bytes()).hexdigest()==binding['client_sha256'],'new client identity')
 s.cmd('workspace 2');s.spawn('g2-reference',[client,'reference']);s.wait(lambda:s.find('g2-reference'));rid=s.find('g2-reference')['id'];s.cmd(f'[con_id={rid}] border none')
 s.cmd('workspace 1');s.cmd('layout mosaic');s.cmd('gaps inner 0')
 s.spawn('g2-background',[client,'background']);s.wait(lambda:'BACKGROUND_CONFIGURED ' in s.log('g2-background'))
 s.spawn('g2-glass',[client,'glass']);s.wait(lambda:s.find('g2-glass'));gid=s.find('g2-glass')['id'];s.cmd(f'[con_id={gid}] border none')
 s.cmd('blur enable');s.cmd('blur_xray disable');s.cmd('blur_passes 3');s.cmd('blur_radius 5');s.cmd('blur_brightness 1');s.cmd('blur_contrast 1');s.cmd('blur_noise 0');s.cmd('blur_saturation 1')
 # Settle setup before the first arm. This sleep carries no proof of GPU
 # completion; exact native source admission rejects any wrong candidate.
 time.sleep(.35)
 reference=s.capture('G2-H2-baseline1','HEADLESS-2');time.sleep(.15)
 reference2=s.capture('G2-H2-baseline2','HEADLESS-2')
 baseline=exact_rgb(reference,reference2);s.save('G2-H2-baseline',baseline)
 need(baseline['equal'],'static whole H2 baseline changed before A')
 captures=[];validated=[];total=0
 for e,command in enumerate(('G2-A','G2-B','G2-A-return'),1):
  s.debit('mutation');s.record('G2-epoch-reservation',epoch=e,raw_cap=256*1024*1024)
  arm(ROOT,e,nonce,Path(binding['gate_file']),Path(binding['binary']))
  s.proc['g2-background'].stdin.write(command+'\n');s.proc['g2-background'].stdin.flush()
  s.wait(lambda:f'G2_SOURCE_BYTES command={command} ' in s.log('g2-background'))
  path=ROOT/f'epoch-{e}.jsonl'
  def complete_or_rejected():
   if not path.exists():return False
   data=path.read_bytes();need(len(data)<=1024*1024,'bounded metadata while waiting')
   if b'"kind":"rejected"' in data:raise RuntimeError(f'epoch {e} rejected; STOP, no next command/retry')
   return data.endswith(b'\n') and b'"kind":"end"' in data
  s.wait(complete_or_rejected)
  # Failure here exits before subsequent epoch token or source command.
  result=epoch(ROOT,e,nonce,total);total=result['raw_total'];validated.append(result)
  pictures=s.pair_capture(f'G2-{command}');captures.append(pictures);s.snapshot(f'G2-{command}')
  h2=exact_rgb(reference,pictures[1]);s.save(f'G2-{command}-wholeH2',h2)
  need(h2['equal'],'whole H2 changed: rejected epoch, STOP without retry')
  s.record('G2-epoch-accepted',epoch=e,command=command,native_raw_total=total)
 whole_h1=exact_rgb(captures[0][0],captures[2][0]);whole_h2=[exact_rgb(captures[0][1],x[1]) for x in captures[1:]]
 sa=(ROOT/'epoch-1-point-0.rgba').read_bytes();sr=(ROOT/'epoch-3-point-0.rgba').read_bytes()
 result={'schema':'G2-new-v1','epochs':validated,'native_source_A_Areturn_exact':sa==sr,'whole_H1_A_Areturn':whole_h1,'whole_H2_baseline':baseline,'whole_H2_A_B_Areturn':whole_h2,'whole_field_causality':'NOT_PROVEN','physical_present_buffer':'NOT_PROVEN','gpu_completion':'NOT_PROVEN','atomic_generation':'NOT_PROVEN','instrumentation':'INTRUSIVE_ERROR_QUEUE_AND_READBACK_SYNC','source_commands':['G2-A','G2-B','G2-A-return']}
 s.save('G2-result',result)
 for name in ('g2-glass','g2-background','g2-reference'):s.close_client(name,'close')
 return result
