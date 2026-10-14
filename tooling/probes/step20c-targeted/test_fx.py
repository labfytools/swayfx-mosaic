"""Bounded offline validator regression tests and retained E3 evidence audit."""
import hashlib
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import fx_validators as v


class FXTests(unittest.TestCase):
    def test_fx_close_command_drives_actual_c_handler(self):
        source = Path(__file__).with_name('fx-client.c').resolve()
        lab_clients = Path('/home/fy59/swayfx-mosaic-targeted-7gge6h8b/clients')
        harness = r'''#define main fx_client_program_main
#include "SOURCE_PATH"
#undef main
int main(void) {
  mode = "glass";
  running = 1;
  close_received = false;
  handle_command("close-extra\n");
  if (!running || close_received) return 1;
  handle_command("close");
  if (!running || close_received) return 2;
  top_close(NULL, NULL);
  if (running || close_received) return 3;
  running = 1;
  layer_close(NULL, NULL);
  if (running || close_received) return 4;
  running = 1;
  stop(SIGTERM);
  if (running || close_received) return 5;
  running = 1;
  handle_command("close\n");
  if (running || !close_received) return 6;
  return 0;
}
'''.replace('SOURCE_PATH', str(source))
        cflags = shlex.split(subprocess.run(
            ['pkg-config', '--cflags', '--libs', 'wayland-client'],
            check=True, capture_output=True, text=True).stdout)
        with tempfile.TemporaryDirectory(prefix='fx-close-test-') as temp:
            harness_path = Path(temp) / 'fx-close-harness.c'
            binary = Path(temp) / 'fx-close-harness'
            harness_path.write_text(harness)
            compile_argv = [
                'cc', '-std=c17', '-O2', '-I', str(lab_clients),
                str(harness_path), str(lab_clients / 'xdg-shell-protocol.c'),
                str(lab_clients / 'layer-shell-protocol.c'), '-o', str(binary),
                *cflags,
            ]
            subprocess.run(compile_argv, check=True, capture_output=True, text=True)
            result = subprocess.run([str(binary)], check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr.count('CLOSE_RECEIVED '), 1)
        self.assertIn('CLOSE_RECEIVED ', result.stderr)

    def test_whole_difference_survives_exact_center(self):
        a=Image.new('RGB',(8,8)); b=a.copy(); b.putpixel((7,7),(2,3,4))
        result=v.restoration(a,b,b,{'center':[1,1,4,4]})
        self.assertEqual(result['wholeH1']['pixels'],1)
        self.assertEqual(result['wholeH1']['bbox'],[7,7,8,8])
        self.assertTrue(result['rois']['center']['AA']['exact'])
        self.assertEqual(result['wholeH1']['perchannel'][2]['total_abs'],4)

    def test_masks_negative_and_padding_rejected(self):
        a=Image.new('RGB',(8,8))
        for box in ([-1,0,4,4],[0,0,9,4],[0,0,0,4]):
            with self.assertRaises(ValueError):v.diff(a,a,box)
        with self.assertRaises(ValueError):v.diff(a,a,mask=[1,1,7,7])

    def test_classic_requires_nonempty_actual_filter_and_same_source(self):
        a=Image.new('RGB',(8,8)); b=Image.new('RGB',(8,8),(80,80,80))
        for x in range(8):
            for y in range(8):a.putpixel((x,y),(255,255,255) if x%2 else (0,0,0))
        for same,path,witness in ((False,{'nonempty_region':True},True),
            (True,{'nonempty_region':False},True),(True,{'nonempty_region':True},False)):
            self.assertEqual(v.classic(a,b,[0,0,8,8],same,path,witness)['status'],'CLASSIC_BLUR_NOT_EXERCISED')
        self.assertEqual(v.classic(a,a,[0,0,8,8],True,{'nonempty_region':True},True)['status'],'CLASSIC_BLUR_NOT_EXERCISED')
        self.assertEqual(v.classic(a,b,[0,0,8,8],True,{'nonempty_region':True},True)['status'],'EXERCISED')

    def test_unexercised_cache_rejected(self):
        self.assertEqual(v.cache('')['status'],'NOT OBSERVABLE')
        self.assertEqual(v.cache('OPT_BLUR_USE output=HEADLESS-1 optimized=1 chosen=(nil)')['status'],'CACHE_NOT_EXERCISED')
        trace='OPT_DIRTY_SET node=0xa enabled=1 size=800x600\nOPT_REGEN_ATTEMPT output=HEADLESS-1 node=0xa dirty=1\nOPT_REGEN_RESULT output=HEADLESS-1 node=0xa result=1\nOPT_DIRTY_CLEAR output=HEADLESS-1 node=0xa dirty=0\nOPT_BLUR_USE output=HEADLESS-1 optimized=1 chosen=0xb'
        self.assertEqual(v.cache(trace)['status'],'NATIVE_OBSERVED')
        self.assertEqual(v.cache(trace.replace('node=0xa result=1','node=0xc result=1'))['status'],'CACHE_NOT_EXERCISED')

    def test_false_normalclose_rejected(self):
        log='CLIENT_COMMIT ns=1\nRELEASE ns=2 buffer=3\nCLOSE_RECEIVED ns=3\nOBJECTS_DESTROYED ns=4\nEXIT ns=5 error=0 commits=1 normalclose=1 releases=1\n'
        self.assertEqual(v.normalclose(log,0,True,True)['status'],'PASS')
        for text,code,alive,gone in ((log,1,True,True),(log,0,False,True),(log,0,True,False),
            (log.replace('error=0','error=32'),0,True,True),
            (log.replace('OBJECTS_DESTROYED','CLIENT_COMMIT'),0,True,True),
            (log.replace('RELEASE ns=2 buffer=3\n',''),0,True,True)):
            self.assertEqual(v.normalclose(text,code,alive,gone)['status'],'FAIL')


def audit(historical, lab):
    """Read HIST only; write new offline evidence solely below the supplied LAB."""
    hist, lab=Path(historical).resolve(),Path(lab).resolve()
    v.require(hist!=lab and not lab.is_relative_to(hist),'separate new LAB')
    out=lab/'results'/'fx-offline';out.mkdir(parents=True,exist_ok=True)
    results={}
    for variant in ('pristine','mosaic'):
        run=hist/'matrix'/('E3-'+variant)/'run'
        result=v.validate_run(run)
        geom=json.loads((run/'glass-geometry.json').read_text())
        origin=geom['origin']; win=geom['owner']['window_rect']
        x=max(-800,origin[0]);r=min(0,origin[0]+win['width']);y=max(0,origin[1]);t=min(600,origin[1]+win['height'])
        center=[(x+r)//2+800,(y+t)//2];roi=[center[0]-32,center[1]-32,center[0]+32,center[1]+32]
        result['historical_center_reconstructed_from_retained_geometry']=roi
        result['historical_center']=v.diff(run/'optimized-A-H1.png',run/'optimized-A-return-H1.png',roi)
        events=[json.loads(l) for l in (run/'events.jsonl').read_text().splitlines()]
        close=[e for e in events if e['kind']=='client-request' and e.get('command','').startswith('close')]
        exitrows={name:[l for l in (run/(name+'.log')).read_text().splitlines() if l.startswith('EXIT ')] for name in ('glass','background')}
        terminal=json.loads((run/'terminal-ipc.json').read_text())
        trace=(run/'compositor.log').read_text(errors='replace')
        result['shutdown_chronology']=dict(last_capture_ns=max(e['end_ns'] for e in events if e['kind']=='capture'),
            explicit_client_close_requests=close,client_exits=exitrows,terminal_ipc=terminal,
            compositor_shutdown_lines=[l for l in trace.splitlines() if any(k in l.lower() for k in ('shutting down','destroying','exiting'))][-12:],
            inference='error32 after failed equality and runner teardown; normal close NOT EXERCISED; GPU/client lifetime defect NOT PROVEN',
            exact_native_compositor_exit_ns='NOT OBSERVABLE in retained log; stderr textual shutdown order alone is insufficient')
        result['input_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(run.iterdir()) if p.is_file()}
        (out/(variant+'.json')).write_text(json.dumps(result,indent=2)+'\n');results[variant]=result
    (out/'AUDIT.md').write_text('''# Experimental retained E3 FX audit

HIST is read-only. Shared validators report complete RGB differences, including
bbox and per-channel count/sum/max. Central exact RGB does not establish whole
H1 restoration. Old client exits error32 follow runner teardown after the
whole-image predicate failed; no explicit normal close was sent. Native exact
compositor-exit ns is absent, so no precise GPU lifetime chronology is invented.

The old filler0 is static-reference (opaque XRGB 0x00303038), under floating
glass at (-650,200); it hides the striped wallpaper. The classic off/on entire
H1/H2 images are identical. Actual classic filtering was NOT EXERCISED. The
new client substitutes a transparent ARGB filler and retains source bytes.
Glass ARGB 0x88442010 has alpha 136 and RGB 68/32/16 <= alpha (premultiplied).
Background XRGB has 8-pixel alternating stripes. No opaque region is requested
by the client. Background is a layer-shell background on HEADLESS-1; floating
glass is above tiled transparent filler. RGB off/on comparison with immutable
sources distinguishes filter activity from compositing alone.

Source-selected blur: sway/desktop/output.c could_container_overlap returns
true for floating/animated owners; should_optimize_blur = blur_xray OR NOT
could_container_overlap. SceneFX fx_pass.c fx_render_pass_add_blur calls
get_main_buffer_blur for classic, then logs chosen before final texture draw.
A chosen pointer proves neither nonempty final filter region nor pixel effect.
Classic EXERCISED requires same SHM source and actual changing RGB plus reduced
adjacent contrast in the prospectively fixed center. Without that evidence the
status remains CLASSIC_BLUR_NOT_EXERCISED. OPT native events are cache-only;
client wire buffer IDs cannot be equated to output/cache pointers. Aggregate
native trace presence cannot establish causal A/B/A dirty chronology.

No compositor launched. Complete frame/damage/GPU lifetime is NOT PROVEN.
''')
    return {k:dict(wholeH1=r['optimized']['wholeH1'],center=r['historical_center'],
        classic=r['classic_H1']) for k,r in results.items()}


if __name__=='__main__':
    if len(sys.argv)==4 and sys.argv[1]=='--audit':
        print(json.dumps(audit(sys.argv[2],sys.argv[3]),indent=2))
    else:unittest.main()
