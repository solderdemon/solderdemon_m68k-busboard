"""Generate the standardized m68k busboard from the last routed r2 bus.

Run after tools/build_sch.py, with KiCad's python:

    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/standard_pcb.py

The bus (the five slots and their B.Cu wiring) stays as routed in r2; only the bus tracks next to
the new through-hole pads between the slots step aside locally. Everything else follows the 6502
board:

1. The power corner is the 6502 one, part for part, track for track, at the same distances from
   the right-hand and top edges (C1 is the same upright 470 uF). The board is wide enough that the
   corner keeps the 6502 gap to the last slot.
2. One rhythm across the board: every slot is a column, and the line halfway between two slot
   centres carries that gap's 100 nF capacitor (C2..C5), standing vertically with pad 1 level with
   the slots' pin 1 and pad 2 two rows below. C6 continues the rhythm half a pitch past SLOT 4.
   The middle mounting holes sit on the same half-pitch lines, above the capacitors of the
   SLOT 1/2 and SLOT 3/4 gaps.
3. Each capacitor's pad 1 takes a straight F.Cu feed along the pin-1 row from its slot's pin 2
   (C2 is on VCC_HOST).
4. PWR LINK: pin 2 of BUS1 is VCC_HOST. JP1 is the 6502 board's through-hole 1x2 header, lying
   across the HOST/SLOT 1 half-pitch line in pin row LINK_ROW, under C2. It cannot stand: between
   pin rows the bus runs two tracks, which do not fit between pads 2.54 mm apart. C2's pad 1 feeds
   it down the left; its VCC side runs up the right and over BUS2's pin 1 into BUS2's pin 2.
   Through-hole pads between the slots push the B.Cu bus tracks beside them aside (detour()).
5. M3 holes are GND pads 5.08 mm in from the edges, as on the 6502 board. GND pours: F.Cu over
   the whole board, B.Cu in the power corner (between the slots the bus leaves it no room).
6. Solder mask as on the 6502 board: no pad expansion, 0.08 mm minimum web (USB-C pads).
Nets come from the schematic.
"""
from pathlib import Path
import subprocess, tempfile, xml.etree.ElementTree as ET

import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
NAME = 'solderdemon_m68k-busboard'
BOARD = ROOT / f'{NAME}.kicad_pcb'
SOURCE = ROOT.parent / 'solderdemon_6502-busboard' / 'solderdemon_6502-busboard.kicad_pcb'
CLI = 'C:/Program Files/KiCad/10.0/bin/kicad-cli.exe'
STOCK = Path('C:/Program Files/KiCad/10.0/share/kicad/footprints')

CORNER_X = 104.0                     # 6502 board: everything right of this is the power corner
REF = {'C1': 'C1', 'LED1': 'LED1', 'R1': 'R1', 'R3': 'R2', 'R4': 'R3', 'J1': 'J1', 'J2': 'J2',
       'J3': 'J3', 'JP2': 'JP2', 'SW1': 'SW1', 'D1': 'D1'}          # 6502 reference -> m68k
NET = {'Net-(J3-CC1)': 'CC1', 'Net-(J3-CC2)': 'CC2', 'Net-(LED1-K)': 'LED_K'}

GONE = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'D1', 'J1', 'J3', 'J4', 'LED1', 'R1', 'R2', 'R3', 'SW1'] + \
       [f'H{i}' for i in range(1, 9)]
GONE_NETS = {'/DC_IN', '/USB_CC1', '/USB_CC2', '/VBUS_USB', 'Net-(LED1-Pad2)'}
BASE_COMMIT = '3a0c432'             # r2 routing is the immutable input to this generator
SIZE = (185.0, 99.0)                # outline (r2: 175.075 x 99.03); C6 keeps 5 mm from C1's can
LINK_ROW = 5                        # JP1's pin row; rows 1-3 are C2's
HOLE_INSET = 5.08                   # M3 pads this far from the edges, as on the 6502 board
HOLE_GAPS = (1, 3)                  # middle holes on the SLOT 1/2 and SLOT 3/4 half-pitch lines
FEED = 0.5                          # decoupler feeds, as on the 6502 board

mm, MM = pcb.FromMM, pcb.ToMM
KEEP = []                            # removed items must outlive the board (SWIG, see AGENTS.md)


def footprint(fpid):
    lib, name = fpid.split(':')
    path = ROOT.parent / 'tools/capacitors/SolderDemonCaps.pretty' if lib == 'SolderDemonCaps' else ROOT / f'{NAME}.pretty' if lib == NAME else STOCK / f'{lib}.pretty'
    f = pcb.FootprintLoad(str(path), name)
    f.SetFPID(pcb.LIB_ID(lib, name))
    KEEP.append(f)
    return f


def netlist():
    xml = ROOT / 'netlist.xml'
    subprocess.run([CLI, 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(xml),
                    str(ROOT / f'{NAME}.kicad_sch')], check=True, capture_output=True)
    r = ET.parse(xml).getroot()
    xml.unlink()
    parts = {c.get('ref'): (c.findtext('value'), c.findtext('footprint')) for c in r.find('components')}
    pins = {}
    for n in r.find('nets'):
        for node in n.findall('node'):
            pins[(node.get('ref'), node.get('pin'))] = n.get('name')
    return parts, pins


def outline(b):
    """Corner radius and top-left corner of a rounded-rectangle Edge.Cuts outline."""
    shapes = [d for d in b.GetDrawings() if d.GetLayer() == pcb.Edge_Cuts]
    xs = [MM(p.x) for d in shapes for p in (d.GetStart(), d.GetEnd())]
    ys = [MM(p.y) for d in shapes for p in (d.GetStart(), d.GetEnd())]
    arc = next(d for d in shapes if d.GetShape() == pcb.SHAPE_T_ARC)
    return shapes, (min(xs), min(ys)), MM(arc.GetRadius())


def detour(b, pads, radius, nets, at, rel, clearance=0.2, spacing=0.16):
    """Step the horizontal B.Cu bus tracks that pass too close to a row of through-hole pads
    (`pads`: their (x, y), all on one y) aside over the row's width only: two 45 degree jogs and a
    straight run beside the pads. A track pushed into its neighbour pushes that one along as well
    (the r2 bus keeps neighbours `spacing` apart, its net class clearance)."""
    xs, py = [x for x, _ in pads], pads[0][1]
    lo0, hi0 = min(xs) - radius - clearance, max(xs) + radius + clearance
    lanes = []
    for t in b.GetTracks():
        if t.Type() != pcb.PCB_TRACE_T or t.GetLayer() != pcb.B_Cu or t.GetNetCode() in nets:
            continue
        (xa, ya), (xb, yb) = sorted([rel(t.GetStart()), rel(t.GetEnd())])
        if abs(ya - yb) < 1e-3 and xa < lo0 and hi0 < xb and abs(ya - py) < 2.0:
            lanes.append((t, xa, xb, ya, MM(t.GetWidth()) / 2))
    for side in (1, -1):
        edge, margin, lo, hi = py + side * radius, clearance, lo0, hi0   # the obstacle so far
        for t, xa, xb, ya, half in sorted((l for l in lanes if (l[3] - py) * side > 0), key=lambda l: abs(l[3] - py)):
            y2 = edge + side * (margin + half + 0.02)
            if (ya - y2) * side >= 0:
                break                                        # this one and all beyond are clear
            shift = abs(y2 - ya)
            lo, hi = lo - half - 0.02, hi + half + 0.02
            assert xa < lo - shift and hi + shift < xb, ('track ends beside a pad', t.GetNetname(), pads)
            pts = [(xa, ya), (lo - shift, ya), (lo, y2), (hi, y2), (hi + shift, ya), (xb, ya)]
            for a, c in zip(pts, pts[1:]):
                n = pcb.PCB_TRACK(b)
                n.SetStart(at(*a)); n.SetEnd(at(*c)); n.SetWidth(t.GetWidth()); n.SetLayer(pcb.B_Cu)
                n.SetNetCode(t.GetNetCode())
                b.Add(n)
            b.Remove(t)
            KEEP.append(t)
            edge, margin = y2 + side * half, spacing
            lo, hi = lo - shift - spacing, hi + shift + spacing      # the next one clears these jogs



def main():
    raw = subprocess.check_output(['git', 'show', f'{BASE_COMMIT}:{BOARD.name}'], cwd=ROOT)
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / BOARD.name
        base.write_bytes(raw)
        b = pcb.LoadBoard(str(base))
    KEEP.append(b)
    assert b.FindNet('/DC_IN'), 'not the r2 board (already converted?)'
    e = b.GetBoardEdgesBoundingBox()
    ox, oy = MM(e.GetX()), MM(e.GetY())
    at = lambda x, y: pcb.VECTOR2I(mm(ox + x), mm(oy + y))
    rel = lambda p: (round(MM(p.x) - ox, 3), round(MM(p.y) - oy, 3))

    src = pcb.LoadBoard(str(SOURCE))
    KEEP.append(src)
    se = src.GetBoardEdgesBoundingBox()
    sox, soy, sw = MM(se.GetX()), MM(se.GetY()), MM(se.GetWidth())
    srel = lambda p: (MM(p.x) - sox, MM(p.y) - soy)

    parts, pins = netlist()

    # 1. Old power section, holes, decouplers and their tracks.
    for ref in GONE:
        f = b.FindFootprintByReference(ref)
        b.Remove(f)
        KEEP.append(f)
    for t in list(b.GetTracks()):
        n = str(t.GetNetname())
        xs = [rel(t.GetStart())[0], rel(t.GetEnd())[0]]
        corner = max(xs) > 141.0
        host_row = n == 'VCC' and max(xs) <= 53.2          # the VCC chain BUS1 pin 2 -> BUS2 pin 2
        if n in GONE_NETS or (n in ('VCC', 'GND') and corner) or host_row:
            b.Remove(t)
            KEEP.append(t)
    for i in range(1, 6):
        b.FindFootprintByReference(f'BUS{i}-1').SetReference(f'BUS{i}')

    # 2. The outline and pours are drawn afresh.
    edges, (x0, y0), radius = outline(b)
    for d in edges:
        b.Remove(d)
        KEEP.append(d)
    x1, y1 = x0 + SIZE[0], y0 + SIZE[1]
    P = lambda x, y: pcb.VECTOR2I(mm(x), mm(y))
    r, k = radius, radius * (1 - 0.5 ** 0.5)
    for a, c in (((x0 + r, y0), (x1 - r, y0)), ((x1, y0 + r), (x1, y1 - r)),
                 ((x1 - r, y1), (x0 + r, y1)), ((x0, y1 - r), (x0, y0 + r))):
        s = pcb.PCB_SHAPE(b, pcb.SHAPE_T_SEGMENT)
        s.SetStart(P(*a)); s.SetEnd(P(*c))
        s.SetLayer(pcb.Edge_Cuts); s.SetWidth(mm(0.05))
        b.Add(s)
    for s0, m, s1 in (((x0, y0 + r), (x0 + k, y0 + k), (x0 + r, y0)),
                      ((x1 - r, y0), (x1 - k, y0 + k), (x1, y0 + r)),
                      ((x1, y1 - r), (x1 - k, y1 - k), (x1 - r, y1)),
                      ((x0 + r, y1), (x0 + k, y1 - k), (x0, y1 - r))):
        s = pcb.PCB_SHAPE(b, pcb.SHAPE_T_ARC)
        s.SetArcGeometry(P(*s0), P(*m), P(*s1))
        s.SetLayer(pcb.Edge_Cuts); s.SetWidth(mm(0.05))
        b.Add(s)
    e = b.GetBoardEdgesBoundingBox()
    assert (MM(e.GetX()), MM(e.GetY())) == (ox, oy)
    w, h = MM(e.GetWidth()), MM(e.GetHeight())
    dx = w - sw                                  # the corner keeps its distance from the right-hand edge

    gnd_front, corner_back = sorted(b.Zones(), key=lambda z: z.GetLayer() != pcb.F_Cu)
    corner_back.SetNetCode(b.FindNet('GND').GetNetCode())

    def rect(z, xa, ya, xb, yb):
        o = z.Outline()
        o.RemoveAllContours()
        o.NewOutline()
        for x, y in ((xa, ya), (xb, ya), (xb, yb), (xa, yb)):
            o.Append(mm(ox + x), mm(oy + y))

    # 3. New footprints.
    def add(ref, pos, rot=0.0):
        f = footprint(parts[ref][1])
        f.SetReference(ref)
        f.SetValue(parts[ref][0])
        b.Add(f)
        f.SetOrientationDegrees(rot)
        f.SetPosition(at(*pos))
        return f

    for sref, ref in REF.items():
        s = src.FindFootprintByReference(sref)
        x, y = srel(s.GetPosition())
        add(ref, (x + dx, y), s.GetOrientationDegrees())

    pin = lambda ref, n: rel(next(p for p in b.FindFootprintByReference(ref).Pads() if p.GetNumber() == n).GetPosition())
    centre = [(pin(f'BUS{i}', '1')[0] + pin(f'BUS{i}', '2')[0]) / 2 for i in range(1, 6)]
    pitch = centre[1] - centre[0]
    gap = [c + pitch / 2 for c in centre]                     # C2..C6: right of their own slot
    row = lambda n: pin('BUS1', str(2 * n - 1))[1]             # y of pin row n
    for i, x in enumerate(gap):
        add(f'C{i + 2}', (x, (row(1) + row(3)) / 2), -90.0)   # pad 1 on row 1, pad 2 on row 3
    add('JP1', (gap[0] - 1.27, row(LINK_ROW)), 90.0)          # pads across the gap's centre line
    assert abs(pin('JP1', '2')[0] - pin('JP1', '1')[0] - 2.54) < 0.01, 'JP1: pad 2 must be right of pad 1'

    holes = [(HOLE_INSET, HOLE_INSET), *((gap[i], HOLE_INSET) for i in HOLE_GAPS), (w - HOLE_INSET, HOLE_INSET),
             (HOLE_INSET, h - HOLE_INSET), *((gap[i], h - HOLE_INSET) for i in HOLE_GAPS), (w - HOLE_INSET, h - HOLE_INSET)]
    for i, pos in enumerate(holes):
        add(f'H{i + 1}', pos)

    rect(gnd_front, -1.0, -1.0, w + 1.0, h + 1.0)
    corner_left = centre[4] + 5.6                              # clear of BUS5's pads and tracks
    rect(corner_back, corner_left, -1.0, w + 1.0, h + 1.0)

    # 4. Nets from the schematic, on every pad.
    for f in b.GetFootprints():
        for p in f.Pads():
            net = pins.get((f.GetReference(), p.GetNumber()))
            if net is None:
                continue
            ni = b.FindNet(net)
            if ni is None:
                ni = pcb.NETINFO_ITEM(b, net)
                b.Add(ni)
            p.SetNet(ni)

    def track(net, *pts, width=FEED, layer=pcb.F_Cu):
        for a, c in zip(pts, pts[1:]):
            t = pcb.PCB_TRACK(b)
            t.SetStart(at(*a)); t.SetEnd(at(*c)); t.SetWidth(mm(width)); t.SetLayer(layer)
            t.SetNet(b.FindNet(net))
            b.Add(t)

    # 5. The 6502 corner's tracks and vias, moved with it.
    for s in src.GetTracks():
        n = str(s.GetNetname())
        (sx1, sy1), (sx2, sy2) = srel(s.GetStart()), srel(s.GetEnd())
        if min(sx1, sx2) < CORNER_X:
            continue
        n = NET.get(n, n)
        if s.Type() == pcb.PCB_VIA_T:
            v = pcb.PCB_VIA(b)
            v.SetPosition(at(sx1 + dx, sy1)); v.SetWidth(s.GetWidth(pcb.F_Cu)); v.SetDrill(s.GetDrill())
            v.SetNet(b.FindNet(n))
            b.Add(v)
        else:
            track(n, (sx1 + dx, sy1), (sx2 + dx, sy2), width=MM(s.GetWidth()), layer=s.GetLayer())

    # 6. Decoupler feeds: straight along the pin-1 row from pin 2 into pad 1.
    for i in range(5):
        track('VCC_HOST' if i == 0 else 'VCC', pin(f'BUS{i + 1}', '2'), pin(f'C{i + 2}', '1'))

    # PWR LINK: C2's pad 1 runs down its left side into JP1's pad 1; JP1's pad 2 runs up the right
    # side and over BUS2's pin 1 into pin 2.
    c2, j1, j2 = pin('C2', '1'), pin('JP1', '1'), pin('JP1', '2')
    xl = c2[0] - 2.54
    track('VCC_HOST', c2, (xl, c2[1] + 2.54), (xl, j1[1] - (j1[0] - xl)), j1, width=0.6)
    bus2_1, bus2_2 = pin('BUS2', '1'), pin('BUS2', '2')
    x, y = bus2_1[0] - 2.85, bus2_1[1] - 2.0                   # left of BUS2's pin 1 / over it
    track('VCC', j2, (x - 1.0, j2[1]), (x, j2[1] - 1.0), (x, y + 1.0), (x + 1.0, y),
          (bus2_2[0] - 1.0, y), (bus2_2[0], y + 1.0), bus2_2, width=0.6)

    # B.Cu bus tracks beside the new through-hole pads step aside with 45 degree jogs.
    for f in [b.FindFootprintByReference(r) for r in ('C2', 'C3', 'C4', 'C5', 'JP1')]:
        rows = {}
        for p in f.Pads():
            x, y = rel(p.GetPosition())
            rows.setdefault(round(y, 2), []).append((x, y))
        for pads in rows.values():
            detour(b, pads, max(MM(p.GetSizeX()) for p in f.Pads()) / 2,
                   {p.GetNetCode() for p in f.Pads()}, at, rel)

    # The corner's VCC trunk (B.Cu) starts level with LED1; BUS5's pin 2 joins its top end.
    trunk = min((rel(t.GetStart()) for t in b.GetTracks() if t.GetNetname() == 'VCC' and t.GetLayer() == pcb.B_Cu
                 and rel(t.GetStart())[0] > corner_left), key=lambda p: (p[0], p[1]))
    bus5 = pin('BUS5', '2')
    drop = trunk[1] - bus5[1]
    track('VCC', bus5, (trunk[0] - drop, bus5[1]), trunk, width=0.8, layer=pcb.B_Cu)

    ds = b.GetDesignSettings()
    ds.m_SolderMaskExpansion = 0
    ds.m_SolderMaskMinWidth = mm(0.08)

    tb = b.GetTitleBlock()
    tb.SetRevision('r1')
    tb.SetDate('2026-10-14')

    # The filler clips to the outline the board was loaded with, so fill after a reload.
    keep = {p: p.read_bytes() for p in (BOARD.with_suffix('.kicad_pro'), BOARD.with_suffix('.kicad_prl')) if p.exists()}
    pcb.SaveBoard(str(BOARD), b)
    b = pcb.LoadBoard(str(BOARD))
    KEEP.append(b)
    pcb.ZONE_FILLER(b).Fill(b.Zones())
    pcb.SaveBoard(str(BOARD), b)
    for p, data in keep.items():
        p.write_bytes(data)
    print(f'standardized r1: {BOARD.name}  {w:.2f} x {h:.2f} mm, slot pitch {pitch:.2f}, '
          f'C2..C6 at x = {", ".join(f"{x:.2f}" for x in gap)}')


if __name__ == '__main__':
    main()
