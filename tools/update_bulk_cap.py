"""Migrate the existing routed board to the 10 mm C1 and lowered LED1.

Run once with KiCad's Python after build_sch.py. The normal full rebuild is
standard_pcb.py; this migration preserves the existing routed bus when its
historical Git input is unavailable.
"""
from pathlib import Path
import pcbnew as pcb

root = Path(__file__).resolve().parents[1]
path = root / 'design' / 'solderdemon_m68k-busboard.kicad_pcb'
stock = Path('/usr/share/kicad/footprints/Capacitor_THT.pretty')
if not stock.exists():
    stock = Path('C:/Program Files/KiCad/10.0/share/kicad/footprints/Capacitor_THT.pretty')
b = pcb.LoadBoard(str(path))
old = b.FindFootprintByReference('C1')
assert old.GetFPID().GetLibItemName() == 'CP_Radial_D6.3mm_P2.50mm', 'board already migrated or unexpected C1'
f = pcb.FootprintLoad(str(stock), 'CP_Radial_D10.0mm_P3.50mm')
f.SetFPID(pcb.LIB_ID('Capacitor_THT', 'CP_Radial_D10.0mm_P3.50mm'))
f.SetReference('C1'); f.SetValue(old.GetValue()); f.SetPath(old.GetPath())
f.SetPosition(old.GetPosition()); f.SetOrientation(old.GetOrientation())
for pad in f.Pads():
    pad.SetNet(next(p for p in old.Pads() if p.GetNumber() == pad.GetNumber()).GetNet())
b.Remove(old); b.Add(f)
led = b.FindFootprintByReference('LED1')
positions = [p.GetPosition() for p in led.Pads()]
delta = pcb.VECTOR2I(0, pcb.FromMM(2))
for track in b.GetTracks():
    if track.GetStart() in positions: track.SetStart(track.GetStart() + delta)
    if track.GetEnd() in positions: track.SetEnd(track.GetEnd() + delta)
led.SetPosition(led.GetPosition() + delta)
pcb.ZONE_FILLER(b).Fill(b.Zones())
pcb.SaveBoard(str(path), b)
print('Updated C1 and moved LED1 down 2 mm')
