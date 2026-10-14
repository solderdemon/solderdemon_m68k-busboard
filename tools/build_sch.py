"""SolderDemon m68k busboard standardized r1: the schematic, generated.

The bus is unchanged from r2: five 2x32 slots, every pin on the same net in every slot, except
pin 2 of BUS1 (the host), which is VCC_HOST and joins VCC through the PWR LINK jumper JP1.

The power section is the 6502 busboard's, part for part and net for net:
    J3 USB-C, J1 DC jack, J2 terminal -> JP2 SOURCE (one jumper cap picks one input) -> VIN_DC
    -> SW1 POWER (DPST, poles in parallel) -> VCC; D1 1.5KE6.8A TVS across VCC; C1 470 uF;
    LED1 PWR GOOD with R1; R2/R3 the USB-C CC pull-downs; one 100 nF per slot (C2 on VCC_HOST).
The 6502 board's /RESET pull-up and capacitor belong to the 6502 bus and have no counterpart.

    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/build_sch.py      (then tools/standard_pcb.py)
"""
from pathlib import Path
import shutil, subprocess, sys, tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cardlib as g

ROOT = Path(__file__).resolve().parents[1]
NAME = 'solderdemon_m68k-busboard'
REV, DATE = 'r1', '2026-10-14'

# Bus pin -> net, as in r2 (odd pins: address side, even pins: control/data side).
BUS = ['A1', 'VCC', 'A2', 'CPUCLK', 'A3', 'GND', 'A4', 'VPA', 'A5', 'E', 'A6', 'VMA', 'A7', 'IRQ3',
       'A8', 'IOSEL', 'A9', 'EXPSEL', 'A10', 'CPUFC0', 'A11', 'CPUFC1', 'A12', 'CPUFC2', 'A13', 'IPL0',
       'A14', 'IPL1', 'A15', 'IPL2', 'A16', 'LDS', 'A17', 'UDS', 'A18', 'RESET', 'A19', 'D15', 'A20', 'D14',
       'A21', 'D13', 'A22', 'D12', 'A23', 'D11', 'AS', 'D10', 'BERR', 'D9', 'BG', 'D8', 'BGACK', 'D7',
       'BR', 'D6', 'DTACK', 'D5', 'RW', 'D4', 'D0', 'D3', 'D1', 'D2']
assert len(BUS) == 64

d = g.Design(NAME, 'SolderDemon m68k Bus Board', REV, DATE)
conn = d.standard('Connector_Generic', 'Conn_02x32_Odd_Even', f'{NAME}:pin-2X32')
for i in range(5):
    nets = {n + 1: net for n, net in enumerate(BUS)}
    if i == 0:
        nets[2] = 'VCC_HOST'
    d.add(f'BUS{i + 1}', conn, 'Conn_02x32_Odd_Even', nets, (60 + 90 * i, 70))

C = d.standard('Device', 'C', 'SolderDemonCaps:C_Radial_5.08mm')
CP = d.standard('Device', 'C_Polarized', 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm')
R = d.standard('Device', 'R', 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal')
LED = d.standard('Device', 'LED', 'LED_THT:LED_D5.0mm')
TVS = d.standard('Diode', '1.5KExxA', 'Diode_THT:D_DO-201AE_P15.24mm_Horizontal')
SW = d.standard('Switch', 'SW_DPST', f'{NAME}:NKK-M2021SS1W01')
JACK = d.standard('Connector', 'Jack-DC', 'Connector_BarrelJack:BarrelJack_Horizontal')
TERM = d.standard('Connector', 'Conn_01x02_Pin', 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
USB = d.standard('Connector', 'USB_C_Receptacle_USB2.0_16P',
                 'Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal')
SRC = d.standard('Connector_Generic', 'Conn_02x03_Odd_Even', 'Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical')
LINK = d.standard('Jumper', 'Jumper_2_Open',
                  'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical')
HOLE = d.standard('Mechanical', 'MountingHole_Pad', 'MountingHole:MountingHole_3.2mm_M3_Pad')

Y = 220
d.add('J3', USB, 'USB-C 5V', {'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND', 'SH': 'GND',
                              'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS', 'A5': 'CC1', 'B5': 'CC2',
                              'A6': None, 'A7': None, 'B6': None, 'B7': None, 'A8': None, 'B8': None}, (60, Y))
d.add('R2', R, '5.1k', {1: 'CC1', 2: 'GND'}, (120, Y - 20))
d.add('R3', R, '5.1k', {1: 'CC2', 2: 'GND'}, (120, Y))
d.add('J1', JACK, 'Jack-DC', {1: 'VIN_JACK', 2: 'GND'}, (120, Y + 30))
d.add('J2', TERM, '5V IN', {1: 'VIN_TERM', 2: 'GND'}, (160, Y + 30))
d.add('JP2', SRC, 'SOURCE', {1: 'VIN_TERM', 2: 'VIN_DC', 3: 'VIN_JACK', 4: 'VIN_DC', 5: 'VBUS', 6: 'VIN_DC'}, (200, Y))
d.add('SW1', SW, 'POWER', {1: 'VIN_DC', 2: 'VCC', 3: 'VIN_DC', 4: 'VCC'}, (250, Y))
d.add('D1', TVS, '1.5KE6.8A', {1: 'VCC', 2: 'GND'}, (300, Y))
d.add('C1', CP, '470uF', {1: 'VCC', 2: 'GND'}, (330, Y))
d.add('LED1', LED, 'PWR GOOD', {1: 'LED_K', 2: 'VCC'}, (360, Y))
d.add('R1', R, '1k', {1: 'GND', 2: 'LED_K'}, (390, Y))
d.add('JP1', LINK, 'PWR LINK', {1: 'VCC_HOST', 2: 'VCC'}, (250, Y + 40))
for i in range(5):
    d.add(f'C{i + 2}', C, '100nF', {1: 'VCC_HOST' if i == 0 else 'VCC', 2: 'GND'}, (300 + 25 * i, Y + 40))
for i in range(8):
    d.add(f'H{i + 1}', HOLE, 'MountingHole_Pad', {1: 'GND'}, (60 + 25 * i, Y + 80), bom=False)

with tempfile.TemporaryDirectory() as tmp:
    parts, nets = d.write(tmp, [])
    shutil.copy(Path(tmp) / f'{NAME}.kicad_sch', ROOT / f'{NAME}.kicad_sch')
subprocess.run(['C:/Program Files/KiCad/10.0/bin/kicad-cli.exe', 'sch', 'export', 'bom',
                '-o', str(ROOT / f'{NAME}-bom.csv'), str(ROOT / f'{NAME}.kicad_sch')],
               check=True)
print(f'{NAME}.kicad_sch: {parts} parts, {nets} nets')
