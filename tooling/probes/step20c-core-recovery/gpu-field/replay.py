"""Read-only G1 epoch1 audit. No compositor, GPU call, runtime writer or launcher."""
import argparse
import json
import struct
from pathlib import Path
import validate as v

HISTORICAL = Path('/home/fy59/swayfx-mosaic-minimal-core-2l7riqt_/gpu-field')
HASHES = {'meta':'c8ca51bca694db9e21471356a4260064ed81ab7013a88d4edb4b8572044a825c',
          'rgba':'a6dc7fd873e1ab7e52e04625bacb3251ba8e1aad2e766811efebde7ae7932a99',
          'arm':'06f961b802bc46ee168555f066d28f4f0e9afdf3f88174c1ee6f9de004fc30a0'}


def load(directory=HISTORICAL/'runtime'):
    directory = Path(directory)
    data = {ext:(directory/f'epoch-1.{ext}').read_bytes() for ext in HASHES}
    for ext, digest in HASHES.items():
        v.need(v.sha(data[ext]) == digest, 'immutable historical hash '+ext)
    rows = [json.loads(line) for line in data['meta'].splitlines()]
    return rows, data['rgba']


def sample_protocol(rows, raw):
    samples = [r for r in rows if r['kind'] == 'sample']
    v.need([s['point'] for s in samples] == list(range(9)), 'nine ordered samples')
    offset = 0
    for sample in samples:
        offset = v.validate_sample(sample, raw, 1, rows[0]['context'], offset)
    v.need(offset == len(raw) == rows[-1]['bytes'] == 8312048
           and v.sha(raw) == rows[-1]['sha256'], 'whole readback extent/hash')
    v.need(all(samples[p]['after_ns'] <= samples[p+1]['before_ns'] for p in range(8)),
           'sample native ordering')
    return samples


def audit(directory=HISTORICAL/'runtime'):
    rows, raw = load(directory)
    samples = sample_protocol(rows, raw)
    envelope = v.validate_g1_envelope(rows, samples, rows[0]['context'])
    try:
        v.validate_epoch(directory, 1)
    except v.Rejected as error:
        global_result = {'status':'REJECTED','reason':str(error)}
    else:
        global_result = {'status':'STRUCTURAL_ONLY','scientific_acceptance':False}
    uniform_bits = []
    for r in (r for r in rows if r['kind'] == 'write' and r['stage'] >= 0):
        u = {u['name']:u for u in r['uniforms']}
        expected = (1/800,1/600) if r['stage'] < 3 else (1/3200,1/2400)
        uniform_bits.append(dict(stage=r['stage'], observed=u['halfpixel']['value'],
            expected_float32=[struct.unpack('I',struct.pack('f',x))[0] for x in expected],
            observed_float=[struct.unpack('f',struct.pack('I',x))[0] for x in u['halfpixel']['value']]))
    def field(p):
        s=samples[p]
        return raw[s['offset']:s['offset']+s['bytes']]
    u0 = field(6)
    roi = b''.join(u0[(y*800+784)*4:(y*800+800)*4] for y in range(292,308))
    return dict(status='EXPERIMENTAL_OFFLINE_ONLY', historical_status='INCONCLUSIVE_UNCHANGED',
        historical_hashes=HASHES, samples=9, raw_bytes=len(raw),sample_protocol='PASS',
        native_envelope=envelope, epoch_validator=global_result,
        plane_evidence=v.validate_object(samples[1]['object']), halfpixel=uniform_bits,
        sampled_relations=dict(U0_cache_RGBA_exact=roi==field(7),cache_presubmit_RGBA_exact=field(7)==field(8)),
        GL_ERROR_QUEUE=rows[0]['GL_ERROR_QUEUE'],read_success=rows[0]['read_success'],
        GPU_MODIFIER_AWARE_OFFLINE='INCONCLUSIVE',plane_metadata_correction='PASS',
        GPU_DCC_DESIGN_REVIEW='NOT_PROVEN',GPU_DCC_RUNTIME='NOT_RUN',
        GPU_WHOLE_FIELD_CAUSALITY='INCONCLUSIVE',epochs_acquired=1,
        causal_limit='No B/A-return or whole-field output; no fitted precision tolerance; no physical DCC decoding.',
        runtime_prerequisites=['Authorized new diagnostic binary with defensible read-success and GL error observability contract',
            'Resolve effective uniform precision validation from primary specification without fitted tolerances',
            'Allocation/FD/auxiliary bounds observability or explicit limited contract',
            'Independent review of exact new source and acquisition preflight before any run reservation'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--historical-runtime',type=Path,default=HISTORICAL/'runtime')
    args=parser.parse_args()
    print(json.dumps(audit(args.historical_runtime),indent=2))
