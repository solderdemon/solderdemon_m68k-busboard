"""Update busboard documentation for the two-input power corner."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'README.md'; s=p.read_text()
s=s.replace('the power circuit and protection match the SolderDemon 6502 busboard; both busboards share one silkscreen layout.', 'the power circuit provides two selectable 5 V inputs and TVS protection.')
s=s.replace('  - USB Type-C receptacle (`J3`, power only, 5.1 kΩ CC pull-downs `R2` / `R3`)\n', '')
s=s.replace('the `USB`, `DC` or `TERM` row', 'the `DC` or `TERM` row (the third row is unused)')
s=s.replace('through-hole components except the USB-C receptacle', 'through-hole components')
s=s.replace('| **J3** | USB-C 5V | GCT USB4105-xx-A, 16P | 5V USB power input, CC1/CC2 pulled down with 5.1 kΩ |\n', '')
s=s.replace('odd pins 1 terminal, 3 DC jack, 5 USB-C; even pins the common input', 'odd pins 1 terminal and 3 DC jack; pin 5 unused; even pins the common input')
s=s.replace('through USB-C, the `J2` terminal or the barrel jack', 'through the `J2` terminal or the barrel jack')
s=s.replace('| **J3** | USB-C 16P | GCT USB4105-xx-A, top mount | USB Type-C power receptacle |\n', '')
s=s.replace('Radial electrolytic, D6.3 mm, P2.5 mm, upright', 'Radial electrolytic, D10 mm, P3.5 mm, upright')
s=s.replace('| **R2, R3** | 5.1 kΩ | Axial DIN0207, P10.16 mm | USB-C CC1 / CC2 pull-down resistors |\n', '')
s=s.replace('| ![Top View](solderdemon_m68k-busboard-top.png) | ![Bottom View](solderdemon_m68k-busboard-bottom.png) |', '| Preview predates the latest changes | Preview predates the latest changes |')
s=s.replace('above the USB tolerance of 5.25 V', 'above 5.25 V')
p.write_text(s)
p=root.parent/'README.md'; s=p.read_text(); s=s.replace('Силова частина, захист і PWR LINK — ті самі, що на 6502-busboard, деталь у деталь: USB-C, DC-гніздо або клеми, вибір джерела перемичкою SOURCE (завжди одне)', 'Живлення через DC-гніздо або два піни, вибір джерела перемичкою SOURCE (завжди одне)'); s=s.replace('живлення на правому торці, 175 × 99 мм', 'живлення на правому торці, 185 × 99 мм'); p.write_text(s)
