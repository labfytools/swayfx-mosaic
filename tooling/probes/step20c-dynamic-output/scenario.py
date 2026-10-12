"""Private scenario source inserted inside the bounded runner try/finally."""
SCENARIO = r'''    # EXPERIMENTAL fragment inserted inside the inherited bounded runner's try.
    # WHY: persistence observations precede reference clicks that can dismiss grabs.
    # CONTRACT: four reserved dynamic actions per mode; no additional camera pair.
    dynamic_stage = 'D0'
    initial_ws_id = workspace()['id']
    initial_owner_id = owner()['id']
    ref_right = find(tree(), lambda n: n.get('app_id') == 'wev')['id']
    command('workspace 1')
    left_proc = spawn(['stdbuf','-oL','wev'], 'wev-left.log')
    wait(lambda: find(tree(), lambda n: n.get('app_id') == 'wev' and n['id'] != ref_right))
    ref_left = find(tree(), lambda n: n.get('app_id') == 'wev' and n['id'] != ref_right)['id']
    command('shadows disable'); command('blur disable')
    command('output * bg #1e1e2e solid_color')

    def closed():
        client_command('close_a')
        time.sleep(.12)

    def calibrate(tag):
        outputs = {o['name']: o for o in ipc('-t','get_outputs') if o['active']}
        active = {w['output']:w for w in ipc('-t','get_workspaces') if w['visible']}
        for out, con_id, logname in [('HEADLESS-1',ref_left,'wev-left.log'),('HEADLESS-2',ref_right,'wev.log')]:
            name = active[out]['name']
            command(f'[con_id={con_id}] move container to workspace {name}')
            command(f'[con_id={con_id}] floating enable')
            command(f'[con_id={con_id}] border none')
            command(f'[con_id={con_id}] resize set 200 150')
            ox=outputs[out]['rect']['x']+50; oy=400
            command(f'[con_id={con_id}] move absolute position {ox} {oy}')
            time.sleep(.25)
        # WHY: after return both references can temporarily share workspace 1.
        # CONTRACT: relocate BOTH before scoring input, avoiding mutual occlusion.
        for out, con_id, logname in [('HEADLESS-1',ref_left,'wev-left.log'),('HEADLESS-2',ref_right,'wev.log')]:
            ox=outputs[out]['rect']['x']+50; oy=400
            text=lambda: (run/logname).read_text()
            # Force a different surface, then accept actual enter or motion.
            inject('move', outputs['HEADLESS-2' if out=='HEADLESS-1' else 'HEADLESS-1']['rect']['x']+10,10)
            before=len(text());inject('move',ox+20,oy+30)
            pattern=r'(?:enter:[^\n]*|motion:[^\n]*)x, y: ([\d.]+), ([\d.]+)'
            wait(lambda: re.search(pattern,text()[before:]))
            ex,ey=map(float,re.findall(pattern,text()[before:])[-1])
            if ex != 20 or not 0 <= ey < 100:
                raise RuntimeError(f'calibration interior mismatch {tag} {out}: {ex},{ey}')
            before=len(text());inject('move',ox+60,oy+50)
            wait(lambda: f'x, y: {ex+40:.6f}, {ey+20:.6f}' in text()[before:])
            before=len(text())
            inject('left',ox+60,oy+50);inject('right',ox+60,oy+50)
            wait(lambda: 'button: 272' in text()[before:] and 'button: 273' in text()[before:])
            record('pointer_calibration',tag=tag,output=out,con_id=con_id,global_point=[ox+60,oy+50],local_expected=[ex+40,ey+20],surface_origin=[ox+20-ex,oy+30-ey],passed=True)
        for x in (-2,-1,0,1,2):inject('move',x,550)
        inject('move',outputs['HEADLESS-1']['rect']['x']+110,450)
        command('workspace 1')

    def stable(tag, expected_owner):
        # CONTRACT: repeated geometry and paired settled captures are evidence,
        # not proof that intermediate configurations each had a presentation.
        time.sleep(.35)
        before=ipc('-t','get_outputs')
        time.sleep(.12)
        after=ipc('-t','get_outputs')
        if before != after:
            raise RuntimeError(f'unstable output IPC at {tag}')
        ws=workspace();o=owner()
        current=next(w for w in ipc('-t','get_workspaces') if w['id']==initial_ws_id)
        if ws['id']!=initial_ws_id or o['id']!=initial_owner_id or current['output']!=expected_owner:
            raise RuntimeError(f'workspace/owner identity mismatch at {tag}')
        snapshot(tag)
        time.sleep(.16);snapshot(tag+'-repeat')
        record('identity',tag=tag,workspace_id=ws['id'],owner_id=o['id'],output=current['output'],layout=ws['layout'],order=[n['id'] for n in ws['nodes']],mosaic=ws.get('mosaic'),focused=current['focused'])

    def owner_hit(tag):
        o=owner();ws=workspace()
        scroll_x=ws['mosaic']['rows'][0]['scroll_x'] if args.mode=='private_mosaic' else 0
        point=[int(o['rect']['x']-scroll_x+o['window_rect']['x']+100),150]
        before=len(client_text());inject('move',*point);inject('right',*point)
        delivered='POINTER_BUTTON target=TOPLEVEL' in client_text()[before:]
        record('owner_hit',tag=tag,point=point,delivered=delivered,events=client_text()[before:])
        if not delivered:raise RuntimeError(f'visible owner input failed {tag}')

    calibrate('D0')
    command('[app_id="org.mosaic.NestedGrabProbe"] focus')
    stable('D0','HEADLESS-1');owner_hit('D0')
    open_chain('D0-chain')
    stable('D0-popup','HEADLESS-1')
    reserve(lab,args.mode,'D1')
    record('dynamic_launch',action='D1')
    dynamic_stage='D1'
    command('output HEADLESS-1 mode 1200x750 scale 1.25 position -960 0')
    stable('D1-popup','HEADLESS-1')
    closed();calibrate('D1');owner_hit('D1')
    open_chain('D1-chain');stable('D1-reopened','HEADLESS-1')
    reserve(lab,args.mode,'D2');record('dynamic_launch',action='D2')
    dynamic_stage='D0'
    command('output HEADLESS-1 mode 1000x750 scale 1.25 position -800 0')
    stable('D2-popup','HEADLESS-1')
    closed();calibrate('D2');owner_hit('D2')
    open_chain('D2-chain');stable('D3-before','HEADLESS-1')
    # Context is explicitly verified before moving the target workspace.
    if not next(w for w in ipc('-t','get_workspaces') if w['name']=='1')['focused']:
        raise RuntimeError('workspace 1 is not migration context')
    reserve(lab,args.mode,'D3');record('dynamic_launch',action='D3')
    command('move workspace to output HEADLESS-2')
    stable('D3-popup','HEADLESS-2')
    record('popup_lifecycle',tag='D3-before-calibration',done_a=count('POPUP_A POPUP_DONE'),done_b=count('POPUP_B POPUP_DONE'),client_events=client_text())
    closed();calibrate('D3');owner_hit('D3')
    open_chain('D3-new-chain');stable('D3-reopened','HEADLESS-2')
    # New-owner forbidden region is on the old H1, not historical x=20.
    before=len(client_text());inject('move',-20,190);inject('right',-20,190)
    record('forbidden_click',tag='D3',global_point=[-20,190],events=client_text()[before:],delivered=bool(re.search(r'POINTER_BUTTON target=POPUP_[AB]',client_text()[before:])))
    closed();open_chain('D3-return-chain');stable('D5-before','HEADLESS-2')
    reserve(lab,args.mode,'D5');record('dynamic_launch',action='D5')
    command('move workspace to output HEADLESS-1')
    stable('D5-popup','HEADLESS-1')
    record('popup_lifecycle',tag='D5-before-calibration',done_a=count('POPUP_A POPUP_DONE'),done_b=count('POPUP_B POPUP_DONE'),client_events=client_text())
    closed();calibrate('D5');owner_hit('D5')
    open_chain('D5-new-chain');stable('D5-reopened','HEADLESS-1')
    before=len(client_text());inject('move',20,190);inject('right',20,190)
    record('forbidden_click',tag='D5',global_point=[20,190],events=client_text()[before:],delivered=bool(re.search(r'POINTER_BUTTON target=POPUP_[AB]',client_text()[before:])))
    closed();stable('D5-closed','HEADLESS-1')
'''
