"""Which car this Pico is on. main.py takes its settings from SETTINGS below.

Rev B's defaults (sequencer.Settings) were chosen for the built-in 4S3P 18650 pack behind a JBD BMS and for the
SICK TiM561 on the board's switched lidar feed. Car 1 v2 stage 1 is different in three ways:

  - the pack is a 4S LiPo. Its cells should not be run as low as the 18650 pack's, so the two low-pack levels
    are higher. The BMS and the ESC have their own cut-offs (docs/CAR1V2.md, "Settings to make").
  - the BMS is a JK-B1A8S10P. Its serial port runs at 115200 baud, which the board's PC817 optocouplers cannot
    pass, so nothing answers on the BMS UART. The supervisor already treats a silent BMS as "offline" and
    reports the pack from its own ADC; nothing to change, only to know.
  - the lidar is an RPLidar C1 on USB, so the switched 12 V lidar feed stays off at boot.

To go back to rev B's values (18650 pack, JBD BMS, TiM561), set SETTINGS = Settings.
"""
from sequencer import Settings


class Car1v2Lipo(Settings):
    LIDAR_AT_BOOT = False
    BAT_LOW_V = 14.0        # 3.50 V per cell for BAT_LOW_MS: tell the Jetson the pack is low
    BAT_CUT_V = 13.2        # 3.30 V per cell for BAT_CUT_MS: clean shutdown
    # Starting values. LiPo makers put the floor at 3.0 V per cell; these keep 0.3 V above it under load.


SETTINGS = Car1v2Lipo
