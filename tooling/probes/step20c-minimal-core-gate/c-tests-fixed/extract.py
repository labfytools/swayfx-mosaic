#!/usr/bin/env python3
"""WHY: exercise exact core C rather than an algorithmic rewrite.
CONTRACT: inputs are read-only; every extracted byte range is independently bound.
INVARIANT: generated function bodies are identical to their source slices.
"""
from pathlib import Path
import hashlib, json, re
LAB=Path(__file__).resolve().parent.parent
OUT=LAB/'c-tests-fixed'
bindings=[]
def capture(path,name):
    raw=(LAB/path).read_bytes()
    pattern=rb'^(?:static )?(?:bool|int) '+name.encode()+rb'\('
    found=list(re.finditer(pattern,raw,re.M))
    assert len(found)==1,(path,name,len(found))
    start=found[0].start(); opening=raw.index(b'{',start)
    depth=1; end=opening+1
    while depth:
        if raw[end:end+1]==b'{': depth+=1
        elif raw[end:end+1]==b'}': depth-=1
        end+=1
    snippet=raw[start:end]
    bindings.append(dict(symbol=name,source=str(path),source_sha256=hashlib.sha256(raw).hexdigest(),start_byte=start,end_byte_exclusive=end,start_line=raw[:start].count(b'\n')+1,sha256=hashlib.sha256(snippet).hexdigest(),kind='exact_function'))
    assert snippet==raw[start:end]
    return snippet
parts=[]
for path,name in [('mosaic-fixed/sway/desktop/transaction.c','probe_clip_box_intersection'),('scene-core/types/scene/wlr_scene.c','scene_clip_translate'),('mosaic-fixed/sway/desktop/transaction.c','workspace_tiling_scene_x')]:
    parts.append(capture(Path(path),name))
raw=(LAB/'mosaic-fixed/sway/desktop/transaction.c').read_bytes()
start=raw.index(b'if (isfinite(row->state.scroll_x) &&')
end=raw.index(b'\n\t\t\t\t\twlr_scene_tree_set_clip',start)
statement=raw[start:end]
bindings.append(dict(symbol='arrange_output:camera_clip_conversion_statement',source='mosaic-fixed/sway/desktop/transaction.c',source_sha256=hashlib.sha256(raw).hexdigest(),start_byte=start,end_byte_exclusive=end,start_line=raw[:start].count(b'\n')+1,sha256=hashlib.sha256(statement).hexdigest(),kind='exact_statement_in_adapter'))
(OUT/'core-functions.inc').write_bytes(b'\n\n'.join(parts)+b'\n')
(OUT/'core-guard.inc').write_bytes(statement+b'\n')
(OUT/'bindings.json').write_text(json.dumps(dict(status='EXPERIMENTAL',bindings=bindings),indent=2)+'\n')
