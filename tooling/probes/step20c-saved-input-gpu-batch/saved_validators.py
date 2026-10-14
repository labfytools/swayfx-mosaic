"""Shared runtime/replay saved predicates; derived intervals are not native epochs."""
import re
from runtime import historical
from ledger import need
from PIL import ImageChops
# Reuse wire and geometry predicates without modifying any executed fixture.
import importlib.util,sys
from plans import HERE
_diag=HERE.parent/'step20c-targeted-diagnostic/diagnostic.py'
# Extract the reviewed pure predicates only; no diagnostic registration/budget.
_source=_diag.read_text();_ns={'held_configure':historical('validators').held_configure}
exec('from runtime import engine\nworkspace=engine.workspace\nnodes=engine.nodes\nfrom geometry import need,intersection\nimport re\n'+_source[_source.index('def pending_geometry('):],_ns)
pending_geometry=_ns['pending_geometry']
held_configure=_ns['held_configure']
records=_ns['records']
def lifetime_instances(text):
    lines=text.splitlines();active={};instances=[];retired={}
    for index,raw in enumerate(lines):
        tags=[t for t in ('SD_CREATE','SD_TREE','SD_SAMPLE','SD_REMOVE','SD_NODE_DESTROY','SD_RELEASE','SD_BUFFER_DESTROY') if t+' ' in raw]
        if not tags:continue
        tag=tags[0];r=dict(re.findall(r'(\w+)=([^\s]+)',raw),raw=raw,line=index);need('ns' in r,'native ns');ns=int(r['ns'])
        if tag=='SD_CREATE':
            need(all(r.get(k) not in (None,'(nil)','0x0') for k in ('node','source','tree','parent','source_node')),'create identity fields')
            need(r['node'] not in active,'overlapping address lifetime');need(r['node']!=r['source_node'],'distinct copy')
            v=dict(create=r,activation=None,samples=[],destroy=None,releases=[],buffer_destroy=[],observed_instance=len(instances));instances.append(v);active[r['node']]=v
        elif tag=='SD_TREE':
            matches=[v for v in active.values() if v['create']['tree']==r.get('tree') and v['activation'] is None]
            # Empty initialization trees carry no saved-buffer lifetime.
            if not matches:continue
            for v in matches:
                need(v['create']['parent']==r.get('parent') and ns>int(v['create']['ns']) and r.get('owner') and r.get('saved_enabled')=='1' and r.get('content_enabled')=='0','tree owner/parent/activation');v['activation']=r
        elif tag in ('SD_SAMPLE','SD_NODE_DESTROY'):
            need(r.get('node') in active,'sample/destroy outside live instance');v=active[r['node']];c=v['create'];need(r.get('source')==c['source'] and ns>=int(c['ns']),'matching source/lifetime')
            if tag=='SD_SAMPLE':
                need(v['activation'] is not None and ns>int(v['activation']['ns']) and r.get('output') in ('HEADLESS-1','HEADLESS-2') and r.get('enabled')=='1' and r.get('node_enabled')=='1','sample active owner/output');v['samples'].append(r)
            else:v['destroy']=r;active.pop(r['node']);retired.setdefault((r['node'],r['source']),[]).append(v)
        elif tag in ('SD_RELEASE','SD_BUFFER_DESTROY'):
            matches=[v for v in instances if v['create']['node']==r.get('node') and v['create']['source']==r.get('source') and not v['buffer_destroy'] and int(v['create']['ns'])<ns]
            need(matches and r.get('gpu_complete')=='NOT_PROVEN','release observed source interval; GPU not inferred')
            if len(matches)>1:
                # Multiple lingering sidecars share reused node+source labels.
                # Keep raw ambiguity; callback order is no native generation.
                for v in matches:v.setdefault('ambiguous_signals',[]).append(r)
                continue
            matches[0]['releases' if tag=='SD_RELEASE' else 'buffer_destroy'].append(r)
    need(instances,'nonempty native evidence')
    for v in instances:
        if not v['destroy']:continue
        c=v['create'];later=[int(w['create']['ns']) for w in instances if w['create']['node']==c['node'] and int(w['create']['ns'])>int(c['ns'])]
        end=min(later) if later else 2**63
        draws=[r for r in records(text,'OPT_BUFFER_DRAW') if r.get('node')==c['node'] and r.get('buffer')==c['source'] and int(v['destroy']['ns'])<int(r['ns'])<end]
        need(not draws,'native draw after saved-node destruction')
    return instances

def saved_identity(text,owner,creation_after,require_destroy=False):
    instances=lifetime_instances(text)
    selected=[v for v in instances if v['activation'] and v['activation']['owner']==str(owner) and int(v['create']['ns'])>creation_after]
    need(selected and len({v['activation']['line'] for v in selected})==1,'command-associated unique owner activation')
    # WHY CONTRACT INVARIANT: native pointers may recur after destruction.
    # Filter each observed interval, never globally deduplicate its address.
    activation=selected[0]['activation'];start=min(v['create']['line'] for v in selected);end=max((v['destroy']['line'] if v['destroy'] else len(text.splitlines())-1) for v in selected)
    allowed={(v['create']['node'],v['create']['source']) for v in selected}
    subset=[]
    for raw in text.splitlines()[start:end+1]:
        if 'SD_RELEASE ' in raw or 'SD_BUFFER_DESTROY ' in raw:
            f=dict(re.findall(r'(\w+)=([^\s]+)',raw))
            if (f.get('node'),f.get('source')) not in allowed:continue
        subset.append(raw)
    result=_ns['saved_identity']('\n'.join(subset),owner,creation_after,require_destroy)
    result['observed_instances']=selected;result['tree']=activation;return result

def natural_retirement(text,identity,capture_start_ns,cleanup_start_ns,client_alive,wire_before,wire_after,prior):
    need(client_alive and capture_start_ns<cleanup_start_ns,'timeout with live client before teardown')
    held_configure(wire_before,wire_after,prior)
    lines=text.splitlines();tree=identity['tree'];activation=lines.index(tree['raw'])
    timeouts=[i for i,l in enumerate(lines) if i>activation and re.search(r'Transaction .*timed out \(\d*[1-9]\d* waiting\)',l)]
    need(len(timeouts)==1,'unique native timeout after activation')
    removes=[r for r in records(text,'SD_REMOVE') if r.get('tree')==tree['tree'] and int(r['ns'])>int(tree['ns'])]
    need(len(removes)==1,'exact target natural removal');remove=removes[0]
    need(remove.get('owner')==tree['owner'] and remove.get('content')==tree['content'] and timeouts[0]<lines.index(remove['raw']) and int(remove['ns'])<capture_start_ns<cleanup_start_ns,'removal causal owner/content/window')
    dead=[]
    for v in identity['observed_instances']:
        d=v['destroy'];need(d is not None and int(remove['ns'])<=int(d['ns'])<capture_start_ns and lines.index(remove['raw'])<lines.index(d['raw']),'instance destroyed after natural removal before capture')
        dead.append(d)
    return dict(timeout_raw=lines[timeouts[0]],timeout_line=timeouts[0],remove=remove,nodes=dead,before_ns=capture_start_ns,gpu_completion='NOT PROVEN')

def rgb_exact(a,b):
    need(a.mode==b.mode=='RGB' and a.size==b.size,'whole RGB contract')
    need(ImageChops.difference(a,b).getbbox() is None,'whole RGB equal; no masked channel/ROI');return True

def timeout_line(text,activation_line,client_alive,request_ns,observed_ns,cleanup_ns):
    need(client_alive and request_ns+4_700_000_000<=observed_ns<cleanup_ns,'natural timeout window/client alive')
    matches=[(i,l) for i,l in enumerate(text.splitlines()) if i>activation_line and re.search(r'Transaction .*timed out \(\d*[1-9]\d* waiting\)',l)]
    need(len(matches)==1,'native natural timeout required');return matches[0]
