"""Pure read-only native-field float64 ideal analysis. No fitted tolerances.
WHY/CONTRACT/INVARIANT: the ideal bilinear coordinates are a source-derived
model, never a measurement of mediump interpolation or linked GPU arithmetic.
"""
import numpy as np
from validate import need, FRESH, reconstruct


def field(epoch,p):
    s=epoch['samples'][p];x,y,w,h=s['roi']
    return np.frombuffer(epoch['raw'][s['offset']:s['offset']+s['bytes']],dtype=np.uint8).reshape(h,w,4)

def deltas(a,b):
    need(a.shape==b.shape,'homologous field dimensions')
    d=b.astype(np.int16)-a.astype(np.int16);changed=np.any(d!=0,axis=2);yy,xx=np.where(changed)
    return dict(pixels=int(changed.sum()),bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None,
        min=d.min(axis=(0,1)).tolist(),max=d.max(axis=(0,1)).tolist(),maxabs=int(np.abs(d).max()),
        signed_histograms=[{str(int(k)):int(v) for k,v in zip(*np.unique(d[:,:,c],return_counts=True))} for c in range(4)])

def bilinear(src,x,y):
    # Physical texture edge clamp, never clamp to its fresh domain.
    x=np.clip(x,0,src.shape[1]-1);y=np.clip(y,0,src.shape[0]-1)
    x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);x1=np.minimum(x0+1,src.shape[1]-1);y1=np.minimum(y0+1,src.shape[0]-1)
    tx=(x-x0)[...,None];ty=(y-y0)[...,None]
    return src[y0,x0]*(1-tx)*(1-ty)+src[y0,x1]*tx*(1-ty)+src[y1,x0]*(1-tx)*ty+src[y1,x1]*tx*ty

def ideal(src,w,h,down,fresh):
    src=src.astype(np.float64);yy,xx=np.mgrid[:h,:w]
    if down:
        x,y=2*xx+.5,2*yy+.5;taps=[(0,0,4/8),(-5,-5,1/8),(5,5,1/8),(5,-5,1/8),(-5,5,1/8)]
    else:
        x,y=xx/2-.25,yy/2-.25;taps=[(-2.5,0,1/12),(2.5,0,1/12),(0,-2.5,1/12),(0,2.5,1/12),(-1.25,-1.25,2/12),(1.25,1.25,2/12),(1.25,-1.25,2/12),(-1.25,1.25,2/12)]
    mask=np.zeros(src.shape[:2],dtype=np.float64);mask[:fresh[1],:fresh[0]]=1
    inside=src*mask[...,None];outside=src*(1-mask)[...,None]
    a=np.zeros((h,w,4));b=np.zeros_like(a)
    for dx,dy,weight in taps:a+=bilinear(inside,x+dx,y+dy)*weight;b+=bilinear(outside,x+dx,y+dy)*weight
    return a+b,a,b

def residual_stats(d):
    return dict(min=d.min(axis=(0,1)).tolist(),max=d.max(axis=(0,1)).tolist(),maxabs=float(np.abs(d).max()),nonzero_pixels=int(np.any(d!=0,axis=2).sum()))

def composition(rgb,coefficient=119):
    need(coefficient==119,'prospective composition coefficient')
    return np.floor(np.array((68,32,16))+rgb[:,:,:3].astype(np.float64)*(119/255)+.5)

def whole_hypothesis(epochs):
    a,b=epochs[0],epochs[2];stats={}
    for p in range(7):
        aa,bb=field(a,p),field(b,p);fresh=FRESH[p];stats[str(p)]=dict(full=deltas(aa,bb),fresh=deltas(aa[:fresh[1],:fresh[0]],bb[:fresh[1],:fresh[0]]))
    first=next((p for p in range(1,7) if stats[str(p)]['fresh']['pixels']),None)
    return dict(SOURCE_MAIN_WHOLE_EQUALITY='EXACT' if not stats['0']['full']['pixels'] else 'REFUTED',
        FIRST_FRESH_DIVERGENCE_WHOLE=first,H_FRONTIERE_CHAMP_ENTIER='COMPATIBLE_EXACT_PREDICTIONS' if not any(stats[str(p)]['fresh']['pixels'] for p in (0,1,2)) and first==3 else 'REFUTED',fields=stats)

def ideal_residuals(epochs,output=None):
    results=[];native=[]
    for e in (epochs[0],epochs[2]):
        r=reconstruct(e);arr=lambda b:np.frombuffer(b,dtype=np.uint8).reshape(600,800,4)
        srcs=[field(e,0),field(e,1),field(e,2),arr(r['P2']),arr(r['Q2']),arr(r['P1'])]
        predicted=[];measured=[];freshparts=[];tails=[]
        for i,src in enumerate(srcs):
            w,h=FRESH[i+1];v,a,b=ideal(src,w,h,i<3,FRESH[i]);dst=field(e,i+1)[:h,:w]
            predicted.append(v);measured.append(dst);freshparts.append(a);tails.append(b)
        native.append((predicted,measured,freshparts,tails))
    for i in range(6):
        pa,ma,fa,ta=[native[0][k][i] for k in range(4)];pb,mb,fb,tb=[native[1][k][i] for k in range(4)]
        pd=pb-pa;md=mb.astype(float)-ma.astype(float);res=md-pd
        results.append(dict(stage=i,absolute_A=residual_stats(ma-pa),absolute_Areturn=residual_stats(mb-pb),differential=residual_stats(res),fresh_difference=residual_stats(fb-fa),outside_difference=residual_stats(tb-ta),ideal_source_exact_but_destination_different=int((np.all(pd==0,axis=2)&np.any(md!=0,axis=2)).sum())))
        if output:
            np.savez(output/f'stage-{i}-ideal-and-residuals.npz',ideal_A=pa,ideal_Areturn=pb,absolute_A=ma-pa,absolute_Areturn=mb-pb,differential=res,fresh=fb-fa,outside=tb-ta)
    return dict(model='SOURCE_DERIVED_FLOAT64_IDEAL_NO_TOLERANCE',effective_precision='NOT_MEASURED',residuals=results)

def glass_relation(epochs,run,states):
    from PIL import Image
    run=__import__('pathlib').Path(run)
    pngs=[np.array(Image.open(run/(tag+'-H1.png')).convert('RGB')) for tag in ('optimized-A','optimized-B','optimized-A-return')]
    need(all(p.shape==(600,800,3) for p in pngs),'whole H1 PNG dimensions')
    aa=pngs[0];ar=pngs[2];changed=np.any(aa!=ar,axis=2)
    # Fixed prospective H1 domain, every pixel accounted for; unknown predicates
    # stay unknown. CORE IPC pending geometry cannot prove atomic applied order.
    relation=[]
    for e,png in zip((epochs[0],epochs[2]),(aa,ar)):
        u=field(e,6);pred=composition(u)
        direct=png.astype(float)-pred
        flipped=png.astype(float)-pred[::-1]
        relation.append(dict(raw_direct_all_H1_residual=residual_stats(direct),raw_flip_y_all_H1_residual=residual_stats(flipped),admissibility='NOT_PROVEN',orientation='SOURCE_PROJECTION_PREDICTS_GL_LOW_TO_HIGH; constant-y witness does not prove orientation'))
    sampled=[]
    for e in epochs:
        cache=field(e,7);pre=field(e,8)
        if e['rows'][0]['epoch']==2:u=field(e,6)
        else:u=field(e,6)[292:308,784:800]
        sampled.append(dict(epoch=e['rows'][0]['epoch'],U0_cache_RGBA=deltas(u,cache),cache_presubmit_RGBA=deltas(cache,pre),ideal_glass_presubmit_RGB_residual=residual_stats(pre[:,:,:3].astype(float)-composition(u))))
    return dict(WHOLE_VISIBLE_GLASS_RELATION='INCONCLUSIVE',WHOLE_H1_DEFECT_REPRODUCED='EXERCISED' if changed.any() else 'NOT_EXERCISED',
        whole_H1_RGBA_equivalent_RGB=dict(pixels=int(changed.sum()),min=(ar.astype(int)-aa).min(axis=(0,1)).tolist(),max=(ar.astype(int)-aa).max(axis=(0,1)).tolist()),
        exhaustive_partition=dict(total_pixels=480000,admissible=0,other=0,predicate_unknown=480000,changed_admissible=0,changed_other=0,changed_predicate_unknown=int(changed.sum())),
        candidate_geometry=states,all_H1_relation=relation,CACHE_COPY_SAMPLED=sampled,
        meaning='Raw formula residuals cover every H1 pixel and do not define admissibility. No precision tolerance or anomaly mask.',GPU_FULL_FIELD='OBSERVED_UNDER_VALIDATOR_GATES',COMPLETE_DAMAGE='NOT_PROVEN',ATOMIC_GENERATION='NOT_PROVEN')
