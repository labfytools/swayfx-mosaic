#!/usr/bin/env python3
"""Single ELF audit and justified notice stage; never launches compositor code.

WHY: loader resolution, interposition and notice closure are separate gates.
CONTRACT: only SceneFX is archived; system wlroots remains a shared provider.
INVARIANT: each notice is verbatim, attributed and traced to a compiled input.
"""
import argparse
import json
from pathlib import Path
import re
import stat
from support import command,reserve,save,sha

p=argparse.ArgumentParser();p.add_argument('lab',type=Path);a=p.parse_args();lab=a.lab.resolve()
binary=lab/'stage-static/usr/bin/swayfx-mosaic';reserve(lab,'elf')
raw={}
for label,argv in [('elf-header',['readelf','-hW']),('elf-dynamic',['readelf','-dW']),('elf-symbols',['readelf','-Ws']),('elf-relocations',['readelf','-rW']),('elf-versions',['readelf','-VW']),('elf-notes',['readelf','-nW']),('elf-nm',['nm','--format=posix']),('elf-objdump',['objdump','-d']),('elf-ldd',['ldd','-r'])]:
    raw[label]=command(lab,label,[*argv,binary],timeout=60)
assert 'libscenefx' not in raw['elf-dynamic'] and 'libscenefx' not in raw['elf-ldd']
assert 'undefined symbol:' not in raw['elf-ldd'] and 'not found' not in raw['elf-ldd']
assert 'libwlroots-0.20.so' in raw['elf-dynamic']
assert '(RPATH)' not in raw['elf-dynamic'] and '(RUNPATH)' not in raw['elf-dynamic']
clips=['wlr_scene_tree_set_clip','wlr_scene_tree_get_clip']
for name in clips:
    assert re.search(r'^'+name+r' T ',raw['elf-nm'],re.M)
    assert re.search(r'call\s+[^\n]*<'+name+r'>',raw['elf-objdump']), 'static call site absent'
needed=re.findall(r'\(NEEDED\).*\[([^]]+)\]',raw['elf-dynamic'])
wl=Path('/usr/lib/libwlroots-0.20.so').resolve()
wl_header=command(lab,'wlroots-elf',['readelf','-nW','-dW','-VW',wl],timeout=60)
save(lab,'binary-elf',{'status':'PASS','path':str(binary),'sha256':sha(binary),'bytes':binary.stat().st_size,'DT_NEEDED':needed,'RPATH':[],'RUNPATH':[],'build_id':re.findall(r'Build ID: (\w+)',raw['elf-notes']),'header':raw['elf-header'],'versions_file':'raw/elf-versions.log'})
save(lab,'static-symbols',{'status':'PASS','clips':clips,'definitions':'ordinary T executable symbols','call_sites':'raw/elf-objdump.log','semantic_ABI':'not established by ELF'})
# Glibc diagnostic mode exits before the compositor entry point; no run debit.
bindings=command(lab,'loader-bindings',['ldd','-r',binary],extra={'LD_DEBUG':'bindings'},timeout=60)
records=[]
for line in bindings.splitlines():
    m=re.search(r"binding file (.*?) \[0\] to (.*?) \[0\].*symbol `([^']+)'",line)
    if m and 'libwlroots' in m[1] and m[3].startswith('wlr_scene_'):
        rec={'consumer':m[1],'provider':m[2],'symbol':m[3]}
        if rec not in records:records.append(rec)
save(lab,'dependency-resolution',{'status':'PASS','ldd_exit':0,'records':records,'executable_scene_bindings':sum(x['provider']==str(binary) for x in records),'wlroots_scene_bindings':sum('libwlroots' in x['provider'] for x in records),'runtime_identity':'must still be checked from /proc maps'})
headers=[]
for path in (lab/'wlroots-source/include').rglob('*.h'):
    rel=path.relative_to(lab/'wlroots-source/include');installed=Path('/usr/include/wlroots-0.20')/rel
    if installed.is_file():headers.append({'path':str(rel),'source_sha256':sha(path),'installed_sha256':sha(installed),'match':sha(path)==sha(installed)})
assert headers and all(x['match'] for x in headers)
metadata=list(Path('/var/lib/pacman/local').glob('wlroots0.20-*/desc'))
save(lab,'wlroots-qualified-pair',{'SceneFX':'37ccd723bef49e6891156ffafce8f549f01446cc','wlroots_source':'d783533489e1f75d6886c2ab5c5960090ef268f8','wlroots_pkg_config':command(lab,'wlroots-pkg-config',['pkg-config','--modversion','--cflags','--libs','wlroots-0.20']),'library':str(wl),'sha256':sha(wl),'build_id':re.findall(r'Build ID: (\w+)',wl_header),'package_metadata':[{'path':str(x),'text':x.read_text()} for x in metadata],'headers':headers,'features_header':Path('/usr/include/wlroots-0.20/wlr/config.h').read_text(),'struct_layouts':'retained historical 17 structs/6 offsets only; no old ABI probe rerun','other_pairs':'NOT QUALIFIED'})
# Compile inputs conservatively cover all SceneFX archive members. Some unused
# members may be over-included; no dynamic system-library license dump is used.
inputs=[];notice_records=[];payloads={}
for tree in ('mosaic','scene'):
    build=lab/(tree+'-build');commands=json.loads((build/'compile_commands.json').read_text())
    for rec in commands:
        src=(build/rec['file']).resolve()
        if not src.is_file():continue
        inputs.append({'source':str(src),'sha256':sha(src),'object':rec.get('output'),'component':tree,'command':rec['command']})
        text=src.read_text(errors='strict')
        comments=[c for c in re.findall(r'/\*.*?\*/',text,re.S) if re.search(r'copyright|permission|redistribution|SPDX',c,re.I)]
        for comment in comments:
            # SPDX alone names a license; root license text is staged separately.
            if not re.search(r'copyright|permission|redistribution',comment,re.I):continue
            key=__import__('hashlib').sha256(comment.encode()).hexdigest()
            payloads.setdefault(key,comment)
            notice_records.append({'source':str(src),'source_sha256':sha(src),'notice_sha256':key,'component':tree,'generated':src.is_relative_to(build)})
roots=[('SwayFX','swayfx-source/LICENSE'),('SceneFX','scene-source/LICENSE'),('wlroots','wlroots-source/LICENSE')]
root_records=[]
for name,rel in roots:
    src=lab/rel;root_records.append({'component':name,'source':str(src),'sha256':sha(src),'destination':f'/usr/share/licenses/swayfx-mosaic/{name}-LICENSE','reason':'compositor code' if name=='SwayFX' else 'static scene/renderer archive including copied wlroots code' if name=='SceneFX' else 'copied scene/renderer code within SceneFX; system wlroots stays dynamic'})
assert notice_records and any(x['generated'] for x in notice_records)
reserve(lab,'notices');dest=lab/'stage-static/usr/share/licenses/swayfx-mosaic';dest.mkdir(parents=True)
for row in root_records:
    path=lab/'stage-static'/row['destination'].lstrip('/');path.write_bytes(Path(row['source']).read_bytes());path.chmod(0o644)
# Each full comment is retained once with all provenance paths, including
# generated protocol supporting-documentation and attribution clauses.
notice_path=dest/'INCORPORATED-NOTICES'
blocks=[]
for key,text in payloads.items():
    sources=[r['source'] for r in notice_records if r['notice_sha256']==key]
    blocks.append('Sources:\n'+'\n'.join(sources)+'\n\n'+text)
notice_path.write_text('\n\n'.join(blocks)+'\n');notice_path.chmod(0o644)
save(lab,'license-inventory',{'status':'PARTIAL DISTRIBUTION QUALIFICATION; compiled/root/generated notices inventoried; legal/header/shader/exact extraction closure remains open','roots':root_records,'compiled_inputs':inputs,'source_notices':notice_records,'extra_archive_members':'conservative coverage of archive compile inputs; exact extraction of every unused member not claimed','dynamic_libraries':'not indiscriminately copied','notice_destination':'/usr/share/licenses/swayfx-mosaic/INCORPORATED-NOTICES'})
save(lab,'license-files',[{'path':str(x.relative_to(lab/'stage-static')),'sha256':sha(x),'bytes':x.stat().st_size} for x in sorted(dest.iterdir())])
# Compiled source provenance verifies actual config paths as well as Meson opts.
config=(lab/'mosaic-build/include/config.h').read_text();(lab/'raw/compiled-config.h').write_text(config)
compiled=(lab/'mosaic-build/compile_commands.json').read_text()
assert '/usr/local' not in compiled and 'SYSCONFDIR' in compiled
save(lab,'compiled-paths',{'prefix':'/usr','bindir':'bin','sysconfdir':'/etc (compiler spelling //etc)','source':'Meson build options, intro-installed.json and compile_commands.json'})
print('PASS ELF, clip definitions/calls, relocations, header identity, notices; bindings',len(records))
