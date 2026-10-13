"""Exact reusable historical geometry/protocol/terminal core tests.
Derived AST nodes from geometry-replay/tests_offline.py; no historical gate.
"""
import unittest
import re
from dataclasses import replace
from PIL import Image
from model import *
from predicates import *
from pixels import color_geometry
ACTIVE=None
class Case(unittest.TestCase):

    def setUp(self):
        global ACTIVE
        ACTIVE = self.id()
        self.p = Provenance(9, 6, 'applied-1', 'synthetic applied trace')
        self.a = Applied(Rect(Space.GLOBAL, -320, 0, 640, 600, self.p), Rect(Space.CONTENT, 2, 0, 636, 573, self.p), Rect(Space.CONFIGURE, 0, 0, 636, 573, self.p), Native(Rect(Space.NATIVE, 0, 0, 420, 320, self.p), 12, 1680, 1, 20), 2, 25, 25, 21)
        self.r = content(self.a)
        self.o = Output('H1', Rect(Space.GLOBAL, -800, 0, 800, 600, self.p), 1.0, 'normal')
        self.clip = Rect(Space.VIEWPORT, -800, 0, 800, 600, self.p)

    def tearDown(self):
        global ACTIVE
        ACTIVE = None

    def reject(self, contract, fn):
        with self.assertRaisesRegex(Invalid, '^' + re.escape(contract) + '$'):
            fn()

    def test_positive_geometry(self):
        self.assertEqual(self.r.values(), [-318, 25, 636, 573])
        self.assertEqual(to_png(intersect(self.r, self.clip), self.o).values(), [482, 25, 318, 573])
        self.assertEqual(from_png(Rect(Space.PNG, 482, 25, 318, 573, self.p), self.o).values(), [-318, 25, 318, 573])
        verify_paint(self.r, self.o, [482, 25, 800, 598], 182214, self.clip)

    def test_negative_native_height(self):
        self.reject('paint-origin-intersection', lambda: verify_paint(replace(self.r, height=320), self.o, [482, 25, 800, 598], 182214, self.clip))

    def test_negative_scene_window_y(self):
        self.reject('paint-origin-intersection', lambda: verify_paint(replace(self.r, y=0), self.o, [482, 25, 800, 598], 182214, self.clip))

    def test_negative_titlebar(self):
        self.reject('titlebar-content-offset', lambda: content(replace(self.a, titlebar=0)))

    def test_negative_output_origin(self):
        self.reject('paint-origin-intersection', lambda: verify_paint(self.r, replace(self.o, rectangle=replace(self.o.rectangle, x=0)), [482, 25, 800, 598], 182214, self.clip))

    def test_negative_png_space(self):
        self.reject('global-to-png-spaces', lambda: to_png(replace(self.r, space=Space.PNG), self.o))

    def test_negative_png_bounds(self):
        self.reject('png-bounds', lambda: from_png(Rect(Space.PNG, -1, 25, 318, 573, self.p), self.o))

    def test_negative_assignment(self):
        self.reject('configure-assignment', lambda: content(replace(self.a, configured=replace(self.a.configured, width=420))))

    def test_negative_workspace(self):
        self.reject('workspace-identity', lambda: content(replace(self.a, window=replace(self.a.window, provenance=replace(self.p, workspace=7)))))

    def test_negative_owner(self):
        self.reject('owner-identity', lambda: content(replace(self.a, window=replace(self.a.window, provenance=replace(self.p, owner=10)))))

    def test_negative_old_camera(self):
        self.reject('applied-generation', lambda: intersect(self.r, replace(self.clip, provenance=replace(self.p, generation='old-camera'))))

    def test_negative_local_global_clip(self):
        self.reject('global-intersection', lambda: intersect(self.r, replace(self.clip, space=Space.CONTENT)))

    def test_negative_buffer_identity(self):
        self.reject('native-buffer-identity', lambda: content(replace(self.a, native=replace(self.a.native, buffer_id=0))))

    def test_negative_pending(self):
        self.reject('pending-not-applied', lambda: content(replace(self.a, scene=replace(self.a.scene, provenance=replace(self.p, state='pending')))))

    def test_negative_scale(self):
        self.reject('unmeasured-output-scale', lambda: to_png(self.r, replace(self.o, scale=2.0)))

    def test_negative_transform(self):
        self.reject('unmeasured-output-transform', lambda: to_png(self.r, replace(self.o, transform='90')))

    def test_positive_popup(self):
        A = popup(self.r, Rect(Space.POPUP, 100, 80, 350, 170, self.p), 9, 9, 22, True)
        B = popup(A, Rect(Space.POPUP, 100, 60, 300, 130, self.p), 12, 12, 23, True)
        self.assertEqual(A.values(), [-218, 105, 350, 170])
        self.assertEqual(B.values(), [-118, 165, 300, 130])
        self.assertEqual(crossing(B, 0), 'EXERCISED')
        self.assertEqual(crossing(replace(B, x=1), 0), 'NOT EXERCISED')
        pointer_local((-100, 175), B, (18, 10))
        constraints(0, [100, 80, 350, 170], [100, 80, 350, 170])
        self.assertEqual(local_clip_to_global(Rect(Space.CONTENT, -482, -25, 800, 600, self.p), (-318, 25), self.p).values(), [-800, 0, 800, 600])

    def test_negative_parent(self):
        self.reject('xdg-parent', lambda: popup(self.r, Rect(Space.POPUP, 100, 80, 350, 170, self.p), 11, 9, 22, True))

    def test_negative_ack(self):
        self.reject('popup-ack', lambda: popup(self.r, Rect(Space.POPUP, 100, 80, 350, 170, self.p), 9, 9, 0, True))

    def test_negative_map(self):
        self.reject('popup-map', lambda: popup(self.r, Rect(Space.POPUP, 100, 80, 350, 170, self.p), 9, 9, 22, False))

    def test_negative_constraints(self):
        self.reject('zero-flags-no-adjustment', lambda: constraints(0, [100, 80, 350, 170], [99, 80, 350, 170]))

    def test_negative_pointer(self):
        self.reject('pointer-local-correlation', lambda: pointer_local((-308, 35), self.r, (0, 0)))

    def test_negative_occlusion(self):
        im = Image.new('RGB', (800, 600))
        r = Rect(Space.GLOBAL, -800, 0, 1, 1, self.p)
        self.reject('replay-paint-POPUP_A', lambda: color_geometry(im, 'POPUP_A', r, self.o, None))

    def test_negative_standard_stale_origin(self):
        self.reject('fresh-standard-generation', lambda: fresh_standard(self.r, self.r))

    def test_positive_standard_fresh(self):
        self.assertEqual(fresh_standard(self.r, replace(self.r, x=-398, provenance=replace(self.p, generation='standard-2'))).x, -398)

    def test_negative_E2_identity(self):
        self.reject('fresh-E2-identity', lambda: fresh_chain(dict(owner=9, pid=10, serials=[1, 2]), dict(owner=9, pid=11, serials=[3, 4])))

    def test_negative_E2_serials(self):
        self.reject('fresh-E2-serials', lambda: fresh_chain(dict(owner=9, pid=10, serials=[1, 2]), dict(owner=10, pid=11, serials=[2, 3])))

    def test_positive_E2(self):
        fresh_chain(dict(owner=9, pid=10, serials=[1, 2]), dict(owner=10, pid=11, serials=[3, 4]))

    def test_positive_terminal(self):
        for ipc in (0, 1):
            self.assertTrue(terminal(True, ipc, 0, "Handling command 'exit'\nShutting down sway", False, False, stdout='actual reply', stderr='actual stderr')['scientific_cleanup_pass'])

    def test_negative_terminal_incomplete(self):
        self.assertFalse(terminal(False, 1, 0, "Handling command 'exit'\nShutting down sway", False, False)['scientific_cleanup_pass'])

    def test_negative_terminal_unhandled(self):
        self.assertFalse(terminal(True, 1, 0, 'Shutting down sway', False, False)['scientific_cleanup_pass'])

    def test_negative_terminal_compositor(self):
        self.assertFalse(terminal(True, 1, 1, "Handling command 'exit'\nShutting down sway", False, False)['scientific_cleanup_pass'])

    def test_negative_terminal_protocol(self):
        self.assertFalse(terminal(True, 1, 0, "Handling command 'exit'\nShutting down sway", True, False)['scientific_cleanup_pass'])

    def test_negative_terminal_rescue(self):
        self.assertFalse(terminal(True, 1, 0, "Handling command 'exit'\nShutting down sway", False, True)['scientific_cleanup_pass'])

    def test_negative_dismissal_hit(self):
        with self.assertRaisesRegex(Defect, 'invisible popup'):
            dismissal('POPUP_B POPUP_DONE \nPOPUP_A POPUP_DONE \nPOPUP_B DESTROY \nPOPUP_A DESTROY ', ['POINTER_BUTTON target=POPUP_B serial=22 button=273 state=1'])

    def test_negative_dismissal_incomplete(self):
        with self.assertRaises(AssertionError):
            dismissal('POPUP_A POPUP_DONE ', [])

    def test_positive_dismissal(self):
        self.assertEqual(dismissal('POPUP_B POPUP_DONE \nPOPUP_A POPUP_DONE \nPOPUP_B DESTROY \nPOPUP_A DESTROY ', [])['status'], 'PASS')

    def test_positive_button(self):
        pair(['POINTER_BUTTON target=POPUP_B serial=22 button=273 state=1', 'POINTER_BUTTON target=POPUP_B serial=23 button=273 state=0'], 'POPUP_B')

    def test_negative_button(self):
        with self.assertRaises(Defect):
            pair(['POINTER_BUTTON target=POPUP_A serial=22 button=273 state=1'], 'POPUP_B')

    def test_negative_root_ambiguous(self):
        trace = 'PI_OWNER output=HEADLESS-1 ns=10 id=9 scene_valid=1\nPI_POPUP output=HEADLESS-1 ns=11 local_index=1 tree=0x1 enabled=1 clip_valid=1 clip=-482,-25,800,600\nPI_POPUP output=HEADLESS-1 ns=12 local_index=2 tree=0x2 enabled=1 clip_valid=1 clip=-482,-25,800,600'
        self.reject('root-chain-unique', lambda: root_clip(trace, [-318, 25], True, 9, 1, 20))

    def test_positive_root(self):
        trace = 'PI_OWNER output=HEADLESS-1 ns=10 id=9 scene_valid=1\nPI_POPUP output=HEADLESS-1 ns=11 local_index=1 tree=0x1 enabled=1 clip_valid=1 clip=-482,-25,800,600'
        self.assertTrue(root_clip(trace, [-318, 25], True, 9, 1, 20)['clip_valid'])
