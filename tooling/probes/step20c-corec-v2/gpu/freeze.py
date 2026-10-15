"""Freeze new G2 source-only bytes and delta. Never accepts its own review."""
import ctypes,difflib,hashlib,json,resource
from pathlib import Path
resource.setrlimit(resource.RLIMIT_CORE,(0,0));assert ctypes.CDLL(None).prctl(4,0,0,0,0)==0
ROOT=Path('/var/tmp/swayfx-mosaic-corec-v2-i516p6po');KIT=Path(__file__).resolve().parent
PARENT=ROOT/'sources/scene-core';TARGET=ROOT/'sources/scene-gpu'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(p):return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file() and '.git' not in f.relative_to(p).parts}
changed=['render/fx_renderer/fx_pass.c','render/fx_renderer/g2_gl.h','render/fx_renderer/g2_native.h']
assert sha(PARENT/changed[0])=='398d594ace7257f4b69319290be7c1f14dc1ded446545ceb337404f5caab0cd3'
assert sha(Path('/usr/include/libdrm/drm_fourcc.h'))=='992f33804acda60b0b46f1a272942c3592484ea3217d469239f1cb12249de2eb'
for f in changed[1:]:assert sha(KIT/Path(f).name)==sha(TARGET/f)
pmap,tmap=tree(PARENT),tree(TARGET)
assert {name for name in pmap.keys()|tmap.keys() if pmap.get(name)!=tmap.get(name)}==set(changed)
assert tree(ROOT/'sources/mosaic-core')==tree(ROOT/'sources/mosaic-gpu')
patch=''
for f in changed:
 old=(PARENT/f).read_text().splitlines(True) if (PARENT/f).exists() else []
 patch+=''.join(difflib.unified_diff(old,(TARGET/f).read_text().splitlines(True),fromfile='a/'+f if old else '/dev/null',tofile='b/'+f))
assert not any(line[1:].rstrip('\n').endswith((' ','\t')) for line in patch.splitlines(True) if line.startswith('+') and not line.startswith('+++'))
(KIT/'g2-native.patch').write_text(patch)
files={}
for f in sorted(KIT.rglob('*')):
 if f.is_file():files[str(f.relative_to(ROOT))]={'sha256':sha(f),'bytes':f.stat().st_size}
for f in changed:files['sources/scene-gpu/'+f]={'sha256':sha(TARGET/f),'bytes':(TARGET/f).stat().st_size}
for f in ['render/fx_renderer/shaders/blur1.frag','render/fx_renderer/shaders/blur2.frag']:
 assert sha(PARENT/f)==sha(TARGET/f)
 files['sources/scene-gpu/'+f]={'sha256':sha(TARGET/f),'bytes':(TARGET/f).stat().st_size,'unchanged':True}
tests=json.loads((ROOT/'gpu-fifo-fix/gpu-targeted-tests-corrected.json').read_text());assert tests['pass']
repo=Path('/home/fy59/Documents/Development/swayfx-mosaic')
historical=['tooling/probes/step20c-core-recovery/gpu-field/validate.py','tooling/probes/step20c-core-recovery/gpu-field/analysis.py','tooling/probes/step20c-optimized-blur-edge/clients.c']
m={'schema':'G2-new-source-freeze-v1','status':'EXPERIMENTAL_SOURCE_ONLY','review':'PENDING_INDEPENDENT_R_GPU','runtime':'NOT_RUN','actual_gl_observability':'NOT_PROVEN','port':'PARTIAL: GLES3 RBO only; GLES2/texture attachments refused','metadata_offline':'PASS_CONTROLLED_ONLY','whole_field_causality':'NOT_PROVEN','present_buffer':'NOT_PROVEN','gpu_completion':'NOT_PROVEN','pair3_build':'NOT_RUN','new_gpu_acquisitions':0,'parent_scene_base':'37ccd723bef49e6891156ffafce8f549f01446cc + accepted CORE','parent_fx_pass_sha256':sha(PARENT/changed[0]),'parent_scene_tree':hashlib.sha256(json.dumps(pmap,sort_keys=True).encode()).hexdigest(),'target_scene_tree':hashlib.sha256(json.dumps(tmap,sort_keys=True).encode()).hexdigest(),'mosaic_unchanged_tree':hashlib.sha256(json.dumps(tree(ROOT/'sources/mosaic-core'),sort_keys=True).encode()).hexdigest(),'drm_header':{'path':'/usr/include/libdrm/drm_fourcc.h','sha256':sha(Path('/usr/include/libdrm/drm_fourcc.h'))},'historical_controls':{'status':'HISTORICAL_REPORTED_ONLY','sources':{f:sha(repo/f) for f in historical}},'raw_plan':{'epochs':3,'points_per_epoch':10,'physical_dimensions':[800,600],'bytes':57600000,'cap':268435456},'capture_plan':{'H2_baseline':2,'H1_H2_epoch_pairs':3,'total':8,'G2_cap':16},'test_receipt':{'path':'gpu-fifo-fix/gpu-targeted-tests-corrected.json','sha256':sha(ROOT/'gpu-fifo-fix/gpu-targeted-tests-corrected.json')},'files':files}
(ROOT/'results/gpu-source-freeze-corrected.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps({'status':m['status'],'review':m['review'],'files':len(files),'freeze_sha256':sha(ROOT/'results/gpu-source-freeze-corrected.json')},indent=2))
