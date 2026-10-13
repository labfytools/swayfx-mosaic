#!/usr/bin/env python3
"""Read-only real E2 transition replay; raw PNGs/logs remain outside Git."""
import json
from pathlib import Path
import re
from PIL import Image
from transition import validate_applied_standard_transition, source_bindings
from predicates import protocol, geometry, popup_pixels, reference
from model import Provenance,require
from support import sha,verify

HISTORICAL=Path('/home/fy59/swayfx-mosaic-static-nested-runtime-pvn0osxm')
SEALS={'source-sha256.txt':(60,'263f5dbee5e96f2c49619802d063115f792718f6aeb71fa41c58c73b83eb8c91'),
       'evidence-sha256.txt':(178,'e8b2307612ce2402ff9b31e68b50a47d666ca38cd8cce1d67096297f8129034a')}

def historical_inputs():
    for name,(count,digest) in SEALS.items():
        p=HISTORICAL/'results'/name
        require(sha(p)==digest and verify(p)['entries']==count,'historical-seal')
    events=[json.loads(l) for l in (HISTORICAL/'run/events.jsonl').read_text().splitlines()]
    replies=[e for e in events if e.get('args')==['[con_id=10] layout splith']]
    require(len(replies)==1,'single-historical-transition');reply=replies[0]
    text=(HISTORICAL/'run/compositor.log').read_text()
    handling="Handling command 'layout splith'"
    require(text.count(handling)==1,'historical-command-handling')
    after=text.split(handling,1)[1]
    # Lower bound is previous actual runner event; upper bound is first actual
    # monotonic compositor record after handling. Exact request time was omitted.
    previous=max(e['ns'] for e in events if e['ns']<reply['ns'])
    upper=int(re.search(r'ns=(\d+)',after)[1])
    window=[previous,max(e['ns'] for e in events if e.get('kind')=='capture')]
    captures=[]
    for e in events:
        if e.get('file') in ('standard-H1.png','standard-H2.png'):
            captures.append(dict(file=e['file'],output=e['output'],start_ns=e['start_ns'],
                                 end_ns=e['ns'],exit=e['exit'],sha256=sha(HISTORICAL/'run'/e['file'])))
    client=(HISTORICAL/'run/E2.log').read_text()
    # Historical client log includes teardown after runner failure. Replay the
    # measured prefix, explicitly cut at cleanup command, never silently delete
    # a done/destroy during the measured window.
    # Historical shutdown is corroborated by seat capabilities(0), then
    # DESTROY records. No explicit owner-close measurement happened.
    shutdown=re.search(r'\{Default Queue\} wl_seat#\d+\.capabilities\(0\)',client)
    require(shutdown is not None and shutdown.start()<client.index('POPUP_B DESTROY '),'historical-shutdown-boundary')
    client=client[:shutdown.start()]
    snapshot=json.loads((HISTORICAL/'results/standard-snapshot.json').read_text())
    ids=protocol(client)['ids']
    return dict(request_ns=[previous,upper],ipc_response=reply,trace=text,
        owner_id=10,root_id='0x56292fbcc170',workspace_id=6,output='HEADLESS-1',
        applied_layout='splith',captures=captures,client_protocol=client,snapshot=snapshot,
        expected_ids=ids,window=window,source_contract=source_bindings())


def replay():
    data=historical_inputs();result=validate_applied_standard_transition(**data)
    g=geometry(data['client_protocol'],[-398,25],Provenance(10,6,'historical-standard','actual PI_OWNER + IPC window'))
    require(g['A']==[-298,105,350,170] and g['B']==[-198,165,300,130],'historical-standard-geometry')
    images={n:Image.open(HISTORICAL/'run'/n).convert('RGB') for n in
            ('H2-reference-1.png','H2-reference-2.png','standard-H1.png','standard-H2.png')}
    reference(images['H2-reference-1.png'],images['H2-reference-2.png'])
    pixels=popup_pixels(images['standard-H1.png'],images['standard-H2.png'],g,False,images['H2-reference-1.png'])
    require(pixels['H2']['POPUP_A']['count']==3120 and pixels['H2']['POPUP_B']['count']==13260,'historical-H2-counts')
    roots=[s for s in result['states'] if s['ns'] in (181923034904618,181923236944243,181923848675032)]
    require(len(roots)==3 and [s['root']['clip_valid'] for s in roots]==['1','0','0'],'raw-transition-chronology')
    return dict(status='PASS',transition=result,geometry=g,pixels=pixels,
        request_time='bounded omission; no exact request timestamp reconstructed',
        runtime_completion='NOT TESTED; historical run remains INCONCLUSIVE')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
    result=replay()
    if a.output:
        with a.output.open('x') as out:json.dump(result,out,indent=2);out.write('\n')
    print('E2_RAW_TRANSITION_REPLAY=PASS')
