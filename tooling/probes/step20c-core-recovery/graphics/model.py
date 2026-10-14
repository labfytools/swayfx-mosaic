"""EXPERIMENTAL typed half-open geometry. Pure: no processes or sockets.

Source contracts are recorded in the offline gate, not inferred from RGB.
Every conversion is explicit and keeps assignment/owner/generation provenance.
"""
from dataclasses import dataclass
from enum import Enum

class Invalid(ValueError):
    pass

class Space(str, Enum):
    NATIVE = 'NativeSHM'
    CONFIGURE = 'XDGConfigure'
    CONTENT = 'AppliedContent'
    GLOBAL = 'SceneGlobal'
    POPUP = 'PopupLocal'
    VIEWPORT = 'GlobalViewport'
    PNG = 'OutputPNG'


def require(value, contract):
    if not value:
        raise Invalid(contract)

@dataclass(frozen=True)
class Provenance:
    owner: int
    workspace: int
    generation: str
    evidence: str
    state: str = 'applied'

@dataclass(frozen=True)
class Rect:
    space: Space
    x: int
    y: int
    width: int
    height: int
    provenance: Provenance

    def __post_init__(self):
        require(isinstance(self.space, Space), 'tag-required')
        require(all(type(v) is int for v in (self.x, self.y, self.width, self.height)), 'integer-geometry')
        require(self.width >= 0 and self.height >= 0, 'nonnegative-size')
        require(bool(self.provenance.evidence), 'evidence-required')

    @property
    def end(self):
        return (self.x + self.width, self.y + self.height)

    def contains(self, xy):
        return self.x <= xy[0] < self.end[0] and self.y <= xy[1] < self.end[1]

    def values(self):
        return [self.x, self.y, self.width, self.height]

@dataclass(frozen=True)
class Native:
    rectangle: Rect
    buffer_id: int
    stride: int
    format: int
    commit_serial: int

@dataclass(frozen=True)
class Applied:
    scene: Rect
    window: Rect
    configured: Rect
    native: Native
    border_left: int
    border_top: int
    titlebar: int
    configure_ack: int
    view_offset: tuple = (0, 0)

@dataclass(frozen=True)
class Output:
    name: str
    rectangle: Rect
    scale: float
    transform: str


def same(a, b):
    require(a.owner == b.owner, 'owner-identity')
    require(a.workspace == b.workspace, 'workspace-identity')
    require(a.generation == b.generation, 'applied-generation')
    require(a.state == b.state == 'applied', 'pending-not-applied')


def content(applied):
    s, w, c, n = applied.scene, applied.window, applied.configured, applied.native
    require(s.space is Space.GLOBAL and w.space is Space.CONTENT and c.space is Space.CONFIGURE,
            'assignment-spaces')
    require(n.rectangle.space is Space.NATIVE, 'native-space')
    for r in (w, c, n.rectangle):
        same(s.provenance, r.provenance)
    require(n.buffer_id > 0 and n.stride == n.rectangle.width * 4 and n.format in (0, 1), 'native-buffer-identity')
    require(0 < n.commit_serial <= 0xffffffff, 'commit-serial')
    require(0 < applied.configure_ack <= 0xffffffff, 'assigned-configure-ack')
    require((w.width, w.height) == (c.width, c.height), 'configure-assignment')
    require(applied.border_left == w.x and applied.border_top == applied.titlebar + w.y,
            'titlebar-content-offset')
    require(w.width + 2 * applied.border_left == s.width and
            w.height + applied.border_top + applied.border_left == s.height, 'assigned-destination')
    return Rect(Space.GLOBAL, s.x + applied.border_left + applied.view_offset[0],
                s.y + applied.border_top + applied.view_offset[1], w.width, w.height, s.provenance)


def intersect(rect, boundary):
    require(rect.space is Space.GLOBAL and boundary.space in (Space.GLOBAL, Space.VIEWPORT), 'global-intersection')
    same(rect.provenance, boundary.provenance)
    x, y = max(rect.x, boundary.x), max(rect.y, boundary.y)
    return Rect(Space.GLOBAL, x, y, max(0, min(rect.end[0], boundary.end[0]) - x),
                max(0, min(rect.end[1], boundary.end[1]) - y), rect.provenance)


def to_png(rect, output):
    require(rect.space is Space.GLOBAL and output.rectangle.space is Space.GLOBAL, 'global-to-png-spaces')
    require(output.scale == 1.0, 'unmeasured-output-scale')
    require(output.transform == 'normal', 'unmeasured-output-transform')
    same(rect.provenance, output.rectangle.provenance)
    visible = intersect(rect, output.rectangle)
    return Rect(Space.PNG, min(max(visible.x - output.rectangle.x,0),output.rectangle.width), min(max(visible.y - output.rectangle.y,0),output.rectangle.height),
                visible.width, visible.height, rect.provenance)


def from_png(rect, output):
    require(rect.space is Space.PNG and output.rectangle.space is Space.GLOBAL, 'png-to-global-spaces')
    require(output.scale == 1.0 and output.transform == 'normal', 'unmeasured-png-transform')
    same(rect.provenance, output.rectangle.provenance)
    require(0 <= rect.x <= rect.end[0] <= output.rectangle.width and
            0 <= rect.y <= rect.end[1] <= output.rectangle.height, 'png-bounds')
    return Rect(Space.GLOBAL, rect.x + output.rectangle.x, rect.y + output.rectangle.y,
                rect.width, rect.height, rect.provenance)


def verify_paint(rect, output, bbox, count, clip=None):
    expected = to_png(intersect(rect, clip) if clip is not None else rect, output)
    actual = [] if bbox is None else list(bbox)
    box=[expected.x, expected.y, *expected.end] if expected.width and expected.height else []
    require(actual == box, 'paint-origin-intersection')
    require(count == expected.width * expected.height, 'paint-area')
    return expected


def popup(parent, configured, parent_xdg, expected_parent_xdg, ack, mapped):
    require(parent.space is Space.GLOBAL and configured.space is Space.POPUP, 'popup-spaces')
    same(parent.provenance, configured.provenance)
    require(parent_xdg == expected_parent_xdg and expected_parent_xdg > 0, 'xdg-parent')
    require(0 < ack <= 0xffffffff, 'popup-ack')
    require(mapped is True, 'popup-map')
    return Rect(Space.GLOBAL, parent.x + configured.x, parent.y + configured.y,
                configured.width, configured.height, parent.provenance)


def crossing(rect, boundary_x):
    require(rect.space is Space.GLOBAL, 'crossing-space')
    return 'EXERCISED' if rect.x < boundary_x < rect.end[0] else 'NOT EXERCISED'


def local_clip_to_global(local, origin, provenance):
    require(local.space is Space.CONTENT, 'clip-local-space')
    same(local.provenance, provenance)
    return Rect(Space.VIEWPORT, local.x + origin[0], local.y + origin[1],
                local.width, local.height, provenance)


def pointer_local(xy, rect, actual):
    require(rect.space is Space.GLOBAL and rect.contains(xy), 'pointer-global-bounds')
    require(list(actual) == [xy[0] - rect.x, xy[1] - rect.y], 'pointer-local-correlation')
    return list(actual)


def fresh_chain(old, new):
    require(old['owner'] != new['owner'] and old['pid'] != new['pid'], 'fresh-E2-identity')
    require(len(set(old['serials'] + new['serials'])) == 4 and
            max(old['serials']) < min(new['serials']), 'fresh-E2-serials')


def fresh_standard(mosaic, standard):
    require(mosaic.provenance.owner == standard.provenance.owner and
            mosaic.provenance.workspace == standard.provenance.workspace, 'standard-owner')
    require(mosaic.provenance.generation != standard.provenance.generation, 'fresh-standard-generation')
    return standard


def constraints(flags, requested, configured):
    require(type(flags) is int and 0 <= flags <= 63, 'positioner-flags')
    require(flags != 0 or requested == configured, 'zero-flags-no-adjustment')
    return {'flags': flags, 'request': requested, 'actual': configured, 'prediction_only': True}
