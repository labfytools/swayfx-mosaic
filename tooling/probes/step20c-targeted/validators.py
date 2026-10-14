"""Shared offline/runtime evidence predicates; absent wire evidence fails closed."""
import re
from geometry import need

def held_configure(before,after,prior_serial):
    need(type(prior_serial)is int and prior_serial>0,'prior serial required')
    need(re.search(rf'ACK ns=\d+ serial={prior_serial}\b',before) and re.search(rf'ack_configure\({prior_serial}\)',before),'initial actual ACK required')
    need('wl_shm_pool#' in before and '.create_buffer(' in before and 'COMMIT ns=' in before,'real initial SHM required')
    held=re.findall(r'HELD ns=(\d+) serial=(\d+)',after);need(len(held)==1,'unique real HELD configure')
    ns,serial=map(int,held[0]);need(serial!=prior_serial,'new held serial')
    need(re.search(rf'xdg_surface#\d+\.configure\({serial}\)',after),'received actual configure wire')
    need(re.search(rf'XDG_CONFIGURE ns=\d+ serial={serial}\b.*hold=1',after),'client received hold state')
    old=re.findall(r'ACK ns=\d+ serial='+str(prior_serial)+r' size=(\d+)x(\d+)',before);new=re.findall(r'XDG_CONFIGURE ns=\d+ serial='+str(serial)+r' size=(\d+)x(\d+)',after)
    need(old and new and old[-1]!=new[-1],'new geometry configure required')
    need(not re.search(rf'ack_configure\({serial}\)|ACK ns=\d+ serial={serial}\b',after),'held serial must remain unACKed')
    return dict(ns=ns,serial=serial,prior_serial=prior_serial,initial_size=list(map(int,old[-1])),requested_size=list(map(int,new[-1])),status='HELD_WIRE_VALIDATED',native_saved_identity='NOT OBSERVABLE')

def native_pairs(text):
    commits=[];presents={};seen=set()
    for raw in text.splitlines():
        if not ('PI_OUTPUT_COMMIT ' in raw or 'PI_OUTPUT_PRESENT ' in raw):continue
        f=dict(re.findall(r'(\w+)=([^\s]+)',raw));need(all(k in f for k in ('output','commit_seq','ns')),'native pair fields');key=(f['output'],int(f['commit_seq']))
        if 'PI_OUTPUT_COMMIT ' in raw:
            need(key not in seen,'duplicate native commit');seen.add(key);commits.append((key,f,raw))
        else:
            need(key not in presents,'duplicate native present');presents[key]=(f,raw)
    rows=[]
    for key,f,raw in commits:
        p=presents.get(key)
        if p:need(int(p[0]['ns'])>int(f['ns']),'present order')
        rows.append(dict(output=key[0],seq=key[1],commit=raw,present=p[1] if p else None,presented=p[0].get('presented') if p else None,status='PAIRED' if p else 'MISSING_PRESENT'))
    return dict(total_commits=len(commits),analyzed=rows,paired=sum(r['status']=='PAIRED' for r in rows),missing=sum(r['status']=='MISSING_PRESENT' for r in rows),unmatched_presents=[dict(output=k[0],seq=k[1],raw=v[1]) for k,v in presents.items() if k not in seen],atomic_generation='NOT PROVEN',buffer_identity='NOT PROVEN',physical_presentation='NOT PROVEN')
