# Car 1 v2 wiring

Stage 1: the car drives on a 4S LiPo, an RPLidar C1 and an OAK-D Pro. The board is ATLAS-PWR-1 from rev B with
nothing changed in copper. `docs/WIRING.md` (rev B section) has the cable lengths for the rev B kit; this page
says what is different on car 1 v2 and gives the whole picture on one diagram. Dashed lines are signal, solid
lines carry power.

```mermaid
flowchart LR
  subgraph BATT["battery, in the chassis battery bay"]
    LIPO["4S LiPo (owned)<br/>XT90 and 5-pin balance plug"]
    FUSE["MIDI fuse 100 A<br/>in the + lead"]
    BMS["JK-B1A8S10P BMS<br/>in the - lead, on the pack lid"]
    XT["XT90-S<br/>master disconnect"]
    LIPO -- "+ , 10 AWG" --> FUSE --> XT
    LIPO -- "- , 10 AWG" --> BMS -- "P- = car ground" --> XT
    LIPO -. "balance plug, 5 wires" .-> BMS
  end

  subgraph PWR["power board ATLAS-PWR-1"]
    PADS["BAT+ / BAT- pads<br/>3 x 680 uF, TVS"]
    SW["main switch<br/>3 x IRFB7430, MIC5014<br/>precharge 10 ohm"]
    AND["74HCT08<br/>E-stop AND enable"]
    LATCH["Pololu 2813 latch"]
    V5["5 V regulator"]
    PICO["Pico supervisor"]
    DEV["dev-kit feed<br/>5 A fuse, over-voltage cut"]
    HUB["USB hub + console"]
    SRV["servo header J406<br/>signal buffered to 5 V"]
  end

  XT == "10 AWG pigtail, XT90 male" ==> PADS
  PADS ==> SW
  PADS ==> LATCH
  ESTOP["E-stop button<br/>normally closed, on the tail"] -. "J1001, 2 wires" .-> AND
  PICO -. "MAIN_EN, PRECHARGE_EN" .-> AND
  AND -.-> SW
  LATCH ==> V5 ==> PICO
  LATCH ==> DEV

  SW == "ESC+ / ESC- pads, 12 AWG" ==> ESC["Flipsky FSESC (the spare)"]
  ESC == "3 phase leads, 4 mm bullets" ==> MOTOR["Puller Pro 540, 2200 kV"]
  MOTOR -. "sensor lead" .-> ESC
  SW == "BEC+ pad J401, 16 AWG" ==> BEC["Hobbywing UBEC 10A<br/>jumper at 7.4 V"]
  BEC == "J403" ==> SRV == "servo lead" ==> SERVO["INJORA INJS235"]
  ESC -. "servo/PPM out to J904" .-> SRV
  ESC -. "COMM to J903: UART, ADC2 kill" .-> PICO

  DEV == "DC lead, 5.5 x 2.5 mm" ==> JET["Jetson Orin Nano<br/>second dev kit"]
  JET -. "J12, 40-wire ribbon to J801" .-> PICO
  JET -. "J14 harness to J802" .-> PICO
  PICO -. "micro-USB to a USB-A port" .-> JET
  JET -. "UART1 on the ribbon" .-> ESC
  LIDAR["RPLidar C1"] -. "its USB adapter, USB-A" .-> JET
  CAM["OAK-D Pro"] -. "USB-C to a blue USB-A port" .-> JET
  WIFI["Wi-Fi: TP-Link T3U"] -. "USB-A" .-> JET

  LAPTOP["laptop, one USB-C cable"] -.-> HUB
  HUB -. "port 1, J601 to the dev kit's USB-C" .-> JET
  HUB -. "port 2, console on J14" .-> JET
  HUB -. "port 3, J602 to the FSESC's USB" .-> ESC
  FAN["pod fan, 5 V PWM"] -. "J1003" .-> PICO
```

## What differs from the rev B wiring table

| connection | rev B | car 1 v2 stage 1 |
| --- | --- | --- |
| pack | built-in 4S3P 18650 pack, cell taps on a 7-pin lead | an owned 4S LiPo; its 5-pin balance plug goes to the BMS through an extension lead |
| BMS | JBD 4S 100 A, UART to J201 | JK-B1A8S10P. Its UART is left unconnected: it talks at 115200 baud and the board's optocouplers pass 9600. J201 stays empty. Cell voltages are read in the JK phone app |
| servo supply | Castle BEC 2.0 at 7.5 V | Hobbywing UBEC 10A set to 7.4 V, on the same pads (BEC+ J401 in, J403 out), with a 10 A in-line blade fuse in its red input lead. The latch's VIN lead gets a 7.5 A one. The board has no fuse on either |
| lidar | SICK TiM561: 12 V from J409, Ethernet through a USB adapter | RPLidar C1: one USB lead from its adapter board to a dev-kit USB-A port. J409 stays empty |
| camera | LUCID Triton: 12 V from the Pololu regulator, Ethernet on the dev kit's RJ45 | OAK-D Pro: one USB-C lead to a USB 3 port. The regulator (MOD402) is not fitted and its pads stay empty |
| charging | USB-C PD trigger and CC/CV module on the charge pads | not fitted. The LiPo comes out and goes on the balance charger. The charge pads stay empty; `CHG_PRESENT_N` rests high through its pull-up |
| E-stop | "a wire loop if no button is fitted" | a normally closed button on the tail bracket, wired to J1001. No loop jumper |
| Jetson | car 1's dev kit | the second dev kit, so car 1 keeps its own |

Everything else is as in rev B: the FSESC on the ESC pads and J903/J904, the dev-kit DC lead, the 40-wire
ribbon, the J14 harness, the Pico's USB lead, the three hub leads, the fan and the latch.

## Three things to get right

1. **The servo is fed from the UBEC, not from the FSESC.** On car 1 the servo plugs into the FSESC. On car 1 v2
   only the FSESC's signal wire is used: it goes to J904, the board buffers it, and the servo plugs into J406,
   where the red wire is the UBEC's 7.4 V. Do not plug the INJS235 straight into the FSESC.
2. **The balance plug goes to the BMS and nowhere else.** The pack's main leads go through the fuse and the BMS
   to the XT90-S. To charge, unplug both the XT90-S and the balance plug and take the pack to the charger.
3. **The E-stop loop is two wires and no ground.** One side is J1001 pin 1, the other pin 2. Keep them away
   from the motor leads and twist them.
