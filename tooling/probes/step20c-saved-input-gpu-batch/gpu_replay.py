"""EXPERIMENTAL whole-image historical evidence; no GPU diagnosis inferred."""
import hashlib,sys
from pathlib import Path
sys.path.insert(1,str(Path(__file__).resolve().parents[1]/'step20c-targeted'))
from fx_validators import diff,sources
from input_validators import require
GPU_ASSERTIONS=('whole-RGB-unmasked', 'same-SHM-not-output-identity', 'homologous-A-G-exact')

def replay(run):
    run=Path(run)
    aa=diff(run/'optimized-A-H1.png',run/'optimized-A-return-H1.png')
    ab=diff(run/'optimized-A-H1.png',run/'optimized-B-H1.png')
    source=sources(run,(run/'background.log').read_text())
    return dict(whole_H1_A_return=aa,whole_H1_AB=ab,source_SHM=source,
                CACHE_A_RETURN_CAUSALITY='INCONCLUSIVE',FBO_CONTENT_IDENTITY='NOT_PROVEN',
                OUTPUT_BUFFER_IDENTITY='NOT_PROVEN',GPU_COMPLETION='NOT_PROVEN')

def homologous(a,g):
    paths=sorted(Path(a).glob('*.png'));require(len(paths)==16,'exact historical sixteen images')
    comparisons={p.name:diff(p,Path(g)/p.name) for p in paths}
    require(all(r['exact'] for r in comparisons.values()),'A/G whole images differ')
    return comparisons
