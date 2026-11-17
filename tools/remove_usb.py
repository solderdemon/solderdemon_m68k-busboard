"""Remove the USB input from the previously generated routed busboard, once."""
from pathlib import Path
import pcbnew as pcb
root = Path(__file__).resolve().parents[1]
path = root / 'design' / 'solderdemon_m68k-busboard.kicad_pcb'
b = pcb.LoadBoard(str(path))
keep = []
usb = b.FindFootprintByReference('J3')
assert usb, 'USB input already removed'
ground = [p.GetPosition() for p in usb.Pads() if p.GetNetname() == 'GND']
for t in list(b.GetTracks()):
    if t.GetNetname() in ('VBUS', 'CC1', 'CC2') or (t.GetNetname() == 'GND' and (t.GetStart() in ground or t.GetEnd() in ground)):
        b.Remove(t); keep.append(t)
for ref in ('J3', 'R2', 'R3'):
    f = b.FindFootprintByReference(ref); b.Remove(f); keep.append(f)
for d in list(b.GetDrawings()):
    if isinstance(d, pcb.PCB_TEXT) and d.GetText() in ('USB', 'USB-C 5V'):
        for group in b.Groups():
            if any(i.m_Uuid.AsString() == d.m_Uuid.AsString() for i in group.GetItems()): group.RemoveItem(d)
        b.Remove(d); keep.append(d)
for pad in b.FindFootprintByReference('JP2').Pads():
    if pad.GetNumber() == '5':
        net = pcb.NETINFO_ITEM(b, 'unconnected-(JP2-Pin_5-Pad5)'); b.Add(net); pad.SetNet(net)
pcb.ZONE_FILLER(b).Fill(b.Zones())
pcb.SaveBoard(str(path), b)
print('Removed USB-C input, CC resistors, associated tracks and labels')
