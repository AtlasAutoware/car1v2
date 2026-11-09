# Car 1 v2

Car 1 v2 is the rebuild of car 1, Atlas Autoware's 1/10-scale self-driving race car for RoboRacer (F1TENTH).
The repository and the older notes call it "car v2" or "car 2". There is one car. Everything on car 1 today
and everything bought or donated for "car 2" is one pile of parts, and this page says which of them the car
uses, what still has to be bought, and what was left out to fit the money.

Status on 2026-11-09: designed and priced. Nothing ordered, nothing built, nothing merged. The work is on the
`rev-b-tht` branch (pull request #1).

| | |
| --- | --- |
| Design basis | rev B (`docs/REV_B.md`): one hand-soldered power board, the NVIDIA dev-kit carrier, a Flipsky ESC |
| Money | $1,831.92 expected in the bank; the car may use $1,500; stage 1 comes to $968.08, and $1,272.86 if every estimate turns out badly (`bom/car1v2/BUDGET.md`) |
| Student build guide | `docs/CAR1V2_BUILD.md` (session by session; the board itself is `docs/BUILD_POWER_BOARD.md`) |
| Student checklist | `docs/CAR1V2_CHECKLIST.md` (what to confirm, measure and test by hand) |
| Wiring | `docs/CAR1V2_WIRING.md` |
| Aero and cooling | `docs/AERO.md` |
| Speed against the competition | `docs/PERFORMANCE.md` |
| Independent review | `docs/review_car1v2_2026-11-09.md` ("pass with fixes" three times; what was done about each finding is at the end of this page) |

## What the car is made of, and why

| part | choice | from | why this one |
| --- | --- | --- | --- |
| Chassis | Traxxas Slash 4x4 | the "car 2" pile | It is not in use, so the whole car can be built and tested while car 1 keeps driving. The printed deck, pods and canopy in `mech/` were drawn for it. Four-wheel drive puts the power down more evenly than car 1's rear-drive Slash. |
| Motor | Holmes Hobbies Puller Pro 540, 2200 kV, sensored | already in that chassis | A crawler motor wound for smooth low-speed torque, which is where the car runs today (1.5 m/s cruise, 2.0 m/s cap). Holmes rates it to 50,000 rpm; 2200 kV on a full 4S pack is about 37,000 rpm with no load. Car 1's Castle 1415 stays in car 1. |
| Servo | INJORA INJS235 | the "car 2" pile | Fits the Slash 4x4 servo bay. 25 kg cm at 6.0 V and 35 kg cm at 8.4 V, 4.8 to 8.4 V (seller listings; INJORA's own page was not read). Car 1's Hitec D625MW stays in car 1, whose right steering lock is short. |
| ESC | the spare Flipsky FSESC | shelf | VESC firmware, the same interface car 1 uses, and it leaves car 1's ESC where it is. The servo signal comes from the FSESC as on car 1. |
| Lidar | RPLidar C1 | car 1, moved on swap day | The driving model and the simulator are built round it. 360 degrees, 10 Hz, 0.72 degree steps, 5 V at 0.23 A from USB (Slamtec datasheet). No new wiring, no new software. |
| Camera | Luxonis OAK-D Pro | car 1, moved on swap day | Same reason. It also brings stereo depth and an IMU (a 9-axis BNO086 on current units, a 6-axis BMI270 on units built mid 2021 to mid 2023), so the IMU costs nothing. |
| Computer | the second Jetson Orin Nano on NVIDIA's dev-kit carrier | shelf (Ragini, Nov 9) | Car 1 keeps its own Jetson. The new electronics are bench-tested on a real Jetson from the first day. |
| Battery | a 4S LiPo the team owns, charged on the iCharger | shelf | No cells, welder or charger to buy. The pack rides in the chassis battery bay. |
| Pack protection | JK-B1A8S10P smart BMS, a 100 A MIDI fuse, an XT90-S | Amazon, $66.49; small parts | Bought because the JBD in rev B is sold out at both US shops that list it. Per-cell under-voltage, over-current and short-circuit cut in the BMS; the fuse is the backstop. |
| Servo supply | Hobbywing UBEC 10A V2, set to 7.4 V | Hobbywing Direct, $24.99 | Replaces the Castle BEC 2.0 and the Castle Link programmer ($73.94 together). Its voltage is a jumper, so nothing needs programming. |
| Power board | ATLAS-PWR-1, unchanged copper | PCBWay | See below. |

Kept for later, not thrown away: the SICK TiM561, the LUCID Triton with the Edmund Optics lens, car 1's
Castle 1415 and D625MW, the UGREEN and Omni power banks (no longer needed on the car).

## What a sensor change would cost in software

The donated SICK lidar and LUCID camera are better instruments, and Edmund Optics is owed a case study with
the lens. Car 1 v2 is built so they bolt on later: the power board keeps the switched 12 V lidar feed and the
pads for the camera's 12 V regulator, the TiM561 plinth and Triton cradle in `mech/` share their mounting
holes with the C1 plinth and OAK-D cradle, and `setup_car1v2.sh --tim561` brings up the lidar's network. The
parts for that are priced at $84.64 (`bom/car1v2/cart_sensor_upgrade.csv`). What it costs is software time:

| change | what has to be redone | rough size |
| --- | --- | --- |
| RPLidar C1 to TiM561 | A new driver (`sick_scan_xd`) and the Ethernet link. The scan changes shape: 270 degrees instead of 360, a different beam count and rate, nothing behind the car. The policy's lidar input, the simulator's lidar model, the gap follower, emergency braking and the opponent tracker all read the C1's layout, so each needs the new layout or a resampling node in front of it. Then the driving model is retrained on the new scan in simulation and the 5-seed evaluation is repeated. | about a week for one student, plus a training run |
| OAK-D Pro to Triton | A new camera driver (Aravis already runs the Triton on the laptop), colour conversion and resizing on the Jetson instead of in the camera, and lens calibration: the 4 mm lens has about 20 % barrel distortion. Stereo depth and the camera's IMU go away. The detector has to be checked on the new images and probably retrained. The pilot page's video path changes. | one to two weeks |
| Chassis, motor and servo (this build) | VESC motor detection for the Puller Pro, the steering and speed calibration (the hallway tool on car 1 does it unattended), and the simulator's vehicle numbers: the Slash 4x4 wheelbase is 324 mm in the kit model, about 11 mm shorter than car 1. The steering path is unchanged: car 1 already steers through the FSESC. | one session |

The sizes are judgments, not measurements. The point is the order: move the car first with nothing changed
in the model's inputs, then change one sensor at a time in simulation before touching the car.

## The three things the car must do

**Drive itself with a lidar, a camera and the Jetson.** Car 1's sensors and stack on the second Jetson.

**Run everything from one 4S battery that is protected against a short circuit and over-discharge.** One
LiPo feeds the motor, the servo and, through the board's 5 A fuse and over-voltage cut-off, the Jetson. The
power banks are gone. A short anywhere downstream opens the BMS in well under a second and, if the BMS fails,
the 100 A fuse in the positive lead next to the pack. On the board, the Jetson's feed, the lidar feed, the
camera pads, the precharge path and the charge input each have a fuse or polyfuse. Three branches do not:
the UBEC's lead from the motor bus, the latch's lead from the pack bus, and the servo rail. Car 1 v2 adds an
in-line blade fuse to the first two (10 A and 7.5 A, in the small-parts cart).
Over-discharge is stopped three times, each a little lower than the last:

| level | who acts | what happens |
| --- | --- | --- |
| 14.0 V (3.50 V a cell) for 30 s | the Jetson's battery daemon, and the supervisor's warning at the same level; the VESC starts cutting motor current | the Jetson shuts itself down cleanly and the car switches off. This is where a normal run ends |
| 13.2 V (3.30 V a cell) for 10 s | the supervisor; the VESC stops the motor | the backstop if the Jetson did not act: the supervisor asks it to shut down, then switches the car off |
| 3.00 V on any one cell | the BMS | the pack disconnects. This one works with every other part dead |

The BMS level is 3.00 V, as in rev B, not higher: the Pico's voltage reading can be a few tenths of a volt
off until it is compared with a meter (checklist E2), and the BMS must not cut before the supervisor has
shut the Jetson down. Stopping at 3.5 V a cell is the cautious choice for a LiPo. If runs end too early, the
level to raise or lower is `ATLAS_SHUTDOWN_CELL_V` in `/etc/atlas/atlas.conf`, not the BMS.

**Cut motor power from a hardware E-stop with no firmware in the path.** A normally closed button on the
tail opens a two-wire loop. The loop's level goes straight into a 74HCT08 AND gate whose output is the enable
of the main switch's gate driver (MIC5014) and of the precharge transistor. Open loop, broken wire or an
unplugged button all read as "stop". The Pico only supplies the other input of the gate, so it can open the
switch but cannot hold it closed. This is rev B's circuit, unchanged.

The independent review traced that path and agrees that nothing firmware-controlled is in series with it.
It found three limits, and they are stated here so nobody relies on more than is there:

- One Pico pin (GP10) sits on the loop's sense node so the firmware can see the E-stop. The firmware only
  reads it, and a test now fails the build if any file ever makes it an output. But a pin driven high by
  mistake could hold the node up against its 10 kOhm pull-down. The clean fix is a 47 kOhm resistor between
  the node and the pin. That needs either new copper or a one-resistor rework at the Pico's pin 14, and it is
  a decision for before the boards are ordered (see "Decisions" below).
- Rev B's last fallback is gone on this car: the Pico cannot tell the BMS to open, because the JK BMS is not
  on its serial port. If a main FET ever failed shorted, what is left is the VESC kill line and pulling the
  XT90-S.
- The E-stop cuts motor power. It does not brake. The car coasts, and the steering loses power with the
  motor bus. At walking pace that is a metre or two. At speed it is not a stop (`docs/PERFORMANCE.md`).

## The nice-to-haves

| wish | in stage 1? | how |
| --- | --- | --- |
| Battery telemetry on the Jetson | yes, pack level | The supervisor measures pack and motor-bus voltage and sends them once a second; the Jetson's battery daemon already falls back to that when no BMS answers. Cell voltages, current and temperature are in the JK phone app, not on the Jetson: the JK's serial port runs at 115200 baud and the board's optocouplers were chosen for the JBD's 9600. |
| IMU | yes | The OAK-D Pro's. |
| Laptop debugging over one USB-C cable | yes | The hub block on the board: the Jetson, the FSESC and the serial console behind one port. About $16 of parts at cart prices. |
| Built-in 18650 pack with USB-C charging | not yet; priced | It needs cells, a charger and a spot welder the team does not have: $508.07 with a welder, $185.29 if one can be borrowed. With stage 1 that is $1,476.15, which is under the cap only if every estimate holds; in the pessimistic case it is not. $323 of it is one welder and the prices are September quotes. Treat it as not yet affordable inside the cap. The board is built ready for it (only two plug-in modules are left off), so it can follow once the car drives. |

## The power board for this car

The board is rev B's ATLAS-PWR-1 with no copper changed, so the Gerbers from Oct 26 are still the ones to
upload (`boards/power/out/fab/atlas_power_gerbers_pcbway.zip`). Four things happened to it today:

1. **KiCad 10 checks, for the first time.** On the team laptop (KiCad 10.0.8): the electrical rules check
   reports 0 errors and 0 warnings. The design rules check with schematic parity reports 0 unconnected pads,
   0 errors and 47 warnings, all of them silkscreen: 33 labels touching other silkscreen, 11 labels clipped by
   solder-mask openings on the bare power copper, and 3 hub-module labels that run over through-hole pads of
   U601. The board house clips ink at pads, so none has an electrical effect. The reports are
   `boards/power/erc.rpt` and `drc.rpt`.
2. **One real mismatch fixed.** The parity check found three resistors (R801, R802, R805) marked "do not
   populate" in the schematic and not on the board. The board now carries the flag. No track or pad moved.
3. **A stage 1 population.** Fit everything except the camera's 12 V regulator (MOD402), the USB-C PD trigger
   (MOD501) and the CC/CV charger module (MOD502). `bom/car1v2/power_board_stage1.csv` lists every reference.
   The parts left on the board for those features (a few transistors, a TVS, a fuse holder) cost about $8 and
   mean the later upgrades are plug-in. Leave the 5 A fuse out of F501 (the charge input) so that branch is
   not live.
4. **One resistor value changed after the review: R419 is 470 ohm, not 10 kOhm.** R419 sits across the
   base of the transistor that shuts off the Jetson's feed on over-voltage. The TL431 that drives it can
   draw a few hundred microamps even when it is not tripped, and through 10 kOhm that is enough to shut the
   feed off for good. 470 ohm keeps the transistor off until 1.3 mA, above anything the idle TL431 draws,
   and still gives it 2 mA when the cut-off really trips. Same footprint, no copper change. This comes from
   datasheets, not from a bench: try the five parts on a breadboard first (checklist C5).

After the value changes, KiCad 10 was run once more on the laptop: 0 errors, 0 parity issues, the same 47
silkscreen warnings.

The silkscreen warnings were left alone. They are cosmetic, and clearing them means moving labels on a board
whose layout tools run on KiCad 7 here; the first order is five boards for hand assembly with the build guide
open. If a clean report matters for the sponsor article, it is an hour in KiCad's editor.

Five parts DigiKey cannot ship have substitutes, each read on its DigiKey page today for size and stock:

| refs | was | now | fits? |
| --- | --- | --- | --- |
| C101 to C103 | Panasonic EEU-FR1V681, 680 uF 35 V | EEU-FM1V681: 12.5 mm can, 22 mm seated, 5.0 mm pitch | yes; 1 mm under the tray's 23 mm limit |
| C404 | EEU-FR1C102, 1000 uF 16 V | EEU-FM1C102: 10 mm can, 22 mm seated, 5.0 mm pitch | yes; 6 mm taller than drawn |
| C405 | EEU-FR1V221, 220 uF 35 V | EEU-FM1V151: **150 uF** 35 V, 8 mm can, 3.5 mm pitch | yes, but it is a value change: no 220 uF 35 V part in an 8 mm can was in stock |
| five 10 uF 1210 | Murata GRM32ER71H106KA12L | Samsung CL32B106KBJNNNE, 10 uF 50 V X7R | yes |
| C104, C603, C604 | TDK C3216X7R1H105K160AB (out until March 2027) | KEMET C1206C105K5RACTU, 1 uF 50 V X7R | yes, by its part number; in the cart |

The first version of this list had two "long-lead" Panasonic parts that the review showed were different can
sizes. They are still sitting in the DigiKey cart and are marked for deletion in `cart_digikey.csv`. The FM
series replaces the FR series; its ripple-current rating was not compared with what the design needs.

## Settings to make

All of these are starting values to confirm on the bench, not measured ones.

| where | setting | value |
| --- | --- | --- |
| JK BMS (phone app) | cells, chemistry | 4, Li-ion |
| | cell under-voltage cut, release | 3.00 V, 3.20 V |
| | cell over-voltage cut | 4.25 V (regen on a full pack must not trip it) |
| | discharge over-current | 80 A with the longest delay offered up to 2 s |
| | charge over-current | 40 A or more, so braking cannot trip it |
| FSESC (VESC Tool) | motor current max, battery current max | 60 A, 60 A (car 1 runs 45 A commanded) |
| | battery current max regen | -12 A to start. -30 A for racing, only if the pack's label allows a 30 A charge burst (`docs/PERFORMANCE.md`) |
| | max ERPM | 48,300, which is 13.5 m/s with a 15 / 54 gearing |
| | battery cut-off start, end | 14.0 V, 13.2 V |
| | maximum input voltage | 18 V |
| | servo output, kill switch on ADC2, UART app at 115200 | as rev B (`docs/SOFTWARE.md`) |
| Hobbywing UBEC | output | 7.4 V, before the servo is plugged in. The page lists 6.0, 7.4 and 8.4 V and does not say how it is selected: read its leaflet |
| Chassis | pinion / spur | 15 / 54 (`docs/PERFORMANCE.md`); check what is fitted first |
| Pico | `car_profile.py` | `SETTINGS = Car1v2Lipo` (the default in the repo) |
| Jetson | `setup_car1v2.sh` | 25 W mode, lidar feed off, shutdown at 3.50 V a cell held for 30 s |

## What was analysed while designing

- **Aerodynamics and cooling** (`docs/AERO.md`): a CFD model of the car built from the same CAD the parts are
  printed from, run with no wing and with the kit's wing at three angles. At 8 m/s the car has 1.6 N of drag
  and the wing adds at most 0.12 N of downforce; at the 2 m/s cap that is 0.007 N on a car that weighs about
  50 N. So the wing is left off, which also takes two posts out of the lidar's rear view. The pod vents
  (28.8 cm2) are enough for the 2.9 l/s of air that 35 W needs, and the fans move it, not the car's speed.
  The model is coarse and nothing in it was measured.
- **Camera mount strength**: a hand check in `mech/car1v2.py`. A 20 g stop puts about 20 N on the upright and
  1.7 MPa in it, a factor of about 12 against a cautious 20 MPa for PETG-CF across its layers.
- **Fit**: the C1 plinth's screw slots clear the four deck inserts by 1.7 mm, the lidar's top is 57 mm under
  the camera base, and the two M3 screw heads under the camera clear the upright by 3.9 mm.
- **Firmware**: 126 tests pass on the simulated board, five of them new for this car (runs with a BMS that
  never answers, E-stop cut, the LiPo levels). The Jetson tools' 77 tests pass unchanged.

SOLIDWORKS: the team's Student Team sponsorship (20 activations, to July 2028) arrived on Nov 9. The STEP
files in `sim/aero/out/step/` and `mech/out/` open in it, and `docs/AERO.md` ends with the Flow Simulation
set-up that repeats the CFD cases, so the students can check these numbers on their own machines.

## Building it without stopping car 1

1. Sections A to C of the checklist (confirm the shelf, measure, three bench tests). No money spent yet.
2. Order: boards, the DigiKey cart, the BMS, the UBEC, small parts. Print the fit coupons, then the kit.
3. Build and bench-test the board (two sessions). Mount it with the second Jetson and the spare FSESC on the
   new chassis. Bring-up, section E. Car 1 has not been touched.
4. Install the driving stack on the second Jetson and drive the new chassis by joystick.
5. Swap session: car 1's lidar and camera move across (two mounts, six screws, two USB leads), calibration,
   first autonomous lap at walking pace. Moving them back restores car 1.

## What has not been verified

- **The bank balance today.** Truthifi's free plan was out of credits; the figures are the ones in the brief.
- **Prices not read today**: the PCBWay quote (Oct 26), the import duty on the boards (35 % assumed from
  JLCPCB's published rate), every "small parts" line, six low-value DigiKey lines that would not go into the
  cart from a pasted list, and all of phase 2 and the sensor upgrade. `BUDGET.md` shows how many dollars sit
  in each class. Sales tax is assumed at 6 %.
- **The JK BMS**: its size comes from the Amazon listing; its wake-up procedure, lead positions and whether
  its discharge limit can be set as above come from nowhere yet. Read its manual first.
- **The LiPo packs**: nobody has given their size or ratings. The battery bay, the deck's pack opening and
  the fuse choice wait on that (checklist A1, B7). This is the biggest open mechanical item.
- **The second Jetson**: confirmed as NVIDIA's dev kit; its module, storage and JetPack version are not.
- **Mount hole patterns**: the C1's and the OAK-D Pro's (checklist B1, B2).
- **INJS235 and Puller Pro numbers** come from seller pages, not from the makers' datasheets.
- **Nothing in this revision has run on hardware**, as in rev B: not the board, the firmware or the scripts.
- **Not produced**: a deck with a LiPo-sized opening and an interference check of the JK BMS holder against
  the rest of the car. Both wait on measurements (checklist A1, B4, B7).
