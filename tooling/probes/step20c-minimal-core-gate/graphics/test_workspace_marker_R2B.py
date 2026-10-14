"""R2B nullable/workspace-marker IPC adapter regressions; offline, no native qualification."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from engine import Session
from ipc_predicates import nodes, ancestry
from geometry import assigned_origin, exterior_ipc

BASE=Path(__file__).resolve().parent

class NullableAncestor(unittest.TestCase):
    def call_owner(self,snapshot):
        owners=[n for n in nodes(snapshot['tree']) if n.get('app_id')=='org.mosaic.NestedGrabProbe']
        self.assertEqual(len(owners),1)
        owner=owners[0]
        session=Session.__new__(Session)
        session.proc={'owner':SimpleNamespace(pid=owner['pid'])}
        session.snapshot=lambda tag:snapshot
        session.save=lambda *args:None
        with patch('engine.subprocess.Popen',side_effect=AssertionError('offline only')),patch('engine.subprocess.run',side_effect=AssertionError('offline only')):
            result=session.owner('owner')
        self.assertTrue(result['geometry_status'].startswith('IPC_PENDING_CANDIDATE'))
        self.assertIn('fresh pointer-local corroboration',result['evidence'])
        return owner,result

    def test_retained_null_ancestors_actual_owner(self):
        for case in ('E0-pristine','E0-core','E2-vertical'):
            with self.subTest(case=case):
                snap=json.loads((BASE/'runs'/case/'run/owner-owner-snapshot.json').read_text())
                owner=next(n for n in nodes(snap['tree']) if n.get('app_id')=='org.mosaic.NestedGrabProbe')
                path=ancestry(snap['tree'],owner['id'])
                for kind in ('root','output','workspace'):
                    rows=[n for n in path if n['type']==kind]
                    self.assertEqual(len(rows),1)
                    self.assertIn('floating',rows[0]);self.assertIsNone(rows[0]['floating'])
                owner,result=self.call_owner(snap)
                origin=assigned_origin(owner);scene=exterior_ipc(owner)
                ws=result['workspace']
                if ws.get('layout')=='mosaic':
                    scroll=int(ws['mosaic']['rows'][0]['scroll_x']);origin[0]-=scroll;scene[0]-=scroll
                self.assertEqual(result['origin'],origin);self.assertEqual(result['scene'],scene)

    def test_valid_strings_and_floating_membership_preserved(self):
        original=json.loads((BASE/'runs/E0-core/run/owner-owner-snapshot.json').read_text())
        for flag,membership in (('auto_on',False),('user_on',False),('auto_off',True),('user_off',False)):
            with self.subTest(flag=flag,membership=membership):
                snap=copy.deepcopy(original)
                owner=next(n for n in nodes(snap['tree']) if n.get('app_id')=='org.mosaic.NestedGrabProbe')
                path=ancestry(snap['tree'],owner['id']);owner['floating']=flag
                ws=next(n for n in path if n['type']=='workspace')
                ws['layout']='mosaic';ws['mosaic']={'rows':[{'scroll_x':70}]}
                if membership:
                    parent=path[-2];parent['nodes'].remove(owner);parent['floating_nodes'].append(owner)
                owner,result=self.call_owner(snap);origin=assigned_origin(owner)
                if flag.endswith('off') and not membership:origin[0]-=70
                self.assertEqual(result['origin'],origin)

    def test_true_fullscreen_container_ancestry(self):
        original=json.loads((BASE/'runs/E0-core/run/owner-owner-snapshot.json').read_text())
        for level in ('leaf','parent'):
            with self.subTest(level=level):
                snap=copy.deepcopy(original)
                owner=next(n for n in nodes(snap['tree']) if n.get('app_id')=='org.mosaic.NestedGrabProbe')
                path=ancestry(snap['tree'],owner['id']);ws=next(n for n in path if n['type']=='workspace')
                ws['layout']='mosaic';ws['mosaic']={'rows':[{'scroll_x':70}]}
                owner['floating']='auto_off'
                if level=='leaf':owner['fullscreen_mode']=1
                else:
                    parent=path[-2];index=parent['nodes'].index(owner)
                    parent['nodes'][index]={'id':987654,'type':'con','fullscreen_mode':1,'floating':None,'nodes':[owner],'floating_nodes':[]}
                owner,result=self.call_owner(snap)
                self.assertEqual(result['origin'],assigned_origin(owner))
                self.assertEqual(result['scene'],exterior_ipc(owner))

if __name__=='__main__':unittest.main(verbosity=2)
