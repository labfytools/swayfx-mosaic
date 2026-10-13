#!/usr/bin/env python3
"""Optional standalone scientific SVG from complete offline distributions."""
import json
import sys
import os
from pathlib import Path
lab=Path(sys.argv[1]).resolve()
os.environ['MPLCONFIGDIR']=str(lab/'plot-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

out=lab/'results'
columns=json.loads((out/'column-distribution.json').read_text())
rows=json.loads((out/'row-distribution.json').read_text())
model=json.loads((out/'edge-model-comparison.json').read_text())['distributions']
pairs=['P1-B-natural -> P2-B-explicit','P0-FX2 -> P3-A-natural']
fig,axes=plt.subplots(2,2,figsize=(12,7),constrained_layout=True)
for index,key in enumerate(pairs):
    for dim,data,name in [(0,columns,'columns'),(1,rows,'rows')]:
        ax=axes[dim,index]
        ax.plot(data['R0'][key],label='R0/R1 standard native',color='#376ca0',linewidth=1.1)
        ax.plot(data['R2'][key],label='R2/R3 Mosaic native',color='#19816b',linewidth=1.1)
        ax.plot(model[key]['predicted_'+name],label='Fixed offline model, Mosaic domain',
                color='#ba6d20',linewidth=1,linestyle='--',alpha=.8)
        ax.axvspan(750 if dim==0 else 550,800 if dim==0 else 600,color='#888888',alpha=.12)
        ax.set_title(('B natural / explicit' if index==0 else 'A initial / return')+' — '+name)
        ax.set_xlabel('Output-local '+('x' if dim==0 else 'y')+' (px)')
        ax.set_ylabel('Changed pixels per '+('column' if dim==0 else 'row'))
        ax.set_xlim(0,800 if dim==0 else 600);ax.grid(alpha=.2)
axes[0,0].legend(fontsize=8)
fig.suptitle('Complete edge distributions — shared native behavior; offline model is not causal proof',fontsize=12)
fig.savefig(out/'edge-distributions.svg',metadata={'Date':None})
print('PASS standalone SVG; not an additional compositor capture')
