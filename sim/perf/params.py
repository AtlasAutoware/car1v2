"""Numbers the speed study rests on, each with where it came from.

    basis: 'page'  = read on the maker's or a seller's page on 2026-11-09 (URL in src)
           'paper' = read in the cited paper on 2026-11-09
           'repo'  = from this repository or the team's driving stack
           'cfd'   = from sim/aero (docs/AERO.md)
           'est'   = an estimate. Not measured, not read anywhere. Replace it when the part is on the bench.

Nothing here has been measured on a car. The lines marked 'est' are the ones the checklist asks for.
"""
G = 9.81
RHO = 1.2

# ---------------------------------------------------------------- what the competition runs at
BENCHMARK = dict(
    top_speed_mps=11.0,
    src=('ForzaETH Race Stack (Baumann et al., J. Field Robotics 2025, arXiv 2403.11784): the car was tested "up to" '
         '11 m/s and the abstract says over 10 m/s on tracks up to 150 m. ForzaETH won the German Grand Prix 2022 and '
         'the ICRA Grand Prix 2023. The IROS 2026 Sim Racing League report gives top speeds "over 11 m/s" and a 7.16 s '
         'best lap for the winner, in simulation.'),
    margin_mps=(1.5, 2.5),          # Ragini, 2026-11-09: 1.5 to 2.5 m/s faster than the competition
)

# ---------------------------------------------------------------- shared chassis facts (Traxxas Slash 4x4)
SLASH = dict(
    tyre_d_m=(0.1095, 'page', 'Traxxas Slash 4x4 spec: tire diameter 4.31 in (109.5 mm). Stock tyres; the donated chassis may differ (checklist A4)'),
    diff_ratio=(2.85, 'page', 'Traxxas Slash 4x4 owner\'s manual: final ratio = spur / pinion x 2.85'),
    stock_gearing=((13, 54), 'page', 'Traxxas manual: 13/54 stock, overall 11.82'),
    wheelbase_m=(0.324, 'page', 'Traxxas spec: 12.75 in'),
    rtr_mass_kg=(2.64, 'page', 'Traxxas spec, ready to run with body, Velineon motor (262 g) and VXL-3s (90 g), no battery'),
)

# ---------------------------------------------------------------- assumptions common to both cars
COMMON = dict(
    mu=(0.80, 'est', 'tyre grip. The team plans with 6 to 8 m/s2; a 1/10 car on tile was measured near 0.69 (arXiv 2509.15423); '
                     'the F1TENTH simulator default is 1.05. Not measured on any floor the car will race on'),
    drivetrain_eff=(0.85, 'est', 'gears, diffs and bearings'),
    crr=(0.02, 'est', 'rolling resistance of foam-filled rubber tyres on a hard floor'),
    duty_max=(0.95, 'est', 'VESC default maximum duty cycle'),
    cda_m2=(0.0412, 'cfd', 'drag area of car 1 v2 without the wing, pressure only (sim/aero/out/results.json). Used for both cars'),
)

# ---------------------------------------------------------------- car 1 v2
CAR1V2 = dict(
    name='car 1 v2',
    kv_rpm_per_v=(2200.0, 'page', 'Holmes Hobbies Puller Pro V2 Standard 2200 kv'),
    motor_rpm_max=(50000.0, 'page', 'Holmes Hobbies: 50,000 rpm max'),
    pole_pairs=(2, 'page', 'four-pole rotor'),
    r_motor_ohm=(0.030, 'est', 'winding resistance, line to line. Holmes does not publish it. VESC Tool reports it at motor detection (checklist E6)'),
    cells=4,
    v_cell_nominal=(3.7, 'est', 'a LiPo at about half charge with no load'),
    r_supply_ohm=(0.025, 'est', 'pack, leads, fuse, BMS, the board\'s switch and the ESC together. Pack unknown (checklist A1)'),
    i_motor_max=(60.0, 'repo', 'docs/CAR1V2.md settings: motor current max 60 A'),
    i_batt_max=(60.0, 'repo', 'docs/CAR1V2.md settings: battery current max 60 A (BMS limit 80 A, fuse 100 A)'),
    i_regen_max=(12.0, 'repo', 'battery regen limit, rev B value. See docs/PERFORMANCE.md: raising it is one of the changes'),
    gearing=((13, 54), 'est', 'pinion and spur on the donated chassis are not known (checklist A4). 13/54 is the Traxxas stock'),
)

# ---------------------------------------------------------------- a standard competition car, as published
REFERENCE = dict(
    name='reference car',
    kv_rpm_per_v=(3500.0, 'paper', 'Traxxas Velineon 3500, as on the ForzaETH car and in the F1TENTH build'),
    motor_rpm_max=(50000.0, 'est', 'not read today'),
    pole_pairs=(2, 'est', 'not read today; only used for ERPM, which the study does not need for this car'),
    r_motor_ohm=(0.012, 'est', 'not published'),
    cells=3,
    v_cell_nominal=(3.7, 'est', 'as above'),
    r_supply_ohm=(0.020, 'est', 'pack, leads, ESC'),
    i_motor_max=(100.0, 'est', 'set high on purpose so that the published power figure is what limits this car'),
    i_batt_max=(100.0, 'est', 'as above'),
    i_regen_max=(40.0, 'est', 'set high on purpose: this car is never held back by its brakes in the comparison'),
    p_mech_max_w=(300.0, 'paper', 'ForzaETH paper: the Velineon 3500 "achieves maximum power at 300 W"'),
    gearing=((13, 54), 'page', 'Traxxas stock'),
    mass_kg=(3.74, 'page', 'the F1TENTH simulator\'s identified vehicle mass (f1tenth_gym default parameters)'),
)


def val(entry):
    return entry[0] if isinstance(entry, tuple) else entry
