"""Car 1 v2 stage 1: a 4S LiPo, a BMS that never answers on the UART, no charger, the lidar on USB."""
import sequencer as Q
from car_profile import SETTINGS, Car1v2Lipo
from sim import Rig, SimUart


def silent_bms_rig(**kw):
    rig = Rig(settings=Car1v2Lipo, **kw)
    # the JK BMS is not on the opto link: nothing ever comes back on the BMS UART
    rig.uart.read = lambda: b''
    return rig


def test_profile_is_the_default_and_keeps_the_levels_in_order():
    assert SETTINGS is Car1v2Lipo
    assert issubclass(Car1v2Lipo, Q.Settings)
    assert 4 * 3.0 < Car1v2Lipo.BAT_CUT_V < Car1v2Lipo.BAT_LOW_V < 4 * 3.7
    assert Car1v2Lipo.BAT_MIN_V < Car1v2Lipo.BAT_CUT_V


def test_runs_with_a_silent_bms_and_leaves_the_lidar_feed_off():
    rig = silent_bms_rig(bat_v=15.2)
    rig.run(3000)
    assert rig.state() == Q.RUN
    assert rig.hw.out['MAIN_EN'] == 1 and rig.hw.out['VESC_KILL'] == 1
    assert rig.hw.out['LIDAR_EN'] == 0
    assert rig.seq.bms is not None and not rig.seq.bms.online()


def test_estop_still_cuts_with_the_profile():
    rig = silent_bms_rig(bat_v=15.2)
    rig.run(1500)
    assert rig.state() == Q.RUN
    rig.hw.set_input('ESTOP_OK', 0)
    rig.run(200)
    assert rig.hw.out['MAIN_EN'] == 0 and rig.state() == Q.LOCKOUT


def test_low_lipo_asks_for_a_clean_shutdown_above_three_volts_a_cell():
    rig = silent_bms_rig(bat_v=13.0)                 # 3.25 V per cell, under BAT_CUT_V
    rig.run(1500)
    rig.jetson_boots()
    rig.run_with_heartbeat(Car1v2Lipo.BAT_CUT_MS + Car1v2Lipo.BAT_FILTER_MS + 5000)
    assert rig.state() in (Q.SHUTDOWN_REQUESTED, Q.HALTING, Q.OFF)


def test_healthy_lipo_is_left_alone():
    rig = silent_bms_rig(bat_v=14.8)
    rig.run(1500)
    rig.jetson_boots()
    rig.run_with_heartbeat(Car1v2Lipo.BAT_LOW_MS + 10000)
    assert rig.state() == Q.RUN
    assert not rig.events('low_battery')


def _held(bat_v, ms):
    rig = silent_bms_rig(bat_v=bat_v)
    rig.run(1500)
    rig.jetson_boots()
    rig.run_with_heartbeat(ms)
    return rig


def test_warning_edge_is_at_fourteen_volts():
    hold = Car1v2Lipo.BAT_LOW_MS + Car1v2Lipo.BAT_FILTER_MS + 5000
    above = _held(14.05, hold)
    assert not above.events('low_battery') and above.state() == Q.RUN
    below = _held(13.95, hold)
    assert [e['level'] for e in below.events('low_battery')] == ['warn'] and below.state() == Q.RUN


def test_shutdown_edge_is_at_thirteen_point_two_volts():
    hold = Car1v2Lipo.BAT_LOW_MS + Car1v2Lipo.BAT_FILTER_MS + 5000
    above = _held(13.25, hold)
    assert 'shutdown' not in [e['level'] for e in above.events('low_battery')] and above.state() == Q.RUN
    below = _held(13.15, hold)
    assert 'shutdown' in [e['level'] for e in below.events('low_battery')]
    assert below.state() in (Q.SHUTDOWN_REQUESTED, Q.HALTING, Q.OFF)


def test_the_estop_sense_pin_is_never_an_output():
    """GP10 sits on the E-stop loop's sense node (review S2). A pin driven high there could hold the node up with
    the loop open, so the firmware may only ever read it. This fails if a pin table or any file on the Pico changes
    that."""
    import os, re
    import pins
    assert 'ESTOP_OK' in [n for n, _, _ in pins.INPUTS]
    assert 'ESTOP_OK' not in [n for n, _, _ in pins.OUTPUTS]
    assert pins.ESTOP_OK not in [gp for _, gp, _ in pins.OUTPUTS]
    assert dict((n, pull) for n, _, pull in pins.INPUTS)['ESTOP_OK'] is None        # no internal pull-up either
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in ('pins.py', 'hal.py', 'jbd.py', 'link.py', 'sequencer.py', 'car_profile.py', 'main.py'):
        src = open(os.path.join(here, f)).read()
        assert not re.search(r"write\(\s*['\"]ESTOP_OK['\"]", src), f
        assert not re.search(r'Pin\(\s*(10|pins\.ESTOP_OK|ESTOP_OK)\s*,\s*Pin\.OUT', src), f
