"""Speed study of car 1 v2 against the published RoboRacer (F1TENTH) pace.

    python3 sim/perf/run_all.py      # writes sim/perf/out/summary.json, summary.md, two plots and a parameter file

The question (Ragini, 2026-11-09): can the car, simulated with its weight, go 1.5 to 2.5 m/s faster than its
competition? docs/PERFORMANCE.md is written from these numbers.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from params import G, BENCHMARK, CAR1V2, REFERENCE, COMMON, SLASH, val
from model import Car, straight, load_track, rounded_box, lap
import mass

OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
MB = mass.budget()
M, M_LO, M_HI = MB['total_kg'], MB['low_kg'], MB['high_kg']
BENCH = BENCHMARK['top_speed_mps']
WIN = (BENCH + BENCHMARK['margin_mps'][0], BENCH + BENCHMARK['margin_mps'][1])       # 12.5 to 13.5 m/s

# The set-up this study recommends for car 1 v2
PINION, SPUR = 15, 54
I_REGEN = 30.0
V_CAP = WIN[1]


def c1v2(**kw):
    kw.setdefault('pinion', PINION); kw.setdefault('i_regen', I_REGEN)
    return Car(CAR1V2, kw.pop('mass', M), **kw)


def run_to(car, v0, targets, ds=0.02, limit=120.0):
    """Distance and time from v0 to each target speed, flat out on a straight."""
    v, s, t, out = v0, 0.0, 0.0, {}
    while s < limit and len(out) < len(targets):
        a = car.accel(v)
        if a <= 1e-4:
            break
        v2 = math.sqrt(v * v + 2 * a * ds)
        t += 2 * ds / (v + v2); v = v2; s += ds
        for g in targets:
            if g not in out and v >= g:
                out[g] = dict(m=round(s, 1), s=round(t, 2))
    return {str(g): out.get(g) for g in targets}


def stop(car, v0, powered=True, ds=0.02):
    """Distance to stop from v0. powered=False is the hardware E-stop: the motor is off, only drag and rolling slow it."""
    v, s = v0, 0.0
    while v > 0.2 and s < 2000:
        a = car.decel(v) if powered else car.resist(v) / car.m
        v = math.sqrt(max(0.0, v * v - 2 * a * ds)); s += ds
    return round(s, 1)


ref = Car(REFERENCE, val(REFERENCE['mass_kg']))
S = dict(question='can car 1 v2 go 1.5 to 2.5 m/s faster than its competition', benchmark=BENCHMARK, window_mps=WIN,
         mass=dict(total_kg=M, low_kg=M_LO, high_kg=M_HI, reference_kg=ref.m),
         setup=dict(pinion=PINION, spur=SPUR, ratio=round(c1v2().ratio, 2), i_motor=val(CAR1V2['i_motor_max']),
                    i_batt=val(CAR1V2['i_batt_max']), i_regen=I_REGEN, v_cap=V_CAP))

# 1. top speed on an endless straight, by gearing, across what is not known
rows = []
for pin in (13, 14, 15, 16):
    worst = Car(CAR1V2, M_HI, pinion=pin, v_cell=3.5, r_motor=0.045, r_supply=0.040)
    nom = Car(CAR1V2, M, pinion=pin)
    best = Car(CAR1V2, M_LO, pinion=pin, v_cell=4.0, r_motor=0.015, r_supply=0.015)
    rows.append(dict(pinion=pin, ratio=round(nom.ratio, 2), worst=round(worst.top_speed(), 1), nominal=round(nom.top_speed(), 1),
                     best=round(best.top_speed(), 1), launch_force_N=round(nom.drive_force(1.0), 1),
                     grip_force_N=round(nom.grip(), 1), rpm_at_cap=round(nom.motor_rpm(V_CAP)),
                     back_emf_at_cap_V=round(nom.motor_rpm(V_CAP) / nom.kv, 1)))
S['top_speed_by_gearing'] = rows
S['top_speed_reference'] = round(ref.top_speed(), 1)

# 2. how much straight it takes
S['run_up_from_5'] = {str(mu): run_to(c1v2(mu=mu), 5.0, WIN) for mu in (0.6, 0.8, 1.05)}
S['run_up_from_5_reference'] = {str(mu): run_to(Car(REFERENCE, ref.m, mu=mu), 5.0, WIN) for mu in (0.6, 0.8, 1.05)}

# 3. peak speed on a straight between two 5 m/s corners
lengths = [8, 10, 12, 14, 16, 18, 20, 22, 25, 30]
variants = {'reference car': ref, 'car 1 v2, regen 12 A': c1v2(i_regen=12.0), 'car 1 v2, regen 30 A': c1v2(),
            'car 1 v2, regen 30 A, capped at 13.5': c1v2(v_cap=V_CAP)}
peaks = {name: [round(float(straight(c, L, 5.0)[1].max()), 2) for L in lengths] for name, c in variants.items()}
S['peak_on_straight'] = dict(lengths_m=lengths, corner_speed_mps=5.0, mu=val(COMMON['mu']), peaks=peaks)
# the straight on which each car first reaches the benchmark and the window
def first_len(car, target):
    lo, hi = 2.0, 80.0
    if straight(car, hi, 5.0)[1].max() < target:
        return None
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if straight(car, mid, 5.0)[1].max() >= target:
            hi = mid
        else:
            lo = mid
    return round(hi, 1)
S['straight_needed_m'] = {name: {str(t): first_len(c, t) for t in (BENCH,) + WIN} for name, c in variants.items()
                          if 'capped' not in name}

# 3b. the same straight on which the reference car peaks at the benchmark: what would make car 1 v2 faster there
L_ref = S['straight_needed_m']['reference car'][str(BENCH)]
R_corner = 5.0 ** 2 / (val(COMMON['mu']) * G)                    # the corner that is taken at 5 m/s with mu 0.8
grip_rows = []
for mu in (0.8, 0.9, 1.0, 1.1, 1.2):
    vc = math.sqrt(mu * G * R_corner)
    grip_rows.append(dict(mu=mu, corner_mps=round(vc, 2),
                          peak_60A=round(float(straight(c1v2(mu=mu), L_ref, vc)[1].max()), 2),
                          peak_80A=round(float(straight(c1v2(mu=mu, i_motor=80.0, i_batt=80.0, i_regen=40.0), L_ref, vc)[1].max()), 2)))
S['same_straight_more_grip'] = dict(straight_m=L_ref, reference_peak=BENCH, rows=grip_rows)

# 4. laps
tracks = {'team comp_track race line (243 m)': load_track(os.path.join(HERE, 'tracks', 'comp_track_raceline.csv')),
          'box, 26 x 9 m centre line (66 m)': rounded_box(21.0, 4.0, 2.5)}
laps, traces = {}, {}
for tname, tr in tracks.items():
    laps[tname] = {}
    for name, c in variants.items():
        r, v = lap(c, *tr)
        laps[tname][name] = r
        traces[(tname, name)] = (tr[0], v)
    for mu in (0.6, 1.05):
        laps[tname][f'reference car, mu {mu}'] = lap(Car(REFERENCE, ref.m, mu=mu), *tr)[0]
        laps[tname][f'car 1 v2, regen 30 A, mu {mu}'] = lap(c1v2(mu=mu), *tr)[0]
    laps[tname][f'car 1 v2, regen 30 A, {M_LO} kg'] = lap(c1v2(mass=M_LO), *tr)[0]
    laps[tname][f'car 1 v2, regen 30 A, {M_HI} kg'] = lap(c1v2(mass=M_HI), *tr)[0]
S['laps'] = laps
# cross-check against the team's own speed profile for comp_track (6.5 m/s2 lateral, 7 m/s ceiling: 41.0 s)
S['cross_check'] = dict(team_profile_lap_s=41.0, team_profile='racelines/comp_raceline.csv: lateral 6.5 m/s2, ceiling 7.0 m/s',
                        this_model_lap_s=lap(c1v2(mu=6.5 / G), *tracks['team comp_track race line (243 m)'], v_ceiling=7.0)[0]['lap_s'])

# 5. stopping
S['stopping_from_cap_m'] = {
    'motor braking, regen 12 A': stop(c1v2(i_regen=12.0), V_CAP),
    'motor braking, regen 30 A': stop(c1v2(), V_CAP),
    'grip only (mu g)': round(V_CAP ** 2 / (2 * val(COMMON['mu']) * G), 1),
    'hardware E-stop: motor off, car coasts': stop(c1v2(), V_CAP, powered=False),
    'hardware E-stop from 2 m/s': stop(c1v2(), 2.0, powered=False),
}
S['kinetic_energy_J'] = {str(v): round(0.5 * M * v * v) for v in (2.0, BENCH, V_CAP)}

# 6. numbers for the ESC and the driving stack
car = c1v2()
erpm_per_mps = car.erpm(1.0)
S['esc'] = dict(erpm_per_mps=round(erpm_per_mps), max_erpm_for_cap=round(erpm_per_mps * V_CAP, -2),
                formula='60 x ratio x pole pairs / (pi x tyre diameter)',
                current_at_grip_limit_A=round(car.grip() * car.r / (car.kt * car.ratio * car.eta), 1),
                battery_power_at_12_5_W=round((car.motor_rpm(12.5) / car.kv + car.motor_current(12.5) * car.rm) * car.motor_current(12.5)),
                scan_travel_m={'RPLidar C1, 10 Hz': round(V_CAP / 10, 2), 'SICK TiM561, 15 Hz': round(V_CAP / 15, 2),
                               'Hokuyo UST-10LX, 40 Hz (what ForzaETH runs)': round(V_CAP / 40, 2)})

# 7. the verdict, as checks
worst15 = next(r for r in rows if r['pinion'] == PINION)
S['checks'] = {
    'top speed reaches the top of the window in the worst case (heavy car, 3.5 V a cell, high resistances)': worst15['worst'] >= WIN[1],
    'window reached within 15 m of straight from a 5 m/s corner at mu 0.8': (S['run_up_from_5']['0.8'][str(WIN[1])] or {}).get('m', 1e9) <= 15.0,
    'motor stays under its 50,000 rpm limit at the cap': worst15['rpm_at_cap'] < val(CAR1V2['motor_rpm_max']),
    'launch is grip-limited, not current-limited, at mu 0.8': worst15['launch_force_N'] >= worst15['grip_force_N'],
    'lap time within 1 % of the reference car at equal grip (regen 30 A)': all(
        abs(laps[t]['car 1 v2, regen 30 A']['lap_s'] / laps[t]['reference car']['lap_s'] - 1) < 0.01 for t in laps),
}

# 8. what this study can give the team's simulator (f1tenth_gym vehicle parameters). The rest keep their defaults.
v_sw = 1.0
while v_sw < 30 and car.drive_force(v_sw) >= car.grip() * 0.999:
    v_sw += 0.05
gym = dict(m=M, a_max=round(min(car.mu * G, car.drive_force(1.0) / M), 2), v_switch=round(v_sw, 2), v_max=V_CAP,
           mu=car.mu, width=0.296, length=0.568,
           note='m from sim/perf/mass.py (not weighed); a_max and v_switch from the motor model at mu 0.8; v_max is the ESC cap; '
                'width and length are the Traxxas figures. lf, lr, h, I, C_Sf and C_Sr were not derived: keep the simulator defaults '
                'until the car is weighed on each axle.')
json.dump(gym, open(os.path.join(OUT, 'f1tenth_gym_params_car1v2.json'), 'w'), indent=1)
S['gym_params'] = gym
json.dump(S, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1)

# ---------------------------------------------------------------- markdown tables
L = []; A = L.append
A('| pinion / spur | overall ratio | top speed: worst case | nominal | best case | launch force at 60 A | grip at mu 0.8 | motor rpm at 13.5 m/s |')
A('| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |')
for r in rows:
    A(f"| {r['pinion']} / 54 | {r['ratio']} | {r['worst']} m/s | {r['nominal']} m/s | {r['best']} m/s | {r['launch_force_N']} N | {r['grip_force_N']} N | {r['rpm_at_cap']:,} |")
A('')
A('| straight between two 5 m/s corners | ' + ' | '.join(f'{x} m' for x in lengths) + ' |')
A('| --- | ' + ' | '.join('---:' for _ in lengths) + ' |')
for name, p in peaks.items():
    A(f'| {name} | ' + ' | '.join(f'{x:.1f}' for x in p) + ' |')
A('')
for tname in laps:
    A(f'**{tname}**'); A('')
    A('| car | lap | top speed | average |'); A('| --- | ---: | ---: | ---: |')
    for name, r in laps[tname].items():
        A(f"| {name} | {r['lap_s']} s | {r['v_max']} m/s | {r['v_mean']} m/s |")
    A('')
open(os.path.join(OUT, 'summary.md'), 'w').write('\n'.join(L) + '\n')
print('\n'.join(L))
print(json.dumps({k: S[k] for k in ('window_mps', 'mass', 'setup', 'top_speed_reference', 'run_up_from_5', 'run_up_from_5_reference',
                                     'straight_needed_m', 'cross_check', 'stopping_from_cap_m', 'kinetic_energy_J', 'esc', 'checks', 'gym_params')}, indent=1))

# ---------------------------------------------------------------- plots
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    col = {'reference car': '#555555', 'car 1 v2, regen 12 A': '#b5482a', 'car 1 v2, regen 30 A': '#1f5fa8',
           'car 1 v2, regen 30 A, capped at 13.5': '#1f5fa8'}
    sty = {'reference car': 'o-', 'car 1 v2, regen 12 A': 's--', 'car 1 v2, regen 30 A': '^-', 'car 1 v2, regen 30 A, capped at 13.5': ':'}
    fig, ax = plt.subplots(figsize=(6.6, 3.8), dpi=150)
    ax.axhspan(WIN[0], WIN[1], color='#1f5fa8', alpha=0.10, lw=0)
    ax.axhline(BENCH, color='#888888', lw=0.8)
    ax.text(lengths[-1], BENCH - 0.32, 'published competition top speed, 11 m/s', fontsize=7, color='#555555', ha='right')
    ax.text(lengths[0], WIN[1] + 0.08, 'target window, 12.5 to 13.5 m/s', fontsize=7, color='#1f5fa8')
    for name, p in peaks.items():
        ax.plot(lengths, p, sty[name], color=col[name], label=name, ms=4, lw=1.2)
    ax.set_xlabel('length of the straight between two 5 m/s corners, m'); ax.set_ylabel('highest speed reached, m/s')
    ax.set_title('Same grip (mu 0.8) for both cars', fontsize=9); ax.grid(alpha=0.3); ax.legend(fontsize=7, frameon=False, loc='lower right')
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'peak_vs_straight.png')); plt.close(fig)

    tname = 'box, 26 x 9 m centre line (66 m)'
    fig, ax = plt.subplots(figsize=(6.6, 3.4), dpi=150)
    for name in ('reference car', 'car 1 v2, regen 12 A', 'car 1 v2, regen 30 A'):
        s, v = traces[(tname, name)]
        ax.plot(s, v, color=col[name], ls='--' if '12 A' in name else '-', lw=1.2, label=f"{name}: {laps[tname][name]['lap_s']} s")
    ax.axhline(BENCH, color='#888888', lw=0.8)
    ax.set_xlabel('distance round the lap, m'); ax.set_ylabel('speed, m/s'); ax.grid(alpha=0.3)
    ax.set_title('One lap of a competition-sized box track, same grip (mu 0.8)', fontsize=9); ax.legend(fontsize=7, frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'lap_box.png')); plt.close(fig)
    print('plots written')
except Exception as e:
    print('no plots:', e)
