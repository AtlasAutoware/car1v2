# Car 1 v2: build and bring-up guide

This is the students' guide for building car 1 v2, session by session. It does not repeat the long soldering
guide. `docs/BUILD_POWER_BOARD.md` is still the guide for the board itself, and this page says, step by step,
what is different for car 1 v2 and what comes before and after the board. Read `docs/CAR1V2.md` first so you
know what the car is.

Three files go with this one:

- `docs/CAR1V2_CHECKLIST.md`: the measurements and tests, with boxes to tick. This guide points at its items
  as A1, B3, E2 and so on.
- `docs/CAR1V2_WIRING.md`: every cable on one diagram.
- `bom/car1v2/power_board_stage1.csv`: every part on the board, marked "fit" or "leave off".

Car 1 keeps driving through all of it. Nothing comes off car 1 until session 8.

## Safety, on top of the board guide's safety section

- **The LiPo is the most dangerous thing on the table.** It can deliver hundreds of amps into a short and it
  burns if it is punctured, crushed, over-charged or run flat. It lives in a LiPo bag or an ammunition tin when
  it is not in the car. Charge it only on the balance charger, in balance mode, with the balance plug in, at
  1C or less (a 5000 mAh pack: 5 A), on a surface that does not burn, with someone in the room.
- **Never work on the wiring with the XT90-S plugged in.** Pulling the XT90-S is the "off" you can trust. The
  power button and the E-stop are not for working on the car.
- **A puffy, dented or hot pack is retired.** Do not charge it. Tell an adult.
- **Stop at 3.5 V a cell.** The car does this for you once it is set up. On the bench, watch the meter.
- An adult is present for session 6 (first time on the pack) and for every test that pulls more than a few
  amps.
- Wheels off the ground whenever the motor can turn and you are not driving.

## Session 0: before any money is spent

Checklist sections A, B and C. About two hours with the parts on the table.

1. Section A: look at every part the design calls "owned" and write down what it really is. A1 (the LiPo
   packs) and A3 (which Flipsky is which) change the design if they come out differently, so do those first.
2. Print the two fit coupons (`mech/out/stl/fit_coupon_front.stl`, `fit_coupon_rear.stl`), put them on the
   Slash 4x4 chassis and do the measurements in section B that the checklist takes from MEASURE_FIRST.
3. Section C: the three bench tests that need no new board (C1, C2 if the UBEC has arrived, C3).
4. Hand the numbers to whoever holds the repo. If A1 says the LiPo does not fit the battery bay or the deck's
   opening, the deck is redrawn before anything is printed.

Nothing is ordered until Ragini says so.

## Session 1: check the kits when the orders arrive

1. Count the DigiKey bag against `bom/car1v2/power_board_stage1.csv`, block by block, as in the board guide's
   "Check the parts kit". Lines marked "leave off" will not be in the bag. That is correct.
2. These parts are substitutes for the ones the board guide names. Same value, same footprint:

   | on the board | the board guide says | in the bag |
   | --- | --- | --- |
   | C101, C102, C103 (680 uF 35 V) | Panasonic EEU-FR1V681 | EEU-FR1V681L, the same capacitor with long leads. Trim them |
   | C404 (1000 uF 16 V) | EEU-FR1C102 | EEU-FR1C102L, long leads |
   | C104, C603, C604 (1 uF 50 V, 1206) | TDK C3216X7R1H105K160AB | KEMET C1206C105K5RACTU |
   | the 10 uF 50 V 1210 capacitors | as listed | whichever in-stock 10 uF 50 V X7R 1210 was bought. Write its number on the sign-off sheet |
   | C405 (220 uF 35 V) | EEU-FR1V221 | whichever in-stock 220 uF 35 V low-ESR part with the same 8 mm can and 3.5 mm lead spacing was bought. Check it against the footprint before soldering |

3. Check the five bare boards under a light: no scratches across tracks, all holes open, the silkscreen
   readable. Some labels overlap each other or are clipped by the bare copper areas. That was known when the
   boards were ordered and it is why the board guide's orientation table matters more than the printing on
   the board.
4. JK BMS: read its manual. Find out how it is switched on the first time, and write that on the sign-off
   sheet (B4).
5. UBEC: set its output jumper to 7.4 V now, with nothing connected (B8).

## Sessions 2 and 3: solder the board

Follow `docs/BUILD_POWER_BOARD.md`, "Order of assembly", steps 1 to 11, with these changes.

| board guide step | change for car 1 v2 |
| --- | --- |
| 2. The chips on the bottom | none. R801, R802 and R805 stay empty, as in the guide |
| 9. Chips into their sockets, fuses, modules | do not fit MOD402 (the camera's 12 V regulator). Its pads stay empty |
| 11. Wire pads | do not wire the PD trigger (MOD501) or the CC/CV module (MOD502). The PD-trigger pads and the four CC/CV pads stay empty. The camera pads stay empty |
| connectors | J201 (BMS UART) and J409 (lidar 12 V) are soldered in but nothing plugs into them on this car |

Everything else on the board is fitted, including the few small parts of the charging and camera circuits.
They cost about four dollars and they mean the later upgrades only need the modules.

Put a strip of Kapton over the empty module pads when the board is finished, so nothing loose can bridge them.

## Session 4: bench tests of the board

The board guide's "The bench tests", with these changes.

**Test 1 (logic only, from 5 V).** Step 5, the BMS loop-back, is optional: nothing uses J201 on this car. Do
it if there is time, so the board is known good for the upgrade later.

**Test 2 (pack bus from a bench supply).** Run it as written at 14.0 V and at 12.0 V. Then add one step,
because a full LiPo is 16.8 V:

- Set the supply to 16.8 V. The dev-kit feed must still be on (DEV+ reads 16.8 V). In step 6 it should cut
  off at about 18.7 V. Write down both numbers. If it cuts off below 17.5 V, stop and ask: a full pack with
  the motor braking could then switch the Jetson off.

In step 7, checking the lidar terminal (J409) and the camera pads is still worth the minute.

**Pico files.** After test 2, copy seven files, not six. `car_profile.py` is the new one and it holds this
car's battery levels:

```
cd firmware/supervisor
mpremote connect /dev/ttyACM0 cp pins.py hal.py jbd.py link.py sequencer.py car_profile.py main.py :
mpremote connect /dev/ttyACM0 reset
```

The status line shows `"bms": {"ok": false, ...}` with a growing `timeouts` count. That is expected on this
car, because no BMS is wired to the Pico. The supervisor uses its own voltage measurement (`bat`) instead.

**Test 3 (main switch under load).** The pack is the LiPo with its fuse and the JK BMS, built in session 5,
so do session 5 first. Three differences:

- The fuse is 100 A, not 125 A, and the BMS limit is set to 80 A. The 50 A and 70 A pulses stay under both.
- Check the LiPo's label first (A1). Do not pull more than its continuous rating. If the pack cannot give
  70 A, do the 50 A part only and write that down.
- The pack sits in a LiPo bag or on a fireproof surface, not in the car.

**Test 4 (precharge into the real FSESC and BEC).** The BEC is the Hobbywing UBEC at 7.4 V. This is checklist
item C2 on the real board. Nobody has tried this UBEC on this precharge circuit, so this test is the one
most likely to show something new. If the motor bus does not come up, the board guide's two fixes still
apply (move the UBEC's red lead to BEC+ALT, or fit the 4.7 ohm resistor as R313).

## Session 5: the battery assembly

Read "Three things to get right" in `docs/CAR1V2_WIRING.md` before starting. XT90-S unplugged throughout.

1. Meter every pin of the LiPo's balance plug against its black wire: four steps of one cell each (3.7 to
   4.2 V per step). Write the four cell voltages down. If any cell is under 3.0 V, stop.
2. Build the positive lead: pack plus (through the mating XT90) to the MIDI fuse holder, fuse holder to the
   XT90-S plus. 10 AWG. Do not fit the fuse yet.
3. Build the negative lead: pack minus to the BMS's B- wire, the BMS's P- wire to the XT90-S minus.
4. Plug the balance extension into the BMS, then into the pack, in the order the JK manual gives.
5. Wake the BMS as its manual says. In the JK app set: 4 cells, Li-ion, cell under-voltage 3.20 V with
   release at 3.40 V, cell over-voltage 4.25 V, discharge over-current 80 A. Save, read the settings back,
   and check the four cell voltages in the app against your meter.
6. Fit the 100 A fuse. Meter the XT90-S: it reads the pack voltage, with plus on the pin moulded "+".
7. Heat-shrink every joint. No bare metal anywhere on the pack side.

The settings in step 5 are starting values from `docs/CAR1V2.md`. If the app does not offer one of them,
write down what it does offer and ask before driving.

## Session 6: build the car

**Print** (PETG-CF, settings in `mech/PRINTING.md`):

| part | file | note |
| --- | --- | --- |
| the three deck pieces, four splices, post washers | `mech/out/stl/deck_*.stl`, `splice_*.stl`, `post_washer.stl` | `deck_mid` only after B7 says the pack opening is right |
| bumper, camera arch, both side pods | `bumper.stl`, `camera_arch.stl`, `side_pod_*.stl` | flipped and supported as PRINTING.md says |
| dev-kit tray, canopy leg, canopy | `devkit_tray.stl`, `canopy_leg.stl`, `stack_canopy.stl` | after MEASURE_FIRST item 17 on the second dev kit |
| ESC cradle | `esc_cradle.stl` | after A3 and MEASURE_FIRST item 21 |
| **lidar plinth for the RPLidar C1** | `mech/out/car1v2/stl/c1_plinth.stl` | instead of `lidar_plinth.stl`. After B1 |
| **camera cradle for the OAK-D Pro** | `mech/out/car1v2/stl/oakd_cradle.stl` | instead of `camera_cradle.stl`. After B2 |
| **E-stop bracket** | `mech/out/car1v2/stl/estop_bracket.stl` | after B5 |
| **BMS holder** | `mech/out/car1v2/stl/bms_fence_jk.stl` | after B4. It has not been checked against the other parts. Hold the printed part on the car before you fit inserts for it |

Not printed for this car: `pack_box`, `pack_lid`, the two `cell_holder` parts, `bms_fence`, `lidar_plinth`,
the three `camera_cradle` parts. The rear wing is optional: `docs/AERO.md` explains why it is left off.

**Cut:** the acrylic FET shield (`mech/out/laser/laser_fet_shield.dxf`) on the school laser or through
SendCutSend. The FET bar is in the SendCutSend cart.

**Assemble** in this order, following the kit manual in `mech/README.md`:

1. Deck pieces and splices onto the chassis posts. Bumper. Side pods.
2. ESC cradle and the spare FSESC. Motor phase leads and the sensor lead. Leave the phases unplugged for now.
3. Power board on its standoffs, FET bar and shield, then the dev-kit tray with the second Jetson.
4. The harnesses from the board guide's "Harnesses" table, except these, which do not exist on this car:
   pack to fuse and BMS as built in session 5 instead of the pack-box leads, no balance adapter, no BMS UART,
   no camera power, no camera regulator input, no PD trigger, no CC/CV, no lidar power. The "Castle BEC" row
   is the UBEC.
5. Servo into J406. UBEC output into J403. FSESC servo lead into J904. Check the first of the three cautions
   in the wiring doc again.
6. E-stop bracket on the tail, button in it, its normally closed pair to J1001.
7. Camera arch and canopy last, after bring-up, so the board stays reachable.

**Bring-up:** checklist section E, E1 to E8, in order. Do not skip E3 (the E-stop test, and the test with the
Pico pulled out).

## Session 7: the driving stack on the second Jetson

1. JetPack 6 on the second dev kit, booting from its own storage (A2).
2. Clone this repo and run `sudo software/jetson/system/setup_car1v2.sh`. Fix what it flags, then run it
   again with `--check`.
3. Install the driving stack the way car 1's Jetson has it (the team's own notes; this repo does not hold the
   stack).
4. VESC Tool through the board's USB-C: motor detection for the Puller Pro, the limits in `docs/CAR1V2.md`,
   servo limits so the steering does not bind (E6, E7).
5. Drive by joystick in the hallway. No lidar or camera yet.

## Session 8: the swap

Checklist section F. One session, about two hours with calibration. Car 1 is whole again when its lidar and
camera go back.

## Sign-off for car 1 v2

Use the board guide's sign-off sheet with these lines changed or added.

- [ ] Kit counted against `power_board_stage1.csv`. MOD402, MOD501, MOD502, R801, R802, R805 not fitted.
      Substitute part numbers written here: 10 uF 1210 ________, C405 ________.
- [ ] Test 2: dev-kit feed still on at 16.8 V: ______ V. Cuts off at ______ V, comes back at ______ V.
- [ ] Test 3 run on the LiPo, 100 A fuse. Pack rating from its label: ______ A. Highest current pulled: ______ A.
- [ ] Test 4 with the Hobbywing UBEC. Motor bus after precharge at 12.0 V: ______ V. UBEC on BEC+ / BEC+ALT,
      R313 10 / 4.7 ohm (circle).
- [ ] UBEC measured at 7.4 V before the servo was connected: ______ V.
- [ ] JK BMS: first power-on done as the manual says. Settings saved and read back: under-voltage ______ V,
      over-voltage ______ V, over-current ______ A. Four cell voltages match the meter.
- [ ] FSESC: maximum input voltage 18 V; battery cut-off 14.0 V to 13.2 V; current limits 60 A.
- [ ] Pico: MicroPython and the seven supervisor files, `car_profile.py` among them.
- [ ] E-stop: pressing it drops the motor bus. Unplugging J1001 drops it. Pulling the Pico drops it.
- [ ] Pack reaches 3.5 V a cell: the Jetson shuts down and the car switches off (try it once, on the bench,
      wheels off the ground).

Not used on this car, so cross them out on the sheet: the Castle BEC line, the PD trigger and CC/CV line, the
JBD line.
