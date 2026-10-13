#!/usr/bin/env python3
"""Read-only ELF/header/package audit of prepared trusted private artifacts.

WHY: record missing relocations, symbol overlap and header provenance separately.
CONTRACT: no compositor entry point executes; loader commands only inspect ELF.
INVARIANT: results may be derived again before sealing, never after sealing.
"""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('lab', type=Path)
a = p.parse_args(); lab = a.lab.resolve(); repo = Path(__file__).resolve().parents[3]
assert lab.is_dir() and lab.is_relative_to(Path.home()) and lab != Path.home()
assert not lab.is_relative_to(repo)
assert not (lab/'results/evidence-sha256.txt').exists(), 'sealed evidence; verify, never rewrite'
results = lab/'results'; raw = lab/'raw'
env = {k: v for k, v in os.environ.items() if k not in (
    'SWAYSOCK', 'I3SOCK', 'WAYLAND_DISPLAY', 'DISPLAY', 'XDG_RUNTIME_DIR',
    'LD_LIBRARY_PATH', 'LD_PRELOAD', 'PKG_CONFIG_PATH')}
env['LC_ALL'] = 'C'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name, value): (results/(name+'.json')).write_text(json.dumps(value, indent=2)+'\n')
def run(label, args, extra=None):
    proc = subprocess.run(list(map(str, args)), env={**env, **(extra or {})},
                          capture_output=True, text=True, timeout=60)
    entry = {'args': list(map(str, args)), 'env_override': extra or {},
             'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}
    (raw/(label+'.json')).write_text(json.dumps(entry, indent=2)+'\n')
    return entry

def elf(label, path):
    path = path.resolve(); parts = {}
    assert path.stat().st_size <= 128*1024*1024, 'ELF input exceeds audit bound'
    for tag, args in [('header', ['readelf','-hW']), ('dynamic',['readelf','-dW']),
                      ('symbols',['readelf','--dyn-syms','-W']), ('versions',['readelf','-VW']),
                      ('nm',['nm','-D','--format=posix']), ('nm-all',['nm','--format=posix']), ('objdump',['objdump','-p'])]:
        parts[tag] = run(label+'-'+tag, [*args, path])
        assert parts[tag]['returncode']==0, (label,tag)
    defs = []; undefs = []; weak = []
    for line in parts['symbols']['stdout'].splitlines():
        fields = line.split()
        if len(fields) >= 8 and fields[0].rstrip(':').isdigit():
            name = fields[7]; base = name.split('@')[0]
            if fields[6]=='UND':
                (weak if fields[4]=='WEAK' else undefs).append(base)
            elif fields[4] in ('GLOBAL','WEAK'): defs.append(base)
    d = parts['dynamic']['stdout']
    result = {'path':str(path), 'sha256':sha(path), 'bytes':path.stat().st_size,
              'class':re.search(r'Class:\s+(.*)',parts['header']['stdout'])[1],
              'machine':re.search(r'Machine:\s+(.*)',parts['header']['stdout'])[1],
              'SONAME':re.findall(r'\(SONAME\).*?\[(.*?)\]',d),
              'DT_NEEDED':re.findall(r'\(NEEDED\).*?\[(.*?)\]',d),
              'RPATH':re.findall(r'\(RPATH\).*?\[(.*?)\]',d),
              'RUNPATH':re.findall(r'\(RUNPATH\).*?\[(.*?)\]',d),
              'defined':sorted(set(defs)), 'undefined':sorted(set(undefs)),
              'weak_undefined':sorted(set(weak)),
              'clip_defined':[x for x in defs if x in clips],
              'clip_undefined':[x for x in undefs if x in clips]}
    save(label,result);return result
clips = ['wlr_scene_tree_set_clip','wlr_scene_tree_get_clip']
versions = {}
for pkg in ['scenefx-0.5','wlroots-0.20','wayland-server','libdrm','pixman-1']:
    versions[pkg] = {op:run('pkg-'+pkg+'-'+op,['pkg-config','--'+op,pkg])['stdout'].strip()
                     for op in ('modversion','cflags','libs')}
for pkg in ['scenefx-0.5','wlroots-0.20']:
    path=Path('/usr/lib/pkgconfig')/(pkg+'.pc');sh=(raw/(pkg+'.pc'));sh.write_bytes(path.read_bytes())
features = {name:run('feature-'+name,['pkg-config','--variable=have_'+name,'wlroots-0.20'])['stdout'].strip()
            for name in ['drm_backend','x11_backend','libinput_backend','xwayland',
                         'gles2_renderer','vulkan_renderer','gbm_allocator','udmabuf_allocator','session','color_management']}
save('dependency-versions',{'packages':versions,'wlroots_features':features})
# Metadata is evaluated in a non-installing shell: functions are defined but not called.
meta = run('pkgbuild-metadata',['bash','-c','startdir=$2; source "$1"; declare -p pkgname pkgver pkgrel arch license depends makedepends checkdepends source sha256sums _upstream_commit; declare -p conflicts provides replaces 2>/dev/null || true','audit',repo/'PKGBUILD',repo])
assert meta['returncode']==0
save('pkgbuild-metadata',meta)
pkgtext=(repo/'PKGBUILD').read_text()
expected=re.findall(r"'([a-f0-9]{64})'",pkgtext)
paths=[repo/'patches/0001-mosaic-layout-viewport.patch',repo/'tests/headless-ipc.py']
checks=[{'path':str(path),'expected':exp,'actual':sha(path),'PASS':sha(path)==exp} for path,exp in zip(paths,expected)]
assert len(checks)==2 and all(x['PASS'] for x in checks)
save('package-source-checksums',checks)
assert not re.search(r'^\s*(conflicts|provides|replaces)=',pkgtext,re.M)
save('package-contract',{'authority':'docs/PACKAGING.md','expected':['/usr/bin/swayfx-mosaic'],
                        'conflicts_provides_replaces':False,'stock_scene_dependency':True,'STEP20C':False})
stage=lab/'stage-current'
entries=[]
for path in sorted(stage.rglob('*')):
    if path.is_symlink() or not path.is_dir():
        entries.append({'path':'/'+str(path.relative_to(stage)), 'symlink':path.is_symlink(),
                        'executable':os.access(path,os.X_OK),'sha256':sha(path) if path.is_file() else None})
assert len(entries)==1 and entries[0]['path']=='/usr/bin/swayfx-mosaic' and not entries[0]['symlink'] and entries[0]['executable']
save('stock-stage-manifest',{'status':'CURRENT_PACKAGE_STAGE_PASS','entries':entries})
paths={'system-scenefx-symbols':Path('/usr/lib/libscenefx-0.5.so'),
       'system-wlroots-elf':Path('/usr/lib/libwlroots-0.20.so'),
       'pristine-scenefx-symbols':lab/'scene-pristine-build/libscenefx-0.5.so',
       'private-scenefx-symbols':lab/'scene-private-build/libscenefx-0.5.so',
       'stock-binary-elf':stage/'usr/bin/swayfx-mosaic',
       'experimental-binary-elf':lab/'private-build/sway/swayfx-mosaic'}
if (lab/'retained-pristine-sway').exists():paths['pristine-sway-elf']=lab/'retained-pristine-sway'
if (lab/'static-build/sway/swayfx-mosaic').exists():paths['static-binary-elf']=lab/'static-build/sway/swayfx-mosaic'
elves={label:elf(label,path) for label,path in paths.items()}
stockdefs=set(elves['system-scenefx-symbols']['defined']);privdefs=set(elves['private-scenefx-symbols']['defined'])
wlrootsdefs=set(elves['system-wlroots-elf']['defined'])
save('symbol-comparison',{'private_added':sorted(privdefs-stockdefs),'private_removed':sorted(stockdefs-privdefs),
                         'scene_wlroots_overlap':sorted(privdefs & wlrootsdefs),
                         'pristine_system_added':sorted(set(elves['pristine-scenefx-symbols']['defined'])-stockdefs),
                         'pristine_system_removed':sorted(stockdefs-set(elves['pristine-scenefx-symbols']['defined']))})
assert set(clips)<=privdefs and not set(clips)&stockdefs
assert set(clips)<=set(elves['experimental-binary-elf']['undefined'])
save('unresolved-symbols',{'stock_missing':clips,'experimental_requires':clips,'classification':'INCOMPATIBLE_WITH_STOCK_SCENEFX'})
# ld-linux --list never enters the application. Stock --library-path overrides
# DT_RUNPATH on this artifact; verify the selected absolute library in raw output.
loader='/usr/lib/ld-linux-x86-64.so.2';loads={}
for label,path in [('stock',paths['stock-binary-elf']),('private',paths['experimental-binary-elf'])]:
    loads[label+'-default']=run('loader-'+label+'-default',[loader,'--list',path])
for label,directory in [('private',lab/'scene-private-build'),('stock',Path('/usr/lib'))]:
    loads['experimental-'+label]=run('loader-experimental-'+label,[loader,'--library-path',directory,'--list',paths['experimental-binary-elf']])
    loads['relocations-'+label]=run('relocations-'+label,['ldd','-r',paths['experimental-binary-elf']],{'LD_LIBRARY_PATH':str(directory)})
loads['stock-bindings']=run('stock-bindings',['ldd','-r',paths['stock-binary-elf']],{'LD_DEBUG':'bindings'})
loads['stock-relocations']=run('stock-relocations',['ldd','-r',paths['stock-binary-elf']])
if 'static-binary-elf' in paths:
    loads['static-default']=run('loader-static-default',[loader,'--list',paths['static-binary-elf']])
    loads['static-relocations']=run('static-relocations',['ldd','-r',paths['static-binary-elf']])
assert '/usr/lib/libscenefx-0.5.so' in loads['experimental-stock']['stdout']
assert all('undefined symbol: '+c in loads['relocations-stock']['stdout'] for c in clips)
assert 'undefined symbol:' not in loads['relocations-private']['stdout']
assert 'undefined symbol:' not in loads['stock-relocations']['stdout']
if 'static-relocations' in loads: assert 'undefined symbol:' not in loads['static-relocations']['stdout']
if 'static-binary-elf' in paths:
    loads['static-bindings']=run('static-bindings',['ldd','-r',paths['static-binary-elf']],{'LD_DEBUG':'bindings'})
loads['private-bindings']=run('private-bindings',['ldd','-r',paths['experimental-binary-elf']],{'LD_DEBUG':'bindings','LD_LIBRARY_PATH':str(lab/'scene-private-build')})
run('installed-package-metadata',['pacman','-Qi','scenefx','wlroots0.20','swayfx'])
save('loader-resolution',loads)
bindings={}
for name in ['stock-bindings','private-bindings','static-bindings']:
    if name in loads:
        lines=[line.strip() for line in loads[name]['stdout'].splitlines()
               if 'binding file /usr/lib/libwlroots' in line and 'wlr_scene_' in line]
        bindings[name]={'total':len(lines),
                        'external_provider':sum(' to /usr/lib/libwlroots' not in line for line in lines),
                        'self_wlroots':sum(' to /usr/lib/libwlroots' in line for line in lines),
                        'lines':lines}
save('scene-symbol-bindings',bindings)
# All installed public headers are compared; generated config headers are reported
# separately rather than mistaken for source changes.
stockheaders=Path('/usr/include/scenefx-0.5/scenefx')
headeraudit=[]
for installed in sorted(stockheaders.rglob('*.h')):
    rel=installed.relative_to(stockheaders);pristine=lab/'scene-pristine/include/scenefx'/rel;private=lab/'scene-private/include/scenefx'/rel
    if not pristine.exists():
        headeraudit.append({'path':str(rel),'generated_or_missing_source':True,'installed_sha256':sha(installed)});continue
    diff=''.join(difflib.unified_diff(pristine.read_text().splitlines(True),private.read_text().splitlines(True),fromfile='pristine/'+str(rel),tofile='private/'+str(rel)))
    headeraudit.append({'path':str(rel),'system_pristine_equal':installed.read_bytes()==pristine.read_bytes(),
                        'pristine_private_equal':pristine.read_bytes()==private.read_bytes(),'diff':diff,
                        'sha256':{'installed':sha(installed),'pristine':sha(pristine),'private':sha(private)}})
save('public-header-diff',headeraudit)
# Compile tiny C17 layout observers, not scene/compositor instances. Size/offset
# equality is a measured necessary condition, never a full ABI guarantee.
structs=['wlr_scene_node','wlr_scene_tree','wlr_scene','wlr_scene_surface','wlr_scene_rect','wlr_scene_shadow','wlr_scene_blur','wlr_scene_optimized_blur','wlr_scene_buffer','wlr_scene_output','wlr_scene_timer','wlr_scene_layer_surface_v1','wlr_output','wlr_output_state','wlr_surface','wlr_buffer','wlr_renderer']
source='#define WLR_USE_UNSTABLE\n#include <stddef.h>\n#include <stdio.h>\n#include <scenefx/types/wlr_scene.h>\n#include <wlr/types/wlr_output.h>\n#include <wlr/types/wlr_compositor.h>\n#include <wlr/types/wlr_buffer.h>\n#include <wlr/version.h>\nint main(void) {\nprintf("wlroots_runtime %d.%d.%d\\n",wlr_version_get_major(),wlr_version_get_minor(),wlr_version_get_micro());\n'
for struct in structs:source+=f'printf("{struct} %zu %zu\\n", sizeof(struct {struct}), _Alignof(struct {struct}));\n'
for struct,field in [('wlr_scene_tree','children'),('wlr_scene','tree'),('wlr_scene','outputs'),('wlr_scene_node','parent'),('wlr_scene_buffer','buffer'),('wlr_scene_output','output')]:
    source+=f'printf("offset:{struct}.{field} %zu\\n", offsetof(struct {struct},{field}));\n'
source+='return 0; }\n'; (lab/'struct-layout.c').write_text(source)
flags=shlex.split(run('layout-pkg-cflags',['pkg-config','--cflags','wlroots-0.20','wayland-server','pixman-1'])['stdout'])
layouts={}
for name,inc in [('system',Path('/usr/include/scenefx-0.5')),('pristine',lab/'scene-pristine/include'),('private',lab/'scene-private/include')]:
    exe=lab/('layout-'+name)
    build=run('layout-compile-'+name,['cc','-std=c17','-Wall','-Wextra','-Werror','-I'+str(inc),*flags,lab/'struct-layout.c','-o',exe,'-lwlroots-0.20'])
    assert build['returncode']==0,build['stderr']
    layouts[name]=run('layout-run-'+name,[exe])['stdout']
assert len(set(layouts.values()))==1
save('struct-abi-audit',{'layouts':layouts,'size_alignment_offsets':'IDENTICAL in 17 structs / 6 offsets',
                        'complete_ABI':'NOT ESTABLISHED; layout equality alone insufficient',
                        'private_storage':'destroy-listener-owned sidecar; no public field additions'})
wlheaders=[]
for src in sorted((lab/'wlroots-source/include/wlr').rglob('*.h')):
    rel=src.relative_to(lab/'wlroots-source/include/wlr');installed=Path('/usr/include/wlroots-0.20/wlr')/rel
    wlheaders.append({'path':str(rel),'installed':installed.exists(),'equal':installed.exists() and src.read_bytes()==installed.read_bytes(), 'source_sha256':sha(src),'installed_sha256':sha(installed) if installed.exists() else None})
required={label:sorted(set(info['undefined']) & wlrootsdefs) for label,info in elves.items() if label!='system-wlroots-elf'}
save('wlroots-compatibility',{'pkg_config':'wlroots-0.20','version':'0.20.2','source_pin':'d783533489e1f75d6886c2ab5c5960090ef268f8','headers':wlheaders,'required_symbols_provided_by_installed_wlroots':required,'exact_installed_binary_source_provenance':'NOT ESTABLISHED by version/headers alone','future_0_20_ABI':'NOT ESTABLISHED'})
# Compiler dependency files contain headers actually read, not inferred flags.
for build in ['stock-build','private-build','static-build','scene-private-build']:
    if (lab/build).exists():run('compiler-headers-'+build,['ninja','-C',lab/build,'-t','deps'])
static=elves.get('static-binary-elf')
save('static-link-feasibility',{'status':'BUILD_AND_LOADER_PASS' if static else 'NOT TESTED',
    'scene_DT_NEEDED_absent':static is not None and 'libscenefx-0.5.so' not in static['DT_NEEDED'],
    'wlroots_still_dynamic':static is not None and 'libwlroots-0.20.so' in static['DT_NEEDED'],
    'clip_dynamic_defined':static['clip_defined'] if static else [],
    'clip_static_symbols':[line for line in run('static-clip-symbols',['nm','--format=posix',paths['static-binary-elf']])['stdout'].splitlines() if line.split()[0] in clips] if static else [],
    'overlapping_dynamic_exports':sorted(set(static['defined']) & wlrootsdefs) if static else [],
    'unique_file_possible':'ELF shape demonstrated; no second stage performed',
    'licenses':'MIT notices must accompany substantial copied code; embedded notice strategy NOT TESTED',
    'update_safety':'NOT ESTABLISHED; executable interposes shared wlroots scene symbols'})
save('private-shared-feasibility',{'status':'PROCESS_LOCAL_LOADER_PASS; distinct SONAME packaging NOT TESTED',
    'same_SONAME':'unsafe naive substitution; default build RUNPATH is private LAB, not distributable',
    'future_requirements':['distinct SONAME and DT_NEEDED','private installation path','controlled RUNPATH','audit all transitive scene consumers and interposition','security/version owner'],
    'current_one_file_contract':'would require new decision for additional library artifact'})
print('PASS stock stage, ELF/loader comparisons, missing clip proof, C17 17-struct layouts and header audit')
