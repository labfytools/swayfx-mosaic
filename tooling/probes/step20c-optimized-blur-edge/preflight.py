#!/usr/bin/env python3
"""Offline source, callback, protocol and pinned sampling audit; no graphics."""
import ast
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

lab = Path(sys.argv[1]).resolve()
fixture = Path(__file__).resolve().parent
repo = fixture.parents[2]
results = lab / 'results'
for path in fixture.glob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
for path in lab.glob('*.xml'):
    ET.parse(path)
client = (fixture / 'clients.c').read_text()
assert client == (lab / 'client-source.c').read_text()
callback = client[client.index('static void layer_configure('):client.index('static void layer_close(')]
assert 'draw(' not in callback and 'ack_configure(s, serial)' in callback
# WHY: exercise the real callback text under duplicate configures without Wayland.
# CONTRACT: stub only ACK and clock; no native graphics or mutation reservation.
harness = '''#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
struct zwlr_layer_surface_v1 {int unused;};
static int width=420,height=320;
static unsigned commits=0,acks=0;
static long long stamp(void){return 0;}
static void zwlr_layer_surface_v1_ack_configure(struct zwlr_layer_surface_v1 *s,uint32_t serial){(void)s;(void)serial;++acks;}
''' + callback + '''
int main(void){struct zwlr_layer_surface_v1 s={0};layer_configure(NULL,&s,1,800,600);layer_configure(NULL,&s,2,800,600);assert(acks==2 && commits==0 && width==800 && height==600);commits=1;layer_configure(NULL,&s,3,800,600);assert(acks==3 && commits==1);return 0;}
'''
(lab / 'callback-test.c').write_text(harness)
subprocess.run(['cc', '-std=c17', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
                str(lab / 'callback-test.c'), '-o', str(lab / 'callback-test')], check=True)
subprocess.run([str(lab / 'callback-test')], check=True)
assert 'commits >= 3' in client and "pattern != (commits == 1 ? 'B' : 'A')" in client
assert 'WL_SHM_FORMAT_ARGB8888' in client and 'WL_SHM_FORMAT_XRGB8888' in client
assert 'live_buffers >= 8' in client and 'wl_buffer_listener' in client
assert 'wl_display_roundtrip(display)' in client and 'wl_output_interface, 4' in client
run = (fixture / 'run.py').read_text()
assert "reserve(lab,mode,'mutation')" in run and "reserve(lab,mode,'capture')" in run
assert "['swaymsg','-s',str(sock)" in run and "signal.setitimer(signal.ITIMER_REAL,150)" in run
assert "if instrumented:env['OPT_TRACE']='1'" in run
# Both private controls have every same unconditional borrowed read and old trace.
trace_header = (lab / 'scenefx/include/render/opt_probe.h').read_text()
assert 'if (getenv("OPT_TRACE"))' in trace_header
for shader in ('blur1.frag', 'blur2.frag'):
    rel = Path('render/fx_renderer/shaders') / shader
    assert (lab / 'scene0' / rel).read_bytes() == (lab / 'scenefx' / rel).read_bytes()
command = (lab / 'pristine/sway/commands/blur.c').read_text()
assert 'arrange_container(con)' in command and 'root->all_outputs' in command
passes = []
# Source-derived coordinate support, ideal bilinear positions, no driver claims.
for direction, level, valid in [('down', 0, (800,600)), ('down', 1, (400,300)),
                                ('down', 2, (200,150)), ('up', 2, (100,75)),
                                ('up', 1, (200,150)), ('up', 0, (400,300))]:
    written = (800 // (2 ** (level + 1 if direction == 'down' else level)),
               600 // (2 ** (level + 1 if direction == 'down' else level)))
    mapping = '2*(p+0.5)-0.5 plus offsets +/-5' if direction == 'down' else '(p+0.5)/2-0.5 plus axial +/-2.5 and diagonal +/-1.25'
    maximum = [(2 * (v - .5) - .5 + 5) if direction == 'down'
               else ((v - .5) / 2 - .5 + 2.5) for v in written]
    passes.append({'direction': direction, 'level': level, 'framebuffer': [800,600],
                   'fresh_input_domain': list(valid), 'written_domain': list(written),
                   'sampler_mapping': mapping, 'max_unclamped_sample_xy': maximum,
                   'can_read_beyond_fresh_domain': (direction == 'up') or (direction == 'down' and level > 0),
                   'possible_value': 'earlier write/allocation content, native content NOT OBSERVED',
                   'final_influence': 'propagated right/bottom boundary bands; strength predicted by model only'})
source_files = [lab / 'scene0/render/fx_renderer' / p for p in
                ('fx_pass.c','fx_texture.c','fx_framebuffer.c','fx_offscreen_buffers.c','shaders/blur1.frag','shaders/blur2.frag')]
(results / 'sampling-domain-audit.json').write_text(json.dumps({
    'status': 'SOURCE POSSIBILITY; native intermediate content NOT OBSERVED',
    'source_sha256': {str(p.relative_to(lab)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
    'passes': passes, 'filter': 'GL_LINEAR', 'wrap': 'GL_CLAMP_TO_EDGE full texture, not reduced domain',
    'precision': 'native mediump GLES versus ideal offline bilinear/8-bit rounding',
    'clear': 'no full color clear between blur passes in audited render_blur_segments',
    'blur_cycle': 'scoped blur flag + arrange_container; dirty every output; natural background commit dirties its output',
    'causality': 'not established by source audit'}, indent=2) + '\n')
(results / 'preflight.json').write_text(json.dumps({
    'AST': 'PASS', 'XML': 'PASS', 'C17_callback_duplicate_ACK_no_draw': 'PASS',
    'SHM_bounds_formats_lifetimes': 'PASS source audit, live proof pending',
    'Wayland_connections_protocols': 'PASS source audit and C17 build, live proof pending',
    'explicit_command_reservations': 'PASS source audit',
    'timeouts_owned_cleanup': 'PASS source audit',
    'shader_bytes_pristine_private': 'IDENTICAL',
    'trace_toggle': 'presence only; same private code, old traces remain',
    'graphical_runs': 0}, indent=2) + '\n')
print('PASS AST/XML/C17 callback, SHM/Wayland/reservation/cleanup audit, immutable shaders, sampling audit')
