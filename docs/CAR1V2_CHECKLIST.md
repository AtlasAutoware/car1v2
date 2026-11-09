# Car 1 v2: what needs hands on the hardware

Everything here is something the design assumed and nobody has measured or tried yet. Work through it in
order. Sections A and B come before any order is placed. Write the answer next to each box, with initials and
the date, and tell whoever holds the repo so the number goes into the file named in the last column.

Car 1 is not touched anywhere in sections A to E. Section F is the one session where its lidar and camera move.

## A. Confirm the shelf (before ordering)

| # | check | why it matters | goes into |
| --- | --- | --- | --- |
| A1 | Each 4S LiPo pack: capacity, C rating, length x width x height, main connector (XT90?), balance plug (5-pin JST-XH?), age and how puffy | the battery bay and the deck opening are sized from it; the fuse and BMS limits from its ratings | `mech/kit.py` `BATT_BAY`, `docs/CAR1V2.md` |
| A2 | The second Jetson: module name on the label, Super firmware or not, what it boots from (NVMe or the old 256 GB SD card), JetPack version (`cat /etc/nv_tegra_release`) | the setup script and the 25 W power mode assume JetPack 6 on the dev-kit carrier | `docs/CAR1V2.md` |
| A3 | The two Flipsky units: read the silkscreen. Which is the Mini FSESC 6.7 Pro, which is the cased one. Which one is on car 1 | the spare goes on the new chassis; the cradle and the 14 V minimum depend on the model (MEASURE_FIRST 21) | `mech/kit.py` `ESC_CASE` |
| A4 | Slash 4x4 chassis: the Puller Pro is mounted, turns freely, its sensor lead is there; pinion and spur tooth counts | motor detection and the speed calibration | `docs/CAR1V2.md` |
| A5 | INJS235 servo: fits the servo bay, horn spline, lead length to J406 | servo mount; whether an extension lead is needed | - |
| A6 | Progressive RC box: wire gauge printed on the two XT90-to-bare-wire cables; count the loose XT90s (pairs or singles) | one of those cables can be the board's 10 AWG pigtail, and then no XT90 or 10 AWG wire is bought | `bom/car1v2/make_car1v2.py` |
| A7 | RC4WD box: list what is in it | its wish list had a servo, an ESC, leads and hex drivers; anything usable drops a cart line | same |
| A8 | Soldering: do the Hakko irons have tips now? If not, are the school lab's irons free for the build sessions? | the board is hand-soldered; T15 tips are about $14 each and are not in the carts | same |
| A9 | Noctua fan: model and voltage | J1003 is a 5 V PWM header | - |
| A10 | Powerpole crimper in the lab? | the Anderson PP45 kit is only useful with one, or soldered | - |
| A11 | A current-limited bench supply, a meter, an oscilloscope, a thermocouple, a 4.7 ohm 50 W resistor and a load for 50 A pulses | the bench tests below assume them | - |

## B. Measure before printing or ordering (from `docs/MEASURE_FIRST.md`)

Items 1 to 9, 13 and 17 to 22 of MEASURE_FIRST apply as written (chassis towers, body posts, battery bay,
servo and gearbox heights, tyre clearance, the dev-kit carrier's hole positions and heights, the FSESC case,
the J12 and J14 bench readings). Use the second dev kit for 17 to 20 and 22. Print the two fit coupons first.

New for car 1 v2:

| # | measure | now | why |
| --- | --- | --- | --- |
| B1 | RPLidar C1: the four M2.5 holes in its base. Distance between centres both ways; is the pattern square; how deep are the threads | slots take a square pattern from 36 to 50 mm; screws engage 3 mm (4 mm is the limit) | `mech/car1v2.py` `C1_SLOT` or `C1_HOLES` |
| B2 | OAK-D Pro: are there two M4 holes on the back, 75 mm apart? Their height on the back and their depth. Is there a 1/4-20 thread underneath | the cradle hangs the camera on the M4 pair; pick a screw that does not bottom out | `OAKD_VESA` |
| B3 | Which IMU the OAK-D Pro reports (`depthai` device info): BNO086 or BMI270 | Luxonis fitted the 6-axis BMI270 to units built from mid 2021 to mid 2023 | `docs/CAR1V2.md` |
| B4 | JK BMS when it arrives: length x width x thickness, where B-, P-, the balance socket and the temperature probes leave | the holder was drawn from the listing's 151 x 105 x 15.5 mm and has had no interference check | `JK_BMS` |
| B5 | E-stop button when it arrives: panel hole diameter, depth behind the panel, which terminals are the normally closed pair | bracket hole is 22.3 mm | `ESTOP_D` |
| B6 | Pick the spot for the E-stop bracket on the deck's tail and mark two M3 inserts 30 mm apart | not placed in the CAD | - |
| B7 | With A1 in hand: does the pack drop into the chassis bay through the deck's pack opening, and does the stock hold-down still close | the deck opening was drawn for the 18650 pack box (about 126 x 46 mm). If the LiPo is longer, the opening has to grow before `deck_mid` is printed | `mech/kit.py` |
| B8 | Hobbywing UBEC when it arrives: output plug type, and set its jumper to 7.4 V before it ever meets the servo | J403 expects a servo-style plug | - |
| B9 | Rear view from the C1 once mounted: which angles the camera arch legs and the canopy block | mask those bins in the lidar driver | driving stack |
| B10 | Weigh the finished car with the pack in, and each axle on its own if the scale allows | `docs/AERO.md` and the simulator both use a guessed 3 to 4 kg | `docs/AERO.md`, simulator vehicle file |

MEASURE_FIRST items 10, 12, 23 and 24 (Triton holes, TiM561 plugs, Triton 12 V, the USB Ethernet adapter) and
30 (charge modules) wait for the sensor upgrade and phase 2.

## C. Bench tests before the boards are ordered (from `docs/REV_B.md`)

None needs the new board. Do them on the second dev kit and the spare FSESC.

- [ ] C1. Drive J12 pin 10 through 10 kOhm from a 3.3 V USB-UART at 115200 while `cat /dev/ttyTHS1` runs.
      Clean text means the 1 kOhm the board uses has margin.
- [ ] C2. Precharge the real FSESC and the UBEC (7.4 V, servo connected, 1000 uF on its output) through
      10 ohm from a 12 V supply with a scope on the bus. It must come within 2.5 V of the supply and stop
      rising. The review's test named the Castle BEC; the UBEC replaces it, so its start-up is the unknown.
- [ ] C3. Run the spare FSESC at 12.0 V on the bench supply (the Mini is rated from 14 V).
- [ ] C4. (phase 2 only) The CC/CV module's current sense: 20 V in, 4.7 ohm on the output, measure IN- to OUT-.

## D. Build the board (`docs/BUILD_POWER_BOARD.md`), with these changes

- [ ] Do not fit MOD402 (camera regulator), MOD501 (PD trigger) or MOD502 (CC/CV module). R801, R802 and R805
      stay empty as before. Everything else is fitted, so the board is ready for the sensor upgrade and for
      USB-C charging later. The list is `bom/car1v2/power_board_stage1.csv`.
- [ ] Substitutions in the cart: C101 to C103 and C404 are the long-lead versions of the same Panasonic
      capacitors (trim the leads); C104, C603 and C604 are KEMET C1206C105K5RACTU; the 10 uF 1210 parts and
      C405 are whatever equivalent was bought (write the part number here: ________).
- [ ] Copy seven files to the Pico, `car_profile.py` among them (`firmware/supervisor/README.md`).
- [ ] Run bench bring-up steps 1 to 4 of REV_B.md ("Bench bring-up order"). In step 2 skip the camera feed.
      In step 1 the BMS loop-back is optional, since J201 is not used.

## E. Bring-up on the new chassis, car 1 still untouched

- [ ] E1. Pack and BMS alone, XT90-S unplugged. Meter on every balance pin. Connect the BMS, wake it as its
      manual says, set it in the JK app (settings in `docs/CAR1V2.md`), read all four cells.
- [ ] E2. Fuse fitted, XT90-S in, motor phases unplugged, E-stop released. Press the power button: green LED
      blinks, then stays on. `atlas supervisor` on the second Jetson shows RUN and `pre_ms`.
- [ ] E3. Press the E-stop. The motor bus drops at once and stays off after the button is twisted out, until
      the power button is pressed. Pull the Pico out of its sockets with the car on: the bus must drop too.
- [ ] E4. Short press of the power button: the Jetson shuts down and the car switches itself off.
- [ ] E5. `sudo software/jetson/system/setup_car1v2.sh` on the second Jetson. Fix what it flags.
- [ ] E6. VESC Tool on the spare FSESC through the hub: motor detection for the Puller Pro, the limits and
      cut-offs in `docs/CAR1V2.md`, kill switch on ADC2, servo output on. Wheels off the ground.
- [ ] E7. UBEC at 7.4 V, servo on J406: steer end to end from VESC Tool; set the servo limits so nothing binds.
- [ ] E8. Main switch under load and the ESC at 50 A (REV_B steps 3 and 8), thermocouples on the FET bar and
      the FSESC. An adult present, the pack in a LiPo bag or on a non-flammable surface.
- [ ] E9. Heat, canopy on, car standing still: run the Jetson at full load for ten minutes (the driving stack,
      or a stress tool) and watch `tegrastats`. Write down the hottest CPU and GPU readings and whether it
      throttled. Repeat with the canopy off. If the two differ by more than a few degrees, the canopy is too
      close to the fan (`docs/AERO.md`, "Cooling").

## F. The swap session (one work session)

Before the day: sections A to E are done, the car's driving stack is installed on the second Jetson and has
driven the new chassis by joystick with no sensors.

1. Photograph car 1's lidar and camera cabling.
2. Move the RPLidar C1 and its USB adapter: four M2.5 screws from below into the C1 plinth, then the plinth's
   four bolts. Move the OAK-D Pro: cradle onto the arch first, then the two M4 screws into the camera's back.
3. Move the Wi-Fi adapter and the joystick receiver.
4. `setup_car1v2.sh --check`: all four lines say ok.
5. Run the steering and speed calibration in the hallway (`~/calib/calib_go.sh` from car 1's stack).
6. Drive by joystick, then the lidar-only gap follower at walking pace, with a hand on the E-stop.
7. Going back takes the same two moves in reverse: car 1 is complete again once its lidar and camera return.

Stop and ask if: a cell reads under 3.0 V, anything gets hot with no load, the E-stop does not drop the bus,
or the bus does not come up within three precharge tries.
