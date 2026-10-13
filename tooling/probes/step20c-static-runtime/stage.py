#!/usr/bin/env python3
"""Read-only stage verification; notices are added only by the one-shot audit.

CONTRACT: regular binary plus exactly inventoried regular notice files only.
INVARIANT: links, devices, libraries, configs and unlisted files are rejected.
"""
import argparse
import json
from pathlib import Path
import stat
from support import save,sha
p=argparse.ArgumentParser();p.add_argument('lab',type=Path);a=p.parse_args();lab=a.lab.resolve();stage=lab/'stage-static'
licenses=json.loads((lab/'results/license-files.json').read_text())
allowed={'usr/bin/swayfx-mosaic':sha(lab/'mosaic-build/sway/swayfx-mosaic')}
allowed.update({x['path']:x['sha256'] for x in licenses});entries=[];seen=set()
for path in sorted(stage.rglob('*')):
    s=path.lstat();rel=str(path.relative_to(stage));mode=stat.S_IMODE(s.st_mode)
    if stat.S_ISDIR(s.st_mode):
        assert any(x.startswith(rel+'/') for x in allowed),rel
        assert mode==0o755,(rel,mode)
        continue
    assert stat.S_ISREG(s.st_mode) and rel in allowed,rel
    assert sha(path)==allowed[rel] and mode==(0o755 if rel=='usr/bin/swayfx-mosaic' else 0o644),(rel,mode)
    if rel!='usr/bin/swayfx-mosaic':assert path.read_text().strip()
    seen.add(rel);entries.append({'path':'/'+rel,'type':'regular','mode':oct(mode),'uid':s.st_uid,'gid':s.st_gid,'bytes':s.st_size,'sha256':sha(path),'origin':'meson install' if rel=='usr/bin/swayfx-mosaic' else 'future package simulation'})
assert seen==set(allowed)
options=json.loads((lab/'mosaic-build/meson-info/intro-buildoptions.json').read_text());values={x['name']:x['value'] for x in options}
assert values['prefix']=='/usr' and values['bindir']=='bin'
compiled=(lab/'mosaic-build/compile_commands.json').read_text();assert '/usr/local' not in compiled
save(lab,'compiled-paths',{'prefix':values['prefix'],'bindir':values['bindir'],'sysconfdir':values['sysconfdir'],'compiler_definition':'SYSCONFDIR=//etc; canonical /etc','compiled_command_provenance':'mosaic-build/compile_commands.json'})
save(lab,'static-stage-manifest',{'status':'PASS','marker':'STATIC_STAGE_WITH_LICENSES=PASS','files':entries,'installation':'private user-owned DESTDIR; no package installed'})
print('STATIC_STAGE_WITH_LICENSES=PASS',len(entries),'regular files')
