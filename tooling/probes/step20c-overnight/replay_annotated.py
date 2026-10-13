"""WHY: requalify annotated identity without inheriting historical graphics.
CONTRACT: pinned replay gate before reserved one-shot builds.
INVARIANT: historical LAB read only; no semantic source edit or build retry.
"""
import sys, json, hashlib, shutil, subprocess, tarfile, re, time, os, argparse
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('lab',type=Path)
parser.add_argument('--historical',type=Path,required=True)
args=parser.parse_args()
LAB=args.lab.resolve(); D=args.historical.resolve()
REPO=Path(__file__).resolve().parents[3]
assert LAB != D and not LAB.is_relative_to(REPO)
LAB.mkdir(exist_ok=True)
sys.path.insert(0,str(REPO/'tooling/probes/step20c-overnight'))
from ledger import initialize,reserve as debit
for name in ('scripts','raw','results','patches'): (LAB/name).mkdir(exist_ok=True)
initialize(LAB/'budget.json')
for name in ('support.py','audit-d.py','qualify-d.py','stage-d.py'):
    shutil.copy2(D/'scripts'/name,LAB/'scripts'/name)
p=LAB/'scripts/support.py';txt=p.read_text();start=txt.index('def reserve(');end=txt.index('\ndef environment()',start)
txt=txt[:start]+"def reserve(lab, kind):\n    import sys\n    sys.path.insert(0, '"+str(REPO/'tooling/probes/step20c-overnight')+"')\n    from ledger import reserve as debit\n    return debit(Path(lab)/'budget.json', kind)\n"+txt[end:]
# Every command records wall time/date/return code, including failed diagnostics.
txt=txt.replace("lab=Path(lab); path=", "started=time.time(); lab=Path(lab); path=")
txt=txt.replace("'env':extra or {},'exit':proc.returncode", "'env':extra or {},'exit':proc.returncode,'started_unix':started,'duration_s':time.time()-started")
p.write_text(txt)
sys.path.insert(0,str(LAB/'scripts'))
from support import command,save,sha,reserve

def treehash(root):
    entries=[{'path':str(p.relative_to(root)),'sha256':sha(p),'mode':oct(p.stat().st_mode&0o777)} for p in sorted(root.rglob('*')) if p.is_file()]
    return hashlib.sha256(json.dumps(entries,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def tokens(text):
    # Strings/chars are consumed before comment syntax; comments inside literals survive.
    expr=r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*|[A-Za-z_]\w*|(?:\d[\w.]*)|[^\s]'
    return [m.group(0) for m in re.finditer(expr,text,re.S) if not m.group(0).startswith(('/*','//'))]

state={'status':'RUNNING','source_gate':'NOT RUN','graphics':'NOT TESTED','historical':str(D)}
def checkpoint(): (LAB/'phase-a.json').write_text(json.dumps(state,indent=2)+'\n')
try:
    versions=json.loads((D/'results/source-versions.json').read_text())
    components=json.loads((D/'results/component-patches.json').read_text())
    for name in ('mosaic-source','swayfx-source','scene-source','wlroots-source'):
        arc=LAB/(name+'.tar');shutil.copy2(D/(name+'.tar'),arc)
        assert sha(arc)==versions['archives'][arc.name]
        if name in ('mosaic-source','swayfx-source'):
            rev=versions['pins']['Mosaic' if name=='mosaic-source' else 'SwayFX']
            with (LAB/(name+'-git-check.tar')).open('wb') as out:subprocess.run(['git','-C',str(REPO),'archive',rev],stdout=out,check=True)
            assert sha(LAB/(name+'-git-check.tar'))==sha(arc)
        (LAB/name).mkdir()
        with tarfile.open(arc) as tf:tf.extractall(LAB/name,filter='data')
    state['components']=[]
    for item in components['ordered_patches']:
        tree=LAB/item['tree'];src=Path(item['source']);patch=LAB/'patches'/src.name
        assert sha(src)==sha(Path(item['candidate_path']))==item['sha256']
        shutil.copy2(src,patch)
        assert treehash(tree)==item['parent_tree_sha256']
        command(LAB,'replay-'+src.stem+'-check',['git','apply','--check',patch],tree)
        command(LAB,'replay-'+src.stem+'-apply',['git','apply',patch],tree)
        assert treehash(tree)==item['result_tree_sha256']
        state['components'].append({**item,'replayed_path':str(patch),'verified':True})
    for name in ('mosaic-source','scene-source'):
        assert treehash(LAB/name)==treehash(D/name)
    manifest=json.loads((D/'comment-repair/repair-manifest.json').read_text())
    before={row['path']:(LAB/row['path']).read_text() for row in manifest['files']}
    for row in manifest['files']:assert sha(LAB/row['path'])==row['parent_sha256']
    for name,digest in manifest['patches'].items():
        patch=LAB/'patches'/name;shutil.copy2(D/'comment-repair'/name,patch);assert sha(patch)==digest
        command(LAB,'comment-'+name+'-check',['git','apply','--check',patch],LAB)
        command(LAB,'comment-'+name+'-apply',['git','apply',patch],LAB)
    for row in manifest['files']:
        assert sha(LAB/row['path'])==row['result_sha256']
        assert tokens(before[row['path']])==tokens((LAB/row['path']).read_text())
    state.update(source_gate='PASS',comments=manifest,source_trees={name:treehash(LAB/name) for name in ('scene-source','mosaic-source')})
    assert sha(Path('/usr/lib/libwlroots-0.20.so').resolve())=='7edca9a7d65855addda68e29ba5db94d57c803eb5fa7d0f86db3136b90ca9837'
    save(LAB,'source-versions',versions);checkpoint();print('SOURCE_GATE_PASS',flush=True)
    command(LAB,'compiler',['cc','--version']);command(LAB,'meson-version',['meson','--version'])
    command(LAB,'dependencies',['pkg-config','--modversion','wlroots-0.20','scenefx-0.5','wayland-server','wayland-client','wayland-protocols','libdrm','xkbcommon','pixman-1'])
    reserve(LAB,'scene_build')
    command(LAB,'scene-setup',['meson','setup',LAB/'scene-build',LAB/'scene-source','--prefix=/usr','-Ddefault_library=static','-Dexamples=false','-Dwerror=false'])
    command(LAB,'scene-build',['meson','compile','-C',LAB/'scene-build','-j','8'])
    reserve(LAB,'mosaic_build')
    extra={'PKG_CONFIG_PATH':str(LAB/'scene-build/meson-uninstalled')}
    flags=['--prefix=/usr','--bindir=bin','-Dwerror=false','-Dsd-bus-provider=libsystemd','-Dmosaic-package=true','-Dswaybar=false','-Dswaynag=false','-Dman-pages=disabled','-Ddefault-wallpaper=false']
    command(LAB,'mosaic-setup',['meson','setup',LAB/'mosaic-build',LAB/'mosaic-source',*flags],extra=extra)
    command(LAB,'mosaic-build',['meson','compile','-C',LAB/'mosaic-build','-j','8'],extra=extra)
    state['builds']='PASS';checkpoint();print('BUILDS_PASS',flush=True)
    command(LAB,'mosaic-model',['meson','test','-C',LAB/'mosaic-build','--no-rebuild','mosaic-model','--print-errorlogs'])
    save(LAB,'static-build',{'status':'PASS','flags':flags,'options':json.loads((LAB/'mosaic-build/meson-info/intro-buildoptions.json').read_text()),'archive_sha256':sha(LAB/'scene-build/libscenefx-0.5.a'),'binary_sha256':sha(LAB/'mosaic-build/sway/swayfx-mosaic')})
    reserve(LAB,'stage')
    command(LAB,'meson-stage',['meson','install','-C',LAB/'mosaic-build','--no-rebuild','--destdir',LAB/'stage-static'])
    for script,args in [('audit-d.py',[LAB]),('qualify-d.py',[]),('stage-d.py',[LAB])]:
        command(LAB,script,['python',LAB/'scripts'/script,*args],timeout=600)
    state['binary']=json.loads((LAB/'results/binary-elf.json').read_text())
    state['stage']=json.loads((LAB/'results/static-stage-manifest.json').read_text())
    state['ABI']='PASS local layout/headers/85-symbol characterization; semantic maintenance NOT ESTABLISHED'
    state['status']='PASS'
except Exception as exc:
    state['status']='FAIL';state['error']=repr(exc);raise
finally:
    state['budget']=json.loads((LAB/'budget.json').read_text());checkpoint()
