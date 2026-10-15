"""Private source-only adapter to the independently reviewed graphics-kit Session.
No native run entry point. O1/O2 remain NOT_ADMITTED until separate review.
"""
import os,re
from pathlib import Path
PLANS={
 'OM-ROOT':dict(status='NOT_ADMITTED',role='root_popup',max_captures=8,max_injections=1,requires_rootA_stable=False),
 'OM-NESTED':dict(status='NOT_ADMITTED',role='nested_popup',max_captures=8,max_injections=1,requires_rootA_stable=True),
}
CAPTURES=('reference-H2-a','reference-H2-b','pre-H1','pre-H2','post-H1','post-H2','final-H1','final-H2')
def process_environment(lab,run,nonce):
    assert run in PLANS and re.fullmatch('[0-9a-f]{32}',nonce)
    lab=Path(lab);assert lab.is_absolute() and lab.resolve()==lab and lab.stat().st_uid==os.getuid()
    # Parent must use this update solely in Session's compositor spawn environment.
    # Do not put it into Session.env inherited by scientific clients/helpers.
    path=lab/'graphics-runs'/run/'run'/'oom-token'
    assert not path.exists() and not path.is_symlink()
    return dict(SMX_OOM_TOKEN_PATH=str(path),SMX_OOM_NONCE=nonce,SMX_OOM_ROLE=PLANS[run]['role'])
def arm(session,env,admission,stable):
    run=session.spec['id'];assert run in PLANS
    # Separate reviewed admission must bind variant binary + OOM source freeze,
    # graphics engine freeze, independent R-OOM, build review and publication.
    assert admission==session.auth['prospective']
    assert admission['decision']=='ACCEPTED' and admission['source_manifest_sha256']==session.auth['manifest_sha256']
    assert admission.get('oom_source_review')=='ACCEPTED' and session.auth['build_review']=='ACCEPTED'
    assert session.auth['publication_sha256'] and admission['variant_identity']=='COREC_V2_NATIVE_OOM_DIAGNOSTIC'
    assert stable['startup'] and stable['owner'] and stable['neighbor'] and stable['reference_H2_twice']
    if PLANS[run]['requires_rootA_stable']:assert stable['rootA'] and stable['rootA_native_success']
    assert env['SMX_OOM_ROLE']==PLANS[run]['role']
    path=Path(env['SMX_OOM_TOKEN_PATH']);assert path.parent.resolve()==session.run.resolve()
    assert path.name=='oom-token' and not path.is_symlink()
    # The parent's reviewed OOM ledger extension must provide hook cap=1. Debit
    # precedes O_EXCL write; failed arm stays spent, with no retry/refund.
    session.debit('hook')
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600)
    try:
        os.fchmod(fd,0o600)
        token=f"SMXOOM1 {env['SMX_OOM_NONCE']} {env['SMX_OOM_ROLE']}\n".encode('ascii')
        assert os.write(fd,token)==len(token);os.fsync(fd)
    finally:os.close(fd)
    session.record('oom-arm',role=env['SMX_OOM_ROLE'],nonce=env['SMX_OOM_NONCE'],path=str(path))
def native_failure(log,env,pid):
    lines=[line for line in log.splitlines() if 'SMX_OOM ENOMEM ' in line]
    assert len(lines)==1
    fields=dict(re.findall(r'([a-z_]+)=([^ ]+)',lines[0]))
    for key,value in dict(role=env['SMX_OOM_ROLE'],nonce=env['SMX_OOM_NONCE'],pid=str(pid),matched='1',failures='1',initialized='0',listeners='0',published='0').items():assert fields.get(key)==value,(key,fields)
    assert all(fields.get(k) not in (None,'(nil)','0x0') for k in ['xdg','xdg_parent','parent','tree'])
    assert fields.get('successes')==('0' if env['SMX_OOM_ROLE']=='root_popup' else '1')
    assert re.fullmatch(r'\d+',fields.get('children',''))
    # WHY: native children counts existing PARENT children, not the failed tree.
    # CONTRACT: preserve it without demanding impossible nested parent_children0.
    # INVARIANT: NULL result must bind same role/PID/xdg/parent, unpublished node.
    results=[line for line in log.splitlines() if 'SMX_OOM result ' in line and 'role='+env['SMX_OOM_ROLE']+' ' in line]
    assert len(results)==1,'unique targeted NULL caller result'
    result=dict(re.findall(r'([a-z_]+)=([^ ]+)',results[0]))
    for key in ('role','pid','xdg','xdg_parent','parent','successes','failures'):assert result.get(key)==fields[key]
    assert result.get('tree') in ('(nil)','0x0'),'failed tree returned non-NULL'
    fields.update(parent_children=fields['children'],children_scope='existing parent children, not failed tree',caller_result=result)
    return fields
