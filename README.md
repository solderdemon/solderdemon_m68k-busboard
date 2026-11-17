# SolderDemon m68k Busboard

A five-slot backplane with one host slot, four expansion slots, and selectable 5 V DC power inputs.

Built for the SolderDemon m68k host and compatible with [rosco_m68k](https://github.com/rosco-m68k/rosco_m68k) expansion cards. Based on the roscbus-01 backplane.

**Status.** r1 fabrication files are available.

## Start here

- [KiCad project](design/solderdemon_m68k-busboard.kicad_pro)
- [Schematic (PDF)](manufacturing/solderdemon_m68k-busboard-schematic.pdf)
- [Gerbers and drill files](manufacturing/solderdemon_m68k-busboard-gerbers.zip)
- [Connecting the host and cards](#connecting-the-host-and-the-cards)

## Features

- **Slot Architecture:** 5 identical slots (`BUS1`–`BUS5`), 2×32 vertical pin headers (2.54 mm / 0.1" pitch), 29.21 mm slot pitch; every slot carries the full 64-pin main bus; pin 1 of each slot is marked with a silkscreen triangle. `BUS1` (labelled `HOST`; the others `SLOT 1`–`SLOT 4`) is the host slot: the 20 mm strip to its left is kept free of tall parts so the host's components can face outwards
- **Power Inputs:** 5V DC only, from one of, down the right-hand edge:
  - DC Barrel Jack (`J1`, center-positive)
  - 2-pin 2.54 mm terminal (`J2`, under the jack)
- **Source Selection:** one jumper cap on the 2×3 header `JP2` (`SOURCE`) picks the input — the `DC` or `TERM` row (the third row is unused). Only the selected input reaches the switch, so two adapters are never tied together. No diodes, no voltage drop
- **Power Switch:** NKK M2021SS1W01 DPST toggle (`SW1`, both poles in parallel) between the selected input and `VCC`
- **Input Protection:** 1.5KE6.8A unidirectional TVS (`D1`, DO-201AE) across `VCC` / `GND`: 5.8 V standoff, above 5.25 V, so it does not leak on a good supply; it clamps over-voltage and conducts on reversed polarity
- **Host Power Link:** through-hole 1×2 jumper header `JP1` (`PWR LINK`), lying across the line midway between `HOST` and `SLOT 1`, under `C2`. It joins the host slot's pin 2 (`VCC_HOST`) to the bus `VCC`. Remove the jumper to power the host from its own `J5` while this board powers the cards
- **Filtering & Status:** 470 µF bulk reservoir (`C1`, upright) at the top right with `LED1` below it, as on the 6502 busboard. One 100 nF capacitor per slot stands vertically exactly halfway between two slot centres (`C2`–`C5`), its upper pad level with the slots' pin 1; `C6` continues the same 29.21 mm rhythm half a pitch past `SLOT 4`. Each is fed straight along the pin-1 row from its slot's pin 2; `C2` is on `VCC_HOST`
- **Form Factor:** 185 × 99 mm 2-layer PCB, through-hole components; power connectors and switch on the right-hand end, away from the host
- **Mounting:** 8× M3 mounting holes (3.2 mm) with grounded pads, 5.08 mm in from the edges as on the 6502 busboard; the four middle holes sit on the same half-pitch lines as the capacitors, above `C3` and `C5` and below the slots

## Pinout

All five slots are wired 1:1 to the main bus:

| Pin | Signal | Description | Pin | Signal | Description |
|:---:|:---|:---|:---:|:---|:---|
| **1** | **A1** | Address bus bit 1 | **2** | **VCC** | +5V power rail |
| **3** | **A2** | Address bus bit 2 | **4** | **CPUCLK** | CPU system clock |
| **5** | **A3** | Address bus bit 3 | **6** | **GND** | System ground (0V) |
| **7** | **A4** | Address bus bit 4 | **8** | **VPA** | Valid Peripheral Address |
| **9** | **A5** | Address bus bit 5 | **10** | **E** | 6800-style E clock |
| **11** | **A6** | Address bus bit 6 | **12** | **VMA** | Valid Memory Address |
| **13** | **A7** | Address bus bit 7 | **14** | **IRQ3** | Active-low interrupt input on the SolderDemon m68k host |
| **15** | **A8** | Address bus bit 8 | **16** | **IOSEL** | I/O select |
| **17** | **A9** | Address bus bit 9 | **18** | **EXPSEL** | Expansion select |
| **19** | **A10** | Address bus bit 10 | **20** | **FC0** | CPU function code 0 |
| **21** | **A11** | Address bus bit 11 | **22** | **FC1** | CPU function code 1 |
| **23** | **A12** | Address bus bit 12 | **24** | **FC2** | CPU function code 2 |
| **25** | **A13** | Address bus bit 13 | **26** | **IPL0** | Interrupt priority level 0 |
| **27** | **A14** | Address bus bit 14 | **28** | **IPL1** | Interrupt priority level 1 |
| **29** | **A15** | Address bus bit 15 | **30** | **IPL2** | Interrupt priority level 2 |
| **31** | **A16** | Address bus bit 16 | **32** | **LDS** | Lower Data Strobe |
| **33** | **A17** | Address bus bit 17 | **34** | **UDS** | Upper Data Strobe |
| **35** | **A18** | Address bus bit 18 | **36** | **RESET** | System reset |
| **37** | **A19** | Address bus bit 19 | **38** | **D15** | Data bus bit 15 |
| **39** | **A20** | Address bus bit 20 | **40** | **D14** | Data bus bit 14 |
| **41** | **A21** | Address bus bit 21 | **42** | **D13** | Data bus bit 13 |
| **43** | **A22** | Address bus bit 22 | **44** | **D12** | Data bus bit 12 |
| **45** | **A23** | Address bus bit 23 | **46** | **D11** | Data bus bit 11 |
| **47** | **AS** | Address Strobe | **48** | **D10** | Data bus bit 10 |
| **49** | **BERR** | Bus Error | **50** | **D9** | Data bus bit 9 |
| **51** | **BG** | Bus Grant | **52** | **D8** | Data bus bit 8 |
| **53** | **BGACK** | Bus Grant Acknowledge | **54** | **D7** | Data bus bit 7 |
| **55** | **BR** | Bus Request | **56** | **D6** | Data bus bit 6 |
| **57** | **DTACK** | Data Transfer Acknowledge | **58** | **D5** | Data bus bit 5 |
| **59** | **R/W** | Read / Write | **60** | **D4** | Data bus bit 4 |
| **61** | **D0** | Data bus bit 0 | **62** | **D3** | Data bus bit 3 |
| **63** | **D1** | Data bus bit 1 | **64** | **D2** | Data bus bit 2 |

### Connecting the host and the cards

- **Host board in `BUS1`.** Fit a **right-angle 2×32 socket on the bottom side** of the `solderdemon_m68k` board in the J3 holes, body overhanging the left edge, instead of the vertical header. The host then stands in `BUS1` with its component side facing outwards (left), all its connectors reachable, pins matched 1:1. The socket must be on the bottom side: on the top side the pin order along the row comes out reversed. The host sits about 2 mm lower than the cards because J3 is 5.45 mm from the board edge; its tallest parts reach roughly the left edge of this board.
- **Host on a cable.** With the stock vertical header on J3 the host can instead hang off a 64-way IDC ribbon cable with a socket at both ends, plugged into any slot. The cable is wired 1:1; keep it short (under about 20 cm) because the bus is unbuffered and has a single GND line. Neither header is keyed: match the cable's pin 1 (red stripe) to the triangle on the slot and to pin 1 on J3, otherwise the bus board's own 5V lands on the CPU data lines.
- **Cards.** Expansion cards use a right-angle 2×32 socket on the component side of their right edge, pin 1 at the bottom. Plugged in, every card stands with its components facing left, towards the host slot, so cards look at the back of their left-hand neighbour and the `BUS5` card turns its back to the power section. A card inserted the other way round gets `VCC` on a data line, so check the triangle before powering up.
- **One power source.** With `JP1` fitted, the host's 5V rail is the bus `VCC`: power the system from this board only. To power the host from its own `J5` (for example during bring-up), take `JP1` off — the cards still run from this board, the host from its own supply.

### Power Interfaces & Control

| Designator | Label | Type / Footprint | Description |
|:---|:---|:---|:---|
| **J1** | DC 5V ONLY | Barrel jack 5.5 / 2.1 mm | 5V DC input (center-positive, polarity symbol on the silkscreen) |
| **J2** | GND / +5V | Pin header 1×2, 2.54 mm | 5V input for a power cable, pin 1 = +5V (`VIN_TERM`), pin 2 = GND |
| **JP2** | SOURCE | Pin header 2×3, 2.54 mm, one jumper cap | Source select: odd pins 1 terminal and 3 DC jack; pin 5 unused; even pins the common input |
| **SW1** | POWER | NKK M2021SS1W01, DPST toggle | Main power ON / OFF, both poles in parallel |
| **D1** | — | 1.5KE6.8A, DO-201AE (THT) | TVS protection diode across `VCC` / `GND` |
| **JP1** | PWR LINK | Pin header 1×2, 2.54 mm, jumper cap | Links the host slot's `VCC_HOST` to `VCC` (fitted by default) |
| **LED1** | — | LED 5 mm | PWR GOOD: `VCC` present |

> **5V only.** There is no voltage regulator on this board. Supply regulated 5V through the `J2` terminal or the barrel jack. If more than ~6.5V or reversed polarity is applied, `D1` starts conducting and shorts the input. There is no fuse, so this relies on the supply's own over-current protection — a supply without it can destroy `D1`.

> **One input at a time, by design.** `JP2` connects exactly one input to the switch; the others stay open even when plugged in.

## Bill of Materials (BOM)

| Reference | Value | Package / Footprint | Notes |
|:---|:---|:---|:---|
| **BUS1–BUS5** | Conn_02x32 | Pin header 2×32, 2.54 mm, vertical | Bus slots |
| **J1** | Jack-DC | Barrel jack 5.5 / 2.1 mm, horizontal | 5V DC input |
| **J2** | 5V IN | Pin header 1×2, 2.54 mm, vertical | 5V terminal input |
| **JP1** | PWR LINK | Pin header 1×2, 2.54 mm + jumper cap | Host power link |
| **JP2** | SOURCE | Pin header 2×3, 2.54 mm + jumper cap | Source select |
| **SW1** | M2021SS1W01 | NKK M-series DPST ON-OFF toggle switch | Main power switch |
| **D1** | 1.5KE6.8A | DO-201AE, Axial P15.24 mm (THT) | Unidirectional TVS diode |
| **LED1** | LED 5 mm | Radial D5.0 mm (THT) | PWR GOOD indicator |
| **C1** | 470 µF | Radial electrolytic, D10 mm, P3.5 mm, upright | Bulk reservoir capacitor |
| **C2–C6** | 100 nF | Radial ceramic, 5.08 mm lead pitch | One per slot (`C2`: host, on `VCC_HOST`) |
| **R1** | 1 kΩ | Axial DIN0207, P10.16 mm | LED1 current-limiting resistor |
| **H1–H8** | Mounting Hole | 3.2 mm M3, GND pad | Mounting holes |
| **LOGO1** | SolderDemon logo | Silkscreen only | Board-only graphic, not in the BOM |

Machine-readable BOM: [solderdemon_m68k-busboard-bom.csv](design/solderdemon_m68k-busboard-bom.csv).

## Design files

- **KiCad Project (KiCad 10):** `design/solderdemon_m68k-busboard.kicad_pro`, `design/solderdemon_m68k-busboard.kicad_sch`, `design/solderdemon_m68k-busboard.kicad_pcb`
- **How r1 is made:** `tools/build_sch.py` generates the schematic and BOM; `tools/standard_pcb.py` rebuilds from the routed bus at git `3a0c432`, brings over the 6502 power circuit and applies the revised placement and routing; `../tools/brand/apply_identity.py solderdemon_m68k-busboard` draws the shared labels and identity
- **Footprint Library:** `solderdemon_m68k-busboard.pretty/` (bus header, capacitor, resistor and power switch footprints, SolderDemon logo)
- **Logo:** the shared SolderDemon logo from `../tools/brand/` (library `SolderDemonBrand`)
- **Schematic PDF:** [solderdemon_m68k-busboard.pdf](solderdemon_m68k-busboard.pdf)
- **Fabrication files:** [manufacturing/](manufacturing/)
- **PCB Specs:** 2-layer board, 185 × 99 mm, 1.6 mm thickness, standard 1 oz copper, HASL / ENIG finish
- **Design Verification:** [DRC Report](solderdemon_m68k-busboard-drc.rpt) (0 violations, 0 unconnected, 0 schematic parity issues), [ERC Report](solderdemon_m68k-busboard-erc.rpt) (0 violations)

<!-- repository-layout -->
## Repository layout

- [`design/`](design/solderdemon_m68k-busboard.kicad_pro): KiCad project, schematic sheets, PCB, local libraries and design data. Open the project directly here.
- [`code/firmware/`](code/firmware/): ROM and programmable-logic sources and programming files.
- [`code/software/`](code/software/): drivers, examples and applications.
- [`code/build/`](code/build/): local build products; ignored by Git except for its README.
- [`tools/`](tools/): generators, simulations and export scripts. Run commands from the repository root unless stated otherwise.
- [`manufacturing/`](manufacturing/): fabrication packages.

This passive busboard has no firmware or software; the code directories document that explicitly.
Design files and documentation are generated by scripts in `tools/`; change the sources and regenerate. Keep `.kicad_pro` as the source of DRC rules.
<!-- /repository-layout -->

## Licences and attribution

- **Hardware:** [CERN Open Hardware Licence v1.2](LICENCE.hardware.txt).

Based on the roscbus-01 backplane for [rosco_m68k](https://github.com/rosco-m68k/rosco_m68k), © 2020 Ross Bamford & Contributors. The SolderDemon r1 revision updates the power section, component placement and board identity. Copyright © 2026 SolderDemon. Original authorship and licence notices are retained.
