"""Frozen bounded questions/actions; source absence limits the scientific verdict."""
C=[dict(name='HEADLESS-1',logical=[-800,0,800,600],mode=[800,600],scale=1.,transform='normal'),dict(name='HEADLESS-2',logical=[0,0,800,600],mode=[800,600],scale=1.,transform='normal')]
D1=[dict(name='HEADLESS-1',logical=[0,0,800,600],mode=[800,600],scale=1.,transform='normal'),dict(name='HEADLESS-2',logical=[0,600,800,600],mode=[800,600],scale=1.,transform='normal')]
D2=[{**C[0],'mode':[1000,750],'scale':1.25},C[1]]
D3=[{**C[0],'mode':[750,1000],'scale':1.25,'transform':'90'},C[1]]
LIMITS=dict(duration_s=150,active_watchdog_s=143,capture=20,click=8,grab=2,camera=2,mutation=24,move=16,chain=1)
SPECS={
 'D1':dict(outputs=D1,client='vertical-client',placement='v_both_cross',axis=1,boundary=600,
   question='Do genuine root/child vertical crossings preserve upper pixels/input and exclude lower popup pixels/input under Mosaic?',
   limits={**LIMITS,'capture':16,'camera':1},steps=['stable-H2-reference-pair','open-owner','real-left-TOPLEVEL-open-A','real-left-A-open-B','actual-y600-crossing-A-B','upper-B-right-input','lower-B-right-standard-or-forbidden-Mosaic','record-dismissal','normal-close','whole-H2-restoration']),
 'D2':dict(outputs=D2,client='nested-client',placement='static_cross',axis=0,boundary=0,
   question='Does scale1.25 use logical pointer coordinates once and preserve sampled crossing popup clipping?',
   limits={**LIMITS,'capture':16,'camera':1},steps=['five-asymmetric-output-markers','observe-logical-PNG-frame-and-physical-mode','stable-H2-reference-pair','owner-once-calibration','two-real-grabs','actual-A-B-x0-crossing','visible-B-right','H2-standard-or-forbidden-B-right','record-dismissal','normal-close','whole-H2-restoration']),
 'D3':dict(outputs=D3,client='nested-client',placement='static_cross',axis=0,boundary=0,
   question='Does R90 scale1.25 preserve measured logical popup and pointer geometry?',
   limits={**LIMITS,'capture':16,'camera':1},steps=['five-asymmetric-output-markers','observe-IPC-transform-string90-and-PNG-frame','stable-H2-reference-pair','owner-once-calibration','two-real-grabs','actual-A-B-x0-crossing','visible-B-right','H2-standard-or-forbidden-B-right','record-dismissal','normal-close','whole-H2-restoration']),
 'D4':dict(outputs=C,client='nested-client',placement='static_cross',axis=0,boundary=0,
   question='Do output resize/clamp and workspace migration preserve observed owner/order and clear old output pixels?',
   limits=LIMITS,steps=['startup-vacated-H1-reference','all-clients-open-before-camera','H2-reference-pair','owner-calibration','two-real-grabs','initial-identities-order-camera-clip','H1-mode960x600-position-960','single-known-extent-large-scroll-source-clamp','H1-mode800x600-position-800','workspace1-move-to-H2','workspace1-move-back-H1','record-live-identities-or-legitimate-dismissal','normal-close','final-vacated-H1-and-whole-H2']),
 'E1':dict(outputs=C,client='nested-client',placement='static_cross',axis=0,boundary=0,
   question='Does a fully hidden applied owner hide the same root/child and allow an unchanged live chain to return?',
   limits={**LIMITS,'capture':16,'grab':4,'chain':2,'camera':4},steps=['two-prefix-fillers-owner-two-tail-fillers-preopened','calibrate-once','H2-reference-pair','two-real-grabs-crossing','visible-B-right','hide-owner-camera-computed-from-applied-endpoint','empty-root-clip-and-no-popup-colors-H1-H2','motion-no-popup-enter','return-exact-inverse-camera','same-object-IDs-no-popup_done-or-recreation','visible-B-right','normal-close','whole-H2-restoration']),
 'E2':dict(outputs=C,client='saved-client',placement=None,axis=0,boundary=0,
   question='What is actually observed during one natural200ms held XDG transaction, without saved-node traces?',
   limits={**LIMITS,'capture':12,'click':2,'move':2,'camera':1,'grab':0,'chain':0},steps=['all-clients-preopened','one-crossing-camera','H2-reference-pair','arm-hold_next_configure','normal-gaps-inner30-configure-request','received-serial-HOLD-wire','held-capture-if-before-timeout','natural-default200ms-timeout-no-forced-ACK','client-alive-wire-ping-dispatch','post-timeout-capture','normal-close','whole-H2-restoration'],
   ceilings=['saved-node identity NOT OBSERVABLE','native saved render NOT PROVEN','saved clipping verdict INCONCLUSIVE even if sampled H2 RGB passes']),
 'E3':dict(outputs=C,client='fx-clients',placement=None,axis=0,boundary=0,
   question='Are shadow/classic/optimized blur actual RGB effects and fresh A/B/A pixels sampled with protected whole H2?',
   limits={**LIMITS,'mutation':10,'capture':20,'grab':0,'chain':0},steps=['static-H2-reference-pair','real-H1-checker-layer-explicit-A','translucent-XDG-and-fillers','single-crossing-camera-or-standard-spill','FX-off-pair','shadow-on-pair-visible-ROI-change','shadow-off-classic-floating-glass-wholly-H1-off-pair','classic-blur-on-pair-actual-filtered-RGB','retile-and-once-recalibrate-for-optimized','optimized-on-natural-cache-A-pair','explicit-background-B-pair','explicit-background-A-pair','central-A-B-A-fresh-RGB','Mosaic-whole-H2-protected-every-state','normal-close'],
   ceilings=['pristine has no OBC trace','sampling/cache-source and final-draw clip are distinct','classic floating wholly H1 does not qualify Mosaic-tiled classic clipping','standard glass tiled at output edge does not establish optimized glass crossing; H2 shadow spill recorded separately','common edge delta measured anew, historical max6 not a threshold']),
 'F':dict(outputs=C,client='region-client',placement='both_cross',axis=0,boundary=0,
   question='What natural applied scene/client input/damage/native commit-present ordering is actually sampled?',
   limits={**LIMITS,'capture':12,'click':12,'move':12,'mutation':24,'camera':3,'grab':0,'chain':0},steps=['H2-reference-pair','owner-current-assignment-and-applied-scene','baseline-right-input','region-empty-real-client-commit','same-point-right-no-owner-delivery','region-full-real-client-commit','same-point-right-owner-delivery','focus-filler-and-owner','gaps-inner30-and0','one-camera-forward-and-inverse-if-Mosaic','layout-splith-and-Mosaic-if-candidate','sample-settled-pixels-and-whole-H2','analyze-at-most12-exact-output-seq-commit-present-pairs','record-missing-present-and-natural-window-NOT_EXERCISED','normal-close'],
   ceilings=['native buffer reference/release identity NOT PROVEN','atomic applied epoch NOT PROVEN','no GPU readback, forced timing or interval-seeking loop'])}
RUNS={}
for group,spec in SPECS.items():
    modes=('mosaic',) if group in ('E1','E2') else ('pristine','mosaic')
    for mode in modes:
        run_id=group+'-'+mode
        RUNS[run_id]={**spec,'id':run_id,'campaign':group,'mode':mode,
           'preconditions':['independent final-byte review','exact annotated979dcd95 or pinned pristine8ac86548','exact wlroots7edca9','owned0700 runtime and explicit sockets','unused unique run token','global/local budget','complete client/protocol source provenance'],
           'click_computation':'measured solid color interior converted via observed PNG frame/scale/output origin; recompute against latest live configured/applied geometry before each injection; half-open logical bounds; no double scale',
           'stop_criteria':['deadline143s','log32MiB','ambiguous owner/root/popup ancestry','output mismatch','missing actual marker frame for scale/rotation','crossing not actually exercised','protocol error','unobservable mandatory predicate','local/global budget exhausted'],
           'retention':['all raw stdout/stderr/process and terminal IPC codes','all IPC snapshots/request intervals','client WAYLAND_DEBUG with object/serial/ACK/buttons','renderer and proc maps','original full RGB PNGs','every reservation and observed consumption','independent source windows without atomic generation claim']}
