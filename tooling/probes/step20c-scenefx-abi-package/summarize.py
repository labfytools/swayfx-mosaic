#!/usr/bin/env python3
"""Summarize measured evidence without turning a candidate into an approval.

CONTRACT: successful S0 and expected incompatible naive S1 are distinct.
INVARIANT: no ABI inference from SONAME, compile success, or struct size alone.
"""
import argparse
import json
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__);p.add_argument('lab',type=Path)
a=p.parse_args();lab=a.lab.resolve();r=lab/'results'
assert not (r/'evidence-sha256.txt').exists(), 'already sealed'
def read(name):return json.loads((r/(name+'.json')).read_text())
def save(name,value):(r/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
assert read('stock-stage-manifest')['status']=='CURRENT_PACKAGE_STAGE_PASS'
assert read('unresolved-symbols')['classification']=='INCOMPATIBLE_WITH_STOCK_SCENEFX'
options={
 'A_upstream':{'technical':'UNKNOWN acceptance; API source prototype demonstrated',
 'system_library_intact':'normal maintained upstream upgrade required; no private overwrite',
 'sway_intact':True,'coexistence':'conditional on supported upstream API/version',
 'stable_API':'NOT AVAILABLE in pinned stock','ABI':'NOT ESTABLISHED for future upstream release',
 'one_file':'possible after adoption, NOT TESTED','upgrade_risk':'medium; shared dependency transition',
 'SceneFX_maintenance':'upstream if accepted; no commitment obtained','wlroots':'version-paired qualification',
 'reproducibility':'private prototype only','human_decision':True,
 'remaining':['accepted ownership/error/bounds contract','upstream maintainer agreement','public ABI/version policy','graphical feasibility gates']},
 'B_static':{'technical':'shared-source static build and loader PASS',
 'system_library_intact':True,'sway_intact':True,'coexistence':'conditional; no filesystem overlap',
 'stable_API':'private','ABI':'17-struct layout and current relocations PASS; future safety NOT ESTABLISHED',
 'one_file':'binary dependency shape demonstrated, static stage NOT TESTED',
 'upgrade_risk':'high until explicit wlroots interposition/update policy',
 'SceneFX_maintenance':'Mosaic must own all embedded security fixes; no owner committed',
 'wlroots':'still shared libwlroots-0.20.so; overlapping exports must be qualified',
 'reproducibility':'fixed sources/patches/commands retained; bit reproducibility NOT TESTED',
 'human_decision':True,'remaining':['symbol binding contract','wlroots version matrix','MIT notices in one-file distribution','security/rebase owner','static package contract acceptance','graphical tests separately authorized']},
 'C_private_shared':{'technical':'same-SONAME private process resolution PASS; distinct-SONAME candidate NOT TESTED',
 'system_library_intact':True,'sway_intact':True,'coexistence':'conditional on separate file/SONAME and complete binding audit',
 'stable_API':'private','ABI':'future isolated distribution NOT ESTABLISHED',
 'one_file':False,'upgrade_risk':'medium/high; shared wlroots still imposes constraints',
 'SceneFX_maintenance':'Mosaic-private library owner required','wlroots':'shared consumers/interposition remain',
 'reproducibility':'laboratory lookup only','human_decision':True,
 'remaining':['new owned library file and packaging decision','distinct SONAME/DT_NEEDED','private RUNPATH/transitive lookup','no stock/private duplication within process','security owner']},
 'D_no_new_API':{'technical':'UNKNOWN; no implementation authorized',
 'system_library_intact':True,'sway_intact':True,'coexistence':'conditional on valid compositor architecture',
 'stable_API':'existing unstable scene API only','ABI':'new dependency avoided, architecture unproved',
 'one_file':'possible, NOT TESTED','upgrade_risk':'unknown, broad renderer maintenance possible',
 'SceneFX_maintenance':'normal upstream for stock; Mosaic owns alternate mechanism',
 'wlroots':'same version-paired graphical contracts','reproducibility':'NOT TESTED','human_decision':True,
 'remaining':['popup/global stacking','hit traversal','damage/visibility','effects and saved buffers','rotation/scaling/migration','transaction state consistency']}}
save('architectural-options',options)
save('coexistence-matrix',{'S0':'no filesystem conflict; stock dynamic dependency',
 'S1_naive_stock':'missing two symbols; cannot be distributed as stock-compatible',
 'S2_static':'no SceneFX file, 85 overlapping exports with shared wlroots',
 'S2_shared':'extra private library file requires new package ownership contract',
 'standard_sway':'no modification in any experiment'})
save('upgrade-rollback-risks',{'current_upgrade':'no conflicts/provides/replaces prevents package-manager block; shared SONAME/API changes can still break Mosaic and require separate rebuild',
 'static_upgrade':'SceneFX system upgrade does not update embedded code; shared wlroots remains an ABI constraint',
 'private_shared_upgrade':'private file protects library ownership; shared wlroots plus symbol semantics still require qualification',
 'rollback':'hypothetical remove only /usr/bin/swayfx-mosaic in S0; stock sway/libraries untouched; actual removal NOT TESTED',
 'forbidden':'pinning shared system dependencies to block stock SwayFX updates'})
save('decision-gates',{'public_API':'new decision before implementation',
 'package_contract':'unchanged; static bundling or extra private library requires explicit decision',
 'GPU_lifetime_and_cache':'NOT TESTED here; separate from linker evidence',
 'recommended_next':'bounded non-graphical design of symbol/ownership/update and license contracts for static candidate; prepare upstream API dossier without submission',
 'integration_authorized':False})
save('matrix',{'S0_build':'PASS','S0_model':'PASS','S0_stage':'CURRENT_PACKAGE_STAGE_PASS',
 'S1_private_loader':'PASS relocations only','S1_stock_loader':'INCOMPATIBLE_WITH_STOCK_SCENEFX',
 'S2_static_build':'PASS','S2_static_loader':'PASS relocations only','distinct_SONAME_build':'NOT TESTED',
 'graphics':'NOT RUN / FORBIDDEN','system_install':'NOT RUN / FORBIDDEN','bit_reproducibility':'NOT TESTED'})
save('summary',{'verdict':'PARTIALLY_FEASIBLE','architecture':'SCENEFX_ABI_PACKAGE_REQUIRES_ARCHITECTURAL_DECISION',
 'current_package':'CURRENT_PACKAGE_STAGE_PASS','experimental_stock':'INCOMPATIBLE_WITH_STOCK_SCENEFX',
 'candidate':'static embedding demonstrated technically; unresolved maintenance, symbol and license gates',
 'long_term_direction':'upstream maintained API preferred conditionally, no acceptance presumed',
 'budget':{'stock_rebuild':1,'stock_stage':1,'private_shared_chain':1,'optional_static_chain':1,
 'pristine_SceneFX_reference_build':1,'compositor_launches':0,'graphical_runs':0,'installs':0},
 'phase_B_commit_push':False})
print(json.dumps(read('summary'),indent=2))
